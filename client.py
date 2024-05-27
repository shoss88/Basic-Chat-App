import sys
import getopt
import socket
import random
from threading import Thread
import os
import util


'''
In the start() function, read user-input and act accordingly.
receive_handler() function is running another thread 
'''


class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username

    def send_packet(self, request):
        '''
        Code for sending packet containing the response to a given server address
        '''

        req_pkt = util.make_packet(msg=request)
        self.sock.sendto(req_pkt.encode(), (self.server_addr, self.server_port))

    def start(self):
        '''
        Main Loop is here
        Starts by sending the server a JOIN message.
        Use make_message() and make_util() functions from util.py to make the first join packet
        Waits for userinput and then process it
        '''

        # Create a join message and send it to the server.
        request = util.make_message("join", 1, self.name)
        self.send_packet(request)
        # Loop indefinitely until not necessary
        while True:
            # Get input from the user
            user_input = input()
            # Parse the input and get the input type.
            input_contents = util.parse_input(user_input)
            input_type = input_contents[0]

            # Match the input type with any of the types and request accordingly
            if input_type == "msg":
                # Send the message to the server, including the list of usernames.
                full_msg = input_contents[1] + " " + input_contents[2]
                request = util.make_message("send_message", 4, full_msg)
                self.send_packet(request)

            elif input_type == "list":
                # Send a request_users_list request to the server
                request = util.make_message("request_users_list", 2)
                self.send_packet(request)

            elif input_type == "help":
                # Print all the possible user-inputs and their format input
                print("All inputs and their format:\n" +
                      "msg <number_of_users> <username1> <username2> … <message>\n" +
                      "list\n" +
                      "help\n" +
                      "quit\n", file=sys.stdout)

            elif input_type == "quit":
                # Send a disconnect request to the server
                request = util.make_message("disconnect", 1, self.name)
                self.send_packet(request)
                print("quitting\n", file=sys.stdout)
                # Break from the loop and close the socket.
                break

            else:
                print("incorrect userinput format\n", file=sys.stdout)

        self.sock.close()

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''

        # Loop indefinitely until server informs of error.
        while True:
            # Let the client get a response from the server and store its message and address
            msg, server_addr = self.sock.recvfrom(util.CHUNK_SIZE)
            # Parse the packet from the server to extract the message from it.
            parsed_pkt = util.parse_packet(msg.decode())
            # Grab only the data from the resulting tuple. This data is the actual message content.
            data = parsed_pkt[2]
            # Grab the message type from the data
            msg_contents = util.parse_message(data)
            msg_type = msg_contents[0]

            # Match the message type with any of the types and handle accordingly
            if msg_type == "err_server_full":
                # Break from the loop to allow client to close.
                print("disconnected: server full\n", file=sys.stdout)
                break

            elif msg_type == "err_username_unavailable":
                # Break from the loop to allow client to close.
                print("disconnected: username not available\n", file=sys.stdout)
                break

            elif msg_type == "err_unknown_message":
                # Break from the loop to allow client to close.
                print("disconnected: server received an unknown command\n", file=sys.stdout)
                break

            elif msg_type == "response_users_list":
                # Get the username list and parse it, ignoring number of users.
                users_list = msg_contents[2].split(",")[1:]
                # Convert it to a string and print the list
                users_str = " ".join(users_list)
                print("list: " + users_str + "\n", file=sys.stdout)

            elif msg_type == "forward_message":
                # Get the username of the original client sending the message, and their message
                sender_name = msg_contents[2].split(",")[1:][0]
                sender_msg = msg_contents[3]
                print("msg: " + sender_name + ": " + sender_msg + "\n", file=sys.stdout)

        self.sock.close()


if __name__ == "__main__":
    def helper():
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
