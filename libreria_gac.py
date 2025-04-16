# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librer�a de GAC (parte com�n a editor, compilador e int�rprete)
# Copyright (C) 2025 Jos� Manuel Ferrer Ortiz
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
import sys  # Para stderr

from bajo_nivel import *
from prn_func   import _, prn


# Variables que se exportan (fuera del paquete)

# Ponemos los m�dulos de condactos en orden, para permitir que las funciones de los condactos de igual firma (nombre, tipo y n�mero de par�metros) de los sistemas m�s nuevos tengan precedencia sobre las de sistemas anteriores
mods_condactos = ('condactos_gac', )

accion_okay    = [0]    # Si la �ltima acci�n fue satisfactoria, para el condacto OKAY
atributos      = {}     # Atributos de los objetos (sus pesos)
conexiones     = {}     # Listas de conexiones de cada localidad
conversion     = {}     # Tabla de conversi�n de caracteres
desc_locs      = {}     # Descripciones de las localidades
desc_objs      = {}     # Descripciones de los objetos
loc_inicio     = [1]    # Localidad de inicio en la aventura
locs_iniciales = {}     # Localidades iniciales de los objetos
msgs_sys       = {}     # Mensajes de sistema
msgs_usr       = []     # Mensajes de usuario
nombres_objs   = {}     # Nombre y adjetivo de los objetos
num_objetos    = [256]  # N�mero de objetos (en lista para pasar por referencia)
tablas_proceso = {}     # Tablas de proceso
udgs           = []     # UDGs (caracteres gr�ficos definidos por el usuario)
vocabulario    = []     # Vocabulario

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = (('carga_sna', ('sna',), _('ZX 48K memory snapshots with GAC')), )
# Funci�n que crea una nueva base de datos (vac�a)
func_nueva = ''


# Constantes que se exportan (fuera del paquete)

BANDERA_VERBO      = [128]  # Bandera con el verbo de la SL actual
BANDERA_NOMBRE     = [129]  # Bandera con el primer nombre de la SL actual
BANDERA_LOC_ACTUAL = [130]  # Bandera con la localidad actual
BANDERA_ADVERBIO   = [131]  # Bandera con el adverbio o preposici�n de la SL actual
BANDERA_NOMBRE2    = [132]  # Bandera con el segundo nombre de la SL actual
BANDERA_PRONOMBRE  = [133]  # Bandera con la palabra por la que sustituir el pronombre
INDIRECCION        = False  # El parser no soporta indirecci�n (para el IDE)
LONGITUD_PAL       = 99     # Longitud m�xima para las palabras de vocabulario
NOMBRE_SISTEMA     = 'GAC'  # Nombre de este sistema
NUM_ATRIBUTOS      = [0]    # N�mero de atributos de objeto
NUM_BANDERAS       = [134]  # N�mero de banderas del parser (de usuario y de sistema)
NUM_BANDERAS_ACC   = [128]  # N�mero de banderas del parser accesibles por el programador
NUM_MARCADORES     = 256    # N�mero de marcadores booleanos del parser
NOMB_COMO_VERB     = [0]    # N�mero de nombres convertibles a verbo
PREP_COMO_VERB     = 0      # N�mero de preposiciones convertibles a verbo
# Nombres de las tablas de proceso (para el IDE)
NOMBRES_PROCS = {0: _('High priority'), None: _('Location'), 10000: _('Low priority')}
# Nombres de los tipos de palabra (para el IDE y el int�rprete)
TIPOS_PAL    = (_('Verb'), _('Adverb'), _('Noun'))
TIPOS_PAL_ES = ('Verbo', 'Adverbio', 'Nombre')


# Variables que s�lo se usan en este m�dulo

# Desplazamientos (offsets/posiciones) en la cabecera
CAB_FIN_MEMORIA     =  0  # �ltima posici�n de memoria
CAB_POS_NOMBRES     =  2  # Posici�n de los nombres
CAB_POS_ADVERBIOS   =  4  # Posici�n de los adverbios
CAB_POS_OBJETOS     =  6  # Posici�n de los objetos
CAB_POS_LOCALIDADES =  8  # Posici�n de las localidades
CAB_POS_CONDS_ALTA  = 10  # Posici�n de las condiciones de alta prioridad
CAB_POS_CONDS_LOCS  = 12  # Posici�n de las condiciones locales
CAB_POS_CONDS_BAJA  = 14  # Posici�n de las condiciones de baja prioridad
CAB_POS_MENSAJES    = 16  # Posici�n de los mensajes
CAB_POS_PALABRAS    = 20  # Posici�n de las palabras

# Desplazamientos que no est�n en la cabecera, respecto al inicio de la cabecera
CAB_PUNTUACION    = -824  # Posici�n de la marca identificativa del int�rprete GAC
LOC_INICIO        = 48    # Localidad de inicio en la aventura
POS_VERBOS        = 50    # Datos de los verbos

abreviaturas   = []
alinear        = False  # Si alineamos con relleno (padding) las listas de desplazamientos a posiciones pares
compatibilidad = True   # Modo de compatibilidad con los int�rpretes originales
despl_ini      = 0      # Desplazamiento inicial para cargar desde memoria
palabras       = []     # Palabras que se usan para el vocabulario y los textos
pos_cabecera   = 0      # Posici�n en el fichero donde inicia la base de datos

puntuacion = '\x00 .,-!?:'  # Secuencia que identifica que hay un int�rprete de GAC

# Desplazamientos iniciales para cargar desde memoria, de las plataformas en las que �ste no es 0
despl_ini_plat = {
  0: 16357  # Spectrum ZX
}


# Diccionario de condactos

condactos = {
  # XXX: parece que s�lo IF se comporta como una condici�n
  # XXX: parece que s�lo PUSH tiene par�metros
  # El formato es el siguiente:
  # c�digo : (nombre, par�metros, es_acci�n, flujo)
  # Donde:
  #   par�metros es una cadena con el tipo de cada par�metro
  #   flujo indica si el condacto cambia el flujo de ejecuci�n incondicionalmente, por lo que todo c�digo posterior en su entrada ser� inalcanzable
  # Y los tipos de los par�metros se definen as�:
  # W : Valor entero de 15 bits (word) sin signo, de 0 a 32767
   1 : ('AND',  '',  True,  False),
   2 : ('OR',   '',  True,  False),
   3 : ('NOT',  '',  True,  False),
   4 : ('XOR',  '',  True,  False),
   5 : ('HOLD', '',  True,  False),
   6 : ('GET',  '',  True,  False),
   7 : ('DROP', '',  True,  False),
   8 : ('SWAP', '',  True,  False),
   9 : ('TO',   '',  True,  False),
  10 : ('OBJ',  '',  True,  False),
  11 : ('SET',  '',  True,  False),
  12 : ('RESE', '',  True,  False),
  13 : ('SET?', '',  True,  False),
  14 : ('RES?', '',  True,  False),
  15 : ('CSET', '',  True,  False),
  16 : ('CTR',  '',  True,  False),
  17 : ('DECR', '',  True,  False),
  18 : ('INCR', '',  True,  False),
  19 : ('EQU?', '',  True,  False),
  20 : ('DESC', '',  True,  False),
  21 : ('LOOK', '',  True,  False),
  22 : ('MESS', '',  True,  False),
  23 : ('PRIN', '',  True,  False),
  24 : ('RAND', '',  True,  False),
  25 : ('LT',   '',  True,  False),  # Es el condacto <
  26 : ('GT',   '',  True,  False),  # Es el condacto >
  27 : ('EQ',   '',  True,  False),  # Es el condacto =
  28 : ('SAVE', '',  True,  False),
  29 : ('LOAD', '',  True,  False),
  30 : ('HERE', '',  True,  False),
  31 : ('CARR', '',  True,  False),  # TODO: revisar por qu� hay dos CARR y se usan los dos en Quijote de ZX
  32 : ('CARR', '',  True,  False),  # TODO: revisar por qu� hay dos CARR y se usan los dos en Quijote de ZX
  33 : ('PLUS', '',  True,  False),  # Es el condacto +
  34 : ('MINU', '',  True,  False),  # Es el condacto -
  35 : ('TURN', '',  True,  False),
  36 : ('AT',   '',  True,  False),
  37 : ('BRIN', '',  True,  False),
  38 : ('FIND', '',  True,  False),
  39 : ('IN',   '',  True,  False),
  42 : ('OKAY', '',  True,  True),
  43 : ('WAIT', '',  True,  True),
  44 : ('QUIT', '',  True,  True),
  45 : ('EXIT', '',  True,  True),
  46 : ('ROOM', '',  True,  False),
  47 : ('NOUN', '',  True,  False),
  48 : ('VERB', '',  True,  False),
  49 : ('ADVE', '',  True,  False),
  50 : ('GOTO', '',  True,  True),   # TODO: comprobar si corta el flujo de ejecuci�n incondicionalmente
  51 : ('NO1',  '',  True,  False),
  52 : ('NO2',  '',  True,  False),
  53 : ('VBNO', '',  True,  False),
  54 : ('LIST', '',  True,  False),
  55 : ('PICT', '',  True,  False),
  56 : ('TEXT', '',  True,  False),
  57 : ('CONN', '',  True,  False),
  58 : ('WEIG', '',  True,  False),
  59 : ('WITH', '',  True,  False),
  60 : ('STRE', '',  True,  False),
  61 : ('LF',   '',  True,  False),
  62 : ('IF',   '',  False, False),
  80 : ('PUSH', 'W', True,  False),
}

# Funciones que utiliza el IDE, el int�rprete o el m�dulo de condactos directamente

def cadena_es_mayor (cadena1, cadena2):
  # type: (str, str) -> bool
  """Devuelve si la cadena1 es mayor a la cadena2 en el juego de caracteres de este sistema"""
  return cadena1 > cadena2

# Carga la base de datos entera desde el fichero de entrada
# Para compatibilidad con el IDE:
# - Recibe como primer par�metro un fichero abierto
# - Recibe como segundo par�metro la longitud del fichero abierto
# - Devuelve False si ha ocurrido alg�n error
def carga_sna (fichero, longitud):
  # type: (BinaryIO, int) -> bool
  """Carga la base de datos entera desde un fichero de imagen de memoria de Spectrum 48K

Para compatibilidad con el IDE:
- Recibe como primer par�metro un fichero abierto
- Recibe como segundo par�metro la longitud del fichero abierto
- Devuelve False si ha ocurrido alg�n error"""
  global fich_ent, long_fich_ent, plataforma
  fich_ent      = fichero
  long_fich_ent = longitud
  plataforma    = 0
  bajo_nivel_cambia_ent (fichero)
  try:
    preparaPlataforma()
    fich_ent.seek (pos_cabecera + CAB_PUNTUACION)
    assert fich_ent.read (8).decode() == puntuacion  # Secuencia que identifica que hay un int�rprete de GAC
    cargaPalabras()
    cargaLocalidades()
    cargaMensajes()
    cargaObjetos()
    cargaTablasProcesos()
    cargaVocabulario()
  except:
    return False

def escribe_secs_ctrl (cadena):
  # type: (str) -> str
  """Devuelve la cadena dada convirtiendo la representaci�n de secuencias de control en sus c�digos"""
  # TODO: implementar
  return cadena

def lee_secs_ctrl (cadena):
  # type: (str) -> str
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representaci�n imprimible"""
  return cadena.replace ('\\', '\\\\').replace ('\n', '\\n')


# Funciones auxiliares que s�lo se usan en este m�dulo

def cargaLocalidades ():
  # type: () -> None
  """Carga los datos de las localidades"""
  # Cargamos el c�digo de la localidad donde inicia la aventura
  fich_ent.seek (pos_cabecera + LOC_INICIO)
  loc_inicio[0] = carga_int2()
  # Vamos a la posici�n de las localidades
  fich_ent.seek (carga_desplazamiento (pos_cabecera + CAB_POS_LOCALIDADES))
  # Cargamos los datos cada localidad
  while True:
    codigo = carga_int2()
    if codigo == 0:
      break  # Ya no hay m�s localidades
    longitud = carga_int2() - 2  # Descontamos ya los 2 bytes de su gr�fico
    grafico  = carga_int2()
    # Cargamos las conexiones de esta localidad
    salidas = []
    while True:
      verbo     = carga_int1()  # Verbo de direcci�n
      longitud -= 1
      if verbo == 0:  # Fin de las conexiones de esta localidad
        break
      destino   = carga_int2()  # Localidad de destino
      longitud -= 2
      salidas.append ((verbo, destino))
    # Guardamos los datos de esta localidad
    conexiones[codigo] = salidas
    desc_locs[codigo]  = daCadena (longitud)

def cargaMensajes ():
  # type: () -> None
  # Vamos a la posici�n de los mensajes
  fich_ent.seek (carga_desplazamiento (pos_cabecera + CAB_POS_MENSAJES))
  # Cargamos cada mensaje
  while True:
    codigo = carga_int1()
    if codigo == 0:
      break  # Ya no hay m�s mensajes
    longitud = carga_int1()
    msgs_sys[codigo] = daCadena (longitud)

def cargaObjetos ():
  # type: () -> None
  """Carga los datos de los objetos"""
  # Vamos a la posici�n de los objetos
  fich_ent.seek (carga_desplazamiento (pos_cabecera + CAB_POS_OBJETOS))
  # Cargamos los datos cada objeto
  while True:
    codigo = carga_int1()
    if codigo == 0:
      break  # Ya no hay m�s objetos
    longitud   = carga_int1() - 3  # Descontamos ya los 3 bytes de su peso y localidad inicial
    peso       = carga_int1()
    locInicial = carga_int2()
    # Guardamos los datos de este objeto
    atributos[codigo]      = peso
    desc_objs[codigo]      = daCadena (longitud)
    locs_iniciales[codigo] = locInicial
    nombres_objs[codigo]   = ((codigo, 255))

def cargaPalabras ():
  # type: () -> None
  """Carga las palabras que se usan para el vocabulario y los textos"""
  # Vamos a la posici�n de las palabras
  fich_ent.seek (carga_desplazamiento (pos_cabecera + CAB_POS_PALABRAS))
  # Cargamos cada palabra
  while True:
    invalida = True  # Si parece que esta palabra es inv�lida
    palabra  = ''
    try:
      longitud = carga_int1()
      invalida = False
      for c in range (longitud):
        byteActual = carga_int1()
        caracter   = chr (byteActual & 127)
        palabra   += caracter
        if caracter < '"' or caracter.islower():
          invalida = True
          break  # Esto no parece ser una palabra
        if byteActual & 128:  # Marca de fin de la palabra
          break
      if len (palabra) < longitud:
        if invalida:
          prn ('Advertencia: la palabra', len (palabras), 'parece ser inv�lida', file = sys.stderr)
        else:
          prn ('Advertencia: la palabra', len (palabras), 'termina antes de lo que indica su longitud', file = sys.stderr)
        for c in range (longitud - len (palabra)):
          carga_int1()
    except:  # Normalmente, s�lo ocurrir� cuando termine el fichero
      if palabra:
        palabras.append (palabra.lower())
      break  # Ya no deber�a haber m�s palabras
    palabras.append ('' if invalida else palabra.lower())

def cargaTablasProcesos ():
  # type: () -> None
  """Carga las tablas de condiciones sobre tablas_proceso como diccionario, con �ndice 0 la de alta prioridad, �ndice de la localidad correspondiente las locales, y con �ndice 10000 la de baja prioridad"""
  posiciones = {CAB_POS_CONDS_ALTA: 0, CAB_POS_CONDS_LOCS: None, CAB_POS_CONDS_BAJA: 10000}
  for posicion, indiceTabla in posiciones.items():
    # Vamos a la posici�n de este tipo de condiciones
    fich_ent.seek (carga_desplazamiento (pos_cabecera + posicion))
    # Cargamos cada condici�n de este tipo
    entrada  = []
    entradas = []
    numTabla = 0
    while True:
      if indiceTabla == None:  # Son las condiciones locales
        if not numTabla:
          numTabla = carga_int2()
          if not numTabla:  # Ya no hay m�s condiciones locales
            break
      else:
        numTabla = indiceTabla
      codCondacto = carga_int1()  # C�digo de condacto/opcode
      if codCondacto == 0:  # Fin de este tipo de condiciones
        tablas_proceso[numTabla] = ((((255, 255), ) * len (entradas), entradas))
        entradas = []
        numTabla = None
        if indiceTabla != None:
          break
        else:
          continue
      if codCondacto & 128:  # Es PUSH
        byteBajo   = carga_int1()
        parametros = [((codCondacto & 127) << 8) + byteBajo]
        entrada.append ((80, parametros))
      elif codCondacto == 63:  # Es END, fin de entrada de condici�n
        entradas.append (entrada)
        entrada = []
      else:
        if codCondacto not in condactos:
          nombreTabla = NOMBRES_PROCS[indiceTabla]
          if indiceTabla == None:
            nombreTabla += ' ' + str (numTabla)
          try:
            muestraFallo ('FIXME: Condacto desconocido', 'C�digo de condacto: ' + str (codCondacto) + '\nTabla de condiciones: ' + nombreTabla + '\n�ndice de entrada: ' + str (len (entradas)))
          except:
            prn ('FIXME: N�mero de condacto', codCondacto, 'desconocido, en entrada', len (entradas), 'de la tabla de condiciones de', nombreTabla, file = sys.stderr)
            entradas.append (entrada)
            tablas_proceso[numTabla] = (((255, 255), ) * len (entradas), entradas)
            for entrada in entradas:
              for codCondacto, parametros in entrada:
                prn (condactos[codCondacto][0], parametros)
              prn()
          return
        parametros = []
        # TODO: �s�lo PUSH tiene par�metros? parece que s�, entonces lo siguiente es in�til
        # for i in range (len (condactos[codCondacto][1])):
        #   parametros.append (carga_int1())  # XXX: tipo de condactos si es que hay m�s de uno
        entrada.append ((codCondacto, parametros))

def cargaVocabulario ():
  # type: () -> None
  """Carga el vocabulario"""
  completas  = set()  # Palabras completas a�adidas al vocabulario
  prefijos   = {}     # Prefijos de palabras
  posiciones = (pos_cabecera + POS_VERBOS, carga_desplazamiento (pos_cabecera + CAB_POS_ADVERBIOS), carga_desplazamiento (pos_cabecera + CAB_POS_NOMBRES))
  for t in range (len (TIPOS_PAL)):
    posicion = posiciones[t]
    # Vamos a la posici�n de este tipo de palabras de vocabulario
    fich_ent.seek (posicion)
    # Cargamos cada palabra de vocabulario de este tipo
    while True:
      codigo = carga_int1()
      if codigo == 0:  # Fin de este tipo de palabra de vocabulario
        break
      numPalabra = carga_int2() & 2047
      palabra    = palabras[numPalabra & 2047] if numPalabra < len (palabras) else ''
      if not palabra:
        mensajeGUIcomun     = 'Se omite una palabra de vocabulario por tener asociada una palabra %s: ' + str (numPalabra) + '\nTipo de palabra de vocabulario: ' + TIPOS_PAL[t] + '\nC�digo de ' + TIPOS_PAL[t].lower() + ': ' + str (codigo) + '\n' + (('Palabra del mismo tipo anterior: ' + vocabulario[-1][0]) if vocabulario and vocabulario[-1][2] == t else 'Ninguna palabra anterior del mismo tipo')
        mensajeConsolaComun = 'Advertencia: omitida palabra de vocabulario ' + str (codigo) + ' de tipo ' + TIPOS_PAL[t] + ' por tener asociada una palabra %s con c�digo ' + str (numPalabra)
        if numPalabra < len (palabras):
          try:
            muestraFallo ('Palabra de vocabulario vac�a', mensajeGUIcomun % 'vac�a')
          except:
            prn (mensajeConsolaComun % 'vac�a', file = sys.stderr)
        else:
          try:
            muestraFallo ('Palabra inexistente', mensajeGUIcomun % 'inexistente')
          except:
            prn (mensajeConsolaComun % 'inexistente' + ', cuando s�lo hay', len (palabras), 'palabras', file = sys.stderr)
        continue
      vocabulario.append ((palabra, codigo, t))
      completas.add (palabra)
      # Anotamos los prefijos de la palabra
      for p in range (1, len (palabra)):
        prefijo = palabra[:p]
        if prefijo in prefijos:
          prefijos[prefijo][2] += 1
        else:
          prefijos[prefijo] = [codigo, t, 1]
  # A�adimos al vocabulario los prefijos �nicos
  for prefijo in prefijos:
    if prefijo in completas:
      continue
    codigo, tipo, cuenta = prefijos[prefijo]
    if cuenta == 1:
      vocabulario.append ((prefijo, codigo, tipo))

def daCadena (longitud):
  # type: (int) -> str
  """Devuelve la cadena en la posici�n actual del fichero con la longitud dada"""
  cadena = ''
  for l in range (0, longitud, 2):
    par   = carga_int2()
    tipo  = par >> 14
    signo = puntuacion[(par >> 11) & 7]
    if tipo == 3:  # Es un signo de puntuaci�n
      if signo == '\x00':  # Fin de la cadena
        l += 2
        break
      repetir = par & 255  # Cu�ntas veces repetir el signo de puntuaci�n
      cadena += signo * repetir
    else:
      if par & 2047 < len (palabras):
        palabra = palabras[par & 2047]
      else:
        palabra = '!??!'
        try:
          muestraFallo ('Texto incompleto', 'Uno de los textos tiene un n�mero de palabra inexistente: ' + str (par & 2047) + '\nN�mero de palabras: ' + len (palabras) + '\nSe reemplaza por "��?!"')
        except:
          prn ('Advertencia: n�mero de palabra', par & 2047, 'inexistente, s�lo hay', len (palabras), 'palabras. Se reemplaza por "!??!"', file = sys.stderr)
      if tipo == 0:  # Se debe pasar la primera letra a may�sculas
        palabra = palabra[:1].upper() + palabra[1:]
      # Con tipo == 1 se deja la palabra en min�sculas
      elif tipo == 2:  # Se debe pasar la palabra a may�sculas
        palabra = palabra.upper()
      cadena += palabra
      if signo == '\x00':  # Fin de la cadena
        l += 2
        break
      cadena += signo
  if l < longitud:
    fich_ent.seek (longitud - l, 1)  # Saltamos los bytes que haya de m�s
  return cadena

def preparaPlataforma ():
  # type: () -> None
  """Prepara la configuraci�n sobre la plataforma"""
  global carga_desplazamiento, carga_int2, despl_ini, pos_cabecera
  carga_desplazamiento = carga_desplazamiento2
  # Preparamos "endianismo"
  carga_int2 = carga_int2_le
  bajo_nivel_cambia_endian (le = True)
  # Preparamos el desplazamiento inicial para carga desde memoria
  if plataforma in despl_ini_plat:
    despl_ini = despl_ini_plat[plataforma]
    bajo_nivel_cambia_despl (despl_ini)
    pos_cabecera = 25912  # TODO: s�lo servir� para aventuras GAC en formato SNA de Spectrum ZX
