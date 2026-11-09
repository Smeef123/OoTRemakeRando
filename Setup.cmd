@echo off
rem One-time setup: installs what's missing (Git, Python, a C++ compiler) with winget, downloads Ship of Harkinian's
rem source, builds the seed generator, asks for your Hookshot game folder and puts shortcuts on the desktop.
setlocal
cd /d "%~dp0"
echo == OoT Remake Randomizer setup ==

where git >nul 2>nul || (echo Installing Git... & winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements)
where python >nul 2>nul || (echo Installing Python... & winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements)
where g++ >nul 2>nul || (echo Installing the WinLibs C++ compiler... & winget install -e --id BrechtSanders.WinLibs.POSIX.UCRT --accept-source-agreements --accept-package-agreements)
echo.
echo If anything was just installed, close this window and run Setup.cmd again so Windows finds it.
echo.

set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%BASH%" (echo Git Bash not found at "%BASH%". & pause & exit /b 1)

python -m pip install --quiet --upgrade zstandard evfl mmh3 || (echo pip failed & pause & exit /b 1)
"%BASH%" tools/fetch_deps.sh || (echo Downloading sources failed & pause & exit /b 1)
echo Building the seed generator (takes a few minutes)...
"%BASH%" -c "PYTHON=python sh tools/build_gen.sh" || (echo Build failed: see build\err & pause & exit /b 1)
python -I tools\setup_finish.py || (pause & exit /b 1)
echo.
echo Done. Use "OoT Remake Randomizer" on the desktop to make a seed, and "OoT Remake (Randomizer)" to play it.
pause
