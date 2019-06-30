
#IMPORTAÇÃO_DE_BIBLIOTECA-----------------------------------------------------------------

import tkinter as tk
import time
import RPi.GPIO as gpio
import threading

import matplotlib.pyplot as plt

#  sensor


import os
import glob





#KERAS

import tensorflow
import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import History

#SET_GPIO---------------------------------------------------------------------------------
gpio.setwarnings(False)
gpio.setmode (gpio.BOARD)
gpio.setup(37,gpio.OUT)
atuador = gpio.PWM(37,6.25)
atuador.start(0)
#VARIAVEIS--------------------------------------------------------------------------------

contador = 5 # contador integrador



#COMANDOS/BUTTON
cor = ('#1b9ac1')
primeiro_ciclo=True
alterar_setpoint=0
start=False
start_dois=True
liga=False
desliga=False
# TEMPOS
segundo_inicial = 0
tempo=0
segundo_atual=0
tempo_total=0
duty=50
#SENSORES
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28-021317df07aa*')[0]
device_file = device_folder + '/w1_slave'


sensor_um=0
sensor_dois=30
#GRAFICO
linhax = []
linhay = []

# IA
history = History()
epoca =500
# PID
kp=28
ki=0.1

PI=0
P = 0
I = 0
erro=0
rang=0
h=0 #gravar o range do pid

# JANELA----------------------------------------------------------------------------------
Window = tk.Tk()
Window.configure(background=('#11579d'))
Window.title('Controlador de temperatura')
Window.geometry('800x450')
# AVISOS----------------------------------------------------------------------------------

label4 = tk.Label(text='SECADOR °C', font=('Times New Roman',18),bg=('#11579d'), fg=('#110f7a'))
label4.place(x=80, y=5)


label5 = tk.Label(text='SET POINT °C', font=('Times New Roman',18),bg=('#11579d'), fg=('#110f7a'))
label5.place(x=78, y=87)
label6 = tk.Label(text='FABRICA °C', font=('Times New Roman',18),bg=('#11579d'), fg=('#110f7a'))
label6.place(x=320, y=5)
label7 = tk.Label(text='VENTILAÇÃO %', font=('Times New Roman',18),bg=('#11579d'), fg=('#110f7a'))
label7.place(x=520, y=5)
label6 = tk.Label(text='ATUADOR %', font=('Times New Roman',18),bg=('#11579d'), fg=('#110f7a'))
label6.place(x=320, y=87)
label6 = tk.Label(text='   ERRO   ', font=('Times New Roman',18),bg=('#11579d'), fg=('#110f7a'))
label6.place(x=540, y=87)
#icon1 = tk.PhotoImage(file='logo_satc.png')
#icon1 = icon1.subsample(2,4)
#label10 = tk.Label(image=icon1)
#label10.place(x=360, y=220,relwidth=0.15,relheight=0.18)

# CAIXAS_DE_TEXTO--------------------------------------------------------------------------

text_field_int = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=9)
text_field_int.place(x=55, y=35)
text_field_ext = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=9)
text_field_ext.place(x=290, y=35)
text_field_atu = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=9)
text_field_atu.place(x=290, y=120)
text_field_vent = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=9)
text_field_vent.place(x=520, y=35)
text_field_k = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=9)
text_field_k.place(x=520, y=120)

text_field_nki = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=11)
text_field_nki.place(x=306, y=320)
121
text_field_kp = tk.Text(master=Window,font=('Times New Roman',30),height=1, width=11)
text_field_kp.place(x=552, y=190)

text_field_ki = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=11)
text_field_ki.place(x=552, y=255)



text_field_nkp = tk.Text(master=Window,font=('Times New Roman',30),height=1, width=11)
text_field_nkp.place(x=306, y=190)

text_field_loss = tk.Text(master=Window,font=('Times New Roman',30), height=1, width=11)
text_field_loss.place(x=306, y=255)


# ENTRADAS_DE_TEXTO------------------------------------------------------------------------
entry_field_set = tk.Entry(font=('Times New Roman',30),width=9)
entry_field_set.place(x=55, y=120)

# LOOP-------------------------------------------------------------------------------------





def sensor():
  global start,sensor_um,segundo_inicial,segundo_atual,linhax,linhay,duty,segundo_inicial,out,setpoint,kp,Ki,P,I,rang,h,contador

  
  segundo_inicial = time.time()
  atuador.ChangeDutyCycle(duty)


  
  while True:
      print (segundo_atual)
      segundo_atual = time.time() - segundo_inicial
      segundo_atual = ("%.2f" % segundo_atual)
      f = open(device_file, 'r')
      lines = f.readlines()
      f.close()
      text_field_int.delete('1.0', 'end')
      text_field_k.delete('1.0', 'end')
      text_field_kp.delete('1.0', 'end')
      text_field_ki.delete('1.0', 'end')
  
      
      equals_pos = lines[1].find('t=')
      temp_string = lines[1][equals_pos+2:]  
      sensor_um = float(temp_string) / 1000.0
      sensor_um = ("%.2f" % sensor_um)
      text_field_int.insert(tk.END,sensor_um)
                          
      linhax.append(segundo_atual)
      linhay.append(sensor_um)    
      setpoint=float(entry_field_set.get())
      erro = -(float(sensor_um) -setpoint)
      erro = ("%.2f" % erro)
      text_field_k.insert(tk.END,erro)
      P = (float(erro)*kp)
      I = I+(float(erro)*ki)
  
      if contador != 5:
        contador += 1
      if (contador == 5):
        contador = 0

      text_field_kp.insert(tk.END,P)
      text_field_ki.insert(tk.END,I)
  
      PI = P + I
    
      if h == 0:
        rang = P
        h=1
      duty = (PI*100)/rang
      if duty>=100:
        duty=100
        atuador.ChangeDutyCycle(duty/2)
        text_field_atu.delete('1.0', 'end')
        text_field_atu.insert(tk.END,duty,'%')
      elif duty<=0:
        duty=0
        atuador.ChangeDutyCycle(duty/2)
        text_field_atu.delete('1.0', 'end')
        text_field_atu.insert(tk.END,duty,'%')

        
      else:
   
        atuador.ChangeDutyCycle(duty/2)
        text_field_atu.delete('1.0', 'end')
        text_field_atu.insert(tk.END,duty,'%')
  
def liga():
  global primeiro_ciclo,sensor_um,sensor_dois,start,ia,setpoint,kp,ki
  setpoint=int(entry_field_set.get())

  f = open(device_file, 'r')
  lines = f.readlines()
  f.close()
  text_field_int.delete('1.0', 'end')
  equals_pos = lines[1].find('t=')
  temp_string = lines[1][equals_pos+2:]
  sensor_um = float(temp_string) / 1000.0
  sensor_um = ("%.2f" % sensor_um)
  text_field_ext.insert(tk.END,sensor_um)
  text_field_int.insert(tk.END,sensor_um)
  text_field_vent.insert(tk.END,'100 %')



  
  sensor_um = float(sensor_um)
  print ('TEMPERATURA DA FABRICA:',sensor_um,'°C')
  
  x = np.array([[0.24,0.24,0.2],[0.25,0.25,0.2],[0.23,0.23,0.2],[0.38,0.38,0.2],#Matriz entrada
      [0.36,0.36,0.2],[0.39,0.39,0.2],[0.01,0.01,0.2],[0.01,0.01,0.2],[0.01,0.01,0.2]]) 
  y = np.array([[0.21], [0.21], [0.21],[0.31],[0.31],[0.31],[0.28],[0.28],[0.28]])#Matriz resultante
  model = Sequential()# Modelo sequencial
  model.add(Dense(9, input_dim=3))# Modelo três entradas nove camadas internas
  model.add(Dense(1))# Uma saida
  model.compile(optimizer='sgd', loss='mse', metrics=['acc'])# Parâmetros funcionais
  model.fit(x, y,callbacks=[history], epochs=epoca)# Passa esse modelo 500 vezes pela rede
  w =(sensor_um/100)#Lê sensor temperatura interna
  v =(sensor_dois/100)#Lê sensor temperatura externa
  z =ki#Lê ki
  lista = float(w), float(v),float(z)# Transforma os valores em uma lista
  th = np.asmatrix(lista)# Transforma a lista em uma matriz
  result = model.predict(th)# Passa a matriz no modelo treinado
  losss = history.history ['loss']
  kp = result*100 # Resultado de kp
  kp= kp[0][0]
  print('')
  print('')
  print('')
  print('')
  text_field_nkp.insert(tk.END, kp )
  text_field_loss.insert(tk.END,"%.10f" % losss[epoca-1])
  print("IA-KP %.2f" % kp)




  l = np.array([[0.20,0.20,0.18],[0.22,0.22,0.18],[0.26,0.26,0.18],[0.38,0.38,0.24],[0.36,0.36,0.24],[0.32,0.32,0.24],[0.01,0.01,0.08],[0.01,0.01,0.05],[0.01,0.01,0.05]])
  m = np.array([[0.02], [0.02], [0.02],[0.03],[0.03],[0.03],[0.01],[0.01],[0.01]])
  model = Sequential()
  model.add(Dense(9, input_dim=3))
  model.add(Dense(1))
  model.compile(optimizer='sgd', loss='mse', metrics=['acc'])
  model.fit(x, y,callbacks=[history], epochs=epoca)
  n =(sensor_um/100) 
  o =(sensor_um/100)
  p =kp/100
  lista = float(n), float(o),float(p)
  th = np.asmatrix(lista)
  result = model.predict(th)
  losss = history.history ['loss']
  ki= result[0][0]
  print('',ki)

  text_field_nki.insert(tk.END,ki)
  text_field_loss.insert(tk.END,"%.10f" % losss[epoca-1])
  print("IA-KI %.2f" % ki)
    
  controle2=threading.Timer(1,sensor)
  controle2.start()



def desliga():
  global primeiro_ciclo,duty,start
  
 
  start_dois=True
  start=False
  duty=0
  atuador.ChangeDutyCycle(duty)
  primeiro_ciclo== False
  print('desligado')





def grafico():
        global segundo_atual,linhax,linhay
        fig = plt.figure(1, figsize=(13, 6))
        rect= fig.patch
        rect.set_facecolor('#72858e')
        ax1 = fig.add_subplot(1,1,1,axisbg='w')
        ax1.plot(linhax,linhay,'r',linewidth=2 )
        ax1.tick_params(axis='x', colors='b')
        ax1.tick_params(axis='y',colors='r')
        ax1.spines['bottom'].set_color('k')
        ax1.spines['top'].set_color('r')
        ax1.spines['left'].set_color('k')
        ax1.xaxis.label.set_color('b')
        ax1.yaxis.label.set_color('r')
        ax1.set_title('Controle de Temperatura', color='k',fontsize=23)
        ax1.set_xlabel('Tempo (s)', fontsize=21)
        ax1.set_ylabel('Temperatura °C ', fontsize=21)
        plt.grid(True)
        plt.savefig("frio01G1.png")
        print('KP = 2,2 KI = 0,15 Ti = 5s')
        print('')
        print (linhax)
        print('')
        print (linhay)
        print('')
        plt.show()

def volta():
  entry_field_set.delete(0,'end')
def zero():
  entry_field_set.insert(tk.END,0)
def um():
  entry_field_set.insert(tk.END,1)
def dois():
  entry_field_set.insert(tk.END,2)
def tres():
  entry_field_set.insert(tk.END,3)
def quatro():
  entry_field_set.insert(tk.END,4)
def cinco():
  entry_field_set.insert(tk.END,5)
def seis():
  entry_field_set.insert(tk.END,6)
def sete():
  entry_field_set.insert(tk.END,7)
def oito():
  entry_field_set.insert(tk.END,8)
def nove():
  entry_field_set.insert(tk.END,9)

def a():
  global duty
  atuador.ChangeDutyCycle(duty)
  text_field_atu.insert(tk.END,duty,'%')


# BOTOES-----------------------------------------------------------------------------------
button1 = tk.Button(text='Iniciar', bg=('#26e04e'), fg=('white'),command=liga)
button1.place(x=552, y=385)
button1.config(height=3, width=26)
button2 = tk.Button(text='Desligar', bg=('#d11717'), fg=('white'),command=desliga)
button2.config(height=3, width=26)
button2.place(x=306, y=385)
button3 = tk.Button(text='Del', bg=cor, fg=('white'),command=volta)
button3.config(height=3, width=8)
button3.place(x=205, y=385)
button4 = tk.Button(text='0', bg=cor, fg=('white'),command=zero)
button4.config(height=3, width=8)
button4.place(x=105, y=385)
button5 = tk.Button(text='#', bg=cor, fg=('white'),command=a)
button5.config(height=3, width=8)
button5.place(x=5, y=385)
button6 = tk.Button(text='1', bg=cor, fg=('white'),command=um)
button6.config(height=3, width=8)
button6.place(x=5, y=190)
button7 = tk.Button(text='2', bg=cor, fg=('white'),command=dois)
button7.config(height=3, width=8)
button7.place(x=105, y=190)
button8 = tk.Button(text='3', bg=cor, fg=('white'),command=tres)
button8.config(height=3, width=8)
button8.place(x=205, y=190)
button9 = tk.Button(text='4', bg=cor, fg=('white'),command=quatro)
button9.config(height=3, width=8)
button9.place(x=5, y=255)
button10 = tk.Button(text='5', bg=cor, fg=('white'),command=cinco)
button10.config(height=3, width=8)
button10.place(x=105, y=255)
button11= tk.Button(text='6', bg=cor, fg=('white'),command=seis)
button11.config(height=3, width=8)
button11.place(x=205, y=255)
button12 = tk.Button(text='7', bg=cor, fg=('white'),command=sete)
button12.config(height=3, width=8)
button12.place(x=5, y=320)
button13= tk.Button(text='8', bg=cor, fg=('white'),command=oito)
button13.config(height=3, width=8)
button13.place(x=105, y=320)
button14 = tk.Button(text='9', bg=cor, fg=('white'),command=nove)
button14.config(height=3, width=8)
button14.place(x=205, y=320)
button15 = tk.Button(text='Gerar Gráfico', bg=cor, fg=('white'),command=grafico)
button15.config(height=3, width=26)
button15.place(x=552, y=320)

Window.mainloop()
