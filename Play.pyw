"""Start the OoT remake (Hookshot) with the randomizer's mod folder and its own save folder. Other mods in Hookshot's
own mods folder stay out of it, and your normal saves are left alone."""
import os, subprocess, sys
import tkinter as tk
from tkinter import filedialog, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools'))
import paths  # noqa: E402


def ask_game_dir():
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo('OoT Remake Randomizer', 'Pick your Hookshot game folder (the one with bin, romfs and image.bin).')
    d = filedialog.askdirectory(title='Hookshot game folder')
    root.destroy()
    return d


game = paths.game_dir()
if not paths.is_game_dir(game):
    game = ask_game_dir()
    if not paths.is_game_dir(game):
        sys.exit('not a Hookshot game folder')
    paths.set_game_dir(game)
os.makedirs(paths.MODS, exist_ok=True)
os.makedirs(paths.SAVES, exist_ok=True)
env = dict(os.environ, HOS_MODS=paths.MODS)
subprocess.Popen([os.path.join(game, 'bin', 'hookshot.exe'), os.path.join(game, 'image.bin'),
                  '--romfs', os.path.join(game, 'romfs'), '--user', paths.SAVES], cwd=game, env=env)
