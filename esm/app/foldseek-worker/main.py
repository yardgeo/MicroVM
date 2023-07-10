import json
import os
import subprocess

import pika

from config import Config
from utils import check_files_existence, finish_job

# RabbitMQ connection parameters
RABBITMQ_HOST = Config.RABBITMQ_HOST
RABBITMQ_QUEUE = Config.RABBITMQ_RESULTS_QUEUE

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

    # pdb files
    esm_pdb = f"{Config.ESM_DIR}/{job_id}/{uniprot_id}.pdb"
    af_pdb = f"{Config.AF_DIR}/{job_id}/{uniprot_id}.pdb"
    pdb = f"{Config.PDB_DIR}/{job_id}/{uniprot_id}.pdb"

    # result files
    result_AF_PDB = f"{Config.RESULTS_DIR}/{job_id}/AF_PDB.html"
    result_ESM_PDB = f"{Config.RESULTS_DIR}/{job_id}/ESM_PDB.html"
    result_ESM_AF = f"{Config.RESULTS_DIR}/{job_id}/ESM_AF.html"

    # wait for files
    # should_continue = check_files_existence(esm_pdb, af_pdb)
    should_continue = check_files_existence(af_pdb, af_pdb)

    if not should_continue:
        print("Files do not exist, exit ...")
        return

    if os.path.isfile(pdb):
        # AF pdb
        command = f"/opt/foldseek/bin/foldseek easy-search {af_pdb}" \
                  f" {pdb} {result_AF_PDB} tmp " \
                  f"--format-mode 3 --alignment-type 1"

        subprocess.call(command, shell=True)
        print(f"Executed command: {command}")

        # # ESM pdb
        # command = f"/opt/foldseek/bin/foldseek easy-search {esm_pdb}" \
        #           f" {pdb} {result_ESM_PDB} tmp " \
        #           f"--format-mode 3 --alignment-type 1"
        #
        # subprocess.call(command, shell=True)
        # print(f"Executed command: {command}")

    # # ESM AF
    # command = f"/opt/foldseek/bin/foldseek easy-search {esm_pdb}" \
    #           f" {af_pdb} {result_ESM_AF} tmp " \
    #           f"--format-mode 3 --alignment-type 1"
    #
    # subprocess.call(command, shell=True)
    # print(f"Executed command: {command}")

    # mark job as completed
    if job_type == Config.FINISH_TYPE:
        finish_job(job_id, result_AF_PDB)#TODO

    # Acknowledge the message to remove it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Set the consumer to consume messages from the queue
channel.basic_consume(queue=RABBITMQ_QUEUE,
                      on_message_callback=process_message)

print('Consumer is waiting for messages...')

# Start consuming messages
channel.start_consuming()
