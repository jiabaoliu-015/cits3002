import sys
import random
import string
from config import MAX_SEGMENT_DATA_SIZE
from protocol import create_data_segment

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
    print(f"Application message size: {message_size} bytes")
    print(f"Number of transport segments: {len(blocks)}")

    for index, block in enumerate(blocks):
        seq = index % 2
        print(f"=== Segment {index + 1}: data size={len(block)}, seq={seq} ===")
        print(f"Host A: Layer 4: Data received from Application Layer. Data size={len(block)}")

        segment = create_data_segment(block, seq)

        if segment:
            print("Host A: Layer 4: Checksum computed")
            print(f"Debug: segment data size = {len(segment.data)}")
            print(f"Debug: segment length = {segment.length}")
            print(f"Debug: segment checksum = {segment.checksum}")
            print(f"Debug: segment type = {segment.seg_type}")
            print(f"Debug: segment seq = {segment.seq}")
        
main()
