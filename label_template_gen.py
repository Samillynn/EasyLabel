import os
import json
import random
from pathlib import Path
from typing import List, Dict, Set

from markkk.pyutils.check_text_encoding import is_ascii, ensure_no_zh_punctuation

from commonutils import *
from commonutils import logger
from qa_class import QASet, QASetPool, get_qa_pool_from_json

# basic high frequency QASet pool
QA_BANK_JSON_FILEPATH = "qa_bank/7_AUG_high.json"
bhf_qa_pool: QASetPool = get_qa_pool_from_json(QA_BANK_JSON_FILEPATH)

# basic low frequency QASet pool
QA_BANK_JSON_FILEPATH = "qa_bank/7_AUG_low.json"
blf_qa_pool: QASetPool = get_qa_pool_from_json(QA_BANK_JSON_FILEPATH)

# advance high frequency QASet pool
QA_BANK_JSON_FILEPATH = "qa_bank/dummy.json"   
ahf_qa_pool: QASetPool = get_qa_pool_from_json(QA_BANK_JSON_FILEPATH)

qa_section = """
--------------------{{  }} # [1-6] or [d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}
"""

def auto_populated_qa_section(qa_pool: QASetPool, q_num: int, type=None) -> str:
    assert isinstance(qa_pool, QASetPool)

    qa_sections: str = ""
    qa_sets: Set[QASet] = qa_pool.random_draw_multiple(q_num=q_num, type=type)

    for qa_set in qa_sets:
        qn, options = qa_set.get()
        q_type_char: str = qa_set.type[0]
        qa_sections += "--------------------{{ " + q_type_char + " }}\n"
        qa_sections += "<QASet_ID>: {{ None }}\n"
        qa_sections += "<ANS>: {{  }}\n"
        qa_sections += f"{qn}\n"
        for option in options:
            qa_sections += f"{option}\n"
        qa_sections += "\n"

    return qa_sections


def template_video_section(filename: str, duration: str, dimension: str) -> str:
    """ 
    Generate the video section string for basic category
    Including: 5 high-frequecy, 2 low-frequency, 3 blank sections
    """
    vid_section = ""
    vid_section = f"~~~~~~~~~~~~~~~~~~~~ {filename} "
    vid_section += "~" * (80 - 22 - len(filename)) + "\n"
    vid_section += f"<LENGTH> {duration}\n"
    vid_section += f"<DIM> {dimension}\n\n"
    vid_section += "<PERSPECTIVE>: {{  }}\n"
    vid_section += "<RE_TRIM>: {{ START_TS, END_TS }}\n"
    vid_section += "<CRITICAL_POINT>: {{ TS }}\n\n"
    vid_section += auto_populated_qa_section(qa_pool=bhf_qa_pool, q_num=5)
    vid_section += auto_populated_qa_section(qa_pool=blf_qa_pool, q_num=2)
    vid_section += qa_section * 3

    return vid_section

def adv_template_video_section(filename: str, duration: str, dimension: str) -> str:
    """ 
    Generate the video section string for advance category
    Including: 5 high-frequency, 3 blank section
    """  
    adv_types = (        
        "Predictive",
        "Reverse Inference",
        "Counterfactual",
        "Introspection",
        )
    adv_type = random.choice(adv_types)
    
    vid_section = ""
    vid_section = f"~~~~~~~~~~~~~~~~~~~~ {filename} "
    vid_section += "~" * (80 - 22 - len(filename)) + "\n"
    vid_section += f"<LENGTH> {duration}\n"
    vid_section += f"<DIM> {dimension}\n\n"
    vid_section += "<PERSPECTIVE>: {{  }}\n"
    vid_section += "<RE_TRIM>: {{ START_TS, END_TS }}\n"
    vid_section += "<CRITICAL_POINT>: {{ TS }}\n\n"
    vid_section += auto_populated_qa_section(qa_pool=ahf_qa_pool, q_num=5, type=adv_type)
    vid_section += qa_section * 3

    return vid_section

def generate_template(folder_path: str = None, metadata_lst_filepath: str = None, qu_type = "B"):
    """
    Generate the whole .txt template with 2 methods availble.
    qu_type = "B" will generate basic questions using both its low and high frequency QABANK
    qu_type = "A" will generate advance questions using only its high frequency QABANK
    """
    if folder_path and metadata_lst_filepath:
        logger.error(
            "Extra Argument. You should supply either `folder_path` or `metadata_lst_filepath`, not both."
        )
        return
    elif not folder_path and not metadata_lst_filepath:
        logger.error(
            "Missing argument. You should supply either `folder_path` or `metadata_lst_filepath`, not both."
        )
        return

    if folder_path:
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            logger.error(f"Directory: `{folder_path}` does not exist")
            return

        head = folder_path.resolve()
        try:
            dir_file_lst: List[str] = sorted(
                os.listdir(folder_path),
                key=lambda x: os.path.getmtime(head / x),
                reverse=True,
            )
            logger.debug(
                "Videos successfully sorted by `Last modified time` in descending order."
            )
        except Exception as err:
            logger.error(
                "Encounter an error while getting and sorting vid_lst from folder, Error:\n{err}"
            )
            return
        vid_lst: List[Dict] = []
        for name in dir_file_lst:
            if name[-4:] == ".mp4":
                vid_lst.append({"filename": name[:-4]})
        if not vid_lst:
            logger.error(
                f"Directory: `{folder_path.resolve()}` does not contain any video (.mp4) file."
            )
            return

    else:
        metadata_lst_filepath = Path(metadata_lst_filepath)
        if not metadata_lst_filepath.is_file():
            logger.error(f"`{metadata_lst_filepath}` does not exist")
            raise Exception(f"ERR: `{metadata_lst_filepath}` does not exist")

        head, tail = os.path.split(metadata_lst_filepath)
        head: Path = Path(head).resolve()
        name, ext = os.path.splitext(tail)
        if ext != ".json":
            logger.error(f"`{metadata_lst_filepath}` is not a json file")
            raise Exception(f"ERR: `{metadata_lst_filepath}` is not a json file")

        with metadata_lst_filepath.open() as f:
            vid_lst: List[Dict] = json.load(f)

        if not vid_lst:
            logger.error(f"`{metadata_lst_filepath}` has no video information.")
            return

        # check video file existence
        vid_lst_new = []
        for vid in vid_lst:
            vid_path: Path = head / f"{vid['filename'] + vid['ext']}"
            if not vid_path.is_file():
                logger.warning(
                    f"{vid['filename'] + vid['ext']} is listed inside metadata_lst json file, but does NOT exist in the files system."
                )
            else:
                vid_lst_new.append(vid)

        _skip_sorting = False

        if not vid_lst_new:
            logger.warning(
                f"All videos listed in the metadata_lst json file are not found locally."
            )
            _continue = input(
                "Do you want to generate template according to the metadata_lst anyway (y/n)? "
            )
            if _continue in ("Y", "y", "yes"):
                vid_lst_new = vid_lst
                logger.info(f"Template generation will continue...")
                logger.warning(
                    f"Sorting of videos will be skipped, order of videos in the output file will follow metadata_lst"
                )
                _skip_sorting = True
            else:
                logger.error(f"Template generation aborted")
                return

        # sort vide_lst by last modified time
        try:
            if not _skip_sorting:
                vid_lst: List[Dict] = sorted(
                    vid_lst_new,
                    key=lambda vid: os.path.getmtime(
                        head / f"{vid['filename'] + vid['ext']}"
                    ),
                    reverse=True,
                )
                logger.debug(
                    "Videos successfully sorted by `Last modified time` in descending order."
                )
        except Exception as err:
            logger.error(
                "Encounter an error while getting and sorting vid_lst, Error:\n{err}"
            )
            return

    if qu_type == "B":
        export_fp = Path(os.path.join(head, "qa_label_template.txt"))
        export_fp: Path = bump_version(export_fp)
    elif qu_type == "A":
        export_fp = Path(os.path.join(head, "qa_label_template_advance.txt"))
        export_fp: Path = bump_version(export_fp)   

    string_lst_to_write: List[str] = []

    if qu_type == "B":
        for video in vid_lst:
            filename = video.get("filename")
            duration = f"{video.get('duration', 'NA')}s"
            dimension = f"(W){video.get('width', 'NA')} x (H){video.get('height', 'NA')}"
            string_lst_to_write.append(
                template_video_section(filename, duration, dimension)
            )
    elif qu_type == "A":
        for video in vid_lst:
            filename = video.get("filename")
            duration = f"{video.get('duration', 'NA')}s"
            dimension = f"(W){video.get('width', 'NA')} x (H){video.get('height', 'NA')}"
            string_lst_to_write.append(
                adv_template_video_section(filename, duration, dimension)
            ) 

    with export_fp.open(mode="w") as f:
        to_write = "\n\n".join(string_lst_to_write)
        if not is_ascii(to_write):
            logger.warning("Text to write contains non-ASCII characters.")
            logger.warning("Template generation may fail.")
            to_write = ensure_no_zh_punctuation(to_write)
        try:
            f.write(to_write)
            logger.debug(
                f"Successfully generated QA Label Template:\n         {export_fp.resolve()}"
            )
        except Exception as err:
            logger.error(
                f"Encounter an error while generating template, details:\n{err}"
            )


if __name__ == "__main__":

    # !!! Only use one of two methods below:

    # Method 1 (recommended): replace `None` to a valid file path to the `video_metadata_lst.json`
    video_metadata_lst_json_path = None

    # Method 2: replace `None` to a valid folder path that contains all the videos.
    video_folder_path = None

    generate_template(
        folder_path=video_folder_path,
        metadata_lst_filepath=video_metadata_lst_json_path,
    )
