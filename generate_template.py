import os
import json
from pathlib import Path
from typing import List, Dict


qa_section = """
--------------------
<Q-sub>: {{ None }}
<A-sub>: {{ None }}
<ANS>: {{ + }}

"""


def template_video_section(filename: str, duration: str, dimension: str) -> str:
    """ Generate the video section string."""
    vid_section = ""
    vid_section = f"~~~~~~~~~~~~~~~~~~~~ {filename} ~~~~~~~~~~~~~~~~~~~~\n"
    vid_section += f"<LENGTH={duration}>\n"
    vid_section += f"<DIM={dimension}>\n"
    vid_section += "<PERSPECTIVE>: {{  }}\n"
    vid_section += "<RE_TRIM>: {{ START_TS, END_TS }}\n"
    vid_section += "<CRITICAL_POINT>: {{ TS }}\n"
    vid_section += qa_section * 5

    return vid_section


def generate_qa_template_from_json(json_fp: str):
    json_fp = Path(json_fp)
    if not json_fp.is_file():
        raise Exception(f"ERR: `{json_fp}` does not exist")

    head, tail = os.path.split(json_fp)
    name, ext = os.path.splitext(tail)
    if ext != ".json":
        raise Exception(f"ERR: `{json_fp}` is not a json file")

    export_fp = Path(os.path.join(head, "qa_label.txt"))

    with json_fp.open() as f:
        vid_lst: List[Dict] = json.load(f)

    string_lst_to_write: List[str] = []

    for video in vid_lst:
        filename = video.get("filename")
        duration = f"{video.get('duration')}s"
        dimension = f"(W){video.get('width')} x (H){video.get('height')}"
        string_lst_to_write.append(
            template_video_section(filename, duration, dimension)
        )

    with export_fp.open(mode="w") as f:
        f.write("\n\n".join(string_lst_to_write))
    print(f"successfully generated: {export_fp}")


if __name__ == "__main__":
    generate_qa_template_from_json("example/video_metadata_lst.json")
