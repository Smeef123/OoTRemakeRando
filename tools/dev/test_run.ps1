# Test run of Hookshot with a seed's mod folder: its own save folder, muted, window that never takes focus, a screenshot
# every -ShotEvery presents, input from tools/live_input.txt (lines in HOS_INPUT_SCRIPT syntax, appended while it runs).
# Developer tool. Game folder: -Game, or the one in config.json.
param([string]$Game = "", [int]$Seconds = 900, [string]$Name = "test1", [int]$ShotEvery = 120, [string]$Mods = "", [switch]$FreshUser)
$ErrorActionPreference = "Stop"
$R = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$game = if ($Game) { $Game } else { (Get-Content (Join-Path $R "config.json") | ConvertFrom-Json).game }
if (Get-Process hookshot -ErrorAction SilentlyContinue) { "hookshot.exe already running: one at a time"; exit 2 }
if (-not $Mods) { $Mods = Join-Path $R "out\mods" }
$out = Join-Path $R "out\runs\$Name"; $shots = Join-Path $out "shots"; $user = Join-Path $R "out\runs\user"
if ($FreshUser -and (Test-Path $user)) { Remove-Item -Recurse -Force $user }
New-Item -ItemType Directory -Force $out, $shots, $user | Out-Null
$live = Join-Path $out "live_input.txt"; Set-Content -Path $live -Value "" -Encoding ascii
$env:RX_BACKEND = "vulkan"
Remove-Item Env:HOS_HEADLESS -ErrorAction SilentlyContinue
$env:HOS_WINDOW_NOACTIVATE = "1"; $env:HOS_AUDIO = "0"; $env:HOS_NO_UPDATE_CHECK = "1"; $env:HOOKSHOT_NO_UPDATE_CHECK = "1"
$env:HOS_MODS = $Mods; $env:HOS_INPUT_LIVE = $live; $env:HOS_INPUT_SCRIPT_BACKGROUND = "1"
$env:RX_VK_SHOTS = $shots; $env:RX_VK_SHOT_EVERY = "$ShotEvery"
$t0 = Get-Date
$p = Start-Process -FilePath (Join-Path $game "bin\hookshot.exe") `
    -ArgumentList @("`"$(Join-Path $game 'image.bin')`"", "--romfs", "`"$(Join-Path $game 'romfs')`"", "--user", "`"$user`"") `
    -WorkingDirectory $game -PassThru -NoNewWindow `
    -RedirectStandardOutput (Join-Path $out "stdout.txt") -RedirectStandardError (Join-Path $out "log.txt")
try { $p.PriorityClass = "BelowNormal" } catch {}
"started pid $($p.Id) at $(Get-Date -Format HH:mm:ss)"
$exited = $p.WaitForExit($Seconds * 1000)
if (-not $exited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
"run '$Name': $([int]((Get-Date) - $t0).TotalSeconds) s, " + $(if ($exited) { "exited with $($p.ExitCode)" } else { "stopped after $Seconds s" })
"shots: $((Get-ChildItem $shots -File).Count)"
