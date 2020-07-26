import os
import json
import shutil
from pathlib import Path
from qa_template_gen import generate_template

BASE_DIR = Path("/home/UROP/shared_drive/Video_Folders/Trimmed_All_Videos")


def main():
    for folder in os.listdir(BASE_DIR):
        print(folder)
        folder_path: Path = BASE_DIR / folder
        assert folder_path.is_dir()

        sublist_fp: Path = folder_path / "video_metadata_lst.json"
        assert sublist_fp.is_file()

        # generate label template
        generate_template(metadata_lst_filepath=sublist_fp)


if __name__ == "__main__":
    main()
