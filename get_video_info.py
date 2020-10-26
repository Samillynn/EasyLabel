"""
depencency: ffmpeg

reference: https://trac.ffmpeg.org/wiki/FFprobeTips#FrameRate
"""

import subprocess
import shlex
import json
from pathlib import Path
import os
from markkk.logger import logger


def get_video_metadata(video_path: str) -> dict:

    # check if the file exist
    video_path = Path(video_path)
    if not video_path.is_file():
        logger.error(f"Invalid video_path: `{video_path}` does not exist.")
        raise Exception("Invalid video_path: file does not exist.")

    # check if it is a video file
    known_video_formats = (".mp4", ".flv", ".mov", ".avi", ".wmv", ".mkv")
    video_path_obs = video_path.resolve()
    head, tail = os.path.split(video_path_obs)
    name, ext = os.path.splitext(tail)
    if ext not in known_video_formats:
        logger.warning(f"Invalid video_path: `{tail}` is not a known video format.")
        raise Exception(f"Invalid video_path: `{tail}` is not a known video format.")

    command_template = "ffprobe -v error -select_streams v:0 -show_entries stream=width,height,avg_frame_rate,duration -of json"
    args = shlex.split(command_template)
    args.append(str(video_path))
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    out: bytes = proc.communicate()[0]
    json_string: str = out.decode("utf-8").strip()

    # logger.debug(json_string)

    json_obj: dict = json.loads(json_string)

    streams: list = json_obj.get("streams", [])
    if len(streams) == 1:
        _data = streams[0]
    elif len(streams) == 0:
        raise Exception()
    else:
        _data: dict = streams[0]
        logger.info(f"More than one stream is found at {video_path}")

    width: int = _data.get("width")
    height: int = _data.get("height")
    ratio = width / height
    avg_frame_rate: str = _data.get("avg_frame_rate")
    frame_rate: int = round(eval(avg_frame_rate)) if avg_frame_rate else None
    duration: float = round(float(_data.get("duration")), 2)

    video_metadata: dict = {
        "filepath": str(video_path_obs),
        "filename": name,
        "ext": ext,
        "width": width,
        "height": height,
        "ratio": ratio,  # width / height
        "duration": duration,  # in number of seconds
        "fps": frame_rate,  # frame per seconds
        "avg_frame_rate": avg_frame_rate,
    }

    # logger.debug(json.dumps(video_metadata, indent=4))
    return video_metadata


def generate_video_list(video_folder: str):
    """
    get metadata of all videos inside a video_folder, and
    write to `video_metadata_lst.json` and save it to the video_folder
    existing `video_metadata_lst.json` inside the target folder will be overwritten
    """
    video_folder = Path(video_folder)
    if not video_folder.is_dir():
        raise ValueError(f"'{dir}' is not a valid path to a folder.")

    video_list: list = []

    for file in os.listdir(video_folder):
        logger.debug(file)
        video_filepath = os.path.join(video_folder, file)
        if os.path.isfile(video_filepath):
            try:
                video_metadata: dict = get_video_metadata(video_filepath)
                video_list.append(video_metadata)
            except Exception as err:
                logger.error(f"Error for {video_filepath}: {err}")
                continue

    # sort video list by video name alphabetically
    video_list = sorted(video_list, key=lambda x: x["filename"])

    print(f"\nTotal number of videos: {len(video_list)}\n")

    export_filepath = video_folder / "video_metadata_lst.json"
    with export_filepath.open(mode="w") as f:
        f.write(json.dumps(video_list, indent=4))


if __name__ == "__main__":
    # single_video_path = "0PgyK_oW1Vg.mp4"
    # get_video_metadata(single_video_path)
    VIDEO_FOLDER = "/data/urop/all_videos_final"
    generate_video_list(VIDEO_FOLDER)
