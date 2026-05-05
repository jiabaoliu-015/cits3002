from dataclasses import dataclass

from config import (
    SRC_PORT,
    DST_PORT,
    TRANSPORT_HEADER_SIZE,
    NETWORK_HEADER_SIZE,
    DEFAULT_TTL,
    UDP_PROTOCOL,
    ETH_TYPE_IPV4,
    DATA,
    ACK,
)

@dataclass
class Segment:
    src_port: int
    dst_port: int
    length: int
    checksum: int
    seg_type: int
    seq: int
    data: str


def compute_checksum(segment):
    checksum = 0

    fields = [
        segment.src_port,
        segment.dst_port,
        segment.length,
        segment.seg_type,
        segment.seq
    ]

    for value in fields:
        checksum ^= value

    for char in segment.data:
        checksum ^= ord(char)

    return checksum & 0xFFFF

def verify_checksum(segment):
    expected_checksum = compute_checksum(segment)
    return segment.checksum == expected_checksum

def create_data_segment(data, seq):
    segment = Segment(
        src_port=SRC_PORT,
        dst_port=DST_PORT,
        length=TRANSPORT_HEADER_SIZE + len(data),
        checksum=0,
        seg_type=DATA,
        seq=seq,
        data=data
    )

    segment.checksum = compute_checksum(segment)

    return segment


def create_ack_segment(seq):
    segment = Segment(
        src_port=DST_PORT,
        dst_port=SRC_PORT,
        length=TRANSPORT_HEADER_SIZE,
        checksum=0,
        seg_type=ACK,
        seq=seq,
        data=""
    )

    segment.checksum = compute_checksum(segment)

    return segment

@dataclass
class Packet:
    src_ip: str
    dst_ip: str
    ttl: int
    protocol: int
    total_length: int
    payload: Segment

def create_ip_packet(src_ip, dst_ip, segment):
    packet = Packet(
        src_ip=src_ip,
        dst_ip=dst_ip,
        ttl=DEFAULT_TTL,
        protocol=UDP_PROTOCOL,
        total_length=NETWORK_HEADER_SIZE + segment.length,
        payload=segment
    )

    return packet
        
@dataclass
class Frame:
    dst_mac: str
    src_mac: str
    eth_type: int
    payload: Packet

def create_ethernet_frame(src_mac, dst_mac, packet):
      frame = Frame(
        dst_mac=dst_mac,
        src_mac=src_mac,
        eth_type=ETH_TYPE_IPV4,
        payload=packet
    )
      return frame