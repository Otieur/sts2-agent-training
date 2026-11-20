# Runbook: Keep the Player's Fight Recordings (read-only)

The game writes `replays/latest.mcr` in the active profile at the end of every fight and overwrites it at the next one. Each recording is ground truth for the simulator: `tools/sim.py fidelity` replays it and compares every turn boundary with the game's own stored state. The Agent's runs cover only what the Agent reaches; the Player's own play adds acts 2 and 3, other characters and rarer cards and relics. Agreed with the Player on 2026-11-20.

## While the Player plays
Start this before or during a session (a terminal tab is enough):

```bash
python3 -I tools/keep_replays.py watch --while-game-runs
```

It checks every 2 seconds, copies each new recording once it is completely written, and stops a minute after the game closes. `Ctrl-C` stops it at any time. Without `--while-game-runs` it runs until stopped.

## Afterwards
```bash
python3 -I tools/keep_replays.py status
```

```bash
python3 -I tools/sim.py fidelity
```

## Rules it follows
- The save folder is only read: each recording is opened read-only and copied; nothing there is written, renamed or deleted.
- The Agent's profile (`modded/profile2`) is skipped; `tools/play_turn.py` keeps those.
- Copies go to `data/sim/replays/player-<profile>/<time>-<game version>.mcr`, ignored by git; an index (`data/sim/replays/player-index.json`) prevents duplicates. Names never contain the Steam id.
- Recordings from another game build (the header names it) are kept but skipped by `tools/sim.py fidelity`. Example: a fight recorded on v0.113.1 before the branch switch.
