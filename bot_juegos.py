# -*- coding: utf-8 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Lista de juegos disponibles para la ejecución con el bot de Telegram
# Copyright (C) 2023 José Manuel Ferrer Ortiz
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

# El formato es el siguiente:
# Título del juego : [ruta a la carpeta/BD del juego, [parámetros para el intérprete]]
juegos = {
  'Aventura original': ['orig'],
  'Hampstead':         ['hampstead.sna', ['-c32']],
}
