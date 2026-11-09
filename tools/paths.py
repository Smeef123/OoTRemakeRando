"""Where things are. The game folder (your Hookshot build of the OoT remake) is asked for once and kept in config.json."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'config.json')
sys.path.insert(0, os.path.join(ROOT, 'tools', 'lib'))  # byml / zs / restbl readers


def game_dir():
    """The Hookshot game folder: the one holding bin\\hookshot.exe, image.bin and romfs."""
    try:
        return json.load(open(CONFIG, encoding='utf-8'))['game']
    except Exception:
        return ''


def set_game_dir(path):
    cfg = {}
    if os.path.exists(CONFIG):
        try:
            cfg = json.load(open(CONFIG, encoding='utf-8'))
        except Exception:
            cfg = {}
    cfg['game'] = path
    json.dump(cfg, open(CONFIG, 'w', encoding='utf-8'), indent=1)


def is_game_dir(path):
    return bool(path) and all(os.path.exists(os.path.join(path, p)) for p in ('image.bin', 'romfs', os.path.join('bin', 'hookshot.exe')))


ROMFS = lambda: os.path.join(game_dir(), 'romfs')  # noqa: E731
GENERATOR = os.path.join(ROOT, 'build', 'sohrando.exe')
LANG = os.path.join(ROOT, 'build', 'lang')           # SoH's English text, copied in by the build
OPTIONS = os.path.join(ROOT, 'build', 'soh_options.json')  # SoH's settings menu, written by the build
MODS = os.path.join(ROOT, 'mods')                    # the folder Play.pyw hands to the game
SAVES = os.path.join(ROOT, 'saves')                  # randomizer saves, apart from your normal ones
SEEDS = os.path.join(ROOT, 'seeds')
