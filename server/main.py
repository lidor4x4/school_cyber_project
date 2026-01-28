import socket
import threading
import select
import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

import utils.utils as utils

TCP_PORT = 12345
VIDEO_PORT = 12346
AUDIO_PORT = 12347

video_clients = []
audio_clients = []
methods = utils.Utils()

def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen()
    server.setblocking(False)

    sockets = [server]

    print("TCP AUTH server running on port", TCP_PORT)

    while True:
        readable, _, _ = select.select(sockets, [], [])

        for sock in readable:
            if sock is server:
                client, addr = server.accept()
                client.setblocking(False)
                sockets.append(client)
                print("TCP connected:", addr)

            else:
                try:
                    data = sock.recv(1024)
                    if not data:
                        sockets.remove(sock)
                        sock.close()
                        continue

                    data = methods.decrypt_message(data)
                    print("Received:", data)

                    if data.startswith("SIGN_UP"):
                        fields = data.split(', ')[1:]  # Remove the 'SIGN_UP,' part and keep the rest
                        email, password, username, user_type = map(str.strip, fields)  # remoe spaces and assign each var 
                        print(f"Received sign up data: {email}, {password}, {username}, {user_type}")
                        response = methods.handle_signup(email, password, username, user_type)
                        print(f"Sign up response: {response}")
                        if response == "200":
                            sock.send(methods.encrypt_message(f"Sign up was successful!!"))
                        else:
                            sock.send(methods.encrypt_message(f"There was an error: {response}"))

                    elif data.startswith("LOGIN"):
                        fields = [x.strip() for x in data.split(',')]

                        email = fields[1]         
                        password = fields[2]    
                        print(f"Received login data: {email}, {password}")
                        response = methods.handle_login(email, password)
                        username_login = methods.get_username(email)
                        if response == "200":
                            sock.send(methods.encrypt_message(f"Login was successful!!, {username_login}"))
                        else:
                            sock.send(methods.encrypt_message(f"There was an error: {response}"))
                    
                    elif data.startswith("VERIFY"):
                        return methods.get_verified_by_username(data.split(",")[-1])


                except Exception as e:
                    print("TCP error:", e)
                    sockets.remove(sock)
                    sock.close()



def udp_relay(port, client_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"UDP relay on port {port} running")

    while True:
        data, addr = sock.recvfrom(65535)

        if addr not in client_list:
            client_list.append(addr)

        for client in client_list:
            if client != addr:
                sock.sendto(data, client)



if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_relay, args=(VIDEO_PORT, video_clients), daemon=True).start()
    threading.Thread(target=udp_relay, args=(AUDIO_PORT, audio_clients), daemon=True).start()

    print("SERVER READY")

    while True:
        pass

