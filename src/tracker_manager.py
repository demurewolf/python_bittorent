#!/usr/bin/env python

import requests
import bencodepy

DEFAULT_INTERVAL = 120

class TrackerManager():

    """
    Maintains communication with the torrent tracker
    """

    def __init__(self, url, filesize):
        
        self.url = url
        self.left = filesize

        self.uploaded = 0
        self.downloaded = 0
        self.interval = DEFAULT_INTERVAL

        self.stats = {}

        super().__init__()

    def contact_tracker(self, info_hash, peer_id, port, event="started"):
        data = {
            'info_hash': info_hash,
            'peer_id': peer_id,
            'port': port,
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'left': self.left,
            'event': event,
            'compact': 1
        }

        # Support for udp trackers in the future
        if self.url.startswith("http"):
            resp = requests.get(self.url, params=data)
        else:
            resp = None

        if not resp or resp.status_code != 200:
            print(f"Status {resp.status_code} for: {resp.content}")
        else:
            # Decode tracker response
            dec_resp = bencodepy.decode(resp.content)
            ret_resp = {}
            for k in dec_resp:
                ret_resp[k.decode()] = dec_resp[k]

            self.interval = ret_resp['interval']
            self.stats = {
                'complete': ret_resp['complete'],
                'incompete': ret_resp['incomplete']
            }

            return ret_resp
    
    # Parses peers results based on either bencoded dictionary or compact form
    def get_peers(self, raw_peers):
        peers = []

        # raw_peers is in compact form
        for i in range(0, len(raw_peers), 6):
            peer_ip = f"{raw_peers[i]}.{raw_peers[i+1]}.{raw_peers[i+2]}.{raw_peers[i+3]}"
            peer_port = int.from_bytes(raw_peers[i+4:i+6], byteorder="big")
            peers.append({
                "peer_id": f"peer-{i//6}",
                "peer_ip": peer_ip,
                "peer_port": peer_port
            })

        return peers
