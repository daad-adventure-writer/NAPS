# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Librería de QUILL (versión de Spectrum). Parte común a editor, compilador e intérprete
# Copyright (C) 2010, 2018-2020, 2022, 2024-2025 José Manuel Ferrer Ortiz
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

import sys  # Para stderr

import alto_nivel

from bajo_nivel import *
from prn_func   import _, maketrans, prn


# Variables que se exportan (fuera del paquete)

# Sólo se usará este módulo de condactos
mods_condactos = ('condactos_quill',)

adaptados      = {}   # Condactos que se han adaptado al convertir de una plataforma a otra (para el IDE)
colores_inicio = []   # Colores iniciales: tinta, papel, borde y opcionalmente: brillo, otros según plataforma
conexiones     = []   # Listas de conexiones de cada localidad
desc_locs      = []   # Descripciones de las localidades
desc_objs      = []   # Descripciones de los objetos
dlg_progreso   = []   # Diálogo de progreso al exportar (para el IDE)
locs_iniciales = []   # Localidades iniciales de los objetos
msgs_sys       = []   # Mensajes de sistema
msgs_usr       = []   # Mensajes de usuario
nombres_objs   = []   # Palabras de los objetos
num_objetos    = [0]  # Número de objetos (en lista para pasar por referencia)
tablas_proceso = []   # Tablas de proceso (la de estado y la de eventos)
udgs           = []   # UDGs (caracteres gráficos definidos por el usuario)
vocabulario    = []   # Vocabulario

despl_ini       = 0           # Desplazamiento inicial para cargar desde memoria
fin_cadena      = 0           # Código del carácter de fin de cadena
max_llevables   = 0           # Número máximo de objetos que puede llevar el jugador
nada_tras_flujo = []          # Si omitiremos los condactos que haya después de los de cambio de flujo incondicional
nueva_linea     = ord ('\n')  # Código del carácter de nueva línea
pos_msgs_sys    = 0           # Posición de los mensajes de sistema en versiones de Quill sin lista de posiciones para ellos

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
funcs_exportar = (
  ('guarda_bd',      ('dtb',), _('Optimized Quill database for Atari 800')),
  ('guarda_bd',      ('prg',), _('Optimized Quill database for Commodore 64')),
  ('guarda_bd',      ('qql',), _('Optimized Quill database for Sinclair QL')),
  ('guarda_bd_a800', ('dtb',), _('Quill database for Atari 800')),
  ('guarda_bd_c64',  ('prg',), _('Quill database for Commodore 64')),
  ('guarda_bd_ql',   ('qql',), _('Quill database for Sinclair QL')),
  ('guarda_codigo_fuente', ('qse', 'sce',), _('Quill source code')),
)
funcs_importar = (
  ('carga_bd_cpc',  ('bin',),        _('Quill databases for Amstrad CPC')),
  ('carga_bd_a800', ('dtb', 'prg'),  _('Quill databases for Atari 800 AdventureWriter')),
  ('carga_bd_c64',  ('prg',),        _('Quill databases for Commodore 64')),
  ('carga_bd_pc',   ('dat', 'exe'),  _('Quill databases for PC AdventureWriter')),
  ('carga_bd_ql',   ('qql',),        _('Quill databases for Sinclair QL')),
  ('carga_bd_sna',  ('sna',),        _('ZX 48K memory snapshots with Quill')),
  ('carga_sce',     ('qse', 'sce',), _('Quill source code')),
)
# Función que crea una nueva base de datos (vacía)
func_nueva = 'nueva_bd'

# Mensajes de sistema predefinidos
nuevos_sys = (
  _("Everything is dark. I can't see."),
  _('I also see:-'),
  _("\nI'm waiting for your command."),
  _("\nI'm ready for a new command."),
  _('\nTell me what to do.'),
  _('\nGive me your instruction.'),
  _("Sorry, I don't understand.\nTry with other words."),
  _("I can't go that way."),
  _("I can't do that."),
  _('I have:-'),
  _('(worn)'),
  _('Nothing at all.'),
  _('Are you sure you want to quit?'),
  _('\nGAME OVER\nDo you want another try?'),
  _('Goodbye. Have a nice day.'),
  _('Alright.'),
  _('Press any key to continue'),
  _("You took "),
  _(' turn'),
  _('s'),
  _('.'),
  _('You completed '),
  _('%'),
  _("I'm not wearing that."),
  _("I can't. My hands are full."),
  _('I already have that.'),
  _("That's not here."),
  _("I can't carry more things."),
  _("I don't have that."),
  _("It's already worn."),
  _('Y'),
  _('N'),
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
NOMBRES_PROCS    = (_('Event table'), _('Status table'))
# Nombres de los tipos de palabra (para el IDE y el intérprete)
TIPOS_PAL        = (_('Word'),)
TIPOS_PAL_ES     = ('Palabra',)

cods_tinta    = {}  # Caracteres que si se encuentran en una cadena, cambiará el color de tinta por el del valor
conversion    = {}  # Tabla de conversión de caracteres
id_plataforma = ''  # Identificador de plataforma como cadena


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

acciones_comun = {
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

# Reemplazo de acciones en Commodore 64, y en AdventureWriter para Atari 800 y PC
acciones_c64pc = {
  11 : ('CLS',     '',   False),
  12 : ('DROPALL', '',   False),
  13 : ('PAUSE',   'u',  False),
  14 : ('PAPER',   'u',  False),  # Llamada SCREEN en AdventureWriter para Atari 800 y PC
  15 : ('INK',     'u',  False),  # Llamada TEXT   en AdventureWriter para Atari 800 y PC
  16 : ('BORDER',  'u',  False),
  17 : ('GOTO',    'l',  False),
  18 : ('MESSAGE', 'm',  False),
  19 : ('REMOVE',  'o',  False),
  20 : ('GET',     'o',  False),
  21 : ('DROP',    'o',  False),
  22 : ('WEAR',    'o',  False),
  23 : ('DESTROY', 'o',  False),
  24 : ('CREATE',  'o',  False),
  25 : ('SWAP',    'oo', False),
  26 : ('PLACE',   'oL', False),
  27 : ('SET',     'f',  False),
  28 : ('CLEAR',   'f',  False),
  29 : ('PLUS',    'fu', False),
  30 : ('MINUS',   'fu', False),
  31 : ('LET',     'fu', False),
  32 : ('BEEP',    'uu', False),  # Llamada SID en Commodore 64, y SOUND en AdventureWriter para PC
}

# Reemplazo de acciones en Amstrad CPC
acciones_cpc = dict (acciones_nuevas)
acciones_cpc.update ({
  19 : ('INK', 'uu', False),
})
#del acciones_cpc[18]  # TODO: investigar. Es PAPER, en teoría inexistente en Amstrad CPC

# Reemplazo de acciones en Atari 800
acciones_a800 = dict (acciones_c64pc)
acciones_a800.update ({
  32 : ('SOUND', 'uuuu', False),
})

# Reemplazo de acciones en Sinclair QL
acciones_ql = dict (acciones_nuevas)
acciones_ql.update ({
  37 : ('RAMSAVE', '',   False),
  38 : ('RAMLOAD', '',   False),
  39 : ('SYSMESS', 's',  False),
})

# Diccionarios de actualización de acciones para cada plataforma
acciones_plataforma = {
  'Atari800': acciones_a800,
  'C64':      acciones_c64pc,
  'CPC':      acciones_cpc,
  'PC':       acciones_c64pc,
  'QL':       acciones_ql,
  'ZX':       acciones_nuevas,
}

acciones  = dict (acciones_comun)
condactos = {}  # Diccionario de condactos
for codigo in condiciones:
  condiciones[codigo] = condiciones[codigo] + (False, )  # Marcamos así que las condiciones no cambian el flujo incondicionalmente
  condactos[codigo]   = condiciones[codigo] + (False, )  # Marcamos que las condiciones no son acciones
for codigo in acciones:
  condactos[100 + codigo] = acciones[codigo][:2] + (True, acciones[codigo][2])


# Variables que sólo se usan en este módulo

petscii = ''.join (('%c' % c for c in range (65))) + 'abcdefghijklmnopqrstuvwxyz' + ''.join (('%c' % c for c in range (91, 96))) + '\xc0ABCDEFGHIJKLMNOPQRSTUVWXYZ' + ''.join (('%c' % c for c in tuple (range (219, 224)) + tuple (range (128, 193)))) + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + ''.join (('%c' % c for c in tuple (range (219, 224)) + tuple (range (160, 192))))
petscii_a_ascii = maketrans (''.join (('%c' % c for c in range (256))), petscii)
ascii_para_petscii = ''.join (('%c' % c for c in tuple (range (65)) + tuple (range (193, 219)) + tuple (range (91, 97)))) + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + ''.join (('%c' % c for c in range (123, 256)))
ascii_a_petscii = maketrans (''.join (('%c' % c for c in range (256))), ascii_para_petscii)

conversion_inv        = {}  # Tabla de conversión de caracteres invertida
conversion_plataforma = {
  'Atari800': {'\x00': u'\u2665', '\x01': u'\u2523\u251c', '\x02': u'\u2595', '\x03': u'\u251b\u2518', '\x04': u'\u252b\u2524', '\x05': u'\u2513\u2510', '\x06': u'\u2571', '\x07': u'\u2572', '\x08': u'\u25e2', '\x09': u'\u2597', '\x0a': u'\u25e3', '\x0b': u'\u259d', '\x0c': u'\u2598', '\x0d': u'\u2594', '\x0e': u'\u2581', '\x0f': u'\u2596', '\x10': u'\u2663', '\x11': u'\u250f\u250c', '\x12': u'\u2501\u2500', '\x13': u'\u254b\u253c', '\x14': u'\u2022', '\x15': u'\u2584', '\x16': u'\u258e\u258f', '\x17': u'\u2533\u252c', '\x18': u'\u253b\u2534', '\x19': u'\u258c', '\x1a': u'\u2517\u2514', '\x1c': u'\u2191', '\x1d': u'\u2193', '\x1e': u'\u2190', '\x1f': u'\u2192', '`': u'\u2666\u25c6', '{': u'\u2660', '|': u'\u2503|\u2502', '}': u'\u2196', '~': u'\u25c0', '\x7f': u'\u25b6'},
  'QL': {'`': '£', '\x81': 'ã', '\x82': 'å', '\x83': 'é', '\x84': 'ö', '\x85': 'õ', '\x86': 'ø', '\x87': 'ü', '\x88': 'ç', '\x89': 'ñ', '\x8a': 'æ', '\x8b': 'œ', '\x8c': 'á', '\x8d': 'à', '\x8e': 'â', '\x8f': 'ë', '\x90': 'è', '\x91': 'ê', '\x92': 'ï', '\x93': 'í', '\x94': 'ì', '\x95': 'î', '\x96': 'ó', '\x97': 'ò', '\x98': 'ô', '\x99': 'ú', '\x9a': 'ù', '\x9b': 'û', '\x9c': 'ß', '\x9d': '¢', '\x9e': '¥', '\x9f': '`', '\xa0': 'Ä', '¡': 'Ã', '¢': 'Â', '£': 'É', '\xa4': 'Ö', '¥': 'Õ', '§': 'Ü', '\xa8': 'Ç', '©': 'Ñ', 'ª': 'Æ', '«': 'Œ', '¬': u'\u03b1', '\xad': u'\u03b4', '®': u'\u0398', '¯': u'\u03bb', '°': 'µ', '±': u'\u03c0', '²': u'\u03a6', '³': '¡', '\xb4': '¿', 'µ': u'\u1e62', '¶': '§', '·': u'\u00a4', '\xb8': '«', '¹': '»', '»': '÷', '\xbc': u'\u2190', '\xbd': u'\u2192', '\xbe': u'\u2191', '¿': u'\u2193'},
  'ZX': {'\x7f': '©', '\x81': u'\u259d', '\x82': u'\u2598', '\x83': u'\u2580', '\x84': u'\u2597', '\x85': u'\u2590', '\x86': u'\u259a', '\x87': u'\u259c', '\x88': u'\u2596', '\x89': u'\u259e', '\x8a': u'\u258c', '\x8b': u'\u259b', '\x8c': u'\u2584', '\x8d': u'\u259f', '\x8e': u'\u2599', '\x8f': u'\u2588'},
}

# Nombre completo de cada plataforma por su identificador en id_plataforma
plataformas = {
  'Atari800': 'Atari 800',
  'C64':      'Commodore 64',
  'CPC':      'Amstrad CPC',
  'PC':       'IBM PC',
  'QL':       'Sinclair QL',
}


# Funciones que utiliza el IDE o el intérprete directamente

def cadena_es_mayor (cadena1, cadena2):
  """Devuelve si la cadena1 es mayor a la cadena2 en el juego de caracteres de este sistema"""
  return cadena1 > cadena2

def carga_bd_a800 (fichero, longitud):
  """Carga la base de datos entera desde una base de datos de AdventureWriter para Atari 800

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, plataforma, id_plataforma
  carga_desplazamiento = carga_desplazamiento2
  bajo_nivel_cambia_endian (le = True)
  bajo_nivel_cambia_ent    (fichero)
  fichero.seek (0)
  if carga_int2_le() != 65535:  # Los ficheros de aventura y base de datos de Atari 800 comienzan así
    return False
  despl_ini     = carga_int2_le() - 6
  fin_cadena    = 0
  inicio        = 0
  nueva_linea   = 155  # Es este, aunque el editor parece no dejar escribir nueva línea
  plataforma    = 1    # Apaño para que el intérprete lo considere como Spectrum
  id_plataforma = 'Atari800'
  cods_tinta.clear()
  bajo_nivel_cambia_despl (despl_ini)
  # TODO: cargar y usar colores iniciales, que son muy distintos en esta plataforma, con 256 colores posibles
  colores_inicio.extend ((7, 0, 0, 0))  # Tinta blanca, papel y borde negro, y sin brillo
  preparaPosCabecera ('a800', inicio + 10)
  return cargaBD (fichero, longitud)

def carga_bd_c64 (fichero, longitud):
  """Carga la base de datos entera desde una base de datos de Quill para Commodore 64

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, plataforma, id_plataforma
  carga_desplazamiento = carga_desplazamiento2
  bajo_nivel_cambia_endian (le = True)
  bajo_nivel_cambia_ent    (fichero)
  fichero.seek (0)
  despl_ini     = carga_int2_le() - 2
  fin_cadena    = 0
  nueva_linea   = 141  # El 13 también podría ser, pero tal vez no se use
  plataforma    = 1    # Apaño para que el intérprete lo considere como Spectrum
  id_plataforma = 'C64'
  cods_tinta.clear()
  cods_tinta.update ({5: 1, 25: 2, 30: 5, 31: 6, 129: 8, 144: 0, 149: 9, 150: 10, 151: 11, 152: 12, 153: 13, 154: 14, 155: 15, 156: 4, 158: 7, 159: 3})
  bajo_nivel_cambia_despl (despl_ini)
  # Cargamos los colores iniciales
  fichero.seek (3)
  colores_inicio.append (carga_int1())  # Color de tinta
  colores_inicio.append (carga_int1())  # Color de papel
  colores_inicio.append (carga_int1())  # Color de borde
  preparaPosCabecera ('c64', 6)
  return cargaBD (fichero, longitud)

# TODO: soporte de aventuras de Amstrad CPC
def carga_bd_cpc (fichero, longitud):
  """Carga la base de datos entera desde una base de datos de Quill para Amstrad CPC

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, plataforma, id_plataforma
  carga_desplazamiento = carga_desplazamiento2
  despl_ini     = 6987
  fin_cadena    = 0
  nueva_linea   = 20
  plataforma    = 1   # Apaño para que el intérprete lo considere como Spectrum
  id_plataforma = 'CPC'
  bajo_nivel_cambia_endian (le = True)
  bajo_nivel_cambia_ent    (fichero)
  bajo_nivel_cambia_despl  (despl_ini)
  inicio = 128
  # Cargamos los colores iniciales
  fichero.seek (inicio + 1)
  colores_inicio.append (carga_int1())     # Color de papel (tinta 0)
  colores_inicio.insert (0, carga_int1())  # Color de tinta (tinta 1)
  colores_inicio.append (carga_int1())     # Color de tinta 2
  colores_inicio.append (carga_int1())     # Color de tinta 3
  colores_inicio.insert (2, carga_int1())  # Color de borde
  colores_inicio.insert (3, 0)             # Sin brillo
  preparaPosCabecera ('cpc', inicio + 6)
  return cargaBD (fichero, longitud)

def carga_bd_pc (fichero, longitud):
  """Carga la base de datos entera desde una base de datos de AdventureWriter para IBM PC

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, plataforma, id_plataforma
  carga_desplazamiento = carga_desplazamiento2
  extension     = os.path.splitext (fichero.name)[1][1:].lower()
  despl_ini     = 6242 if extension == 'dat' else -4912
  fin_cadena    = 0
  inicio        = 0
  nueva_linea   = ord ('\r')  # Es este, aunque el editor parece no dejar escribir nueva línea
  plataforma    = 0
  id_plataforma = 'PC'
  bajo_nivel_cambia_endian (le = True)
  bajo_nivel_cambia_ent    (fichero)
  bajo_nivel_cambia_despl  (despl_ini)
  # Detectamos la posición de la cabecera de la base de datos
  secuencia = os.path.basename (os.path.splitext (fichero.name)[0]).upper().ljust (8) + 'EXE'
  secuencia = [ord (c) for c in secuencia]
  posicion  = busca_secuencia (secuencia)
  if posicion == None:
    return False  # Cabecera de la base de datos no encontrada
  inicio = posicion + 34
  # Cargamos los colores iniciales
  fichero.seek (inicio + 3)
  colores_inicio.append (carga_int1())  # Color de tinta
  colores_inicio.append (carga_int1())  # Color de papel
  colores_inicio.append (carga_int1())  # Color de borde
  preparaPosCabecera ('pc', inicio + 6)
  return cargaBD (fichero, longitud)

def carga_bd_ql (fichero, longitud):
  """Carga la base de datos entera desde el fichero de entrada, en formato de Sinclair QL

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, plataforma, id_plataforma
  carga_desplazamiento  = carga_desplazamiento4  # Así es en las bases de datos de Quill para QL
  fin_cadena            = 0                      # Así es en las bases de datos de Quill para QL
  nueva_linea           = 254                    # Así es en las bases de datos de Quill para QL
  plataforma            = 1                      # Apaño para que el intérprete lo considere como Spectrum
  id_plataforma         = 'QL'
  BANDERA_VERBO[0]      = 64
  BANDERA_NOMBRE[0]     = 65
  BANDERA_LLEVABLES[0]  = 66
  BANDERA_LOC_ACTUAL[0] = 63
  NUM_ATRIBUTOS[0]      = 1
  NUM_BANDERAS[0]       = 67
  NUM_BANDERAS_ACC[0]   = 63
  cods_tinta.clear()
  cods_tinta.update ({16: 0, 17: 1, 18: 2, 19: 3, 20: 4, 21: 5, 22: 6, 23: 7})
  fichero.seek (0)
  if fichero.read (18) == b']!QDOS File Header':  # Tiene cabecera QDOS puesta por el emulador
    despl_ini = -30  # Es de 30 bytes en sQLux
  else:
    despl_ini = 0  # En QL, los desplazamientos son directamente las posiciones en la BD
  bajo_nivel_cambia_endian (le = False)  # Los desplazamientos en las bases de datos de QL son big endian
  bajo_nivel_cambia_despl  (despl_ini)
  # Cargamos los colores iniciales
  bajo_nivel_cambia_ent (fichero)
  fichero.seek (-despl_ini + 1)
  colores_inicio.append (carga_int1())     # Color de papel
  colores_inicio.insert (0, carga_int1())  # Color de tinta
  colores_inicio.append (carga_int1())     # Quill no usa este valor. Lo usaremos para almacenar valor de brillo
  colores_inicio.append (carga_int1())     # Ancho del borde
  colores_inicio.insert (2, carga_int1())  # Color de borde
  preparaPosCabecera ('qql', -despl_ini + 6)
  return cargaBD (fichero, longitud)

def carga_bd_sna (fichero, longitud):
  """Carga la base de datos entera desde un fichero de imagen de memoria de Spectrum 48K

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global carga_desplazamiento, despl_ini, fin_cadena, nueva_linea, pos_msgs_sys, id_plataforma
  # if longitud not in (49179, 131103):  # Tamaño de 48K y de 128K
  if longitud != 49179:
    return False  # No parece un fichero de imagen de memoria de Spectrum 48K
  carga_desplazamiento = carga_desplazamiento2
  id_plataforma        = 'ZX'
  # Detectamos la posición de la cabecera de la base de datos
  bajo_nivel_cambia_ent (fichero)
  posicion = busca_secuencia ((16, None, 17, None, 18, None, 19, None, 20, None, 21))
  if posicion == None:
    return False  # Cabecera de la base de datos no encontrada
  despl_ini = 16357  # Al menos es así en Hampstead y Manor of Madness, igual que PAWS
  bajo_nivel_cambia_endian (le = True)  # Al menos es así en ZX Spectrum
  bajo_nivel_cambia_despl  (despl_ini)
  fin_cadena  = 31  # Igual que PAWS
  nueva_linea = ord ('\r')
  # Cargamos los colores iniciales
  fichero.seek (posicion - 9)
  colores_inicio.append (ord (fichero.read (1)))  # Color de tinta
  fichero.read (1)
  colores_inicio.append (ord (fichero.read (1)))  # Color de papel
  fichero.read (3)
  colores_inicio.append (ord (fichero.read (1)))  # Brillo
  fichero.read (5)
  colores_inicio.insert (2, ord (fichero.read (1)))  # Color de borde
  posBD = posicion + 3
  # Detectamos si es una versión vieja de Quill, sin lista de posiciones de mensajes de sistema
  formato = 'sna48k'  # Por defecto asumimos que no es una versión de Quill vieja
  # Buscamos el código ensamblador de la parte de Quill donde utiliza el mensaje de sistema 0
  if busca_secuencia ((0xdd, 0xbe, 0, 0x28, None, 0xdd, 0xbe, 3, 0x28, None, 0xdd, 0x35, 3, 0x3a, None, None, 0xdd, 0xbe, None, 0x28, None, 0xfe, 0xfd, 0x30, None, 0x21)):
    pos_msgs_sys = carga_int2_le()
    if pos_msgs_sys:
      formato = 'sna48k_old'
      # TODO: cargar UDGs presentes en este formato, añadiéndolos a la fuente tipográfica
  preparaPosCabecera (formato, posBD)
  return cargaBD (fichero, longitud, formato == 'sna48k')

def carga_sce (fichero, longitud):
  """Carga la base de datos desde el código fuente SCE del fichero de entrada

  Para compatibilidad con el IDE:
  - Recibe como primer parámetro un fichero abierto
  - Recibe como segundo parámetro la longitud del fichero abierto
  - Devuelve False si ha ocurrido algún error"""
  global id_plataforma, max_llevables, plataforma, version
  # Los dos valores siguientes son necesarios para el intérprete y esta librería, pondremos valores de PAWS PC
  plataforma = 1  # Apaño para que el intérprete lo considere como Spectrum
  version    = 1
  id_plataforma = 'QL'      # Esta es la más completa en cuanto a condactos disponibles
  actualizaAcciones (True)  # Ponemos las acciones correctas para esta plataforma
  BANDERA_VERBO[0]      = 64
  BANDERA_NOMBRE[0]     = 65
  BANDERA_LLEVABLES[0]  = 66
  BANDERA_LOC_ACTUAL[0] = 63
  NUM_ATRIBUTOS[0]      = 1
  NUM_BANDERAS[0]       = 67
  NUM_BANDERAS_ACC[0]   = 63
  # Asignamos colores y número máximo de objetos llevables
  cods_tinta.clear()
  cods_tinta.update ({16: 0, 17: 1, 18: 2, 19: 3, 20: 4, 21: 5, 22: 6, 23: 7})
  colores_inicio.extend ((4, 0, 0, 0))  # Tinta verde, papel y borde negro, y sin brillo
  max_llevables = 4
  retorno = alto_nivel.carga_codigo_fuente (fichero, longitud, LONGITUD_PAL, NOMBRE_SISTEMA, [], [], condactos, {}, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, [], num_objetos, tablas_proceso, vocabulario, escribe_secs_ctrl)
  # Liberamos la memoria utilizada para la carga
  import gc
  gc.collect()
  return retorno

def guarda_bd (bbdd):
  """Almacena la base de datos entera en el fichero de salida, de forma optimizada. Devuelve None si no hubo error, o mensaje resumido y detallado del error"""
  global carga_desplazamiento, fich_sal, guarda_desplazamiento
  extension = os.path.splitext (bbdd.name)[1][1:].lower()
  formato   = 'c64' if extension == 'prg' else extension
  areasYaEscritas = []  # Áreas del fichero ya escritas, para deduplicar datos ya existentes en la base de datos
  porColocar      = {}  # Secciones del fichero reubicables pendientes de colocar
  fich_sal     = bbdd
  conversion   = None             # Conversión de juego de caracteres
  desplIniFich = 0                # Posición donde empieza la BD en el fichero
  desplIniMem  = 0                # Posición donde se cargará en memoria la BD
  finCadena    = 0                # Carácter de fin de cadena
  nuevaLinea   = ord ('\r')       # Carácter de nueva línea
  numLocs      = len (desc_locs)  # Número de localidades
  numMsgsUsr   = len (msgs_usr)   # Número de mensajes de usuario
  numMsgsSys   = len (msgs_sys)   # Número de mensajes de sistema
  tamCabecera  = 0                # Tamaño en bytes de la cabecera de Quill
  tamDespl     = 2                # Tamaño en bytes de las posiciones
  tamMaxBD     = 65536            # Tamaño máximo de base de datos
  bajo_nivel_cambia_despl (desplIniMem)
  bajo_nivel_cambia_ent   (bbdd)
  bajo_nivel_cambia_sal   (bbdd)
  if formato == 'c64':
    plataformaDestino = 'C64'
    conversion   = ascii_a_petscii
    desplIniFich = 2
    desplIniMem  = 2048
    nuevaLinea   = 141
    tamCabecera  = 31
    tamMaxBD     = 35071
    carga_desplazamiento  = carga_desplazamiento2
    guarda_desplazamiento = guarda_desplazamiento2
    bajo_nivel_cambia_despl  (desplIniMem)
    bajo_nivel_cambia_endian (le = True)
    preparaPosCabecera (formato, desplIniFich + 4)
    # Guardamos la cabecera de Commodore 64
    guarda_desplazamiento (0)  # Desplazamiento donde se cargará en memoria la BD
  elif formato == 'dtb':  # Atari 800
    plataformaDestino = 'Atari800'
    desplIniMem  = 7418
    nuevaLinea   = 155
    tamCabecera  = 37
    tamMaxBD     = 31680
    carga_desplazamiento  = carga_desplazamiento2
    guarda_desplazamiento = guarda_desplazamiento2
    bajo_nivel_cambia_despl  (desplIniMem)
    bajo_nivel_cambia_endian (le = True)
    preparaPosCabecera ('a800', 10)
    # Guardamos la cabecera de Atari 800
    guarda_int2_le (65535)  # Marca de ejecutable
    guarda_int2_le (7424)   # Desplazamiento donde se cargará en memoria la BD
    # Dejamos espacio para la posición siguiente tras la base de datos
    guarda_desplazamiento (-desplIniMem)
  else:  # formato == 'qql'
    plataformaDestino = 'QL'
    desplIniFich = 30
    nuevaLinea   = 254
    tamCabecera  = 60
    tamDespl     = 4
    carga_desplazamiento  = carga_desplazamiento4
    guardaInt4            = guarda_int4_be
    guarda_desplazamiento = guarda_desplazamiento4
    bajo_nivel_cambia_endian (le = False)
    preparaPosCabecera (formato, desplIniFich + 6)
    # Guardamos la cabecera para QDOS (al menos la usa el emulador sQLux)
    fich_sal.write (b']!QDOS File Header')
    guarda_int1 (0)   # Reservado
    guarda_int1 (15)  # Longitud de la cabecera de QDOS en palabras de 16 bits
    guarda_int1 (0)   # Tipo de acceso de fichero
    guarda_int1 (72)  # Tipo de fichero
    guardaInt4  (0)   # Longitud de datos
    guardaInt4  (0)   # Reservado

  # Guardamos la cabecera de Quill

  guarda_int1 (0)  # ¿Plataforma?
  if formato == 'qql':
    guarda_int1 (colores_inicio[1])  # Color de papel
  if formato == 'dtb':  # Atari 800
    guarda_int1 (13)  # Contraste de la tinta
  else:
    guarda_int1 (colores_inicio[0])  # Color de tinta
  if formato == 'qql' and len (colores_inicio) > 3:
    guarda_int1 (colores_inicio[3])  # Quill no usa este valor. Lo usaremos para almacenar valor de brillo
  elif formato == 'dtb':
    guarda_int1 (176)  # Papel verde oscuro
  else:
    guarda_int1 (colores_inicio[1])  # Color de papel
  if formato == 'qql':
    guarda_int1 (colores_inicio[4] if len (colores_inicio) > 4 else 2)  # Anchura del borde
  if formato == 'dtb':
    guarda_int1 (176)  # Borde verde oscuro
  else:
    guarda_int1 (colores_inicio[2])  # Color del borde
  guarda_int1 (max_llevables)
  guarda_int1 (num_objetos[0])
  guarda_int1 (numLocs)
  guarda_int1 (numMsgsUsr)
  guarda_int1 (numMsgsSys)
  if formato == 'qql':
    guarda_int1 (0)  # Relleno
  # Eliminamos entradas sin acciones, los editores de Quill no las permiten y el código de guardado optimizado de tablas de proceso tampoco
  tablasLimpias = []
  for cabeceras, entradas in tablas_proceso:
    cabecerasLimpias = []
    entradasLimpias  = []
    for e in range (len (entradas)):
      algunaAccion = False
      for entrada in entradas[e]:
        condacto, parametros = entrada[:2]
        if condacto >= 100:
          algunaAccion = True
          break
      if algunaAccion:
        cabecerasLimpias.append (cabeceras[e])
        entradasLimpias.append  (entradas[e])
    tablasLimpias.append ((cabecerasLimpias, entradasLimpias))
  # Dejamos anotado lo que ya está escrito
  if formato == 'dtb':
    areasYaEscritas.extend (([0, 2 * tamDespl], [3 * tamDespl, CAB_POS_EVENTOS]))
  else:
    areasYaEscritas.append ([desplIniFich, CAB_POS_EVENTOS])
  # Guardamos la posición de las cabeceras de las tablas de eventos y estado que no estén vacías
  ocupado = tamCabecera  # Espacio ocupado hasta ahora
  for t in range (2):
    if tablasLimpias[t][0]:
      anyadeArea (fich_sal.tell(), fich_sal.tell() + tamDespl, areasYaEscritas)
      guarda_desplazamiento (ocupado)
      ocupado += (len (tablasLimpias[t][0]) * (2 + tamDespl)) + 1
    else:  # Esta tabla está vacía
      porColocar[fich_sal.tell()] = [0]     # Secuencia que colocar con una cabecera de tabla vacía
      guarda_desplazamiento (-desplIniMem)  # Dejamos espacio para la posición de la cabecera vacía
  # Guardamos la posición de la lista de posiciones de las descripciones de los objetos
  guarda_desplazamiento (ocupado)
  ocupado += num_objetos[0] * tamDespl
  # Guardamos la posición de la lista de posiciones de las descripciones de las localidades
  guarda_desplazamiento (ocupado)
  ocupado += numLocs * tamDespl
  # Guardamos la posición de la lista de posiciones de los mensajes de usuario
  guarda_desplazamiento (ocupado)
  ocupado += numMsgsUsr * tamDespl
  # Guardamos la posición de la lista de posiciones de los mensajes de sistema
  guarda_desplazamiento (ocupado)
  ocupado += numMsgsSys * tamDespl
  # Guardamos la posición de la lista de posiciones de las conexiones
  guarda_desplazamiento (ocupado)
  ocupado += numLocs * tamDespl
  # Dejamos espacio para la posición del vocabulario
  areasYaEscritas.append ([CAB_POS_LST_POS_OBJS, CAB_POS_VOCAB])
  guarda_desplazamiento (-desplIniMem)
  # Dejamos espacio para la posición de las localidades iniciales de los objetos
  guarda_desplazamiento (-desplIniMem)
  if formato == 'qql':
    # Dejamos espacio para la posición de los nombres de los objetos
    guarda_desplazamiento (-desplIniMem)
  # Dejamos espacio para la posición siguiente tras la base de datos
  guarda_desplazamiento (-desplIniMem)
  # Guardamos la posición siguiente tras la base de datos más grande posible
  guarda_desplazamiento (tamMaxBD - desplIniMem)
  areasYaEscritas.append ([desplIniFich + tamCabecera - tamDespl, desplIniFich + tamCabecera])

  # Guardamos las tablas con posiciones que rellenar

  # Guardamos las cabeceras de las tablas de eventos y de estado, dejando espacio para las posiciones de las entradas
  # De paso, recopilaremos el código de las entradas como reubicables
  adaptados.clear()  # Condactos que se han adaptado al convertir de una plataforma a otra
  for t in range (2):
    cabeceras, entradas = tablasLimpias[t]
    for e in range (len (entradas)):
      posicion = fich_sal.tell()
      guarda_int1 (cabeceras[e][0])  # Palabra 1 (normalmente verbo)
      guarda_int1 (cabeceras[e][1])  # Palabra 2 (normalmente nombre)
      if areasYaEscritas[-1][1] == posicion:
        areasYaEscritas[-1][1] += 2
      else:
        areasYaEscritas.append ([posicion, posicion + 2])
      algunaAccion = False  # Si se ha encontrado ya alguna acción en la entrada
      accionFlujo  = False  # Si la entrada termina con una acción que cambia el flujo de ejecución incondicionalmente
      secuencia    = []
      for entrada in entradas[e]:
        condacto, parametros = entrada[:2]
        if condacto >= 100:
          if not algunaAccion:
            secuencia.append (255)  # Fin de condiciones
          algunaAccion = True
        entradaOcurrencia = (t, e)  # El lugar de esta ocurrencia (número de proceso y de entrada en éste)
        nombreCondacto    = condactos[condacto][0]
        condactoDestino, nombreCondacto, parametrosDestino = convierteCondacto (condacto, nombreCondacto, parametros, plataformaDestino, entradaOcurrencia)  # Condacto en plataforma de destino
        if condactoDestino == None:  # Hay error y el mensaje está en nombreCondacto
          prn ('ERROR:', nombreCondacto, file = sys.stderr)  # Por si se exportaba desde otro sitio que no sea el IDE
          return (_('Missing condact'), nombreCondacto)
        secuencia.append (condactoDestino - (100 if algunaAccion else 0))
        secuencia.extend (parametrosDestino)
        if algunaAccion and condactos_destino[plataformaDestino][nombreCondacto][3]:
          accionFlujo = True
          break  # Esta acción cambia el flujo de ejecución incondicionalmente
      if not accionFlujo:
        secuencia.append (255)  # Fin de acciones y entrada
      porColocar[fich_sal.tell()] = secuencia
      # Dejamos espacio para la posición de esta entrada
      guarda_desplazamiento (-desplIniMem)
    posicion = fich_sal.tell()
    if entradas:
      guarda_int1 (0)  # Marca de fin de cabecera de tabla
      areasYaEscritas.append ([posicion, posicion + 1])

  # Recopilamos las demás secciones reubicables de la base de datos

  # Obtenemos el vocabulario
  porColocar[CAB_POS_VOCAB] = daVocabulario (conversion)
  # Recopilamos las localidades iniciales de los objetos
  secuencia = []
  for localidad in locs_iniciales:
    secuencia.append (localidad)
  secuencia.append (255)  # Fin de la lista de localidades iniciales de los objetos
  porColocar[CAB_POS_LOCS_OBJS] = secuencia
  if formato == 'qql':
    # Recopilamos los nombres de los objetos
    secuencia = []
    for nombre, adjetivo in nombres_objs:
      secuencia.append (nombre)
    secuencia.append (0)  # Fin de la lista de nombres de los objetos
    porColocar[CAB_POS_NOMS_OBJS] = secuencia
  # Recopilamos las conexiones de las localidades
  posicion = carga_desplazamiento (CAB_POS_LST_POS_CNXS) + desplIniFich
  for c in range (len (conexiones)):
    secuencia = []
    for conexion in conexiones[c]:
      secuencia.extend (list (conexion))
    secuencia.append (255)  # Fin de las conexiones de esta localidad
    porColocar[posicion + c * tamDespl] = secuencia
  # Recopilamos los textos de la aventura
  # TODO: eliminar espacios superfluos a final de línea en cada línea cuando se parten con nueva línea, salvo la última
  #       ojo que puede haber espacios no superfluos, si causan nueva línea adicional por superar ancho de línea o si cambian el color de fondo
  diccConversion = {}
  if plataformaDestino in conversion_plataforma:
    for entrada, salida in conversion_plataforma[plataformaDestino].items():
      diccConversion[salida] = ord (entrada)
  for posCabecera, mensajes in ((CAB_POS_LST_POS_OBJS, desc_objs), (CAB_POS_LST_POS_LOCS, desc_locs), (CAB_POS_LST_POS_MSGS_USR, msgs_usr), (CAB_POS_LST_POS_MSGS_SYS, msgs_sys)):
    posicion = carga_desplazamiento (posCabecera) + desplIniFich
    for m in range (len (mensajes)):
      secuencia = daCadena (mensajes[m], finCadena, nuevaLinea, conversion, diccConversion)
      porColocar[posicion + m * tamDespl] = secuencia

  # Detectamos las secuencias reubicables duplicadas
  duplicadas    = set()  # Posiciones de secuencias duplicadas, salen todas menos la primera ocurrencia
  duplicadasInv = {}     # Posiciones de secuencias duplicadas para cada primera ocurrencia
  for posicion, secuencia in porColocar.items():
    if posicion in duplicadas:
      continue
    for posicion2, secuencia2 in porColocar.items():
      if posicion2 == posicion:
        continue
      if secuencia == secuencia2:
        duplicadas.add (posicion2)
        if posicion not in duplicadasInv:
          duplicadasInv[posicion] = []
        duplicadasInv[posicion].append (posicion2)
  for posicion in duplicadas:
    del porColocar[posicion]
  # prn (len (porColocar), len (duplicadasInv), file = sys.stderr)

  # Colocamos las secciones reubicables

  dlg_progreso[0].setRange (- len (porColocar) - len (duplicadasInv), 0)
  ahorrosColocar = {}
  iteracion      = 0
  secuenciaFinal = []
  while porColocar:
    if dlg_progreso[0].wasCanceled():
      colocaSiguiente = True
      siguiente       = porColocar.keys()[0]
      solape          = 0
    else:
      # Colocamos las secciones cuyo contenido esté por completo entre las áreas ya escritas del fichero
      cambia_progreso.emit (- len (porColocar) - len (duplicadasInv))
      # Juntamos las secuencias de porColocar en un árbol "trie" para buscarlas todas en el fichero de una sola pasada
      porColocarSecs = {}
      for posicion, secuencia in porColocar.items ():
        casilla = porColocarSecs
        for s in range (len (secuencia)):
          if secuencia[s] not in casilla:
            casilla[secuencia[s]] = [{}, None]
          if s == len (secuencia) - 1:
            casilla[secuencia[s]][1] = posicion  # Basta con esto porque no hay secuencias duplicadas en porColocar
          else:
            casilla = casilla[secuencia[s]][0]
      # Colocamos las secciones cuyo contenido ya estaba escrito en algún lugar del fichero
      for posicion, posSecuencia in buscaSecuenciasEnAreas (porColocarSecs, areasYaEscritas, porColocar, desplIniFich).items():
        posSecuencia -= desplIniFich
        posiciones    = [posicion]
        if posicion in duplicadasInv:
          posiciones.extend (duplicadasInv[posicion])
          del duplicadasInv[posicion]
        # Guardamos punteros a secciones como esta
        for posicion in posiciones:
          fich_sal.seek (posicion)
          guarda_desplazamiento (posSecuencia)
          anyadeArea (posicion, posicion + tamDespl, areasYaEscritas)
        del porColocar[posiciones[0]]
      # prn (len (porColocar), len (duplicadasInv), file = sys.stderr)
      cambia_progreso.emit (- len (porColocar) - len (duplicadasInv))
      if not porColocar:
        break  # Ya las hemos colocado todas
      # Vemos el tamaño de los solapes que hay entre el fin de la última área del fichero y el inicio de cada sección restante por colocar
      if areasYaEscritas[-1][1] >= ocupado:  # Sólo si la última área del fichero ya está escrita
        # Extendemos secuenciaFinal con lo que haya nuevo al final del fichero
        nuevoAlFinal = areasYaEscritas[-1][1] - areasYaEscritas[-1][0] - len (secuenciaFinal)
        if nuevoAlFinal > 0:
          fich_sal.seek (areasYaEscritas[-1][1] - nuevoAlFinal)
          for b in range (areasYaEscritas[-1][1] - nuevoAlFinal, areasYaEscritas[-1][1]):
            secuenciaFinal.append (ord (fich_sal.read (1)))
        # Buscamos solapes entre lo último escrito al final del fichero y cada sección restante por colocar
        for posicion, secuencia in porColocar.items():
          for s in range (min (len (secuencia), len (secuenciaFinal)), 0, -1):
            if secuenciaFinal[-s:] == secuencia[:s]:
              ahorro = s
              if posicion in duplicadasInv:
                ahorro += s * len (duplicadasInv[posicion])
              if ahorro not in ahorrosColocar:
                ahorrosColocar[ahorro] = []
              ahorrosColocar[ahorro].append ((0, posicion))
              break
      if not iteracion:  # Sólo en la primera iteración
        # Vemos el tamaño de los solapes que hay entre fin e inicio de cada combinación de secciones restantes por colocar
        for posicion, secuencia in porColocar.items():
          for posicion2, secuencia2 in porColocar.items():
            if posicion2 == posicion:
              continue
            # XXX: esto es código común con lo de justo arriba
            for s in range (min (len (secuencia), len (secuencia2)), 0, -1):
              if secuencia[-s:] == secuencia2[:s]:
                ahorro = s
                if posicion2 in duplicadasInv:
                  ahorro += s * len (duplicadasInv[posicion2])
                if ahorro not in ahorrosColocar:
                  ahorrosColocar[ahorro] = []
                ahorrosColocar[ahorro].append ((posicion, posicion2))
                break
            # XXX: aquí termina el código duplicado
      for ahorro in ahorrosColocar:
        ahorrosColocar[ahorro].sort()  # Los necesitamos ordenados
      # Vemos cuáles de las secciones restantes ahorrarán espacio por solaparse sobre la última área escrita del fichero
      colocaSiguiente = False
      siguientes      = {}  # Posición de secuencias que ahorrarán espacio por colocarse tras la última área escrita, solape con ésta y cuánto ahorran
      for ahorro in ahorrosColocar:
        for posicion, posicion2 in ahorrosColocar[ahorro]:
          if posicion:
            break  # Ya hemos terminado de ver las combinaciones que ahorran ahorro tras la última área escrita
          siguientes[posicion2] = [ahorro // (len (duplicadasInv.get (posicion2, ())) + 1), ahorro]
      # Vemos cuáles de las secciones restantes si se ponen al final del fichero constituiría un prefijo mayor de otra
      if areasYaEscritas[-1][1] >= ocupado:  # Sólo si la última área del fichero ya está escrita
        ahorrosExtraFin  = {}
        ahorrosSolapeFin = {}
        for posicion, secuencia in porColocar.items():
          secuenciaSobreFin = secuenciaFinal + secuencia
          for posicion2, secuencia2 in porColocar.items():
            if posicion2 == posicion:
              continue
            if secuencia2 in secuenciaSobreFin and secuencia2 not in secuenciaFinal:  # Quedará totalmente incluida gracias a esto
              if posicion in ahorrosExtraFin:
                ahorrosExtraFin[posicion] += len (secuencia2)
              else:
                ahorrosExtraFin[posicion] = len (secuencia2)
            else:  # No quedará totalmente incluida con esto
              # Buscamos solapes adicionales si se coloca la sección de posición posicion tras la última área escrita
              for s in range (min (len (secuencia2) - 1, len (secuenciaSobreFin)), len (secuencia), -1):
                if secuenciaSobreFin[-s:] == secuencia2[:s]:
                  ahorroTotal = s
                  if posicion in ahorrosSolapeFin:
                    ahorrosSolapeFin[posicion] = max (ahorrosSolapeFin[posicion], ahorroTotal)
                  else:
                    ahorrosSolapeFin[posicion] = ahorroTotal
                  break
        for posicion in ahorrosSolapeFin:
          if posicion in siguientes:
            siguientes[posicion][1] = max (siguientes[posicion], ahorrosSolapeFin[posicion])
          else:
            siguientes[posicion] = [0, ahorrosSolapeFin[posicion]]
        for posicion in ahorrosExtraFin:
          if posicion in siguientes:
            siguientes[posicion][1] += ahorrosExtraFin[posicion]
          else:
            siguientes[posicion] = [0, ahorrosExtraFin[posicion]]
      if siguientes:
        # TODO: quitar de siguientes las que ahorrarían más colocadas detrás de alguna otra
        # Buscamos las de máximo ahorro
        maxAhorro = 0
        posMax    = None  # Primera posición encontrada con máximo ahorro
        solapeMax = None  # Solape de la primera posición encontrada con máximo ahorro
        for siguiente in siguientes:
          solape, ahorro = siguientes[siguiente]
          if ahorro > maxAhorro:
            maxAhorro = ahorro
            solapeMax = solape
            posMax    = siguiente
        colocaSiguiente = True
        siguiente       = posMax
        solape          = solapeMax
      else:  # Ninguna de las secuencias restantes ahorrarán nada por ponerlas al final del fichero
        solape = 0
        # Buscamos una sección de las restantes que no tenga ahorro por colocarse detrás de ninguna otra
        for posicion, secuencia in porColocar.items():
          clavesAhorros = sorted (ahorrosColocar.keys(), reverse = True)
          for a in (range (len (clavesAhorros))):
            for parPosiciones in ahorrosColocar[ahorro]:
              if parPosiciones[1] == posicion:
                break  # Encontrada, no sirve esta
            else:  # No encontrada, puede servir esta
              continue
            break  # Encontrada, no sirve esta
          else:  # No encontrada, sirve esta
            colocaSiguiente = True
            siguiente       = posicion
            break
        else:  # Todas tenían algo de ahorro por colocarse detrás de alguna otra
          colocaSiguiente = True  # Nos quedamos una cualquiera (la última recorrida, en este caso)
          siguiente       = posicion
    # Colocamos la sección
    if colocaSiguiente:
      posicion     = siguiente
      posSecuencia = ocupado - solape
      secuencia    = porColocar[siguiente]
      # TODO: crear función con el siguiente código, duplicado arriba
      posiciones = [posicion]
      if posicion in duplicadasInv:
        posiciones.extend (duplicadasInv[posicion])
        del duplicadasInv[posicion]
      # Guardamos punteros a secciones como esta
      for posicion in posiciones:
        fich_sal.seek (posicion)
        guarda_desplazamiento (posSecuencia)
        anyadeArea (posicion, posicion + tamDespl, areasYaEscritas)
      del porColocar[posiciones[0]]
      # XXX: aquí termina el código duplicado
      # Guardamos esta sección
      fich_sal.seek (desplIniFich + ocupado)
      for codigo in secuencia[solape:]:
        guarda_int1 (codigo)
      anyadeArea (desplIniFich + ocupado, desplIniFich + ocupado + len (secuencia) - solape, areasYaEscritas)
      ocupado += len (secuencia) - solape
      # Limpiamos ahorrosColocar, quitando entradas desde 0 (el final de fichero anterior), y desde y hasta la secuencia de la posición siguiente
      for ahorro in tuple (ahorrosColocar.keys()):
        indicesEliminar = set()
        for a in range (len (ahorrosColocar[ahorro])):
          parPosiciones = ahorrosColocar[ahorro][a]
          if parPosiciones[0] == 0 or siguiente in parPosiciones:
            indicesEliminar.add (a)
        eliminados = 0
        for a in sorted (indicesEliminar):
          del ahorrosColocar[ahorro][a - eliminados]
          eliminados += 1
        if not ahorrosColocar[ahorro]:
          del ahorrosColocar[ahorro]
    # prn (len (porColocar), len (duplicadasInv), file = sys.stderr)
    if not dlg_progreso[0].wasCanceled():
      cambia_progreso.emit (- len (porColocar) - len (duplicadasInv))
    iteracion += 1

  # Guardamos la posición siguiente tras la base de datos
  fich_sal.seek (CAB_POS_NOMS_OBJS + (tamDespl if formato == 'qql' else 0))
  guarda_desplazamiento (ocupado)
  if formato == 'dtb':  # Atari 800
    fich_sal.seek (4)
    guarda_desplazamiento (ocupado)
    fich_sal.seek (0, 2)
    guarda_int1 (0)  # Byte final para que no dé error de carga desde el editor de AdventureWriter

def guarda_bd_a800 (bbdd):
  """Almacena la base de datos entera en el fichero de salida, para Atari 800, replicando el formato original. Devuelve None si no hubo error, o mensaje resumido y detallado del error"""
  global fich_sal, guarda_desplazamiento
  fich_sal     = bbdd
  desplIniFich = 0                # Posición donde empieza la BD en el fichero
  desplIniMem  = 7418             # Posición donde se cargará en memoria la BD
  numLocs      = len (desc_locs)  # Número de localidades
  numMsgsUsr   = len (msgs_usr)   # Número de mensajes de usuario
  numMsgsSys   = len (msgs_sys)   # Número de mensajes de sistema
  tamCabecera  = 37               # Tamaño en bytes de la cabecera de Quill
  tamDespl     = 2                # Tamaño en bytes de las posiciones
  tamMaxBD     = 31680            # Tamaño máximo de base de datos
  bajo_nivel_cambia_despl  (desplIniMem)
  bajo_nivel_cambia_endian (le = True)
  bajo_nivel_cambia_sal    (bbdd)
  guarda_desplazamiento = guarda_desplazamiento2
  preparaPosCabecera ('a800', desplIniFich + 10)
  # Guardamos la cabecera de Atari 800
  guarda_int2_le (65535)  # Marca de ejecutable
  guarda_int2_le (7424)   # Desplazamiento donde se cargará en memoria la BD
  # Dejamos espacio para la posición siguiente tras la base de datos
  guarda_desplazamiento (-desplIniMem)
  # Guardamos la cabecera de Quill
  guarda_int1 (0)    # ¿Plataforma?
  guarda_int1 (13)   # Contraste de la tinta
  guarda_int1 (176)  # Papel verde oscuro
  guarda_int1 (176)  # Borde verde oscuro
  guarda_int1 (max_llevables)
  guarda_int1 (num_objetos[0])
  guarda_int1 (numLocs)
  guarda_int1 (numMsgsUsr)
  guarda_int1 (numMsgsSys)
  ocupado = tamCabecera  # Espacio ocupado hasta ahora
  # Guardamos las entradas y cabeceras de las tablas de eventos y de estado
  adaptados.clear()  # Condactos que se han adaptado al convertir de una plataforma a otra
  fich_sal.seek (desplIniFich + ocupado)
  for t in range (2):
    cabeceras, entradas = tablas_proceso[t]
    # Guardamos el contenido de las entradas
    posiciones = []  # Posición de cada entrada
    for e in range (len (entradas)):
      posiciones.append (ocupado)
      algunaAccion = False
      for entrada in entradas[e]:
        condacto, parametros = entrada[:2]
        if condacto >= 100:
          if not algunaAccion:
            guarda_int1 (255)  # Fin de condiciones
          algunaAccion = True
        entradaOcurrencia = (t, e)  # El lugar de esta ocurrencia (número de proceso y de entrada en éste)
        nombreCondacto    = condactos[condacto][0]
        condactoDestino, nombreCondacto, parametrosDestino = convierteCondacto (condacto, nombreCondacto, parametros, 'Atari800', entradaOcurrencia)  # Condacto en plataforma de destino
        if condactoDestino == None:  # Hay error y el mensaje está en nombreCondacto
          prn ('ERROR:', nombreCondacto, file = sys.stderr)  # Por si se exportaba desde otro sitio que no sea el IDE
          return (_('Missing condact'), nombreCondacto)
        guarda_int1 (condactoDestino - (100 if algunaAccion else 0))
        for parametro in parametrosDestino:
          guarda_int1 (parametro)
        ocupado += 1 + len (parametrosDestino)
      if not algunaAccion:
        guarda_int1 (255)  # Fin de condiciones
      guarda_int1 (255)  # Fin de acciones y entrada
      ocupado += 2  # Las marcas de fin de condiciones y acciones
    # Guardamos la posición de la cabecera de la tabla
    fich_sal.seek (CAB_POS_EVENTOS + t * tamDespl)
    guarda_desplazamiento (ocupado)
    # Guardamos las cabeceras de las entradas
    fich_sal.seek (desplIniFich + ocupado)
    for e in range (len (entradas)):
      guarda_int1 (cabeceras[e][0])          # Palabra 1 (normalmente verbo)
      guarda_int1 (cabeceras[e][1])          # Palabra 2 (normalmente nombre)
      guarda_desplazamiento (posiciones[e])  # Posición de la entrada
      ocupado += 2 + tamDespl
    guarda_int1 (0)  # Marca de fin de cabecera de tabla
    ocupado += 1
  # Guardamos los textos de la aventura y sus posiciones
  for posCabecera, mensajes in ((CAB_POS_LST_POS_OBJS, desc_objs), (CAB_POS_LST_POS_LOCS, desc_locs), (CAB_POS_LST_POS_MSGS_USR, msgs_usr), (CAB_POS_LST_POS_MSGS_SYS, msgs_sys)):
    posPrimerMsg = ocupado
    ocupado += guardaMsgs (mensajes, finCadena = 0, nuevaLinea = 155)
    fich_sal.seek (posCabecera)
    guarda_desplazamiento (ocupado)  # Posición de la lista de posiciones de este tipo de mensajes
    fich_sal.seek (desplIniFich + ocupado)
    guardaPosMsgs (mensajes, posPrimerMsg)
    ocupado += len (mensajes) * tamDespl
  # Guardamos las conexiones de las localidades
  posiciones = []  # Posición de las conexiones de cada localidad
  for lista in conexiones:
    posiciones.append (ocupado)
    for conexion in lista:
      guarda_int1 (conexion[0])
      guarda_int1 (conexion[1])
    guarda_int1 (255)  # Fin de las conexiones de esta localidad
    ocupado += len (lista) * 2 + 1
  fich_sal.seek (CAB_POS_LST_POS_CNXS)
  guarda_desplazamiento (ocupado)  # Posición de las conexiones
  fich_sal.seek (desplIniFich + ocupado)
  for posicion in posiciones:
    guarda_desplazamiento (posicion)
  ocupado += len (posiciones) * tamDespl
  # Guardamos el vocabulario
  fich_sal.seek (CAB_POS_VOCAB)
  guarda_desplazamiento (ocupado)  # Posición del vocabulario
  fich_sal.seek (desplIniFich + ocupado)
  guardaVocabulario (optimizado = False)
  ocupado += (len (vocabulario) + 1) * (LONGITUD_PAL + 1)
  # Guardamos las localidades iniciales de los objetos
  fich_sal.seek (CAB_POS_LOCS_OBJS)
  guarda_desplazamiento (ocupado)  # Posición de las localidades iniciales de los objetos
  fich_sal.seek (desplIniFich + ocupado)
  for localidad in locs_iniciales:
    guarda_int1 (localidad)
  guarda_int1 (255)  # Fin de la lista de localidades iniciales de los objetos
  ocupado += len (locs_iniciales) + 1
  guarda_int1 (0)  # Byte final, que no se cuenta para ocupado
  # Guardamos los últimos valores de la cabecera
  fich_sal.seek (4)
  guarda_desplazamiento (ocupado)
  fich_sal.seek (CAB_POS_NOMS_OBJS)
  guarda_desplazamiento (ocupado)                 # Posición justo detrás de la base de datos
  guarda_desplazamiento (tamMaxBD - desplIniMem)  # Posición justo detrás de la base de datos si esta fuera de tamaño máximo

def guarda_bd_c64 (bbdd):
  """Almacena la base de datos entera en el fichero de salida, para Commodore 64, replicando el formato original. Devuelve None si no hubo error, o mensaje resumido y detallado del error"""
  global fich_sal, guarda_desplazamiento
  fich_sal     = bbdd
  desplIniFich = 2                # Posición donde empieza la BD en el fichero
  desplIniMem  = 2048             # Posición donde se cargará en memoria la BD
  numLocs      = len (desc_locs)  # Número de localidades
  numMsgsUsr   = len (msgs_usr)   # Número de mensajes de usuario
  numMsgsSys   = len (msgs_sys)   # Número de mensajes de sistema
  tamCabecera  = 31               # Tamaño en bytes de la cabecera de Quill
  tamDespl     = 2                # Tamaño en bytes de las posiciones
  bajo_nivel_cambia_despl  (desplIniMem)
  bajo_nivel_cambia_endian (le = True)
  bajo_nivel_cambia_sal    (bbdd)
  guarda_desplazamiento = guarda_desplazamiento2
  guarda_desplazamiento (0)  # Desplazamiento donde se cargará en memoria la BD
  preparaPosCabecera ('c64', desplIniFich + 4)
  # Guardamos la cabecera de Quill
  guarda_int1 (0)  # ¿Plataforma?
  guarda_int1 (colores_inicio[0])  # Color de tinta
  guarda_int1 (colores_inicio[1])  # Color de papel
  guarda_int1 (colores_inicio[2])  # Color del borde
  guarda_int1 (max_llevables)
  guarda_int1 (num_objetos[0])
  guarda_int1 (numLocs)
  guarda_int1 (numMsgsUsr)
  guarda_int1 (numMsgsSys)
  ocupado = tamCabecera  # Espacio ocupado hasta ahora
  # Guardamos las entradas y cabeceras de las tablas de eventos y de estado
  adaptados.clear()  # Condactos que se han adaptado al convertir de una plataforma a otra
  fich_sal.seek (desplIniFich + ocupado)
  for t in range (2):
    cabeceras, entradas = tablas_proceso[t]
    # Guardamos el contenido de las entradas
    posiciones = []  # Posición de cada entrada
    for e in range (len (entradas)):
      posiciones.append (ocupado)
      algunaAccion = False
      for entrada in entradas[e]:
        condacto, parametros = entrada[:2]
        if condacto >= 100:
          if not algunaAccion:
            guarda_int1 (255)  # Fin de condiciones
          algunaAccion = True
        entradaOcurrencia = (t, e)  # El lugar de esta ocurrencia (número de proceso y de entrada en éste)
        nombreCondacto    = condactos[condacto][0]
        condactoDestino, nombreCondacto, parametrosDestino = convierteCondacto (condacto, nombreCondacto, parametros, 'C64', entradaOcurrencia)  # Condacto en plataforma de destino
        if condactoDestino == None:  # Hay error y el mensaje está en nombreCondacto
          prn ('ERROR:', nombreCondacto, file = sys.stderr)  # Por si se exportaba desde otro sitio que no sea el IDE
          return (_('Missing condact'), nombreCondacto)
        guarda_int1 (condactoDestino - (100 if algunaAccion else 0))
        for parametro in parametrosDestino:
          guarda_int1 (parametro)
        ocupado += 1 + len (parametrosDestino)
      if not algunaAccion:
        guarda_int1 (255)  # Fin de condiciones
      guarda_int1 (255)  # Fin de acciones y entrada
      ocupado += 2  # Las marcas de fin de condiciones y acciones
    # Guardamos la posición de la cabecera de la tabla
    fich_sal.seek (CAB_POS_EVENTOS + t * tamDespl)
    guarda_desplazamiento (ocupado)
    # Guardamos las cabeceras de las entradas
    fich_sal.seek (desplIniFich + ocupado)
    for e in range (len (entradas)):
      guarda_int1 (cabeceras[e][0])          # Palabra 1 (normalmente verbo)
      guarda_int1 (cabeceras[e][1])          # Palabra 2 (normalmente nombre)
      guarda_desplazamiento (posiciones[e])  # Posición de la entrada
      ocupado += 2 + tamDespl
    guarda_int1 (0)  # Marca de fin de cabecera de tabla
    ocupado += 1
  # Guardamos los textos de la aventura y sus posiciones
  for posCabecera, mensajes in ((CAB_POS_LST_POS_OBJS, desc_objs), (CAB_POS_LST_POS_LOCS, desc_locs), (CAB_POS_LST_POS_MSGS_USR, msgs_usr), (CAB_POS_LST_POS_MSGS_SYS, msgs_sys)):
    posPrimerMsg = ocupado
    ocupado += guardaMsgs (mensajes, finCadena = 0, nuevaLinea = 141, conversion = ascii_a_petscii)
    fich_sal.seek (posCabecera)
    guarda_desplazamiento (ocupado)  # Posición de la lista de posiciones de este tipo de mensajes
    fich_sal.seek (desplIniFich + ocupado)
    guardaPosMsgs (mensajes, posPrimerMsg)
    ocupado += len (mensajes) * tamDespl
  # Guardamos las conexiones de las localidades
  posiciones = []  # Posición de las conexiones de cada localidad
  for lista in conexiones:
    posiciones.append (ocupado)
    for conexion in lista:
      guarda_int1 (conexion[0])
      guarda_int1 (conexion[1])
    guarda_int1 (255)  # Fin de las conexiones de esta localidad
    ocupado += len (lista) * 2 + 1
  fich_sal.seek (CAB_POS_LST_POS_CNXS)
  guarda_desplazamiento (ocupado)  # Posición de las conexiones
  fich_sal.seek (desplIniFich + ocupado)
  for posicion in posiciones:
    guarda_desplazamiento (posicion)
  ocupado += len (posiciones) * tamDespl
  # Guardamos el vocabulario
  fich_sal.seek (CAB_POS_VOCAB)
  guarda_desplazamiento (ocupado)  # Posición del vocabulario
  fich_sal.seek (desplIniFich + ocupado)
  guardaVocabulario (ascii_a_petscii, False)
  ocupado += (len (vocabulario) + 1) * (LONGITUD_PAL + 1)
  # Guardamos las localidades iniciales de los objetos
  fich_sal.seek (CAB_POS_LOCS_OBJS)
  guarda_desplazamiento (ocupado)  # Posición de las localidades iniciales de los objetos
  fich_sal.seek (desplIniFich + ocupado)
  for localidad in locs_iniciales:
    guarda_int1 (localidad)
  guarda_int1 (255)  # Fin de la lista de localidades iniciales de los objetos
  ocupado += len (locs_iniciales) + 1
  # Guardamos los últimos valores de la cabecera
  fich_sal.seek (CAB_POS_NOMS_OBJS)
  guarda_desplazamiento (ocupado)  # Posición justo detrás de la base de datos
  guarda_desplazamiento (33023)    # Posición justo detrás de la base de datos si esta fuera de tamaño máximo

def guarda_bd_ql (bbdd):
  """Almacena la base de datos entera en el fichero de salida, para Sinclair QL, replicando el formato original. Devuelve None si no hubo error, o mensaje resumido y detallado del error"""
  global fich_sal, guarda_desplazamiento
  fich_sal     = bbdd
  desplIniFich = 30               # Posición donde empieza la BD en el fichero
  desplIni     = -desplIniFich    # Para descontar la cabecera para QDOS
  numLocs      = len (desc_locs)  # Número de localidades
  numMsgsUsr   = len (msgs_usr)   # Número de mensajes de usuario
  numMsgsSys   = len (msgs_sys)   # Número de mensajes de sistema
  tamCabecera  = 60               # Tamaño en bytes de la cabecera de Quill
  tamDespl     = 4                # Tamaño en bytes de las posiciones
  bajo_nivel_cambia_despl  (desplIni)  # Posición donde se cargará en memoria la BD
  bajo_nivel_cambia_endian (le = False)
  bajo_nivel_cambia_ent    (bbdd)
  bajo_nivel_cambia_sal    (bbdd)
  guardaInt4            = guarda_int4_be
  guarda_desplazamiento = guarda_desplazamiento4
  preparaPosCabecera ('qql', desplIniFich + 6)
  # Guardamos la cabecera para QDOS (al menos la usa el emulador sQLux)
  fich_sal.write (b']!QDOS File Header')
  guarda_int1 (0)   # Reservado
  guarda_int1 (15)  # Longitud de la cabecera de QDOS en palabras de 16 bits
  guarda_int1 (0)   # Tipo de acceso de fichero
  guarda_int1 (72)  # Tipo de fichero
  guardaInt4  (0)   # Longitud de datos
  guardaInt4  (0)   # Reservado
  # Guardamos la cabecera de Quill
  guarda_int1 (0)  # ¿Plataforma?
  guarda_int1 (colores_inicio[1])  # Color de papel
  guarda_int1 (colores_inicio[0])  # Color de tinta
  guarda_int1 (colores_inicio[3] if len (colores_inicio) > 3 else 0)  # No se usa, guardaré aquí el brillo
  guarda_int1 (colores_inicio[4] if len (colores_inicio) > 4 else 2)  # Anchura del borde
  guarda_int1 (colores_inicio[2])  # Color del borde
  guarda_int1 (max_llevables)
  guarda_int1 (num_objetos[0])
  guarda_int1 (numLocs)
  guarda_int1 (numMsgsUsr)
  guarda_int1 (numMsgsSys)
  guarda_int1 (0)  # Relleno
  # Estas dos posiciones no están calculadas aún
  guarda_desplazamiento (-desplIni)  # Posición de las cabeceras de la tabla de eventos
  guarda_desplazamiento (-desplIni)  # Posición de las cabeceras de la tabla de estado
  ocupado = tamCabecera - desplIni   # Espacio ocupado hasta ahora
  guarda_desplazamiento (ocupado)    # Posición de la lista de posiciones de las descripciones de los objetos
  ocupado += num_objetos[0] * tamDespl
  guarda_desplazamiento (ocupado)  # Posición de la lista de posiciones de las descripciones de las localidades
  ocupado += numLocs * tamDespl
  guarda_desplazamiento (ocupado)  # Posición de la lista de posiciones de los mensajes de usuario
  ocupado += numMsgsUsr * tamDespl
  guarda_desplazamiento (ocupado)  # Posición de la lista de posiciones de los mensajes de sistema
  ocupado += numMsgsSys * tamDespl
  guarda_desplazamiento (ocupado)  # Posición de la lista de posiciones de las conexiones
  ocupado += numLocs * tamDespl
  # Las siguientes tres posiciones se conocerán más adelante
  guarda_desplazamiento (-desplIni)         # Posición del vocabulario
  guarda_desplazamiento (-desplIni)         # Posición de las localidades de los objetos
  guarda_desplazamiento (-desplIni)         # Posición de los nombres de los objetos
  guarda_desplazamiento (-desplIni)         # Siguiente posición tras la base de datos
  guarda_desplazamiento (65536 - desplIni)  # Siguiente posición tras la base de datos más grande posible
  fich_sal.seek (CAB_POS_EVENTOS)
  guarda_desplazamiento (ocupado)  # Posición de las cabeceras de la tabla de eventos
  ocupado += (len (tablas_proceso[0][0]) + 1) * (2 + tamDespl)
  guarda_desplazamiento (ocupado)  # Posición de las cabeceras de la tabla de estado
  ocupado += (len (tablas_proceso[1][0]) + 1) * (2 + tamDespl)
  fich_sal.seek (desplIniFich + tamCabecera)  # Justo tras la cabecera de Quill
  # Guardamos las posiciones de las descripciones de los objetos
  ocupado += guardaPosMsgs (desc_objs, ocupado)
  # Guardamos las posiciones de las descripciones de las localidades
  ocupado += guardaPosMsgs (desc_locs, ocupado)
  # Guardamos las posiciones de los mensajes de usuario
  ocupado += guardaPosMsgs (msgs_usr, ocupado)
  # Guardamos las posiciones de los mensajes de sistema
  ocupado += guardaPosMsgs (msgs_sys, ocupado)
  # Guardamos las posiciones de las listas de conexiones de cada localidad
  for l in range (numLocs):
    guarda_desplazamiento (ocupado)
    ocupado += (2 * len (conexiones[l])) + 1
  fich_sal.seek (CAB_POS_VOCAB)
  guarda_desplazamiento (ocupado)  # Posición del vocabulario
  tamVocabulario = len (vocabulario) + (0 if ('*', 255, 0) in vocabulario else 1)
  ocupado += (tamVocabulario * (LONGITUD_PAL + 1)) + LONGITUD_PAL
  # Guardamos las cabeceras y entradas de las tablas de eventos y de estado
  adaptados.clear()  # Condactos que se han adaptado al convertir de una plataforma a otra
  for t in range (2):
    posicion = carga_desplazamiento4 (fich_sal.seek (CAB_POS_EVENTOS + t * tamDespl))
    fich_sal.seek (ocupado)  # Necesario si no hay entradas de proceso
    cabeceras, entradas = tablas_proceso[t]
    for e in range (len (entradas)):
      # Guardamos la cabecera de la entrada
      fich_sal.seek (posicion + e * (2 + tamDespl))
      guarda_int1 (cabeceras[e][0])    # Palabra 1 (normalmente verbo)
      guarda_int1 (cabeceras[e][1])    # Palabra 2 (normalmente nombre)
      guarda_desplazamiento (ocupado)  # Posición de la entrada
      # Guardamos el contenido de la entrada
      fich_sal.seek (ocupado)
      algunaAccion = False
      for entrada in entradas[e]:
        condacto, parametros = entrada[:2]
        if condacto >= 100:
          if not algunaAccion:
            guarda_int1 (255)  # Fin de condiciones
          algunaAccion = True
        entradaOcurrencia = (t, e)  # El lugar de esta ocurrencia (número de proceso y de entrada en éste)
        nombreCondacto    = condactos[condacto][0]
        condactoDestino, nombreCondacto, parametrosDestino = convierteCondacto (condacto, nombreCondacto, parametros, 'QL', entradaOcurrencia)  # Condacto en plataforma de destino
        if condactoDestino == None:  # Hay error y el mensaje está en nombreCondacto
          prn ('ERROR:', nombreCondacto, file = sys.stderr)  # Por si se exportaba desde otro sitio que no sea el IDE
          return (_('Missing condact'), nombreCondacto)
        guarda_int1 (condactoDestino - (100 if algunaAccion else 0))
        for parametro in parametrosDestino:
          guarda_int1 (parametro)
        ocupado += 1 + len (parametrosDestino)
      if not algunaAccion:
        guarda_int1 (255)  # Fin de condiciones
      guarda_int1 (255)  # Fin de acciones y entrada
      ocupado += 2  # Las marcas de fin de condiciones y acciones
    # Guardamos la entrada vacía final, de relleno
    guarda_int1 (255)  # Fin de condiciones
    guarda_int1 (255)  # Fin de acciones y entrada
    # Guardamos la cabecera de entrada vacía final
    fich_sal.seek (posicion + len (entradas) * (2 + tamDespl))
    guarda_int2_be (0)               # Marca de fin
    guarda_desplazamiento (ocupado)  # Posición de la entrada de relleno
    ocupado += 2
  # Guardamos los textos de la aventura
  diccConversion = {}
  for entrada, salida in conversion_plataforma['QL'].items():
    diccConversion[salida] = ord (entrada)
  fich_sal.seek (carga_desplazamiento4 (desplIniFich + tamCabecera))  # Vamos a la posición de la descripción del objeto 0
  for mensajes in (desc_objs, desc_locs, msgs_usr, msgs_sys):
    guardaMsgs (mensajes, finCadena = 0, nuevaLinea = 254, diccConversion = diccConversion)
  # Guardamos las listas de conexiones de cada localidad
  for lista in conexiones:
    for conexion in lista:
      guarda_int1 (conexion[0])
      guarda_int1 (conexion[1])
    guarda_int1 (255)  # Fin de las conexiones de esta localidad
  # Guardamos el vocabulario
  guardaVocabulario (optimizado = False)
  # Guardamos las localidades iniciales de los objetos
  fich_sal.seek (CAB_POS_LOCS_OBJS)
  guarda_desplazamiento (ocupado)  # Posición de las localidades iniciales de los objetos
  fich_sal.seek (ocupado)
  for localidad in locs_iniciales:
    guarda_int1 (localidad)
  guarda_int1 (255)  # Fin de la lista de localidades iniciales de los objetos
  ocupado += num_objetos[0] + 1
  # Guardamos los nombres de los objetos
  fich_sal.seek (CAB_POS_NOMS_OBJS)
  guarda_desplazamiento (ocupado)                       # Posición de los nombres de los objetos
  guarda_desplazamiento (ocupado + num_objetos[0] + 1)  # Siguiente posición tras la base de datos
  fich_sal.seek (ocupado)
  for nombre, adjetivo in nombres_objs:
    guarda_int1 (nombre)
  guarda_int1 (0)  # Fin de la lista de nombres de los objetos

def guarda_codigo_fuente (fichero):
  """Guarda la base de datos a código fuente SCE sobre el fichero de salida

  Para compatibilidad con el IDE:
  - Recibe como primer parámetro un fichero abierto
  - Devuelve False si ha ocurrido algún error"""
  return alto_nivel.guarda_codigo_fuente (fichero, NOMBRE_SISTEMA, NOMB_COMO_VERB, PREP_COMO_VERB, [], [], [], condactos, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, False, num_objetos, tablas_proceso, vocabulario, lee_secs_ctrl)

def inicializa_banderas (banderas):
  """Inicializa banderas con valores propios de Quill"""
  # Banderas de sistema, no accesibles directamente, en posición estándar de PAWS
  banderas[BANDERA_LLEVABLES[0]] = max_llevables

def escribe_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo la representación de secuencias de control en sus códigos"""
  convertida = ''
  inversa    = False  # Texto en inversa
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if c == '\t' and id_plataforma == 'ZX':
      convertida += '\x06'  # Tabulador
    elif c == '\\':
      if cadena[i + 1:i + len (_('BRIGHT')) + 2] == (_('BRIGHT') + '_') and id_plataforma == 'ZX':
        try:
          codigo = int (cadena[i + len (_('BRIGHT')) + 2: i + len (_('BRIGHT')) + 4], 16)
        except:
          codigo = 999
        if codigo < 256:
          convertida += chr (19) + chr (8 if codigo == 8 else (1 if codigo else 0))
          i += len (_('BRIGHT')) + 3
        else:
          convertida += c  # Lo trataremos literalmente como ese texto \BRILLO_loquesea
      elif cadena[i + 1:i + len (_('FLASH')) + 2] == (_('FLASH') + '_') and id_plataforma == 'ZX':
        try:
          codigo = int (cadena[i + len (_('FLASH')) + 2: i + len (_('FLASH')) + 4], 16)
        except:
          codigo = 999
        if codigo < 256:
          convertida += chr (19) + chr (8 if codigo == 8 else (1 if codigo else 0))
          i += len (_('FLASH')) + 3
        else:
          convertida += c  # Lo trataremos literalmente como ese texto \FLASH_loquesea
      elif cadena[i + 1:i + len (_('INVERSE')) + 2] == _('INVERSE') + '_':
        inversa = cadena[i + len (_('INVERSE')) + 2:i + len (_('INVERSE')) + 4] not in ('0', '00')
        if id_plataforma == 'C64':
          convertida += chr (18 if inversa else 146)
        elif id_plataforma == 'CPC':
          convertida += chr (9)
        elif id_plataforma == 'QL':
          convertida += chr (24)
        elif id_plataforma == 'ZX':
          convertida += chr (20) + chr (1 if inversa else 0)
        i += len (_('INVERSE')) + 3
      elif cadena[i + 1:i + len (_('INK')) + 2] == (_('INK') + '_'):
        try:
          codigo = int (cadena[i + len (_('INK')) + 2: i + len (_('INK')) + 4], 16)
        except:
          codigo = 999
        if id_plataforma == 'C64' and codigo < len (cods_tinta):
          for codigoColor in cods_tinta:
            if cods_tinta[codigoColor] == codigo:
              convertida += chr (codigoColor)
              break
          i += len (_('INK')) + 3
        elif id_plataforma == 'CPC' and codigo < 4:
          convertida += chr (codigo + 1)
          i += len (_('INK')) + 3
        elif id_plataforma == 'QL' and codigo < 8:
          convertida += chr (16 + codigo)
          i += len (_('INK')) + 3
        elif id_plataforma == 'ZX' and codigo < 10:  # Aparte de los colores 0-7, están los valores 8 (transparente) y 9 (contraste)
          convertida += chr (16) + chr (codigo)
          i += len (_('INK')) + 3
        else:  # No es un número de color permitido
          convertida += c  # Lo trataremos literalmente como ese texto \TINTA_loquesea
      elif cadena[i + 1:i + len (_('OVER')) + 2] == (_('OVER') + '_') and id_plataforma == 'ZX':
        encima = cadena[i + len (_('OVER')) + 2:i + len (_('OVER')) + 4] not in ('0', '00')
        convertida += chr (21) + chr (1 if encima else 0)
        i += len (_('OVER')) + 3
      elif cadena[i + 1:i + len (_('PAPER')) + 2] == (_('PAPER') + '_'):
        try:
          codigo = int (cadena[i + len (_('PAPER')) + 2: i + len (_('PAPER')) + 4], 16)
        except:
          codigo = 999
        if id_plataforma == 'CPC' and codigo < 4:
          convertida += chr (codigo + 5)
          i += len (_('PAPER')) + 3
        elif id_plataforma == 'QL' and codigo < 8:
          convertida += chr (16 + codigo) + chr (24)
          i += len (_('PAPER')) + 3
        elif id_plataforma == 'ZX' and codigo < 10:  # Aparte de los colores 0-7, están los valores 8 (transparente) y 9 (contraste)
          convertida += chr (17) + chr (codigo)
          i += len (_('PAPER')) + 3
        else:  # No es un número de color permitido
          convertida += c  # Lo trataremos literalmente como ese texto \PAPEL_loquesea
      elif cadena[i + 1:i + len (_('RESET')) + 1] == _('RESET') and id_plataforma == 'QL':
        convertida += chr (25)
        i += len (_('RESET'))
      elif cadena[i + 1:i + len (_('TAB')) + 2] == (_('TAB') + '_') and id_plataforma == 'ZX':
        columna = cadena[i + len (_('TAB')) + 2:i + len (_('TAB')) + 4]
        try:
          columna     = int (columna, 16)
          convertida += chr (23) + chr (columna)
        except:
          pass
        i += len (_('TAB')) + 3
      elif cadena[i + 1:i + 2] == 'x':  # Códigos escritos en hexadecimal
        try:
          codigo = int (cadena[i + 2: i + 4], 16)
        except:
          codigo = 0
        convertida += chr (codigo)
        i += 3
      else:
        convertida += c
      # TODO: interpretar el resto de secuencias escapadas con barra invertida (\)
    elif c in conversion_inv:
      convertida += conversion_inv[c]
    else:
      if inversa and id_plataforma in ('Atari800', 'PC'):
        convertida += chr (o + 128)
      else:
        convertida += c
    i += 1
  return convertida

def lee_secs_ctrl (cadena):
  """Devuelve la cadena dada convirtiendo las secuencias de control en una representación imprimible"""
  convertida = ''
  inversa    = False  # Texto en inversa bajo plataforma PC
  i = 0
  while i < len (cadena):
    c = cadena[i]
    o = ord (c)
    if o > 127 and id_plataforma in ('Atari800', 'PC'):
      if not inversa:
        convertida += '\\' + _('INVERSE') + '_01'
      inversa = True
      c = chr (o - 128)
    elif id_plataforma in ('Atari800', 'PC'):
      if inversa:
        convertida += '\\' + _('INVERSE') + '_00'
      inversa = False
    if c == '\n':
      convertida += '\\n'
    elif o == 6 and id_plataforma == 'ZX':  # Tabulador
      convertida += '\\t'
    elif id_plataforma == 'CPC' and o in range (1, 9):
      if o < 5:
        convertida += '\\' + _('INK') + '_%02X' % (o - 1)
      else:
        convertida += '\\' + _('PAPER') + '_%02X' % (o - 5)
    elif o == 9 and id_plataforma == 'CPC':
      convertida += '\\' + _('INVERSE') + ('_00' if inversa else '_01')
      inversa     = not inversa
    elif id_plataforma == 'QL' and o in range (16, 26):
      convertida += '\\'
      if o < 24:
        if (i + 1) < len (cadena):
          if ord (cadena [i + 1]) == 24:
            convertida += _('PAPER')
            i += 1  # El siguiente carácter ya se ha procesado
          else:
            convertida += _('INK')
          convertida += '_%02X' % (o - 16)
      elif o == 24:
        convertida += _('INVERSE') + '_01'
      else:  # o == 25
        convertida += _('RESET')
    elif id_plataforma == 'ZX' and o in range (16, 22) and (i + 1) < len (cadena):
      convertida += '\\'
      if o == 16:
        convertida += _('INK')
      elif o == 17:
        convertida += _('PAPER')
      elif o == 18:
        convertida += _('FLASH')
      elif o == 19:
        convertida += _('BRIGHT')
      elif o == 20:
        convertida += _('INVERSE')
      else:  # o == 21
        convertida += _('OVER')
      convertida += '_%02X' % ord (cadena[i + 1])
      i += 1  # El siguiente carácter ya se ha procesado
    elif o in (18, 146) and id_plataforma == 'C64':  # Cambio de inversa
      convertida += '\\' + _('INVERSE') + '_0' + ('1' if o == 18 else '0')
    elif o == 23 and id_plataforma == 'ZX':  # Salto a columna en la misma fila
      convertida += '\\' + _('TAB') + '_%02X' % ord (cadena[i + 1])
      i += 2  # El siguiente carácter ya se ha procesado y el de después se ignora
    elif o in cods_tinta:
      convertida += '\\' + _('INK') + '_%02X' % cods_tinta[o]
    elif c == '\\':
      convertida += '\\\\'
    elif c in conversion:
      convertida += conversion[c]
    else:
      convertida += c
    i += 1
  if inversa:
    convertida += '\\' + _('INVERSE') + '_00'
  return convertida

def nueva_bd ():
  """Crea una nueva base de datos de The Quill (versión de Spectrum)"""
  global max_llevables
  # Vaciamos los datos pertinentes de la base de datos que hubiese cargada anteriormente
  del colores_inicio[:]
  del conexiones[:]
  del desc_locs[:]
  del desc_objs[:]
  del locs_iniciales[:]
  del msgs_sys[:]
  del msgs_usr[:]
  del nombres_objs[:]
  del tablas_proceso[:]
  del vocabulario[:]
  # Asignamos colores de inicio y número máximo de objetos llevables
  colores_inicio.extend ((4, 0, 0, 0))  # Tinta verde, papel y borde negro, y sin brillo
  max_llevables = 4
  # Creamos la localidad 0
  desc_locs.append  (_("Location 0's description, the initial location."))
  conexiones.append ([])  # Ninguna conexión en esta localidad
  # Creamos el vocabulario
  vocabulario.append((_('n'),    1,   0))  # 0 es el tipo de palabra
  vocabulario.append((_('nort'), 1,   0))
  vocabulario.append((_('s'),    2,   0))
  vocabulario.append((_('sout'), 2,   0))
  vocabulario.append((_('e'),    3,   0))
  vocabulario.append((_('east'), 3,   0))
  vocabulario.append((_('w'),    4,   0))
  vocabulario.append((_('west'), 4,   0))
  vocabulario.append((_('i'),    13,  0))
  vocabulario.append((_('inve'), 13,  0))
  vocabulario.append((_('desc'), 14,  0))
  vocabulario.append((_('look'), 14,  0))
  vocabulario.append((_('quit'), 15,  0))
  vocabulario.append((_('ligh'), 100, 0))
  # Creamos el objeto 0
  desc_objs.append      (_("Object 0's description, source of light."))
  locs_iniciales.append (ids_locs['NO_CREADOS'])
  nombres_objs.append   ((100, 255))
  num_objetos[0] = 1
  # Creamos el mensaje de usuario 0
  msgs_usr.append (_('Text of message 0.'))
  # Ponemos los mensajes de sistema predefinidos
  for mensaje in nuevos_sys:
    msgs_sys.append (mensaje)
  # Creamos la tabla de eventos y la de estado
  tablas_proceso.append (([[(13, 255), (14, 255), (15, 255)], [
    [(100, (), )],           # INVE *: INVEN
    [(101, (), )],           # MIRA *: DESC
    [(102, ()), (103, ())],  # FIN  *: QUIT END
  ]]))
  tablas_proceso.append (([[], []]))


# Funciones auxiliares que sólo se usan en este módulo

def actualizaAcciones (nuevasAcciones):
  """Actualiza los diccionarios de acciones y condactos quitando las acciones anteriores y poniendo las de la plataforma actual"""
  acciones.clear()
  acciones.update (acciones_comun)
  if id_plataforma in acciones_plataforma and nuevasAcciones:
    acciones.update (acciones_plataforma[id_plataforma])
  # Quitamos todas las acciones que hubiese en condactos y ponemos ahí las recién preparadas
  for codigo in list (condactos.keys()):
    if codigo > 99:
      del condactos[codigo]
  for codigo in acciones:
    condactos[100 + codigo] = acciones[codigo][:2] + (True, acciones[codigo][2])

def anyadeArea (rangoInicio, rangoFin, areas):
  # type: (int, int, List[List[int, int]]) -> None
  """Añade un área de rango dado a la lista de áreas ordenadas del fichero dada, ordenadamente y extendiendo o integrando áreas contiguas. El rango dado no debe solapar ninguna otra área"""
  for a in range (len (areas)):
    posInicio, posFin = areas[a]
    if posFin < rangoInicio:
      continue
    if posFin == rangoInicio:
      if a + 1 < len (areas) and areas[a + 1][0] == rangoFin:  # Este rango cubre el hueco entre el área anterior y la posterior
        areas[a][1] = areas[a + 1][1]
        del areas[a + 1]
        return
      areas[a][1] = rangoFin
      return
    if posInicio == rangoFin:
      areas[a][0] = rangoInicio
      return
    areas.insert (a, [rangoInicio, rangoFin])
    return
  areas.append ([rangoInicio, rangoFin])

def buscaSecuenciasEnAreas (arbolSecuencias, areas, secuencias, inicioFich):
  # type: (Dict[str, list[Dict[str, list], Optional[int]]], List[List[int, int]], Dict[int, Sequence[int]], int) -> Dict[int, int]
  """Busca las secuencias de valores de byte del árbol "trie" dado a partir de la posición inicioFich del fichero, entre las áreas ordenadas del fichero dadas, tomando la longitud de las secuencias desde el diccionario secuencias dado, indexado por posición donde se guardará su desplazamiento. Devuelve un diccionario con clave los valores de las hojas de las secuencias encontradas, y como valor la primera posición donde se ha encontrado en las áreas del fichero"""
  secuenciasEnAreas = {}
  for posicion, posSecuencias in busca_secuencias (arbolSecuencias, inicioFich).items():
    for posSecuencia in posSecuencias:
      for posInicio, posFin in areas:
        if posFin <= posSecuencia:
          continue
        if posInicio > posSecuencia or posSecuencia + len (secuencias[posicion]) > posFin:
          break  # No está la secuencia ahí o no está completa
        secuenciasEnAreas[posicion] = posSecuencia
        break
      if posicion in secuenciasEnAreas:
        break
  return secuenciasEnAreas

def cargaBD (fichero, longitud, nuevasAcciones = True):
  """Carga la base de datos entera desde el fichero de entrada

Para compatibilidad con el IDE:
- Recibe como primer parámetro un fichero abierto
- Recibe como segundo parámetro la longitud del fichero abierto
- Devuelve False si ha ocurrido algún error"""
  global fich_ent, max_llevables
  preparaConversion()
  fich_ent = fichero
  bajo_nivel_cambia_ent (fichero)
  try:
    max_llevables  = carga_int1 (CAB_MAX_LLEVABLES)
    num_objetos[0] = carga_int1 (CAB_NUM_OBJS)
    cargaCadenas (CAB_NUM_LOCS,     CAB_POS_LST_POS_LOCS,     desc_locs)
    cargaCadenas (CAB_NUM_OBJS,     CAB_POS_LST_POS_OBJS,     desc_objs)
    cargaCadenas (CAB_NUM_MSGS_USR, CAB_POS_LST_POS_MSGS_USR, msgs_usr)
    if pos_msgs_sys:
      cargaMensajesSistema()
    else:
      cargaCadenas (CAB_NUM_MSGS_SYS, CAB_POS_LST_POS_MSGS_SYS, msgs_sys)
    cargaConexiones()
    cargaLocalidadesObjetos()
    cargaNombresObjetos()
    cargaVocabulario()
    actualizaAcciones (nuevasAcciones)  # Ponemos las acciones correctas para esta plataforma
    cargaTablasProcesos()
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
  convertir      = 'NOMBRE_GUI' in globals() and NOMBRE_GUI != 'pygame'  # Si debe decodificar los caracteres según conversion
  saltaSiguiente = False  # Si salta el siguiente carácter, como ocurre tras algunos códigos de control
  for posicion in posiciones:
    fich_ent.seek (posicion)
    cadena = []
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if saltaSiguiente or (id_plataforma == 'ZX' and caracter in (range (16, 22))):  # Códigos de control de Spectrum ZX
        cadena.append (chr (caracter))
        saltaSiguiente = not saltaSiguiente
      elif caracter == nueva_linea:  # Un carácter de nueva línea en la cadena
        cadena.append ('\n')
      elif convertir and chr (caracter) in conversion:
        cadena.append (conversion[chr (caracter)])
      else:
        cadena.append (chr (caracter))
    if id_plataforma == 'C64':
      cadenas.append (''.join (cadena).translate (petscii_a_ascii))
    else:
      cadenas.append (''.join (cadena))

def cargaConexiones ():
  """Carga las conexiones"""
  # Cargamos el número de localidades
  numLocs = carga_int1 (CAB_NUM_LOCS)
  # Vamos a la posición de la lista de posiciones de las conexiones
  fich_ent.seek (carga_desplazamiento (CAB_POS_LST_POS_CNXS))
  # Cargamos las posiciones de las conexiones de cada localidad
  posiciones = []
  for i in range (numLocs):
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
  # Vamos a la posición de las localidades de los objetos
  fich_ent.seek (carga_desplazamiento (CAB_POS_LOCS_OBJS))
  # Cargamos la localidad de cada objeto
  for i in range (num_objetos[0]):
    locs_iniciales.append (carga_int1())

def cargaNombresObjetos ():
  """Carga o rellena los nombres y adjetivos de los objetos"""
  # No hay nombres de objetos en Atari 800, C64, PC, ni versiones de Quill con posiciones fijas de mensajes de sistema
  if pos_msgs_sys or id_plataforma in ('Atari800', 'C64', 'PC'):
    for i in range (num_objetos[0]):
      nombres_objs.append ((255, 255))
    return
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
    cadena = ''
    ceros  = 0  # Cuenta del número de ceros consecutivos al inicio de la cadena
    while True:
      caracter = carga_int1() ^ 255
      if caracter == fin_cadena:  # Fin de esta cadena
        break
      if saltaSiguiente or (id_plataforma == 'ZX' and caracter in (range (16, 22))):  # Códigos de control de Spectrum ZX
        cadena += chr (caracter)
        saltaSiguiente = not saltaSiguiente
        continue
      if caracter == 255 and not cadena:
        ceros += 1
        if ceros > 20:  # Consideramos esto como marca de fin de mensajes de sistema
          return
      elif caracter == nueva_linea:  # Un carácter de nueva línea en la cadena
        cadena += '\n'
      else:
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
      condactoFlujo = False  # Si hay alguna acción en la entrada que cambia el flujo incondicionalmente
      entrada       = []
      for listaCondactos in (condiciones, acciones):
        while True:
          numCondacto = carga_int1()
          if numCondacto == 255:  # Fin de esta entrada
            break
          if numCondacto not in listaCondactos:
            if condactoFlujo:
              break  # Dejamos de obtener acciones para esta entrada
            try:
              muestraFallo ('Condacto desconocido', 'Número de ' + ('condición' if listaCondactos == condiciones else 'acción') + ' ' + str (numCondacto) + ' desconocida, en entrada ' + str (numEntrada) + ' de la tabla de ' + ('estado' if numProceso else 'eventos'))
            except:
              prn ('FIXME: Número de', 'condición' if listaCondactos == condiciones else 'acción', numCondacto, 'desconocida, en entrada', numEntrada, 'de la tabla de', 'estado' if numProceso else 'eventos', file = sys.stderr)
          elif not condactoFlujo and listaCondactos == acciones and acciones[numCondacto][2]:
            condactoFlujo = True
          parametros = []
          for i in range (len (listaCondactos[numCondacto][1])):
            parametros.append (carga_int1())
          if listaCondactos == acciones:
            entrada.append ((numCondacto + 100, parametros))
          else:
            entrada.append ((numCondacto, parametros))
          if nada_tras_flujo and condactoFlujo:
            break  # Dejamos de obtener condactos para esta entrada
      entradas.append (entrada)
    if len (cabeceras) != len (entradas):
      prn ('ERROR: Número distinto de cabeceras y entradas para la tabla de ' + ('estado' if numProceso else 'eventos'), file = sys.stderr)
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
    palabra = ''.join (palabra).rstrip()  # Quill guarda las palabras de menos de cuatro letras con espacios al final
    if id_plataforma == 'C64':
      palabra = palabra.translate (petscii_a_ascii)
    # Quill guarda las palabras en mayúsculas
    vocabulario.append ((palabra.lower(), carga_int1(), 0))

def convierteCondacto (codigoCondacto, nombreCondacto, parametros, plataforma, posicionOcurrencia):
  """Devuelve el código, nombre y parámetros convertidos del condacto dado con los parámetros dados y en la plataforma de destino dada, anotando en el diccionario adaptados las ocurrencias de cambios realizados. Las ocurrencias serán una cuenta para los cambios no importantes, y la lista de posiciones donde están para los importantes. Devuelve None y el mensaje de error si la plataforma de destino no tiene ese condacto y no se ha podido reemplazar por otro"""
  global condactos_destino
  try:
    condactos_destino
  except:
    condactos_destino = {}
  if plataforma not in condactos_destino:
    # Preparamos diccionario de condactos en la plataforma de destino indexados por nombre
    condactos_destino[plataforma] = {}
    for codigo in condiciones:
      condactos_destino[plataforma][condiciones[codigo][0]] = (codigo, ) + condiciones[codigo][1:]
    for diccAcciones in (acciones_comun, acciones_plataforma[plataforma]):
      for codigo in diccAcciones:
        condactos_destino[plataforma][diccAcciones[codigo][0]] = (100 + codigo, ) + diccAcciones[codigo][1:2] + (True, diccAcciones[codigo][2])
    # import pprint
    # pprint.pprint (sorted (condactos_destino[plataforma].items(), key = lambda item: item[1][0]))

  if nombreCondacto not in condactos_destino[plataforma]:  # Ese condacto no está en la plataforma de destino
    if len (condactos[codigoCondacto][1]) == 0 and 'ANYKEY' in condactos_destino[plataforma]:
      condactoDestino = condactos_destino[plataforma]['ANYKEY'][0]  # No tiene parámetros, intentamos cambiarlo por ANYKEY
      reemplazo     = 'ANYKEY'
    elif len (condactos[codigoCondacto][1]) == 1 and 'PAUSE' in condactos_destino[plataforma]:
      condactoDestino = condactos_destino[plataforma]['PAUSE'][0]  # Tiene un solo parámetro, intentamos cambiarlo por PAUSE
      reemplazo     = 'PAUSE'
    else:
      return None, _("Export failed because condact %(name)s doesn't exist on target platform %(platform)s") % {'name': nombreCondacto, 'platform': plataformas[plataforma]}, None
  else:
    condactoDestino = condactos_destino[plataforma][nombreCondacto][0]  # Código del condacto en la plataforma de destino
    reemplazo       = None

  if condactoDestino != codigoCondacto or reemplazo:
    if nombreCondacto not in adaptados:
      adaptados[nombreCondacto] = {}
    if reemplazo:
      mensaje = _('Inexistent condact %(name)s on %(platform)s, replaced by %(replacement)s')
      if mensaje not in adaptados[nombreCondacto]:
        adaptados[nombreCondacto][mensaje] = [{'name': nombreCondacto, 'platform': plataformas[plataforma], 'replacement': reemplazo}, []]
      if posicionOcurrencia not in adaptados[nombreCondacto][mensaje][1]:
        adaptados[nombreCondacto][mensaje][1].append (posicionOcurrencia)
      return condactoDestino, reemplazo, parametros
    mensaje = _('Condact %(name)s changed from code %(origCode)d to %(destCode)d')
    if mensaje in adaptados[nombreCondacto]:
      adaptados[nombreCondacto][mensaje][1] += 1  # Incrementamos el número de ocurrencias
    else:
      adaptados[nombreCondacto][mensaje] = [{'destCode': condactoDestino % 100, 'name': nombreCondacto, 'origCode': codigoCondacto % 100}, 1]

  numParametrosDest = len (condactos_destino[plataforma][nombreCondacto][1])
  numParametrosOrig = len (condactos[codigoCondacto][1])
  if numParametrosDest == numParametrosOrig:
    return condactoDestino, nombreCondacto, parametros
  if nombreCondacto not in adaptados:
    adaptados[nombreCondacto] = {}
  mensaje = _('Number of parameters for condact %(name)s changed from %(lenBefore)d to %(lenAfter)d')
  if mensaje not in adaptados[nombreCondacto]:
    adaptados[nombreCondacto][mensaje] = [{'lenAfter': numParametrosDest, 'lenBefore': numParametrosOrig, 'name': nombreCondacto}, []]
  if posicionOcurrencia not in adaptados[nombreCondacto][mensaje][1]:
    adaptados[nombreCondacto][mensaje][1].append (posicionOcurrencia)
  if numParametrosDest > numParametrosOrig:  # Tendrá más parámetros que antes
    return condactoDestino, nombreCondacto, parametros + ([0] * (numParametrosDest - numParametrosOrig))
  # Tendrá menos parámetros que antes
  return condactoDestino, nombreCondacto, parametros[:numParametrosDest]

def daCadena (cadena, finCadena, nuevaLinea, conversion = None, diccConversion = {}):
  """Devuelve una cadena en el formato de Quill"""
  if conversion:
    cadena = cadena.translate (conversion)
  resultado = []
  for caracter in cadena:
    if caracter == '\n':
      caracter = nuevaLinea
    elif caracter in diccConversion:
      caracter = diccConversion[caracter]
    else:
      caracter = ord (caracter)
    resultado.append (caracter ^ 255)
  resultado.append (finCadena ^ 255)  # Fin de cadena
  return resultado

def daVocabulario (conversion = None):
  """Devuelve la sección de vocabulario en el formato de Quill, pero optimizado"""
  resultado = []
  for palabra in vocabulario:
    if palabra == ('*', 255, 0):
      continue
    # Rellenamos el texto de la palabra con espacios al final
    cadena = palabra[0].upper()
    if conversion:
      cadena = cadena.translate (conversion)
    cadena = cadena.ljust (LONGITUD_PAL)
    for caracter in cadena:
      caracter = ord (caracter)
      resultado.append (caracter ^ 255)
    resultado.append (palabra[1])  # Código de la palabra
  resultado.append (0)  # Fin del vocabulario
  return resultado

def guardaCadena (cadena, finCadena, nuevaLinea, conversion = None, diccConversion = {}):
  """Guarda una cadena en el formato de Quill"""
  if conversion:
    cadena = cadena.translate (conversion)
  for caracter in cadena:
    if caracter == '\n':
      caracter = nuevaLinea
    elif caracter in diccConversion:
      caracter = diccConversion[caracter]
    else:
      caracter = ord (caracter)
    guarda_int1 (caracter ^ 255)
  guarda_int1 (finCadena ^ 255)  # Fin de cadena

def guardaMsgs (msgs, finCadena, nuevaLinea, conversion = None, diccConversion = {}):
  """Guarda una sección de mensajes sobre el fichero de salida, y devuelve cuántos bytes ocupa la sección"""
  ocupado = 0
  for mensaje in msgs:
    guardaCadena (mensaje, finCadena, nuevaLinea, conversion, diccConversion)
    ocupado += len (mensaje) + 1
  return ocupado

def guardaPosMsgs (msgs, pos):
  """Guarda una sección de posiciones de mensajes sobre el fichero de salida, y devuelve cuántos bytes en total ocupan estos mensajes

  msgs es la lista de mensajes que guardar
  pos es la posición donde se guardará el primer mensaje"""
  ocupado = 0
  for i in range (len (msgs)):
    guarda_desplazamiento (pos + ocupado)
    ocupado += len (msgs[i]) + 1
  return ocupado

def guardaVocabulario (conversion = None, optimizado = True):
  """Guarda la sección de vocabulario sobre el fichero de salida"""
  listaVocabulario = list (vocabulario)
  if not optimizado and ('*', 255, 0) not in vocabulario:
    listaVocabulario.append (('*', 255, 0))
  for palabra in listaVocabulario:
    # Rellenamos el texto de la palabra con espacios al final
    cadena = palabra[0].upper()
    if conversion:
      cadena = cadena.translate (conversion)
    cadena = cadena.ljust (LONGITUD_PAL)
    for caracter in cadena:
      caracter = ord (caracter)
      guarda_int1 (caracter ^ 255)
    guarda_int1 (palabra[1])  # Código de la palabra
  guarda_int1 (0)  # Fin del vocabulario

def preparaConversion ():
  """Prepara los diccionarios conversion y conversion_inv con las tablas de conversión de caracteres para la plataforma actual"""
  conversion.clear()
  conversion_inv.clear()
  if id_plataforma in conversion_plataforma:
    conversion.update (conversion_plataforma[id_plataforma])
    for entrada, salida in conversion.items():
      for caracter in salida:
        conversion_inv[caracter] = entrada
      conversion[entrada] = salida[0]

def preparaPosCabecera (formato, inicio):
  # type: (str, int) -> None
  """Asigna las "constantes" de desplazamientos (offsets/posiciones) en la cabecera"""
  global CAB_MAX_LLEVABLES, CAB_NUM_OBJS, CAB_NUM_LOCS, CAB_NUM_MSGS_USR, CAB_NUM_MSGS_SYS, CAB_POS_EVENTOS, CAB_POS_ESTADO, CAB_POS_LST_POS_OBJS, CAB_POS_LST_POS_LOCS, CAB_POS_LST_POS_MSGS_USR, CAB_POS_LST_POS_MSGS_SYS, CAB_POS_LST_POS_CNXS, CAB_POS_VOCAB, CAB_POS_LOCS_OBJS, CAB_POS_NOMS_OBJS
  CAB_MAX_LLEVABLES = inicio + 0  # Número máximo de objetos llevables
  CAB_NUM_OBJS      = inicio + 1  # Número de objetos
  CAB_NUM_LOCS      = inicio + 2  # Número de localidades
  CAB_NUM_MSGS_USR  = inicio + 3  # Número de mensajes de usuario
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
  elif formato in ('a800', 'c64', 'cpc', 'pc', 'sna48k'):
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
