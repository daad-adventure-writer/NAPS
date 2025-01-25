# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Condactos de Graphic Adventure Creator (GAC)
# Copyright (C) 2025 José Manuel Ferrer Ortiz
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

from prn_func import prn


# Funciones auxiliares


# Los nombres de las funciones que implementan los condactos son Xn_*, siendo:
# X: 'c' ó 'a', según si son condiciones o acciones, respectivamente
# n: el número de parámetros
# *: el nombre del condacto

# CONDICIONES

def c0_IF ():
  # type: () -> bool
  """Termina la entrada actual si el último valor en la pila de datos evalúa como falso"""
  return True if pila_datos.pop() else False


# ACCIONES

def a0_AND ():
  """Comprueba si el último y el penúltimo valor de la pila de datos evalúan como verdadero, y añade el resultado de la condición a la pila"""
  valor1 = pila_datos.pop()
  valor2 = pila_datos.pop()
  pila_datos.append (1 if valor1 and valor2 else 0)

def a0_AT ():
  """Comprueba si el valor de la localidad actual del jugador equivale al último valor en la pila de datos, y añade el resultado de la condición a la pila"""
  pila_datos.append (1 if pila_datos.pop() == banderas[BANDERA_LOC_ACTUAL] else 0)

def a0_CARR ():
  """Comprueba si el jugador lleva el objeto cuyo número está en el último valor de la pila, y añade el resultado de la condición a la pila"""
  numObjeto = pila_datos.pop()
  if numObjeto > len (locs_objs):
    pila_datos.append (0)
    return
  pila_datos.append (1 if locs_objs[numObjeto] == 32767 else 0)

def a0_CTR ():
  """Añade a la pila de datos el valor de la bandera (contador en terminología de GAC) cuyo número está en el tope de la pila de datos"""
  numBandera = pila_datos.pop()
  valor      = 0 if numBandera > NUM_BANDERAS_ACC else banderas[numBandera]
  pila_datos.append (valor)

def a0_DECR ():
  """Decrementa en uno la bandera cuyo número está en el tope de la pila de datos

Si el resultado es negativo, la bandera se deja a 0"""
  numBandera = pila_datos.pop()
  if numBandera > NUM_BANDERAS_ACC:
    return
  banderas[numBandera] -= 1
  if banderas[numBandera] < 0:
    banderas[numBandera] = 0

def a0_DROP ():
  """Intenta dejar el objeto cuyo número está en el último valor de la pila, mostrando los mensajes adecuados si no se puede"""
  numObjeto = pila_datos.pop()
  if numObjeto > len (locs_objs):
    return
  # TODO: ver si hay más condiciones
  if locs_objs[numObjeto] == 32767:  # El objeto se tenía
    libreria.accion_okay[0] = True
    locs_objs[numObjeto] = banderas[BANDERA_LOC_ACTUAL]
  else:  # El objeto no se tenía
    gui.imprime_cadena (msgs_sys[246])
    libreria.accion_okay[0] = False

def a0_EQ ():
  """Comprueba si el último valor de la pila de datos es igual que el penúltimo valor en la pila, y añade el resultado de la condición a la pila"""
  valor1 = pila_datos.pop()
  valor2 = pila_datos.pop()
  pila_datos.append (1 if valor1 == valor2 else 0)

def a0_EQU_ ():
  """Comprueba si el valor de la bandera cuyo número está en el último valor de la pila de datos equivale al penúltimo valor en la pila, y añade el resultado de la condición a la pila"""
  numBandera = pila_datos.pop()
  valor      = pila_datos.pop()
  if numBandera > NUM_BANDERAS_ACC:
    pila_datos.append (0)
    return
  pila_datos.append (1 if banderas[numBandera] == valor else 0)

def a0_EXIT ():
  """Reinicia el juego sin preguntar, pero pidiendo tecla"""
  gui.imprime_cadena (msgs_sys[243])
  gui.espera_tecla()
  return 0

def a0_GET ():
  """Intenta coger el objeto cuyo número está en el último valor de la pila, mostrando los mensajes adecuados si no se puede"""
  numObjeto = pila_datos.pop()
  if numObjeto > len (locs_objs):
    return
  # TODO: ver si hay más condiciones
  if locs_objs[numObjeto] == banderas[BANDERA_LOC_ACTUAL]:
    libreria.accion_okay[0] = True
    locs_objs[numObjeto] = 32767  # Localidad de los objetos llevados
  else:
    libreria.accion_okay[0] = False
    if locs_objs[numObjeto] == 32767:  # El objeto ya se tenía
      gui.imprime_cadena (msgs_sys[245])
    else:  # El objeto no está presente
      gui.imprime_cadena (msgs_sys[247])

def a0_GOTO ():
  """Mueve el jugador a la localidad cuyo número está en el tope de la pila de datos y salta a describir la localidad"""
  banderas[BANDERA_LOC_ACTUAL] = pila_datos.pop()
  return 1

def a0_GT ():
  """Comprueba si el penúltimo valor de la pila de datos es mayor que el último valor en la pila, y añade el resultado de la condición a la pila"""
  valor1 = pila_datos.pop()
  valor2 = pila_datos.pop()
  pila_datos.append (1 if valor2 > valor1 else 0)

def a0_HOLD ():
  """Pausa por un tiempo de v/50 segundos o hasta que se pulse una tecla, siendo v el valor en la pila de datos"""
  gui.espera_tecla (pila_datos.pop() / 50.)

def a0_INCR ():
  """Incrementa en uno la bandera cuyo número está en el tope de la pila de datos

Si el resultado excede 255, la bandera se pone a 255"""
  numBandera = pila_datos.pop()
  if numBandera > NUM_BANDERAS_ACC:
    return
  banderas[numBandera] += 1
  if banderas[numBandera] > 255:
    banderas[numBandera] = 255

def a0_LF ():
  """Imprime una nueva línea"""
  gui.imprime_cadena ('\n')

def a0_LIST (texto = ''):
  # type: (Optional[str]) -> None
  """Lista los objetos presentes en la localidad cuyo número está en el tope de la pila de datos"""
  numLocalidad = pila_datos.pop()
  alguno = False  # Si se ha listado ya algún objeto
  for numObjeto in desc_objs:
    if locs_objs[numObjeto] == numLocalidad:
      if alguno:
        texto = ','
      else:
        alguno = True
      texto += desc_objs[numObjeto]
      gui.imprime_cadena (texto)
  if not alguno and not texto:
    gui.imprime_cadena ('nothing')

def a0_LOOK ():
  """Describe la localidad actual"""
  return 1

def a0_LT ():
  """Comprueba si el penúltimo valor de la pila de datos es menor que el último valor en la pila, y añade el resultado de la condición a la pila"""
  valor1 = pila_datos.pop()
  valor2 = pila_datos.pop()
  pila_datos.append (1 if valor2 < valor1 else 0)

def a0_MESS ():
  """Imprime el mensaje cuyo número está en el tope de la pila de datos"""
  numMensaje = pila_datos.pop()
  if numMensaje not in msgs_sys:
    return
  gui.imprime_cadena (msgs_sys[numMensaje])

def a0_NO1 ():
  """Añade a la pila de datos el primer nombre de la SL actual"""
  pila_datos.append (banderas[BANDERA_NOMBRE])

def a0_NO2 ():
  """Añade a la pila de datos el segundo nombre de la SL actual"""
  pila_datos.append (banderas[BANDERA_NOMBRE2])

def a0_NOT ():
  """Niega el último valor de la pila de datos"""
  valor = pila_datos.pop()
  pila_datos.append (0 if valor else 1)

def a0_NOUN ():
  """Comprueba si el primer nombre de la SL actual equivale al valor del tope de la pila, y añade el resultado de la condición a la pila"""
  pila_datos.append (1 if banderas[BANDERA_NOMBRE] == pila_datos.pop() else 0)

def a0_OKAY ():
  """Imprime el mensaje de 'Okay' y pasa a pedir orden del jugador"""
  if libreria.accion_okay[0]:
    gui.imprime_cadena (msgs_sys[254])
  return 9

def a0_OR ():
  """Comprueba si el último o el penúltimo valor de la pila de datos evalúa como verdadero, y añade el resultado de la condición a la pila"""
  valor1 = pila_datos.pop()
  valor2 = pila_datos.pop()
  pila_datos.append (1 if valor1 or valor2 else 0)

def a0_PRIN ():
  """Imprime el número que está en el tope de la pila de datos"""
  valor = pila_datos.pop()
  gui.imprime_cadena (str (valor))

def a0_RESE ():
  """Pone a falso el marcador cuyo número está en el tope de la pila de datos"""
  numMarcador = pila_datos.pop()
  if numMarcador > NUM_MARCADORES:
    return
  marcadores[numMarcador] = 0

def a0_RES_ ():
  """Comprueba si el marcador cuyo número está en el tope de la pila de datos vale falso, y añade el resultado de la condición a la pila"""
  numMarcador = pila_datos.pop()
  if numMarcador > NUM_MARCADORES:
    pila_datos.append (0)
    return
  pila_datos.append (0 if marcadores[numMarcador] else 1)

def a0_ROOM ():
  """Añade a la pila de datos el valor de la localidad actual"""
  pila_datos.append (banderas[BANDERA_LOC_ACTUAL])

def a0_SET ():
  """Pone a verdadero el marcador cuyo número está en el tope de la pila de datos"""
  numMarcador = pila_datos.pop()
  if numMarcador > NUM_MARCADORES:
    return
  marcadores[numMarcador] = 1

def a0_SET_ ():
  """Comprueba si el marcador cuyo número está en el tope de la pila de datos vale verdadero, y añade el resultado de la condición a la pila"""
  numMarcador = pila_datos.pop()
  if numMarcador > NUM_MARCADORES:
    pila_datos.append (0)
    return
  pila_datos.append (1 if marcadores[numMarcador] else 0)

def a0_STRE ():
  """Asigna el peso máximo llevable por el jugador"""
  peso_llevable[0] = pila_datos.pop()

def a0_TO ():
  """Mueve a la localidad cuyo número está en el último valor de la pila, el objeto cuyo número está en el penúltimo valor de la pila"""
  locDestino = pila_datos.pop()
  locs_objs[pila_datos.pop()] = locDestino

def a0_VBNO ():
  """Añade a la pila de datos el verbo de la SL actual"""
  pila_datos.append (banderas[BANDERA_VERBO])

def a0_VERB ():
  """Comprueba si el verbo de la SL actual equivale al valor del tope de la pila, y añade el resultado de la condición a la pila"""
  pila_datos.append (1 if banderas[BANDERA_VERBO] == pila_datos.pop() else 0)

def a0_WAIT ():
  """Pasa a pedir orden del jugador"""
  return 9

def a0_WITH ():
  """Añade a la pila de datos el número de la localidad de los objetos llevados"""
  pila_datos.append (32767)

def a1_PUSH (valor):
  # type: (int) -> None
  """Añade a la pila de datos el valor dado como parámetro"""
  pila_datos.append (valor)
