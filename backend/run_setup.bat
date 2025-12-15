@echo off
cd /d "%~dp0"
python setup_export_features.py > setup_output.txt 2>&1
type setup_output.txt


