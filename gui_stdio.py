# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gráfica de usuario (GUI) con entrada y salida estándar para el intérprete PAW-like
# Copyright (C) 2010, 2018-2021 José Manuel Ferrer Ortiz
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

import sys


from prn_func import *


traza = False  # Si queremos una traza del funcionamiento del módulo

# Variables que ajusta el intérprete
cambia_brillo    = None      # Carácter que si se encuentra en una cadena, daría o quitaría brillo al color de tinta de la letra
cambia_tinta     = None      # Carácter que si se encuentra en una cadena, cambiaría el color de tinta de la letra
centrar_graficos = []        # Si se deben centrar los gráficos al dibujarlos
historial        = []        # Historial de órdenes del jugador
juego_alto       = None      # Carácter que si se encuentra en una cadena, pasaría al juego de caracteres alto
juego_bajo       = None      # Carácter que si se encuentra en una cadena, pasaría al juego de caracteres bajo
paleta           = ([], [])  # Paleta de colores sin y con brillo, para los cambios con cambia_*
todo_mayusculas  = False     # Si la entrada del jugador será incondicionalmente en mayúsculas
ruta_graficos    = ''

limite      = (53, 25)  # Ancho y alto máximos absolutos de cada subventana
num_subvens = 8         # DAAD tiene 8 subventanas

# Variables propias de este módulo de entrada y salida estándar
elegida    = 1      # Subventana elegida (la predeterminada es la 1)
nuevaLinea = False  # Si el siguiente texto a imprimir debería ir en una nueva línea


# Funciones que no hacen nada al usar entrada y salida estándar de puro texto

def borra_orden ():
  """Borra la entrada realimentada en pantalla en la subventana de entrada si es subventana propia, y recupera la subventana anterior"""
  pass

def cambia_subv_input (stream, opciones):
  """Cambia la subventana de entrada por el stream dado, con las opciones dadas, según el condacto INPUT"""
  pass

def cambia_topes (columna, fila):
  """Cambia los topes de la subventana de dibujo elegida"""
  pass

def guarda_cursor ():
  """Guarda la posición del cursor de la subventana elegida """
  pass

def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gráfico en la posición del cursor"""
  pass

def elige_subventana (numero):
  """Selecciona una de las subventanas"""
  global elegida, nuevaLinea
  if numero != elegida:
    elegida    = numero
    nuevaLinea = True

def espera_tecla (tiempo = 0):
  """Espera hasta que se pulse una tecla (modificadores no), o hasta que pase tiempo segundos, si tiempo > 0"""
  pass

def pos_subventana (columna, fila):
  """Cambia la posición de origen de la subventana de dibujo elegida"""
  pass

def prepara_topes (columnas, filas):
  """Inicializa los topes al número de columnas y filas dado"""
  pass

def redimensiona_ventana (evento = None):
  """Maneja eventos en relación a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  pass


# Funciones que implementan la entrada y salida por entrada y salida estándar de puro texto

def abre_ventana (traza, modoPantalla, bbdd):
  """Abre la ventana gráfica de la aplicación"""
  global cambia_brillo, cambia_tinta, juego_alto, juego_bajo
  if juego_alto == 48:  # La @ de SWAN
    juego_alto = '@'
    juego_bajo = '@'
  elif juego_alto == 14:  # La ü de las primeras versiones de DAAD
    juego_alto = '\x0e'
    juego_bajo = '\x0f'
  if cambia_brillo:
    cambia_brillo = chr (cambia_brillo)
    cambia_tinta  = chr (cambia_tinta)

def borra_pantalla (desdeCursor = False, noRedibujar = False):
  """Limpia la subventana de dibujo"""
  marcaNuevaLinea()

def borra_todo ():
  """Limpia la pantalla completa"""
  marcaNuevaLinea()

def carga_cursor ():
  """Carga la posición del cursor guardada de la subventana elegida """
  marcaNuevaLinea()

def hay_grafico (numero):
  """Devuelve si existe el gráfico de número dado"""
  return False

def imprime_banderas (banderas):
  """Imprime el contenido de las banderas (en la salida de error estándar)"""
  prn ('Impresión de banderas como texto (en stderr) no implementada', file = sys.stderr)

def imprime_cadena (cadena, scroll = True, redibujar = True):
  """Imprime una cadena en la posición del cursor (dentro de la subventana)"""
  global nuevaLinea
  if nuevaLinea:
    prn()
  prn (limpiaCadena (cadena), end = '')
  nuevaLinea = False

def lee_cadena (prompt, inicio, timeout, espaciar = False):
  """Lee una cadena (terminada con Enter) desde el teclado, dando realimentación al jugador

El parámetro prompt, es el mensaje de prompt
El parámetro inicio es la entrada a medias anterior
El parámetro timeout es una lista con el tiempo muerto, en segundos
El parámetro espaciar permite elegir si se debe dejar una línea en blanco tras el último texto"""
  if prompt:
    imprime_cadena (prompt)
  entrada = raw_input()
  return entrada

def marcaNuevaLinea ():
  """La próxima vez que se escriba algo, hacerlo en línea nueva"""
  global nuevaLinea
  nuevaLinea = True

def mueve_cursor (columna, fila = None):
  """Cambia de posición el cursor de la subventana elegida"""
  marcaNuevaLinea()


# Funciones auxiliares que sólo se usan en este módulo

def limpiaCadena (cadena):
  if not cambia_brillo and not cambia_tinta and not juego_alto and not juego_bajo:
    return cadena
  limpia = ''
  c = 0
  while c < len (cadena):
    if cadena[c] in (cambia_brillo, cambia_tinta, juego_alto, juego_bajo):
      if cadena[c] in (cambia_brillo, cambia_tinta):
        c += 1  # Descartamos también el siguiente byte, que indica el color o si se activa o no
    else:
      limpia += cadena[c]
    c += 1
  return limpia
