from typing import List
import re

# helper function

def search_list(pattern, lst):
    pattern = re.compile(pattern)
    for s in lst:
        match = pattern.search(s)
        if match:
            return match

def divide_lines(lines: List[str], pattern: str) -> List[List[str]]:
    """ divide a list of lines into blocks according to occurance of pattern"""
    pattern = re.compile(pattern)
    dividers = [line_no for line_no, line in enumerate(lines) if pattern.search(line)]
    dividers.append(len(lines))
    blocks = [lines[divider:next_divider] for divider, next_divider in zip(dividers, dividers[1:])]
    return blocks


# parse the main label file

def parse(infile: str) -> dict:
    """ parse original information from a label file """
    res_dict = {}
    lines = [line.strip() for line in open(infile) if line.strip()]

    # divide lines to blocks by different videos
    video_blocks = divide_lines(lines, '~')

    # extract  info from each video
    for video_block in video_blocks:

        # parse video name
        video_name = video_block[0].strip('~ \n\t')

        # parse trimpoint and viewpoint
        trimpoint = search_list('\(TIME\)\s*(.*)', video_block[1:]).group(1)
        viewpoint = search_list('\(VIEW\)\s*(.*)', video_block[1:]).group(1)

        # divide each video block into some question blocks
        ques_blocks = divide_lines(video_block, '\?|^#')

        # put parsed info into a dictionary
        ques_lst = [parse_single_ques(ques_block) for ques_block in ques_blocks]
        res_dict[video_name] = {'time': trimpoint, 'view': viewpoint, 'questions': ques_lst}

    return res_dict


def parse_single_ques(lines: List[str]) -> dict:
    """ parse info for a single question """

    ques = lines[0]

    # check if '@' is used in the current funciton
    expand_exist = any(line.startswith('@') for line in lines[1:]) or ques.startswith('#')

    # locate answers
    answer_nos = []
    for no, line in enumerate(lines[1:]):
        if line.startswith('+'):
            lines[no + 1] = line[1:]
            answer_nos.append(no)

    # error when no answer is supplied for any question
    if len(answer_nos) == 0:
        raise Exception('You should mark answers for every question.')

    # extract options and answers when '@' is used
    if expand_exist:
        if len(answer_nos) == 1 and answer_nos[0] == len(lines) - 2:
            options, answers = lines[1:-1], list(lines[-1].upper())
        else:
            raise Exception('When "@" are used, the answer can only be marked at '
                            'the end of each question following a "+".')

    # extract options and answers when '@' is NOT used
    else:
        options = lines[1:]
        answers = [chr(ord('A') + answer_no) for answer_no in answer_nos]

    return {'questions': ques, 'options': options, 'answers': answers}


# parse other sheets

def parse_option_sheet(infile):
    lines = [line.strip() for line in open(infile) if line.strip()]
    option_blocks = divide_lines(lines, '^@')
    return [option_block[1:] for option_block in option_blocks]

def parse_question_sheet(infile):
    lines = [line.strip() for line in open(infile) if line.strip()]
    ques_blocks = divide_lines(lines, '^#')
    return [ques_block[1] for ques_block in ques_blocks]


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 3:
        print(parse(sys.argv[1]))
        print(parse_option_sheet(sys.argv[2]))
        print(parse_question_sheet(sys.argv[3]))
