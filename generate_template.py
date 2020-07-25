import os
import json
from pathlib import Path
from typing import List, Dict, Set
from my_logger import logger as _logger
from qa_class import QASet, QASetPool, get_qa_pool_from_json
from markkk.pyutils.check_text_encoding import is_ascii, ensure_no_zh_punctuation

QA_BANK_JSON_FILEPATH = "example/qa_bank_sample_2.json"
qa_pool: QASetPool = get_qa_pool_from_json(QA_BANK_JSON_FILEPATH)
qa_section = """
--------------------{{  }} # [1-6] or [d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}

"""


def auto_populated_qa_section(q_num: int, type=None) -> str:
    qa_sections: str = ""
    qa_sets: Set[QASet] = qa_pool.random_draw_multiple(q_num=q_num, type=type)

    for qa_set in qa_sets:
        qa: Tuple[str, Tuple] = qa_set.get()
        qa_sections += "!--------------------{{ auto }}\n"
        qa_sections += "<QASet_ID>: {{ auto }}\n"
        qa_sections += "<ANS>: {{  }}\n"
        qa_sections += f"{qa[0]}\n"
        for option in qa[1]:
            qa_sections += f"{option}\n"
        qa_sections += "\n"

    return qa_sections


def template_video_section(filename: str, duration: str, dimension: str) -> str:
    """ Generate the video section string."""
    vid_section = ""
    vid_section = f"~~~~~~~~~~~~~~~~~~~~ {filename} "
    vid_section += "~" * (80 - 22 - len(filename)) + "\n"
    vid_section += f"<LENGTH> {duration}\n"
    vid_section += f"<DIM> {dimension}\n\n"
    vid_section += "<PERSPECTIVE>: {{  }}\n"
    vid_section += "<RE_TRIM>: {{ START_TS, END_TS }}\n"
    vid_section += "<CRITICAL_POINT>: {{ TS }}\n\n"
    vid_section += auto_populated_qa_section(6)
    vid_section += qa_section * 3

    return vid_section


def bump_version(filepath: Path) -> Path:
    head, tail = os.path.split(filepath)
    name, ext = os.path.splitext(tail)
    suffix = 1
    while filepath.is_file():
        _logger.info(f"{filepath} already exist")
        suffix += 1
        new_name = f"{name}_v{str(suffix)}{ext}"
        filepath = Path(head) / new_name
    return filepath


def generate_template_from_metadata_lst(json_fp: str):
    json_fp = Path(json_fp)
    if not json_fp.is_file():
        _logger.error(f"`{json_fp}` does not exist")
        raise Exception(f"ERR: `{json_fp}` does not exist")

    head, tail = os.path.split(json_fp)
    name, ext = os.path.splitext(tail)
    if ext != ".json":
        _logger.error(f"`{json_fp}` is not a json file")
        raise Exception(f"ERR: `{json_fp}` is not a json file")

    export_fp = Path(os.path.join(head, "qa_label_template.txt"))
    export_fp: Path = bump_version(export_fp)

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
        to_write = "\n\n".join(string_lst_to_write)
        if not is_ascii(to_write):
            _logger.warning("Text to write contains non-ASCII characters.")
            _logger.warning("Template generation may fail.")
            to_write = ensure_no_zh_punctuation(to_write)
        try:
            f.write(to_write)
            _logger.debug(
                f"Successfully generated QA Label Template:\n         {export_fp.resolve()}"
            )
        except Exception as err:
            _logger.error(
                f"Encounter an error while generating template, details:\n{err}"
            )


if __name__ == "__main__":
    generate_template_from_metadata_lst("example/video_metadata_lst.json")
