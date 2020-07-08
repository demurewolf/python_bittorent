#!/usr/bin/env python3

import socket

import bittorrent_messages

"""
Notes: if a socket is not provided then the proxy should initiate connection with the
peer, otherwise the proxy should expect to receive the initial handshake
"""

class BitTorrentProxy():

    def __init__(self, sock, addr, peer_id, info_hash, server):
        self._sock = sock
        self._addr = addr
        self._peer_id = peer_id
        self._info_hash = info_hash
        self._server = server

        self._tosend = None

    @property
    def sock(self):
        return self._sock

    def read_event(self):
        data = self._sock.recv(1024)

        if data:
            # TODO
            self._tosend = data
            self._server.register_for_write_events(self._sock, self)

        else:
            self.close_connection()

    def write_event(self):
        if self._tosend:
            self._sock.sendall(self._tosend)
            self._tosend = None

        self._server.unregister_for_write_events(self._sock)

    def close_connection(self):
        self._tosend = None
        self._server.unregister_for_read_events(self._sock)
        self._server.unregister_for_write_events(self._sock)
        self._sock.close()