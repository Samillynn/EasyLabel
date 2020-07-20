import os
import json
from pathlib import Path
from typing import List, Dict
from qa_class import QASet, QASetPool, get_qa_pool_from_json

QA_BANK_JSON_FILEPATH = "example/qa_bank_sample.json"

qa_section = """
--------------------{{  }} # [1-6] or [d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}

"""

qa_pool = QASetPool()
qa_pool: QASetPool = get_qa_pool_from_json(QA_BANK_JSON_FILEPATH)


def auto_populated_qa_section(num: int) -> str:
    qa_sections: str = ""
    # print(len(qa_pool._pool))

    for _ in range(num):
        qa_set: QASet = qa_pool.random_draw()
        qa: Tuple[str, Tuple] = qa_set.get()
        qa_sections += "--------------------{{ auto }}\n"
        qa_sections += "<QASet_ID>: {{ auto }}\n"
        qa_sections += "<QASet_ID>: {{ None }}\n"
        qa_sections += f"{qa[0]}\n"
        for option in qa[1]:
            qa_sections += f"{option}\n"
        qa_sections += "\n\n"

    return qa_sections


def template_video_section(filename: str, duration: str, dimension: str) -> str:
    """ Generate the video section string."""
    vid_section = ""
    vid_section = f"~~~~~~~~~~~~~~~~~~~~ {filename} "
    vid_section += "~" * (80 - 22 - len(filename)) + "\n"
    vid_section += f"<LENGTH> {duration}\n"
    vid_section += f"<DIM> {dimension}\n"
    vid_section += "<PERSPECTIVE>: {{  }}\n"
    vid_section += "<RE_TRIM>: {{ START_TS, END_TS }}\n"
    vid_section += "<CRITICAL_POINT>: {{ TS }}\n"
    vid_section += auto_populated_qa_section(5)
    vid_section += qa_section * 3

    return vid_section


def generate_qa_template_from_json(json_fp: str):
    json_fp = Path(json_fp)
    if not json_fp.is_file():
        raise Exception(f"ERR: `{json_fp}` does not exist")

    head, tail = os.path.split(json_fp)
    name, ext = os.path.splitext(tail)
    if ext != ".json":
        raise Exception(f"ERR: `{json_fp}` is not a json file")

    export_fp = Path(os.path.join(head, "qa_label_template.txt"))

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
