# Specify the path of the script that you want to build
SCRIPT = src/QuintTest.py

# Specify the PyInstaller options that you want to use
PYINSTALLER_OPTS = --onefile --clean --noconfirm --distpath build --workpath temp

# Define the "build" target for the makefile
build:
	pyinstaller $(PYINSTALLER_OPTS) $(SCRIPT)