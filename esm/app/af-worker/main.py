import pika
from config import Config
import json
from utils import finish_job

from download_af import download_model

# RabbitMQ connection parameters
RABBITMQ_HOST = Config.RABBITMQ_HOST
RABBITMQ_QUEUE = Config.RABBITMQ_AF_QUEUE

# Establish connection to RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=RABBITMQ_QUEUE)


# Callback function for processing messages
def process_message(ch, method, properties, body):
    message = json.loads(body)
    job_id = message['job_id']
    uniprot_id = message['uniprot_id']
    job_type = message['type']

    # check if job type allowed
    if job_type not in Config.ALLOWED_TYPES:
        return

    # Execute the shell command with the job ID
    output_dir = f"{Config.AF_DIR}"

    download_model(uniprot_id, job_id, output_dir)

    print("AF model was downloaded")

    # mark job as completed
    if job_type == Config.FINISH_TYPE:
        finish_job(job_id, f"{output_dir}/{job_id}/{uniprot_id}.pdb")

    # Acknowledge the message to remove it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Set the consumer to consume messages from the queue
channel.basic_consume(queue=RABBITMQ_QUEUE,
                      on_message_callback=process_message)

print('Consumer is waiting for messages...')

# Start consuming messages
channel.start_consuming()
