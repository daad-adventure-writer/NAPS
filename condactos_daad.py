# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Condactos específicos de DAAD
# Copyright (C) 2010, 2019-2024 José Manuel Ferrer Ortiz
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
import struct
import sys

from prn_func import prn


grafico_preparado = None


# Funciones auxiliares

def accionAUTO (accion, localidades, sysno):
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en el orden de prioridad de la lista localidades dada. Si se encuentra, ejecuta accion sobre ese objeto. Si no se encuentra ahí, imprime sysno si el nombre de la SL no está en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: ¿creado?), o MS8 si no hay ningún objeto con ese nombre. En caso de error, al final hace NEWTEXT y luego DONE"""
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  if banderas[34] == 255 and banderas[35] == 255:
    gui.imprime_cadena (msgs_sys[sysno], tiempo = tiempoTimeout)
    busca_condacto ('a0_NEWTEXT')()
    return busca_condacto ('a0_DONE')()
  # Obtenemos los objetos que están en las localidades dadas, y en otros sitios
  presentes = {}
  for localidad in localidades + (-1,):  # -1 representará en otros sitios
    presentes[localidad] = []
  for objno in range (len (locs_objs)):
    localidad = locs_objs[objno]
    if localidad not in localidades:  # FIXME: comprobar si se debe omitir los no creados
      localidad = -1
    presentes[localidad].append (objno)
  # Vemos si alguno encaja con la SL actual
  # TODO: validar esto comprobando con los intérpretes de DAAD originales, viendo cómo se desambigua por adjetivos, y qué pasa si más de uno encaja
  for localidad in localidades + (-1,):
    for objeto in presentes[localidad]:
      (nombre, adjetivo) = nombres_objs[objeto]
      if banderas[34] == nombre and banderas[35] in (adjetivo, 255):  # TODO: encajes parciales
        if localidad == -1:
          gui.imprime_cadena (msgs_sys[sysno], tiempo = tiempoTimeout)
          busca_condacto ('a0_NEWTEXT')()
          return busca_condacto ('a0_DONE')()
        return accion (objeto)
  gui.imprime_cadena (msgs_sys[8], tiempo = tiempoTimeout)  # 'No puedes hacer eso'
  busca_condacto ('a0_NEWTEXT')()
  return busca_condacto ('a0_DONE')()

def accionAUTO2 (accion, localidades, sysno, locno, sysno2 = None):
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en el orden de prioridad de la lista localidades dada. Si se encuentra, ejecuta accion sobre ese objeto y el objeto contenedor dado en locno. Si no se encuentra, imprime sysno si el nombre de la SL no está en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: ¿creado?), o MS8 si no hay ningún objeto con ese nombre. En caso de error, al final hace NEWTEXT y luego DONE"""
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  if banderas[34] == 255 and banderas[35] == 255:
    gui.imprime_cadena (msgs_sys[sysno], tiempo = tiempoTimeout)
    if sysno2:
      if locno < num_objetos[0]:
        desc_obj = desc_objs[locno]
        if '.' in desc_obj:
          desc_obj = desc_obj[:desc_obj.index ('.')]
        gui.imprime_cadena (cambia_articulo (desc_obj), tiempo = tiempoTimeout)
      gui.imprime_cadena (msgs_sys[sysno2], tiempo = tiempoTimeout)
    busca_condacto ('a0_NEWTEXT')()
    return busca_condacto ('a0_DONE')()
  # Obtenemos los objetos que están en las localidades dadas, y en otros sitios
  presentes = {}
  for localidad in localidades + (-1,):  # -1 representará en otros sitios
    presentes[localidad] = []
  for objno in range (len (locs_objs)):
    localidad = locs_objs[objno]
    if localidad not in localidades:  # FIXME: comprobar si se debe omitir los no creados
      localidad = -1
    presentes[localidad].append (objno)
  # Vemos si alguno encaja con la SL actual
  # TODO: validar esto comprobando con los intérpretes de DAAD originales, viendo cómo se desambigua por adjetivos, y qué pasa si más de uno encaja
  for localidad in localidades + (-1,):
    for objeto in presentes[localidad]:
      (nombre, adjetivo) = nombres_objs[objeto]
      if banderas[34] == nombre and banderas[35] in (adjetivo, 255):  # TODO: encajes parciales
        if localidad == -1:
          gui.imprime_cadena (msgs_sys[sysno], tiempo = tiempoTimeout)
          if sysno2:
            if locno < num_objetos[0]:
              desc_obj = desc_objs[locno]
              if '.' in desc_obj:
                desc_obj = desc_obj[:desc_obj.index ('.')]
              gui.imprime_cadena (cambia_articulo (desc_obj), tiempo = tiempoTimeout)
            gui.imprime_cadena (msgs_sys[sysno2], tiempo = tiempoTimeout)
          busca_condacto ('a0_NEWTEXT')()
          return busca_condacto ('a0_DONE')()
        return accion (objeto, locno)
  gui.imprime_cadena (msgs_sys[8], tiempo = tiempoTimeout)  # 'No puedes hacer eso'
  busca_condacto ('a0_NEWTEXT')()
  return busca_condacto ('a0_DONE')()


# Los nombres de las funciones que implementan los condactos son Xn_*, siendo:
# X: 'c' ó 'a', según si son condiciones o acciones, respectivamente
# n: el número de parámetros
# *: el nombre del condacto


# CONDICIONES


def c0_INKEY ():
  """Guarda en las banderas 60 y 61 el par de códigos ASCII de la tecla pulsada (si hay alguna pulsada), y devuelve si hay alguna tecla pulsada o no"""
  tecla = gui.da_tecla_pulsada()
  if tecla == None:
    return False
  banderas[60] = tecla[0]
  banderas[61] = tecla[1]
  return True

def c0_ISDONE ():
  """Satisfactorio si la última tabla que terminó, lo hizo habiendo ejecutado alguna acción, o terminando con DONE, pero no con NOTDONE"""
  return tabla_hizo_algo()

def c0_ISNDONE ():
  """Satisfactorio si la última tabla que terminó, lo hizo sin ejecutar ninguna acción, o con NOTDONE"""
  return not tabla_hizo_algo()

def c0_LOAD ():
  """Carga el contenido de las banderas y de las localidades de los objetos desde un fichero"""
  nombreFich = (gui.lee_cadena (msgs_sys[60] + msgs_sys[33]) + '.' + EXT_SAVEGAME).lower()
  # Buscamos el fichero con independencia de mayúsculas y minúsculas
  for nombreFichero in os.listdir (os.path.dirname (ruta_bbdd)):
    if nombreFichero.lower() == nombreFich:
      nombreFich = os.path.join (os.path.dirname (ruta_bbdd), nombreFichero)
      break
  bien = True
  try:
    fichero = open (nombreFich, 'rb')
  except:
    bien = False
  if bien:
    try:
      fichero.seek (0, os.SEEK_END)
      if fichero.tell() == NUM_BANDERAS[0] + 256:  # Comprueba su longitud
        fichero.seek (0)
        leido = struct.unpack ('512B', fichero.read (512))
        del banderas[:]
        banderas.extend (leido[:NUM_BANDERAS[0]])
        del locs_objs[:]
        locs_objs.extend (leido[NUM_BANDERAS[0]:NUM_BANDERAS[0] + num_objetos[0]])
        gui.borra_todo()
        del gui.historial[:]
      else:
        bien = False
    except:
      bien = False
  if not bien:
    imprime_mensaje (msgs_sys[57])  # Error E/S
    a0_ANYKEY()
  return bien

def c0_QUIT ():
  """Pide confirmación (MS12), y devuelve si la respuesta empieza por la primera letra del MS30"""
  respuesta = gui.lee_cadena (msgs_sys[12] + msgs_sys[33])
  return respuesta[0].lower() == msgs_sys[30][0].lower()


def c1_HASAT (attribute):
  """Satisfactorio si el atributo dado tiene valor verdadero"""
  bitAtributo = attribute  % 8
  posBandera  = attribute // 8
  numBandera  = 59 - posBandera
  if numBandera == -1:
    prn ('FIXME: bandera del atributo', attribute, 'desconocida')
    return False
  mascara = 2 ** bitAtributo
  return banderas[numBandera] & mascara == mascara

def c1_HASNAT (attribute):
  """Satisfactorio si el atributo dado tiene valor falso"""
  return not c1_HASAT (attribute)

def c1_LOAD (opt):
  """Carga el contenido de las banderas y de las localidades de los objetos desde un fichero"""
  return c0_LOAD()  # TODO: ¿para qué sirve opt?

def c1_PARSE (mode):
  """Con mode 0, obtiene e interpreta la orden del jugador para rellenar la sentencia lógica actual. Con mode 1, interpreta la parte entrecomillada de la orden del jugador, para conversación con PSI, como hace c0_PARSE de PAWS. Devuelve satisfactorio en caso de fallo"""
  return parsea_orden (mode)
  
def c1_PICTURE (picno):
  """Prepara el gráfico definido por picno, devolviendo falso si no existe"""
  global grafico_preparado
  if gui.hay_grafico (picno):
    grafico_preparado = picno
    return True
  return False

def c1_RAMLOAD (flagno):
  """Carga el contenido de las banderas hasta flagno y de las localidades de los objetos desde memoria"""
  if not partida:  # No hay partida guardada en memoria
    return False
  for b in range (flagno + 1):
    banderas[b] = partida[b]
  for o in range (num_objetos[0]):
    locs_objs[o] = partida[NUM_BANDERAS[0] + o]
  gui.borra_todo()
  del gui.historial[:]
  return True


def c2_BIGGER (flagno1, flagno2):
  """Satisfactorio si el valor de la bandera flagno1 es mayor que el de la bandera flagno2"""
  return banderas[flagno1] > banderas[flagno2]

def c2_SMALLER (flagno1, flagno2):
  """Satisfactorio si el valor de la bandera flagno1 es menor que el de la bandera flagno2"""
  return banderas[flagno1] < banderas[flagno2]


# ACCIONES

def a0_ANYKEY ():
  """Imprime el mensaje del sistema 16 y se espera hasta que se pulse una tecla, o hasta que haya pasado el tiempo muerto, si se ha usado tiempo muerto"""
  gui.imprime_cadena (msgs_sys[16])
  gui.espera_tecla (banderas[48] if banderas[49] & 4 else 0)

def a0_CENTRE ():
  """Centra horizontalmente la subventana actual en la pantalla de juego"""
  gui.centra_subventana()

def a0_LISTOBJ ():
  """Lista los objetos presentes, si los hay, anteponiendo el mensaje de sistema 1"""
  presentes = []
  for objno in range (len (locs_objs)):
    if locs_objs[objno] == banderas[38]:
      presentes.append (objno)
  if presentes:
    tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
    gui.imprime_cadena (msgs_sys[1], tiempo = tiempoTimeout)  # 'Puedes ver '
    if not banderas[53] & 64:  # Listar uno por línea
      gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
    for i in range (len (presentes)):
      descripcion = desc_objs[presentes[i]]
      if banderas[53] & 64:  # Listar como una frase
        if '.' in descripcion:
          descripcion = descripcion[:descripcion.index ('.')]
        if gui.centrar_graficos and compatibilidad:  # En la Aventura Original sí cambia el artículo por uno definido
          gui.imprime_cadena (cambia_articulo (descripcion), tiempo = tiempoTimeout)
        else:
          gui.imprime_cadena (descripcion[0].lower() + descripcion[1:], tiempo = tiempoTimeout)
        if i == len (presentes) - 1:  # Último objeto presente
          gui.imprime_cadena (msgs_sys[48], tiempo = tiempoTimeout)  # '.'
        elif i == len (presentes) - 2:
          gui.imprime_cadena (msgs_sys[47], tiempo = tiempoTimeout)  # ' y '
        else:
          gui.imprime_cadena (msgs_sys[46], tiempo = tiempoTimeout)  # ', '
      else:  # Listar uno por línea
        gui.imprime_cadena (descripcion, tiempo = tiempoTimeout)
        gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
    banderas[53] |= 128  # Marca que se han listado objetos
  elif banderas[53] & 128:
    banderas[53] ^= 128  # Marca que no se han listado objetos

# FIXME: Comprobar si debe salir de los bucles DOALL también
def a0_REDO ():
  """Reinicia la ejecución de la tabla de proceso actual"""
  return 2

def a0_RESTART ():
  """Termina todo lo que estuviese en ejecución (tablas, bucles DOALL, etc.) y salta al inicio del proceso 0"""
  return 1

def a0_RESET ():
  """Coloca los objetos en sus localidades iniciales, ajustando las banderas necesarias"""
  restaura_objetos()

def a0_SAVE ():
  """Guarda el contenido de las banderas y de las localidades de los objetos a un fichero"""
  nombreFich = gui.lee_cadena (msgs_sys[60] + msgs_sys[33])
  invalido   = False
  if compatibilidad and (len (nombreFich) > 8 or not nombreFich.isalnum()):
    invalido = True
  else:
    for caracter in nombreFich:
      if not caracter.isalnum():
        invalido = True
        break
  if invalido:
    imprime_mensaje (msgs_sys[59])  # Nombre de fichero inválido
    a0_ANYKEY()
  else:
    try:
      fichero = open (os.path.join (os.path.dirname (ruta_bbdd), nombreFich + '.' + EXT_SAVEGAME), 'wb')
      for bandera in banderas:
        fichero.write (struct.pack ('B', bandera))
      for loc_obj in locs_objs:
        fichero.write (struct.pack ('B', loc_obj))
      for i in range (len (locs_objs), 256):  # El resto de bytes los ocupamos con 0
        fichero.write (struct.pack ('B', 0))
      gui.borra_orden()
    except:
      imprime_mensaje (msgs_sys[57])  # Error I/O
      a0_ANYKEY()

def a0_SPACE ():
  """Imprime un espacio en blanco"""
  gui.imprime_cadena (' ', tiempo = banderas[48] if banderas[49] & 2 else 0)


def a1_CALL (address):
  """Es como un EXTERN"""
  prn ('XXX: a1_CALL no implementado', file = sys.stderr)

def a1_DESC (locno):
  """Imprime la descripción de la localidad dada"""
  imprime_mensaje (desc_locs[locno])

def a1_DISPLAY (value):
  """Dibuja el gráfico preparado"""
  if value == 0:
    gui.dibuja_grafico (grafico_preparado, parcial = True)
  else:
    prn ('TODO: a1_DISPLAY con value != 0 no implementado')  # TODO

def a1_DPRINT (flagno):
  """Imprime el número de 16 bits contenido en las banderas flagno y flagno + 1"""
  numero = banderas[flagno]
  if flagno < 255:
    numero += banderas[flagno + 1] * 256
  gui.imprime_cadena (str (numero), tiempo = banderas[48] if banderas[49] & 2 else 0)

def a1_EXIT (value):
  """Si value es 0, termina completamente la ejecución de la aventura. Si no, reinicia la aventura, reinicializando ventanas y otras cosas; o bien salta a la parte value, según el sistema"""
  if value == 0:
    return 7
  prn ('FIXME: a1_EXIT con value != 0 parcialmente implementado')  # FIXME
  return 0

def a1_LISTAT (locno):
  """Lista los objetos presentes en la localidad locno, o el mensaje de sistema 53 si no hay ninguno"""
  # TODO: ver si se debe mantener en sincronía con LISTOBJ
  # Obtenemos los objetos presentes en locno
  presentes = []
  for objno in range (len (locs_objs)):
    if locs_objs[objno] == locno:
      presentes.append (objno)
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  if presentes:  # Los listamos
    for i in range (len (presentes)):
      descripcion = desc_objs[presentes[i]]
      if banderas[53] & 64:  # Listar como una frase
        if '.' in descripcion:
          descripcion = descripcion[:descripcion.index ('.')]
        # Las primeras versiones de DAAD parecen cambiar en este modo de listar, los artículos indefinidos por definidos
        if nueva_version or not gui.centrar_graficos:
          gui.imprime_cadena (descripcion[0].lower() + descripcion[1:], tiempo = tiempoTimeout)
        else:
          gui.imprime_cadena (cambia_articulo (descripcion), tiempo = tiempoTimeout)
        if i == len (presentes) - 1:  # Último objeto presente
          gui.imprime_cadena (msgs_sys[48], tiempo = tiempoTimeout)  # '.'
        elif i == len (presentes) - 2:
          gui.imprime_cadena (msgs_sys[47], tiempo = tiempoTimeout)  # ' y '
        else:
          gui.imprime_cadena (msgs_sys[46], tiempo = tiempoTimeout)  # ', '
      else:  # Listar uno por línea
        gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
        gui.imprime_cadena (descripcion, tiempo = tiempoTimeout)
    banderas[53] |= 128  # Marca que se han listado objetos
  else:
    gui.imprime_cadena (msgs_sys[53], tiempo = tiempoTimeout)  # 'nada.'
    if banderas[53] & 128:
      banderas[53] ^= 128  # Marca que no se han listado objetos

def a1_MODE (mode):
  """Cambia el modo de pantalla al indicado por mode"""
  banderas[40] = mode  # FIXME

def a1_SAVE (opt):
  """Guarda el contenido de las banderas y de las localidades de los objetos a un fichero"""
  a0_SAVE()  # TODO: ¿para qué sirve opt?

def a1_SETCO (objno):
  """Cambia el objeto referido actualmente a objno"""
  obj_referido (objno)

def a1_SKIP (distance):
  """Salta al inicio de una entrada contigua"""
  if distance > 128:
    return [distance - 256]
  return [distance]

def a1_TAB (colno):
  """La columna para la posición de impresión actual se cambia al valor dado por colno"""
  gui.mueve_cursor (colno)

def a1_WINDOW (value):
  """Selecciona la subventana de impresión value"""
  if value > 7:  # Aunque DAAD lo soporta (no da error, aunque dibuje mal), fallamos
    prn ('ERROR: Condacto WINDOW llamado con un valor mayor que 7')
    return
  banderas[63] = value
  gui.elige_subventana (value)


def a2_COPYBF (flagno1, flagno2):
  """El contenido de la bandera flagno2 se copia en la bandera flagno1"""
  banderas[flagno1] = banderas[flagno2]

def a2_EXTERN (*args):
  """Llamada a función externa. Toma número de parámetros ilimitado para soporte de Maluva"""
  if len (args) == 3 and args[1] == 3:  # XMES de Maluva
    mensaje = carga_xmessage (args[0] + args[2] * 256)
    if mensaje == None:
      mensaje = msgs_sys[57]  # Error E/S
    imprime_mensaje (mensaje)
    return
  prn ('a2_EXTERN', args, 'no implementado', file = sys.stderr)

def a2_GFX (value1, value2):
  """Es como un EXTERN"""
  prn ('a2_GFX no implementado', file = sys.stderr)

def a2_INPUT (stream, options):
  """Cambia el "stream" (subventana de impresión) del que leer órdenes del jugador, y las opciones de entrada. Un valor 0 para stream hace que la entrada se obtenga de la subventana actual"""
  banderas[41] = stream % 8
  gui.cambia_subv_input (banderas[41], options)

def a2_SFX (value1, value2):
  prn ('TODO: a2_SFX no implementado', file = sys.stderr)  # TODO

def a2_SYNONYM (verb, noun):
  """Cambia el verbo y/o el nombre de la SL actual por los dados. Si alguno es 255, ese no lo cambiará"""
  if verb != 255:
    banderas[33] = verb
  if noun != 255:
    banderas[34] = noun

def a2_WINAT (rowno, colno):
  """Cambia la posición de la subventana de impresión elegida"""
  gui.pos_subventana (colno, rowno)

# TODO: Es posible que empiece a contar desde 1, en lugar de desde 0, pues en
# el Jabato, el código pone como topes de la subventana 0 (así están en el
# momento del prompt) [31, 25]. Ese 25 puede que deba convertirse a 24 para el
# módulo gui
def a2_WINSIZE (rowno, colno):
  """Cambia los topes de la subventana de impresión elegida"""
  gui.cambia_topes (colno, rowno)
