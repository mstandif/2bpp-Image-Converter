from cx_Freeze import setup, Executable
import sys

# Define the base for the executable
# 'None' for console application, 'Win32GUI' for a GUI application on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Options for the build process
build_exe_options = {
    "packages": ["ntpath","png","numpy","PySide6"],  # Include specific packages
    "includes": ["PySide6.QtCore", "PySide6.QtWidgets"],
    "include_files": [],      # Include additional files/folders
}

setup(
    name="2bpp Image Converter",
    version="1.0",
    description="Converts images to 2bpp format",
    options={"build_exe": build_exe_options},
    executables=[Executable("2bpp Image Converter.py", base=base)]
)