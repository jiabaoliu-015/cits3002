from config import (
    HOST_A_IP,
    HOST_B_IP,
    R1_IF1_IP,
    R1_IF2_IP,
    HOST_A_MAC,
    R1_IF1_MAC,
    R1_IF2_MAC,
    HOST_B_MAC,
    DEFAULT_TTL,
)

from protocol import compute_checksum, create_ack_segment


def verify_checksum(segment):
    return segment.checksum == compute_checksum(segment)


def send_data_from_a_to_b(segment):
    """
    Simulate sending one DATA segment from Host A to Host B through Router R1.
    This function currently handles the DATA direction only:
    Host A -> Router R1 -> Host B
    """

    # Host A Layer 4 to Layer 3
    print("Host A: Layer 4: Segment sent to Network Layer")

    # Host A Layer 3
    src_ip = HOST_A_IP
    dst_ip = HOST_B_IP
    ttl = DEFAULT_TTL

    print(f"Host A: Layer 3: Segment received from Transport Layer: SRC_IP={src_ip}, DST_IP={dst_ip}, TTL={ttl}")
    print(f"Host A: Layer 3: Destination IP read: {dst_ip}")
    print("Host A: Layer 3: Routing table lookup performed")
    print(f"Host A: Layer 3: Next-hop IP determined: {R1_IF1_IP}")
    print("Host A: Layer 3: Outgoing interface selected")
    print("Host A: Layer 3: Packet forwarded to Data Link Layer")

    # Host A Layer 2
    print("Host A: Layer 2: Packet received from Network Layer")
    print(f"Host A: Layer 2: Destination MAC lookup for next-hop IP ({R1_IF1_IP}) → {R1_IF1_MAC}")
    print(f"Host A: Layer 2: Frame created: SRC_MAC={HOST_A_MAC}, DST_MAC={R1_IF1_MAC}")
    print("Host A: Layer 2: Frame sent")

    # Router R1 receives frame on Interface 1
    print("Router R1: Layer 2: Frame received on Interface 1")
    print(f"Router R1: Layer 2: Source MAC learned: {HOST_A_MAC} on Interface 1")
    print("Router R1: Layer 2: Packet delivered to Network Layer")

    # Router R1 Layer 3 routing
    old_ttl = ttl
    ttl = ttl - 1

    print(f"Router R1: Layer 3: Packet received from Data Link Layer: SRC_IP={src_ip}, DST_IP={dst_ip}, TTL={old_ttl}")
    print(f"Router R1: Layer 3: Destination IP read: {dst_ip}")
    print(f"Router R1: Layer 3: TTL decremented: {old_ttl} → {ttl}")
    print("Router R1: Layer 3: Routing table lookup performed")
    print(f"Router R1: Layer 3: Next-hop IP determined: {HOST_B_IP}")
    print("Router R1: Layer 3: Outgoing interface selected (Interface 2)")
    print("Router R1: Layer 3: Packet forwarded to Data Link Layer")

    # Router R1 Layer 2 sends to Host B
    print("Router R1: Layer 2: Packet received from Network Layer")
    print(f"Router R1: Layer 2: Destination MAC lookup for next-hop IP ({HOST_B_IP}) → {HOST_B_MAC}")
    print(f"Router R1: Layer 2: Frame created: SRC_MAC={R1_IF2_MAC}, DST_MAC={HOST_B_MAC}")
    print("Router R1: Layer 2: Frame forwarded on Interface 2")

    # Host B receives frame
    print("Host B: Layer 2: Frame received")
    print(f"Host B: Layer 2: Source MAC learned: {R1_IF2_MAC}")
    print("Host B: Layer 2: Packet delivered to Network Layer")

    # Host B Layer 3 local delivery
    print(f"Host B: Layer 3: Packet received from Data Link Layer: SRC_IP={src_ip}, DST_IP={dst_ip}, TTL={ttl}")
    print(f"Host B: Layer 3: Destination IP read: {dst_ip}")
    print("Host B: Layer 3: Packet identified as local delivery")
    print("Host B: Layer 3: Segment delivered to Transport Layer")

    # Host B Layer 4 receives DATA segment
    print("Host B: Layer 4: Segment received from Network Layer")

    if verify_checksum(segment):
        print("Host B: Layer 4: Checksum verified")
        print(f"Host B: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
    else:
        print("Host B: Layer 4: Segment discarded due to checksum error")
        return None

    # Create ACK segment
    ack_segment = create_ack_segment(segment.seq)
    print(f"Host B: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq})")

    return ack_segment