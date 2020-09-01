import os
import json
from pathlib import Path
from typing import List, Dict, Tuple

from commonutils import get_stat

from markkk.logger import logger


def main():
    base_path = Path("/home/UROP/data_urop/gs-samill/Video_Folders/Label_Files")
    label_data_master: List[Dict] = list()

    for filename in os.listdir(base_path):
        if filename[-5:] != ".json":
            continue
        logger.debug(filename)
        labelfile_path: Path = base_path / filename

        with labelfile_path.open() as f:
            label_data: List = json.load(f)
            label_data_master.extend(label_data)

    stats: Dict = get_stat(label_data_master)
    print()
    logger.debug("=====================================================\n")
    logger.debug("Status: OK\n")
    logger.debug(f"Stats: {json.dumps(stats, indent=9)}")
    if stats["Average Num of questions per video        "] <= 3:
        logger.warning("Average Num of questions per video is too low.")
    print()


if __name__ == "__main__":
    main()
