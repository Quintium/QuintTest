# Specify the path of the scripts that you want to build
QUINTTEST_SCRIPT = QuintTest.py
CLOPQUINTTEST_SCRIPT = CLOP_QuintTest.py

# Specify the PyInstaller options that you want to use
PYINSTALLER_OPTS = --onefile --clean --noconfirm --distpath build --workpath temp

# Define the "build" target for the makefile
QuintTest: $(SCRIPT)
	pyinstaller $(PYINSTALLER_OPTS) $(QUINTTEST_SCRIPT)

CLOP_QuintTest: $(SCRIPT)
	pyinstaller $(PYINSTALLER_OPTS) $(CLOPQUINTTEST_SCRIPT)

