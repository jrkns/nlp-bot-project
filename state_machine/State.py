from .form import is_fulfil
from .form import merge_information
from .output import require_information, answer_and_reset
# state


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
        self.state = 0
        self.intention = -1
        self.information = {
            'cmd': 'asdpifojsapfoiajsdf',
            'course': '',
            'period': '',
        }

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
                return

    def restart(self):
        self.intention = -1
        self.information = {
            'cmd': 'asdpifojsapfoiajsdf',
            'course': '',
            'period': '',
        }
