# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funciones para compatibilidad con Python 2.X y 3.X
# Copyright (C) 2010, 2021, 2024 José Manuel Ferrer Ortiz
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

# La versión de Python será al menos la 2.0 (es la versión que introdujo la
# tupla version_info del módulo sys)

import gettext  # Para localización
import os
import string
from sys import version_info


# Preparativos para la localización de textos

def traduceConGettext (cadena, quitarAnd = False):
  """Devuelve la traducción de la cadena al idioma del usuario, opcionalmente quitando del resultado el símbolo '&'"""
  traducida = gettext.gettext (cadena)
  if quitarAnd:
    traducida = traducida.replace ('&', '')
  if version_info[0] < 3:
    return unicode (traducida.decode ('utf8'))
  return traducida

if os.name == 'nt':
  import locale
  if not os.getenv ('LANG') and not os.getenv ('LANGUAGE'):
    idioma, codificacion   = locale.getdefaultlocale()
    os.environ['LANG']     = idioma
    os.environ['LANGUAGE'] = idioma

gettext.bindtextdomain ('naps', os.path.join (os.path.abspath (os.path.dirname (__file__)), 'locale'))
gettext.textdomain ('naps')
_ = traduceConGettext


# Con try... except SyntaxError hacemos que el código pueda ser visto correcto
# por el analizador sintáctico independientemente de la versión de Python

if version_info[0] < 3:
  # La versión de Python es 2.X
  maketrans = string.maketrans
  if version_info[1] < 6:
    # La versión de Python es menor que la 2.6
    try:
      from prn_2 import prn
    except SyntaxError:
      pass
  else:
    # La versión de Python es mayor que la 2.5
    try:
      from prn_26 import prn
    except SyntaxError:
      pass
else:
  # La versión de Python es 3.X
  maketrans = str.maketrans
  raw_input = input
  try:
    from prn_3 import prn
  except SyntaxError:
    pass
