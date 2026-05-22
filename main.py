"""Palette Pairs — tile memory game."""

from __future__ import annotations

import random
import tkinter as tk
from pathlib import Path
from tkinter import Label, LabelFrame

from PIL import Image, ImageTk

TILE_SIZE = 32
TILE_CROP_Y_OFFSET = 8
GRID_COLUMNS = 8
GRID_ROWS = 8
PAIR_COUNT = 32

# (column, row) indices into the spritesheet for each tile type
SPRITE_COORDS = (
    [(x, 10) for x in range(11)]
    + [(11, 7), (1, 11), (2, 11), (3, 11), (2, 3), (3, 3), (4, 3)]
    + [(x, 4) for x in range(2, 10)]
    + [(x, 3) for x in (7, 8, 10, 11)]
    + [(x, 5) for x in (2, 4, 6)]
)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
SPRITESHEET_PATH = ASSETS_DIR / "colours.png"


def crop_box(col: int, row: int) -> tuple[int, int, int, int]:
    x0, y0 = col * TILE_SIZE, row * TILE_SIZE + TILE_CROP_Y_OFFSET
    return (x0, y0, x0 + TILE_SIZE, y0 + TILE_SIZE)


def build_deck() -> list[tuple[int, int]]:
    deck: list[tuple[int, int]] = []
    counts: dict[tuple[int, int], int] = {}

    while len(deck) < PAIR_COUNT:
        tile = random.choice(SPRITE_COORDS)
        if counts.get(tile, 0) < 1:
            deck.append(tile)
            counts[tile] = counts.get(tile, 0) + 1

    pairs = deck * 2
    random.shuffle(pairs)
    return pairs


class PalettePairsGame:
    def __init__(self, root: tk.Tk, spritesheet_path: Path = SPRITESHEET_PATH) -> None:
        if not spritesheet_path.is_file():
            raise FileNotFoundError(f"Spritesheet not found: {spritesheet_path}")

        self.root = root
        self.root.title("Palette Pairs")

        self.spritesheet = Image.open(spritesheet_path)
        self.grass_photo = ImageTk.PhotoImage(self.spritesheet.crop(crop_box(0, 1)))

        self.deck = build_deck()
        self.tile_photos = [
            ImageTk.PhotoImage(self.spritesheet.crop(crop_box(c, r))) for c, r in self.deck
        ]

        self.matched: set[int] = set()
        self.first_pick: int | None = None
        self.reswap_job: str | None = None
        self.score = 0
        self.tries = 0

        self._build_ui()

    def _build_ui(self) -> None:
        board = LabelFrame(self.root)
        board.grid(row=0, column=0, padx=8, pady=8)

        hud = LabelFrame(self.root)
        hud.grid(row=1, column=0, padx=8, pady=(0, 8))

        self.score_label = Label(hud, text="Score: 0")
        self.tries_label = Label(hud, text="Tries: 0")
        self.score_label.grid(row=0, column=0, padx=12, pady=4)
        self.tries_label.grid(row=1, column=0, padx=12, pady=4)
        self.win_label: Label | None = None

        self.buttons: list[tk.Button] = []
        for index in range(GRID_COLUMNS * GRID_ROWS):
            button = tk.Button(
                board,
                image=self.grass_photo,
                command=lambda i=index: self.on_tile_click(i),
            )
            button.grid(row=index // GRID_COLUMNS, column=index % GRID_COLUMNS)
            self.buttons.append(button)

    def on_tile_click(self, index: int) -> None:
        if (
            index in self.matched
            or self.reswap_job is not None
            or index == self.first_pick
        ):
            return

        self.buttons[index].config(image=self.tile_photos[index])

        if self.first_pick is None:
            self.first_pick = index
            return

        self.tries += 1
        self.tries_label.config(text=f"Tries: {self.tries}")

        first = self.first_pick
        if self.deck[index] == self.deck[first]:
            self.matched.update({index, first})
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            if self.score == PAIR_COUNT and self.win_label is None:
                self.win_label = Label(self.score_label.master, text="You win!")
                self.win_label.grid(row=2, column=0, pady=4)
            self.first_pick = None
        else:
            self.reswap_job = self.root.after(200, lambda: self.hide_pair(index, first))

    def hide_pair(self, second: int, first: int) -> None:
        self.reswap_job = None
        self.buttons[second].config(image=self.grass_photo)
        self.buttons[first].config(image=self.grass_photo)
        self.first_pick = None


def main() -> None:
    root = tk.Tk()
    PalettePairsGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
