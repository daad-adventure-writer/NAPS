#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Intérprete de sistemas PAW-like
# Copyright (C) 2010, 2018-2025 José Manuel Ferrer Ortiz
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

from alto_nivel import *
from prn_func   import prn

import argparse  # Para procesar argumentos de línea de comandos
import os        # Para soporte multiplataforma
import random    # Para choice y seed
import re        # Para quitar acentos en GAC
import sys       # Para exit, salida estándar, y argumentos de línea de comandos
import types     # Para poder comprobar si algo es una función


# Variables de estado del intérprete

banderas       = []     # Banderas del sistema
conjunciones   = []     # Palabras que son conjunciones
dicc_vocab     = {}     # Vocabulario como diccionario, con el texto de las palabras como claves
doall_activo   = []     # Si hay bucle DOALL activo, guarda puntero al condacto DOALL activo
frases         = []     # Buffer de órdenes parseadas por ejecutar, cuando el jugador tecleó más de una
locs_objs      = []     # Localidades de los objetos
marcadores     = []     # Marcadores en sistemas GAC (banderas de tipo booleano, con valor 0 ó 1)
orden          = ''     # Orden a medio obtener (para tiempo muerto)
orden_psi      = ''     # Parte de la orden entrecomillada
partida        = []     # Partida guardada mediante RAMSAVE
peso_llevable  = [0]    # Peso máximo llevable en sistemas GAC  # TODO: hacer con bandera de sistema
peso_llevado   = [0]    # Peso total de objetos llevados y puestos
pila_datos     = []     # Pila de datos en sistemas GAC
pila_procs     = []     # Pila con estado de los procesos en ejecución
proceso_acc    = False  # Guarda si el proceso ejecutó alguna acción adecuada
proceso_ok     = None   # Guarda si el proceso terminó con DONE u OK (True), NOTDONE (False) o ninguno de estos (None)
pronombre      = ''     # Alguna palabra que sea pronombre
puntos_ruptura = []     # Puntos de ruptura donde pausar la ejecución

modulos = []     # Módulos de condactos cargados
traza   = False  # Si queremos una traza de la ejecución

frase_guardada = []     # Tendrá valor verdadero cuando se está ejecutando la segunda frase introducida o posterior
hay_asterisco  = False  # Si está la palabra '*', 1, 255 en el vocabulario, en sistema PAWS no compilado (con editor)


# Constantes (o casi) del intérprete

BANDERA_VERBO      = 33  # Bandera con el verbo de la SL actual
BANDERA_NOMBRE     = 34  # Bandera con el primer nombre de la SL actual
BANDERA_LOC_ACTUAL = 38  # Bandera con la localidad actual

acentos    = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'ñ': 'n', 'Ñ': 'N'}
er_acentos = re.compile ('|'.join (re.escape (c) for c in acentos.keys()))

# Funciones auxiliares para los módulos de condactos

def adapta_msgs_sys ():
  """Adapta los mensajes de sistema de la base de datos para las interfaces de texto"""
  if args.gui in ('stdio', 'telegram'):
    msgs_sys[243 if NOMBRE_SISTEMA == 'GAC' else 16] = ''  # Mensaje de espera una tecla
  if args.gui == 'telegram' and len (msgs_sys) > 32:
    if NOMBRE_SISTEMA == 'GAC':
      if msgs_sys[240][:1] == '>':  # Es un prompt y no una petición como 'What now?'
        msgs_sys[240] = ''
    else:
      msgs_sys[33] = ''  # Prompt

def busca_condacto (firma):
  """Busca en los módulos de condactos la función donde está implementado el condacto con la firma dada"""
  firma = firma.replace ('?', '_')
  for modulo in modulos:
    if firma in modulo.__dict__:
      return modulo.__dict__[firma]
  prn ('FIXME: Condacto con firma', firma, 'no implementado')
  sys.exit()

def busca_conexion (locOrigen):
  """Busca en las entradas de locOrigen en la tabla de conexiones el verbo de la SL actual, y devuelve la localidad de destino, o bien None si no estaba"""
  if (type (conexiones) == list and locOrigen >= len (conexiones)) or (type (conexiones) == dict and locOrigen not in conexiones):
    return None
  for verbo, destino in conexiones[locOrigen]:
    if verbo == banderas[BANDERA_VERBO]:  # Verbo de la SL actual
      return destino
  return None

def cambia_articulo (texto, mayusculas = False):
  if not texto:
    return texto
  articulo = texto.split()[0].lower()
  if articulo in ('a', 'an', 'some', 'the'):  # Artículos en inglés
    return texto[len (articulo) + 1:]  # Quita el artículo
  elif articulo in ('um', 'uma', 'uns', 'umas'):  # Artículos en portugués
    if articulo == 'uns':
      texto = 'os ' + texto[4:]
    elif articulo == 'um':
      texto = 'o ' + texto[3:]
    else:
      texto = texto[2:]
  elif articulo == 'un':
    texto = 'el ' + texto[3:]
  elif compatibilidad:
    if articulo[:2] == 'un':
      texto = 'l' + texto[2:]  # XXX: verificado que lo hace así el intérprete original
  else:
    if articulo == 'una':
      texto = 'la ' + texto[4:]
    elif articulo == 'unas':
      texto = 'las ' + texto[5:]
    elif articulo == 'unos':
      texto = 'los ' + texto[5:]
  if mayusculas:
    return texto[0].upper() + texto[1:]
  return texto

def da_peso (objeto, nivel = 0):
  """Devuelve el peso total del objeto dado, teniendo en cuenta que puede ser un contenedor"""
  peso = atributos[objeto] & 63  # Peso del objeto
  if peso and atributos[objeto] & 64 and nivel < 10:  # Es un contenedor con peso (si no tiene, no cuenta contenido)
    for i in range (len (locs_objs)):
      if locs_objs[i] == objeto:
        peso += da_peso (i, nivel + 1)
  return peso

def imprime_mensaje (texto):
  if not texto:
    return
  objetoReferido = ''
  if NOMBRE_SISTEMA != 'QUILL' and banderas[51] < len (desc_objs):
    objetoReferido = desc_objs[banderas[51]]
    if '.' in objetoReferido:
      objetoReferido = objetoReferido[:objetoReferido.index ('.')]
  if NOMBRE_SISTEMA == 'DAAD':
    iniParte = 0
    partes   = []
    for i in range (len (texto)):
      if texto[i] in ('\x0b', '\x0c'):  # Equivale a '\b', '\k'
        if i:
          partes.append (texto[iniParte:i])
        partes.append (texto[i])
        iniParte = i + 1
    if iniParte <= i:
      partes.append (texto[iniParte:])
  else:
    partes = [texto]
  tiempoTimeout = banderas[48] if NOMBRE_SISTEMA != 'QUILL' and banderas[49] & 2 else 0
  for parte in partes:
    if parte == '\x0b':  # Equivale a \b
      busca_condacto ('a0_CLS') ()
    elif parte == '\x0c':  # Equivale a \k
      gui.espera_tecla()
    elif '_' in parte:
      gui.imprime_cadena (parte.replace ('_', cambia_articulo (objetoReferido)), tiempo = tiempoTimeout)
    elif '@' in parte and NOMBRE_SISTEMA == 'DAAD':
      gui.imprime_cadena (parte.replace ('@', cambia_articulo (objetoReferido, True)), tiempo = tiempoTimeout)
    else:
      gui.imprime_cadena (parte, tiempo = tiempoTimeout)

def obj_referido (objeto):
  """Asigna el objeto dado como nuevo objeto referido actual. Usar el valor 255 para limpiar las banderas de objeto referido"""
  if objeto == 255:
    banderas[51] = 255
    for numBandera in range (54, 60 if NOMBRE_SISTEMA == 'DAAD' and nueva_version else 58):
      banderas[numBandera] = 0
    return
  banderas[51] = objeto
  banderas[54] = locs_objs[objeto]
  banderas[55] = da_peso (objeto)
  banderas[56] = 128 if atributos[objeto] &  64 else 0  # Si es contenedor
  banderas[57] = 128 if atributos[objeto] & 128 else 0  # Si es prenda
  # FIXME: ¿se pondría en la bandera 58 los atributos normales en versión de formato 1?
  if NOMBRE_SISTEMA == 'DAAD' and nueva_version:
    banderas[58] = atributos_extra[objeto] // 256
    banderas[59] = atributos_extra[objeto]  % 256

def parsea_orden (psi, mensajesInvalida = True):
  """Obtiene e interpreta la orden del jugador para rellenar la sentencia lógica actual, o la del PSI entrecomillada. Devuelve verdadero si la frase no es válida o ha ocurrido tiempo muerto"""
  return prepara_orden (True, psi, mensajesInvalida) != None

def prepara_vocabulario ():
  """Prepara el diccionario con el vocabulario, y la lista conjunciones"""
  global hay_asterisco, pronombre
  dicc_vocab.clear()
  del conjunciones[:]
  pronombre = 'Pronombre'
  for palabraVoc in vocabulario:
    if palabraVoc[2] < len (TIPOS_PAL):
      if palabraVoc[0] not in dicc_vocab:
        dicc_vocab[palabraVoc[0]] = []
      dicc_vocab[palabraVoc[0]].append (tuple (palabraVoc[1:]))
      tipo = TIPOS_PAL_ES[palabraVoc[2]]
      if tipo == 'Conjuncion':
        conjunciones.append (palabraVoc[0])
      elif tipo == 'Pronombre':
        pronombre = palabraVoc[0]
    elif NOMBRE_SISTEMA == 'PAWS' and palabraVoc[0] == '*' and palabraVoc[1] == 1 and palabraVoc[2] == 255:
      hay_asterisco = True

def restaura_objetos ():
  """Restaura las localidades iniciales de los objetos, ajusta el número de objetos llevados (bandera 1) y calcula el peso total (llevado + puesto)"""
  global peso_llevado
  peso_llevado[0] = 0
  banderas[1]     = 0
  for i in range (num_objetos[0]):
    locs_objs[i] = locs_iniciales[i]
    if locs_objs[i] in (253, 254):  # De paso, contamos los objetos llevados, y calculamos el peso total
      if locs_objs[i] == 254:
        banderas[1] += 1  # Número de objetos llevados, pero no puestos
      if NUM_ATRIBUTOS[0]:
        peso_llevado[0] += da_peso (i)

# FIXME: cambiar el intérprete para registrar si se registró alguna acción o no
def tabla_hizo_algo ():
  """Devuelve si la última tabla que terminó, lo hizo habiendo ejecutado alguna acción, o terminando con DONE, pero no con NOTDONE"""
  return proceso_acc


# Funciones que implementan el intérprete tipo-PAWS

def bucle_daad_nuevo ():
  """Bucle principal del intérprete, para últimas versiones de DAAD"""
  while True:
    inicializa()
    valor = True
    while valor:
      valor = ejecuta_proceso (0)
      if valor == 7:  # Terminar completamente la aventura
        return
    if valor == False:
      continue  # Se reinicia la aventura
    return

def bucle_gac ():
  """Bucle principal del intérprete, para sistema GAC"""
  estado = 0  # Estado del intérprete
  while True:
    if estado == 0:  # Inicialización
      gui.borra_pantalla()
      for i in range (NUM_BANDERAS[0]):
        banderas[i] = 0
      banderas[BANDERA_LOC_ACTUAL] = loc_inicio[0]
      for i in range (NUM_MARCADORES):
        marcadores[i] = 0
      for numObjeto in locs_iniciales:
        locs_objs[numObjeto] = locs_iniciales[numObjeto]
      estado = 1
    elif estado < 2:  # Descripción de localidad y condiciones de alta prioridad
      # Describir localidad actual
      descLocActual = desc_locs[banderas[BANDERA_LOC_ACTUAL]] if banderas[BANDERA_LOC_ACTUAL] in desc_locs else ''
      gui.imprime_cadena (descLocActual)
      # Listar objetos presentes
      pila_datos.append (banderas[BANDERA_LOC_ACTUAL])
      busca_condacto ('a0_LIST') (msgs_sys[253])
      estado = 3 if estado > 1 else 2
    elif estado == 2:  # Condiciones de alta prioridad
      # Ejecutar las condiciones de alta prioridad
      valor = ejecuta_proceso (0)
      if valor == False:  # Fin de la aventura
        if args.gui in ('stdio', 'telegram'):
          return  # Terminamos completamente la aventura
        estado = 0  # Reiniciamos el juego
      elif valor == True:  # Si la tabla de condiciones termina con algo equivalente a DESC en PAWS
        estado = 1.5
        # El intérprete original tras imprimir la descripción de localidad por esto, salta a pedir orden sin revisar la tabla de condiciones de alta prioridad
        # TODO: revisar si sólo ocurre aquí, o si hace lo mismo en los estados 4 y 5
      elif valor != True:
        estado = 3
    elif estado == 3:  # Obtener orden y comprobar conexiones
      gui.imprime_cadena ('\n')
      prepara_orden_gac()
      incrementa_turno()
      # Comprobar tabla de conexiones
      destino = busca_conexion (banderas[BANDERA_LOC_ACTUAL])  # De la localidad actual
      if destino == None:
        estado = 4
      else:
        banderas[BANDERA_LOC_ACTUAL] = destino
        estado = 1
    elif estado == 4:  # Condiciones locales
      # Ejecutar las condiciones de la localidad actual
      if banderas[BANDERA_LOC_ACTUAL] in tablas_proceso:
        valor = ejecuta_proceso (banderas[BANDERA_LOC_ACTUAL])
      if valor == False:  # Fin de la aventura
        if args.gui in ('stdio', 'telegram'):
          return  # Terminamos completamente la aventura
        estado = 0  # Reiniciamos el juego
      elif valor == True:  # Si la tabla de condiciones termina con algo equivalente a DESC en PAWS
        estado = 1
      elif valor == 9:  # Pedir orden
        estado = 2
      else:
        estado = 5
    elif estado == 5:  # Condiciones de baja prioridad
      valor = ejecuta_proceso (10000)
      if valor == False:  # Fin de la aventura
        if args.gui in ('stdio', 'telegram'):
          return  # Terminamos completamente la aventura
        estado = 0  # Reiniciamos el juego
      elif valor == True:  # Si la tabla de condiciones termina con algo equivalente a DESC en PAWS
        estado = 1
      elif valor == 9:  # Pedir orden
        estado = 2
      else:
        gui.imprime_cadena (msgs_sys[242 if banderas[BANDERA_VERBO] == 0 else 241])
        estado = 2

def bucle_paws ():
  """Bucle principal del intérprete, para PAWS y primeras versiones de DAAD"""
  estado = 0  # Estado del intérprete
  while True:
    if estado == 0:  # Inicialización
      inicializa()
      estado = 1
      turnos = True  # Si se incrementará el número de turnos
    elif estado == 1:  # Descripción de localidad y Proceso 1
      describe_localidad()
      valor = ejecuta_proceso (1)
      if valor == False:  # Hay que reiniciar la aventura
        estado = 0
      elif valor == 7:  # Terminar completamente la aventura
        return
      # Si el proceso 1 termina con DESC, seguimos en este estado
      elif valor != True:
        estado = 2
    elif estado == 2:  # Proceso 2 y obtener orden
      valor = ejecuta_proceso (2) if len (tablas_proceso) > 2 else None
      if valor == False:  # Hay que reiniciar la aventura
        estado = 0
      elif valor == 7:  # Terminar completamente la aventura
        return
      if valor == 8:  # Saltar a procesar la tabla de respuestas
        estado = 3
        turnos = False
      elif valor == True:  # Ha terminado con DESC
        estado = 1  # Saltamos a la descripción de la localidad
      else:
        # Mientras no tengamos una orden válida, reiniciaremos este estado
        if obtener_orden() != True:
          estado = 3
    elif estado == 3:  # Incremento de turno y Tabla de respuestas
      if turnos:
        incrementa_turno()
      turnos = True
      valor  = ejecuta_proceso (0)
      if valor == False:  # Hay que reiniciar la aventura
        estado = 0
      elif valor == True:  # Ha terminado con DESC
        estado = 1  # Saltamos a la descripción de la localidad
      elif valor == 7:  # Terminar completamente la aventura
        return
      elif valor == 8:  # Saltar a procesar la tabla de respuestas
        estado = 3
        turnos = False
      elif proceso_ok:  # Ha terminado con DONE u OK
        estado = 2
      # TODO: ¡parece que en Jabato sí lo hace! Al menos tras un DOALL sin objetos que encajen, y tras un NOTDONE
      elif NOMBRE_SISTEMA in ('PAWS', 'QUILL'):  # Ni SWAN ni DAAD buscan automáticamente en la tabla de conexiones, para eso la aventura debe usar MOVE 38 y demás
        estado = 4
      else:
        estado = 5
    elif estado == 4:  # Búsqueda en tabla de conexiones
      destino = busca_conexion (banderas[BANDERA_LOC_ACTUAL])  # De la localidad actual
      if destino == None:
        estado = 5
      else:
        banderas[BANDERA_LOC_ACTUAL] = destino
        estado = 1
    elif estado == 5:  # Tablas de respuestas y de conexiones exhaustas, o se terminó con NOTDONE
      tiempoTimeout = banderas[48] if NOMBRE_SISTEMA != 'QUILL' and banderas[49] & 2 else 0
      if not proceso_acc:  # No se ha ejecutado ninguna "acción"
        if banderas[BANDERA_VERBO] >= (13 if NOMBRE_SISTEMA == 'QUILL' else 14):  # No es verbo de dirección
          gui.imprime_cadena (msgs_sys[8], tiempo = tiempoTimeout)  # No puedes hacer eso
        elif NOMBRE_SISTEMA in ('QUILL', 'PAWS'):  # Ni SWAN ni DAAD imprimen este mensaje por sí mismos
          gui.imprime_cadena (msgs_sys[7], tiempo = tiempoTimeout)  # No puedes ir por ahí
      estado = 2

def inicializa ():
  """Hace lo que dice la guía técnica de PAWS, página 7: 1.- LA INICIALIZACIÓN DEL SISTEMA"""

  # Los colores de fondo y el juego de caracteres son seleccionados
  gui.juego = 0  # Seleccionamos el juego bajo
  if 'colores_inicio' in libreria.__dict__ and libreria.colores_inicio:  # Cargamos los colores de inicio
    gui.cambia_color_tinta (libreria.colores_inicio[0])
    gui.cambia_color_papel (libreria.colores_inicio[1])
    gui.cambia_color_borde (libreria.colores_inicio[2])
    if len (libreria.colores_inicio) > 3:
      gui.cambia_color_brillo (libreria.colores_inicio[3])
    gui.elige_subventana (gui.elegida)  # Para que se apliquen los colores iniciales a la fuente

  # Las banderas son puestas a 0, las primeras 248 en el caso de las primeras versiones de DAAD, y todas en los demás
  for i in range (248 if NOMBRE_SISTEMA == 'DAAD' and not nueva_version else NUM_BANDERAS[0]):
    banderas[i] = 0
  # excepto:

  # No lo dice la Guía Técnica, pero las localidades de los objetos deben restaurarse a las localidades iniciales
  if NOMBRE_SISTEMA != 'DAAD' or not nueva_version:  # Pero en nuevas versiones de DAAD, sólo RESET lo hace
    restaura_objetos()

  # La bandera 37, contiene el número máximo de objetos llevados, que se pondrá a 4
  if NOMBRE_SISTEMA != 'QUILL':
    banderas[37] = 4
    # La bandera 52, lleva el máximo peso permitido, que se pone a 10
    banderas[52] = 10
    # Las banderas 46 y 47, que llevan el pronombre actual, que se pondrán a 255
    # (no hay pronombre)
    banderas[46] = 255
    banderas[47] = 255

  del frases[:]
  del gui.historial[:]

  if NOMBRE_SISTEMA == 'DAAD' or (NOMBRE_SISTEMA == 'PAWS' and extension == 'sna'):
    gui.reinicia_subventanas()  # Inicializamos las subventanas de impresión
    if NOMBRE_SISTEMA == 'DAAD':
      # La subventana predeterminada es la 1
      gui.elige_subventana (1)
      banderas[63] = 1
      if nueva_version:  # Carga la paleta por defecto, evitando hacerlo en modo CGA (que de momento sólo está para DAAD v1)
        gui.carga_paleta_defecto()

  # Permitimos que la librería inicialice banderas de modo distinto a la inicialización PAWS estándar
  if 'inicializa_banderas' in libreria.__dict__:
    libreria.inicializa_banderas (banderas)

def describe_localidad ():
  """Hace lo que dice la guía técnica de PAWS, página 7: 2.- DESCRIPCIÓN DE LA LOCALIDAD ACTUAL"""
  # Si la bandera 2 no está a cero, será decrementada en 1
  if banderas[2] > 0:
    banderas[2] -= 1

  # Si está oscuro (que la bandera 0 no es cero) y la bandera 3 no es cero,
  # entonces la bandera 3 es decrementada
  if (banderas[0] > 0) and (banderas[3] > 0):
    banderas[3] -= 1

  # Si está oscuro, la bandera 4 no está a cero y el objeto 0 (la fuente de luz)
  # está ausente, la bandera 4 es decrementada
  if (banderas[0] > 0) and (banderas[4] > 0) and busca_condacto ('c1_ABSENT') (0):
    banderas[4] -= 1

  # Se hace una limpieza de pantalla (clear) si el contenido del modo de
  # pantalla (el que se contiene en la bandera 40) es par
  # Según http://graemeyeandle.atwebpages.com/advent/pawtech.html debe ser así,
  # en lugar de si no está a 1, como decía la guía técnica en papel
  if NOMBRE_SISTEMA == 'QUILL':
    gui.borra_pantalla()
  elif NOMBRE_SISTEMA == 'PAWS' and not banderas[40] & 1:
    if gui.elegida == 2:  # Se había usado PROTECT
      gui.elige_subventana (1)
    gui.borra_pantalla()

  # Si está oscuro y el objeto 0 está ausente, entonces el Mensaje del Sistema 0
  # (el que se refiere al mensaje "está muy oscuro para ver") se imprime
  if (banderas[0] > 0) and busca_condacto ('c1_ABSENT') (0):
    gui.borra_todo()  # TODO: ver si hay que borrar sólo el gráfico (subventana 0)
    if NOMBRE_SISTEMA == 'DAAD':
      busca_condacto ('a1_WINDOW') (1)
      gui.mueve_cursor (0, 0)
    gui.imprime_cadena (msgs_sys[0])
  # Si no, cualquier gráfico presente para la localidad es dibujado, y la
  # descripción de la localidad en texto aparecerá sin hacer un NEWLINE
  else:
    actualiza_grafico()

    if desc_locs[banderas[BANDERA_LOC_ACTUAL]]:
      gui.imprime_cadena (desc_locs[banderas[BANDERA_LOC_ACTUAL]], tiempo = banderas[48] if NOMBRE_SISTEMA != 'QUILL' and banderas[49] & 2 else 0)

    # Lista objetos presentes en QUILL
    if NOMBRE_SISTEMA == 'QUILL':
      # TODO: ver si esta nueva línea se debe escribir aunque no haya objetos en la localidad actual
      # TODO: ver si es correcto que restaure los colores en caso de haber objetos en la localidad actual, modificando una BD para poner algo en la localidad inicial, y vaciarle el mensaje de sistema 1 (También puedo ver)
      gui.imprime_cadena ('\n', restauraColores = True)
      alguno = False
      for objno in range (num_objetos[0]):
        if locs_objs[objno] == banderas[BANDERA_LOC_ACTUAL]:
          if not alguno:
            gui.imprime_cadena (msgs_sys[1] + '\n')
            alguno = True
          gui.imprime_cadena (desc_objs[objno] + '\n')

def actualiza_grafico ():
  """Actualiza el gráfico de localidad con el de la localidad actual, si ésta tiene gráfico, o quita el gráfico de localidad"""
  global imagenesSWAN
  if NOMBRE_SISTEMA == 'DAAD':
    if gui.hay_grafico (banderas[38]):
      busca_condacto ('a1_WINDOW') (0)
      gui.borra_pantalla()
      gui.dibuja_grafico (banderas[38], True)
    busca_condacto ('a1_WINDOW') (1)
    if not banderas[40] & 1:
      gui.borra_pantalla()
    else:
      gui.mueve_cursor (0, 0)
  elif NOMBRE_SISTEMA == 'SWAN':
    if 'imagenesSWAN' not in globals():  # Lista para conversión de número de localidad a número de gráfico
      from graficos_bitmap import imagenesSWAN
      prefijoAventura = args.bbdd[-12:-7].lower()
      if prefijoAventura in imagenesSWAN:
        imagenesSWAN  = imagenesSWAN[prefijoAventura]
        gui.grf_borde = imagenesSWAN['caracterBorde']
      else:
        imagenesSWAN = {'imagenPorLocalidad': tuple (range (len (desc_locs)))}
    if banderas[38] < len (imagenesSWAN['imagenPorLocalidad']):
      numImagen = imagenesSWAN['imagenPorLocalidad'][banderas[38]]
    else:
      numImagen = imagenesSWAN['imagenPorDefecto']
    if gui.hay_grafico (numImagen):
      subventanaAntes = gui.elegida  # Así sabremos si antes había gráfico o no
      gui.elige_subventana (0)
      gui.dibuja_grafico (numImagen, True)
      gui.elige_subventana (2)
      if subventanaAntes != 2:  # Antes no había gráfico
        gui.pos_subventana (0, 10)
        gui.cambia_topes   (0, 0)  # Topes al máximo tamaño posible
    else:  # No se dispone de ese gráfico, así que el texto lo pondremos a pantalla completa
      gui.elige_subventana (1)
      if gui.elegida == 2:  # Justo antes de describir esta localidad sí había gráfico
        gui.mueve_cursor (gui.cursores[2][0], gui.cursores[2][1] + 10)  # Recuperamos el cursor a la posición equivalente a pantalla completa
  else:
    gui.dibuja_grafico (banderas[BANDERA_LOC_ACTUAL], True)

def obtener_orden ():
  """Hace lo que dice la guía técnica de PAWS, páginas 8 y 9: 5.- COGER LA FRASE

Devuelve True si la frase no es válida o ha ocurrido tiempo muerto (para que vuelva a buscar en la tabla de proceso 2)"""
  # Si las banderas 5 a la 8 no están a cero, son decrementadas (la versión en español de la guía técnica dice de la 7 a la 8, pero es una errata)
  for i in range (5, 9):
    if banderas[i] > 0:
      banderas[i] -= 1

  # Si está oscuro (la bandera 0 no está a cero) y la bandera cero no está a 9,
  # entonces se decrementa
  if (banderas[0] != 0) and (banderas[9] > 0):
    banderas[9] -= 1

  # Si está oscuro y la bandera 10 no está a cero, será decrementada si el
  # objeto 0 está ausente
  if (banderas[0] > 0) and (banderas[10] > 0) and busca_condacto ('c1_ABSENT') (0):
    banderas[10] -= 1

  return prepara_orden() != None

def prepara_orden (espaciar = False, psi = False, mensajesInvalida = True):
  """Prepara una orden de las pendientes de ejecutar u obtiene una nueva

Devuelve None si la frase es válida, True si no, False si ha ocurrido tiempo muerto"""
  global frases, orden, orden_psi, traza
  # Borramos las banderas de SL actual
  if NUM_BANDERAS[0] > 70:  # De PAWS en adelante
    banderasSL = {BANDERA_VERBO: 'Verbo', BANDERA_NOMBRE: 'Nombre1', 35: 'Adjetivo1', 36: 'Adverbio', 43: 'Preposicion', 44: 'Nombre2', 45: 'Adjetivo2'}
  else:  # Quill
    banderasSL = {BANDERA_VERBO: 'Verbo', BANDERA_NOMBRE: 'Nombre1'}
  for i in banderasSL:
    banderas[i] = 255
  # Si no hay órdenes ya parseadas pendientes de ejecutar
  if not frases:
    if not psi:
      if frase_guardada:
        del frase_guardada[:]  # Fin de ejecución de frases pendientes de ejecutar
        gui.borra_orden()

      # Si el buffer de input está vacío
      if not orden:
        # se imprime el mensaje que contenga la bandera 42.
        if NUM_BANDERAS[0] < 256 or banderas[42] == 0:  # En Quill o si tiene un valor igual a 0,
          # los mensajes 2-5 serán seleccionados con una frecuencia de
          # 30:30:30:10, respectivamente
          peticion = random.choice ((2, 2, 2, 3, 3, 3, 4, 4, 4, 5))
        else:
          peticion = banderas[42]
        peticion = msgs_sys[peticion]
      else:
        peticion = ''
      # Quitamos la marca de tiempo muerto
      if NUM_BANDERAS[0] > 70 and banderas[49] & 128:  # De PAWS en adelante
        banderas[49] ^= 128
      # Aunque no lo vea en la Guía Técnica, se imprime el mensaje 33 justo antes de esperar la orden
      if NUM_BANDERAS[0] > 70 and len (msgs_sys) > 32:
        peticion += msgs_sys[33]
      elif args.gui != 'telegram':
        peticion += '\n>'  # Prompt de QUILL
        if args.gui == 'pygame':  # Nos aseguramos que la orden no vaya en inversa
          if gui.cod_inversa_fin:
            peticion += chr (gui.cod_inversa_fin)
          elif gui.cod_inversa:
            peticion += chr (gui.cod_inversa)
      if traza:
        gui.imprime_banderas  (banderas)
        gui.imprime_locs_objs (locs_objs)
      timeout = [banderas[48]] if NUM_BANDERAS[0] > 70 and (not orden or not banderas[49] & 1) else [0]

      ordenObtenida = False
      while not ordenObtenida:
        orden = gui.lee_cadena (peticion, orden, timeout, espaciar, timeout[0] and banderas[49] & 1)
        # Activamos o desactivamos la depuración paso a paso
        if type (timeout[0]) == int and args.gui != 'telegram' and orden.strip().lower() == '*debug*':
          orden = ''
          traza = not traza
          gui.abre_ventana (traza, args.scale, args.bbdd)
          gui.borra_orden()
          if traza:
            gui.banderas_antes = None  # Que siempre dibuje los números de bandera
            gui.imprime_banderas  (banderas)
            gui.imprime_locs_objs (locs_objs)
        else:
          ordenObtenida = True

      # Si ha vencido el tiempo muerto, el mensaje de sistema 35 aparece, y se
      # vuelve a la búsqueda en la tabla de proceso 2
      if type (timeout[0]) != int:
        # TODO: comentado hasta que se pueda elegir modo de compatibilidad no estricto, porque no veo bien borrar la orden ya escrita
        # if compatibilidad and gui.centrar_graficos:  # En la Aventura Original, la orden se borra cuando hay timeout
        #   orden = ''
        if (NOMBRE_SISTEMA != 'DAAD' or not nueva_version) and msgs_sys[35]:  # Evitamos imprimir una línea en blanco sin necesidad
          gui.imprime_cadena (msgs_sys[35])
          gui.imprime_cadena ('\n')
        banderas[49] |= 128  # Indicador de tiempo muerto vencido
        return False

    # Una frase es sacada y convertida en una sentencia lógica, por medio de la
    # conversión de cualquier palabra en ella presente, que esté en el
    # vocabulario, a su número de palabra y poniéndola luego en la bandera
    # requerida
    if psi:
      ordenes = separa_orden (orden_psi)
    else:
      ordenes = separa_orden (orden)
    if traza:
      prn ('Orden' + (' de PSI ' if psi else ' ') + 'partida en estas frases:', ordenes)
    for f in range (len (ordenes)):
      frase = {'Verbo': None, 'Nombre1': None, 'Nombre2': None, 'Adjetivo1': None, 'Adjetivo2': None, 'Adverbio': None, 'Preposicion': None, 'Pronombre': None}
      preposicionSinNombre = False  # Si se encuentra una preposición antes que ningún nombre
      if len (TIPOS_PAL) == 1:  # Como en Quill
        for palabra in ordenes[f]:
          for codigo, tipo in dicc_vocab.get (palabra, ()):
            if not frase['Verbo']:
              frase['Verbo'] = codigo
            elif not frase['Nombre1']:
              frase['Nombre1'] = codigo
      else:  # Hay más de un tipo de palabra
        for palabra in ordenes[f]:
          if palabra == pronombre:
            frase['Pronombre'] = palabra
            continue
          for codigo, tipo in dicc_vocab.get (palabra, ()):
            tipo = TIPOS_PAL_ES[tipo]
            if tipo in ('Verbo', 'Adverbio', 'Preposicion', 'Pronombre'):
              if tipo == 'Preposicion' and not frase['Nombre1'] and not frase['Adjetivo1']:
                preposicionSinNombre = True
              if not frase[tipo]:
                frase[tipo] = codigo
                break  # Palabra ya procesada
            elif tipo in ('Nombre', 'Adjetivo'):
              if frase['Pronombre']:
                if not frase['Nombre1'] and not frase['Adjetivo1']:  # Hubo Pronombre antes que Nombre o Adjetivo
                  frase[tipo + '2'] = codigo
                  break  # Palabra ya procesada
              elif frase['Preposicion'] and not preposicionSinNombre:
                if not frase[tipo + '2']:
                  frase[tipo + '2'] = codigo
                  break  # Palabra ya procesada
              elif frase[tipo + '1']:
                frase[tipo + '2'] = codigo
                break  # Palabra ya procesada
              else:
                frase[tipo + '1'] = codigo
                break  # Palabra ya procesada
            else:
              if not ide and args.gui != 'telegram':
                import pdb
                pdb.set_trace()
              pass  # Tipo de palabra inesperado
            if compatibilidad:
              break  # No hay palabras iguales de más de un tipo, pasamos a la siguiente palabra
      if not frase['Verbo']:
        if frase['Nombre1']:
          if frase['Nombre1'] < NOMB_COMO_VERB[0] and not frase['Preposicion']:  # Con nombre que actúa como verbo
            frase['Verbo'] = frase['Nombre1']
          elif f and frases[-1]['Verbo']:  # Verbo heredado de la frase anterior
            frase['Verbo'] = frases[-1]['Verbo']
        elif frase['Preposicion'] and frase['Preposicion'] < PREP_COMO_VERB:  # Con preposición que actúa como verbo
          # TODO: ver si esto ocurre también en PAWS y/o en DAAD
          frase['Verbo'] = frase['Preposicion']
      frases.append (frase)
    if len (frases) > 1:
      del texto_nuevo[:]  # Hay más de una orden, por lo queremos saber cuándo se escribe texto nuevo
  else:  # Había frases pendientes de ejecutar
    gui.espera_tecla()
    frase_guardada.append (True)
  if not frases:  # Sólo se escribió espacio en blanco, conjunciones o ,.;:
    if not psi and (NOMBRE_SISTEMA != 'DAAD' or not nueva_version):
      gui.imprime_cadena (msgs_sys[6])  # No entendí nada
      gui.borra_orden()
    if psi:
      orden_psi = ''
    else:
      orden = ''
    return True

  frase  = frases.pop (0)
  valida = True
  if frase['Verbo']:
    # Cargamos pronombres
    if frase['Pronombre']:
      if frase['Nombre1']:
        if not frase['Nombre2']:
          frase['Nombre2']   = banderas[46]
          frase['Adjetivo2'] = banderas[47]
      else:
        frase['Nombre1']   = banderas[46]
        frase['Adjetivo1'] = banderas[47]
    # Guardamos las palabras de la frase en las banderas correspondientes
    for flagno, tipo in banderasSL.items():
      banderas[flagno] = frase[tipo] if frase[tipo] else 255
    if len (TIPOS_PAL) > 1 and frase['Nombre1'] and frase['Nombre1'] >= 50:  # Guardamos pronombres, sólo para nombres considerados no propios (código >= 50)
      banderas[46] = frase['Nombre1']
      banderas[47] = frase['Adjetivo1'] if frase['Adjetivo1'] else 255
    # TODO: ver cuándo se cambia o vacía el último objeto referido
    # XXX: en el PARSE de nueva_version, lo vaciaba tras convertir nombre que actuaba como verbo
  else:
    # Si no se encuentra una frase válida, entonces se muestra el mensaje de sistema 6, y vuelve a buscar al proceso 2
    tiempoTimeout = banderas[48] if NOMBRE_SISTEMA != 'QUILL' and banderas[49] & 2 else 0
    valida = False
    if frase['Nombre1']:
      if psi or NOMBRE_SISTEMA == 'DAAD':
        for flagno, tipo in {34: 'Nombre1', 44: 'Nombre2'}.items():
          banderas[flagno] = frase[tipo] if frase[tipo] else 255
        valida = True
      else:
        gui.imprime_cadena (msgs_sys[8], tiempo = tiempoTimeout)  # No puedes hacer eso
    elif not psi and mensajesInvalida and (NOMBRE_SISTEMA != 'DAAD' or not nueva_version):
      gui.imprime_cadena (msgs_sys[6], tiempo = tiempoTimeout)  # No entendí nada

  if psi:
    orden_psi = ''  # Vaciamos ya la orden
  else:
    if not valida:
      del frases[:]  # Dejamos de procesar frases

    orden = ''  # Vaciamos ya la orden
    if NUM_BANDERAS[0] > 70:
      banderas[49] &= 127  # Quitamos el indicador de tiempo muerto vencido
    if not frases:
      gui.borra_orden()

  if not valida:
    return True

def prepara_orden_gac ():
  # type: () -> None
  """Prepara una orden de las pendientes de ejecutar u obtiene una nueva"""
  global frases, traza
  # Borramos las banderas de SL actual
  banderasSL = {BANDERA_VERBO: 'Verbo', BANDERA_NOMBRE: 'Nombre1', BANDERA_ADVERBIO: 'Adverbio', BANDERA_NOMBRE2: 'Nombre2'}
  for i in banderasSL:
    banderas[i] = 0
  # Si no hay órdenes ya parseadas pendientes de ejecutar
  if not frases:
    if frase_guardada:
      del frase_guardada[:]  # Fin de ejecución de frases pendientes de ejecutar
      gui.borra_orden()

    peticion = ''
    if args.gui != 'telegram':
      peticion = msgs_sys[240]  # Prompt de GAC
    if traza:
      gui.imprime_banderas  (banderas)
      gui.imprime_locs_objs (locs_objs)

    ordenObtenida = False
    while not ordenObtenida:
      orden = gui.lee_cadena (peticion)
      # Activamos o desactivamos la depuración paso a paso
      if args.gui != 'telegram' and orden.strip().lower() == '*debug*':
        orden = ''
        traza = not traza
        gui.abre_ventana (traza, args.scale, args.bbdd)
        gui.borra_orden()
        if traza:
          gui.banderas_antes = None  # Que siempre dibuje los números de bandera
      elif orden:
        ordenObtenida = True
      if traza:
        gui.imprime_banderas  (banderas)
        gui.imprime_locs_objs (locs_objs)

    ordenes = separa_orden (orden)
    if traza:
      prn ('Orden partida en estas frases:', ordenes)
    for f in range (len (ordenes)):
      frase = {'Verbo': None, 'Nombre1': None, 'Nombre2': None, 'Adverbio': None, 'Pronombre': None}
      for palabra in ordenes[f]:
        if palabra == pronombre:
          frase['Pronombre'] = palabra
          continue
        for codigo, tipo in dicc_vocab.get (palabra, ()):
          tipo = TIPOS_PAL_ES[tipo]
          if tipo in ('Verbo', 'Adverbio', 'Pronombre'):
            if not frase[tipo]:
              frase[tipo] = codigo
              break  # Palabra ya procesada
          elif tipo == 'Nombre':
            if frase['Pronombre']:
              if not frase['Nombre1']:  # Hubo Pronombre antes que Nombre
                frase['Nombre2'] = codigo
                break  # Palabra ya procesada
            elif frase['Nombre1']:
              frase['Nombre2'] = codigo
              break  # Palabra ya procesada
            else:
              frase['Nombre1'] = codigo
              break  # Palabra ya procesada
          else:
            if not ide and args.gui != 'telegram':
              import pdb
              pdb.set_trace()
            pass  # Tipo de palabra inesperado
      if not frase['Verbo']:
        if frase['Nombre1'] and f and frases[-1]['Verbo']:  # Verbo heredado de la frase anterior
          frase['Verbo'] = frases[-1]['Verbo']
      frases.append (frase)
    if len (frases) > 1:
      del texto_nuevo[:]  # Hay más de una orden, por lo queremos saber cuándo se escribe texto nuevo
  else:  # Había frases pendientes de ejecutar
    gui.espera_tecla()
    frase_guardada.append (True)
  if not frases:  # Sólo se escribió espacio en blanco, conjunciones o ,.;:
    gui.borra_orden()
    return

  frase = frases.pop (0)
  if frase['Verbo']:
    # Cargamos pronombres
    if frase['Pronombre']:
      if frase['Nombre1']:
        if not frase['Nombre2']:
          frase['Nombre2'] = banderas[BANDERA_PRONOMBRE]
      else:
        frase['Nombre1'] = banderas[BANDERA_PRONOMBRE]
    # Guardamos las palabras de la frase en las banderas correspondientes
    for flagno, tipo in banderasSL.items():
      banderas[flagno] = frase[tipo] if frase[tipo] else 0
    if frase['Nombre1']:  # Guardamos como pronombre el último nombre usado
      banderas[BANDERA_PRONOMBRE] = frase['Nombre2'] if frase['Nombre2'] else frase['Nombre1']

  orden = ''  # Vaciamos ya la orden
  if not frases:
    gui.borra_orden()

def ejecuta_condacto (codigo, parametros):
  """Ejecuta el condacto con el código y parámetros dados

Devuelve el modo en que el condacto altera el flujo de ejecución:
  -X: pasa a ejecutar el subproceso X (como PROCESS)
   0: termina la ejecución y reinicia la aventura (como END)
   1: termina la ejecución y pasa a describir la localidad (como DESC)
   2: reinicia la ejecución de la tabla actual (como REDO de DAAD)
   3: termina la ejecución de la tabla actual con éxito (como DONE)
   4: termina la ejecución de la tabla actual con fallo (como NOTDONE)
   5: termina la ejecución de la tabla actual sin más detalle (como fallo GET)
   6: termina la entrada de tabla actual (como una condición que no se cumple)
   7: termina completamente la ejecución de la aventura
   8: termina la ejecución y pasa a ejecutar la tabla de respuestas
   9: termina la ejecución y pasa a pedir orden al jugador (como WAIT de GAC)
None: pasa al siguiente condacto"""
  global proceso_acc
  if libreria.INDIRECCION and codigo > 127:  # Si el sistema soporta indirección
    if traza and codigo == 220:  # Condacto DEBUG (NEWTEXT con indirección)
      return None
    codigo    -= 128
    indirecto  = True
  else:
    indirecto = False
  condacto = libreria.condactos[codigo]
  firma    = ('a' if condacto[2] else 'c') + str (condacto[1] if type (condacto[1]) == int else len (condacto[1])) + '_' + condacto[0]
  funcion  = busca_condacto (firma)
  if indirecto and parametros:
    parametros = [banderas[parametros[0]]] + parametros[1:]
  valor = funcion (*parametros)  # El * saca los parámetros de la lista
  if condacto[2] == False:  # El condacto es una condición
    if NOMBRE_SISTEMA != 'GAC' and codigo in (20, 106) and valor == True:  # QUIT, MOVE
      proceso_acc = True
    if valor == False:  # No se cumple
      return 6
    if valor == True:  # Se cumple
      return None
    return valor  # Permite que condactos se comporten como acción y condición, como QUIT de PAWS
  if NOMBRE_SISTEMA != 'GAC':
    if codigo == 103 or (codigo == 85 and valor == 4):  # NOTDONE, o DOALL que termina con NOTDONE
      proceso_acc = False
    elif codigo not in (75, 108, 116):  # PROCESS, REDO, SKIP
      proceso_acc = True
  return valor

def ejecuta_pasos (numPasos):
  """Ejecuta un número dado de pasos de ejecución

Un paso es la comparación de una cabecera o la ejecución de un condacto.

Devuelve True si ha ejecutado DESC o equivalente. False si se debe reiniciar la aventura"""
  global pila_procs, proceso_ok, punto_ruptura_actual
  try:
    punto_ruptura_actual
  except:
    punto_ruptura_actual = ()
  for paso in range (numPasos):
    if traza and numPasos > 1 and paso:
      imprime_condacto()
    # Obtenemos los índices de tabla, entrada y condacto actuales
    numTabla, numEntrada, numCondacto = pila_procs[-1]
    # Paramos en puntos de ruptura
    if (numTabla, numEntrada, numCondacto) in puntos_ruptura:
      if punto_ruptura_actual != (numTabla, numEntrada, numCondacto):
        punto_ruptura_actual = (numTabla, numEntrada, numCondacto)
        sys.stdout.flush()  # Que se imprima todo lo que quede
        return
      punto_ruptura_actual = ()
    tabla = tablas_proceso[numTabla]
    cambioFlujo = 0
    if numCondacto == -1 and tabla[0]:  # Toca comprobar la cabecera
      cabecera = tabla[0][numEntrada]
      if (NOMBRE_SISTEMA == 'DAAD' or numTabla not in (1, 2)) and (
          (not hay_asterisco and ((cabecera[0] not in (255, banderas[BANDERA_VERBO])) or (cabecera[1] not in (255, banderas[BANDERA_NOMBRE])))) or
          (hay_asterisco and ((cabecera[0] not in (1, 255, banderas[33])) or (cabecera[1] not in (1, 255, banderas[34]))))):
         cambioFlujo = 6  # No encaja la cabecera
      elif tabla[1][numEntrada]:  # Ha encajado la cabecera, y la entrada tiene algún condacto
        pila_procs[-1][2] = 0  # Apuntamos al primer condacto
        continue
      else:  # Ha encajado la cabecera, pero la entrada está vacía
        cambioFlujo = 6  # Continuamos para que pase correctamente al siguiente condacto o entrada
    if tabla[0]:  # La tabla no está vacía
      # Toca ejecutar un condacto (o saltar la entrada si la cabecera no encaja)
      entrada = tabla[1][numEntrada]
      if cambioFlujo == 0:  # La cabecera encajó (ahora o en su momento)
        # Dejamos de ejecutar pasos tras ANYKEY, LOAD, PARSE de órdenes del jugador, y DEBUG
        if traza and NOMBRE_SISTEMA != 'GAC' and entrada[numCondacto][0] in (24, 26, 73, 220):
          # Aseguramos que PARSE sea de órdenes del jugador, que será con parámetro 0
          if entrada[numCondacto][0] != 73 or (entrada[numCondacto][1] and not entrada[numCondacto][1][0]):
            paso = numPasos
            sys.stdout.flush()  # Que se imprima todo lo que quede
        cambioFlujo = ejecuta_condacto (entrada[numCondacto][0], entrada[numCondacto][1])
      if type (cambioFlujo) == int:
        if cambioFlujo < 0:  # Ejecutar subproceso
          prepara_tabla_proceso (-cambioFlujo)
          continue
        if cambioFlujo in (0, 1, 8, 9):  # Terminar todo
          del doall_activo[:]
          del pila_procs[:]
          if cambioFlujo == 0:  # Reiniciar aventura
            gui.borra_todo()  # TODO: se hace en DAAD, ver si también lo hace PAWS
            proceso_ok = None
            return False
          # cambioFlujo in (1, 8, 9):  # Saltar a describir la localidad, a ejecutar el proceso 0, o a pedir orden
          proceso_ok = True  # TODO: comprobar si esto es así
          if cambioFlujo == 1:
            return True
          return cambioFlujo
        if cambioFlujo == 2:  # Reiniciar tabla actual
          numEntrada  = 0
          numCondacto = -2
        elif cambioFlujo < 6:  # Terminar tabla
          if doall_activo and numTabla == doall_activo[0]:
            numEntrada  = doall_activo[1]
            numCondacto = doall_activo[2] - 1
          else:
            numEntrada  = len (tabla[0])
            numCondacto = -2
          if cambioFlujo == 3:  # Con éxito
            proceso_ok = True
          elif cambioFlujo == 4:  # Con fallo
            proceso_ok = False
          else:  # cambioFlujo == 5:  # Sin más detalle
            proceso_ok = None
        elif cambioFlujo == 6:  # Terminar entrada actual
          numCondacto = len (entrada)
        elif cambioFlujo == 7:  # Terminar completamente la aventura
          del pila_procs[:]
          return 7
      elif cambioFlujo != None:  # Saltar al inicio de una entrada contigua
        numEntrada  += cambioFlujo[0] + 1
        numCondacto  = -2
    else:
      entrada = []
    # Pasamos al siguiente condacto
    while True:
      numCondacto += 1
      if numCondacto >= len (entrada):  # Se ha terminado esta entrada
        numCondacto  = -1
        numEntrada  += 1
      if numEntrada >= len (tabla[0]):  # Se ha terminado esta tabla
        if doall_activo and numTabla == doall_activo[0]:
          numEntrada  = doall_activo[1]
          numCondacto = doall_activo[2]
          break
        pila_procs.pop()
        if not pila_procs:  # No quedan más tablas en ejecución
          break
        # Obtenemos los índices de tabla, entrada y condacto de la tabla antigua
        numTabla, numEntrada, numCondacto = pila_procs[-1]
        tabla   = tablas_proceso[numTabla]
        entrada = tabla[1][numEntrada]
        continue
      break
    if pila_procs:  # Queda alguna tabla en ejecución
      pila_procs[-1][1] = numEntrada
      pila_procs[-1][2] = numCondacto
    else:
      return
    if paso == numPasos:
      return  # Dejamos de ejecutar el resto de pasos

def ejecuta_proceso (num_proceso):
  """Ejecuta una tabla de proceso hasta que esta termine

Devuelve True si termina con DESC o equivalente. False si hay que reiniciar la aventura"""
  prepara_tabla_proceso (num_proceso)
  while True:
    if traza:
      gui.imprime_banderas  (banderas)
      gui.imprime_locs_objs (locs_objs)
      imprime_condacto()
      pasos = tecla_o_fin()  # Ejecutaremos 1, 10, 100 ó 1000 pasos a la vez, según qué se pulse
    else:
      pasos = 10000
    valor = ejecuta_pasos (pasos)
    if valor != None:
      return valor
    if not pila_procs:
      if ide:
        prn (pila_procs)  # Avisamos al IDE que se ha vaciado la pila de procesos
      return  # Ha concluido la ejecución de la tabla

def imprime_condacto ():
  """Imprime en la salida estándar el siguiente condacto que se ejecutará"""
  if ide:
    prn (pila_procs)
    return
  # Obtenemos los índices de tabla, entrada y condacto actuales
  num_tabla, num_entrada, num_condacto = pila_procs[-1]
  tabla = tablas_proceso[num_tabla]
  if num_condacto == -1 and not num_entrada and not tabla[0]:  # Tabla vacía
    prn ('[' + str (num_tabla) + ']')
    return
  prn (pila_procs[-1], ': ', sep = '', end = '')
  # Imprimimos la cabecera si corresponde hacerlo ahora
  if num_condacto == -1:
    cabecera = tabla[0][num_entrada]
    if cabecera[0] == 255:
      prn ('_', end = ' ')
    elif hay_asterisco and cabecera[0] == 1:
      prn ('*', end = ' ')
    else:
      if len (TIPOS_PAL) > 1 and cabecera[0] < NOMB_COMO_VERB[0]:  # Podría ser un nombre convertible en verbo
        idTipos = (cabecera[0], 0), (cabecera[0], 2)
      else:
        idTipos = ((cabecera[0], 0),)
      for palabra in vocabulario:
        if palabra[1:] in idTipos:
          prn (palabra[0].rstrip().upper(), end = ' ')
          break
      else:  # Palabra no encontrada, así que imprimimos el número
        prn (cabecera[0], end = ' ')
    if cabecera[1] == 255:
      prn ('_')
    elif hay_asterisco and cabecera[1] == 1:
      prn ('*')
    else:
      if len (TIPOS_PAL) > 1:
        idTipo = (cabecera[1], 2)
      else:
        idTipo = (cabecera[1], 0)
      for palabra in vocabulario:
        if palabra[1:] == idTipo:
          prn (palabra[0].rstrip().upper())
          break
      else:  # Palabra no encontrada, así que imprimimos el número
        prn (cabecera[1])
    return
  entrada = tabla[1][num_entrada]
  condacto, parametros = entrada[num_condacto]
  if condacto > 127 and libreria.INDIRECCION:  # Condacto indirecto
    condacto -= 128
    indirecto = True
  else:
    indirecto = False
  condacto = libreria.condactos[condacto]
  prn (condacto[0].ljust (7), '@' if indirecto else ' ', end = '')
  for parametro in parametros:
    prn (str (parametro).rjust (3), end = ' ')
  prn()
  if condacto[0] in ('ANYKEY', 'HOLD'):  # Dejará las banderas actualizadas al momento de esta pausa
    gui.imprime_banderas  (banderas)
    gui.imprime_locs_objs (locs_objs)

def incrementa_turno ():
  """Incrementa el número de turnos jugados"""
  banderaTurnosLSB = 31
  banderaTurnosMSB = 32
  if NUM_BANDERAS[0] == 68:  # Quill para Sinclair QL
    banderaTurnosLSB = 62
    banderaTurnosMSB = 61
  elif NOMBRE_SISTEMA == 'GAC':
    banderaTurnosLSB += 95
    banderaTurnosMSB += 95
  banderas[banderaTurnosLSB] += 1
  if banderas[banderaTurnosLSB] > 255:
    banderas[banderaTurnosLSB]  = 0
    banderas[banderaTurnosMSB] += 1

def prepara_tabla_proceso (num_tabla):
  """Cambia el flujo de ejecución para que se ejecute la tabla de proceso num_tabla"""
  global proceso_acc, proceso_ok
  proceso_acc = False
  if not pila_procs:  # Pila de procesos vacía
    proceso_ok = None
  pila_procs.append ([num_tabla, 0, -1])  # Índices de tabla, entrada y condacto
  if len (pila_procs) > 10:
    prn ('ERROR PAW: Límite alcanzado: anidación máxima de subprocesos (10)')
    sys.exit()  # Salimos del programa

def separa_orden (orden):
  """Separa la orden por frases y palabras, recortadas a LONGITUD_PAL"""
  global orden_psi
  comillas   = False
  frases     = []
  palabras   = []
  palabra    = ''
  puntuacion = libreria.puntuacion[1:] if NOMBRE_SISTEMA == 'GAC' else ' ,.;:'
  if NOMBRE_SISTEMA == 'GAC':  # Quitamos acentos
    orden = er_acentos.sub (cambiaAcento, orden)
  for caracter in orden:
    if caracter == '"':
      comillas = not comillas
      if comillas:  # Era apertura de comillas
        orden_psi = ''
    elif comillas:
      orden_psi += caracter
    elif caracter in puntuacion:
      if not palabra:
        continue
      if palabra in conjunciones:  # TODO: en GAC, partir con las conjunciones (AND y THEN) hardcodeados de GAC
        if palabras:
          frases.append (palabras)
          palabras = []
      elif palabraSinPronombre (palabra) != palabra:
        palabras.append (palabraSinPronombre (palabra)[:LONGITUD_PAL])
        palabras.append (pronombre)
      else:
        palabras.append (palabra[:LONGITUD_PAL])
      palabra = ''
      if caracter != ' ' and palabras:
        frases.append (palabras)
        palabras = []
    else:
      palabra += caracter.lower()
  if palabra and palabra not in conjunciones:
    if palabraSinPronombre (palabra) != palabra:
      palabras.append (palabraSinPronombre (palabra)[:LONGITUD_PAL])
      palabras.append (pronombre)
    else:
      palabras.append (palabra[:LONGITUD_PAL])
  if palabras:
    frases.append (palabras)
  return frases

def tecla_o_fin ():
  """Espera que el usuario pulse una tecla

Si es Escape termina. Si es D entra en modo depuración de Python.

Para depuración paso a paso, devuelve el número de pasos a ejecutar, que es: 10, 100, 1000 o 1; en función de si la tecla pulsada era Espacio, Tabulador, Enter o cualquier otra; respectivamente"""
  sys.stdout.flush()  # Que se imprima todo lo que quede
  tecla = gui.espera_tecla (numPasos = True)
  if tecla == None:
    return 1
  if tecla == gui.pygame.K_ESCAPE:
    sys.exit()  # Salimos del programa
  if tecla == gui.pygame.K_SPACE:
    return 10
  if tecla == gui.pygame.K_TAB:
    return 100
  if tecla in (gui.pygame.K_KP_ENTER, gui.pygame.K_RETURN):
    return 1000
  if tecla == gui.pygame.K_d and not ide:  # Depuramos desde Python
    import pdb
    pdb.set_trace()
  return 1


# Funciones auxiliares que sólo se usan en este módulo

def cambiaAcento (encaje):
  """Devuelve sin acento gráfico la letra dada en el encaje de expresión regular"""
  return acentos[encaje.group (0)]

def palabraSinPronombre (palabra):
  """Devuelve la palabra dada quitándole el pronombre si tenía"""
  # TODO: modo de compatibilidad con cómo hace DAAD con los pronombres, buscando sufijos -la -lo
  # Vemos si la palabra está tal cual en el vocabulario como no verbo
  for codigo, tipo in dicc_vocab.get (palabra, ()):
    if TIPOS_PAL_ES[tipo] != 'Verbo':
      return palabra  # No la consideraremos para ver si tiene sufijo de pronombre
  if palabra[-4:] in ('alas', 'alos', 'elas', 'elos', 'rlas', 'rlos'):
    inicioSufijo = -3
  elif palabra[-3:] in ('ala', 'alo', 'ela', 'elo', 'nla', 'nlo', 'rla', 'rlo'):
    inicioSufijo = -2
  else:  # No tiene ninguno de los sufijos
    return palabra
  # Vemos si la palabra sin sufijo de pronombre está en el vocabulario como verbo
  for codigo, tipo in dicc_vocab.get (palabra[:inicioSufijo][:LONGITUD_PAL], ()):
    if TIPOS_PAL_ES[tipo] == 'Verbo':
      return palabra[:inicioSufijo]  # Contamos el sufijo como pronombre
  return palabra


if __name__ == '__main__':
  if sys.version_info[0] < 3:
    import codecs
    import locale
    reload (sys)  # Necesario para poder ejecutar sys.setdefaultencoding
    sys.stderr = codecs.getwriter (locale.getpreferredencoding()) (sys.stderr)  # Locale del sistema para la salida de error
    sys.stdout = codecs.getwriter (locale.getpreferredencoding()) (sys.stdout)  # Locale del sistema para la salida estándar
    sys.setdefaultencoding ('iso-8859-15')  # Nuestras cadenas están en esta codificación, no en ASCII
  random.seed()  # Inicializamos el generador de números aleatorios

  # Vemos si está disponible la librería PyQt para diálogo de selección de fichero o carpeta
  if os.name != 'nt' and not os.environ.get ('DISPLAY'):
    QDialog = None  # Para que no intente abrir diálogo al ejecutarse desde consola de texto aunque esté disponible PyQt
  else:
    try:
      from PyQt4.QtGui import QApplication, QDialog, QFileDialog
    except:
      try:
        from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
      except:
        QDialog = None

  argsParser = argparse.ArgumentParser (sys.argv[0], description = 'Intérprete de Quill/PAWS/SWAN/DAAD en Python')
  argsParser.add_argument ('-c', '--columns', type = int, choices = range (32, 43), help = 'número de columnas a usar al imitar Spectrum')
  argsParser.add_argument ('--conversion', metavar = 'módulo', help = 'convertir caracteres con valores del diccionario conversion en el módulo Python dado')
  argsParser.add_argument ('-D', '--debug', action = 'store_true', help = 'ejecutar los condactos paso a paso')
  argsParser.add_argument ('-g', '--gui', choices = ('pygame', 'stdio', 'telegram'), help = 'interfaz gráfica a utilizar')
  argsParser.add_argument ('--icon', type = str, help = argparse.SUPPRESS)
  argsParser.add_argument ('--ide', action = 'store_true', help = argparse.SUPPRESS)
  argsParser.add_argument ('-s', '--scale', type = int, choices = range (1, 10), help = 'factor de escalado para la ventana')
  argsParser.add_argument ('--system', choices = ('gac', 'quill', 'paws', 'swan', 'daad'), help = 'usar este sistema en lugar de autodetectarlo')
  argsParser.add_argument ('--title', type = str, help = argparse.SUPPRESS)
  argsParser.add_argument ('bbdd', metavar = 'bd_cf_o_carpeta', nargs = '?' if QDialog else 1, help = 'base de datos, snapshot, código fuente, o carpeta de Quill/PAWS/SWAN/DAAD a ejecutar')
  argsParser.add_argument ('ruta_graficos', metavar = 'bd_o_carpeta_gráficos', nargs = '?', help = 'base de datos gráfica o carpeta de la que tomar las imágenes (con nombre pic###.png)')
  args  = argsParser.parse_args()
  ide   = args.ide
  traza = args.debug or args.ide

  librerias = (f[:-3] for f in os.listdir (os.path.dirname (os.path.realpath (__file__)))
               if (f[:9] == 'libreria_' and f[-3:] == '.py'))

  if type (args.bbdd) == list:
    args.bbdd = args.bbdd[0]
  if not args.bbdd or not args.bbdd.strip():
    rutaFichero = None
    if QDialog:
      filtro     = []
      soportadas = set()  # Extensiones soportadas
      for nombreModulo in librerias:
        try:
          modulo = __import__ (nombreModulo)
        except SyntaxError as excepcion:
          prn ('Error al importar el módulo:', excepcion, file = sys.stderr)
          continue
        for funcion, extensiones, descripcion in modulo.funcs_importar:
          if comprueba_tipo (modulo, funcion, types.FunctionType):
            filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
            for extension in extensiones:
              soportadas.add (extension)
      aplicacion = QApplication (sys.argv)
      dialogo = QFileDialog (None, 'Elige carpeta o fichero a ejecutar', os.curdir, 'Todos los formatos soportados (*.' + ' *.'.join (sorted (soportadas)) + ');;' + ';;'.join (sorted (filtro)))
      dialogo.accept = lambda: QDialog.accept (dialogo)
      dialogo.setFileMode (QFileDialog.AnyFile)
      dialogo.setOption   (QFileDialog.DontUseNativeDialog)
      if dialogo.exec_():  # No se ha cancelado
        rutaFichero = (str if sys.version_info[0] > 2 else unicode) (dialogo.selectedFiles()[0])
    if not rutaFichero or not rutaFichero.strip():
      argsParser.print_help()
      sys.exit()
    args.bbdd = rutaFichero

  if not args.gui:
    if args.ruta_graficos:
      args.gui = 'pygame'
    else:
      try:
        import pygame
        args.gui = 'pygame'
      except:
        args.gui = 'stdio'
  gui = __import__ ('gui_' + args.gui)
  gui.frase_guardada = frase_guardada
  gui.ide            = args.ide
  gui.puntos_ruptura = puntos_ruptura
  gui.ruta_icono     = args.icon
  gui.titulo_ventana = args.title
  texto_nuevo        = gui.texto_nuevo

  if os.path.isdir (args.bbdd):
    gui.NOMBRE_SISTEMA = 'DAAD'
    libreria    = __import__ ('libreria_daad')
    partes, gfx = libreria.busca_partes (args.bbdd)
    if not partes:
      gui.NOMBRE_SISTEMA = 'SWAN'
      libreria    = __import__ ('libreria_swan')
      partes, gfx = libreria.busca_partes (args.bbdd)
      if not partes:
        prn ('Ninguna base de datos con nombre válido detectada en esa carpeta', file = sys.stderr)
        sys.exit()
    if traza:
      prn ('Bases de datos de partes detectadas:', partes, file = sys.stderr)
      prn ('Bases de datos gráficas detectadas:',  gfx,    file = sys.stderr)
    gui.abre_ventana (traza, args.scale, args.bbdd)
    args.bbdd = gui.elige_parte (partes, gfx)
  elif not os.path.isfile (args.bbdd):
    prn ('No hay ningún fichero ni carpeta con ese nombre:', args.bbdd, file = sys.stderr)
    sys.exit()

  # Cargamos el diccionario de conversión de caracteres
  if args.conversion:
    try:
      sys.path.append (os.path.dirname (args.conversion))
      moduloConversion = __import__ (os.path.basename (args.conversion)[:-3])
    except Exception as excepcion:
      prn ('Error al tratar de cargar el módulo de conversión de caracteres:', excepcion, file = sys.stderr)
      sys.exit()

  # Detectamos qué librerías pueden cargar bases de datos con esa extensión
  extension = args.bbdd[args.bbdd.rfind ('.') + 1:].lower()
  modLibs   = []  # Librerías que soportan la extensión, junto con su función de carga
  librerias = (f[:-3] for f in os.listdir (os.path.dirname (os.path.realpath (__file__)))
               if (f[:9] == 'libreria_' and f[-3:] == '.py'))
  for nombreModulo in librerias:
    if args.system and nombreModulo != 'libreria_' + args.system:
      continue
    try:
      modulo = __import__ (nombreModulo)
      if args.conversion and 'conversion' in modulo.__dict__ and 'conversion' in moduloConversion.__dict__:
        modulo.conversion.update (moduloConversion.conversion)
      if args.conversion and 'secuencias' in gui.__dict__ and 'secuencias' in moduloConversion.__dict__:
        gui.secuencias.update (moduloConversion.secuencias)
    except Exception as excepcion:
      prn ('Error al importar el módulo:', excepcion, file = sys.stderr)
      continue
    for funcion, extensiones, descripcion in modulo.funcs_importar:
      if extension in extensiones:
        modLibs.append ((modulo, funcion))
  if not modLibs:
    prn ('No se puede importar la base datos: extensión no reconocida', file = sys.stderr)
    sys.exit()

  # Cargamos la base de datos
  bbdd = open (args.bbdd, 'rb')
  for modulo, funcion in modLibs:
    if traza or len (modLibs) > 1:
      prn ('Intentando cargar el fichero', extension.upper(), 'con sistema', modulo.NOMBRE_SISTEMA, file = sys.stderr)
    # Solicitamos la importación
    modulo.NOMBRE_GUI = args.gui
    try:
      correcto = modulo.__dict__[funcion] (bbdd, os.path.getsize (args.bbdd)) != False
    except:
      correcto = False
    if correcto:
      libreria = modulo
      gui.num_objetos    = libreria.num_objetos
      gui.NOMBRE_SISTEMA = libreria.NOMBRE_SISTEMA
      gui.NUM_BANDERAS   = libreria.NUM_BANDERAS
      modulo.ruta_bbdd   = args.bbdd
      for constante in ('BANDERA_ADVERBIO', 'BANDERA_LLEVABLES', 'BANDERA_LOC_ACTUAL', 'BANDERA_NOMBRE', 'BANDERA_NOMBRE2', 'BANDERA_PRONOMBRE', 'BANDERA_VERBO', 'NUM_BANDERAS_ACC'):
        if constante in libreria.__dict__:
          globals()[constante] = libreria.__dict__[constante][0]
      break
    bbdd.seek (0)
    if len (modLibs) > 1:
      prn (file = sys.stderr)
  if not correcto:
    prn ('Error al tratar de cargar la base de datos: formato incompatible o fichero corrupto', file = sys.stderr)
    sys.exit()

  if extension == 'sna' or libreria.plataforma == 1:  # Plataforma con menos de 53 columnas
    if extension == 'sna' and args.gui not in ('stdio', 'telegram'):
      # Trataremos de cargar fuente tipográfica desde el snapshot
      gui.conversion = libreria.conversion
      gui.udgs       = libreria.udgs
      gui.carga_fuente_zx (bbdd)
      gui.prepara_topes (args.columns if args.columns else 32, 24)
    elif extension == 'prg':
      gui.prepara_topes (args.columns if args.columns else 40, 25)
    elif args.columns or args.gui not in ('stdio', 'telegram'):
      if libreria.strPlataforma == 'QL':
        gui.prepara_topes (args.columns if args.columns else 37, 22)
      else:
        gui.prepara_topes (42, 24)
  elif args.gui not in ('stdio', 'telegram'):
    gui.prepara_topes (53, 25)

  bbdd.close()

  constantes = ('EXT_SAVEGAME', 'LONGITUD_PAL', 'NOMB_COMO_VERB', 'NOMBRE_SISTEMA', 'NUM_ATRIBUTOS', 'NUM_BANDERAS', 'NUM_MARCADORES', 'PREP_COMO_VERB', 'TIPOS_PAL', 'TIPOS_PAL_ES')
  funciones  = ('actualiza_grafico', 'adapta_msgs_sys', 'busca_condacto', 'busca_conexion', 'cambia_articulo', 'da_peso', 'imprime_mensaje', 'obj_referido', 'parsea_orden', 'prepara_vocabulario', 'restaura_objetos', 'tabla_hizo_algo')
  funcsLib   = ('carga_xmessage', )
  variables  = ('atributos', 'atributos_extra', 'banderas', 'compatibilidad', 'conexiones', 'desc_locs', 'desc_objs', 'doall_activo', 'frases', 'loc_inicio', 'locs_iniciales', 'locs_objs', 'marcadores', 'msgs_usr', 'msgs_sys', 'nombres_objs', 'nueva_version', 'num_objetos', 'partida', 'peso_llevable', 'peso_llevado', 'pila_datos', 'pila_procs', 'tablas_proceso', 'vocabulario')

  # Hacemos lo equivalente a: from libreria import *, cargando sólo lo exportable
  for lista in (constantes, funcsLib, variables):
    for variable in lista:
      if variable in libreria.__dict__:
        globals()[variable] = libreria.__dict__[variable]

  for modulo in libreria.mods_condactos:
    modulo = __import__ (modulo)
    # Propagamos las constantes y estructuras básicas del intérprete y la librería entre los módulos de condactos
    modulo.gui       = gui
    modulo.libreria  = libreria
    modulo.ruta_bbdd = args.bbdd
    for constante in ('BANDERA_ADVERBIO', 'BANDERA_LLEVABLES', 'BANDERA_LOC_ACTUAL', 'BANDERA_NOMBRE', 'BANDERA_NOMBRE2', 'BANDERA_VERBO', 'NUM_BANDERAS_ACC'):
      if constante in globals():
        modulo.__dict__[constante] = globals()[constante]
    for lista in (constantes, funcsLib, variables):
      for variable in lista:
        if variable in globals():
          modulo.__dict__[variable] = globals()[variable]
    # Propagamos las funciones auxiliares para los módulos de condactos
    for funcion in funciones:
      modulo.__dict__[funcion] = globals()[funcion]
    modulos.append (modulo)

  if args.ruta_graficos:
    if os.path.isfile (args.ruta_graficos):
      error = gui.carga_bd_pics (args.ruta_graficos)
      if error:
        prn ('Error al tratar de cargar la base datos gráfica:', error, file = sys.stderr)
    elif os.path.isdir (args.ruta_graficos):
      if args.ruta_graficos[-1] != os.sep:
        args.ruta_graficos += os.sep
      gui.ruta_graficos = args.ruta_graficos
    else:
      prn ('No hay ningún fichero ni carpeta con ese nombre:', args.ruta_graficos, file = sys.stderr)

  if NOMBRE_SISTEMA != 'DAAD':
    if NOMBRE_SISTEMA != 'GAC' and libreria.strPlataforma != 'QL':
      gui.todo_mayusculas = True
    if not gui.paleta[0]:
      # Colores en este orden: negro, azul, rojo, magenta, verde, cyan, amarillo, blanco
      gui.paleta[0].extend (((0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215),  # Sin brillo
                             (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)))
      gui.paleta[1].extend (((0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),  # Con brillo
                             (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)))
    if NOMBRE_SISTEMA == 'SWAN':
      if gui.paleta[1]:
        gui.brillo = 1   # Con brillo por defecto
      gui.cod_juego_alto = 48  # @
      gui.cod_juego_bajo = 48
    elif NOMBRE_SISTEMA == 'QUILL' or (NOMBRE_SISTEMA == 'PAWS' and extension == 'sna'):  # Quill, o PAWS de Spectrum
      if NOMBRE_SISTEMA == 'PAWS' or libreria.strPlataforma == 'ZX':
        gui.cod_brillo    = 19
        gui.cod_columna   = 23
        gui.cod_flash     = 18
        gui.cod_inversa   = 20
        gui.cod_papel     = 17
        gui.cod_tabulador = 6
        gui.cod_tinta     = 16
      if NOMBRE_SISTEMA == 'PAWS':
        gui.cambia_cursor (msgs_sys[34])
      else:  # Es QUILL
        gui.partir_espacio = False
        gui.strPlataforma  = libreria.strPlataforma
        if gui.strPlataforma == 'C64':  # Plataforma Commodore 64
          gui.cod_inversa_ini = 18
          gui.cod_inversa_fin = 146
          gui.cods_tinta      = libreria.cods_tinta
          del gui.paleta[0][:]
          del gui.paleta[1][:]
          # Colores en este orden: negro, blanco, rojo, cyan, violeta, verde, azul, amarillo,
          #                        naranja, marrón, rojo claro, gris oscuro, gris, verde claro, azul claro, gris claro
          gui.paleta[0].extend (((0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238), (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
                                (221, 136, 85), (102, 68, 0), (255, 119, 119), (51, 51, 51), (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187)))
  else:  # Es DAAD
    gui.nueva_version = nueva_version
    if not gui.paleta[0]:
      # Colores con brillo en este orden: negro, azul, rojo, magenta, verde, cyan, amarillo, blanco
      gui.paleta[0].extend (((0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),
                             (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)))
    gui.chichen  = False
    gui.espacial = False
    gui.templos  = False
    # XXX: apaño para diferenciar la Aventura Original de aventuras posteriores
    if len (msgs_usr) > 77 and (msgs_usr[77] == '\x0eAVENTURA ORIGINAL I\x0f' or msgs_usr[0] == '\x0eAVENTURA ORIGINAL II\x0f'):
      gui.centrar_graficos.append (True)
      gui.cod_juego_alto = 14  # ü
      gui.cod_juego_bajo = 15  # Ü
    else:
      # XXX: apaño para detectar Chichén Itzá, al menos las versiones de 16 bits
      import hashlib
      if len (msgs_sys) > 100 and hashlib.sha1 ((msgs_sys[21] + msgs_sys[77] + msgs_sys[80] + msgs_sys[82] + msgs_sys[94] + msgs_sys[100]).encode ('utf8')).hexdigest() == 'cfea71b482cc37f6353bca664c8b36bbbed87f97':
        gui.chichen = True
      # XXX: apaño para detectar La Aventura Espacial, al menos las versiones de 16 bits
      elif len (msgs_sys) > 69 and hashlib.sha1 ((msgs_sys[5] + msgs_sys[6] + msgs_sys[10] + msgs_sys[18] + msgs_sys[19] + msgs_sys[23] + msgs_sys[50] + msgs_sys[69]).encode ('utf8')).hexdigest() == '967672803a8234257a76dd478571b7793c9eb159':
        gui.espacial = True
      # XXX: apaño para detectar Los Templos Sagrados, al menos las versiones de 16 bits
      elif len (msgs_sys) > 83 and hashlib.sha1 ((msgs_sys[6] + msgs_sys[27] + msgs_sys[43] + msgs_sys[66] + msgs_sys[74] + msgs_sys[77] + msgs_sys[81] + msgs_sys[83]).encode ('utf8')).hexdigest() == 'fe8d542a35c3f87f354bb60c6da50abca518b616':
        gui.templos = True
      elif nueva_version:
        gui.cod_juego_alto = 14  # ü
        gui.cod_juego_bajo = 15  # Ü
  if NOMBRE_SISTEMA not in ('GAC', 'QUILL'):
    gui.txt_mas = msgs_sys[32]  # (más)

  # Fallamos ahora si falta algún condacto
  if False:
    comprobados = set()
    for numTabla in tablas_proceso.keys() if type (tablas_proceso) == dict else tablas_proceso:
      for numEntrada in range (len (tablas_proceso[numTabla][1])):
        entrada = tablas_proceso[numTabla][1][numEntrada]
        for codigo, parametros in entrada:
          if codigo > 127:
            codigo -= 128
          if codigo in comprobados:
            continue
          condacto = libreria.condactos[codigo]
          firma    = ('a' if condacto[2] else 'c') + str (len (condacto[1])) + '_' + condacto[0]
          funcion  = busca_condacto (firma)
          comprobados.add (codigo)

  gui.abre_ventana (traza, args.scale, args.bbdd)

  # Preparamos las listas banderas y locs_objs
  # TODO: ver si locs_objs está bien así para GAC
  banderas.extend  ([0,] * NUM_BANDERAS[0])  # Banderas del sistema
  locs_objs.extend ([0,] * num_objetos[0])   # Localidades de los objetos

  # Adaptamos los mensajes de sistema si corresponde, según la interfaz
  adapta_msgs_sys()

  # Preparamos el diccionario con el vocabulario, y la lista conjunciones
  prepara_vocabulario()

  if NOMBRE_SISTEMA == 'DAAD' and nueva_version:
    bucle_daad_nuevo()
  elif NOMBRE_SISTEMA == 'GAC':
    marcadores.extend ([0,] * NUM_MARCADORES)  # Banderas del sistema
    bucle_gac()
  else:
    bucle_paws()

  if texto_nuevo:
    gui.espera_tecla()
  if args.gui == 'telegram':
    gui.escribe_buffer()
