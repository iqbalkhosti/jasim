SCRIPT_NAME = Car Catalog
ENTRY_SCRIPT = Front_Layout.py
BUILD_DIR = dist
PYINSTALLER_FLAGS = --onefile --noconsole --hidden-import=tkVideoPlayer
PYPATH = python

all: build

# Build the executable using PyInstaller
build:
	$(PYPATH) -m PyInstaller $(PYINSTALLER_FLAGS) $(ENTRY_SCRIPT)

# Clean up build artifacts (Windows & Unix compatible)
clean:
	@if exist build rmdir /s /q build
	@if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
	@if exist $(SCRIPT_NAME).spec del $(SCRIPT_NAME).spec

# Rebuild the executable
rebuild: clean build

