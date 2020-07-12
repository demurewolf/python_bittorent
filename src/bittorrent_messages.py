#!/usr/bin/env python3

import logging
from struct import pack, unpack

from bitarray import bitarray

# Message codes used in the protocol
CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
UNINTERESTED = 3
HAVE = 4
BITFIELD = 5
REQUEST = 6
PIECE = 7
CANCEL = 8
PORT = 9


def handshake(info_hash: bytes, peer_id):
    if type(peer_id) == str:
       peer_id = bytes(peer_id, encoding='ascii')
    return b'\x13BitTorrent protocol' + (b'\x00' * 8) + info_hash + peer_id

def keepalive():
    return b'\x00'

def choke():
    return pack('!ib', 1, CHOKE)

def unchoke():
    return pack('!ib', 1, UNCHOKE)

def interested():
    return pack('!ib', 1, INTERESTED)

def uninterested():
    return pack('!ib', 1, UNINTERESTED)

def have(piece_index):
    return pack('!ibi', 5, HAVE, piece_index)

def bitfield(pieces: bytes):
    msg_len = 1 + len(pieces)
    return pack('!ib', msg_len, BITFIELD) + pieces

def request(piece_index, begin, length):
    return pack('!ibiii', 13, REQUEST, piece_index, begin, length)

def piece(piece_index, begin, data: bytes):
    msg_len = 9
    return pack('!ibii', msg_len, PIECE, piece_index, begin) + data

def cancel(piece_index, begin, length):
    return pack('!ibiii', 13, CANCEL, piece_index, begin, length) 

def port(port_num):
    return pack('!ibi', 5, PORT, port_num)

def decode_message(buff):
    if len(buff) >= 4:
        msg_len = unpack('!i', buff[0:4])[0]

        if msg_len > 0:
            msg_type = buff[4]
            
            if msg_type >= HAVE:
                param_switcher = {
                    HAVE: _sw_have,
                    BITFIELD: _sw_bitfield,
                    REQUEST: _sw_request,
                    PIECE: _sw_piece,
                    CANCEL: _sw_cancel,
                    PORT: _sw_port
                }
                
                msg_data = buff[5:]
                
                params = param_switcher.get(msg_type)(msg_data)

                return (msg_len, msg_type, params)

            else:
                return (msg_len, msg_type)

        else:
            return (msg_len, )


def _sw_have(buff):
    return {
        'piece_index': unpack('!i', buff)[0]
    }

def _sw_bitfield(buff):
    bf = bitarray()
    bf.frombytes(buff)
    return {
        'bitfield': bf
    }

def _sw_request(buff):
    (p_i, b, l) = unpack('!iii', buff)
    return {
        'piece_index': p_i,
        'begin': b,
        'length': l
    }

def _sw_piece(buff):
    (p_i, b) = unpack('!ii', buff[0:8])
    return {
        'piece_index': p_i,
        'begin': b,
        'data': buff[8:]
    }

def _sw_cancel(buff):
    (p_i, b, l) = unpack('!iii', buff)
    return {
        'piece_index': p_i,
        'begin': b,
        'length': l
    }

def _sw_port(buff):
    return {
        'port': unpack('!i', buff)
    }