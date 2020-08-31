from pathlib import Path
import os
import shutil
from markkk.logger import logger


def main():
    base_path = Path("/home/UROP/data_urop/Video_Folders_local/Trimmed_All_Videos")
    destination_folder = Path("/home/UROP/data_urop/unlabelled")
    assert base_path.is_dir()
    assert destination_folder.is_dir()

    for folder in os.listdir(base_path):
        logger.debug(folder)
        if folder.startswith("bilibili_"):
            folder_num = int(folder[-3:])
            if folder_num <= 80:
                continue

            folder_path = base_path / folder
            assert folder_path.is_dir()

            for file in os.listdir(folder_path):
                if file[-4:] != ".mp4":
                    continue
                new_name = "b_" + file
                video_filepath: Path = folder_path / file
                dst_path: Path = destination_folder / new_name
                logger.debug(f"{video_filepath} -> {dst_path}")
                shutil.move(video_filepath, dst_path)

        elif folder.startswith("youtube_"):
            folder_num = int(folder[-3:])
            if folder_num <= 10:
                continue

            folder_path = base_path / folder
            assert folder_path.is_dir()

            for file in os.listdir(folder_path):
                if file[-4:] != ".mp4":
                    continue
                new_name = "y_" + file
                video_filepath: Path = folder_path / file
                dst_path: Path = destination_folder / new_name
                logger.debug(f"{video_filepath} -> {dst_path}")
                shutil.move(video_filepath, dst_path)

        elif folder.endswith("yutian"):
            folder_path = base_path / folder
            assert folder_path.is_dir()

            for file in os.listdir(folder_path):
                if file[-4:] != ".mp4":
                    continue
                new_name = ""
                for i in file.lower():
                    if i == "(":
                        new_name += "_"
                    elif i == ")":
                        pass
                    else:
                        new_name += i
                new_name = "c_" + new_name
                video_filepath: Path = folder_path / file
                dst_path: Path = destination_folder / new_name
                logger.debug(f"{video_filepath} -> {dst_path}")
                shutil.move(video_filepath, dst_path)


if __name__ == "__main__":
    main()
