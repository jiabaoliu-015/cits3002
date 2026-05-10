import sys

from config import HOST_A_IP,HOST_B_IP, HOST_A_MAC, HOST_B_MAC
from devices import Host, Router

    
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


def main():
    message_size = get_message_size()

    host_a = Host("Host A", HOST_A_IP, HOST_A_MAC)
    host_b = Host("Host B", HOST_B_IP, HOST_B_MAC)
    router = Router("Router R1")

    packets = host_a.send_application_data(HOST_B_IP, message_size)

    for packet, next_hop_ip, frame in packets:
        if frame is not None:
            forwarded_frame = router.receive_frame(frame)

            if forwarded_frame is not None:
                ack_segment = host_b.receive_frame(forwarded_frame)

                if ack_segment is not None:
                    ack_packet, ack_next_hop_ip, ack_frame = host_b.send_ack_segment(
                        ack_segment,
                        HOST_A_IP
                    )

                    if ack_frame is not None:
                        returned_ack_frame = router.receive_frame(ack_frame)

                        if returned_ack_frame is not None:
                            host_a.receive_frame(returned_ack_frame)

main()