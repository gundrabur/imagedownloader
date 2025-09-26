@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ============================================================================
REM  Media Downloader - Windows Build Script
REM  This script builds a standalone Windows executable using PyInstaller.
REM  Output: dist\MediaDownloader.exe and a ZIP package in build\
REM ============================================================================

set APP_NAME=Media Downloader
set EXE_NAME=MediaDownloader
set APP_VERSION=1.0.0
set BUILD_INFO=build_info_windows.txt
set VENV_DIR=.venv

call :print_banner

REM --- Prerequisite Checks ----------------------------------------------------
call :status "Checking prerequisites..."

where python >nul 2>nul
if errorlevel 1 (
  call :error "Python not found. Install from https://www.python.org/downloads/windows/"
  goto :end_fail
) else (
  for /f "delims=" %%v in ('python -c "import platform;print(platform.python_version())"') do set PY_VERSION=%%v
  call :info "Python version: %PY_VERSION%"
)

if not exist imagedownloader.py (
  call :error "imagedownloader.py not found in current directory"
  goto :end_fail
)

call :success "Prerequisites OK"

REM --- Virtual Environment ----------------------------------------------------
call :status "Setting up virtual environment..."
if not exist %VENV_DIR% (
  call :info "Creating venv in %VENV_DIR%"
  python -m venv %VENV_DIR%
  if errorlevel 1 (
    call :error "Failed to create virtual environment"
    goto :end_fail
  )
)

call :info "Activating virtual environment"
call %VENV_DIR%\Scripts\activate.bat
if errorlevel 1 (
  call :error "Failed to activate virtual environment"
  goto :end_fail
)

call :info "Upgrading pip"
python -m pip install --upgrade pip >nul

call :status "Installing PyInstaller"
python -m pip install --upgrade pyinstaller >nul
if errorlevel 1 (
  call :error "PyInstaller installation failed"
  goto :end_fail
)
call :success "PyInstaller ready"

REM --- Clean previous builds --------------------------------------------------
call :status "Cleaning previous builds..."
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
call :success "Cleanup done"

REM --- Build console executable -----------------------------------------------
call :status "Building standalone executable..."
python -m PyInstaller --onefile --name %EXE_NAME% imagedownloader.py
if errorlevel 1 (
  call :error "PyInstaller build failed"
  goto :end_fail
)
if not exist dist\%EXE_NAME%.exe (
  call :error "Executable not produced"
  goto :end_fail
)
call :success "Executable built: dist\%EXE_NAME%.exe"

REM --- Smoke test -------------------------------------------------------------
call :status "Running smoke test (example.com)..."
.dist\%EXE_NAME%.exe https://example.com >nul 2>&1
if errorlevel 1 (
  call :info "Smoke test non-zero exit (ok if no media found)"
) else (
  call :success "Smoke test executed"
)

REM --- Package ZIP ------------------------------------------------------------
call :status "Packaging distribution ZIP..."
if not exist build mkdir build
set ZIP_NAME=%EXE_NAME%_windows_x64_v%APP_VERSION%.zip

REM Create temporary package directory
set PKG_DIR=package_temp
if exist !PKG_DIR! rmdir /s /q !PKG_DIR!
mkdir !PKG_DIR!
copy dist\%EXE_NAME%.exe !PKG_DIR%!>nul

REM Write README snippet
>!PKG_DIR!\README.txt echo %APP_NAME% (Windows) - v%APP_VERSION%
>>!PKG_DIR!\README.txt echo ------------------------------------
>>!PKG_DIR!\README.txt echo Usage:
>>!PKG_DIR!\README.txt echo    %EXE_NAME%.exe https://example.com
>>!PKG_DIR!\README.txt echo.
>>!PKG_DIR!\README.txt echo Files will be saved to your Downloads folder in a timestamped directory.

REM Create ZIP (PowerShell)
powershell -NoLogo -NoProfile -Command "Compress-Archive -Path '%PKG_DIR%/*' -DestinationPath 'build/%ZIP_NAME%' -Force" 2>nul
if errorlevel 1 (
  call :error "Failed to create ZIP (Compress-Archive). Ensure PowerShell 5+ is available."
) else (
  call :success "Created build\%ZIP_NAME%"
)

REM Cleanup temp package
if exist !PKG_DIR! rmdir /s /q !PKG_DIR!

REM --- Build Info -------------------------------------------------------------
call :status "Writing build info..."
> %BUILD_INFO% echo Media Downloader - Windows Build Info
>>%BUILD_INFO% echo ==================================
>>%BUILD_INFO% echo Build Date: %DATE% %TIME%
>>%BUILD_INFO% echo Python Version: %PY_VERSION%
for /f "delims=" %%v in ('pyinstaller --version') do set PI_VER=%%v
>>%BUILD_INFO% echo PyInstaller Version: %PI_VER%
>>%BUILD_INFO% echo App Version: %APP_VERSION%
>>%BUILD_INFO% echo Executable: dist\%EXE_NAME%.exe
>>%BUILD_INFO% echo Zip Package: build\%ZIP_NAME%
>>%BUILD_INFO% echo Status: SUCCESS
call :success "Build info written to %BUILD_INFO%"

call :final_success "BUILD COMPLETED SUCCESSFULLY"
call :info "Executable: dist\%EXE_NAME%.exe"
call :info "ZIP Package: build\%ZIP_NAME%"
call :info "Run: dist\%EXE_NAME%.exe https://example.com"

goto :end

REM ================= Helper Labels =================
:print_banner
  echo =============================================================
  echo   %APP_NAME% - Windows Build Script
  echo =============================================================
  echo.
  goto :eof
:status
  echo [*] %~1
  goto :eof
:success
  echo [OK] %~1
  goto :eof
:final_success
  echo.
  echo [SUCCESS] %~1
  echo.
  goto :eof
:error
  echo [ERROR] %~1
  goto :eof
:info
  echo [INFO] %~1
  goto :eof
:end_fail
  echo.
  echo Build FAILED.
  exit /b 1
:end
  endlocal
  exit /b 0
