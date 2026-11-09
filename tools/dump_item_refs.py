"""Every event-flow step whose parameters name an item actor (any event type, any parameter name).
usage: python -I dump_item_refs.py <romfs> <out.json>"""
import sys, os, glob, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402,F401
import zs, evfl  # noqa: E402
romfs, out = sys.argv[1:3]
ITEM = ('Item_', 'Obj_Heart', 'Armor_', 'Obj_Rupee', 'TBox_', 'Weapon_', 'Obj_MiniGame')
rows = []
for f in sorted(glob.glob(os.path.join(romfs, 'Event', 'EventFlow', '*.bfevfl.zs'))):
    ef = evfl.EventFlow(); ef.read(zs.decompress_any(romfs, open(f, 'rb').read()))
    if not ef.flowchart: continue
    for e in ef.flowchart.events:
        d = e.data; ps = getattr(d, 'params', None); ps = ps.data if ps else {}
        for k, v in ps.items():
            if isinstance(v, str) and v.startswith(ITEM):
                act = getattr(d, 'actor', None); aa = getattr(d, 'actor_action', None) or getattr(d, 'actor_query', None)
                how = (f'{d.res_flowchart_name}::{d.entry_point_name}' if isinstance(d, evfl.event.SubFlowEvent)
                       else f'{act.v.identifier.name}.{aa.v.v}' if act and aa else type(d).__name__)
                rows.append({'file': os.path.basename(f)[:-10], 'event': e.name, 'how': how, 'param': k, 'item': v})
json.dump(rows, open(out, 'w'), indent=0)
c = collections.Counter((r['how'], r['param']) for r in rows)
print(len(rows)); [print(v, k) for k, v in c.most_common(30)]
