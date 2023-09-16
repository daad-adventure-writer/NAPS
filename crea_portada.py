#!/usr/bin/env python
# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Crea portada de DAAD a partir de la imagen dada como argumento
# Copyright (C) 2023 José Manuel Ferrer Ortiz
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

import pygame.image

import graficos_bitmap
from prn_func import prn


formatos = {
  'amiga': {'extension': 'scr', 'modo': 'ST'},
}

if len (sys.argv) < 4:
  prn ('Uso:', sys.argv[0], 'ruta_imagen formato_portada ruta_portada')
  sys.exit()

formato = sys.argv[2]
if formato not in formatos:
  prn ('Formato de portada no soportado. Usar uno de los siguientes:', ', '.join (formatos))
  sys.exit()
resolucion = graficos_bitmap.resolucion_por_modo[formatos[formato]['modo']]

imagen = pygame.image.load (sys.argv[1])
if imagen.get_width() != resolucion[0] or imagen.get_height() != resolucion[1]:
  prn ('La imagen debe tener una resolución de %d x %d píxeles' % resolucion)
  sys.exit()

# Obtenemos la paleta de la imagen
try:
  paleta = imagen.get_palette()
except:  # No está en formato de paleta indexada
  paleta = []
  for x in range (resolucion[0]):
    for y in range (resolucion[1]):
      color = imagen.get_at ((x, y))[:3]
      if color not in paleta:
        paleta.append (color)
        if len (paleta) > 16:
          prn ('La imagen no debe tener más de 16 colores diferentes')
          sys.exit()
  prn ('Advertencia: al no estar la imagen en formato de paleta indexada, se ha construido la paleta con los colores en orden de aparición')

# Obtenemos la imagen como índices en la paleta
imgComoIndices = []
for y in range (resolucion[1]):
  for x in range (resolucion[0]):
    imgComoIndices.append (paleta.index (imagen.get_at ((x, y))[:3]))

destino = sys.argv[3]
if '.' not in os.path.basename (destino):
  destino += '.' + formatos[formato]['extension']
fichero = open (destino, 'wb')
if formato == 'amiga':
  graficos_bitmap.guarda_portada_amiga (imgComoIndices, paleta, fichero)
fichero.close()
