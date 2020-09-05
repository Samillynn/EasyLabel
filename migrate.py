import os
import json
import shutil
import subprocess
from pathlib import Path
import multiprocessing
from markkk.logger import logger
from typing import List, Dict, Tuple


def call_safe_copy(job: List):
    src = job[0]
    dest = job[1]
    safe_copy(src, dest)
    return dest


def safe_copy(src, dest):
    if not Path(src).exists():
        logger.error(f"safe_copy cannot be done, because source file {src} not found.")
        return
    if Path(dest).exists():
        logger.error(
            f"safe_copy cannot be done, because destination file {dest} already exist."
        )
        return
    try:
        subprocess.run(f"cp {str(src)} {str(dest)}")
        logger.debug(f"'{src}' has been copied to '{dest}'")
    except Exception as err:
        logger.error(f"Copy operation failed, reason: {err}")


def migrate_from_drive_to_local():
    base_path = Path("/home/UROP/shared_drive/Video_Folders/Trimmed_All_Videos")
    destination_folder = Path("/home/UROP/data_urop/all_videos_local")
    assert base_path.is_dir()
    assert destination_folder.is_dir()
    migration_list = []

    for folder in os.listdir(base_path):
        folder_path = base_path / folder
        if not folder_path.is_dir():
            logger.info(f"Skip {folder_path}")
            continue

        logger.debug(folder)

        if folder.startswith("bilibili_"):
            # folder_num = int(folder[-3:])
            # if folder_num <= 80:
            #     continue

            folder_path = base_path / folder
            assert folder_path.is_dir()

            for file in os.listdir(folder_path):
                if file[-4:] != ".mp4":
                    logger.info(f"Skip {file}")
                    continue
                new_name = "b_" + file
                video_filepath: Path = folder_path / file
                dst_path: Path = destination_folder / new_name
                logger.debug(f"{video_filepath} -> {dst_path}")
                migration_list.append([video_filepath, dst_path])

        elif folder.startswith("youtube_"):
            # folder_num = int(folder[-3:])
            # if folder_num <= 10:
            #     continue

            folder_path = base_path / folder
            assert folder_path.is_dir()

            for file in os.listdir(folder_path):
                if file[-4:] != ".mp4":
                    logger.info(f"Skip {file}")
                    continue
                new_name = "y_" + file
                video_filepath: Path = folder_path / file
                dst_path: Path = destination_folder / new_name
                logger.debug(f"{video_filepath} -> {dst_path}")
                migration_list.append([video_filepath, dst_path])

        elif folder.endswith("yutian"):
            folder_path = base_path / folder
            assert folder_path.is_dir()

            for file in os.listdir(folder_path):
                if file[-4:] != ".mp4":
                    logger.info(f"Skip {file}")
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
                migration_list.append([video_filepath, dst_path])

    logger.debug(f"Number of file to copy: {len(migration_list)}")
    proceed = input("Proceed? (y/n)")
    if proceed != "y":
        logger.warning("Abort")
        return
    logger.debug(json.dumps(migration_list, indent=4))
    proceed = input("Proceed? (y/n)")
    if proceed != "y":
        logger.warning("Abort")
        return
    pool = multiprocessing.Pool()
    result = pool.map(call_safe_copy, migration_list)
    print(list(result))


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
    joe_video_folder = Path(
        "/home/UROP/data_urop/Video_Folders_local/joe_videos/traffic_videos"
    )
    destination_folder = Path("/home/UROP/data_urop/unlabelled")
    assert joe_video_folder.is_dir()

    for file in os.listdir(joe_video_folder):
        if file[-4:] != ".mov":
            continue

        new_name = "j_" + file.lower()[4:-4] + ".mp4"
        file_in = str(joe_video_folder / file)
        file_out = str(destination_folder / new_name)
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


def migrate_3():
    base_path = Path("/home/UROP/data_urop/Video_Folders_local/Trimmed_All_Videos")
    destination_folder = Path("/home/UROP/data_urop/labelled")
    assert base_path.is_dir()
    assert destination_folder.is_dir()

    for folder in os.listdir(base_path):
        logger.debug(folder)
        if folder.startswith("bilibili_"):
            folder_num = int(folder[-3:])
            if folder_num > 80:
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
            if folder_num > 10:
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


if __name__ == "__main__":
    # convert_joe_vids_to_mp4()
    # run_stats()
    # migrate_3()
    migrate_from_drive_to_local()
