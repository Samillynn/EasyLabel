import os
import json
import shutil
from pathlib import Path

BASE_DIR = Path("/home/UROP/shared_drive/Video_Folders/Trimmed_All_Videos")


def main():
    for folder in os.listdir(BASE_DIR):
        print(folder)
        folder_path: Path = BASE_DIR / folder
        assert folder_path.is_dir()
        sublist_fp: Path = folder_path / "video_metadata_lst.json"
        assert sublist_fp.is_file()
        with sublist_fp.open() as f:
            vid_lst: list = json.load(f)
            name_list = [f'{video["filename"]+video["ext"]}' for video in vid_lst]

        for video in os.listdir(folder_path):
            assert video in name_list
            print("True")


if __name__ == "__main__":
    main()
