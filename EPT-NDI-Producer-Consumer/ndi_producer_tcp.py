import socket
import random
import time

HOST = "127.0.0.1"  # Bus server host
PORT = 8888


def generate_quaternion():
    """Generate a random normalized quaternion (w, x, y, z)."""
    q = [random.uniform(-1, 1) for _ in range(4)]
    norm = sum(v * v for v in q) ** 0.5
    return [v / norm for v in q]


def generate_position():
    """Generate a random (x, y, z) position."""
    return [round(random.uniform(-100, 100), 2) for _ in range(3)]


def generate_ndi_frame():
    snr = round(random.uniform(10, 40), 2)
    quaternion = generate_quaternion()
    position = generate_position()
    return f"SNR:{snr} Q:{quaternion} P:{position}"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Send handshake
        s.sendall(b"NDI\n")

        interval = 1.0 / 30.0  # ~33 ms (≈30 Hz)
        next_time = time.time() + interval
        count = 0

        while True:
            msg = generate_ndi_frame() + "\n"
            s.sendall(msg.encode())

            count += 1
            if count % 10 == 0:
                print(f"[NDI] Sent {count} messages")

            # keep accurate 30 Hz interval
            next_time += interval
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)


if __name__ == "__main__":
    main()
