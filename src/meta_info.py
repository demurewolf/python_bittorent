#!/usr/bin/env python3

import bencodepy

from hashlib import sha1

"""
Torrent file keys for decoding data
"""
ANNOUNCE = b'announce'
CREATED_BY = b'created by'
CREATION_DATE = b'creation date'
ENCODING = b'encoding'
INFO = b'info'

class MetaInfo():

    def __init__(self, tf_name):
        raw_data = bencodepy.decode_from_file(tf_name)

        self._announce = raw_data[ANNOUNCE].decode()
        self._created_by = raw_data[CREATED_BY].decode()
        # self._encoding = raw_data[ENCODING].decode()

        from datetime import datetime
        timestamp = datetime.fromtimestamp(raw_data[CREATION_DATE])
        self._creation_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        self._info = {}
        for k in raw_data[INFO]:
            self._info[k.decode()] = raw_data[INFO][k]

        # Calculate infohash
        binfo = bencodepy.encode(self._info)
        hasher = sha1()
        hasher.update(binfo)
        self._info_hash = hasher.digest()

    def print_metadata(self):
        print("======== TORRENT FILE METADATA ========")
        print(f"ANNOUNCE URL - {self._announce}")
        print(f"CREATED BY - {self._created_by}")
        # print(f"ENCODING - {self._encoding}")
        print(f"CREATION DATE - {self._creation_date}")
        print("=======================================")

    @property
    def info(self):
        return self._info

    @property
    def announce(self):
        return self._announce

    @property
    def info_hash(self):
        return self._info_hash