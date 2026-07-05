"""A tiny from-scratch policy network (numpy only) for the Troll Farm A2C loop.

One-hidden-layer MLP trunk -> a factored categorical policy over the MultiDiscrete
action heads (nvec) + a scalar value head. Backprop and Adam are hand-written in
`rl/train.py`; this module holds the parameters, the forward pass, action
sampling, and save/load. No torch, so it always runs given only numpy.
"""

import numpy as np


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


class MLPPolicy:
    def __init__(self, obs_dim, nvec, hidden=128, seed=0):
        self.obs_dim = obs_dim
        self.nvec = list(int(n) for n in nvec)
        self.n_out = int(sum(self.nvec))
        self.hidden = hidden
        rng = np.random.RandomState(seed)
        # He-ish init for the tanh trunk; tiny init for the output heads.
        self.W1 = (rng.randn(obs_dim, hidden) * np.sqrt(1.0 / obs_dim)).astype(np.float64)
        self.b1 = np.zeros(hidden)
        self.Wp = (rng.randn(hidden, self.n_out) * 0.01)
        self.bp = np.zeros(self.n_out)
        self.Wv = (rng.randn(hidden, 1) * 0.01)
        self.bv = np.zeros(1)
        self._names = ["W1", "b1", "Wp", "bp", "Wv", "bv"]
        # Adam moments
        self._m = {k: np.zeros_like(getattr(self, k)) for k in self._names}
        self._v = {k: np.zeros_like(getattr(self, k)) for k in self._names}
        self._t = 0

    # ── forward ──
    def forward(self, X):
        """X: (N, obs_dim) -> (h, logits, value)."""
        h = np.tanh(X @ self.W1 + self.b1)
        logits = h @ self.Wp + self.bp
        value = (h @ self.Wv + self.bv)[:, 0]
        return h, logits, value

    def split(self, logits):
        """Split concatenated logits (N, n_out) into per-head (N, n_i) chunks."""
        out, off = [], 0
        for n in self.nvec:
            out.append(logits[:, off:off + n])
            off += n
        return out

    # ── act (sampling / greedy) ──
    def act(self, obs, rng, greedy=False):
        _, logits, value = self.forward(obs[None, :])
        action = np.empty(len(self.nvec), dtype=np.int64)
        for gi, g in enumerate(self.split(logits)):
            p = softmax(g[0])
            action[gi] = int(p.argmax()) if greedy else int(rng.choice(len(p), p=p))
        return action, float(value[0])

    # ── Adam update given grads dict {name: grad} ──
    def adam_step(self, grads, lr=2e-3, b1=0.9, b2=0.999, eps=1e-8, clip=5.0):
        # global-norm clip
        total = np.sqrt(sum(float((grads[k] ** 2).sum()) for k in self._names))
        scale = clip / (total + 1e-8) if total > clip else 1.0
        self._t += 1
        for k in self._names:
            g = grads[k] * scale
            self._m[k] = b1 * self._m[k] + (1 - b1) * g
            self._v[k] = b2 * self._v[k] + (1 - b2) * (g * g)
            mhat = self._m[k] / (1 - b1 ** self._t)
            vhat = self._v[k] / (1 - b2 ** self._t)
            setattr(self, k, getattr(self, k) - lr * mhat / (np.sqrt(vhat) + eps))
        return total  # pre-clip grad norm (for logging)

    # ── persistence ──
    def save(self, path):
        np.savez(path, obs_dim=self.obs_dim, nvec=np.array(self.nvec),
                 hidden=self.hidden, **{k: getattr(self, k) for k in self._names})

    @classmethod
    def load(cls, path):
        d = np.load(path)
        p = cls(int(d["obs_dim"]), list(d["nvec"]), hidden=int(d["hidden"]))
        for k in p._names:
            setattr(p, k, d[k])
        return p
