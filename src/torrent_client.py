#!/usr/bin/env python3

"""
This file will start up the torrent client and begin the download as a cmd arg
"""

import sys
import bencodepy

from socket import gethostname

from event_server import EventServer
from meta_info import MetaInfo
from tracker_manager import TrackerManager
from connection_manager import ConnectionManager

# Debugging tool
# import pdb; pdb.set_trace()

class TorrentClient():
    
    def __init__(self, tf_name):
        self._port = 6881
        self._event_server = EventServer((gethostname(), self._port))
        self._meta_info = MetaInfo(tf_name)

        # Generate peer id
        from random import choices
        base_peer_id = "-JRW0010-"
        rand_nums = choices(range(10), k=(20 - len(base_peer_id)))
        rand_nums_str = ''.join([str(x) for x in rand_nums])
        self.peer_id = base_peer_id + rand_nums_str

        # Collect subcomponents
        self.tracker = TrackerManager(url=self._meta_info.announce, filesize=self._meta_info.info['length'])
        self.conn_manager = None

        super().__init__()

    def start_download(self):

        # Announce to tracker
        tracker_resp = self.tracker.contact_tracker(self._meta_info.info_hash, self.peer_id, self._port)
        print(tracker_resp)

        peers = self.tracker.get_peers(tracker_resp['peers'])

        if peers and len(peers) > 0:
            # self.conn_manager = ConnectionManager(peers=peers, info_hash=self.info_hash)

            # self.conn_manager.initiate_connections()
            pass
        else:
            print("Problem getting peers from tracker...")
            print(tracker_resp)
    
    def stop_download(self):
       # Tell tracker we're done downloading
        tracker_resp = self.tracker.contact_tracker(self._meta_info.info_hash, self.peer_id, self._port, event="stopped")
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