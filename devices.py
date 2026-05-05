from protocol import create_ip_packet

class Host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac

    def send_segment_to_network_layer(self, segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        packet = create_ip_packet(self.ip, dst_ip, segment)

        print(
            f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        return packet