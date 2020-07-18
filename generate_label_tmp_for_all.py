import os
import json
import shutil
from pathlib import Path
from generate_template import generate_qa_template_from_json

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
        sys_name_list = os.listdir(folder_path)
        sys_name_list.remove("video_metadata_lst.json")
        assert len(sys_name_list) == len(name_list)
        assert sys_name_list == name_list

        # generate label template
        generate_qa_template_from_json(sublist_fp)


if __name__ == "__main__":
    main()
