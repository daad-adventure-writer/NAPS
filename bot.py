#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Bot de Telegram para ejecutar aventuras mediante NAPS
# Copyright (C) 2023 José Manuel Ferrer Ortiz
#
# *****************************************************************************
# *                                                                           *
# *  This program is free software; you can redistribute it and/or modify it  *
# *  under the terms of the GNU General Public License version 2, as          *
# *  published by the Free Software Foundation.                               *
# *                                                                           *
# *  This program is distributed in the hope that it will be useful, but      *
# *  WITHOUT ANY WARRANTY; without even the implied warranty of               *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU         *
# *  General Public License version 2 for more details.                       *
# *                                                                           *
# *  You should have received a copy of the GNU General Public License        *
# *  version 2 along with this program; if not, write to the Free Software    *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA  *
# *                                                                           *
# *****************************************************************************

import importlib
import os
import subprocess
import sys
import telebot
import time

import bot_juegos

from prn_func import prn

try:
  from PyQt4.QtCore import *
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtWidgets import *


carpeta_juegos = '../juegos'  # Ruta a la carpeta donde están los juegos
cod_interprete = 'utf-8'      # Codificación de entrada y salida del intérprete

MAX_ESPERA    = 30 * 60  # Tiempo máximo desde la última orden que se reserva la plaza a los jugadores
MAX_SESION    = 90 * 60  # Tiempo máximo desde la última orden que se mantiene la sesión de los jugadores
MAX_JUGADORES = 12       # Número máximo de jugadores simultáneos
hilos         = []       # Hilos de ejecución para los intérpretes
hilos_usados  = {}       # Número de hilo que está usando cada jugador
interpretes   = {}       # Procesos del intérprete en curso para los jugadores activos
ultima_orden  = {}       # Momento de la última orden de cada jugador

juegos = bot_juegos.juegos


def imprimeLog (mensaje):
  hora = time.strftime ('%H:%M:%S ', time.localtime())
  prn (hora + mensaje)

def limpiaRecursos (usuario):
  if usuario in hilos_usados:
    del hilos_usados[usuario]
  if usuario in interpretes:
    del interpretes[usuario]
  if usuario in ultima_orden:
    del ultima_orden[usuario]


class ManejoInterprete (QThread):
  """Maneja la comunicación con el intérprete ejecutando la base de datos"""
  def __init__ (self, padre):
    QThread.__init__ (self, parent = padre)

  def preparaHilo (self, numHilo, procInterprete, usuario):
    self.numHilo        = numHilo
    self.procInterprete = procInterprete
    self.usuario        = usuario

  def run (self):
    """Lee del proceso del intérprete"""
    parrafo = ''
    while True:
      linea = self.procInterprete.stdout.readline()
      # prn (str (linea))
      if not linea:
        linea = True
        while linea:
          linea = self.procInterprete.stderr.readline()
          imprimeLog (str (linea))
        break  # Ocurre cuando el proceso ha terminado
      linea = linea.rstrip()
      if linea:  # Añadimos la línea al párrafo
        parrafo += ('\n' if parrafo else '') + linea
      elif parrafo:
        if self.usuario:
          if '```' in parrafo:
            bot.send_message (self.usuario, parrafo, parse_mode = 'markdown')
          else:
            bot.send_message (self.usuario, parrafo)
        parrafo = ''
    # El proceso ha terminado
    imprimeLog ('Proceso terminado del jugador ' + str (self.usuario))
    limpiaRecursos (self.usuario)

aplicacion = QApplication (sys.argv)
for i in range (MAX_JUGADORES):
  hilos.append (ManejoInterprete (aplicacion))

bot = telebot.TeleBot (os.environ.get ('TELEGRAM_TOKEN'))

@bot.message_handler (commands=['quit', 'start'])
def menuPrincipal (message):
  usuario = message.chat.id
  if usuario in interpretes:
    interpretes[usuario].kill()
    limpiaRecursos (usuario)
  opciones = telebot.types.ReplyKeyboardMarkup (one_time_keyboard = True)
  for nombreJuego in juegos:
    opciones.add (telebot.types.KeyboardButton ('/jugar ' + nombreJuego))
  bot.send_message (usuario, 'Bienvenido a NAPS bot, el bot de Telegram que utiliza NAPS para permitirte jugar una selección de aventuras conversacionales de los sistemas Quill, PAWS, SWAN o DAAD.', reply_markup = opciones)
  ayuda (message)

@bot.message_handler (commands=['ayuda', 'help'])
def ayuda (message):
  usuario = message.chat.id
  bot.send_message (usuario, 'Utiliza el comando /quit o /start para terminar el juego en curso y preparar el botón de Telegram con la lista de juegos disponibles.')
  bot.send_message (usuario, 'Elige qué juego jugar o cambia el juego en curso con el comando /jugar o /play. Puedes usar el botón de Telegram para esta función.')
  bot.send_message (usuario, 'Utiliza el comando /ayuda o /help para volver a mostrar estos mensajes de ayuda.')

@bot.message_handler (commands=['jugar', 'play'])
def comandoJugar (message):
  eleccion = message.text[7 if message.text[1] == 'j' else 6:].strip()
  if eleccion not in juegos:
    bot.reply_to (message, 'Ese no es uno de los juegos disponibles.')
    return
  usuario = message.chat.id
  if usuario in interpretes:
    interpretes[usuario].kill()
    limpiaRecursos (usuario)
  elif len (interpretes) >= MAX_JUGADORES:
    cerrar     = []  # Usuarios con tiempo de sesión superado
    masAntiguo = (None, 99999999999999)
    for jugador, tiempo in ultima_orden.items():
      if int (time.time()) - tiempo >= MAX_SESION:
        cerrar.append (jugador)
      elif tiempo < masAntiguo[1]:
        masAntiguo = (jugador, tiempo)
    # Liberamos recursos cerrando los intérpretes de jugadores que han superado el tiempo de sesión
    for jugador in cerrar:
      interpretes[jugador].kill()
      limpiaRecursos (jugador)
    if len (interpretes) >= MAX_JUGADORES and int (time.time()) - masAntiguo[1] < MAX_ESPERA:  # Están todos activos
      bot.send_message (usuario, 'Se ha alcanzado el número máximo de jugadores simultáneos activos. Inténtalo de nuevo en otra ocasión.')
      return
    # Cerramos el intérprete del más antiguo
    interpretes[masAntiguo[0]].kill()
    limpiaRecursos (masAntiguo[0])
  opciones = telebot.types.ReplyKeyboardMarkup()
  opciones.add (telebot.types.KeyboardButton ('/start'))
  bot.send_message (usuario, 'Has elegido jugar a ' + eleccion + '. Puedes usar el comando /quit o /start para terminar la partida.', reply_markup = opciones)
  bot.send_message (usuario, 'El tiempo de inactividad es de 30 minutos. Si pasa ese tiempo, tu plaza como jugador se cede a otros.')
  nombreFichBD   = os.path.join (os.path.dirname (os.path.realpath (__file__)), carpeta_juegos, juegos[eleccion][0].replace ('/', os.sep))
  rutaInterprete = os.path.join (os.path.dirname (os.path.realpath (__file__)), 'interprete.py')
  argumentos     = ['python', rutaInterprete, '-g', 'telegram', nombreFichBD]
  if len (juegos[eleccion]) > 1:
    argumentos.extend (juegos[eleccion][1])
  if '--conversion' in argumentos:  # Anteponemos la carpeta del juego al fichero de conversión
    posicion = argumentos.index ('--conversion') + 1
    argumentos[posicion] = os.path.join (os.path.dirname (nombreFichBD), argumentos[posicion])
  imprimeLog ('El jugador ' + str (usuario) + ' intenta cargar ' + nombreFichBD)
  # devnull        = open (os.devnull, 'w')
  # procInterprete = subprocess.Popen (argumentos, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = devnull)
  procInterprete = subprocess.Popen (argumentos, encoding = cod_interprete, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  interpretes[usuario]  = procInterprete
  ultima_orden[usuario] = int (time.time())
  for i in range (MAX_JUGADORES):
    if i not in hilos_usados.values():
      hilos_usados[usuario] = i
      hilos[i].preparaHilo (i, procInterprete, usuario)
      hilos[i].start()
      break

@bot.message_handler (func = lambda msg: True)
def ordenRecibida (message):
  usuario = message.chat.id
  if usuario not in interpretes:
    return  # Ese usuario no está jugando ahora mismo
  ultima_orden[usuario] = int (time.time())
  enviar = message.text
  interpretes[usuario].stdin.write (enviar + '\n')
  interpretes[usuario].stdin.flush()
  if os.path.isfile ('recargar/juegos'):
    try:
      modulo = importlib.reload (bot_juegos)
    except Exception as e:
      imprimeLog ('Fallo al intentar recargar la lista de juegos')
      imprimeLog (e)
      return
    global juegos
    juegos = bot_juegos.juegos
    imprimeLog ('Recargada la lista de juegos')
    try:
      os.remove ('recargar/juegos')
    except:
      imprimeLog ('Imposible borrar el fichero que pide la recarga')


bot.infinity_polling()
