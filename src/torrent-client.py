#!/usr/bin/env python

"""
This file will start up the torrent client and begin the download as a cmd arg
"""

import sys
from bencodepy import decode_from_file

# Debugging tool
# import pdb; pdb.set_trace()

"""
Torrent file keys for decoding data
"""
ANNOUNCE = b'announce'
CREATED_BY = b'created_by'
CREATION_DATE = b'creation_date'
INFO = b'info'

class TorrentClient():
    """
    Steps:
    1) Read torrent file
        We need the tracker ip, piece hashes, and 

    2) Contact the torrent tracker

    3) Connect to peers

    4) Download pieces w/ bittorrent

    5) Assemble pieces to file

    """
    def __init__(self, tf_name):
        # Torrent client initialization steps

        raw_tf_data = decode_from_file(tf_name)
        
        print(raw_tf_data[ANNOUNCE])

        super().__init__()




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./torrent-client torrent-file-name")
        exit(1)

    tf_name = sys.argv[1]
    client = TorrentClient(tf_name)
