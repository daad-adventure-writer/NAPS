# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Condactos de The Quill
# Copyright (C) 2010, 2019-2024 José Manuel Ferrer Ortiz
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

import random  # Para randint
import sys
import time    # Para sleep

from prn_func import prn


# Los nombres de las funciones que implementan los condactos son Xn_*, siendo:
# X: 'c' ó 'a', según si son condiciones o acciones, respectivamente
# n: el número de parámetros
# *: el nombre del condacto

# CONDICIONES

def c1_ABSENT (objno):
  """Si el objeto objno no está llevado, ni puesto, ni en la localidad actual"""
  if objno == 255:  # TODO: comprobar si funciona así también en otros sistemas que DAAD
    return True
  aqui = (254, 253, banderas[38])  # Llevado, puesto y localidad actual, respec.
  return locs_objs[objno] not in aqui

def c1_AT (locno):
  """Si el código de la localidad actual es locno"""
  return banderas[38] == locno

def c1_ATGT (locno):
  """Si el código de la localidad actual es mayor que locno"""
  return banderas[38] > locno

def c1_ATLT (locno):
  """Si el código de la localidad actual es menor que locno"""
  return banderas[38] < locno

def c1_CARRIED (objno):
  """Si el objeto objno está llevado"""
  if objno == 255:  # TODO: comprobar si funciona así también en otros sistemas que DAAD
    return False
  return locs_objs[objno] == 254

def c1_CHANCE (percent):
  """Si el número en percent es mayor o igual que otro número al azar entre 1 y 100

La documentación original dice menor o igual, pero es una errata"""
  return percent >= random.randint (1, 100)

def c1_NOTAT (locno):
  """Si el código de la localidad actual es otro distinto al de locno"""
  return banderas[38] != locno

def c1_NOTCARR (objno):
  """Si el objeto objno no está llevado"""
  if objno == 255:  # TODO: comprobar si funciona así también en otros sistemas que DAAD
    return True
  return locs_objs[objno] != 254

def c1_NOTWORN (objno):
  """Si el objeto objno no está puesto"""
  if objno == 255:  # TODO: comprobar si funciona así también en otros sistemas que DAAD
    return True
  return locs_objs[objno] != 253

def c1_NOTZERO (flagno):
  """Si el valor en la bandera flagno es distinto de cero"""
  return banderas[flagno] != 0

def c1_PRESENT (objno):
  """Si el objeto objno está llevado, o puesto, o en la localidad actual"""
  if objno == 255:  # TODO: comprobar si funciona así también en otros sistemas que DAAD
    return False
  aqui = (254, 253, banderas[38])  # Llevado, puesto y localidad actual, respec.
  return locs_objs[objno] in aqui

def c1_WORN (objno):
  """Si el objeto objno está puesto"""
  if objno == 255:  # TODO: comprobar si funciona así también en otros sistemas que DAAD
    return False
  return locs_objs[objno] == 253

def c1_ZERO (flagno):
  """Si el valor en la bandera flagno es igual a cero"""
  return banderas[flagno] == 0


def c2_EQ (flagno, value):
  """Si el valor en la bandera flagno es igual al de value"""
  return banderas[flagno] == value

def c2_GT (flagno, value):
  """Si el valor en la bandera flagno es mayor que el de value"""
  return banderas[flagno] > value

def c2_LT (flagno, value):
  """Si el valor en la bandera flagno es menor que el de value"""
  return banderas[flagno] < value


# ACCIONES

def a0_ANYKEY ():
  """Imprime el mensaje del sistema 16 al final de la pantalla, y espera hasta que se pulse una tecla"""
  subvActual = gui.elige_subventana (3)
  gui.mueve_cursor (0, gui.limite[1] - 2)  # Es en las dos últimas líneas donde se imprime
  gui.imprime_cadena (msgs_sys[16], False)
  gui.espera_tecla()
  gui.mueve_cursor (0, gui.limite[1] - 2)
  gui.borra_pantalla (True)          # Borra el texto escrito
  gui.elige_subventana (subvActual)  # Vuelve a la subventana inicial

def a0_AUTOG ():
  """Busca en la tabla de palabras de los objetos, la segunda palabra de la orden introducida por el jugador. Si se encuentra, ejecuta GET sobre ese objeto. Si no se encuentra ahí, imprime el mensaje de sistema 8 y luego ejecuta DONE"""
  prn ('FIXME: condacto a0_AUTOG no implementado')  # FIXME

def a0_CLS ():
  """Limpia la pantalla a los colores de fondo definidos actualmente, y deja la posición actual de PRINT y de SAVEAT a 0, 0"""
  gui.borra_pantalla()

def a0_DESC ():
  """Termina todo lo que estuviese en ejecución (tablas, bucles DOALL, etc.) y salta a describir la localidad actual"""
  return 1

def a0_DONE ():
  """Concluye la ejecución de la tabla actual, terminando satisfactoriamente"""
  return 3

def a0_END ():
  """Pregunta si se desea volver a empezar (MS13), y si la respuesta empieza por la primera letra del MS31, imprime el MS14 y termina completamente la ejecución de la aventura. Si no, reinicia la aventura"""
  respuesta = gui.lee_cadena (msgs_sys[13] + '>')
  if respuesta[0].lower() == msgs_sys[31].lower():
    gui.imprime_cadena (msgs_sys[14])
    return 7
  return 0

def a0_INVEN ():
  """Primero muestra el MS9. Luego, si no hay objetos llevados ni puestos, muestra el MS11. Si los hay, los lista con su texto completo, cada uno en una línea, y añadiendo el MS10 al final para los objetos puestos. Después ejecuta DONE"""
  gui.imprime_cadena (msgs_sys[9])
  gui.imprime_cadena ('\n')
  alguno = False
  for objno in range (num_objetos[0]):
    if locs_objs[objno] in (253, 254):
      alguno = True
      gui.imprime_cadena (desc_objs[objno])
      if locs_objs[objno] == 253:  # Puesto
        gui.imprime_cadena (msgs_sys[10])
      gui.imprime_cadena ('\n')
  if not alguno:
    gui.imprime_cadena (msgs_sys[11])
  return 3  # Lo mismo que hace DONE

def a0_OK ():
  """Imprime el mensaje de sistema 15 y luego ejecuta DONE"""
  gui.imprime_cadena (msgs_sys[15])
  gui.imprime_cadena ('\n')
  return 3  # Lo mismo que hace DONE

def a0_QUIT ():
  """Pide confirmación (MS12), y si la respuesta empieza por la primera letra del MS30, continúa. Si no, ejecuta DONE"""
  # FIXME: según el manual, no cambia el flujo incondicionalmente
  respuesta = gui.lee_cadena (msgs_sys[12] + '>')
  if respuesta[0].lower() != msgs_sys[30][0].lower():
    return 3  # Lo mismo que hace DONE

def a0_RAMLOAD ():
  """Carga el contenido de las banderas y de las localidades de los objetos desde memoria"""
  if not partida:  # No hay partida guardada en memoria
    return  # TODO: averiguar si imprime algo
  for b in range (NUM_BANDERAS[0]):
    banderas[b] = partida[b]
  for o in range (num_objetos[0]):
    locs_objs[o] = partida[NUM_BANDERAS[0] + o]
  del gui.historial[:]

def a0_RAMSAVE ():
  """Guarda el contenido de las banderas y de las localidades de los objetos a memoria"""
  del partida[:]
  for bandera in banderas:
    partida.append (bandera)
  for loc_obj in locs_objs:
    partida.append (loc_obj)

def a0_SCORE ():
  """Imprime la puntuación, con los mensajes de sistema 21 y 22, y el valor de la bandera 30 (60 en Quill para QL)"""
  banderaPuntos = 30 + (30 if NUM_BANDERAS[0] == 64 else 0)
  gui.imprime_cadena (msgs_sys[21])  # 'Has logrado '
  gui.imprime_cadena (str (banderas[banderaPuntos]))
  gui.imprime_cadena (msgs_sys[22])  # ' puntos.'

def a0_TURNS ():
  """Imprime el número de turnos, con los mensajes de sistema 17 a 20, y el valor de las banderas 31 y 32 (61 y 62 en Quill para QL)"""
  banderaTurnosLSB = 31
  banderaTurnosMSB = 32
  if NUM_BANDERAS[0] == 64:  # Quill para Sinclair QL
    banderaTurnosLSB += 30
    banderaTurnosMSB += 30
  gui.imprime_cadena (msgs_sys[17])  # 'Has jugado '
  turnos = banderas[banderaTurnosLSB] + banderas[banderaTurnosMSB] * 256
  gui.imprime_cadena (str (turnos))
  gui.imprime_cadena (msgs_sys[18])  # ' turno'
  if turnos != 1:
    gui.imprime_cadena (msgs_sys[19])  # 's'
  gui.imprime_cadena (msgs_sys[20])  # '.'


def a1_BORDER (colour):
  """Cambia el color de fondo al borrar la pantalla"""
  gui.cambia_color_borde (colour)

def a1_CLEAR (flagno):
  """Pone el valor de la bandera flagno a 0"""
  banderas[flagno] = 0

def a1_CREATE (objno):
  """Cambia la localidad del objeto objno a la localidad actual, y decrementa el número de objetos llevados si objno se estaba llevando"""
  if locs_objs[objno] == 254:  # Llevado
    banderas[1] = max (0, banderas[1] - 1)
  locs_objs[objno] = banderas[38]

def a1_DESTROY (objno):
  """Cambia la localidad del objeto objno a 252 (no creado), y decrementa el número de objetos llevados si objno se estaba llevando"""
  if locs_objs[objno] == 254:  # Llevado
    banderas[1] = max (0, banderas[1] - 1)
  locs_objs[objno] = 252

def a1_GET (objno):
  """Si el objeto se lleva (inventario o puesto), imprime MS25. Si el objeto no está presente, imprime MS26. Si se superaría el máximo de objetos llevables, imprime MS27. En caso de una de estas condiciones de fallo, termina con DONE. En caso contrario (éxito), mueve el objeto al inventario (254) e incrementa la bandera 1"""
  if locs_objs[objno] in (253, 254):
    gui.imprime_cadena (msgs_sys[25])
  elif locs_objs[objno] != banderas[38]:
    gui.imprime_cadena (msgs_sys[26])
  elif banderas[1] >= banderas[37]:
    gui.imprime_cadena (msgs_sys[27])
  else:
    banderas[1] += 1
    locs_objs[objno] = 254
    return
  return 3  # Lo mismo que hace DONE

def a1_GOTO (locno):
  """Cambia la localidad actual al número dado por locno"""
  banderas[38] = locno

def a1_INK (colour):
  """Cambia el color de la letra al imprimir texto"""
  gui.cambia_color_tinta (colour)

def a1_MESSAGE (mesno):
  """Imprime el mensaje de usuario dado por mesno, en los colores actuales, y luego ejecuta una acción NEWLINE"""
  imprime_mensaje (msgs_usr[mesno])
  gui.imprime_cadena ('\n')

def a1_PAPER (colour):
  """Cambia el color de fondo/papel al imprimir texto"""
  gui.cambia_color_papel (colour)

def a1_PAUSE (value):
  """Pausa por un tiempo de value/50 segundos

Si el valor es cero, la pausa es de 256/50 segundos
El teclado se desconecta durante la duración de una pausa"""
  if value == 0:
    value = 256
  time.sleep (value / 50.)
  gui.redimensiona_ventana()  # Da la oportunidad de manejar eventos de redimensión de ventana

def a1_REMOVE (objno):
  """Si el objeto no está puesto, imprime MS32. Si se superaría el máximo de objetos llevables, imprime MS24. En caso de una de estas condiciones de fallo, termina con DONE. En caso contrario (éxito), mueve el objeto al inventario (254), e incrementa la bandera 1"""
  if locs_objs[objno] != 253:
    imprime_mensaje (msgs_sys[32])
  elif banderas[1] >= banderas[37]:
    imprime_mensaje (msgs_sys[24])
  else:
    banderas[1]      = min (banderas[1] + 1, 255)
    locs_objs[objno] = 254
    return
  return a0_DONE()

def a1_SET (flagno):
  """Pone el valor de la bandera flagno a 255"""
  banderas[flagno] = 255

def a1_WEAR (objno):
  """Si el objeto está puesto, imprime MS29. Si el objeto no se lleva, imprime MS28. En caso de una de estas condiciones de fallo, termina con DONE. En caso contrario (éxito), mueve el objeto a puestos (253), y decrementa la bandera 1"""
  if locs_objs[objno] == 253:
    imprime_mensaje (msgs_sys[29])
  elif locs_objs[objno] != 254:
    imprime_mensaje (msgs_sys[28])
  else:
    banderas[1]      = max (0, banderas[1] - 1)
    locs_objs[objno] = 253
    return
  return a0_DONE()


def a2_BEEP (duration, pitch):
  """Emite un pitido"""
  prn ('a2_BEEP no implementado', file = sys.stderr)

def a2_LET (flagno, value):
  """Pone el valor de la bandera flagno a value"""
  banderas[flagno] = value

def a2_MINUS (flagno, value):
  """El valor de la bandera flagno se decrementa por el número value

Si el resultado es negativo, la bandera se deja a 0"""
  banderas[flagno] -= value
  if banderas[flagno] < 0:
    banderas[flagno] = 0

def a2_PLUS (flagno, value):
  """Le añade a la bandera flagno el número que se ponga en value

Si el resultado excede de 255, la bandera se pone a 255"""
  banderas[flagno] += value
  if banderas[flagno] > 255:
    banderas[flagno] = 255

def a2_SWAP (objno1, objno2):
  """Se intercambian las localidades del objeto objno1 y objno2, y se marca objno2 como objeto actualmente referido"""
  for objno in (objno1, objno2):
    if locs_objs[objno] in (253, 254):  # Llevado o puesto
      peso_llevado[0] -= min (peso_llevado[0], da_peso (objno))
  locno = locs_objs[objno1]
  locs_objs[objno1] = locs_objs[objno2]
  locs_objs[objno2] = locno
  obj_referido (objno2)
  for objno in (objno1, objno2):
    if locs_objs[objno] in (253, 254):  # Llevado o puesto
      peso_llevado[0] += da_peso (objno)
