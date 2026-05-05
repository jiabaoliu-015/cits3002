from dataclasses import dataclass

from config import SRC_PORT, DST_PORT, TRANSPORT_HEADER_SIZE, DATA, ACK


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