import socket
import select
import os
import sys

# Add project root to sys.path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

import utils.utils as utils

methods = utils.Utils()


def handle_client_data(client_socket):
    raw_data = client_socket.recv(4096)
    if not raw_data:
        return False

    data = methods.decrypt_message(raw_data)


    if data.startswith("SIGN_UP"):
        fields = data.split(', ')[1:]
        email, password, username = map(str.strip, fields)  # Strip any surrounding spaces
        print(f"Received sign up data: {email}, {password}, {username}")
        response = methods.handle_signup(email, password, username)
        print(f"Sign up response: {response}")
        if response == "200":
            client_socket.send(methods.encrypt_message(f"Sign up was successful!!"))
        else:
            client_socket.send(methods.encrypt_message(f"There was an error: {response}"))

    elif data.startswith("LOGIN"):
        fields = data.split(", ")[1:]
        email, password = map(str.strip, fields)
        print(f"Received login data: {email}, {password}")
        response = methods.handle_login(email, password)
        if response == "200":
            client_socket.send(methods.encrypt_message(f"Login was successful!!"))
        else:
            client_socket.send(methods.encrypt_message(f"There was an error: {response}"))

    return True  # Return True to keep the client socket open for further interaction


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)  # Max 5 pending connections
    server_socket.setblocking(False)  # Make the server socket non-blocking

    print("Server listening on port 12345...")

    # List of open client sockets
    open_sockets = [server_socket]

    while True:
        # Use select to monitor open sockets for incoming data
        rlist, _, _ = select.select(open_sockets, [], [])
        
        for sock in rlist:
            if sock is server_socket:  # New client connection
                client_socket, addr = server_socket.accept()
                client_socket.setblocking(False)  # Make client socket non-blocking
                open_sockets.append(client_socket)
                print(f"Accepted connection from {addr}")
            else:  # Handle existing client data
                try:
                    if not handle_client_data(sock):
                        # If client socket is closed, remove it
                        print(f"Closing connection from {sock.getpeername()}")
                        open_sockets.remove(sock)
                        sock.close()
                except Exception as e:
                    # Handle any exceptions (e.g., client disconnects unexpectedly)
                    print(f"Error handling client {sock.getpeername()}: {e}")
                    open_sockets.remove(sock)
                    sock.close()

if __name__ == "__main__":
    start_server()
