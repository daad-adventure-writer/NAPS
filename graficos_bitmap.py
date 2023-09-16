# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería para operar con bases de datos gráficas y otros gráficos de mapa de bits
# Copyright (C) 2008, 2018-2023 José Manuel Ferrer Ortiz
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


# Paleta de colores por defecto de varios modos gráficos, sin reordenar para textos
colores_por_defecto = {
  'VGA': ((  0,   0,   0), (255, 255, 255), (255,   0,   0), (  0, 255,  0),
          (  0,   0, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
          (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
          (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)),
}

# Número de colores de cada modo gráfico
colores_por_modo = {
  'CGA': 4,
  'EGA': 16,
  'PCW': 2,
  'ST':  16,
  'VGA': 16,
}

# Resolución de cada modo gráfico
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

# Paleta blanco y negro, en el orden necesario
paletaBN = ((255, 255, 255), (0, 0, 0))

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

# Paleta PCW en el orden necesario, negro y verde
paletaPCW = ((0, 0, 0), (0, 255, 0))


indice_nuevos     = -1    # Índice para almacenar la posición de nuevos recursos
le                = None  # Si el formato de la base de datos gráfica es Little Endian
long_cabecera     = None  # Longitud de la cabecera de la base de datos
long_cabecera_rec = None  # Longitud de la cabecera de recurso
modo_gfx          = None  # Modo gráfico
pos_recursos      = {}    # Asociación entre cada posición de recurso, y los números de recurso que la usan
recursos          = []    # Gráficos y sonidos de la base de datos gráfica


# Funciones que utilizan el IDE, el editor de bases de datos gráficas, o el intérprete directamente

def cambia_imagen (numRecurso, ancho, alto, imagen, paleta):
  global indice_nuevos
  if recursos[numRecurso]:
    recurso = recursos[numRecurso]
    pos_recursos[recurso['desplazamiento']].remove (numRecurso)
    limpiarPosicion = recurso['desplazamiento']
  else:
    limpiarPosicion = None
    recurso         = {'banderas': set(), 'banderasInt': 0, 'desplazamiento': None, 'posicion': (0, 0)}
  # Vemos si ya había algún recurso con la misma imagen
  for recursoExistente in recursos:
    if not recursoExistente:
      continue  # Saltamos los recursos inexistentes
    if recursoExistente['dimensiones'] == (ancho, alto) and imagen == recursoExistente['imagen']:
      recurso['desplazamiento'] = recursoExistente['desplazamiento']
      pos_recursos[recurso['desplazamiento']].append (numRecurso)
      break
  else:  # No había ninguno con la misma imagen
    recurso['desplazamiento']   = indice_nuevos
    pos_recursos[indice_nuevos] = [numRecurso]
    indice_nuevos -= 1
  # Quitamos la entrada de pos_recursos si ya no queda ninguna imagen con el desplazamiento que tenía la imagen anterior
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
  """Carga a memoria la base de datos gráfica desde el fichero de nombre dado. Devuelve un mensaje de error si falla"""
  global fichero
  try:
    fichero = open (nombreFichero, 'rb')
  except IOError as excepcion:
    return excepcion.args[1]
  extension = nombreFichero[-4:].lower()
  if extension not in ('.cga', '.dat', '.ega', '.pcw'):
    return 'Extensión %s inválida para bases de datos gráficas de DAAD' % extension
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
  """Carga y devuelve una fuente tipográfica de DAAD junto con su paleta, como índices en la paleta de cada píxel, organizados como en fuente.png"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  fichero.seek ((128 if 3200 > longFichero > 2048 else 0) + (16 * 8 if longFichero < 3200 else 0))
  fichero.seek (0)
  ancho  = 628
  alto   = 38 + (0 if longFichero < 3200 else 10)
  imagen = [0] * ancho * alto  # Índices en la paleta de cada píxel en la imagen
  for caracter in range (256 - (16 if longFichero < 3200 else 0)):
    posPorCol  = (caracter % 63) * 10
    posPorFila = (caracter // 63) * 10 * ancho
    for fila in range (8):
      b = carga_int1()  # Byte actual
      for indiceBit in range (8):  # Cada bit del byte actual
        imagen[posPorFila + posPorCol + indiceBit] = 0 if b & (2 ** (7 - indiceBit)) else 1
      posPorFila += ancho
  return imagen, paletaBN

def carga_portada (fichero):
  """Carga y devuelve una portada de DAAD junto con su paleta, como índices en la paleta de cada píxel, detectando su modo gráfico"""
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  fichero.seek (0)
  if longFichero in (16000, 16384):
    return cargaPortadaCGA (fichero, longFichero)
  if longFichero == 32001:
    return cargaPortadaEGA (fichero)
  if longFichero == 32049:
    return cargaPortadaVGA (fichero)
  if longFichero in (32034, 32127):
    return cargaPortadaAmiga (fichero)
  if longFichero == 32066:
    return cargaPortadaAtari (fichero)
  return None

def da_paletas_del_formato ():
  """Devuelve un diccionario con las paletas del formato de base de datos gráfica, que será lista vacía para los modos que soportan paleta variable"""
  if modo_gfx == 'CGA':
    return {'CGA': [paleta1b, paleta2b]}
  if modo_gfx == 'EGA':
    return {'EGA': [paletaEGA]}
  if modo_gfx == 'PCW':
    return {'PCW': [paletaPCW]}
  if modo_gfx in ('ST', 'VGA'):
    return {'CGA': [paleta1b, paleta2b], 'EGA': [paletaEGA], 'ST/VGA': []}

def guarda_bd_pics (fichero):
  """Exporta la base de datos gráfica en memoria sobre el fichero dado"""
  # TODO: completar para el formato de DMG versión 3+
  bajo_nivel_cambia_endian (le)
  bajo_nivel_cambia_sal    (fichero)
  if le:
    guarda_int2 = guarda_int2_le
    guarda_int4 = guarda_int4_le
  else:
    guarda_int2 = guarda_int2_be
    guarda_int4 = guarda_int4_be
  # Guardamos la plataforma y el modo gráfico
  if modo_gfx == 'ST':
    guarda_int2 (4)  # Plataforma Amiga/Atari ST
    guarda_int2 (0)  # No tiene modo gráfico
  else:
    guarda_int2 (0)  # Plataforma DOS/PCW
    if modo_gfx == 'EGA':
      guarda_int2 (13)  # Modo gráfico EGA
    else:
      guarda_int2 (4)  # Modo gráfico CGA/PCW
  # Guardamos el número de imágenes únicas
  guarda_int2 (len (pos_recursos))
  if version > 1:  # Dejamos espacio para la longitud de la base de datos gráfica
    guarda_int4 (0)
  # Dejamos espacio para las cabeceras de los recursos
  if sys.version_info [0] < 3:
    fichero.write (chr (0) * long_cabecera_rec * 256)
  else:
    fichero.write (bytes ([0] * long_cabecera_rec * 256))
  # Guardamos la posición actual para empezar a guardar los datos de los recursos desde aquí
  desplActual = fichero.tell()
  # Ordenamos los recursos de menor a mayor desplazamiento dentro de la base de datos gráfica
  desplazamientos = sorted (pos_recursos.keys())
  if desplazamientos:  # Ponemos los números negativos (los de nuevos recursos) al final
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
    # TODO: resto de formatos aparte de PCW
    # TODO: no forzar compresión de imágenes
    imagen, repetir = comprimeRLEporBytes (recurso['imagen'], recurso['dimensiones'][0], True, forzarRLE = True)
    # Guardamos el contenido del recurso
    # Guardamos el ancho de la imagen y la bandera de compresión RLE
    rle            = 128 if len (imagen) else 0                      # 0 no comprimir, 128 comprimir
    lsbAncho       = recurso['dimensiones'][0] & 255                 # LSB de la anchura de la imagen
    msbAnchoMasRLE = ((recurso['dimensiones'][0] >> 8) & 127) + rle  # MSB de la anchura de la imagen + bit de compresión RLE
    if le:
      guarda_int1 (lsbAncho)
      guarda_int1 (msbAnchoMasRLE)
    else:
      guarda_int1 (msbAnchoMasRLE)
      guarda_int1 (lsbAncho)
    guarda_int2 (recurso['dimensiones'][1])  # Altura de la imagen
    # TODO: no compresión de imágenes
    guarda_int2 (len (imagen) + (5 if rle else 0))  # Longitud de la imagen codificada
    # Guardamos la información para compresión RLE
    if rle:
      guarda_int1 (len (repetir))
      for i in range (4):
        if i < len (repetir):
          guarda_int1 (repetir[i])
        else:
          guarda_int1 (0)
    # Guardamos datos de la imagen en sí
    fichero.write (bytes (imagen))
    # Guardamos la posición actual para guardar el contenido del siguiente recurso aquí
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
      # TODO: guardar la paleta
    desplActual = desplSiguiente
  # Guardamos la longitud de la base de datos gráfica
  if version > 1:
    fichero.seek (6)
    guarda_int4 (desplActual)

def guarda_portada_amiga (imagen, paleta, fichero):
  """Guarda una portada de Amiga en el fichero abierto dado con la imagen dada como lista de índices"""
  bajo_nivel_cambia_sal (fichero)
  guarda_int2_be (0)
  guardaPaleta16 (paleta, 4)
  ancho, alto = resolucion_por_modo['ST']
  guardaImagenPlanar (imagen, ancho, alto, 4)

def recurso_es_unico (numRecurso):
  """Devuelve si el contenido del recurso es único, o si por el contrario es usado por varios recursos"""
  return len (pos_recursos[recursos[numRecurso]['desplazamiento']]) == 1


# Funciones de apoyo de alto nivel

def cargaImagenAmiga (repetir, tamImg):
  """Carga y devuelve una imagen de Amiga/Atari ST con el formato que usan DMG 1 y DMG 3+ en imágenes sin compresión, como lista de índices en la paleta"""
  color     = None  # Índice de color del píxel actual
  imagen    = []    # Índices en la paleta de cada píxel en la imagen
  numPlanos = 4
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    colores = [0] * 8
    for plano in range (numPlanos):
      b = carga_int1()  # Byte actual
      for indiceBit in range (8):
        bit = b & (2 ** indiceBit)
        colores[7 - indiceBit] += (2 ** plano) if bit else 0
    for pixel in range (8):  # Cada píxel en el grupo
      if color == None:
        color = colores[pixel]
        if color in repetir:
          continue  # El número de repeticiones vendrá en el valor del siguiente píxel
      if color in repetir:
        repeticiones = min (colores[pixel] + 1, tamImg - len (imagen))
      else:
        repeticiones = 1
      imagen += [color] * repeticiones
      color   = None
      if len (imagen) == tamImg:
        break
  return imagen

def cargaImagenCGA (ancho, repetir, tamImg):
  """Carga y devuelve una imagen CGA de DMG 1, como lista de índices en la paleta"""
  fila    = []    # Índices en la paleta de cada píxel en la fila actual
  imagen  = []    # Índices en la paleta de cada píxel en la imagen
  izqAder = True  # Sentido de procesado de píxeles de la fila actual
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    b = carga_int1()  # Byte actual
    if b in repetir:
      repeticiones = carga_int1()
    else:
      repeticiones = 1
    pixeles = [b >> 6, (b >> 4) & 3, (b >> 2) & 3, b & 3]  # Color de los cuatro píxeles actuales
    if izqAder:  # Sentido de izquierda a derecha
      fila += pixeles * repeticiones  # Añadimos al final 
    else:  # Sentido de derecha a izquierda
      fila = (pixeles * repeticiones) + fila  # Añadimos al principio
    while len (fila) >= ancho:  # Al repetirse, se puede exceder la longitud de una fila
      if izqAder:  # Sentido de izquierda a derecha
        imagen += fila[0:ancho]
        fila    = fila[ancho:]
      else:  # Sentido de derecha a izquierda
        imagen += fila[-ancho:]
        fila    = fila[:-ancho]
      if repetir:  # Si la imagen usa compresión RLE
        izqAder = not izqAder
  return imagen

def cargaPortadaAmiga (fichero):
  """Carga y devuelve una portada de Amiga junto con su paleta, como índices en la paleta de cada píxel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (2)
  paleta = cargaPaleta16 (4, True)
  ancho  = 320
  alto   = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paleta

def cargaPortadaAtari (fichero):
  """Carga y devuelve una portada de Atari ST junto con su paleta, como índices en la paleta de cada píxel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (2)
  paleta    = cargaPaleta16 (3)
  imagen    = []  # Índices en la paleta de cada píxel en la imagen
  numPlanos = 4
  tamImg    = 320 * 200
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    colores = [0] * 16
    for plano in range (numPlanos):
      b = carga_int2_be()  # Doble byte actual
      for indiceBit in range (16):
        bit = b & (2 ** indiceBit)
        colores[15 - indiceBit] += (2 ** plano) if bit else 0
    for pixel in range (16):  # Cada píxel en el grupo
      imagen += [colores[pixel]]
      if len (imagen) == tamImg:
        break
  return imagen, paleta

def cargaPortadaCGA (fichero, longFichero):
  """Carga y devuelve una portada CGA junto con su paleta, como lista de índices en la paleta de cada fila"""
  bajo_nivel_cambia_ent (fichero)
  ancho   = 320
  alto    = 200
  fila    = []           # Índices en la paleta de cada píxel en la fila actual
  imagen  = [[]] * alto  # Lista de filas, cada una con los índices en la paleta de cada píxel en ella
  tamFila = ancho // 4   # Tamaño de una fila en bytes
  for i in range (alto):  # Cada fila de la imagen
    # Primero van las filas pares, y luego las impares
    numFila = i * 2
    if numFila >= alto:
      if numFila == alto and longFichero == 16384:  # Se acaba de leer la primera mitad de la imagen
        fichero.seek (8192)
      numFila -= alto - 1
    for indiceByte in range (tamFila):  # Cada byte de la fila
      b = carga_int1()  # Byte actual
      fila += [b >> 6, (b >> 4) & 3, (b >> 2) & 3, b & 3]  # Color de los cuatro píxeles actuales
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
  """Carga y devuelve una portada EGA junto con su paleta, como índices en la paleta de cada píxel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (1)  # El primer byte es otra cosa (¿tal vez el modo gráfico?)
  ancho = 320
  alto  = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paletaEGA

def cargaPortadaVGA (fichero):
  """Carga y devuelve una portada VGA junto con su paleta, como índices en la paleta de cada píxel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (1)  # El primer byte es otra cosa (¿tal vez el modo gráfico?)
  paleta = cargaPaleta16_6bpc()
  ancho  = 320
  alto   = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paleta

def cargaImagenDMG3DOS (le, numImagen, repetir, tamImg):
  """Carga una imagen en formato de DMG 3+ para DOS, que también se usa para imágenes de Amiga/Atari ST comprimidas, y la devuelve como lista de índices en la paleta. Devuelve un mensaje de error si falla"""
  cargar  = 1 if le else 4  # Cuántos bytes de valores cargar cada vez, tomando primero el último cargado
  color   = None  # Índice de color del píxel actual
  imagen  = []    # Índices en la paleta de cada píxel en la imagen
  valores = []    # Valores (índices de color y contador de repeticiones) pendientes de procesar, en orden
  while len (imagen) < tamImg:  # Mientras quede imagen por procesar
    if not valores:
      try:
        for i in range (cargar):
          b = carga_int1()  # Byte actual
          valores = [b & 15, b >> 4] + valores  # Los 4 bits más bajos primero, y luego los 4 más altos
      except:
        return 'Imagen %d incompleta. ¿Formato incorrecto?' % numImagen
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

def cargaImagenPlanar (ancho, alto, numPlanos, numImg, repetir, tamImg):
  """Carga una imagen EGA o PCW de DMG 1, modos gráficos PCW monocromo y Amiga y EGA en orden planar con cuatro planos de bit de color enteros consecutivos, y la devuelve como lista de índices en la paleta. Devuelve un mensaje de error si falla"""
  imagen       = [0] * tamImg  # Índices en la paleta de cada píxel en la imagen
  izqAder      = True          # Sentido de procesado de píxeles de la fila actual
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
              return 'Valor inesperado (0) para el número de repeticiones de RLE, en la imagen ' + str (numImg)
          else:
            repeticiones = 1
        except:
          return 'Imagen %d incompleta. ¿Formato incorrecto?' % numImg
        bits = []  # Bits del byte actual
        for indiceBit in range (7, -1, -1):  # Cada bit del byte actual
          bits.append (1 if b & (2 ** indiceBit) else 0)
      cuantas = min (repeticiones, (ancho - len (bitsFila)) // 8)  # Evitamos exceder la longitud de una fila
      if izqAder:  # Sentido de izquierda a derecha
        bitsFila.extend (bits * cuantas)  # Añadimos al final
      else:  # Sentido de derecha a izquierda
        bitsReversa = bits[::-1]
        bitsFila.extend (bitsReversa * cuantas)  # Añadimos al final, pero con los bits invertidos
      repeticiones -= cuantas
      if len (bitsFila) == ancho:  # Al repetir no se excede la longitud de una fila
        if numPlanos == 1 and not repetir:  # Modo PCW sin compresión RLE
          bytesEnFila   = ancho       // 8
          bloquesEnFila = bytesEnFila // 8  # Bloques de 8 bytes por cada fila
          for indiceByte in range (bytesEnFila):
            byte = bitsFila[indiceByte * 8 : (indiceByte * 8) + 8]
            numBloqueDest = numFila // 8      # Índice del bloque de 8 filas, en destino
            numFilaDest   = (indiceByte % 8)  # Índice de fila dentro del bloque, en destino
            numByteDest   = ((numFila % 8) * bloquesEnFila) + (indiceByte // 8)  # Índice del byte dentro de la fila, en destino
            primerPixel   = (numBloqueDest * ancho * 8) + (numFilaDest * ancho) + (numByteDest * 8)  # Índice del primer píxel del byte, en destino
            for indiceBit in range (8):
              bit = byte[indiceBit]
              imagen[primerPixel + indiceBit] += (2 ** plano) if bit else 0
        elif izqAder:  # Sentido de izquierda a derecha
          primerPixel = (numFila * ancho)  # Índice del primer píxel del byte
          for indiceBit in range (ancho):
            bit = bitsFila[indiceBit]
            imagen[primerPixel + indiceBit] += (2 ** plano) if bit else 0
        else:  # Sentido de derecha a izquierda
          ultimoPixel = (numFila * ancho) + ancho - 1  # Índice del último píxel del byte
          for indiceBit in range (ancho):
            bit = bitsFila[indiceBit]
            imagen[ultimoPixel - indiceBit] += (2 ** plano) if bit else 0
        bitsFila = []
        if repetir:  # Si la imagen usa compresión RLE
          izqAder = not izqAder
        numFila += 1
  return imagen

def cargaPaleta16 (bpc, portadaAmiga = False):
  """Carga y devuelve una paleta de 16 colores, con el número de bits por componente de color dado"""
  bytesPaleta = []
  for color in range (16):
    bytesPaleta.append ((carga_int1(), carga_int1()))  # Rojo primero, y luego verde y azul juntos
  ordenAmiga = True  # Si el cuarto bit de componente de color es el más significativo
  if not portadaAmiga and bpc == 4 and version > 1 and modo_gfx == 'ST':
    # Es paleta de imagen de BD gráfica DMG 3+ de Amiga/Atari ST con 4 bpc
    # Vemos si los 4 bytes de la tabla de conversión de colores para CGA marcan orden de Amiga, si valen 0xDAADDAAD
    tablaCGA = (carga_int1(), carga_int1(), carga_int1(), carga_int1())
    if tablaCGA != (0xDA, 0xAD, 0xDA, 0xAD):
      ordenAmiga = False
  valorMax  = (2 ** bpc) - 1   # Valor máximo en componentes de color
  distancia = 255. / valorMax  # Distancia para equiespaciar de 0 a 255
  paleta = []
  for color in range (16):
    rojo, veaz = bytesPaleta[color]
    if ordenAmiga:
      rojo  = (rojo        & valorMax) * distancia
      verde = ((veaz >> 4) & valorMax) * distancia
      azul  = (veaz        & valorMax) * distancia
    else:  # Los bits de las componentes de color están en el orden de las paletas de Atari STe
      rojo  = ((rojo        & 7) * 2 + (1 if rojo & 8   else 0)) * distancia
      verde = (((veaz >> 4) & 7) * 2 + (1 if veaz & 128 else 0)) * distancia
      azul  = ((veaz        & 7) * 2 + (1 if veaz & 8   else 0)) * distancia
    paleta.append ((int (round (rojo)), int (round (verde)), int (round (azul))))
  return paleta

def cargaPaleta16_6bpc ():
  """Carga y devuelve una paleta de 16 colores, con 6 bits por componente de color, y cada componente en un byte aparte"""
  valorMax  = (2 ** 6) - 1     # Valor máximo en componentes de color
  distancia = 255. / valorMax  # Distancia para equiespaciar de 0 a 255
  paleta = []
  for color in range (16):
    rojo  = carga_int1() * distancia
    verde = carga_int1() * distancia
    azul  = carga_int1() * distancia
    paleta.append ((int (round (rojo)), int (round (verde)), int (round (azul))))
  return paleta

def cargaRecursos ():
  """Carga todos los gráficos y sonidos de la base de datos gráfica. Devuelve un mensaje de error si falla"""
  pos_recursos.clear()
  del recursos[:]
  for numRecurso in range (256):
    cabRecurso = long_cabecera + (long_cabecera_rec * numRecurso)  # Desplazamiento de la cabecera del recurso
    posRecurso = carga_desplazamiento4 (cabRecurso)
    if not posRecurso:
      recursos.append (None)
      continue  # Ningún recurso con ese número
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

    # Detectamos imágenes con el mismo desplazamiento para ahorrar memoria y reducir tiempo de carga
    recurso['desplazamiento'] = posRecurso
    if posRecurso in pos_recursos:
      recurso['dimensiones'] = recursos[pos_recursos[posRecurso][0]]['dimensiones']
      recurso['imagen']      = recursos[pos_recursos[posRecurso][0]]['imagen']
      recursos.append (recurso)
      pos_recursos[posRecurso].append (numRecurso)
      continue
    pos_recursos[posRecurso] = [numRecurso]

    fichero.seek (posRecurso)  # Saltamos a donde está el recurso (en este caso, imagen)
    if le:
      ancho = carga_int1()  # LSB de la anchura de la imagen
      valor = carga_int1()
    else:
      valor = carga_int1()
      ancho = carga_int1()  # LSB de la anchura de la imagen
    ancho += (valor & 127) * 256
    if ancho == 0 or ancho % 8:
      return 'El ancho de la imagen %d no es mayor que 0 y múltiplo de 8, vale %d' % (numRecurso, ancho)
    rle  = valor & 128
    alto = carga_int2()  # Altura de la imagen
    if alto == 0 or alto % 8:
      return 'El alto de la imagen %d no es mayor que 0 y múltiplo de 8, vale %d' % (numRecurso, alto)
    recurso['dimensiones'] = (ancho, alto)

    # Secuencias que se repiten para la compresión RLE
    repetir = []
    fichero.seek (2, 1)  # Saltamos valor de longitud de la imagen
    if rle:
      if modo_gfx == 'ST' or version > 1:
        bits = carga_int2()  # Máscara de colores que se repetirán
        for indiceBit in range (16):
          if bits & (2 ** indiceBit):
            repetir.append (indiceBit)
      else:
        b = carga_int1()  # Número de secuencias que se repetirán
        if b > 4:
          return 'Valor inesperado para el número de secuencias que se repetirán: %d para la imagen %d' % (b, numRecurso)
        for i in range (4):
          if i < b:
            repetir.append (carga_int1())
          else:
            fichero.seek (1, 1)

    # Carga de la imagen en sí
    imagen = []            # Índices en la paleta de cada píxel en la imagen
    tamImg = ancho * alto  # Tamaño en píxeles (y bytes) que tendrá la imagen
    if modo_gfx == 'CGA':
      imagen = cargaImagenCGA (ancho, repetir, tamImg)
    elif modo_gfx in ('EGA', 'PCW'):
      imagen = cargaImagenPlanar (ancho, alto, 4 if modo_gfx == 'EGA' else 1, numRecurso, repetir, tamImg)
    elif version < 3 or (modo_gfx == 'ST' and not rle):  # Formato de Amiga/Atari ST de DMG 1 y de DMG 3+ sin compresión
      imagen = cargaImagenAmiga (repetir, tamImg)
    else:  # Formato de DMG3+ de DOS o de Amiga/Atari ST comprimido
      imagen = cargaImagenDMG3DOS (le, numRecurso, repetir, tamImg)

    if type (imagen) == str:
      return imagen

    recurso['imagen'] = imagen
    recursos.append (recurso)

def comprimeRLEporBytes (imagen, anchoFilaEnBits, invertirBits, forzarRLE = False):
  """Devuelve una lista de bytes como enteros con la compresión RLE óptima, y una lista de bytes como enteros con las combinaciones que se repiten.

    Si forzarRLE es falso y comprimir la imagen no ahorrará espacio, devuelve las dos listas vacías"""
  # TODO: soporte de mayor profundidad de color, como será necesario en los demás formatos aparte de PCW
  # Primero calculamos cuánto se ahorra con cada secuencia de bits
  ahorros        = {}    # Cuánto ahorrará cada secuencia
  izqAder        = True  # Sentido de procesado de píxeles de la fila actual
  numFila        = 0     # Número de fila que se está procesando
  ocurrencias    = 1     # Número de veces seguidas que se ha encontrado el último valor
  valorAnterior  = imagen[:8]
  for primerBit in range (8, len (imagen) + 8, 8):
    if primerBit % anchoFilaEnBits == 0:
      izqAder  = not izqAder
      numFila += 1
    if primerBit == len (imagen):  # Para procesar también el último valor
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
    return [], []  # La compresión RLE en esta imagen no ahorra nada
  # Realizamos la compresión RLE
  comprimida    = []
  izqAder       = True
  numFila       = 0
  ocurrencias   = 1  # Número de veces seguidas que se ha encontrado el último valor
  valorAnterior = imagen[:8]
  for primerBit in range (8, len (imagen) + 8, 8):
    if primerBit % anchoFilaEnBits == 0:
      izqAder  = not izqAder
      numFila += 1
    if primerBit == len (imagen):  # Para procesar también el último valor
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
  """Guarda de modo planar la imagen dada como lista de índices, con ancho, alto y número de planos de color dados"""
  bitsPlano = []
  for p in range (numPlanos):
    bitsPlano.append ([])
  for color in imagen:
    for indicePlano in range (numPlanos):
      bitsPlano[indicePlano].append (1 if color & (2 ** indicePlano) else 0)
  for indicePlano in range (numPlanos):
    for primerBit in range (0, len (imagen), 8):
      pixeles       = bitsPlano[indicePlano][primerBit : primerBit + 8]  # Siguientes 8 píxeles de este plano
      valorComoByte = 0  # Valor como byte de los siguientes 8 píxeles de este plano
      for indiceBit in range (8):
        valorComoByte += 2 ** indiceBit if pixeles[7 - indiceBit] else 0
      guarda_int1 (valorComoByte)

def guardaPaleta16 (paleta, bpc):
  """Guarda una paleta de 16 colores, con el número de bits por componente de color dado"""
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
    guarda_int1 (rojo)
    guarda_int1 ((verde << 4) + azul)

def preparaPlataforma (extension, fichero):
  """Prepara la configuración dependiente de la versión, plataforma y modo gráfico. Devuelve un mensaje de error si falla"""
  global carga_int2, le, long_cabecera, long_cabecera_rec, long_paleta, modo_gfx, version
  # Obtenemos y pre-comprobamos la longitud del fichero
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  if longFichero < 1:
    return 'Fichero vacío'
  elif longFichero < 4:
    return 'Longitud de fichero insuficiente'
  fichero.seek (0)
  le         = True
  plataforma = carga_int2_be()
  modo       = carga_int2_le()
  if plataforma not in (0, 4, 768, 65535):
    return 'Identificador de plataforma inválido'
  if plataforma > 255:  # Formato de DMG 3+
    if modo != 0:
      return 'Identificador de modo gráfico inválido'
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
      return 'Identificador de modo gráfico inválido'
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
