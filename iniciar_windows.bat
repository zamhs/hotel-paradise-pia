@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto error
.venv\Scripts\python.exe manage.py datos_demo
if errorlevel 1 goto error
.venv\Scripts\python.exe abrir_paradise.py %*
if errorlevel 1 goto error
goto fin
:error
echo No se pudo preparar el sistema. Comprueba que Python esta instalado.
pause
:fin
