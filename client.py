#!/usr/bin/env python3

import socket
from sys import argv
from evdev import InputDevice, ecodes

class Joypad(object):

    def __init__(self, path):
        self.path = path
        self.device = InputDevice(self.path)
        self.left_z = 0
        self.right_z = 0

    def read_loop(self):
        for event in self.device.read_loop():
            if event.type in (ecodes.EV_KEY, ecodes.EV_ABS):
                yield self._translate_event(event)

    def _translate_event(self, event):
        type = {ecodes.EV_ABS: 'axis', ecodes.EV_KEY: 'button'}[event.type]
        if event.code in (16, 17):
            type = 'pov'
        if type == 'axis' and event.code not in (16, 17):
            if event.code in (2, 5):
                code = 'Z'
                value = self._z_axis_value(event)
            else:
                code = {
                    0: 'X',
                    1: 'Y',
                    3: 'RX',
                    4: 'RY',
                }[event.code]
                value = (event.value + 0x8000) // 2
        elif type == 'pov':
            code = self._pov_code(event)
            value = self._pov_value(event)
        else:
            code = {
                304: 1,  # A
                305: 2,  # B
                307: 3,  # X
                308: 4,  # Y
                310: 5,  # left bumper
                311: 6,  # right bumper
                314: 7,  # back
                315: 8,  # start
                317: 9,  # left stick button
                318: 10, # right stick button
            }[event.code]
            value = event.value

        return f'{type} {code} {value}\n'

    def _z_axis_value(self, event):
        if event.code == 2:
            self.left_z = event.value
        else:
            self.right_z = this_z = event.value

        return 64 * (self.left_z - self.right_z) + 0x4000

    ### TODO
    def _pov_code(self, event):
        return 1

    ### TODO
    def _pov_value(self, event):
        return abs(event.value)


class JoypadClient(object):

    def __init__(self, host, port, joypad, auth):
        self.auth = auth
        self.joypad = joypad
        self.socket = socket.socket()
        self.socket.connect((host, port))
        self.socket.send(auth + b'\n')

    def start_loop(self):
        for event in self.joypad.read_loop():
            self.socket.send(event.encode('utf-8'))


def main():
    with open('auth', 'rb') as f:
        auth = f.read().strip()
    joypad = Joypad(argv[1])
    host, port = argv[2].split(':')
    port = int(port)
    joypad_client = JoypadClient(host, port, joypad, auth)
    joypad_client.start_loop()

if __name__ == '__main__':
    main()
