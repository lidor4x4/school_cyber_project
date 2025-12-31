import socket
import threading

TCP_PORT = 12345
VIDEO_PORT = 12346
AUDIO_PORT = 12347

# Store addresses of clients for relaying
video_clients = []
audio_clients = []

# ---------------- TCP AUTH (simplified, just accepts connections) ----------------
def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", TCP_PORT))
    s.listen()
    print("TCP AUTH server running on port", TCP_PORT)

    while True:
        client, addr = s.accept()
        print("TCP connected:", addr)
        # In a real app, you’d handle login/signup here

# ---------------- UDP relay ----------------
def udp_relay(port, client_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"UDP relay on port {port} running")

    while True:
        data, addr = sock.recvfrom(65535)

        if addr not in client_list:
            client_list.append(addr)

        # send to all except sender
        for client in client_list:
            if client != addr:
                sock.sendto(data, client)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_relay, args=(VIDEO_PORT, video_clients), daemon=True).start()
    threading.Thread(target=udp_relay, args=(AUDIO_PORT, audio_clients), daemon=True).start()

    print("SERVER READY")
    while True:
        pass
