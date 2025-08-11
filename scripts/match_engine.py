# scripts/match_engine.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from boxing.engine import MatchEngine
from boxing.models import Boxer

ROUNDS = 12
ROUND_COLS = [f"Round{i}" for i in range(1, ROUNDS + 1)] + ["Total"]


# ------------------------------ Boxer helpers ------------------------------ #
def make_boxer(name: str, base: int) -> Boxer:
    """Create a 22-field Boxer with all ratings = base."""
    fields: dict[str, int] = {
        # Fundamentals
        "jab": base, "straight": base, "lead_hook": base, "hook": base,
        "lead_uppercut": base, "uppercut": base, "blocking": base, "accuracy": base,
        # Boxing IQ
        "anticipation": base, "composure": base, "positioning": base, "decision": base,
        "aggression": base, "focus": base, "workrate": base, "planning": base,
        # Athleticism
        "power": base, "hand_speed": base, "foot_speed": base,
        "reflexes": base, "stamina": base, "agility": base,
    }
    return Boxer(name=name, **fields)


def round_points(rsum: dict) -> tuple[int, int]:
    """Compute 10-Point-Must points for one round from telemetry (landed counts)."""
    red_landed = sum(rsum["red"]["landed"].values())
    blue_landed = sum(rsum["blue"]["landed"].values())
    if red_landed > blue_landed:
        return 10, 9
    if blue_landed > red_landed:
        return 9, 10
    return 10, 10


# ---------------------------------- GUI ----------------------------------- #
class MatchEngineApp(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=10)
        master.title("Main Event Mogul — Match Engine")
        master.geometry("980x380")
        master.minsize(820, 360)
        self.grid(sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self._build_controls()
        self._build_table()
        self._build_footer()

    # ---- Controls row ----
    def _build_controls(self):
        frm = ttk.Frame(self)
        frm.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frm.columnconfigure(6, weight=1)  # spacer

        ttk.Label(frm, text="Seed").grid(row=0, column=0, padx=(0, 6))
        self.seed_var = tk.IntVar(value=42)
        ttk.Entry(frm, textvariable=self.seed_var, width=7).grid(row=0, column=1, padx=(0, 12))

        ttk.Label(frm, text="Red base (1–20)").grid(row=0, column=2, padx=(0, 6))
        self.red_base = tk.IntVar(value=12)
        ttk.Entry(frm, textvariable=self.red_base, width=6).grid(row=0, column=3, padx=(0, 12))

        ttk.Label(frm, text="Blue base (1–20)").grid(row=0, column=4, padx=(0, 6))
        self.blue_base = tk.IntVar(value=12)
        ttk.Entry(frm, textvariable=self.blue_base, width=6).grid(row=0, column=5, padx=(0, 12))

        ttk.Button(frm, text="Simulate", command=self.run_sim).grid(row=0, column=7, padx=(6, 0))
        ttk.Button(frm, text="Transcript…", command=self.show_transcript).grid(row=0, column=8, padx=(12, 0))

        self.result_var = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.result_var, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=9, padx=12, sticky="w"
        )

    # ---- Scoreboard table ----
    def _build_table(self):
        cols = ["Name"] + ROUND_COLS
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=6)
        self.tree.grid(row=1, column=0, sticky="nsew")

        # layout stretch
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # headings
        self.tree.heading("Name", text="Name")
        self.tree.column("Name", width=120, anchor="w")
        for c in ROUND_COLS:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=70, anchor="center")

        # rows
        self.tree.insert("", "end", iid="Red", values=["Red"] + [""] * (len(ROUND_COLS)))
        self.tree.insert("", "end", iid="Blue", values=["Blue"] + [""] * (len(ROUND_COLS)))

        # style
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

    def _build_footer(self):
        self.footer = ttk.Label(self, text="", anchor="w")
        self.footer.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    # ---- Simulate and fill UI ----
    def run_sim(self):
        try:
            seed = int(self.seed_var.get())
            rbase = max(1, min(20, int(self.red_base.get())))
            bbase = max(1, min(20, int(self.blue_base.get())))
        except ValueError:
            messagebox.showerror("Input error", "Seed and base ratings must be integers (1–20).")
            return

        red = make_boxer("Red", rbase)
        blue = make_boxer("Blue", bbase)

        fight = MatchEngine(red, blue, seed=seed).simulate()
        self._populate_scoreboard(fight)
        self._last_fight = fight  # keep for transcript window

    def _populate_scoreboard(self, fight: dict):
        # collect per-round points
        red_pts, blue_pts = [], []
        for r in fight["rounds"]:
            rp, bp = round_points(r)
            red_pts.append(rp)
            blue_pts.append(bp)

        # fill rows
        for i, (rp, bp) in enumerate(zip(red_pts, blue_pts), start=1):
            col = f"Round{i}"
            self.tree.set("Red", col, str(rp))
            self.tree.set("Blue", col, str(bp))

        self.tree.set("Red", "Total", str(sum(red_pts)))
        self.tree.set("Blue", "Total", str(sum(blue_pts)))

        self.result_var.set(f"Winner: {fight['winner'] or 'Draw'}")
        self.footer.config(text=f"Scores from engine: {fight['scores']} — seed={self.seed_var.get()}")

    def show_transcript(self):
        fight = getattr(self, "_last_fight", None)
        if not fight:
            messagebox.showinfo("Transcript", "Run a simulation first.")
            return
        win = tk.Toplevel(self)
        win.title("Transcript")
        win.geometry("700x420")
        txt = tk.Text(win, wrap="word")
        scr = ttk.Scrollbar(win, command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        txt.pack(side="left", fill="both", expand=True)
        scr.pack(side="right", fill="y")
        header = f"Winner: {fight['winner'] or 'Draw'}    Scores: {fight['scores']}\n\n"
        txt.insert("1.0", header + "\n".join(fight["events"]))
        txt.config(state="disabled")


def main():
    root = tk.Tk()
    MatchEngineApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
