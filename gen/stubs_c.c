// Inventory tables come from SoH at build time (inventory_tables.inc); everything else: no-op stubs for game/UI code the generator links but never runs.
#include <stdint.h>
typedef uint32_t u32; typedef uint8_t u8; typedef uint16_t u16;
#include "z64item.h"
#include "inventory_tables.inc"  /* SoH z_inventory.c tables, extracted by tools/prepare_soh.py */
const char gBuildVersion[] = "sohrando";
const char gGitBranch[] = "remake";
const char gGitCommitHash[] = "0";
void* sNesMessageEntryTablePtr; void* sGerMessageEntryTablePtr; void* sFraMessageEntryTablePtr;
_Alignas(16) char gSaveContext[0x20000];
void* gPlayState;
#define NOP(n) void n(void) {}
NOP(Actor_Kill) NOP(Camera_RequestMode) NOP(Color_RGBA8_Copy) NOP(EffectSsGRipple_Spawn) NOP(EffectSsKiraKira_SpawnDispersed)
NOP(EnItem00_CustomItemsParticles) NOP(FrameInterpolation_RecordCloseChild) NOP(FrameInterpolation_RecordOpenChild)
NOP(GetItemEntry_Draw) NOP(Graph_CloseDisps) NOP(Graph_OpenDisps) NOP(Math_Vec3f_Copy) NOP(Matrix_Pop) NOP(Matrix_Push) NOP(Matrix_Scale)
NOP(func_8002EBCC) NOP(func_8002ED80)
NOP(Randomizer_DrawBeanSprout) NOP(Randomizer_DrawBombchuBag) NOP(Randomizer_DrawBossKey) NOP(Randomizer_DrawBossSoul) NOP(Randomizer_DrawBronzeScale)
NOP(Randomizer_DrawCompass) NOP(Randomizer_DrawDoubleDefense) NOP(Randomizer_DrawFishingPoleGI) NOP(Randomizer_DrawJabberNut) NOP(Randomizer_DrawKeyRing)
NOP(Randomizer_DrawKneePads) NOP(Randomizer_DrawLadder) NOP(Randomizer_DrawMap) NOP(Randomizer_DrawMasterSword) NOP(Randomizer_DrawMysteryItem)
NOP(Randomizer_DrawNutBag) NOP(Randomizer_DrawOcarinaButton) NOP(Randomizer_DrawOpenChest) NOP(Randomizer_DrawOverworldKey) NOP(Randomizer_DrawPowerBracelet)
NOP(Randomizer_DrawRocsFeather) NOP(Randomizer_DrawScarecrowsSong) NOP(Randomizer_DrawSilverRupee) NOP(Randomizer_DrawSkeletonKey) NOP(Randomizer_DrawSmallKey) NOP(Randomizer_DrawStickBag)
float Math_CosS(short a) { return 1.0f; }
float Rand_ZeroOne(void) { return 0.5f; } float Rand_Centered(void) { return 0; } float Rand_CenteredFloat(float f) { return 0; }
int ResourceMgr_IsSceneMasterQuest(int s) { return 0; }
int Entrance_GetIsEntranceDiscovered(int e) { return 0; }
int Flags_GetRandomizerInf(int f) { return 0; } void Flags_SetRandomizerInf(int f) {}
