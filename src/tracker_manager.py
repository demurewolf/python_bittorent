#!/usr/bin/env python

import requests
import bencodepy

class TrackerManager():

    def __init__(self, url, filesize):
        
        self.url = url
        self.uploaded = 0
        self.downloaded = 0
        self.left = filesize

        super().__init__()

    def contact_tracker(self, info_hash, peer_id, port, event="started"):
        data = {
            'info_hash': info_hash,
            'peer_id': peer_id,
            'port': port,
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'left': self.left,
            'event': event
        }

        if self.url.startswith("http"):
            resp = requests.get(self.url, params=data)
        else:
            resp = None

        if not resp or resp.status_code != 200:
            print("Problems w/ tracker")
        else:
            dec_resp = bencodepy.decode(resp.content)
            ret_resp = {}
            for k in dec_resp:
                ret_resp[k.decode()] = dec_resp[k]

            return ret_resp