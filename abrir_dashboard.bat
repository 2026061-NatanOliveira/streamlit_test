@echo off
title Dashboard - Integrated CA2
cd /d "%~dp0"
echo Iniciando o dashboard... (feche esta janela ou use Ctrl+C para encerrar)
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8050"
py -3.14 app.py
echo.
echo O dashboard foi encerrado.
pause
