import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from easylabeltool.my_logger import logger as _logger
from easylabeltool.commonutils import *


def get_value(line: str) -> str:
    if not isinstance(line, str):
        _logger.error("func: get_value accepts string only.")
        return
    try:
        start = line.index("{{") + 2
        end = line.index("}}")
    except:
        _logger.error(f"`{line}` does not satisfy expected format")
        return
    value = line[start:end].strip()
    if value in ("None", "none", "nan", "NONE", "null"):
        value = None
    return value


def qa_section_parser(qa_section: List) -> Tuple[Dict, bool]:
    _is_valid = True
    q_ignore = False  # wether skip this qa section
    q_type = None  # store parsed question type
    q_sub = None  # store parsed QASet_ID
    q_body = ""  # store parsed question
    option_lst: List = []  # store parsed options
    correct_ans: List = []  # store correct answer index
    ans_indexes: Set = set()
    plus_indexes: Set = set()

    for line in qa_section:
        line: str
        if line.startswith("!"):
            q_ignore = True
        elif line.startswith("---------"):
            q_type: str = get_value(line)
            if q_type and q_type == "auto":
                q_type = abbr_to_qtype_map.get("d")

            elif q_type and q_type != "auto":
                q_type = abbr_to_qtype_map.get(q_type.lower(), None)
                if not q_type:
                    _is_valid = False
                    _logger.error("Invalid Question Type")
                    q_type = "error"

        elif line.startswith("<QASet_ID>"):
            q_sub: str = get_value(line)
            if q_sub in ("auto", "Auto", "AUTO"):
                q_sub = None
            if q_sub:
                sub = " "
                q_body = sub
        elif line.startswith("<ANS>"):
            ans = get_value(line)
            for char in ans.upper():
                if char in ans_map:
                    ans_indexes.add(ans_map[char])

        else:
            if not q_sub and "?" in line:
                # get question line
                q_body = line.strip()
            elif q_sub and "?" in line:
                _is_valid = False
                _logger.error(
                    "Conflict: Question line detected while <QASet_ID> also presents."
                )
            else:
                if line:
                    option_lst.append(line.strip())

    # check for correct ans marked with '+'
    for index, option in enumerate(option_lst):
        if option.startswith("+"):
            plus_indexes.add(index)
            option_lst[index] = option.strip("+").strip()

    # store parsed data
    if len(ans_indexes) == 0 and len(plus_indexes) == 0:
        q_ignore = True

    if not q_ignore:
        if not q_type:
            _is_valid = False
            _logger.error("Missing Question Type")
        if not q_sub and not q_body:
            _is_valid = False
            _logger.error("Missing Question Line")

    # store parsed data
    qa_section_data: Dict = {
        "q_ignore": q_ignore,
        "q_type": q_type,
        "q_sub": q_sub,
        "q_body": q_body,
        "option_lst": option_lst,
        "correct_ans": correct_ans,
        "ans_indexes": tuple(ans_indexes),
        "plus_indexes": tuple(plus_indexes),
    }

    if not q_ignore and not _is_valid:
        _logger.warning(
            f"Error above occured at this QA: {json.dumps(qa_section_data, indent=2)}"
        )

    return qa_section_data, _is_valid


def valid_time_format(time_string: str) -> bool:
    # 00:00
    p1 = "^[0-5]?[0-9]:[0-5]?[0-9]$"
    # 00:00.000
    p2 = "^[0-5]?[0-9]:[0-5]?[0-9]\.[0-9]{1,3}$"
    # 000
    p3 = "^[0-9]{1,3}$"
    # 00.000
    p4 = "^[0-9]{1,3}\.[0-9]{1,3}$"

    for pattern in (p1, p2, p3, p4):
        match = re.fullmatch(pattern, time_string)
        if match:
            return True
    return False


def vid_section_parser(vid_section: List) -> Tuple[Dict, bool]:
    _is_valid = True
    v_ignore = False
    # traverse thru vid_section line by line
    # and store the indexes where qa_sections starts
    qa_section_indexes = []
    for index, line in enumerate(vid_section):
        if line.startswith("-------"):
            qa_section_indexes.append(index)

    ### Parsing of video info
    # get video info section
    vid_info_section: List = vid_section[: qa_section_indexes[0]]
    # temporary data store
    filename = None
    perspective = None
    re_trim_ts = None
    critical_ts = None
    for line in vid_info_section:
        if line.startswith("!~~~~~~~~~~~~~~~~"):
            v_ignore = True
            filename = line.strip("!").strip("~").strip()
            if not filename:
                _is_valid = False
                _logger.error(f"Missing video filename")
            else:
                print()
                _logger.debug(f"Checking video section: {filename} >>>>")
                _logger.warning("This video is being ignored")
            break
        elif line.startswith("~~~~~~~~~~~~~~~~~~~~ "):
            filename = line.strip("~").strip()
            if not filename:
                _is_valid = False
                _logger.error(f"Missing video filename")
            else:
                print()
                _logger.debug(f"Checking video section: {filename} >>>>")
        elif line.startswith("<PERSPECTIVE>"):
            perspective = get_value(line)
            if perspective:
                if perspective not in ("1", "3"):
                    _is_valid = False
                    _logger.error(f"Unexpected value for <PERSPECTIVE>: {perspective}")
            else:
                _is_valid = False
                _logger.error(f"Missing value for <PERSPECTIVE>.")

        elif line.startswith("<RE_TRIM>"):
            re_trim_ts = get_value(line)
            if re_trim_ts == "START_TS, END_TS":
                re_trim_ts = None
            else:
                try:
                    start_ts, end_ts = tuple(re_trim_ts.split(","))
                except:
                    _is_valid = False
                    _logger.error(f"Error parsing <RE_TRIM> timestamps: {re_trim_ts}")
                    start_ts, end_ts = None, None

                # validate start time
                if start_ts and start_ts == "START_TS":
                    start_ts = "0"
                elif start_ts:
                    if not valid_time_format(start_ts):
                        _is_valid = False
                        _logger.error(
                            f"Invalid START_TS Format for <RE_TRIM>: {start_ts}"
                        )
                        start_ts = None

                # validate start time
                if end_ts and end_ts == "END_TS":
                    # leave it for now
                    pass
                elif end_ts:
                    if not valid_time_format(end_ts):
                        _is_valid = False
                        _logger.error(f"Invalid END_TS Format for <RE_TRIM>: {end_ts}")
                        end_ts = None

        elif line.startswith("<CRITICAL_POINT>"):
            critical_ts = get_value(line)
            if critical_ts == "TS":
                critical_ts = None
            else:
                if not valid_time_format(critical_ts):
                    _is_valid = False
                    _logger.error(
                        f"Invalid Time Format for <CRITICAL_POINT>: {critical_ts}"
                    )
                    critical_ts = None

    ### Parsing of qa sections
    qa_list: List[Dict] = []
    if not v_ignore:
        for index, section_start in enumerate(qa_section_indexes):
            if index < len(qa_section_indexes) - 1:
                qa_section: List = vid_section[
                    section_start : qa_section_indexes[index + 1]
                ]
            else:
                qa_section: List = vid_section[section_start:]

            qa_section_data, valid_qa_section = qa_section_parser(qa_section)
            qa_list.append(qa_section_data)
            if not valid_qa_section:
                _is_valid = False

    vid_section_data: Dict = {
        "v_ignore": v_ignore,
        "filename": filename,
        "perspective": perspective,
        "re_trim_ts": re_trim_ts,
        "critical_ts": critical_ts,
        "qa_list": qa_list,
    }

    return vid_section_data, _is_valid


def get_stat(qa_label_lst: List[Dict]) -> Dict:
    num_video_sections = len(qa_label_lst)
    num_video_ignore = 0
    num_video_require_retrim = 0
    num_video_has_critical_point = 0
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
    average_num_ops_per_qns = total_num_ops / total_num_qns if total_num_qns != 0 else 0
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
        "Average Num of options per questions      ": average_num_ops_per_qns,
        "Number of question types                  ": num_of_q_type,
        "Number of unique questions                ": num_of_unique_qns,
        # "q_type_count_map": q_type_count_map,
        # "q_body_count_map": q_body_count_map,
    }
    return stats


def parse_qa_label_txt(txt_fp: str, writeToJson=False) -> List[Dict]:
    label_file_is_valid = True
    # store parsed result
    qa_label_lst: List[Dict] = []
    # ensure txt file path is valid
    txt_fp = Path(txt_fp)
    try:
        assert txt_fp.is_file()
    except AssertionError:
        _logger.error(f"File '{str(txt_fp)}' does not exist.")
        return

    # reas txt as a list of lines
    with txt_fp.open() as f:
        lines: List = f.readlines()

    lines: List = list(map(lambda x: x.strip("\n"), lines))

    # store the indexes where a vid_section starts
    vid_section_indexes = []

    # look for video sections
    for index, line in enumerate(lines):
        line: str = line.strip()
        # if line.startswith("~~~~~~~~~~~~~~~~~~~~ "):
        if "~~~~~~~~~~~~~~~~~" in line:
            vid_section_indexes.append(index)

    num_video_sections = len(vid_section_indexes)
    _logger.info(f"Number of video sections found: {num_video_sections}")

    # split the whole txt file into video sections
    for index, section_start in enumerate(vid_section_indexes):
        if index < num_video_sections - 1:
            vid_section: List = lines[section_start : vid_section_indexes[index + 1]]
        else:
            vid_section: List = lines[section_start:]

        vid_section_data, _valid = vid_section_parser(vid_section)
        qa_label_lst.append(vid_section_data)
        if not _valid:
            label_file_is_valid = False

    if label_file_is_valid:
        stats: Dict = get_stat(qa_label_lst)
        print()
        _logger.debug("=====================================================\n")
        _logger.debug(f"Stats: {json.dumps(stats, indent=9)}")
        print()

    else:
        print()
        _logger.warning(
            f"Your Label txt file ({txt_fp}) contains some errors, please check non-green error logs above.\n"
        )

    if writeToJson and label_file_is_valid:
        export_fp: Path = txt_fp.parent / "qa_label.json"
        export_fp: Path = bump_version(export_fp)

        with export_fp.open(mode="w") as f:
            f.write(json.dumps(qa_label_lst, indent=4))
            print()
            _logger.debug(f"Successfully exported: {export_fp}\n")
    elif writeToJson and not label_file_is_valid:
        print()
        _logger.warning(f"No json file is generated.")

    return qa_label_lst


if __name__ == "__main__":
    import sys

    LABEL_FILE = "REPLACE ME"

    if len(sys.argv) == 1:
        parse_qa_label_txt(LABEL_FILE, writeToJson=True)
    elif len(sys.argv) == 2:
        LABEL_FILE = sys.argv[1]
        parse_qa_label_txt(LABEL_FILE, writeToJson=True)
    else:
        _logger.error(f"Unexpected arguments: {sys.argv[1:]}")
