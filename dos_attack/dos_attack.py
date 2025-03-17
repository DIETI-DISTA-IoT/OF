import shutil
import subprocess
import time

class dos_attack:
    def __init__(self, container_id, attack_type="cpu", duration=60, intensity=80):
        self.container_id = container_id
        self.attack_type = attack_type
        self.duration = duration
        self.intensity = intensity
        
    def launch_cpu_attack(self):
        """Launch a CPU DoS attack on the container."""
        print(f"[*] Launching CPU stress attack with {self.intensity}% load for {self.duration} seconds")
        
        # Verifica se 'docker' è disponibile nell'host (non nel contenitore)
        if shutil.which('docker') is None:
            print("[!] Docker non è disponibile sull'host!")
            return
        
        command_stress_ng = [
            "docker", "exec", self.container_id, 
            "stress-ng", "--cpu", "0", "--cpu-load", str(self.intensity), "--timeout", f"{self.duration}s"
        ]
        
        try:
            process = subprocess.Popen(
                command_stress_ng,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # Attendere fino alla fine dell'attacco o terminazione dell'attacco
            process.communicate()
            print("[+] Attacco CPU completato.")
            
        except Exception as e:
            print(f"[!] Errore durante l'attacco CPU: {e}")

# Esempio di utilizzo
attacco = dos_attack(container_id="nome_o_id_contenitore", attack_type="cpu", duration=60, intensity=80)
attacco.launch_cpu_attack()
