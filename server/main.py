import socket
import threading

TCP_PORT = 12345
UDP_CONTROL_PORT = 12348
VIDEO_PORT = 12346
AUDIO_PORT = 12347

clients = []  # dicts: {tcp, control, video, audio}

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", TCP_PORT))
    s.listen()
    print("TCP AUTH server running")

    while True:
        client, addr = s.accept()
        clients.append({"tcp": client, "control": None, "video": None, "audio": None})
        print("TCP connected:", addr)

def udp_control_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_CONTROL_PORT))
    print("UDP CONTROL listening")

    while True:
        data, addr = sock.recvfrom(4096)
        for c in clients:
            if c["control"] is None:
                c["control"] = addr
                break
        for c in clients:
            if c["control"] != addr and c["control"]:
                sock.sendto(data, c["control"])

def udp_relay(port, key):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"UDP {key.upper()} relay running")

    while True:
        data, addr = sock.recvfrom(65535)
        for c in clients:
            if c[key] is None:
                c[key] = addr
                break
        for c in clients:
            if c[key] != addr and c[key]:
                sock.sendto(data, c[key])

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_control_server, daemon=True).start()
    threading.Thread(target=udp_relay, args=(VIDEO_PORT, "video"), daemon=True).start()
    threading.Thread(target=udp_relay, args=(AUDIO_PORT, "audio"), daemon=True).start()
    print("SERVER READY")
    while True:
        pass
