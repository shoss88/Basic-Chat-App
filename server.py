
import sys
import getopt
import socket
import util


class Server:
    '''
    This is the main Server Class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        # List of currently connected clients
        self.clients = {}

    def send_packet(self, response, client_addr):
        '''
        Code for sending packet containing the response to a given client address
        '''

        reply_pkt = util.make_packet(msg=response)
        self.sock.sendto(reply_pkt.encode(), client_addr)

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it.

        '''

        # Loop indefinitely until not necessary
        while True:
            # Let the server get a request from the client and store its message and address
            msg, client_addr = self.sock.recvfrom(util.CHUNK_SIZE)
            # Parse the packet from the client to extract the message from it.
            parsed_pkt = util.parse_packet(msg.decode())
            # Grab only the data from the resulting tuple. This data is the actual message content.
            data = parsed_pkt[2]
            # Grab the message type from the data
            msg_contents = util.parse_message(data)
            msg_type = msg_contents[0]

            # Match the message type with any of the types and respond accordingly
            if msg_type == "join":
                client_name = msg_contents[2]
                if len(self.clients) == util.MAX_NUM_CLIENTS:
                    # Send err_server_full message to the client if there is no more space.
                    err_response = util.make_message("err_server_full", 2)
                    self.send_packet(err_response, client_addr)
                elif client_name in self.clients.values():
                    # Send err_username_unavailable message to the client if the name was already taken.
                    err_response = util.make_message("err_username_unavailable", 2)
                    self.send_packet(err_response, client_addr)
                else:
                    # Else, add the client to the list of joined clients.
                    self.clients[client_addr] = client_name
                    print("join: " + client_name + "\n", file=sys.stdout)

            elif msg_type == "request_users_list":
                # Create the list of users to send (alphabetical order)
                users_list = str(len(self.clients))
                for username in sorted(self.clients.values()):
                    users_list += "," + username
                # Reply to the client with a response_users_list message.
                response = util.make_message("response_users_list", 3, users_list)
                self.send_packet(response, client_addr)
                print("request_users_list: " + self.clients[client_addr] + "\n", file=sys.stdout)

            elif msg_type == "send_message":
                receiver_list = msg_contents[2]
                message_to_send = msg_contents[3]
                print("msg: " + self.clients[client_addr] + "\n", file=sys.stdout)
                # Parse receiver_list by splitting by commas, and excluding the number of users included.
                receiver_list = receiver_list.split(",")[1:]
                # Check the parsed receiver list for existing clients and send a forward_message response to each client
                curr_clients_list = self.clients.values()
                # Keep track of clients already receiving a message.
                received_clients = []
                for client in receiver_list:
                    if client in curr_clients_list:
                        if client not in received_clients:
                            # Combine the original format of a "list of usernames" with the given message.
                            # The "list of usernames" here would just be the sender's username.
                            forward_msg = "1," + self.clients[client_addr] + " " + message_to_send
                            # Find the client_addr of the receiver client.
                            receiver_client_addr = client_addr
                            for addr in self.clients:
                                if self.clients[addr] == client:
                                    receiver_client_addr = addr
                                    break
                            response = util.make_message("forward_message", 4, forward_msg)
                            self.send_packet(response, receiver_client_addr)
                            received_clients.append(client)
                    # If a client in the receiver list doesn't exist, print the appropriate message.
                    else:
                        print("msg: " + self.clients[client_addr] + " to non-existent user " + client + "\n",
                              file=sys.stdout)

            elif msg_type == "disconnect":
                client_name = msg_contents[2]
                # Remove the client from the clients list and print the appropriate message.
                del self.clients[client_addr]
                print("disconnected: " + client_name + "\n")

            else:
                # Send an err_unknown_message back to the client because there were no recognizable message types sent.
                err_response = util.make_message("err_unknown_message", 2)
                self.send_packet(err_response, client_addr)
                print("disconnected: " + self.clients[client_addr] + " sent unknown command\n")


if __name__ == "__main__":
    def helper():
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
