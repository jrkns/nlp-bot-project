# command line
# line
import json
import random
required_form = json.load(open('config/require_form.json'))

answer_require_information = json.load(
    open('config/answer_require_information.json'))
answer_question = json.load(
    open('config/answer_question.json'))


def require_information(machine, output_method, intention, information):
    for i in required_form[intention]:
        if information[i] == '':
            output_method(random.choice(
                answer_require_information[i]), machine.token)
            return


def answer_and_reset(machine, output_method,  intention, information):
    machine.restart()
    output_method(answer_question[intention], machine.token)
