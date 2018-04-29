import json
required_form = json.load(open('config/require_form.json'))


def merge_information(information, new_information):
    for i in new_information:
        if new_information[i]:
            information[i] = new_information[i]
    return information


def is_fulfil(intention, information):
    fulfil = True
    for i in required_form[intention]:
        fulfil = fulfil and (information[i] != '')
    return fulfil
