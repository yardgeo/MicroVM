import pika
import subprocess
from config import Config

# RabbitMQ connection parameters
RABBITMQ_HOST = Config.RABBITMQ_HOST
RABBITMQ_QUEUE = Config.RABBITMQ_ESM_QUEUE

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
    input_file = f"{Config.UNIPROT_DIR}/{job_id}/protein.fasta"
    output_dir = f"{Config.ESM_DIR}/{job_id}"

    command = f"python fold.py -i {input_file} -o {output_dir}"
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
