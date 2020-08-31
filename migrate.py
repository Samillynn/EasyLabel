import os
import json
import shutil
import subprocess
from pathlib import Path

from markkk.logger import logger


def migrate_1():
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


def convert_joe_vids_to_mp4():
    joe_video_folder = Path("/home/UROP/data_urop/unlabelled/joe")
    assert joe_video_folder.is_dir()

    for file in os.listdir(joe_video_folder):
        if file[-4:] != ".mov":
            continue

        new_name = file[-4:] + ".mp4"
        file_in = str(joe_video_folder / file)
        file_out = str(joe_video_folder.parent / new_name)
        logger.debug(f"{file_in} -> {file_out}")

        subprocess.run(
            f'ffmpeg -loglevel warning -i "{file_in}" -vcodec copy -acodec copy "{file_out}"',
            shell=True,
            # stdout=subprocess.PIPE,
        )


def migrate_2():
    joe_video_folder = Path(
        "/data/urop/gs-samill/Video_Folders/joe_videos/traffic_videos"
    )
    destination_folder = Path("/home/UROP/data_urop/unlabelled/joe")
    assert joe_video_folder.is_dir()
    assert destination_folder.is_dir()

    for file in os.listdir(joe_video_folder):
        if file[-4:] != ".mov":
            continue
        new_name = "j_" + file.lower()[4:]
        video_filepath: Path = joe_video_folder / file
        dst_path: Path = destination_folder / new_name
        logger.debug(f"{video_filepath} -> {dst_path}")
        shutil.copy2(video_filepath, dst_path)


def run_stats():
    folder = Path("/home/UROP/data_urop/unlabelled")
    from get_video_info import generate_video_list

    generate_video_list(folder)


if __name__ == "__main__":
    migrate_2()
    convert_joe_vids_to_mp4()
    run_stats()
