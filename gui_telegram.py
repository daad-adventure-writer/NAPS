# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gr�fica de usuario (GUI) con entrada y salida est�ndar para el bot de Telegram
# Copyright (C) 2010, 2018-2025 Jos� Manuel Ferrer Ortiz
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

import locale
import sys

from prn_func import *


traza = False  # Si queremos una traza del funcionamiento del m�dulo

# Variables que ajusta el int�rprete y usa esta GUI u otro m�dulo

cod_brillo       = None      # Car�cter que si se encuentra en una cadena, dar�a o quitar�a brillo al color de tinta de la letra
cod_columna      = None      # Car�cter que si se encuentra en una cadena, mover� el cursor a la columna dada
cod_flash        = None      # Car�cter que si se encuentra en una cadena, pondr�a o quitar�a efecto flash a la letra
cod_inversa      = None      # Car�cter que si se encuentra en una cadena, invertir�a o no el papel/fondo de la letra
cod_inversa_fin  = None      # Car�cter que si se encuentra en una cadena, quitar�a  inversi�n del papel/fondo de la letra
cod_inversa_ini  = None      # Car�cter que si se encuentra en una cadena, activar�a inversi�n del papel/fondo de la letra
cod_juego_alto   = None      # Car�cter que si se encuentra en una cadena, pasar�a al juego de caracteres alto
cod_juego_bajo   = None      # Car�cter que si se encuentra en una cadena, pasar�a al juego de caracteres bajo
cod_papel        = None      # Car�cter que si se encuentra en una cadena, cambiar�a el color de papel/fondo de la letra
cod_tabulador    = None      # Car�cter que si se encuentra en una cadena, pondr� espacios hasta mitad o final de l�nea
cod_tinta        = None      # Car�cter que si se encuentra en una cadena, cambiar�a el color de tinta de la letra
cods_tinta       = {}        # Caracteres que si se encuentran en una cadena, cambiar�a el color de tinta por el del valor
centrar_graficos = []        # Si se deben centrar los gr�ficos al dibujarlos
historial        = []        # Historial de �rdenes del jugador
paleta           = ([], [])  # Paleta de colores sin y con brillo, para los cambios con funciones cambia_*
partir_espacio   = True      # Si se deben partir las l�neas en el �ltimo espacio
secuencias       = {}        # Secuencias que convertir en las cadenas
texto_nuevo      = []        # Tendr� valor verdadero si se ha escrito texto nuevo tras el �ltimo borrado de pantalla o espera de tecla

cursores    = [[0, 0]] * 2  # Posici�n relativa del cursor de cada subventana
limite      = [999, 25]     # Ancho y alto m�ximos absolutos de cada subventana
num_subvens = 8             # DAAD tiene 8 subventanas


# Constantes que se exportan (fuera del paquete)

NOMBRE_GUI = 'telegram'


# Variables propias de este m�dulo de entrada y salida est�ndar

bufferTexto = ''     # Texto acumulado entre llamadas a lee_cadena
elegida     = 1      # Subventana elegida (la predeterminada es la 1)
nuevaLinea  = False  # Si el siguiente texto a imprimir deber�a ir en una nueva l�nea


# Funciones que no hacen nada al usar entrada y salida est�ndar de puro texto

def borra_orden ():
  """Borra la entrada realimentada en pantalla en la subventana de entrada si es subventana propia, y recupera la subventana anterior"""
  pass

def cambia_color_borde (color):
  """Cambia el color de borde de la subventana actual por el de c�digo dado"""
  pass

def cambia_color_brillo (valor):
  """Cambia el valor de brillo de la subventana actual seg�n el valor dado"""
  pass

def cambia_color_papel (color):
  """Cambia el color de papel/fondo al escribir la subventana actual por el dado"""
  pass

def cambia_color_tinta (color):
  """Cambia el color de tinta al escribir la subventana actual por el dado"""
  pass

def cambia_cursor (cadenaCursor):
  """Cambia el car�cter que marca la posici�n del cursor en la entrada del jugador"""
  pass

def cambia_subv_input (stream, opciones):
  """Cambia la subventana de entrada por el stream dado, con las opciones dadas, seg�n el condacto INPUT"""
  pass

def cambia_topes (columna, fila):
  """Cambia los topes de la subventana de impresi�n elegida"""
  pass

def carga_paleta_defecto ():
  """Carga a la paleta por defecto para el modo gr�fico"""
  pass

def centra_subventana ():
  """Centra horizontalmente en la ventana la subventana elegida"""
  pass

def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gr�fico en la posici�n del cursor"""
  pass

def guarda_cursor ():
  """Guarda la posici�n del cursor de la subventana elegida """
  pass

def imprime_locs_objs (locs_objs):
  """Imprime las localidades de los objetos"""
  pass

def pos_subventana (columna, fila):
  """Cambia la posici�n de origen de la subventana de impresi�n elegida"""
  pass

def redimensiona_ventana (evento = None):
  """Maneja eventos en relaci�n a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  # Como se usa al hacer pausa, escribimos el buffer ya para no demorar el texto
  escribe_buffer()

def reinicia_subventanas ():
  """Ajusta todas las subventanas de impresi�n a sus valores por defecto"""
  pass


# Funciones que implementan la entrada y salida por entrada y salida est�ndar de puro texto

def abre_ventana (traza, factorEscala, bbdd):
  """Abre la ventana gr�fica de la aplicaci�n"""
  global cod_brillo, cod_columna, cod_flash, cod_inversa, cod_inversa_fin, cod_inversa_ini, cod_juego_alto, cod_juego_bajo, cod_papel, cod_tabulador, cod_tinta
  if cod_juego_alto == 48:  # La @ de SWAN
    cod_juego_alto = '@'
    cod_juego_bajo = '@'
  elif cod_juego_alto == 14:  # La � de las primeras versiones de DAAD
    cod_juego_alto = '\x0e'
    cod_juego_bajo = '\x0f'
  if cod_brillo:
    cod_brillo    = chr (cod_brillo)
    cod_columna   = chr (cod_columna)
    cod_inversa   = chr (cod_inversa)
    cod_flash     = chr (cod_flash)
    cod_papel     = chr (cod_papel)
    cod_tabulador = chr (cod_tabulador)
    cod_tinta     = chr (cod_tinta)
  elif cods_tinta:
    for codigo, color in tuple (cods_tinta.items()):
      del (cods_tinta[codigo])
      cods_tinta[chr (codigo)] = color
    cod_inversa_fin = chr (cod_inversa_fin)
    cod_inversa_ini = chr (cod_inversa_ini)

def borra_pantalla (desdeCursor = False, noRedibujar = False):
  """Limpia la subventana de impresi�n"""
  marcaNuevaLinea()

def borra_todo ():
  """Limpia la pantalla completa"""
  marcaNuevaLinea()

def carga_cursor ():
  """Carga la posici�n del cursor guardada de la subventana elegida """
  marcaNuevaLinea()

def da_tecla_pulsada ():
  """Devuelve el par de c�digos ASCII de la tecla m�s recientemente pulsada si hay alguna tecla pulsada, o None si no hay ninguna pulsada"""
  return None

def elige_parte (partes, graficos):
  """Obtiene del jugador el modo gr�fico a usar y a qu� parte jugar, y devuelve el nombre de la base de datos elegida"""
  if len (partes) == 1:
    return partes.popitem()[1]
  numerosPartes = tuple (partes.keys())
  numParteMenor = min (numerosPartes)
  numParteMayor = max (numerosPartes)
  entrada = None
  while entrada not in numerosPartes:
    imprime_cadena ('�Qu� parte quieres cargar? (%d%s%d) ' % (numParteMenor, '/' if (numParteMayor - numParteMenor == 1) else '-', numParteMayor))
    try:
      entrada = int (lee_cadena().strip())
    except (KeyboardInterrupt, ValueError) as e:
      if type (e).__name__ != 'ValueError':
        raise
      entrada = None
  return partes[entrada]

def elige_subventana (numero):
  """Selecciona una de las subventanas"""
  global elegida, nuevaLinea
  if numero != elegida:
    elegida    = numero
    nuevaLinea = True

def escribe_buffer ():
  """Escribe a la salida est�ndar todo lo que hay en el buffer y luego lo vac�a"""
  global bufferTexto
  if not bufferTexto:
    return
  if bufferTexto[0] != '\n':
    prn()
  prn (bufferTexto.encode (locale.getpreferredencoding(), 'ignore').decode (locale.getpreferredencoding(), 'ignore'))
  # prn (bufferTexto.encode ('iso-8859-15', 'ignore').decode ('iso-8859-15', 'ignore'), encoding = 'iso-8859-15')
  if bufferTexto[-2:] != '\n\n':
    prn()
  sys.stdout.flush()
  bufferTexto = ''

def espera_tecla (tiempo = 0, numPasos = False):
  """Espera hasta que se pulse una tecla (modificadores no), o hasta que pase tiempo segundos, si tiempo > 0"""
  if NOMBRE_SISTEMA in ('GAC', 'QUILL'):
    marcaNuevaLinea()

def hay_grafico (numero):
  """Devuelve si existe el gr�fico de n�mero dado"""
  return False

def imprime_banderas (banderas):
  """Imprime el contenido de las banderas (en la salida de error est�ndar)"""
  global advertencia_banderas
  try:
    advertencia_banderas
  except:
    advertencia_banderas = True
    prn ('Impresi�n de banderas u objetos como texto (en stderr) no implementada', file = sys.stderr)

def imprime_cadena (cadena, textoNormal = True, redibujar = True, abajo = False, tiempo = 0, restauraColores = False):
  """Imprime una cadena en la posici�n del cursor (dentro de la subventana)"""
  global bufferTexto, nuevaLinea
  if nuevaLinea or bufferTexto[-1:] == '\n':  # Siempre lo pondremos en nuevo p�rrafo
    if bufferTexto[-2:] != '\n\n':
      bufferTexto += '\n\n'
    else:
      bufferTexto += '\n'
  nuevaLinea = False
  cadena = limpiaCadena (cadena)
  if limite[0] == 999:  # Sin l�mite
    if cod_tabulador:
      cadena = cadena.replace (cod_tabulador, '\t')
    bufferTexto += cadena
    return
  # Convertimos las secuencias de control TAB en espacios
  if cod_columna:
    posTabulador = cadena.find (cod_columna)
    while posTabulador > -1:
      numEspacios   = -1
      posTabEnLinea = posTabulador % limite[0]  # Columna en la l�nea donde est� el tabulador
      if len (cadena) > posTabulador + 2:
        columna     = (ord (cadena[posTabulador + 1]) + 1) % limite[0]
        numEspacios = columna - posTabEnLinea  # Rellena con espacios hasta la columna indicada
      cadena = cadena[:posTabulador] + (' ' * (numEspacios if numEspacios > 0 else 0)) + cadena[posTabulador + 2:]
      posTabulador = cadena.find (cod_columna)
  # Convertimos los tabuladores en espacios
  if cod_tabulador:
    mitadAnchura = limite[0] // 2  # Anchura de media l�nea
    posTabulador = cadena.find (cod_tabulador)
    while posTabulador > -1:
      posTabEnLinea = posTabulador % limite[0]  # Columna en la l�nea donde est� el tabulador
      if posTabEnLinea < mitadAnchura:
        numEspacios = mitadAnchura - posTabEnLinea  # Rellena con espacios hasta mitad de l�nea
      else:
        numEspacios = limite[0] - posTabEnLinea  # Rellena el resto de la l�nea con espacios
      cadena       = cadena[:posTabulador] + (' ' * numEspacios) + cadena[posTabulador + 1:]
      posTabulador = cadena.find (cod_tabulador)
  # Dividimos la cadena en l�neas
  lineas = []
  while len (cadena) > limite[0]:
    posPartir = -1
    if '\n' in cadena[:limite[0]]:
      posPartir = cadena.find ('\n')
    elif partir_espacio:
      posPartir = cadena.rfind (' ', 0, limite[0] + 1)
    if posPartir == -1:  # Ning�n car�cter de espacio en la l�nea
      posPartir = limite[0]  # La partimos suciamente (en mitad de palabra)
    lineas.append (cadena[:posPartir])
    if partir_espacio:
      cadena = cadena[posPartir + (1 if cadena[posPartir] in ' \n' else 0):]
    else:
      cadena = cadena[posPartir + (1 if cadena[posPartir] == '\n' else 0):]
  for linea in lineas:
    bufferTexto += linea + '\n'
  if cadena:  # Queda algo en la �ltima l�nea
    bufferTexto += cadena

def lee_cadena (prompt = '', inicio = '', timeout = [0], espaciar = False, pararTimeout = False):
  """Lee una cadena (terminada con Enter) desde el teclado, dando realimentaci�n al jugador

El par�metro prompt, es el mensaje de prompt
El par�metro inicio es la entrada a medias anterior
El par�metro timeout es una lista con el tiempo muerto, en segundos
El par�metro espaciar permite elegir si se debe dejar una l�nea en blanco tras el �ltimo texto
El par�metro pararTimeout indica si se evitar� el tiempo muerto cuando la entrada tenga algo escrito"""
  global nuevaLinea
  entrada = None
  while not entrada:
    if prompt:
      nuevaLinea = True
      imprime_cadena (prompt)
    escribe_buffer()
    entrada = raw_input()
  return entrada

def mueve_cursor (columna, fila = None):
  """Cambia de posici�n el cursor de la subventana elegida"""
  marcaNuevaLinea()

def prepara_topes (columnas, filas):
  """Inicializa los topes al n�mero de columnas y filas dado"""
  limite[0] = columnas  # Ancho m�ximo absoluto de cada subventana


# Funciones auxiliares que s�lo se usan en este m�dulo

def limpiaCadena (cadena):
  for secuencia in secuencias:
    if secuencia in cadena:
      cadena = cadena.replace (secuencia, secuencias[secuencia])
  if not cod_brillo and not cod_juego_alto and not cods_tinta:
    return cadena
  limpia = ''
  c = 0
  while c < len (cadena):
    if cadena[c] in (cod_brillo, cod_flash, cod_inversa, cod_inversa_fin, cod_inversa_ini, cod_juego_alto, cod_juego_bajo, cod_papel, cod_tinta) or \
        cadena[c] in cods_tinta:
      if cadena[c] in (cod_juego_alto, cod_juego_bajo):
        if cod_juego_alto == '@':  # En SWAN los caracteres del juego alto son en negrita
          limpia += '`*`'
      elif cadena[c] not in (cod_inversa_fin, cod_inversa_ini) and cadena[c] not in cods_tinta:
        c += 1  # Descartamos tambi�n el siguiente byte, que indica el color o si se activa o no
    elif centrar_graficos and cadena[c] == '\x7f':  # Abreviatura 0 en la Aventura Original
      limpia += ' '
    else:
      limpia += cadena[c]
    c += 1
  return limpia

def marcaNuevaLinea ():
  """La pr�xima vez que se escriba algo, hacerlo en l�nea nueva"""
  global nuevaLinea
  nuevaLinea = True
