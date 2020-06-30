#!/usr/bin/env python

"""
This file will start up the torrent client and begin the download as a cmd arg
"""

import sys
from hashlib import sha1

import bencodepy

from tracker_manager import TrackerManager
from connection_manager import ConnectionManager


# Debugging tool
import pdb; pdb.set_trace()

"""
Torrent file keys for decoding data
"""
ANNOUNCE = b'announce'
CREATED_BY = b'created by'
CREATION_DATE = b'creation date'
ENCODING = b'encoding'
INFO = b'info'

class TorrentClient():
    
    def __init__(self, tf_name):
        # Torrent client initialization steps

        raw_tf_data = bencodepy.decode_from_file(tf_name)
        
        self.print_metadata(raw_tf_data)

        # Gather info data
        self.info = {}
        for k in raw_tf_data[INFO]:
            self.info[k.decode()] = raw_tf_data[INFO][k]

        # Calculate info hash
        binfo = bencodepy.encode(self.info)
        hasher = sha1()
        hasher.update(binfo)
        self.info_hash = hasher.digest()

        # Generate peer id
        from random import choices
        base_peer_id = "-JRW0010-"
        rand_nums = choices(range(10), k=(20 - len(base_peer_id)))
        rand_nums_str = ''.join([str(x) for x in rand_nums])
        self.peer_id = base_peer_id + rand_nums_str

        # Find available port on host
        self.port = 6881

        # Collect subcomponents
        self.tracker = TrackerManager(url=raw_tf_data[ANNOUNCE].decode(), filesize=self.info['length'])
        self.conn_manager = None

        super().__init__()

    def print_metadata(self, data):
        print("======== TORRENT FILE METADATA ========")
        print(f"ANNOUNCE URL - {data[ANNOUNCE].decode()}")
        print(f"CREATED BY - {data[CREATED_BY].decode()}")
        print(f"ENCODING - {data[ENCODING].decode()}")

        from datetime import datetime
        timestamp = datetime.fromtimestamp(data[CREATION_DATE])
        print(f"CREATION DATE - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=======================================")

    def start_download(self):

        # Announce to tracker
        tracker_resp = self.tracker.contact_tracker(self.info_hash, self.peer_id, self.port)
        print(tracker_resp)

        peers = self.tracker.get_peers(tracker_resp['peers'])

        if peers and len(peers) > 0:
            self.conn_manager = ConnectionManager(peers=peers, info_hash=self.info_hash)

            self.conn_manager.initiate_connections()

        else:
            print("Problem getting peers from tracker...")
            print(tracker_resp)
    
    def stop_download(self):
       # Tell tracker we're done downloading
        tracker_resp = self.tracker.contact_tracker(self.info_hash, self.peer_id, self.port, event="stopped")
        print(tracker_resp)

        # Terminate peer connections
        if self.conn_manager:
            self.conn_manager.terminate_connections()



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./torrent-client torrent-file-name")
        exit(1)

    tf_name = sys.argv[1]
    
    client = TorrentClient(tf_name)
    
    client.start_download()
    client.stop_download()