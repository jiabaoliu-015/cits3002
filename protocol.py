from dataclasses import dataclass

from config import (
    SRC_PORT,
    DST_PORT,
    TRANSPORT_HEADER_SIZE,
    NETWORK_HEADER_SIZE,
    DEFAULT_TTL,
    UDP_PROTOCOL,
    ETH_TYPE_IPV4,
    MAX_SEGMENT_DATA_SIZE,
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


def split_data(data):
    blocks = []

    for i in range(0, len(data), MAX_SEGMENT_DATA_SIZE):
        block = data[i:i + MAX_SEGMENT_DATA_SIZE]
        blocks.append(block)

    return blocks


def crc16(data):
    crc = 0xFFFF

    for byte in data:
        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1

            crc &= 0xFFFF

    return crc


def compute_checksum(segment):
    data_bytes = segment.data.encode("utf-8")
    checksum = crc16(data_bytes)

    return checksum & 0xFFFF


def verify_checksum(segment):
    received_checksum = segment.checksum
    recalculated_checksum = compute_checksum(segment)

    return received_checksum == recalculated_checksum


def create_data_segment(data, seq):
    segment = Segment(
        src_port=SRC_PORT,
        dst_port=DST_PORT,
        length=TRANSPORT_HEADER_SIZE + len(data.encode("utf-8")),
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