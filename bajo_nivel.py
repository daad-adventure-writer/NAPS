# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funciones de apoyo de bajo nivel
# Copyright (C) 2010, 2013, 2018-2022 José Manuel Ferrer Ortiz
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

despl_ini = 0

def bajo_nivel_cambia_despl (desplazamiento):
  """Prepara el desplazamiento inicial para el módulo"""
  global despl_ini
  despl_ini = desplazamiento

def bajo_nivel_cambia_endian (le):
  """Prepara el "endianismo" del módulo"""
  global carga_int2, guarda_int2
  if le:
    carga_int2  = carga_int2_le
    guarda_int2 = guarda_int2_le
  else:
    carga_int2  = carga_int2_be
    guarda_int2 = guarda_int2_be

def bajo_nivel_cambia_ent (fichero):
  """Prepara el módulo para leer del fichero de entrada dado"""
  global fich_ent
  fich_ent = fichero

def bajo_nivel_cambia_sal (fichero):
  """Prepara el módulo para escribir en el fichero de salida dado"""
  global fich_sal
  fich_sal = fichero

def carga_desplazamiento (desplazamiento = None):
  """Carga un desplazamiento (2 bytes) en relación con el fichero

  desplazamiento (opcional) es la posición en el fichero de donde leerá el desplazamiento"""
  if desplazamiento:
    fich_ent.seek (desplazamiento)
  return carga_int2() - despl_ini

def carga_int1 ():
  """Carga un entero de tamaño 1 byte"""
  return ord (fich_ent.read (1))

def carga_int2_be ():
  """Carga un entero de tamaño 2 bytes, en formato Big Endian"""
  return (ord (fich_ent.read (1)) << 8) + ord (fich_ent.read (1))

def carga_int2_le ():
  """Carga un entero de tamaño 2 bytes, en formato Little Endian"""
  return ord (fich_ent.read (1)) + (ord (fich_ent.read (1)) << 8)

def carga_int4_be ():
  """Carga un entero de tamaño 4 bytes, en formato Big Endian"""
  return (ord (fich_ent.read (1)) << 24) + (ord (fich_ent.read (1)) << 16) + (ord (fich_ent.read (1)) << 8) + ord (fich_ent.read (1))

def carga_int4_le ():
  """Carga un entero de tamaño 4 bytes, en formato Little Endian"""
  return ord (fich_ent.read (1)) + (ord (fich_ent.read (1)) << 8) + (ord (fich_ent.read (1)) << 16) + (ord (fich_ent.read (1)) << 24)

def guarda_desplazamiento (entero):
  """Guarda un desplazamiento (2 bytes) en relación con la memoria"""
  guarda_int2 (entero + despl_ini)

def guarda_int1 (entero):
  """Guarda un entero en un byte"""
  fich_sal.write (chr (entero))

def guarda_int2_be (entero):
  """Guarda un entero en dos bytes, en formato Big Endian"""
  fich_sal.write (chr (entero >> 8))
  fich_sal.write (chr (entero & 255))

def guarda_int2_le (entero):
  """Guarda un entero en dos bytes, en formato Little Endian"""
  fich_sal.write (chr (entero & 255))
  fich_sal.write (chr (entero >> 8))
