# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Interfaz gráfica de usuario (GUI) con PyGame para el intérprete PAW-like
# Copyright (C) 2010, 2018-2021 José Manuel Ferrer Ortiz
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

from prn_func import *
from sys      import version_info

import math    # Para ceil
import string  # Para algunas constantes

import pygame


traza = False  # Si queremos una traza del funcionamiento del módulo
if traza:
  from prn_func import prn

izquierda  = 'ª¡¿«»áéíóúñÑçÇüÜ !"º$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]¯_`abcdefghijklmnopqrstuvwxyz{|}~\n'
noEnFuente = {'©': 'c', u'\u2192': '>', u'\u2190': '<'}  # Tabla de conversión de caracteres que no están en la fuente

der = []
for i in range (len (izquierda)):
  der.append (chr (i))
derecha = ''.join (der)

iso8859_15_a_fuente = maketrans (izquierda, derecha)

# Teclas imprimibles y de edición, con código < 256
teclas_edicion = string.printable + string.punctuation + 'ñçº¡\b\x1b'
# Teclas de edición con código >= 256
# 314 es Alt Gr + ` (es decir, '[' en el teclado español)
teclas_mas_256 = (314, pygame.K_DELETE, pygame.K_DOWN, pygame.K_END, pygame.K_HOME, pygame.K_KP_ENTER, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
# Teclas imprimibles del teclado numérico
teclas_kp = {pygame.K_KP0: '0', pygame.K_KP1: '1', pygame.K_KP2: '2', pygame.K_KP3: '3', pygame.K_KP4: '4', pygame.K_KP5: '5', pygame.K_KP6: '6', pygame.K_KP7: '7', pygame.K_KP8: '8', pygame.K_KP9: '9', pygame.K_KP_DIVIDE: '/', pygame.K_KP_MULTIPLY: '*', pygame.K_KP_MINUS: '-', pygame.K_KP_PLUS: '+', pygame.K_KP_PERIOD: '.'}
# Teclas que al pulsar Alt Gr son otra
teclas_alt_gr = {'º': '\\', '1': '|', '2': '@', '4': '~', '7': '{', '8': '[', '9': ']', '0': '}', '+': ']', 'ñ': '~', 'ç': '}', 'z': '«', 'x': '»'}
# Teclas que al pulsar Shift son otra
teclas_shift = {'º': 'ª', '1': '!', '2': '"', '4': '$', '5': '%', '6': '&', '7': '/', '8': '(', '9': ')', '0': '=', "'": '?', '¡': '¿', '+': '*', 'ñ': 'Ñ', 'ç': 'Ç', '<': '>', ',': ';', '.': ':', '-': '_'}


pygame.init()  # Necesario para trabajar con la librería PyGame
pygame.event.set_blocked (pygame.MOUSEMOTION)  # No atenderemos los movimientos del ratón
escalada = None
modo     = 'normal'  # Modo de ventana: normal, scale[2-3]x (escalado), o fullscreen (a pantalla completa)
ventana  = None

fuente = pygame.image.load ('fuente.png')  # Fuente tipográfica
fuente.set_palette (((255, 255, 255), (0, 0, 0)))

guion_bajo = pygame.Surface ((6, 8))  # Carácter de guión bajo con transparencia, para marcar posición de input
guion_bajo.blit (fuente, (0, 0), ((79 % 63) * 10, (79 // 63) * 10, 6, 8))  # '_' está en la posición 79
guion_bajo.set_colorkey ((0, 0, 0))  # El color negro será ahora transparente

# Variables que ajusta el intérprete
cambia_brillo    = None      # Carácter que si se encuentra en una cadena, dará o quitará brillo al color de tinta de la letra
cambia_flash     = None      # Carácter que si se encuentra en una cadena, pondría o quitaría efecto flash a la letra
cambia_papel     = None      # Carácter que si se encuentra en una cadena, cambiará el color de papel/fondo de la letra
cambia_tinta     = None      # Carácter que si se encuentra en una cadena, cambiará el color de tinta de la letra
centrar_graficos = []        # Si se deben centrar los gráficos al dibujarlos
juego_alto       = None      # Carácter que si se encuentra en una cadena, pasará al juego de caracteres alto
juego_bajo       = None      # Carácter que si se encuentra en una cadena, pasará al juego de caracteres bajo
paleta           = ([], [])  # Paleta de colores sin y con brillo, para los cambios con cambia_*
todo_mayusculas  = False     # Si la entrada del jugador será incondicionalmente en mayúsculas
ruta_graficos    = ''

banderas_antes  = None  # Valor anterior de las banderas
banderas_viejas = None  # Banderas que antes cambiaron de valor
historial       = []    # Historial de órdenes del jugador
historial_temp  = []    # Orden a medias, guardada al acceder al historial

# Todas las coordenadas son columna, fila
num_subvens = 8                # DAAD tiene 8 subventanas
elegida     = 1                # Subventana elegida (la predeterminada es la 1)
opcs_input  = 2                # Opciones para la entrada del usuario (TODO: revisar valor por defecto)
subv_input  = 0                # Subventana para entrada del usuario (0 indica la actual)
limite      = [53, 25]         # Ancho y alto máximos absolutos de cada subventana
cursores    = [[0, 0],] * 8    # Posición relativa del cursor de cada subventana
cursores_at = [(0, 0),] * 8    # Posición relativa del cursor guardado mediante SAVEAT de cada subventana
subventanas = [[0, 0],] * 8    # Posición absoluta de cada subventana (de su esquina superior izquierda)
topes       = [[53, 25],] * 8  # Topes relativos de cada subventana de impresión
topes_gfx   = [53, 25]         # Ancho y alto del último gráfico dibujado en la subventana 0
resolucion  = (320, 200)       # Resolución gráfica de salida, sin escalar


def abre_ventana (traza, modoPantalla, bbdd):
  """Abre la ventana gráfica de la aplicación"""
  global escalada, modo, resolucion, ventana
  pygame.display.set_caption ('NAPS - ' + bbdd)
  modo = 'normal'
  if traza:
    ventana = pygame.display.set_mode ((780, 200))  # Ventana juego + banderas
  # Ventana juego sólo
  else:
    if limite[0] == 42:
      resolucion = (256, 192)
    if modoPantalla[:5] == 'scale' and modoPantalla[5].isdigit() and modoPantalla[-1] == 'x':
      factorEscala = int (modoPantalla[5])
      modo         = 'scale' + modoPantalla[5] + 'x'
      escalada     = pygame.display.set_mode ((resolucion[0] * factorEscala, resolucion[1] * factorEscala), pygame.RESIZABLE)
      ventana      = pygame.Surface (resolucion)
    else:
      ventana = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
  return
  # FIXME: si no funciona el modo gráfico, deja X Window mal permanentemente, aún al cerrarse el intérprete
  if modoPantalla == 'fullscreen':
    ventana = pygame.display.set_mode ((640, 400), ventana.get_flags() ^ pygame.FULLSCREEN)

def actualizaVentana ():
  if modo[:5] == 'scale':
    factorEscala = int (modo[5])
    pygame.transform.scale (ventana, (resolucion[0] * factorEscala, resolucion[1] * factorEscala), escalada)
  pygame.display.flip()

def redimensiona_ventana (evento = None):
  """Maneja eventos en relación a la ventana, como si se ha redimensionado o se le ha dado al aspa de cerrar"""
  global escalada, modo, ventana
  if not evento:
    if pygame.event.peek (pygame.VIDEORESIZE):  # Si ha ocurrido un evento de redimensión de ventana
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
  if evento.w < resolucion[0] or evento.h < resolucion[1]:
    modo       = 'normal'
    superficie = ventana.copy()
    ventana    = pygame.display.set_mode (resolucion, pygame.RESIZABLE)
    ventana.blit (superficie, (0, 0) + resolucion)
    actualizaVentana()
  else:
    if evento.w > (resolucion[0] * 2) or evento.h > (resolucion[1] * 2):
      factorEscala = 3
    elif evento.w > resolucion[0] or evento.h > resolucion[1]:
      factorEscala = 2
    modo       = 'scale' + str (factorEscala) + 'x'
    superficie = ventana.copy()
    escalada   = pygame.display.set_mode ((resolucion[0] * factorEscala, resolucion[1] * factorEscala), pygame.RESIZABLE)
    ventana    = superficie
    actualizaVentana()


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
  """Limpia la subventana de impresión"""
  if frase_guardada and texto_nuevo:
    espera_tecla()  # Esperamos pulsación de tecla si se habían entrado varias frases y se había mostrado texto nuevo
    del texto_nuevo[:]
  if not desdeCursor:
    cursores[elegida] = [0, 0]
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if elegida == 0:
    tope = topes_gfx
  inicio_x = (subventana[0] + cursor[0]) * 6  # Esquina superior izquierda X
  inicio_y = (subventana[1] + cursor[1]) * 8  # Esquina superior izquierda Y
  ancho    = math.ceil (((tope[0] - cursor[0]) * 6) / 8.) * 8  # Anchura del rectángulo a borrar
  alto     = (tope[1] - cursor[1]) * 8  # Altura del rectángulo a borrar
  # Los gráficos pueden dibujar hasta dos píxeles más allá de la última columna de texto
  if subventana[0] + tope[0] == 53:
    ancho += 2
  ventana.fill ((0, 0, 0), (inicio_x, inicio_y, ancho, alto))
  if not desdeCursor and not noRedibujar:
    actualizaVentana()
  if traza:
    prn ('Subventana', elegida, 'en', subventana, 'con topes', tope, 'limpiada y cursor en', cursores[elegida])

def borra_todo ():
  """Limpia la pantalla completa"""
  ventana.fill ((0, 0, 0), (0, 0) + resolucion)
  actualizaVentana()

def cambia_subv_input (stream, opciones):
  """Cambia la subventana de entrada por el stream dado, con las opciones dadas, según el condacto INPUT"""
  global subv_input, opcs_input
  subv_input = stream
  opcs_input = opciones

def cambia_topes (columna, fila):
  """Cambia los topes de la subventana de impresión elegida"""
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

# FIXME: Hay que dibujar sólo la región que no sale de los topes
def dibuja_grafico (numero, descripcion = False, parcial = False):
  """Dibuja un gráfico en la posición del cursor

El parámetro descripcion indica si se llama al describir la localidad
El parámetro parcial indica si es posible dibujar parte de la imagen"""
  tope = topes[elegida]
  if descripcion:
    if traza:
      prn ('Dibujo', numero, 'desde la descripción de la localidad, en (0, 0)')
  else:
    cursor     = cursores[elegida]
    subventana = subventanas[elegida]
    if traza:
      prn ('Dibujo', numero, 'sobre subventana', elegida, 'en', subventana,
           'con topes', tope, 'y cursor en', cursor)
  try:
    grafico = pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
  except Exception as e:
    if traza:
      prn ('Gráfico', numero, 'inválido o no encontrado en:', ruta_graficos)
      prn (e)
    return  # No dibujamos nada
  if elegida == 0:
    topes_gfx[0] = min (grafico.get_width()  // 8, limite[0])
    topes_gfx[1] = min (grafico.get_height() // 8, limite[1])
  if (descripcion or elegida == 0) and not parcial:
    ancho = tope[0] * 6
    # TODO: se centran los gráficos en la Aventura Original, pero no en El Jabato. Averiguar si es por el valor de alguna bandera
    if centrar_graficos and ancho > grafico.get_width():  # Centramos el gráfico
      destino      = ((ancho - grafico.get_width()) // 2, 0)
      topes_gfx[0] = min ((grafico.get_width() + (ancho - grafico.get_width()) // 2) // 8, limite[0])
    else:
      destino = (0, 0)
    ventana.blit (grafico, destino)
  else:
    # TODO: Asegurarse de si hay que tener en cuenta la posición del cursor
    ancho   = ((tope[0] - cursor[0]) * 6)  # Anchura del dibujo
    alto    = ((tope[1] - cursor[1]) * 8)  # Altura del dibujo
    destino = [(subventana[0] + cursor[0]) * 6, (subventana[1] + cursor[1]) * 8]
    if centrar_graficos and ancho > grafico.get_width():  # Centramos el gráfico
      destino[0] += (ancho - grafico.get_width()) // 2
    # Los gráficos pueden dibujar hasta dos píxeles más allá de la última columna de texto
    if ancho < grafico.get_width() and subventana[0] + tope[0] == 53:
      ancho += max (2, grafico.get_width() - ancho)
    ventana.blit (grafico, destino, (0, 0, ancho, alto))
  actualizaVentana()
  # TODO: Ver si hay que actualizar la posición del cursor (puede que no)

def elige_subventana (numero):
  """Selecciona una de las subventanas"""
  global elegida
  elegida = numero
  if traza:
    prn ('Subventana', elegida, 'elegida, en', subventanas[elegida],
         'con topes', topes[elegida], 'y cursor en', cursores[elegida])

def espera_tecla (tiempo = 0):
  """Espera hasta que se pulse una tecla (modificadores no), o hasta que pase tiempo segundos, si tiempo > 0"""
  pygame.time.set_timer (pygame.USEREVENT, tiempo * 1000)  # Ponemos el timer
  while True:
    evento = pygame.event.wait()
    if evento.type == pygame.KEYDOWN:
      if ((evento.key < 256) and (chr (evento.key) in teclas_edicion)) or evento.key in teclas_kp or evento.key in teclas_mas_256:
          pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
          return evento.key
    elif evento.type == pygame.USEREVENT:  # Tiempo de espera superado
      pygame.time.set_timer (pygame.USEREVENT, 0)  # Paramos el timer
      return None
    redimensiona_ventana (evento)

def carga_cursor ():
  """Carga la posición del cursor guardada de la subventana elegida """
  mueve_cursor (*cursores_at[elegida])

def guarda_cursor ():
  """Guarda la posición del cursor de la subventana elegida """
  cursores_at[elegida] = tuple (cursores[elegida])

def hay_grafico (numero):
  """Devuelve si existe el gráfico de número dado"""
  try:
    pygame.image.load (ruta_graficos + 'pic' + str (numero).zfill (3) + '.png')
  except Exception as e:
    if traza:
      prn ('Gráfico', numero, 'inválido o no encontrado en:', ruta_graficos)
      prn (e)
    return False
  return True

def insertaHastaMax (listaChrs, posInput, caracter, longMax):
  """Inserta el carácter dado a la posición de la lista de caracteres dada contenida en la lista posInput, si no superaría con ello la longitud máxima longMax. Incrementa la posición (valor entero) dentro de posInput si lo ha añadido"""
  if len (listaChrs) < longMax:
    listaChrs.insert (posInput[0], caracter)
    posInput[0] += 1

def lee_cadena (prompt, inicio, timeout, espaciar = False):
  """Lee una cadena (terminada con Enter) desde el teclado, dando realimentación al jugador

El parámetro prompt, es el mensaje de prompt
El parámetro inicio es la entrada a medias anterior
El parámetro timeout es una lista con el tiempo muerto, en segundos
El parámetro espaciar permite elegir si se debe dejar una línea en blanco tras el último texto"""
  posHistorial = len (historial)
  textoAntes   = False  # Si había texto en la subventana de entrada antes de la línea del prompt
  if subv_input:  # Guardamos la subventana que estaba elegida justo antes, y cambiamos a la de entrada
    global elegida
    if inicio:
      borra_orden()
    subvAntes = elegida
    elegida   = subv_input
    if cursores[elegida][0] > subventanas[elegida][0] and prompt[0] == '\n':  # Hay texto antes de la línea del prompt
      # Cambiamos la subventana de entrada para que omita el texto escrito antes, y así no lo borre
      cursores[elegida][0]     = subventanas[elegida][0]
      cursores[elegida][1]    += 1
      subventanas[elegida][1] += 1  # FIXME: no asumir que es una línea lo que se había ocupado antes del prompt en la subventana de entrada
      prompt     = prompt[1:]
      textoAntes = True
  elif espaciar and cursores[elegida][1] >= topes[elegida][1] - 2 and cursores[elegida][0]:
    prompt = '\n' + prompt  # Dejaremos una línea en blanco entre el último texto y el prompt
  # El prompt se imprimirá en la siguiente línea de la subventana de entrada
  imprime_cadena (prompt, False)
  entrada = []
  entrada.extend (list (inicio))  # Partimos la entrada anterior por caracteres
  longAntes = len (inicio) + 1  # Longitud de la entrada más el marcador (_) de entrada de carácter (porque está al final)
  longMax   = (topes[elegida][0] - cursores[elegida][0] - 1) + (topes[elegida][0] * (topes[elegida][1] - 1))  # Ancho máximo de la entrada
  posInput  = [len (inicio)]  # Posición del marcador (cursor) de entrada de carácter, inicialmente al final
  while True:
    realimentacion = ''.join (entrada)
    if subv_input:
      borra_pantalla (noRedibujar = True)
      imprime_cadena (prompt, False, False)
    else:
      diferencia = longAntes - (len (entrada) + (1 if posInput[0] == len (entrada) else 0))  # Caracteres de más antes vs. ahora
      if diferencia > 0:
        realimentacion += ' ' * (diferencia + 1)  # Para borrar el resto de la orden anterior
      longAntes = len (entrada) + (1 if posInput[0] == len (entrada) else 0)
    imprime_lineas (realimentacion.translate (iso8859_15_a_fuente), posInput[0])
    tecla = espera_tecla (timeout[0])

    if tecla == None:  # Tiempo muerto vencido
      timeout[0] = True
      if subv_input:
        borra_pantalla()  # Borramos la entrada realimentada en pantalla
        if textoAntes:
          subventanas[elegida][1] -= 1  # FIXME: no asumir que es una línea lo que se había ocupado antes del prompt en la subventana de entrada
        elegida = subvAntes  # Recuperamos la subventana elegida justo antes
      else:  # Quitamos el guión bajo del final de la entrada
        realimentacion = ''.join (entrada) + ' '  # El espacio borrará el guión bajo cuando estaba al final
        imprime_lineas (realimentacion.translate (iso8859_15_a_fuente))
      return ''.join (entrada)

    modificadores = pygame.key.get_mods()
    mayuscula     = (modificadores & pygame.KMOD_CAPS)  != 0  # Caps Lock activo
    altGr         = (modificadores & pygame.KMOD_MODE)  != 0
    control       = (modificadores & pygame.KMOD_CTRL)  != 0
    shift         = (modificadores & pygame.KMOD_SHIFT) != 0
    # Primero, tratamos los códigos superiores a 255
    if tecla in (pygame.K_KP_ENTER, pygame.K_RETURN):
      if entrada:
        break
      # Seguimos leyendo entrada del jugador si se pulsa Enter sin haber escrito nada
    elif tecla == 314:  # Alt Gr + `
      insertaHastaMax (entrada, posInput, '[', longMax)
    elif tecla in teclas_kp:
      insertaHastaMax (entrada, posInput, teclas_kp[tecla], longMax)
    elif tecla == pygame.K_LEFT:
      if control:  # Salta al inicio de palabras
        if posInput[0]:  # Sólo si no está al inicio del todo
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
    else:  # Código inferior a 256
      tecla = chr (tecla)
      if (tecla.isalpha() or tecla == ' ') and tecla != 'º':  # Una tecla de letra
        # Vemos si tenemos que añadirla en mayúscula o minúscula
        if todo_mayusculas or mayuscula ^ shift:
          tecla = tecla.upper()
        insertaHastaMax (entrada, posInput, tecla, longMax)
      elif tecla == '\b':  # La tecla Backspace, arriba del Enter
        entrada     = entrada[:posInput[0] - 1] + entrada[posInput[0]:]
        posInput[0] = max (0, posInput[0] - 1)
      elif not shift:  # Shift sin pulsar
        if altGr:  # Alt Gr pulsado
          if tecla in teclas_alt_gr:
            insertaHastaMax (entrada, posInput, teclas_alt_gr[tecla], longMax)
        elif (tecla in string.digits) or (tecla in "º'¡ñç<,.-+"):
          insertaHastaMax (entrada, posInput, tecla, longMax)  # Es válida tal cual
      elif tecla in teclas_shift:  # Shift está pulsado
        insertaHastaMax (entrada, posInput, teclas_shift[tecla], longMax)
  # Borramos la entrada realimentada en pantalla, sólo si no es en subventana propia (usar borra_orden en el otro caso)
  if subv_input:
    borra_pantalla (noRedibujar = True)
    imprime_cadena (prompt, False, False)
    realimentacion = ''.join (entrada) + ' '  # El espacio borrará el guión bajo
    imprime_lineas (realimentacion.translate (iso8859_15_a_fuente))
    if textoAntes:
      subventanas[elegida][1] -= 1  # FIXME: no asumir que es una línea lo que se había ocupado antes del prompt en la subventana de entrada
    elegida = subvAntes  # Recuperamos la subventana elegida
  else:
    borra_pantalla (True)
  if not subv_input or opcs_input & 2:  # Realimentación permanente de la orden, junto al texto del juego
    imprime_cadena (''.join (entrada) + ' ')
    imprime_cadena ('\n')
  # Guardamos la entrada en el historial
  if not historial or historial[-1] != entrada:
    historial.append (entrada)
  # Devolvemos la cadena
  return ''.join (entrada)

def imprime_banderas (banderas):
  """Imprime el contenido de las banderas (en la extensión de la ventana)"""
  global banderas_antes, banderas_viejas
  if banderas_antes == None:
    banderas_antes  = [0,] * 256
    banderas_viejas = set (range (256))
    # Seleccionamos el color de impresión
    fuente.set_palette (((0, 192, 192), (0, 0, 0)))
    # Imprimimos los índices de cada bandera
    for num in range (256):
      columna = 320 + ((num // 25) * 42)
      fila    = (num % 25) * 8
      cadena = str (num).zfill (3).translate (iso8859_15_a_fuente)
      for pos in range (3):
        c = ord (cadena[pos])
        ventana.blit (fuente, (columna + (pos * 6), fila),
                      ((c % 63) * 10, (c // 63) * 10, 6, 8))
  for num in range (256):
    # Sólo imprimimos cada bandera la primera vez y cuando cambie de color
    if (banderas[num] == banderas_antes[num]) and (num not in banderas_viejas):
      continue
    columna = 339 + ((num // 25) * 42)
    fila    = (num % 25) * 8
    cadena  = str (banderas[num]).zfill (3).translate (iso8859_15_a_fuente)
    # Seleccionamos el color de impresión
    if banderas_antes[num] != banderas[num]:
      banderas_antes[num] = banderas[num]
      banderas_viejas.add (num)
      fuente.set_palette (((64, 255, 0), (0, 0, 0)))
    else:  # La bandera estaba en banderas_viejas
      banderas_viejas.remove (num)
      if banderas[num] == 0:
        fuente.set_palette (((96, 96, 96), (0, 0, 0)))
      else:
        fuente.set_palette (((255, 255, 255), (0, 0, 0)))
    # Imprimimos los valores de cada bandera
    for pos in range (3):
      c = ord (cadena[pos])
      ventana.blit (fuente, (columna + (pos * 6), fila),
                    ((c % 63) * 10, (c // 63) * 10, 6, 8))
  actualizaVentana()
  fuente.set_palette (((255, 255, 255), (0, 0, 0)))

def imprime_cadena (cadena, scroll = True, redibujar = True):
  """Imprime una cadena en la posición del cursor (dentro de la subventana)

El cursor deberá quedar actualizado.

Si scroll es True, se desplazará el texto del buffer hacia arriba (scrolling) cuando se vaya a sobrepasar la última línea"""
  if not cadena:
    return
  if not texto_nuevo:
    texto_nuevo.append (True)
  cursor     = cursores[elegida]
  subventana = subventanas[elegida]
  tope       = topes[elegida]
  if cadena == '\n':  # TODO: sacar a función nueva_linea
    if cursor[1] >= tope[1] - 1:
      scrollLineas (1, subventana, tope)
    cursores[elegida] = [0, min (tope[1] - 1, cursor[1] + 1)]
    if traza:
      prn ('Nueva línea, cursor en', cursores[elegida])
    return
  if traza:
    prn ('Impresión sobre subventana', elegida, 'en', subventana, 'con topes',
         tope, 'y cursor en', cursor)
  # Convertimos la cadena a posiciones sobre la tipografía
  if todo_mayusculas and juego_alto and izquierda[juego_alto] in cadena:  # Se trata de SWAN
    # En la fuente alta sólo hay letras mayúsculas, así que las demás las ponemos como fuente baja
    juego    = False  # Si la parte actual de la cadena está en juego alto o no
    bajado   = False  # Si la parte actual de la cadena está pasada a juego bajo por letras no mayúsculas
    cambiada = ''     # Cadena cambiada teniendo en cuenta que en la fuente alta sólo hay letras mayúsculas
    for c in cadena:
      if c == izquierda[juego_alto]:  # Es el mismo carácter para alternar entre juego alto y bajo
        juego = not juego
        if not bajado:
          cambiada += c
        bajado = False
        continue
      if juego:
        if c.isupper():
          if bajado:
            bajado    = False
            cambiada += izquierda[juego_alto]
        elif not bajado:
          bajado    = True
          cambiada += izquierda[juego_alto]
      cambiada += c
    cadena = cambiada
  elif cambia_brillo:
    cadena, colores = parseaColores (cadena)
  convertida = cadena.translate (iso8859_15_a_fuente)
  # Dividimos la cadena en líneas
  juego     = 0    # 128 si está en el juego alto, 0 si no
  iniLineas = [0]  # Posición de inicio de cada línea, para colorear
  lineas    = []
  linea     = []
  restante  = tope[0] - cursor[0]  # Columnas restantes que quedan en la línea
  for c in convertida:
    ordinal = ord (c)
    if ((ordinal == len (izquierda) - 1) or  # Carácter nueva línea (el último)
        ((restante == 0) and (ordinal == 16))):  # Termina la línea con espacio
      lineas.append (''.join (linea))
      iniLineas.append (iniLineas[-1] + len (linea) + (1 if (ordinal == len (izquierda) - 1) else 0))
      linea    = []
      restante = tope[0]
    elif ordinal == juego_alto and juego == 0:
      juego = 128
    elif ordinal == juego_bajo:
      juego = 0
    elif restante > 0:
      linea.append (chr (ordinal + juego))
      restante -= 1
    else:  # Hay que partir la línea, desde el último carácter de espacio
      for i in range (len (linea) - 1, -1, -1):  # Desde el final al inicio
        if ord (linea[i]) == 16:  # Este carácter es un espacio
          lineas.append (''.join (linea[:i]))
          linea = linea[i + 1:]
          iniLineas.append (iniLineas[-1] + i)
          break
      else:  # Ningún carácter de espacio en la línea
        if len (linea) == tope[0]:  # La línea nunca se podrá partir limpiamente
          # La partimos suciamente (en mitad de palabra)
          lineas.append   (''.join (linea))
          iniLineas.append (iniLineas[-1] + len (linea))
          linea = []
        else:  # Lo que ya teníamos será para una nueva línea
          lineas.append (' '.translate (iso8859_15_a_fuente) * len (linea))  # TODO: revisar qué es esto y si es correcto
          iniLineas.append (iniLineas[-1] + len (linea))
      linea.append (chr (ordinal + juego))
      restante = tope[0] - len (linea)
  if linea:  # Queda algo en la última línea
    lineas.append (''.join (linea))
  # Hacemos scrolling antes de nada, en caso de que vaya a ser necesario
  # TODO: Esperar si se escriben más líneas que las que caben en la subventana
  #       i.e. paginar con pausa
  lineasAsubir = cursor[1] + len (lineas) - tope[1]
  if lineasAsubir > 0:  # Hay que desplazar el texto ese número de líneas
    scrollLineas (lineasAsubir, subventana, tope)
    cursor[1] -= lineasAsubir  # Actualizamos el cursor antes de imprimir
  # Imprimimos la cadena línea por línea
  for i in range (len (lineas)):
    if i > 0:  # Nueva línea antes de cada una, salvo la primera
      cursor = [0, cursor[1] + 1]
      cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
    if cambia_brillo:
      imprime_linea (lineas[i], redibujar = redibujar, colores = colores, inicioLinea = iniLineas[i])
    else:
      imprime_linea (lineas[i], redibujar = redibujar)
  if lineas:  # Había alguna línea
    if cadena[-1] == '\n':  # La cadena terminaba en nueva línea
      cursor = [0, cursor[1] + 1]
    else:
      cursor = [cursor[0] + len (lineas[-1]), cursor[1]]
    cursores[elegida] = cursor  # Actualizamos el cursor de la subventana
  if traza:
    prn ('Fin de impresión, cursor en', cursor)

def imprime_linea (linea, posInput = None, redibujar = True, colores = {}, inicioLinea = 0):
  """Imprime una línea de texto en la posición del cursor, sin cambiar el cursor

Los caracteres de linea deben estar convertidos a posiciones en la tipografía"""
  # Coordenadas de destino
  destinoX = (subventanas[elegida][0] + cursores[elegida][0]) * 6
  destinoY = (subventanas[elegida][1] + cursores[elegida][1]) * 8
  for i in range (len (linea)):
    c = ord (linea[i])
    if i + inicioLinea in colores:
      fuente.set_palette (colores[i + inicioLinea])
    # Curioso, aquí fuente tiene dos significados correctos :)
    # (SPOILER: Como sinónimo de origen y como sinónimo de tipografía)
    ventana.blit (fuente, (destinoX + (i * 6), destinoY),
                  ((c % 63) * 10, (c // 63) * 10, 6, 8))
  if posInput != None:
    ventana.blit (guion_bajo, (destinoX + (posInput * 6), destinoY), (0, 0, 6, 8))
  if redibujar:
    actualizaVentana()

def imprime_lineas (texto, posInput = None):
  """Imprime el texto en la posición del cursor, sin cambiar el cursor, partiendo por líneas si texto alcanza el tope de la subventana

Los caracteres de linea deben estar convertidos a posiciones en la tipografía"""
  cursor     = list (cursores[elegida])  # Copia del cursor, para recuperarlo después
  lineas     = []  # Líneas partidas como corresponde ("a lo bruto")
  maxPrimera = topes[elegida][0] - cursores[elegida][0]  # Anchura máxima de la primera línea
  posInputEn = 0   # En qué línea está el guión bajo de feedback gráfico de entrada
  if len (texto) < maxPrimera:
    lineas.append (texto)
  else:
    lineas.append (texto[:maxPrimera])
    inicio = maxPrimera
    fin    = maxPrimera + topes[elegida][0]
    if posInput >= inicio:
      posInputEn += 1
      posInput   -= maxPrimera
    while fin <= len (texto):
      lineas.append (texto[inicio:fin])
      inicio += topes[elegida][0]
      fin    += topes[elegida][0]
      if posInput >= inicio:
        posInputEn += 1
        posInput   -= topes[elegida][0]
    lineas.append (texto[inicio:fin])
  for l in range (len (lineas)):
    linea = lineas[l]
    if l:  # No es la primera línea
      cursores[elegida][0] = 0
      if posInput != None and subv_input:
      	scrollLineas (1, subventanas[elegida], topes[elegida], False)
      else:
      	cursores[elegida][1] += 1
    if posInputEn == l:
      imprime_linea (linea, posInput, False)
    else:
      imprime_linea (linea, redibujar = False)
  cursores[elegida] = cursor
  actualizaVentana()

def mueve_cursor (columna, fila = cursores[elegida][1]):
  """Cambia de posición el cursor de la subventana elegida"""
  cursores[elegida] = [columna, fila]
  subventana        = subventanas[elegida]
  tope              = topes[elegida]
  if traza:
    prn ('Subventana', elegida, 'en', subventana, 'con topes', tope,
         'y cursor movido a', cursores[elegida])

def prepara_topes (columnas, filas):
  """Inicializa los topes al número de columnas y filas dado"""
  global topes, topes_gfx
  limite[0] = columnas                  # Ancho máximo absoluto de cada subventana
  limite[1] = filas                     # Alto máximo absoluto de cada subventana
  topes     = [[columnas, filas],] * 8  # Topes relativos de cada subventana de impresión
  topes_gfx = [columnas,  filas]        # Ancho y alto del último gráfico dibujado en la subventana 0

def pos_subventana (columna, fila):
  """Cambia la posición de origen de la subventana de impresión elegida"""
  subventanas[elegida] = [columna, fila]
  # Ajustamos los topes para que no revasen el máximo permitido
  # No sé si DAAD hace esto, en caso de no usar el condacto WINSIZE
  # FIXME: Comprobar qué ocurre si no se usa WINSIZE, ¿se usan los topes
  #        anteriores, o se maximizan?
  topes[elegida] = [min (topes[elegida][0], limite[0] - columna),
                    min (topes[elegida][1], limite[1] - fila)]
  # Ponemos el cursor al origen de la subventana
  cursores[elegida] = [0, 0]
  if traza:
    prn ('Subventana', elegida, 'puesta en', subventanas[elegida], 'con topes',
         topes[elegida], 'y cursor en', cursores[elegida])

def reinicia_subventanas ():
  """Ajusta todas las subventanas de impresión a sus valores por defecto"""
  for i in range (num_subvens):
    cursores[i]    = [0, 0]
    subventanas[i] = [0, 0]
    topes[i]       = list (limite)
  topes_gfx = list (limite)
  if traza:
    prn ('Subventanas reiniciadas a [0, 0] con topes', limite,
         'y cursor en [0, 0]')


# Funciones auxiliares que sólo se usan en este módulo

def parseaColores (cadena):
  """Procesa los códigos de control de colores, devolviendo la cadena sin ellos, y un diccionario posición: colores a aplicar"""
  if not cambia_brillo:
    return cadena, {}
  brillo     = 0      # Sin brillo por defecto
  papel      = 0      # Color de papel/fondo por defecto (negro)
  tinta      = 7      # Color de tinta por defecto (blanco)
  sigBrillo  = False  # Si el siguiente carácter indica si se pone o quita brillo al color de tinta
  sigFlash   = False  # Si el siguiente carácter indica si se pone o quita efecto flash
  sigPapel   = False  # Si el siguiente carácter indica el color de papel/fondo
  sigTinta   = False  # Si el siguiente carácter indica el color de tinta
  sinColores = ''     # Cadena sin los códigos de control de colores
  colores    = {0: (paleta[brillo][tinta], (0, 0, 0))}
  for i in range (len (cadena)):
    c = ord (cadena[i])
    if sigBrillo or sigFlash or sigPapel or sigTinta:
      if sigBrillo:
        brillo    = 1 if c else 0
        sigBrillo = False
      elif sigFlash:
        sigFlash = False
      elif sigPapel:
        papel    = c % len (paleta[brillo])
        sigPapel = False
      else:
        sigTinta = False
        tinta    = c % len (paleta[brillo])
      colores[len (sinColores)] = (paleta[brillo][tinta], paleta[brillo][papel])  # Color de tinta y papel a aplicar
    elif c in (cambia_brillo, cambia_flash, cambia_papel, cambia_tinta):
      if c == cambia_brillo:
        sigBrillo = True
      elif c == cambia_flash:
        sigFlash = True
      elif c == cambia_papel:
        sigPapel = True
      else:
        sigTinta = True
    elif cadena[i] in noEnFuente:
      sinColores += noEnFuente[cadena[i]]
    else:
      sinColores += cadena[i]
  if version_info[0] < 3:  # La versión de Python es 2.X
    sinColores = sinColores.encode ('iso-8859-15')
  return sinColores, colores

def scrollLineas (lineasAsubir, subventana, tope, redibujar = True):
  """Hace scroll gráfico del número dado de líneas, en la subventana dada, con topes dados"""
  destino = (subventana[0] * 6, subventana[1] * 8)  # Posición de destino
  origenX = subventana[0] * 6  # Coordenada X del origen (a subir)
  origenY = (subventana[1] + lineasAsubir) * 8  # Coordenada Y del origen
  anchura = tope[0] * 6  # Anchura del área a subir
  altura  = (tope[1] - lineasAsubir) * 8  # Altura del área a subir
  # Copiamos las líneas a subir
  ventana.blit (ventana, destino, (origenX, origenY, anchura, altura))
  # Borramos el hueco
  origenY = (subventana[1] + tope[1] - lineasAsubir) * 8
  altura  = lineasAsubir * 8
  ventana.fill ((0, 0, 0), (origenX, origenY, anchura, altura))
  if redibujar:
    actualizaVentana()
