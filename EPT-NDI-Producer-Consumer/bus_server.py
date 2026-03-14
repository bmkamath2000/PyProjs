import socket
import threading
import json
import pika
import datetime

HOST = "0.0.0.0"
PORT = 8888
RABBIT_HOST = "172.29.166.4"  # your RabbitMQ host in WSL

DEVICE_CONFIGS = {
    "EPT": "ept_config.json",
    "NDI": "ndi_config.json"
}

def load_config(device_type):
    """Load JSON config for given device type."""
    with open(DEVICE_CONFIGS[device_type], "r") as f:
        return json.load(f)

def handle_client(conn, addr, channel):
    try:
        f = conn.makefile("r")  # line-buffered reader
        handshake = f.readline().strip()
        if handshake not in DEVICE_CONFIGS:
            print(f"Unknown device tried to connect: {handshake}")
            conn.close()
            return

        config = load_config(handshake)
        queue = config["queue"]
        log_file = config["log_file"]

        print(f"[{handshake}] Connected from {addr}, queue={queue}, log={log_file}")

        while True:
            line = f.readline()
            if not line:
                break

            msg = line.strip()
            ts = datetime.datetime.utcnow().isoformat()
            final_msg = f"{ts} {msg}"

            # log to file
            with open(log_file, "a") as logf:
                logf.write(final_msg + "\n")

            # publish to RabbitMQ
            channel.basic_publish(exchange="", routing_key=queue, body=final_msg.encode())

    except Exception as e:
        print(f"[{addr}] Error: {e}")
    finally:
        conn.close()
        print(f"Connection closed: {addr}")

def main():
    # connect to RabbitMQ once
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()

    # ensure queues exist
    for cfg in DEVICE_CONFIGS.values():
        with open(cfg, "r") as f:
            q = json.load(f)["queue"]
            channel.queue_declare(queue=q)

    # start TCP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Bus server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr, channel), daemon=True).start()

if __name__ == "__main__":
    main()
