import os
from pathlib import Path
from typing import List, Dict, Set, Tuple

import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "green",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel("DEBUG")

ans_map: Dict[str, int] = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7,
    "I": 8,
    "J": 9,
    "K": 10,
    "L": 11,
    "M": 12,
}
supported_types: Tuple[str] = (
    "Descriptive",
    "Explanatory",
    "Predictive",
    "Reverse Inference",
    "Counterfactual",
    "Introspection",
)

abbr_to_qtype_map: Dict[str, str] = {
    "d": "Descriptive",
    "e": "Explanatory",
    "p": "Predictive",
    "r": "Reverse Inference",
    "c": "Counterfactual",
    "i": "Introspection",
    "1": "Descriptive",
    "2": "Explanatory",
    "3": "Predictive",
    "4": "Reverse Inference",
    "5": "Counterfactual",
    "6": "Introspection",
}


def bump_version(filepath: Path) -> Path:
    head, tail = os.path.split(filepath)
    name, ext = os.path.splitext(tail)
    suffix = 1
    while filepath.is_file():
        logger.info(f"{filepath} already exist")
        suffix += 1
        new_name = f"{name}_v{str(suffix)}{ext}"
        filepath = Path(head) / new_name
    return filepath


def get_stat(qa_label_lst: List[Dict]) -> Dict:
    num_video_sections = len(qa_label_lst)
    num_video_ignore = 0
    num_video_require_retrim = 0
    num_video_has_critical_point = 0
    total_num_of_chars_in_qn_body = 0
    total_num_of_words_in_qn_body = 0
    total_num_qns = 0
    total_num_ops = 0
    q_type_count_map: Dict = {}
    q_body_count_map: Dict = {}

    for video_section in qa_label_lst:
        if video_section.get("v_ignore"):
            num_video_ignore += 1
        if video_section.get("re_trim_ts"):
            num_video_require_retrim += 1
        if video_section.get("critical_ts"):
            num_video_has_critical_point += 1

        qa_list: List[Dict] = video_section.get("qa_list")
        for qa_section in qa_list:
            is_ignored: bool = qa_section.get("q_ignore")
            if not is_ignored:
                total_num_qns += 1
                q_type = qa_section.get("q_type")
                if q_type in q_type_count_map:
                    q_type_count_map[q_type] += 1
                else:
                    q_type_count_map[q_type] = 1

                q_body = qa_section.get("q_body")
                total_num_of_chars_in_qn_body += len(q_body)
                total_num_of_words_in_qn_body += len(q_body.split())
                if q_body in q_body_count_map:
                    q_body_count_map[q_body] += 1
                else:
                    q_body_count_map[q_body] = 1

                total_num_ops += len(qa_section.get("option_lst"))

    # derived values
    num_video_labelled = num_video_sections - num_video_ignore

    average_num_qns_per_video = (
        total_num_qns / num_video_labelled if num_video_labelled != 0 else 0
    )
    average_num_qns_per_video = round(average_num_qns_per_video, 1)

    average_num_ops_per_qn = total_num_ops / total_num_qns if total_num_qns != 0 else 0
    average_num_ops_per_qn = round(average_num_ops_per_qn, 1)

    average_num_chars_per_qn = (
        total_num_of_chars_in_qn_body / total_num_qns if total_num_qns != 0 else 0
    )
    average_num_chars_per_qn = int(average_num_chars_per_qn)

    average_num_words_per_qn = (
        total_num_of_words_in_qn_body / total_num_qns if total_num_qns != 0 else 0
    )
    average_num_words_per_qn = int(average_num_words_per_qn)

    num_of_q_type = len(q_type_count_map)
    num_of_unique_qns = len(q_body_count_map)

    stats: Dict = {
        "Number of video sections found            ": num_video_sections,
        "Number of video sections ignored          ": num_video_ignore,
        "Number of videos Labelled                 ": num_video_labelled,
        "Number of videos to be re-trimmed         ": num_video_require_retrim,
        "Number of videos has critical point       ": num_video_has_critical_point,
        "Total number of questions                 ": total_num_qns,
        # "total_num_ops": total_num_ops,
        "Average Num of questions per video        ": average_num_qns_per_video,
        "Average Num of options per question       ": average_num_ops_per_qn,
        "Average Num of characters per question    ": average_num_chars_per_qn,
        "Average Num of words per question         ": average_num_words_per_qn,
        "Number of question types                  ": num_of_q_type,
        "Number of unique questions                ": num_of_unique_qns,
        "Question Count per question types": q_type_count_map,
        # "q_body_count_map": q_body_count_map,
    }
    return stats
