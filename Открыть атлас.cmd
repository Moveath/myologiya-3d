@echo off
cd /d "%~dp0"
py -3 scripts\launch_atlas.py
if errorlevel 1 pause
