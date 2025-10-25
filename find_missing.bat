:: i'm sorry this is crappy clanker garbage, but i'm not writing all this myself D:

@echo off
REM ==================================================
REM Blender Missing Resources Finder
REM ==================================================
setlocal enabledelayedexpansion
echo ================================================
echo Blender Missing Resources Finder
echo ================================================
echo.

REM --------------------------------------------------
REM Step 1: Locate Blender
REM --------------------------------------------------

if defined BLENDER_PATH (
    set "BLENDER_EXE=%BLENDER_PATH%"
    goto :check_blender
)

set "BLENDER_EXE="
if exist "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" (
    set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
    goto :check_blender
)
if exist "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" (
    set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
    goto :check_blender
)
if exist "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe" (
    set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
    goto :check_blender
)
if exist "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" (
    set "BLENDER_EXE=C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"
    goto :check_blender
)

where blender.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "BLENDER_EXE=blender.exe"
    goto :check_blender
)

echo ERROR: Blender not found!
echo Please set BLENDER_PATH or install Blender.
pause
exit /b 1

:check_blender
echo Found Blender: %BLENDER_EXE%
echo.

REM --------------------------------------------------
REM Step 2: Find Python script
REM --------------------------------------------------

set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%blender_find_and_relink.py"

if not exist "%PYTHON_SCRIPT%" (
    if exist "%SCRIPT_DIR%find_missing.py" set "PYTHON_SCRIPT=%SCRIPT_DIR%find_missing.py"
    if exist "%SCRIPT_DIR%blender_find_missing.py" set "PYTHON_SCRIPT=%SCRIPT_DIR%blender_find_missing.py"
)

if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: blender_find_and_relink.py not found!
    echo Expected: %PYTHON_SCRIPT%
    pause
    exit /b 1
)

REM --------------------------------------------------
REM Step 3: Parse arguments
REM --------------------------------------------------

if "%~1"=="" (
    echo ERROR: No target specified!
    echo Usage:
    echo   find_missing.bat ^<blend_file_or_folder^> [extra_search_folders...]
    echo Example:
    echo   find_missing.bat ".\Rooms" "C:\Assets\Textures" "C:\Assets\Materials"
    pause
    exit /b 1
)

REM First argument = target (folder or .blend)
set "TARGET=%~1"
shift

REM Collect remaining args as extra search paths
set "EXTRA_ARGS="
:collect_args
if "%~1"=="" goto :run
set "EXTRA_ARGS=%EXTRA_ARGS% "%~1""
shift
goto :collect_args

:run
echo Target: %TARGET%
if not "%EXTRA_ARGS%"=="" (
    echo Extra search paths:%EXTRA_ARGS%
)
echo ================================================
echo Scanning and relinking missing resources...
echo ================================================

REM --------------------------------------------------
REM Step 4: Run Blender in background
REM --------------------------------------------------

"%BLENDER_EXE%" --background --python "%PYTHON_SCRIPT%" -- "%TARGET%" %EXTRA_ARGS%

if %errorlevel% neq 0 (
    echo.
    echo ================================================
    echo ERROR: Process failed with error code %errorlevel%
    echo ================================================
    pause
    exit /b %errorlevel%
)

echo.
echo ================================================
echo Scan completed successfully!
echo ================================================
pause
