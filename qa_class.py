import json
import random
import pandas
import numpy as np
from collections import abc
from pathlib import Path
from typing import List, Dict, Tuple, Set, Iterable, Union


class QASet:

    info_list = ["_id", "_type", "_sub_type", "qns", "options"]

    def __init__(
        self,
        _id: int,
        _type: str,
        qns: Union[str, List[str]],
        options: Iterable[str],
        _sub_type: str = None,
    ):
        # id should be immutable
        self._id: int = int(_id)

        # type and _sub_type should be immutable
        self._type: str = _type
        self._sub_type: str = _sub_type

        if isinstance(qns, str):
            self.qns: List[str] = [qns]
        elif isinstance(qns, abc.Sequence):
            self.qns: List[str] = list(qns)
        else:
            raise ValueError(
                f"qns of QASet should be str or List[str], but not {qns}({qns.__class__})"
            )

        # options should be immutable
        self.options: Tuple[str] = tuple(options)

    def __repr__(self):
        return f"{self._id}, {str(self.qns)}, {str(self.options)}"

    def get(self) -> Tuple[str, Tuple]:
        """ Randomly select a qn from self.qns
        return the selected qn and the option_lst
        """
        return random.choice(self.qns), self.options

    def append_rephrase(self, qn):
        """ Append qn into self.qns """
        if isinstance(qn, str):
            self.qns.append(qn)
        elif isinstance(qn, abc.Sequence):
            self.qns.extend(qn)
        else:
            raise ValueError(f"can't append {qn}({qn.__class__}) to QASet")


class QASetPool:
    def __init__(self):
        self._pool: List[QASet] = []
        self._id_map: Dict[str:QASet] = {}
        self._type_map: Dict = {}

    def add(self, qa_set: QASet):
        """ Add a QASet object into self._pool """
        assert isinstance(qa_set, QASet)

        # add qa_set to _pool and _id_map
        try:
            self._id_map[qa_set._id].append_rephrase(qa_set.qns)
        except KeyError:
            self._id_map[qa_set._id] = qa_set
            self._pool.append(qa_set)

            # add qa_set to _type_map
            _type = qa_set._type
            try:
                self._type_map[_type].append(qa_set)
            except KeyError:
                self._type_map[_type] = [qa_set]

    def random_draw(self, _type=None, duration: float = None) -> QASet:
        """ Randomly draw a QASet from self._QASetPool """

        data = self._type_map[_type] if _type else list(self._id_map.values())
        return random.choice(data)

    def draw_many(self, q_num, _type=None):
        num, iter_num = q_num, 0
        res = set()
        subtype_list = []
        while num > 0:
            iter_num += 1
            if iter_num > 1000:
                raise ValueError(
                    f"question number {q_num} is too large, " "make it smaller"
                )
            qa_set = self.random_draw(_type)
            _sub_type = qa_set._sub_type
            if qa_set in res or _sub_type in subtype_list:
                continue
            if _sub_type is not None:
                subtype_list.append(_sub_type)
            num -= 1
            res.add(qa_set)
        return res

    def get_by_id(self, _id: str) -> QASet:
        """ Get a specific QASet by QASet.id attribute """
        _id = int(_id)
        return self._id_map.get(_id)

    def load_from_excel(self, excel_fp: str):
        """ 1. read from excel
        2. create QASet objects from excel data
        3. add QASet objects into self._pool
        """
        qa_sheet = pandas.read_excel(excel_fp)
        rows_num = len(qa_sheet)
        cols_num = len(qa_sheet.columns)
        for i in range(0, rows_num):
            try:
                qa_set_id = int(qa_sheet.iloc[i][3])
            except Exception as e:
                continue
            qa_set_qn = qa_sheet.iloc[i][4]
            if self.get_by_id(qa_set_id) == None:
                qa_set_type = qa_sheet.iloc[i][0]
                qa_set_subtype = qa_sheet.iloc[i][2]
                qa_set_options = tuple(qa_sheet.iloc[i][j] for j in range(5, cols_num))

                # remove None
                qa_set_options_copy, qa_set_options = qa_set_options, []
                for option in qa_set_options_copy:
                    if str(option) != "nan":
                        qa_set_options.append(option)
                qa_set_options = tuple(qa_set_options)

                qa_set = QASet(
                    qa_set_id, qa_set_type, qa_set_qn, qa_set_options, qa_set_subtype
                )
                self.add(qa_set)
            else:
                self.get_by_id(qa_set_id).append_rephrase(qa_set_qn)

    def write_to_json(self, export_fp: str):
        """
        get all QASet objects from self._pool
        convert every QASet object into a dictionary
        write the list of dictionaries into json
        """

        with open(export_fp, "w") as f:
            lst = []
            for qa_set in self._pool:
                lst.append({tag: getattr(qa_set, tag) for tag in QASet.info_list})
            json.dump(lst, open(export_fp, "w"), indent=4)

    def load_from_json(self, json_fp: str):
        """ 1. read from json
        2. create QASet objects from json data
        3. add QASet objects into self._pool
        """

        qadict_lst = json.load(open(json_fp))
        for qa_dict in qadict_lst:
            self.add(QASet(**qa_dict))


def get_qa_pool_from_json(qa_bank_json: str) -> QASetPool:
    assert Path(qa_bank_json).is_file()

    qa_pool = QASetPool()
    qa_pool.load_from_json(Path(qa_bank_json))
    return qa_pool


if __name__ == "__main__":
    pool = QASetPool()
    pool.load_from_excel("example/qa_bank_sample.xlsx")
    pool.write_to_json("example/qa_bank_sample.json")
    # q = pool.random_draw()
    # print(q)
