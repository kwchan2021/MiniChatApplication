#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.


# added package
import socket
import select
import errno
import asyncio
import logging
import patterns

# VIEW.LOG WILL BE CREATED
logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

#REQUIREMENTS FOR USERNAME, NICKNAME, MESSAGE
HEADER_LENGTH = 64 # 512 Charcters = 64 bytes
MSGLENG = 510
NICKLENG = 9

class IRCClient(patterns.Subscriber):

    def __init__(self):
        super().__init__()

        # [HOST]
        print("Please register your connection with the server (Declare Host and Port) : ")
        self.host = input("Host (IP) : ")
        # [HOST]

        # [PORT]
        PORT = input("Port: ")
        while not PORT.isdigit(): # check if it is an integer
            print(f"<port> : ERR_NOSUCHSERVER (Port Should be an Integer!) ")
            PORT = input("Port: ")
        PORT = int(PORT)
        self.port = PORT
        # [PORT]

        # [USERNAME]
        USERNAME = input("Username: ")
        while not len(USERNAME):
            print("431 ERR_NONICKNAMEGIVEN:\"No nickname given\" (Nickname is not defined)")
            USERNAME = input("Username: ")
        self.username = USERNAME
        # [USERNAME]

        # [NICKNAME]
        NICKNAME = input("Nickname: ")
        while not len(NICKNAME):
            print(f"431 <nick> :Nickname is not defined")
            NICKNAME = input("Username: ")
        while len(NICKNAME) > 9:
            print(f"432 <nick> :Erroneus nickname (Length of nickname cannot be larger than 9)")
            NICKNAME = input("Username: ")
        self.nickname = NICKNAME
        # [NICKNAME]

        # to create a socket but do not connect
        self.connect()

        self._run = True

    def set_view(self, view):
        self.view = view

    def update(self):

        while True:
            # Will need to modify this
            msg = input(f'{self.nickname} > ')

            # Send message
            # [Bad cases]
            if msg.lower().startswith('/quit'):
                print(f'QUIT : {self.nickname} quitted the channel')  # According to rfc1459#section-4.1.6
                # Command that leads to the closure of the process
                raise KeyboardInterrupt
            elif not isinstance(msg, str): #check if the msg is a string
                print(f"Update argument needs to be a string")
            elif not len(msg): # check if the message is empty won't trigger this
                # Empty string
                print(' [Refresh] ') #Update argument cannot be an empty string -
            elif len(msg) >= (MSGLENG - len(self.nickname)): # Length of message have to be within 510 characters
                print(f"Message limit: 510 characters")
            # [Bad cases]

            # [Good case]
            else:
                msg = msg.encode("utf-8")
                message_header = f"{len(msg):<{HEADER_LENGTH}}".encode("utf-8")
                self.client_socket.send(message_header + msg)
            # [Good case]
            # Send message

            try:
                while True:
                    # To receive message from other client
                    username_header = self.client_socket.recv(HEADER_LENGTH)

                    # Convert header to int value
                    username_length = int(username_header.decode('utf-8').strip())

                    # Receive and decode username
                    username = self.client_socket.recv(username_length).decode('utf-8')

                    # same for msg
                    message_header = self.client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_length).decode('utf-8')

                    # print msg
                    print(f'{username} > {message}')
                    # To receive message from other client

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    continue

        # log msg
        logger.info(f"IRCClient.update -> msg: {msg}")

        # Quit condition
        self.add_msg(msg)

    def process_input(self, msg):
        # Will need to modify this
        self.add_msg(msg) # all msg to log? TODO
        if msg.lower().startswith('/quit'): # to quit channel using /quit
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def connect(self):
        # to create a socket but do not connect
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # After nickname and username are both defined, connect to given and port
        self.client_socket.connect((self.host, self.port))

        # Set connection to non-blocking state,
        # so .recv() call won;t block, just return some exception we'll handle
        self.client_socket.setblocking(False)

        # encode username to bytes, then count number of bytes
        # and prepare header of fixed size, that we encode to bytes as well
        nick = self.nickname.encode('utf-8')
        nick_header = f"{len(nick):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(nick_header + nick)

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    async def run(self):
        self.update()


    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass



def main(args):

    client = IRCClient()  # no argument coz input() is used within constructor

    async def inner_run():
        await asyncio.gather(
            client.run(),
            return_exceptions=True,
        )
    try:
        asyncio.run(inner_run())
    except KeyboardInterrupt as e:
        logger.debug(f"Signifies end of process")
    client.close()


if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(args)
