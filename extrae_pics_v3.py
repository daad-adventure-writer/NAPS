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

from prn_func import prn

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
paleta1b = ((0, 0, 0), (84, 254, 254), (254, 84, 254), (254, 254, 254))
paleta2b = ((0, 0, 0), (84, 254, 84),  (254, 84, 84),  (254, 254, 84))

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

if 'pygame' in sys.modules:
  pygame.display.init()  # Necesario para poner la paleta de la imagen

fichero = open (bbddimg, 'rb')  # Fichero de base de datos DAAD de imágenes

longCabeceraImg = 48  # Longitud de la cabecera de imagen

if fichero.read (4) != '\xff\xff\x00\x00':
  prn ('El fichero de entrada no es una base de datos de imágenes de DAAD de formato conocido')
  sys.exit()

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
  posicion = ord (fichero.read (1)) + (ord (fichero.read (1)) << 8) + \
             (ord (fichero.read (1)) << 16)  # La posición toma 4 bytes, pero basta con 3

  if not posicion:
    continue  # Ninguna imagen con ese número

  # Obtenemos la paleta de la imagen
  fichero.seek (9, 1)  # El segundo parámetro indica posición relativa
  paleta = []
  for color in range (16):
    # TODO: calcular valores exactos
    rojo  = ord (fichero.read (1))
    rojo  = (rojo & 7) << 5
    # rojo  = rojo & 4 + ((rojo & 3) << 4)
    veaz  = ord (fichero.read (1))
    verde = ((veaz >> 4) & 7) << 5
    azul  = (veaz & 7) << 5
    paleta.append ((rojo, verde, azul))

  fichero.seek (posicion)  # Saltamos a donde está la imagen

  ancho = ord (fichero.read (1))  # LSB de la anchura de la imagen
  valor = ord (fichero.read (1))
  ancho += (valor & 127) * 256
  if ancho == 0 or ancho % 4:
    prn ('El ancho de la imagen', numImg, 'no es mayor que 0 y múltiplo de 4, vale', ancho)
  ancho /= 4  # Anchura de la imagen (en bloques de 4 píxeles)
  rle = valor & 128

  alto = ord (fichero.read (1))  # Altura de la imagen (en número de filas)
  fichero.read (1)
  if alto == 0 or alto % 8:
    prn ('El alto de la imagen', numImg, 'no es mayor que 0 y múltiplo de 8, vale', alto)

  if 0 in (ancho, alto):
    continue

  repetir = []
  fichero.seek (2, 1)  # Saltamos valor de longitud de la imagen
  if rle:
    bits = ord (fichero.read (1)) + (ord (fichero.read (1)) * 256)  # Máscara de colores que se repetirán
    for indiceBit in range (16):
      if bits & (2 ** indiceBit):
        repetir.append (indiceBit)

  strImg  = ''              # Cadena que representa toda la imagen
  tamFila = ancho   * 4     # Tamaño en píxeles (y bytes) que tendrá cada fila
  tamImg  = tamFila * alto  # Tamaño en píxeles (y bytes) que tendrá la imagen

  color   = None  # Índice de color del píxel actual
  valores = []    # Valores (índices de color y contador de repeticiones) pendientes de procesar, en orden
  while len (strImg) < tamImg:  # Mientras quede imagen por procesar
    if not valores:
      try:
        b = ord (fichero.read (1))  # Byte actual
      except:
        prn ('Imagen', numImg, 'incompleta. ¿Formato incorrecto?')
        break
      valores.extend ((b & 15, b >> 4))  # Los 4 bits más bajos primero, y luego los 4 más altos
    if color == None:
      color = valores.pop (0)
      continue  # Por si hay que cargar un nuevo byte
    if rle and color in repetir:
      repeticiones = valores.pop (0) + 1
    else:
      repeticiones = 1
    strImg += chr (color) * repeticiones
    color   = None

  bpp = 4

  if 'png' in sys.modules:
    listaImg = []
    for numFila in range (alto):
      listaImg.append (strImg[numFila * ancho * 4 : (numFila + 1) * ancho * 4])
    escritor = png.Writer (ancho * 4, alto, palette = paleta, bitdepth = bpp)
    salida   = open ('%s/pic%03d.png' % (destino, numImg), 'wb')
    escritor.write(salida, listaImg)
  else:
    # OJO: pygame no guarda las imágenes como paleta indexada
    imagen = pygame.image.fromstring (strImg, (ancho * 4, alto), 'P')
    imagen.set_palette (paleta)
    pygame.image.save (imagen, '%s/pic%03d.png' % (destino, numImg))
