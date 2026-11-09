"""Last setup step: remember the Hookshot game folder and put the two shortcuts on the desktop."""
import os, subprocess, sys
import tkinter as tk
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

if not os.path.exists(paths.GENERATOR):
    sys.exit('build/sohrando.exe is missing: the build did not finish')
game = paths.game_dir()
while not paths.is_game_dir(game):
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo('OoT Remake Randomizer', 'Pick your Hookshot game folder (the one with bin, romfs and image.bin).')
    game = filedialog.askdirectory(title='Hookshot game folder'); root.destroy()
    if not game:
        sys.exit('no game folder picked')
paths.set_game_dir(game)
print('game folder:', game)

pyw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
icon = os.path.join(game, 'bin', 'hookshot.exe') + ',0'
ps = []
for name, script in (('OoT Remake Randomizer', 'Randomizer.pyw'), ('OoT Remake (Randomizer)', 'Play.pyw')):
    ps.append(f"$s=$ws.CreateShortcut((Join-Path $d '{name}.lnk')); $s.TargetPath='{pyw}'; "
              f"$s.Arguments='\"{os.path.join(paths.ROOT, script)}\"'; $s.WorkingDirectory='{paths.ROOT}'; "
              f"$s.IconLocation='{icon}'; $s.Save()")
subprocess.check_call(['powershell', '-NoProfile', '-Command',
                       "$ws=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); " + '; '.join(ps)])
print('desktop shortcuts made')
