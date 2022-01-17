# Třída pro tvorbu GUI.
# @author Michaela Benešová
# @verze 1.0
# datum 12.01.2022

from cgitb import text
from tkinter import *
from tkinter import messagebox
from client import Client
import threading
import sys

class Quiz:
	global round
	round = 0

	def __init__(self, gui):
		""" Metoda, která se zavolá při inicializaci nového objektu.
		"""

		#klient
		self.client = Client(self)
		self.gui = gui
		self.canvas= Canvas(gui, width = 820, height = 460,bg="gray")
		self.canvas.pack()			

		self.radio_buttons_array = []
		for i in range(4):
			radio_btn = Radiobutton(gui,text=" ",variable="", value = i+1,font = ("ariel",14),bg='white')
			self.radio_buttons_array.append(radio_btn)

		# vytvoření jednotlivých labelů a tlačítek
		self.right_btn = Button()

		self.text_points = Text()
		self.text_points = " "
		self.points_label = Label()
		self.points_label = Label(self.canvas,text=self.text_points,fg='black',bg='gray', font=('ariel' ,16, 'bold'))
		self.points_label.place(relx=0.015,rely=0.035)

		self.opt_selected = IntVar()

		self.quit_button()
		self.display_menu()		

	
	def display_menu(self):
		""" Zobrazí menu.
		"""
		for idx, btn in enumerate(self.radio_buttons_array):
			btn.config(text=" ",variable=self.opt_selected, value = idx+1,font = ("ariel",14))
			btn.place(x = 10000, y = 1000)

		self.right_btn.place(x=-100, y=-100)
		
		texts = Text()
		texts = "                "
		self.points_label = Label(self.canvas,text=texts,fg='black',bg='gray', font=('ariel' ,16, 'bold'))
		self.points_label.place(relx=0.015,rely=0.035)


		user_name = StringVar()
		ip_address = StringVar()
		port = IntVar()
		passwd = StringVar()

		menu_frame = Frame(self.canvas,bg="white")
		menu_frame.place(relwidth=0.8,relheight=0.8,relx=0.1,rely=0.1)

		heading = Label(menu_frame,text="Kvíz",fg="pink",bg="white")
		heading.config(font=('´helvetica 36 italic'))
		heading.place(relx=0.4,rely=0.1)

		#user_name
		ulabel = Label(menu_frame,text="Přezdívka",fg='black',bg='white')
		ulabel.place(relx=0.21,rely=0.4)
		uname = Entry(menu_frame,bg='#d3d3d3',fg='black',textvariable = user_name)
		uname.config(width=42)
		uname.place(relx=0.31,rely=0.4)

		#ip_address
		iplabel = Label(menu_frame,text="IP adresa",fg='black',bg='white')
		iplabel.place(relx=0.21,rely=0.5)
		ipname = Entry(menu_frame,bg='#d3d3d3',fg='black',textvariable = ip_address)
		ipname.config(width=42)
		ipname.place(relx=0.31,rely=0.5)

		#port
		portlabel = Label(menu_frame,text="Port",fg='black',bg='white')
		portlabel.place(relx=0.21,rely=0.6)
		portname = Entry(menu_frame,bg='#d3d3d3',fg='black',textvariable = port)
		portname.config(width=42)
		portname.place(relx=0.31,rely=0.6)

		#heslo
		passlabel = Label(menu_frame,text="Heslo",fg='black',bg='white')
		passlabel.place(relx=0.21,rely=0.7)
		passname = Entry(menu_frame,bg='#d3d3d3',fg='black',textvariable = passwd)
		passname.config(width=42)
		passname.place(relx=0.31,rely=0.7)

		log = Button(menu_frame,text='Připojit se na server',padx=5,pady=5,width=5, command= lambda: self.connect(user_name.get(), portname.get(), ipname.get(), passname.get()))
		log.configure(width = 15,height=1, activebackground = "#33B5E5", relief = FLAT)
		log.place(relx=0.5,rely=0.9)


	def connect(self, name, portname, ipname, passname):
		can = True
		global round
		if round == 0:
			if portname == "":
					self.show_wrong_label("Vypiš port")
					can = False
			elif ipname == "":
					self.show_wrong_label("Vypiš ip")
					can = False
			elif name == "":
					self.show_wrong_label("Vypiš jméno")
					can = False	

			if can == True and self.client.connect(portname, ipname):
				thread = threading.Thread(target=self.client.recieve_from_server)
				thread.start()
			else:
				can = False
				
		
		if(can == True):
			self.client.request_id_player(name, passname)
		


	def connect_input(self):
		""" Připojení do místnosti či vytvoření místnosti.
		"""
		connect_input_frame = Frame(self.canvas,bg="white")
		connect_input_frame.place(relwidth=0.8,relheight=0.8,relx=0.1,rely=0.1)
		id_room = IntVar()

		#číslo místnosti, kam se chce uživatel připojit
		idroomlabel = Label(connect_input_frame,text="ID místnosti",fg='black',bg='white')
		idroomlabel.place(relx=0.4,rely=0.53)
		idroom = Entry(connect_input_frame,bg='#d3d3d3',fg='black',textvariable = id_room)
		idroom.config(width=42)
		idroom.place(relx=0.50,rely=0.53)

		#vytvoření méstnosti
		newroom = Button(connect_input_frame,text='Vytvořit místnost',padx=5,pady=5,width=5,command= lambda: self.client.create_new_room())
		newroom.configure(width = 15,height=1, activebackground = "#33B5E5", relief = FLAT)
		newroom.place(relx=0.2,rely=0.3)

		#připojení do místnosti
		existingroom = Button(connect_input_frame,text='Připojit se do místnosti',padx=5,pady=5,width=5, command= lambda: self.client.connect_to_game(id_room.get()))
		existingroom.configure(width = 15,height=1, activebackground = "#33B5E5", relief = FLAT)
		existingroom.place(relx=0.2,rely=0.5)

	def display_room(self, num_players, admin, id = ''):
			""" Zobrazí lobby.
			@param num_players = počet hráčů
			@param admin (boolean) = zda je nebo není admin
			@param id = id lobby, zobrazuje se jen adminovi
			"""
			display_room_frame = Frame(self.canvas,bg="white")
			display_room_frame.place(relwidth=0.8,relheight=0.8,relx=0.1,rely=0.1)

			if admin:
				text_people = Text()
				text_people.pack()
				text_people = f"Room ID - {id}\nPlayers: {num_players}/3"
				people_id_label = Label(display_room_frame,text=text_people,fg='black',bg='white', font=('ariel' ,16, 'bold'))
				people_id_label.place(relx=0.4,rely=0.53)
			
			else:
				text_people = Text()
				text_people.pack()
				text_people = f"Players: {num_players}/3"
				people_id_label = Label(display_room_frame,text=text_people,fg='black',bg='white', font=('ariel' ,16, 'bold'))
				people_id_label.place(relx=0.4,rely=0.53)

			if admin:
				start_game_button = Button(display_room_frame,text='Začít hru',padx=5,pady=5,width=5, command= lambda: self.client.start_game())
				start_game_button.configure(width = 15,height=1, activebackground = "#33B5E5", relief = FLAT)
				start_game_button.place(relx=0.2,rely=0.5)

			else:
				text_wait_to_start = Text()
				text_wait_to_start.pack()
				text_wait_to_start = "A teď počkej na zahájení hry adminem."
				wait_to_start_label = Label(display_room_frame,text=text_wait_to_start,fg='black',bg='white', font=('ariel' ,16, 'bold'))
				wait_to_start_label.place(relx=0.4,rely=0.53)
				


	def show_q(self, question, answers):
		""" Zobrazení první otázky.
		@param question = otázka
		@param answers = odpovědi
		"""
		show_q_frame = Frame(self.canvas,bg="white")
		show_q_frame.place(relwidth=0.8,relheight=0.8,relx=0.1,rely=0.1)

		self.display_question(question, show_q_frame)
		self.opt_selected=IntVar()
		self.radio_buttons()
		self.display_options(answers)
		self.send_answer_button()

	def display_question(self, question, show_q_frame):
		""" Zobrazí otázku.
		"""

		question_text = Text()
		question_text.pack()
		question_text = question
		question_label = Label(show_q_frame,text=question_text,fg='black',bg='white', font=('Comic Sans MS' ,16, 'bold'))
		question_label.place(relx=0.3,rely=0.15)


	def display_options(self, answers):
		""" Ukáže možné odpovědi.
		"""
		print(f"odpovedi: {answers}")
		val=0
		answers = answers.split('-')
		self.opt_selected.set(0)

		for idx, option in enumerate(answers):
			self.radio_buttons_array[idx]['text']=option
			val+=1

	def send_answer_button(self):
		""" Tlačítka pro uložení odpovědi a ukončení hry.
		"""
		self.right_btn.config(text="Ulozit odpoved",command=self.send_answer_server, width=22, bg="red",fg="white",font=("ariel",16,"bold"))
		self.right_btn.place(x=350,y=300)

	def send_answer_server(self):
		""" Odešlě odpověď na server.
		"""
		self.client.send_quiz_answer(self.opt_selected.get())


	
	def display_answer(self, answer, points):
		""" Zobrazí správnou odpověď a body.
		"""

		right_answer_text = Text()
		right_answer_text.pack()
		right_answer_text = answer
		right_answer_label = Label(self.canvas,text=f"Správná odpověď: {right_answer_text}.",fg='black',bg='white', font=('Comic Sans MS' ,16, 'bold'))
		right_answer_label.place(relx=0.4,rely=0.4)
		
		self.text_points = f"Body: {points}" 
		self.points_label = Label(self.canvas,text=self.text_points,fg='black',bg='gray', font=('ariel' ,16, 'bold'))
		self.points_label.place(relx=0.015,rely=0.035)



	def start_btn(self):
		""" Při spuštění hry vyžadá id pro hráče na serveru.
		"""
		self.client.request_id_player()

	def show_wrong_label(self, txt):
		""" Ukáže chybovou hlášku.
		@param txt = chybová hláška
		"""
		wrong_text = Text()
		wrong_text.pack()
		wrong_text = txt
		wrong_label = Label(self.canvas,text=wrong_text,fg='black',bg='white', font=('Comic Sans MS' ,16, 'bold'))
		wrong_label.place(relx=0.4,rely=0.2)

		back_to_menu_button = Button(self.canvas,text='zkusit znovu',padx=5,pady=5,width=5, command= lambda: self.back_to_menu(), bg='red')
		back_to_menu_button.configure(width = 15,height=1, activebackground = "#33B5E5", relief = FLAT)
		back_to_menu_button.place(relx=0.4,rely=0.3)
		


	def quit_button(self):
		quit_button = Button(gui, text="Ukončit", command=self.quit_game, width=6,bg="black", fg="white",font=("ariel",16," bold"))
		quit_button.place(x=640,y=50)



	def close_window(self):
		self.quit_game()

	def quit_game(self):
		""" Ukončení hry.
		"""
		self.client.run_ping = False
		self.client.leave_game()
		if(self.client.soc != None):
			self.client.soc.close()
		self.gui.destroy()
		self.gui.quit()

	def radio_buttons(self):
		""" Tlačítka ve stylu radio pro odpovědi.
		"""
		y_pos = 150
		
		for idx, btn in enumerate(self.radio_buttons_array):
			btn.config(text=" ",variable=self.opt_selected, value = idx+1,font = ("ariel",14))
			btn.place(x = 100, y = y_pos)
			y_pos += 40


	def show_score(self, msg:str):
		""" Zobrazí větu zda vyhrál či nevyhrál uživatel.
		"""
		for idx, btn in enumerate(self.radio_buttons_array):
			btn.config(text=" ",variable=self.opt_selected, value = idx+1,font = ("ariel",14))
			btn.place(x = 10000, y = 1000)
		

		self.clean_canvas()

		score_frame = Frame(self.canvas,bg="white")
		score_frame.place(relwidth=0.8,relheight=0.8,relx=0.1,rely=0.1)

		score_text = Text()
		score_text.pack()
		score_text = msg
		score_label = Label(score_frame,text=score_text,fg='black',bg='white', font=('Comic Sans MS' ,16, 'bold'))
		score_label.place(relx=0.4,rely=0.4)

		back_to_menu_button = Button(score_frame,text='Zpět do menu',padx=5,pady=5,width=5, command= lambda: self.back_to_menu())
		back_to_menu_button.configure(width = 15,height=1, activebackground = "#33B5E5", relief = FLAT)
		back_to_menu_button.place(relx=0.2,rely=0.5)

		global round
		round = 1
		if(round != 0):
			self.client.leave_game()


	def clean_canvas(self):
		self.right_btn.place(x=-100, y=-100)
		
		texts = Text()
		texts = "                "
		self.points_label = Label(self.canvas,text=texts,fg='black',bg='gray', font=('ariel' ,16, 'bold'))
		self.points_label.place(relx=0.015,rely=0.035)


	def back_to_menu(self):
		""" Vrátí do menu.
		"""
		self.display_menu()


#vytvoří gui
gui = Tk()
#nastaví velikost
gui.geometry("820x460")
gui.maxsize(height=460, width=820)
#zobrazí název
gui.title("Kvízeček")
#vytvoří objekt
quiz = Quiz(gui)
gui.protocol("WM_DELETE_WINDOW", quiz.close_window)
#zapne gui
gui.mainloop()


