import json
import random
import pandas
import numpy as np
from pathlib import Path
from collections import abc
from orderedset import OrderedSet
from typing import List, Dict, Tuple, Set, Iterable, Union

from .commonutils import logger
from markkk.pyutils.check_text_encoding import ensure_no_zh_punctuation


class QASet:

    property_list = ["id", "type", "subtype", "qns", "options"]
    supported_types = (
        "Descriptive",
        "Explanatory",
        "Predictive",
        "Reverse Inference",
        "Counterfactual",
        "Introspection",
    )

    def __init__(
        self,
        *,
        id: int,
        type: str,
        subtype: str = None,
        qns: Union[str, List[str]] = [],
        options: Iterable[str] = [],
    ):
        try:
            id = int(id)
        except:
            raise TypeError(
                f"ID of QASet should be an integer, but not {id}({id.__class__})"
            )
        self._id: int = id

        type = type.strip().capitalize()
        if type in self.supported_types:
            self._type: str = type

        subtype = ensure_no_zh_punctuation(subtype.strip())
        self._subtype: str = subtype

        if isinstance(qns, str):
            qns: str = ensure_no_zh_punctuation(qns.strip())
            self.qns: List[str] = [qns]
        elif isinstance(qns, abc.Sequence):
            qns_lst = []
            for qn in qns:
                qn = ensure_no_zh_punctuation(qn.strip())
                qns_lst.append(qn)
            self.qns: List[str] = qns_lst
        else:
            raise TypeError(
                f"qns of QASet should be str or List[str], but not {qns}({qns.__class__})"
            )

        options_lst = []
        for i in options:
            option = ensure_no_zh_punctuation(i.strip())
            options_lst.append(option)
        self._options: Tuple[str] = tuple(options_lst)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        logger.error(f"QASet ID is immutable, and it remains as {self._id}")
        return

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        logger.error(f"QASet type is immutable, and it remains as {self._type}")
        return

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, value):
        logger.error(f"QASet subtype is immutable, and it remains as {self._subtype}")
        return

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        logger.error(f"QASet options is immutable, and it remains as {self._options}")
        return

    def __repr__(self):
        return f"<QASet ID: {self.id}> ({self.type} - {self.subtype})\n{str(self.qns)}\n{str(self.options)}\n"

    def get(self) -> Tuple[str, Tuple]:
        """ Randomly select a qn from self.qns
        return the selected qn and the option_lst
        """
        return random.choice(self.qns), self.options

    def append_rephrase(self, qns: Union[str, List[str]]):
        """ Append qns into self.qns """
        if isinstance(qns, str):
            qns: str = ensure_no_zh_punctuation(qns)
            self.qns.append(qns)
        elif isinstance(qns, abc.Sequence):
            qns_lst = []
            for qn in qns:
                qn = ensure_no_zh_punctuation(qn)
                qns_lst.append(qn)
            self.qns.extend(qns_lst)
        else:
            raise ValueError(f"can't append {qn}({qn.__class__}) to QASet")


################################################################################


class QASetPool:
    def __init__(self):
        self._pool: List[QASet] = []
        self._id_map: Dict[int:QASet] = {}
        self._type_map: Dict = {}

    @property
    def pool(self):
        return self._pool

    @property
    def id_map(self):
        return self._id_map

    @property
    def type_map(self):
        return self._type_map

    def add_to_pool(self, qa_set: QASet):
        """ Add a QASet object into self.pool """
        assert isinstance(qa_set, QASet)

        # add qa_set to pool and id_map
        try:
            self.id_map[qa_set.id].append_rephrase(qa_set.qns)
        except KeyError:
            self.id_map[qa_set.id] = qa_set
            self.pool.append(qa_set)

            # add qa_set to type_map
            type = qa_set.type
            try:
                self.type_map[type].append(qa_set)
            except KeyError:
                self.type_map[type] = [qa_set]

    def random_draw_one(self, type=None) -> QASet:
        """ Randomly draw a QASet from self._QASetPool """
        data = self.type_map[type] if type else list(self.id_map.values())
        return random.choice(data)

    def random_draw_multiple(self, q_num: int, type=None) -> Set[QASet]:
        """ Randomly draw given number of QASet from self._QASetPool """
        iter_num = 0
        res = set()
        # subtype_list = []
        while len(res) < q_num:
            iter_num += 1
            qa_set: QASet = self.random_draw_one(type=type)
            # _subtype: str = qa_set._subtype
            # if qa_set in res or _subtype in subtype_list:
            #     continue
            # if _subtype:
            #     subtype_list.append(_subtype)
            res.add(qa_set)

        return res

    def get_by_id(self, _id: str) -> QASet:
        """ Get a specific QASet by QASet.id attribute """
        _id = int(_id)
        return self.id_map.get(_id)

    def load_from_excel(self, excel_fp: str):
        """ 1. read from excel
        2. create QASet objects from excel data
        3. add QASet objects into self.pool
        """
        qa_sheet = pandas.read_excel(excel_fp)
        rows_num, cols_num = qa_sheet.shape
        logger.debug(f"rows_num: {rows_num}")
        logger.debug(f"cols_num: {cols_num}\n")

        for i in range(0, rows_num):
            try:
                qa_set_id = int(qa_sheet.iloc[i][2])
                logger.debug(f"ID: {qa_set_id}")
            except Exception as e:
                logger.error("Failed getting QASet ID from excel row")
                continue

            qa_set_qn: str = qa_sheet.iloc[i][3]
            logger.debug(f"qa_set_qn: {qa_set_qn}")

            if not self.get_by_id(qa_set_id):
                qa_set_type: str = qa_sheet.iloc[i][0]
                logger.debug(f"qa_set_type: {qa_set_type}")

                qa_set_subtype: str = qa_sheet.iloc[i][1]
                logger.debug(f"qa_set_subtype: {qa_set_subtype}")

                qa_set_options: OrderedSet = OrderedSet(
                    str(qa_sheet.iloc[i][j]) for j in range(4, cols_num)
                )
                # remove emtpy option, which is 'nan' in pandas
                qa_set_options.discard("nan")
                logger.debug(f"qa_set_options: {qa_set_options}")

                qa_set: QASet = QASet(
                    id=qa_set_id,
                    type=qa_set_type,
                    subtype=qa_set_subtype,
                    qns=qa_set_qn,
                    options=qa_set_options,
                )
                self.add_to_pool(qa_set)
                logger.debug(">>> Added new QASet into pool\n")
                # logger.debug(qa_set)
            else:
                self.get_by_id(qa_set_id).append_rephrase(qa_set_qn)
                logger.debug("### Added new rephrased version into existing QASet\n")

    def write_to_json(self, export_fp: str):
        """
        get all QASet objects from self.pool
        convert every QASet object into a dictionary
        write the list of dictionaries into json
        """
        export_fp: Path = Path(export_fp)
        if export_fp.is_file():
            overwrite = input(f"{export_fp} already exist, overwrite it (y/n)? ")
            if overwrite in ("Y", "y", "yes"):
                logger.warning(f"Overwriting {export_fp}")
            else:
                logger.error(f"Export aborted")
                return

        lst = []
        # gather all data from pool
        for qa_set in self.pool:
            lst.append({tag: getattr(qa_set, tag) for tag in QASet.property_list})

        with export_fp.open(mode="w") as f:
            json.dump(lst, f, indent=4)

    def load_from_json(self, json_fp: str):
        """ 1. read from json
        2. create QASet objects from json data
        3. add QASet objects into self.pool
        """
        assert Path(json_fp).is_file()
        try:
            qadict_lst = json.load(open(json_fp))
            logger.debug(f"{json_fp} has been loaded")
        except:
            logger.error(f"Failed loading {json_fp}")
            return

        for qa_dict in qadict_lst:
            self.add_to_pool(QASet(**qa_dict))


################################################################################


def get_qa_pool_from_json(qa_bank_json: str) -> QASetPool:
    """ Return a QASetPool instance with loaded QASets from json """
    assert Path(qa_bank_json).is_file()
    qa_pool = QASetPool()
    qa_pool.load_from_json(Path(qa_bank_json))
    return qa_pool


def export_excel_to_json(qa_bank_excel: str):
    qa_bank_excel = Path(qa_bank_excel)
    if not qa_bank_excel.is_file():
        logger.error(f"Filepath '{str(qa_bank_excel)}' does not exist.")
        return
    if str(qa_bank_excel)[-5:] != ".xlsx":
        logger.error(
            f"QA Bank Filepath requires an Excel file. '{str(qa_bank_excel)}' doesn't match with '*.xlsx'."
        )
        return
    pool = QASetPool()
    pool.load_from_excel(qa_bank_excel)
    export_fp = qa_bank_excel.parent / f"{qa_bank_excel.stem}.json"
    pool.write_to_json(export_fp)
    return


if __name__ == "__main__":
    pool = QASetPool()
    pool.load_from_excel("qa_bank/7_AUG_high.xlsx")
    pool.write_to_json("qa_bank/7_AUG_high.json")

    # pool = QASetPool()
    # pool.load_from_excel("example/qa_bank_sample_2.xlsx")
    # pool.write_to_json("example/qa_bank_sample_2.json")
    #
    # pool_2 = get_qa_pool_from_json("example/qa_bank_sample_2.json")
    # q = pool_2.random_draw_one()
    # print(q)
