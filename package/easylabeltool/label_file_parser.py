import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

from .commonutils import *
from .qa_class import QASet, QASetPool, get_qa_pool_from_json

platform_prefix = ""


def get_value(line: str) -> str:
    if not isinstance(line, str):
        logger.error("func: get_value accepts string only.")
        return
    try:
        start = line.index("{{") + 2
        end = line.index("}}")
    except:
        logger.error(f"`{line}` does not satisfy expected format.")
        return
    value = line[start:end].strip()
    if value in ("None", "none", "nan", "NONE", "null", ""):
        value = None
    return value


def qa_section_parser(
    qa_section: List, local_qa_pool: QASetPool = None
) -> Tuple[Dict, bool]:
    _is_valid = True
    q_ignore = False  # wether skip this qa section
    q_type = None  # store parsed question type
    q_sub_id = None  # store parsed QASet_ID
    q_body = ""  # store parsed question
    option_lst: List = []  # store parsed options
    correct_ans: Set = set()  # store correct answer in complete sentence
    ans_indexes: Set = set()  # store correct answer index
    qu_identifier_list = [
        "?",
        "Are",
        "Is",
        "How",
        "Will",
        "Judging",
        "What",
        "Was",
        "Did",
        "Would",
        "Could",
        "Which",
        "Were",
        "Can",
        "Do",
        "Does",
        "Why",
    ]

    for line in qa_section:
        line: str
        if line.startswith("!"):
            q_ignore = True

        elif line.startswith("---------"):
            q_type_value: str = get_value(line)

            if q_type_value:
                if q_type_value == "auto":
                    # hard code
                    q_type = abbr_to_qtype_map.get("d")
                else:
                    q_type = abbr_to_qtype_map.get(q_type_value.lower())
                    if not q_type:
                        _is_valid = False
                        logger.error(f"Invalid Question Type: '{q_type_value}'")

        elif line.startswith("<QASet_ID>"):
            q_sub_id: str = get_value(line)
            if q_sub_id in ("auto", "Auto", "AUTO"):
                q_sub_id = None
            if q_sub_id:
                if not local_qa_pool:
                    logger.error(
                        "This Label File uses QA substitution, but no QA bank is provided."
                    )
                    raise Exception(
                        "This Label File uses QA substitution, but no QA bank is provided."
                    )
                if not isinstance(local_qa_pool, QASetPool):
                    logger.error(
                        "This Label File uses QA substitution, but QA bank is not valid."
                    )
                    raise Exception(
                        "This Label File uses QA substitution, but QA bank is not valid."
                    )

                try:
                    q_sub_id = int(q_sub_id)
                except:
                    logger.error(
                        f"Unexpected value for <QASet_ID>: '{q_sub_id}'. QASet_ID should be an integer value."
                    )
                    _is_valid = False
                qa_set: QASet = local_qa_pool.get_by_id(q_sub_id)
                if qa_set:
                    logger.debug(qa_set)
                    # get body and optiosn from a QASet object
                    q_sub_body, q_sub_options = qa_set.get()
                    # assign them to reserved variables respectively
                    q_body = q_sub_body
                    option_lst.extend(q_sub_options)
                    # get q type
                    q_type = qa_set.type
                else:
                    _is_valid = False
                    logger.error(f"QASet_ID: '{q_sub_id}' not found in the QA Bank.")

        elif line.startswith("<ANS>"):
            ans = get_value(line)
            if ans:
                for char in ans.upper():
                    if char in ans_map:
                        ans_indexes.add(ans_map[char])

        else:
            if not q_sub_id and "?" in line:
                # not using identifier here to flag missing "?" error
                # non-empty line with a question mark, this should be the question line
                q_body = line.strip()
            elif q_sub_id and any(
                identifier in line for identifier in qu_identifier_list
            ):
                # something is wrong
                _is_valid = False
                logger.error(
                    "Conflict: Question line detected while <QASet_ID> also presents."
                )
            else:
                # non-empty line: this should be an option to the question
                if line:
                    option_lst.append(line.strip())

    # check for correct ans marked with '+'
    for index, option in enumerate(option_lst):
        if option.startswith("+"):
            ans_indexes.add(index)
            # remove "+" sign from line
            ans: str = option.strip("+").strip()
            # Update option
            option_lst[index] = ans

    # check once again
    for index in ans_indexes:
        try:
            an_answer = option_lst[int(index)]
            correct_ans.add(an_answer)
        except IndexError:
            _is_valid = False
            logger.error(
                "Given correct answer out of range, please check your value for <ANS>."
            )

    # store parsed data
    if len(ans_indexes) == 0:
        q_ignore = True

    if not q_ignore:
        if not q_type:
            _is_valid = False
            logger.error("Missing Question Type")
        if not q_sub_id and not q_body:
            _is_valid = False
            logger.error("Missing Question Line")

    # store parsed data
    qa_section_data: Dict = {
        "q_ignore": q_ignore,  # bool
        "q_type": q_type,  # string
        "q_body": q_body,  # string
        "option_lst": option_lst,  # List[str]
        "correct_ans": tuple(correct_ans),
        "ans_indexes": tuple(ans_indexes),
    }

    if not q_ignore and not _is_valid:
        logger.warning(
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


def vid_section_parser(
    vid_section: List, local_qa_pool: QASetPool = None
) -> Tuple[Dict, bool]:
    global platform_prefix

    _is_valid = True
    v_ignore = False
    # traverse thru vid_section line by line
    # and store the indexes where qa_sections starts
    qa_section_indexes = []
    for index, line in enumerate(vid_section):
        if "-------" in line:
            qa_section_indexes.append(index)

    ### Parsing of video info
    # get video info section
    vid_info_section: List = vid_section[: qa_section_indexes[0]]
    # temporary data store
    filename = None
    vid_length = None
    perspective = None
    re_trim_ts = None
    critical_ts = None
    critical_type = None
    contains_p_type = False
    contains_r_type = False

    for line in vid_info_section:
        if line.startswith("!~~~~~~~~~~~~~~~~"):
            v_ignore = True
            filename = line.strip("!").strip("~").strip()
            if not filename:
                _is_valid = False
                logger.error(f"Missing video filename")
            else:
                print()
                logger.debug(f"Checking video section: {filename} >>>>")
                logger.warning("This video is being ignored")
            break
        elif line.startswith("~~~~~~~~~~~~~~~~~~~~ "):
            filename = line.strip("~").strip()
            if not filename:
                _is_valid = False
                logger.error(f"Missing video filename")
            else:
                print()
                logger.debug(f"Checking video section: {filename} >>>>")
        elif line.startswith("<LENGTH>"):
            vid_length = line.strip("<LENGTH>s ")
            try:
                vid_length = float(vid_length)
            except:
                logger.warning("Failed to get video length value")
        elif line.startswith("<PERSPECTIVE>"):
            perspective = get_value(line)
            if perspective:
                if perspective not in ("1", "3"):
                    _is_valid = False
                    logger.error(f"Unexpected value for <PERSPECTIVE>: {perspective}")
            else:
                _is_valid = False
                logger.error(f"Missing value for <PERSPECTIVE>.")

        elif line.startswith("<RE_TRIM>"):
            re_trim_ts = get_value(line)
            if re_trim_ts == "START_TS, END_TS":
                re_trim_ts = None
            else:
                try:
                    start_ts, end_ts = tuple(re_trim_ts.split(","))
                    start_ts = start_ts.strip()
                    end_ts = end_ts.strip()
                except:
                    _is_valid = False
                    logger.error(f"Error parsing <RE_TRIM> timestamps: {re_trim_ts}")
                    start_ts, end_ts = None, None

                # validate start time
                if start_ts == "START_TS":
                    start_ts = "00:00"
                elif start_ts:
                    if not valid_time_format(start_ts):
                        _is_valid = False
                        logger.error(
                            f"Invalid START_TS Format for <RE_TRIM>: {start_ts}"
                        )
                        start_ts = None

                # validate end time
                if end_ts == "END_TS":
                    end_ts = "END"
                elif end_ts:
                    if not valid_time_format(end_ts):
                        _is_valid = False
                        logger.error(f"Invalid END_TS Format for <RE_TRIM>: {end_ts}")
                        end_ts = None

                re_trim_ts = [start_ts, end_ts]

        elif line.startswith("<CRITICAL_POINT>"):
            critical_ts = get_value(line)
            if critical_ts == "TS":
                critical_ts = None
            elif critical_ts == "END":
                critical_ts = "END"
            else:
                if not valid_time_format(critical_ts):
                    _is_valid = False
                    logger.error(
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

            qa_section_data, valid_qa_section = qa_section_parser(
                qa_section, local_qa_pool=local_qa_pool
            )
            if not qa_section_data["q_ignore"]:
                if qa_section_data["q_type"] == "Predictive":
                    contains_p_type = True
                elif qa_section_data["q_type"] == "Reverse Inference":
                    contains_r_type = True
            qa_list.append(qa_section_data)
            if not valid_qa_section:
                _is_valid = False

    if contains_p_type and contains_r_type:
        logger.error(
            "'Predictive' and 'Reverse Inference' cannot co-exist for a video."
        )
        _is_valid = False

    if contains_p_type or contains_r_type:
        if not critical_ts:
            logger.error("Missing CRITICAL_POINT.")
            _is_valid = False
        if contains_p_type:
            critical_type = "p"
        else:
            critical_type = "r"

    if filename:
        if platform_prefix:
            filename = platform_prefix + filename
    else:
        logger.error("Missing video filename.")

    vid_section_data: Dict = {
        "v_ignore": v_ignore,
        "filename": filename,
        "vid_length": vid_length,
        "perspective": perspective,
        "re_trim_ts": re_trim_ts,
        "critical_ts": critical_ts,
        "critical_type": critical_type,
        "qa_list": qa_list,
    }

    return vid_section_data, _is_valid


def parse_qa_label_txt(
    txt_fp: str, writeToJson: bool = False, local_qa_bank_fp: str = ""
) -> List[Dict]:
    """Entry point of parsing of txt file"""
    label_file_is_valid = True

    global platform_prefix

    if str(txt_fp.stem).startswith("bilibili"):
        platform_prefix = "b_"
    elif str(txt_fp.stem).startswith("youtube"):
        platform_prefix = "y_"
    elif str(txt_fp.stem).startswith("unlabelled"):
        platform_prefix = ""
    else:
        logger.error(f"Unexpected file name: {txt_fp}")
        logger.error(
            f"Please rename your label file to the Video Folder Name first before parsing it. (e.g. unlabelled_008, bilibili_020)"
        )
        return

    # store parsed result
    qa_label_lst: List[Dict] = []
    # ensure txt file path is valid
    txt_fp = Path(txt_fp)

    if local_qa_bank_fp and local_qa_bank_fp != "":
        local_qa_bank_fp = Path(local_qa_bank_fp)
    else:
        local_qa_bank_fp = None

    if not txt_fp.is_file():
        logger.error(f"Label File: '{str(txt_fp)}' does not exist.")
        return
    if str(txt_fp)[-4:] != ".txt":
        logger.error(f"Argument txt_fp requires a txt filepath")
        return

    local_qa_pool = None
    if local_qa_bank_fp:
        if not local_qa_bank_fp.is_file():
            logger.error(f"local_qa_bank_fp '{str(local_qa_bank_fp)}' does not exist.")
            return
        if str(local_qa_bank_fp)[-5:] != ".json":
            logger.error(f"Argument local_qa_bank_fp requires a json filepath")
            return
        # try to load qa bank
        try:
            local_qa_pool: QASetPool = get_qa_pool_from_json(local_qa_bank_fp)
        except Exception as err:
            logger.error("Encounter error while loading your local QA Bank")
            logger.error(str(err))
            return

    # read txt as a list of lines
    with txt_fp.open() as f:
        lines: List = f.readlines()

    lines: List = list(map(lambda x: x.strip("\n"), lines))

    # store the indexes where a vid_section starts
    vid_section_indexes = []

    # look for video sections
    for index, line in enumerate(lines):
        line: str = line.strip()
        if "~~~~~~~~~~~~~~~~~" in line:
            vid_section_indexes.append(index)

    num_video_sections = len(vid_section_indexes)
    logger.info(f"Number of video sections found: {num_video_sections}")

    # split the whole txt file into video sections
    for index, section_start in enumerate(vid_section_indexes):
        if index < num_video_sections - 1:
            vid_section: List = lines[section_start : vid_section_indexes[index + 1]]
        else:
            vid_section: List = lines[section_start:]

        vid_section_data, _valid = vid_section_parser(
            vid_section, local_qa_pool=local_qa_pool
        )
        qa_label_lst.append(vid_section_data)
        if not _valid:
            label_file_is_valid = False

    if label_file_is_valid:
        stats: Dict = get_stat(qa_label_lst)
        print()
        logger.debug("=====================================================\n")
        logger.debug("Status: OK\n")
        logger.debug(f"Stats: {json.dumps(stats, indent=9)}")
        if stats["Average Num of questions per video        "] <= 3:
            logger.warning("Average Num of questions per video is too low.")
        print()

    else:
        print()
        logger.warning(
            f"Your Label txt file ({txt_fp}) contains some errors, please check non-green error logs above.\n"
        )

    if writeToJson and label_file_is_valid:
        export_fp: Path = txt_fp.parent / f"{txt_fp.stem}.json"
        export_fp: Path = bump_version(export_fp)

        with export_fp.open(mode="w") as f:
            f.write(json.dumps(qa_label_lst, indent=4))
            print()
            logger.debug(f"Successfully exported: {export_fp}\n")
    elif writeToJson and not label_file_is_valid:
        print()
        logger.warning(f"No json file is generated.")

    return qa_label_lst, label_file_is_valid


if __name__ == "__main__":
    import sys

    LABEL_FILE = "REPLACE ME"
    QA_BANK_JSON_FILE = None  # Optional

    if len(sys.argv) == 1:
        parse_qa_label_txt(
            LABEL_FILE, writeToJson=True, local_qa_bank_fp=QA_BANK_JSON_FILE
        )
    elif len(sys.argv) == 2:
        LABEL_FILE = sys.argv[1]
        parse_qa_label_txt(LABEL_FILE, writeToJson=True)
    elif len(sys.argv) == 3:
        LABEL_FILE = sys.argv[1]
        QA_BANK_JSON_FILE = sys.argv[2]
        parse_qa_label_txt(
            LABEL_FILE, writeToJson=True, local_qa_bank_fp=QA_BANK_JSON_FILE
        )
    else:
        logger.error(f"Unexpected arguments: {sys.argv[1:]}")
