from protocol import split_data, create_ip_packet, create_data_segment , create_ethernet_frame
from config import (HOST_A_IP, 
                    HOST_B_IP, 
                    R1_IF1_IP, 
                    R1_IF2_IP, 
                    R1_IF1_MAC, 
                    R1_IF2_MAC)

class Host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routing_table = self.create_routing_table()
        self.mac_table = self.create_mac_table()
        
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
    def create_mac_table(self):
        if self.ip == HOST_A_IP:
            return {
                R1_IF1_IP: R1_IF1_MAC
            }

        if self.ip == HOST_B_IP:
            return {
                R1_IF2_IP: R1_IF2_MAC
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

            packet, next_hop_ip, frame = self.send_segment_to_network_layer(segment, dst_ip)
            packets.append((packet, next_hop_ip, frame))

        return packets


    def send_segment_to_network_layer(self, segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        packet = create_ip_packet(self.ip, dst_ip, segment)

        print(
            f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        next_hop_ip, frame = self.forward_packet_from_network_layer(packet)

        return packet, next_hop_ip, frame

    def forward_packet_from_network_layer(self, packet):
        dst_ip = packet.dst_ip

        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        next_hop_ip = self.lookup_next_hop_ip(dst_ip)

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")

        outgoing_interface = self.select_outgoing_interface(next_hop_ip)

        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        frame = self.send_packet_to_data_link_layer(packet, next_hop_ip, outgoing_interface)

        return next_hop_ip, frame

    def lookup_next_hop_ip(self, dst_ip):
        if dst_ip in self.routing_table:
            return self.routing_table[dst_ip]

        return dst_ip
    
    def select_outgoing_interface(self, next_hop_ip):
        return {
            "ip": self.ip,
            "mac": self.mac
        }
    def send_packet_to_data_link_layer(self, packet, next_hop_ip, outgoing_interface):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        dst_mac = self.lookup_mac_address(next_hop_ip)

        print(
            f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP "
            f"({next_hop_ip}) > {dst_mac}"
        )

        frame = create_ethernet_frame(
            src_mac=outgoing_interface["mac"],
            dst_mac=dst_mac,
            packet=packet
        )

        print(
            f"{self.name}: Layer 2: Frame created: "
            f"SRC_MAC={frame.src_mac}, DST_MAC={frame.dst_mac}"
        )
        print(f"{self.name}: Layer 2: Frame sent")

        return frame

    def lookup_mac_address(self, next_hop_ip):
        if next_hop_ip in self.mac_table:
            return self.mac_table[next_hop_ip]

        return None
class Router:
    def __init__(self, name):
        self.name = name