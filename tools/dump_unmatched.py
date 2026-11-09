"""List, per area, the SoH chest/freestanding checks and remake spots not yet in data/check_map.json.
usage: python -I dump_unmatched.py <repo> > data/unmatched.txt"""
import json, os, re, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import match_checks as M  # noqa (runs the matcher; reuses its tables)
root = sys.argv[1]
region = {}
for p in glob.glob(os.path.join(root, 'soh-src/soh/soh/Enhancements/randomizer/location_access/**/*.cpp'), recursive=True):
    cur = None
    for line in open(p, encoding='utf-8'):
        m = re.search(r'areaTable\[RR_\w+\]\s*=\s*Region\("([^"]+)"', line)
        if m: cur = m.group(1)
        for rc in re.findall(r'LOCATION\((RC_\w+)', line):
            region.setdefault(rc, cur)
cmap = json.load(open(os.path.join(root, 'data/check_map.json')))
used = {(v['folder'], int(v['hash'])) for v in cmap.values() if 'hash' in v}
by = collections.defaultdict(lambda: ([], []))
for a in M.soh:
    if a['rc'] in cmap: continue
    rg = [x for x in a['args'] if x.startswith('RG_')]
    by[M.area_of(a['rc'])][0].append(f"  S {a['rc'][3:]:48} {rg[-1][3:] if rg else '':28} [{region.get(a['rc'])}]")
for (f, h), x in M.remake.items():
    if (f, int(h)) in used: continue
    dy = x['dynamic']; ev = dy.get('GetEventName') or dy.get('RequestEventName') or ''
    kind = x['file'].rsplit('/', 1)[1].replace(f + '_', '').replace('.bcett.byml.zs', '')
    by[f][1].append(f"  R {h:<21} {x['gyaml'][:24]:24} r{dy.get('DefaultDungeonRoomIndex','-')!s:3} {str([round(v) for v in x['pos']]):18} {dy['Drop__DropActor']:26} {kind[:16]:16} {ev[:40]}")
for f in sorted(by, key=str):
    s, r = by[f]
    print(f'== {f}: {len(s)} SoH, {len(r)} remake')
    print('\n'.join(sorted(s))); print('\n'.join(sorted(r, key=lambda l: l.split()[3])))
