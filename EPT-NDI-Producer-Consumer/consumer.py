import pika

RABBITMQ_HOST = "localhost"   # if running consumer in Docker and RabbitMQ also in Docker, we'll change this later

def callback_ept(ch, method, properties, body):
    print(f"[EPTQueue] {body.decode()}")

def callback_ndi(ch, method, properties, body):
    print(f"[NDIQueue] {body.decode()}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare queues (in case producer hasn't created them yet)
    channel.queue_declare(queue="EPTQueue", durable=True)
    channel.queue_declare(queue="NDIQueue", durable=True)

    # Set up consumers
    channel.basic_consume(queue="EPTQueue", on_message_callback=callback_ept, auto_ack=True)
    channel.basic_consume(queue="NDIQueue", on_message_callback=callback_ndi, auto_ack=True)

    print(" [*] Waiting for messages. Press CTRL+C to exit.")
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Consumer stopped.")
