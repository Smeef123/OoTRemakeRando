"""Shops for the remake: which shelf slot is which SoH shop check, and new shop item packages for any item.

A shop slot in the remake is a placed actor `Shop_<Item>` (Banc map data) with a ShopItemIndex 0-7 (0 written as no
index). Its package (Pack/Actor/Shop_<Item>.pack.zs) is the shop base (Shop_Item_Base: AI, physics, blackboard) plus the
item's own name, model, animation and pouch entry, and a price (PriceParam). To sell any item, a package is made:
  - for SoH's "buy" items (bundles, potions, shields, tunics): the remake's own shop package for that good, cloned
    with SoH's price;
  - for anything else: Shop_Weapon_Shield_Deku's shop parts with the shield's parts swapped for the item's own
    (taken from the item's package, Pack/Actor/<item>.pack.zs).
Each new package also gets rows in the actor tables (RSDB ActorInfo, GameActorInfo, PouchActorInfo), copied from the
package it was made from, as OoT TotK Mod/tools/new_item.py does for TotK."""
import copy, glob, math, os, re
import paths  # noqa: F401  (tools/lib on the path)
import byml, zs

# SoH shop -> remake map area and the shop's centre on the map (x, z)
SHOPS = {'KF_SHOP': ('KokiriForest', (-2.5, -26.5)), 'GC_SHOP': ('GoronCity', (-20, -20)),
         'ZD_SHOP': ('ZoraDomain', (-30, 20.5)), 'KAK_BAZAAR': ('KakarikoVillage', (-74.5, 5)),
         'KAK_POTION_SHOP': ('KakarikoVillage', (-33.5, 10)), 'MARKET_BAZAAR': ('Market', (23, 16)),
         'MARKET_POTION_SHOP': ('Market', (24, 6)), 'MARKET_BOMBCHU_SHOP': ('Market', (-24, 37))}

# SoH "buy" items -> the remake's shop package for that good (bundle sizes by the remake's price order)
BUY = {'RG_BUY_ARROWS_10': 'Shop_ArrowBundle_01', 'RG_BUY_ARROWS_30': 'Shop_ArrowBundle_02',
       'RG_BUY_ARROWS_50': 'Shop_ArrowBundle_03', 'RG_BUY_BOMBS_525': 'Shop_BombBundle_01',
       'RG_BUY_BOMBS_535': 'Shop_BombBundle_01', 'RG_BUY_BOMBS_10': 'Shop_BombBundle_02',
       'RG_BUY_BOMBS_20': 'Shop_BombBundle_03', 'RG_BUY_BOMBS_30': 'Shop_BombBundle_04',
       'RG_BUY_BOMBCHUS_10': 'Shop_BombchuBundle_04', 'RG_BUY_BOMBCHUS_20': 'Shop_BombchuBundle_05',
       'RG_BUY_BLUE_FIRE': 'Shop_Bottle_BlueFire', 'RG_BUY_BOTTLE_BUG': 'Shop_Bottle_Bug',
       'RG_BUY_DEKU_NUTS_5': 'Shop_DekuNutBundle_01', 'RG_BUY_DEKU_NUTS_10': 'Shop_DekuNutBundle_02',
       'RG_BUY_DEKU_SEEDS_30': 'Shop_DekuSeedBundle_01', 'RG_BUY_DEKU_SHIELD': 'Shop_Weapon_Shield_Deku',
       'RG_BUY_DEKU_STICK_1': 'Shop_DekuStick', 'RG_BUY_FAIRYS_SPIRIT': 'Shop_Bottle_Fairy',
       'RG_BUY_FISH': 'Shop_Bottle_Fish', 'RG_BUY_GORON_TUNIC': 'Shop_Armor_Goron',
       'RG_BUY_GREEN_POTION': 'Shop_Bottle_GreenPotion', 'RG_BUY_HEART': 'Shop_Heart',
       'RG_BUY_HYLIAN_SHIELD': 'Shop_Weapon_Shield_Hylian', 'RG_BUY_POE': 'Shop_Bottle_Poe',
       'RG_BUY_RED_POTION_30': 'Shop_Bottle_RedPotion', 'RG_BUY_RED_POTION_40': 'Shop_Bottle_RedPotion',
       'RG_BUY_RED_POTION_50': 'Shop_Bottle_RedPotion', 'RG_BUY_ZORA_TUNIC': 'Shop_Armor_Zora',
       'RG_BUY_BLUE_POTION': 'Item_Bottle_BluePotion'}
TEMPLATE = 'Shop_Weapon_Shield_Deku'
TEMPLATE_ITEM_PARTS = ('Component/ModelInfo/Weapon_Shield_Deku', 'Component/AnimationParam/Obj_Shield_Deku',
                       'Component/PouchContentParam/', 'GameParameter/GameParameterTable/Weapon_Shield_Deku',
                       'GameParameter/PlayerEquipmentActor/', 'GameParameter/XLink/EquipmentTypeParam/',
                       'GameParameter/PriceParam/Shop_Weapon_Shield_Deku')


def slot_of(rc_enum):
    """'RC_KF_SHOP_ITEM_3' -> ('KF_SHOP', 2)"""
    m = re.match(r'RC_(.+)_ITEM_(\d)$', rc_enum)
    return (m.group(1), int(m.group(2)) - 1) if m and m.group(1) in SHOPS else None


def shop_of(folder, pos):
    best = None
    for name, (f, (x, z)) in SHOPS.items():
        d = math.hypot(pos[0] - x, pos[2] - z)
        if f == folder and d < 5 and (best is None or d < best[1]):
            best = (name, d)
    return best[0] if best else None


def _pack(romfs, name):
    return zs.sarc_files(zs.decompress_any(romfs, open(os.path.join(romfs, 'Pack', 'Actor', name + '.pack.zs'), 'rb').read()))


def _rename(v, src, new):
    if isinstance(v, dict):
        return {k: _rename(x, src, new) for k, x in v.items()}
    if isinstance(v, list):
        return [_rename(x, src, new) for x in v]
    return v.replace(src, new) if isinstance(v, str) and src in v else v


def _dump(obj, like):
    return byml.dump(obj, byml.version_of(like), byml.is_big_endian(like))


def _set_price(files, own_price_name, price):
    """Set the package's own price (every PriceParam file but the shop base's 1-rupee default)."""
    done = False
    for n in list(files):
        if n.startswith('GameParameter/PriceParam/') and 'Shop_Item_Base' not in n:
            d = byml.load(files[n])
            if d.get('BuyingPrice', 0) <= 1 and own_price_name not in n:
                continue
            d['BuyingPrice'] = int(price); files[n] = _dump(d, files[n]); done = True
    return done


class Builder:
    def __init__(self, romfs):
        self.romfs = romfs
        self.made = {}       # new actor name -> source actor whose table rows it copies
        self.files = {}      # romfs rel -> bytes (new packages)

    def shop_actor(self, rg_enum, item_actor, price):
        """Name of a shop package selling this item at this price (made if needed)."""
        src = BUY.get(rg_enum)
        if src and src.startswith('Shop_'):
            new = f'{src}_Rando_{price}'
            if new not in self.made:
                files = {n.replace(src, new): (_dump(_rename(byml.load(b), src, new), b) if n.endswith('.bgyml') else b)
                         for n, b in _pack(self.romfs, src).items()}
                if not _set_price(files, new, price):
                    raise RuntimeError(f'{src}: no price file')
                self._add(new, files, src)
            return new
        item = src or item_actor
        new = f'Shop_Rando_{item}_{price}'
        if new not in self.made:
            self._add(new, self._synth(item, new, price), TEMPLATE)
        return new

    def _synth(self, item, new, price):
        shop = _pack(self.romfs, TEMPLATE)
        it = _pack(self.romfs, item)
        files = {n: b for n, b in shop.items() if not n.startswith(TEMPLATE_ITEM_PARTS)
                 and n != f'Actor/{TEMPLATE}.engine__actor__ActorParam.bgyml'}
        for n, b in it.items():  # the item's own parts (not its actor/AI/base, which are its own actor's)
            if not n.startswith(('Actor/', 'AI/')):
                files.setdefault(n, b)
        ia = byml.load(it[f'Actor/{item}.engine__actor__ActorParam.bgyml'])['Components']
        sa = byml.load(shop[f'Actor/{TEMPLATE}.engine__actor__ActorParam.bgyml'])
        comp = dict(sa['Components'])
        for k in ('ActorNameRef', 'AnimationRef', 'ModelInfoRef', 'PouchContentRef'):
            if k in ia:
                comp[k] = ia[k]
            else:
                comp.pop(k, None)
        # the shop's own parameter table: the item's (if any) plus a price
        price_rel = f'GameParameter/PriceParam/{new}.game__pouchcontent__PriceParam.bgyml'
        like = shop[f'GameParameter/PriceParam/{TEMPLATE}.game__pouchcontent__PriceParam.bgyml']
        files[price_rel] = _dump({'BuyingPrice': int(price), 'SellingPrice': 1}, like)
        table_rel = f'GameParameter/GameParameterTable/{new}.engine__actor__GameParameterTable.bgyml'
        tlike = shop['GameParameter/GameParameterTable/Weapon_Shield_Deku.engine__actor__GameParameterTable.bgyml']
        if 'GameParameterTableRef' in ia:
            t = byml.load(it[ia['GameParameterTableRef'][1:]])
        else:
            t = {'Category': 'GameParameterTableDefault', 'Components': {}}
        t.setdefault('Components', {})['PriceParam'] = '?' + price_rel
        files[table_rel] = _dump(t, tlike)
        comp['GameParameterTableRef'] = '?' + table_rel
        sa['Components'] = comp
        files[f'Actor/{new}.engine__actor__ActorParam.bgyml'] = _dump(sa, shop[f'Actor/{TEMPLATE}.engine__actor__ActorParam.bgyml'])
        return files

    def _add(self, new, files, src):
        self.made[new] = src
        self.files[f'Pack/Actor/{new}.pack.zs'] = zs.sarc_build(files)

    def tables(self):
        """RSDB tables with a row for every new package (copied from its source's row)."""
        out = {}
        for name in ('ActorInfo', 'GameActorInfo', 'PouchActorInfo'):
            found = glob.glob(os.path.join(self.romfs, 'RSDB', f'{name}.Product.*.rstbl.byml.zs'))
            if not found:
                continue
            rel = os.path.relpath(found[0], self.romfs).replace(os.sep, '/')
            raw = zs.decompress_any(self.romfs, open(found[0], 'rb').read())
            data = byml.load(raw)
            rows = data if isinstance(data, list) else next(v for v in data.values() if isinstance(v, list))
            have = {r.get('__RowId') for r in rows}
            added = 0
            for new, src in self.made.items():
                if new in have:
                    continue
                row = next((r for r in rows if r.get('__RowId') == src), None)
                if row is None:
                    continue
                nr = _rename(copy.deepcopy(row), src, new)
                nr['__RowId'] = new
                if 'ActorName' in nr:
                    nr['ActorName'] = new
                at = next((i for i, r in enumerate(rows) if r.get('__RowId', '').encode() > new.encode()), len(rows))
                rows.insert(at, nr); added += 1
            if added:
                out[rel] = byml.dump(data, byml.version_of(raw), byml.is_big_endian(raw))
        return out
