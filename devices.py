from protocol import (split_data, 
                      create_ip_packet, 
                      create_data_segment ,
                      create_ack_segment,
                      create_ethernet_frame,
                      verify_checksum)

from config import (HOST_A_IP, 
                    HOST_B_IP, 
                    R1_IF1_IP, 
                    R1_IF2_IP, 
                    R1_IF1_MAC, 
                    R1_IF2_MAC,
                    HOST_A_MAC,
                    HOST_B_MAC,
                    ETH_TYPE_IPV4,)

class Host:

    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routing_table = self.create_routing_table()
        self.mac_table = self.create_mac_table()
        self.expected_seq = 0
        self.last_ack_seq = None


    def is_expected_data(self, segment):
        return segment.seq == self.expected_seq


    def update_expected_seq(self):
        self.expected_seq = 1 - self.expected_seq


    def create_ack_for_segment(self, segment):
        return create_ack_segment(segment.seq)


    def is_correct_ack(self, received_ack_seq, expected_seq):
        return received_ack_seq == expected_seq
        
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

            while True:
                # Clear old ACK before sending the current DATA segment.
                # This prevents the sender from accidentally using an ACK from an earlier segment.
                self.last_ack_seq = None

                packet, next_hop_ip, frame = self.send_segment_to_network_layer(segment, dst_ip)

                yield packet, next_hop_ip, frame

                # After yield, main.py has passed the frame to Router R1.
                # If Host A receives an ACK, receive_frame() will update self.last_ack_seq.
                if self.last_ack_seq is None:
                    print(
                        f"{self.name}: Layer 4: No ACK received for DATA seq={seq}. "
                        f"Retransmitting current segment"
                    )
                    continue

                if self.is_correct_ack(self.last_ack_seq, seq):
                    print(f"{self.name}: Layer 4: Correct ACK received for DATA seq={seq}")
                    break

                print(
                    f"{self.name}: Layer 4: Incorrect or duplicate ACK received: "
                    f"expected seq={seq}, received seq={self.last_ack_seq}"
                )
                print(
                f"{self.name}: Layer 4: Retransmitting DATA segment due to incorrect ACK "
                f"(seq={segment.seq})"
                )
        
    
    def receive_frame(self, frame):
        print(f"{self.name}: Layer 2: Frame received")

        if frame.dst_mac != self.mac:
            print(f"{self.name}: Layer 2: Frame dropped because destination MAC does not match host")
            return None

        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer\n")

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
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer\n")

        segment = packet.payload

        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        if verify_checksum(segment):
            print(f"{self.name}: Layer 4: Checksum verified")

            if segment.seg_type == 0:
                if self.is_expected_data(segment):
                    print(
                        f"{self.name}: Layer 4: DATA segment delivered to Application Layer. "
                        f"Data size={len(segment.data)}"
                    )

                    ack_segment = self.create_ack_for_segment(segment)

                    print(
                        f"{self.name}: Layer 4: Segment created by adding transport layer header "
                        f"(ACK, seq={ack_segment.seq})"
                        )

                    self.last_ack_seq = ack_segment.seq

                    self.update_expected_seq()

                    return ack_segment

                else:
                    print(
                        f"{self.name}: Layer 4: Duplicate DATA segment detected. "
                        f"Expected seq={self.expected_seq}, received seq={segment.seq}"
                    )
                    print(f"{self.name}: Layer 4: Duplicate segment not delivered to Application Layer")

                    last_accepted_seq = 1 - self.expected_seq
                    ack_segment = create_ack_segment(last_accepted_seq)

                    self.last_ack_seq = ack_segment.seq

                    print(f"{self.name}: Layer 4: Re-sending ACK with seq={ack_segment.seq}")

                    return ack_segment

            elif segment.seg_type == 1:
                print(f"{self.name}: Layer 4: ACK received: seq={segment.seq}")
                self.last_ack_seq = segment.seq
                return segment

        else:
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")
            
            if self.last_ack_seq is not None:
                ack_segment = create_ack_segment(self.last_ack_seq)

                print(
                    f"{self.name}: Layer 4: Re-sending last ACK with seq={ack_segment.seq}"
                )

                return ack_segment

            print(f"{self.name}: Layer 4: No previous ACK available")
            return None


    def send_segment_to_network_layer(self, segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer\n")

        packet = create_ip_packet(self.ip, dst_ip, segment)

        print(
            f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        next_hop_ip, frame = self.forward_packet_from_network_layer(packet)

        return packet, next_hop_ip, frame
    
    def send_ack_segment(self, ack_segment, dst_ip):
        print(f"{self.name}: Layer 4: Segment sent to Network Layer\n")

        packet = create_ip_packet(self.ip, dst_ip, ack_segment)

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
            f"({next_hop_ip}) → {dst_mac}"
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

        self.interface_mac_table = {
            "Interface 1": R1_IF1_MAC,
            "Interface 2": R1_IF2_MAC
        }

        self.connected_hosts_by_mac = {}
        self.learned_mac_table = {}

    def connect_host(self, host):
        self.connected_hosts_by_mac[host.mac] = host

    def receive_frame(self, frame):
        incoming_interface = self.get_incoming_interface(frame)

        if incoming_interface is None:
            print(f"{self.name}: Layer 2: Frame dropped because destination MAC does not match router")
            return None

        print(f"{self.name}: Layer 2: Frame received on {incoming_interface}")

        original_packet = frame.payload
        original_segment = original_packet.payload

        forwarded_frame = self.forward_frame(frame, incoming_interface)

        if forwarded_frame is None:
            return None

        delivered_host, delivered_result = self.deliver_frame_to_host(forwarded_frame)

        if delivered_host is None:
            return forwarded_frame

        if original_segment.seg_type == 0 and delivered_result is not None:
            ack_segment = delivered_result

            ack_packet, ack_next_hop_ip, ack_frame = delivered_host.send_ack_segment(
                ack_segment,
                original_packet.src_ip
            )

            if ack_frame is not None:
                self.receive_frame(ack_frame)

        return forwarded_frame

    def get_incoming_interface(self, frame):
        if frame.dst_mac in self.interface_table:
            return self.interface_table[frame.dst_mac]

        return None

    def deliver_frame_to_host(self, frame):
        if frame is None:
            return None, None

        host = self.connected_hosts_by_mac.get(frame.dst_mac)

        if host is None:
            print(f"{self.name}: Layer 2: Frame could not be delivered to any connected host")
            return None, None

        result = host.receive_frame(frame)

        return host, result
    
    def learn_source_mac(self, src_mac, incoming_interface):
        self.learned_mac_table[src_mac] = incoming_interface

    def lookup_learned_interface(self, dst_mac):
        if dst_mac in self.learned_mac_table:
            return self.learned_mac_table[dst_mac]

        return None

    def extract_packet_from_frame(self, frame):
        if frame.eth_type != ETH_TYPE_IPV4:
            print(f"{self.name}: Layer 2: Frame dropped because EtherType is not IPv4")
            return None

        if frame.payload is None:
            print(f"{self.name}: Layer 2: Frame dropped because payload is missing")
            return None

        return frame.payload


    def forward_packet_from_network_layer(self, packet):
        print(
            f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )

        dst_ip = packet.dst_ip
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")

        if not self.decrement_ttl(packet):
            return None

        route = self.lookup_route(dst_ip)
        print(f"{self.name}: Layer 3: Routing table lookup performed")

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
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer\n")

        new_frame = self.send_packet_to_data_link_layer(
            packet,
            next_hop_ip,
            outgoing_interface
        )

        return new_frame
    
    def create_routing_table(self):
        return {
            HOST_B_IP: {
                "next_hop_ip": HOST_B_IP,
                "outgoing_interface": "Interface 2",
                "outgoing_mac": R1_IF2_MAC
            },
            HOST_A_IP: {
                "next_hop_ip": HOST_A_IP,
                "outgoing_interface": "Interface 1",
                "outgoing_mac": R1_IF1_MAC
            }
        }

    def create_mac_table(self):
        return {
            HOST_B_IP: HOST_B_MAC,
            HOST_A_IP: HOST_A_MAC
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

        print(f"{self.name}: Layer 3: TTL decremented: {old_ttl} → {packet.ttl}")

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
            f"({next_hop_ip}) → {dst_mac}"
            )   

        if dst_mac is None:
            print(f"{self.name}: Layer 2: Frame not sent because destination MAC was not found")
            return None

        learned_interface = self.lookup_learned_interface(dst_mac)

        if learned_interface is not None:
            print(
            f"{self.name}: Layer 2: Learned MAC table used: "
            f"{dst_mac} is on {learned_interface}"
                )

            outgoing_interface = {
            "name": learned_interface,
            "mac": self.interface_mac_table[learned_interface]
            }

        else:
            print(
            f"{self.name}: Layer 2: Destination MAC not found in learned MAC table; "
            f"using routing-selected interface {outgoing_interface['name']}"
        )

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

        print(f"{self.name}: Layer 2: Frame forwarded on {outgoing_interface['name']}\n")

        return frame


    def forward_frame(self, frame, incoming_interface):
        self.learn_source_mac(frame.src_mac, incoming_interface)
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {incoming_interface}")

        packet = self.extract_packet_from_frame(frame)

        if packet is None:
            return None

        print(f"{self.name}: Layer 2: Packet delivered to Network Layer\n")

        new_frame = self.forward_packet_from_network_layer(packet)

        return new_frame