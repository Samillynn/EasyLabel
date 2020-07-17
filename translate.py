import json
import os
from parse import parse, parse_question_sheet, parse_option_sheet
from expand import expand
from write import write_outfile

def main(label_path: str, option_sheet_path=None, question_sheet_path=None):
    ori_dict = parse(label_path)
    option_list = parse_option_sheet(option_sheet_path)
    ques_list = parse_question_sheet(question_sheet_path)
    exp_dict = expand(ori_dict, option_list, ques_list)
    name, ext = os.path.splitext(label_path)
    exp_label_path = name + '-pprint' + ext
    json_path = name + '.json'
    write_outfile(exp_dict, exp_label_path)
    json.dump(exp_dict, open(json_path, 'w'), indent=4)
    

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:4])
