Packages used: pyinstaller

If not working properly, install Visual C++ Redistrubutable

Usage:
1. Install Python 3.10+ and pip.
2. (Optional) Create and activate a virtual environment.
3. Install PyInstaller: pip install pyinstaller
4. Run the script directly: python passgen.py

Build (Windows):
1. Ensure Visual C++ Redistributable is installed.
2. From this folder, run: pyinstaller passgen.spec
3. The built executable will be created under dist/.

Notes:
- If PyInstaller build fails, try upgrading: pip install --upgrade pyinstaller
- Run from a terminal with permissions to write to build/ and dist/.