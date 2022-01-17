# Třída, která reprezentuje klienta.
# @author Michaela Benešová
# @verze 1.0
# datum 12.01.2022

import socket
import threading
from time import sleep
from msg_codes import *


class Client:
    def __init__(self, gui) -> None:
        """ Konstruktor, který připraví základní věci pro připojení.
        """
        self.HOST = ""  # adresa serveru
        self.PORT = 0       # port využívaný serverem
        self.id = -1
        self.gui = gui
        self.run_ping = True
        self.run_receive = True
        self.soc = None
        self.thread_ping = None

    def ping(self):
        while(self.run_ping):
            if(self.send_msg(PING) == False):
                print("Odpojeni")
                self.end_threads()
            sleep(1)
    
    def end_threads(self):
        self.run_recieve = False
        self.run_ping = False
        self.soc.close()

    def connect(self, port, ipname):
        """ Pokus o připojení na server.
        """
        self.HOST = ipname
        self.PORT = int(port)
        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect((self.HOST, self.PORT))
            return True
        except:
            self.receive_wrong("server nefunguje")
            return False


    def send_msg(self, msg_code, msg_param='x'):
        """ Poslání zprávy
            @param msg_code = kód zprávy
            @param msg_param = parametr zprávy
        """
        msg = f'{self.id},{msg_code},{msg_param}'
        print(f'Na server odesilam: {msg}')
        try:
            self.soc.sendall(msg.encode())
            return True
        except:
            self.gui.show_wrong_label('Server nefunguje.')
            return False

    def recieve_from_server(self):
        """Přijímání zpráv ze serveru
        """
        while(self.run_receive):
            data = ''
            try:
                data = self.soc.recv(512)
            except:
                return

            data = data.decode()
            print(f'Přijímám: {data}')
            data = data.split(',')
            data = [s.rstrip('\x00') for s in data]
            try:
                msg_code = int(data[0])
            except:
                break
            if msg_code == REQ_ID:
                self.set_player_id(int(data[1]))
            elif msg_code == CONNECT_TO_GAME:
                self.can_connect_to_game(data[1])
            elif msg_code == CREATE_NEW_ROOM:
                self.receive_create_new_room(data[1])
            elif msg_code == START_GAME:
                self.receive_start_game(data[1])
            elif msg_code == NEXT_QUESTION:
                self.receive_next_question(data[1])
            elif msg_code == SEND_QUIZ_ANSWER:
                self.receive_quiz_answer(data[1])
            elif msg_code == ERR:
                self.receive_wrong(data[1])
            elif msg_code == BACK_TO_MENU:
                self.receive_back_to_menu()
            elif msg_code == SHOW_TABLE:
                self.show_table(data[1])
            else:
                print('chybný kód')
            
            
#-----------------------------------------------------
#------------ Metody, které odesílají na server a přijímají z něj --------
#-----------------------------------------------------
    
    def connect_to_game(self, id_game):
        """Žádá o připojení do hry
        """
        self.send_msg(str(CONNECT_TO_GAME), str(id_game))

    def can_connect_to_game(self, msg):
        """ Získá ze serveru odpověď, zda se hráč může či nemůže připojit
        """
        if int(msg) > 1:
            self.gui.display_room(int(msg), False)
        else:
            print('Maximální počet hráčů ve hře')


#-----------------------------------------------------

    def request_id_player(self, name, passname):
        """Žádá server o přiřazení id hráče
        """
        sendingmsg = name + "+" + passname
        self.send_msg(str(REQ_ID), sendingmsg)

    def set_player_id(self, id):
        if id == None or id == -1:
            return

        self.thread_ping = threading.Thread(target=self.ping)
        self.thread_ping.start()

        print(f'Nastavuji id hráče na {id}')
        self.id = id
        self.gui.connect_input()

#-----------------------------------------------------


    def reconnect_to_game(self, id_game):
        """Snaží se o znovupřipojení hráče.
        """
        self.send_msg(str(RECONNECT_TO_GAME), str(id_game))

#-----------------------------------------------------


    def create_new_room(self):
        """Žádá server o vytvoření nové místnosti.
        """
        self.send_msg(str(CREATE_NEW_ROOM))

    def receive_create_new_room(self, msg):
        """ Získá odpověď ze serveru, zda se podařilo nebo nepodařilo vytvořit místnost.
        """
        msg = msg.split(';')
        print(msg)
        if int(msg[0]) > -1:
            self.gui.display_room(msg[1], True, int(msg[0]))
        else:
            msg = "Nepodařilo se vytvořit místnost"
            self.gui.show_wrong_label(msg)
            pass

#-----------------------------------------------------

    def start_game(self):
        """ Žáda o začátek hry.
        """
        self.send_msg(str(START_GAME))

    def receive_start_game(self, msg:str):
        """ Získá první otázku a možné odpovědi ze serveru.
        """
        msg = msg.split(';')
        self.gui.show_q(msg[0], msg[1])

    def receive_next_question(self, msg:str):
        """ Získá další otázku a možné odpovědi.
        """
        msg = msg.split(';')
        self.gui.display_question(msg[0])
        self.gui.display_options(msg[1])


#-----------------------------------------------------

    def send_quiz_answer(self, answer):
        """Odešle na server odpověď na otázku
        """
        self.send_msg(str(SEND_QUIZ_ANSWER), answer)

    def receive_quiz_answer(self, msg:str):
        """ Získá ze serveru správnou odpověď na otázku a body.
        """
        msg = msg.split(';')
        self.gui.display_answer(msg[1], msg[0])


#-----------------------------------------------------

    def leave_game(self):
        """ Uživatel žádá o opuštění hry.
        """
        self.send_msg(str(LEAVE_GAME))

#-----------------------------------------------------

    
    def receive_wrong(self, msg:str):
        """ Získání erroru ze serveru.
        """
        self.gui.show_wrong_label(msg)

    def receive_back_to_menu(self):
        """ Server žádá o návrat do menu.
        """
        self.gui.back_to_menu()

    def show_table(self, msg:str):
        """ Získání informace, zda uživatel vyhrál či nevyhrál.
        """
        self.gui.show_score(msg)

