@echo off
start "Converter" cmd /k "python smart_engine\excel_to_json.py"
timeout /t 2 /nobreak > nul
start "Dashboard" cmd /k "python smart_engine\main.py"
exit
