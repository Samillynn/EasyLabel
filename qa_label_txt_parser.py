import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from my_logger import logger as _logger

ans_map = {
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
}


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
    if value in ("None", "none", "nan", "NONE", "auto"):
        value = None
    return value


def qa_section_parser(qa_section: List) -> Dict:
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
        elif line.startswith("<QASet_ID>"):
            q_sub: str = get_value(line)
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

    return qa_section_data


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


def vid_section_parser(vid_section: List) -> Dict:
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
        if line.startswith("~~~~~~~~~~~~~~~~~~~~ "):
            filename = line.strip("~").strip()
            if not filename:
                _logger.error(f"Missing video filename")
            else:
                print()
                _logger.debug(f"~~~~~~~~ video section: {filename}")
        elif line.startswith("<PERSPECTIVE>"):
            perspective = get_value(line)
            if not perspective:
                _logger.error(f"Missing required <PERSPECTIVE> for {filename}")
        elif line.startswith("<RE_TRIM>"):
            re_trim_ts = get_value(line)
            if re_trim_ts == "START_TS, END_TS":
                re_trim_ts = None
            else:
                try:
                    start_ts, end_ts = tuple(re_trim_ts.split(","))
                except:
                    _logger.error(f"Error parsing <RE_TRIM> timestamps: {re_trim_ts}")
                    start_ts, end_ts = None, None

                # validate start time
                if start_ts and start_ts == "START_TS":
                    start_ts = "0"
                elif start_ts:
                    if not valid_time_format(start_ts):
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
                        _logger.error(f"Invalid END_TS Format for <RE_TRIM>: {end_ts}")
                        end_ts = None

        elif line.startswith("<CRITICAL_POINT>"):
            critical_ts = get_value(line)
            if critical_ts == "TS":
                critical_ts = None
            else:
                if not valid_time_format(critical_ts):
                    _logger.error(
                        f"Invalid Time Format for <CRITICAL_POINT>: {critical_ts}"
                    )
                    critical_ts = None

    ### Parsing of qa sections
    qa_list: List[Dict] = []
    for index, section_start in enumerate(qa_section_indexes):
        if index < len(qa_section_indexes) - 1:
            qa_section: List = vid_section[
                section_start : qa_section_indexes[index + 1]
            ]
        else:
            qa_section: List = vid_section[section_start:]

        qa_list.append(qa_section_parser(qa_section))

    vid_section_data: Dict = {
        "filename": filename,
        "perspective": perspective,
        "re_trim_ts": re_trim_ts,
        "critical_ts": critical_ts,
        "qa_list": qa_list,
    }
    # _logger.debug(json.dumps(vid_section_data))

    return vid_section_data


def parse_qa_label_txt(txt_fp: str, writeToJson=False) -> List[Dict]:
    # store parsed result
    qa_label_lst: List[Dict] = []
    # ensure txt file path is valid
    txt_fp = Path(txt_fp)
    assert txt_fp.is_file()

    # reas txt as a list of lines
    with txt_fp.open() as f:
        lines: List = f.readlines()

    lines: List = list(map(lambda x: x.strip("\n"), lines))

    # store the indexes where a vid_section starts
    vid_section_indexes = []

    # look for video sections
    for index, line in enumerate(lines):
        line: str = line.strip()
        if line.startswith("~~~~~~~~~~~~~~~~~~~~ "):
            vid_section_indexes.append(index)

    num_video_sections = len(vid_section_indexes)
    _logger.info(f"Number of video sections found: {num_video_sections}")

    # split the whole txt file into video sections
    for index, section_start in enumerate(vid_section_indexes):
        if index < num_video_sections - 1:
            vid_section: List = lines[section_start : vid_section_indexes[index + 1]]
        else:
            vid_section: List = lines[section_start:]

        qa_label_lst.append(vid_section_parser(vid_section))

    if writeToJson:
        export_fp: Path = txt_fp.parent / "qa.json"
        with export_fp.open(mode="w") as f:
            f.write(json.dumps(qa_label_lst, indent=4))
            _logger.debug(f"Successfully exported: {export_fp}")

    return qa_label_lst


if __name__ == "__main__":
    parse_qa_label_txt(
        "/Volumes/T5-SSD-Markkk/bilibili_003/qa_label_template.txt",
        # verbose=False,
        writeToJson=False,
    )
