# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librer�a para operar con bases de datos gr�ficas y otros gr�ficos de mapa de bits
# Copyright (C) 2008, 2018-2025 Jos� Manuel Ferrer Ortiz
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


traza = False  # Si queremos traza del funcionamiento del m�dulo
if traza:
  from prn_func import prn


# Paleta de colores por defecto de varios modos gr�ficos, sin reordenar para textos
colores_por_defecto = {
  'VGA': ((  0,   0,   0), (255, 255, 255), (255,   0,   0), (  0, 255,  0),
          (  0,   0, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
          (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
          (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)),
}

# N�mero de colores de cada modo gr�fico
colores_por_modo = {
  'CGA': 4,
  'EGA': 16,
  'PCW': 2,
  'ST':  16,
  'VGA': 16,
}

# Marca de orden de componentes de color con el bit menos significativo en el bit m�s bajo
marca_amiga = (0xDA, 0xAD, 0xDA, 0xAD)

# Resoluci�n de cada modo gr�fico
resolucion_por_modo = {
  'CGA': (320, 200),
  'EGA': (320, 200),
  'PCW': (720, 256),
  'ST':  (320, 200),
  'VGA': (320, 200),
}

# Paletas CGA 1 y 2 con y sin brillo, en el orden necesario
paleta1b = ((0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255))
paleta2b = ((0, 0, 0), (85, 255,  85), (255, 85,  85), (255, 255,  85))
paleta1s = ((0, 0, 0), ( 0, 170, 170), (170,  0, 170), (170, 170, 170))
paleta2s = ((0, 0, 0), ( 0, 170,   0), (170,  0,   0), (170,  85,   0))

# Paletas de blanco y negro, en el orden necesario
paletaBN = ((255, 255, 255), (0, 0, 0))
paletaNB = ((0, 0, 0), (255, 255, 255))

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

# Paleta PCW en el orden necesario, negro y verde
paletaPCW = ((0, 0, 0), (0, 255, 0))


# Valores 'hardcodeados' para las im�genes de las aventuras SWAN
imagenesSWAN = {
  'mindf': {
    'caracterBorde': (  # Los �ndices de color son sobre la paleta reordenada para textos
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 2, 2, 2, 2, 2, 2, 0,
      0, 2, 0, 0, 0, 0, 2, 0,
      0, 2, 0, 2, 2, 0, 2, 0,
      0, 2, 0, 2, 2, 0, 2, 0,
      0, 2, 0, 0, 0, 0, 2, 0,
      0, 2, 2, 2, 2, 2, 2, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
    ),
    'imagenPorDefecto': 1,
    'imagenPorLocalidad': (3, 1, 1, 1, 1, 4, 4, 1, 1, 1, 1, 7, 5, 5, 1, 1, 1, 3, 3, 1, 7, 1, 1, 7, 7, 3, 3, 3, 3, 1, 1, 8, 8, 1, 8, 8, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 4, 4, 10, 9, 10, 10, 9, 9, 10, 10, 10, 9, 10, 11, 11, 10, 9, 9, 10, 10, 9, 10, 11, 11, 10, 10, 11, 11, 11, 11, 11, 10, 10, 1, 16, 16, 16, 16, 16, 12, 12, 12, 12, 12, 12, 12, 12, 12, 1, 14, 13, 12, 4, 1, 6)
    }
}


indice_nuevos     = -1    # �ndice para almacenar la posici�n de nuevos recursos
le                = None  # Si el formato de la base de datos gr�fica es Little Endian
long_cabecera     = None  # Longitud de la cabecera de la base de datos
long_cabecera_rec = None  # Longitud de la cabecera de recurso
modo_gfx          = None  # Modo gr�fico
pos_recursos      = {}    # Asociaci�n entre cada posici�n de recurso, y los n�meros de recurso que la usan
recursos          = []    # Gr�ficos y sonidos de la base de datos gr�fica


# Funciones que utilizan el IDE, el editor de bases de datos gr�ficas, o el int�rprete directamente

def cambia_imagen (numRecurso, ancho, alto, imagen, paleta):
  global indice_nuevos
  if recursos[numRecurso]:
    recurso = recursos[numRecurso]
    pos_recursos[recurso['desplazamiento']].remove (numRecurso)
    limpiarPosicion = recurso['desplazamiento']
  else:
    limpiarPosicion = None
    recurso         = {'banderas': set(), 'banderasInt': 0, 'desplazamiento': None, 'posicion': (0, 0)}
  # Vemos si ya hab�a alg�n recurso con la misma imagen
  for recursoExistente in recursos:
    if not recursoExistente:
      continue  # Saltamos los recursos inexistentes
    if recursoExistente['dimensiones'] == (ancho, alto) and imagen == recursoExistente['imagen']:
      recurso['desplazamiento'] = recursoExistente['desplazamiento']
      pos_recursos[recurso['desplazamiento']].append (numRecurso)
      break
  else:  # No hab�a ninguno con la misma imagen
    recurso['desplazamiento']   = indice_nuevos
    pos_recursos[indice_nuevos] = [numRecurso]
    indice_nuevos -= 1
  # Quitamos la entrada de pos_recursos si ya no queda ninguna imagen con el desplazamiento que ten�a la imagen anterior
  if limpiarPosicion != None and not len (pos_recursos[limpiarPosicion]):
    del pos_recursos[limpiarPosicion]
  if modo_gfx == 'CGA':
    if paleta == paleta1b:
      recurso['banderas'].add ('cgaPaleta1')
      recurso['banderasInt'] |= 4 if version > 1 else 128
    elif 'cgaPaleta1' in recurso['banderas']:
      recurso['banderas'].remove ('cgaPaleta1')
      if recurso['banderasInt'] & (4 if version > 1 else 128):
        recurso['banderasInt'] -= 4 if version > 1 else 128
  recurso['dimensiones'] = (ancho, alto)
  recurso['imagen']      = imagen
  recurso['paleta']      = paleta
  recursos[numRecurso] = recurso

def carga_bd_pics (nombreFichero):
  """Carga a memoria la base de datos gr�fica desde el fichero de nombre dado. Devuelve un mensaje de error si falla"""
  global fichero
  try:
    fichero = open (nombreFichero, 'rb')
  except IOError as excepcion:
    return excepcion.args[1]
  extension = nombreFichero[-4:].lower()
  if extension not in ('.cga', '.dat', '.ega', '.pcw'):
    return 'Extensi�n %s inv�lida para bases de datos gr�ficas de DAAD' % extension
  bajo_nivel_cambia_ent (fichero)
  for funcion, parametros in ((preparaPlataforma, (extension, fichero)), (cargaRecursos, ())):
    try:
      msgError = funcion (*parametros)
      if msgError:
        fichero.close()
        return msgError
    except Exception as excepcion:
      fichero.close()
      return excepcion.args[0]
  fichero.close()

def carga_fuente (fichero):
  """Carga y devuelve una fuente tipogr�fica de DAAD junto con su paleta, como �ndices en la paleta de cada p�xel, organizados como en fuente.png"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  fichero.seek ((128 if 3200 > longFichero > 2048 else 0) + (16 * 8 if longFichero < 3200 else 0))
  ancho  = 628
  alto   = 38 + (0 if longFichero < 3200 else 10)
  imagen = [0] * ancho * alto  # �ndices en la paleta de cada p�xel en la imagen
  for caracter in range (256 - (16 if longFichero < 3200 else 0)):
    posPorCol  = (caracter  % 63) * 10
    posPorFila = (caracter // 63) * 10 * ancho
    for fila in range (8):
      b = carga_int1()  # Byte actual
      for indiceBit in range (8):  # Cada bit del byte actual
        imagen[posPorFila + posPorCol + indiceBit] = 0 if b & (2 ** (7 - indiceBit)) else 1
      posPorFila += ancho
  return imagen, paletaBN

def carga_fuente_zx_8 (fichero, posicion = None):
  """Carga y devuelve una fuente tipogr�fica de ZX Spectrum de 8x8 junto con su paleta, como �ndices en la paleta de cada p�xel, organizados como en fuente.png"""
  if posicion == None:
    posicion = detectaFuente8 (fichero)
    if posicion == None:
      return [], []
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (posicion)
  ancho  = 628
  alto   = 48
  imagen = [0] * ancho * alto  # �ndices en la paleta de cada p�xel en la imagen
  for caracter in range (96):
    posPorCol  = (caracter  % 63) * 10
    posPorFila = (caracter // 63) * 10 * ancho
    for fila in range (8):
      b = carga_int1()  # Fila actual
      for indiceBit in range (8):  # Cada bit de la fila actual
        imagen[posPorFila + posPorCol + indiceBit] = 0 if b & (2 ** (7 - indiceBit)) else 1
      posPorFila += ancho
  return imagen, paletaBN

def carga_imagen_pix (fichero):
  """Carga y devuelve una imagen PIX de SWAN junto con su paleta y dimensiones, como �ndices en la paleta de cada p�xel, detectando su modo gr�fico"""
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  fichero.seek (0)
  if longFichero < 15488:  # Como no ocupa lo suficiente para poder ser una imagen de Atari, asumimos que es en blanco y negro
    dimensiones = (304, 64)
    imagen, paleta = cargaImagenPIXenBN (fichero)
  else:
    dimensiones = (320, 96)
    imagen, paleta = cargaImagenAtari (fichero)
  return imagen, paleta, dimensiones

def carga_portada (fichero, pareceST = False):
  """Carga y devuelve una portada de DAAD junto con su paleta, como �ndices en la paleta de cada p�xel, detectando su modo gr�fico"""
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  fichero.seek (0)
  if longFichero in (16000, 16384):
    return cargaPortadaCGA (fichero, longFichero)
  if longFichero == 32001:
    return cargaPortadaEGA (fichero)
  if longFichero == 32049:
    return cargaPortadaVGA (fichero)
  if (longFichero == 32034 and not pareceST) or (longFichero in (32127, 32128)):
    return cargaPortadaAmiga (fichero)
  if longFichero in (32034, 32066):
    return cargaPortadaAtari (fichero)
  return None

def carga_udgs_zx (fichero, posicion, numUDGs):
  """Carga y devuelve el n�mero dado de UDGs de ZX Spectrum de 8x8 junto con su paleta, como �ndices en la paleta de cada p�xel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (posicion)
  ancho  = numUDGs * 8
  alto   = 8
  imagen = [0] * ancho * alto  # �ndices en la paleta de cada p�xel en la imagen
  for u in range (numUDGs):
    posPorCol  = u * 8
    posPorFila = 0
    for fila in range (8):
      b = carga_int1()  # Fila actual
      for indiceBit in range (8):  # Cada bit de la fila actual
        imagen[posPorFila + posPorCol + indiceBit] = 0 if b & (2 ** (7 - indiceBit)) else 1
      posPorFila += ancho
  return imagen, paletaBN

def da_paletas_del_formato ():
  """Devuelve un diccionario con las paletas del formato de base de datos gr�fica, que ser� lista vac�a para los modos que soportan paleta variable"""
  if modo_gfx == 'CGA':
    return {'CGA': [paleta1b, paleta2b]}
  if modo_gfx == 'EGA':
    return {'EGA': [paletaEGA]}
  if modo_gfx == 'PCW':
    return {'PCW': [paletaPCW]}
  if modo_gfx in ('ST', 'VGA'):
    return {'CGA': [paleta1b, paleta2b], 'EGA': [paletaEGA], 'ST/VGA': []}

def elimina_recurso (numRecurso):
  """Elimina los datos del recurso de n�mero dado"""
  recurso = recursos[numRecurso]
  if len (pos_recursos[recurso['desplazamiento']]) > 1:  # El contenido de este recurso era usado por m�s de un recurso
    pos_recursos[recurso['desplazamiento']].remove (numRecurso)
  else:  # El contenido de este recurso era �nico
    del pos_recursos[recurso['desplazamiento']]
  recursos[numRecurso] = None

def guarda_bd_pics (fichero, ordenAmiga = True):
  """Exporta la base de datos gr�fica en memoria sobre el fichero dado"""
  # TODO: completar para el formato de DMG versi�n 3+
  bajo_nivel_cambia_endian (le)
  bajo_nivel_cambia_sal    (fichero)
  if le:
    guarda_int2 = guarda_int2_le
    guarda_int4 = guarda_int4_le
  else:
    guarda_int2 = guarda_int2_be
    guarda_int4 = guarda_int4_be
  # Guardamos la plataforma y el modo gr�fico
  if version > 1:
    if modo_gfx == 'ST':
      guarda_int2 (768)  # Plataforma Amiga/Atari ST
    else:
      guarda_int2 (65535)  # Plataforma PC
    guarda_int2 (0)  # No se especifica modo gr�fico
  else:  # version == 1
    if modo_gfx == 'ST':
      guarda_int2 (4)  # Plataforma Amiga/Atari ST
      guarda_int2 (0)  # No tiene modo gr�fico
    else:
      guarda_int2 (0)  # Plataforma PC/PCW
      if modo_gfx == 'EGA':
        guarda_int2 (13)  # Modo gr�fico EGA
      else:
        guarda_int2 (4)  # Modo gr�fico CGA/PCW
  # Guardamos el n�mero de im�genes �nicas
  guarda_int2 (len (pos_recursos))
  if version > 1:  # Dejamos espacio para la longitud de la base de datos gr�fica
    guarda_int4 (0)
  # Dejamos espacio para las cabeceras de los recursos
  if sys.version_info [0] < 3:
    fichero.write (chr (0) * long_cabecera_rec * 256)
  else:
    fichero.write (bytes ([0] * long_cabecera_rec * 256))
  # Guardamos la posici�n actual para empezar a guardar los datos de los recursos desde aqu�
  desplActual = fichero.tell()
  # Ordenamos los recursos de menor a mayor desplazamiento dentro de la base de datos gr�fica
  desplazamientos = sorted (pos_recursos.keys())
  if desplazamientos:  # Ponemos los n�meros negativos (los de nuevos recursos) al final
    ultimoNegativo = -1
    while ultimoNegativo + 1 < len (desplazamientos) and desplazamientos[ultimoNegativo + 1] < 0:
      ultimoNegativo += 1
    desplNegativos = desplazamientos[:ultimoNegativo + 1]
    desplNegativos.reverse()
    desplazamientos = desplazamientos[ultimoNegativo + 1:] + desplNegativos
  # Guardamos cada recurso y su cabecera en orden
  for desplazamiento in desplazamientos:
    fichero.seek (desplActual)
    numRecursos = pos_recursos[desplazamiento]
    recurso     = recursos[numRecursos[0]]
    # TODO: resto de formatos aparte de PCW y DMG3+
    # TODO: no forzar compresi�n de im�genes
    if version > 1:
      imagen, repetir = comprimeImagenDMG3 (recurso['imagen'], forzarRLE = True)
    else:
      imagen, repetir = comprimeImagenPlanar (recurso['imagen'], recurso['dimensiones'][0], True, forzarRLE = True)
    # Guardamos el contenido del recurso
    # Guardamos el ancho de la imagen y la bandera de compresi�n RLE
    rle            = 128 if len (imagen) else 0                      # 0 no comprimir, 128 comprimir
    lsbAncho       = recurso['dimensiones'][0] & 255                 # LSB de la anchura de la imagen
    msbAnchoMasRLE = ((recurso['dimensiones'][0] >> 8) & 127) + rle  # MSB de la anchura de la imagen + bit de compresi�n RLE
    if le:
      guarda_int1 (lsbAncho)
      guarda_int1 (msbAnchoMasRLE)
    else:
      guarda_int1 (msbAnchoMasRLE)
      guarda_int1 (lsbAncho)
    guarda_int2 (recurso['dimensiones'][1])  # Altura de la imagen
    # TODO: no compresi�n de im�genes
    longImagenRLE = len (imagen)  # Longitud de la imagen incluyendo la informaci�n para compresi�n RLE
    if rle:
      longImagenRLE += 2 if modo_gfx == 'ST' or version > 1 else 5
    guarda_int2 (longImagenRLE)  # Longitud de la imagen codificada
    # Guardamos la informaci�n para compresi�n RLE
    if rle:
      if modo_gfx == 'ST' or version > 1:
        bits = 0  # M�scara de colores que se repetir�n
        for indiceBit in range (16):
          if indiceBit in repetir:
            bits += 2 ** indiceBit
        guarda_int2 (bits)
      else:
        guarda_int1 (len (repetir))  # N�mero de secuencias que se repetir�n
        for i in range (4):
          if i < len (repetir):
            guarda_int1 (repetir[i])
          else:
            guarda_int1 (0)
    # Guardamos datos de la imagen en s�
    fichero.write (bytes (bytearray (imagen)))
    # Guardamos la posici�n actual para guardar el contenido del siguiente recurso aqu�
    desplSiguiente = fichero.tell()
    # Guardamos la cabecera de cada uno de los recursos con este mismo desplazamiento
    for numRecurso in numRecursos:
      cabRecurso = long_cabecera + (long_cabecera_rec * numRecurso)
      fichero.seek (cabRecurso)  # Vamos al desplazamiento de la cabecera del recurso
      guarda_int4 (desplActual)
      recurso = recursos[numRecurso]
      guarda_int2 (recurso['banderasInt'])
      guarda_int2 (recurso['posicion'][0])  # Coordenada X donde dibujar la imagen
      guarda_int2 (recurso['posicion'][1])  # Coordenada Y donde dibujar la imagen
      if 'cambioPaleta' in recurso:
        guarda_int1 (recurso['cambioPaleta'][0])
        guarda_int1 (recurso['cambioPaleta'][1])
      guardaPaletas (recurso, ordenAmiga)
    desplActual = desplSiguiente
  # Guardamos la longitud de la base de datos gr�fica
  if version > 1:
    fichero.seek (6)
    guarda_int4 (desplActual)

def guarda_portada_amiga (imagen, paleta, fichero):
  """Guarda una portada de Amiga en el fichero abierto dado con la imagen dada como lista de �ndices"""
  bajo_nivel_cambia_sal (fichero)
  guarda_int2_be (0)
  guardaPaleta16 (paleta, 4)
  ancho, alto = resolucion_por_modo['ST']
  guardaImagenPlanar (imagen, ancho, alto, 4)

def recurso_es_unico (numRecurso):
  """Devuelve si el contenido del recurso es �nico, o si por el contrario es usado por varios recursos"""
  return len (pos_recursos[recursos[numRecurso]['desplazamiento']]) == 1


# Funciones de apoyo de alto nivel

def cargaImagenAmiga (repetir, tamImg):
  """Carga y devuelve una imagen de Amiga/Atari ST con el formato que usan DMG 1 y DMG 3+ en im�genes sin compresi�n, como lista de �ndices en la paleta"""
  color     = None  # �ndice de color del p�xel actual
  imagen    = []    # �ndices en la paleta de cada p�xel en la imagen
  numPlanos = 4
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    colores = [0] * 8
    for plano in range (numPlanos):
      b = carga_int1()  # Byte actual
      for indiceBit in range (8):
        bit = b & (2 ** indiceBit)
        colores[7 - indiceBit] += (2 ** plano) if bit else 0
    for pixel in range (8):  # Cada p�xel en el grupo
      if color == None:
        color = colores[pixel]
        if color in repetir:
          continue  # El n�mero de repeticiones vendr� en el valor del siguiente p�xel
      if color in repetir:
        repeticiones = min (colores[pixel] + 1, tamImg - len (imagen))
      else:
        repeticiones = 1
      imagen += [color] * repeticiones
      color   = None
      if len (imagen) == tamImg:
        break
  return imagen

def cargaImagenAtari (fichero):
  """Carga y devuelve una imagen de Atari ST (en formato PIX de SWAN) junto con su paleta, como �ndices en la paleta de cada p�xel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (4)
  paleta = cargaPaleta16 (3)
  fichero.seek (128)
  imagen    = []  # �ndices en la paleta de cada p�xel en la imagen
  numPlanos = 4
  tamImg    = 320 * 96
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    colores = [0] * 16
    for plano in range (numPlanos):
      b = carga_int2_be()  # Doble byte actual
      for indiceBit in range (16):
        bit = b & (2 ** indiceBit)
        colores[15 - indiceBit] += (2 ** plano) if bit else 0
    for pixel in range (16):  # Cada p�xel en el grupo
      imagen += [colores[pixel]]
      if len (imagen) == tamImg:
        break
  return imagen, paleta

def cargaImagenCGA (ancho, repetir, tamImg):
  """Carga y devuelve una imagen CGA de DMG 1, como lista de �ndices en la paleta"""
  fila    = []    # �ndices en la paleta de cada p�xel en la fila actual
  imagen  = []    # �ndices en la paleta de cada p�xel en la imagen
  izqAder = True  # Sentido de procesado de p�xeles de la fila actual
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    b = carga_int1()  # Byte actual
    if b in repetir:
      repeticiones = carga_int1()
    else:
      repeticiones = 1
    pixeles = [b >> 6, (b >> 4) & 3, (b >> 2) & 3, b & 3]  # Color de los cuatro p�xeles actuales
    if izqAder:  # Sentido de izquierda a derecha
      fila += pixeles * repeticiones  # A�adimos al final 
    else:  # Sentido de derecha a izquierda
      fila = (pixeles * repeticiones) + fila  # A�adimos al principio
    while len (fila) >= ancho:  # Al repetirse, se puede exceder la longitud de una fila
      if izqAder:  # Sentido de izquierda a derecha
        imagen += fila[0:ancho]
        fila    = fila[ancho:]
      else:  # Sentido de derecha a izquierda
        imagen += fila[-ancho:]
        fila    = fila[:-ancho]
      if repetir:  # Si la imagen usa compresi�n RLE
        izqAder = not izqAder
  return imagen

def cargaImagenDMG3DOS (le, numImagen, repetir, tamImg):
  """Carga una imagen en formato de DMG 3+ para DOS, que tambi�n se usa para im�genes de Amiga/Atari ST comprimidas, y la devuelve como lista de �ndices en la paleta. Devuelve un mensaje de error si falla"""
  cargar  = 1 if le else 4  # Cu�ntos bytes de valores cargar cada vez, tomando primero el �ltimo cargado
  color   = None  # �ndice de color del p�xel actual
  imagen  = []    # �ndices en la paleta de cada p�xel en la imagen
  valores = []    # Valores (�ndices de color y contador de repeticiones) pendientes de procesar, en orden
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    if not valores:
      try:
        for i in range (cargar):
          b = carga_int1()  # Byte actual
          valores = [b & 15, b >> 4] + valores  # Los 4 bits m�s bajos primero, y luego los 4 m�s altos
      except:
        return 'Imagen %d incompleta. �Formato incorrecto?' % numImagen
    if color == None:
      color = valores.pop (0)
      continue  # Por si hay que cargar un nuevo byte
    if color in repetir:
      repeticiones = valores.pop (0) + 1
    else:
      repeticiones = 1
    imagen += [color] * repeticiones
    color   = None
  return imagen

def cargaImagenPIXenBN (fichero):
  """Carga y devuelve una imagen PIX de SWAN en blanco y negro junto con su paleta, como �ndices en la paleta de cada p�xel"""
  fichero.seek (8)
  bajo_nivel_cambia_ent (fichero)
  ancho = 304
  alto  = 64
  return cargaImagenPlanar (ancho, alto, 1, 0, [None], ancho * alto, invertir = False), (paletaBN[1], paletaBN[0])

def cargaImagenPlanar (ancho, alto, numPlanos, numImg, repetir, tamImg, invertir = True):
  """Carga una imagen EGA o PCW de DMG 1, modos gr�ficos PCW monocromo y Amiga y EGA en orden planar con cuatro planos de bit de color enteros consecutivos, y la devuelve como lista de �ndices en la paleta. Devuelve un mensaje de error si falla"""
  imagen       = [0] * tamImg  # �ndices en la paleta de cada p�xel en la imagen
  izqAder      = True          # Sentido de procesado de p�xeles de la fila actual
  repeticiones = 0
  for plano in range (numPlanos):
    bitsFila = []
    numFila  = 0
    while numFila < alto:
      if not repeticiones:
        try:
          b = carga_int1()  # Byte actual
          if b in repetir:
            repeticiones = carga_int1()
            if repeticiones < 1:
              return 'Valor inesperado (0) para el n�mero de repeticiones de RLE, en la imagen ' + str (numImg)
          else:
            repeticiones = 1
        except:
          return 'Imagen %d incompleta. �Formato incorrecto?' % numImg
        bits = []  # Bits del byte actual
        for indiceBit in range (7, -1, -1):  # Cada bit del byte actual
          bits.append (1 if b & (2 ** indiceBit) else 0)
      cuantas = min (repeticiones, (ancho - len (bitsFila)) // 8)  # Evitamos exceder la longitud de una fila
      if izqAder or not invertir:  # Sentido de izquierda a derecha
        bitsFila.extend (bits * cuantas)  # A�adimos al final
      else:  # Sentido de derecha a izquierda
        bitsReversa = bits[::-1]
        bitsFila.extend (bitsReversa * cuantas)  # A�adimos al final, pero con los bits invertidos
      repeticiones -= cuantas
      if len (bitsFila) == ancho:  # Al repetir no se excede la longitud de una fila
        if numPlanos == 1 and not repetir:  # Modo PCW sin compresi�n RLE
          bytesEnFila   = ancho       // 8
          bloquesEnFila = bytesEnFila // 8  # Bloques de 8 bytes por cada fila
          for indiceByte in range (bytesEnFila):
            byte = bitsFila[indiceByte * 8 : (indiceByte * 8) + 8]
            numBloqueDest = numFila // 8      # �ndice del bloque de 8 filas, en destino
            numFilaDest   = (indiceByte % 8)  # �ndice de fila dentro del bloque, en destino
            numByteDest   = ((numFila % 8) * bloquesEnFila) + (indiceByte // 8)  # �ndice del byte dentro de la fila, en destino
            primerPixel   = (numBloqueDest * ancho * 8) + (numFilaDest * ancho) + (numByteDest * 8)  # �ndice del primer p�xel del byte, en destino
            for indiceBit in range (8):
              bit = byte[indiceBit]
              imagen[primerPixel + indiceBit] += (2 ** plano) if bit else 0
        elif izqAder or not invertir:  # Sentido de izquierda a derecha
          primerPixel = (numFila * ancho)  # �ndice del primer p�xel del byte
          for indiceBit in range (ancho):
            bit = bitsFila[indiceBit]
            imagen[primerPixel + indiceBit] += (2 ** plano) if bit else 0
        else:  # Sentido de derecha a izquierda
          ultimoPixel = (numFila * ancho) + ancho - 1  # �ndice del �ltimo p�xel del byte
          for indiceBit in range (ancho):
            bit = bitsFila[indiceBit]
            imagen[ultimoPixel - indiceBit] += (2 ** plano) if bit else 0
        bitsFila = []
        if repetir:  # Si la imagen usa compresi�n RLE
          izqAder = not izqAder
        numFila += 1
  return imagen

def cargaPortadaAmiga (fichero):
  """Carga y devuelve una portada de Amiga junto con su paleta, como �ndices en la paleta de cada p�xel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (2)
  paleta = cargaPaleta16 (4, True)
  ancho  = 320
  alto   = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paleta

def cargaPortadaAtari (fichero):
  """Carga y devuelve una portada de Atari ST junto con su paleta, como �ndices en la paleta de cada p�xel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (2)
  paleta    = cargaPaleta16 (3)
  imagen    = []  # �ndices en la paleta de cada p�xel en la imagen
  numPlanos = 4
  tamImg    = 320 * 200
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    colores = [0] * 16
    for plano in range (numPlanos):
      b = carga_int2_be()  # Doble byte actual
      for indiceBit in range (16):
        bit = b & (2 ** indiceBit)
        colores[15 - indiceBit] += (2 ** plano) if bit else 0
    for pixel in range (16):  # Cada p�xel en el grupo
      imagen += [colores[pixel]]
      if len (imagen) == tamImg:
        break
  return imagen, paleta

def cargaPortadaCGA (fichero, longFichero):
  """Carga y devuelve una portada CGA junto con su paleta, como lista de �ndices en la paleta de cada fila"""
  bajo_nivel_cambia_ent (fichero)
  ancho   = 320
  alto    = 200
  fila    = []           # �ndices en la paleta de cada p�xel en la fila actual
  imagen  = [[]] * alto  # Lista de filas, cada una con los �ndices en la paleta de cada p�xel en ella
  tamFila = ancho // 4   # Tama�o de una fila en bytes
  for i in range (alto):  # Cada fila de la imagen
    # Primero van las filas pares, y luego las impares
    numFila = i * 2
    if numFila >= alto:
      if numFila == alto and longFichero == 16384:  # Se acaba de leer la primera mitad de la imagen
        fichero.seek (8192)
      numFila -= alto - 1
    for indiceByte in range (tamFila):  # Cada byte de la fila
      b = carga_int1()  # Byte actual
      fila += [b >> 6, (b >> 4) & 3, (b >> 2) & 3, b & 3]  # Color de los cuatro p�xeles actuales
    imagen[numFila] = fila
    fila = []
  if longFichero == 16384:
    fichero.seek (16382)
    fondo     = carga_int1() & 15
    paleta    = list (paleta1s if carga_int1() & 1 else paleta2s)
    paleta[0] = paletaEGA[fondo]
  else:
    paleta = list (paleta1b)
  return imagen, paleta

def cargaPortadaEGA (fichero):
  """Carga y devuelve una portada EGA junto con su paleta, como �ndices en la paleta de cada p�xel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (1)  # El primer byte es otra cosa (�tal vez el modo gr�fico?)
  ancho = 320
  alto  = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paletaEGA

def cargaPortadaVGA (fichero):
  """Carga y devuelve una portada VGA junto con su paleta, como �ndices en la paleta de cada p�xel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (1)  # El primer byte es otra cosa (�tal vez el modo gr�fico?)
  paleta = cargaPaleta16_6bpc()
  ancho  = 320
  alto   = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paleta

def cargaPaleta16 (bpc, portadaAmiga = False):
  """Carga y devuelve una paleta de 16 colores, con el n�mero de bits por componente de color dado"""
  bytesPaleta = []
  for color in range (16):
    bytesPaleta.append ((carga_int1(), carga_int1()))  # Rojo primero, y luego verde y azul juntos
  ordenAmiga = True  # Si el cuarto bit de componente de color es el m�s significativo
  if not portadaAmiga and bpc == 4 and version > 1 and modo_gfx == 'ST':
    # Es paleta de imagen de BD gr�fica DMG 3+ de Amiga/Atari ST con 4 bpc
    # Vemos si los 4 bytes de la tabla de conversi�n de colores para CGA marcan orden de Amiga, si valen 0xDAADDAAD
    tablaCGA = (carga_int1(), carga_int1(), carga_int1(), carga_int1())
    if tablaCGA != marca_amiga:
      ordenAmiga = False
  valorMax  = (2 ** bpc) - 1   # Valor m�ximo en componentes de color
  distancia = 255. / valorMax  # Distancia para equiespaciar de 0 a 255
  paleta = []
  for color in range (16):
    rojo, veaz = bytesPaleta[color]
    if ordenAmiga:
      rojo  = (rojo        & valorMax) * distancia
      verde = ((veaz >> 4) & valorMax) * distancia
      azul  = (veaz        & valorMax) * distancia
    else:  # Los bits de las componentes de color est�n en el orden de las paletas de Atari STe
      rojo  = ((rojo        & 7) * 2 + (1 if rojo & 8   else 0)) * distancia
      verde = (((veaz >> 4) & 7) * 2 + (1 if veaz & 128 else 0)) * distancia
      azul  = ((veaz        & 7) * 2 + (1 if veaz & 8   else 0)) * distancia
    paleta.append ((int (round (rojo)), int (round (verde)), int (round (azul))))
  return paleta

def cargaPaleta16_6bpc ():
  """Carga y devuelve una paleta de 16 colores, con 6 bits por componente de color, y cada componente en un byte aparte"""
  valorMax  = (2 ** 6) - 1     # Valor m�ximo en componentes de color
  distancia = 255. / valorMax  # Distancia para equiespaciar de 0 a 255
  paleta = []
  for color in range (16):
    rojo  = carga_int1() * distancia
    verde = carga_int1() * distancia
    azul  = carga_int1() * distancia
    paleta.append ((int (round (rojo)), int (round (verde)), int (round (azul))))
  return paleta

def cargaRecursos ():
  """Carga todos los gr�ficos y sonidos de la base de datos gr�fica. Devuelve un mensaje de error si falla"""
  errores = ''
  pos_recursos.clear()
  del recursos[:]
  for numRecurso in range (256):
    cabRecurso = long_cabecera + (long_cabecera_rec * numRecurso)  # Desplazamiento de la cabecera del recurso
    posRecurso = carga_desplazamiento4 (cabRecurso)
    if not posRecurso:
      recursos.append (None)
      continue  # Ning�n recurso con ese n�mero
    banderas = set()
    flags    = carga_int2()
    if flags & 1:
      banderas.add ('flotante')
    if flags & 2:
      banderas.add ('residente')
    if (flags & 4 and version > 1) or (flags & 128 and version < 3):
      banderas.add ('cgaPaleta1')
    if flags & 256 and version > 1:
      banderas.add ('sonido')
    recurso = {'banderas': banderas, 'banderasInt': flags, 'posicion': (carga_int2(), carga_int2())}
    if modo_gfx == 'ST' or version > 1:
      recurso['cambioPaleta'] = (carga_int1(), carga_int1())
    if long_paleta:
      recurso['paleta'] = cargaPaleta16 (4 if version > 1 and modo_gfx == 'ST' else 3)
    elif modo_gfx == 'CGA':
      recurso['paleta'] = paleta1b if 'cgaPaleta1' in banderas else paleta2b
    elif modo_gfx == 'EGA':
      recurso['paleta'] = paletaEGA
    elif modo_gfx == 'PCW':
      recurso['paleta'] = paletaPCW

    if 'sonido' in banderas:
      recursos.append (None)
      continue  # TODO: manejo de recursos de sonido no implementado

    # Detectamos im�genes con el mismo desplazamiento para ahorrar memoria y reducir tiempo de carga
    recurso['desplazamiento'] = posRecurso
    if posRecurso in pos_recursos:
      recurso['dimensiones'] = recursos[pos_recursos[posRecurso][0]]['dimensiones']
      recurso['imagen']      = recursos[pos_recursos[posRecurso][0]]['imagen']
      recursos.append (recurso)
      pos_recursos[posRecurso].append (numRecurso)
      continue
    pos_recursos[posRecurso] = [numRecurso]

    fichero.seek (posRecurso)  # Saltamos a donde est� el recurso (en este caso, imagen)
    if le:
      ancho = carga_int1()  # LSB de la anchura de la imagen
      valor = carga_int1()
    else:
      valor = carga_int1()
      ancho = carga_int1()  # LSB de la anchura de la imagen
    ancho += (valor & 127) * 256
    if ancho == 0 or ancho % 8:
      return 'El ancho de la imagen %d no es mayor que 0 y m�ltiplo de 8, vale %d' % (numRecurso, ancho)
    rle  = valor & 128
    alto = carga_int2()  # Altura de la imagen
    if alto == 0 or alto % 8:
      return 'El alto de la imagen %d no es mayor que 0 y m�ltiplo de 8, vale %d' % (numRecurso, alto)
    recurso['dimensiones'] = (ancho, alto)

    # Secuencias que se repiten para la compresi�n RLE
    repetir = []
    fichero.seek (2, 1)  # Saltamos valor de longitud de la imagen
    if rle:
      if modo_gfx == 'ST' or version > 1:
        bits = carga_int2()  # M�scara de colores que se repetir�n
        for indiceBit in range (16):
          if bits & (2 ** indiceBit):
            repetir.append (indiceBit)
      else:
        b = carga_int1()  # N�mero de secuencias que se repetir�n
        if b > 4:
          return 'Valor inesperado para el n�mero de secuencias que se repetir�n: %d para la imagen %d' % (b, numRecurso)
        for i in range (4):
          if i < b:
            repetir.append (carga_int1())
          else:
            fichero.seek (1, 1)

    # Carga de la imagen en s�
    imagen = []            # �ndices en la paleta de cada p�xel en la imagen
    tamImg = ancho * alto  # Tama�o en p�xeles (y bytes) que tendr� la imagen
    if modo_gfx == 'CGA':
      imagen = cargaImagenCGA (ancho, repetir, tamImg)
    elif modo_gfx in ('EGA', 'PCW'):
      imagen = cargaImagenPlanar (ancho, alto, 4 if modo_gfx == 'EGA' else 1, numRecurso, repetir, tamImg)
    elif version < 3 or (modo_gfx == 'ST' and not rle):  # Formato de Amiga/Atari ST de DMG 1 y de DMG 3+ sin compresi�n
      imagen = cargaImagenAmiga (repetir, tamImg)
    else:  # Formato de DMG3+ de DOS o de Amiga/Atari ST comprimido
      imagen = cargaImagenDMG3DOS (le, numRecurso, repetir, tamImg)

    if type (imagen) == str:  # Ha ocurrido alg�n error al tratar de cargar la imagen
      errores += ('\n' if errores else '') + imagen
      recursos.append (None)
    else:  # Imagen cargada correctamente
      recurso['imagen'] = imagen
      recursos.append (recurso)

  if errores:
    return errores

def comprimeImagenDMG3 (imagen, forzarRLE = False):
  """Devuelve una lista de bytes como enteros con la compresi�n RLE �ptima en el formato de DMG 3+ (el de DMG 1 para Amiga y ST), y una lista de bytes como enteros con las combinaciones que se repiten.

    Si forzarRLE es falso y comprimir la imagen no ahorrar� espacio, devuelve las dos listas vac�as"""
  # Primero calculamos cu�nto se ahorra con cada secuencia de bits
  ahorros       = {}  # Cu�nto ahorrar� cada secuencia
  ocurrencias   = 1   # N�mero de veces seguidas que se ha encontrado el �ltimo valor
  valorAnterior = imagen[0]
  for i in range (1, len (imagen) + 1):
    if i == len (imagen):  # Para procesar tambi�n el �ltimo valor
      valor = None
    else:
      valor = imagen[i]
      if valor == valorAnterior:
        ocurrencias += 1
        continue
    if valorAnterior not in ahorros:
      ahorros[valorAnterior] = 0
    while ocurrencias:
      cuantos = min (16, ocurrencias)
      ahorros[valorAnterior] += cuantos - 2
      ocurrencias -= cuantos
    ocurrencias   = 1
    valorAnterior = valor
  ahorroTotal = 0
  mejores     = []
  for valor in ahorros:
    if ahorros[valor] < 1:
      continue
    mejores.append (valor)
    ahorroTotal += ahorros[valor]
  if not forzarRLE and ahorroTotal < 2:
    return [], []  # La compresi�n RLE en esta imagen no ahorra nada
  # Realizamos la compresi�n RLE
  comprimida  = []  # Imagen comprimida por �ndices en la paleta
  numFila     = 0
  ocurrencias = 1   # N�mero de veces seguidas que se ha encontrado el �ltimo valor
  valorAnterior = imagen[0]
  for i in range (1, len (imagen) + 1):
    if i == len (imagen):  # Para procesar tambi�n el �ltimo valor
      valor = None
    else:
      valor = imagen[i]
    if valorAnterior not in mejores:
      comprimida.append (valorAnterior)
      valorAnterior = valor
      continue
    if valor == valorAnterior:
      ocurrencias += 1
      continue
    while ocurrencias:
      cuantos = min (16, ocurrencias)
      comprimida.append (valorAnterior)
      comprimida.append (cuantos - 1)
      ocurrencias -= cuantos
    ocurrencias   = 1
    valorAnterior = valor
  # Convertimos a bytes la secuencia comprimida
  comprimidaPorBytes = []
  bytesEnGrupo       = 1 if le else 4  # Cu�ntos bytes se guardan cada vez
  nibblesEnGrupo     = bytesEnGrupo * 2
  for c in range (0, len (comprimida), nibblesEnGrupo):
    grupoBytes = []
    for g in range (bytesEnGrupo):
      indiceNibble = c + (g * 2)
      if indiceNibble + 1 >= len (comprimida):
        if indiceNibble < len (comprimida):
          grupoBytes.append (comprimida[indiceNibble])
        while len (grupoBytes) < bytesEnGrupo:
          grupoBytes.append (0)
        break
      grupoBytes.append (comprimida[indiceNibble] + (comprimida[indiceNibble + 1] << 4))
    comprimidaPorBytes.extend (grupoBytes[::-1])
  return comprimidaPorBytes, mejores

def comprimeImagenPlanar (imagen, anchoFilaEnBits, invertirBits, forzarRLE = False):
  """Devuelve una lista de bytes como enteros con la compresi�n RLE �ptima para im�genes planares en el formato de DMG 1, y una lista de bytes como enteros con las combinaciones que se repiten.

    Si forzarRLE es falso y comprimir la imagen no ahorrar� espacio, devuelve las dos listas vac�as"""
  # TODO: soporte de mayor profundidad de color, como ser� necesario en los dem�s formatos aparte de PCW
  # Primero calculamos cu�nto se ahorra con cada secuencia de bits
  ahorros        = {}    # Cu�nto ahorrar� cada secuencia
  izqAder        = True  # Sentido de procesado de p�xeles de la fila actual
  numFila        = 0     # N�mero de fila que se est� procesando
  ocurrencias    = 1     # N�mero de veces seguidas que se ha encontrado el �ltimo valor
  valorAnterior  = imagen[:8]
  for primerBit in range (8, len (imagen) + 8, 8):
    if primerBit % anchoFilaEnBits == 0:
      izqAder  = not izqAder
      numFila += 1
    if primerBit == len (imagen):  # Para procesar tambi�n el �ltimo valor
      valor = []
    else:
      if izqAder:
        valor = imagen[primerBit : primerBit + 8]
      else:
        ultimoBit = ((numFila + 1) * anchoFilaEnBits) - (primerBit % anchoFilaEnBits)
        valor     = imagen[ultimoBit - 8 : ultimoBit]
      if invertirBits:
        valor = valor[::-1]
      if valor == valorAnterior:
        ocurrencias += 1
        continue
    valorComoByte = 0  # Valor anterior como byte
    for indiceBit in range (8):
      valorComoByte += 2 ** indiceBit if valorAnterior[indiceBit] else 0
    if valorComoByte not in ahorros:
      ahorros[valorComoByte] = 0
    while ocurrencias:
      cuantos = min (255, ocurrencias)
      ahorros[valorComoByte] += cuantos - 2
      ocurrencias -= cuantos
    ocurrencias   = 1
    valorAnterior = valor
  ahorroTotal = 0
  mejores     = []
  while ahorros and len (mejores) < 4:
    mejor = max (ahorros, key = ahorros.get)
    if ahorros[mejor] < 1:
      break
    mejores.append (mejor)
    ahorroTotal += ahorros[mejor]
    del ahorros[mejor]
  if not forzarRLE and ahorroTotal < 5:
    return [], []  # La compresi�n RLE en esta imagen no ahorra nada
  # Realizamos la compresi�n RLE
  comprimida    = []
  izqAder       = True
  numFila       = 0
  ocurrencias   = 1  # N�mero de veces seguidas que se ha encontrado el �ltimo valor
  valorAnterior = imagen[:8]
  for primerBit in range (8, len (imagen) + 8, 8):
    if primerBit % anchoFilaEnBits == 0:
      izqAder  = not izqAder
      numFila += 1
    if primerBit == len (imagen):  # Para procesar tambi�n el �ltimo valor
      valor = []
    else:
      if izqAder:
        valor = imagen[primerBit:primerBit + 8]
      else:
        ultimoBit = ((numFila + 1) * anchoFilaEnBits) - (primerBit % anchoFilaEnBits)
        valor = imagen[ultimoBit - 8 : ultimoBit]
      if invertirBits:
        valor = valor[::-1]
    valorComoByte = 0  # Valor anterior como byte
    for indiceBit in range (8):
      valorComoByte += 2 ** indiceBit if valorAnterior[indiceBit] else 0
    if valorComoByte not in mejores:
      comprimida.append (valorComoByte)
      valorAnterior = valor
      continue
    if valor == valorAnterior:
      ocurrencias += 1
      continue
    while ocurrencias:
      cuantos = min (255, ocurrencias)
      comprimida.append (valorComoByte)
      comprimida.append (cuantos)
      ocurrencias -= cuantos
    ocurrencias   = 1
    valorAnterior = valor
  return comprimida, mejores

def detectaFuente8 (fichero):
  """Detecta con heur�sticas la posici�n de memoria que con mayor probabilidad contiene una fuente de 8x8 en el fichero abierto dado, o None si no detect� ninguna o no pudo descartar hasta quedarse con una sola"""
  # Cargamos primero todo el contenido del fichero a memoria para buscar all� m�s r�pidamente
  fichero.seek (0)
  memoria  = fichero.read()
  espacio  = b'\x00' * 8  # Secuencia de un car�cter de espacio en blanco
  medioEsp = b'\x00' * 4  # Secuencia de medio car�cter de espacio en blanco
  inicio   = 0      # Posici�n donde inicia la b�squeda
  posibles = set()  # Posiciones que la heur�stica considera posibles
  posicion = memoria.find (espacio)  # Posici�n donde se ha encontrado (o no) la secuencia

  # Paso de descarte 1
  while posicion > -1 and posicion + 768 <= len (memoria):  # En posicion est� la secuencia de posible car�cter de espacio en blanco
    # Con heur�sticas, averiguamos si hay algo que parece una fuente de 8x8 en posicion
    inicioComa    = posicion      + 12 * 8  # Posici�n donde empezar�a el car�cter ',' en la fuente
    caracterComa  = memoria[inicioComa:inicioComa + 8]
    inicioPunto   = inicioComa    +  2 * 8  # Posici�n donde empezar�a el car�cter '.' en la fuente
    caracterPunto = memoria[inicioPunto:inicioPunto + 8]
    inicioNumeros = inicioPunto   +  2 * 8  # Posici�n donde empezar�a el car�cter '0' en la fuente
    inicioMayusc  = inicioNumeros + 17 * 8  # Posici�n donde empezar�a el car�cter 'A' en la fuente
    inicioMinusc  = inicioMayusc  + 32 * 8  # Posici�n donde empezar�a el car�cter 'a' en la fuente
    if (caracterComa[:4] == medioEsp and caracterPunto[:4] == medioEsp  # La parte superior de la coma y el punto est�n en blanco
        and caracterComa != espacio and caracterPunto != espacio):  # Pero su parte inferior no est� en blanco
      # Vemos que no haya caracteres en blanco en las posiciones de los n�meros y letras
      rangos = ((inicioNumeros, 10), (inicioMayusc, 26), (inicioMinusc, 26))
      for inicioRango, cuantos in rangos:
        for inicioCaracter in range (inicioRango, inicioRango + cuantos * 8, 8):
          if memoria[inicioCaracter:inicioCaracter + 8] == espacio:  # El car�cter de esta posici�n est� en blanco
            break
        else:
          continue  # Ninguno estaba en blanco
        break  # Alg�n car�cter en blanco
      else:
        posibles.add (posicion)
    inicio   = posicion + 1
    posicion = memoria.find (espacio, inicio)
  if traza:
    prn ('Posiciones posibles para fuente de 8x8 en el paso 1:', posibles, file = sys.stderr)

  # Paso de descarte 2
  if len (posibles) > 1:
    # Vemos que no haya ning�n car�cter con pocos p�xeles "encendidos" en las posiciones de los n�meros y letras, salvo '1IJTLijlt'
    import struct
    for posicion in tuple (posibles):
      inicioNumeros = posicion      + 16 * 8  # Posici�n donde empezar�a el car�cter '0' en la fuente
      inicioMayusc  = inicioNumeros + 17 * 8  # Posici�n donde empezar�a el car�cter 'A' en la fuente
      inicioMinusc  = inicioMayusc  + 32 * 8  # Posici�n donde empezar�a el car�cter 'a' en la fuente
      rangos = ((inicioNumeros, 1), (inicioNumeros + 2 * 8, 8), (inicioMayusc, 8), (inicioMayusc + 10 * 8, 1), (inicioMayusc + 12 * 8, 7), (inicioMayusc + 20 * 8, 6), (inicioMinusc, 8), (inicioMinusc + 10 * 8, 1), (inicioMinusc + 12 * 8, 7), (inicioMinusc + 20 * 8, 6))
      for inicioRango, cuantos in rangos:
        for inicioCaracter in range (inicioRango, inicioRango + cuantos * 8, 8):
          bits     = bin (struct.unpack ('=Q', memoria[inicioCaracter:inicioCaracter + 8])[0])[2:]
          bitsAuno = bits.count ('1')
          # prn ('En posicion', posicion, 'de', idAventura, 'el caracter en', inicioCaracter, 'tiene bits a uno:', bitsAuno)
          # prn (bits)
          if bitsAuno < 10:  # Demasiados pocos bits a uno, insuficientes para representar el car�cter
            posibles.remove (posicion)
            break
        else:
          continue  # Todos los caracteres del rango ten�an suficientes bits a uno
        break  # Alg�n car�cter con pocos bits a uno
    if traza:
      prn ('Posiciones posibles para fuente de 8x8 en el paso 2:', posibles, file = sys.stderr)

  # Paso de descarte 3
  if len (posibles) > 1:
    # Vemos que los caracteres de letras min�sculas que normalmente no sobresalen por arriba (acegmnopqrsuvwxyz) no tengan nada en la primera fila
    for posicion in tuple (posibles):
      inicioMinusc = posicion + 65 * 8  # Posici�n donde empezar�a el car�cter 'a' en la fuente
      rangos = ((inicioMinusc, 1), (inicioMinusc + 2 * 8, 1), (inicioMinusc + 4 * 8, 1), (inicioMinusc + 6 * 8, 1), (inicioMinusc + 12 * 8, 7), (inicioMinusc + 20 * 8, 6))
      for inicioRango, cuantos in rangos:
        for inicioCaracter in range (inicioRango, inicioRango + cuantos * 8, 8):
          if memoria[inicioCaracter:inicioCaracter + 1] != b'\x00':
            posibles.remove (posicion)
            break
        else:
          continue  # Todos los caracteres del rango ten�an su primera fila en blanco
        break  # Alg�n car�cter con algo en su primera fila
    if traza:
      prn ('Posiciones posibles para fuente de 8x8 en el paso 3:', posibles, file = sys.stderr)

  # Paso de descarte 4
  if len (posibles) > 1:
    # Vemos que los caracteres de letras min�sculas que normalmente no sobresalen por abajo (abcdehiklmnorstuvwx) no tengan nada en la �ltima fila
    for posicion in tuple (posibles):
      inicioMinusc = posicion + 65 * 8  # Posici�n donde empezar�a el car�cter 'a' en la fuente
      rangos = ((inicioMinusc, 5), (inicioMinusc + 7 * 8, 2), (inicioMinusc + 10 * 8, 5), (inicioMinusc + 17 * 8, 7))
      for inicioRango, cuantos in rangos:
        for inicioCaracter in range (inicioRango, inicioRango + cuantos * 8, 8):
          if memoria[inicioCaracter + 7:inicioCaracter + 8] != b'\x00':
            posibles.remove (posicion)
            break
        else:
          continue  # Todos los caracteres del rango ten�an su �ltima fila en blanco
        break  # Alg�n car�cter con algo en su �ltima fila
    if traza:
      prn ('Posiciones posibles para fuente de 8x8 en el paso 4:', posibles, file = sys.stderr)

  # Paso de descarte 5
  if len (posibles) > 1:
    # Vemos que los caracteres de n�meros y de letras may�sculas est�n centrados verticalmente (que el n�mero de filas vac�as arriba no difiere de las de abajo en m�s de uno)
    for posicion in tuple (posibles):
      alineados = 0
      inicioMayusc = posicion + 33 * 8  # Posici�n donde empezar�a el car�cter 'A' en la fuente
      for inicioCaracter in range (inicioMayusc, inicioMayusc + 26 * 8, 8):
        blancoArriba = 0  # Filas en blanco en el car�cter desde la primera fila en adelante
        blancoAbajo  = 0  # Filas en blanco en el car�cter desde la �ltima fila hacia atr�s
        for numFila in range (0, 4):
          if memoria[inicioCaracter + numFila:inicioCaracter + numFila + 1] == b'\x00':
            blancoArriba += 1
          else:
            break
        for numFila in range (7, 3, -1):
          if memoria[inicioCaracter + numFila:inicioCaracter + numFila + 1] == b'\x00':
            blancoAbajo += 1
          else:
            break
        if abs (blancoArriba - blancoAbajo) < 2:
          alineados += 1
      if alineados < 24:
        posibles.remove (posicion)
    if traza:
      prn ('Posiciones posibles para fuente de 8x8 en el paso 5:', posibles, file = sys.stderr)

  if len (posibles) == 1:
    return posibles.pop()
  return None

def generaPaletaEGA (destino = 'paletas'):
  try:
    os.mkdir (destino)
  except:
    pass  # Asumimos que ese directorio ya existe
  fichero = open (destino + '/ega.xpm', 'wb')
  lineas  = [
    '/* XPM */',
    'static char * ega[] = {',
    '"16 1 16 1",'
  ]
  for i in range (16):
    lineas.append ('"%X c #%02x%02x%02x",' % (i, paletaEGA[i][0], paletaEGA[i][1], paletaEGA[i][2]))
  lineas.extend ((
      '"0123456789ABCDEF",',
      '}',
    ))
  for linea in lineas:
    fichero.write (linea + '\n')
  fichero.close()

def generaPaletasCGA (destino = 'paletas'):
  try:
    os.mkdir (destino)
  except:
    pass  # Asumimos que ese directorio ya existe
  for nombre, paleta in {'1b': paleta1b, '1s': paleta1s, '2b': paleta2b, '2s': paleta2s}.items():
    for i in range (16):
      fichero = open ('%s/cga%s%x.xpm' % (destino, nombre, i), 'wb')
      lineas  = (
        '/* XPM */',
        'static char * cga%s%x[] = {' % (nombre, i),
        '"4 1 4 1",',
        '"0 c #%02x%02x%02x",' % (paletaEGA[i][0], paletaEGA[i][1], paletaEGA[i][2]),
        '"1 c #%02x%02x%02x",' % (paleta[1][0],    paleta[1][1],    paleta[1][2]),
        '"2 c #%02x%02x%02x",' % (paleta[2][0],    paleta[2][1],    paleta[2][2]),
        '"3 c #%02x%02x%02x",' % (paleta[3][0],    paleta[3][1],    paleta[3][2]),
        '"0123",',
        '}',
      )
      for linea in lineas:
        fichero.write (linea + '\n')
      fichero.close()

def guardaImagenPlanar (imagen, ancho, alto, numPlanos):
  """Guarda de modo planar la imagen dada como lista de �ndices, con ancho, alto y n�mero de planos de color dados"""
  bitsPlano = []
  for p in range (numPlanos):
    bitsPlano.append ([])
  for color in imagen:
    for indicePlano in range (numPlanos):
      bitsPlano[indicePlano].append (1 if color & (2 ** indicePlano) else 0)
  for indicePlano in range (numPlanos):
    for primerBit in range (0, len (imagen), 8):
      pixeles       = bitsPlano[indicePlano][primerBit : primerBit + 8]  # Siguientes 8 p�xeles de este plano
      valorComoByte = 0  # Valor como byte de los siguientes 8 p�xeles de este plano
      for indiceBit in range (8):
        valorComoByte += 2 ** indiceBit if pixeles[7 - indiceBit] else 0
      guarda_int1 (valorComoByte)

def guardaPaleta16 (paleta, bpc, ordenAmiga = True):
  """Guarda una paleta de 16 colores, con el n�mero de bits por componente de color dado"""
  for c in range (16):
    if c < len (paleta):
      rojo, verde, azul = paleta[c]
    elif (255, 255, 255) not in paleta:
      rojo, verde, azul = (255, 255, 255)  # Color blanco
    else:
      rojo, verde, azul = (0, 0, 0)  # Color negro
    # Aproximamos el color a los disponibles
    rojo  >>= 8 - bpc
    verde >>= 8 - bpc
    azul  >>= 8 - bpc
    if bpc == 4 and not ordenAmiga:
      # Reordenamos los bits para Atari STE
      rojo  = (rojo  >> 1) + (8 if rojo  & 1 else 0)
      verde = (verde >> 1) + (8 if verde & 1 else 0)
      azul  = (azul  >> 1) + (8 if azul  & 1 else 0)
    guarda_int1 (rojo)
    guarda_int1 ((verde << 4) + azul)

def guardaPaletas (recurso, ordenAmiga):
  """Guarda las paletas de un recurso"""
  if not long_paleta or 'sonido' in recurso:
    return
  # TODO: paletas de 3 bpc
  # TODO: paleta EGA en DMG3+ al menos para plataforma PC
  guardaPaleta16 (recurso['paleta'], 4, ordenAmiga)
  if modo_gfx == 'ST' and version > 1 and ordenAmiga:
    # Marcamos orden de bits de Amiga para formato ST en DMG3+
    for byteMarca in marca_amiga:
      guarda_int1 (byteMarca)
  # TODO: paleta CGA en DMG3+ al menos para plataforma PC

def preparaPlataforma (extension, fichero):
  """Prepara la configuraci�n dependiente de la versi�n, plataforma y modo gr�fico. Devuelve un mensaje de error si falla"""
  global carga_int2, le, long_cabecera, long_cabecera_rec, long_paleta, modo_gfx, version
  # Obtenemos y pre-comprobamos la longitud del fichero
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  if longFichero < 1:
    return 'Fichero vac�o'
  elif longFichero < 4:
    return 'Longitud de fichero insuficiente'
  fichero.seek (0)
  le         = True
  plataforma = carga_int2_be()
  modo       = carga_int2_le()
  if plataforma not in (0, 4, 768, 65535):
    return 'Identificador de plataforma inv�lido'
  if plataforma > 255:  # Formato de DMG 3+
    if modo != 0:
      return 'Identificador de modo gr�fico inv�lido'
    long_cabecera     = 10
    long_cabecera_rec = 48
    long_paleta       = 36
    version           = 3
    if plataforma == 768:
      le       = False
      modo_gfx = 'ST'  # Amiga/Atari ST
    else:
      modo_gfx = 'VGA'
  else:
    long_cabecera     = 6
    long_cabecera_rec = 10
    long_paleta       = 0
    if modo == 0:
      le                = False
      long_cabecera_rec = 44
      long_paleta       = 32
      modo_gfx          = 'ST'  # Amiga/Atari ST
    elif modo == 4:
      if extension in ('.dat', '.pcw'):
        modo_gfx = 'PCW'
      else:
        modo_gfx = 'CGA'
    elif modo == 13:
      modo_gfx = 'EGA'
    else:
      return 'Identificador de modo gr�fico inv�lido'
    version = 1
  if longFichero < (long_cabecera + long_cabecera_rec * 256):
    return 'Longitud de fichero insuficiente'
  if le:
    carga_int2 = carga_int2_le
  else:
    carga_int2 = carga_int2_be
  bajo_nivel_cambia_endian (le)


if __name__ == '__main__':
  generaPaletasCGA()
  generaPaletaEGA()
