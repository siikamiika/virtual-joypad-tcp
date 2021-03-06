#!/usr/bin/env python3

import socket
from sys import argv
from evdev import InputDevice, ecodes
import os
from os.path import dirname, realpath

os.chdir(dirname(realpath(__file__)))

class Joypad(object):

    def __init__(self, path):
        self.path = path
        self.device = InputDevice(self.path)
        self.left_z = 0
        self.right_z = 0
        self.pov_down = {
            16: [],
            17: [],
        }

    def read_loop(self):
        for event in self.device.read_loop():
            if event.type in (ecodes.EV_KEY, ecodes.EV_ABS):
                translated_event = self._translate_event(event)
                if translated_event:
                    yield translated_event

    def _translate_event(self, event):
        type = {ecodes.EV_ABS: 'axis', ecodes.EV_KEY: 'button'}[event.type]
        if event.code in (16, 17):
            type = 'pov'

        if type == 'axis':
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
                value = (min(int(event.value * 1.20), 0x8000) + 0x8000) // 2
        elif type == 'pov':
            code = self._pov_code(event)
            value = self._pov_value(event)
            if value == 0:
                out = []
                for _ in range(len(self.pov_down[code])):
                    c = self.pov_down[code].pop(0)
                    out.append(f'pov {c} 0\n')
                return ''.join(out)
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
                # 11-14: POV hack
                316: 15, # xbox button
            }[event.code]
            value = event.value

        return f'{type} {code} {value}\n'

    def _z_axis_value(self, event):
        if event.code == 2:
            self.left_z = event.value
        else:
            self.right_z = event.value

        return 64 * (self.left_z - self.right_z) + 0x4000

    ### hack
    def _pov_code(self, event):
        if event.code == 16:
            if event.value == -1:
                self.pov_down[16].append(11)
                return 11
            elif event.value == 1:
                self.pov_down[16].append(12)
                return 12
            else:
                return 16
        elif event.code == 17:
            if event.value == -1:
                self.pov_down[17].append(13)
                return 13
            elif event.value == 1:
                self.pov_down[17].append(14)
                return 14
            else:
                return 17

    ### hack
    def _pov_value(self, event):
        return abs(event.value)


class JoypadClient(object):

    def __init__(self, host, port, joypad, auth):
        self.auth = auth
        self.joypad = joypad
        self.socket = socket.socket()
        self.socket.settimeout(5)
        self.socket.connect((host, port))
        self.socket.send(auth + b'\n')
        self.socket.settimeout(0)

    def start_loop(self):
        for event in self.joypad.read_loop():
            self.socket.settimeout(1)
            self.socket.send(event.encode('utf-8'))
            self.socket.settimeout(0)


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
