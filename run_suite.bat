@echo off
setlocal
set "HERE=%~dp0"
set "PYTHONPATH=%HERE%src"
python -m essence_omega_os suite --examples "%HERE%examples" --output "%HERE%outputs\reference"
endlocal
