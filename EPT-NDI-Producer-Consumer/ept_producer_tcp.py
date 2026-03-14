import socket
import random
import time

HOST = "127.0.0.1"
PORT = 8888

def generate_ept_frame():
    return " ".join(str(random.randint(-2048, 2047)) for _ in range(40))

def run_producer():
    interval = 0.001
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(b"EPT\n")
                print("[EPT] Connected to bus server")

                next_time = time.time() + interval
                count = 0

                while True:
                    msg = generate_ept_frame() + "\n"
                    s.sendall(msg.encode())

                    count += 1
                    if count % 1000 == 0:
                        print(f"[EPT] Sent {count} messages")

                    next_time += interval
                    sleep_time = next_time - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        except (ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError) as e:
            print(f"[EPT] Connection lost ({e}), retrying in 1s...")
            time.sleep(1)

if __name__ == "__main__":
    run_producer()
