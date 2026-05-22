"""Palette Pairs — colour memory game."""

from __future__ import annotations

import math
import random
import time
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

from PIL import Image, ImageDraw, ImageTk

GRID_COLUMNS = 8
GRID_ROWS = 8
CELL_COUNT = GRID_COLUMNS * GRID_ROWS
PAIR_COUNT = CELL_COUNT // 2
SHEET_COLS = 8
SHEET_ROWS = 8
DISPLAY_TILE = 56
FLIP_BACK_MS = 700
PEEK_MS = 1400

COLORS = {
    "bg": "#11111b",
    "panel": "#1e1e2e",
    "panel_border": "#313244",
    "text": "#cdd6f4",
    "muted": "#a6adc8",
    "accent": "#89b4fa",
    "success": "#a6e3a1",
    "card_back": "#45475a",
    "card_back_border": "#585b70",
    "matched_border": "#f9e2af",
}

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
SPRITESHEET_PATH = ASSETS_DIR / "colours.png"


def load_spritesheet(path: Path) -> tuple[Image.Image, int, int]:
    sheet = Image.open(path).convert("RGB")
    cell_w = sheet.width // SHEET_COLS
    cell_h = sheet.height // SHEET_ROWS
    return sheet, cell_w, cell_h


def crop_cell(sheet: Image.Image, cell_w: int, cell_h: int, col: int, row: int) -> Image.Image:
    box = (col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h)
    tile = sheet.crop(box)
    return tile.resize((DISPLAY_TILE, DISPLAY_TILE), Image.Resampling.LANCZOS)


def make_card_back(size: int = DISPLAY_TILE) -> Image.Image:
    img = Image.new("RGB", (size, size), COLORS["card_back"])
    draw = ImageDraw.Draw(img)
    margin = max(4, size // 10)
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=size // 8,
        outline=COLORS["card_back_border"],
        width=3,
    )
    draw.rounded_rectangle(
        (size // 4, size // 4, 3 * size // 4, 3 * size // 4),
        radius=size // 10,
        fill="#313244",
        outline=COLORS["accent"],
        width=2,
    )
    cx, cy = size // 2, size // 2
    r = size // 6
    palette = [
        "#f38ba8", "#fab387", "#f9e2af", "#a6e3a1",
        "#89dceb", "#89b4fa", "#cba6f7", "#f5c2e7",
    ]
    for i, colour in enumerate(palette):
        angle = i * (360 / len(palette))
        x = cx + int(r * math.cos(math.radians(angle)))
        y = cy + int(r * math.sin(math.radians(angle)))
        dot = size // 14
        draw.ellipse((x - dot, y - dot, x + dot, y + dot), fill=colour)
    return img


def all_sheet_cells() -> list[tuple[int, int]]:
    return [(c, r) for r in range(SHEET_ROWS) for c in range(SHEET_COLS)]


def build_deck() -> list[tuple[int, int]]:
    pool = all_sheet_cells()
    random.shuffle(pool)
    chosen = pool[:PAIR_COUNT]
    deck = chosen * 2
    random.shuffle(deck)
    return deck


class PalettePairsGame:
    def __init__(self, root: tk.Tk, spritesheet_path: Path = SPRITESHEET_PATH) -> None:
        if not spritesheet_path.is_file():
            raise FileNotFoundError(f"Spritesheet not found: {spritesheet_path}")

        self.root = root
        self.root.title("Palette Pairs")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.sheet, self.cell_w, self.cell_h = load_spritesheet(spritesheet_path)
        self.back_photo = ImageTk.PhotoImage(make_card_back())
        self.photo_cache: dict[tuple[int, int], ImageTk.PhotoImage] = {}

        self.title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.stat_font = tkfont.Font(family="Segoe UI", size=12)
        self.big_font = tkfont.Font(family="Segoe UI", size=22, weight="bold")

        self.reswap_job = None
        self.tiles: list[tk.Label] = []
        self.win_banner = None
        self._build_ui()

    def reset_game_state(self) -> None:
        if self.reswap_job is not None:
            self.root.after_cancel(self.reswap_job)
        self.deck = build_deck()
        self.matched: set[int] = set()
        self.revealed: set[int] = set()
        self.first_pick: int | None = None
        self.reswap_job: str | None = None
        self.lock_board = False
        self.pairs_found = 0
        self.moves = 0
        self.started_at = time.time()
        self.game_over = False
        if self.tiles:
            for i in range(CELL_COUNT):
                self.hide(i)
            self._update_hud()
            self.root.after(300, self.peek_all_cards)

    def tile_photo(self, cell: tuple[int, int]) -> ImageTk.PhotoImage:
        if cell not in self.photo_cache:
            pil = crop_cell(self.sheet, self.cell_w, self.cell_h, cell[0], cell[1])
            self.photo_cache[cell] = ImageTk.PhotoImage(pil)
        return self.photo_cache[cell]

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=COLORS["bg"], padx=16, pady=16)
        outer.grid(row=0, column=0)

        header = tk.Frame(outer, bg=COLORS["bg"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        tk.Label(
            header,
            text="Palette Pairs",
            fg=COLORS["text"],
            bg=COLORS["bg"],
            font=self.title_font,
        ).pack(side="left")
        tk.Label(
            header,
            text="Match the colour swatches",
            fg=COLORS["muted"],
            bg=COLORS["bg"],
            font=self.stat_font,
        ).pack(side="left", padx=(12, 0))

        body = tk.Frame(outer, bg=COLORS["bg"])
        body.grid(row=1, column=0, columnspan=2)

        self.board = tk.Frame(
            body,
            bg=COLORS["panel_border"],
            padx=2,
            pady=2,
        )
        self.board.grid(row=0, column=0, padx=(0, 16))

        inner = tk.Frame(self.board, bg=COLORS["panel"])
        inner.pack()

        for index in range(CELL_COUNT):
            tile = tk.Label(
                inner,
                image=self.back_photo,
                bg=COLORS["panel"],
                bd=0,
                highlightthickness=2,
                highlightbackground=COLORS["panel"],
                cursor="hand2",
            )
            tile.grid(row=index // GRID_COLUMNS, column=index % GRID_COLUMNS, padx=2, pady=2)
            tile.bind("<Button-1>", lambda _e, i=index: self.on_tile_click(i))
            self.tiles.append(tile)

        side = tk.Frame(body, bg=COLORS["panel"], padx=20, pady=20)
        side.grid(row=0, column=1, sticky="ns")

        self.pairs_var = tk.StringVar()
        self.moves_var = tk.StringVar()
        self.accuracy_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.status_var = tk.StringVar()

        for row, (label, var) in enumerate(
            [
                ("Pairs", self.pairs_var),
                ("Moves", self.moves_var),
                ("Accuracy", self.accuracy_var),
                ("Time", self.time_var),
            ]
        ):
            tk.Label(side, text=label, fg=COLORS["muted"], bg=COLORS["panel"], font=self.stat_font).grid(
                row=row * 2, column=0, sticky="w", pady=(0, 2)
            )
            tk.Label(side, textvariable=var, fg=COLORS["text"], bg=COLORS["panel"], font=self.big_font).grid(
                row=row * 2 + 1, column=0, sticky="w", pady=(0, 14)
            )

        self.progress = tk.Canvas(side, width=180, height=10, bg=COLORS["panel"], highlightthickness=0)
        self.progress.grid(row=8, column=0, sticky="ew", pady=(0, 16))

        tk.Label(
            side,
            textvariable=self.status_var,
            fg=COLORS["accent"],
            bg=COLORS["panel"],
            font=self.stat_font,
            wraplength=180,
            justify="left",
        ).grid(row=9, column=0, sticky="w", pady=(0, 16))

        tk.Button(
            side,
            text="New game",
            command=self.new_game,
            bg=COLORS["accent"],
            fg=COLORS["bg"],
            activebackground="#b4befe",
            activeforeground=COLORS["bg"],
            font=self.stat_font,
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).grid(row=10, column=0, sticky="ew")

        self.reset_game_state()
        self._update_hud()
        self._tick_clock()

    def _tick_clock(self) -> None:
        if not self.game_over:
            elapsed = int(time.time() - self.started_at)
            mins, secs = divmod(elapsed, 60)
            self.time_var.set(f"{mins:02d}:{secs:02d}")
        self.root.after(500, self._tick_clock)

    def _update_hud(self) -> None:
        self.pairs_var.set(f"{self.pairs_found} / {PAIR_COUNT}")
        self.moves_var.set(str(self.moves))
        if self.moves == 0:
            self.accuracy_var.set("—")
        else:
            pct = round(100 * self.pairs_found / self.moves)
            self.accuracy_var.set(f"{pct}%")
        progress = self.pairs_found / PAIR_COUNT
        self.progress.delete("all")
        w = 180
        self.progress.create_rectangle(0, 0, w, 10, fill=COLORS["panel_border"], outline="")
        if progress > 0:
            self.progress.create_rectangle(0, 0, w * progress, 10, fill=COLORS["success"], outline="")

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def reveal(self, index: int) -> None:
        self.tiles[index].config(image=self.tile_photo(self.deck[index]))
        self.revealed.add(index)

    def hide(self, index: int) -> None:
        if index in self.matched:
            return
        self.tiles[index].config(
            image=self.back_photo,
            highlightbackground=COLORS["panel"],
        )
        self.revealed.discard(index)

    def mark_matched(self, index: int) -> None:
        self.tiles[index].config(
            image=self.tile_photo(self.deck[index]),
            highlightbackground=COLORS["matched_border"],
            highlightthickness=3,
        )
        self.matched.add(index)
        self.revealed.add(index)

    def peek_all_cards(self) -> None:
        self.lock_board = True
        self.set_status("Memorise the colours…")
        for i in range(CELL_COUNT):
            self.reveal(i)
        self.root.after(PEEK_MS, self.hide_after_peek)

    def hide_after_peek(self) -> None:
        for i in range(CELL_COUNT):
            self.hide(i)
        self.lock_board = False
        self.set_status("Find matching colour pairs.")

    def on_tile_click(self, index: int) -> None:
        if self.lock_board or self.game_over:
            return
        if index in self.matched or index in self.revealed or self.reswap_job:
            return
        if index == self.first_pick:
            return

        self.reveal(index)

        if self.first_pick is None:
            self.first_pick = index
            self.set_status("Pick a second tile…")
            return

        self.moves += 1
        first = self.first_pick
        self.first_pick = None
        self.lock_board = True

        if self.deck[index] == self.deck[first]:
            self.root.after(200, lambda: self.resolve_match(index, first))
        else:
            self.set_status("Not a match.")
            self.reswap_job = self.root.after(FLIP_BACK_MS, lambda: self.resolve_mismatch(index, first))

    def resolve_match(self, a: int, b: int) -> None:
        self.mark_matched(a)
        self.mark_matched(b)
        self.pairs_found += 1
        self._update_hud()
        self.lock_board = False
        self.set_status("Match!")

        if self.pairs_found == PAIR_COUNT:
            self.finish_game()

    def resolve_mismatch(self, a: int, b: int) -> None:
        self.reswap_job = None
        self.hide(a)
        self.hide(b)
        self.lock_board = False
        self.set_status("Find matching colour pairs.")
        self._update_hud()

    def finish_game(self) -> None:
        self.game_over = True
        elapsed = int(time.time() - self.started_at)
        mins, secs = divmod(elapsed, 60)
        acc = round(100 * self.pairs_found / self.moves) if self.moves else 100
        self.set_status(f"Finished in {mins:02d}:{secs:02d} with {acc}% accuracy.")
        if self.win_banner is None:
            self.win_banner = tk.Label(
                self.progress.master,
                text="You win!",
                fg=COLORS["success"],
                bg=COLORS["panel"],
                font=self.title_font,
            )
            self.win_banner.grid(row=11, column=0, sticky="w", pady=(8, 0))

    def new_game(self) -> None:
        if self.win_banner is not None:
            self.win_banner.destroy()
            self.win_banner = None
        self.reset_game_state()


def main() -> None:
    root = tk.Tk()
    PalettePairsGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
