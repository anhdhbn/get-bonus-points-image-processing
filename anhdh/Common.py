import os
from pathlib import Path

class Common(object):
    def __init__(self, img_path):
        self.output = "out"
        self.img_path = img_path
        self.basename = os.path.basename(self.img_path)
        self.name = f"{self.basename.split('.')[0]}"
        self.folder = os.path.join(Path(self.img_path).parent, self.output)
        self.folder_process = os.path.join(self.folder, f"process_{self.name}")
        self.raster_folder = os.path.join(self.folder_process, "raster")
        self.jpg_folder = os.path.join(self.folder_process, "jpg")
        self.matches_folder = os.path.join(self.folder, f"matches_{self.name}")

        self.mkdir(self.output)
        self.mkdir(self.folder)
        self.mkdir(self.folder_process)
        self.mkdir(self.raster_folder)
        self.mkdir(self.jpg_folder)
        self.mkdir(self.matches_folder)

    def mkdir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)