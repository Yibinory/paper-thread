@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
pushd "%~dp0"
if errorlevel 1 exit /b 1

if exist ".venv\Scripts\python.exe" goto venv
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 goto pylauncher
python -c "import sys" >nul 2>&1
if not errorlevel 1 goto python
echo PaperThread requires Python 3.10 or newer.
echo Install Python from https://www.python.org/downloads/ and enable Add Python to PATH.
set "paperthread_exit=1"
goto done

:venv
".venv\Scripts\python.exe" -X utf8 scripts\start.py %*
set "paperthread_exit=%errorlevel%"
goto done

:pylauncher
py -3 -X utf8 scripts\start.py %*
set "paperthread_exit=%errorlevel%"
goto done

:python
python -X utf8 scripts\start.py %*
set "paperthread_exit=%errorlevel%"

:done
popd
if not "%paperthread_exit%"=="0" if not defined PAPERTHREAD_NO_PAUSE pause
exit /b %paperthread_exit%
