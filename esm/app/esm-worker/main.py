import time

import pika
import subprocess
from config import Config
import json
from utils import finish_job

from esm.data import read_fasta

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
    message = json.loads(body)
    job_id = message['job_id']
    uniprot_id = message['uniprot_id']
    job_type = message['type']

    # check if job type allowed
    if job_type not in Config.ALLOWED_TYPES:
        return

    # Execute the shell command with the job ID
    input_file = f"{Config.UNIPROT_DIR}/{job_id}/{uniprot_id}.fasta"
    output_dir = f"{Config.ESM_DIR}/{job_id}"

    # command = f"python fold.py -i {input_file} -o {output_dir}"

    # API command
    time.sleep(5)
    output = f"{output_dir}/{uniprot_id}.pdb"
    _, sequence = read_fasta(input_file)
    command = f" curl -X POST -o {output} --data {sequence}" \
              f" https://api.esmatlas.com/foldSequence/v1/pdb/"

    subprocess.call(command, shell=True)

    print(f"Executed command: {command}")

    # mark job as completed
    if job_type == Config.FINISH_TYPE:
        finish_job(job_id, f"{output_dir}/{uniprot_id}.pdb")  # TODO

    # Acknowledge the message to remove it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Set the consumer to consume messages from the queue
channel.basic_consume(queue=RABBITMQ_QUEUE,
                      on_message_callback=process_message)

print('Consumer is waiting for messages...')

# Start consuming messages
channel.start_consuming()
