import os
import json
import shutil
from pathlib import Path


def main():
    to_folder_base = Path("/home/UROP/shared_drive/Video_Folders/Trimmed_All_Videos")
    json_filepath = Path(
        "/home/UROP/shared_drive/Video_Folders/bilibili/video_metadata_lst.json"
    )
    assert json_filepath.is_file()

    with json_filepath.open() as f:
        vid_lst: list = json.load(f)

    vid_lst = sorted(vid_lst, key=lambda x: (x["duration"], x["filename"]))

    counter = 0
    folder_count = 1
    folder_prefix = "bilibili_"
    # folder_prefix = "youtube_"
    sub_list = []
    dst_folder_path = Path("")

    for video in vid_lst:
        counter += 1

        if counter == 1:
            # clear sub list
            sub_list = []
            # append to sub list
            sub_list.append(video)

            # create a new folder
            if folder_count <= 9:
                folder_suffix = f"00{str(folder_count)}"
            elif 10 <= folder_count <= 99:
                folder_suffix = f"0{str(folder_count)}"
            else:
                folder_suffix = str(folder_count)
            # new folder name
            dst_folder_name = f"{folder_prefix}{folder_suffix}"
            dst_folder_path: Path = to_folder_base / dst_folder_name

        elif 1 < counter <= 99:
            # append to sub list
            sub_list.append(video)
            pass

        elif counter == 100:
            # append to sub list
            sub_list.append(video)
            # set counter to zero
            counter = 0
            # folder_count next
            folder_count += 1

            out_json_fp: Path = dst_folder_path / "video_metadata_lst.json"
            with out_json_fp.open(mode="w") as f:
                print(">>>")
                print(dst_folder_name)
                print(len(sub_list))
                f.write(json.dumps(sub_list))
                print(f"Generated: {out_json_fp}")

        else:
            print("unexpected: something is wrong")
            return

    out_json_fp: Path = dst_folder_path / "video_metadata_lst.json"
    with out_json_fp.open(mode="w") as f:
        print(">>>")
        print(dst_folder_name)
        print(len(sub_list))
        f.write(json.dumps(sub_list))
        print(f"Generated: {out_json_fp}")


if __name__ == "__main__":
    main()
