#!/usr/bin/env python

import socket

class BitTorrentProxy():

    def __init__(self, sock, addr, server):
        self._sock = sock
        self._addr = addr
        self._server = server

        self._tosend = None

    def read_event(self):
        data = self._sock.recv(1024)

        if data:
            # TODO
            self._msg = data
            self._server.register_for_write_events(self._sock, self)

        else:
            self.close_connection()

    def write_event(self):
        if self._msg:
            self._sock.sendall(self._msg)
            self._msg = None

        self._server.unregister_for_write_events(self._sock)

    def close_connection(self):
        self._msg = None
        self._server.unregister_for_read_events(self._sock)
        self._server.unregister_for_write_events(self._sock)
        self._sock.close()