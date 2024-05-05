# SHELL TROJAN CLIENT 
    Ce module est la partie client du programme Shell Reverse Trojan, une fois installer ce module offre un acces console au serveur, il est fournis des utilitaire de script qui facilite son installation et son utilisation 

## Table des matieres 
    1. Installation 
    2. Utilisation 
    3. Contribution 
    4. License 


### 1. Installation 
    
    Idealement le client et le serveur sont conçu pour s'exedcuter sur des machines differentes, mais il peuvent egalement s'executer en local sur une meme machine a condition qu'il s'execute sur des environement differents.
    
   

#### Script bash 
    ```console

        sudo apt-get update 
        sudo apt-get upgrade 
        sudo apt-get install python3 pip virtualenv git
        mkdir shellTrojanProject 
        cd shellTrojanProject
        git clone https://github.com/AudreyDenis/SHELL_REVERSE_TROJAN
        cd SHELL_REVERSE_TROJAN 
        git pull clientTrojan 
        virtualenv trojanenv -p /usr/bin/python3
        sudo trojanenv/bin/activate 
        sudo pip install -r requirement.txt 
        sudo python3 clientTrojan.py 
    
    ```


### Utilisation 

    Configurer l'adresse du client sur la mchine serveur soit sur le fichier de configuration client, mais l'ideal serait que le client soit capable de retrouver automatiquement l'adresse du serveur sans besoin de configuration. 

    Une fois le client lancer vous devrier voir un motif de skull (crane) sur la console.

    !!! ATTENTION !!! :
    Toute responsabilité lié a l'usage (l'egal ou non ) de ce programme revient a son utilisateur, le createur n'est nullement responable de toutes actes des utilisateur commis avec ou grace a ce programme.  
            


### Contribution 
    Pour aider a contribuer a ce projet vous pouvez envoyer un mail a l'adresse < audreyndinga0@gmail.com >. 

    Plusieur fonctionnalité et possibilité sont a explorer pour ce logiciel et donc tout aide serait la bienvenue. 

    Ou encore creer un fork du projet conformement au condition et restriction de la licence 

### License 
    
    Le present projet est distribuer avec une License MIT. 

    Pour plus de details, consulter le fichier < License.md > 