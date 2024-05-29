
# Mettre a jour la liste des paquets 
sudo apt-get update 
# Installer snap
sudo apt-get install snap 
# Depuis snap installer lxd 
sudo snap install lxd 
# Configuration initial de lxd
lxd init 
# Activation du service snapd
sudo systemctl enable snapd
# Lancer le service snapd
sudo systemctl start snapd
# Verification de l'etat du service 
sudo systemctl status snapd


# Ajouter votre utilisateur dans le groupe lxd pour utiliser les commande lxc 

# Telecharger un image linux ubuntu pour les containers 
lxc image copy images:ubuntu/amd64 local: --alias ubuntu
# Verifier le telechargement d l'image 
lxc image list 
# Creation des containers avec l'image telechatger  
lxc launch ubuntu WebAppClient 
