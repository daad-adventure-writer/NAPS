#!/usr/bin/env python
# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Crea bases de datos gráficas de DAAD, en el formato de las primeras versiones de DAAD
# Copyright (C) 2008-2009, 2021 José Manuel Ferrer Ortiz
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

import pygame.image

from prn_func import prn


if len (sys.argv) < 3:
  prn ('Uso:', sys.argv[0], 'carpeta_origen base_de_datos_imágenes')
  sys.exit()

anchoMiniImg = 56  # Ancho en píxeles de mini-imágenes que no se comprimen

# Paletas CGA (1 y 2 con brillo) en el orden necesario
paleta1b = [(0, 0, 0), (84, 254, 254), (254, 84, 254), (254, 254, 254)]
paleta2b = [(0, 0, 0), (84, 254, 84),  (254, 84, 84),  (254, 254, 84)]

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

# Paleta PCW en el orden necesario, negro y verde
paletaPCW = ((0, 0, 0), (0, 255, 0))

origen   = sys.argv[1]  # Ruta al directorio de origen de imágenes
destino  = sys.argv[2]  # Ruta de destino a base de datos DAAD de imágenes
imagenes = []  # Lista de números de imagen válidos

if destino[-4:].lower() == '.cga':
  modo = 'CGA'
elif destino[-4:].lower() == '.ega':
  modo = 'EGA'
  paleta = paletaEGA
elif destino[-4:].lower() == '.pcw':
  modo = 'PCW'
  paleta = paletaPCW
else:
  prn ('La base de datos de imágenes debe tener una de las siguientes extensiones: CGA, EGA, PCW')
  sys.exit()


def cargaStrImgCGA (imagen, ancho, alto, paleta):
  anchoBytes = ancho / 4  # Ancho de una fila en bytes
  strImg  = ''
  strOrig = ''
  for fila in range (alto):
    cadena = ''
    for columna in range (anchoBytes):
      pixels = []
      for i in range (4):
        pixels.append (paleta.index (imagen.get_at (((columna * 4) + i, fila))[:3]))
      cadena += (chr ((pixels[0] << 6) + (pixels[1] << 4) + (pixels[2] << 2) + pixels[3]))
    strOrig += cadena
    if ((fila % 2) == 0) or ancho <= anchoMiniImg:  # Si la fila es par o no comprimida
      strImg += cadena
    else:
      for i in range (anchoBytes - 1, -1, -1):
        strImg += cadena[i]  # Añadimos la cadena invertida
  return strImg, strOrig

def cargaStrImgPlanar (imagen, ancho, alto, paleta, numPlanos):
  bits         = []  # Bits del byte actual
  bytesFila    = ''  # Bytes de la fila actual
  bytesFilaInv = ''  # Bytes de la fila actual en orden invertido
  strImg  = ''
  strOrig = ''
  for plano in range (numPlanos):
    for fila in range (alto):
      for columna in range (ancho):
        bits.append (paleta.index (imagen.get_at ((columna, fila))[:3]) & (2 ** plano))
        if len (bits) == 8:
          byte = 0
          for indiceBit in range (8):
            if bits[indiceBit]:
              byte += 2 ** (7 - indiceBit)
          bytesFila    += chr (byte)
          bytesFilaInv  = chr (byte) + bytesFilaInv
          if len (bytesFila) % (ancho / 8) == 0:
            if (len (strImg) // (ancho / 8)) % 2:  # En 'líneas' impares, dejamos invertidos los bits para comprimir
              strImg += bytesFilaInv
            else:
              strImg += bytesFila
            strOrig += bytesFila
            bytesFila    = ''
            bytesFilaInv = ''
          bits = []
  return strImg, strOrig

def ordenaStrImgPCW (strOrig, ancho):
  """Reordena los bytes de cadena de imagen de mapa de bits PCW, con 1 bppp, para ser guardada sin compresión en la base de datos gráfica"""
  anchoBytes = ancho / 8  # Ancho de una fila en bytes
  lstDest    = [' '] * len (strOrig)
  numBloque  = 0  # Número de bloque de 8 filas actual
  posByte    = 0  # Posición del byte actual dentro del bloque
  tamBloque  = anchoBytes * 8  # Tamaño en bytes de un bloque de 8 filas
  for indiceByte in range (len (strOrig)):
    posDest = (numBloque * tamBloque) + posByte
    lstDest[posDest] = strOrig[indiceByte]
    posByte += 8
    if posByte >= tamBloque:
      if posByte == tamBloque + 7:
        numBloque += 1
        posByte    = 0
      else:
        posByte -= tamBloque
        posByte += 1
  strDest = ''
  for byte in lstDest:
    strDest += byte
  return strDest


fichero = open (destino, 'wb')  # Fichero de destino de BBDD DAAD imágenes
if modo == 'EGA':
  fichero.write ('\x00\x00\x0d\x00\x00\x00')  # Cabecera para DOS EGA
else:
  fichero.write ('\x00\x00\x04\x00\x00\x00')  # Cabecera para modos CGA y PCW

strImgs = {}  # Cada imagen ya tratada, para detectar duplicados, junto con su número

for numImg in range (256):
  try:
    imagen = pygame.image.load (origen + '/pic%03d.png' % (numImg))
  except:
    fichero.write ('\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    continue
  imagenes.append (numImg)
  fichero.write ('\x00\x00\x00\x00')
  if imagen.get_width() <= 56:  # Es una mini-imagen
    fichero.write ('\x03')  # Flotante y guardada en memoria
  elif (254, 254, 84) in imagen.get_palette():
    fichero.write ('\x00')  # Paleta 2 con brillo
  else:
    fichero.write ('\x80')  # Paleta 1 con brillo
  fichero.write ('\x00\x00\x00\x00\x00')

for numImg in imagenes:
  imagen = pygame.image.load (origen + '/pic%03d.png' % (numImg))
  alto   = imagen.get_height()  # Altura en píxeles de la imagen
  ancho  = imagen.get_width()   # Anchura en píxeles de la imagen

  if modo == 'CGA':
    paleta = paleta1b if (254, 254, 254) in imagen.get_palette() else paleta2b
    strImg, strOrig = cargaStrImgCGA (imagen, ancho, alto, paleta)
  elif modo == 'EGA':
    strImg, strOrig = cargaStrImgPlanar (imagen, ancho, alto, paleta, numPlanos = 4)
  else:  # Modo PCW
    strImg, strOrig = cargaStrImgPlanar (imagen, ancho, alto, paleta, numPlanos = 1)
    strOrig = ordenaStrImgPCW (strOrig, ancho)  # Cambia al formato de imagen sin comprimir para PCW

  if strImg in strImgs:  # Imagen repetida
    # Obtenemos el desplazamiento de la imagen original
    numOrig  = strImgs[strImg][0]
    posicion = strImgs[strImg][1]
    # Guardamos el desplazamiento para la imagen repetida
    fichero.seek ((10 * int (numImg)) + 6)
    fichero.write (chr (posicion & 0xff))
    fichero.write (chr ((posicion >> 8) & 0xff))
    fichero.write (chr ((posicion >> 16) & 0xff))
    # Guardamos la paleta de esta imagen
    fichero.seek (1, 1)
    if modo != 'CGA' or paleta == paleta2b:
      fichero.write ('\x00')  # Paleta 2 con brillo en modo CGA
    else:
      fichero.write ('\x80')  # Paleta 1 con brillo en modo CGA

    prn ('Imagen', numImg, 'igual que la', numOrig, '\n')
  else:  # Imagen diferente
    # Escribimos la posición donde irá la nueva imagen
    fichero.seek (0, 2)  # El dos indica desde el final del fichero
    posicion = fichero.tell()
    fichero.seek ((10 * numImg) + 6)
    fichero.write (chr (posicion & 0xff))
    fichero.write (chr ((posicion >> 8) & 0xff))
    fichero.write (chr ((posicion >> 16) & 0xff))

    strImgs[strImg] = [numImg, posicion]

    if ancho > anchoMiniImg:
      # Buscamos secuencias de pixels que se repitan (consecutivamente)
      repetidos = set()
      for i in range (1, len (strImg)):
        if strImg[i] == strImg[i - 1]:
          repetidos.add (strImg[i])
      # Vemos cuántos bytes ahorraríamos usando dichas secuencias con compresión
      ahorro = dict()
      i = 0
      while i < len (strImg):
        if strImg[i] in repetidos:
          c = strImg[i]
          cuenta = -1
          i += 1
          while (i < len (strImg)) and (strImg[i] == c):
            cuenta += 1
            i      += 1
          ahorro[c] = ahorro.get (c, 0) + cuenta
        else:
          i += 1
      # Descartamos las secuencias con las que empeoraríamos el tamaño
      for clave, valor in dict (ahorro).items():
        if valor < 0:
          del ahorro[clave]
      while len (ahorro) > 4:  # DAAD sólo soporta 4 secuencias para compresión
        minimo = min (ahorro.values())
        for clave, valor in dict (ahorro).items():
          if valor == minimo:
            del ahorro[clave]
            break
      # Sustituimos las secuencias repetidas por su modo comprimido
      strTmp = ''
      i = 0
      while i < len (strImg):
        if strImg[i] in ahorro.keys():
          c = strImg[i]
          strTmp += c
          cuenta = 1
          i += 1
          while (i < len (strImg)) and (strImg[i] == c):
            cuenta += 1
            i      += 1
          while cuenta > 255:  # Hay que trocear. Puede que 0 indique 256 veces
            strTmp += chr (255) + c
            cuenta -= 255
          strTmp += chr (cuenta)
        else:
          strTmp += strImg[i]
          i += 1
      strImg = strTmp

    # Guardamos el ancho y alto de la imagen, y si estará comprimida
    fichero.seek (0, 2)  # El dos indica desde el final del fichero
    fichero.write (chr (ancho & 255))
    if ancho <= anchoMiniImg or len (ahorro) < 1:  # Es mini-imagen o no se ahorraba nada
      fichero.write (chr ((ancho >> 8) % 128))
    else:  # Es imagen comprimida
      fichero.write (chr (((ancho >> 8) % 128) + 128))
    fichero.write (chr (alto & 255) + chr (alto / 256))

    # Guardamos la longitud de la imagen
    longitud = len (strImg)
    if ancho > anchoMiniImg and len (ahorro) > 0:
      longitud += 5
    fichero.write (chr (longitud & 0xff))
    fichero.write (chr (longitud >> 8))

    # Guardamos las secuencias que aparecen en modo comprimido
    if ancho > anchoMiniImg and len (ahorro) > 0:  # Es imagen comprimida
      fichero.write (chr (len (ahorro)))
      for elem in ahorro.keys():
        fichero.write (elem)
      for i in range (4 - len (ahorro)):  # Rellenamos los valores restantes
        fichero.write (ahorro.keys()[0])
      # Escribimos al fichero la imagen comprimida
      fichero.write (strImg)
      prn ('Imagen', str (numImg) + ', tamaño original:', len (strOrig), 'bytes, compresión: {')
      for clave, valor in ahorro.items():
        prn ('\tsecuencia "' + hex (ord (clave)) + '" ahorra', valor, 'bytes')
      prn ('} Resultado:', len (strImg), 'bytes')
    else:  # Escribimos al fichero la imagen original
      fichero.write (strOrig)
      prn ('Imagen', str (numImg) + ', tamaño:', len (strOrig), 'bytes (no comprimida)')
    prn()


# Guardamos el número de imágenes únicas
fichero.seek (4)
fichero.write (chr (len (strImgs)))
