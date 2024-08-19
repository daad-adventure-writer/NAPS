# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funciones de apoyo de bajo nivel
# Copyright (C) 2010, 2013, 2018-2024 José Manuel Ferrer Ortiz
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

import os  # Para SEEK_END

from sys import version_info

if version_info[0] == 3 and version_info[1] >= 5:  # Para Python 3.5+
  from typing import *  # Para que PyCharm reconozca BinaryIO

despl_ini = 0

def bajo_nivel_cambia_despl (desplazamiento):
  # type: (int) -> None
  """Prepara el desplazamiento inicial para el módulo"""
  global despl_ini
  despl_ini = desplazamiento

def bajo_nivel_cambia_endian (le):
  # type: (bool) -> None
  """Prepara el "endianismo" del módulo"""
  global carga_int2, carga_int4, guarda_int2, guarda_int4
  if le:
    carga_int2  = carga_int2_le
    carga_int4  = carga_int4_le
    guarda_int2 = guarda_int2_le
    guarda_int4 = guarda_int4_le
  else:
    carga_int2  = carga_int2_be
    carga_int4  = carga_int4_be
    guarda_int2 = guarda_int2_be
    guarda_int4 = guarda_int4_be

def bajo_nivel_cambia_ent (fichero):
  # type: (BinaryIO) -> None
  """Prepara el módulo para leer del fichero de entrada dado"""
  global fich_ent
  fich_ent = fichero

def bajo_nivel_cambia_sal (fichero):
  # type: (BinaryIO) -> None
  """Prepara el módulo para escribir en el fichero de salida dado"""
  global fich_sal
  fich_sal = fichero

def busca_secuencia (secuencia, posInicio = 0):
  # type: (Sequence[Optional[int]], Optional[int]) -> Optional[int]
  """Busca la secuencia de valores de byte dada y devuelve la posición donde se quedó al encontrarla o None si no se encontró

  secuencia es la lista de valores de byte a buscar. Puede incluir valores None para posiciones que siempre encajarán
  posInicio es el índice donde se empezará a buscar"""
  fich_ent.seek (0, os.SEEK_END)
  longitud = fich_ent.tell()
  if posInicio >= longitud:
    return
  posicion = posInicio
  fich_ent.seek (posicion)
  encajeSec = []  # Secuencia de encajes hasta ahora
  c = carga_int1()
  while True:
    if secuencia[len (encajeSec)] is None or c == secuencia[len (encajeSec)]:
      encajeSec.append (c)
      if len (encajeSec) == len (secuencia):  # Secuencia encontrada
        return posicion
    elif encajeSec:
      del encajeSec[:]
      continue  # Empezamos de nuevo desde este carácter
    if posicion + 1 == longitud:
      return  # No se ha encontrado
    c = carga_int1()
    posicion += 1

def carga_desplazamiento2 (desplazamiento = None):
  # type: (int) -> int
  """Carga un desplazamiento de 2 bytes en relación con el fichero

  desplazamiento (opcional) es la posición en el fichero de donde leerá el desplazamiento"""
  muevePosicion (desplazamiento)
  return carga_int2() - despl_ini

def carga_desplazamiento4 (desplazamiento = None):
  # type: (int) -> int
  """Carga un desplazamiento de 4 bytes en relación con el fichero

  desplazamiento (opcional) es la posición en el fichero de donde leerá el desplazamiento"""
  muevePosicion (desplazamiento)
  return carga_int4() - despl_ini

def carga_int1 (desplazamiento = None):
  # type: (int) -> int
  """Carga un entero de tamaño 1 byte

  desplazamiento (opcional) es la posición en el fichero de donde leerá el desplazamiento"""
  muevePosicion (desplazamiento)
  return ord (fich_ent.read (1))

def carga_int2_be ():
  # type: () -> int
  """Carga un entero de tamaño 2 bytes, en formato Big Endian"""
  return (ord (fich_ent.read (1)) << 8) + ord (fich_ent.read (1))

def carga_int2_le ():
  # type: () -> int
  """Carga un entero de tamaño 2 bytes, en formato Little Endian"""
  return ord (fich_ent.read (1)) + (ord (fich_ent.read (1)) << 8)

def carga_int4_be ():
  # type: () -> int
  """Carga un entero de tamaño 4 bytes, en formato Big Endian"""
  return (ord (fich_ent.read (1)) << 24) + (ord (fich_ent.read (1)) << 16) + (ord (fich_ent.read (1)) << 8) + ord (fich_ent.read (1))

def carga_int4_le ():
  # type: () -> int
  """Carga un entero de tamaño 4 bytes, en formato Little Endian"""
  return ord (fich_ent.read (1)) + (ord (fich_ent.read (1)) << 8) + (ord (fich_ent.read (1)) << 16) + (ord (fich_ent.read (1)) << 24)

def guarda_desplazamiento2 (entero):
  # type: (int) -> None
  """Guarda un desplazamiento (2 bytes) en relación con la memoria"""
  guarda_int2 (entero + despl_ini)

def guarda_desplazamiento4 (entero):
  """Guarda un desplazamiento (4 bytes) en relación con la memoria"""
  # type: (int) -> None
  guarda_int4 (entero + despl_ini)

if version_info[0] < 3:  # Para Python 2
  def guarda_int1 (entero):
    # type: (int) -> None
    """Guarda un entero en un byte"""
    fich_sal.write (chr (entero))

  def guarda_int2_be (entero):
    # type: (int) -> None
    """Guarda un entero en dos bytes, en formato Big Endian"""
    fich_sal.write (chr (entero >> 8))
    fich_sal.write (chr (entero & 255))

  def guarda_int2_le (entero):
    # type: (int) -> None
    """Guarda un entero en dos bytes, en formato Little Endian"""
    fich_sal.write (chr (entero & 255))
    fich_sal.write (chr (entero >> 8))

  def guarda_int4_be (entero):
    # type: (int) -> None
    """Guarda un entero en cuatro bytes, en formato Big Endian"""
    fich_sal.write (chr (entero >> 24))
    fich_sal.write (chr ((entero >> 16) & 255))
    fich_sal.write (chr ((entero >> 8) & 255))
    fich_sal.write (chr (entero & 255))

  def guarda_int4_le (entero):
    # type: (int) -> None
    """Guarda un entero en cuatro bytes, en formato Little Endian"""
    fich_sal.write (chr (entero & 255))
    fich_sal.write (chr ((entero >> 8) & 255))
    fich_sal.write (chr ((entero >> 16) & 255))
    fich_sal.write (chr (entero >> 24))
else:  # Para Python 3
  def guarda_int1 (entero):
    # type: (int) -> None
    """Guarda un entero en un byte"""
    fich_sal.write (bytes ([entero]))

  def guarda_int2_be (entero):
    # type: (int) -> None
    """Guarda un entero en dos bytes, en formato Big Endian"""
    fich_sal.write (bytes ([entero >> 8, entero & 255]))

  def guarda_int2_le (entero):
    # type: (int) -> None
    """Guarda un entero en dos bytes, en formato Little Endian"""
    fich_sal.write (bytes ([entero & 255, entero >> 8]))

  def guarda_int4_be (entero):
    # type: (int) -> None
    """Guarda un entero en cuatro bytes, en formato Big Endian"""
    fich_sal.write (bytes ([entero >> 24, (entero >> 16) & 255, (entero >> 8) & 255, entero & 255]))

  def guarda_int4_le (entero):
    # type: (int) -> None
    """Guarda un entero en cuatro bytes, en formato Little Endian"""
    fich_sal.write (bytes ([entero & 255, (entero >> 8) & 255, (entero >> 16) & 255, entero >> 24]))


# Funciones auxiliares que sólo se usan en este módulo

def muevePosicion (desplazamiento):
  # type: (int) -> None
  if desplazamiento != None:
    fich_ent.seek (desplazamiento)
