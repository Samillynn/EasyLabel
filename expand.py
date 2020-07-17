import json

def expand(videoinfo_dict, option_lst, question_lst):
    for video in videoinfo_dict:
        video_info = videoinfo_dict[video]
        q_lst = video_info['questions']
        for q in q_lst:
            
             ### expand the question
            q_question = q['question']
            if (q_question[0] == '#'):
                question = question_lst[int(q_question[1:])-1]
                q_type = question[-1]
                q['question'] = question[0:-1]
            else:
                q_type = q_question[-1]
                q['question'] = q['question'][0:-1]
                
            ### expand the type
            if (q_type == '1' or q_type == 'd' or q_type == 'D'):
                q_type = 'Descriptive'
            elif (q_type == '2' or q_type == 'e' or q_type == 'E'):
                q_type = 'Explanatory'
            elif (q_type == '3' or q_type == 'p' or q_type == 'P'):
                q_type = 'Predictive'
            elif (q_type == '4' or q_type == 'r' or q_type == 'R'):
                q_type = 'Reverse Inference'
            elif (q_type == '5' or q_type == 'c' or q_type == 'C'):
                q_type = 'Counterfactual'
            elif (q_type == '6' or q_type == 'i' or q_type == 'I'):
                q_type = 'Introspection'
            q['type'] = q_type
                
            ### expand the option
            q_option = q['options']
            q_options = []
            for i in q_option:
                if (i[0] == '@'):
                    q_options += option_lst[int(i[1:])-1]
                else: 
                    q_options.append(i)
            q['options'] = q_options
    return videoinfo_dict

