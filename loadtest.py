import socket
import json
import threading
import time

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 7002
NUM_BOTS = 50

def simulate_client_bot(bot_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(3.0)
        client_socket.connect((TARGET_HOST, TARGET_PORT))
        
        nrp_payload = {"command": "login", "payload": f"50252410{bot_id}"}
        client_socket.sendall((json.dumps(nrp_payload) + "\n").encode())
        
        response = client_socket.recv(1024).decode()
        
        otp_payload = {"command": "verify_otp", "payload": "123456"}
        client_socket.sendall((json.dumps(otp_payload) + "\n").encode())
        
        for i in range(5):  
            msg_payload = {
                "command": "broadcast",
                "payload": f"Bot {bot_id} - msg {i}"
            }
            client_socket.sendall((json.dumps(msg_payload) + "\n").encode())
            print(f"[Bot {bot_id}] Berhasil kirim pesan ke-{i}")
            time.sleep(2.0)
            
        client_socket.close()
        print(f"Bot {bot_id} SELESAI!")
    except socket.timeout:
        print(f"Bot {bot_id} Error: Timeout (Server kelamaan ngerespon)")
    except Exception as e:
        print(f"Bot {bot_id} Error: {e}")

threads = []
for i in range(NUM_BOTS):
    t = threading.Thread(target=simulate_client_bot, args=(i,))
    threads.append(t)
    t.start()
    time.sleep(0.05)

for t in threads:
    t.join()

print("Load testing selesai.")