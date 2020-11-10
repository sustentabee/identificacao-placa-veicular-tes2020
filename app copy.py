import serial # leitura da saida da COM
import time # delay de conexão
import os # verificar se o script está rodando em um windows
import msvcrt # input original do windows

conexao = serial.Serial('COM3', 9600) # configuração da conexão
time.sleep(1.8) # delay de conexão

while(True):
    conexao.write(b'F')
    conexao.write(b'V')

conexao.write(b'X') # fim da conexão do lado do arduino
conexao.close() # fim da conexão do lado do python