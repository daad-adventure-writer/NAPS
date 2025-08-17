# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Condactos PAWS est�ndar
# Copyright (C) 2010, 2018-2025 Jos� Manuel Ferrer Ortiz
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
import random  # Para randint
import struct
import sys

from prn_func import prn


# Funciones auxiliares

def accionAUTO (accion, localidades, sysno):
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en el orden de prioridad de la lista localidades dada. Si se encuentra, ejecuta accion sobre ese objeto. Si no se encuentra ah�, imprime sysno si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  if banderas[34] == 255 and banderas[35] == 255:
    gui.imprime_cadena (msgs_sys[sysno], tiempo = tiempoTimeout)
    a0_NEWTEXT()
    return busca_condacto ('a0_DONE')()
  # Obtenemos los objetos que est�n en las localidades dadas, y en otros sitios
  presentes = {}
  for localidad in localidades + (-1,):  # -1 representar� en otros sitios
    presentes[localidad] = []
  for objno in range (len (locs_objs)):
    localidad = locs_objs[objno]
    if localidad not in localidades:  # FIXME: comprobar si se debe omitir los no creados
      localidad = -1
    presentes[localidad].append (objno)
  # Vemos si alguno encaja con la SL actual
  # TODO: validar esto comprobando con los int�rpretes de PAWS originales, viendo c�mo se desambigua por adjetivos, y qu� pasa si m�s de uno encaja
  for localidad in localidades + (-1,):
    encontrado = False
    for objeto in presentes[localidad]:
      (nombre, adjetivo) = nombres_objs[objeto]
      if banderas[34] == nombre and banderas[35] in (adjetivo, 255):  # TODO: encajes parciales
        if localidad == -1:
          gui.imprime_cadena (msgs_sys[sysno], tiempo = tiempoTimeout)
          a0_NEWTEXT()
        else:
          accion (objeto)
        encontrado = True
        break
    if encontrado:
      break
  else:
    gui.imprime_cadena (msgs_sys[8], tiempo = tiempoTimeout)  # 'No puedes hacer eso'
    a0_NEWTEXT()
  return busca_condacto ('a0_DONE')()

def accionAUTO2 (accion, localidades, sysno, locno, sysno2 = None):
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en el orden de prioridad de la lista localidades dada. Si se encuentra, ejecuta accion sobre ese objeto y el objeto contenedor dado en locno. Si no se encuentra, imprime sysno si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
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
    a0_NEWTEXT()
    return busca_condacto ('a0_DONE')()
  # Obtenemos los objetos que est�n en las localidades dadas, y en otros sitios
  presentes = {}
  for localidad in localidades + (-1,):  # -1 representar� en otros sitios
    presentes[localidad] = []
  for objno in range (len (locs_objs)):
    localidad = locs_objs[objno]
    if localidad not in localidades:  # FIXME: comprobar si se debe omitir los no creados
      localidad = -1
    presentes[localidad].append (objno)
  # Vemos si alguno encaja con la SL actual
  # TODO: validar esto comprobando con los int�rpretes de PAWS originales, viendo c�mo se desambigua por adjetivos, y qu� pasa si m�s de uno encaja
  for localidad in localidades + (-1,):
    encontrado = False
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
          a0_NEWTEXT()
        else:
          accion (objeto, locno)
        encontrado = True
        break
    if encontrado:
      break
  else:
    gui.imprime_cadena (msgs_sys[8], tiempo = tiempoTimeout)  # 'No puedes hacer eso'
    a0_NEWTEXT()
  return busca_condacto ('a0_DONE')()


# Los nombres de las funciones que implementan los condactos son Xn_*, siendo:
# X: 'c' � 'a', seg�n si son condiciones o acciones, respectivamente
# n: el n�mero de par�metros
# *: el nombre del condacto


# CONDICIONES

def c0_PARSE ():
  """Interpreta una orden de conversaci�n con PSI (entrecomillada). Satisfactorio en caso de orden inv�lida"""
  return parsea_orden (True)

def c0_QUIT ():
  """Pide confirmaci�n (MS12), y si la respuesta empieza por la primera letra del MS30, devuelve condici�n satisfecha. Si no, hace NEWTEXT y DONE"""
  respuesta = gui.lee_cadena (msgs_sys[12] + msgs_sys[33])
  if respuesta[0].lower() == msgs_sys[30][0].lower():
    return True
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE')()

def c0_TIMEOUT ():
  """Satisfactorio si la �ltima entrada de �rdenes del jugador ha vencido el tiempo m�ximo de espera (timeout)"""
  return (banderas[49] & 128) != 0


def c1_ABSENT (objno):
  """Si el objeto objno no est� llevado, ni puesto, ni en la localidad actual"""
  if objno == 255:
    return True
  aqui = (254, 253, banderas[38])  # Llevado, puesto y localidad actual, respec.
  return locs_objs[objno] not in aqui

def c1_ADJECT1 (word):
  """Satisfactorio si el adjetivo del primer nombre de la SL actual es igual a word"""
  return banderas[35] == word

def c1_ADJECT2 (word):
  """Satisfactorio si el adjetivo del segundo nombre de la SL actual es igual a word"""
  return banderas[45] == word

def c1_ADVERB (word):
  """Satisfactorio si el adverbio de la SL actual es igual a word"""
  return banderas[36] == word

def c1_MOVE (flagno):
  """Busca el verbo de la SL actual en las conexiones de la localidad contenida en la bandera flagno. Si ese verbo estaba, guarda la localidad de destino en esa bandera, y devuelve resultado satisfactorio"""
  destino = busca_conexion (banderas[flagno])
  if destino == None:
    return False
  banderas[flagno] = destino
  return True

def c1_NOUN2 (word):
  """Satisfactorio si el segundo nombre de la SL actual es igual a word"""
  return banderas[44] == word

def c1_PREP (word):
  """Satisfactorio si la preposici�n de la SL actual es igual a word"""
  return banderas[43] == word


def c2_ISAT (objno, locno):
  """Satisfactorio si el objeto objno se encuentra en la localidad locno. Un valor de 255 para locno indica la localidad actual"""
  return locs_objs[objno] == (locno if locno != 255 else banderas[38])

def c2_ISNOTAT (objno, locno):
  """Satisfactorio si el objeto objno no se encuentra en la localidad locno. Un valor de 255 para locno indica la localidad actual"""
  return locs_objs[objno] != (locno if locno != 255 else banderas[38])

def c2_NOTEQ (flagno, value):
  """Si el valor en la bandera flagno no es igual al de value"""
  return banderas[flagno] != value

def c2_NOTSAME (flagno1, flagno2):
  """Satisfactorio si el contenido de la bandera flagno1 no es el mismo que el de la bandera flagno2"""
  return banderas[flagno1] != banderas[flagno2]

def c2_SAME (flagno1, flagno2):
  """Satisfactorio si el contenido de la bandera flagno1 es el mismo que el de la bandera flagno2"""
  return banderas[flagno1] == banderas[flagno2]


# ACCIONES

def a0_ANYKEY ():
  """Imprime el mensaje del sistema 16 al final de la pantalla, y se espera hasta que se pulse una tecla, o hasta que haya pasado el tiempo muerto, si se ha usado tiempo muerto"""
  subvActual = gui.elige_subventana (3)
  gui.mueve_cursor (0, gui.limite[1] - 2)  # Es en las dos �ltimas l�neas donde se imprime
  gui.imprime_cadena (msgs_sys[16], False)
  gui.espera_tecla (banderas[48] if banderas[49] & 4 else 0)
  gui.mueve_cursor (0, gui.limite[1] - 2)
  gui.borra_pantalla (True)          # Borra el texto escrito
  gui.elige_subventana (subvActual)  # Vuelve a la subventana inicial

def a0_AUTOD ():
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en este orden de prioridad: en la lista de objetos llevados, en la de objetos puestos, y en la localidad actual. Si se encuentra, ejecuta DROP sobre ese objeto. Si no se encuentra ah�, imprime MS28 si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  return busca_condacto ('accionAUTO') (a1_DROP, (254, 253, banderas[38]), 28)

def a0_AUTOG ():
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en este orden de prioridad: en la localidad actual, en la lista de objetos llevados, y en la de objetos puestos. Si se encuentra, ejecuta GET sobre ese objeto. Si no se encuentra ah�, imprime MS26 si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  return busca_condacto ('accionAUTO') (a1_GET, (banderas[38], 254, 253), 26)

def a0_AUTOR ():
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en este orden de prioridad: en la lista de objetos puestos, en la de objetos llevados, y en la localidad actual. Si se encuentra, ejecuta REMOVE sobre ese objeto. Si no se encuentra ah�, imprime MS23 si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  return busca_condacto ('accionAUTO') (a1_REMOVE, (253, 254, banderas[38]), 23)

def a0_AUTOW ():
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en este orden de prioridad: en la lista de objetos llevados, en la de objetos puestos, y en la localidad actual. Si se encuentra, ejecuta WEAR sobre ese objeto. Si no se encuentra ah�, imprime MS28 si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  return busca_condacto ('accionAUTO') (a1_WEAR, (254, 253, banderas[38]), 28)

def a0_BACKAT ():
  """Cambia la posici�n del cursor de la subventana elegida, a la guardada mediante SAVEAT"""
  gui.carga_cursor()

def a0_BELL ():
  """Emite un pitido"""
  prn ('a0_BELL no implementado', file = sys.stderr)

def a0_END ():
  """Pregunta si se desea volver a empezar (MS13), y si la respuesta empieza por la primera letra del MS31, imprime el MS14 y termina completamente la ejecuci�n de la aventura. Si no, reinicia la aventura"""
  respuesta = gui.lee_cadena (msgs_sys[13] + msgs_sys[33])
  if respuesta[0].lower() == msgs_sys[31][0].lower():
    gui.imprime_cadena (msgs_sys[14])
    return 7
  return 0

def a0_LISTOBJ ():
  """Lista los objetos presentes, si los hay, anteponiendo el mensaje de sistema 1"""
  presentes = []
  for objno in range (len (locs_objs)):
    if locs_objs[objno] == banderas[38]:
      presentes.append (objno)
  if presentes:
    tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
    gui.imprime_cadena (msgs_sys[1], tiempo = tiempoTimeout)  # 'Puedes ver '
    if not banderas[53] & 64:  # Listar uno por l�nea
      gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
    for i in range (len (presentes)):
      descripcion = desc_objs[presentes[i]]
      if banderas[53] & 64:  # Listar como una frase
        if '.' in descripcion:
          descripcion = descripcion[:descripcion.index ('.')]
        gui.imprime_cadena (descripcion[0].lower() + descripcion[1:], tiempo = tiempoTimeout)
        if i == len (presentes) - 1:  # �ltimo objeto presente
          gui.imprime_cadena (msgs_sys[48], tiempo = tiempoTimeout)  # '.'
        elif i == len (presentes) - 2:
          gui.imprime_cadena (msgs_sys[47], tiempo = tiempoTimeout)  # ' y '
        else:
          gui.imprime_cadena (msgs_sys[46], tiempo = tiempoTimeout)  # ', '
      else:  # Listar uno por l�nea
        gui.imprime_cadena (descripcion, tiempo = tiempoTimeout)
        gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
    banderas[53] |= 128  # Marca que se han listado objetos
  elif banderas[53] & 128:
    banderas[53] ^= 128  # Marca que no se han listado objetos

def a0_LOAD ():
  """Carga el contenido de las banderas y de las localidades de los objetos desde un fichero"""
  nombreFich = (gui.lee_cadena (msgs_sys[60] + msgs_sys[33]) + '.' + EXT_SAVEGAME).lower()
  # Buscamos el fichero con independencia de may�sculas y min�sculas
  for nombreFichero in os.listdir (os.path.dirname (ruta_bbdd)):
    if nombreFichero.lower() == nombreFich:
      nombreFich = os.path.join (os.path.dirname (ruta_bbdd), nombreFichero)
      break
  bien = True
  try:
    fichero = open (nombreFich, 'rb')
  except:
    imprime_mensaje (msgs_sys[54])  # Fichero inexistente
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
        del gui.historial[:]
      else:
        jkhsdjkfh  # Para que falle
    except:
      imprime_mensaje (msgs_sys[55])  # Fichero corrupto
  a0_ANYKEY()
  return 1  # Lo mismo que DESC

def a0_NEWLINE ():
  """Imprime un caracter de nueva l�nea"""
  if gui.paleta[1]:  # S�lo si hay paletas con y sin brillo
    gui.cambia_color_brillo (0)  # Parece ocurrir as� en el PAWS espa�ol de Aventuras AD.  TODO: revisar si recupera el valor de brillo inicial
  gui.imprime_cadena ('\n', tiempo = banderas[48] if banderas[49] & 2 else 0, restauraColores = True)

def a0_NEWTEXT ():
  """Vac�a el resto de la orden"""
  del frases[:]

def a0_NOTDONE ():
  """Concluye la ejecuci�n de la tabla actual, terminando como no satisfactorio"""
  return 4

def a0_PROTECT ():
  """Ejecutado desde el proceso 1, protege las l�neas anteriores a la del cursor, para que s�lo se haga scroll desde la del cursor en adelante"""
  if pila_procs[-1][0] == 1:
    gui.elige_subventana (2)
    gui.pos_subventana (0, gui.cursores[1][1])
    gui.cambia_topes (0, 0)  # Topes al m�ximo tama�o posible
    gui.mueve_cursor (gui.cursores[1][0])  # Deja el cursor en la misma columna que estaba
    banderas[41] = gui.cursores[1][1]

def a0_SAVE ():
  """Guarda el contenido de las banderas y de las localidades de los objetos a un fichero"""
  nombreFich = gui.lee_cadena (msgs_sys[60] + msgs_sys[33])
  invalido   = False
  if compatibilidad and len (nombreFich) > 8:
    invalido = True
  else:
    for caracter in nombreFich:
      if not caracter.isalnum():
        invalido = True
        break
  if invalido:
    imprime_mensaje (msgs_sys[59])  # Nombre de fichero inv�lido
  else:
    try:
      fichero = open (os.path.join (os.path.dirname (ruta_bbdd), nombreFich + '.' + EXT_SAVEGAME), 'wb')
      for bandera in banderas:
        fichero.write (struct.pack ('B', bandera))
      for loc_obj in locs_objs:
        fichero.write (struct.pack ('B', loc_obj))
      for i in range (len (locs_objs), 256):  # El resto de bytes los ocupamos con 0
        fichero.write (struct.pack ('B', 0))
    except:
      imprime_mensaje (msgs_sys[56])  # Error I/O
  a0_ANYKEY()
  return 1  # Lo mismo que DESC

def a0_SAVEAT ():
  """Memoriza la posici�n del cursor actual en la subventana elegida, para poderla recuperar luego con BACKAT"""
  gui.guarda_cursor()

def a0_WHATO ():
  # XXX: comportamiento no documentado: guarda el objeto est� donde est�, creado o no. TODO: ver si s�lo DAAD lo hace as�
  # TODO: ver si se combina este c�digo con el de accionAUTO
  """Busca el nombre y adjetivo de la SL actual en la tabla de objetos, y lo guarda como objeto referido actual si est� llevado, puesto o en la localidad del jugador, con este orden de prioridad"""
  localidades = (254, 253, banderas[38])
  # Obtenemos los objetos que est�n en estos sitios
  presentes   = {
    banderas[38]: [],
    253:          [],
    254:          [],
    -1:           []  # En otros sitios
  }
  for objno in range (len (locs_objs)):
    localidad = locs_objs[objno]
    if localidad in localidades:
      presentes[localidad].append (objno)
    elif nombres_objs[objno] != (255, 255):  # Para que no encajen con SL sin nombre ni adjetivo
      presentes[-1].append (objno)
  # Vemos si alguno encaja con la SL actual
  # TODO: validar esto comprobando con los int�rpretes de DAAD originales, viendo c�mo se desambigua por adjetivos, y qu� pasa si m�s de uno encaja
  for localidad in localidades + (-1, ):
    parcial = []  # Objetos que hicieron encaje parcial
    for objno in presentes[localidad]:
      (nombre, adjetivo) = nombres_objs[objno]
      if banderas[34] == nombre:
        if banderas[35] == adjetivo:
          obj_referido (objno)  # Encaje completo
          return
        if banderas[35] == 255:  # Encaje parcial, que dar por bueno si no hay encaje completo
          parcial.append (objno)
    if len (parcial) == 1:
      obj_referido (parcial[0])
      return
  obj_referido (255)  # Ning�n objeto encajaba, o hab�a ambig�edad


def a1_AUTOP (objno):
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en este orden de prioridad: en la lista de objetos llevados, en la de objetos puestos, y en la localidad actual. Si se encuentra, ejecuta PUTIN sobre ese objeto. Si no se encuentra ah�, imprime MS28 si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  return busca_condacto ('accionAUTO2') (a2_PUTIN, (254, 253, banderas[38]), 28, objno)

def a1_AUTOT (objno):
  """Busca un objeto con el primer nombre/adjetivo de la SL actual, en este orden de prioridad: en el contenedor dado, en la lista de objetos llevados, en la de objetos puestos, y en la localidad actual. Si se encuentra, ejecuta TAKEOUT sobre ese objeto. Si no se encuentra ah�, imprime MS52 m�s la descripci�n corta del objeto y MS51 si el nombre de la SL no est� en el vocabulario o existe un objeto con ese nombre en el juego (FIXME: �creado?), o MS8 si no hay ning�n objeto con ese nombre. Al final, hace NEWTEXT en caso de error, y luego DONE incondicionalmente"""
  return busca_condacto ('accionAUTO2') (a2_TAKEOUT, (objno, 254, 253, banderas[38]), 52, objno, 51)

def a1_CREATE (objno):
  """Cambia la localidad del objeto objno a la localidad actual, y decrementa el n�mero de objetos llevados si objno se estaba llevando"""
  obj_referido (objno)
  if locs_objs[objno] in (253, 254):  # Llevado o puesto
    peso_llevado[0] -= min (peso_llevado[0], banderas[55])
    if locs_objs[objno] == 254:  # Llevado
      banderas[1] = max (0, banderas[1] - 1)
  locs_objs[objno] = banderas[38]

def a1_CHARSET (numFuente):
  """Cambia la fuente seleccionada por la de �ndice dado si es v�lido, de lo contrario no hace nada"""
  gui.cambia_fuente (numFuente)

def a1_DESTROY (objno):
  """Cambia la localidad del objeto objno a 252 (no creado), y decrementa el n�mero de objetos llevados si objno se estaba llevando"""
  obj_referido (objno)  # TODO: comprobar si PAWS tambi�n lo hace
  if locs_objs[objno] in (253, 254):  # Llevado o puesto
    peso_llevado[0] -= min (peso_llevado[0], banderas[55])
    if locs_objs[objno] == 254:  # Llevado
      banderas[1] = max (0, banderas[1] - 1)
  locs_objs[objno] = 252

def a1_DOALL (locno):
  global doall_siguiente
  if doall_activo:
    if banderas[50] == locno:
      doall_siguiente += 1  # Siguiente objeto que comprobar
    else:  # TODO: ver si es as� como se interrumpe DOALL, y no s�lo poni�ndola a cero
      doall_siguiente = 256  # Interrumpimos limpiamente el bucle DOALL
  else:
    banderas[50] = locno
    doall_activo.extend (pila_procs[-1])
    doall_siguiente = 0
  # Buscamos en los objetos presentes en locno
  if locno == 255:  # Hace referencia a la localidad actual
    locno = banderas[38]
  for objno in range (doall_siguiente, len (locs_objs)):
    if locs_objs[objno] == locno:
      (nombre, adjetivo) = nombres_objs[objno]
      # Si hay encaje con nombre/adjetivo 2, el int�rprete asume que se us� excepci�n, como COGER TODO SALVO BOLI ROJO
      if banderas[44] == nombre and banderas[45] in (adjetivo, 255):
        continue  # Encaja con la excepci�n, por lo que omite este objeto
      banderas[34] = nombre
      banderas[35] = adjetivo
      obj_referido (objno)
      return  # Prosigue la ejecuci�n con estos valores para la SL
  else:  # No hay m�s objetos que encajen, fin del bucle DOALL
    del doall_activo[:]
    if not doall_siguiente:  # Ning�n encaje desde el inicio
      return busca_condacto ('a0_NOTDONE') ()
    return busca_condacto ('a0_DONE') ()

def a1_DROP (objno):
  """Si el objeto se lleva puesto, imprime MS24. Si el objeto est� en la localidad actual, imprime MS49. Si no est� presente, imprime MS28. En caso de una de estas condiciones de fallo, ejecuta NEWTEXT y termina con DONE. En caso contrario (�xito), mueve el objeto a la localidad actual, decrementa la bandera 1, e imprime MS39"""
  obj_referido (objno)
  if locs_objs[objno] == 253:
    imprime_mensaje (msgs_sys[24])
  elif locs_objs[objno] == banderas[38]:
    imprime_mensaje (msgs_sys[49])
  elif locs_objs[objno] != 254:
    imprime_mensaje (msgs_sys[28])
  else:
    banderas[1]      = max (0, banderas[1] - 1)
    locs_objs[objno] = banderas[38]
    peso_llevado[0] -= min (peso_llevado[0], banderas[55])
    imprime_mensaje (msgs_sys[39])  # Dejo _
    return
  gui.imprime_cadena ('\n', tiempo = banderas[48] if banderas[49] & 2 else 0)
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE') ()

def a1_EXTERN (value):
  prn ('a1_EXTERN no implementado', file = sys.stderr)

def a1_GET (objno):
  """Si el objeto se lleva (puesto o no), imprime MS25. Si el objeto no est� presente, imprime MS26. Si el peso total de los objetos llevados (puestos o no) m�s el de este objeto superar� el m�ximo permitido, imprime MS43. Si se superar�a el m�ximo de objetos llevables, imprime MS27. En caso de una de estas condiciones de fallo, ejecuta NEWTEXT y termina con DONE. En caso contrario (�xito), mueve el objeto al inventario (254), incrementa la bandera 1, e imprime MS36"""
  obj_referido (objno)  # TODO: comprobar si PAWS tambi�n lo hace
  if locs_objs[objno] in (253, 254):
    imprime_mensaje (msgs_sys[25])
  elif locs_objs[objno] != banderas[38]:
    imprime_mensaje (msgs_sys[26])
  elif peso_llevado[0] + banderas[55] > banderas[52]:
    imprime_mensaje (msgs_sys[43])
  elif banderas[1] >= banderas[37]:
    imprime_mensaje (msgs_sys[27])
  else:
    banderas[1]       = min (banderas[1] + 1, 255)
    locs_objs[objno]  = 254
    peso_llevado[0]  += banderas[55]
    imprime_mensaje (msgs_sys[36])  # Cojo _
    return
  gui.imprime_cadena ('\n', tiempo = banderas[48] if banderas[49] & 2 else 0)
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE') ()

def a1_GRAPHIC (option):
  prn ('TODO: a1_GRAPHIC no implementado', file = sys.stderr)  # TODO

def a1_INPUT (options):
  """Cambia opciones de la entrada del jugador"""
  if options & 1:  # Pedir la orden en la parte de abajo de la pantalla
    # Usaremos el n�mero de opci�n 8 porque el 1 en DAAD es otra cosa
    options = options - (options & 1) + 8
  gui.cambia_subv_input (0, options)

def a1_LINE (lineno):
  """Cambia el n�mero de l�nea donde inicia el texto, para dejar la parte de arriba reservada para gr�ficos"""
  gui.pos_subventana (0, lineno)

def a1_LISTAT (locno):
  """Lista los objetos presentes en la localidad locno, o el mensaje de sistema 53 si no hay ninguno"""
  # Obtenemos los objetos presentes en locno
  presentes = []
  for objno in range (len (locs_objs)):
    if locs_objs[objno] == locno:
      presentes.append (objno)
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  if presentes:  # Los listamos
    for i in range (len (presentes)):
      descripcion = desc_objs[presentes[i]][0].lower() + desc_objs[presentes[i]][1:]
      if banderas[53] & 64:  # Listar como una frase
        if '.' in descripcion:
          descripcion = descripcion[:descripcion.index ('.')]
        gui.imprime_cadena (descripcion, tiempo = tiempoTimeout)
        if i == len (presentes) - 1:  # �ltimo objeto presente
          gui.imprime_cadena (msgs_sys[48], tiempo = tiempoTimeout)  # '.'
        elif i == len (presentes) - 2:
          gui.imprime_cadena (msgs_sys[47], tiempo = tiempoTimeout)  # ' y '
        else:
          gui.imprime_cadena (msgs_sys[46], tiempo = tiempoTimeout)  # ', '
      else:  # Listar uno por l�nea
        gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
        gui.imprime_cadena (descripcion, tiempo = tiempoTimeout)
    banderas[53] |= 128  # Marca que se han listado objetos
  else:
    gui.imprime_cadena (msgs_sys[53], tiempo = tiempoTimeout)  # 'nada.'
    if banderas[53] & 128:
      banderas[53] ^= 128  # Marca que no se han listado objetos

def a1_MES (mesno):
  """Imprime el mensaje de usuario dado por mesno, en los colores actuales"""
  imprime_mensaje (msgs_usr[mesno])

def a1_MODE (value):
  """Cambia el modo de impresi�n"""
  banderas[40] = value

def a1_PICTURE (locno):
  """Dibuja el gr�fico definido por locno, sin importar que sea una subrutina o un gr�fico principal

Nota: no se hace un clear de la pantalla ni de los colores (como s� ocurre cuando se describe una localidad)

Ser� dibujado a partir del �ltimo punto usado por el gr�fico que se pint� con anterioridad"""
  gui.dibuja_grafico (locno)

def a1_PRINT (flagno):
  """Imprime el n�mero contenido en la bandera flagno"""
  gui.imprime_cadena (str (banderas[flagno]), tiempo = banderas[48] if banderas[49] & 2 else 0)

def a1_PROCESS (procno):
  """Transfiere el flujo de ejecuci�n del int�rprete a la tabla de proceso de n�mero procno"""
  return -procno

def a1_PROMPT (sysno):
  """Hace que el mensaje de sistema que indica sysno se imprima cada vez que el int�rprete vaya a pedirle una l�nea de �rdenes al jugador"""
  banderas[42] = sysno

# TODO: ver si se comporta como PLACE si locno es 255. Si es as�, corregir la firma y llamar a PLACE desde aqu�
def a1_PUTO (locno):
  """Mueve el objeto actual referido a la localidad dada, actualizando la cuenta de objetos llevados"""
  if banderas[51] > len (locs_objs):
    prn ('Advertencia: llamado PUTO con objeto referido fuera del rango de objetos:', banderas[51])
    return
  locActual = locs_objs[banderas[51]]
  if locno == locActual:
    return
  locs_objs[banderas[51]] = locno
  if locActual == 254:  # Estaba siendo llevado
    banderas[1] = max (0, banderas[1] - 1)
  elif locno == 254:  # Pasa a ser llevado
    banderas[1] = min (banderas[1] + 1, 255)

def a1_RAMLOAD (flagno):
  """Carga el contenido de las banderas hasta flagno y de las localidades de los objetos desde memoria"""
  if not partida:  # No hay partida guardada en memoria
    gui.imprime_cadena (msgs_sys[8], tiempo = banderas[48] if banderas[49] & 2 else 0)  # No puedes
    return
  for b in range (flagno + 1):
    banderas[b] = partida[b]
  for o in range (num_objetos[0]):
    locs_objs[o] = partida[NUM_BANDERAS[0] + o]
  del gui.historial[:]

def a1_RANDOM (flagno):
  """Pone en la bandera flagno un n�mero al azar entre 1 y 100"""
  banderas[flagno] = random.randint (1, 100)

def a1_REMOVE (objno):
  """Si el objeto se lleva (pero no puesto) o est� en la localidad actual, imprime MS50. Si el objeto no est� puesto, imprime MS23. Si el objeto no es prenda, imprime MS41. Si se superar�a el m�ximo de objetos llevables, imprime MS42. En caso de una de estas condiciones de fallo, ejecuta NEWTEXT y termina con DONE. En caso contrario (�xito), mueve el objeto al inventario (254), incrementa la bandera 1, e imprime MS38"""
  obj_referido (objno)  # TODO: comprobar si PAWS tambi�n lo hace
  if locs_objs[objno] in (254, banderas[38]):
    imprime_mensaje (msgs_sys[50])
  elif locs_objs[objno] != 253:
    imprime_mensaje (msgs_sys[23])
  elif not banderas[57]:  # El objeto no es prenda
    imprime_mensaje (msgs_sys[41])
  elif banderas[1] >= banderas[37]:
    imprime_mensaje (msgs_sys[42])
  else:
    banderas[1]      = min (banderas[1] + 1, 255)
    locs_objs[objno] = 254
    imprime_mensaje (msgs_sys[38])  # Me quito _
    return
  gui.imprime_cadena ('\n', tiempo = banderas[48] if banderas[49] & 2 else 0)
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE') ()

def a1_WEAR (objno):
  """Si el objeto est� en la localidad actual, imprime MS49. Si el objeto est� puesto, imprime MS29. Si el objeto no se lleva, imprime MS28. Si el objeto no es prenda, imprime MS40. En caso de una de estas condiciones de fallo, ejecuta NEWTEXT y termina con DONE. En caso contrario (�xito), mueve el objeto a puestos (253), decrementa la bandera 1, e imprime MS37"""
  obj_referido (objno)  # TODO: comprobar si PAWS tambi�n lo hace
  if locs_objs[objno] == banderas[38]:
    imprime_mensaje (msgs_sys[49])
  elif locs_objs[objno] == 253:
    imprime_mensaje (msgs_sys[29])
  elif locs_objs[objno] != 254:
    imprime_mensaje (msgs_sys[28])
  elif not banderas[57]:  # El objeto no es prenda
    imprime_mensaje (msgs_sys[40])
  else:
    banderas[1]      = max (0, banderas[1] - 1)
    locs_objs[objno] = 253
    imprime_mensaje (msgs_sys[37])  # Me pongo _
    return
  gui.imprime_cadena ('\n', tiempo = banderas[48] if banderas[49] & 2 else 0)
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE') ()

def a1_SET (flagno):
  """Pone el valor de la bandera flagno a 255"""
  if flagno == 38:
    gui.imprime_cadena ('Error en tiempo de ejecuci�n 1. Se intent� hacer SET 38')
    a0_ANYKEY()
    return 7
  banderas[flagno] = 255

def a1_WEIGHT (flagno):
  """Calcula el peso total de los objetos llevados por el jugador, y lo guarda en la bandera flagno

Si el resultado excede 255, la bandera flagno se pone a 255"""
  banderas[flagno] = min (peso_llevado[0], 255)


def a2_ABILITY (value1, value2):
  """Ajusta la bandera 37 (que tiene el n�mero m�ximo de objetos llevados) al valor dado por value1, y la bandera 52 (el peso m�ximo que el jugador puede llevar) al valor dado por value2"""
  banderas[37] = value1
  banderas[52] = value2

def a2_ADD (flagno1, flagno2):
  """Se le a�ade al valor de la bandera flagno2 el valor de la bandera flagno1

Si el resultado excede 255, la bandera flagno2 se pone a 255"""
  banderas[flagno2] += banderas[flagno1]
  if banderas[flagno2] > 255:
    banderas[flagno2] = 255

def a2_COPYFF (flagno1, flagno2):
  """El contenido de la bandera flagno1 se copia en la bandera flagno2"""
  banderas[flagno2] = banderas[flagno1]

# TODO: debe fallar si flagno vale 255
def a2_COPYFO (flagno, objno):
  """El contenido de la bandera flagno1 se copia como localidad del objeto objno"""
  obj_referido (objno)  # TODO: comprobar si PAWS tambi�n lo hace
  locs_objs[objno] = banderas[flagno]

def a2_COPYOF (objno, flagno):
  """La localidad del objeto objno se copia en la bandera flagno"""
  banderas[flagno] = locs_objs[objno] if objno < len (locs_objs) else 255  # XXX: al menos La Aventura Espacial lo hace as�

def a2_COPYOO (objno1, objno2):
  """La localidad del objeto objno1 se copia como localidad del objeto objno2, y se marca objno2 como objeto actualmente referido"""
  obj_referido (objno2)
  locs_objs[objno2] = locs_objs[objno1]

def a2_MODE (value, option):
  """Cambia el modo de impresi�n"""
  banderas[40] = value
  # TODO: implementar interpretaci�n del par�metro option

def a2_PLACE (objno, locno):
  """Mueve el objeto a la localidad locno, actualizando cuenta de objetos llevados en caso necesario."""
  if locno == 255:  # Hace referencia a la localidad actual
    locno = banderas[38]
  obj_referido (objno)  # TODO: comprobar si PAWS tambi�n lo hace
  locActual = locs_objs[objno]  # Localidad actual del objeto
  if locno == locActual:
    return
  locs_objs[objno] = locno
  if locActual == 254:  # Estaba siendo llevado
    banderas[1]      = max (0, banderas[1] - 1)
    peso_llevado[0] -= min (peso_llevado[0], banderas[55])
  elif locno == 254:  # Pasa a ser llevado
    banderas[1]      = min (banderas[1] + 1, 255)
    peso_llevado[0] += banderas[55]

def a2_PUTIN (objno, locno):
  """Si el objeto objno se lleva puesto, imprime MS24. Si el objeto objno est� en la localizaci�n actual, imprime MS49. Si no est� presente, imprime MS28. En caso de una de estas condiciones de fallo, ejecuta NEWTEXT y termina con DONE. En caso contrario (�xito), mueve el objeto al contenedor locno, decrementa la bandera 1, e imprime MS44, la descripci�n corta del contenedor locno y MS51"""
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  obj_referido (objno)
  if locs_objs[objno] == 253:
    imprime_mensaje (msgs_sys[24])
  elif locs_objs[objno] == banderas[38]:
    imprime_mensaje (msgs_sys[49])
  elif locs_objs[objno] != 254:
    imprime_mensaje (msgs_sys[28])
  else:
    if locs_objs[locno] not in (253, 254):
      peso_llevado[0] -= min (peso_llevado[0], banderas[55])
    banderas[1]      = max (0, banderas[1] - 1)
    locs_objs[objno] = locno
    imprime_mensaje (msgs_sys[44])  # El _ est� en
    if locno < num_objetos[0]:
      desc_obj = desc_objs[locno]
      if '.' in desc_obj:
        desc_obj = desc_obj[:desc_obj.index ('.')]
      gui.imprime_cadena (cambia_articulo (desc_obj), tiempo = tiempoTimeout)
    gui.imprime_cadena (msgs_sys[51], tiempo = tiempoTimeout)
    return
  gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE') ()

def a2_PRINTAT (rowno, colno):
  """La posici�n de impresi�n actual se cambia al valor espec�fico dado por rowno y colno

Esto tambi�n vaciar� el buffer actual y restaurar� los colores temporales a los colores de fondo"""
  gui.mueve_cursor (colno, rowno)
  # FIXME: �Vaciar? �Colores?

def a2_SUB (flagno1, flagno2):
  """Se le resta al valor de la bandera flagno2 el valor de la bandera flagno1

Si el resultado es menor que 0, la bandera flagno2 se pone a 0"""
  banderas[flagno2] -= banderas[flagno1]
  if banderas[flagno2] < 0:
    banderas[flagno2] = 0

def a2_TAKEOUT (objno, locno):
  """Si el objeto objno se lleva encima o puesto, imprime MS25. Si el objeto objno est� en la localizaci�n actual, imprime MS45, la descripci�n corta del contenedor locno y MS51. Si no est� en locno, imprime MS52, la descripci�n corta del contenedor locno y MS51. Si el peso total de los objetos llevados (puestos o no) m�s el de este objeto superar� el m�ximo permitido, imprime MS43. Si se superar�a el m�ximo de objetos llevables, imprime MS27. En caso de una de estas condiciones de fallo, ejecuta NEWTEXT y termina con DONE. En caso contrario (�xito), mueve el objeto al contenedor locno, incrementa la bandera 1, e imprime MS36"""
  # XXX: �no deber�a comprobar tambi�n que el contenedor locno est� presente?
  tiempoTimeout = banderas[48] if banderas[49] & 2 else 0
  obj_referido (objno)
  if locs_objs[objno] in (253, 254):
    imprime_mensaje (msgs_sys[25])
  elif locs_objs[objno] != locno:
    if locs_objs[objno] == banderas[38]:
      imprime_mensaje (msgs_sys[45])
    else:
      imprime_mensaje (msgs_sys[52])
    if locno < num_objetos[0]:
      desc_obj = desc_objs[locno]
      if '.' in desc_obj:
        desc_obj = desc_obj[:desc_obj.index ('.')]
      gui.imprime_cadena (cambia_articulo (desc_obj), tiempo = tiempoTimeout)
    gui.imprime_cadena (msgs_sys[51], tiempo = tiempoTimeout)
  elif locs_objs[locno] == banderas[38] and peso_llevado[0] + banderas[55] > banderas[52]:
    imprime_mensaje (msgs_sys[43])
  elif banderas[1] >= banderas[37]:
    imprime_mensaje (msgs_sys[27])
  else:
    if locs_objs[locno] == banderas[38]:
      peso_llevado[0] += banderas[55]
    banderas[1]      = min (banderas[1] + 1, 255)
    locs_objs[objno] = 254
    imprime_mensaje (msgs_sys[36])  # Coges _
    return
  gui.imprime_cadena ('\n', tiempo = tiempoTimeout)
  a0_NEWTEXT()
  return busca_condacto ('a0_DONE') ()

def a2_TIME (length, option):
  """Permite que los INPUT aparezcan solos despu�s de pasar un tiempo length, cuya duraci�n se especifica en intervalos de 1 segundo (1,28 en la versi�n Spectrum)

option determina en qu� circunstancias puede ocurrir esto"""
  banderas[48] = length
  banderas[49] = option

def a2_WEIGH (objno, flagno):
  """Guarda en flagno el peso completo del objeto objno"""
  banderas[flagno] = da_peso (objno)
