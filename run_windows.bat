@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 goto with_py
where python >nul 2>&1
if not errorlevel 1 goto with_python
echo Can cai dat Python 3 tai https://www.python.org/downloads/
echo Khi cai dat, chon Add python.exe to PATH.
goto end

:with_py
py -3 server.py
goto end

:with_python
python server.py

:end
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
