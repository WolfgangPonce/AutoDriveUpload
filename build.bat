@echo off
REM ===========================================================
REM   AutoDrive Uploader - Build Script com versionamento
REM ===========================================================
REM
REM Le a versao do arquivo VERSION e cria uma pasta organizada em:
REM   C:\Users\woltr\OneDrive\Documents\Apps\Autodrive Uploader\<versao>\
REM
REM Cada pasta de versao contem:
REM   - source\          (codigo fonte completo, incluindo rclone.exe)
REM   - AutoDriveUploader.exe (build final)
REM   - CHANGELOG.md     (notas da versao)
REM
REM Pre-requisito: Python 3.11+ e rclone.exe em bin\rclone.exe

setlocal enabledelayedexpansion

echo ============================================
echo   AutoDrive Uploader - Build Script
echo ============================================
echo.

REM ---------- Le a versao ----------
if not exist "VERSION" (
    echo [ERRO] Arquivo VERSION nao encontrado na raiz do projeto.
    pause
    exit /b 1
)

set /p APP_VERSION=<VERSION
REM Remove espacos e quebras de linha
for /f "tokens=*" %%a in ("!APP_VERSION!") do set APP_VERSION=%%a

if "!APP_VERSION!"=="" (
    echo [ERRO] Arquivo VERSION esta vazio.
    pause
    exit /b 1
)

echo Versao a buildar: !APP_VERSION!
echo.

REM ---------- Define paths ----------
set RELEASES_ROOT=C:\Users\woltr\OneDrive\Documents\Apps\Autodrive Uploader
set RELEASE_DIR=!RELEASES_ROOT!\!APP_VERSION!
set SOURCE_DIR=!RELEASE_DIR!\source

REM ---------- Verifica rclone ----------
if not exist "bin\rclone.exe" (
    echo [ERRO] bin\rclone.exe nao encontrado!
    echo.
    echo Baixe em https://rclone.org/downloads/
    echo Pegue "Windows / AMD - 64 Bit"
    echo Extraia o rclone.exe e coloque em bin\rclone.exe
    echo.
    pause
    exit /b 1
)

REM ---------- Confirma sobrescrita se versao ja existe ----------
if exist "!RELEASE_DIR!" (
    echo [AVISO] A pasta da versao !APP_VERSION! ja existe:
    echo   !RELEASE_DIR!
    echo.
    set /p CONFIRM="Sobrescrever? (s/N): "
    if /i not "!CONFIRM!"=="s" (
        echo Build cancelado.
        pause
        exit /b 0
    )
    echo Removendo pasta antiga...
    rmdir /s /q "!RELEASE_DIR!"
)

REM ---------- Cria estrutura de pastas ----------
echo [1/6] Criando estrutura de pastas...
mkdir "!RELEASE_DIR!" 2>nul
mkdir "!SOURCE_DIR!" 2>nul

REM ---------- Cria/usa venv ----------
if not exist ".venv" (
    echo [2/6] Criando ambiente virtual Python...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar venv. Python esta instalado?
        pause
        exit /b 1
    )
) else (
    echo [2/6] Ambiente virtual ja existe, pulando criacao.
)

REM ---------- Instala dependencias ----------
echo [3/6] Instalando dependencias...
call .venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

REM ---------- Limpa builds anteriores ----------
echo [4/6] Limpando build temporario anterior...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM ---------- Compila ----------
echo [5/6] Compilando .exe...
pyinstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERRO] Falha no PyInstaller.
    pause
    exit /b 1
)

if not exist "dist\AutoDriveUploader.exe" (
    echo [ERRO] .exe nao foi gerado.
    pause
    exit /b 1
)

REM ---------- Copia output e source pra pasta de release ----------
echo [6/6] Organizando release !APP_VERSION!...

REM Copia o .exe pra raiz da pasta de release
copy /y "dist\AutoDriveUploader.exe" "!RELEASE_DIR!\AutoDriveUploader.exe" >nul

REM Copia source completo (incluindo rclone.exe na pasta bin/)
robocopy . "!SOURCE_DIR!" /E /XD .venv build dist __pycache__ .git "!RELEASES_ROOT!" /XF *.pyc >nul

REM Copia/gera CHANGELOG dessa versao
if exist "CHANGELOG.md" (
    copy /y "CHANGELOG.md" "!RELEASE_DIR!\CHANGELOG.md" >nul
) else (
    echo [AVISO] CHANGELOG.md nao encontrado na raiz, gerando template vazio.
    echo # AutoDrive Uploader v!APP_VERSION! > "!RELEASE_DIR!\CHANGELOG.md"
    echo. >> "!RELEASE_DIR!\CHANGELOG.md"
    echo Build em %DATE% %TIME% >> "!RELEASE_DIR!\CHANGELOG.md"
)

echo.
echo ============================================
echo   Build !APP_VERSION! concluido!
echo ============================================
echo.
echo Local: !RELEASE_DIR!
echo.
echo Estrutura:
echo   !RELEASE_DIR!\
echo     ^|-- AutoDriveUploader.exe
echo     ^|-- CHANGELOG.md
echo     ^|-- source\          (backup do codigo fonte)
echo.

REM Abre a pasta da release no Explorer
explorer "!RELEASE_DIR!"

pause
