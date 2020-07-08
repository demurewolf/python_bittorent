#!/usr/bin/env python3

from struct import pack

# All messages are prefixed with the message length



def handshake(info_hash: bytes, peer_id):
    if type(peer_id) == str:
       peer_id = bytes(peer_id, encoding='ascii')
    return b'\x13BitTorrent protocol' + (b'\x00' * 8) + info_hash + peer_id

def keepalive():
    return b'\x00'

def choke():
    return pack('!ib', 1, 0)

def unchoke():
    return pack('!ib', 1, 1)

def interested():
    return pack('!ib', 1, 2)

def uninterested():
    return pack('!ib', 1, 3)

def have(piece_index):
    return pack('!ibi', 5, 4, piece_index)

def bitfield(pieces: bytes):
    msg_len = 1 + len(pieces)
    return pack('!ib', msg_len, 5) + pieces

def request(piece_index, begin, length):
    return pack('!ibiii', 13, 6, piece_index, begin, length)

def piece(piece_index, begin, data: bytes):
    msg_len = 9
    return pack('!ibii', msg_len, 7, piece_index, begin) + data

def cancel(piece_index, begin, length):
    return pack('!ibiii', 13, 8, piece_index, begin, length) 

def port(port_num):
    return pack('!ibi', 5, 9, port_num)