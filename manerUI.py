from os import system
from time import sleep
from os import path

def chargement(message = 'Chargement en cours ...',tour = 2,sprite=['| ','/ ','- ',"\ "]):#-------------------------------------------------------------Juste pour le kiff :) !...
    for i in range(0,tour):
        for j in sprite:
            print(message,j)
            sleep(0.20)
            system('cls')
    print(f" {message.split(' ')[0]} terminé avec succes :) !...")
    sleep(1.10)
    system('cls')
    
class Option: #-------------------------------------------------------------Chaque element du menu est une option, une option peut etre un menu ou une fonction 
    
    num_opt = 0 
    def __init__(self,libelle='Option',exe=object):
        Option.num_opt += 1
        self.num = Option.num_opt
        if libelle == 'Option' :
            self.libelle = f"{libelle} {self.num}"
        else:
            self.libelle = libelle
        self.__exe = exe
        self.pagination = f'> {self.libelle} '
        
    def format_option(self,num=0):
        print(f"\t|  {num} - )  {self.libelle}")
    
    def run(self,page=''):
        system('cls')
        print('\n',page,self.pagination,'\n','_-'*int((len(self.pagination+page)/2)),'\n')
        self.__exe()
        sleep(2)
        print('')
    
class Menu(Option):
    
    def __init__(self,titre='Menu principale',options=list):
        Option.__init__(self,libelle=titre,exe=object())
        self.pagination = f'/  {self.libelle} '
        self.options = {k+1:v for k,v in enumerate(options)}
        
    def affiche_menu(self,page=''):
        system('cls')
        print("\n\n\n")
        print("=".center(120,'='))
        print("[ Ecrit par >++> Designer_#@rt_242 (~_~) ]".center(100,"$"))
        print('\n\t\t ',page,self.pagination,
              '\n\t\t','_-'*int((len(self.pagination+page)/2)),
              '\n'
              )
        for num,opt in self.options.items():
            opt.format_option(num)
        if len(page) == 0:
            print("\t|  0 - )  Quitter \n")
        else:
            print("\t|  0 - )  Retour  \n")
        
    
    def __choisit_option(self,page=''):
        try :
            choix = input("\t Entrer votre choix > ").strip()
            if len(choix) == 0:
                print('\n\t Aucune option selectionnée :( ...' )
                sleep(1.20)
                chargement(message='Redirection vers le menu ...',tour=1)
                system('cls')
                return
            choix = int(choix)
        except KeyboardInterrupt:
            try : 
                confirme_sortit = input("\n\n\t Tentative d'interruption d'urgence, veuillez confirmer [yes/no] > ").lower()
            except KeyboardInterrupt as e : 
                chargement(message="Retour au menu...")
                pass
            else:
                if confirme_sortit in ['yes','y','oui']:
                    system('cls')
                    chargement(message="Sortit d'urgence en cours ...")
                    system('cls')
                    return 0
                else:
                    print("\n Tentative de sortit annuler ! ")
                    sleep(1)
                    chargement(message='Redirection vers le menu ')
                    system('cls')
                    return  
        except ValueError:
            print('\n Choix incorrect !')
            sleep(1.20)
            chargement(message='Redirection vers le menu ...')
            system('cls')
            return
        except Exception :
            print('\n Une erreur inconnue est survenue :( !!!!!!')
            sleep(1.20)
            chargement(message='Redirection vers le menu ...')
            sleep(0.30)
            system('cls')
            return
        else: #--------------------------------------------------------------------------------Si aucun platage ne survient dans la saisit du choix ! Alors 
            if choix == 0:
                chargement(message='Sortit du menu :) !...') #-------------------------------------Si l'utilisateur quitte le menu ! 
                system('cls')
                return 0 
            elif choix not in self.options.keys(): #---------------------------------------------Si le numero d'option n'est pas present dans la liste ! 
                print('\n Option inexisitante ! veuillez selectioner une option presente dans le menu !')
                sleep(1.20)
                chargement(message='Redirection vers le menu ...')
                sleep(0.30)
                system('cls')
            else :
                for num,opt in self.options.items():#------------------------------------------l'utilisateur entre un numero d'option valide alors on execute l'option correspondante 
                    if choix == num :
                        opt.run(page+" "+self.pagination)
    
    def run(self,page='',choix=0):
        chargement(tour=3)
        while 1 : 
            self.affiche_menu(page)
            if self.__choisit_option(page) == 0:
                break           
        
def HelloWord():
    print(" Bonjour tout le monde :) !... ")
    
def GoodBye():
    print(" Aurevoir tout le monde :) !... ")

def Moonlight():
    print(" Au clair de la lune :) !... ")
    
option1 = Option("Hello",HelloWord)
option2 = Option('Bye',GoodBye)
option3 = Option(exe=Moonlight)

sub_menu1 = Menu(
                titre='sub_sub 1',
                options=[option1,option2]
                )

menu1 = Menu(
            titre='sub menu 1',
            options=[option1,option2,option3,sub_menu1]
           )

menu2 = Menu(
            titre='sub menu 2',
            options=[option1,option2,option3,sub_menu1]
           )

menu3 = Menu(
            titre='sub menu 3',
            options=[option1,option2,option3]
           )

main_menu = Menu(
                titre='Menu principale',
                options=[
                        menu1,menu2,menu3
                        ]
                )

super_menu = Menu(
                options=[
                        Menu(
                            titre="Envoie d'argent",
                            options=[
                                    Menu(
                                        titre="Abonné",
                                        options=[option1,option2]
                                        ),
                                    Menu(
                                        titre="Non abonné",
                                        options=[option1,option2]
                                        )   
                                    ]
                            ),
                    
                        Menu(
                            titre='Payement des facture',
                            options=[
                                    Menu(
                                        titre='Facture E2C',
                                        options=[option1]
                                        ),
                                    Menu(
                                        titre="Facture LCDE",
                                        options=[option1,option2]
                                        )
                                    ]
                            ),
                        
                        Menu(
                            titre="Achat credit et forfait",
                            options=[
                                    Menu(
                                        titre="Pour soi meme",
                                        options=[
                                                Menu(
                                                    titre="Forfait voix",
                                                    options=[
                                                            Menu(
                                                                titre='Forfait 1 jour',
                                                                options=[
                                                                        Option(libelle="4 min",exe=HelloWord),
                                                                        Option(libelle="14 min",exe=Moonlight),
                                                                        Option(libelle="17 min",exe=GoodBye)
                                                                        ]
                                                                ),
                                                            Menu(
                                                                titre='Forfait 7 jours',
                                                                options=[
                                                                        Option(libelle="27 mi",exe=Moonlight),
                                                                        Option(libelle="45 min",exe=GoodBye),
                                                                        Option(libelle="95 min",exe=GoodBye)
                                                                        ]
                                                                ),
                                                            Menu(
                                                                titre='Forfait 30 jours',
                                                                options=[
                                                                        Option(libelle="105 min",exe=HelloWord)
                                                                        ]
                                                                )
                                                            ]
                                                    ),
                                                
                                                Menu(
                                                    titre='Forfait sms',
                                                    options=[
                                                            Option(libelle="100 sms",exe=Moonlight)
                                                            ]
                                                    ),
                                                
                                                Menu(
                                                    titre="Forfait internet",
                                                    options=[
                                                            option1,
                                                            option2
                                                            ]
                                                    )
                                                ]
                                        ),    
                                    ]
                            ),
                        Menu(
                            titre="Epargne et credit",
                            options=[option1]
                            ),
                        Menu(
                            titre="Mon compte",
                            options=[option2]
                            ),
                        Menu(
                            titre="Momopay",
                            options=[option3]
                            ),
                        Menu(
                            titre="Banque",
                            options=[option3]
                            ),
                        Menu(
                            titre="GIMAC-PAY",
                            options=[option1]
                            )
                        ]
                )


if __name__ == "__main__":
    print("""
                    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    ==============================================================================
                                            MODULE MENU MAKE (UIManager)
                    ------------------------------------------------------------------------------
                    [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
          
                                <<< It's your friend "Designer" from Congo/Brazza 242 >>>
          
                    I make this for help to create a console menu. It's one module of my projet.
                    I share it with you, and I hope you can join me on this project. For more 
                    information you can check my GitHub on this link []
           

                    You don't can use this module like a main script, you just can use this like 
                    a imported module. But if you excute this like a main script, It doing show 
                    you a little demo of a MomoMTN's menu. 

                    ==============================================================================
                                                    THANKS YOU 


        """ )
    sleep(8)
    super_menu.run()   