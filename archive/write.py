def pprint_outfile(expand_dict, outfile_path):
    outfile = open(outfile_path, 'w')
    for video in expand_dict:
        video_name = expand_dict[video]
        time = video_name['time']
        view = video_name['view']
        out = f'~~~~~~{video}~~~~~~\n(TIME) {time}\n(VIEW) {view}\n\n'
        outfile.write(out)
        
        questions = video_name['questions']
        for q_no, q in enumerate(questions):
            q_type = q['type']
            q_question = q['question']
            out = f'Q: {q_question}\n'
            outfile.write(out)
            out = f'Type: {q_type}\n'
            outfile.write(out)
            
            q_options = q['options']
            out_option = ''
            for q_option in q_options:
                out_option += q_option
                out_option += '\n'
            outfile.write(out_option)   
             
            q_answer = q['answers']
            out = f'{q_answer}\n\n'
            outfile.write(out)
       
if __name__ == '__main__':
    q1 = {'question':'is lynn drunk?d','options':['Yes','@3'],'answer':'A'}
    q2 = {'question':'is samill drunk?e','options':['@1','@3'],'answer':'C','type':'E'}
    q3 = {'question':'#1','options':['@2','purple'],'answer':'A','type':'6'}
    videoinfo_dict = {'BV90882938':{'time':'','view':'3','questions':[q1,q2]},
                      'BVsjdheoej':{'time':'','view':'1','questions':[q3]}}
    option_lst = [['Yes'],['grey','blue','red'],['no','No']]
    question_lst = ['what is the color?d']

    expand_dict = expand(videoinfo_dict, option_lst, question_lst)
    write_outfile(expand_dict, '/Users/linyutian/Desktop/write_out.txt', '/Users/linyutian/Desktop/out_json.json')

