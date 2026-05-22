<div align="center">

# Palette Pairs

### Memory match game with pixel-art tiles

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Tkinter-desktop%20UI-2d3748?style=for-the-badge)]()
[![Pillow](https://img.shields.io/badge/Pillow-spritesheet-FFE873?style=for-the-badge)](https://python-pillow.org/)

<br/>

[![Grid](https://img.shields.io/badge/grid-8×8-22c55e?style=flat-square)]()
[![Pairs](https://img.shields.io/badge/pairs-32-3b82f6?style=flat-square)]()
[![Offline](https://img.shields.io/badge/offline-no%20server-64748b?style=flat-square)]()

<br/>

[![GitHub last commit](https://img.shields.io/github/last-commit/hackerbotfz/Python-Games?style=flat-square&logo=github)](https://github.com/hackerbotfz/Python-Games/commits)
[![GitHub repo size](https://img.shields.io/github/repo-size/hackerbotfz/Python-Games?style=flat-square&logo=github)](https://github.com/hackerbotfz/Python-Games)
[![GitHub stars](https://img.shields.io/github/stars/hackerbotfz/Python-Games?style=flat-square&logo=github)](https://github.com/hackerbotfz/Python-Games/stargazers)

<br/>

**[Faiz Lawan](https://github.com/hackerbotfz)**

</div>

---

**Palette Pairs** is a desktop memory game: flip tiles on an 8×8 board, find matching pixel-art sprites, and clear all 32 pairs in as few tries as possible. Built with **Python**, **Tkinter**, and a single spritesheet asset.

## Overview

| Detail | Value |
|--------|--------|
| **Board** | 64 hidden tiles (8×8) |
| **Goal** | Match all 32 sprite pairs |
| **Feedback** | Live score and try counter; win banner at completion |
| **Assets** | Sprites cropped from `assets/colours.png` |

Click a tile to reveal it; click a second to check for a match. Wrong pairs flip back after a short delay.

## Architecture

```mermaid
flowchart LR
    SS[colours.png] --> PIL[Pillow crop]
    PIL --> TK[ImageTk tiles]
    TK --> UI[Tkinter 8×8 grid]
    UI --> LOGIC[PalettePairsGame]
```

`PalettePairsGame` owns deck generation, input handling, match detection, and HUD updates. Assets resolve relative to the project via `pathlib` — no hard-coded machine paths.

## Tech stack

Python · Tkinter · Pillow

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Repository

```
python_games/
├── main.py
├── requirements.txt
├── assets/
│   └── colours.png
└── README.md
```

## License

© Faiz Lawan.
