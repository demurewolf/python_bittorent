#!/usr/bin/env python

from bittorrent_proxy import BitTorrentProxy

class ConnectionManager():

    """
    Maintains connections w/ swarm peers for download
    """

    def __init__(self, peers, peer_id, info_hash, event_server):

        self._peer_addrs = peers # This will contain ip/port info for each peer
        self._peer_id = peer_id
        self._info_hash = info_hash
        self._server = event_server

        self.peers = {} # This contians each connected peer's socket -> proxy obj

        super().__init__()

    def initiate_connections(self):
        for p in self._peer_addrs:
            addr = (p['ip'], p['port'])
            proxy = BitTorrentProxy(None, addr, self._peer_id, self._info_hash, self._server)
            self._server.register_for_read_events(proxy.sock)

    def terminate_connections(self):
        pass

    def add_connection(self, peer_addr):
        self._peer_addrs.append(peer_addr)

    def update_peers(self):
        pass