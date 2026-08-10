# Deploying coordd (P1 shadow mode)

Spec: `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md`.
Order: VM first, tunnel second, shadow runbook third
(`coordination/coordd-shadow-runbook.md`).

## On the Yandex Cloud VM (hosts claude_1 and codex_1)

```bash
sudo useradd -r -m -d /var/lib/coordd coordd
sudo mkdir -p /opt/troll_farm /etc/coordd
sudo git clone git@github.com:tarstars/troll_farm.git /opt/troll_farm   # or update an existing clone
sudo -u coordd git clone --mirror git@github.com:tarstars/troll_farm.git /var/lib/coordd/repo.git
openssl rand -hex 32 | sudo tee /etc/coordd/token >/dev/null
sudo chmod 600 /etc/coordd/token
sudo cp /opt/troll_farm/deploy/coordd.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now coordd
curl -s http://127.0.0.1:7077/health   # {"ok": true, ...}
```

Agents on the VM read the token from `/etc/coordd/token` into `~/.coordd/token`
(per agent user) and use `COORDD_URL=http://127.0.0.1:7077`.

## On project_host (local agents)

```bash
mkdir -p ~/.coordd && scp VM_ALIAS:/etc/coordd/token ~/.coordd/token && chmod 600 ~/.coordd/token
mkdir -p ~/.config/systemd/user
cp deploy/coordd-tunnel.service ~/.config/systemd/user/   # edit VM_ALIAS first
systemctl --user daemon-reload && systemctl --user enable --now coordd-tunnel
curl -s http://127.0.0.1:7077/health
python3 scripts/coordctl.py doctor --repo .
```

## Not done here

No public port, no TLS (the tunnel is the boundary), no CI (owner ruling
2026-08-10), no authority switch — git remains authoritative until the P2 plan.
Daily dump: `python3 scripts/coordd.py dump --db /var/lib/coordd/coordd.sqlite3
--out /var/lib/coordd/backup-$(date -u +%F).sqlite3` (add as a coordd-user cron
on the VM); audit export lands in-repo during P2.
