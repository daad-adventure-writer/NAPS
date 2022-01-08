#!/usr/bin/env python
# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Extrae gráficos de bases de datos gráficas de DAAD, en el formato de las primeras versiones de DAAD
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


bbddimg = sys.argv[1]  # Ruta a base de datos DAAD de imágenes CGA/EGA/PCW
destino = sys.argv[2]  # Ruta de destino de las imágenes extraídas
# ancho   = 64           # Anchura de la imagen (en bloques de 4 píxeles)

# Paletas CGA (1 y 2 con brillo) en el orden necesario
paleta1b = ((0, 0, 0), (84, 254, 254), (254, 84, 254), (254, 254, 254))
paleta2b = ((0, 0, 0), (84, 254, 84),  (254, 84, 84),  (254, 254, 84))

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

# Paleta PCW en el orden necesario, negro y verde
paletaPCW = ((0, 0, 0), (0, 255, 0))

if 'pygame' in sys.modules:
  pygame.display.init()  # Necesario para poner la paleta de la imagen

fichero   = open (bbddimg, 'rb')  # Fichero de base de datos DAAD de imágenes CGA/EGA
extension = bbddimg[-4:].lower()

le              = True  # Si es Little Endian
longCabeceraImg = 10    # Longitud de la cabecera de imagen

fichero.seek (2)
modo = ord (fichero.read (1))
if modo == 4:
  if extension in ('.dat', '.pcw'):
    bpp  = 1
    modo = 'PCW'
  else:
    bpp  = 2
    modo = 'CGA'
elif modo == 13:
  bpp  = 4
  modo = 'EGA'
elif modo == 0 and extension == '.dat':
  bpp  = 4
  le   = False
  modo = 'ST'
  longCabeceraImg = 44
else:
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
  fichero.seek (6 + (longCabeceraImg * numImg))  # Parte de cabecera de la imagen
  if le:
    posicion = ord (fichero.read (1)) + (ord (fichero.read (1)) << 8) + \
               (ord (fichero.read (1)) << 16)
    # La posición toma 4 bytes, pero basta con 3
    fichero.seek (1, 1)  # El segundo parámetro indica posición relativa
  else:
    fichero.read (1)  # Omitimos el MSB
    posicion = (ord (fichero.read (1)) << 16) + (ord (fichero.read (1)) << 8) + \
               ord (fichero.read (1))

  if not posicion:
    continue  # Ninguna imagen con ese número

  # Obtenemos la paleta de la imagen
  if modo == 'CGA':
    if ord (fichero.read (1)) & 128:
      paleta = paleta1b
    else:
      paleta = paleta2b
  elif modo == 'ST':
    fichero.seek (8, 1)
    paleta = []
    for color in range (16):
      # TODO: calcular valores correctos
      rojo  = ord (fichero.read (1))
      rojo  = (rojo & 7) << 5
      # rojo  = rojo & 4 + ((rojo & 3) << 4)
      veaz  = ord (fichero.read (1))
      verde = ((veaz >> 4) & 7) << 5
      azul  = (veaz & 7) << 5
      paleta.append ((rojo, verde, azul))
  elif modo == 'PCW':
    paleta = paletaPCW
  else:
    paleta = paletaEGA

  fichero.seek (posicion)  # Saltamos a donde está la imagen

  if le:
    ancho = ord (fichero.read (1))  # LSB de la anchura de la imagen
    valor = ord (fichero.read (1))
  else:
    valor = ord (fichero.read (1))
    ancho = ord (fichero.read (1))  # LSB de la anchura de la imagen
  ancho += (valor & 127) * 256
  if ancho == 0 or ancho % 4:
    prn ('El ancho de la imagen', numImg, 'no es mayor que 0 y múltiplo de 4, vale', ancho)
  ancho /= 4  # Anchura de la imagen (en bloques de 4 píxeles)
  rle = valor & 128

  if le:
    alto = ord (fichero.read (1))  # Altura de la imagen (en número de filas)
    fichero.read (1)
  else:
    fichero.read (1)
    alto = ord (fichero.read (1))  # Altura de la imagen (en número de filas)
  if alto == 0 or alto % 8:
    prn ('El alto de la imagen', numImg, 'no es mayor que 0 y múltiplo de 8, vale', alto)

  if 0 in (ancho, alto):
    continue

  repetir = []
  fichero.seek (2, 1)  # Saltamos valor de longitud de la imagen
  if rle:
    if modo == 'ST':
      bits = (ord (fichero.read (1)) * 256) + ord (fichero.read (1))  # Ḿáscara de colores que se repetirán
      for indiceBit in range (16):
        if bits & (2 ** indiceBit):
          repetir.append (indiceBit)
    else:
      b = ord (fichero.read (1))  # Número de secuencias que se repetirán
      if b > 4:
        prn ('Valor inesperado para el número de secuencias que se repetirán:', b, 'para la imagen:', numImg)
      for i in range (4):
        if i < b:
          repetir.append (ord (fichero.read (1)))
        else:
          fichero.seek (1, 1)

  strImg  = ''    # Cadena que representa toda la imagen
  fila    = ''    # Cadena que representa la fila actual
  izqAder = True  # Sentido de procesado de píxeles de la fila actual
  tamFila = ancho   * 4     # Tamaño en píxeles (y bytes) que tendrá cada fila
  tamImg  = tamFila * alto  # Tamaño en píxeles (y bytes) que tendrá la imagen

  if modo == 'CGA':
    while len (strImg) < tamImg:  # Mientras quede imagen por procesar
      b = ord (fichero.read (1))  # Byte actual
      if b in repetir:
        repeticiones = ord (fichero.read (1))
      else:
        repeticiones = 1
      pixels = chr (b >> 6) + chr ((b >> 4) & 3) + chr ((b >> 2) & 3) + chr (b & 3)  # Número de color de los cuatro píxeles
      if izqAder:  # Sentido de izquierda a derecha
        fila += pixels * repeticiones  # Añadimos al final 
      else:  # Sentido de derecha a izquierda
        fila = (pixels * repeticiones) + fila  # Añadimos al principio
      while len (fila) >= tamFila:  # Al repetirse, se puede exceder la longitud de una fila
        if izqAder:  # Sentido de izquierda a derecha
          strImg += fila[0:tamFila]
          fila    = fila[tamFila:]
        else:  # Sentido de derecha a izquierda
          strImg += fila[-tamFila:]
          fila    = fila[:-tamFila]
        if rle:
          izqAder = not izqAder
  elif modo != 'ST':
    # Modos PCW monocromo y EGA en orden planar con cuatro planos de bit de color enteros consecutivos
    resolucion   = ancho * 4 * alto
    colores      = ([0] * resolucion)
    numPlanos    = 1 if modo == 'PCW' else 4
    repeticiones = 0
    for plano in range (numPlanos):
      bitsFila = []
      numFila  = 0
      while numFila < alto:
        if not repeticiones:
          try:
            b = ord (fichero.read (1))  # Byte actual
            if b in repetir:
              repeticiones = ord (fichero.read (1))
              if repeticiones < 1:
                prn ('Valor inesperado (' + str (repeticiones) + ') para el número de repeticiones de LRE, en la imagen', numImg)
            else:
              repeticiones = 1
          except:
            prn ('Imagen', numImg, 'incompleta. ¿Formato incorrecto?')
          bits = []  # Bits del byte actual
          for indiceBit in range (7, -1, -1):  # Cada bit del byte actual
            bits.append (1 if b & (2 ** indiceBit) else 0)
        cuantas = min (repeticiones, (tamFila - len (bitsFila)) / 8)  # Evitamos exceder la longitud de una fila
        if izqAder:  # Sentido de izquierda a derecha
          bitsFila.extend (bits * cuantas)  # Añadimos al final
        else:  # Sentido de derecha a izquierda
          bitsReversa = bits[::-1]
          bitsFila.extend (bitsReversa * cuantas)  # Añadimos al final, pero con los bits invertidos
        repeticiones -= cuantas
        if len (bitsFila) == tamFila:  # Al repetir no se excede la longitud de una fila
          if modo == 'PCW' and not rle:
            bytesEnFila   = tamFila     / 8
            bloquesEnFila = bytesEnFila / 8  # Bloques de 8 bytes por cada fila
            for indiceByte in range (bytesEnFila):
              byte = bitsFila[indiceByte * 8 : (indiceByte * 8) + 8]
              numBloqueDest = numFila // 8      # Índice del bloque de 8 filas, en destino
              numFilaDest   = (indiceByte % 8)  # Índice de fila dentro del bloque, en destino
              numByteDest   = ((numFila % 8) * bloquesEnFila) + (indiceByte // 8)  # Índice del byte dentro de la fila, en destino
              primerPixel   = (numBloqueDest * tamFila * 8) + (numFilaDest * tamFila) + (numByteDest * 8)  # Índice del primer píxel del byte, en destino
              for indiceBit in range (8):
                bit = byte[indiceBit]
                colores[primerPixel + indiceBit] += (2 ** plano) if bit else 0
          elif izqAder:  # Sentido de izquierda a derecha
            primerPixel = (numFila * tamFila)  # Índice del primer píxel del byte
            for indiceBit in range (tamFila):
              bit = bitsFila[indiceBit]
              colores[primerPixel + indiceBit] += (2 ** plano) if bit else 0
          else:  # Sentido de derecha a izquierda
            ultimoPixel = (numFila * tamFila) + tamFila - 1  # Índice del último píxel del byte
            for indiceBit in range (tamFila):
              bit = bitsFila[indiceBit]
              colores[ultimoPixel - indiceBit] += (2 ** plano) if bit else 0
          bitsFila = []
          if rle:
            izqAder = not izqAder
          numFila += 1
    for pixel in range (resolucion):  # Cada píxel en la imagen
      strImg += chr (colores[pixel])
  else:  # Modo de Amiga/Atari ST
    color     = None  # Índice de color del píxel actual
    numPlanos = 4
    while len (strImg) < tamImg:  # Mientras quede imagen por procesar
      colores = ([0] * 8)
      for plano in range (numPlanos):
        b = ord (fichero.read (1))  # Byte actual
        for indiceBit in range (8):
          bit = b & (2 ** indiceBit)
          colores[7 - indiceBit] += (2 ** plano) if bit else 0
      for pixel in range (8):  # Cada píxel en el grupo
        if color == None:
          color = colores[pixel]
          if rle and color in repetir:
            continue  # El número de repiticiones vendrá en el valor del siguiente píxel
        if rle and color in repetir:
          repeticiones = colores[pixel] + 1
        else:
          repeticiones = 1
        strImg += chr (color) * repeticiones
        color   = None

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
