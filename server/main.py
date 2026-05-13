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
ips_to_remove = []

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

                        try:
                            user_ip = sock.getpeername()[0]
                            ips_to_remove.append(user_ip)
                            print(f"[DISCONNECT] {user_ip}")
                        except:
                            pass

                        sock.close()
                        continue

                    data = methods.decrypt_message(data)
                    print("Received:", data)

                    if data.startswith("SIGN_UP"):
                        fields = data.split(', ')[1:]
                        email, password, username, user_type, dr_specialty = map(str.strip, fields)

                        response = methods.handle_signup(email, password, username, user_type, dr_specialty)

                        if response == "200":
                            clients_by_name[username] = sock
                            sock.send(methods.encrypt_message("Sign up was successful!!"))
                        else:
                            sock.send(methods.encrypt_message(f"There was an error: {response}"))

                    elif data.startswith("LOGIN"):
                        fields = [x.strip() for x in data.split(',')]
                        email = fields[1]
                        password = fields[2]

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

                    elif data.startswith("CHANGE_TO_OFFLINE"):
                        user_to_change = data.split(',')[1].strip()
                        methods.set_user_online_status(user_to_change, 0)
                        sock.send(methods.encrypt_message("User status changed successfully!!"))

                    elif data.startswith("SET_USER_ONLINE"):
                        user_to_change = data.split(',')[1].strip()
                        methods.set_user_online_status(user_to_change, 1)
                        sock.send(methods.encrypt_message("User status changed successfully!!"))


                    elif data.startswith("GET_QUEUE"):
                        dr_username = data.split(',')[1].strip()
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
                        add_queue_dr_username = data.split(",")[-2]
                        user_username = data.split(",")[-1]

                        ret = methods.add_to_dr_queue(add_queue_dr_username, user_username)
                        sock.send(methods.encrypt_message(ret))

                    elif data.startswith("ACCEPT_PATIENT"):
                        patient_username = data.split(",")[-1]

                        if patient_username in clients_by_name:
                            patient_sock = clients_by_name[patient_username]

                            video_clients.clear()
                            audio_clients.clear()
                            print("[RESET] Cleared UDP client lists")

                            patient_ip = patient_sock.getpeername()[0]
                            doctor_ip = sock.getpeername()[0]

                            patient_sock.send(methods.encrypt_message(f"ACCEPTED,{doctor_ip}"))
                            sock.send(methods.encrypt_message(patient_ip))

                    elif data.startswith("KICK_PATIENT"):
                        patient_username = data.split(",")[-1]

                        if patient_username in clients_by_name:
                            clients_by_name[patient_username].send(methods.encrypt_message("KICKED"))

                        sock.send(methods.encrypt_message("OK"))

                except Exception as e:
                    print("TCP error:", e)

                    if sock in sockets:
                        sockets.remove(sock)

                    try:
                        user_ip = sock.getpeername()[0]
                        ips_to_remove.append(user_ip)
                    except:
                        pass

                    sock.close()


def udp_relay(port, client_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"UDP relay on port {port} running")

    while True:
        for ip in ips_to_remove[:]:
            client_list[:] = [c for c in client_list if c[0] != ip]
            ips_to_remove.remove(ip)
            print(f"[CLEAN] Removed {ip} from port {port}")

        data, addr = sock.recvfrom(65535)

        client_list[:] = [c for c in client_list if c[0] != addr[0]]

        client_list.append(addr)
        print(f"[ADD] {addr} to port {port}")

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