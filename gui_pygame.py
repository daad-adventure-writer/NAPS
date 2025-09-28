# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gr�fica de usuario (GUI) con PyGame para el int�rprete PAW-like
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

from os       import environ, name, path
from prn_func import *
from sys      import stderr, stdout, version_info

import math    # Para ceil y log10
import string  # Para algunas constantes

import graficos_bitmap
import pygame

if version_info[0] == 3 and version_info[1] >= 5:  # Para Python 3.5+
  from typing import *  # Para que PyCharm reconozca BinaryIO, Dict, Optional y Union


traza = False  # Si queremos una traza del funcionamiento del m�dulo
if traza:
  from prn_func import prn

izquierda  = '���������������� !"�$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\r\t\n'
noEnFuente = {'�': 'c', u'\u2192': '>', u'\u2190': '<'}  # Tabla de conversi�n de caracteres que no est�n en la fuente

# Pares de c�digos ASCII para teclas pulsadas
mapeo_unicode    = {}  # Asociaci�n de scan codes con c�digos de caracteres iso-8859-15
teclas_ascii     = {pygame.K_DOWN: (0, 80), pygame.K_LEFT: (0, 75), pygame.K_RIGHT: (0, 77), pygame.K_UP: (0, 72)}
teclas_ascii_inv = {27: pygame.K_ESCAPE, 71: pygame.K_HOME, 72: pygame.K_UP, 75: pygame.K_LEFT, 77: pygame.K_RIGHT, 79: pygame.K_END, 80: pygame.K_DOWN}
# Teclas que procesar como unicode
teclas_unicode = '�������������ܺ*+-?@[\\]_{}~'
# Teclas imprimibles y de edici�n, con c�digo < 256
teclas_edicion = string.printable + string.punctuation + teclas_unicode + '\b\x1b'
# Teclas de edici�n con c�digo >= 256
# 314 es Alt Gr + ` (es decir, '[' en el teclado espa�ol) FIXME: pero tambi�n es Alt Gr + acento, que deber�a ser '{' en el teclado espa�ol
teclas_mas_256 = (314, pygame.K_DELETE, pygame.K_DOWN, pygame.K_END, pygame.K_HOME, pygame.K_KP_ENTER, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
# Teclas imprimibles del teclado num�rico
teclas_kp = {pygame.K_KP0: '0', pygame.K_KP1: '1', pygame.K_KP2: '2', pygame.K_KP3: '3', pygame.K_KP4: '4', pygame.K_KP5: '5', pygame.K_KP6: '6', pygame.K_KP7: '7', pygame.K_KP8: '8', pygame.K_KP9: '9', pygame.K_KP_DIVIDE: '/', pygame.K_KP_MULTIPLY: '*', pygame.K_KP_MINUS: '-', pygame.K_KP_PLUS: '+', pygame.K_KP_PERIOD: '.'}
# Teclas que al pulsar Alt Gr son otra
teclas_alt_gr = {'�': '\\', '1': '|', '2': '@', '4': '~', '7': '{', '8': '[', '9': ']', '0': '}', '+': ']', '�': '~', '�': '}', 'z': '�', 'x': '�'}
# Teclas que al pulsar Shift son otra
teclas_shift = {'�': '�', '1': '!', '2': '"', '4': '$', '5': '%', '6': '&', '7': '/', '8': '(', '9': ')', '0': '=', "'": '?', '�': '�', '+': '*', '�': '�', '�': '�', '<': '>', ',': ';', '.': ':', '-': '_'}


if name == 'nt':
  environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()  # Necesario para trabajar con la librer�a PyGame
pygame.event.set_blocked (pygame.MOUSEMOTION)  # No atenderemos los movimientos del rat�n
escalada      = None
factor_escala = 1  # Factor de escalado, de 1 a 9
forzar_escala = name == 'nt' and pygame.version.vernum < (1, 9, 5)  # Que escale aun con factor de escalado 1
ventana       = None

ancho_caracter = 6
fuente = pygame.image.load (path.dirname (path.realpath (__file__)) + path.sep + 'fuente.png')  # Fuente tipogr�fica seleccionada
fuente.set_palette (graficos_bitmap.paletaBN)
fuente_estandar = fuente
fuentes_zx      = []

cad_cursor = '_'
chr_cursor = pygame.Surface ((8, 8))  # Car�cter con transparencia, para marcar posici�n de input


# Variables que ajusta el int�rprete y usa esta GUI u otro m�dulo

brillo           = 0         # Sin brillo por defecto
cod_brillo       = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, dar� o quitar� brillo al color de tinta de la letra
cod_columna      = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, mover� el cursor a la columna dada
cod_flash        = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, pondr�a o quitar�a efecto flash a la letra
cod_inversa      = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, invertir� o no el papel/fondo de la letra
cod_inversa_fin  = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, quitar�  inversi�n del papel/fondo de la letra
cod_inversa_ini  = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, activar� inversi�n del papel/fondo de la letra
cod_juego_alto   = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, pasar� al juego de caracteres alto
cod_juego_bajo   = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, pasar� al juego de caracteres bajo
cod_papel        = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, cambiar� el color de papel/fondo de la letra
cod_reset        = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, aplicar� los colores de inicio para tinta y papel
cod_tabulador    = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, pondr� espacios hasta mitad o final de l�nea
cod_tinta        = None      # type: Optional[int]  # C�digo  de car�cter que si se encuentra  en una cadena, cambiar� el color de tinta de la letra
cods_tinta       = {}        # type: Dict[int, int] # C�digos de car�cter que si se encuentran en una cadena, cambiar� el color de tinta por el del valor
centrar_graficos = []        # Si se deben centrar los gr�ficos al dibujarlos
grf_borde        = None      # Cuadrado 8x8 que usar repetidamente como borde de los gr�ficos
paleta           = ([], [])  # Paleta de colores sin y con brillo para los textos, que cambia con funciones cambia_*
paleta_gfx       = []        # Paleta de colores para los gr�ficos
partir_espacio   = True      # Si se deben partir las l�neas en el �ltimo espacio
ruta_graficos    = ''        # Carpeta de donde cargar los gr�ficos a dibujar
texto_nuevo      = []        # Tendr� valor verdadero si se ha escrito texto nuevo tras el �ltimo borrado de pantalla o espera de tecla
todo_mayusculas  = False     # Si la entrada del jugador ser� incondicionalmente en may�sculas
txt_mas          = '(m�s)'   # Cadena a mostrar cuando no cabe m�s texto y se espera a que el jugador pulse una tecla
udgs             = []        # UDGs (caracteres gr�ficos definidos por el usuario)

banderas_antes   = None   # Valor anterior de las banderas
historial        = []     # Historial de �rdenes del jugador


# Variables propias de este m�dulo

banderas_viejas  = None   # Banderas que antes cambiaron de valor
graficos         = {}     # Gr�ficos ya cargados
historial_temp   = []     # Orden a medias, guardada al acceder al historial
locs_objs_antes  = None   # Valor anterior de las localidades de los objetos
locs_objs_viejas = None   # Localidades de los objetos que antes cambiaron de valor
tras_portada     = False  # Esperar pulsaci�n de tecla antes de borrar la portada
teclas_pulsadas  = []     # Lista de teclas actualmente pulsadas

# Todas las coordenadas son columna, fila
num_subvens = 8                # DAAD tiene 8 subventanas
elegida     = 1                # Subventana elegida (la predeterminada es la 1)
opcs_input  = 2                # Opciones para la entrada del usuario (TODO: revisar valor por defecto)
subv_input  = 0                # Subventana para entrada del usuario (0 indica la actual)
limite      = [53, 25]         # Ancho y alto m�ximos absolutos de cada subventana
color_subv  = [[7, 0, 0]] * 8  # Color de tinta, papel y borde de cada subventana
cursores    = [[0, 0]] * 8     # Posici�n relativa del cursor de cada subventana
cursores_at = [(0, 0)] * 8     # Posici�n relativa del cursor guardado mediante SAVEAT de cada subventana
lineas_mas  = [0] * 8          # L�neas impresas desde que se esper� tecla para cada subventana
pos_gfx_sub = [[0, 0]] * 8     # Posici�n guardada de dibujo de gr�ficos flotantes en cada subventana
subventanas = [[0, 0]] * 8     # Posici�n absoluta de cada subventana (de su esquina superior izquierda)
topes       = [[53, 25]] * 8   # Topes relativos de cada subventana de impresi�n
topes_gfx   = [53, 25]         # Ancho y alto del �ltimo gr�fico dibujado en la subventana 0
ancho_juego = 320              # Ancho de la ventana de juego
resolucion  = (320, 200)       # Resoluci�n gr�fica de salida, sin escalar
color_tinta = None             # Color de tinta por defecto
tintas_cpc  = []               # Colores disponibles para Amstrad CPC de entre los de su paleta


# Constantes que se exportan (fuera del paquete)

NOMBRE_GUI = 'pygame'


def abre_ventana (traza, escalar, bbdd):
  """Abre la ventana gr�fica de la aplicaci�n"""
  global ancho_juego, escalada, factor_escala, resolucion, ventana
  preparaConversion()
  if ide:
    if not ventana:
      ancho_juego = int (math.ceil ((limite[0] * ancho_caracter) / 8.)) * 8
      resolucion  = (ancho_juego, limite[1] * 8)  # Tama�o de la ventana de juego
      ventana     = pygame.Surface (resolucion)
    return
  copia    = None
  iniAntes = False  # Si ya hab�a sido inicializada antes
  if pygame.display.get_caption():  # Ya hab�a sido inicializada antes
    copia    = ventana.copy()
    iniAntes = True
  elif ruta_icono:
    try:
      icono = pygame.image.load (ruta_icono)
      pygame.display.set_icon (icono)
    except Exception as e:
      prn ('No se ha podido cargar la imagen para el icono:', ruta_icono)
      prn (e)
  if titulo_ventana:
    pygame.display.set_caption (titulo_ventana)
  else:
    rutaBD = path.abspath (bbdd)
    if len (path.relpath (bbdd)) < len (rutaBD):
      rutaBD = path.relpath (bbdd)
    pygame.display.set_caption ('NAPS - ' + rutaBD)
  ancho_juego = int (math.ceil ((limite[0] * ancho_caracter) / 8.)) * 8
  resolucion  = (ancho_juego, limite[1] * 8)  # Tama�o de la ventana de juego
  if traza and 'NUM_BANDERAS' in globals():  # A�adiremos espacio para las banderas
    if NUM_BANDERAS[0] > 140:  # Sistemas desde PAWS en adelante
      resolucion = (resolucion[0] + ((5 * 6) + 3) * 8 - 2, 32 * 8)
    elif NUM_BANDERAS[0] > 67:  # Sistema GAC
      resolucion = (resolucion[0] + ((5 * 6) + 3) * 5 - 2, 32 * 8)
    elif NUM_BANDERAS[0] == 67:  # Sistema Quill para Sinclair QL
      resolucion = (resolucion[0] + ((5 * 6) + 3) * (3 + int (math.ceil (float (num_objetos[0]) / limite[1]))), resolucion[1])
    else:  # Resto de sistemas Quill, con 33 banderas
      resolucion = (resolucion[0] + ((5 * 6) + 3) * (2 + int (math.ceil (float (num_objetos[0]) / limite[1]))), resolucion[1])
  if iniAntes:
    factor_escala = min (factor_escala, factorEscalaMaximo())
  elif escalar:
    factor_escala = min (escalar, factorEscalaMaximo())
  else:
    factor_escala = factorEscalaMaximo()
  if name != 'nt':
    environ['SDL_VIDEO_WINDOW_POS'] = str ((infoPantalla.current_w - (resolucion[0] * factor_escala)) // 2) + ',0'
  if factor_escala > 1 or forzar_escala:
    escalada = pygame.display.set_mode ((resolucion[0] * factor_escala, resolucion[1] * factor_escala), pygame.RESIZABLE)
    ventana  = pygame.Surface (resolucion)
  else:
    ventana = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
  if not iniAntes:
    try:
      pygame.scrap.init()
    except:
      pass
  if copia:  # Recuperamos contenido anterior
    ventana.blit (copia, (0, 0) + resolucion)
    actualizaVentana()
  return
  # FIXME: si no funciona el modo gr�fico, deja X Window mal permanentemente, a�n al cerrarse el int�rprete
  if escalar == 0:  # Pantalla completa
    ventana = pygame.display.set_mode ((640, 400), ventana.get_flags() ^ pygame.FULLSCREEN)

def actualizaVentana ():
  if ide:
    global rutaImgPantalla
    try:
      rutaImgPantalla
    except:
      rutaImgPantalla = path.join (path.dirname (path.realpath (__file__)), 'ventanaJuegoActual.bmp')
    # Esperamos hasta lograr guardar la imagen, dado que en Windows se bloquea el fichero al abrirlo el IDE
    guardada = False
    while not guardada:
      try:
        pygame.image.save (ventana, rutaImgPantalla)
        guardada = True
      except:
        continue
    prn ('img')
    stdout.flush()
    return
  if factor_escala > 1 or forzar_escala:
    pygame.transform.scale (ventana, (resolucion[0] * factor_escala, resolucion[1] * factor_escala), escalada)
  pygame.display.flip()

def redimensiona_ventana (evento = None, copiaVentana = None):
  """Maneja eventos en relaci�n a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  global escalada, factor_escala, ventana
  if not evento:
    if pygame.event.peek (pygame.VIDEORESIZE):  # Si ha ocurrido un evento de redimensi�n de ventana
      evento = pygame.event.get (pygame.VIDEORESIZE)[0]
    elif pygame.event.peek (pygame.QUIT):  # Si ha ocurrido un evento de cierre de ventana
      evento = pygame.event.get (pygame.QUIT)[0]
    else:
      return
  if evento.type == pygame.QUIT:
    import sys
    sys.exit()
  if evento.type != pygame.VIDEORESIZE:
    return
  cambiado = False  # Si el factor de escalado ha cambiado
  while factor_escala > 1 and (evento.w < (resolucion[0] * factor_escala) or evento.h < (resolucion[1] * factor_escala)):
    factor_escala -= 1
    cambiado       = True
  if not cambiado:
    factorMaximo = factorEscalaMaximo()
    while factor_escala < factorMaximo and (evento.w > (resolucion[0] * factor_escala) or evento.h > (resolucion[1] * factor_escala)):
      factor_escala += 1
  if factor_escala == 1:
    superficie = ventana.copy()
    ventana    = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
    while ventana.get_size() != resolucion:
      ventana = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
    ventana.blit (superficie, (0, 0) + resolucion)
  else:
    if copiaVentana:
      superficie = copiaVentana.copy()
    else:
      superficie = ventana.copy()
    ventana    = superficie
    resVentana = (resolucion[0] * factor_escala, resolucion[1] * factor_escala)
    escalada   = pygame.display.set_mode (resVentana, pygame.RESIZABLE)
    while escalada.get_size() != resVentana:
      escalada = pygame.display.set_mode (resVentana, pygame.RESIZABLE)
    pygame.transform.scale (ventana, resVentana, escalada)
  pygame.display.flip()


def borra_orden ():
  """Borra la entrada realimentada en pantalla en la subventana de entrada si es subventana propia, y recupera la subventana anterior"""
  if not subv_input:
    return
  global elegida
  # Guardamos la subventana que estaba elegida justo antes, y cambiamos a la de entrada
  subvAntes = elegida
  elegida   = subv_input
  borra_pantalla()
  elegida = subvAntes  # Recuperamos la subventana elegida

def borra_pantalla (desdeCursor = False, noRedibujar = False):
  """Limpia la subventana de impresi�n"""
  global tras_portada
  if tras_portada:
    espera_tecla()
    tras_portada = False
  if not desdeCursor:
    cursores[elegida]   = [0, 0]
    lineas_mas[elegida] = 0
  colorPapel = daColorPapel()
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if elegida == 0:
    tope = topes_gfx  # Borrar �nicamente ancho de la �ltima imagen dibujada all�
  inicioX = (subventana[0] + cursor[0]) * ancho_caracter  # Esquina superior izquierda X
  inicioY = (subventana[1] + cursor[1]) * 8               # Esquina superior izquierda Y
  if desdeCursor:
    ancho = (tope[0] * ancho_caracter) - inicioX  # Anchura del rect�ngulo a borrar
    alto  = 8                                     # Altura del rect�ngulo a borrar, luego se borrar� el resto si es m�s de una l�nea
  else:
    ancho = int (math.ceil ((tope[0] * ancho_caracter) / 8.)) * 8  # Anchura del rect�ngulo a borrar
    alto  = tope[1] * 8                                            # Altura del rect�ngulo a borrar
  ventana.fill (colorPapel, (inicioX, inicioY, ancho, alto))
  if desdeCursor and tope[1] - cursor[1] > 0:  # Borrado de las siguientes l�neas
    inicioX = subventana[0] * ancho_caracter       # Esquina superior izquierda X
    inicioY = (subventana[1] + cursor[1] + 1) * 8  # Esquina superior izquierda Y
    ancho   = tope[0] * ancho_caracter             # Anchura del rect�ngulo a borrar
    alto    = (tope[1] - cursor[1] - 1) * 8        # Altura del rect�ngulo a borrar
    ventana.fill (colorPapel, (inicioX, inicioY, ancho, alto))
  if not desdeCursor and not noRedibujar:
    actualizaVentana()
  if traza:
    prn ('Subventana', elegida, 'en', subventana, 'con topes', tope, 'limpiada y cursor en', cursores[elegida])

def borra_todo ():
  """Limpia la pantalla completa"""
  colorPapel = daColorPapel()
  ventana.fill (colorPapel, (0, 0, resolucion[0], resolucion[1]))
  actualizaVentana()

def cambia_color_borde (color):
  """Cambia el color de borde de la subventana actual por el de c�digo dado"""
  # TODO: revisar porque esto seguramente no deba ser por subventana, sino com�n a todas
  if traza:
    prn ('Color de borde cambiado a', color, 'en subventana', elegida)
  color_subv[elegida][2] = color % len (paleta[0])

def cambia_color_brillo (valor):
  """Cambia el valor de brillo de la subventana actual seg�n el valor dado"""
  global brillo
  brillo = 1 if valor else 0

def cambia_tintas_cpc (tintas):
  """Cambia las tintas de CPC por las dadas"""
  for c in range (len (tintas)):
    if len (tintas_cpc) < c + 1:
      tintas_cpc.append (tintas[c])
    else:
      tintas_cpc[c] = tintas[c]

def cambia_color_papel (color):
  """Cambia el color de papel/fondo al escribir la subventana actual por el dado"""
  if traza:
    prn ('Color de papel cambiado a', color, 'en subventana', elegida)
  color_subv[elegida][1] = color % len (paleta[0])

def cambia_color_tinta (color):
  """Cambia el color de tinta al escribir la subventana actual por el dado"""
  if traza:
    prn ('Color de tinta cambiado a', color, 'en subventana', elegida)
  color_subv[elegida][0] = color

def cambia_cursor (cadenaCursor):
  """Cambia el car�cter que marca la posici�n del cursor en la entrada del jugador"""
  global cad_cursor
  cad_cursor = cadenaCursor

def cambia_fuente (numFuente):
  """Cambia la fuente seleccionada por la de �ndice dado si es v�lido, de lo contrario no hace nada"""
  global fuente
  if numFuente >= len (fuentes_zx):
    return
  if traza:
    prn ('Fuente cambiada a la', numFuente)
  fuente = fuentes_zx[numFuente]
  elige_subventana (elegida)  # Para que se apliquen los colores actuales a la fuente

def cambia_subv_input (stream, opciones):
  """Cambia la subventana de entrada por el stream dado, con las opciones dadas, seg�n el condacto INPUT"""
  global subv_input, opcs_input
  subv_input = stream
  opcs_input = opciones

def cambia_topes (columna, fila):
  """Cambia los topes de la subventana de impresi�n elegida"""
  if not columna:
    columna = limite[0]
  if not fila:
    fila    = limite[1]
  topes[elegida] = [min (columna, limite[0] - subventanas[elegida][0]),
                    min (fila,    limite[1] - subventanas[elegida][1])]
  if traza:
    prn ('Subventana', elegida, 'en', subventanas[elegida],
         'con topes puestos a', topes[elegida], 'y cursor en',
         cursores[elegida])

def da_tecla_pulsada ():
  """Devuelve el par de c�digos ASCII de la tecla m�s recientemente pulsada si hay alguna tecla pulsada, o None si no hay ninguna pulsada"""
  if pygame.event.peek ((pygame.KEYDOWN, pygame.KEYUP)):
    for evento in pygame.event.get ((pygame.KEYDOWN, pygame.KEYUP)):
      if evento.type == pygame.KEYDOWN:
        if evento.key not in teclas_pulsadas:
          teclas_pulsadas.append (evento.key)
      else:  # evento.type == pygame.KEYUP
        if evento.key in teclas_pulsadas:
          teclas_pulsadas.remove (evento.key)
  redimensiona_ventana()
  if not teclas_pulsadas:
    return None
  tecla = teclas_pulsadas.pop()  # Tomamos la �ltima tecla pulsada y la quitamos de la lista
  if tecla in teclas_ascii:
    return teclas_ascii[tecla]
  return (tecla, 0)

def carga_bd_pics (rutaBDGfx):
  """Carga la base de datos gr�fica de ruta dada, y prepara la paleta y lo relacionado con ella. Devuelve un mensaje de error si falla"""
  global color_tinta
  extension = rutaBDGfx[rutaBDGfx.rfind ('.') + 1:]
  error     = graficos_bitmap.carga_bd_pics (rutaBDGfx)
  if error and not graficos_bitmap.recursos:
    return error
  if graficos_bitmap.modo_gfx == 'CGA':
    cambiaPaleta (graficos_bitmap.paleta1b)  # Dejamos cargada la paleta CGA 1 con brillo
  elif graficos_bitmap.modo_gfx == 'EGA':
    cambiaPaleta (graficos_bitmap.paletaEGA, False)  # Dejamos cargada la paleta EGA
  else:
    if len (paleta[0]) in (0, 8):  # Dejamos paleta de la portada si la hab�a
      carga_paleta_defecto()
    color_tinta = 1  # Ponemos este color de tinta por defecto
  if graficos_bitmap.recursos:
    precargaGraficos()

def carga_fuente_zx (fichero, posFuente = None):
  # type: (BinaryIO) -> None
  """Carga una fuente tipogr�fica de 8x8 de GAC, QUILL o PAWS desde el fichero abierto dado con snapshot de ZX Spectrum"""
  global ancho_caracter, fuente, izquierda
  if NOMBRE_SISTEMA not in ('GAC', 'QUILL', 'PAWS'):
    return
  ancho_caracter = 8
  izquierda      = '�' * 16 + ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_�abcdefghijklmnopqrstuvwxyz{|}~\x7f\r\t\n'
  for c, convertido in conversion.items():
    izquierda = izquierda.replace (c, convertido)
  fuente_zx = pygame.image.load (path.dirname (path.realpath (__file__)) + path.sep + 'fuente_zx_8x8.png')
  if posFuente != None:
    if posFuente == 0:
      fuente = fuente_zx
    else:
      imagen, palImg = graficos_bitmap.carga_fuente_zx_8 (fichero, posFuente)
      bufferImg = bytes (bytearray (imagen))
      fuente    = pygame.image.frombuffer (bufferImg, (628, 48), 'P')
  else:
    imagen, palImg = graficos_bitmap.carga_fuente_zx_8 (fichero)
    if not imagen:
      fuente = fuente_zx
      fuente.set_palette (graficos_bitmap.paletaBN)
      return
    bufferImg = bytes (bytearray (imagen))
    fuente    = pygame.image.frombuffer (bufferImg, (628, 48), 'P')
  fuente.set_palette (graficos_bitmap.paletaNB)
  # Copiamos caracteres de s�mbolos gr�ficos est�ndar (sobre las posiciones de la fuente 96 a la 111)
  fuente_zx.set_palette (graficos_bitmap.paletaNB)
  fuente.blit (fuente_zx, (330, 10), (330, 10, 160, 8))
  # Copiamos caracteres de gr�ficos definidos por el usuario si los hay (sobre las posiciones de la fuente de 112 en adelante)
  if udgs:
    bufferImg  = bytes (bytearray (udgs))
    anchoUDGs  = len (udgs) // 8
    numUDGs    = anchoUDGs  // 8
    imagenUDGs = pygame.image.frombuffer (bufferImg, (anchoUDGs, 8), 'P')
    imagenUDGs.set_palette (graficos_bitmap.paletaNB)
    for u in range (numUDGs):
      c = 112 + u  # N�mero de car�cter en la fuente
      fuente.blit (imagenUDGs, ((c % 63) * 10, (c // 63) * 10), (u * 8, 0, 8, 8))
  if posFuente != None:
    fuentes_zx.append (fuente)

def carga_paleta_defecto ():
  """Carga a la paleta por defecto para el modo gr�fico"""
  if graficos_bitmap.modo_gfx in graficos_bitmap.colores_por_defecto:
    cambiaPaleta (graficos_bitmap.colores_por_defecto[graficos_bitmap.modo_gfx], False)
  else:
    cambiaPaleta (graficos_bitmap.paletaEGA, False)  # Dejamos cargada la paleta EGA

def centra_subventana ():
  """Centra horizontalmente en la ventana la subventana elegida"""
  subventanas[elegida][0] = (limite[0] - topes[elegida][0]) // 2

# FIXME: Hay que dibujar s�lo la regi�n que no sale de los topes
def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gr�fico en la posici�n del cursor

El par�metro descripcion indica si se llama al describir la localidad
El par�metro parcial indica si es posible dibujar parte de la imagen"""
  global grf_borde
  if ruta_graficos:
    try:
      grafico = pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
    except Exception as e:
      if traza:
        prn ('Gr�fico', numero, 'inv�lido o no encontrado en:', ruta_graficos)
        prn (e)
      return  # No dibujamos nada
  elif graficos_bitmap.recursos:
    if numero not in graficos:
      if not graficos_bitmap.recursos[numero] or 'imagen' not in graficos_bitmap.recursos[numero]:
        if traza:
          if not graficos_bitmap.recursos[numero]:
            razon = 'no est� en la base de datos gr�fica'
          else:
            razon = 'ese recurso de la base de datos gr�fica no es una imagen, o est� corrupta'
          prn ('Gr�fico', numero, 'inv�lido,', razon)
        return  # No dibujamos nada
      cargaGrafico (numero)
    recurso = graficos[numero]
    grafico = recurso['grafico']
    if 'flotante' not in recurso['banderas']:
      cambiaPaleta (recurso['paleta'])
    grafico.set_palette (paleta_gfx)
  elif numero in graficos:
    grafico = graficos[numero]
    recurso = None
  else:
    return  # No dibujamos nada
  global tras_portada
  if tras_portada:
    borra_pantalla()
  tope = topes[elegida]
  if descripcion:
    if traza:
      prn ('Dibujo', numero, 'desde la descripci�n de la localidad, en (0, 0)')
  else:
    cursor     = cursores[elegida]
    subventana = subventanas[elegida]
    if traza:
      prn ('Dibujo', numero, 'sobre subventana', elegida, 'en', subventana,
           'con topes', tope, 'y cursor en', cursor)
  if elegida == 0:
    topes_gfx[0] = min (grafico.get_width()  // 6, limite[0])
    topes_gfx[1] = min (grafico.get_height() // 6, limite[1])
  if (descripcion or elegida == 0) and not parcial:
    ancho = tope[0] * 6
    if numero in graficos and recurso and 'flotante' not in recurso['banderas']:
      destino = recurso['posicion']
    elif centrar_graficos and ancho > grafico.get_width():  # Centramos el gr�fico
      # Se centran los gr�ficos en la Aventura Original, pero no en El Jabato, as� est� en la base de datos gr�fica
      destino      = ((ancho - grafico.get_width()) // 2, 0)
      topes_gfx[0] = min ((grafico.get_width() + (ancho - grafico.get_width()) // 2) // 6, limite[0])  # TODO: revisar si esto es correcto
    elif grf_borde:  # Dibujaremos un borde alrededor del gr�fico, de ancho m�ximo, a partir del gr�fico de 8x8 en grf_borde
      if type (grf_borde) != pygame.Surface:  # Preparamos el gr�fico de borde como superficie de pygame
        bufferImg = bytes (bytearray (grf_borde))
        grf_borde = pygame.image.frombuffer (bufferImg, (8, 8), 'P')
        grf_borde.set_palette (paleta[0])
      destino  = [0, 0]
      numFilas = 2 + grafico.get_height() // 8  # N�mero de filas para el gr�fico contando el recuadro con el borde
      for fila in range (numFilas):
        if fila in (0, numFilas - 1):  # Repetiremos grf_borde durante toda la fila
          destino[0] = 0
          for columna in range (limite[0]):
            ventana.blit (grf_borde, (destino))
            destino[0] += 8
        else:  # Dibujamos grf_borde en la primera y �ltima columna
          ventana.blit (grf_borde, (0, destino[1]))
          ventana.blit (grf_borde, ((limite[0] * 8) - 8, destino[1]))
        destino[1] += 8
      destino = (8, 8)
    else:
      destino = (0, 0)
    ventana.blit (grafico, destino)
  else:
    ancho = ((tope[0] - cursor[0]) * 6)  # Anchura del dibujo
    alto  = ((tope[1] - cursor[1]) * 8)  # Altura del dibujo
    if numero in graficos:
      if nueva_version and elegida > 0 and not espacial:
        if 'flotante' not in recurso['banderas']:
          pos_gfx_sub[elegida] = recurso['posicion']  # Otros gr�ficos flotantes en esta subventana se dibujar�n aqu�
        destino = pos_gfx_sub[elegida]
      elif templos:
        # TODO: Probar esto m�s, ocurre as� con gr�ficos de localidad de Los Templos Sagrados, pero no en Chichen Itz�, ni sirve para Aventura Espacial
        ancho   = ((((tope[0] - cursor[0]) * 6) // 8) * 8)  # Anchura del dibujo
        destino = [(((subventana[0] + cursor[0]) * 6) // 8) * 8, (subventana[1] + cursor[1]) * 8]
      elif 'flotante' in recurso['banderas']:
        # TODO: Asegurarse de si hay que tener en cuenta la posici�n del cursor
        destino = [(subventana[0] + cursor[0]) * 6, (subventana[1] + cursor[1]) * 8]
      else:
        destino = recurso['posicion']
    else:
      # TODO: Asegurarse de si hay que tener en cuenta la posici�n del cursor
      destino = [(subventana[0] + cursor[0]) * 6, (subventana[1] + cursor[1]) * 8]
      if centrar_graficos and ancho > grafico.get_width():  # Centramos el gr�fico
        destino[0] += (ancho - grafico.get_width()) // 2
    # Los gr�ficos pueden dibujar hasta dos p�xeles m�s all� de la �ltima columna de texto
    if ancho < grafico.get_width() and subventana[0] + tope[0] == 53:
      ancho += max (2, grafico.get_width() - ancho)
    ventana.blit (grafico, destino, (0, 0, ancho, alto))
  actualizaVentana()
  # TODO: Ver si hay que actualizar la posici�n del cursor (puede que no)

def elige_parte (partes, graficos):
  """Obtiene del jugador el modo gr�fico a usar y a qu� parte jugar, y devuelve el nombre de la base de datos elegida"""
  global ancho_caracter, fuente, titulo_ventana, tras_portada
  portada = None
  for modoPortada, tinta in (('dat', 15), ('ega', 15), ('cga', 3)):
    if modoPortada in graficos and 0 in graficos[modoPortada]:
      try:
        fichero = open (graficos[modoPortada][0], 'rb')
        imagen, palImg = graficos_bitmap.carga_portada (fichero, 'ch0' in graficos)
        strImg = b''
        for fila in imagen if modoPortada == 'cga' else [imagen]:
          if version_info[0] > 2:
            for pixel in fila:
              strImg += bytes ([pixel])
          else:
            for pixel in fila:
              strImg += chr (pixel)
        portada = pygame.image.frombuffer (strImg, (320, 200), 'P')
        cambiaPaleta (palImg, False, True)
        portada.set_palette (paleta_gfx)
        break
      except Exception:
        portada = None  # No dibujaremos nada
      if 'fichero' in locals():
        fichero.close()
  if paleta[0]:
    if len (paleta[0]) == 8:
      tinta = 7
    else:
      tinta = 1  # Paleta cargada desde portada
  else:  # Cargamos una paleta m�nima para poder pedir qu� parte cargar
    cambiaPaleta (graficos_bitmap.paleta1b, False)
    tinta = 3
  color_subv[elegida][0] = tinta  # Color de tinta
  numerosPartes = tuple (partes.keys())
  numParteMenor = min (numerosPartes)
  numParteMayor = max (numerosPartes)
  entrada = list (partes.keys())[0] if len (partes) == 1 else None
  while entrada not in numerosPartes:
    borra_todo()
    if portada:
      ventana.blit (portada, (0, 0))
      ventana.fill (palImg[0], (11 * 8, 10 * 8, 19 * 8, 5 * 8))
    mueve_cursor (18, 11)
    imprime_cadena ('�Qu� parte quieres')
    mueve_cursor (21, 13)
    imprime_cadena ('cargar? (%d%s%d)' % (numParteMenor, '/' if (numParteMayor - numParteMenor == 1) else '-', numParteMayor))
    entrada = espera_tecla() - ord ('0')
  if titulo_ventana:
    if len (partes) > 1:
      titulo_ventana += ' - Parte ' + str (entrada)
    pygame.display.set_caption (titulo_ventana)
  else:
    rutaBD = path.abspath (partes[entrada])
    if len (path.relpath (partes[entrada])) < len (rutaBD):
      rutaBD = path.relpath (partes[entrada])
    pygame.display.set_caption ('NAPS - ' + rutaBD)
  if portada:
    ventana.blit (portada, (0, 0))
    actualizaVentana()
    tras_portada = True
    if entrada in graficos[modoPortada]:
      carga_bd_pics (graficos[modoPortada][entrada])
    elif 'dat' in graficos and entrada in graficos['dat']:
      carga_bd_pics (graficos['dat'][entrada])
  else:
    if tuple (paleta[0]) == graficos_bitmap.paleta1b:  # Es la paleta m�nima cargada para poder pedir qu� parte cargar
      del paleta[0][:]  # La quitamos para que se cargue la paleta correspondiente a los gr�ficos
    for modo in ('dat', 'ega', 'cga'):
      if modo in graficos and entrada in graficos[modo]:
        carga_bd_pics (graficos[modo][entrada])
        if graficos_bitmap.recursos:
          break
  # Cargamos la fuente tipogr�fica para esta parte si la hay
  if ('chr' in graficos and entrada in graficos['chr']) or ('ch0' in graficos and entrada in graficos['ch0']):
    if 'ch0' in graficos and entrada in graficos['ch0']:  # Cargamos preferentemente la fuente .ch0, porque en ST la chr es para alta resoluci�n
      fichero = open (graficos['ch0'][entrada], 'rb')
    else:
      fichero = open (graficos['chr'][entrada], 'rb')
    imagen, palImg = graficos_bitmap.carga_fuente (fichero)
    fichero.close()
    if len (imagen) > 23864:
      ancho_caracter = 8
    bufferImg = bytes (bytearray (imagen))
    fuente = pygame.image.frombuffer (bufferImg, (628, 48 if len (imagen) > 23864 else 38), 'P')
    fuente.set_palette (palImg)
  if not graficos_bitmap.recursos and 'pix' in graficos:
    precargaGraficosSWAN (graficos['pix'])
  return partes[entrada]

def elige_subventana (numero):
  """Selecciona la subventana dada y devuelve el n�mero de subventana anterior"""
  global elegida
  anterior = elegida
  elegida  = numero
  # Ponemos en la fuente los colores que ten�a la subventana elegida
  papel = color_subv[elegida][1]  # Color de papel/fondo
  tinta = daTinta()               # Color de tinta
  fuente.set_palette ((paleta[brillo][tinta], paleta[brillo][papel]))
  if traza:
    prn ('Subventana', elegida, 'elegida, en', subventanas[elegida],
         'con topes', topes[elegida], 'y cursor en', cursores[elegida])
  return anterior

def espera_tecla (tiempo = 0, numPasos = False):
  # type: (Optional[Union[float, int]], Optional[bool]) -> Optional[Union[int, str]]
  """Espera hasta que se pulse una tecla (modificadores no) y la devuelve, o hasta que pase tiempo segundos (si es > 0)

  numPasos indica si se espera tecla para el n�mero de pasos a ejecutar, al depurar"""
  global lineas_mas, tras_portada
  del texto_nuevo[:]
  if not numPasos:  # Si no es para el n�mero de pasos a ejecutar cuando se depura
    lineas_mas   = [0] * 8
    tras_portada = False
    if traza:
      prn ('Esperando tecla, con tiempo muerto', tiempo, 'segundos')
  if ide:
    # TODO: tiempo muerto, teclas pulsadas, revisar teclas de edici�n y que ninguna indebida resulte en un Enter pulsado
    actualizaVentana()
    prn ('stp' if numPasos else 'key')  # Avisamos al IDE si esperamos una tecla para n�mero de pasos de ejecuci�n o no
    stdout.flush()
    while True:
      entrada = raw_input()
      if not entrada:
        return ord ('\r')
      if ord (entrada[0]) == 0 and len (entrada) > 1 and ord (entrada[1]) in teclas_ascii_inv:
        return teclas_ascii_inv[ord (entrada[1])]
      if entrada[0] in '#$%' and len (entrada) > 3:  # Cambio de valor de bandera, punto de ruptura, o localidad actual de objeto
        separador = ',' if entrada[0] == '$' else '='
        if type (entrada) != str:
          separador = separador.encode ('iso-8859-15')
        valores = entrada[1:].split (separador)
        if entrada[0] == '#':  # Cambio de valor de bandera
          banderas_viejas[int (valores[0])] = int (valores[1])  # Actualizamos el valor de la bandera en su m�dulo
        elif entrada[0] == '%':  # Cambio de localidad actual de objeto
          locs_objs_viejas[int (valores[0])] = int (valores[1])  # Actualizamos la localidad del objeto en su m�dulo
        else:  # A�adir o quitar punto de ruptura
          puntoRuptura = (int (valores[0]), int (valores[1]), int (valores[2]))
          if puntoRuptura in puntos_ruptura:
            puntos_ruptura.remove (puntoRuptura)
          else:
            puntos_ruptura.append (puntoRuptura)
        continue
      return ord (entrada[0] if entrada else '\r')
  pygame.time.set_timer (pygame.USEREVENT, int (tiempo * 1000))  # Ponemos el timer
  copia = ventana.copy()  # Porque con PyGame 2 se pierde al menos al redimensionar
  while True:
    pygame.event.pump()
    evento = pygame.event.wait (500) if pygame.vernum[0] > 1 else pygame.event.wait()
    if evento.type == pygame.KEYDOWN:
      if evento.unicode and evento.unicode in teclas_unicode:
        tecla  = evento.unicode
        codigo = ord (tecla)
        mapeo_unicode[evento.scancode] = codigo
      elif evento.scancode == 40 and evento.unicode not in ('\r', 'D', 'd'):  # Omitimos la tecla de acento
        continue
      else:
        codigo = evento.key
        tecla  = chr (codigo) if codigo < 256 else ''
      if codigo not in teclas_pulsadas:
        teclas_pulsadas.append (codigo)
      if ((codigo < 256) and (tecla in teclas_edicion)) or codigo in teclas_kp or codigo in teclas_mas_256:
        pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
        return codigo
    elif evento.type == pygame.KEYUP:
      codigo = mapeo_unicode[evento.scancode] if evento.scancode in mapeo_unicode else evento.key
      if codigo in teclas_pulsadas:
        teclas_pulsadas.remove (codigo)
    elif evento.type == pygame.USEREVENT:  # Tiempo de espera superado
      pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
      return None
    elif evento.type == pygame.VIDEOEXPOSE:  # Ventana maximizada/restaurada
      if name == 'nt':
        try:  # Intentamos recuperar el tama�o de la ventana no maximizada
          import ctypes
          ctypes.windll.user32.ShowWindow (pygame.display.get_wm_info()['window'], 9)
        except:
          pass
    elif evento.type in (pygame.QUIT, pygame.VIDEORESIZE):
      redimensiona_ventana (evento, copia)
    pygame.display.update()  # Para que recupere el contenido si se cubri� la ventana

def carga_cursor ():
  """Carga la posici�n del cursor guardada de la subventana elegida """
  mueve_cursor (*cursores_at[elegida])

def guarda_cursor ():
  """Guarda la posici�n del cursor de la subventana elegida """
  cursores_at[elegida] = tuple (cursores[elegida])

def hay_grafico (numero):
  """Devuelve si existe el gr�fico de n�mero dado"""
  if ruta_graficos:
    try:
      pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
    except Exception as e:
      if traza:
        prn ('Gr�fico', numero, 'inv�lido o no encontrado en:', ruta_graficos)
        prn (e)
      return False
  elif graficos_bitmap.recursos:
    if not graficos_bitmap.recursos[numero] or 'imagen' not in graficos_bitmap.recursos[numero]:
      if traza:
        if not graficos_bitmap.recursos[numero]:
          razon = 'no est� en la base de datos gr�fica'
        else:
          razon = 'ese recurso de la base de datos gr�fica no es una imagen, o est� corrupta'
        prn ('Gr�fico', numero, 'inv�lido,', razon)
      return False
  elif numero not in graficos:
    return False
  return True

def insertaHastaMax (listaChrs, posInput, caracter, longMax):
  """Inserta el car�cter dado a la posici�n de la lista de caracteres dada contenida en la lista posInput, si no superar�a con ello la longitud m�xima longMax. Incrementa la posici�n (valor entero) dentro de posInput si lo ha a�adido"""
  if len (listaChrs) < longMax:
    listaChrs.insert (posInput[0], caracter)
    posInput[0] += 1

def lee_cadena (prompt = '', inicio = '', timeout = [0], espaciar = False, pararTimeout = False):
  """Lee una cadena (terminada con Enter) desde el teclado, dando realimentaci�n al jugador

El par�metro prompt, es el mensaje de prompt
El par�metro inicio es la entrada a medias anterior
El par�metro timeout es una lista con el tiempo muerto, en segundos
El par�metro espaciar permite elegir si se debe dejar una l�nea en blanco tras el �ltimo texto
El par�metro pararTimeout indica si se evitar� el tiempo muerto cuando la entrada tenga algo escrito"""
  cursorMovido = None  # Posici�n de cursor que recuperar si se ha movido
  posHistorial = len (historial)
  textoAntes   = False  # Si hab�a texto en la subventana de entrada antes de la l�nea del prompt
  if subv_input:  # Guardamos la subventana que estaba elegida justo antes, y cambiamos a la de entrada
    global elegida
    if inicio:
      borra_orden()
    subvAntes = elegida
    elegida   = subv_input
    if cursores[elegida][0] > subventanas[elegida][0] and prompt[0] == '\n':  # Hay texto antes de la l�nea del prompt
      # Cambiamos la subventana de entrada para que omita el texto escrito antes, y as� no lo borre
      cursores[elegida][0]     = subventanas[elegida][0]
      cursores[elegida][1]    += 1
      subventanas[elegida][1] += 1  # FIXME: no asumir que es una l�nea lo que se hab�a ocupado antes del prompt en la subventana de entrada
      prompt     = prompt[1:]
      textoAntes = True
  elif opcs_input & 8:  # Pedir la entrada debajo del todo
    brilloAntes  = brillo  # Valor de brillo antes de imprimir nada
    cursorMovido = list (cursores[elegida])
  elif (espaciar and cursores[elegida][1] >= topes[elegida][1] - 2 and cursores[elegida][0]) or \
      (NOMBRE_SISTEMA == 'QUILL' and cursores[elegida][0]):
    prompt = '\n' + prompt  # Dejaremos una l�nea en blanco entre el �ltimo texto y el prompt
  # El prompt se imprimir�
  if opcs_input & 8:  # Pedir la entrada debajo del todo
    lineas    = imprime_cadena (prompt, False, abajo = True)
    finPrompt = lineas[-1]  # �ltima l�nea del prompt
    if cursorMovido[1] + len (lineas) >= topes[elegida][1]:  # Hab�a hecho scroll
      cursorMovido[1] = topes[elegida][1] - len (lineas)
  else:  # Pedirla en la siguiente l�nea de la subventana de entrada
    imprime_cadena (prompt, False)
  entrada = []
  entrada.extend (list (inicio))  # Partimos la entrada anterior por caracteres
  longAntes = len (inicio) + 1  # Longitud de la entrada m�s el marcador (_) de entrada de car�cter (porque est� al final)
  longMax   = (topes[elegida][0] - cursores[elegida][0] - 1) + (topes[elegida][0] * (topes[elegida][1] - 1))  # Ancho m�ximo de la entrada
  posInput  = [len (inicio)]  # Posici�n del marcador (cursor) de entrada de car�cter, inicialmente al final
  while True:
    realimentacion = ''.join (entrada)
    if subv_input:
      borra_pantalla (noRedibujar = True)
      imprime_cadena (prompt, False, False)
    else:
      diferencia = longAntes - (len (entrada) + (1 if posInput[0] == len (entrada) else 0))  # Caracteres de m�s antes vs. ahora
      if diferencia > 0 or posInput[0] == len (entrada):
        realimentacion += ' ' * (diferencia + 1)  # Para borrar el cursor al final y el resto de la orden anterior
      longAntes = len (entrada) + (1 if posInput[0] == len (entrada) else 0)
    imprime_lineas (realimentacion.translate (iso8859_15_a_fuente), posInput[0])
    tecla = espera_tecla (timeout[0])

    if tecla == None:  # Tiempo muerto vencido
      if pararTimeout and entrada:
        continue  # Omitimos el tiempo muerto porque hay algo escrito en la entrada
      timeout[0] = True
      if subv_input:
        borra_pantalla()  # Borramos la entrada realimentada en pantalla
        if textoAntes:
          subventanas[elegida][1] -= 1  # FIXME: no asumir que es una l�nea lo que se hab�a ocupado antes del prompt en la subventana de entrada
        elegida = subvAntes  # Recuperamos la subventana elegida justo antes
      else:  # Quitamos el cursor del final de la entrada
        realimentacion = ''.join (entrada) + ' '  # El espacio borrar� el cursor cuando estaba al final
        imprime_lineas (realimentacion.translate (iso8859_15_a_fuente))
      return ''.join (entrada)

    modificadores = pygame.key.get_mods()
    mayuscula     = (modificadores & pygame.KMOD_CAPS)  != 0  # Caps Lock activo
    altGr         = (modificadores & pygame.KMOD_MODE)  != 0
    control       = (modificadores & pygame.KMOD_CTRL)  != 0
    shift         = (modificadores & pygame.KMOD_SHIFT) != 0
    # Primero, tratamos los c�digos superiores a 255
    if tecla in (pygame.K_KP_ENTER, pygame.K_RETURN):
      if entrada or NOMBRE_SISTEMA == 'GAC':
        break
      # Seguimos leyendo entrada del jugador si se pulsa Enter sin haber escrito nada, salvo en sistema GAC
    elif tecla == 314:  # Alt Gr + `
      insertaHastaMax (entrada, posInput, '[', longMax)
    elif tecla in teclas_kp:
      insertaHastaMax (entrada, posInput, teclas_kp[tecla], longMax)
    elif tecla == pygame.K_LEFT:
      if control:  # Salta al inicio de palabras
        if posInput[0]:  # S�lo si no est� al inicio del todo
          posInput[0] = ''.join (entrada).rfind (' ', 0, posInput[0] - 1) + 1
      else:
        posInput[0] = max (0, posInput[0] - 1)
    elif tecla == pygame.K_RIGHT:
      if control:  # Salta al final de palabras
        posInput[0] = ''.join (entrada).find (' ', posInput[0] + 2)
        if posInput[0] < 0:
          posInput[0] = len (entrada)
      else:
        posInput[0] = min (len (entrada), posInput[0] + 1)
    elif tecla == pygame.K_UP:
      if historial and posHistorial:
        if posHistorial == len (historial):
          historial_temp = list (entrada)  # Hace una copia para no modificarlo
        posHistorial = max (0, posHistorial - 1)
        entrada      = list (historial[posHistorial])  # Hace una copia para no modificarlo
        posInput[0]  = len (entrada)
    elif tecla == pygame.K_DOWN:
      if historial and posHistorial < len (historial):
        posHistorial = min (len (historial), posHistorial + 1)
        if posHistorial == len (historial):
          entrada = list (historial_temp)  # Hace una copia para no modificarlo
          del historial_temp[:]
        else:
          entrada = list (historial[posHistorial])  # Hace una copia para no modificarlo
        posInput[0] = len (entrada)
    elif tecla == pygame.K_HOME:
      posInput[0] = 0
    elif tecla == pygame.K_END:
      posInput[0] = len (entrada)
    elif tecla == pygame.K_DELETE:
      entrada = entrada[:posInput[0]] + entrada[posInput[0] + 1:]
    else:  # C�digo inferior a 256
      tecla = chr (tecla)
      if (tecla.isalpha() or tecla in ' ��') and tecla != '�':  # Una tecla de letra
        # Vemos si es texto que pegar desde el portapapeles
        texto = None
        if tecla == 'v' and control:
          try:
            if name == 'nt':
              texto = pygame.scrap.get (pygame.SCRAP_TEXT)[:-1].decode()
            else:
              texto = pygame.scrap.get ('text/plain;charset=utf-8').decode ('utf8')
            if type (texto) != str:
              texto = texto.encode ('iso-8859-15')
          except:
            texto = None
        if texto == None:  # Era (o considerar como) una tecla pulsada
          # Vemos si tenemos que a�adirla en may�scula o min�scula
          if todo_mayusculas or mayuscula ^ shift:
            if tecla == '�':  # Python 2 no sabe pasar a may�sculas � ni �
              tecla = '�'
            elif tecla == '�':
              tecla = '�'
            else:
              tecla = tecla.upper()
          insertaHastaMax (entrada, posInput, tecla, longMax)
        else:  # A�adimos el texto del portapapeles car�cter a car�cter
          if todo_mayusculas:
            texto = texto.upper()
          for tecla in texto:
            insertaHastaMax (entrada, posInput, tecla, longMax)
      elif tecla == '\b':  # La tecla Backspace, arriba del Enter
        if posInput[0]:
          entrada = entrada[:posInput[0] - 1] + entrada[posInput[0]:]
        posInput[0] = max (0, posInput[0] - 1)
      elif not shift:  # Shift sin pulsar
        if altGr:  # Alt Gr pulsado
          if tecla in teclas_alt_gr:
            insertaHastaMax (entrada, posInput, teclas_alt_gr[tecla], longMax)
        elif tecla in izquierda[:-1]:
          insertaHastaMax (entrada, posInput, tecla, longMax)  # Es v�lida tal cual
      elif tecla in teclas_shift:  # Shift est� pulsado
        insertaHastaMax (entrada, posInput, teclas_shift[tecla], longMax)
      else:
        insertaHastaMax (entrada, posInput, tecla, longMax)
  # Borramos la entrada realimentada en pantalla, s�lo si no es en subventana propia (usar borra_orden en el otro caso)
  if subv_input:
    borra_pantalla (noRedibujar = True)
    imprime_cadena (prompt, False, False)
    realimentacion = ''.join (entrada) + ' '  # El espacio borrar� el gui�n bajo
    imprime_lineas (realimentacion.translate (iso8859_15_a_fuente))
    if textoAntes:
      subventanas[elegida][1] -= 1  # FIXME: no asumir que es una l�nea lo que se hab�a ocupado antes del prompt en la subventana de entrada
    elegida = subvAntes  # Recuperamos la subventana elegida
  else:
    if cursorMovido:
      cursores[elegida] = cursorMovido
    borra_pantalla (True)
  if not subv_input or opcs_input & 2:  # Realimentaci�n permanente de la orden, junto al texto del juego
    if prompt and opcs_input & 8:  # Se imprim�a abajo del todo y hab�a prompt
      if cursores[elegida][0]:  # No est� en la primera columna
        imprime_cadena ('\n')
      if brillo != brilloAntes:
        colorTinta, colorPapel = fuente.get_palette()[:2]
        papel = paleta[brillo].index (colorPapel[:3])  # Omitimos el canal alfa
        tinta = paleta[brillo].index (colorTinta[:3])
        cambia_color_brillo (brilloAntes)
        fuente.set_palette ((paleta[brilloAntes][tinta], paleta[brilloAntes][papel]))
      imprime_linea (finPrompt)
      cursores[elegida][0] += len (finPrompt)
    imprime_cadena (''.join (entrada) + ' ')  # TODO: eliminar el espacio cuando no haga falta, como para QUILL y PAWS
    imprime_cadena ('\n')
  # Guardamos la entrada en el historial
  if not historial or historial[-1] != entrada:
    historial.append (entrada)
  # Devolvemos la cadena
  return ''.join (entrada)

def imprime_banderas (banderas):
  """Imprime el contenido de las banderas (en la extensi�n de la ventana)"""
  global banderas_antes, banderas_viejas
  if ide:
    if banderas_antes == None:
      banderas_antes  = [0,] * NUM_BANDERAS[0]
      banderas_viejas = banderas  # Guardamos aqu� acceso a la lista original, por si el IDE pide modificar alguna
      return
    cambiosBanderas = {}
    for numBandera in range (NUM_BANDERAS[0]):
      if banderas[numBandera] != banderas_antes[numBandera]:
        cambiosBanderas[numBandera] = banderas[numBandera]
        banderas_antes[numBandera]  = banderas[numBandera]
    prn ('flg', cambiosBanderas)
    return
  cifrasBandera = 2
  if NUM_BANDERAS[0] > 67:
    numFilas = 32
  else:
    numFilas = limite[1]
  paletaAntes = fuente_estandar.get_palette()
  if banderas_antes == None:
    banderas_antes  = [0,] * NUM_BANDERAS[0]
    banderas_viejas = set (range (NUM_BANDERAS[0]))
    # coloresBanderas = ((0, 192, 192), (96, 192, 96),  (192, 192, 0))   # Colores c�lidos
    coloresBanderas = ((0, 192, 192), (64, 128, 192), (128, 64, 192))  # Colores fr�os
    # Imprimimos los �ndices de cada bandera
    for num in range (NUM_BANDERAS[0]):
      # Cambiamos el color de impresi�n cuando se sobrepase cada centena
      if num % 100 == 0:
        fuente_estandar.set_palette ((coloresBanderas[num // 100], (0, 0, 0)))
      columna = ancho_juego + ((num // numFilas) * (((cifrasBandera + 3) * 6) + 3))
      fila    = (num % numFilas) * 8
      cadena  = str (num % (10 ** cifrasBandera)).zfill (cifrasBandera).translate (iso8859_15_a_fuente)
      for pos in range (cifrasBandera):
        c = ord (cadena[pos])
        ventana.blit (fuente_estandar, (columna + (pos * 6), fila),
                      ((c % 63) * 10, (c // 63) * 10, 6, 8))
  # Imprimimos los valores de las banderas
  for num in range (NUM_BANDERAS[0]):
    # S�lo imprimimos cada bandera la primera vez y cuando cambie de color
    if (banderas[num] == banderas_antes[num]) and (num not in banderas_viejas):
      continue
    columna = ancho_juego + (cifrasBandera * 6) + 1 + ((num // numFilas) * (((cifrasBandera + 3) * 6) + 3))
    fila    = (num % numFilas) * 8
    cadena  = str (banderas[num]).zfill (3).translate (iso8859_15_a_fuente)
    # Seleccionamos el color de impresi�n
    if banderas_antes[num] != banderas[num]:
      banderas_antes[num] = banderas[num]
      banderas_viejas.add (num)
      fuente_estandar.set_palette (((64, 255, 0), (0, 0, 0)))
    else:  # La bandera estaba en banderas_viejas
      banderas_viejas.remove (num)
      if banderas[num] == 0:
        fuente_estandar.set_palette (((96, 96, 96), (0, 0, 0)))
      else:
        fuente_estandar.set_palette (graficos_bitmap.paletaBN)
    # Imprimimos los valores de cada bandera
    for pos in range (3):
      c = ord (cadena[pos])
      ventana.blit (fuente_estandar, (columna + (pos * 6), fila),
                    ((c % 63) * 10, (c // 63) * 10, 6, 8))
  actualizaVentana()
  fuente_estandar.set_palette (paletaAntes)

def imprime_locs_objs (locs_objs):
  """Imprime las localidades de los objetos (en la extensi�n de la ventana)"""
  global locs_objs_antes, locs_objs_viejas
  if locs_objs == locs_objs_antes and not locs_objs_viejas:
    return  # No hacemos nada si no cambiaron ni hab�an cambiado justo antes
  if ide:
    if locs_objs_antes == None:
      locs_objs_antes  = locs_objs.copy() if type (locs_objs) == dict else [0,] * num_objetos[0]
      locs_objs_viejas = locs_objs  # Guardamos aqu� acceso a la lista original, por si el IDE pide modificar alguna
      return
    cambiosObjetos = {}
    for numObjeto in locs_objs if type (locs_objs) == dict else range (num_objetos[0]):
      if locs_objs[numObjeto] != locs_objs_antes[numObjeto]:
        cambiosObjetos[numObjeto]  = locs_objs[numObjeto]
        locs_objs_antes[numObjeto] = locs_objs[numObjeto]
    prn ('obj', cambiosObjetos)
    return
  if locs_objs_antes == None:
    locs_objs_antes  = [0,] * num_objetos[0]
    locs_objs_viejas = set (range (num_objetos[0]))
  if NOMBRE_SISTEMA == 'GAC':
    alias = ({0: 'N', 32767: 'C'}, {0: 'NC', 32767: 'CA'}, {0: 'NCR', 32767: 'CAR'})
  else:
    alias = ({252: 'N', 253: 'W', 254: 'C'}, {252: 'NC', 253: 'WO', 254: 'CA'}, {252: 'NCR', 253: 'WOR', 254: 'CAR'})
  if NUM_BANDERAS[0] > 67:  # Posici�n bajo la ventana de juego
    colInicial  = 0
    colFinal    = ancho_juego
    filaInicial = limite[1] * 8
    numFilas    = 32 - limite[1]
    # coloresObjetos = ((0, 192, 192), (96, 192, 96),  (192, 192, 0))   # Colores c�lidos
    coloresObjetos = ((0, 192, 192), (64, 128, 192), (128, 64, 192))  # Colores fr�os
  else:  # Posici�n a la derecha de las banderas
    colInicial  = ancho_juego + ((5 * 6) + 3) * (3 if NUM_BANDERAS[0] == 67 else 2)
    colFinal    = resolucion[0]
    filaInicial = 0
    numFilas    = limite[1]
    # coloresObjetos = ((192, 192, 0), (96, 192, 96), (0, 192, 192))   # Colores c�lidos
    coloresObjetos = ((128, 64, 192), (64, 128, 192), (0, 192, 192))  # Colores fr�os
  paletaAntes = fuente_estandar.get_palette()
  # Borramos la secci�n de localidades de objeto
  ventana.fill ((0, 0, 0), (colInicial, filaInicial, colFinal, numFilas * 8))
  # Imprimimos columna por columna los �ndices y valores de cada localidad de objeto
  colsCambio = (10 // numFilas, 100 // numFilas)  # Columnas donde cambia el n�mero de cifras para n�meros de objeto
  colColumna = colInicial  # Columna en p�xeles donde escribir �ndices en la columna actual
  for c in range (int (math.ceil (num_objetos[0] / float (numFilas)))):  # Para cada columna de localidades de objeto
    maxCol = 0  # Valor m�ximo en la columna, excluyendo valores con alias
    maxNum = min (num_objetos[0], c * numFilas + numFilas)  # Mayor n�mero de objeto en la columna + 1
    for num in range (c * numFilas, maxNum):
      if locs_objs[num] > maxCol and locs_objs[num] not in alias[0]:
        maxCol = locs_objs[num]
    cifrasValores = max (1, int (math.ceil (math.log10 (maxCol + 1))))  # Cifras necesarias para valores de esta columna
    cifrasObjeto  = max (1, int (math.ceil (math.log10 (maxNum))))      # Cifras necesarias para n�meros de objeto en esta columna
    cifrasObjeto  = min (2, cifrasObjeto)  # Limitamos a dos cifras, igual que con las banderas
    if colColumna + ((cifrasObjeto + cifrasValores) * 6) + 1 >= colFinal:
      break  # No cabe nada m�s, paramos para evitar imprimir donde van las banderas, evitando llegar a colFinal
    # Imprimimos los �ndices y valores de esta columna
    fila = filaInicial  # Fila en p�xeles donde escribir �ndice o valor
    for num in range (c * numFilas, maxNum):
      # Seleccionamos el color de impresi�n para el �ndice, que cambiar� cuando se sobrepase cada centena
      fuente_estandar.set_palette ((coloresObjetos[num // 100], (0, 0, 0)))
      # Imprimimos el �ndice del objeto en esta fila y columna
      cadena  = str (num % (10 ** cifrasObjeto)).zfill (cifrasObjeto).translate (iso8859_15_a_fuente)
      columna = colColumna  # Columna en p�xeles donde escribir �ndice o valor
      for pos in range (cifrasObjeto):
        c = ord (cadena[pos])
        ventana.blit (fuente_estandar, (columna + (pos * 6), fila),
                      ((c % 63) * 10, (c // 63) * 10, 6, 8))
      # Imprimimos el valor de esta fila y columna
      columna += cifrasObjeto * 6 + 1
      if locs_objs[num] in alias[0]:
        cadena = alias[cifrasValores - 1][locs_objs[num]]
      else:
        cadena = str (locs_objs[num]).zfill (cifrasValores)
      cadena = cadena.translate (iso8859_15_a_fuente)
      # Seleccionamos el color de impresi�n para el valor
      if locs_objs_antes[num] != locs_objs[num]:  # Ha cambiado su valor
        locs_objs_antes[num] = locs_objs[num]
        locs_objs_viejas.add (num)
        fuente_estandar.set_palette (((64, 255, 0), (0, 0, 0)))
      else:  # No ha cambiado su valor
        if num in locs_objs_viejas:  # El objeto estaba en locs_objs_viejas
          locs_objs_viejas.remove (num)
        if locs_objs[num] == 252:  # No creados
          fuente_estandar.set_palette (((96, 96, 96), (0, 0, 0)))
        else:
          fuente_estandar.set_palette (graficos_bitmap.paletaBN)
      # Imprimimos el valor de este objeto
      for pos in range (cifrasValores):
        c = ord (cadena[pos])
        ventana.blit (fuente_estandar, (columna + (pos * 6), fila),
                      ((c % 63) * 10, (c // 63) * 10, 6, 8))
      fila += 8
    colColumna += ((cifrasObjeto + cifrasValores) * 6) + 3
  actualizaVentana()
  fuente_estandar.set_palette (paletaAntes)

def imprime_cadena (cadena, textoNormal = True, redibujar = True, abajo = False, tiempo = 0, restauraColores = False):
  """Imprime una cadena en la posici�n del cursor (dentro de la subventana), y devuelve la cadena partida en l�neas

El cursor deber� quedar actualizado.

Si textoNormal es True, la cadena no es un prompt, por lo que antes de imprimir textos nuevos en cada l�nea de la subventana incluyendo la �ltima, paginar� antes de imprimir la �ltima. Cuando el texto era de prompt, textoNormal ser� False y no paginar� al imprimir la �ltima l�nea del texto en la �ltima l�nea de la subventana

Si abajo es True, imprimir� abajo del todo de la subventana sin hacer scroll mientras no alcance el cursor

Si tiempo no es 0, esperar� hasta ese tiempo en segundos cuando se espere tecla al paginar"""
  global juego
  if not cadena:
    return
  if tras_portada:
    borra_pantalla()
  if not texto_nuevo:
    texto_nuevo.append (True)
  if not textoNormal:
    restauraColores = True
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if cadena == '\n':  # TODO: sacar a funci�n nueva_linea
    lineas_mas[elegida] += 1
    restante = tope[0] - cursor[0]  # Columnas restantes que quedan en la l�nea
    colores  = {0: (daColorTinta(), daColorPapel(), None)} if restauraColores else {}
    imprime_linea ([chr (16)] * restante, redibujar = redibujar, colores = colores)
    if cursor[1] >= tope[1] - 1:
      scrollLineas (1, subventana, tope)
    cursores[elegida] = [0, min (tope[1] - 1, cursor[1] + 1)]
    if lineas_mas[elegida] == (tope[1] - 1) and (not subv_input or elegida != subv_input):
      esperaMas (tiempo)  # Paginaci�n
    if traza:
      prn ('Nueva l�nea, cursor en', cursores[elegida])
    return
  if traza:
    prn ('Impresi�n sobre subventana', elegida, 'en', subventana, 'con topes',
         tope, 'y cursor en', cursor)
  # Convertimos la cadena a posiciones sobre la tipograf�a
  if NOMBRE_SISTEMA == 'SWAN':
    colores = {}
    if ancho_caracter == 6:  # No se ha cargado la tipograf�a desde fichero
      # En la fuente alta s�lo hay letras may�sculas, as� que las dem�s las ponemos como fuente baja
      juego    = False  # Si la parte actual de la cadena est� en juego alto o no
      bajado   = False  # Si la parte actual de la cadena est� pasada a juego bajo por letras no may�sculas
      cambiada = ''     # Cadena cambiada teniendo en cuenta que en la fuente alta s�lo hay letras may�sculas
      for c in cadena:
        if c == izquierda[cod_juego_alto]:  # Es el mismo car�cter para alternar entre juego alto y bajo
          juego = not juego
          if not bajado:
            cambiada += c
          bajado = False
          continue
        if juego:
          if c.isupper():
            if bajado:
              bajado    = False
              cambiada += izquierda[cod_juego_alto]
          elif not bajado:
            bajado    = True
            cambiada += izquierda[cod_juego_alto]
        cambiada += c
      cadena = cambiada
      juego  = 0  # Inicializa la variable como n�mero, se necesitar� as� a continuaci�n
    else:  # Cargada tipograf�a de 8 x 8
      # Mantendremos el valor anterior de la variable juego, para poder mantenernos en el juego alto entre mensajes
      try:
        juego
      except:
        juego = 0
  else:  # No es SWAN
    cadena, colores = parseaColores (cadena, restauraColores)
    juego = 0  # Primera posici�n en la fuente del juego alto, si est� en el juego alto, 0 (primera del juego bajo) si no
  convertida = cadena.translate (iso8859_15_a_fuente)
  # Dividimos la cadena en l�neas
  iniLineas = [0]  # Posici�n de inicio de cada l�nea, para colorear
  lineas    = []
  linea     = []
  omitir    = 0  # N�mero de caracteres pendientes de omitir
  restante  = tope[0] - cursor[0]  # Columnas restantes que quedan en la l�nea
  for c in range (len (convertida)):
    if omitir:
      omitir -= 1
      continue
    ordinal = ord (convertida[c])
    ordOrig = ordinal if NOMBRE_SISTEMA == 'SWAN' else ord (cadena[c])
    if ((ordinal == len (izquierda) - 1) or  # Car�cter nueva l�nea (el �ltimo)
        (partir_espacio and restante == 0 and ordinal == 16)):  # Termina la l�nea con espacio
      lineas.append (''.join (linea))
      iniLineas.append (iniLineas[-1] + len (linea) + (1 if (ordinal == len (izquierda) - 1) else 0))
      linea    = []
      restante = tope[0]
    elif ordOrig == cod_juego_alto and juego == 0:
      juego = 128  # TODO: �hay alg�n int�rprete donde juego parta desde 128 - 16?
      if ancho_caracter == 8:  # SWAN con tipograf�a cargada desde fichero
        juego -= 32
    elif ordOrig == cod_juego_bajo:
      juego = 0
    elif cod_columna and cod_tabulador and ordinal in (len (izquierda) - 2, len (izquierda) - 3):  # Pen�ltimo o antepen�ltimo car�cter: tabulador o movimiento de cursor
      numEspacios  = 0
      posTabulador = iniLineas[-1] + len (linea)
      if cadena[c] == '\t':  # Es un tabulador
        if restante > tope[0] // 2:
          numEspacios = (tope[0] // 2) - len (linea)  # Rellena con espacios hasta mitad de l�nea
        else:
          numEspacios = restante  # Rellena el resto de la l�nea con espacios
      elif cadena[c] == '\r' and len (cadena) > c + 2:  # Es un cambio de columna en la misma fila
        columna     = (ord (cadena[c + 1]) + 1) % limite[0]
        numEspacios = columna - posTabulador  # Rellena con espacios hasta la columna indicada
        omitir      = 2
      if numEspacios > 0:
        linea.extend (chr (16) * numEspacios)
        restante -= numEspacios
        if restante == 0:
          lineas.append (''.join (linea))
          iniLineas.append (iniLineas[-1] + len (linea))
          linea = []
          restante = tope[0]
        if cadena[c] == '\r':
          numEspacios -= 2  # Para descontar los caracteres que indican fila y columna
      elif numEspacios:  # Era un n�mero negativo de espacios
        numEspacios = -2  # Para descontar los caracteres que indican fila y columna
      coloresNuevos = {}
      for inicio in tuple (colores.keys()):
        if inicio > posTabulador:
          coloresNuevos[inicio + numEspacios - 1] = colores[inicio]
        else:
          coloresNuevos[inicio] = colores[inicio]
      colores = coloresNuevos
    elif restante > 0:
      linea.append (chr (ordinal + juego))
      restante -= 1
    else:  # Hay que partir la l�nea, desde el �ltimo car�cter de espacio
      for i in range (len (linea) - 1, -1, -1) if partir_espacio else ():  # Desde el final al inicio
        if ord (linea[i]) == 16:  # Este car�cter es un espacio
          lineas.append (''.join (linea[:i + 1]))
          linea = linea[i + 1:]
          iniLineas.append (iniLineas[-1] + i + 1)
          break
      else:  # Ning�n car�cter de espacio en la l�nea
        if len (linea) == tope[0]:  # La l�nea nunca se podr� partir limpiamente
          # La partimos suciamente (en mitad de palabra)
          lineas.append    (''.join (linea))
          iniLineas.append (iniLineas[-1] + len (linea))
          linea = []
        else:  # Lo que ya ten�amos ser� para una nueva l�nea
          lineas.append (' '.translate (iso8859_15_a_fuente) * len (linea))  # TODO: revisar qu� es esto y si es correcto
          iniLineas.append (iniLineas[-1] + len (linea))
      linea.append (chr (ordinal + juego))
      restante = tope[0] - len (linea)
  if linea:  # Queda algo en la �ltima l�nea
    lineas.append (''.join (linea))
  # Paginamos antes de escribir sobre la �ltima l�nea si todas las anteriores eran nuevas
  if cursor[0] == 0 and tope[1] > 1 and cursor[1] == tope[1] - 1 and lineas_mas[elegida] == tope[1] - 1:
    esperaMas (tiempo)  # Paginaci�n
  if abajo:
    cursor[0] = 0
    cursor[1] = max (0, tope[1] - len (lineas) - (1 if cadena[-1] == '\n' else 0))
  # Imprimimos la cadena l�nea por l�nea
  for i in range (len (lineas)):
    if i > 0:  # Nueva l�nea antes de cada una, salvo la primera
      cursorAntes = cursor
      cursor      = [0, min (cursor[1] + 1, tope[1] - 1)]
      cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
      if cursorAntes[1] == cursor[1] and cursor[1] == tope[1] - 1:  # Tope de l�neas sobrepasado, hacemos scroll con cada una
        scrollLineas (1, subventana, tope)
      if lineas_mas[elegida] == (tope[1] - 1) and (textoNormal or i < len (lineas) - 1) and (not subv_input or elegida != subv_input):
        esperaMas (tiempo)  # Paginaci�n
    elif 0 in colores and not lineas[i]:  # La primera l�nea es s�lo \n
      if colores[0][2] != None:
        cambia_fuente (colores[0][2])  # Cargamos la fuente actual
      fuente.set_palette (tuple (colores[0][:2]))  # Cargamos el color inicial de la cadena
    if cod_brillo or cods_tinta or id_plataforma in ('Atari800', 'CPC', 'PC'):
      imprime_linea (lineas[i], redibujar = redibujar, colores = colores, inicioLinea = iniLineas[i])
    else:
      imprime_linea (lineas[i], redibujar = redibujar, colores = colores)
    if i < len (lineas) - 1:  # S�lo si la l�nea se ha completado
      lineas_mas[elegida] += 1
      if iniLineas[i + 1] - 1 in colores:  # Cambiamos los colores si al final de la l�nea cambiaban
        if colores[iniLineas[i + 1] - 1][2] != None:
          cambia_fuente (colores[iniLineas[i + 1] - 1][2])  # Cargamos la fuente actual
        fuente.set_palette (tuple (colores[iniLineas[i + 1] - 1][:2]))
      if textoNormal and id_plataforma != 'QL' and cursor[0] + len (lineas[i]) < tope[0]:  # Cab�an m�s caracteres al final de la l�nea
        cursor[0] += len (lineas[i])
        imprime_linea (chr (16) * (tope[0] - cursor[0]))
  if lineas:  # Hab�a alguna l�nea
    if cadena[-1] == '\n':  # La cadena terminaba en nueva l�nea
      if cursor[1] == tope[1] - 1:
        scrollLineas (1, subventana, tope, redibujar)
        cursor = [0, cursor[1]]
      else:
        cursor = [0, cursor[1] + 1]
      lineas_mas[elegida] += 1
    else:
      cursor = [cursor[0] + len (lineas[-1]), cursor[1]]
    cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
    if len (cadena) in colores:  # Cambiaban los colores al final de la cadena
      if colores[len (cadena)][2] != None:
        cambia_fuente (colores[len (cadena)][2])  # Cargamos la fuente actual
      fuente.set_palette (tuple (colores[len (cadena)][:2]))  # Cargamos el color final de la cadena
  if traza:
    prn ('Fin de impresi�n, cursor en', cursor)
  return lineas

def imprime_linea (linea, posInput = None, redibujar = True, colores = {}, inicioLinea = 0):
  """Imprime una l�nea de texto en la posici�n del cursor, sin cambiar el cursor

Los caracteres de linea deben estar convertidos a posiciones en la tipograf�a"""
  # Coordenadas de destino
  destinoX = (subventanas[elegida][0] + cursores[elegida][0]) * ancho_caracter
  destinoY = (subventanas[elegida][1] + cursores[elegida][1]) * 8
  for i in range (len (linea)):  # Dibujamos cada caracter en la l�nea
    destinoXchr = destinoX + (i * ancho_caracter)  # Posici�n X donde toca dibujar el caracter
    restantes   = ancho_juego - destinoXchr        # P�xeles restantes desde esta posici�n en la ventana de juego
    if restantes < 1:
      break  # No dibujar m�s all� del ancho de la ventana de juego
    c = ord (linea[i])
    if ancho_caracter == 8:
      c -= 16 if c < 128 or NOMBRE_SISTEMA == 'SWAN' else 32
    if i + inicioLinea in colores:
      if colores[i + inicioLinea][2] != None:
        cambia_fuente (colores[i + inicioLinea][2])  # Cargamos la fuente actual
      fuente.set_palette (tuple (colores[i + inicioLinea][:2]))
    # Curioso, aqu� fuente tiene dos significados correctos :)
    # (SPOILER: Como sin�nimo de origen y como sin�nimo de tipograf�a)
    ventana.blit (fuente, (destinoXchr, destinoY),
                  ((c % 63) * 10, (c // 63) * 10, min (ancho_caracter, restantes), 8))
  if posInput != None:
    preparaCursor()
    flagsBlit = pygame.BLEND_ADD if daColorPapel() == (0, 0, 0) else 0
    ventana.blit (chr_cursor, (destinoX + (posInput * ancho_caracter), destinoY), (0, 0, ancho_caracter, 8), special_flags = flagsBlit)
  if redibujar:
    actualizaVentana()

def imprime_lineas (texto, posInput = None):
  """Imprime el texto en la posici�n del cursor, sin cambiar el cursor, partiendo por l�neas si texto alcanza el tope de la subventana

Los caracteres de linea deben estar convertidos a posiciones en la tipograf�a"""
  cursor     = list (cursores[elegida])  # Copia del cursor, para recuperarlo despu�s
  lineas     = []  # L�neas partidas como corresponde ("a lo bruto")
  maxPrimera = topes[elegida][0] - cursores[elegida][0]  # Anchura m�xima de la primera l�nea
  posInputEn = 0   # En qu� l�nea est� el gui�n bajo de feedback gr�fico de entrada
  if len (texto) < maxPrimera:
    lineas.append (texto)
  else:
    lineas.append (texto[:maxPrimera])
    inicio = maxPrimera
    fin    = maxPrimera + topes[elegida][0]
    if posInput != None and posInput >= inicio:
      posInputEn += 1
      posInput   -= maxPrimera
    while fin <= len (texto):
      lineas.append (texto[inicio:fin])
      inicio += topes[elegida][0]
      fin    += topes[elegida][0]
      if posInput != None and posInput >= inicio:
        posInputEn += 1
        posInput   -= topes[elegida][0]
    lineas.append (texto[inicio:fin])
  for l in range (len (lineas)):
    linea = lineas[l]
    if l:  # No es la primera l�nea
      cursores[elegida][0] = 0
      if subv_input:
        scrollLineas (1, subventanas[elegida], topes[elegida], False)
      else:
        cursores[elegida][1] += 1
    if posInputEn == l:
      imprime_linea (linea, posInput, False)
    else:
      imprime_linea (linea, redibujar = False)
  cursores[elegida] = cursor
  actualizaVentana()

def mueve_cursor (columna, fila = None):
  """Cambia de posici�n el cursor de la subventana elegida"""
  if fila == None:
    fila = cursores[elegida][1]
  else:
    lineas_mas[elegida] = fila
  cursores[elegida] = [columna, fila]
  if traza:
    prn ('Subventana', elegida, 'en', subventanas[elegida], 'con topes', topes[elegida],
         'y cursor movido a', cursores[elegida])

def prepara_topes (columnas, filas):
  """Inicializa los topes al n�mero de columnas y filas dado"""
  global topes, topes_gfx
  if columnas == 53 and ancho_caracter == 8:  # Ajustamos ancho en caracteres cuando se ha cargado fuente de 8 x 8
    columnas = resolucion[0] // 8
  limite[0] = columnas           # Ancho m�ximo absoluto de cada subventana
  limite[1] = filas              # Alto m�ximo absoluto de cada subventana
  topes_gfx = [columnas, filas]  # Ancho y alto del �ltimo gr�fico dibujado en la subventana 0
  for topesSubventana in topes:  # Topes relativos de cada subventana de impresi�n
    topesSubventana[0] = columnas
    topesSubventana[1] = filas

def pos_subventana (columna, fila):
  """Cambia la posici�n de origen de la subventana de impresi�n elegida"""
  subventanas[elegida] = [columna, fila]
  pos_gfx_sub[elegida] = (columna * ancho_caracter, fila * 8)
  # Ajustamos los topes para que no revasen el m�ximo permitido
  # No s� si DAAD hace esto, en caso de no usar el condacto WINSIZE
  # FIXME: Comprobar qu� ocurre si no se usa WINSIZE, �se usan los topes
  #        anteriores, o se maximizan?
  topes[elegida] = [min (topes[elegida][0], limite[0] - columna),
                    min (topes[elegida][1], limite[1] - fila)]
  # Ponemos el cursor al origen de la subventana
  cursores[elegida] = [0, 0]
  if traza:
    prn ('Subventana', elegida, 'puesta en', subventanas[elegida], 'con topes',
         topes[elegida], 'y cursor en', cursores[elegida])

def reinicia_subventanas ():
  """Ajusta todas las subventanas de impresi�n a sus valores por defecto"""
  colorTinta = len (paleta[0]) - 1 if color_tinta == None else color_tinta
  for i in range (num_subvens):
    color_subv[i]  = [colorTinta, 0, 0]
    cursores[i]    = [0, 0]
    subventanas[i] = [0, 0]
    topes[i]       = list (limite)
  topes_gfx = list (limite)
  if traza:
    prn ('Subventanas reiniciadas a [0, 0] con topes', limite,
         'y cursor en [0, 0]')


# Funciones auxiliares que s�lo se usan en este m�dulo

def cambiaPaleta (nuevaPaleta, convertir = True, paraPortada = False):
  """Cambia la paleta de la ventana de juego por la dada, la reordena para textos, y opcionalmente convierte los colores dibujados por los nuevos"""
  if traza:
    prn ('Paleta cambiada')
  if paleta[0]:
    if convertir and nuevaPaleta != paleta_gfx:
      for x in range (320):
        for y in range (200):
          try:
            indicePaleta = paleta_gfx.index (ventana.get_at ((x, y))[:3])
          except:
            continue
          ventana.set_at ((x, y), nuevaPaleta[indicePaleta])
    del paleta[0][:]
  del paleta_gfx[:]
  paleta_gfx.extend (nuevaPaleta)
  # Dejamos la paleta tal cual en modos gr�ficos que no soportan cambio de paleta
  if not paraPortada and graficos_bitmap.modo_gfx not in ('ST', 'VGA'):
    paleta[0].extend (nuevaPaleta)
    return
  # Asignamos la paleta en el orden para textos
  copiaPaleta = list (nuevaPaleta)
  if paraPortada:
    # Buscamos los colores m�s cercanos al negro y al blanco
    masCercanos = [[None, 999999], [None, 999999]]  # �ndice en paleta de colores m�s cercanos al negro y al blanco, y su cercan�a a �stos
    for cp in range (len (nuevaPaleta)):
      rojoPaleta, verdePaleta, azulPaleta = nuevaPaleta[cp]
      # Cercan�a al color negro
      cercania = rojoPaleta + verdePaleta + azulPaleta
      if cercania < masCercanos[0][1]:
        masCercanos[0] = [cp, cercania]
      # Cercan�a al color blanco
      cercania = (255 - rojoPaleta) + (255 - verdePaleta) + (255 - azulPaleta)
      if cercania < masCercanos[1][1]:
        masCercanos[1] = [cp, cercania]
    # Ponemos el negro primero y el blanco despu�s
    paleta[0].append (copiaPaleta.pop (masCercanos[0][0]))
    paleta[0].append (copiaPaleta.pop (masCercanos[1][0] - 1))
  else:  # No es para la portada
    if graficos_bitmap.modo_gfx == 'VGA':
      for i in (0, 15, 4, 2, 1, 3):  # Orden que aplican los int�rpretes originales sobre las primeras posiciones
        paleta[0].append (copiaPaleta[i])
      copiaPaleta = copiaPaleta[5:15]  # Colores restantes
    else:  # modo_gfx == 'ST'
      paleta[0].append (copiaPaleta[0])
      paleta[0].append (copiaPaleta[15])
      copiaPaleta = copiaPaleta[1:15]  # Colores restantes
  # A�adimos los colores restantes en el mismo orden
  paleta[0].extend (copiaPaleta)

def cargaGrafico (numero):
  """Carga un gr�fico del recurso de base de datos gr�fica de n�mero dado, dejando su informaci�n y la imagen PyGame preparada en graficos"""
  recurso   = graficos_bitmap.recursos[numero]
  bufferImg = bytes (bytearray (recurso['imagen']))
  graficos[numero] = {'grafico': pygame.image.frombuffer (bufferImg, recurso['dimensiones'], 'P')}
  for propiedad in ('banderas', 'paleta', 'posicion'):
    graficos[numero][propiedad] = recurso[propiedad]

def daColorPapel ():
  """Devuelve el color de fondo de la subventana elegida, seg�n corresponda a la plataforma"""
  if paleta[1]:  # Si hay dos paletas, debe ser Spectrum
    return paleta[brillo][color_subv[elegida][1]]  # Color del papel
  return paleta[0][color_subv[elegida][1]] if paleta[0] else (0, 0, 0)  # Color del papel

def daColorTinta ():
  """Devuelve el color de tinta de la subventana elegida, seg�n corresponda a la plataforma"""
  if paleta[1]:  # Si hay dos paletas, debe ser Spectrum
    return paleta[brillo][daTinta()]
  return paleta[0][daTinta()]

def daTinta ():
  """Devuelve el n�mero de color de tinta de la subventana elegida, seg�n corresponda a la plataforma"""
  if paleta[1]:  # Si hay dos paletas, debe ser Spectrum
    if color_subv[elegida][0] == 9:  # Contraste
      return 0 if color_subv[elegida][1] > 3 else 7  # Negro para colores de papel oscuros, y blanco para colores claros
  return color_subv[elegida][0] % len (paleta[0])

def esperaMas (tiempo):
  """Muestra el texto de paginaci�n, espera una tecla, y luego lo borra

Si tiempo no es 0, esperar� hasta ese tiempo en segundos"""
  imprime_linea (txt_mas.translate (iso8859_15_a_fuente))
  espera_tecla (tiempo)
  imprime_linea (' '.translate (iso8859_15_a_fuente) * len (txt_mas))

def factorEscalaMaximo ():
  """Devuelve el factor m�ximo de escalado sin alcanzar la resoluci�n de pantalla"""
  global infoPantalla
  try:
    infoPantalla
  except:
    if name == 'nt':  # Intentamos tener en cuenta el factor de escala de Windows
      try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
      except:
        pass
    infoPantalla = pygame.display.Info()
  factorMaximo = 1
  while resolucion[0] * (factorMaximo + 1) < infoPantalla.current_w and resolucion[1] * (factorMaximo + 1) < infoPantalla.current_h:
    factorMaximo += 1
  return factorMaximo

def parseaColores (cadena, restauraColores = False):
  """Procesa los c�digos de control de cambio de color y fuente, devolviendo la cadena sin ellos, y un diccionario posici�n: colores e �ndice de fuente a aplicar"""
  global brillo
  papel = color_subv[elegida][1]  # Color de papel/fondo
  tinta = daTinta()               # Color de tinta
  if not cod_brillo and not cods_tinta and id_plataforma not in ('Atari800', 'CPC', 'PC'):
    return cadena, {0: (paleta[brillo][tinta], paleta[brillo][papel], None)}
  if restauraColores:
    colores = {0: (paleta[brillo][tinta], paleta[brillo][papel], None)}
  else:
    colores = {}
  fuente     = None   # �ndice de fuente actual
  inversa    = False  # Si se invierten o no papel y fondo
  omitir     = 0      # N�mero de caracteres pendientes de omitir por completo
  sigBrillo  = False  # Si el siguiente car�cter indica si se pone o quita brillo al color de tinta
  sigFlash   = False  # Si el siguiente car�cter indica si se pone o quita efecto flash
  sigInversa = False  # Si el siguiente car�cter indica si se invierten o no papel y fondo
  sigPapel   = False  # Si el siguiente car�cter indica el color de papel/fondo
  sigTinta   = False  # Si el siguiente car�cter indica el color de tinta
  sinColores = ''     # Cadena sin los c�digos de control de colores
  talCual    = 0      # N�mero de caracteres pendientes de omitir dej�ndolos tal cual est�n
  for i in range (len (cadena)):
    if omitir:
      omitir -= 1
      continue
    if talCual:
      omitir     -= 1
      sinColores += cadena[i]
      continue
    c = ord (cadena[i])
    if sigBrillo or sigFlash or sigInversa or sigPapel or sigTinta:
      if sigBrillo:
        brillo    = 1 if c else 0
        sigBrillo = False
      elif sigFlash:
        sigFlash = False
        continue
      elif sigInversa:
        sigInversa = False
        if inversa and not c or not inversa and c:  # Si se ha activado o desactivado inversa
          color   = papel
          papel   = tinta
          tinta   = color
          inversa = True if c else False
        else:
          continue
      elif sigPapel:
        papel    = c % len (paleta[brillo])
        sigPapel = False
      else:
        sigTinta = False
        tinta    = c % len (paleta[brillo])
    elif c in (cod_inversa_fin, cod_inversa_ini):
      if c == cod_inversa_ini and not inversa or c == cod_inversa_fin and inversa:  # Si se ha activado o desactivado inversa
        color   = papel
        papel   = tinta
        tinta   = color
        inversa = not inversa
      else:
        continue
    elif c in (cod_brillo, cod_flash, cod_inversa, cod_papel, cod_tinta):
      if c == cod_brillo:
        sigBrillo = True
      elif c == cod_flash:
        sigFlash = True
      elif c == cod_inversa:
        sigInversa = True
      elif c == cod_papel:
        sigPapel = True
      else:
        sigTinta = True
      continue
    elif c == cod_reset:
      inversa = False
      tinta, papel = colores_inicio[:2]
    elif c in cods_tinta:
      if id_plataforma == 'QL' and i < len (cadena) - 1 and ord (cadena[i + 1]) == cod_inversa_ini:
        papel  = cods_tinta[c]
        omitir = 1
      else:
        tinta = cods_tinta[c]
    elif id_plataforma == 'CPC' and c in range (1, 9):
      if c < 5:
        tinta = tintas_cpc[c - 1]
      else:
        papel = tintas_cpc[c - 5]
    elif c < 6 and NOMBRE_SISTEMA == 'PAWS' and id_plataforma == 'ZX':
      if c >= len (fuentes_zx):
        continue
      fuente = c
    elif c == cod_tabulador:
      sinColores += '\t'
      continue
    elif c == cod_columna:
      sinColores += '\r'
      talCual = 2
      continue
    elif cadena[i] not in izquierda and cadena[i] in noEnFuente:
      sinColores += noEnFuente[cadena[i]]
      continue
    elif NOMBRE_SISTEMA == 'QUILL' and id_plataforma in ('Atari800', 'PC') and c > 127:  # Es un car�cter en inversa
      if not inversa:  # S�lo lo hacemos para el primer car�cter consecutivo en inversa
        # Invertimos color de tinta y papel
        color   = papel
        papel   = tinta
        tinta   = color
        inversa = True
        colores[len (sinColores)] = (paleta[brillo][tinta], paleta[brillo][papel], fuente)  # Color de tinta, papel y n�mero de fuente a aplicar
      sinColores += chr (c - 128)
      continue
    elif paleta[1] and c < 32 and c != ord ('\n'):  # C�digos de control de Spectrum ZX inv�lidos o desconocidos
      continue
    else:
      if inversa and NOMBRE_SISTEMA == 'QUILL' and id_plataforma in ('Atari800', 'PC'):  # Este car�cter terminar� la impresi�n en inversa, al no estar en inversa
        # Invertimos color de tinta y papel
        color   = papel
        papel   = tinta
        tinta   = color
        inversa = False
        colores[len (sinColores)] = (paleta[brillo][tinta], paleta[brillo][papel], fuente)  # Color de tinta, papel y n�mero de fuente a aplicar
      sinColores += cadena[i]
      continue
    colores[len (sinColores)] = (paleta[brillo][tinta], paleta[brillo][papel], fuente)  # Color de tinta, papel y n�mero de fuente a aplicar
  if version_info[0] < 3:  # La versi�n de Python es 2.X
    sinColores = sinColores.encode ('iso-8859-15', errors = 'replace')
  return sinColores, colores

def precargaGraficos ():
  """Deja preparados los gr�ficos residentes en la base de datos gr�fica cargada"""
  for numero in range (len (graficos_bitmap.recursos)):
    recurso = graficos_bitmap.recursos[numero]
    if not recurso or 'imagen' not in recurso or 'residente' not in recurso['banderas']:
      continue
    cargaGrafico (numero)

def precargaGraficosSWAN (gfx):
  """Deja preparados los gr�ficos de ficheros PIX de SWAN detectados"""
  for numImagen, rutaImagen in gfx.items():
    try:
      fichero = open (rutaImagen, 'rb')
      imagen, paleta, dimensiones = graficos_bitmap.carga_imagen_pix (fichero)
      fichero.close()
      bufferImg = bytes (bytearray (imagen))
      graficos[numImagen] = pygame.image.frombuffer (bufferImg, dimensiones, 'P')
    except Exception as e:
      prn ('Fichero de gr�fico', rutaImagen, 'corrupto o inv�lido', file = stderr)
      if traza:
        prn (e)
      continue
    graficos[numImagen].set_palette (paleta)

def preparaConversion ():
  """Prepara la variable global iso8859_15_a_fuente para convertir las cadenas de la aventura a posiciones en la fuente"""
  global iso8859_15_a_fuente
  der = []
  for i in range (len (izquierda)):
    der.append (chr (i))
  derecha = ''.join (der)
  iso8859_15_a_fuente = maketrans (izquierda, derecha)

def preparaCursor ():
  """Prepara el cursor con el car�cter y color adecuado"""
  cadenaCursor, colores = parseaColores (cad_cursor)
  if len (cadenaCursor) >= 1:
    posEnFuente = izquierda.index (cadenaCursor[0]) if cadenaCursor[0] in izquierda else ord (cadenaCursor[0])
    if ancho_caracter == 8:
      posEnFuente -= 16 if posEnFuente < 128 else 32
    if colores:
      chr_cursor.set_colorkey (colores[0][1])  # El color de papel/fondo ser� ahora transparente
      if colores[0][2] != None:
        cambia_fuente (colores[0][2])  # Cargamos la fuente actual
      fuente.set_palette (tuple (colores[0][:2]))
    chr_cursor.blit (fuente, (0, 0), ((posEnFuente % 63) * 10, (posEnFuente // 63) * 10, ancho_caracter, 8))

def scrollLineas (lineasAsubir, subventana, tope, redibujar = True):
  """Hace scroll gr�fico del n�mero dado de l�neas, en la subventana dada, con topes dados"""
  destino = (subventana[0] * ancho_caracter, subventana[1] * 8)  # Posici�n de destino
  origenX = destino[0]  # Coordenada X del origen (a subir)
  origenY = (subventana[1] + lineasAsubir) * 8  # Coordenada Y del origen
  anchura = tope[0] * ancho_caracter      # Anchura del �rea a subir
  altura  = (tope[1] - lineasAsubir) * 8  # Altura del �rea a subir
  # Copiamos las l�neas a subir
  if altura > 0:
    ventana.blit (ventana, destino, (origenX, origenY, anchura, altura))
  # Borramos el hueco
  lineasAsubir = min (lineasAsubir, tope[1])
  colorPapel   = daColorPapel()
  origenY      = (subventana[1] + tope[1] - lineasAsubir) * 8
  altura       = lineasAsubir * 8
  ventana.fill (colorPapel, (origenX, origenY, anchura, altura))
  if redibujar:
    actualizaVentana()
