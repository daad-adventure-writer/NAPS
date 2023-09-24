# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Condactos específicos de SWAN
# Copyright (C) 2020-2023 José Manuel Ferrer Ortiz
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

import os
import struct
import sys


# Los nombres de las funciones que implementan los condactos son Xn_*, siendo:
# X: 'c' ó 'a', según si son condiciones o acciones, respectivamente
# n: el número de parámetros
# *: el nombre del condacto


# CONDICIONES

def c2_BSET (flagno, value):
  return banderas[flagno] & value != 0

def c2_NOTBSET (flagno, value):
  return banderas[flagno] & value == 0

def c2_OAT (objno, flagno):
  # TODO: verificar probando si esta implementación es correcta
  # XXX: creo que este condacto no se usa en ninguna parte de Mind Fighter, al menos de la versión PC que tengo
  return busca_condacto ('c2_ISAT') (objno, banderas[flagno])


# ACCIONES

def a0_ANYKEY ():
  """Imprime el mensaje del sistema 16 y se espera hasta que se pulse una tecla, o hasta que haya pasado el tiempo muerto, si se ha usado tiempo muerto"""
  gui.imprime_cadena (msgs_sys[16])
  gui.espera_tecla (banderas[48] if banderas[49] & 4 else 0)

def a0_COMMAND ():
  """Obtiene e interpreta la orden del jugador para rellenar la sentencia lógica actual, y salta a procesar la tabla de respuestas"""
  parsea_orden (0, mensajesInvalida = False)
  return 8

def a0_DESC ():
  """Termina todo lo que estuviese en ejecución (tablas, bucles DOALL, etc.) y salta a describir la localidad actual"""
  gui.imprime_cadena ('\n', tiempo = banderas[48] if banderas[49] & 2 else 0)
  return 1

def a0_OOPSAVE ():
  prn ('TODO: a0_OOPSAVE no implementado', file = sys.stderr)  # TODO

def a0_SAVE ():
  """Guarda el contenido de las banderas y de las localidades de los objetos a un fichero"""
  nombreFich = gui.lee_cadena (msgs_sys[60] + msgs_sys[33])
  invalido   = False
  if compatibilidad:  # Recortamos el nombre del fichero a 8 caracteres como máximo
    nombreFich = nombreFich[:8]
  for caracter in nombreFich:
    if not caracter.isalnum():
      invalido = True
      break
  if invalido:
    imprime_mensaje (msgs_sys[59])  # Nombre de fichero inválido
  else:
    try:
      fichero = open (os.path.join (os.path.dirname (ruta_bbdd), nombreFich + '.' + EXT_SAVEGAME), 'wb')
      for bandera in banderas:
        fichero.write (struct.pack ('B', bandera))
      for loc_obj in locs_objs:
        fichero.write (struct.pack ('B', loc_obj))
      fichero.write (struct.pack ('B', 255))  # Marca de fin de localidades de objetos
      for i in range (len (locs_objs), 256 - 2):  # El resto de bytes los ocupamos con 0
        fichero.write (struct.pack ('B', 0))
      fichero.write (struct.pack ('B', len (locs_objs)))  # Número de objetos
    except:
      imprime_mensaje (msgs_sys[56])  # Error I/O
  parsea_orden (0)
  return 8  # Salta a procesar la tabla de respuestas


def a1_FMES (flagno):
  # TODO: verificar probando si esta implementación es correcta
  mesno = banderas[flagno]
  if mesno >= len (msgs_usr):
    prn ('ERROR PAW: Llamada a FMES con número de mensaje de usuario inexistente:', mesno)
    return
  busca_condacto ('a1_MES') (mesno)

def a1_OVERLAY (partno):
  """Carga la parte dada como parámetro y reinicia la ejecución"""
  msgError = libreria.carga_parte (partno)
  if msgError:
    imprime_mensaje (msgError)
  prepara_vocabulario()
  return busca_condacto ('a0_DONE') ()  # Termina la ejecución de la tabla actual (evidentemente necesario, al haberse cargado otra base de datos)


def a2_CLEARB (flagno, value):
  banderas[flagno] -= banderas[flagno] & value

def a2_FGET (flagno1, flagno2):
  # TODO: verificar probando si esta implementación es correcta
  if flagno2 == 38 or banderas[banderas[flagno1]] >= len (desc_locs):  # TODO: lo correcto es comprobar número de localidades directamente
    prn ('ERROR PAW: Llamada a FGET con número de localidad inexistente')
    return
  banderas[flagno2] = banderas[banderas[flagno1]]

def a2_FPUT (flagno1, flagno2):
  # TODO: verificar probando si esta implementación es correcta
  if flagno2 == 38 or banderas[flagno1] >= len (desc_locs):  # TODO: lo correcto es comprobar número de localidades directamente
    prn ('ERROR PAW: Llamada a FGET con número de localidad inexistente')
    return
  banderas[banderas[flagno2]] = banderas[flagno1]

def a2_SETB (flagno, value):
  banderas[flagno] |= value
