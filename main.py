"""Palette Pairs — pastel symbol memory game."""

from __future__ import annotations

import math
import random
import time
import tkinter as tk
from tkinter import font as tkfont

from PIL import Image, ImageDraw, ImageTk

GRID_COLUMNS = 8
GRID_ROWS = 8
CELL_COUNT = GRID_COLUMNS * GRID_ROWS
PAIR_COUNT = CELL_COUNT // 2
SYMBOL_COUNT = PAIR_COUNT
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

# Pastel tile backgrounds with slightly deeper accent shapes (32 pairs).
TILE_STYLES: list[tuple[str, str]] = [
    ("#fde8e8", "#e07a7a"),
    ("#fce7f3", "#db6b9a"),
    ("#fae8ff", "#b07cc6"),
    ("#ede9fe", "#8b7fd6"),
    ("#e0e7ff", "#6b7fd4"),
    ("#dbeafe", "#5b8fd4"),
    ("#cffafe", "#4a9fb8"),
    ("#ccfbf1", "#3d9e8e"),
    ("#d1fae5", "#3d9e6b"),
    ("#dcfce7", "#5a9e4a"),
    ("#ecfccb", "#7a9e3a"),
    ("#fef9c3", "#b89e3a"),
    ("#fef3c7", "#c48a4a"),
    ("#ffedd5", "#c47a5a"),
    ("#ffe4e6", "#c46a6a"),
    ("#f5f0e8", "#9a8a6a"),
    ("#f0ebe3", "#8a7a6a"),
    ("#e8f4f8", "#5a8a9a"),
    ("#e8f0f8", "#5a7a9a"),
    ("#f0e8f4", "#7a5a9a"),
    ("#f4e8f0", "#9a5a7a"),
    ("#e8f8f0", "#4a8a6a"),
    ("#f8f0e8", "#9a7a5a"),
    ("#f0f4e8", "#7a9a5a"),
    ("#e8f0eb", "#5a8a7a"),
    ("#f0e8eb", "#8a5a7a"),
    ("#ebe8f4", "#6a5a9a"),
    ("#e8ebf4", "#5a6a9a"),
    ("#f4ebe8", "#9a6a5a"),
    ("#ebf4e8", "#6a9a5a"),
    ("#e8f4eb", "#5a9a7a"),
    ("#f4e8eb", "#9a5a8a"),
]

SHAPE_NAMES = (
    "circle",
    "ring",
    "square",
    "square_outline",
    "rounded_square",
    "triangle_up",
    "triangle_down",
    "diamond",
    "hexagon",
    "star5",
    "plus",
    "cross",
    "pill_h",
    "pill_v",
    "semicircle_up",
    "semicircle_down",
    "double_dot",
    "triple_dot",
    "chevron_up",
    "chevron_down",
    "heart",
    "star4",
    "thick_cross",
    "grid2",
    "center_dot",
    "corner_dot",
    "slash",
    "backslash",
    "pie",
    "pentagon",
    "octagon",
    "bowtie",
)


def _regular_polygon(cx: int, cy: int, r: int, sides: int, rotation_deg: float = -90) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    for i in range(sides):
        angle = math.radians(rotation_deg + i * (360 / sides))
        points.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
    return points


def _inset(size: int, ratio: float = 0.22) -> tuple[int, int, int, int]:
    m = int(size * ratio)
    return m, m, size - m, size - m


def draw_symbol(draw: ImageDraw.ImageDraw, shape: str, size: int, fg: str, bg: str) -> None:
    cx, cy = size // 2, size // 2
    r = size // 4
    x0, y0, x1, y1 = _inset(size)

    if shape == "circle":
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fg)
    elif shape == "ring":
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fg, width=max(3, size // 14))
    elif shape == "square":
        draw.rectangle((cx - r, cy - r, cx + r, cy + r), fill=fg)
    elif shape == "square_outline":
        draw.rectangle((cx - r, cy - r, cx + r, cy + r), outline=fg, width=max(3, size // 14))
    elif shape == "rounded_square":
        draw.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), radius=r // 3, fill=fg)
    elif shape == "triangle_up":
        draw.polygon([(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)], fill=fg)
    elif shape == "triangle_down":
        draw.polygon([(cx, cy + r), (cx - r, cy - r), (cx + r, cy - r)], fill=fg)
    elif shape == "diamond":
        draw.polygon([(cx, y0), (x1, cy), (cx, y1), (x0, cy)], fill=fg)
    elif shape == "hexagon":
        draw.polygon(_regular_polygon(cx, cy, r, 6), fill=fg)
    elif shape == "star5":
        outer = _regular_polygon(cx, cy, r, 5, -90)
        inner_r = int(r * 0.45)
        inner = _regular_polygon(cx, cy, inner_r, 5, -90 + 36)
        star: list[tuple[int, int]] = []
        for i in range(5):
            star.append(outer[i])
            star.append(inner[i])
        draw.polygon(star, fill=fg)
    elif shape == "plus":
        t = max(3, size // 10)
        draw.rectangle((cx - t, cy - r, cx + t, cy + r), fill=fg)
        draw.rectangle((cx - r, cy - t, cx + r, cy + t), fill=fg)
    elif shape == "cross":
        t = max(3, size // 12)
        draw.line((x0, y0, x1, y1), fill=fg, width=t)
        draw.line((x1, y0, x0, y1), fill=fg, width=t)
    elif shape == "pill_h":
        draw.rounded_rectangle((x0, cy - r // 2, x1, cy + r // 2), radius=r // 2, fill=fg)
    elif shape == "pill_v":
        draw.rounded_rectangle((cx - r // 2, y0, cx + r // 2, y1), radius=r // 2, fill=fg)
    elif shape == "semicircle_up":
        draw.pieslice((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=fg)
    elif shape == "semicircle_down":
        draw.pieslice((cx - r, cy - r, cx + r, cy + r), 0, 180, fill=fg)
    elif shape == "double_dot":
        d = r // 2
        gap = r // 2
        draw.ellipse((cx - gap - d, cy - d, cx - gap + d, cy + d), fill=fg)
        draw.ellipse((cx + gap - d, cy - d, cx + gap + d, cy + d), fill=fg)
    elif shape == "triple_dot":
        d = max(3, size // 14)
        for i, (dx, dy) in enumerate(((-r // 2, -r // 3), (0, r // 3), (r // 2, -r // 3))):
            draw.ellipse((cx + dx - d, cy + dy - d, cx + dx + d, cy + dy + d), fill=fg)
    elif shape == "chevron_up":
        draw.polygon([(cx, cy - r), (cx - r, cy + r // 2), (cx + r, cy + r // 2)], fill=fg)
    elif shape == "chevron_down":
        draw.polygon([(cx, cy + r), (cx - r, cy - r // 2), (cx + r, cy - r // 2)], fill=fg)
    elif shape == "heart":
        draw.ellipse((cx - r, cy - r // 2, cx, cy + r // 3), fill=fg)
        draw.ellipse((cx, cy - r // 2, cx + r, cy + r // 3), fill=fg)
        draw.polygon([(cx - r, cy), (cx + r, cy), (cx, cy + r)], fill=fg)
    elif shape == "star4":
        draw.polygon(
            [(cx, cy - r), (cx + r // 2, cy), (cx, cy + r), (cx - r // 2, cy)],
            fill=fg,
        )
    elif shape == "thick_cross":
        t = max(4, size // 8)
        draw.rectangle((cx - t, cy - r, cx + t, cy + r), fill=fg)
        draw.rectangle((cx - r, cy - t, cx + r, cy + t), fill=fg)
    elif shape == "grid2":
        g = r // 2
        for ox, oy in ((-g, -g), (g, -g), (-g, g), (g, g)):
            draw.rectangle((cx + ox - g // 2, cy + oy - g // 2, cx + ox + g // 2, cy + oy + g // 2), fill=fg)
    elif shape == "center_dot":
        d = r
        draw.ellipse((cx - d, cy - d, cx + d, cy + d), fill=fg)
    elif shape == "corner_dot":
        d = r // 2
        draw.ellipse((x1 - d * 2, y1 - d * 2, x1, y1), fill=fg)
    elif shape == "slash":
        t = max(3, size // 10)
        draw.line((x0, y1, x1, y0), fill=fg, width=t)
    elif shape == "backslash":
        t = max(3, size // 10)
        draw.line((x0, y0, x1, y1), fill=fg, width=t)
    elif shape == "pie":
        draw.pieslice((cx - r, cy - r, cx + r, cy + r), 30, 300, fill=fg)
    elif shape == "pentagon":
        draw.polygon(_regular_polygon(cx, cy, r, 5), fill=fg)
    elif shape == "octagon":
        draw.polygon(_regular_polygon(cx, cy, r, 8), fill=fg)
    elif shape == "bowtie":
        draw.polygon([(cx - r, cy - r), (cx, cy), (cx - r, cy + r), (cx, cy)], fill=fg)
        draw.polygon([(cx + r, cy - r), (cx, cy), (cx + r, cy + r), (cx, cy)], fill=fg)
    else:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fg)


def render_symbol_tile(symbol_id: int, size: int = DISPLAY_TILE) -> Image.Image:
    bg, fg = TILE_STYLES[symbol_id % len(TILE_STYLES)]
    shape = SHAPE_NAMES[symbol_id % len(SHAPE_NAMES)]
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    margin = max(3, size // 14)
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=size // 8,
        fill=bg,
        outline=fg,
        width=2,
    )
    draw_symbol(draw, shape, size, fg, bg)
    return img


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


def build_deck() -> list[int]:
    symbols = list(range(SYMBOL_COUNT))
    deck = symbols * 2
    random.shuffle(deck)
    return deck


class PalettePairsGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Palette Pairs")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.back_photo = ImageTk.PhotoImage(make_card_back())
        self.photo_cache: dict[int, ImageTk.PhotoImage] = {}

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
        self.reswap_job = None
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

    def tile_photo(self, symbol_id: int) -> ImageTk.PhotoImage:
        if symbol_id not in self.photo_cache:
            self.photo_cache[symbol_id] = ImageTk.PhotoImage(render_symbol_tile(symbol_id))
        return self.photo_cache[symbol_id]

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
            text="Match the pastel symbols",
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
        self.set_status("Memorise the symbols…")
        for i in range(CELL_COUNT):
            self.reveal(i)
        self.root.after(PEEK_MS, self.hide_after_peek)

    def hide_after_peek(self) -> None:
        for i in range(CELL_COUNT):
            self.hide(i)
        self.lock_board = False
        self.set_status("Find matching symbol pairs.")

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
        self.set_status("Find matching symbol pairs.")
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
