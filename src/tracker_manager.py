#!/usr/bin/env python3

import requests
import bencodepy

from meta_info import MetaInfo

DEFAULT_INTERVAL = 120

class TrackerManager():

    """
    Maintains communication with the torrent tracker
    """

    def __init__(self, meta_info: MetaInfo, peer_id, event_server):
        
        self._meta_info = meta_info
        self._peer_id = peer_id
        self._server = event_server

        self._left = meta_info.info['length']

        self._uploaded = 0
        self._downloaded = 0
        self._interval = DEFAULT_INTERVAL

        self._stats = {}
        self._peers = []

        print(self.contact_tracker())

        super().__init__()

    def contact_tracker(self, event="started"):
        url = self._meta_info.announce

        data = {
            'info_hash': self._meta_info.info_hash,
            'peer_id': self._peer_id,
            'port': self._server.port,
            'uploaded': self._uploaded,
            'downloaded': self._downloaded,
            'left': self._left,
            'event': event,
            'compact': 0
        }

        # Support for udp trackers in the future
        if url.startswith("http"):
            resp = requests.get(url, params=data)
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

            if 'failure reason' in ret_resp.keys():
                print("Tracker failure for: {}".format(ret_resp['failure reason'].decode()))
                return None

            self.interval = ret_resp['interval']
            self._stats = {
                'complete': ret_resp['complete'],
                'incompete': ret_resp['incomplete']
            }
            
            try:
                test_peer_id = ret_resp['peers'][0]['peer_id']

                self._peers = ret_resp['peers']

            except TypeError as err:
                self._peers = self._parse_binary_peers(ret_resp['peers'])

            print(self._peers)
            return ret_resp

    def timer_event(self):
        pass
    
    # Parses peers results based on either bencoded dictionary or compact form
    def _parse_binary_peers(self, raw_peers):
        peers = []

        # raw_peers is in compact form
        for i in range(0, len(raw_peers), 6):
            peer_ip = f"{raw_peers[i]}.{raw_peers[i+1]}.{raw_peers[i+2]}.{raw_peers[i+3]}"
            peer_port = int.from_bytes(raw_peers[i+4:i+6], byteorder="big")
            peers.append({
                "peer_id": f"peer-{i//6}",
                "ip": peer_ip,
                "port": peer_port
            })

        return peers

    @property
    def peers(self):
        return self._peers
