# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería para operar con bases de datos gráficas de DAAD
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

from bajo_nivel import *


# Paletas CGA 1 y 2 con y sin brillo, en el orden necesario
paleta1b = ((0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255))
paleta2b = ((0, 0, 0), (85, 255,  85), (255, 85,  85), (255, 255,  85))
paleta1s = ((0, 0, 0), ( 0, 170, 170), (170,  0, 170), (170, 170, 170))
paleta2s = ((0, 0, 0), ( 0, 170,   0), (170,  0,   0), (170,  85,   0))

# Paleta EGA en el orden necesario
paletaEGA = ((  0,  0,  0), (  0,  0, 170), (  0, 170,  0), (  0, 170, 170),
             (170,  0,  0), (170,  0, 170), (170,  85,  0), (170, 170, 170),
             ( 85, 85, 85), ( 85, 85, 255), ( 85, 255, 85), ( 85, 255, 255),
             (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255))

# Paleta PCW en el orden necesario, negro y verde
paletaPCW = ((0, 0, 0), (0, 255, 0))


le                = None  # Si el formato de la base de datos gráfica es Little Endian
long_cabecera     = None  # Longitud de la cabecera de la base de datos
long_cabecera_rec = None  # Longitud de la cabecera de recurso
modo_gfx          = None  # Modo gráfico
pos_recursos      = {}    # Asociación entre cada posición de recurso, y el primer número de recurso que la usa
recursos          = []    # Gráficos y sonidos de la base de datos gráfica


# Funciones que utilizan el IDE, el editor de bases de datos gráficas, o el intérprete directamente

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
  for funcion, parametros in ((preparaPlataforma, [extension]), (cargaRecursos, ())):
    try:
      msgError = funcion (*parametros)
      if msgError:
        fichero.close()
        return msgError
    except Exception as excepcion:
      fichero.close()
      return excepcion.args[0]
  fichero.close()


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
        repeticiones = colores[pixel] + 1
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

def cargaPortada (fichero):
  """Carga y devuelve una portada de DAAD junto con su paleta, como índices en la paleta de cada píxel, detectando su modo gráfico"""
  fichero.seek (0, os.SEEK_END)
  longFichero = fichero.tell()
  fichero.seek (0)
  if longFichero == 16384:
    return cargaPortadaCGA (fichero)
  if longFichero == 32001:
    return cargaPortadaEGA (fichero)
  if longFichero == 32034:
    return cargaPortadaAmiga (fichero)
  if longFichero == 32066:
    return cargaPortadaAtari (fichero)
  return None

def cargaPortadaAmiga (fichero):
  """Carga y devuelve una portada de Amiga junto con su paleta, como índices en la paleta de cada píxel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (2)
  paleta = cargaPaleta16 (4)
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

def cargaPortadaCGA (fichero):
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
      if numFila == alto:  # Se acaba de leer la primera mitad de la imagen
        fichero.seek (8192)
      numFila -= alto - 1
    for indiceByte in range (tamFila):  # Cada byte de la fila
      b = carga_int1()  # Byte actual
      fila += [b >> 6, (b >> 4) & 3, (b >> 2) & 3, b & 3]  # Color de los cuatro píxeles actuales
    imagen[numFila] = fila
    fila = []
  fichero.seek (16382)
  fondo     = carga_int1() & 15
  paleta    = list (paleta1s if carga_int1() & 1 else paleta2s)
  paleta[0] = paletaEGA[fondo]
  return imagen, paleta

def cargaPortadaEGA (fichero):
  """Carga y devuelve una portada EGA junto con su paleta, como índices en la paleta de cada píxel"""
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (1)  # El primer byte es otra cosa (¿tal vez el modo gráfico?)
  ancho = 320
  alto  = 200
  return cargaImagenPlanar (ancho, alto, 4, 0, [], ancho * alto), paletaEGA

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

def cargaPaleta16 (bpc):
  """Carga y devuelve una paleta de 16 colores, con el número de bits por componente de color dado"""
  valorMax  = (2 ** bpc) - 1   # Valor máximo en componentes de color
  distancia = 255. / valorMax  # Distancia para equiespaciar de 0 a 255
  paleta = []
  for color in range (16):
    rojo  = carga_int1()
    rojo  = (rojo & valorMax) * distancia
    veaz  = carga_int1()
    verde = ((veaz >> 4) & valorMax) * distancia
    azul  = (veaz & valorMax) * distancia
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
    recurso = {'banderas': banderas, 'posicion': (carga_int2(), carga_int2())}
    if modo_gfx == 'ST' or version > 1:
      recurso['cambioPaleta'] = (carga_int1(), carga_int1())
    if long_paleta:
      recurso['paleta'] = cargaPaleta16 (3)
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
    if posRecurso in pos_recursos:
      recurso['dimensiones'] = recursos[pos_recursos[posRecurso]]['dimensiones']
      recurso['imagen']      = recursos[pos_recursos[posRecurso]]['imagen']
      recursos.append (recurso)
      continue
    pos_recursos[posRecurso] = numRecurso

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
        'static char * cga%s%x[] = {\n' % (nombre, i),
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

def preparaPlataforma (extension):
  """Prepara la configuración dependiente de la versión, plataforma y modo gráfico. Devuelve un mensaje de error si falla"""
  global carga_int2, le, long_cabecera, long_cabecera_rec, long_paleta, modo_gfx, version
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
  if le:
    carga_int2 = carga_int2_le
  else:
    carga_int2 = carga_int2_be
  bajo_nivel_cambia_endian (le)


if __name__ == '__main__':
  generaPaletasCGA()
