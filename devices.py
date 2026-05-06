from protocol import split_data ,create_ip_packet ,create_data_segment

class Host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        
    def send_application_data(self, dst_ip, message_size):
        data = "A" * message_size
        blocks = split_data(data)

        print(f"Application message size: {message_size} bytes")
        print(f"Number of transport segments: {len(blocks)}")

        for index, block in enumerate(blocks):
            seq = index % 2

            print(f"=== Segment {index + 1}: data size={len(block)}, seq={seq} ===")
            print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(block)}")

            segment = create_data_segment(block, seq)

            print(f"{self.name}: Layer 4: Checksum computed")
            print(
                f"{self.name}: Layer 4: Segment created by adding transport layer header "
                f"(DATA, seq={segment.seq}) (encapsulation)"
            )
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

    def send_segment_to_network_layer(self, segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        packet = create_ip_packet(self.ip, dst_ip, segment)

        print(
            f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        return packet
    
    
class Router:
    def __init__(self, name):
        self.name = name