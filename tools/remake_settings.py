"""Settings the remake cannot follow, held at the unmodified game's value (used by rando.py and the window)."""
# Settings the remake cannot follow (yet): the game would not do what SoH's logic then assumes, so they are held at
# the value that matches the unmodified game. Shuffle settings for checks the remake can't change (pots, cows,
# tokens, scrubs...) stay free: those checks simply keep their vanilla item and SoH's logic knows it.
S = 'gRandoSettings.'
FORCED = {S + 'LinksPocket': 3,           # "Nothing": nothing is handed to Link at the start
          S + 'StartingAge': 0, S + 'StartingHearts': 2,  # a new file starts as child with 3 hearts
          S + 'DoorOfTime': 0, S + 'ZorasFountain': 0, S + 'SleepingWaterfall': 0,
          S + 'FortressCarpenters': 0, S + 'RainbowBridge': 0, S + 'GanonTrial': 1, S + 'GanonTrialCount': 6,
          S + 'MedallionLockedTrials': 0, S + 'ShuffleGanonBossKey': 0, S + 'LockOverworldDoors': 0,
          S + 'SkipChildStealth': 0, S + 'SkipEponaRace': 0, S + 'SkipPlantingBeans': 0,
          S + 'MQDungeons': 0, S + 'MQDungeonCount': 0, S + 'TriforceHuntTotalPieces': 0}
for k in ('ShuffleDungeonsEntrances', 'ShuffleBossEntrances', 'ShuffleOverworldEntrances', 'ShuffleInteriorsEntrances',
          'ShuffleGrottosEntrances', 'ShuffleOwlDrops', 'ShuffleWarpSongs', 'ShuffleOverworldSpawns', 'MixedEntrances',
          'DecoupleEntrances', 'ShuffleGanonTowerEntrance', 'ShuffleThievesHideoutEntrances',
          # abilities and items SoH adds that the remake does not have
          'ShuffleMasterSword', 'ShuffleSwim', 'ShuffleOpenChest', 'ShuffleSpeak', 'ShuffleOcarinaButtons',
          'ShuffleChildWallet', 'ShuffleDekuNutBag', 'ShuffleDekuStickBag', 'ShuffleBossSouls', 'ShuffleGanonsSoul',
          'ShuffleFishingPole', 'RocsFeather', 'SunlightArrows', 'BlueFireArrows', 'BombchuBag', 'IncludeTycoonWallet',
          'InfiniteUpgrades', 'FullWallets', 'MasksAsAdult', 'ShuffleKeyRingsForestTemple', 'ShuffleKeyRingsGerudoFortress',
          'ShuffleKeyRingsGanonsCastle'):
    FORCED[S + k] = 0
# starting inventory: nothing can be handed over at the start yet
for k in ('Beans BiggoronSword BoleroOfFire BombBag BombchuBag Boomerang Bottle1 Bottle2 Bottle3 Bottle4 Bow BunnyHood '
          'ClaimCheck DekuShield DinsFire EponasSong FaroresWind FireArrows GerudoCard GerudoMask GoronMask GoronTunic '
          'Hookshot HoverBoots HylianShield IceArrows IronBoots KeatonMask KokiriSword LensOfTruth LightArrows MagicMeter '
          'MaskOfTruth MasterSword MegatonHammer MinuetOfForest MirrorShield NayrusLove NocturneOfShadow Nuts Ocarina '
          'PreludeOfLight RequiemOfSpirit SariasSong Scale ScarecrowsSong SerenadeOfWater SkullMask SkulltulaToken '
          'Slingshot SongOfStorms SongOfTime SpookyMask Sticks StoneOfAgony Strength SunsSong Wallet WeirdEgg '
          'ZeldasLetter ZeldasLullaby ZoraMask ZoraTunic').split():
    FORCED[S + 'Starting' + k] = 0
# SoH gameplay changes the remake doesn't have
for k, v in (('JabuJabu', 0), ('EarlyGrannysShop', 0), ('SwordlessEponaItems', 0), ('BunnyHood', 0),
             ('SlingBowBeehives', 0), ('BigPoeTargetCount', 10)):
    FORCED[S + k] = v
# SoH's Triforce Hunt / alternative win conditions: the remake has no Triforce pieces, you win by beating Ganon
for k, v in (('ShuffleWincon', 0), ('TriforceHuntPiecesLocation', 2), ('GbkTriforceCount', 100),
             ('GanonsSoulTriforceCount', 100), ('WinconTriforceCount', 100), ('TriforcePieceCount', 100)):
    FORCED[S + k] = v

# ---- everything else the remake doesn't have or the installer can't change: held at SoH's default
import json as _json, os as _os
_DEFAULTS = {}
def _walk(g):
    for o in g.get('options', []): _DEFAULTS[o['cvar']] = o['default']
    for s in g.get('groups', []): _walk(s)
for _t in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'build', 'soh_options.json'),
                          encoding='utf-8'))['tabs']:
    _walk(_t)
FIXED = """GbkRewardOptions GbkMedallionCount GbkStoneCount GbkDungeonCount GbkRewardCount GbkTokenCount
GanonsSoulRewardOptions GanonsSoulMedallionCount GanonsSoulStoneCount GanonsSoulDungeonCount GanonsSoulRewardCount
GanonsSoulTokenCount WinconRewardOptions WinconMedallionCount WinconStoneCount WinconDungeonCount WinconRewardCount
WinconTokenCount BridgeRewardOptions StoneCount MedallionCount RewardCount DungeonCount TokenCount
MixDungeons MixBosses MixOverworld MixInteriors MixThievesHideout MixGrottos
ShuffleTokens ShuffleMasks Fishsanity FishsanityPondCount FishsanityAgeSplit ShuffleFreestanding ShuffleWonderItems
ShuffleSilver ShuffleBeehives ShuffleCows ShufflePots ShuffleGrass ShuffleCrates ShuffleBoulders ShuffleRocks ShuffleTrees
ShuffleBushes ShuffleIcicles ShuffleRedIce ShuffleFireGorons ShuffleSigns ShuffleFrogSongRupees Shuffle100GSReward
ShuffleFountainFairies ShuffleStoneFairies ShuffleBeanFairies ShuffleFairySpots ShuffleButterflyFairies
ShopsanityTycoonWalletWeight ShopShieldsTunicsGate ShuffleScrubs ScrubsPrices ScrubsFixedPrice
ScrubsPriceRange1 ScrubsPriceRange2 ScrubsNoWalletWeight ScrubsChildWalletWeight ScrubsAdultWalletWeight
ScrubsGiantWalletWeight ScrubsTycoonWalletWeight ScrubsPricesAffordable ShuffleMerchants MerchantPrices
MerchantFixedPrice MerchantPriceRange1 MerchantPriceRange2 MerchantNoWalletWeight MerchantChildWalletWeight
MerchantAdultWalletWeight MerchantGiantWalletWeight MerchantTycoonWalletWeight MerchantPricesAffordable ShuffleBeggar
ShuffleFishermansHat ShuffleGrab ShuffleClimb ShuffleCrawl ShuffleBeanSouls NayrusLoveUses EnableBombchuDrops
ProgressiveGoronSword SkeletonKey GerudoKeys ShuffleKeyRings ShuffleKeyRingsRandomCount ShuffleKeyRingsFireTemple
ShuffleKeyRingsWaterTemple ShuffleKeyRingsSpiritTemple ShuffleKeyRingsShadowTemple ShuffleKeyRingsBottomOfTheWell
ShuffleKeyRingsGTG ShuffleKeyRingsChestGame MQDungeonsSelection MQDungeonsDekuTree MQDungeonsDodongosCavern
MQDungeonsJabuJabu MQDungeonsForestTemple MQDungeonsFireTemple MQDungeonsWaterTemple MQDungeonsSpiritTemple
MQDungeonsShadowTemple MQDungeonsBottomOfTheWell MQDungeonsIceCavern MQDungeonsGTG MQDungeonsGanonsCastle
BaseIceTraps AdditionalIceTraps IceTrapPercent IceTrapNames""".split()
for k in FIXED:
    FORCED.setdefault(S + k, _DEFAULTS.get(S + k, 0))
# static hints live in NPC dialogue the installer doesn't rewrite: off, so the spoiler log lists only real hints
for k in """AltarHint GanondorfHint SheikLAHint BossKeyHint DampeHint GregHint LoachHint SariaHint MidoHint FrogsHint
OoTHint BiggoronHint BigPoesHint ChickensHint MalonHint HBAHint FishingPoleHint WarpSongText ScrubText MerchantText
10GSHint 20GSHint 30GSHint 40GSHint 50GSHint 100GSHint MaskShopHint""".split():
    FORCED[S + k] = 0
# options where only some choices work in the remake: cvar -> allowed choice indices
ALLOWED = {S + 'GossipStoneHints': [0, 1],   # stones that need the Mask of Truth / Stone of Agony aren't in the remake
           S + 'ShuffleWeirdEgg': [0, 1],    # "Skip Waking Talon" changes the game
           S + 'StartingMapsCompasses': [1, 2, 3, 4, 5], S + 'Keysanity': [1, 2, 3, 4, 5],
           S + 'BossKeysanity': [1, 2, 3, 4, 5]}  # "Start With" needs a start-of-game grant
