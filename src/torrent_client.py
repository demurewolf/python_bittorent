#!/usr/bin/env python

"""
This file will start up the torrent client and begin the download as a cmd arg
"""

import sys
from hashlib import sha1

import bencodepy

from tracker_manager import TrackerManager


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

        self.tracker = TrackerManager(url=raw_tf_data[ANNOUNCE].decode(), filesize=self.info['length'])


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
        """
        Steps:
        1) Read torrent file -- torrent-client
            We need the tracker ip, piece hashes, and 

        2) Contact the torrent tracker -- tracker-handler

        3) Connect to peers -- connection-manager

        4) Download pieces w/ bittorrent -- connection-manager & piece-manager

        5) Assemble pieces to file -- torrent-client & piece-manager

        """
        
        # Announce to tracker
        tracker_resp = self.tracker.contact_tracker(self.info_hash, self.peer_id, self.port)
        print(tracker_resp)

        # Tell tracker we're done downloading
        tracker_resp = self.tracker.contact_tracker(self.info_hash, self.peer_id, self.port, event="stopped")
        print(tracker_resp)
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./torrent-client torrent-file-name")
        exit(1)

    tf_name = sys.argv[1]
    
    client = TorrentClient(tf_name)
    
    client.start_download()
