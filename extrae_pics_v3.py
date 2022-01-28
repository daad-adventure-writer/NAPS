#!/usr/bin/env python
# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Extrae gráficos de bases de datos gráficas de DAAD, en el formato de las versiones más recientes de DAAD
# Copyright (C) 2008, 2018-2022 José Manuel Ferrer Ortiz
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

import os
import sys

from bajo_nivel import *
from prn_func   import prn

try:
  import png
except:
  try:
    import pygame.display
    import pygame.image
    prn ('Si quieres guardar las imágenes en formato de paleta indexada (necesario para crea_bd_pics), instala la librería PyPNG')
  except:
    prn ('Se necesita o bien la librería PyPNG (preferiblemente), o la librería pygame')
    sys.exit()


if len (sys.argv) < 3:
  prn ('Uso:', sys.argv[0], 'base_de_datos_imágenes carpeta_destino')
  sys.exit()

try:
  import progressbar
  hayProgreso = True
except:
  hayProgreso = False


bbddimg = sys.argv[1]  # Ruta a base de datos DAAD de imágenes
destino = sys.argv[2]  # Ruta de destino de las imágenes extraídas

# Paletas CGA (1 y 2 con brillo) en el orden necesario
paleta1b = ((0, 0, 0), (85, 255, 255), (255, 85, 255), (254, 255, 255))
paleta2b = ((0, 0, 0), (85, 255,  85), (255, 85,  85), (255, 255,  85))

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

if 'pygame' in sys.modules:
  pygame.display.init()  # Necesario para poner la paleta de la imagen

fichero = open (bbddimg, 'rb')  # Fichero de base de datos DAAD de imágenes
bajo_nivel_cambia_ent (fichero)

longCabeceraImg = 48  # Longitud de la cabecera de imagen

modo = fichero.read (4)
if modo not in ('\x03\x00\x00\x00', '\xff\xff\x00\x00'):
  prn ('El fichero de entrada no es una base de datos de imágenes de DAAD de formato conocido')
  sys.exit()
if modo == '\x03\x00\x00\x00':  # Amiga/Atari ST
  carga_int2 = carga_int2_be
  carga_int4 = carga_int4_be
  le = False
else:
  carga_int2 = carga_int2_le
  carga_int4 = carga_int4_le
  le = True

try:
  os.mkdir (destino)
except:
  pass  # Asumimos que ese directorio ya existe


rango = range (256)  # Recorremos todas las imágenes posibles
if hayProgreso:
  progreso = progressbar.ProgressBar()
  rango    = progreso (range (256))
for numImg in rango:
  fichero.seek (10 + (longCabeceraImg * numImg))  # Parte de cabecera de la imagen
  posicion = carga_int4()
  if not posicion:
    continue  # Ninguna imagen con ese número

  # Obtenemos la paleta de la imagen
  fichero.seek (8, 1)  # El segundo parámetro indica posición relativa
  paleta = []
  for color in range (16):
    # TODO: calcular valores exactos
    rojo  = carga_int1()
    rojo  = (rojo & 7) << 5
    # rojo  = rojo & 4 + ((rojo & 3) << 4)
    veaz  = carga_int1()
    verde = ((veaz >> 4) & 7) << 5
    azul  = (veaz & 7) << 5
    paleta.append ((rojo, verde, azul))

  fichero.seek (posicion)  # Saltamos a donde está la imagen

  if le:
    ancho = carga_int1()  # LSB de la anchura de la imagen
    valor = carga_int1()
  else:
    valor = carga_int1()
    ancho = carga_int1()  # LSB de la anchura de la imagen
  ancho += (valor & 127) * 256
  if ancho == 0 or ancho % 4:
    prn ('El ancho de la imagen', numImg, 'no es mayor que 0 y múltiplo de 4, vale', ancho)
  ancho /= 4  # Anchura de la imagen (en bloques de 4 píxeles)
  rle = valor & 128

  alto = carga_int2()  # Altura de la imagen (en número de filas)
  if alto == 0 or alto % 8:
    prn ('El alto de la imagen', numImg, 'no es mayor que 0 y múltiplo de 8, vale', alto)

  if 0 in (ancho, alto):
    continue

  repetir = []
  fichero.seek (2, 1)  # Saltamos valor de longitud de la imagen
  if rle:
    bits = carga_int2()  # Máscara de colores que se repetirán
    for indiceBit in range (16):
      if bits & (2 ** indiceBit):
        repetir.append (indiceBit)

  strImg  = ''              # Cadena que representa toda la imagen
  tamFila = ancho   * 4     # Tamaño en píxeles (y bytes) que tendrá cada fila
  tamImg  = tamFila * alto  # Tamaño en píxeles (y bytes) que tendrá la imagen

  if le or rle:  # Formato de DOS o comprimido
    cargar  = 1 if le else 4  # Cuántos bytes de valores cargar cada vez, tomando primero el último cargado
    color   = None  # Índice de color del píxel actual
    valores = []    # Valores (índices de color y contador de repeticiones) pendientes de procesar, en orden
    while len (strImg) < tamImg:  # Mientras quede imagen por procesar
      if not valores:
        try:
          for i in range (cargar):
            b = carga_int1()  # Byte actual
            valores = [b & 15, b >> 4] + valores  # Los 4 bits más bajos primero, y luego los 4 más altos
        except:
          prn ('Imagen', numImg, 'incompleta. ¿Formato incorrecto?')
          break
      if color == None:
        color = valores.pop (0)
        continue  # Por si hay que cargar un nuevo byte
      if rle and color in repetir:
        repeticiones = valores.pop (0) + 1
      else:
        repeticiones = 1
      strImg += chr (color) * repeticiones
      color   = None
  else:  # Formato de Amiga/Atari ST sin comprimir
    numPlanos = 4
    while len (strImg) < tamImg:  # Mientras quede imagen por procesar
      colores = ([0] * 8)
      for plano in range (numPlanos):
        b = carga_int1()  # Byte actual
        for indiceBit in range (8):
          bit = b & (2 ** indiceBit)
          colores[7 - indiceBit] += (2 ** plano) if bit else 0
      for pixel in range (8):  # Cada píxel en el grupo
        strImg += chr (colores[pixel])

  bpp = 4

  if 'png' in sys.modules:
    listaImg = []
    for numFila in range (alto):
      listaImg.append (strImg[numFila * ancho * 4 : (numFila + 1) * ancho * 4])
    escritor = png.Writer (ancho * 4, alto, palette = paleta, bitdepth = bpp)
    salida   = open ('%s/pic%03d.png' % (destino, numImg), 'wb')
    escritor.write (salida, listaImg)
  else:
    # OJO: pygame no guarda las imágenes como paleta indexada
    imagen = pygame.image.fromstring (strImg, (ancho * 4, alto), 'P')
    imagen.set_palette (paleta)
    pygame.image.save (imagen, '%s/pic%03d.png' % (destino, numImg))
