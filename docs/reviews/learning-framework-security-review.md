# Security Review: Learning Framework (P9.E5.S1, SA-8)

**Verdict: APPROVED by the Player on 2026-11-20 at 12:34 for PyTorch 2.15.0**, with the install method and the rules below. MLX was not chosen. Checked 2026-11-20 from PyPI's public metadata (`https://pypi.org/pypi/<name>/json`) on this Mac (macOS 15.6, Apple silicon, Python 3.13.3 from python.org).

## Why it is needed
Phase 9 trains a combat value network and a policy network on the simulator's self-play data (`tools/selfplay.py`, `data/learn/`). The project's tools are standard-library Python; neural networks need a numerical library. No learning code runs until one is approved.

## Candidates

| | PyTorch | MLX |
|---|---|---|
| Package and version | `torch` 2.15.0 | `mlx` 0.32.4 with `mlx-metal` 0.32.4 |
| Publisher, source | PyTorch Foundation, https://pytorch.org (source https://github.com/pytorch/pytorch) | Apple, https://github.com/ml-explore/mlx |
| Published on PyPI | 2026-10-28 (23 days before this review) | 2026-10-14 (37 days) |
| Licence (PyPI metadata) | Apache-2.0 AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND ISC AND MIT AND Zlib | MIT |
| Wheel for this Mac | `torch-2.15.0-cp313-cp313-macosx_14_0_arm64.whl`, 138.6 MB, sha256 `fbefd73b521d3c75c5a1d7c77056b2c6339b81468d14d4e33c55f525418a5855` | `mlx-0.32.4-cp313-cp313-macosx_14_0_arm64.whl`, 0.7 MB, sha256 `c7375f2d6acd8c72f413d018266ae06387cb9caab31f475f3ff1c5600a7cb4c5`; `mlx_metal-0.32.4-py3-none-macosx_14_0_arm64.whl`, 45.0 MB, sha256 `8019b2db622599267d66cc168b2f0dbf5af929790a6c3b3913e00eabc42a7947` |
| Other dependencies on macOS | filelock, typing-extensions, setuptools, sympy (with mpmath), networkx, jinja2 (with MarkupSafe), fsspec. The CUDA packages in its metadata are Linux-only and are not installed on macOS | none |
| Apple GPU | yes (MPS backend) | yes (Metal; built for Apple silicon) |
| Export for fast inference in the C# simulator host | ONNX export is built in (the host could then run models through ONNX Runtime, a later and separate review) | no standard export path to .NET |

## Recommendation
**PyTorch 2.15.0.** It is the more mature library, its ONNX export lets a trained model later run inside the simulator host for fast search, and the networks planned here are small enough for the CPU or the Apple GPU. MLX is lighter (no other dependencies) and a sound alternative if the Player prefers fewer packages; the code would be written so the model code can change library.

## Install method (after approval only)
1. A project virtual environment at `.venv-learn/` (ignored by git), created with `python3 -m venv .venv-learn`. Nothing is installed globally or into the system Python.
2. Exact pins with hashes: `requirements-learn.txt` lists `torch==2.15.0` with the sha256 above and every dependency at an exact version with its sha256, generated from PyPI at install time and committed before first use; install with `.venv-learn/bin/pip install --require-hashes --only-binary :all: -r requirements-learn.txt`, so pip refuses anything else.
3. The installed set is recorded (`pip freeze`) in the experiment records (P9.E5.S3).

## Network behaviour
- pip contacts `pypi.org` and `files.pythonhosted.org` during installation only.
- At run time neither library contacts the network on its own. PyTorch downloads only when code calls download helpers (`torch.hub`, dataset loaders); the project's code will not call them (rule below). Training jobs run with the same `lsof` network check as the simulator sandbox test (`tools/sim.py sandbox`).

## What it can access
Like any Python package, it runs with the user's permissions. Mitigations: training jobs read only `data/learn/` and write only `data/learn/` and `models/` (ignored by git except manifests); they never touch the game's save folder; Python runs with `-I` from the project's own scripts.

## Rules if approved
- No download helpers (`torch.hub`, pretrained weights, dataset downloaders). Models are trained from the project's own data only.
- `torch.load` only on the project's own checkpoints and always with `weights_only=True` (a checkpoint from elsewhere could run code when loaded).
- Version changes need a new entry in this review (version, date, hashes) before installing.
- Deployed models take the visible observation only (FP-10); the model card states the data and the teacher (P9.E2.S4).

## Install record (2026-11-20)
- `.venv-learn/` created with `python3 -m venv` (Python 3.13.3); nothing installed globally.
- The 10 wheels were downloaded into an empty folder with `pip download torch==2.15.0 --only-binary :all:`; each wheel's sha256 matched the hash PyPI publishes for it, and torch's matched the hash recorded above. `requirements-learn.txt` (committed) pins every package with its hash.
- Installed offline from that folder: `pip install --require-hashes --only-binary :all: --no-index --find-links <folder> -r requirements-learn.txt`. Installed set: filelock 4.2.12, fsspec 2026.9.0, Jinja2 3.1.6, MarkupSafe 3.0.4, mpmath 1.3.0, networkx 3.7, setuptools 84.2.1, sympy 1.14.0, torch 2.15.0, typing_extensions 4.16.0.
- Check: `import torch` works; the Apple GPU backend (MPS) is available; 200 training steps of a small network ran on CPU (3.0 s) and MPS (1.9 s); the process was polled with `lsof -i` 39 times while it ran and opened no socket.
- NumPy is not installed (torch prints a warning and works without it). Adding NumPy later needs a new entry here.
