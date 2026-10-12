@echo off
setlocal
cd /d "%~dp0"

set "BANKSHIELD_PYTHON="
if exist "%~dp0..\us\Scripts\python.exe" (
    set "BANKSHIELD_PYTHON=%~dp0..\us\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "BANKSHIELD_PYTHON=%~dp0.venv\Scripts\python.exe"
)

if not defined BANKSHIELD_PYTHON (
    echo No project Python environment was found.
    echo Follow the Windows setup instructions in README.md to create .venv and install requirements.txt.
    pause
    exit /b 1
)

"%BANKSHIELD_PYTHON%" -X utf8 -m streamlit run "%~dp0app.py" %*
set "BANKSHIELD_EXIT_CODE=%ERRORLEVEL%"
if not "%BANKSHIELD_EXIT_CODE%"=="0" (
    echo BankShield could not start. Review the error above and the setup instructions in README.md.
    pause
)
exit /b %BANKSHIELD_EXIT_CODE%
