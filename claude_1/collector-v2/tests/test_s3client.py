"""Offline tests for the stdlib SigV4 S3 client (B2, task `20260811-s3-collector-v2`).

The load-bearing test is a DIFFERENTIAL: botocore's `S3SigV4Auth` is a second, independent
implementation of the same specification, and it is installed on this VM. Every canonical
request this client builds is compared against the one botocore builds for the same inputs.
Encoding, header lowercasing, header sorting and query canonicalisation are exactly where a
hand-written signer goes wrong, and they are all visible in the canonical request.

`test_differential_fails_when_perturbed` is the control. A differential that cannot fail
proves nothing, so it perturbs the request and asserts the two implementations DISAGREE — if
that test ever passes trivially, the comparison above is inert.

The full HMAC chain (signing key -> signature) is not oracle-tested here; a wrong chain is
caught end-to-end by the live smoke test, which gets `SignatureDoesNotMatch` from the server.
That is stated so nobody reads this file as proving more than it does.

Run: `uvx --with boto3 pytest claude_1/collector-v2/tests -q` (boto3 is the oracle).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from s3client import (  # noqa: E402
    Credentials,
    S3Client,
    S3Error,
    _quote,
    canonical_request,
)

# The oracle is imported defensively rather than with importorskip: a module-level
# importorskip skips EVERY test in the file, so a missing botocore would turn the whole suite
# green while proving nothing. Instead the non-oracle tests always run, the differential is
# skipped explicitly, and `test_oracle_is_available` FAILS so the gap is impossible to miss.
try:
    from botocore import auth as botocore_auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials as BotoCredentials

    ORACLE_IMPORT_ERROR = None
except ImportError as error:  # pragma: no cover - exercised by running without boto3
    botocore_auth = AWSRequest = BotoCredentials = None
    ORACLE_IMPORT_ERROR = str(error)

needs_oracle = pytest.mark.skipif(ORACLE_IMPORT_ERROR is not None,
                                  reason=f"botocore oracle unavailable: {ORACLE_IMPORT_ERROR}")


def test_oracle_is_available():
    """Fail loudly when the differential cannot run — do not report a green suite.

    Invoke as `uvx --with boto3 pytest claude_1/collector-v2/tests -q`; plain `uvx pytest`
    builds an environment without botocore and would otherwise skip the only test that can
    catch a canonicalisation bug.
    """
    assert ORACLE_IMPORT_ERROR is None, (
        "botocore is required as the SigV4 signing oracle; run "
        "`uvx --with boto3 pytest claude_1/collector-v2/tests -q`")

FIXED_NOW = dt.datetime(2026, 8, 11, 11, 30, 0, tzinfo=dt.timezone.utc)
TEST_KEY_ID = "YCAJEexampleexampleexam"
TEST_SECRET = "YCPexampleSECRETexampleSECRETexample1234"
BUCKET = "troll-farm-data"


def make_client(**kwargs) -> S3Client:
    return S3Client(BUCKET, credentials=Credentials(TEST_KEY_ID, TEST_SECRET),
                    now=lambda: FIXED_NOW, **kwargs)


def boto_canonical(request) -> str:
    """Canonical request for the same inputs, per botocore's S3 signer."""
    aws_request = AWSRequest(method=request.get_method(), url=request.full_url,
                             data=request.data,
                             headers={k: v for k, v in request.header_items()
                                      if k.lower() != "authorization"})
    signer = botocore_auth.S3SigV4Auth(
        BotoCredentials(TEST_KEY_ID, TEST_SECRET), "s3", "ru-central1")
    aws_request.context["timestamp"] = FIXED_NOW.strftime("%Y%m%dT%H%M%SZ")
    return signer.canonical_request(aws_request)


CASES = [
    ("simple key", "GET", "games/probe/hello.txt", None, b""),
    ("nested date key", "PUT", "games/raw/daily/2026-08-11.jsonl.gz", None, b"payload"),
    ("key with spaces", "PUT", "games/probe/a file with spaces.bin", None, b"x"),
    ("key with unicode", "PUT", "games/probe/тролль-ферма.json", None, b"{}"),
    ("key with plus and equals", "GET", "games/probe/a+b=c.txt", None, b""),
    ("key with tilde and dots", "GET", "games/probe/v1.2~rc1/file.json", None, b""),
    ("list with prefix", "GET", "", {"list-type": "2", "prefix": "games/"}, b""),
    ("list with token", "GET", "", {"list-type": "2", "prefix": "games/raw/",
                                    "continuation-token": "abc/def+ghi=="}, b""),
]


@needs_oracle
@pytest.mark.parametrize("name,method,key,query,body",
                         CASES, ids=[c[0] for c in CASES])
def test_canonical_request_matches_botocore(name, method, key, query, body):
    client = make_client()
    request = client.build_request(method, key, query=query, body=body)
    mine, _ = canonical_request(
        method,
        "/" + request.full_url.split(f"//{client.host}/", 1)[1].split("?")[0],
        query or {},
        {k: v for k, v in request.header_items() if k.lower() != "authorization"},
        hashlib.sha256(body).hexdigest() if body else hashlib.sha256(b"").hexdigest(),
    )
    assert mine == boto_canonical(request)


@needs_oracle
def test_header_value_whitespace_is_collapsed_like_botocore():
    """SigV4 collapses interior whitespace in header values; M5 survived without this."""
    client = make_client()
    request = client.build_request(
        "PUT", "games/probe/ws.bin", body=b"x",
        extra_headers={"content-type": "text/plain",
                       "x-amz-meta-note": "  two   spaces  and\ttab  "})
    mine, _ = canonical_request(
        "PUT", f"/{BUCKET}/games/probe/ws.bin", {},
        {k: v for k, v in request.header_items() if k.lower() != "authorization"},
        hashlib.sha256(b"x").hexdigest())
    assert mine == boto_canonical(request)


@needs_oracle
def test_full_signature_matches_botocore():
    """Pins the whole HMAC chain — signing key derivation included — not just the canonical
    request. M8 (signing key skipping the service step) survived until this existed, because
    every other test compared only pre-signature material."""
    client = make_client()
    for method, key, body in [("GET", "games/probe/x", b""),
                              ("PUT", "games/raw/daily/2026-08-11.jsonl.gz", b"payload")]:
        request = client.build_request(method, key, body=body)
        mine = dict(request.header_items())["Authorization"].rsplit("Signature=", 1)[1]

        aws_request = AWSRequest(method=method, url=request.full_url, data=body or None,
                                 headers={k: v for k, v in request.header_items()
                                          if k.lower() != "authorization"})
        aws_request.context["timestamp"] = FIXED_NOW.strftime("%Y%m%dT%H%M%SZ")
        signer = botocore_auth.S3SigV4Auth(
            BotoCredentials(TEST_KEY_ID, TEST_SECRET), "s3", "ru-central1")
        creq = signer.canonical_request(aws_request)
        theirs = signer.signature(signer.string_to_sign(aws_request, creq), aws_request)
        assert mine == theirs, f"signature mismatch for {method} {key}"


@needs_oracle
def test_differential_fails_when_perturbed():
    """The control: if this passes, the comparison above is inert."""
    client = make_client()
    request = client.build_request("PUT", "games/probe/control.bin", body=b"abc")
    correct = boto_canonical(request)
    perturbed, _ = canonical_request(
        "PUT", f"/{BUCKET}/games/probe/control.bin", {},
        {k: v for k, v in request.header_items() if k.lower() != "authorization"},
        hashlib.sha256(b"WRONG").hexdigest(),
    )
    assert perturbed != correct


# --- path encoding: NOT oracle-testable, so pinned to the spec instead ----------------
#
# Measured limit of the differential above, found by mutation rather than by reading:
# dropping '~' from the unreserved set left all 18 tests green. botocore's S3 signer takes
# the URL path ALREADY ENCODED (`S3SigV4Auth._normalize_url_path` returns it untouched, since
# S3 does not re-encode), so feeding it a URL this client built means both sides share this
# client's encoding — the comparison cannot see a path-encoding bug. The tests below close
# that hole from RFC 3986 directly, not from the implementation, so they are not circular.

UNRESERVED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")


def test_quote_encodes_exactly_the_rfc3986_unreserved_set():
    """Every ASCII byte: literal iff unreserved (or '/', preserved in paths)."""
    for code in range(0x20, 0x7F):
        char = chr(code)
        encoded = _quote(char)
        if char in UNRESERVED or char == "/":
            assert encoded == char, f"{char!r} must not be percent-encoded"
        else:
            assert encoded == f"%{code:02X}", f"{char!r} must encode as %{code:02X}"


def test_quote_uses_uppercase_hex_and_utf8():
    assert _quote(" ") == "%20"          # not '+'
    assert _quote("+") == "%2B"          # uppercase hex, and '+' is not a literal
    assert _quote("~") == "~"            # unreserved since RFC 3986 — a classic signer bug
    assert _quote("é") == "%C3%A9"       # UTF-8 bytes, each percent-encoded
    assert _quote("a/b", safe="") == "a%2Fb"


def test_object_path_is_encoded_once_not_twice():
    """Double encoding is the other half of the same bug class: '%' must become '%25'."""
    client = make_client()
    request = client.build_request("GET", "games/probe/already%20encoded.txt")
    path = request.full_url.split(client.host, 1)[1]
    assert path == f"/{BUCKET}/games/probe/already%2520encoded.txt"


def test_spaces_and_unicode_in_key_reach_the_url_encoded():
    client = make_client()
    url = client.build_request("PUT", "games/probe/a b/тролль.json", body=b"x").full_url
    assert url.endswith(f"/{BUCKET}/games/probe/a%20b/%D1%82%D1%80%D0%BE%D0%BB%D0%BB%D1%8C.json")


def test_authorization_header_shape():
    request = make_client().build_request("GET", "games/probe/x")
    auth = dict(request.header_items())["Authorization"]
    assert auth.startswith("AWS4-HMAC-SHA256 Credential=")
    assert f"/20260811/ru-central1/s3/aws4_request" in auth
    assert "SignedHeaders=host;x-amz-content-sha256;x-amz-date," in auth
    assert len(auth.rsplit("Signature=", 1)[1]) == 64


def test_signature_changes_with_body():
    client = make_client()
    one = dict(client.build_request("PUT", "k", body=b"a").header_items())["Authorization"]
    two = dict(client.build_request("PUT", "k", body=b"b").header_items())["Authorization"]
    assert one != two


def test_credentials_never_render_the_secret():
    creds = Credentials("YCAJEabcdefghijklmnop", "supersecretvalue")
    assert "supersecret" not in repr(creds)
    assert "supersecret" not in str(creds)
    assert "supersecret" not in f"{creds}"
    assert "supersecret" not in json.dumps({"c": repr(creds)})


def test_credentials_reject_loose_file_mode(tmp_path):
    path = tmp_path / "keys.json"
    path.write_text(json.dumps({"access_key": {"key_id": "k"}, "secret": "s"}))
    path.chmod(0o644)
    with pytest.raises(PermissionError):
        Credentials.load(path)
    path.chmod(0o600)
    assert Credentials.load(path).key_id == "k"


def test_credentials_reject_wrong_shape(tmp_path):
    path = tmp_path / "keys.json"
    path.write_text(json.dumps({"accessKeyId": "k", "secretAccessKey": "s"}))
    path.chmod(0o600)
    with pytest.raises(ValueError):
        Credentials.load(path)


def test_secret_never_reaches_the_url_or_headers():
    request = make_client().build_request("PUT", "games/probe/x", body=b"y")
    assert TEST_SECRET not in request.full_url
    for _, value in request.header_items():
        assert TEST_SECRET not in str(value)


def test_error_parsing_extracts_s3_code():
    """S3 errors must surface the S3 code, not just an HTTP number."""
    import urllib.error

    body = (b'<?xml version="1.0"?><Error><Code>AccessDenied</Code>'
            b"<Message>Access Denied</Message></Error>")

    def raising_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {},
                                     __import__("io").BytesIO(body))

    client = make_client(urlopen=raising_urlopen)
    with pytest.raises(S3Error) as caught:
        client.get_object("games/probe/nope")
    assert caught.value.status == 403
    assert caught.value.code == "AccessDenied"


def test_etag_is_read_case_insensitively():
    """Regression: the live endpoint returns `etag` lowercase and a plain dict missed it,
    so every uploaded object reported a null ETag. Found by the smoke run, not by review."""
    import email.message
    import io

    headers = email.message.Message()
    headers["etag"] = '"abc123"'
    headers["content-length"] = "3"

    class FakeResponse(io.BytesIO):
        status = 200

        def __init__(self):
            super().__init__(b"xyz")
            self.headers = headers

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    client = make_client(urlopen=lambda request, timeout=None: FakeResponse())
    assert client.head_object("games/probe/x")["etag"] == '"abc123"'
    assert client.put_object("games/probe/x", b"xyz")["etag"] == '"abc123"'


def test_list_objects_follows_continuation_tokens():
    """A single-page lister silently truncates a corpus; this pins the loop."""
    import io
    import urllib.request

    pages = [
        (b'<?xml version="1.0"?><ListBucketResult>'
         b"<Contents><Key>games/a</Key><Size>1</Size><ETag>&quot;x&quot;</ETag></Contents>"
         b"<IsTruncated>true</IsTruncated><NextContinuationToken>T2</NextContinuationToken>"
         b"</ListBucketResult>"),
        (b'<?xml version="1.0"?><ListBucketResult>'
         b"<Contents><Key>games/b</Key><Size>2</Size><ETag>&quot;y&quot;</ETag></Contents>"
         b"<IsTruncated>false</IsTruncated></ListBucketResult>"),
    ]
    seen_tokens = []

    class FakeResponse(io.BytesIO):
        status = 200
        headers: dict = {}

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request: urllib.request.Request, timeout=None):
        seen_tokens.append("continuation-token=T2" in request.full_url)
        return FakeResponse(pages[len(seen_tokens) - 1])

    client = make_client(urlopen=fake_urlopen)
    keys = [row["key"] for row in client.list_objects("games/")]
    assert keys == ["games/a", "games/b"]
    assert seen_tokens == [False, True]
