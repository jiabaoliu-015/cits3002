from protocol import (split_data, 
                      create_ip_packet, 
                      create_data_segment ,
                      create_ethernet_frame,
                      verify_checksum)

from config import (HOST_A_IP, 
                    HOST_B_IP, 
                    R1_IF1_IP, 
                    R1_IF2_IP, 
                    R1_IF1_MAC, 
                    R1_IF2_MAC,
                    HOST_B_MAC,
                    ETH_TYPE_IPV4,)

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
    
    def receive_frame(self, frame):
        print(f"{self.name}: Layer 2: Frame received")

        if frame.dst_mac != self.mac:
            print(f"{self.name}: Layer 2: Frame dropped because destination MAC does not match host")
            return None

        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        packet = frame.payload

        print(
            f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        if packet.dst_ip != self.ip:
            print(f"{self.name}: Layer 3: Packet dropped because destination IP does not match host")
            return None

        print(f"{self.name}: Layer 3: Packet identified as local delivery")
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")

        segment = packet.payload

        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        if verify_checksum(segment):
            print(f"{self.name}: Layer 4: Checksum verified")

            if segment.seg_type == 0:
                print(
                    f"{self.name}: Layer 4: DATA segment delivered to Application Layer. "
                    f"Data size={len(segment.data)}"
                )

            elif segment.seg_type == 1:
                print(f"{self.name}: Layer 4: ACK received: seq={segment.seq}")

        else:
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")

        return segment


    def send_segment_to_network_layer(self, segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer\n")

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
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer\n")

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
            f"({next_hop_ip}) -> {dst_mac}"
        )

        if dst_mac is None:
            print(f"{self.name}: Layer 2: Frame not sent because destination MAC was not found")
            return None

        frame = create_ethernet_frame(
            src_mac=outgoing_interface["mac"],
            dst_mac=dst_mac,
            packet=packet
        )

        if not self.validate_outgoing_frame(frame, outgoing_interface["mac"], dst_mac):
            print(f"{self.name}: Layer 2: Frame not sent because frame validation failed")
            return None

        print(
            f"{self.name}: Layer 2: Frame created: "
            f"SRC_MAC={frame.src_mac}, DST_MAC={frame.dst_mac}"
        )
        print(f"{self.name}: Layer 2: Frame sent\n")

        return frame

    def lookup_mac_address(self, next_hop_ip):
        if next_hop_ip in self.mac_table:
            return self.mac_table[next_hop_ip]

        return None
    
    def validate_outgoing_frame(self, frame, expected_src_mac, expected_dst_mac):
        if frame.src_mac != expected_src_mac:
            return False

        if frame.dst_mac != expected_dst_mac:
            return False

        if frame.eth_type != ETH_TYPE_IPV4:
            return False

        if frame.payload is None:
            return False

        return True
    

class Router:
    def __init__(self, name):
        self.name = name
        self.interface_table = {
            R1_IF1_MAC: "Interface 1",
            R1_IF2_MAC: "Interface 2"
        }

    def receive_frame(self, frame):
        incoming_interface = self.get_incoming_interface(frame)

        if incoming_interface is None:
            print(f"{self.name}: Layer 2: Frame dropped because destination MAC does not match router")
            return None

        print(f"{self.name}: Layer 2: Frame received on {incoming_interface}")

        return self.forward_frame(frame, incoming_interface)

    def get_incoming_interface(self, frame):
        if frame.dst_mac in self.interface_table:
            return self.interface_table[frame.dst_mac]

        return None
    
    def create_routing_table(self):
        return {
            HOST_B_IP: {
                "next_hop_ip": HOST_B_IP,
                "outgoing_interface": "Interface 2",
                "outgoing_mac": R1_IF2_MAC
            }
        }


    def create_mac_table(self):
        return {
            HOST_B_IP: HOST_B_MAC
        }


    def lookup_route(self, dst_ip):
        routing_table = self.create_routing_table()

        if dst_ip in routing_table:
            return routing_table[dst_ip]

        return None


    def lookup_mac_address(self, next_hop_ip):
        mac_table = self.create_mac_table()

        if next_hop_ip in mac_table:
            return mac_table[next_hop_ip]

        return None


    def select_outgoing_interface(self, route):
        return {
            "name": route["outgoing_interface"],
            "mac": route["outgoing_mac"]
        }


    def decrement_ttl(self, packet):
        old_ttl = packet.ttl
        packet.ttl -= 1

        print(f"{self.name}: Layer 3: TTL decremented: {old_ttl} -> {packet.ttl}")

        if packet.ttl <= 0:
            print(f"{self.name}: Layer 3: Packet dropped because TTL expired")
            return False

        return True


    def validate_outgoing_frame(self, frame, expected_src_mac, expected_dst_mac):
        if frame.src_mac != expected_src_mac:
            return False

        if frame.dst_mac != expected_dst_mac:
            return False

        if frame.eth_type != ETH_TYPE_IPV4:
            return False

        if frame.payload is None:
            return False

        return True


    def send_packet_to_data_link_layer(self, packet, next_hop_ip, outgoing_interface):
        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        dst_mac = self.lookup_mac_address(next_hop_ip)

        print(
            f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP "
            f"({next_hop_ip}) -> {dst_mac}"
        )

        if dst_mac is None:
            print(f"{self.name}: Layer 2: Frame not sent because destination MAC was not found")
            return None

        frame = create_ethernet_frame(
            src_mac=outgoing_interface["mac"],
            dst_mac=dst_mac,
            packet=packet
        )

        if not self.validate_outgoing_frame(frame, outgoing_interface["mac"], dst_mac):
            print(f"{self.name}: Layer 2: Frame not sent because frame validation failed")
            return None

        print(
            f"{self.name}: Layer 2: Frame created: "
            f"SRC_MAC={frame.src_mac}, DST_MAC={frame.dst_mac}"
        )

        print(f"{self.name}: Layer 2: Frame forwarded on {outgoing_interface['name']}")

        return frame


    def forward_frame(self, frame, incoming_interface):
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {incoming_interface}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        packet = frame.payload

        print(
            f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        dst_ip = packet.dst_ip
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")

        if not self.decrement_ttl(packet):
            return None

        print(f"{self.name}: Layer 3: Routing table lookup performed")

        route = self.lookup_route(dst_ip)

        if route is None:
            print(f"{self.name}: Layer 3: No route found. Packet dropped")
            return None

        next_hop_ip = route["next_hop_ip"]
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")

        outgoing_interface = self.select_outgoing_interface(route)

        if outgoing_interface is None:
            print(f"{self.name}: Layer 3: No outgoing interface found. Packet dropped")
            return None

        print(f"{self.name}: Layer 3: Outgoing interface selected ({outgoing_interface['name']})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        new_frame = self.send_packet_to_data_link_layer(
            packet,
            next_hop_ip,
            outgoing_interface
        )

        return new_frame