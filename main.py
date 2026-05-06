import sys
import random
import string
from config import MAX_SEGMENT_DATA_SIZE, HOST_A_IP, HOST_B_IP,HOST_A_MAC
from protocol import create_data_segment, create_ip_packet
from devices import Host
from dataclasses import asdict, is_dataclass

DEBUG = True


def debug_print(title, obj):
    if not DEBUG:
        return

    print(f"\n[DEBUG] {title}")

    if obj is None:
        print("[DEBUG] value = None")
        return

    if is_dataclass(obj):
        obj_dict = asdict(obj)
        for key, value in obj_dict.items():
            if key == "data" and isinstance(value, str):
                print(f"[DEBUG] {key}_size = {len(value)}")
                print(f"[DEBUG] {key}_value = {value}")
            elif key == "checksum" and isinstance(value, int):
                print(f"[DEBUG] {key} = {value} / 0x{value:04X}")
            else:
                print(f"[DEBUG] {key} = {value}")
        return

    if hasattr(obj, "__dict__"):
        for key, value in vars(obj).items():
            print(f"[DEBUG] {key} = {value}")
        return

    print(f"[DEBUG] value = {obj}")
    
def get_message_size():
    if len(sys.argv) != 2:
        print("program input error. \nUsage: python3 main.py <message_size>")
        sys.exit(1)
    try:
        message_size = int(sys.argv[1])
    except ValueError:
        print("Error: message_size must be an integer")
        sys.exit(1)

    if message_size <= 0:
        print("Error: message_size must be positive")
        sys.exit(1)

    return message_size


def split_data(data):
    blocks = []

    for i in range(0, len(data), MAX_SEGMENT_DATA_SIZE):
        block = data[i:i + MAX_SEGMENT_DATA_SIZE]
        blocks.append(block)

    return blocks

def generate_random_data(size):
    chars = string.ascii_letters + string.digits
    data = ""

    for _ in range(size):
        data += random.choice(chars)

    return data

def main():
    message_size = get_message_size()
    data = generate_random_data(message_size)
    blocks = split_data(data)
    host_a = Host("Host A", HOST_A_IP, HOST_A_MAC)

    print(f"Application message size: {message_size} bytes")
    print(f"Number of transport segments: {len(blocks)}")

    debug_print("Full application data", data)
    debug_print("Host A object", host_a)
    debug_print("Data blocks", blocks)

    for index, block in enumerate(blocks):
        seq = index % 2

        print(f"=== Segment {index + 1}: data size={len(block)}, seq={seq} ===")
        print(f"Host A: Layer 4: Data received from Application Layer. Data size={len(block)}")

        debug_print(f"Segment {index + 1} raw block data", block)
        debug_print(f"Segment {index + 1} sequence number", seq)

        segment = create_data_segment(block, seq)

        debug_print(f"Segment {index + 1} object after create_data_segment()", segment)

        if segment is not None:
            print("Host A: Layer 4: Checksum computed")
            print(f"Host A: Layer 4: Segment created by adding transport layer header (DATA, seq={seq}) (encapsulation)")

            packet = host_a.send_segment_to_network_layer(segment, HOST_B_IP)

            debug_print(f"Packet object after send_segment_to_network_layer()", packet)

        else:
            print("some wrong happen during the create data segment or checksum")
        

        
main()
