import re
import random

class Problem():
    def __init__(self, p_question, p_options):
        self.p_question = p_question
        self.p_options = p_options
    

def constructor(infile_path):
    try:
        infile = open(infile_path)
        return infile
    except Exception:
        print('Cannot load in such a file')
        
        
def parse(infile):
    is_key = True
    is_question = True
    Q_set = {}
    
    for line in infile:
        line = line.strip()
        if (line == ''):
            is_key = True
            is_question = True
            Q_set[key] = []
            Q_set[key].append(Problem(question, options))
            
        elif (is_key):
            options = []
            key = re.findall('Key:(\S)',line)
            key = int(key[0])
            is_key = False
            
        elif (is_question):
            question = line
            is_question = False
            
        else:
            options.append(line)            
    return Q_set    


def pick_one(Q_list):
    choice_range = len(Q_list)
    if (choice_range > 1):
        num = random.randint(0, choice_range-1)
        return Q_list[num]
    else:
        return Q_list[0]
    
    
def pick_five(Q_set):
    choice_range = len(Q_set)
    Q_seq_list = random.sample(range(0, choice_range-1), 5)
    return Q_seq_list


def main(infile_path):
    problem_list = []
    infile = constructor(infile_path)
    Q_set = parse(infile)
    Q_seq_list = pick_five(Q_set)
    for i in Q_seq_list:
        Q_list = Q_set[i]
        Q = pick_one(Q_list)
        problem_list.append(Q)
    return problem_list

p_list = main('copy.txt')
for p in p_list:
    print(p.p_options)