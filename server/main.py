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
    clients_by_name = {}

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
                        fields = data.split(', ')[1:]
                        email, password, username, user_type, dr_specialty = map(str.strip, fields)
                        print(f"Received sign up data: {email}, {password}, {username}, {user_type}, {dr_specialty}")
                        response = methods.handle_signup(email, password, username, user_type, dr_specialty)
                        print(f"Sign up response: {response}")
                        if response == "200":
                            clients_by_name[username] = sock
                            print(clients_by_name)
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
                            clients_by_name[username_login] = sock
                            sock.send(methods.encrypt_message(f"Login was successful!!, {username_login}"))
                        else:
                            sock.send(methods.encrypt_message(f"There was an error: {response}"))

                    elif data.startswith("GET_USER_ROLE_BY_EMAIL"):
                        email = data.split(",")[-1]
                        user_role = methods.get_role_by_email(email)
                        sock.send(methods.encrypt_message(user_role))

                    elif data.startswith("VERIFY"):
                        username_verify = data.split(",")[-1]
                        verify_status = str(methods.get_verified_by_username(username_verify))
                        sock.send(methods.encrypt_message(verify_status))

                    elif data.startswith("GET_UNVERIFIED"):
                        users = methods.get_unverified_users()
                        sock.send(methods.encrypt_message(','.join(users)))

                    elif data.startswith("GET_QUEUE"):
                        fields = [x.strip() for x in data.split(',')]
                        dr_username = fields[1]
                        dr_queue = methods.get_dr_queue_by_username(dr_username)
                        sock.send(methods.encrypt_message(dr_queue))

                    elif data.startswith("GET_VERIFIED_DR_USERS"):
                        dr_users = ",".join(methods.get_verified_dr_users())
                        sock.send(methods.encrypt_message(dr_users))

                    elif data.startswith("GET_DR_QUEUE_BY_USERNAME"):
                        dr_username_queue = data.split(",")[-1]
                        users_in_queue = methods.get_dr_queue_by_username(dr_username_queue)
                        sock.send(methods.encrypt_message(users_in_queue))

                    elif data.startswith("GET_DR_SPECIALTY_BY_USERNAME"):
                        dr_username_specialty = data.split(",")[-1]
                        dr_specialty = methods.get_dr_specialty_by_username(dr_username_specialty)
                        sock.send(methods.encrypt_message(dr_specialty))

                    elif data.startswith("ADD_TO_DR_QUEUE"):
                        user_username = data.split(",")[-1]
                        add_queue_dr_username = data.split(",")[-2]
                        print("server username", user_username)
                        print("Server Dr username", add_queue_dr_username)
                        ret = methods.add_to_dr_queue(add_queue_dr_username, user_username)
                        print("rettttttttttttttttt", ret)
                        sock.send(methods.encrypt_message(ret))

                    elif data.startswith("ACCEPT_PATIENT"):
                        patient_username = data.split(",")[-1]
                        patient_sock = clients_by_name[patient_username]

                        patient_ip = patient_sock.getpeername()[0]
                        doctor_ip = sock.getpeername()[0]

                        print("doctor ip", doctor_ip)
                        print("patient ip", patient_ip)

                        # Tell patient they were accepted and give them the doctor's IP
                        patient_sock.send(methods.encrypt_message(f"ACCEPTED,{doctor_ip}"))

                        # Reply to doctor with the patient's IP
                        sock.send(methods.encrypt_message(patient_ip))

                    elif data.startswith("KICK_PATIENT"):
                        patient_username = data.split(",")[-1]
                        if patient_username in clients_by_name:
                            clients_by_name[patient_username].send(methods.encrypt_message("KICKED"))
                        sock.send(methods.encrypt_message("OK"))

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

        # Prepend sender's IP into the packet so receivers can filter by it
        sender_ip = addr[0].encode()
        length = len(sender_ip).to_bytes(1, 'big')
        packet = length + sender_ip + data

        for client in client_list:
            if client != addr:
                sock.sendto(packet, client)


if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_relay, args=(VIDEO_PORT, video_clients), daemon=True).start()
    threading.Thread(target=udp_relay, args=(AUDIO_PORT, audio_clients), daemon=True).start()

    print("SERVER READY")

    while True:
        pass