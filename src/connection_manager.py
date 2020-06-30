#!/usr/bin/env python

class ConnectionManager():

    """
    Maintains connections w/ swarm peers for download
    """

    def __init__(self, peers, info_hash):

        self.peer_addrs = peers # This will contain ip/port info for each peer
        self.info_hash = info_hash

        self.peers = [] # This contians each connected peer's socket

        super().__init__()

    def initiate_connections(self):
        pass
    
    def download_from_peers(self):
        pass

    def upload_to_peers(self):
        pass

    def terminate_connections(self):
        pass