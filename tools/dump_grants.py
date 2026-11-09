"""Every item grant in the remake's event flows: a sub-flow call (GetPouchContent*, *GetInEvent*, ...) whose parameter
ActorName names the item. usage: python -I dump_grants.py <romfs> <out.json>"""
import sys, os, glob, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402,F401
import zs, evfl
romfs, out = sys.argv[1:3]
rows, bad, calls = [], [], collections.Counter()
for f in sorted(glob.glob(os.path.join(romfs, 'Event', 'EventFlow', '*.bfevfl.zs'))):
    try:
        ef = evfl.EventFlow(); ef.read(zs.decompress_any(romfs, open(f, 'rb').read()))
    except Exception as e:
        bad.append((os.path.basename(f), str(e)[:80])); continue
    if not ef.flowchart: continue
    for e in ef.flowchart.events:
        d = e.data; ps = getattr(d, 'params', None); ps = ps.data if ps else {}
        an = ps.get('ActorName')
        if isinstance(d, evfl.event.SubFlowEvent) and isinstance(an, str) and an.startswith(('Item_', 'Armor_', 'Obj_Heart', 'Weapon_')):
            calls[f'{d.res_flowchart_name}::{d.entry_point_name}'] += 1
            rows.append({'file': os.path.basename(f), 'event': e.name, 'call': f'{d.res_flowchart_name}::{d.entry_point_name}', 'item': an})
json.dump(rows, open(out, 'w'), indent=0)
print(len(rows), 'grants;', len(bad), 'unreadable files'); print(calls.most_common(20)); print(bad[:5])
