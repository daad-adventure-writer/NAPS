# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de QUILL (versión de Spectrum). Parte común a editor, compilador e intérprete
# Copyright (C) 2010, 2018-2020, 2022, 2024 José Manuel Ferrer Ortiz
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

from bajo_nivel import *
from prn_func   import prn


# Variables que se exportan (fuera del paquete)

# Sólo se usará este módulo de condactos
mods_condactos = ('condactos_quill',)

conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Palabras de los objetos
num_objetos    = [0]  # Número de objetos (en lista para pasar por referencia)
tablas_proceso = []   # Tablas de proceso (la de estado y la de eventos)
vocabulario    = []   # Vocabulario

despl_ini     = 0  # Desplazamiento inicial para cargar desde memoria
max_llevables = 0  # Número máximo de objetos que puede llevar el jugador
pos_msgs_sys  = 0  # Posición de los mensajes de sistema en versiones de Quill sin lista de posiciones para ellos

# Identificadores (para hacer el código más legible) predefinidos
ids_locs = {  0 : 'INICIAL',
                  'INICIAL'    :   0,
            252 : 'NO_CREADOS',
                  'NO_CREADOS' : 252,
            253 : 'PUESTOS',
                  'PUESTOS'    : 253,
            254 : 'LLEVADOS',
                  'LLEVADOS'   : 254}

# Funciones que importan bases de datos desde ficheros
funcs_exportar = ()  # Ninguna, de momento
funcs_importar = (
  ('carga_bd',     ('qql',), 'Bases de datos Quill de Sinclair QL'),
  ('carga_bd_sna', ('sna',), 'Imagen de memoria de ZX 48K con Quill'),
)
# Función que crea una nueva base de datos (vacía)
func_nueva = 'nueva_bd'

# Mensajes de sistema predefinidos
nuevos_sys = (
  'Todo está oscuro. No veo nada.',
  'También veo:-',
  '\nEspero tu orden.',
  '\nEstoy listo para recibir instrucciones.',
  '\nDime qué hago.',
  '\nDame tu orden.',
  'Lo siento, no entiendo eso. Intenta otras palabras.',
  'No puedo ir en esa dirección.',
  'No puedo.',
  'Llevo conmigo:-',
  '(puesto)',
  'Nada de nada.',
  '¿Seguro que quieres salir?',
  '\nFIN DEL JUEGO\n¿Quieres volver a probar?',
  'Adiós. Que tengas un buen día.',
  'De acuerdo.',
  'Pulsa cualquier tecla para continuar',
  'He cogido ',
  ' turno',
  's',
  '.',
  'Has completado el ',
  '%',
  'No lo llevo puesto.',
  'No puedo. Mis manos están llenas.',
  'Ya lo tengo.',
  'No está aquí',
  'No puedo cargar más cosas.',
  'No lo tengo.',
  'Ya lo llevo puesto.',
  'S',
  'N'
)


# Constantes que se exportan (fuera del paquete)

BANDERA_VERBO      = [33]   # Bandera con el verbo de la SL actual
BANDERA_NOMBRE     = [34]   # Bandera con el primer nombre de la SL actual
BANDERA_LLEVABLES  = [35]   # Bandera con el número máximo de objetos llevables
BANDERA_LOC_ACTUAL = [36]   # Bandera con la localidad actual
INDIRECCION      = False    # El parser no soporta indirección (para el IDE)
LONGITUD_PAL     = 4        # Longitud máxima para las palabras de vocabulario
MAX_LOCS         = 252      # Número máximo de localidades posible
MAX_MSGS_USR     = 255      # Número máximo de mensajes de usuario posible
MAX_PROCS        = 2        # Número máximo de tablas de proceso posible
NUM_ATRIBUTOS    = [0]      # Número de atributos de objeto
NUM_BANDERAS     = [37]     # Número de banderas del parser (de usuario y de sistema)
NUM_BANDERAS_ACC = [33]     # Número de banderas del parser accesibles por el programador
NOMBRE_SISTEMA   = 'QUILL'  # Nombre de este sistema
NOMB_COMO_VERB   = [0]      # Número de nombres convertibles a verbo
PREP_COMO_VERB   = 0        # Número de preposiciones convertibles a verbo
# Nombres de las primeras tablas de proceso (para el IDE)
NOMBRES_PROCS    = ('Tabla de eventos', 'Tabla de estado')
TIPOS_PAL        = ('Palabra',)  # Nombres de los tipos de palabra (para el IDE)

conversion = {}  # Tabla de conversión de caracteres


# Diccionarios de condactos

# El formato es el siguiente:
# código : (nombre, parámetros, flujo)
# Donde:
#   parámetros es una cadena con el tipo de cada parámetro
#   flujo indica si el condacto cambia el flujo de ejecución incondicionalmente, por lo que todo código posterior en su entrada será inalcanzable
# Y los tipos de los parámetros se definen así:
# % : Porcentaje (percent), de 1 a 99 (TODO: comprobar si sirven 0 y 100)
# f : Número de bandera (flagno), de 0 a NUM_BANDERAS_ACC - 1
# l : Número de localidad (locno), de 0 a num_localidades - 1
# L : Número de localidad (locno+), de 0 a num_localidades - 1, ó 252-255
# m : Número de mensaje de usuario (mesno), de 0 a num_msgs_usuario - 1
# o : Número de objeto (objno), de 0 a num_objetos - 1
# s : Número de mensaje de sistema (sysno), de 0 a num_msgs_sistema - 1
# u : Valor (value) entero sin signo, de 0 a 255

# Diccionario de condiciones
condiciones = {
   0 : ('AT',      'l'),
   1 : ('NOTAT',   'l'),
   2 : ('ATGT',    'l'),
   3 : ('ATLT',    'l'),
   4 : ('PRESENT', 'o'),
   5 : ('ABSENT',  'o'),
   6 : ('WORN',    'o'),
   7 : ('NOTWORN', 'o'),
   8 : ('CARRIED', 'o'),
   9 : ('NOTCARR', 'o'),
  10 : ('CHANCE',  '%'),
  11 : ('ZERO',    'f'),
  12 : ('NOTZERO', 'f'),
  13 : ('EQ',      'fu'),
  14 : ('GT',      'fu'),
  15 : ('LT',      'fu'),
}

# Diccionarios de acciones

acciones = {
   0 : ('INVEN',   '',   True),
   1 : ('DESC',    '',   True),
   2 : ('QUIT',    '',   False),
   3 : ('END',     '',   True),
   4 : ('DONE',    '',   True),
   5 : ('OK',      '',   True),
   6 : ('ANYKEY',  '',   False),
   7 : ('SAVE',    '',   True),
   8 : ('LOAD',    '',   True),
   9 : ('TURNS',   '',   False),
  10 : ('SCORE',   '',   False),
  11 : ('PAUSE',   'u',  False),
  12 : ('GOTO',    'l',  False),
  13 : ('MESSAGE', 'm',  False),
  14 : ('REMOVE',  'o',  False),
  15 : ('GET',     'o',  False),
  16 : ('DROP',    'o',  False),
  17 : ('WEAR',    'o',  False),
  18 : ('DESTROY', 'o',  False),
  19 : ('CREATE',  'o',  False),
  20 : ('SWAP',    'oo', False),
  21 : ('SET',     'f',  False),
  22 : ('CLEAR',   'f',  False),
  23 : ('PLUS',    'fu', False),
  24 : ('MINUS',   'fu', False),
  25 : ('LET',     'fu', False),
  26 : ('BEEP',    'uu', False),
  27 : ('DESTROY', 'o',  False),
  28 : ('CREATE',  'o',  False),
  29 : ('SWAP',    'oo', False),
  30 : ('PLACE',   'oL', False),
  31 : ('SET',     'f',  False),
  32 : ('CLEAR',   'f',  False),
  33 : ('PLUS',    'fu', False),
  34 : ('MINUS',   'fu', False),
  35 : ('LET',     'fu', False),
  36 : ('BEEP',    'uu', False),
  37 : ('RAMSAVE', '',   False),
  38 : ('RAMLOAD', '',   False),
  39 : ('SYSMESS', 's',  False),
}

# Reemplazo de acciones en nuevas versiones de Quill
acciones_nuevas = {
  11 : ('CLS',     '',  False),
  12 : ('DROPALL', '',  False),
  13 : ('AUTOG',   '',  False),
  14 : ('AUTOD',   '',  False),
  15 : ('AUTOW',   '',  False),
  16 : ('AUTOR',   '',  False),
  17 : ('PAUSE',   'u', False),
  18 : ('PAPER',   'u', False),
  19 : ('INK',     'u', False),
  20 : ('BORDER',  'u', False),
  21 : ('GOTO',    'l', False),
  22 : ('MESSAGE', 'm', False),
  23 : ('REMOVE',  'o', False),
  24 : ('GET',     'o', False),
  25 : ('DROP',    'o', False),
  26 : ('WEAR',    'o', False),
}

acciones_flujo = []  # Acciones que cambian el flujo de ejecución incondicionalmente
condactos      = {}  # Diccionario de condactos
for codigo in condiciones:
  condactos[codigo] = condiciones[codigo] + (False, False)
for codigo in acciones:
  condactos[100 + codigo] = acciones[codigo][:2] + (True, acciones[codigo][2])


# Funciones que utiliza el IDE o el intérprete directamente

def cadena_es_mayor (cadena1, cadena2):
  """Devuelve si la cadena1 es mayor a la cadena2 en el juego de caracteres de este sistema"""
  return cadena1 > cadena2

def carga_bd (fichero, longitud):
  """Carga la base de datos entera desde el fichero de entrada, en formato de Sinclair QL

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, plataforma
  carga_desplazamiento  = carga_desplazamiento4  # Así es en las bases de datos de Quill para QL
  fin_cadena            = 0                      # Así es en las bases de datos de Quill para QL
  nueva_linea           = 254                    # Así es en las bases de datos de Quill para QL
  plataforma            = 1                      # Apaño para que el intérprete lo considere como Spectrum
  BANDERA_VERBO[0]      = 64
  BANDERA_NOMBRE[0]     = 65
  BANDERA_LLEVABLES[0]  = 66
  BANDERA_LOC_ACTUAL[0] = 67
  NUM_BANDERAS[0]       = 68
  NUM_BANDERAS_ACC[0]   = 64
  fichero.seek (0)
  if fichero.read (18) == b']!QDOS File Header':  # Tiene cabecera QDOS puesta por el emulador
    despl_ini = -30  # Parece ser de 30 bytes en sQLux
  else:
    despl_ini = 0  # En QL, los desplazamientos son directamente las posiciones en la BD
  bajo_nivel_cambia_endian (le = False)  # Los desplazamientos en las bases de datos de QL son big endian
  bajo_nivel_cambia_despl  (despl_ini)
  preparaPosCabecera ('qql', -despl_ini + 6)
  acciones.update (acciones_nuevas)
  for codigo in acciones_nuevas:
    condactos[100 + codigo] = acciones_nuevas[codigo][:2] + (True, acciones_nuevas[codigo][2])
  return cargaBD (fichero, longitud)

def carga_bd_sna (fichero, longitud):
  """Carga la base de datos entera desde un fichero de imagen de memoria de Spectrum 48K

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, pos_msgs_sys
  carga_desplazamiento = carga_desplazamiento2
  # if longitud not in (49179, 131103):  # Tamaño de 48K y de 128K
  if longitud != 49179:
    return False  # No parece un fichero de imagen de memoria de Spectrum 48K
  # Detectamos la posición de la cabecera de la base de datos
  bajo_nivel_cambia_ent (fichero)
  posicion = busca_secuencia ((16, None, 17, None, 18, None, 19, None, 20, None, 21))
  if posicion == None:
    return False  # Cabecera de la base de datos no encontrada
  despl_ini = 16357  # Al menos es así en Hampstead y Manor of Madness, igual que PAWS
  bajo_nivel_cambia_endian (le = True)  # Al menos es así en ZX Spectrum
  bajo_nivel_cambia_despl  (despl_ini)
  fin_cadena  = 31  # Igual que PAWS
  nueva_linea = 6
  posBD = posicion + 3
  # Detectamos si es una versión vieja de Quill, sin lista de posiciones de mensajes de sistema
  if busca_secuencia ((0xdd, 0xbe, 0, 0x28, None, 0xdd, 0xbe, 3, 0x28, None, 0xdd, 0x35, 3, 0x3a, None, None, 0xdd, 0xbe, None, 0x28, None, 0xfe, 0xfd, 0x30, None, 0x21)):
    pos_msgs_sys = carga_int2_le()
    if pos_msgs_sys:
      formato = 'sna48k_old'
      # TODO: cargar UDGs presentes en este formato, añadiéndolos a la fuente tipográfica
    else:
      formato = 'sna48k'  # No se ha encontrado, por lo que asumimos que no es una versión de Quill vieja
  preparaPosCabecera (formato, posBD)
  if formato == 'sna48k':
    acciones.update (acciones_nuevas)
    for codigo in acciones_nuevas:
      condactos[100 + codigo] = acciones_nuevas[codigo][:2] + (True, acciones_nuevas[codigo][2])
  return cargaBD (fichero, longitud)

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de Quill"""
  # Banderas de sistema, no accesibles directamente, en posición estándar de PAWS
  banderas[BANDERA_LLEVABLES[0]] = max_llevables

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representación de secuencias de control en sus códigos"""
  convertida = ''
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if c == '\t':
      convertida += '\x06'  # Tabulador
    else:
      convertida += c
    i += 1
  # TODO: interpretar las secuencias escapadas con barra invertida (\)
  return convertida

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representación imprimible"""
  convertida = ''
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if c == '\n':
      convertida += '\\n'
    elif c == '\x06':  # Tabulador
      convertida += '\\t'
    elif o in range (16, 21) and (i + 1) < len (cadena):
      convertida += '\\'
      if o == 16:
        convertida += 'TINTA'
      elif o == 17:
        convertida += 'PAPEL'
      elif o == 18:
        convertida += 'FLASH'
      elif o == 19:
        convertida += 'BRILLO'
      else:  # o == 20
        convertida += 'INVERSA'
      convertida += '_%02X' % ord (cadena[i + 1])
      i += 1  # El siguiente carácter ya se ha procesado
    elif c == '\\':
      convertida += '\\\\'
    else:
      convertida += c
    i += 1
  return convertida

def nueva_bd ():
  """Crea una nueva base de datos de The Quill (versión de Spectrum)"""
  # Creamos la localidad 0
  desc_locs.append  ('Descripción de la localidad 0, la inicial.')
  conexiones.append ([])  # Ninguna conexión en esta localidad
  # Creamos una palabra para el objeto 0
  vocabulario.append(('luz', 13, 0))  # 0 es el tipo de palabra
  # Creamos el objeto 0
  desc_objs.append      ('Descripción del objeto 0, emisor de luz.')
  locs_iniciales.append (ids_locs['NO_CREADOS'])
  nombres_objs.append   (13)
  num_objetos[0] = 1
  # Creamos el mensaje de usuario 0
  msgs_usr.append ('Texto del mensaje 0.')
  # Ponemos los mensajes de sistema predefinidos
  for mensaje in nuevos_sys:
    msgs_sys.append (mensaje)
  # Creamos la tabla de estado y la de eventos
  tablas_proceso.append (([[], []]))
  tablas_proceso.append (([[], []]))


# Funciones auxiliares que sólo se usan en este módulo

def cargaBD (fichero, longitud):
  """Carga la base de datos entera desde el fichero de entrada

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global fich_ent, max_llevables
  fich_ent = fichero
  bajo_nivel_cambia_ent (fichero)
  try:
    cargaCadenas (CAB_NUM_LOCS,     CAB_POS_LST_POS_LOCS,     desc_locs)
    cargaCadenas (CAB_NUM_OBJS,     CAB_POS_LST_POS_OBJS,     desc_objs)
    cargaCadenas (CAB_NUM_MSGS_USR, CAB_POS_LST_POS_MSGS_USR, msgs_usr)
    if pos_msgs_sys:
      cargaMensajesSistema()
    else:
      cargaCadenas (CAB_NUM_MSGS_SYS, CAB_POS_LST_POS_MSGS_SYS, msgs_sys)
    cargaConexiones()
    cargaLocalidadesObjetos()
    cargaVocabulario()
    cargaNombresObjetos()
    cargaTablasProcesos()
    max_llevables = carga_int1 (CAB_MAX_LLEVABLES)
  except:
    return False

def cargaCadenas (posNumCads, posListaPos, cadenas):
  """Carga un conjunto genérico de cadenas

posNumCads es la posición de donde obtener el número de cadenas
posListaPos posición de donde obtener la lista de posiciones de las cadenas
cadenas es la lista donde almacenar las cadenas que se carguen"""
  # Cargamos el número de cadenas
  numCads = carga_int1 (posNumCads)
  # Vamos a la posición de la lista de posiciones de cadenas
  fich_ent.seek (carga_desplazamiento (posListaPos))
  # Cargamos las posiciones de las cadenas
  posiciones = []
  for i in range (numCads):
    posiciones.append (carga_desplazamiento())
  # Cargamos cada cadena
  saltaSiguiente = False  # Si salta el siguiente carácter, como ocurre tras algunos códigos de control
  for posicion in posiciones:
    fich_ent.seek (posicion)
    algo   = False  # Si hay algo imprimible en la línea
    cadena = []
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if saltaSiguiente or (caracter in (range (16, 21))):  # Códigos de control
        cadena.append (chr (caracter))
        saltaSiguiente = not saltaSiguiente
      elif caracter == nueva_linea:  # Un carácter de nueva línea en la cadena
        if algo:
          cadena.append ('\n')
        algo = not algo
      else:
        algo = True
        cadena.append (chr (caracter))
    cadenas.append (''.join (cadena))

def cargaConexiones ():
  """Carga las conexiones"""
  # Cargamos el número de localidades
  num_locs = carga_int1 (CAB_NUM_LOCS)
  # Vamos a la posición de la lista de posiciones de las conexiones
  fich_ent.seek (carga_desplazamiento (CAB_POS_LST_POS_CNXS))
  # Cargamos las posiciones de las conexiones de cada localidad
  posiciones = []
  for i in range (num_locs):
    posiciones.append (carga_desplazamiento())
  # Cargamos las conexiones de cada localidad
  for posicion in posiciones:
    fich_ent.seek (posicion)
    salidas = []
    while True:
      verbo = carga_int1()  # Verbo de dirección
      if verbo == 255:  # Fin de las conexiones de esta localidad
        break
      destino = carga_int1()  # Localidad de destino
      salidas.append ((verbo, destino))
    conexiones.append (salidas)

def cargaLocalidadesObjetos ():
  """Carga las localidades iniciales de los objetos (dónde está cada uno)"""
  # Cargamos el número de objetos (no lo tenemos todavía)
  num_objetos[0] = carga_int1 (CAB_NUM_OBJS)
  # Vamos a la posición de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def cargaNombresObjetos ():
  """Carga los nombres y adjetivos de los objetos"""
  # Vamos a la posición de los nombres de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_NOMS_OBJS))
  # Cargamos el nombre de cada objeto
  for i in range (num_objetos[0]):
    nombres_objs.append ((carga_int1(), 255))

def cargaMensajesSistema ():
  """Carga los mensajes de sistema desde la posición del primero (en pos_msgs_sys). Usar solamente con versiones de Quill viejas, sin lista de posiciones para los mensajes de sistema"""
  fich_ent.seek (pos_msgs_sys - despl_ini)  # Nos movemos a la posición del primer mensaje de sistema
  saltaSiguiente = False  # Si salta el siguiente carácter, como ocurre tras algunos códigos de control
  while True:
    algo   = False  # Si hay algo imprimible en la línea
    cadena = ''
    ceros  = 0  # Cuenta del número de ceros consecutivos al inicio de la cadena
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if saltaSiguiente or (caracter in (range (16, 21))):  # Códigos de control
        cadena += chr (caracter)
        saltaSiguiente = not saltaSiguiente
        continue
      if caracter == 255 and not cadena:
        ceros += 1
        if ceros > 20:  # Consideramos esto como marca de fin de mensajes de sistema
          return
      elif caracter == nueva_linea:  # Un carácter de nueva línea en la cadena
        if algo:
          cadena += '\n'
        algo = not algo
      else:
        algo    = True
        cadena += chr (caracter)
    msgs_sys.append (cadena)

def cargaTablasProcesos ():
  """Carga las dos tablas de procesos: la de estado y la de eventos"""
  # Cargamos cada tabla de procesos
  posiciones = (carga_desplazamiento (CAB_POS_EVENTOS), carga_desplazamiento (CAB_POS_ESTADO))
  for numProceso in range (2):
    posicion = posiciones[numProceso]
    fich_ent.seek (posicion)
    cabeceras   = []
    posEntradas = []
    while True:
      verbo = carga_int1()
      if verbo == 0:  # Fin de este proceso
        break
      cabeceras.append ((verbo, carga_int1()))
      posEntradas.append (carga_desplazamiento())
    entradas = []
    for numEntrada in range (len (posEntradas)):
      posEntrada = posEntradas[numEntrada]
      fich_ent.seek (posEntrada)
      entrada = []
      for listaCondactos in (condiciones, acciones):
        while True:
          numCondacto = carga_int1()
          if numCondacto == 255:  # Fin de esta entrada
            break
          if numCondacto not in listaCondactos:
            prn ('FIXME: Número de', 'condición' if listaCondactos == condiciones else 'acción', numCondacto, 'desconocida, en entrada', numEntrada, 'de la tabla de', 'estado' if numProceso else 'eventos')
          parametros = []
          for i in range (len (listaCondactos[numCondacto][1])):
            parametros.append (carga_int1())
          if listaCondactos == acciones:
            entrada.append ((numCondacto + 100, parametros))
          else:
            entrada.append ((numCondacto, parametros))
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: Número distinto de cabeceras y entradas para una tabla de',
           'procesos')
      return
    tablas_proceso.append ((cabeceras, entradas))

def cargaVocabulario ():
  """Carga el vocabulario"""
  # Vamos a la posición del vocabulario
  fich_ent.seek (carga_desplazamiento (CAB_POS_VOCAB))
  # Cargamos cada palabra de vocabulario
  while True:
    caracter = carga_int1()
    if caracter == 0:  # Fin del vocabulario
      return
    caracter ^= 255
    palabra   = [chr (caracter)]
    for i in range (3):
      caracter = carga_int1() ^ 255
      palabra.append (chr (caracter))
    # Quill guarda las palabras de menos de cuatro letras con espacios al final
    # Quill guarda las palabras en mayúsculas
    vocabulario.append ((''.join (palabra).rstrip().lower(), carga_int1(), 0))

def preparaPosCabecera (formato, inicio):
  """Asigna las "constantes" de desplazamientos (offsets/posiciones) en la cabecera"""
  global CAB_MAX_LLEVABLES, CAB_NUM_OBJS, CAB_NUM_LOCS, CAB_NUM_MSGS_USR, CAB_NUM_MSGS_SYS, CAB_POS_EVENTOS, CAB_POS_ESTADO, CAB_POS_LST_POS_OBJS, CAB_POS_LST_POS_LOCS, CAB_POS_LST_POS_MSGS_USR, CAB_POS_LST_POS_MSGS_SYS, CAB_POS_LST_POS_CNXS, CAB_POS_VOCAB, CAB_POS_LOCS_OBJS, CAB_POS_NOMS_OBJS
  CAB_MAX_LLEVABLES = inicio + 0   # Número máximo de objetos llevables
  CAB_NUM_OBJS      = inicio + 1   # Número de objetos
  CAB_NUM_LOCS      = inicio + 2   # Número de localidades
  CAB_NUM_MSGS_USR  = inicio + 3   # Número de mensajes de usuario
  if formato == 'qql':  # Base de datos para Sinclair QL
    CAB_NUM_MSGS_SYS         = inicio + 4   # Número de mensajes de sistema
    CAB_POS_EVENTOS          = inicio + 6   # Posición de la tabla de eventos
    CAB_POS_ESTADO           = inicio + 10  # Posición de la tabla de estado
    CAB_POS_LST_POS_OBJS     = inicio + 14  # Posición lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = inicio + 18  # Posición lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = inicio + 22  # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = inicio + 26  # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = inicio + 30  # Posición lista de posiciones de conexiones
    CAB_POS_VOCAB            = inicio + 34  # Posición del vocabulario
    CAB_POS_LOCS_OBJS        = inicio + 38  # Posición de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = inicio + 42  # Posición de los nombres de los objetos
  elif formato == 'sna48k':
    CAB_NUM_MSGS_SYS         = inicio + 4   # Número de mensajes de sistema
    CAB_POS_EVENTOS          = inicio + 5   # Posición de la tabla de eventos
    CAB_POS_ESTADO           = inicio + 7   # Posición de la tabla de estado
    CAB_POS_LST_POS_OBJS     = inicio + 9   # Posición lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = inicio + 11  # Posición lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = inicio + 13  # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_MSGS_SYS = inicio + 15  # Pos. lista de posiciones de mensajes de sistema
    CAB_POS_LST_POS_CNXS     = inicio + 17  # Posición lista de posiciones de conexiones
    CAB_POS_VOCAB            = inicio + 19  # Posición del vocabulario
    CAB_POS_LOCS_OBJS        = inicio + 21  # Posición de localidades iniciales de objetos
    CAB_POS_NOMS_OBJS        = inicio + 23  # Posición de los nombres de los objetos
  elif formato == 'sna48k_old':
    CAB_POS_EVENTOS          = inicio + 4   # Posición de la tabla de eventos
    CAB_POS_ESTADO           = inicio + 6   # Posición de la tabla de estado
    CAB_POS_LST_POS_OBJS     = inicio + 8   # Posición lista de posiciones de objetos
    CAB_POS_LST_POS_LOCS     = inicio + 10  # Posición lista de posiciones de localidades
    CAB_POS_LST_POS_MSGS_USR = inicio + 12  # Pos. lista de posiciones de mensajes de usuario
    CAB_POS_LST_POS_CNXS     = inicio + 14  # Posición lista de posiciones de conexiones
    CAB_POS_VOCAB            = inicio + 16  # Posición del vocabulario
    CAB_POS_LOCS_OBJS        = inicio + 18  # Posición de localidades iniciales de objetos
