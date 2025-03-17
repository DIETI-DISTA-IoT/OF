import time
import docker
import logging
from OpenFAIR.producer_manager import ProducerManager
from OpenFAIR.consumer_manager import ConsumerManager
import threading
import subprocess


WANDBER_COMMAND = "python wandber.py"
FL_COMMAND = "python federated_learning.py"
class ContainerManager:
    
    def __init__(self, cfg):
        self.logger = logging.getLogger("CONTAINER_MANAGER")
        self.logger.setLevel(cfg.logging_level.upper())
        # Connect to the Docker daemon
        self.client = docker.from_env()
        self.wandber = {
            'container': None,
            'thread': None}
        self.federated_learner = {
            'container': None,
            'thread': None
        }
        self.producers = {}
        self.consumers = {}
        self.attacker = {}
        self.containers_ips = {}
        self.cfg = cfg
        self.vehicle_names = []
        for vehicle in cfg.vehicles:
            vehicle_name = list(vehicle.keys())[0]
            self.vehicle_names.append(vehicle_name) 

        self.attack_in_progress = False
        self.refresh_containers()


    def create_vehicles(self):

        for vehicle_name in self.vehicle_names:
            self.create_producer(vehicle_name)
            self.create_consumer(vehicle_name)
            #self.create_attacker(vehicle_name)

        self.refresh_containers()
        return "Vehicles created!"


    def delete_vehicles(self):
        self.logger.info("Deleting vehicles")
        for producer in self.producers.values():
            producer.stop()
            producer.remove()
        for consumer in self.consumers.values():
            consumer.stop()
            consumer.remove()
        return "Vehicles deleted!"


    def create_producer(self, vehicle_name):
        container_name = f"{vehicle_name}_producer"
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--network", "of_trains_network",
            "open_fair-producer",
            "tail", "-f", "/dev/null"
        ]
        subprocess.run(cmd)
    
    def create_consumer(self, vehicle_name):
        container_name = f"{vehicle_name}_consumer"
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--network", "of_trains_network",
            "open_fair-consumer",
            "tail", "-f", "/dev/null"
        ]
        subprocess.run(cmd)

    def create_attacker(self):
        container_name = "attacker"
        
        # Crea il contenitore dell'attaccante
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--network", "of_trains_network",
            "open_fair-attack",
            "tail", "-f", "/dev/null"
        ]
        subprocess.run(cmd)
        self.refresh_containers()

        if 'attacker' in self.attacker:
            self.logger.info("Attacker container created successfully.")
        else:
            self.logger.error("Failed to create attacker container.")


    def refresh_containers(self):     

        for container in self.client.containers.list():
            container_info = self.client.api.inspect_container(container.id)
            # Extract the IP address of the container from its network settings
            container_img_name = container_info['Config']['Image']
            container_ip = container_info['NetworkSettings']['Networks']['of_trains_network']['IPAddress']
            self.logger.info(f'Found {container.name} container with ip {container_ip}')
            if 'producer' in container_img_name:
                self.producers[container.name] = container
            elif 'consumer' in container.name:
                self.consumers[container.name] = container
            elif 'wandber' in container.name:
                self.wandber['container'] = container
                self.federated_learner['container'] = container
            elif 'attack' in container.name:
                self.attacker[container.name]= container
            self.containers_ips[container.name] = container_ip 
        

        self.producer_manager = ProducerManager(self.cfg, self.producers)
        self.consumer_manager = ConsumerManager(self.cfg, self.consumers)
    
    def produce_all(self):
        return self.producer_manager.start_all_producers()


    def stop_producing_all(self):
        self.producer_manager.stop_all_producers()
        return "All producers stopped!"


    def consume_all(self):
        return self.consumer_manager.start_all_consumers()


    def stop_consuming_all(self):
        self.consumer_manager.stop_all_consumers()
        return "All consumers stopped!"


    def stop_wandb(self):
        self.wandber['container']
        try:
            # Try to find and kill the process
            pid_result = self.wandber['container'].exec_run(f"pgrep -f '{WANDBER_COMMAND}'")
            pid = pid_result[1].decode().strip()
            
            if pid:
                self.wandber['container'].exec_run(f"kill -SIGINT {pid}")
                self.logger.info(f"Stopping wandber...")
                return "Stopping wandber..."
            else:
                self.logger.info(f"No running process found for wandber")
                return "No running process found for wandber"
        except Exception as e:
            self.logger.error(f"Error stopping wandber: {e}")
            return "Error stopping wandber"


    def start_wandb(self, cfg):

        start_command = f"python wandber.py " + \
            f" --logging_level={cfg.logging_level} " + \
            f" --project_name={cfg.wandb.project_name} " + \
            f" --run_name={cfg.wandb.run_name} " + \
            f" --kafka_broker_url={cfg.wandb.kafka_broker_url} " + \
            f" --kafka_consumer_group_id={cfg.wandb.kafka_consumer_group_id} " + \
            f" --kafka_auto_offset_reset={cfg.wandb.kafka_auto_offset_reset} " + \
            f" --kafka_topic_update_interval_secs={cfg.kafka_topic_update_interval_secs}"
                
        if cfg.wandb.online:
            start_command += " --online"
        
        def run_wandber(self):
            return_tuple = self.wandber['container'].exec_run(
                 start_command,
                 tty=True,
                 stream=True,
                 stdin=True)
            for line in return_tuple[1]:
                print(line.decode().strip())
        
        thread = threading.Thread(target=run_wandber, args=(self,))
        thread.start()
        return "Wandber consumer started!"


    def start_federated_learning(self, cfg):

        start_command = FL_COMMAND + \
            f" --logging_level={cfg.logging_level} " + \
            f" --project_name={cfg.wandb.project_name} " + \
            f" --run_name={cfg.wandb.run_name} " + \
            f" --kafka_broker_url={cfg.wandb.kafka_broker_url} " + \
            f" --kafka_consumer_group_id={cfg.wandb.kafka_consumer_group_id} " + \
            f" --kafka_auto_offset_reset={cfg.wandb.kafka_auto_offset_reset} " + \
            f" --kafka_topic_update_interval_secs={cfg.kafka_topic_update_interval_secs}" +\
            f" --aggregation_strategy={cfg.federated_learning.aggregation_strategy}" +\
            f" --initialization_strategy={cfg.federated_learning.initialization_strategy}" +\
            f" --aggregation_interval_secs={cfg.federated_learning.aggregation_interval_secs}" +\
            f" --weights_buffer_size={cfg.federated_learning.weights_buffer_size}"
                
        if cfg.wandb.online:
            start_command += " --online"
        
        def run_federated_learning(self):
            return_tuple = self.wandber['container'].exec_run(
                 start_command,
                 tty=True,
                 stream=True,
                 stdin=True)
            for line in return_tuple[1]:
                print(line.decode().strip())
        
        thread = threading.Thread(target=run_federated_learning, args=(self,))
        thread.start()
        return "Federated learning started!"
    

    def stop_federated_learning(self):
        try:
            # Try to find and kill the process
            pid_result = self.federated_learner['container'].exec_run(f"pgrep -f '{FL_COMMAND}'")
            pid = pid_result[1].decode().strip()
            
            if pid:
                self.federated_learner['container'].exec_run(f"kill -SIGINT {pid}")
                m = "Stopping FL..."
                self.logger.info(m)
                return m
            else:
                m = "No running process found for federated learning"
                self.logger.info(m)
                return m
        except Exception as e:
            m = f"Error stopping federated learning: {e}"
            self.logger.error(m)
            return m 
    

    def start_attack(self, attack_name, vehicle_name, vehicle_config):
        """Avvia un attacco all'interno del contenitore."""
        if self.attack_in_progress:
            self.logger.warning("An attack is already in progress. Waiting...")
            while self.attack_in_progress:
                time.sleep(1)

        self.attack_in_progress = True  

        # Verifica se il container dell'attaccante esiste
        if 'attacker' not in self.attacker:
            self.logger.info("Attacker container not found. Creating container.")
            self.create_attacker()  
            self.refresh_containers()  

        # Assicurati che il contenitore dell'attaccante sia stato creato correttamente
        attacker_container = self.attacker.get('attacker', None)

        if attacker_container is None:
            self.logger.error("No attacker container available after creation.")
            self.attack_in_progress = False
            return "No attacker container available."

        # Ottieni l'IP del veicolo da attaccare (Flood Attack)
        target_ip = self.containers_ips.get(f"{vehicle_name}_producer") or self.containers_ips.get(f"{vehicle_name}_consumer")
        if not target_ip:
            self.logger.error(f"Could not find IP for vehicle {vehicle_name}.")
            self.attack_in_progress = False
            return f"Could not find IP for vehicle {vehicle_name}."

        self.logger.info(f"Target IP for flood attack: {target_ip}")

        # Comando per eseguire l'attacco flood direttamente nel contenitore
        flood_command = f'python3 -c "import sys; sys.path.append(\'/attack\'); import attacker; a = attacker.Attacker(\'{target_ip}\'); a.start_attack()"'
        
        # Comando per eseguire l'attacco DoS direttamente nel contenitore (su bob_producer)
        dos_target_ip = self.containers_ips.get(f"{vehicle_name}_producer")  # Usare lo stesso veicolo come target
        if not dos_target_ip:
            self.logger.error(f"Could not find IP for {vehicle_name}_producer.")
            self.attack_in_progress = False
            return f"Could not find IP for {vehicle_name}_producer."

        self.logger.info(f"Target IP for DoS attack: {dos_target_ip}")
            
        dos_command = f'python3 -c "import sys; sys.path.append(\'/dos_attack\'); import dos_attack; a = dos_attack.dos_attack(\'{dos_target_ip}\'); a.launch_cpu_attack()"'


        def run_attack_in_container(container, command):
            try:
                # Avvia il comando nel container
                result = container.exec_run(command, tty=True, stream=True, stdin=True)
                for line in result[1]:
                    self.logger.info(line.decode().strip())  # Log dell'output dell'attacco
            except Exception as e:
                self.logger.error(f"Error during attack: {e}")
    
        # Ottieni il contenitore bob_producer
        bob_container = self.client.containers.get('bob_producer')

        # Esegui l'attacco flood e l'attacco DoS nei rispettivi thread
        flood_thread = threading.Thread(target=run_attack_in_container, args=(attacker_container, flood_command))
        dos_thread = threading.Thread(target=run_attack_in_container, args=(bob_container, dos_command))

        flood_thread.start()
        dos_thread.start()

        flood_thread.join()
        dos_thread.join()

        self.logger.info(f"Attack {attack_name} completed for vehicle {vehicle_name} and DoS attack on bob_producer.")
        self.attack_in_progress = False  # Sblocca il programma dopo l'attacco
        return f"Attack {attack_name} completed for vehicle {vehicle_name} and DoS attack on bob_producer!"