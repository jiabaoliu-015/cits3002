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
    
    host_a.send_application_data(HOST_B_IP, message_size)       
main()
