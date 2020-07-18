import json
from openpyxl import Workbook
from pathlib import Path
from typing import List, Dict, Tuple, Set, Iterable


class QASetPool:
    def __init__(self):
        self._pool: List = []

    def add(self, qa_set: QASet):
        """ Add a QASet object into self._pool """
        assert isinstance(qa_set, QASet)
        self._pool.append(qa_set)

    def random_draw(self, duration: float = None) -> QASet:
        """ Randomly draw a QASet from self._QASetPool

        if video duration is not supplied, draw randomly from the whole pool

        if video duration is supplied, based on the video duration -> determine
        long/medium/short video -> filter pool -> randomly draw from filtered
        """
        # TODO:
        pass

    def get_by_id(self, id: str) -> QASet:
        """ Get a specific QASet by QASet.id attribute """
        # TODO:
        pass

    def load_from_excel(self, excel_fp: str):
        """ 1. read from excel
        2. create QASet objects from excel data
        3. add QASet objects into self._pool
        """
        # TODO:
        pass

    def write_to_json(self, export_fp: str):
        """
        get all QASet objects from self._pool
        convert every QASet object into a dictionary
        write the list of dictionaries into json
        """
        # TODO:
        pass

    def load_from_json(self, json_fp: str):
        """ 1. read from json
        2. create QASet objects from json data
        3. add QASet objects into self._pool
        """
        # TODO:
        pass


class QASet:
    def __init__(self, id: int, type: str, qn: str, options: Iterable[str]):
        # id should be immutable
        self.id: int = id
        # type should be immutable
        self.type: str = type
        # create empty _qns list
        self._qns: List = []
        # each QASet should have at least one qn in the self._qns list
        # additional qn can be added to self._qns as rephrased version of the same qn
        self._qns.append(q)
        # options should be immutable
        self.options: Tuple[str] = tuple(options)

    def get(self) -> Tuple[str, Tuple]:
        """ Randomly select a qn from self._qns
        return the selected qn and the option_lst
        """
        # TODO:
        pass

    def append_rephrase(self, qn):
        """ Append qn into self._qns """
        # TODO:
        pass
