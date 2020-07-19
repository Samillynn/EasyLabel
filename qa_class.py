import numpy as np
from collections import abc
import json
import random
import pandas
from pathlib import Path
from typing import List, Dict, Tuple, Set, Iterable, Union

class QASet:
    
    info_list = ['id_', 'type_', 'sub_type', 'qns', 'options']

    def __init__(
        self, id_: int, type_: str, qns: Union[str, List[str]], options: Iterable[str], sub_type: str = None
    ):
        # id should be immutable
        self.id_: int = int(id_)
        # type and sub_type should be immutable

        self.type_ = type_
        self.sub_type: str = sub_type

        if isinstance(qns, str):
            self.qns = [qns]
        elif isinstance(qns, abc.Sequence):
            self.qns = list(qns)
        else:
            raise ValueError(f'qns of QASet should be str or List[str], but not {qns}({qns.__class__})')

        # options should be immutable
        self.options: Tuple[str] = tuple(options)

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
            raise ValueError(f'can\'t append {qn}({qn.__class__}) to QASet')


class QASetPool:
    def __init__(self):
        self._pool: List[QASet] = []
        self._id_map: Dict[str: QASet] = {}
        self._type_map = {}

    def add(self, qa_set: QASet):
        """ Add a QASet object into self._pool """
        assert isinstance(qa_set, QASet)

        # add qa_set to _pool and _id_map
        try:
            self._id_map[qa_set.id_].append_rephrase(qa_set.qns)
        except KeyError:
            self._id_map[qa_set.id_] = qa_set
            self._pool.append(qa_set)

            # add qa_set to _type_map
            type_ = qa_set.type_
            try:
                self._type_map[type_].append(qa_set)
            except KeyError:
                self._type_map[type_] = [qa_set]


        

    def random_draw(self, type_=None, duration: float = None) -> QASet:
        """ Randomly draw a QASet from self._QASetPool

        if video duration is not supplied, draw randomly from the whole pool

        if video duration is supplied, based on the video duration -> determine
        long/medium/short video -> filter pool -> randomly draw from filtered
        """

        data = self._type_map[type_] if type_ else list(self._id_map.values())
        return random.choice(data)


    def draw_many(self, q_num, type_=None):
        num, iter_num = q_num, 0
        res = set()
        subtype_list = []
        while num > 0:
            iter_num += 1
            if iter_num > 1000:
                raise ValueError(f'question number {q_num} is too large, '
                                  'make it smaller')
            qa_set = self.random_draw(type_)
            sub_type = qa_set.sub_type
            if qa_set in res or sub_type in subtype_list:
                continue
            if sub_type is not None:
                subtype_list.append(sub_type)
            num -= 1
            res.add(qa_set)

        return res
                    


    def get_by_id(self, id_: str) -> QASet:
        """ Get a specific QASet by QASet.id attribute """
        id_ = int(id_)
        return self._id_map.get(id_)


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
            if (self.get_by_id(qa_set_id) == None):
                qa_set_type = qa_sheet.iloc[i][0]
                qa_set_subtype = qa_sheet.iloc[i][2] 
                qa_set_options= tuple(qa_sheet.iloc[i][j] for j in range(5, cols_num))
                qa_set = QASet(qa_set_id, qa_set_type, qa_set_qn, qa_set_options, qa_set_subtype)
                self.add(qa_set)
            else:
                self.get_by_id(qa_set_id).append_rephrase(qa_set_qn)

    def write_to_json(self, export_fp: str):
        """
        get all QASet objects from self._pool
        convert every QASet object into a dictionary
        write the list of dictionaries into json
        """

        with open(export_fp, 'w') as f:
            lst = []
            for qa_set in self._pool:
                lst.append(
                     {tag: getattr(qa_set, tag) for tag in QASet.info_list}
                )
            json.dump(lst, open(export_fp, 'w'), indent=4)

                
    def load_from_json(self, json_fp: str):
        """ 1. read from json
        2. create QASet objects from json data
        3. add QASet objects into self._pool
        """

        qadict_lst = json.load(open(json_fp))
        qaset_pool = QASetPool()
        for qa_dict in qadict_lst:
            qaset_pool.add(QASet(**qa_dict))

