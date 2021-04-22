# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Función sustituta de print, compatible con Python 2.X y 3.X
# Copyright (C) 2010 José Manuel Ferrer Ortiz
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

from sys import version_info


# Con try... except SyntaxError hacemos que el código pueda ser visto correcto
# por el analizador sintáctico independientemente de la versión de Python

if version_info[0] < 3:
  # La versión de Python es 2.X
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
  try:
    from prn_3 import prn
  except SyntaxError:
    pass
