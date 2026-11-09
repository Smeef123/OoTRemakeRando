"""OoT remake randomizer (Ship of Harkinian's generator, applied to the Switch 2 remake running in Hookshot).

usage: python -I rando.py <settings.json> [--seed TEXT] [--mods DIR] [--romfs DIR]   (game folder: config.json, set by Setup)

  settings.json  Ship of Harkinian randomizer settings, as SoH's own CVars ("gRandoSettings.<Name>": value).
                 Anything left out keeps SoH's default.
  --seed         seed text (blank: random, like SoH)
  --mods         mods folder to install into (default: mods/, the one Play.pyw uses); the seed becomes mod "oot-rando"
  --romfs        the remake's RomFS (default: <game folder>/romfs)

Writes seeds/<seed>/: SoH's spoiler log (Randomizer/<hash>.json), placement.json, install_report.json."""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(HERE, 'tools'))
import paths  # noqa: E402
from remake_settings import FORCED, ALLOWED  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('settings')
ap.add_argument('--seed', default='')
ap.add_argument('--mods', default=os.path.join(HERE, 'mods'))
ap.add_argument('--romfs', default=paths.ROMFS())
a = ap.parse_args()

cfg = json.load(open(a.settings, encoding='utf-8'))
for k, v in FORCED.items():
    if cfg.get(k, v) != v:
        print(f'note: {k} forced to {v} (not supported in the remake yet)')
    cfg[k] = v
for k, ok in ALLOWED.items():
    if k in cfg and cfg[k] not in ok:
        print(f'note: {k} = {cfg[k]} not supported in the remake, using {ok[0] if 2 not in ok else 2}')
        cfg[k] = ok[0] if 2 not in ok else 2
os.makedirs(os.path.join(HERE, 'seeds'), exist_ok=True)
tmp_cfg = os.path.join(HERE, 'seeds', '_settings.json')
json.dump(cfg, open(tmp_cfg, 'w'), indent=1)

seed = a.seed
out = os.path.join(HERE, 'seeds', seed or '_new')
if os.path.isdir(out):  # a fresh folder per run, so no file from an older run of this seed is picked up
    import shutil
    shutil.rmtree(out)
r = subprocess.run([os.path.join(HERE, 'build', 'sohrando.exe'), tmp_cfg, out, seed,
                    paths.LANG,
                    os.path.join(HERE, 'data', 'check_map.json')], capture_output=True, text=True)
tail = [l for l in r.stdout.splitlines() if l.startswith(('ok', 'remake'))]
print('\n'.join(tail))
if r.returncode != 0:
    print(r.stdout[-3000:], r.stderr[-3000:])
    sys.exit('generation failed')
if not seed:  # name the folder after the seed SoH picked
    seed = json.load(open(os.path.join(out, 'placement.json')))['seed']
    final = os.path.join(HERE, 'seeds', seed)
    if os.path.exists(final):
        import shutil
        shutil.rmtree(final)
    os.replace(out, final)
    out = final
json.dump(cfg, open(os.path.join(out, 'settings.json'), 'w'), indent=1)
r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'tools', 'install_seed.py'), HERE, out, a.romfs, a.mods],
                   capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[-2000:])
if r.returncode != 0:
    sys.exit('install failed')
print(f'seed {seed}: spoiler log and reports in {out}')
