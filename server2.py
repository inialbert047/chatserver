import socket
from threading import Thread
import signal
import sys
import os

# Konfigurasi server
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5006
separator_token = "<SEP>"
client_sockets = set()

# File untuk menyimpan PID
pid_file = '/tmp/my_server.pid'

def signal_handler(sig, frame):
    """Menangani sinyal untuk mematikan server dengan benar."""
    print("\n[!] Mematikan server...")
    for cs in client_sockets:
        cs.close()
    s.close()
    if os.path.isfile(pid_file):
        os.remove(pid_file)
    sys.exit(0)

def listen_for_client(cs):
    """Mendengarkan dan memproses pesan dari klien."""
    while True:
        try:
            msg = cs.recv(1024).decode()
            if not msg:
                break
        except Exception as e:
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
            break
        else:
            msg = msg.replace(separator_token, ": ")
            for client_socket in client_sockets:
                if client_socket != cs:
                    client_socket.send(msg.encode())
    cs.close()
    client_sockets.remove(cs)

# Setup signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Cek dan hapus PID file jika ada
if os.path.isfile(pid_file):
    with open(pid_file, 'r') as f:
        old_pid = int(f.read())
        try:
            os.kill(old_pid, 0)
        except OSError:
            # Proses tidak berjalan, lanjutkan
            pass
        else:
            print(f"[!] Server sudah berjalan dengan PID {old_pid}.")
            sys.exit(1)

# Simpan PID server baru
with open(pid_file, 'w') as f:
    f.write(str(os.getpid()))

# Setup socket server
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind((SERVER_HOST, SERVER_PORT))
except OSError as e:
    if e.errno == 98:
        print(f"[!] Port {SERVER_PORT} sedang digunakan. Coba lagi nanti.")
    else:
        raise e
    sys.exit(1)
s.listen(5)
print(f"[*] Server terbuka di {SERVER_HOST}:{SERVER_PORT}")

while True:
    try:
        client_socket, client_address = s.accept()
        print(f"[+] {client_address} terhubung")
        client_sockets.add(client_socket)
        t = Thread(target=listen_for_client, args=(client_socket,))
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"[!] Error: {e}")
        break
