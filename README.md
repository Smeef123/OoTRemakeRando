# OoT Remake Randomizer

A randomizer for the Nintendo Switch 2 remake of *The Legend of Zelda: Ocarina of Time*, played on PC through
**Hookshot** (a PC version of the remake built from your own copy of the game). It shuffles where items are, the way
**[Ship of Harkinian](https://www.shipofharkinian.com/)**'s randomizer does. It *is* Ship of Harkinian's randomizer:
its item pool, logic and seed generator are used unchanged, so every seed can be beaten.

You get:
- a settings window with Ship of Harkinian's own settings, limited to the ones the remake can follow;
- a seed (type one or roll a random one) that is installed into the game as a mod;
- a spoiler log that lists where everything is, and gossip stone hints in game;
- a separate save folder, so randomizer saves don't mix with your normal ones.

## What you need
- **Windows 10 or 11.**
- **Your own dump of the OoT remake** (Switch 2), built into a PC game folder with **Hookshot**. The game folder is
  the one that holds `bin\hookshot.exe`, `image.bin` and `romfs`. This randomizer contains no game files and does not
  download any; it only works with your own copy.
- About 2 GB free disk space and an internet connection for the one-time setup.

## Install (once)
1. Download this repository (green **Code** button → **Download ZIP**) and unzip it somewhere, for example your
   Desktop.
2. Double-click **`Setup.cmd`**. It:
   - installs Git, Python and a C++ compiler with Windows' own `winget` if they are missing (if it installs anything,
     close the window and run `Setup.cmd` again);
   - downloads Ship of Harkinian's source code and builds the seed generator from it (a few minutes);
   - asks you to pick your Hookshot game folder;
   - puts two shortcuts on your desktop: **OoT Remake Randomizer** and **OoT Remake (Randomizer)**.

## Make a seed and play
1. Open **OoT Remake Randomizer**.
2. Pick your settings on the tabs (hover over a setting to see what it does), type a seed or press **Random**.
3. Press **Generate and install**. When it says *Done*, the seed is installed.
4. Open **OoT Remake (Randomizer)** and start a **New Game**. (A save from an earlier seed keeps that seed's world
   state; start a new file for each seed.)
5. Stuck? **Open spoiler log** shows where every item is and the order to get them.

## The settings
They are Ship of Harkinian's, with its own descriptions. Only the ones that work in the remake are shown:
- **Logic/Access:** item pool size, logic options, **Closed Forest** (Off removes Mido and the Kokiri boy who block
  the Deku Tree and the forest exit).
- **Shuffles:** songs, Kokiri Sword, ocarinas, Weird Egg, Zelda's Letter, Scarecrow's Song, Gerudo Membership Card,
  adult trade items, Treasure Chest Game, **shops** (how many slots per shop, prices).
- **Dungeons:** maps and compasses, small keys, boss keys, dungeon rewards (where each may be placed).
- **Hints:** gossip stone hints on or off, how clear they are, how they are chosen.

Everything else (entrance shuffle, Master Quest, starting items, Triforce Hunt, Ship of Harkinian's extra items
and abilities, ...) is kept as in the normal game, because the remake can't follow it.

## What gets shuffled (246 checks)
- **Chests** across the overworld and dungeons, including Mido's house, the Deku Tree, dungeon maps, compasses, boss
  keys and major items (Hookshot, Bow, boots, gauntlets, Lens of Truth, Mirror Shield, ...).
- **Songs** (Saria, Impa, Malon, the Royal Tomb, Ocarina of Time, the windmill and all of Sheik's).
- **Dungeon rewards** (spiritual stones and medallions), **Great Fairy rewards**.
- **Gifts and minigame prizes:** Saria's ocarina, Zelda's Letter, Malon's egg, Darunia, the Gerudo carpenters, Light
  Arrows, Lost Woods target, Deku Theater, diving and fishing, horseback archery, Skull Kid and his ocarina game, Dampé,
  the man on the roof, the bean seller, Talon's and Anju's cuccos, bombchu bowling, both shooting galleries, the frogs,
  the lab dive, the lost dog, the Big Poe collector, the Gold Skulltula rewards, the rolling Goron and the adult trade
  sequence.
- **Shops** (all 8, with the Shop Shuffle setting): new shop items are built for whatever lands on a shelf.
- **Heart pieces** lying in the world and **boss heart containers**.
- **Gossip stone hints** (all 40 stones, English).

Every other check keeps its normal item, and the randomizer's logic knows that.

## Known limits
- About 100 chests stay normal, mostly small-key chests: their rooms can't be told apart from the game's data, and a
  wrong guess could make a seed unbeatable.
- Not shuffled: pots, grass, rocks, crates, Gold Skulltula tokens themselves, cows, Deku Scrubs, the two Death Mountain
  Crater heart pieces, the Ice Cavern heart piece and the Goron City spinning pot.
- Shop signs ("Bundle 05" boards) still show the normal goods.
- Upgrades (Hookshot → Longshot, bomb bags, ...) are fixed when the seed is installed, in the order the spoiler log
  expects you to find them; Ship of Harkinian decides when you pick them up.
- Hints are English only, and a hint may be on a different stone of the same area than in Ship of Harkinian.
- Tested in game: chest items (bomb bag and ice arrows from Mido's chests) and shops. Minigame prizes and the newer
  heart pieces have been tested as far as generating and installing seeds, not yet in play. Songs, gifts, swapped heart pieces, hints
  and Closed Forest have been tested as far as generating, installing and starting the game, not yet in play.

## Uninstall
Delete the folder and the two desktop shortcuts. Your Hookshot game folder is never changed: the randomizer's mod and
saves live inside this folder (`mods`, `saves`).

## How it works (for the curious)
| Part | What it is |
|---|---|
| `build/sohrando.exe` | Ship of Harkinian's randomizer built on its own (`gen/main.cpp` + stand-ins for the game parts it links but never runs; `tools/build_gen.sh`). One small addition: checks the remake can't change keep their normal item (`gen/remake_lock.cpp`). |
| `tools/install_seed.py` | Writes a seed into the remake's own data as a mod: chest contents (`Banc` map files), heart-piece objects, item grants in event files (`Event/EventFlow`), gossip stone text (`Mals`) and starting flags (`GameData`). |
| `data/*.json` | Which Ship of Harkinian check is which spot in the remake (`check_map.json` is built from `manual_map.json`, `event_map.json` and automatic matches by `tools/match_checks.py`). |
| `Randomizer.pyw`, `Play.pyw`, `rando.py` | The settings window, the game launcher, and the command line (`python -I rando.py settings/default.json --seed TEXT`). |

## Credits and licenses
- **Ship of Harkinian** by HarbourMasters ([github.com/HarbourMasters/Shipwright](https://github.com/HarbourMasters/Shipwright)):
  the randomizer this is built on. Its repository carries no license file, so **none of its code is included here**;
  `Setup.cmd` downloads it from its own repository at a fixed version and builds it on your PC. Its randomizer code
  derives from **OoT Randomizer** (TestRunnerSRL, MIT) and the 3DS randomizer (MIT), whose notice ships with it.
- **libultraship** (kenix3, MIT), **Dear ImGui** (MIT), **spdlog** (MIT), **nlohmann/json** (MIT), **BS::thread_pool**
  (MIT), **SDL2** headers (zlib): downloaded the same way, used to build the generator.
- **evfl** (leoetlino) reads and writes the remake's event files; **zstandard** and **mmh3** from PyPI.
- **Hookshot** and its builder: the PC version of the remake this runs on (not included).
- Built by Claude (Anthropic's Claude Code, model Claude Opus 5.5) working for the project owner.
- This repository's own files: MIT (see `LICENSE`).

Ocarina of Time is © Nintendo. This project is not affiliated with Nintendo or HarbourMasters. You need your own legally
obtained copy of the game.
