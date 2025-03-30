@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: Настройки
set "REPO_OWNER=AntonTriceps"
set "REPO_NAME=InboGame"
set "BRANCH=main"
set "VERSION_FILE=Version.txt"

title Update.bat

:: Получаем удаленную версию
echo Проверяем обновления...
for /f "delims=" %%A in ('powershell -command "(Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/%REPO_OWNER%/%REPO_NAME%/%BRANCH%/%VERSION_FILE%' -UseBasicParsing).Content.Trim()" 2^>nul') do (
    set "remote_version=%%A"
)

if not defined remote_version (
    echo Не удалось проверить версию
    goto :browser_fallback
)

:: Извлекаем номер версии
for /f "tokens=2" %%v in ("%remote_version%") do set "version=%%v"

:: Локальная версия
if exist "%VERSION_FILE%" (
    set /p local_version=<%VERSION_FILE%
) else (
    set "local_version=Version 0.0"
)

:: Сравнение версий
if "%local_version%" == "%remote_version%" (
    echo Версия актуальна: %remote_version%
    pause
    exit /b 0
)

echo.
echo Текущая версия: %local_version%
echo Новая версия:   %remote_version%
echo.

:ask
set "choice="
set /p "choice=Скачать обновление? (Y/N): "
if /i "%choice%"=="Y" goto download
if /i "%choice%"=="N" exit /b 0
goto ask

:download
set "folder=%REPO_NAME%_V%version%"

:: Проверка Git и PowerShell
where git >nul 2>&1
if %errorlevel% equ 0 (
    echo Используем Git...
    git clone https://github.com/%REPO_OWNER%/%REPO_NAME%.git "%folder%"
    goto :check_result
)

where powershell >nul 2>&1
if %errorlevel% equ 0 (
    echo Скачиваем ZIP...
    set "zip_url=https://github.com/%REPO_OWNER%/%REPO_NAME%/archive/refs/heads/%BRANCH%.zip"
    powershell -command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest '%zip_url%' -OutFile '%REPO_NAME%.zip'; Expand-Archive -Path '%REPO_NAME%.zip' -DestinationPath '%folder%'; Remove-Item '%REPO_NAME%.zip'"
    goto :check_result
)

:browser_fallback
echo Открываю GitHub в браузере...
start "" "https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest"
exit /b 0

:check_result
if exist "%folder%\" (
    echo Успешно! Папка: "%folder%"
) else (
    echo Ошибка загрузки
)
pause
endlocal