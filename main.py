import sys

from config import MAX_SEGMENT_DATA_SIZE

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



def main():
    message_size = get_message_size()
    data = "A" * message_size
    blocks = split_data(data)

    print(f"Application message size: {message_size} bytes")
    print(f"Number of transport segments: {len(blocks)}")

    for index, chunk in enumerate(blocks):
        seq = index % 2
        print(f"Segment {index + 1}: data size={len(blocks)}, seq={seq}")

main()
