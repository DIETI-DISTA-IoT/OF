import docker
import json
import http.server
import socketserver
import json
from omegaconf import DictConfig, OmegaConf 
import hydra
import threading
import importlib.util
import sys

from OpenFAIR import ProducerManager, ConsumerManager



def run_command_in_container(container, command):
    # Run the command in the container shell to obtain the PID
    exec_result = container.exec_run(f"sh -c '{command} & echo $!'")
    pid = exec_result.output.decode("utf-8").strip()
    return pid

def refresh_containers():
    global containers_dict, containers_ips, producers, consumers
    global producer_manager, consumer_manager
    # Connect to the Docker daemon
    client = docker.from_env()

    for container in client.containers.list():
        container_info = client.api.inspect_container(container.id)
        # Extract the IP address of the container from its network settings
        container_info_str = container_info['Config']['Hostname']
        container_img_name = container_info_str.split('(')[0]
        container_ip = container_info['NetworkSettings']['Networks']['open_fair_trains_network']['IPAddress']
        print(f'{container_img_name} is {container.name} with ip {container_ip}')
        if 'producer' in container_img_name:
            producers[container_img_name] = container
        elif 'consumer' in container_img_name:
            consumers[container_img_name] = container
        containers_dict[container_img_name] = container
        containers_ips[container_img_name] = container_ip 
    print('\n\n\n')

    producer_manager = ProducerManager(producers)
    consumer_manager = ConsumerManager(consumers)
            

def print_output(container, command, thread_name):
    # Execute the command in the container and stream the output
    return_tuple = container.exec_run(command, stream=True, tty=True, stdin=True)
    for line in return_tuple[1]:
        print(thread_name+": "+line.decode().strip())  # Print the output line by line


def produce_all():
    # Start all producers
    for producer_name, vehicle_name in zip(producers.keys(), vehicle_names):
        producer_manager.start_producer(producer_name, producers[producer_name], vehicle_name)
    return "All producers started!"


def stop_producing_all():
    producer_manager.stop_all_producers()
    return "All producers stopped!"

def consume_all():
    # Start all consumers
    for consumer_name, vehicle_name in zip(consumers.keys(), vehicle_names):
        consumer_manager.start_producer(consumer_name, consumers[consumer_name], vehicle_name)
    return "All consumers started!"


def stop_all_consumers():
    consumer_manager.stop_all_consumers()
    return "All consumers stopped!"


class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/refresh_containers':
                refresh_containers()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'message': 'Containers refreshed!'}
                self.wfile.write(json.dumps(response).encode())
            elif self.path == '/produce_all':
                response_str = produce_all()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')  
                self.end_headers()
                self.wfile.write(response_str.encode())
            elif self.path == '/consume_all':
                response_str = consume_all()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')  
                self.end_headers()
                self.wfile.write(response_str.encode()) 
            elif self.path == '/stop_producing_all':
                stop_producing_all()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
            elif self.path == '/stop_consuming_all':
                stop_all_consumers()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
            else:
                super().do_GET()


# Create a TCPServer instance with SO_REUSEADDR option
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True  # This allows the server to reuse the address


@hydra.main(config_path="config", config_name="default", version_base="1.2")
def main(cfg: DictConfig) -> None:
    global containers_dict, containers_ips, consumers, producers, vehicle_names
    print("\n________________________________________________________________\n\n"+\
          "               OPEN FAIR Container Manager \n" +\
          "________________________________________________________________\n"+\
          "\n"+\
          "IMPORTANT:  - Parameters are read from the open_fair.yaml file at project's root dir. \n" +\
          "            - Re-launch this script each time you change container status (through node restart). \n\n\n")
    
    containers_dict = {}
    consumers = {}
    producers = {}
    containers_ips = {}
    vehicle_names = cfg.vehicle_names
    refresh_containers() 
    
    with ReusableTCPServer(("", cfg.container_manager_port), MyRequestHandler) as httpd:
        print(f"Serving at port {cfg.container_manager_port}")
        httpd.serve_forever()
    

if __name__ == "__main__":
    main()

    

    



