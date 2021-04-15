import socket
import select

HEADER_LENGTH = 64

class Server:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False) # Non-blocking manner
        print("Please Declare the Host and Port for the server: ")

        host = input("Host (IP) for server: ")

        PORT = input("Port: ")
        while not PORT.isdigit(): # check if it is an integer
            print(f"<port> : ERR_NOSUCHSERVER (Port Should be an Integer!) ")
            PORT = input("Port: ")
        PORT = int(PORT) # convert to integer
        port = PORT


        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.read_size = 512 #512 characters

        self.clients = {}
        self.sockets_list = [self.server_socket]
        print(f'Listening for connections on {host}:{port}...')

        self.nicknameList = []

    def receive_message(self, client_socket):
        try:

            message_header = client_socket.recv(HEADER_LENGTH)

            if not len(message_header):
                return False

            # Convert header to int value
            message_length = int(message_header.decode('utf-8').strip())

            # Return an object of message header and message data
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:

            # client closed connection violently with interrupt or has lost connection
            return False


    def run(self):
        print("Server running...")

        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    user = self.receive_message(client_socket)

                    # client has disconnected before he sent his name
                    if user is False:
                        continue

                    # Client has joined channel
                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user
                    print('JOIN #global, Accepted new connection from {}:{}, nickname: {}'.format(*client_address, user['data'].decode('utf-8')))

                else:
                    message = self.receive_message(notified_socket)

                    # disconnect
                    if message is False:
                        print('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    user = self.clients[notified_socket]

                    print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

                    for client_socket in self.clients:
                        if client_socket != notified_socket:
                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]


if __name__ == "__main__":
    server = Server()
    server.run()
