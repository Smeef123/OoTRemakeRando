"""Write a generated seed into the remake as a Hookshot RomFS mod.

usage: python -I install_seed.py <repo dir> <seed out dir> <remake romfs> <mods dir> [mod name]

For every SoH check in data/check_map.json, the chest / freestanding spot it matches in the remake's map files
(romfs/Banc/<area>/*.bcett.byml.zs, every child/adult/static/dynamic copy with that actor hash) gets the seed's
item as its Drop__DropActor. Progressive items are handed out in the spoiler log's playthrough order (first one
found gets level 1). The item-get cutscene event of a changed chest is removed so the old item's scene does not
play (or hand out the old item). Changed files go to <mods dir>/<mod name>/romfs with a resource size table that
covers their new sizes. Prints what changed; writes <seed out dir>/install_report.json."""
import glob, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from remake_items import CHEST, PROGRESSIVE

repo, seed_dir, romfs, mods = sys.argv[1:5]
mod_name = sys.argv[5] if len(sys.argv) > 5 else 'oot-rando'
import paths  # noqa: E402,F401  (puts tools/lib on the path)
import byml, zs, restbl  # noqa: E402

cmap = json.load(open(os.path.join(repo, 'data', 'check_map.json')))
place = json.load(open(os.path.join(seed_dir, 'placement.json')))
spoiler = json.load(open(max(glob.glob(os.path.join(seed_dir, 'Randomizer', '*.json')), key=os.path.getmtime), encoding='utf-8'))

# playthrough order of checks (sphere by sphere), for progressive items
order = {}
for sphere in spoiler.get('playthrough', {}).values():
    for check in sphere:
        order.setdefault(check, len(order))

rows = [r for r in place['placements'] if r['rc_enum'] in cmap]
rows.sort(key=lambda r: order.get(r['check'], 10 ** 6))
level = collections.Counter()
want = {}  # (folder, hash) -> (actor, row)
events = []  # (event_map entry, actor, row)
problems = []
for r in rows:
    rg = r['rg_enum']
    if rg in PROGRESSIVE:
        lv = level[rg]
        level[rg] += 1
        actor = PROGRESSIVE[rg][min(lv, len(PROGRESSIVE[rg]) - 1)]
    else:
        actor = CHEST.get(rg)
    if not actor:
        problems.append(f"{r['check']}: no remake actor for {rg} ({r['item']})")
        continue
    m = cmap[r['rc_enum']]
    if m.get('mode') == 'event':
        events.append((m, actor, r))
    else:
        want[(m['folder'], int(m['hash']))] = (actor, r)

KEEP_EVENTS = ('NaviChatOff',)
# chest-only drop actors -> the free-standing pickup used when an item replaces a placed heart piece/container
# (guess: TotK-style placed pickups; Obj_* rupees/ammo are placed freely in the remake's own maps)
FREESTANDING = {'TBox_Rupee_Green': 'Obj_Rupee_Green', 'TBox_Rupee_Blue': 'Obj_Rupee_Blue',
                'TBox_Rupee_Red': 'Obj_Rupee_Red', 'TBox_Rupee_Purple': 'Obj_Rupee_Purple',
                'TBox_Rupee_Gold': 'Obj_Rupee_Gold', 'TBox_ArrowBundle_Small': 'Obj_ArrowBundle_Small',
                'TBox_ArrowBundle_Medium': 'Obj_ArrowBundle_Medium', 'TBox_ArrowBundle_Large': 'Obj_ArrowBundle_Large',
                'TBox_Shield_Deku': 'Weapon_Shield_Deku', 'TBox_Shield_Hylian': 'Weapon_Shield_Hylian',
                'TBox_DekuNutBundle': 'Item_DekuNut', 'TBox_DekuSeedBundle': 'Item_DekuSeed',
                'Tbox_MagicJar_Large': 'Obj_MagicJar_Large'}
changed_files, report = {}, []
by_folder = collections.defaultdict(dict)
for (folder, h), v in want.items():
    by_folder[folder][h] = v
for folder, items in by_folder.items():
    for path in sorted(glob.glob(os.path.join(romfs, 'Banc', folder, '*.bcett.byml.zs'))):
        raw = zs.decompress_any(romfs, open(path, 'rb').read())
        data = byml.load(raw)
        hit = 0
        for a in data.get('Actors', []) or []:
            h = a.get('Hash')
            if h is None or int(h) not in items:
                continue
            actor, r = items[int(h)]
            m = cmap[r['rc_enum']]
            if m.get('mode') == 'actor':  # a placed pickup (heart piece / container): swap the object itself
                actor = FREESTANDING.get(actor, actor)
                old = a.get('Gyaml')
                if old != actor:
                    a['Gyaml'] = actor
                    hit += 1
            else:
                dy = a['Dynamic']
                old = dy.get('Drop__DropActor')
                if old != actor:
                    dy['Drop__DropActor'] = actor
                    dy.pop('DropViewActor', None)  # minigame chests show their prize; the old one would be wrong
                    ev = dy.get('GetEventName')
                    if ev and not m.get('keep_event') and not any(k in ev for k in KEEP_EVENTS):
                        del dy['GetEventName']
                    hit += 1
            report.append({'check': r['check'], 'item': r['item'], 'actor': actor, 'was': old,
                           'file': os.path.relpath(path, romfs).replace(os.sep, '/')})
        if hit:
            out = byml.dump(data, byml.version_of(raw), byml.is_big_endian(raw))
            changed_files[os.path.relpath(path, romfs).replace(os.sep, '/')] = out

# event flows: the grant's ActorName parameter becomes the seed's item
import io, evfl  # noqa: E402
# parameters through which a step hands Link an item: the give sub-flows (ActorName), NPC hand-overs (ReveiveItem, the
# game's spelling), reward scenes (TakenRewardActor), and the direct pouch add (Actor, when Num > 0)
GRANT_KEYS = ('ActorName', 'ReveiveItem', 'TakenRewardActor', 'Actor')
by_flow = collections.defaultdict(list)
for m, actor, r in events:
    for f in m['files']:
        by_flow[f].append((m, FREESTANDING.get(actor, actor), r))
for flow, lst in by_flow.items():
    rel = f'Event/EventFlow/{flow}.bfevfl.zs'
    raw = zs.decompress_any(romfs, open(os.path.join(romfs, rel), 'rb').read())
    ef = evfl.EventFlow(); ef.read(raw)
    hit = 0
    for e in ef.flowchart.events:
        d = e.data
        ps = getattr(d, 'params', None)
        if not ps: continue
        act = getattr(d, 'actor', None); aa = getattr(d, 'actor_action', None)
        action = f'{act.v.identifier.name}.{aa.v.v}' if act and aa else ''
        if getattr(d, 'actor_query', None) is not None and not aa: continue  # a question ("has the item?"), not a give
        for key in GRANT_KEYS:
            an = ps.data.get(key)
            if not isinstance(an, str): continue
            if key == 'Actor' and not (action.endswith('AddOrRemovePouchContent') and ps.data.get('Num', 1) > 0): continue
            for m, actor, r in lst:
                if an in m['items'] and (not m.get('events') or e.name in m['events']):
                    ps.data[key] = actor
                    hit += 1
                    report.append({'check': r['check'], 'item': r['item'], 'actor': actor, 'was': an, 'file': rel})
                    break
    if not hit:
        problems.append(f'{rel}: no grant of {[x[0]["items"] for x in lst]} found')
        continue
    b = io.BytesIO(); ef.write(b)
    changed_files[rel] = b.getvalue()

# gossip stone hints: SoH's stone texts go into the remake's GOSSIP_<AREA>_NN messages, paired in order per area
import msbt  # noqa: E402  (tools/msbt.py)
STONE_AREA = [('DMC', 'DEATH_MOUNTAIN_CRATER'), ('DMT', 'DEATH_MOUNTAIN_TRAIL'), ('Desert Colossus', 'DESERT_COLOSSUS'),
              ("Dodongo's Cavern", 'DODONGO_CAVERN'), ('Gerudo Valley', 'GERUDO_VALLEY'), ('GC', 'GORON_CITY'),
              ('Graveyard', 'GRAVEYARD'), ('HC', 'HYRULE_CASTLE'), ('HF', 'HYRULE_FIELD'), ('Market', 'HYRULE_MARKET'),
              ('Kak', 'KAKARIKO_VILLAGE'), ('KF', 'KOKIRI_FOREST'), ('LH', 'LAKE_HYLIA'), ('LW', 'LOST_WOOD'),
              ('SFM', 'SACRED_FOREST_MEADOW'), ('ZD', 'ZORA_DOMAIN'), ('ZF', 'ZORA_FOUNTAIN'), ('ZR', 'ZORA_RIVER')]
hints = spoiler.get('Gossip Stone Hints', {})
if hints:
    import textwrap
    mals_rel = 'Mals/USen.Product.110.sarc.zs'
    sarc = zs.sarc_files(zs.decompress_any(romfs, open(os.path.join(romfs, mals_rel), 'rb').read()))
    mname = 'EventFlowMsg/GossipStone.msbt'
    msg = msbt.load(sarc[mname])
    idx = {l: i for i, l in msg['labels'].items()}
    def tag_prefix(t):  # leading control tags (speaker, colour): 0x0E, group u16, type u16, size u16, params
        b = t.encode(msg['enc'], 'surrogateescape')
        i = 0
        while i < len(b) and b[i] == 0x0E:
            i += 7 + (b[i + 5] | (b[i + 6] << 8))
        return b[:i].decode(msg['enc'], 'surrogateescape')
    placed = 0
    for pre, area in STONE_AREA:
        stones = sorted(n for n in hints if n.startswith(pre + ' '))
        labels = sorted(l for l in idx if l.startswith(f'GOSSIP_{area}_'))
        for stone, label in zip(stones, labels):
            text = '\n'.join(textwrap.fill(p, 44) for p in hints[stone]['message'].split('\n'))
            i = idx[label]
            msg['texts'][i] = tag_prefix(msg['texts'][i]) + text + '\x00'
            report.append({'check': stone, 'item': 'hint', 'actor': label, 'was': '', 'file': mals_rel})
            placed += 1
    sarc[mname] = msbt.dump(msg)
    changed_files[mals_rel] = zs.sarc_build(sarc)
    print(f'{placed} of {len(hints)} gossip stone hints written')

# world-state settings that are a save flag's starting value in the remake (GameData Bool defaults)
import struct, mmh3  # noqa: E402
settings = json.load(open(os.path.join(seed_dir, 'settings.json'))) if os.path.exists(os.path.join(seed_dir, 'settings.json')) else {}
flags_off = []
forest = settings.get('gRandoSettings.ClosedForest', 0)
if forest >= 1: flags_off.append('KokiriForest_Npc_Kokiri_007_Child_Blocker_00')  # Kokiri boy at the forest exit
if forest >= 2: flags_off.append('KokiriForest_Npc_Kokiri_Mido_Child_Blocker')     # Mido in front of the Deku Tree
if flags_off:
    gd_rel = os.path.relpath(glob.glob(os.path.join(romfs, 'GameData', 'GameDataList.Product.*.byml.zs'))[0], romfs).replace(os.sep, '/')
    raw = bytearray(zs.decompress_any(romfs, open(os.path.join(romfs, gd_rel), 'rb').read()))
    for name in flags_off:  # in place: DefaultValue sits 8 bytes before Hash
        h = mmh3.hash(name, signed=False); hits = []
        i = raw.find(struct.pack('>I', h))
        while i >= 0:
            if i >= 8 and raw[i - 1] in (0xd3, 0xd4, 0xd1) and raw[i - 9] == 0xd0: hits.append(i - 8)
            i = raw.find(struct.pack('>I', h), i + 1)
        if len(hits) != 1:
            problems.append(f'GameData {name}: {len(hits)} rows found'); continue
        struct.pack_into('>I', raw, hits[0], 0)
        report.append({'check': f'start flag {name}', 'item': 'off', 'actor': '', 'was': 'on', 'file': gd_rel})
    rows = {r.get('Hash'): r for r in byml.load(bytes(raw))['Data']['Bool']}
    assert all(rows[mmh3.hash(n, signed=False)]['DefaultValue'] is False for n in flags_off if not any(n in p for p in problems))
    changed_files[gd_rel] = bytes(raw)

dst = os.path.join(mods, mod_name, 'romfs')
if os.path.isdir(dst):
    for f in glob.glob(os.path.join(dst, '*', '**', '*.zs'), recursive=True):
        os.remove(f)
table_src = restbl.table_path(romfs)
table = restbl.load(table_src)
for rel, out in changed_files.items():
    p = os.path.join(dst, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(zs.compress_with(romfs, out, 'bcett.byml.zsdic' if rel.endswith('.bcett.byml.zs') else 'zs.zsdic'))
    key = rel[:-3]  # size table paths drop .zs
    old = restbl.get(table, key)
    if old is None or old < len(out) + 0x1000:
        restbl.put(table, key, max(old or 0, len(out) + 0x1000))
tdst = os.path.join(dst, os.path.relpath(table_src, romfs))
os.makedirs(os.path.dirname(tdst), exist_ok=True)
restbl.save(table, tdst)

json.dump({'files': sorted(changed_files), 'checks': report, 'problems': problems},
          open(os.path.join(seed_dir, 'install_report.json'), 'w'), indent=1)
print(f'{len(report)} check copies written in {len(changed_files)} map files -> {dst}')
for p in problems:
    print('PROBLEM', p)
