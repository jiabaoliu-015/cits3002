from protocol import split_data, create_ip_packet, create_data_segment
from config import HOST_A_IP, HOST_B_IP, R1_IF1_IP, R1_IF2_IP

class Host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routing_table = self.create_routing_table()

    def create_routing_table(self):
        if self.ip == HOST_A_IP:
            return {
                HOST_B_IP: R1_IF1_IP
            }

        if self.ip == HOST_B_IP:
            return {
                HOST_A_IP: R1_IF2_IP
            }

        return {}

    def send_application_data(self, dst_ip, message_size):
        data = "A" * message_size
        blocks = split_data(data)

        print(f"Application message size: {message_size} bytes")
        print(f"Number of transport segments: {len(blocks)}")

        packets = []

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

            packet, next_hop_ip = self.send_segment_to_network_layer(segment, dst_ip)
            packets.append(packet, next_hop_ip)

        return packets


    def send_segment_to_network_layer(self, segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        packet = create_ip_packet(self.ip, dst_ip, segment)

        print(
            f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        next_hop_ip = self.forward_packet_from_network_layer(packet)

        return packet, next_hop_ip

    def forward_packet_from_network_layer(self, packet):

        dst_ip = packet.dst_ip
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        next_hop_ip = self.lookup_next_hop_ip(packet.dst_ip)

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")


        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        return next_hop_ip

    def lookup_next_hop_ip(self, dst_ip):
        if dst_ip in self.routing_table:
            return self.routing_table[dst_ip]

        return dst_ip
class Router:
    def __init__(self, name):
        self.name = name