"""Dump every remake map placement that holds an item (Drop__DropActor) to JSON.
usage: python -I dump_checks.py <remake romfs> <out.json>"""
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import paths  # noqa: E402,F401
import byml, zs  # noqa: E402
romfs, out = sys.argv[1], sys.argv[2]
rows = []
def plain(v):
    if isinstance(v, dict): return {k: plain(x) for k, x in v.items()}
    if isinstance(v, list): return [plain(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None: return v
    return int(v) if hasattr(v, '__int__') else str(v)
for p in sorted(glob.glob(os.path.join(romfs, 'Banc', '*', '*.bcett.byml.zs'))):
    d = byml.load(zs.decompress_any(romfs, open(p, 'rb').read()))
    rel = os.path.relpath(p, romfs).replace(os.sep, '/')
    for i, a in enumerate(d.get('Actors', []) or []):
        dy = a.get('Dynamic') or {}
        if not isinstance(dy, dict): continue
        if 'Drop__DropActor' in dy or 'Drop__DropTable' in dy:
            rows.append({'file': rel, 'index': i, 'hash': plain(a.get('Hash')), 'gyaml': a.get('Gyaml'),
                         'pos': plain(a.get('Translate')), 'dynamic': plain(dy)})
json.dump(rows, open(out, 'w'), indent=1)
print(len(rows), 'rows')
