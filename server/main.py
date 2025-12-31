import socket
import threading

TCP_PORT = 12345
UDP_CONTROL_PORT = 12348
VIDEO_PORT = 12346
AUDIO_PORT = 12347

clients = []  # List of dicts: {"tcp":..., "control":..., "video":..., "audio":...}

# ---------------- TCP AUTH ----------------
def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", TCP_PORT))
    s.listen()
    print("TCP AUTH server running on port", TCP_PORT)

    while True:
        client, addr = s.accept()
        clients.append({"tcp": client, "control": None, "video": None, "audio": None})
        print("TCP connected:", addr)

# ---------------- UDP CONTROL ----------------
def udp_control():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_CONTROL_PORT))
    print("UDP CONTROL running on port", UDP_CONTROL_PORT)

    while True:
        data, addr = sock.recvfrom(4096)

        # register sender
        for c in clients:
            if c["control"] is None:
                c["control"] = addr
                break

        # relay to others
        for c in clients:
            if c["control"] != addr and c["control"]:
                sock.sendto(data, c["control"])

# ---------------- UDP VIDEO/AUDIO RELAY ----------------
def udp_relay(port, key):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"UDP {key.upper()} relay running on port", port)

    while True:
        data, addr = sock.recvfrom(65535)

        # register sender if not already
        found = False
        for c in clients:
            if c[key] == addr:
                found = True
                break
        if not found:
            for c in clients:
                if c[key] is None:
                    c[key] = addr
                    break

        # relay to all except sender
        for c in clients:
            if c[key] != addr and c[key]:
                sock.sendto(data, c[key])

# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_control, daemon=True).start()
    threading.Thread(target=udp_relay, args=(VIDEO_PORT, "video"), daemon=True).start()
    threading.Thread(target=udp_relay, args=(AUDIO_PORT, "audio"), daemon=True).start()

    print("SERVER READY")
    while True:
        pass
