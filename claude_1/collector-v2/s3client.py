#!/usr/bin/env python3
"""Minimal stdlib S3 client (SigV4) for collector v2 — task `20260811-s3-collector-v2`, B2.

Why stdlib rather than boto3: the plan says stdlib-preferred, the frozen collector this
service sits beside is urllib-only, and collector v2 runs from a systemd timer where every
third-party import is a thing that can break unattended. boto3 IS installed on this VM and is
used in the tests as a signing ORACLE — a second implementation to disagree with — but nothing
at runtime imports it.

Credentials come only from `~/.config/troll-farm/s3-keys.json` in the format
`yc iam access-key create --format json` produces: key id at `.access_key.key_id`, secret at
`.secret`. They are never logged, never placed in a URL, and never included in any artifact:
`__repr__` is overridden so a credentials object cannot be printed into a traceback or a debug
line by accident.

Scope limits that are deliberate, matching the service account's rights and the bucket's
append-only design (storage.uploader + storage.viewer, no delete, no bucket admin):
`delete_object` exists ONLY so callers can prove it is refused; it is never used to clean up.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ENDPOINT = "https://storage.yandexcloud.net"
DEFAULT_REGION = "ru-central1"
DEFAULT_KEYS = Path.home() / ".config/troll-farm/s3-keys.json"
SERVICE = "s3"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"


class S3Error(RuntimeError):
    """An S3 request that came back as an error. Carries status and the parsed S3 code."""

    def __init__(self, status: int, code: str, message: str, key: str | None = None):
        super().__init__(f"HTTP {status} {code}: {message}" + (f" [{key}]" if key else ""))
        self.status = status
        self.code = code
        self.s3_message = message
        self.key = key


@dataclass(frozen=True)
class Credentials:
    key_id: str
    secret: str

    def __repr__(self) -> str:  # never let a secret reach a log or traceback
        return f"Credentials(key_id={self.key_id[:4]}…, secret=<redacted>)"

    __str__ = __repr__

    @classmethod
    def load(cls, path: Path | str = DEFAULT_KEYS) -> "Credentials":
        path = Path(path)
        mode = path.stat().st_mode & 0o777
        if mode & 0o077:
            raise PermissionError(
                f"{path} is mode {mode:o}; credentials must not be group/world readable")
        payload = json.loads(path.read_text())
        try:
            return cls(key_id=payload["access_key"]["key_id"], secret=payload["secret"])
        except (KeyError, TypeError) as error:
            raise ValueError(
                "key file is not in `yc iam access-key create --format json` shape "
                "(expected .access_key.key_id and .secret)") from error


def _quote(value: str, safe: str = "/") -> str:
    """S3 canonical URI encoding: RFC 3986, '/' preserved in paths, '~' unreserved."""
    return urllib.parse.quote(value, safe=safe + "-_.~")


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode(), hashlib.sha256).digest()


def canonical_request(method: str, canonical_uri: str, query: dict[str, str],
                      headers: dict[str, str], payload_sha256: str) -> tuple[str, str]:
    """Return (canonical_request, signed_headers). Split out so tests can pin it directly."""
    canonical_query = "&".join(
        f"{_quote(k, safe='')}={_quote(str(v), safe='')}" for k, v in sorted(query.items()))
    lowered = {k.lower(): " ".join(str(v).split()) for k, v in headers.items()}
    canonical_headers = "".join(f"{k}:{lowered[k]}\n" for k in sorted(lowered))
    signed_headers = ";".join(sorted(lowered))
    request = "\n".join([method, canonical_uri, canonical_query, canonical_headers,
                         signed_headers, payload_sha256])
    return request, signed_headers


class S3Client:
    """SigV4-signing S3 client over urllib. One bucket, path-style addressing."""

    def __init__(self, bucket: str, *, credentials: Credentials | None = None,
                 endpoint: str = DEFAULT_ENDPOINT, region: str = DEFAULT_REGION,
                 timeout: int = 60, urlopen=urllib.request.urlopen,
                 now=None) -> None:
        self.bucket = bucket
        self.credentials = credentials or Credentials.load()
        self.endpoint = endpoint.rstrip("/")
        self.region = region
        self.timeout = timeout
        self._urlopen = urlopen
        self._now = now or (lambda: dt.datetime.now(dt.timezone.utc))
        self.host = urllib.parse.urlparse(self.endpoint).netloc

    def _signing_key(self, datestamp: str) -> bytes:
        key = _sign(f"AWS4{self.credentials.secret}".encode(), datestamp)
        key = _sign(key, self.region)
        key = _sign(key, SERVICE)
        return _sign(key, "aws4_request")

    def build_request(self, method: str, key: str = "", *, query: dict | None = None,
                      body: bytes = b"", extra_headers: dict | None = None
                      ) -> urllib.request.Request:
        """Sign one request. Public because the tests diff it against botocore."""
        query = dict(query or {})
        now = self._now()
        amzdate = now.strftime("%Y%m%dT%H%M%SZ")
        datestamp = now.strftime("%Y%m%d")
        payload_sha256 = hashlib.sha256(body).hexdigest() if body else EMPTY_SHA256
        canonical_uri = "/" + _quote(self.bucket) + ("/" + _quote(key) if key else "")

        headers = {
            "host": self.host,
            "x-amz-content-sha256": payload_sha256,
            "x-amz-date": amzdate,
        }
        headers.update({k.lower(): v for k, v in (extra_headers or {}).items()})
        creq, signed_headers = canonical_request(method, canonical_uri, query, headers,
                                                 payload_sha256)
        scope = f"{datestamp}/{self.region}/{SERVICE}/aws4_request"
        string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amzdate, scope,
                                    hashlib.sha256(creq.encode()).hexdigest()])
        signature = hmac.new(self._signing_key(datestamp), string_to_sign.encode(),
                             hashlib.sha256).hexdigest()
        headers["authorization"] = (
            f"AWS4-HMAC-SHA256 Credential={self.credentials.key_id}/{scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}")

        url = self.endpoint + canonical_uri
        if query:
            url += "?" + "&".join(f"{_quote(k, safe='')}={_quote(str(v), safe='')}"
                                  for k, v in sorted(query.items()))
        return urllib.request.Request(url, data=body or None, headers=headers, method=method)

    def _send(self, request: urllib.request.Request) -> tuple[int, dict, bytes]:
        """Returns (status, headers, body).

        `headers` is passed through as the response's own mapping rather than `dict(...)`:
        urllib's is case-insensitive, and a plain dict is not. The smoke test caught this —
        the server returns `etag` lowercase, so `dict(...)["ETag"]` silently read None and
        every uploaded object reported a null ETag.
        """
        try:
            with self._urlopen(request, timeout=self.timeout) as response:
                return response.status, response.headers, response.read()
        except urllib.error.HTTPError as error:
            raw = error.read()
            code, message = "Unknown", raw[:300].decode(errors="replace")
            try:
                root = ET.fromstring(raw)
                code = (root.findtext("Code") or root.findtext(f"{S3_NS}Code") or code)
                message = (root.findtext("Message") or root.findtext(f"{S3_NS}Message")
                           or message)
            except ET.ParseError:
                pass
            raise S3Error(error.code, code, message) from None

    # --- operations -------------------------------------------------------------

    def put_object(self, key: str, body: bytes, *, content_type: str = "application/octet-stream",
                   if_none_match: bool = False) -> dict:
        """Upload one object. `if_none_match=True` asks the server to refuse an overwrite.

        Append-only is a property of the GRANT (no delete right), but the grant does NOT stop
        an overwrite, so callers that must never clobber pass if_none_match and check for a
        PreconditionFailed. Support is server-dependent; `b2_smoke.py` measures whether this
        endpoint honours it rather than assuming.
        """
        headers = {"content-type": content_type,
                   "content-length": str(len(body))}
        if if_none_match:
            headers["if-none-match"] = "*"
        status, response_headers, _ = self._send(
            self.build_request("PUT", key, body=body, extra_headers=headers))
        return {"status": status, "etag": response_headers.get("ETag"),
                "sha256": hashlib.sha256(body).hexdigest(), "size": len(body)}

    def get_object(self, key: str) -> bytes:
        _, _, body = self._send(self.build_request("GET", key))
        return body

    def head_object(self, key: str) -> dict:
        status, headers, _ = self._send(self.build_request("HEAD", key))
        return {"status": status, "etag": headers.get("ETag"),
                "size": int(headers.get("Content-Length", 0))}

    def list_objects(self, prefix: str = "", *, max_keys: int = 1000) -> list[dict]:
        """List every key under `prefix`, following continuation tokens."""
        out: list[dict] = []
        token = None
        while True:
            query = {"list-type": "2", "max-keys": str(max_keys)}
            if prefix:
                query["prefix"] = prefix
            if token:
                query["continuation-token"] = token
            _, _, body = self._send(self.build_request("GET", "", query=query))
            root = ET.fromstring(body)
            for node in root.findall(f"{S3_NS}Contents") or root.findall("Contents"):
                out.append({
                    "key": node.findtext(f"{S3_NS}Key") or node.findtext("Key"),
                    "size": int(node.findtext(f"{S3_NS}Size")
                                or node.findtext("Size") or 0),
                    "etag": (node.findtext(f"{S3_NS}ETag")
                             or node.findtext("ETag") or "").strip('"'),
                })
            truncated = (root.findtext(f"{S3_NS}IsTruncated")
                         or root.findtext("IsTruncated") or "false")
            if truncated.lower() != "true":
                return out
            token = (root.findtext(f"{S3_NS}NextContinuationToken")
                     or root.findtext("NextContinuationToken"))
            if not token:
                return out

    def delete_object(self, key: str) -> dict:
        """Present ONLY so the smoke test can prove deletion is refused. Never a cleanup path."""
        status, _, _ = self._send(self.build_request("DELETE", key))
        return {"status": status}
