@echo off
setlocal
set "HERE=%~dp0"
set "PYTHONPATH=%HERE%src"
python -m essence_omega_os demo --output "%HERE%outputs\demo"
endlocal
