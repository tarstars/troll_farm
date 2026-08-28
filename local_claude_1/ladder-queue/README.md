# The ladder queue on the VM (2026-08-28, the owner offline for 8 hours)

`runner.py` runs every 5 minutes by cron on the VM (`ssh troll-vm`, checkout
`/home/tarstars/prj/troll_farm`, user crontab). It submits the items of `queue.json` in order,
reads each after 62 minutes (arena-room rank/score, the number the site shows), collects its 160
games into `games-<submission id>/`, appends the reading to `readings.jsonl`, commits and pushes
to `origin/main`, and submits the next. `state.json` is the live state; the log is `/home/tarstars/ladder-queue-runner.log` on the VM (outside the repo).
A submission that is not accepted halts the queue (nothing is resubmitted blindly).

To stop it: `ssh troll-vm crontab -l` and remove the `ladder-queue` line, or create the file
`/home/tarstars/prj/troll_farm/local_claude_1/ladder-queue/HALT` (not yet honoured -- edit the
crontab). To change the order: edit `queue.json` on `main` (the VM pulls before each tick? no --
the runner does not pull; edit it ON THE VM in the checkout, or push and `git pull` there).

Reads of the packages (talents and turn of every TRAIN, the third troll's share and turn, wins by
opponent troll count) are done afterwards with `local_claude_1/the-floor/ladder_read.py`.
