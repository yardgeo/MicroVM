import pika
import subprocess

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'task_queue'

# Establish connection to RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=RABBITMQ_QUEUE)


# Callback function for processing messages
def process_message(ch, method, properties, body):
    job_id = body.decode()

    # Execute the shell command with the job ID
    command = f"python fold.py {job_id}"
    subprocess.call(command, shell=True)

    print(f"Executed command: {command}")

    # Acknowledge the message to remove it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Set the consumer to consume messages from the queue
channel.basic_consume(queue=RABBITMQ_QUEUE,
                      on_message_callback=process_message)

print('Consumer is waiting for messages...')

# Start consuming messages
channel.start_consuming()
