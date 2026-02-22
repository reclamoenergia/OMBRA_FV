@echo off
pip install -r ..\requirements.txt pyinstaller
python ..\demo\generate_demo_data.py
pyinstaller --onefile -n engine ..\api\main.py
