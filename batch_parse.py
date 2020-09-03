import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

from commonutils import *
from label_file_parser import parse_qa_label_txt

BASE_DIR = Path("/Users/mark/Downloads/Label_Files")


def main():
    qa_label_master_lst = []
    invalid_files = []
    for filename in os.listdir(BASE_DIR):
        labelfile: Path = BASE_DIR / filename
        assert labelfile.is_file()

        if str(labelfile).endswith(".txt"):
            print(labelfile, "\n")
            # generate label template
            result: Tuple = parse_qa_label_txt(
                labelfile, local_qa_bank_fp=None, writeToJson=True
            )

            if result:
                qa_label_lst, is_valid = result
                if is_valid:
                    qa_label_master_lst.extend(qa_label_lst)
                else:
                    invalid_files.append(labelfile)
            else:
                invalid_files.append(labelfile)

    if len(invalid_files) != 0:
        logger.debug("=====================================================\n")
        logger.error("Following label files contain errors: ")
        for filename in invalid_files:
            logger.error(filename)

    stats: Dict = get_stat(qa_label_master_lst)
    print()
    logger.debug("=====================================================\n")
    logger.debug("Status: OK\n")
    logger.debug(f"Stats: {json.dumps(stats, indent=9)}")
    if stats["Average Num of questions per video        "] <= 3:
        logger.warning("Average Num of questions per video is too low.")
    print()


if __name__ == "__main__":
    main()
