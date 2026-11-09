"""Ship of Harkinian item (RG_*) -> the remake actor a chest or freestanding spot drops.

Progressive items list one actor per level; the installer hands them out in playthrough order.
Items not listed have no known pickup actor in the remake yet: the generator keeps them at their own
(unmapped) vanilla checks, so a seed never asks the installer for one."""

CHEST = {
    'RG_GREEN_RUPEE': 'TBox_Rupee_Green', 'RG_GREG_RUPEE': 'TBox_Rupee_Green',
    'RG_BLUE_RUPEE': 'TBox_Rupee_Blue', 'RG_RED_RUPEE': 'TBox_Rupee_Red',
    'RG_PURPLE_RUPEE': 'TBox_Rupee_Purple', 'RG_HUGE_RUPEE': 'TBox_Rupee_Gold',
    'RG_PIECE_OF_HEART': 'Obj_Heart_Piece', 'RG_TREASURE_GAME_HEART': 'Obj_Heart_Piece',
    'RG_HEART_CONTAINER': 'Obj_Heart_Container', 'RG_RECOVERY_HEART': 'Obj_Heart',
    'RG_DEKU_SHIELD': 'TBox_Shield_Deku', 'RG_HYLIAN_SHIELD': 'TBox_Shield_Hylian',
    'RG_MIRROR_SHIELD': 'Item_Shield_Mirror',
    'RG_ARROWS_5': 'TBox_ArrowBundle_Small', 'RG_ARROWS_10': 'TBox_ArrowBundle_Medium',
    'RG_ARROWS_30': 'TBox_ArrowBundle_Large',
    'RG_DEKU_NUTS_5': 'TBox_DekuNutBundle', 'RG_DEKU_NUTS_10': 'TBox_DekuNutBundle',
    'RG_DEKU_SEEDS_30': 'TBox_DekuSeedBundle', 'RG_DEKU_STICK_1': 'Item_DekuStickBundle_Small',
    'RG_BOMBS_5': 'Item_BombBundle_Small', 'RG_BOMBS_10': 'Item_BombBundle_Small', 'RG_BOMBS_20': 'Item_BombBundle_Small',
    'RG_BOMBCHU_5': 'Item_BombchuBundle_Small', 'RG_BOMBCHU_10': 'Item_BombchuBundle_Medium',
    'RG_BOMBCHU_20': 'Item_BombchuBundle_Large',
    'RG_KOKIRI_SWORD': 'Item_Sword_Kokiri', 'RG_GIANTS_KNIFE': 'Item_Sword_Giant', 'RG_BIGGORON_SWORD': 'Item_Sword_Biggoron',
    'RG_BOOMERANG': 'Item_Boomerang', 'RG_MEGATON_HAMMER': 'Item_Hammer', 'RG_LENS_OF_TRUTH': 'Item_GlassTruth',
    'RG_HOVER_BOOTS': 'Item_HoverBoot', 'RG_IRON_BOOTS': 'Item_HeavyBoot',
    'RG_FIRE_ARROWS': 'Item_Arrow_Fire', 'RG_ICE_ARROWS': 'Item_Arrow_Ice', 'RG_LIGHT_ARROWS': 'Item_Arrow_Light',
    'RG_DINS_FIRE': 'Item_DinFire', 'RG_FARORES_WIND': 'Item_FaroreWind', 'RG_NAYRUS_LOVE': 'Item_NayruLove',
    'RG_MAGIC_BEAN': 'Item_MagicBean', 'RG_STONE_OF_AGONY': 'Item_AgonyStone',
    'RG_GERUDO_MEMBERSHIP_CARD': 'Item_Token_Gerudo', 'RG_GOLD_SKULLTULA_TOKEN': 'Item_Token_Gold',
    'RG_DOUBLE_DEFENSE': 'Item_FairyBless_DefenseDouble',
    'RG_GORON_TUNIC': 'Armor_Adult_Goron', 'RG_ZORA_TUNIC': 'Armor_Adult_Zora',  # guess: TotK-style armour pickups, not yet seen in game
    'RG_EMPTY_BOTTLE': 'Item_Bottle', 'RG_BOTTLE_WITH_MILK': 'Item_Bottle_Milk', 'RG_RUTOS_LETTER': 'Item_Bottle_Letter',
    'RG_BOTTLE_WITH_BUGS': 'Item_Bottle_Bug', 'RG_BOTTLE_WITH_FISH': 'Item_Bottle_Fish',
    'RG_BOTTLE_WITH_RED_POTION': 'Item_Bottle_RedPotion', 'RG_BOTTLE_WITH_GREEN_POTION': 'Item_Bottle_GreenPotion',
    'RG_BOTTLE_WITH_BLUE_POTION': 'Item_Bottle_BluePotion', 'RG_BOTTLE_WITH_FAIRY': 'Item_Bottle_Fairy',
    'RG_BOTTLE_WITH_BLUE_FIRE': 'Item_Bottle_BlueFire', 'RG_BOTTLE_WITH_BIG_POE': 'Item_Bottle_BigPoe',
    'RG_BOTTLE_WITH_POE': 'Item_Bottle_Poe',
    'RG_WEIRD_EGG': 'Item_WeirdEgg', 'RG_ZELDAS_LETTER': 'Item_ZeldaLetter', 'RG_POCKET_EGG': 'Item_PocketEgg',
    'RG_COJIRO': 'Item_CojiroCucco', 'RG_ODD_MUSHROOM': 'Item_OddMushroom', 'RG_ODD_POTION': 'Item_OddPowder',
    'RG_POACHERS_SAW': 'Item_PoacherSaw', 'RG_BROKEN_SWORD': 'Item_BrokenSword', 'RG_PRESCRIPTION': 'Item_Prescription',
    'RG_EYEBALL_FROG': 'Item_EyeballFrog', 'RG_EYEDROPS': 'Item_EyeDrop', 'RG_CLAIM_CHECK': 'Item_ClaimCheck',
    'RG_ZELDAS_LULLABY': 'Item_Melody_ZeldaLullaby', 'RG_EPONAS_SONG': 'Item_Melody_EponaSong',
    'RG_SARIAS_SONG': 'Item_Melody_SariaSong', 'RG_SUNS_SONG': 'Item_Melody_SunSong',
    'RG_SONG_OF_TIME': 'Item_Melody_TimeSong', 'RG_SONG_OF_STORMS': 'Item_Melody_StormSong',
    'RG_MINUET_OF_FOREST': 'Item_Melody_ForestMinuet', 'RG_BOLERO_OF_FIRE': 'Item_Melody_FireBolero',
    'RG_SERENADE_OF_WATER': 'Item_Melody_WaterSerenade', 'RG_REQUIEM_OF_SPIRIT': 'Item_Melody_SpiritRequiem',
    'RG_NOCTURNE_OF_SHADOW': 'Item_Melody_ShadowNocturne', 'RG_PRELUDE_OF_LIGHT': 'Item_Melody_LightPrelude',
    'RG_KOKIRI_EMERALD': 'Item_Stone_Forest', 'RG_GORON_RUBY': 'Item_Stone_Fire', 'RG_ZORA_SAPPHIRE': 'Item_Stone_Water',
    'RG_FOREST_MEDALLION': 'Item_Medal_Forest', 'RG_FIRE_MEDALLION': 'Item_Medal_Fire',
    'RG_WATER_MEDALLION': 'Item_Medal_Water', 'RG_SPIRIT_MEDALLION': 'Item_Medal_Spirit',
    'RG_SHADOW_MEDALLION': 'Item_Medal_Shadow', 'RG_LIGHT_MEDALLION': 'Item_Medal_Light',
}
# dungeon items: same actor everywhere; the chest's dungeon decides whose key it is (own-dungeon settings)
for d in ('DEKU_TREE', 'DODONGOS_CAVERN', 'JABU_JABUS_BELLY', 'FOREST_TEMPLE', 'FIRE_TEMPLE', 'WATER_TEMPLE',
          'SPIRIT_TEMPLE', 'SHADOW_TEMPLE', 'BOTTOM_OF_THE_WELL', 'ICE_CAVERN', 'GERUDO_TRAINING_GROUND', 'GANONS_CASTLE'):
    CHEST[f'RG_{d}_SMALL_KEY'] = 'Item_Dungeon_SmallKey'
    CHEST[f'RG_{d}_BOSS_KEY'] = 'Item_Dungeon_BossKey'
    CHEST[f'RG_{d}_MAP'] = 'Item_Dungeon_Map'
    CHEST[f'RG_{d}_COMPASS'] = 'Item_Dungeon_Compass'
CHEST['RG_TREASURE_GAME_SMALL_KEY'] = 'Obj_MiniGame_SmallKey'

PROGRESSIVE = {
    'RG_PROGRESSIVE_HOOKSHOT': ['Item_Hookshot', 'Item_Longshot'],
    'RG_PROGRESSIVE_STRENGTH': ['Item_Gauntlet_Goron', 'Item_Gauntlet_Silver', 'Item_Gauntlet_Gold'],
    'RG_PROGRESSIVE_BOMB_BAG': ['Item_BombBag_Small', 'Item_BombBag_Medium', 'Item_BombBag_Large'],
    'RG_PROGRESSIVE_BOW': ['Item_Range_Bow', 'Item_Quiver_Medium', 'Item_Quiver_Large'],
    'RG_PROGRESSIVE_SLINGSHOT': ['Item_Range_SlingShot', 'Item_BulletBag_Medium', 'Item_BulletBag_Large'],
    'RG_PROGRESSIVE_WALLET': ['Item_Wallet_Medium', 'Item_Wallet_Large'],
    'RG_PROGRESSIVE_SCALE': ['Item_Scale_Silver', 'Item_Scale_Gold'],
    'RG_PROGRESSIVE_NUT_UPGRADE': ['Item_NutBag_Medium', 'Item_NutBag_Large'],
    'RG_PROGRESSIVE_STICK_UPGRADE': ['Item_StickBag_Medium', 'Item_StickBag_Large'],
    'RG_PROGRESSIVE_OCARINA': ['Item_Ocarina_Fairy', 'Item_Ocarina_Time'],
    'RG_PROGRESSIVE_MAGIC_METER': ['Item_FairyBless_MP', 'Item_FairyBless_MPDouble'],
}


def installable():
    return set(CHEST) | set(PROGRESSIVE)
