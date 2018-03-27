#!/usr/bin/env python3

import socketserver
import pyvjoy
from pyvjoy.exceptions import vJoyFailedToAcquireException


class Joypad(object):

    def __init__(self):
        self.joypad = self._get_free_joypad_device()

    def set_axis(self, axis, value):
        self.joypad.set_axis(self._translate_axis(axis), value)

    def set_button(self, button, value):
        self.joypad.set_button(button, value)

    def set_pov(self, pov, value):
        self.joypad.set_disc_pov(pov, value)

    def _translate_axis(self, name):
        return {
            'X':  pyvjoy.HID_USAGE_X,
            'Y':  pyvjoy.HID_USAGE_Y,
            'Z':  pyvjoy.HID_USAGE_Z,
            'RX': pyvjoy.HID_USAGE_RX,
            'RY': pyvjoy.HID_USAGE_RY,
            'RZ': pyvjoy.HID_USAGE_RZ,
        }[name]

    def _get_free_joypad_device(self):
        for i in range(1, 9):
            try:
                joypad = pyvjoy.VJoyDevice(i)
                return joypad
            except vJoyFailedToAcquireException:
                continue
        else:
            raise Exception("No free virtual joypads available")


class JoypadServerHandler(socketserver.StreamRequestHandler):

    def handle(self):
        if self.rfile.readline(0x2000).strip() != self.server.auth:
            return
        # deleted automatically when this exits
        joypad = Joypad()
        data = self.rfile.readline()
        while data:
            self.data = data.decode('utf-8').strip().split(' ')
            if self.data[0] == 'quit':
                break
            elif self.data[0] == 'axis':
                joypad.set_axis(self.data[1], int(self.data[2]))
            elif self.data[0] == 'button':
                joypad.set_button(int(self.data[1]), int(self.data[2]))
            elif self.data[0] == 'pov':
                joypad.set_pov(int(self.data[1]), int(self.data[2]))

            data = self.rfile.readline()


class JoypadServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        self.auth = kwargs.pop('auth')
        super(JoypadServer, self).__init__(*args, **kwargs)


def main():
    with open('auth', 'rb') as f:
        auth = f.read().strip()
    joypad_server = JoypadServer(('', 9890), JoypadServerHandler, auth=auth)
    joypad_server.serve_forever()

if __name__ == '__main__':
    main()
