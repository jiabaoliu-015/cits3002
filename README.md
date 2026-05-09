# cits3002

## Team Member
1. jiabao liu student number: 23954936
2. shuo li student number: 24038633

## code detial
### 1.main.py

    The main.py is the entry point of the network simulator. It is used to reading the message size from the command line tester input. Create the network devices. Start the main mission is transmission from Host A to Host B through router. 

  

这里是ai生成的，可以用来后续美化使用(`main.py` is the entry point of the simulator. It reads the application message size from the command-line argument, validates the input, creates the network devices, and starts the transmission process.

The `get_message_size()` function checks that exactly one command-line argument is provided. It then converts the argument into an integer and ensures that the message size is positive. If the input is missing, not an integer, or not positive, the program prints an error message and exits.

The `main()` function creates Host A, Host B, and Router R1 using the fixed IP and MAC addresses defined in `config.py`. After the devices are created, Host A sends application data to Host B by calling `host_a.send_application_data(HOST_B_IP, message_size)`. This begins the encapsulation process, where application data is divided into transport segments, wrapped into IP packets, and then encapsulated into Ethernet-like frames.

The generated frames are then passed to Router R1. For each frame returned by Host A, `main.py` checks whether the frame was successfully created. If the frame is valid, it is delivered to the router by calling `router.receive_frame(frame)`.

Overall, `main.py` controls the high-level execution flow of the simulator. It does not implement the detailed protocol logic itself. Instead, it coordinates the classes and helper functions defined in `devices.py`, `protocol.py`, and `config.py`.)

1. def get_message_size():
    This function is responsible for checking whether the user has entered the correct parameters. And ensure the input data is number and positive. All invalid input will print the error log.

2. def main():
    The program first calls get_message_size() to get the size of the message input by the user.

    Then the program then creates three network devices:

    host_a represents the sender, Host A; 
    host_b represents the receiver, Host B;
    router represents the intermediate router, Router R1.

    The Host class is defined in devices.py. Each Host, when created, stores its own name, IP address, and MAC address, and creates a routing table and a MAC address table.

    ｜｜packets = host_a.send_application_data(HOST_B_IP, message_size)｜｜
    This is where the entire simulation begins.

    In devices.py, `send_application_data()` performs the following:

   （ Creates application data of the specified size;

    If the data exceeds the maximum segment size, it segments the data;

    Creates a Layer 4 segment for each block;

    Creates a Layer 3 IP packet;

    Creates a Layer 2 Ethernet-like frame;

    Returns the generated packet, next hop IP, and frame.

    The segment size is controlled by `MAX_SEGMENT_DATA_SIZE = 500`.）

    Send the frame to Router R1
    code：
    for packet, next_hop_ip, frame in packets:
        if frame is not None:
            router.receive_frame(frame)
    
    Because Host A may generate multiple transport segments, packets are a list.

    The router checks if the destination MAC address of this frame belongs to itself. If the destination MAC address is the interface MAC address of router R1, then the router will accept the frame; otherwise, it will discard it.

    the last line is the program entry. main()

### devices.py

### protocol.py 

### config.py

我们不会上交git hub库。
但是readme.md也会被提交上去，作为代码的解释。
所以我们可以在这里做代码编程的逻辑。
然后进行总结
