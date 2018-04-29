from .form import is_fulfil
from .form import merge_information
from .output import require_information, answer_and_reset
from .filebase import exist, add_user, update_state, get_state, remove_user


transition = {
    0: [{
        'check_method': is_fulfil,
        'invert': True,
        'print': require_information,
        'destination': 1,
    }, {
        'check_method': is_fulfil,
        'invert': False,
        'print': answer_and_reset,
        'destination': 0,
    }],
    1: [{
        'check_method': is_fulfil,
        'invert': False,
        'print': answer_and_reset,
        'destination': 0,
    }, {
        'check_method': is_fulfil,
        'invert': True,
        'print': require_information,
        'destination': 1,
    }]
}


class StateMachine:

    def __init__(self, output_method, token):
        self.token = token
        self.output_method = output_method
        if not exist(self.token):
            self.state = 0
            self.intention = -1
            self.information = {
                'cmd': '',
                'course': '',
                'period': '',
                'date': '',
                'month': '',
                'year': '',
            }
            add_user(self.token)
        else:
            self.load_from_filebase()

    def get_input(self, intention, information):
        if self.intention != -1:
            intention = self.intention
        else:
            self.intention = intention
        self.information = merge_information(self.information, information)
        for trans in transition[self.state]:
            if trans['check_method'](
                    intention, self.information) != trans['invert']:
                trans['print'](self, self.output_method,
                               intention, self.information)
                self.state = trans['destination']
                self.save_to_filebase()
                return

    def restart(self):
        self.intention = -1
        self.information = {
            'cmd': '',
            'course': '',
            'period': '',
            'date': '',
            'month': '',
            'year': '',
        }

    def load_from_filebase(self):
        machine = get_state(self.token)['state']
        print(machine)
        self.state = machine['state']
        self.intention = machine['intention']
        self.information = machine['information']

    def save_to_filebase(self):
        this_machine = {
            'state': self.state,
            'intention': self.intention,
            'information': self.information
        }
        update_state(self.token, this_machine)
        return this_machine

    def remove(self):
        remove_user(self.token)
