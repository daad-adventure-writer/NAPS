#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Entorno de desarrollo integrado (IDE), hecho con PyQt
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

from alto_nivel import *
from prn_func   import _, prn

import argparse    # Para procesar argumentos de l�nea de comandos
import functools   # Para partial
import locale      # Para codificar bien la salida est�ndar
import os          # Para curdir, listdir y path
import subprocess  # Para ejecutar el int�rprete
import sys
import time        # Para evitar reapertura indeseada de modal
import types       # Para poder comprobar si algo es una funci�n

try:
  from PyQt4.QtCore import *
  from PyQt4.QtGui  import *
  vers_pyqt = 4
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtGui     import *
  from PyQt5.QtWidgets import *
  vers_pyqt = 5


dlg_abrir       = None  # Di�logo de abrir fichero
dlg_acerca_de   = None  # Di�logo "Acerca de"
dlg_banderas    = None  # Di�logo para consultar y modificar las banderas
dlg_contadores  = None  # Di�logo de contadores
dlg_fallo       = None  # Di�logo para mostrar fallos leves
dlg_guardar     = None  # Di�logo de guardar fichero
dlg_desc_locs   = None  # type: QTableView|None # Di�logo para consultar y modificar los datos de localidades
dlg_desc_objs   = None  # type: QTableView|None # Di�logo para consultar y modificar los datos de objetos
dlg_msg_sys     = None  # type: QTableView|None # Di�logo para consultar y modificar los mensajes de sistema
dlg_msg_usr     = None  # type: QTableView|None # Di�logo para consultar y modificar los mensajes de usuario
dlg_procesos    = None  # type: QWidget|None    # Di�logo para consultar y modificar las tablas de proceso
dlg_vocabulario = None  # type: QTableView|None # Di�logo para consultar y modificar el vocabulario
mdi_banderas    = None  # Subventana MDI para dlg_banderas
mdi_desc_locs   = None  # Subventana MDI para dlg_desc_locs
mdi_desc_objs   = None  # Subventana MDI para dlg_desc_objs
mdi_msg_sys     = None  # Subventana MDI para dlg_msg_sys
mdi_msg_usr     = None  # Subventana MDI para dlg_msg_usr
mdi_procesos    = None  # Subventana MDI para dlg_procesos
mdi_vocabulario = None  # Subventana MDI para dlg_vocabulario
mdi_juego       = None  # Subventana MDI para la pantalla de juego del int�rprete

campo_txt = None  # El campo de texto    del di�logo de procesos
pestanyas = None  # La barra de pesta�as del di�logo de procesos

mod_actual      = None    # M�dulo de librer�a activo
pal_sinonimo    = dict()  # Sin�nimos preferidos para cada par c�digo y tipo v�lido
pals_mov        = []      # C�digos de palabra de movimiento en el vocabulario y conexiones
pals_no_existen = []      # C�digos de palabra que no existen encontrados en tablas de proceso
pals_salida     = []      # C�digos de palabra que se usan como salida en la tabla de conexiones

color_base      = QColor (10, 10, 10)   # Color de fondo gris oscuro
color_pila      = QColor (60, 35, 110)  # Color de fondo azul brillante
color_tope_pila = QColor (35, 40, 110)  # Color de fondo morado oscuro
inicio_debug    = False  # Para hacer la inicializaci�n de subventanas MDI al lanzar depuraci�n
modo_claro      = False  # Si se muestra la interfaz en modo claro u oscuro
pila_procs      = []     # Pila con estado de los procesos en ejecuci�n
proc_interprete = None   # Proceso del int�rprete
puntos_ruptura  = {}     # Puntos de ruptura donde pausar la ejecuci�n, indexados por proceso
tam_fuente      = 12     # El tama�o de fuente para el di�logo de procesos

# Identificadores (para hacer el c�digo m�s legible) predefinidos
IDS_LOCS = {
  'GAC': {
    0:     'NOTCREATED',
           'NOTCREATED': 0,
    32767: 'CARRIED',
           'CARRIED': 32767},
  None: {
    0:   'INITIAL',
         'INITIAL': 0,
    252: 'NOTCREATED',
         'NOTCREATED': 252,
         '_': 252,
    253: 'WORN',
         'WORN': 253,
    254: 'CARRIED',
         'CARRIED': 254,
    255: 'HERE',
         'HERE': 255}
}

# Conversi�n de teclas para manejo del int�rprete
conversion_teclas = {Qt.Key_Escape: 27, Qt.Key_Down: 80, Qt.Key_End: 79, Qt.Key_Home: 71, Qt.Key_Left: 75, Qt.Key_Right: 77, Qt.Key_Up: 72}

# Estilos CSS para el di�logo de banderas
estilo_banderas   = ''
estilo_cambiada   = 'color: #0f0'
estilo_fila_par   = ''
estilo_fila_impar = ''


# Funciones de exportaci�n e importaci�n, con sus m�dulos, extensiones y descripciones
info_exportar = []
info_importar = []
# Funciones de nueva base de datos, con sus m�dulos
info_nueva = []

# Pares nombre y tipos posibles que deben tener los m�dulos de librer�a
nombres_necesarios = (('acciones',          dict),
                      ('cadena_es_mayor',   types.FunctionType),
                      ('condiciones',       dict),
                      ('conexiones',        (dict, list)),
                      ('desc_locs',         (dict, list)),
                      ('desc_objs',         (dict, list)),
                      ('func_nueva',        str),
                      ('funcs_exportar',    tuple),
                      ('funcs_importar',    tuple),
                      ('escribe_secs_ctrl', types.FunctionType),
                      ('INDIRECCION',       bool),
                      ('lee_secs_ctrl',     types.FunctionType),
                      ('locs_iniciales',    (dict, list)),
                      ('LONGITUD_PAL',      int),
                      ('msgs_sys',          (dict, list)),
                      ('msgs_usr',          list),
                      ('NOMB_COMO_VERB',    list),
                      ('NOMBRE_SISTEMA',    str),
                      ('nombres_objs',      (dict, list)),
                      ('NUM_ATRIBUTOS',     list),
                      ('NUM_BANDERAS',      list),
                      ('PREP_COMO_VERB',    int),
                      ('tablas_proceso',    (dict, list)),
                      ('TIPOS_PAL',         tuple),
                      ('vocabulario',       list))


argparse._ = _  # Para la localizaci�n de textos


class BarraIzquierda (QWidget):
  """Barra vertical del margen izquierdo del campo de texto, para puntos de ruptura"""
  anchoBarra = 20  # Ancho en p�xeles de esta barra
  diametro   = 16  # Di�metro del c�rculo indicador de punto de ruptura
  margenHor  = 2   # Margen horizontal para el indicador de punto de ruptura

  def __init__ (self, parent):
    QWidget.__init__ (self, parent)

  def enterEvent (self, evento):
    selector.statusBar().showMessage (_('Adds or removes breakpoints'))

  def leaveEvent (self, evento):
    selector.statusBar().clearMessage()

  def mousePressEvent (self, evento):
    """A�ade o elimina punto de ruptura al pulsar el rat�n en la barra"""
    linea = campo_txt.cursorForPosition (evento.pos()).block()
    numEntrada, posicion = campo_txt._daNumEntradaYLinea (linea)
    if posicion == 1:  # Es la l�nea en blanco tras la cabecera de entrada
      return
    numProceso = pestanyas.currentIndex()
    proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso de la posici�n pulsada
    if not proceso[0]:  # El proceso no tiene entradas
      return
    entrada     = proceso[1][numEntrada]  # La entrada de la posici�n pulsada
    numCondacto = max (-1, posicion - 2)
    if numCondacto >= len (entrada):  # Es alguna de las l�neas en blanco al final de la entrada
      return
    puntoRuptura = (numEntrada, numCondacto, posicion)
    if numProceso not in puntos_ruptura:
      puntos_ruptura[numProceso] = []
    if puntoRuptura in puntos_ruptura[numProceso]:
      puntos_ruptura[numProceso].remove (puntoRuptura)
    else:
      puntos_ruptura[numProceso].append (puntoRuptura)
      puntos_ruptura[numProceso].sort()  # Se necesita ordenado
    enviaPuntoRuptura (numProceso, numEntrada, numCondacto)
    self.update()

  def paintEvent (self, evento):
    painter = QPainter (self)
    painter.fillRect (evento.rect(), Qt.lightGray if modo_claro else Qt.darkGray)
    numProceso = pestanyas.currentIndex()
    if numProceso not in puntos_ruptura or not puntos_ruptura[numProceso]:
      return
    linea = campo_txt.cursorForPosition (QPoint (0, 0)).block()
    numEntrada, posicion = campo_txt._daNumEntradaYLinea (linea)
    # Saltamos puntos de ruptura anteriores a esta posici�n (est�n ordenados)
    for p in range (len (puntos_ruptura[numProceso])):
      if puntos_ruptura[numProceso][p][0] > numEntrada or (puntos_ruptura[numProceso][p][0] == numEntrada and puntos_ruptura[numProceso][p][2] >= posicion):
        break
    else:  # No hay puntos de ruptura en este proceso desde la primera l�nea visible en adelante
      return
    # Detectamos si al inicio del campo de texto hay una l�nea incompleta o margen antes de la primera l�nea
    alturaLinea = tam_fuente   # Sirve como cota inferior
    for i in range (1, alturaLinea * 2, 2):
      sigLinea    = campo_txt.cursorForPosition (QPoint (0, i)).block()
      sigPosicion = campo_txt._daNumEntradaYLinea (sigLinea)[1]
      if sigPosicion != posicion:  # Ya es la siguiente l�nea
        break
    else:  # Margen superior del campo de texto mayor de lo esperado
      # Puede ocurrir mientras se redibuja el campo de texto, y cuando la l�nea ocupa varias
      i = alturaLinea + 1
    # Dibujamos donde corresponda los marcadores de punto de ruptura visibles
    margenSup      = i - alturaLinea - 1  # Espacio que precede a la primera l�nea, por margen o por estar incompleta
    lineasVisibles = ((self.size().height() - abs (margenSup)) // alturaLinea) + (1 if margenSup < 0 else 0) + 1
    painter.setBrush (Qt.red)
    l        = 0          # �ndice de l�nea actual
    coordY   = margenSup  # Coordenada y que se comprobar� para saber qu� l�nea es
    posAntes = -2         # Posici�n encontrada anteriormente, para distinguir cu�ndo cambia la l�nea
    while p < len (puntos_ruptura[numProceso]) and l < lineasVisibles:
      linea = campo_txt.cursorForPosition (QPoint (0, max (0, coordY))).block()
      numEntrada, posicion = campo_txt._daNumEntradaYLinea (linea)
      if posicion == posAntes:  # Todav�a es la misma l�nea
        coordY += alturaLinea
        continue
      posAntes = posicion
      if puntos_ruptura[numProceso][p][0] == numEntrada and puntos_ruptura[numProceso][p][2] == posicion:
        # Buscamos exactamente el primer p�xel donde empieza
        y = coordY
        for y in range (coordY - 1, max (0, coordY - 2 * alturaLinea), -1):
          linea = campo_txt.cursorForPosition (QPoint (0, y)).block()
          if campo_txt._daNumEntradaYLinea (linea)[1] != posicion:
            break
        # Dibujamos el marcador de punto de ruptura
        painter.drawEllipse (self.margenHor, y + (alturaLinea - self.diametro) // 2, self.diametro, self.diametro)
        p += 1
      l += 1

  def wheelEvent (self, evento):
    """Pasa el evento al campo de texto, para hacer scroll y cambiar el zoom como si fuera el mismo widget"""
    campo_txt.wheelEvent (evento)

class CampoTexto (QTextEdit):
  """Campo de texto para las tablas de proceso"""
  def __init__ (self, parent):
    QTextEdit.__init__ (self, parent)
    self.actualizandoProceso = QTimer()
    self.actualizandoProceso.setSingleShot (True)
    self.actualizandoProceso.timeout.connect (actualizaProceso)
    self.barra = BarraIzquierda (self)
    self.setViewportMargins (self.barra.anchoBarra, 0, 0, 0)
    # Construimos variables necesarias para la introducci�n de condactos
    self.condactos        = {}     # Informaci�n completa de los condactos indexada por nombre
    self.condactosPorCod  = {}     # Nombre de condactos indexado por c�digo
    self.listaAcciones    = set()  # Lista de nombres de acciones
    self.listaCondiciones = set()  # Lista de nombres de condiciones
    for codigo, condacto in mod_actual.acciones.items():
      if mod_actual.NOMBRE_SISTEMA == 'QUILL':
        codigo += 100
      self.listaAcciones.add (condacto[0])
      self.condactos[condacto[0]]  = condacto + (codigo,)
      self.condactosPorCod[codigo] = condacto[0]
    for codigo, condacto in mod_actual.condiciones.items():
      self.listaCondiciones.add (condacto[0])
      self.condactos[condacto[0]]  = condacto + (codigo,)
      self.condactosPorCod[codigo] = condacto[0]

  def _daColsValidas (self, textoLinea):
    """Devuelve las posiciones v�lidas para el cursor en la l�nea de tabla de proceso con texto dado"""
    colsValidas  = []
    espacioAntes = False
    for c in range (len (textoLinea)):
      if textoLinea[c] == ' ':
        espacioAntes = True
        continue
      if espacioAntes:
        if textoLinea[c] == '"':
          colsValidas.append (c + 1)
          break  # Dejamos de buscar nada m�s tras encontrar comillas
        colsValidas.append (c)
        espacioAntes = False
    colsValidas.append (len (textoLinea))
    return colsValidas

  def _daColValida (self, numColumna, textoLinea, colsValidas = None):
    """Devuelve la posici�n v�lida m�s cercana para el cursor en la columna dada de la l�nea de tabla de proceso con texto dado"""
    if colsValidas == None:
      colsValidas = self._daColsValidas (textoLinea)
    if numColumna in colsValidas:
      return numColumna  # Era v�lida
    # Buscamos la columna v�lida m�s cercana
    for c in range (len (colsValidas)):
      if colsValidas[c] < numColumna:
        continue
      if c:  # No es la primera
        # Nos quedamos con la m�s cercana de entre la de la posici�n actual y la anterior
        if abs (numColumna - colsValidas[c]) > abs (numColumna - colsValidas[c - 1]):
          return colsValidas[c - 1]
      return colsValidas[c]
    return colsValidas[-1]  # La �ltima es la m�s cercana

  def _daNumEntradaYLinea (self, bloqueLinea):
    """Devuelve el n�mero de entrada de proceso y el de la l�nea en la entrada del bloque QTextBlock dado"""
    # Buscamos la l�nea de cabecera de la entrada, para obtener de all� el n�mero de entrada del proceso
    cabecera = bloqueLinea
    posicion = 0  # El n�mero de l�nea en la entrada donde est� el cursor
    if cabecera.userState() == -1:
      while cabecera.previous().isValid():
        cabecera  = cabecera.previous()
        posicion += 1
        if cabecera.userState() > -1:
          break
    numEntrada = cabecera.userState()
    return numEntrada, posicion

  def centraLineaCursor (self):
    """Centra verticalmente la l�nea del cursor actual"""
    lineasVisibles = self.size().height() / float (self.cursorRect().height())
    cursor   = self.textCursor()
    posicion = cursor.position()
    self.moveCursor (QTextCursor.End)  # Vamos al final, para que al ir a la l�nea que toca, esa quede arriba
    cursor.movePosition (QTextCursor.Up, n = int (lineasVisibles // 2) - 1)
    self.setTextCursor  (cursor)
    cursor.setPosition  (posicion)
    cursor.movePosition (QTextCursor.Right, n = 2)
    self.setTextCursor  (cursor)

  def contextMenuEvent (self, evento):
    linea      = self.cursorForPosition (evento.pos()).block()
    numEntrada = self._daNumEntradaYLinea (linea)[0]
    # prn ('N� l�nea:', linea.blockNumber())
    # prn ('N� entrada guardado en la l�nea:', linea.userState())
    # prn ('N� entrada guardado en cabecera:', cabecera.userState())
    # prn ('Texto de la l�nea:', linea.text())
    contextual = self.createStandardContextMenu()
    # Deshabilitamos al menos de momento las acciones de cortar, pegar y eliminar
    for accion in contextual.actions():
      if 'Ctrl+V' in accion.text() or 'Ctrl+X' in accion.text() or 'Delete' in accion.text():
        accion.setEnabled (False)
    menuEliminar = QMenu (_('Delete'), contextual)
    accionAntes    = QAction (_('Add entry &before'), contextual)
    accionDespues  = QAction (_('Add entry &after'),  contextual)
    accionElimEnt  = QAction (_('This entry'),        selector)  # Necesario poner como padre selector...
    accionElimTodo = QAction (_('All entries'),       selector)  # ... para que funcionen los status tips
    if numEntrada == -1 or self.textCursor().hasSelection():
      menuEliminar.setEnabled (False)
    if self.textCursor().hasSelection():
      accionAntes.setEnabled (False)
      accionDespues.setEnabled (False)
    accionElimTodo.setStatusTip (_('Deletes all entries in the process'))
    accionElimEnt.triggered.connect  (lambda: quitaEntradaProceso (numEntrada))
    accionElimTodo.triggered.connect (quitaEntradasProceso)
    accionAntes.triggered.connect    (lambda: nuevaEntradaProceso (numEntrada))
    accionDespues.triggered.connect  (lambda: nuevaEntradaProceso (numEntrada + 1))
    menuEliminar.addAction (accionElimEnt)
    menuEliminar.addAction (accionElimTodo)
    contextual.addSeparator()
    contextual.addAction (accionAntes)
    contextual.addAction (accionDespues)
    contextual.addMenu   (menuEliminar)
    contextual.addAction (_('&Go to entry'), irAEntradaProceso, 'Ctrl+G')
    contextual.exec_ (evento.globalPos())

  def irAEntrada (self, numEntrada):
    """Mueve el cursor a la entrada dada del proceso actual, y devuelve el bloque de su l�nea de cabecera"""
    cursor = self.textCursor()
    cursor.movePosition (QTextCursor.Start)
    linea = cursor.block()
    if not linea.text() or linea.userState() != 0:
      return  # Algo inesperado: la primera l�nea del proceso no es la primera cabecera
    entradaActual = 0
    while entradaActual < numEntrada and linea.next().isValid():
      linea = linea.next()
      if linea.userState() > -1:
        entradaActual = linea.userState()
    cursor.setPosition (linea.position())
    self.setTextCursor (cursor)
    return linea

  def irAEntradaYCondacto (self, numEntrada, numCondacto):
    """Mueve el cursor a la entrada y condacto en �sta dados del proceso actual"""
    linea = self.irAEntrada (numEntrada)
    if numCondacto > -1:  # No se estaba comprobando encaje con la cabecera de la entrada
      condactoActual = -2
      while condactoActual < numCondacto and linea.next().isValid():
        linea = linea.next()
        condactoActual += 1
        if linea.userState() > -1:
          break  # No deber�a ocurrir: hemos encontrado la cabecera de la siguiente entrada
      cursor = self.textCursor()
      cursor.setPosition (linea.position())
      self.setTextCursor (cursor)

  def keyPressEvent (self, evento):
    global tam_fuente
    if evento.key() in (Qt.Key_Down, Qt.Key_End, Qt.Key_Home, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up):
      cursor = self.textCursor()
      if evento.key() in (Qt.Key_Down, Qt.Key_Up):
        if evento.key() == Qt.Key_Up:
          cursor.movePosition (QTextCursor.StartOfBlock)  # Hace que funcione en l�neas con ajuste de l�nea
          cursor.movePosition (QTextCursor.Up)
        else:
          cursor.movePosition (QTextCursor.EndOfBlock)  # Hace que funcione en l�neas con ajuste de l�nea
          cursor.movePosition (QTextCursor.Down)
        cursor.movePosition (QTextCursor.StartOfBlock)
        if cursor.block().text():
          cursor.movePosition (QTextCursor.WordRight)
      elif evento.key() == Qt.Key_Home:
        cursor.movePosition (QTextCursor.StartOfBlock)
        if cursor.block().text():
          cursor.movePosition (QTextCursor.WordRight)
      elif evento.key() == Qt.Key_End:
        cursor.movePosition (QTextCursor.EndOfBlock)
      else:  # Flecha izquierda o derecha
        colsValidas = self._daColsValidas (cursor.block().text())
        columna     = self._daColValida (cursor.positionInBlock(), cursor.block().text(), colsValidas)
        posColumna  = colsValidas.index (columna)
        if evento.key() == Qt.Key_Left:
          colNueva = colsValidas[max (0, posColumna - 1)]
        else:
          colNueva = colsValidas[min (posColumna + 1, len (colsValidas) - 1)]
        cursor.setPosition (cursor.position() + (colNueva - columna))
      self.setTextCursor (cursor)
    elif evento.key() == Qt.Key_Backspace:
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      numEntrada, posicion = self._daNumEntradaYLinea (linea)
      numProceso = pestanyas.currentIndex()
      proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
      entrada    = proceso[1][numEntrada]  # La entrada seleccionada
      if posicion > 1 and posicion < len (entrada) + 2 and columna == len (linea.text()):  # S�lo si est� al final de una l�nea de condacto
        del entrada[posicion - 2]
        cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
        self.setTextCursor (cursor)
        self.cut()
        # Actualizamos los puntos de ruptura necesarios de la entrada
        if numProceso in puntos_ruptura:
          # Quitamos punto de ruptura del condacto quitado si ten�a
          if (numEntrada, posicion - 2, posicion) in puntos_ruptura[numProceso]:
            puntos_ruptura[numProceso].remove ((numEntrada, posicion - 2, posicion))
          # Saltamos puntos de ruptura anteriores a la posici�n del condacto quitado
          e = 0
          while e < len (puntos_ruptura[numProceso]):
            if puntos_ruptura[numProceso][e][0] > numEntrada or (puntos_ruptura[numProceso][e][0] == numEntrada and puntos_ruptura[numProceso][e][2] > posicion):
              break
            e += 1
          # Actualizamos los puntos de ruptura de condactos en la entrada posteriores al quitado
          for pe in range (e, len (puntos_ruptura[numProceso])):
            if puntos_ruptura[numProceso][pe][0] > numEntrada:
              break
            puntos_ruptura[numProceso][pe] = (puntos_ruptura[numProceso][pe][0], puntos_ruptura[numProceso][pe][1] - 1, puntos_ruptura[numProceso][pe][2] - 1)
    elif evento.key() == Qt.Key_Insert:
      if self.overwriteMode():
        self.setCursorWidth   (1)
        self.setOverwriteMode (False)
      else:
        self.setCursorWidth   (int (tam_fuente * 0.7))
        self.setOverwriteMode (True)
    elif evento.modifiers() & Qt.ControlModifier:  # Teclas de acci�n
      if evento.key() in (Qt.Key_Minus, Qt.Key_Plus):
        cursor = self.textCursor()
        self.selectAll()
        if evento.key() == Qt.Key_Minus:
          tam_fuente -= 2
        else:
          tam_fuente += 2
        if self.overwriteMode():
          self.setCursorWidth (int (tam_fuente * 0.7))
        fuente = self.font()
        fuente.setPixelSize (tam_fuente)
        self.setFont (fuente)
        self.setTextCursor (cursor)
        if accMostrarRec.isChecked():  # Recortar al ancho de l�nea disponible
          self.actualizandoProceso.start (100)
      elif evento.key() == Qt.Key_G:
        irAEntradaProceso()
      elif evento.key() not in (Qt.Key_V, Qt.Key_X):  # Descartamos las combinaciones de pegar y cortar
        super (CampoTexto, self).keyPressEvent (evento)
    elif proc_interprete:
      return  # No se puede modificar nada cuando la BD est� en ejecuci�n
    # Teclas que pueden causar modificaci�n de la tabla de procesos
    if str (evento.text()).isalpha():  # Letras
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      colsValidas = self._daColsValidas (linea.text())
      if columna not in (colsValidas[0], colsValidas[-1]):
        return  # Intentando escribir texto donde no es posible
      if linea.text() and linea.userState() == -1:  # Una l�nea de entrada que no es la cabecera
        numEntrada, posicion = self._daNumEntradaYLinea (linea)
        numProceso = pestanyas.currentIndex()
        proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
        entrada    = proceso[1][numEntrada]  # La entrada seleccionada
        if self.overwriteMode() and posicion > 1 and posicion < len (entrada) + 2:
          dialogo = ModalEntrada (self, _('Choose a condact:'), evento.text(), self.condactosPorCod[entrada[posicion - 2][0]])
        else:
          dialogo = ModalEntrada (self, _('Choose a condact:'), evento.text())
        dialogo.setComboBoxEditable (True)
        condactosParaCombo = self.condactos.keys()
        if mod_actual.NOMBRE_SISTEMA == 'QUILL' and len (entrada):
          # Detectamos los tipos de condactos que pueden ir en esta posici�n
          if posicion == 1 or (posicion == 2 and columna == colsValidas[0]):  # Posici�n antes del inicio de la entrada
            if entrada[0][0] < 100:                       # Si el primer condacto es una condici�n...
              condactosParaCombo = self.listaCondiciones  # ...s�lo puede ir una condici�n en esta posici�n
          elif (posicion > len (entrada) + 1) or ((posicion == len (entrada) + 1) and columna == colsValidas[-1]):  # Posici�n tras el final de la entrada
            if entrada[-1][0] >= 100:                  # Si el �ltimo condacto es una acci�n...
              condactosParaCombo = self.listaAcciones  # ...s�lo puede ir una acci�n en esta posici�n
          else:  # Posici�n con alg�n condacto por delante y por detr�s
            indiceAntes   = posicion - (2 + (1 if columna == colsValidas[0] else 0))   # �ndice del condacto anterior a la posici�n
            indiceDespues = (posicion - 2) + (1 if columna == colsValidas[-1] else 0)  # �ndice del siguiente condacto a la posici�n
            # Si la entrada es v�lida, las dos condiciones siguientes son mutuamente exclusivas
            if entrada[indiceAntes][0] >= 100:         # Si el condacto anterior es una acci�n...
              condactosParaCombo = self.listaAcciones  # ...s�lo puede ir una acci�n en esta posici�n
            elif entrada[indiceDespues][0] < 100:         # Si el siguiente condacto es una condici�n...
              condactosParaCombo = self.listaCondiciones  # ...s�lo puede ir una condici�n en esta posici�n
          for e in range (len (entrada)):
            condacto, parametros = entrada[e]
        dialogo.setComboBoxItems (sorted (condactosParaCombo))
        if dialogo.exec_() == QDialog.Accepted:
          nomCondacto = str (dialogo.textValue()).upper()
          if nomCondacto not in self.condactos:
            muestraFallo (_('Invalid condact'), _('Condact with name %s not available for this system or platform') % nomCondacto)
          elif nomCondacto not in condactosParaCombo:
            muestraFallo (_('Invalid condact'), _('%s cannot be entered on this position') % (_('A condition') if condactosParaCombo == self.listaAcciones else _('An action')))
          else:
            condacto   = self.condactos[nomCondacto]
            lineaNueva = [condacto[-1], [0] * len (condacto[1])]  # C�digo y par�metros de la nueva l�nea
            if posicion > 1:  # Si no a�ade al inicio de la entrada
              if self.overwriteMode():
                cursor.movePosition (QTextCursor.EndOfBlock)
                cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
                parametros    = entrada[posicion - 2][1]  # Conservaremos par�metros anteriores
                lineaNueva[1] = parametros[: len (condacto[1])] + ([0] * (max (0, len (condacto[1]) - len (parametros))))
              elif columna < len (linea.text()) or posicion == len (entrada) + 2:  # No es fin de l�nea o es final de entrada
                cursor.movePosition (QTextCursor.Up)
                cursor.movePosition (QTextCursor.EndOfBlock)
              self.setTextCursor (cursor)
            imprimeCondacto (*lineaNueva)
            cursor = self.textCursor()
            if posicion == 1:  # A�adir al inicio de la entrada
              entrada.insert (0, lineaNueva)
              cursor.movePosition (QTextCursor.Down)
              cursor.movePosition (QTextCursor.StartOfBlock)
              cursor.movePosition (QTextCursor.WordRight)
            elif posicion < len (entrada) + 2:
              if self.overwriteMode():  # Modificar un condacto ya existente en la entrada, conservando par�metros
                entrada[posicion - 2] = lineaNueva
              elif columna < len (linea.text()):  # No es fin de l�nea, a�ade antes
                entrada.insert (posicion - 2, lineaNueva)
              else:  # Es fin de l�nea, a�ade despu�s
                entrada.insert (posicion - 1, lineaNueva)
            else:  # A�adir al final de la entrada
              entrada.append (lineaNueva)
              if not condacto[1]:  # El nuevo condacto no tiene par�metros
                cursor.movePosition (QTextCursor.Down)
                cursor.movePosition (QTextCursor.EndOfLine)
            if condacto[1]:  # Si el nuevo condacto tiene par�metros, mueve cursor al primero
              cursor.movePosition (QTextCursor.StartOfBlock)
              cursor.movePosition (QTextCursor.WordRight, n = 2)
            self.setTextCursor (cursor)
            # Actualizamos los puntos de ruptura de condactos en la entrada posteriores al a�adido
            if numProceso in puntos_ruptura and not self.overwriteMode() and posicion < len (entrada) + 1:
              if columna >= len (linea.text()):  # Era fin de l�nea, condacto a�adido despu�s
                posicion += 1
              # Saltamos puntos de ruptura anteriores a la posici�n del condacto a�adido
              e = 0
              while e < len (puntos_ruptura[numProceso]):
                if puntos_ruptura[numProceso][e][0] > numEntrada or (puntos_ruptura[numProceso][e][0] == numEntrada and puntos_ruptura[numProceso][e][2] >= posicion):
                  break
                e += 1
              # Actualizamos los puntos de ruptura de condactos en la entrada posteriores al a�adido
              for pe in range (e, len (puntos_ruptura[numProceso])):
                if puntos_ruptura[numProceso][pe][0] > numEntrada:
                  break
                puntos_ruptura[numProceso][pe] = (puntos_ruptura[numProceso][pe][0], puntos_ruptura[numProceso][pe][1] + 1, puntos_ruptura[numProceso][pe][2] + 1)
      elif linea.userState() > -1:  # Estamos en la cabecera
        prn ('En cabecera')
    elif evento.key() in (Qt.Key_At, Qt.Key_BracketLeft) and mod_actual.INDIRECCION:
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      colsValidas = self._daColsValidas (linea.text())
      if not linea.text().trimmed() or linea.userState() > -1:
        return  # Intentando cambiar indirecci�n en l�nea sin condacto
      numEntrada, posicion = self._daNumEntradaYLinea (linea)
      numProceso = pestanyas.currentIndex()
      proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
      entrada    = proceso[1][numEntrada]  # La entrada seleccionada
      condacto   = entrada[posicion - 2]
      lineaNueva = (condacto[0] ^ 128, condacto[1])  # Alternamos indirecci�n en el condacto
      entrada[posicion - 2] = lineaNueva  # C�digo y par�metros de la nueva l�nea
      cursor.movePosition (QTextCursor.EndOfBlock)
      cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
      cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
      self.setTextCursor (cursor)
      imprimeCondacto (*lineaNueva)
      if columna in colsValidas:  # Recuperamos posici�n anterior correcta
        indice = colsValidas.index (columna)
        linea  = cursor.block()
        colsValidas = self._daColsValidas (linea.text())
        columna  = cursor.positionInBlock()
        colNueva = colsValidas[indice]
        cursor.setPosition (cursor.position() + (colNueva - columna))
        self.setTextCursor (cursor)
    elif evento.key() >= Qt.Key_0 and evento.key() <= Qt.Key_9:  # N�meros
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      if str (cursor.selectedText()).isdigit():
        columna -= len (cursor.selectedText())  # Inicio del par�metro
      elif cursor.hasSelection():
        return  # Intentando escribir n�mero donde no es posible
      colsValidas = self._daColsValidas (linea.text())
      columna     = self._daColValida (columna, linea.text(), colsValidas)
      if columna == colsValidas[0] or (columna == colsValidas[-1] and len (colsValidas) < 3) or linea.text()[columna - 1] == '"':
        return  # Intentando escribir n�mero donde no es posible
      if columna == colsValidas[-1]:  # Est� al final del �ltimo par�metro
        columna = colsValidas[-2]
      numParam  = colsValidas.index (columna)
      parametro = str (linea.text()[columna:])
      if ',' in parametro:  # Hay alg�n par�metro posterior
        parametro = parametro[: parametro.find (',')]
      elif ' ' in parametro:  # Hay una anotaci�n posterior (del texto asociado al par�metro)
        parametro = parametro[: parametro.find (' ')]
      dialogo = ModalEntrada (self, _('Parameter value:'), evento.text(), parametro)
      dialogo.setInputMode (QInputDialog.IntInput)
      dialogo.setIntRange  (0, 255)
      if dialogo.exec_() == QDialog.Accepted:
        numEntrada, posicion = self._daNumEntradaYLinea (linea)
        numProceso = pestanyas.currentIndex()
        proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
        entrada    = proceso[1][numEntrada]  # La entrada seleccionada
        valor      = dialogo.intValue()
        condacto   = entrada[posicion - 2]
        condacto[1][numParam - 1] = valor
        cursor.movePosition (QTextCursor.EndOfBlock)
        cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
        self.setTextCursor (cursor)
        imprimeCondacto (*condacto)
        if numParam == 1 and len (condacto[1]) > 1:  # Hemos cambiado el primer par�metro y hay segundo par�metro
          cursor = self.textCursor()
          cursor.movePosition (QTextCursor.StartOfBlock)
          cursor.movePosition (QTextCursor.WordRight, n = 4)  # Vamos al segundo par�metro
          self.setTextCursor (cursor)
    self.barra.update()

  def mousePressEvent (self, evento):
    if evento.button() & Qt.LeftButton and evento.modifiers() & Qt.ControlModifier:  # Puede ser Ctrl+click en un enlace
      enlace = self.anchorAt (evento.pos())
      if enlace and enlace[:8] == 'proceso:':
        self.quitaFormatoEnlace()  # Quitamos el formato anterior
        pestanyas.setCurrentIndex (int (enlace[8:]))
        return
    super (CampoTexto, self).mousePressEvent (evento)

  def mouseReleaseEvent (self, evento):
    if not evento.button() & Qt.LeftButton or self.textCursor().hasSelection():
      return super (CampoTexto, self).mouseReleaseEvent (evento)
    cursor     = self.cursorForPosition (evento.pos())
    bloque     = cursor.block()
    columna    = cursor.positionInBlock()
    textoLinea = bloque.text()
    colNueva   = self._daColValida (columna, textoLinea)
    cursor.setPosition (cursor.position() + (colNueva - columna))
    self.setTextCursor (cursor)

  def quitaFormatoEnlace (self):
    """Quita el formato de enlace a la posici�n del cursor actual"""
    cursor  = self.textCursor()
    formato = cursor.charFormat()
    formato.setAnchor (False)
    formato.setFontUnderline (False)
    formato.setToolTip ('')
    campo_txt.setCurrentCharFormat (formato)

  def resizeEvent (self, evento):
    super (CampoTexto, self).resizeEvent (evento)
    self.barra.resize (self.barra.anchoBarra, evento.size().height())  # Actualizamos la altura de la barra izquierda
    if accMostrarRec.isChecked():  # Recortar al ancho de l�nea disponible
      try:
        self.anchoAntes
      except:
        self.anchoAntes     = evento.oldSize().width()
        self.cuentaDifAncho = {}    # Diccionario para contar cu�ntas veces se encuentra cada diferencia de anchura
        self.difAutoAjuste  = None  # Valor de diferencia en los autoajustes al redibujar el campo de texto
      # Ocurre un bucle de redimensiones por autoajustes al redibujar el campo de texto, en el cual la diferencia es siempre la misma, pero es dependiente del sistema (seguramente del estilo de la interfaz)
      # Detectaremos cu�l es esa diferencia por los autoajustes, y en cuanto la sepamos ignoraremos cambios de anchura de ese valor
      diferencia = abs (evento.size().width() - self.anchoAntes)
      if not diferencia or diferencia == self.difAutoAjuste:  # No cambia o es el valor de la diferencia detectada
        return  # Evitamos bucle de redimensiones por autoajustes al redibujar el campo de texto
      if diferencia <= 25:
        if diferencia in self.cuentaDifAncho:
          if self.cuentaDifAncho[diferencia] >= 14:  # Debe ser �ste el valor de diferencia de los autoajustes
            self.cuentaDifAncho.clear()
            self.difAutoAjuste = diferencia
            return
          self.cuentaDifAncho[diferencia] += 1
        else:
          self.cuentaDifAncho[diferencia] = 1
      self.actualizandoProceso.start (100)
      self.anchoAntes = evento.size().width()

  def viewportEvent (self, evento):
    resultado = super (CampoTexto, self).viewportEvent (evento)
    if isinstance (evento, QMouseEvent) or isinstance (evento, QPaintEvent) or isinstance (evento, QResizeEvent) or isinstance (evento, QWheelEvent):
      self.barra.update()
    return resultado

  def wheelEvent (self, evento):
    global tam_fuente
    if evento.modifiers() & Qt.ControlModifier:
      cursor = self.textCursor()
      self.selectAll()
      if (evento.delta() if vers_pyqt < 5 else evento.angleDelta().y()) < 0:
        tam_fuente = max (8, tam_fuente - 2)
      else:
        tam_fuente += 2
      if self.overwriteMode():
        self.setCursorWidth (int (tam_fuente * 0.7))
      fuente = self.font()
      fuente.setPixelSize (tam_fuente)
      self.setFont (fuente)
      self.setTextCursor (cursor)
      if accMostrarRec.isChecked():  # Recortar al ancho de l�nea disponible
        self.actualizandoProceso.start (100)
    else:
      super (CampoTexto, self).wheelEvent (evento)

class ManejoExportacion (QThread):
  """Hilo que ejecuta la exportaci�n de base de datos sin bloquear la interfaz de usuario"""
  cambia_progreso = pyqtSignal (int)

  def __init__ (self, padre, fichero, indiceFiltroExportar):
    QThread.__init__ (self, parent = padre)
    self.fichero      = fichero
    self.indiceFiltro = indiceFiltroExportar
    self.cambia_progreso.connect (self.cambiaProgreso)
    if 'dlg_progreso' in mod_actual.__dict__:
      del mod_actual.dlg_progreso[:]  # Por si acaso quedaba algo ah�
      self.dialogoProgreso = QProgressDialog (_('Optimizing database...\n\nPressing the "Cancel" button will export it without further optimizations'), _('&Cancel'), 0, 100, selector)
      self.dialogoProgreso.setMinimumDuration (2000)  # Que salga si va a durar m�s de 2 segundos
      self.dialogoProgreso.setWindowTitle (_('Export database'))
      mod_actual.cambia_progreso = self.cambia_progreso
      mod_actual.dlg_progreso.append (self.dialogoProgreso)
    else:
      self.dialogoProgreso = None

  def cambiaProgreso (self, valorProgreso):
    """Cambia el valor actual del progreso en el di�logo de progreso"""
    if self.dialogoProgreso:
      self.dialogoProgreso.setValue (valorProgreso)

  def run (self):
    mod_actual.__dict__[info_exportar[self.indiceFiltro][0]] (self.fichero)
    if self.dialogoProgreso:
      self.dialogoProgreso.close()
      self.dialogoProgreso = None
      del mod_actual.dlg_progreso[:]

class ManejoInterprete (QThread):
  """Maneja la comunicaci�n con el int�rprete ejecutando la base de datos"""
  cambiaBanderas = pyqtSignal (object)
  cambiaObjetos  = pyqtSignal (object)
  cambiaImagen   = pyqtSignal()
  cambiaPila     = pyqtSignal()

  def __init__ (self, procInterprete, padre):
    QThread.__init__ (self, parent = padre)
    self.procInterprete = procInterprete

  def run (self):
    """Lee del proceso del int�rprete, obteniendo por d�nde va la ejecuci�n"""
    global proc_interprete
    if sys.version_info[0] < 3:
      inicioLista     = '['
      finLista        = ']'
      imagenCambiada  = 'img'
      banderasCambian = 'flg'
      objetosCambian  = 'obj'
      esTeclaEntrada  = 'key'
      esTeclaPasos    = 'stp'
    else:
      inicioLista     = ord ('[')
      finLista        = ord (']')
      imagenCambiada  = b'img'
      banderasCambian = b'flg'
      objetosCambian  = b'obj'
      esTeclaEntrada  = b'key'
      esTeclaPasos    = b'stp'
    pilaProcs = []
    while True:
      linea = self.procInterprete.stdout.readline()
      if not linea:
        break  # Ocurre cuando el proceso ha terminado
      tituloJuego = _('Running %s') % mod_actual.NOMBRE_SISTEMA  # T�tulo para la ventana de juego
      if linea[0] == inicioLista and finLista in linea:  # Si es actualizaci�n del estado de la pila, avisamos de ella
        pilaProcs = eval (linea)
        pilas_pendientes.append (pilaProcs)
        self.cambiaPila.emit()
      elif linea[:3] == imagenCambiada:
        self.cambiaImagen.emit()
      elif linea[:3] == banderasCambian:
        cambiosBanderas = eval (linea[4:])
        self.cambiaBanderas.emit (cambiosBanderas)
      elif linea[:3] == objetosCambian:
        cambiosObjetos = eval (linea[4:])
        self.cambiaObjetos.emit (cambiosObjetos)
      elif linea[:3] == esTeclaEntrada:
        acc1Paso.setEnabled     (False)
        acc10Pasos.setEnabled   (False)
        acc100Pasos.setEnabled  (False)
        acc1000Pasos.setEnabled (False)
        accBanderas.setEnabled  (False)
        tituloJuego += _(' - Waiting for key')
      elif linea[:3] == esTeclaPasos:
        acc1Paso.setEnabled     (True)
        acc10Pasos.setEnabled   (True)
        acc100Pasos.setEnabled  (True)
        acc1000Pasos.setEnabled (True)
        accBanderas.setEnabled  (True)
        tituloJuego += _(' - Stopped')
      if mdi_juego:  # Porque puede no estar lista todav�a
        mdi_juego.widget().setWindowTitle (tituloJuego)
    # El proceso ha terminado
    acc1Paso.setEnabled      (False)
    acc10Pasos.setEnabled    (False)
    acc100Pasos.setEnabled   (False)
    acc1000Pasos.setEnabled  (False)
    accBanderas.setEnabled   (False)
    accPasoAPaso.setEnabled  (True)
    menu_BD_nueva.setEnabled (len (info_nueva) > 0)
    if dlg_desc_objs:
      dlg_desc_objs.model().beginRemoveColumns (QModelIndex(), 2, 2)  # Desaparecer� la columna de la localidad actual de los objetos
    proc_interprete = None
    if dlg_desc_objs:
      dlg_desc_objs.model().endRemoveColumns()
    if mdi_juego:
      mdi_juego.close()
    if pilaProcs:
      ultimaEntrada = [pilaProcs[-1][0]]
      if len (pilaProcs[-1]) > 1:
        ultimaEntrada.extend ([pilaProcs[-1][1], -2])
      pilas_pendientes.append ([ultimaEntrada])
      self.cambiaPila.emit()

class ModalEntrada (QInputDialog):
  """Modal de entrada QInputDialog con el primer car�cter ya introducido, para continuar en siguiente pulsaci�n sin machacarlo"""
  def __init__ (self, parent, etiqueta, textoInicial, textoOriginal = ''):
    QInputDialog.__init__ (self, parent)
    self.textoInicial  = textoInicial
    self.textoOriginal = textoOriginal
    self.setLabelText (etiqueta)
    self.setWindowTitle (_('Modal'))
    # En versiones antiguas de Qt, traduciendo los siguientes botones no funcionaba la introducci�n del valor inicial
    self.setCancelButtonText (_('&Cancel'))
    self.setOkButtonText     (_('&Accept'))

  def _valorInicial (self):
    combo   = self.findChild (QComboBox)  # Estar� cuando se elige que sea desplegable
    spinbox = self.findChild (QSpinBox)   # Estar� al editar valores enteros
    if combo:
      campo = combo.lineEdit()
    elif spinbox:
      campo = spinbox.findChild (QLineEdit)
    else:
      campo = self.findChild (QLineEdit)
    if not campo:  # No hay campo que sea editable
      if combo:
        # combo.setCurrentText (self.textoInicial)  # Esto no funcionar� en PyQt4 al no tener ese m�todo
        combo.setCurrentIndex (combo.findText (self.textoInicial))
      return
    if self.textoOriginal:  # De esta manera, se podr� recuperar el valor original deshaciendo
      campo.setText (self.textoOriginal)
      campo.selectAll()
      campo.insert (self.textoInicial)
    else:
      campo.setText (self.textoInicial)

  def showEvent (self, evento):
    QTimer.singleShot (0, self._valorInicial)

class ModalEntradaTexto (QDialog):
  """Modal de entrada de texto multil�nea"""
  def __init__ (self, parent, texto):
    QDialog.__init__ (self, parent)
    texto = daTextoImprimible (texto).replace ('\\n', '\n')
    if mod_actual.NOMBRE_SISTEMA != 'DAAD':  # En DAAD no hay tabulador, all� se usa \t para el c�digo que pasa al juego bajo
      texto = texto.replace ('\\t', '\t')
    self.campo = QPlainTextEdit (texto, self)
    layout = QVBoxLayout (self)
    layout.addWidget (self.campo)
    layoutBotones = QHBoxLayout()
    botonAceptar  = QPushButton (_('&Accept'), self)
    botonCancelar = QPushButton (_('&Cancel'), self)
    botonAceptar.clicked.connect (self.accept)
    botonCancelar.clicked.connect (self.reject)
    layoutBotones.addWidget (botonAceptar)
    layoutBotones.addWidget (botonCancelar)
    layout.addLayout (layoutBotones)
    self.setWindowTitle (_('Edit the text'))

  def daTexto (self):
    """Devuelve el texto editado"""
    return mod_actual.escribe_secs_ctrl (str (self.campo.toPlainText()))

class ModeloTextos (QAbstractTableModel):
  """Modelo para las tablas de mensajes, heredado por las de localidades y objetos"""
  def __init__ (self, parent, listaTextos):
    QAbstractTableModel.__init__ (self, parent)
    self.indicesTextos = sorted (listaTextos.keys()) if type (listaTextos) == dict else list (range (len (listaTextos)))
    self.listaTextos   = listaTextos

  def columnCount (self, parent):
    return 1

  def data (self, index, role):
    if role == Qt.DisplayRole:
      return daTextoImprimible (self.listaTextos[self.indicesTextos[index.row()]])

  def flags (self, index):
    return Qt.ItemIsSelectable | Qt.ItemIsEnabled

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      if self.listaTextos in (mod_actual.msgs_sys, mod_actual.msgs_sys):
        return _('Message text')
      return _('Description text')
    if orientation == Qt.Vertical and role == Qt.DisplayRole:
      return self.indicesTextos[section]  # section cuenta desde 0
    return QAbstractTableModel.headerData (self, section, orientation, role)

  def rowCount (self, parent):
    return len (self.indicesTextos)

class ModeloLocalidades (ModeloTextos):
  """Modelo para la tabla de localidades"""
  def __init__ (self, parent, listaTextos):
    ModeloTextos.__init__ (self, parent, listaTextos)

  def columnCount (self, parent):
    return 1 + len (pals_mov if accMostrarSal.isChecked() else pals_salida)

  def data (self, index, role):
    if role == Qt.DisplayRole and index.column():
      conexionesLocalidad = mod_actual.conexiones[self.indicesTextos[index.row()]]
      for codigo, destino in conexionesLocalidad:
        if codigo == (pals_mov if accMostrarSal.isChecked() else pals_salida)[index.column() - 1]:
          return destino
      return ''
    return ModeloTextos.data (self, index, role)

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole and section:
      # Si no est� la palabra en el vocabulario, mostraremos el c�digo
      if accMostrarSal.isChecked():
        return pal_sinonimo[(pals_mov[section - 1], tipo_verbo)] if (pals_mov[section - 1], tipo_verbo) in pal_sinonimo else pals_mov[section - 1]
      return pal_sinonimo[(pals_salida[section - 1], tipo_verbo)] if (pals_salida[section - 1], tipo_verbo) in pal_sinonimo else pals_salida[section - 1]
    return ModeloTextos.headerData (self, section, orientation, role)

class ModeloObjetos (ModeloTextos):
  """Modelo para la tabla de objetos"""
  def __init__ (self, parent, listaTextos):
    ModeloTextos.__init__ (self, parent, listaTextos)

  def columnCount (self, parent):
    adicional = 1 if proc_interprete else 0  # N�mero de columnas adicionales, seg�n si se est� ejecutando la BD
    # Parte com�n inicial: descripci�n, localidad inicial, y condicionalmente tambi�n localidad actual
    if mod_actual.NUM_ATRIBUTOS[0] == 0:  # Ning�n tipo de atributos
      if mod_actual.NOMBRE_SISTEMA == 'GAC':
        return 3 + adicional  # A�ade columna peso
      return 2 + adicional
    if mod_actual.NUM_ATRIBUTOS[0] == 1:  # Pseudoatributo prenda en Quill para QL
      return 4 + adicional  # A�ade columnas: prenda, y nombre
    if mod_actual.NUM_ATRIBUTOS[0] == 2:  # Contenedor y prenda, adem�s del peso
      return 7 + adicional  # A�ade columnas: peso, contenedor, prenda, nombre, y adjetivo
    # Contenedor, prenda, y 16 atributos extra, adem�s del peso
    return 7 + adicional  # A�ade columnas: peso, contenedor, prenda, (atributos extra), nombre, y adjetivo

  def data (self, index, role):
    if role == Qt.DisplayRole and index.column():
      locsPredefinidas = IDS_LOCS[mod_actual.NOMBRE_SISTEMA] if mod_actual.NOMBRE_SISTEMA in IDS_LOCS else IDS_LOCS[None]
      if index.column() == 1:  # Localidad inicial
        locInicial = mod_actual.locs_iniciales[self.indicesTextos[index.row()]]
        return locsPredefinidas[locInicial] if locInicial in locsPredefinidas else locInicial
      if proc_interprete and index.column() == 2:  # Localidad actual, s�lo mientras se est� ejecutando la BD
        locActual = locs_objs[self.indicesTextos[index.row()]]
        return locsPredefinidas[locActual] if locActual in locsPredefinidas else locActual
      adicional = 1 if proc_interprete else 0  # N�mero de columnas adicionales desde este punto
      nombre    = mod_actual.nombres_objs[self.indicesTextos[index.row()]][0]
      if mod_actual.NUM_ATRIBUTOS[0] == 1:
        if index.column() == 2 + adicional:  # Pseudoatributo prenda en Quill para QL
          return _('&Yes', 1) if 199 < nombre < 255 else _('&No', 1)
        # Nombre
        return (pal_sinonimo[(nombre, tipo_nombre)] if (nombre, tipo_nombre) in pal_sinonimo else nombre) if nombre < 255 else ''
      atributos = mod_actual.atributos[self.indicesTextos[index.row()]]
      if index.column() == 2 + adicional:  # Peso
        return atributos & (255 if mod_actual.NOMBRE_SISTEMA == 'GAC' else 63)
      if index.column() == 5 + adicional:  # Nombre
        return (pal_sinonimo[(nombre, tipo_nombre)] if (nombre, tipo_nombre) in pal_sinonimo else nombre) if nombre < 255 else ''
      if index.column() == 6 + adicional:  # Adjetivo
        adjetivo = mod_actual.nombres_objs[self.indicesTextos[index.row()]][1]
        return (pal_sinonimo[(adjetivo, tipo_adjetivo)] if (adjetivo, tipo_adjetivo) in pal_sinonimo else adjetivo) if adjetivo < 255 else ''
      # Atributos
      return (_('&Yes', 1) if atributos & (64 if index.column() == 3 + adicional else 128) else _('&No', 1))
    elif role == Qt.ForegroundRole and proc_interprete and index.column() == 2:
      idObjeto = self.indicesTextos[index.row()]
      if locs_objs[idObjeto] != locs_objs_antes[idObjeto]:
        return QColor (0, 255, 0)  # La imprimimos en verde porque acaba de cambiar
    return ModeloTextos.data (self, index, role)

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole and section:
      if section == 1:
        return _('Start location')
      if proc_interprete and section == 2:
        return _('Current location')
      adicional = 1 if proc_interprete else 0  # N�mero de columnas adicionales desde este punto
      if mod_actual.NUM_ATRIBUTOS[0] == 1:  # Pseudoatributo prenda en Quill para QL
        if section == 2 + adicional:
          return _('Wearable')
        return _('Noun')
      if section == 2 + adicional:
        return _('Weight')
      if section == 3 + adicional:
        return _('Container')
      if section == 4 + adicional:
        return _('Wearable')
      if section == 5 + adicional:
        return _('Noun')
      return _('Adjective')
    return ModeloTextos.headerData (self, section, orientation, role)

class ModeloVocabulario (QAbstractTableModel):
  """Modelo para la tabla de vocabulario"""
  def __init__ (self, parent):
    QAbstractTableModel.__init__ (self, parent)
    self.tituloCols = (_('Word'), _('Code'), _('Type'))
    self.tipos      = mod_actual.TIPOS_PAL

  def columnCount (self, parent):
    return 3

  def data (self, index, role):
    if role == Qt.DisplayRole:
      if index.column() == 0:
        return daTextoImprimible (mod_actual.vocabulario[index.row()][0])  # Palabra
      if index.column() == 1:
        return mod_actual.vocabulario[index.row()][1]  # C�digo
      # Si llega aqu�, es la tercera columna: el tipo
      tipo = mod_actual.vocabulario[index.row()][2]
      if tipo == 255:
        return _('Reserved')
      if tipo > len (self.tipos):
        return _('Unknown (') + str (tipo) + ')'
      return self.tipos[tipo]

  def flags (self, index):
    return Qt.ItemIsSelectable | Qt.ItemIsEnabled

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.tituloCols[section]
    return QAbstractTableModel.headerData(self, section, orientation, role)

  def rowCount (self, parent):
    return len (mod_actual.vocabulario)

class PantallaJuego (QMdiSubWindow):
  """Subventana MDI para la pantalla de juego del int�rprete"""
  def __init__ (self, parent):
    QMdiSubWindow.__init__ (self, parent)
    self.setAttribute (Qt.WA_InputMethodEnabled, True)
    self.nivelZoom  = 1
    self.rutaImagen = os.path.join (os.path.dirname (os.path.realpath (__file__)), 'ventanaJuegoActual.bmp')
    self.pixmap     = QPixmap (self.rutaImagen)
    self.tamInicial = None
    widget = QLabel (self)
    widget.setPixmap (self.pixmap)
    widget.setWindowTitle ((_('Running %s') % mod_actual.NOMBRE_SISTEMA) + _(' - Stopped'))
    self.setOption (QMdiSubWindow.RubberBandResize)
    self.setWidget (widget)
    selector.centralWidget().addSubWindow (self)
    widget.show()

  def actualizaImagen (self):
    QPixmapCache.clear()
    self.pixmap.load (self.rutaImagen)
    if self.nivelZoom > 1:
      self.widget().setPixmap (self.pixmap.scaled (self.pixmap.size().width() * self.nivelZoom, self.pixmap.size().height() * self.nivelZoom))
    else:
      self.widget().setPixmap (self.pixmap)
    # En cuanto tenga tama�o adecuado, ponemos ese tama�o como m�nimo, para que muestre la pantalla de juego entera
    if not self.tamInicial and self.sizeHint().width() > self.pixmap.width():
      self.anchoBorde = (self.sizeHint().width() - self.pixmap.width()) // 2
      self.altoTitulo = QApplication.style().pixelMetric (QStyle.PM_TitleBarHeight)
      if self.sizeHint().height() == self.pixmap.height() + self.anchoBorde * 2 + self.altoTitulo:
        self.altoTitulo += self.anchoBorde  # pixelMetric no inclu�a el borde al dar el alto de la barra de t�tulo
      if self.sizeHint().height() == self.pixmap.height() + self.anchoBorde + self.altoTitulo:
        self.tamInicial = self.sizeHint()
        selector.centralWidget().tileSubWindows()
        self.setMinimumSize (self.tamInicial)
        self.setMaximumSize (QSize (self.anchoBorde * 2 + self.pixmap.size().width() * 3,
                                    self.anchoBorde + self.altoTitulo + self.pixmap.size().height() * 3))

  def enviaTecla (self, tecla):
    enviar = '\n' if sys.version_info[0] < 3 else b'\n'
    if type (tecla) == int:
      if sys.version_info[0] < 3:
        enviar = chr (0) + chr (tecla) + enviar
      else:
        enviar = bytes ([0, tecla]) + enviar
    else:
      if sys.version_info[0] < 3:
        enviar = tecla + enviar
      else:
        enviar = bytes (tecla, 'iso-8859-15') + enviar
    proc_interprete.stdin.write (enviar)
    proc_interprete.stdin.flush()

  def closeEvent (self, evento):
    global mdi_banderas, mdi_juego
    if proc_interprete:
      proc_interprete.kill()
    evento.accept()
    mdi_juego = None
    if mdi_banderas:
      selector.centralWidget().removeSubWindow (mdi_banderas)
      mdi_banderas = None

  def keyPressEvent (self, evento):
    if evento.key() in (Qt.Key_Alt, Qt.Key_AltGr, Qt.Key_CapsLock, Qt.Key_Control, Qt.Key_Meta, Qt.Key_NumLock, Qt.Key_ScrollLock, Qt.Key_Shift) or Qt.Key_F1 <= evento.key() <= Qt.Key_F35:
      return  # Ignoramos teclas modificadoras, de bloqueo y de funci�n
    if evento.key() in conversion_teclas:
      self.enviaTecla (conversion_teclas[evento.key()])
    elif evento.key() in (Qt.Key_Enter, Qt.Key_Return):
      self.enviaTecla ('')
    else:
      self.enviaTecla (str (evento.text()))

  def inputMethodEvent (self, evento):
    self.enviaTecla (str (evento.commitString()))

  def resizeEvent (self, evento):
    """Ajusta la redimensi�n de la pantalla de juego a los niveles de zoom permitidos"""
    if not self.tamInicial:
      super (PantallaJuego, self).resizeEvent (evento)
      return
    nivelZoomAntes = self.nivelZoom
    if self.size().width() <= self.minimumSize().width() or self.size().height() <= self.minimumSize().height():
      self.nivelZoom = 1
    elif self.size().width() >= (self.anchoBorde * 2 + self.pixmap.size().width() * 3) or \
         self.size().height() >= (self.anchoBorde + self.altoTitulo + self.pixmap.size().height() * 3):
      self.nivelZoom = 3
    elif self.size().width() > (self.anchoBorde * 2 + self.pixmap.size().width() * self.nivelZoom) or \
         self.size().height() > (self.anchoBorde + self.altoTitulo + self.pixmap.size().height() * self.nivelZoom):
      self.nivelZoom = min (3, self.nivelZoom + 1)
    elif self.size().width() < (self.anchoBorde * 2 + self.pixmap.size().width() * self.nivelZoom) or \
         self.size().height() < (self.anchoBorde + self.altoTitulo + self.pixmap.size().height() * self.nivelZoom):
      self.nivelZoom = max (1, self.nivelZoom - 1)
    if nivelZoomAntes != self.nivelZoom:
      evento = QResizeEvent (QSize (self.anchoBorde * 2 + self.pixmap.size().width() * self.nivelZoom,
                                    self.anchoBorde + self.altoTitulo + self.pixmap.size().height() * self.nivelZoom),
                             evento.oldSize())
      self.resize (evento.size())
    super (PantallaJuego, self).resizeEvent (evento)
    self.actualizaImagen()

class VFlowLayout (QLayout):
  """Como el QVBoxLayout pero pasando a la columna siguiente cuando no cabe verticalmente"""
  def __init__ (self, parent):
    QLayout.__init__ (self, parent)
    self.items    = []
    self.tamAntes = None  # Tama�o anterior del layout

  def addItem (self, item):
    self.items.append (item)

  def count (self):
    return len (self.items)

  def hasHeightForWidth (self):
    return False

  def itemAt (self, indice):
    try:
      return self.items[indice]
    except:
      return None

  def setGeometry (self, dimensiones):
    if dimensiones != self.tamAntes:
      super (VFlowLayout, self).setGeometry (dimensiones)
      self.organizaLayout (dimensiones)
      self.tamAntes = dimensiones

  def sizeHint (self):
    if mdi_juego:
      if dlg_procesos and mdi_procesos in selector.centralWidget().subWindowList():
        return QSize (mdi_juego.widget().width(), dlg_procesos.height() - mdi_juego.height())
      return QSize (mdi_juego.widget().width(), 10 * (self.items[0].sizeHint().height()))
    return self.parent().size()

  def organizaLayout (self, dimensiones):
    # En la primera iteraci�n, aplicamos la hoja de estilo a cada bot�n y calculamos el ancho m�ximo de cada columna, y el n�mero de botones por columna
    anchoCol  = 0   # Ancho m�xima de la columna actual
    anchoCols = []  # Ancho m�xima de cada columna
    colEsPar  = True
    x         = 0
    y         = 0
    tamCol    = 0   # Cu�ntos botones hay como m�ximo en una columna
    for item in self.items:
      if y + item.sizeHint().height() > dimensiones.height():  # Sobrepasar� por abajo
        anchoCols.append (anchoCol)
        x       += anchoCol
        y        = 0
        anchoCol = item.sizeHint().width()
        colEsPar = not colEsPar
      else:
        anchoCol = max (anchoCol, item.sizeHint().width())
        if x == 0:
          tamCol += 1
      item.setGeometry (QRect (QPoint (x, y), item.sizeHint()))
      botonBandera = item.widget()
      botonBandera.setStyleSheet (estilo_banderas % ((estilo_fila_par if colEsPar else estilo_fila_impar) + (estilo_cambiada if '\n' in botonBandera.toolTip() else '')))
      y += item.sizeHint().height()
    if y > 0:
      anchoCols.append (anchoCol)
    # En la segunda iteraci�n, aplicamos a cada bot�n el ancho m�ximo de su columna
    colActual  = 0
    itemsEnCol = 0
    for item in self.items:
      if itemsEnCol == tamCol:
        colActual += 1
        itemsEnCol = 1
      else:
        itemsEnCol += 1
      item.widget().setMinimumSize (QSize (anchoCols[colActual], item.sizeHint().height()))

  def redibuja (self):
    self.tamAntes = None


def actualizaBanderas (cambiosBanderas):
  """Actualiza el valor de las banderas"""
  global banderas
  if cambiosBanderas:
    for numBandera in range (mod_actual.NUM_BANDERAS[0]):
      if dlg_banderas:
        botonBandera = dlg_banderas.layout().items[numBandera].widget()
        if numBandera in cambiosBanderas:
          if estilo_cambiada not in botonBandera.styleSheet():
            botonBandera.setStyleSheet (botonBandera.styleSheet()[:-1] + estilo_cambiada + ' }')
          botonBandera.setText (str (numBandera % 100) + ': ' + str (cambiosBanderas[numBandera]))
          botonBandera.setToolTip ((_('Value of flag %d: ') % numBandera) + str (cambiosBanderas[numBandera]) + _('\nPrevious value: ') + str (banderas[numBandera]))
        else:
          if estilo_cambiada in botonBandera.styleSheet():
            botonBandera.setStyleSheet (botonBandera.styleSheet().replace (estilo_cambiada, ''))
          botonBandera.setToolTip ((_('Value of flag %d: ') % numBandera) + str (banderas[numBandera]))
      if numBandera in cambiosBanderas:
        banderas[numBandera] = cambiosBanderas[numBandera]
  elif dlg_banderas:  # No cambiaron las banderas
    for numBandera in range (mod_actual.NUM_BANDERAS[0]):
      botonBandera = dlg_banderas.layout().items[numBandera].widget()
      if '\n' in botonBandera.toolTip():
        botonBandera.setStyleSheet (botonBandera.styleSheet().replace (estilo_cambiada, ''))
        botonBandera.setToolTip ((_('Value of flag %d: ') % numBandera) + str (banderas[numBandera]))
  if dlg_banderas:
    dlg_banderas.layout().redibuja()

def actualizaLocalidades ():
  """Actualiza las columnas del di�logo de localidades al cambiar el checkbox de mostrar todas las palabras de movimiento o no"""
  if dlg_desc_locs:
    dlg_desc_locs.model().beginResetModel()
    dlg_desc_locs.model().endResetModel()

def actualizaObjetos (cambiosObjetos):
  """Actualiza el valor de los objetos"""
  global locs_objs, locs_objs_antes
  locs_objs_antes = locs_objs.copy()
  for numObjeto in cambiosObjetos:
    locs_objs[numObjeto] = cambiosObjetos[numObjeto]
  if dlg_desc_objs:
    dlg_desc_objs.repaint()

def actualizaProceso ():
  """Redibuja el proceso actualmente mostrado, si hay alguno"""
  if dlg_procesos:
    cursor = campo_txt.textCursor()
    linea  = cursor.block()
    numEntrada, posicion = campo_txt._daNumEntradaYLinea (linea)
    cambiaProceso (pestanyas.currentIndex(), numEntrada)

def actualizaPosProcesos ():
  """Refleja la posici�n de ejecuci�n paso a paso actual en el di�logo de tablas de proceso"""
  global inicio_debug, pila_procs
  pilaAnterior = pila_procs
  if len (pilas_pendientes) > 4:
    # Se est�n acumulando, por lo que tomamos la �ltima y descartamos las dem�s
    pila_procs = pilas_pendientes[-1]
    del pilas_pendientes[:]
  elif pilas_pendientes:
    pila_procs = pilas_pendientes.pop (0)
  else:  # No queda nada m�s por actualizar
    return
  muestraProcesos()
  numProcSel = pestanyas.currentIndex()  # N�mero de proceso seleccionado
  if type (mod_actual.tablas_proceso) == dict:
    numProcSel = sorted (mod_actual.tablas_proceso.keys())[numProcSel]
  if not pila_procs:
    cambiaProceso (pestanyas.currentIndex())
  elif numProcSel == pila_procs[-1][0]:  # La l�nea ejecut�ndose actualmente es del proceso seleccionado
    proceso = mod_actual.tablas_proceso[pila_procs[-1][0]]
    # Desmarcamos la l�nea marcada anteriormente
    if pilaAnterior and len (pilaAnterior[-1]) > 1:
      campo_txt.irAEntradaYCondacto (pilaAnterior[-1][1], pilaAnterior[-1][2])
      cursor = campo_txt.textCursor()
      cursor.movePosition (QTextCursor.EndOfBlock)
      cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
      cursor.removeSelectedText()
      campo_txt.setFontWeight (QFont.Normal)
      campo_txt.setTextBackgroundColor (color_base)
      if pilaAnterior[-1][2] == -1:  # Es l�nea de cabecera
        cabecera = proceso[0][pilaAnterior[-1][1]]
        imprimeCabecera (cabecera[0], cabecera[1], pilaAnterior[-1][1], pilaAnterior[-1][0])
      else:
        entrada  = proceso[1][pilaAnterior[-1][1]]
        condacto = entrada[pilaAnterior[-1][2]]
        imprimeCondacto (*condacto, nuevaLinea = False)
    # Marcamos la l�nea ejecut�ndose actualmente
    if len (pila_procs[-1]) > 1 and (proc_interprete or pilas_pendientes):
      campo_txt.irAEntradaYCondacto (pila_procs[-1][1], pila_procs[-1][2])
      cursor = campo_txt.textCursor()
      cursor.movePosition (QTextCursor.EndOfBlock)
      cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
      if pila_procs[-1][2] > -1:  # Es l�nea de condacto
        cursor.movePosition (QTextCursor.Left, QTextCursor.KeepAnchor)
      cursor.removeSelectedText()
      campo_txt.setFontWeight (QFont.Bold)
      campo_txt.setTextBackgroundColor (color_tope_pila)
      if pila_procs[-1][2] == -1:  # Es l�nea de cabecera
        cabecera = proceso[0][pila_procs[-1][1]]
        imprimeCabecera (cabecera[0], cabecera[1], pila_procs[-1][1], pila_procs[-1][0])
      else:
        entrada  = proceso[1][pila_procs[-1][1]]
        condacto = entrada[pila_procs[-1][2]]
        imprimeCondacto (*condacto)
      campo_txt.setFontWeight (QFont.Normal)
    campo_txt.centraLineaCursor()
  else:
    indiceProceso = pila_procs[-1][0]
    if type (mod_actual.tablas_proceso) == dict:
      indiceProceso = sorted (mod_actual.tablas_proceso.keys()).index (indiceProceso)
    pestanyas.setCurrentIndex (indiceProceso)
  if mdi_juego:
    selector.centralWidget().setActiveSubWindow (mdi_juego)
    if inicio_debug:
      inicio_debug = False
      # Aseguramos que la ventana de juego tenga un ancho correcto y adecuado
      mdi_juego.showNormal()
      if selector.centralWidget().width() * 0.65 < mdi_juego.width() or selector.centralWidget().height() - mdi_juego.height() < 180:
        mdi_juego.resize (mdi_juego.width() - 1, mdi_juego.height() - 1)
      actualizaVentanaJuego()
      anchoJuego = mdi_juego.frameGeometry().width()
      # Colocamos el di�logo de procesos a la derecha del de juego, tomando todo el alto disponible
      mdi_juego.move (0, 0)
      mdi_procesos.resize (selector.centralWidget().width() - anchoJuego, selector.centralWidget().height())
      mdi_procesos.move (anchoJuego, 0)
      muestraBanderas()
      selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
      selector.centralWidget().setActiveSubWindow (mdi_juego)

def actualizaVentanaJuego ():
  """Muestra o actualiza la pantalla actual de juego del int�rprete en el di�logo de ventana de juego"""
  global mdi_juego
  if mdi_juego:  # Subventana MDI ya creada
    try:
      mdi_juego.actualizaImagen()
      return
    except RuntimeError:  # Subventana borrada por Qt
      pass  # La crearemos de nuevo
  # Creamos la subventana
  mdi_juego = PantallaJuego (selector)

# FIXME: Diferencias entre PAWS est�ndar y DAAD
def cambiaProceso (numero, numEntrada = None):
  """Llamada al cambiar de pesta�a en el di�logo de procesos"""
  global pals_no_existen
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  if type (mod_actual.tablas_proceso) == dict:
    numero = sorted (mod_actual.tablas_proceso.keys())[numero]
  proceso   = mod_actual.tablas_proceso[numero]  # El proceso seleccionado
  cabeceras = proceso[0]  # Las cabeceras del proceso seleccionado
  entradas  = proceso[1]  # Las entradas del proceso seleccionado
  posicion  = None  # Posici�n donde ir al terminar de cargar el contenido del proceso
  if numEntrada == None and pila_procs and len (pila_procs[-1]) > 1 and pila_procs[-1][0] == numero:
    numEntrada = pila_procs[-1][1]
  campo_txt.clear()  # Borramos el texto anterior
  for i in range (len (cabeceras)):
    if i == numEntrada:
      posicion = campo_txt.textCursor().position()
    if [numero, i, -1] in pila_procs:
      if pila_procs[-1] == [numero, i, -1]:
        campo_txt.setFontWeight (QFont.Bold)
        campo_txt.setTextBackgroundColor (color_tope_pila)
      else:
        campo_txt.setTextBackgroundColor (color_pila)
    else:
      campo_txt.setTextBackgroundColor (color_base)
    imprimeCabecera (cabeceras[i][0], cabeceras[i][1], i, numero)
    campo_txt.setFontWeight (QFont.Normal)
    campo_txt.insertPlainText ('\n     ')
    inalcanzable = False  # Marca de c�digo inalcanzable
    for c in range (len (entradas[i])):
      condacto, parametros = entradas[i][c]
      if [numero, i, c] in pila_procs:
        if pila_procs[-1] == [numero, i, c]:
          posicion = campo_txt.textCursor().position()
          campo_txt.setFontWeight (QFont.Bold)
          campo_txt.setTextBackgroundColor (color_tope_pila)
        else:
          campo_txt.setTextBackgroundColor (color_pila)
      inalcanzable = imprimeCondacto (condacto, parametros, inalcanzable)
      campo_txt.setFontWeight (QFont.Normal)
      campo_txt.setTextBackgroundColor (color_base)
    campo_txt.insertPlainText ('\n     ')
    if i < (len (cabeceras) - 1):
      campo_txt.insertPlainText ('\n\n')
  if posicion:
    cursor = campo_txt.textCursor()
    cursor.setPosition (posicion)
    campo_txt.setTextCursor (cursor)
    campo_txt.centraLineaCursor()
  else:
    campo_txt.moveCursor (QTextCursor.Start)  # Movemos el cursor al principio
  if inicio_debug:
    selector.setCursor (Qt.BusyCursor)  # Puntero de rat�n de trabajo en segundo plano
  else:
    selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def cargaInfoModulos ():
  """Carga la informaci�n de los m�dulos de librer�a v�lidos que encuentre en el directorio"""
  # TODO: Informar de los errores
  # TODO: No permitir entradas con igual conjunto de extensiones y descripci�n,
  # pero distinta funci�n a llamar (aunque sean de m�dulos distintos)
  # Nombres de los m�dulos de librer�a en el directorio
  nombres = [f[:-3] for f in os.listdir (os.path.dirname (os.path.realpath (__file__)))
             if (f[:9] == 'libreria_' and f[-3:] == '.py')]
  for nombre_modulo in nombres:
    try:
      modulo = __import__ (nombre_modulo)
    except SyntaxError as excepcion:
      prn (_('Error when importing module:'), excepcion, file = sys.stderr)
      continue
    # Apa�o para que funcione las librer�as de DAAD, PAW y SWAN tal y como est�n (con lista unificada de condactos)
    if comprueba_tipo (modulo, 'condactos', dict) and not comprueba_tipo (modulo, 'acciones', dict):
      modulo.acciones    = {}
      modulo.condiciones = {}
    # Comprobamos que el m�dulo tenga todos los nombres necesarios
    for nombre, tipos in nombres_necesarios:
      if not comprueba_tipo (modulo, nombre, tipos):
        modulo = None  # M�dulo de librer�a inv�lido, lo liberamos
        break
    if modulo == None:
      continue
    for entrada in modulo.funcs_importar:
      if comprueba_tipo (modulo, entrada[0], types.FunctionType):
        info_importar.append ((nombre_modulo, entrada[0], entrada[1], entrada[2]))
    if comprueba_tipo (modulo, modulo.func_nueva, types.FunctionType):
      info_nueva.append ((nombre_modulo, modulo.func_nueva))
      accion = QAction (_('%s database') % modulo.NOMBRE_SISTEMA, menu_BD_nueva)
      accion.setStatusTip (_('Creates a new %s database') % modulo.NOMBRE_SISTEMA)
      accion.triggered.connect (lambda: nuevaBD (len (info_nueva) - 1))
      menu_BD_nueva.addAction (accion)
    del modulo
  # Actualizamos las distintas acciones y men�s, seg�n corresponda
  accExportar.setEnabled   (False)
  accImportar.setEnabled   (len (info_importar) > 0)
  menu_BD_nueva.setEnabled (len (info_nueva) > 0)

def cierraDialogos ():
  """Cierra todos los di�logos no modales"""
  global dlg_banderas, dlg_desc_locs, dlg_desc_objs, dlg_msg_sys, dlg_msg_usr, dlg_procesos, dlg_vocabulario
  selector.centralWidget().closeAllSubWindows()
  dlg_banderas    = None
  dlg_desc_locs   = None
  dlg_desc_objs   = None
  dlg_msg_sys     = None
  dlg_msg_usr     = None
  dlg_procesos    = None
  dlg_vocabulario = None

def creaAcciones ():
  """Crea las acciones de men� y barra de botones"""
  global acc1Paso, acc10Pasos, acc100Pasos, acc1000Pasos, accAcercaDe, accBanderas, accContadores, accDescLocs, accDescObjs, accDireccs, accExportar, accImportar, accMostrarLoc, accMostrarObj, accMostrarRec, accMostrarSal, accMostrarSys, accMostrarUsr, accMsgSys, accMsgUsr, accPasoAPaso, accSalir, accTblProcs, accTblVocab
  acc1Paso      = QAction (icono ('pasos_1'),    _('1 step'),     selector)
  acc10Pasos    = QAction (icono ('pasos_10'),   _('10 steps'),   selector)
  acc100Pasos   = QAction (icono ('pasos_100'),  _('100 steps'),  selector)
  acc1000Pasos  = QAction (icono ('pasos_1000'), _('1000 steps'), selector)
  accAcercaDe   = QAction (icono_ide, _('&About NAPS IDE'), selector)
  accBanderas   = QAction (icono ('banderas'),       _('&Flags'),         selector)
  accContadores = QAction (icono ('contadores'),     _('&Counters'),      selector)
  accDescLocs   = QAction (icono ('desc_localidad'), _('&Location data'), selector)
  accDescObjs   = QAction (icono ('desc_objeto'),    _('&Object data'),   selector)
  accDireccs    = QAction (icono ('direccion'),      _('&Movement'),      selector)
  accExportar   = QAction (icono ('exportar'),       _('&Export'),        selector)
  accImportar   = QAction (icono ('importar'),       _('&Import'),        selector)
  accMostrarLoc = QAction (_('&Location descriptions'), selector)
  accMostrarObj = QAction (_('&Object descriptions'),   selector)
  accMostrarRec = QAction (_('&Trim to line width'),    selector)
  accMostrarSal = QAction (_('All &movements'),         selector)  # TODO: hacer lo mismo para todos los atributos (extra)
  accMostrarSys = QAction (_('&System messages'),       selector)
  accMostrarUsr = QAction (_('&User messages'),         selector)
  accMsgSys     = QAction (icono ('msg_sistema'), _('&System messages'), selector)
  accMsgUsr     = QAction (icono ('msg_usuario'), _('&User messages'),   selector)
  accPasoAPaso  = QAction (icono ('pasoapaso'),   _('&Step by step'),    selector)
  accSalir      = QAction (icono ('salir'),       _('&Quit'),            selector)
  accTblProcs   = QAction (icono ('proceso'),     _('&Tables'),          selector)
  accTblVocab   = QAction (icono ('vocabulario'), _('&Table'),           selector)
  for accion in (accMostrarLoc, accMostrarObj, accMostrarRec, accMostrarSal, accMostrarSys, accMostrarUsr):
    accion.setCheckable (True)
  for accion in (accMostrarLoc, accMostrarObj, accMostrarRec, accMostrarSys, accMostrarUsr):
    accion.setChecked (True)
  accMostrarSal.setChecked (False)
  for accion in (acc1Paso, acc10Pasos, acc100Pasos, acc1000Pasos, accBanderas, accContadores, accDescLocs, accDescObjs, accDireccs, accMostrarLoc, accMostrarObj, accMostrarRec, accMostrarSal, accMostrarSys, accMostrarUsr, accMsgSys, accMsgUsr, accPasoAPaso, accTblProcs, accTblVocab):
    accion.setEnabled (False)
  acc1Paso.setShortcut     ('F1')
  acc10Pasos.setShortcut   ('F2')
  acc100Pasos.setShortcut  ('F3')
  acc1000Pasos.setShortcut ('F4')
  accSalir.setShortcut     ('Ctrl+Q')
  acc1Paso.setStatusTip      (_('Runs a step on the database and then it stops'))
  acc10Pasos.setStatusTip    (_('Runs up to ten steps on the database and then it stops'))
  acc100Pasos.setStatusTip   (_('Runs up to one hundred steps on the database and then it stops'))
  acc1000Pasos.setStatusTip  (_('Runs up to one thousand steps on the database and then it stops'))
  accAcercaDe.setStatusTip   (_('Shows information about the program'))
  accBanderas.setStatusTip   (_('Allows to check and modify the value of flags'))
  accContadores.setStatusTip (_('Displays the number of elements of each type'))
  accDescLocs.setStatusTip   (_("Allows to check and modify locations' data"))
  accDescObjs.setStatusTip   (_("Allows to check and modify objects' data"))
  accDireccs.setStatusTip    (_('Allows to add and edit movement words'))
  accExportar.setStatusTip   (_('Exports the database to a file'))
  accImportar.setStatusTip   (_('Imports the database from a file'))
  accMostrarLoc.setStatusTip (_('Show location descriptions when condacts reference them'))
  accMostrarObj.setStatusTip (_('Show object descriptions when condacts reference them'))
  accMostrarRec.setStatusTip (_('Trim texts to the available line width'))
  accMostrarSal.setStatusTip (_('Show columns for all possible movement words'))
  accMostrarSys.setStatusTip (_('Show system messages when condacts reference them'))
  accMostrarUsr.setStatusTip (_('Show user messages when condacts reference them'))
  accMsgSys.setStatusTip     (_('Allows to check and modify system messages'))
  accMsgUsr.setStatusTip     (_('Allows to check and modify user messages'))
  accPasoAPaso.setStatusTip  (_('Debugs the database running it step by step'))
  accSalir.setStatusTip      (_('Quits the application'))
  accTblProcs.setStatusTip   (_('Allows to check and modify the process tables'))
  accTblVocab.setStatusTip   (_('Allows to check and modify the vocabulary'))
  accTblProcs.setToolTip (_('Process tables'))
  accTblVocab.setToolTip (_('Vocabulary table'))
  acc1Paso.triggered.connect      (lambda: ejecutaPasos (0))
  acc10Pasos.triggered.connect    (lambda: ejecutaPasos (1))
  acc100Pasos.triggered.connect   (lambda: ejecutaPasos (2))
  acc1000Pasos.triggered.connect  (lambda: ejecutaPasos (3))
  accAcercaDe.triggered.connect   (muestraAcercaDe)
  accBanderas.triggered.connect   (muestraBanderas)
  accContadores.triggered.connect (muestraContadores)
  accDescLocs.triggered.connect   (muestraDescLocs)
  accDescObjs.triggered.connect   (muestraDescObjs)
  accExportar.triggered.connect   (exportaBD)
  accImportar.triggered.connect   (dialogoImportaBD)
  accMostrarLoc.triggered.connect (actualizaProceso)
  accMostrarObj.triggered.connect (actualizaProceso)
  accMostrarRec.triggered.connect (actualizaProceso)
  accMostrarSys.triggered.connect (actualizaProceso)
  accMostrarSal.triggered.connect (actualizaLocalidades)
  accMostrarUsr.triggered.connect (actualizaProceso)
  accMsgSys.triggered.connect     (muestraMsgSys)
  accMsgUsr.triggered.connect     (muestraMsgUsr)
  accPasoAPaso.triggered.connect  (ejecutaPorPasos)
  accSalir.triggered.connect      (selector.close)
  accTblProcs.triggered.connect   (muestraProcesos)
  accTblVocab.triggered.connect   (muestraVistaVocab)

def creaBarraBotones ():
  """Crea la barra de botones"""
  global barra_botones
  barra_botones = selector.addToolBar (_('Button bar'))
  barra_botones.addAction (accImportar)
  barra_botones.addSeparator()
  barra_botones.addAction (accTblProcs)
  barra_botones.addAction (accTblVocab)
  barra_botones.addAction (accMsgSys)
  barra_botones.addAction (accMsgUsr)
  barra_botones.addAction (accDescLocs)
  barra_botones.addAction (accDescObjs)
  barra_botones.setIconSize (QSize (16, 16))

def creaMenus ():
  """Crea y organiza los men�s"""
  global menu_BD_nueva
  menuBD        = selector.menuBar().addMenu (_('&Database'))
  menu_BD_nueva = QMenu (_('&New'), menuBD)
  menu_BD_nueva.setIcon (icono ('nueva'))
  menuBD.addMenu   (menu_BD_nueva)
  menuBD.addAction (accImportar)
  menuBD.addAction (accExportar)
  menuBD.addSeparator()
  menuBD.addAction (accContadores)
  menuBD.addSeparator()
  menuBD.addAction (accSalir)
  menuEjecutar = selector.menuBar().addMenu (_('&Run'))
  menuEjecutar.addAction (accPasoAPaso)
  menuEjecutar.addSeparator()
  menuEjecutar.addAction (acc1Paso)
  menuEjecutar.addAction (acc10Pasos)
  menuEjecutar.addAction (acc100Pasos)
  menuEjecutar.addAction (acc1000Pasos)
  menuEjecutar.addSeparator()
  menuEjecutar.addAction (accBanderas)
  menuProcesos     = selector.menuBar().addMenu (_('&Processes'))
  menuProcsMostrar = QMenu (_('&Show texts'), menuProcesos)
  menuProcsMostrar.addAction (accMostrarLoc)
  menuProcsMostrar.addAction (accMostrarObj)
  menuProcsMostrar.addAction (accMostrarSys)
  menuProcsMostrar.addAction (accMostrarUsr)
  menuProcsMostrar.addSeparator()
  menuProcsMostrar.addAction (accMostrarRec)
  menuProcesos.addAction (accTblProcs)
  menuProcesos.addSeparator()
  menuProcesos.addMenu (menuProcsMostrar)
  menuTextos        = selector.menuBar().addMenu (_('&Texts'))
  menuTextosMostrar = QMenu (_('Show &columns'), menuTextos)
  menuTextosMostrar.addAction (accMostrarSal)
  menuTextos.addAction (accDescLocs)
  menuTextos.addAction (accDescObjs)
  menuTextos.addMenu (menuTextosMostrar)
  menuTextos.addSeparator()
  menuTextos.addAction (accMsgSys)
  menuTextos.addAction (accMsgUsr)
  menuVocabulario = selector.menuBar().addMenu (_('&Vocabulary'))
  menuVocabulario.addAction (accDireccs)
  menuVocabulario.addAction (accTblVocab)
  menuAyuda = selector.menuBar().addMenu (_('&Help'))
  menuAyuda.addAction (accAcercaDe)

def creaSelector ():
  """Crea y organiza la ventana del selector"""
  global icono_ide, selector
  icono_ide = icono ('ide')
  selector  = QMainWindow()
  selector.resize (630, 460)
  areaMdi = QMdiArea (selector)
  if not modo_claro:
    areaMdi.setBackground (QColor (20, 20, 20))
  selector.setCentralWidget (areaMdi)
  selector.setWindowIcon    (icono_ide)
  selector.setWindowTitle   ('NAPS IDE')
  creaAcciones()
  creaMenus()
  creaBarraBotones()
  barraEstado = selector.statusBar()  # Queremos una barra de estado

def daTextoComoParrafoHtml (texto):
  """Devuelve el texto dado metido en un p�rrafo html, con los caracteres que usa html correctamente escapados"""
  texto = texto.replace ('&', '&amp;').replace ('<', '&lt;').replace ('>', '&gt;')
  return '<p>' + texto + '</p>'

def daTextoImprimible (texto):
  """Da la representaci�n imprimible del texto dado seg�n la librer�a de la plataforma PAW-like"""
  texto      = mod_actual.lee_secs_ctrl (texto)
  convertido = ''
  i = 0
  while i < len (texto):
    c = texto[i]
    o = ord (c)
    if o < 32 or (o > 126 and o < 161):
      convertido += '\\x%02X' % o
    else:
      convertido += c
    i += 1
  if sys.version_info[0] < 3:
    return convertido.decode ('iso-8859-15')
  return convertido

def dialogoImportaBD ():
  """Deja al usuario elegir un fichero de base datos, y lo intenta importar"""
  global dlg_abrir
  extSoportadas = set()  # Todas las extensiones soportadas
  filtro        = []
  for modulo, funcion, extensiones, descripcion in info_importar:
    filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
    extSoportadas.update (extensiones)
  filtro.append (_('All supported formats (*.') + ' *.'.join (sorted (extSoportadas)) + ')')
  if not dlg_abrir:  # Di�logo no creado a�n
    dlg_abrir = QFileDialog (selector, _('Import database'), os.curdir, ';;'.join (sorted (filtro)))
    dlg_abrir.setFileMode  (QFileDialog.ExistingFile)
    dlg_abrir.setLabelText (QFileDialog.LookIn,   _('Places'))
    dlg_abrir.setLabelText (QFileDialog.FileName, _('&Name:'))
    dlg_abrir.setLabelText (QFileDialog.FileType, _('Filter:'))
    dlg_abrir.setLabelText (QFileDialog.Accept,   _('&Open'))
    dlg_abrir.setLabelText (QFileDialog.Reject,   _('&Cancel'))
    dlg_abrir.setOption    (QFileDialog.DontUseNativeDialog)
  dlg_abrir.selectNameFilter (filtro[len (filtro) - 1])  # Elegimos el filtro de todos los formatos soportados
  if dlg_abrir.exec_():  # No se ha cancelado
    selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
    cierraDialogos()
    indiceFiltro  = filtro.index (dlg_abrir.selectedNameFilter())
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_abrir.selectedFiles()[0])
    if indiceFiltro == len (filtro) - 1:
      importaBD (nombreFichero)
    else:
      importaBD (nombreFichero, indiceFiltro)
    selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def editaBandera (numBandera):
  # type: (int) -> None
  """Permite editar el valor de una bandera"""
  dialogo = ModalEntrada (dlg_banderas, _('Value of flag %d: ') % numBandera, str (banderas[numBandera]))
  dialogo.setInputMode   (QInputDialog.IntInput)
  dialogo.setIntRange    (0, 255)
  dialogo.setWindowTitle (_('Edit'))
  if dialogo.exec_() == QDialog.Accepted:
    if dialogo.intValue() != banderas[numBandera]:
      banderas[numBandera] = dialogo.intValue()
      botonBandera = dlg_banderas.layout().items[numBandera].widget()
      botonBandera.setText (str (numBandera % 100) + ': ' + str (banderas[numBandera]))
      botonBandera.setToolTip ((_('Value of flag %d: ') % numBandera) + str (banderas[numBandera]))
      dlg_banderas.layout().redibuja()
      if sys.version_info[0] < 3:
        proc_interprete.stdin.write ('#' + str (numBandera) + '=' + str (banderas[numBandera]) + '\n')
      else:  # Python 3+
        proc_interprete.stdin.write (bytes ('#' + str (numBandera) + '=' + str (banderas[numBandera]) + '\n', locale.getpreferredencoding()))

def editaLocalidad (indice):
  # type: (QModelIndex) -> None
  """Permite editar los datos de una localidad, tras hacer doble click en su tabla"""
  locOrigen = dlg_desc_locs.model().indicesTextos[indice.row()]
  if indice.column():  # Se edita una de las salidas
    conexionesLocalidad = mod_actual.conexiones[locOrigen]
    locDestino = -1
    for codigoMovimiento, destino in conexionesLocalidad:
      if codigoMovimiento == (pals_mov if accMostrarSal.isChecked() else pals_salida)[indice.column() - 1]:
        locDestino = destino
        break
    else:  # No hab�a ninguna salida en esa direcci�n
      codigoMovimiento = (pals_mov if accMostrarSal.isChecked() else pals_salida)[indice.column() - 1]
    # Preparamos la lista de localidades a mostrar en el desplegable de la modal
    # TODO: hacer esto con una funci�n, dado que tiene c�digo com�n con editaObjeto
    diccLocalidades = {}
    if mod_actual.NOMBRE_SISTEMA != 'GAC':
      diccLocalidades[IDS_LOCS[None]['INITIAL']] = 'INITIAL'
    for numLocalidad in mod_actual.desc_locs.keys() if type (mod_actual.desc_locs) == dict else range (len (mod_actual.desc_locs)):
      textoLocalidad = mod_actual.lee_secs_ctrl (mod_actual.desc_locs[numLocalidad].lstrip())
      if sys.version_info[0] < 3:
        textoLocalidad = textoLocalidad.decode ('iso-8859-15')
      if numLocalidad in diccLocalidades:  # Puede ocurrir para la localidad inicial
        diccLocalidades[numLocalidad] += ': ' + textoLocalidad
      else:
        diccLocalidades[numLocalidad] = textoLocalidad
      if len (diccLocalidades[numLocalidad]) > 48:
        diccLocalidades[numLocalidad] = diccLocalidades[numLocalidad][:48] + '...'
    listaLocalidades = [_("(Can't go that way)")]
    for numLocalidad in sorted (diccLocalidades.keys()):
      listaLocalidades.append (str (numLocalidad) + ': ' + diccLocalidades[numLocalidad])
    textoLocalidad = (str (locDestino) + ': ' + diccLocalidades[locDestino]) if locDestino > -1 else _("(Can't go that way)")
    movimiento = ('"' + pal_sinonimo[(codigoMovimiento, tipo_verbo)] + '"') if (codigoMovimiento, tipo_verbo) in pal_sinonimo else str (codigoMovimiento)
    dialogo = ModalEntrada (dlg_desc_objs, _('From location %(numOrigin)d: "%(descOrigin)s"\nMovement %(movement)s goes to location:') % {'descOrigin': diccLocalidades[locOrigen], 'movement': movimiento, 'numOrigin': locOrigen}, textoLocalidad)
    dialogo.setComboBoxItems (listaLocalidades)
    dialogo.setWindowTitle   (_('Edit'))
    if dialogo.exec_() == QDialog.Accepted:
      textoLocalidad = dialogo.textValue()
      if locDestino > -1:  # Antes hab�a salida en esa direcci�n
        for c in range (len (conexionesLocalidad)):
          codigo, destino = conexionesLocalidad[c]
          if codigo == codigoMovimiento:
            if ':' in textoLocalidad:  # Actualizamos la salida que hab�a
              nuevoDestino = int (textoLocalidad[:textoLocalidad.find (':')])
              conexionesLocalidad[c] = (codigo, nuevoDestino)
            else:  # Quitamos la salida, al haber elegido que ya no se pueda ir
              del conexionesLocalidad[c]
            break
      elif ':' in textoLocalidad:  # Antes no hab�a salida en esa direcci�n pero ahora s�
        nuevoDestino = int (textoLocalidad[:textoLocalidad.find (':')])
        conexionesLocalidad.append ((codigoMovimiento, nuevoDestino))
    return
  # Se edita la descripci�n de la localidad
  dialogo = ModalEntradaTexto (dlg_desc_locs, mod_actual.desc_locs[locOrigen])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.desc_locs[locOrigen] = dialogo.daTexto()

def editaMsgSys (indice):
  # type: (QModelIndex) -> None
  """Permite editar el texto de un mensaje de sistema, tras hacer doble click en su tabla"""
  dialogo = ModalEntradaTexto (dlg_msg_sys, mod_actual.msgs_sys[dlg_msg_sys.model().indicesTextos[indice.row()]])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.msgs_sys[dlg_msg_sys.model().indicesTextos[indice.row()]] = dialogo.daTexto()

def editaMsgUsr (indice):
  # type: (QModelIndex) -> None
  """Permite editar el texto de un mensaje de usuario, tras hacer doble click en su tabla"""
  dialogo = ModalEntradaTexto (dlg_msg_usr, mod_actual.msgs_usr[dlg_msg_usr.model().indicesTextos[indice.row()]])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.msgs_usr[dlg_msg_usr.model().indicesTextos[indice.row()]] = dialogo.daTexto()

def editaObjeto (indice):
  # type: (QModelIndex) -> None
  """Permite editar los datos de un objeto, tras hacer doble click en su tabla"""
  numObjeto = dlg_desc_objs.model().indicesTextos[indice.row()]
  # Parte com�n inicial: descripci�n, localidad inicial, y condicionalmente tambi�n localidad actual
  adicional = 1 if proc_interprete else 0  # N�mero de columnas adicionales, seg�n si se est� ejecutando la BD
  if indice.column() == 0:  # Descripci�n
    dialogo = ModalEntradaTexto (dlg_desc_objs, mod_actual.desc_objs[numObjeto])
    if dialogo.exec_() == QDialog.Accepted:
      mod_actual.desc_objs[numObjeto] = dialogo.daTexto()
    return
  if indice.column() == 1 or (adicional and indice.column() == 2):  # Localidad inicial o actual
    # Preparamos la lista de localidades a mostrar en el desplegable de la modal
    diccLocalidades  = {}
    locsPredefinidas = IDS_LOCS[mod_actual.NOMBRE_SISTEMA] if mod_actual.NOMBRE_SISTEMA in IDS_LOCS else IDS_LOCS[None]
    for numLocalidad in locsPredefinidas:
      if type (numLocalidad) != int or locsPredefinidas[numLocalidad] == 'HERE':
        continue
      diccLocalidades[numLocalidad] = locsPredefinidas[numLocalidad]
    for numLocalidad in mod_actual.desc_locs.keys() if type (mod_actual.desc_locs) == dict else range (len (mod_actual.desc_locs)):
      textoLocalidad = mod_actual.lee_secs_ctrl (mod_actual.desc_locs[numLocalidad].lstrip())
      if sys.version_info[0] < 3:
        textoLocalidad = textoLocalidad.decode ('iso-8859-15')
      if numLocalidad in diccLocalidades:  # Puede ocurrir al menos para la localidad inicial
        diccLocalidades[numLocalidad] += ': ' + textoLocalidad
      else:
        diccLocalidades[numLocalidad] = textoLocalidad
      if len (diccLocalidades[numLocalidad]) > 48:
        diccLocalidades[numLocalidad] = diccLocalidades[numLocalidad][:48] + '...'
    listaLocalidades = []
    for numLocalidad in sorted (diccLocalidades.keys()):
      listaLocalidades.append (str (numLocalidad) + ': ' + diccLocalidades[numLocalidad])
    if indice.column() == 1:  # Localidad inicial
      textoLocalidad = str (mod_actual.locs_iniciales[numObjeto]) + ': ' + diccLocalidades[mod_actual.locs_iniciales[numObjeto]]
    else:  # Localidad actual
      textoLocalidad = str (locs_objs[numObjeto]) + ': ' + diccLocalidades[locs_objs[numObjeto]]
    dialogo = ModalEntrada (dlg_desc_objs, (_('Start location') if indice.column() == 1 else _('Current location')) + ':', textoLocalidad)
    dialogo.setComboBoxItems (listaLocalidades)
    dialogo.setWindowTitle   (_('Edit'))
    if dialogo.exec_() == QDialog.Accepted:
      textoLocalidad = dialogo.textValue()
      numLocalidad   = textoLocalidad[:textoLocalidad.find (':')]
      if indice.column() == 1:  # Localidad inicial
        mod_actual.locs_iniciales[numObjeto] = int (numLocalidad)
      else:  # Localidad actual
        locs_objs[numObjeto] = int (numLocalidad)
        if sys.version_info[0] < 3:
          proc_interprete.stdin.write ('%' + str (numObjeto) + '=' + numLocalidad + '\n')
        else:  # Python 3+
          proc_interprete.stdin.write (bytes ('%' + str (numObjeto) + '=' + numLocalidad + '\n', locale.getpreferredencoding()))
    return
  if indice.column() == 2 + adicional and mod_actual.NUM_ATRIBUTOS[0] == 1:  # Pseudoatributo prenda en Quill para QL
    return muestraFallo (_('Not editable'), _('This value cannot be edited directly.') + '\n\n' + _('This is the pseudo-attribute "wearable", which cannot be directly modified. Its value depends on the code of the word assigned to this object. Assign to it a word with code value between 200 and 254 to make it "wearable", or a value lower than 200 to make it not "wearable".'), QMessageBox.Information)
  if mod_actual.NUM_ATRIBUTOS[0] == 1 or indice.column() == 5 + adicional:  # Nombre
    diccNombres = {}
    for palabra, codigo, tipo in mod_actual.vocabulario:
      if tipo != tipo_nombre:
        continue
      if codigo in diccNombres:
        diccNombres[codigo] += '|' + palabra
      else:
        diccNombres[codigo] = palabra
    diccNombres[255] = _('(No noun)')
    listaNombres = []
    for numNombre in sorted (diccNombres.keys()):
      listaNombres.append (str (numNombre) + ': ' + diccNombres[numNombre])
    nombre      = mod_actual.nombres_objs[numObjeto][0]
    textoNombre = str (nombre)
    if nombre in diccNombres:
      textoNombre += ': ' + diccNombres[nombre]
    dialogo = ModalEntrada (dlg_desc_objs, _('Noun') + ':', textoNombre)
    dialogo.setComboBoxEditable (True)
    dialogo.setComboBoxItems    (listaNombres)
    dialogo.setWindowTitle      (_('Edit'))
    if dialogo.exec_() == QDialog.Accepted:
      textoNombre = dialogo.textValue().strip().lower()
      if not textoNombre:
        textoNombre = '255'
      elif ':' in textoNombre:
        textoNombre = textoNombre[:textoNombre.find (':')]
      try:
        numNombre = int (textoNombre)
      except:
        numNombre = None
      if numNombre == None:  # Debe ser una palabra
        textoNombre = textoNombre[:mod_actual.LONGITUD_PAL]
        otroTipo    = None  # Si se ha encontrado la palabra en el vocabulario con otro tipo
        for palabra, codigo, tipo in mod_actual.vocabulario:
          if palabra == textoNombre:
            if tipo == tipo_nombre:
              numNombre = codigo
              break
            otroTipo = tipo
        if numNombre == None:
          if otroTipo != None:
            muestraFallo (_('Wrong type for word'), _('The word "%(word)s" cannot be used here because its vocabulary type is %(wrongType)s, when it should be %(correctType)s.') % {'correctType': mod_actual.TIPOS_PAL[tipo_nombre], 'word': textoNombre, 'wrongType': mod_actual.TIPOS_PAL[otroTipo]})
          else:
            muestraFallo (_('Non-existent noun'), _('Noun "%s" not found in the vocabulary') % textoNombre)
          return
      if numNombre != 255:
        for palabra, codigo, tipo in mod_actual.vocabulario:
          if tipo != tipo_nombre:
            continue
          if codigo == numNombre:
            break
        else:
          return muestraFallo (_('Non-existent noun'), _('Noun with code %d not found in the vocabulary') % numNombre)
      mod_actual.nombres_objs[numObjeto] = (numNombre, mod_actual.nombres_objs[numObjeto][1])

def editaVocabulario (indice):
  # type: (QModelIndex) -> None
  """Permite editar una entrada de vocabulario, tras hacer doble clic en su tabla"""
  nuevaPal = None  # Entrada de vocabulario modificada
  numFila  = indice.row()
  palVocab = mod_actual.vocabulario[numFila]
  if indice.column() == 0:  # Palabra
    dialogo = ModalEntrada (dlg_vocabulario, _('Text of the word:'), daTextoImprimible (palVocab[0]))
    dialogo.setWindowTitle (_('Edit'))
    if dialogo.exec_() == QDialog.Accepted:
      nuevaPal = (str (dialogo.textValue())[:mod_actual.LONGITUD_PAL].lower(), ) + palVocab[1:]
  elif indice.column() == 1:  # C�digo
    dialogo = ModalEntrada (dlg_vocabulario, _('Code of the word:'), str (palVocab[1]))
    dialogo.setInputMode   (QInputDialog.IntInput)
    dialogo.setIntRange    (0, 255)
    dialogo.setWindowTitle (_('Edit'))
    if dialogo.exec_() == QDialog.Accepted:
      nuevaPal = (palVocab[0], dialogo.intValue(), palVocab[2])
  else:  # indice.column() == 2:  # Tipo
    tiposPalabra = {255: _('Reserved')}
    for i in range (len (mod_actual.TIPOS_PAL)):
      tiposPalabra[i] = mod_actual.TIPOS_PAL[i]
    dialogo = ModalEntrada (dlg_vocabulario, _('Type of the word:'), tiposPalabra[palVocab[2]])
    dialogo.setComboBoxEditable (True)
    dialogo.setComboBoxItems    (sorted (tiposPalabra.values()))
    dialogo.setWindowTitle      (_('Edit'))
    if dialogo.exec_() == QDialog.Accepted and dialogo.textValue() in tiposPalabra.values():
      nuevaPal = (palVocab[0], palVocab[1],
                  list (tiposPalabra.keys())[list (tiposPalabra.values()).index (dialogo.textValue())])
  dlg_vocabulario.activacionAnterior = time.time()  # Para descartar evento activated posterior
  if not nuevaPal or mod_actual.vocabulario[numFila] == nuevaPal:
    return  # No se ha modificado
  nuevaEntradaVocabulario (nuevaPal, numFila)

def enviaPuntoRuptura (numProceso, numEntrada, numCondacto):
  """Env�a al int�rprete un punto de ruptura para a�adirlo o eliminarlo"""
  if not proc_interprete:
    return
  if sys.version_info[0] < 3:
    proc_interprete.stdin.write ('$' + str (numProceso) + ',' + str (numEntrada) + ',' + str (numCondacto) + '\n')
  else:  # Python 3+
    proc_interprete.stdin.write (bytes ('$' + str (numProceso) + ',' + str (numEntrada) + ',' + str (numCondacto) + '\n', locale.getpreferredencoding()))
  proc_interprete.stdin.flush()

def ejecutaPasos (indicePasos):
  """Pide al int�rprete ejecutar cierto n�mero de pasos"""
  teclasPasos = '1 \t\n'
  proc_interprete.stdin.write (teclasPasos[indicePasos] if sys.version_info[0] < 3 else bytes ([ord (teclasPasos[indicePasos])]))
  if indicePasos < 3:  # Nueva l�nea final
    proc_interprete.stdin.write ('\n' if sys.version_info[0] < 3 else b'\n')
  proc_interprete.stdin.flush()

def ejecutaPorPasos ():
  """Ejecuta la base de datos para depuraci�n paso a paso"""
  global banderas, locs_objs, locs_objs_antes, pilas_pendientes, inicio_debug, proc_interprete
  banderas     = [0] * mod_actual.NUM_BANDERAS[0]  # Inicializamos las banderas
  inicio_debug = True
  # Inicializamos las localidades de los objetos
  locs_objs = {}
  for numObjeto in mod_actual.locs_iniciales if type (mod_actual.locs_iniciales) == dict else range (len (mod_actual.locs_iniciales)):
    locs_objs[numObjeto] = mod_actual.locs_iniciales[numObjeto]
  locs_objs_antes = locs_objs.copy()
  accBanderas.setEnabled   (True)
  accPasoAPaso.setEnabled  (False)
  menu_BD_nueva.setEnabled (False)
  selector.setCursor (Qt.BusyCursor)  # Puntero de rat�n de trabajo en segundo plano
  rutaInterprete = os.path.join (os.path.dirname (os.path.realpath (__file__)), 'interprete.py')
  argumentos     = ['python', rutaInterprete, '--ide', '--system', mod_actual.NOMBRE_SISTEMA.lower(), nombre_fich_bd]
  if nombre_fich_gfx:
    argumentos.append (nombre_fich_gfx)
  devnull = open (os.devnull, 'w')
  proc_interprete  = subprocess.Popen (argumentos, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = devnull)
  pilas_pendientes = []
  hilo = ManejoInterprete (proc_interprete, aplicacion)
  hilo.cambiaBanderas.connect (actualizaBanderas)
  hilo.cambiaObjetos.connect  (actualizaObjetos)
  hilo.cambiaImagen.connect   (actualizaVentanaJuego)
  hilo.cambiaPila.connect     (actualizaPosProcesos)
  hilo.start()
  # Enviamos al int�rprete los puntos de ruptura que ya haya
  for numProceso in puntos_ruptura:
    for numEntrada, numCondacto, posicion in puntos_ruptura[numProceso]:
      enviaPuntoRuptura (numProceso, numEntrada, numCondacto)

def exportaBD ():
  """Exporta la base de datos a fichero"""
  global dlg_guardar, mod_actual
  if not dlg_guardar:  # Di�logo no creado a�n
    filtro = []
    for funcion, extensiones, descripcion in info_exportar:
      filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
    dlg_guardar = QFileDialog (selector, _('Export database'), os.curdir, ';;'.join (filtro))
    dlg_guardar.setAcceptMode (QFileDialog.AcceptSave)
    dlg_guardar.setLabelText  (QFileDialog.LookIn,   _('Places'))
    dlg_guardar.setLabelText  (QFileDialog.FileName, _('&Name:'))
    dlg_guardar.setLabelText  (QFileDialog.FileType, _('Filter:'))
    dlg_guardar.setLabelText  (QFileDialog.Accept,   _('&Save'))
    dlg_guardar.setLabelText  (QFileDialog.Reject,   _('&Cancel'))
    dlg_guardar.setOption     (QFileDialog.DontConfirmOverwrite)
    dlg_guardar.setOption     (QFileDialog.DontUseNativeDialog)
  if dlg_guardar.exec_():  # No se ha cancelado
    indiceFiltro  = list (dlg_guardar.nameFilters()).index (dlg_guardar.selectedNameFilter())
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_guardar.selectedFiles()[0])
    extension     = '.' + info_exportar[indiceFiltro][1][0]
    if nombreFichero[- len (extension):].lower() != extension:
      nombreFichero += extension
    if os.path.isfile (nombreFichero):
      dlgSiNo = QMessageBox (selector)
      dlgSiNo.addButton (_('&Yes'), QMessageBox.YesRole)
      dlgSiNo.addButton (_('&No'), QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle (_('Overwrite'))
      dlgSiNo.setText (_('A file already exists with path and name:\n\n') + nombreFichero)
      dlgSiNo.setInformativeText (_('\nDo you want to overwrite it?'))
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el bot�n S�
        return
    selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
    try:
      fichero = open (nombreFichero, 'w+b')
    except IOError as excepcion:
      muestraFallo (_('Unable to open the file:\n') + nombreFichero,
                    _('Cause:\n') + excepcion.args[1])
      selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
      return
    hilo = ManejoExportacion (aplicacion, fichero, indiceFiltro)
    hilo.finished.connect (lambda: finExportacion (fichero))
    hilo.start()

def finExportacion (fichero):
  fichero.close()
  selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def icono (nombre):
  """Devuelve un QIcon, sacando la imagen de la carpeta de iconos"""
  return QIcon (os.path.join (os.path.dirname (os.path.realpath (__file__)), 'iconos_ide', nombre + '.png'))

def importaBD (nombreFicheroBD, indiceFuncion = None, nombreFicheroGfx = None):
  """Importa una base de datos desde el fichero de nombre dado, devolviendo verdadero si todo ha ido bien"""
  global mod_actual, nombre_fich_bd, nombre_fich_gfx
  nombre_fich_bd = None
  try:
    fichero = open (nombreFicheroBD, 'rb')
  except IOError as excepcion:
    muestraFallo (_('Unable to open the file:\n' + nombreFicheroBD),
                  _('Cause:\n') + excepcion.args[1])
    return
  if '.' not in nombreFicheroBD:
    muestraFallo (_('Unable to import a database from:\n' + nombreFicheroBD),
                  _('Cause:\nThe file lacks an extension'))
    return
  modulos = []  # M�dulos que soportan la extensi�n, junto con su funci�n de carga
  if indiceFuncion != None:
    modulo, funcion, extensiones, descripcion = info_importar[indiceFuncion]
    modulos.append ((modulo, funcion))
  else:
    extension = nombreFicheroBD[nombreFicheroBD.rindex ('.') + 1 :].lower()
    for modulo, funcion, extensiones, descripcion in info_importar:
      if extension in extensiones:
        modulos.append ((modulo, funcion))
    if not modulos:
      muestraFallo (_('Unable to import a database from:\n') + nombreFicheroBD,
                    _('Cause:\nUnknown extension'))
      return
  # Importamos la BD y damos acceso al m�dulo a funciones del IDE
  hayFallo = True
  for modulo, funcion in modulos:
    recargar   = modulo in sys.modules
    mod_actual = __import__ (modulo)
    if recargar:
      mod_actual = reload (mod_actual)
    mod_actual.muestraFallo = muestraFallo
    if args.no_entry_end and 'nada_tras_flujo' in mod_actual.__dict__:
      mod_actual.nada_tras_flujo.append (True)
    # Solicitamos la importaci�n
    if mod_actual.__dict__[funcion] (fichero, os.path.getsize (nombreFicheroBD)) != False:
      hayFallo = False
      break
    fichero.seek (0)
  fichero.close()
  if hayFallo:
    muestraFallo (_('Unable to import a database from:\n') +
                  nombreFicheroBD, _('Cause:\nIncompatible file format or corrupted database'))
    mod_actual = None
    return
  nombre_fich_bd  = nombreFicheroBD
  nombre_fich_gfx = nombreFicheroGfx
  rutaBD = os.path.abspath (nombreFicheroBD)
  if len (os.path.relpath (nombreFicheroBD)) < len (rutaBD):
    rutaBD = os.path.relpath (nombreFicheroBD)
  postCarga (rutaBD)
  return True

def imprimeCabecera (verbo, nombre, numEntrada, numProceso):
  """Imprime la cabecera de la entrada numEntrada del proceso, con el verbo y nombre de c�digos dados, en campo_txt en la posici�n del cursor actual"""
  campo_txt.setTextColor (QColor (200, 200, 200))  # Color gris claro
  campo_txt.setFontItalic (True)  # Cursiva activada
  if verbo == 255:
    campo_txt.insertPlainText ('  _  ')
  elif verbo == 1 and (1, 255) in pal_sinonimo:
    campo_txt.insertPlainText ('  *  ')
  elif (verbo, tipo_verbo) in pal_sinonimo:  # Hay un verbo con ese c�digo
    campo_txt.insertPlainText (pal_sinonimo[(verbo, tipo_verbo)].center (5))
  elif verbo < mod_actual.NOMB_COMO_VERB[0] and (verbo, tipo_nombre) in pal_sinonimo:  # Es nombre convertible en verbo
    campo_txt.insertPlainText (pal_sinonimo[(verbo, tipo_nombre)].center (5))
  # TODO: preposiciones convertibles a verbo de SWAN
  else:
    campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    if (numProceso, verbo, tipo_verbo) not in pals_no_existen:
      muestraFallo (_('Non-existent verb'), _('Verb with code %d not found in the vocabulary') % verbo)
      pals_no_existen.append ((numProceso, verbo, tipo_verbo))
    campo_txt.insertPlainText (str (verbo).center (5))
    campo_txt.setTextColor (QColor (200, 200, 200))  # Color gris claro
  campo_txt.insertPlainText ('  ')
  if nombre == 255:
    campo_txt.insertPlainText ('  _')
  elif nombre == 1 and (1, 255) in pal_sinonimo:
    campo_txt.insertPlainText ('  *')
  elif (nombre, tipo_nombre) in pal_sinonimo:
    campo_txt.insertPlainText (pal_sinonimo[(nombre, tipo_nombre)].center (5).rstrip())
  else:
    campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    if (numProceso, nombre, tipo_nombre) not in pals_no_existen:
      muestraFallo (_('Non-existent noun'), _('Noun with code %d not found in the vocabulary') % nombre)
      pals_no_existen.append ((numProceso, nombre, tipo_nombre))
    campo_txt.insertPlainText (str (nombre).center (5).rstrip())
  campo_txt.setFontItalic (False)  # Cursiva desactivada
  campo_txt.setTextBackgroundColor (color_base)
  campo_txt.textCursor().block().setUserState (numEntrada)  # Guardamos el n�mero de la entrada

def imprimeCondacto (condacto, parametros, inalcanzable = False, nuevaLinea = True):
  """Imprime el condacto de c�digo y par�metros dados en campo_txt en la posici�n del cursor actual, opcionalmente indicando si era c�digo inalcanzable. Devuelve True si el par�metro inalcanzable era True o el condacto cambia el flujo incondicionalmente"""
  if inalcanzable:
    campo_txt.setTextColor (QColor (60, 60, 60))  # Color gris muy oscuro
  campo_txt.insertPlainText (('\n' if nuevaLinea else '') + '  ')
  if condacto > 127 and mod_actual.INDIRECCION:  # Condacto indirecto
    condacto -= 128
    indirecto = '@'  # Condacto indirecto
  else:
    indirecto = ' '  # Condacto no indirecto
  if condacto in mod_actual.condiciones:
    if not inalcanzable:
      campo_txt.setTextColor (QColor (100, 255, 50))  # Color verde claro
    nombre, tiposParams = mod_actual.condiciones[condacto][:2]
  elif condacto - (100 if mod_actual.NOMBRE_SISTEMA == 'QUILL' else 0) in mod_actual.acciones:
    if not inalcanzable:
      campo_txt.setTextColor (QColor (100, 200, 255))  # Color azul claro
    nombre, tiposParams = mod_actual.acciones[condacto - (100 if mod_actual.NOMBRE_SISTEMA == 'QUILL' else 0)][:2]
    if nombre == 'NEWTEXT' and indirecto == '@':
      indirecto = ' '
      nombre    = 'DEBUG'
  else:  # No deber�a ocurrir
    if not inalcanzable:
      prn (_('FIXME: Condact %d not recognized by the library') % condacto, file = sys.stderr)
      campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    nombre      = str (condacto)
    tiposParams = '?' * len (parametros)
  if parametros:  # Imprimiremos los par�metros
    campo_txt.insertPlainText (nombre.center (7) + ' ')
    for p in range (len (parametros)):
      if inalcanzable:
        campo_txt.setTextColor (QColor (60, 60, 60))  # Color gris muy oscuro
      else:
        campo_txt.setTextColor (QColor (255, 160, 32))  # Color anaranjado
      formato   = None
      mensaje   = None
      parametro = parametros[p]
      if p > 0:
        campo_txt.insertPlainText (',')
      elif indirecto == '@':
        parametro = '@' + str (parametro)
      if (p > 0 or indirecto == ' ') and len (tiposParams) > p:
        if (tiposParams[p] == '%' and (parametro < 1 or parametro > 99))              or \
           (tiposParams[p] == 'b' and parametro not in (1, 2, 4, 8, 16, 32, 64, 128)) or \
           (tiposParams[p] == 'l' and parametro >= len (mod_actual.desc_locs))        or \
           (tiposParams[p] == 'L' and parametro >= len (mod_actual.desc_locs) and parametro not in range (252, 256)) or \
           (tiposParams[p] == 'm' and parametro >= len (mod_actual.msgs_usr))       or \
           (tiposParams[p] == 'o' and parametro >= len (mod_actual.desc_objs))      or \
           (tiposParams[p] == 'p' and parametro >= len (mod_actual.tablas_proceso)) or \
           (tiposParams[p] == 's' and parametro >= len (mod_actual.msgs_sys))       or \
           (tiposParams[p] == 'w' and parametro >= 8) or \
           (tiposParams[p] == 'W' and parametro > 32767):
          if inalcanzable:
            campo_txt.setTextColor (QColor (120, 0, 0))  # Color rojo oscuro
          else:
            campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
        elif tiposParams == 'l' and accMostrarLoc.isChecked():
          mensaje = mod_actual.desc_locs[parametro]
        elif tiposParams == 'm' and accMostrarUsr.isChecked():
          mensaje = mod_actual.msgs_usr[parametro]
        elif tiposParams == 'o' and accMostrarObj.isChecked():
          mensaje = mod_actual.desc_objs[parametro]
        elif tiposParams == 's' and accMostrarSys.isChecked():
          mensaje = mod_actual.msgs_sys[parametro]
        elif tiposParams[p] == 'i' and parametro > 128:  # Es un n�mero entero negativo
          parametro -= 256
        elif not inalcanzable and tiposParams == 'p':  # Es un proceso
          cursor  = campo_txt.textCursor()
          formato = cursor.charFormat()
          formato.setAnchor (True)
          formato.setAnchorHref ('proceso:' + str (parametro))
          formato.setFontUnderline (True)
          formato.setToolTip (_('Do Ctrl+click here to open process %d') % parametro)
      if formato:
        parametro = str (parametro)
        campo_txt.insertPlainText (' ' * (4 - len (parametro)))
        cursor.insertText (parametro, formato)
        campo_txt.quitaFormatoEnlace()
      else:
        campo_txt.insertPlainText (str (parametro).rjust (4))
    if not inalcanzable and mensaje != None:
      if accMostrarRec.isChecked():  # Recortar al ancho de l�nea disponible
        qfm = QFontMetrics (campo_txt.font())
        columnasVisibles = int ((campo_txt.size().width() - BarraIzquierda.anchoBarra) // (qfm.size (0, '#').width()))
      if not accMostrarRec.isChecked() or columnasVisibles > 26:  # No recortamos o hay espacio suficiente para mostrar algo de texto
        mensaje = daTextoImprimible (mensaje)
        if not inalcanzable:
          campo_txt.setTextColor (QColor (100, 100, 100))  # Color gris oscuro
        campo_txt.insertPlainText ('       "')
        campo_txt.setFontItalic (True)  # Cursiva activada
        if accMostrarRec.isChecked() and len (mensaje) > columnasVisibles - 26:  # Se recortar� al ancho de l�nea disponible
          cursor  = campo_txt.textCursor()
          formato = cursor.charFormat()
          formato.setToolTip (daTextoComoParrafoHtml (mensaje))
          cursor.insertText (mensaje[: columnasVisibles - 26], formato)
          formato.setToolTip ('')
          cursor.insertText (u'\u2026', formato)
        else:  # No se recorta
          campo_txt.insertPlainText (mensaje)
        campo_txt.setFontItalic (False)  # Cursiva desactivada
        campo_txt.insertPlainText ('"')
  else:  # Condacto sin par�metros
    campo_txt.insertPlainText ((nombre + indirecto).rstrip().center (7).rstrip())
  if inalcanzable or campo_txt.condactos[campo_txt.condactosPorCod[condacto]][2]:
    return True
  return False

def irAEntradaProceso ():
  """Mueve el cursor a la entrada del proceso actual que elija el usuario"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  dialogo    = ModalEntrada (dlg_procesos, _('Entry number:'), '')
  dialogo.setInputMode   (QInputDialog.IntInput)
  dialogo.setIntRange    (0, len (proceso[0]) - 1)
  dialogo.setWindowTitle (_('Go to'))
  if dialogo.exec_() == QDialog.Accepted:
    campo_txt.irAEntrada (dialogo.intValue())
    campo_txt.centraLineaCursor()

def menuContextualTextos (dialogoTextos, listaTextos, punto):
  """Muestra el men� contextual para un di�logo de textos"""
  contextual   = QMenu (dialogoTextos)
  accionCopiar = QAction (_('&Copy'),  contextual)
  accionPegar  = QAction (_('&Paste'), contextual)
  accionCopiar.setShortcut (QKeySequence.Copy)
  accionPegar.setShortcut  (QKeySequence.Paste)
  accionCopiar.triggered.connect (lambda: copiaTexto (dialogoTextos, listaTextos))
  accionPegar.triggered.connect  (lambda: pegaTexto  (dialogoTextos, listaTextos))
  contextual.addAction (accionCopiar)
  contextual.addAction (accionPegar)
  contextual.exec_ (dialogoTextos.viewport().mapToGlobal (punto))

def menuContextualVocabulario (punto):
  """Muestra el men� contextual para la tabla de vocabulario"""
  # Primero obtenemos la informaci�n que necesitaremos
  indice    = dlg_vocabulario.model().mapToSource (dlg_vocabulario.indexAt (punto))
  seleccion = dlg_vocabulario.selectionModel().selection()
  filasSeleccionadas = set()
  for indiceCelda in seleccion.indexes():
    filasSeleccionadas.add (indiceCelda.row())
  # Construimos los componentes del men� contextual
  contextual = QMenu (dlg_vocabulario)
  accionNueva    = QAction (_('Add &entry'),   contextual)
  accionSinonimo = QAction (_('Add &synonym'), contextual)
  accionNueva.setShortcut (QKeySequence (Qt.Key_Enter))
  accionSinonimo.setShortcut ('Ctrl+S')
  accionNueva.triggered.connect    (lambda: nuevaFilaVocabulario (-1))  # No necesita la fila del click
  accionSinonimo.triggered.connect (lambda: nuevaFilaVocabulario (indice, True))
  accionSinonimo.setEnabled (len (filasSeleccionadas) == 1)
  contextual.addAction (accionNueva)
  contextual.addAction (accionSinonimo)
  contextual.exec_ (dlg_vocabulario.viewport().mapToGlobal (punto))

def muestraAcercaDe ():
  """Muestra el di�logo 'Acerca de'"""
  global dlg_acerca_de
  if not dlg_acerca_de:  # Di�logo no creado a�n
    # Cogeremos s�lo los n�meros de la versi�n de Python
    fin = sys.version.find (' (')
    dlg_acerca_de = QMessageBox (selector)
    dlg_acerca_de.addButton (_('&Accept'), QMessageBox.AcceptRole)
    dlg_acerca_de.setIconPixmap (icono_ide.pixmap (96))
    dlg_acerca_de.setText ('NAPS: The New Age PAW-like System\n' +
        _('Integrated Development Environment (IDE)\n') +
        'Copyright � 2010, 2018-2025 Jos� Manuel Ferrer Ortiz')
    dlg_acerca_de.setInformativeText (_('PyQt version: ') +
        PYQT_VERSION_STR + _('\nQt version: ') + QT_VERSION_STR +
        _('\nPython version: ') + sys.version[:fin])
    dlg_acerca_de.setWindowTitle (_('&About NAPS IDE', 1))
  dlg_acerca_de.exec_()

def muestraBanderas ():
  """Muestra el di�logo de banderas"""
  global dlg_banderas, mdi_banderas
  if dlg_banderas and mdi_banderas in selector.centralWidget().subWindowList():
    # Di�logo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (mdi_banderas)
      if selector.centralWidget().activeSubWindow() == mdi_banderas:
        return  # Di�logo recuperado correctamente
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
  dlg_banderas = QWidget (selector)
  layout       = VFlowLayout (dlg_banderas)
  for b in range (mod_actual.NUM_BANDERAS[0]):
    botonBandera = QPushButton (str (b % 100) + ': ' + str (banderas[b]), dlg_banderas)
    botonBandera.clicked.connect (lambda estado, numBandera = b: editaBandera (numBandera))
    botonBandera.setObjectName ('bandera')
    botonBandera.setStyleSheet (estilo_fila_par)
    botonBandera.setToolTip ((_('Value of flag %d: ') % b) + str (banderas[b]))
    layout.addWidget (botonBandera)
  dlg_banderas.setLayout      (layout)
  dlg_banderas.setStyleSheet  ('QPushButton#bandera {padding: 0}')  # Para limitar ancho de columnas del di�logo
  dlg_banderas.setWindowTitle (_('&Flags', 1))
  mdi_banderas = selector.centralWidget().addSubWindow (dlg_banderas)
  mdi_banderas.setOption (QMdiSubWindow.RubberBandResize)
  dlg_banderas.show()

def muestraContadores ():
  """Muestra el di�logo de contadores"""
  global dlg_contadores
  if not dlg_contadores:  # Di�logo no creado a�n
    dlg_contadores = QMessageBox (selector)
    dlg_contadores.addButton (_('&Accept'), QMessageBox.AcceptRole)
    dlg_contadores.setText (
      _('Locations: ')                + str (len (mod_actual.desc_locs))      + '\n'   + \
      _('Objects: ')                  + str (len (mod_actual.desc_objs))      + '\n'   + \
      _('&System messages', 1) + ': ' + str (len (mod_actual.msgs_sys))       + '\t\n' + \
      _('&User messages',   1) + ': ' + str (len (mod_actual.msgs_usr))       + '\n'   + \
      _('Process tables')  + ': '     + str (len (mod_actual.tablas_proceso)) + '\n'   + \
      _('Vocabulary words: ')         + str (len (mod_actual.vocabulario)))
    dlg_contadores.setWindowTitle (_('&Counters', 1))
  dlg_contadores.exec_()

def muestraDescLocs ():
  """Muestra el di�logo para consultar las descripciones de localidades"""
  muestraTextos (dlg_desc_locs, mod_actual.desc_locs, 'desc_localidades', mdi_desc_locs)

def muestraDescObjs ():
  """Muestra el di�logo para consultar las descripciones de objetos"""
  muestraTextos (dlg_desc_objs, mod_actual.desc_objs, 'desc_objetos', mdi_desc_objs)

def muestraFallo (mensaje, detalle, icono = QMessageBox.Warning):
  """Muestra un di�logo de fallo leve"""
  global dlg_fallo
  if not dlg_fallo:  # Di�logo no creado a�n
    dlg_fallo = QMessageBox (selector)
    dlg_fallo.addButton (_('&Accept'), QMessageBox.AcceptRole)
  if icono == QMessageBox.Information:
    dlg_fallo.setWindowTitle (_('Information'))
  else:
    dlg_fallo.setWindowTitle (_('Failure'))
  dlg_fallo.setIcon (icono)
  dlg_fallo.setText (mensaje)
  dlg_fallo.setInformativeText (detalle)
  dlg_fallo.exec_()

def muestraMsgSys ():
  """Muestra el di�logo para consultar los mensajes de sistema"""
  muestraTextos (dlg_msg_sys, mod_actual.msgs_sys, 'msgs_sistema', mdi_msg_sys)

def muestraMsgUsr ():
  """Muestra el di�logo para consultar los mensajes de usuario"""
  muestraTextos (dlg_msg_usr, mod_actual.msgs_usr, 'msgs_usuario', mdi_msg_usr)

def muestraProcesos ():
  """Muestra el di�logo para las tablas de proceso"""
  global campo_txt, dlg_procesos, mdi_procesos, pestanyas
  if dlg_procesos and mdi_procesos in selector.centralWidget().subWindowList():  # Di�logo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (mdi_procesos)
      if selector.centralWidget().activeSubWindow() == mdi_procesos:
        return  # Di�logo recuperado correctamente
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
  dlg_procesos = QWidget (selector)
  layout       = QVBoxLayout (dlg_procesos)
  pestanyas    = QTabBar (dlg_procesos)
  campo_txt    = CampoTexto (dlg_procesos)
  dlg_procesos.setObjectName ('procesos')
  layout.addWidget (pestanyas)
  layout.addWidget (campo_txt)
  layout.setContentsMargins (1, 1, 1, 1)
  pestanyas.currentChanged.connect (cambiaProceso)
  procesos = sorted (mod_actual.tablas_proceso.keys()) if type (mod_actual.tablas_proceso) == dict else range (len (mod_actual.tablas_proceso))
  for numero in procesos:
    strNumero = str (numero)
    titulo    = _('Process ') + strNumero
    if 'NOMBRES_PROCS' in mod_actual.__dict__:
      if (type (mod_actual.NOMBRES_PROCS) in (list, tuple) and numero < len (mod_actual.NOMBRES_PROCS)) or \
         (type (mod_actual.NOMBRES_PROCS) == dict and numero in mod_actual.NOMBRES_PROCS):
        titulo = mod_actual.NOMBRES_PROCS[numero]
      elif type (mod_actual.NOMBRES_PROCS) == dict and None in mod_actual.NOMBRES_PROCS:
        titulo = mod_actual.NOMBRES_PROCS[None] + ' ' + strNumero
    if len (procesos) < 6:  # Hay pocos procesos, espacio de sobra
      pestanyas.addTab (titulo)
    else:
      numPestanya = pestanyas.count()
      pestanyas.addTab (strNumero)
      pestanyas.setTabToolTip (numPestanya, titulo)
  paleta = QPalette (campo_txt.palette())
  paleta.setColor (QPalette.Base, color_base)              # Color de fondo gris oscuro
  paleta.setColor (QPalette.Text, QColor (255, 255, 255))  # Color de frente (para el cursor) blanco
  fuente = QFont ('Courier')  # Fuente que usaremos
  fuente.setPixelSize (tam_fuente)
  fuente.setStyleHint (QFont.TypeWriter)  # Como alternativa, usar una fuente monoespaciada
  campo_txt.setFont            (fuente)
  campo_txt.setPalette         (paleta)
  campo_txt.setUndoRedoEnabled (False)
  dlg_procesos.setLayout      (layout)
  dlg_procesos.setWindowTitle (_('Process tables'))
  mdi_procesos = selector.centralWidget().addSubWindow (dlg_procesos)
  mdi_procesos.setOption (QMdiSubWindow.RubberBandResize)
  dlg_procesos.showMaximized()

def muestraTextos (dialogo, listaTextos, tipoTextos, subventanaMdi):
  """Muestra uno de los di�logos para consultar los textos"""
  global dlg_desc_locs, dlg_desc_objs, dlg_msg_sys, dlg_msg_usr, mdi_desc_locs, mdi_desc_objs, mdi_msg_sys, mdi_msg_usr
  if dialogo:  # Di�logo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (subventanaMdi)
      if selector.centralWidget().activeSubWindow() == subventanaMdi:
        return  # Di�logo recuperado correctamente
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  dialogo = QTableView (selector)
  dialogo.setContextMenuPolicy (Qt.CustomContextMenu)
  if tipoTextos in ('desc_localidades', 'desc_objetos'):
    dialogo.setModel ((ModeloObjetos if tipoTextos == 'desc_objetos' else ModeloLocalidades) (dialogo, listaTextos))
  else:
    dialogo.horizontalHeader().setStretchLastSection(True)
    dialogo.setModel (ModeloTextos (dialogo, listaTextos))
  atajoCopiar = QShortcut (QKeySequence.Copy,  dialogo)
  atajoPegar  = QShortcut (QKeySequence.Paste, dialogo)
  atajoCopiar.activated.connect (lambda: copiaTexto (dialogo, listaTextos))
  atajoPegar.activated.connect  (lambda: pegaTexto  (dialogo, listaTextos))
  dialogo.customContextMenuRequested.connect (functools.partial (menuContextualTextos, dialogo, listaTextos))
  titulo = {'desc_localidades': _('&Location data', 1), 'desc_objetos': _('&Object data', 1), 'msgs_sistema': _('&System messages', 1), 'msgs_usuario': _('&User messages', 1)}[tipoTextos]
  dialogo.setWindowTitle (titulo)
  subventanaMdi = selector.centralWidget().addSubWindow (dialogo)
  if tipoTextos == 'desc_localidades':
    dialogo.doubleClicked.connect (editaLocalidad)
    dlg_desc_locs = dialogo
    mdi_desc_locs = subventanaMdi
  elif tipoTextos == 'desc_objetos':
    dialogo.doubleClicked.connect (editaObjeto)
    dlg_desc_objs = dialogo
    mdi_desc_objs = subventanaMdi
  elif tipoTextos == 'msgs_sistema':
    dialogo.doubleClicked.connect (editaMsgSys)
    dlg_msg_sys = dialogo
    mdi_msg_sys = subventanaMdi
  else:
    dialogo.doubleClicked.connect (editaMsgUsr)
    dlg_msg_usr = dialogo
    mdi_msg_usr = subventanaMdi
  dialogo.showMaximized()
  if tipoTextos in ('desc_localidades', 'desc_objetos'):
    dialogo.horizontalHeader().resizeSections (QHeaderView.ResizeToContents)
  if inicio_debug:
    selector.setCursor (Qt.BusyCursor)  # Puntero de rat�n de trabajo en segundo plano
  else:
    selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def muestraVistaVocab ():
  """Muestra el di�logo para consultar el vocabulario"""
  global dlg_vocabulario, mdi_vocabulario
  if dlg_vocabulario:  # Di�logo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (mdi_vocabulario)
      if selector.centralWidget().activeSubWindow() == mdi_vocabulario:
        return  # Di�logo recuperado correctamente
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  modeloOrden = QSortFilterProxyModel (dlg_vocabulario)
  modeloOrden.setSourceModel (ModeloVocabulario (dlg_vocabulario))
  dlg_vocabulario = QTableView (selector)
  dlg_vocabulario.activacionAnterior = 0
  dlg_vocabulario.setModel (modeloOrden)
  dlg_vocabulario.setSortingEnabled (True)
  dlg_vocabulario.sortByColumn (0, Qt.AscendingOrder)  # Orden alfab�tico por texto de palabras
  # dlg_vocabulario.setHorizontalHeaderLabels (('Palabra', 'N�mero', 'Tipo'))
  dlg_vocabulario.setContextMenuPolicy (Qt.CustomContextMenu)
  dlg_vocabulario.setWindowTitle       (_('&Vocabulary', 1))
  dlg_vocabulario.activated.connect     (lambda indice: nuevaFilaVocabulario (modeloOrden.mapToSource (indice)))
  dlg_vocabulario.doubleClicked.connect (lambda indice: editaVocabulario     (modeloOrden.mapToSource (indice)))
  dlg_vocabulario.customContextMenuRequested.connect (menuContextualVocabulario)
  atajoSinonimo = QShortcut (QKeySequence ('Ctrl+S'), dlg_vocabulario)
  atajoSinonimo.activated.connect (lambda: nuevaFilaVocabulario (None, True))
  mdi_vocabulario = selector.centralWidget().addSubWindow (dlg_vocabulario)
  dlg_vocabulario.showMaximized()
  if inicio_debug:
    selector.setCursor (Qt.BusyCursor)  # Puntero de rat�n de trabajo en segundo plano
  else:
    selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def nuevaBD (posicion):
  """Ejecuta la funci�n de �ndice posicion para crear una nueva base de datos vac�a"""
  global mod_actual, nombre_fich_bd
  nombre_fich_bd = None
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  cierraDialogos()
  mod_actual = __import__ (info_nueva[posicion][0])
  mod_actual.__dict__[info_nueva[posicion][1]]()
  postCarga (_('Untitled'))

def nuevaEntradaProceso (posicion):
  """A�ade una entrada de proceso vac�a en la posici�n dada como par�metro"""
  if posicion < 0:
    posicion = 0
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  # A�adimos la nueva entrada
  proceso[0].insert (posicion, [255, 255])
  proceso[1].insert (posicion, [])
  # Actualizamos los puntos de ruptura que quedan detr�s de la nueva entrada
  if numProceso in puntos_ruptura:
    # Saltamos puntos de ruptura de entradas anteriores
    e = 0
    while e < len (puntos_ruptura[numProceso]):
      if puntos_ruptura[numProceso][e][0] >= posicion:
        break
      e += 1
    # Actualizamos los puntos de ruptura de entradas posteriores a la nueva
    for pe in range (e, len (puntos_ruptura[numProceso])):
      puntos_ruptura[numProceso][pe] = (puntos_ruptura[numProceso][pe][0] + 1, puntos_ruptura[numProceso][pe][1], puntos_ruptura[numProceso][pe][2])
  # Redibujamos el campo de texto para reflejar los cambios
  cambiaProceso (numProceso, posicion)

def nuevaEntradaVocabulario (entrada, numFilaAntes = None):
  """A�ade al vocabulario la entrada dada, en la posici�n que le corresponda"""
  # TODO: comprobar si ya existe otra palabra as� y pedir confirmar en ese caso (pero permitirlo)
  pos = 0
  if mod_actual.NOMBRE_SISTEMA in ('QUILL', 'PAWS'):  # En Quill y PAWS las palabras van ordenadas por c�digo y luego alfab�ticamente
    while pos < len (mod_actual.vocabulario) and (
        entrada[1] > mod_actual.vocabulario[pos][1] or
        (entrada[1] == mod_actual.vocabulario[pos][1] and mod_actual.cadena_es_mayor (entrada[0], mod_actual.vocabulario[pos][0]))):
      pos += 1
  else:  # En SWAN y DAAD las palabras van ordenadas alfab�ticamente
    while pos < len (mod_actual.vocabulario) and mod_actual.cadena_es_mayor (entrada[0], mod_actual.vocabulario[pos][0]):
      pos += 1
  modeloVocab = dlg_vocabulario.model().sourceModel()
  if numFilaAntes:
    modeloVocab.beginRemoveRows (QModelIndex(), numFilaAntes, numFilaAntes)
    del mod_actual.vocabulario[numFilaAntes]
    modeloVocab.endRemoveRows()
  modeloVocab.beginInsertRows (QModelIndex(), pos, pos)
  mod_actual.vocabulario.insert (pos, entrada)
  modeloVocab.endInsertRows()
  dlg_vocabulario.model().invalidate()  # Que reordene la tabla como corresponda

def nuevaFilaVocabulario (indice, sinonimo = False):
  """Permite a�adir una entrada de vocabulario, opcionalmente sin�nimo de otra"""
  tiempo = time.time()
  if tiempo <= dlg_vocabulario.activacionAnterior + 0.2:
    return  # Descartamos el evento por ocurrir tras un doble click anterior
  if sinonimo and indice == None:
    seleccion = dlg_vocabulario.selectionModel().selection()
    filasSeleccionadas = set()
    for indiceCelda in seleccion.indexes():
      filasSeleccionadas.add (indiceCelda.row())
    if len (filasSeleccionadas) != 1:  # Ninguna fila seleccionada o m�s de una
      return
    indice = dlg_vocabulario.model().mapToSource (seleccion.indexes()[0])  # Obtenemos un �ndice a la fila seleccionada
  nuevaPal = []  # Entrada de vocabulario a a�adir
  # Obtenemos el texto de la palabra
  dialogo = ModalEntrada (dlg_vocabulario, _('Text of the word:'), '')
  dialogo.setWindowTitle (_('Add'))
  textoPalabra = ''
  while not textoPalabra:
    if dialogo.exec_() != QDialog.Accepted:
      return
    textoPalabra = str (dialogo.textValue()).strip()
  nuevaPal.append (textoPalabra[:mod_actual.LONGITUD_PAL].lower())
  if sinonimo:  # Cuando est�bamos a�adiendo un sin�nimo, ya no hace falta pedir nada m�s
    nuevaPal.extend (mod_actual.vocabulario[indice.row()][1:])
    nuevaEntradaVocabulario (tuple (nuevaPal))
    return
  # Obtenemos el c�digo de la palabra
  dialogo = ModalEntrada (dlg_vocabulario, _('Code of the word:'), '')
  dialogo.setInputMode   (QInputDialog.IntInput)
  dialogo.setIntRange    (0, 255)
  dialogo.setWindowTitle (_('Add'))
  if dialogo.exec_() != QDialog.Accepted:
    return
  nuevaPal.append (dialogo.intValue())
  # Obtenemos el tipo de la palabra
  if len (mod_actual.TIPOS_PAL) == 1:
    nuevaPal.append (0)  # Quill no distingue palabras por tipos y es extremadamente inusual querer a�adir una de tipo reservado
  else:
    tiposPalabra = {255: _('Reserved')}
    for i in range (len (mod_actual.TIPOS_PAL)):
      tiposPalabra[i] = mod_actual.TIPOS_PAL[i]
    dialogo = ModalEntrada (dlg_vocabulario, _('Type of the word:'), '')
    dialogo.setComboBoxEditable (True)
    dialogo.setComboBoxItems    (sorted (tiposPalabra.values()))
    dialogo.setWindowTitle      (_('Add'))
    if dialogo.exec_() != QDialog.Accepted or dialogo.textValue() not in tiposPalabra.values():
      return
    nuevaPal.append (list (tiposPalabra.keys())[list (tiposPalabra.values()).index (dialogo.textValue())])
  nuevaEntradaVocabulario (tuple (nuevaPal))

def copiaTexto (dialogoTextos, listaTextos):
  """Copia al portapapeles la selecci�n de un di�logo de textos"""
  indices = dialogoTextos.selectionModel().selectedIndexes()
  textoCopiado = ''
  for indice in indices:
    textoCopiado += ('\n' if textoCopiado else '') + mod_actual.lee_secs_ctrl (listaTextos[dialogoTextos.model().indicesTextos[indice.row()]])
  aplicacion.clipboard().setText (textoCopiado)

def pegaTexto (dialogoTextos, listaTextos):
  """Pega desde el portapapeles sobre un di�logo de textos"""
  portapapeles = aplicacion.clipboard()
  if 'text/plain' not in portapapeles.mimeData().formats():
    return
  destinos = dialogoTextos.selectionModel().selectedIndexes()
  modelo   = dialogoTextos.model()
  texto    = str (portapapeles.text())
  if texto[-1:] == '\n':  # Asumimos que es residuo del programa de hoja de c�lculo, LibreOffice/OpenOffice lo dejan, Gnumeric no
    texto = texto[:-1]
  textos = texto.split ('\n')
  for t in range (len (textos)):  # Interpretamos las secuencias de control en los textos
    texto = textos[t].replace ('\\n', '\n')
    if mod_actual.NOMBRE_SISTEMA != 'DAAD':  # En DAAD no hay tabulador, all� se usa \t para el c�digo que pasa al juego bajo
      texto = texto.replace ('\\t', '\t')
    textos[t] = mod_actual.escribe_secs_ctrl (texto)
  if len (destinos) > 1:  # M�ltiples filas seleccionadas
    for d in range (len (destinos)):
      numFila = destinos[d].row()
      modelo.beginRemoveRows (QModelIndex(), numFila, numFila)
      modelo.endRemoveRows()
      modelo.beginInsertRows (QModelIndex(), numFila, numFila)
      listaTextos[numFila] = textos[d % len (textos)]
      modelo.endInsertRows()
  else:  # Una sola fila seleccionada
    numFila = destinos[0].row()
    modelo.beginRemoveRows (QModelIndex(), numFila, min (len (listaTextos) - 1, numFila + len (textos) - 1))
    modelo.endRemoveRows()
    modelo.beginInsertRows (QModelIndex(), numFila, numFila + len (textos) - 1)
    for t in range (len (textos)):
      nuevaFila = numFila + t  # �ndice de la nueva fila
      if type (listaTextos) == dict:  # Se trata de GAC
        if nuevaFila in listaTextos:
          posAnterior = listaTextos.index (nuevaFila)
        else:
          modelo.indicesTextos.insert (posAnterior + 1, nuevaFila)
          posAnterior += 1
          if listaTextos == mod_actual.desc_locs:  # Se ha creado una nueva localidad
            mod_actual.conexiones[nuevaFila] = []
          elif listaTextos == mod_actual.desc_objs:  # Se ha creado un nuevo objeto
            mod_actual.atributos[nuevaFila]      = 0
            mod_actual.locs_iniciales[nuevaFila] = IDS_LOCS['GAC']['NOTCREATED']
            mod_actual.nombres_objs[nuevaFila]   = (nuevaFila, 255)
        listaTextos[nuevaFila] = textos[t]
      else:  # Son sistemas de la familia de Quill
        if nuevaFila >= len (listaTextos):
          modelo.indicesTextos.append (nuevaFila)
          listaTextos.append (textos[t])
          if listaTextos == mod_actual.desc_locs:  # Se ha creado una nueva localidad
            mod_actual.conexiones.append ([])
          elif listaTextos == mod_actual.desc_objs:  # Se ha creado un nuevo objeto
            mod_actual.locs_iniciales.append (IDS_LOCS[None]['NOTCREATED'])
            mod_actual.nombres_objs.append ((255, 255))
            mod_actual.num_objetos[0] += 1
            if 'atributos' in mod_actual.__dict__:
              mod_actual.atributos.append (0)
              if 'atributos_extra' in mod_actual.__dict__:
                mod_actual.atributos_extra.append (0)
        else:
          listaTextos[nuevaFila] = textos[t]
    modelo.endInsertRows()

def quitaEntradaProceso (posicion):
  """Quita la entrada de proceso de la posici�n dada como par�metro"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  # Quitamos la entrada
  del proceso[0][posicion]
  del proceso[1][posicion]
  # Quitamos los puntos de ruptura de la entrada y actualizamos los de detr�s
  if numProceso in puntos_ruptura:
    # Saltamos puntos de ruptura de entradas anteriores
    e = 0
    while e < len (puntos_ruptura[numProceso]):
      if puntos_ruptura[numProceso][e][0] >= posicion:
        break
      e += 1
    # Quitamos puntos de ruptura de la entrada quitada
    while e < len (puntos_ruptura[numProceso]) and puntos_ruptura[numProceso][e][0] == posicion:
      puntos_ruptura[numProceso].pop (e)
    # Actualizamos los puntos de ruptura de entradas posteriores a la nueva
    for pe in range (e, len (puntos_ruptura[numProceso])):
      puntos_ruptura[numProceso][pe] = (puntos_ruptura[numProceso][pe][0] - 1, puntos_ruptura[numProceso][pe][1], puntos_ruptura[numProceso][pe][2])
  # Redibujamos el campo de texto para reflejar los cambios
  cambiaProceso (numProceso, max (0, posicion - 1))

def quitaEntradasProceso ():
  """Quita la entradas del proceso seleccionado"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  # Quitamos las entradas
  del proceso[0][:]
  del proceso[1][:]
  # Quitamos los puntos de ruptura del proceso
  if numProceso in puntos_ruptura:
    del puntos_ruptura[numProceso][:]
  # Redibujamos el campo de texto para reflejar los cambios
  cambiaProceso (numProceso)

def postCarga (nombre):
  """Realiza las acciones convenientes tras la carga satisfactoria de una BD

  Recibe como par�metro el nombre de la base de datos"""
  global tipo_adjetivo, tipo_nombre, tipo_verbo
  # Apa�o para que funcionen tal y como est�n las librer�as con lista unificada de condactos
  # Lo hacemos aqu�, porque la lista de condactos se puede extender tras cargar una BD
  if comprueba_tipo (mod_actual, 'condactos', dict) and (not comprueba_tipo (mod_actual, 'acciones', dict) or not mod_actual.acciones):
    for codigo in mod_actual.condactos:
      if mod_actual.condactos[codigo][2]:  # Es acci�n
        mod_actual.acciones[codigo] = mod_actual.condactos[codigo]
      else:  # Es condici�n
        mod_actual.condiciones[codigo] = mod_actual.condactos[codigo]
  # Cogemos la primera palabra de cada tipo y n�mero como sin�nimo preferido
  if len (mod_actual.TIPOS_PAL) > 3:
    tipo_adjetivo    = mod_actual.TIPOS_PAL.index (_('Adjective'))
    tipo_nombre      = mod_actual.TIPOS_PAL.index (_('Noun'))
    tipo_preposicion = mod_actual.TIPOS_PAL.index (_('Preposition'))
    tipo_verbo       = mod_actual.TIPOS_PAL.index (_('Verb'))
  elif len (mod_actual.TIPOS_PAL) > 1:  # Es GAC
    tipo_nombre      = mod_actual.TIPOS_PAL.index (_('Noun'))
    tipo_preposicion = mod_actual.TIPOS_PAL.index (_('Adverb'))
    tipo_verbo       = mod_actual.TIPOS_PAL.index (_('Verb'))
  else:  # Es Quill
    tipo_nombre = tipo_preposicion = tipo_verbo = 0
  # Elegimos los sin�nimos preferidos de cada palabra y recopilamos las palabras de direcci�n
  del pals_mov[:]
  pal_sinonimo.clear()
  for palabra, codigo, tipo in mod_actual.vocabulario:
    idYtipos = [(codigo, tipo)]
    if (tipo == tipo_nombre      and codigo < mod_actual.NOMB_COMO_VERB[0] or  # Es nombre convertible en verbo
        tipo == tipo_preposicion and codigo < mod_actual.PREP_COMO_VERB):      # Es preposici�n convertible en verbo
      idYtipos.append ((codigo, tipo_verbo))
    for idYtipo in idYtipos:
      # Preferiremos terminaci�n en R para verbos (heur�stica para que sean en forma infinitiva)
      if idYtipo not in pal_sinonimo or \
          (tipo == tipo_verbo and palabra[-1] == 'r' and pal_sinonimo[idYtipo][-1] != 'r'):
        pal_sinonimo[idYtipo] = daTextoImprimible (palabra)
    if codigo < (13 if mod_actual.NOMBRE_SISTEMA == 'QUILL' else 14) and codigo not in pals_mov and tipo in (tipo_nombre, tipo_verbo):
      pals_mov.append (codigo)
  # Recopilamos las palabras usadas como salidas en la tabla de conexiones
  del pals_salida[:]
  for conexionesLocalidad in mod_actual.conexiones.values() if type (mod_actual.conexiones) == dict else mod_actual.conexiones:
    for codigo, destino in conexionesLocalidad:
      if codigo not in pals_mov:
        pals_mov.append (codigo)
      if codigo not in pals_salida:
        pals_salida.append (codigo)
  if not pals_salida:  # No hay ninguna conexi�n, pondremos todas las de direcci�n que haya
    pals_salida.extend (pals_mov)
  pals_mov.sort()
  pals_salida.sort()
  # Preparamos las funciones de exportaci�n
  for entrada in mod_actual.funcs_exportar:
    if comprueba_tipo (mod_actual, entrada[0], types.FunctionType):
      info_exportar.append ((entrada[0], entrada[1], entrada[2]))
  # Habilitamos las acciones que requieran tener una base de datos cargada
  for accion in (accContadores, accDescLocs, accDescObjs, accDireccs, accMostrarLoc, accMostrarObj, accMostrarRec, accMostrarSal, accMostrarSys, accMostrarUsr, accMsgSys, accMsgUsr, accTblProcs, accTblVocab):
    accion.setEnabled (True)
  accExportar.setEnabled  (len (info_exportar) > 0)
  accPasoAPaso.setEnabled (nombre_fich_bd != None)
  # Cambiamos la acci�n importar de la barra de botones por la de exportar
  barra_botones.insertAction (accImportar, accExportar)
  barra_botones.removeAction (accImportar)
  selector.setWindowTitle ('NAPS IDE - ' + nombre + ' (' + mod_actual.NOMBRE_SISTEMA + ')')
  selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal


if sys.version_info[0] < 3:
  import codecs
  reload (sys)  # Necesario para poder ejecutar sys.setdefaultencoding
  sys.stderr = codecs.getwriter (locale.getpreferredencoding()) (sys.stderr)  # Locale del sistema para la salida de error
  sys.stdout = codecs.getwriter (locale.getpreferredencoding()) (sys.stdout)  # Locale del sistema para la salida est�ndar
  sys.setdefaultencoding ('iso-8859-15')  # Nuestras cadenas est�n en esta codificaci�n, no en ASCII
elif sys.version_info[1] < 4:  # Python 3.x < 3.4
  from imp import reload
else:  # Python > 3.3
  from importlib import reload

aplicacion = QApplication (sys.argv)

argsParser = argparse.ArgumentParser (sys.argv[0], description = _('Integrated Development Environment for Quill/PAWS/SWAN/DAAD in Python'))
argsParser.add_argument ('-ne', '--no-entry-end', action = 'store_true', help = _('omit condacts in process entries behind condacts that unconditionally change execution flow'))
argsParser.add_argument ('-r', '--run', action = 'store_true', help = _("directly run 'database' step by step"))
argsParser.add_argument ('--theme', choices = ('dark', 'light'), help = _('choose the color theme to use'))
argsParser.add_argument ('bbdd',     metavar = _('database'),              nargs = '?', help = _('Quill/PAWS/SWAN/DAAD database, snapshot, or source code to run'))
argsParser.add_argument ('graficos', metavar = _('db_or_graphics_folder'), nargs = '?', help = _('graphic database or folder to take images from (with name pic###.png)'))
args = argsParser.parse_args()

if (not args.theme and not modo_claro) or args.theme == 'dark':
  aplicacion.setStyleSheet ('QHeaderView::section, QListView, QMenuBar::item, QPushButton, QSpinBox, QTabBar::tab, QToolTip, QWidget {background: #000; color: #ddd} QComboBox {border: 1px solid gray; color: #ddd; padding: 2px} QHeaderView::section {border: 1px solid #444; color: #ddd; padding: 0.2em 0.5em} QMenu {border: 1px solid #222} QMenu::item:selected, QPushButton:hover {background: #222; color: #fff} QMenu::item {margin: 5px; padding: 1px 25px} QMenu::item:disabled {color: #777} QMenu::separator {background: #555; height: 2px; margin: 2px} QMdiSubWindow {background: #ccc; color: #000} QPushButton {border: 2px outset #444; border-radius: 5px; min-height: 1.5em; padding: 0 0.5em} QPushButton:disabled {background: #111; border-color: #222; color: #bbb} QPushButton:focus {background: #222; outline: 0} QPushButton:pressed {background: #444} QSpinBox {border: 1px solid #444; border-radius: 3px; padding: 5px 3px} QToolBar {border: 1px solid #333} QTabBar {outline: 0} QTabBar::tab {border: 1px solid #c4c1bd; border-top-left-radius: 5px; border-top-right-radius: 5px; min-height: 1.5em; min-width: 3em} QTabBar::tab:selected {background: #222; border-bottom: 0; font-weight: bold} QTabBar::tab:focus {background: #333} QTableCornerButton::section {background: #444} QToolTip {border: 2px solid #555; border-radius: 3px; padding: 2px} QWidget#procesos {background: #222}')
  color_base        = QColor (0, 0, 0)  # Color de fondo negro
  estilo_banderas   = 'QPushButton {border: 0; border-radius: 0; margin-right: 2px; padding: 0; text-align: left; %s}'
  estilo_fila_impar = 'background: #333; '
  modo_claro        = False
else:
  color_base        = QColor (10, 10, 10)   # Color de fondo gris oscuro
  estilo_banderas   = 'QPushButton {border: 0; margin-right: 2px; text-align: left; %s}'
  estilo_fila_impar = 'background: #ddd; '
  modo_claro        = True

creaSelector()
selector.showMaximized()
cargaInfoModulos()

# Ajustamos el tama�o inicial de la fuente para el di�logo de procesos seg�n la resoluci�n de pantalla
pantalla   = QDesktopWidget().screenNumber (selector)
geometria  = QDesktopWidget().screenGeometry (pantalla)
tam_fuente = int (12 * geometria.width() / 1024)  # El tama�o 12 est� bien para resoluci�n de ancho 1024

if args.bbdd:
  if args.graficos and not os.path.exists (args.graficos):
    muestraFallo (_('Inexistent path'),
                  _("There's no file and no folder with the path given from the command line for graphics:\n\n")
                  + (args.graficos.decode ('utf8') if sys.version_info[0] < 3 else args.graficos))
    args.graficos = None
  if args.graficos:
    todoBien = importaBD (args.bbdd, nombreFicheroGfx = args.graficos)
  else:
    todoBien = importaBD (args.bbdd)
  if todoBien and args.run:
    ejecutaPorPasos()

sys.exit (aplicacion.exec_())
