import ntpath
import png
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QListWidget,
)

# Only needed for access to command line arguments
import sys

import os

from pathlib import Path

# 1. Get the path to the user's home directory.
home_directory = Path.home()

# 2. Get the full path to the Pictures folder.
pictures_directory = home_directory / 'Pictures' 

folder_path = f"{pictures_directory}/Converted"

os.makedirs(folder_path, exist_ok=True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.files = []
        self.file_num = len(self.files)

        self.setWindowTitle("2bpp Image Converter")

        self.resize(400, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.link_label = QLabel()
        self.link_label.setTextFormat(Qt.RichText)
        self.link_label.setText("<a href=\"https://ko-fi.com/mintshard\">Buy me a coffee</a>")
        self.link_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.link_label)

        self.git_label = QLabel()
        self.git_label.setTextFormat(Qt.RichText)
        self.git_label.setText("<a href=\"https://github.com/mstandif\">GitHub</a>")
        self.git_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.git_label)

        self.select_button = QPushButton("Select Multiple Files")
        self.select_button.clicked.connect(self.on_select_files_button_clicked)
        self.layout.addWidget(self.select_button)

        self.list_label = QLabel("Number of files selected: 0")
        self.layout.addWidget(self.list_label)

        self.file_list_widget = QListWidget()
        self.layout.addWidget(self.file_list_widget)

        self.convert_button = QPushButton("Convert Images")
        self.convert_button.clicked.connect(self.on_select_convert_files_button_clicked)
        self.layout.addWidget(self.convert_button)

        self.finished_label = QLabel("")
        self.layout.addWidget(self.finished_label)

    def update_text(self):
        self.list_label.setText(f"Number of files selected: {len(self.files)}")

    def update_finished_text(self, text):
        self.finished_label.setText(text)

    def on_select_convert_files_button_clicked(self):
        for file in self.files:
            image = PNGImageProcessor(file)
            width, height, pixels, metadata, index = image.read_image()
            indexed_pixels = image.reindex_bytearrays(pixels, index)
            new_pixels = image.invert_bytearrays(indexed_pixels)
            new_metadata = metadata#{'greyscale': True, 'alpha': False, 'planes': 1, 'bitdepth': 2, 'interlace': 0, 'size': (width, height)}
            image.write_image(image.output_address, width, height, new_pixels, new_metadata)
        
        self.update_finished_text("Conversion Finished!")
    
    def set_metadata(self, metadata):
        self.metadata = metadata
        print(self.metadata)

    def on_select_files_button_clicked(self):
        # Open the file dialog to select multiple files
        # The arguments are: parent, caption, directory, filter
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",  # Start in the current directory
            "All Files (*.*);;Text Files (*.txt);;Python Files (*.py)"
        )

        if filenames:  # If files were selected
            self.file_list_widget.clear()  # Clear previous selections
            self.files.clear()  # Clear previous file list  
            for filename in filenames:
                self.file_list_widget.addItem(filename) # Add each selected file to the list widget
                self.files.append(filename)  # Store the filenames in the list
            self.update_text()  # Update the label with the number of selected files
            self.update_finished_text("")  # Clear finished text


class PNGImageProcessor:
    def __init__(self, address):
        self.address = address
        self.filename = path_leaf(address)
        self.output_address = f"{folder_path}\\{self.filename}"

    def read_image(self):
        reader = png.Reader(filename=self.address)
        width, height, pixels, metadata = reader.read()
        #print(metadata['palette'])
        index = palette_order(metadata['palette'])
        return width, height, pixels, metadata, index
    
    def write_image(self, output_file, width, height, pixels, metadata):
        writer = png.Writer(width, height, greyscale=True, bitdepth=2)
        with open(output_file, 'wb') as f:
            writer.write(f, pixels)

    def reindex_bytearrays(self, pixels, index):
        pixel_list = list(pixels)
        new_list = []
        for x in pixel_list:
            my_bytearray = bytearray()
            for byte in x:
                if byte == 0:
                    my_bytearray.append(index[0])
                elif byte == 1:
                    my_bytearray.append(index[1])
                elif byte == 2:
                    my_bytearray.append(index[2])
                elif byte == 3:
                    my_bytearray.append(index[3])
            new_list.append(my_bytearray)
        return np.array(new_list)

    def invert_bytearrays(self, pixels):
        pixel_list = list(pixels)
        new_list = []
        for x in pixel_list:
            my_bytearray = bytearray()
            for byte in x:
                if byte == 0:
                    my_bytearray.append(3)
                elif byte == 1:
                    my_bytearray.append(2)
                elif byte == 2:
                    my_bytearray.append(1)
                elif byte == 3:
                    my_bytearray.append(0)
            new_list.append(my_bytearray)
        return np.array(new_list)

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.


def printPNGInfo(width, height, pixels, metadata):
    # Access basic information
    print(f"Image size: {width}x{height}")
    print(f"Metadata: {metadata}")

    # Convert pixels to list
    pixel_list = list(pixels)
    print(pixel_list)


def convert_palette_to_grayscale(palette):
    new_palette = []
    for item in palette:
        r = item[0]
        g = item[1]
        b = item[2]
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        new_palette.append((gray,gray,gray))
    return new_palette


def palette_order(palette):
    #print(palette)
    bw_palette = convert_palette_to_grayscale(palette[0:4])
    #print(bw_palette)
    colors = []
    color_index = []
    for color in bw_palette:
        colors.append(color[0])

    for color in colors:
        index = 0
        for i in range(len(colors)):
            if color < colors[i]:
                index += 1
        color_index.append(index)
    #print(color_index)
    return color_index


# Start the event loop.
app.exec()

# Your application won't reach here until you exit and the event
# loop has stopped.

