#!/usr/bin/env python3

import socket
import select
import time
import logging

from bisect import insort

from bittorrent_proxy import BitTorrentProxy

MIN_PORT = 6881
MAX_PORT = 6889

class EventServer():
    def __init__(self, peer_id, info_hash, timeout=0.01):
        self._readers = {}
        self._writers = {}
        self._timers = []

        self._peer_id = peer_id
        self._info_hash = info_hash
        self._timeout = timeout
        self._timer_id = 0

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)

        for p in range(MIN_PORT, MAX_PORT+1):
            try:
                logging.info("Binding to port {}".format(p))
                addr = (socket.gethostname(), p)
                server.bind(addr)
                server.listen(5)
                self._port = p
                break
            except Exception as e:
                logging.error("Encountered error:\n {}".format(str(e)), exc_info=True)

        if not self._port:
            logging.exception("Cannot find open port on local machine")
            raise Exception("Cannot find open port on local machine")

        self._sock = server
        self._readers[server] = self

    def register_for_read_events(self, sock, proxy):
        if sock not in self._readers:
            self._readers[sock] = proxy

    def unregister_for_read_events(self, sock):
        if sock in self._readers:
            del self._readers[sock]

    def register_for_write_events(self, sock, proxy):
        if sock not in self._writers:
            self._writers[sock] = proxy

    def unregister_for_write_events(self, sock):
        if sock in self._writers:
            del self._writers[sock]

    def register_for_time_event(self, proxy, interval):
        self._timer_id += 1
        insort(self._timers, (time.time()+interval, proxy, self._timer_id))
        return self._timer_id

    def unregister_for_time_event(self, timer_id):
        self._timers = [(timeout, proxy, t_id)
                        for (timeout, proxy, t_id) in self._timers
                        if t_id != timer_id]

    @property
    def port(self):
        return self._port

    def read_event(self):
        # Accept connection
        logging.info("Read event on SelectServer")
        client_s, client_addr = self._sock.accept()
        client_s.setblocking(0)

        proxy = BitTorrentProxy(client_s, client_addr, self._peer_id, self._info_hash, self)

        self._readers[client_s] = proxy

    def write_event(self):
        """
        Communication with client is deffered to proxy
        """
        pass

    def run(self):
        logging.info("Running SelectServer...")
        while 1:
            
            # Check timers
            now = time.time()
            
            while self._timers:
                timer_peek = self._timers[0]
                timeout = timer_peek[0]
                proxy = timer_peek[1]

                if timeout < now:
                    proxy.timer_event()
                    self._timers.pop(0)
                else:
                    break
            
            # Check sockets
            to_read, to_write, in_error = select.select(
                self._readers.keys(), 
                self._writers.keys(), 
                [],
                self._timeout)

            for r in to_read:
                if r in self._readers:
                    self._readers[r].read_event()

            for w in to_write:
                if r in self._writers:
                    self._writers[w].write_event()

            for e in in_error:
                if e in self._readers.keys():
                    self._readers[e].close_connection()
                    del self._readers[e]

                elif e in self._writers.keys():
                    self._writers[e].close_connection()
                    del self._writers[e]
