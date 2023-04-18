#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Entorno de desarrollo integrado (IDE), hecho con PyQt4
# Copyright (C) 2010, 2018-2023 José Manuel Ferrer Ortiz
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
from prn_func   import prn

import argparse    # Para procesar argumentos de línea de comandos
import locale      # Para codificar bien la salida estándar
import os          # Para curdir, listdir y path
import subprocess  # Para ejecutar el intérprete
import sys
import types       # Para poder comprobar si algo es una función

try:
  from PyQt4.QtCore import *
  from PyQt4.QtGui  import *
  vers_pyqt = 4
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtGui     import *
  from PyQt5.QtWidgets import *
  vers_pyqt = 5


# TODO: Hacerlo internacionalizable:
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qcoreapplication.html#translate


dlg_abrir       = None  # Diálogo de abrir fichero
dlg_acerca_de   = None  # Diálogo "Acerca de"
dlg_banderas    = None  # Diálogo para consultar y modificar las banderas
dlg_contadores  = None  # Diálogo de contadores
dlg_fallo       = None  # Diálogo para mostrar fallos leves
dlg_guardar     = None  # Diálogo de guardar fichero
dlg_desc_locs   = None  # Diálogo para consultar y modificar las descripciones de localidades
dlg_desc_objs   = None  # Diálogo para consultar y modificar las descripciones de objetos
dlg_msg_sys     = None  # Diálogo para consultar y modificar los mensajes de sistema
dlg_msg_usr     = None  # Diálogo para consultar y modificar los mensajes de usuario
dlg_procesos    = None  # Diálogo para consultar y modificar las tablas de proceso
dlg_vocabulario = None  # Diálogo para consultar y modificar el vocabulario
mdi_banderas    = None  # Subventana MDI para dlg_banderas
mdi_desc_locs   = None  # Subventana MDI para dlg_desc_locs
mdi_desc_objs   = None  # Subventana MDI para dlg_desc_objs
mdi_msg_sys     = None  # Subventana MDI para dlg_msg_sys
mdi_msg_usr     = None  # Subventana MDI para dlg_msg_usr
mdi_procesos    = None  # Subventana MDI para dlg_procesos
mdi_vocabulario = None  # Subventana MDI para dlg_vocabulario
mdi_juego       = None  # Subventana MDI para la pantalla de juego del intérprete

campo_txt = None  # El campo de texto    del diálogo de procesos
pestanyas = None  # La barra de pestañas del diálogo de procesos

mod_actual      = None    # Módulo de librería activo
pal_sinonimo    = dict()  # Sinónimos preferidos para cada par código y tipo válido
pals_no_existen = []      # Códigos de palabra que no existen encontrados en tablas de proceso

color_base      = QColor (10, 10, 10)   # Color de fondo gris oscuro
color_pila      = QColor (60, 35, 110)  # Color de fondo azul brillante
color_tope_pila = QColor (35, 40, 110)  # Color de fondo morado oscuro
inicio_debug    = False  # Para hacer la inicialización de subventanas MDI al lanzar depuración
pila_procs      = []     # Pila con estado de los procesos en ejecución
proc_interprete = None   # Proceso del intérprete

# Identificadores (para hacer el código más legible) predefinidos
IDS_LOCS = {
  252: 'NOTCREATED',
       '_': 252,
  253: 'WORN',
       'WORN': 253,
  254: 'CARRIED',
       'CARRIED': 254,
  255: 'HERE',
       'HERE': 255}

# Conversión de teclas para manejo del intérprete
conversion_teclas = {Qt.Key_Escape: 27, Qt.Key_Down: 80, Qt.Key_End: 79, Qt.Key_Home: 71, Qt.Key_Left: 75, Qt.Key_Right: 77, Qt.Key_Up: 72}

# Estilos CSS para el diálogo de banderas
estilo_fila_impar = 'QPushButton {border: 0; margin-right: 2px; padding: 0; background: #ddd}'
estilo_fila_par   = 'QPushButton {border: 0; margin-right: 2px; padding: 0}'


# Funciones de exportación e importación, con sus módulos, extensiones y descripciones
info_exportar = []
info_importar = []
# Funciones de nueva base de datos, con sus módulos
info_nueva = []

# Pares nombre y tipos posibles que deben tener los módulos de librería
nombres_necesarios = (('acciones',          dict),
                      ('cadena_es_mayor',   types.FunctionType),
                      ('condiciones',       dict),
                      ('func_nueva',        str),
                      ('funcs_exportar',    tuple),
                      ('funcs_importar',    tuple),
                      ('escribe_secs_ctrl', types.FunctionType),
                      ('lee_secs_ctrl',     types.FunctionType),
                      ('INDIRECCION',       bool),
                      ('msgs_sys',          list),
                      ('msgs_usr',          list),
                      ('NOMBRE_SISTEMA',    str),
                      ('tablas_proceso',    list),
                      ('TIPOS_PAL',         tuple),
                      ('vocabulario',       list))


class CampoTexto (QTextEdit):
  """Campo de texto para las tablas de proceso"""
  def __init__ (self, parent):
    QTextEdit.__init__ (self, parent)
    self.actualizandoProceso = QTimer()
    self.actualizandoProceso.setSingleShot (True)
    self.actualizandoProceso.timeout.connect (actualizaProceso)

  def _daColsValidas (self, textoLinea):
    """Devuelve las posiciones válidas para el cursor en la línea de tabla de proceso con texto dado"""
    colsValidas  = []
    espacioAntes = False
    for c in range (len (textoLinea)):
      if textoLinea[c] == ' ':
        espacioAntes = True
        continue
      if espacioAntes:
        if textoLinea[c] == '"':
          colsValidas.append (c + 1)
          break  # Dejamos de buscar nada más tras encontrar comillas
        colsValidas.append (c)
        espacioAntes = False
    colsValidas.append (len (textoLinea))
    return colsValidas

  def _daColValida (self, numColumna, textoLinea, colsValidas = None):
    """Devuelve la posición válida más cercana para el cursor en la columna dada de la línea de tabla de proceso con texto dado"""
    if colsValidas == None:
      colsValidas = self._daColsValidas (textoLinea)
    if numColumna in colsValidas:
      return numColumna  # Era válida
    # Buscamos la columna válida más cercana
    for c in range (len (colsValidas)):
      if colsValidas[c] < numColumna:
        continue
      if c:  # No es la primera
        # Nos quedamos con la más cercana de entre la de la posición actual y la anterior
        if abs (numColumna - colsValidas[c]) > abs (numColumna - colsValidas[c - 1]):
          return colsValidas[c - 1]
      return colsValidas[c]
    return colsValidas[-1]  # La última es la más cercana

  def _daNumEntradaYLinea (self, bloqueLinea):
    """Devuelve el número de entrada de proceso y el de la línea en la entrada del bloque QTextBlock dado"""
    # Buscamos la línea de cabecera de la entrada, para obtener de allí el número de entrada del proceso
    cabecera = bloqueLinea
    posicion = 0  # El número de línea en la entrada donde está el cursor
    if cabecera.userState() == -1:
      while cabecera.previous().isValid():
        cabecera  = cabecera.previous()
        posicion += 1
        if cabecera.userState() > -1:
          break
    numEntrada = cabecera.userState()
    return numEntrada, posicion

  def centraLineaCursor (self):
    """Centra verticalmente la línea del cursor actual"""
    lineasVisibles = self.size().height() / float (self.cursorRect().height())
    cursor   = self.textCursor()
    posicion = cursor.position()
    self.moveCursor (QTextCursor.End)  # Vamos al final, para que al ir a la línea que toca, esa quede arriba
    cursor.movePosition (QTextCursor.Up, n = int (lineasVisibles // 2) - 1)
    self.setTextCursor  (cursor)
    cursor.setPosition  (posicion)
    cursor.movePosition (QTextCursor.Right, n = 2)
    self.setTextCursor  (cursor)

  def contextMenuEvent (self, evento):
    linea      = self.cursorForPosition (evento.pos()).block()
    numEntrada = self._daNumEntradaYLinea (linea)[0]
    # prn ('Nº línea:', linea.blockNumber())
    # prn ('Nº entrada guardado en la línea:', linea.userState())
    # prn ('Nº entrada guardado en cabecera:', cabecera.userState())
    # prn ('Texto de la línea:', linea.text())
    contextual   = self.createStandardContextMenu()
    menuEliminar = QMenu ('Eliminar', contextual)
    accionAntes    = QAction ('Añadir entrada &antes',   contextual)
    accionDespues  = QAction ('Añadir entrada &después', contextual)
    accionElimEnt  = QAction ('Esta entrada',       selector)  # Necesario poner como padre selector...
    accionElimTodo = QAction ('Todas las entradas', selector)  # ... para que funcionen los status tips
    if numEntrada == -1:
      menuEliminar.setEnabled (False)
    accionElimTodo.setStatusTip ('Elimina todas las entradas del proceso')
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
    contextual.addAction ('&Ir a la entrada', irAEntradaProceso, 'Ctrl+G')
    contextual.exec_ (evento.globalPos())

  def irAEntrada (self, numEntrada):
    """Mueve el cursor a la entrada dada del proceso actual, y devuelve el bloque de su línea de cabecera"""
    cursor = self.textCursor()
    cursor.movePosition (QTextCursor.Start)
    linea = cursor.block()
    if not linea.text() or linea.userState() != 0:
      return  # Algo inesperado: la primera línea del proceso no es la primera cabecera
    entradaActual = 0
    while entradaActual < numEntrada and linea.next().isValid():
      linea = linea.next()
      if linea.userState() > -1:
        entradaActual = linea.userState()
    cursor.setPosition (linea.position())
    self.setTextCursor (cursor)
    return linea

  def irAEntradaYCondacto (self, numEntrada, numCondacto):
    """Mueve el cursor a la entrada y condacto en ésta dados del proceso actual"""
    linea = self.irAEntrada (numEntrada)
    if numCondacto > -1:  # No se estaba comprobando encaje con la cabecera de la entrada
      condactoActual = -2
      while condactoActual < numCondacto and linea.next().isValid():
        linea = linea.next()
        condactoActual += 1
        if linea.userState() > -1:
          break  # No debería ocurrir: hemos encontrado la cabecera de la siguiente entrada
      cursor = self.textCursor()
      cursor.setPosition (linea.position())
      self.setTextCursor (cursor)

  def keyPressEvent (self, evento):
    if evento.key() in (Qt.Key_Down, Qt.Key_End, Qt.Key_Home, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up):
      cursor = self.textCursor()
      if evento.key() in (Qt.Key_Down, Qt.Key_Up):
        if evento.key() == Qt.Key_Up:
          cursor.movePosition (QTextCursor.StartOfBlock)  # Hace que funcione en líneas con ajuste de línea
          cursor.movePosition (QTextCursor.Up)
        else:
          cursor.movePosition (QTextCursor.EndOfBlock)  # Hace que funcione en líneas con ajuste de línea
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
      if posicion > 1 and posicion < len (entrada) + 2 and columna == len (linea.text()):  # Sólo si está al final de una línea de condacto
        del entrada[posicion - 2]
        cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
        self.setTextCursor (cursor)
        self.cut()
    elif evento.key() == Qt.Key_Insert:
      if self.overwriteMode():
        self.setCursorWidth   (1)
        self.setOverwriteMode (False)
      else:
        self.setCursorWidth   (self.font().pointSize() * 0.8)
        self.setOverwriteMode (True)
    elif evento.modifiers() & Qt.ControlModifier:  # Teclas de acción
      if evento.key() in (Qt.Key_Minus, Qt.Key_Plus):
        if evento.key() == Qt.Key_Minus:
          self.zoomOut (2)
        else:
          self.zoomIn (2)
        if accMostrarRec.isChecked():  # Recortar al ancho de línea disponible
          self.actualizandoProceso.start (100)
      elif evento.key() == Qt.Key_G:
        irAEntradaProceso()
      else:
        super (CampoTexto, self).keyPressEvent (evento)
    elif proc_interprete:
      return  # No se puede modificar nada cuando la BD está en ejecución
    # Teclas que pueden causar modificación de la tabla de procesos
    if str (evento.text()).isalpha():  # Letras
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      colsValidas = self._daColsValidas (linea.text())
      if columna not in (colsValidas[0], colsValidas[-1]):
        return  # Intentando escribir texto donde no es posible
      if linea.text() and linea.userState() == -1:  # Una línea de entrada que no es la cabecera
        numEntrada, posicion = self._daNumEntradaYLinea (linea)
        try:
          self.condactos
        except:
          self.condactos       = {}  # Información completa de los condactos indexada por nombre
          self.condactosPorCod = {}  # Nombre de condactos indexado por código
          for listaCondactos in (mod_actual.acciones, mod_actual.condiciones):
            for codigo, condacto in listaCondactos.items():
              self.condactos[condacto[0]]  = condacto + (codigo,)
              self.condactosPorCod[codigo] = condacto[0]
        numProceso = pestanyas.currentIndex()
        proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
        entrada    = proceso[1][numEntrada]  # La entrada seleccionada
        if self.overwriteMode() and posicion > 1 and posicion < len (entrada) + 2:
          dialogo = ModalEntrada (self, 'Elige un condacto:', evento.text(), self.condactosPorCod[entrada[posicion - 2][0]])
        else:
          dialogo = ModalEntrada (self, 'Elige un condacto:', evento.text())
        dialogo.setComboBoxEditable (True)
        dialogo.setComboBoxItems (sorted (self.condactos.keys()))
        if dialogo.exec_() == QDialog.Accepted:
          nomCondacto = str (dialogo.textValue()).upper()
          if nomCondacto in self.condactos:
            condacto   = self.condactos[nomCondacto]
            lineaNueva = [condacto[4], [0] * len (condacto[1])]  # Código y parámetros de la nueva línea
            if posicion > 1:  # Si no añade al inicio de la entrada
              if self.overwriteMode():
                cursor.movePosition (QTextCursor.EndOfBlock)
                cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
                parametros    = entrada[posicion - 2][1]  # Conservaremos parámetros anteriores
                lineaNueva[1] = parametros[: len (condacto[1])] + ([0] * (max (0, len (condacto[1]) - len (parametros))))
              elif columna < len (linea.text()) or posicion == len (entrada) + 2:  # No es fin de línea o es final de entrada
                cursor.movePosition (QTextCursor.Up)
                cursor.movePosition (QTextCursor.EndOfBlock)
              self.setTextCursor (cursor)
            imprimeCondacto (*lineaNueva)
            cursor = self.textCursor()
            if posicion == 1:  # Añadir al inicio de la entrada
              entrada.insert (0, lineaNueva)
              cursor.movePosition (QTextCursor.Down)
              cursor.movePosition (QTextCursor.StartOfBlock)
              cursor.movePosition (QTextCursor.WordRight)
            elif posicion < len (entrada) + 2:
              if self.overwriteMode():  # Modificar un condacto ya existente en la entrada, conservando parámetros
                entrada[posicion - 2] = lineaNueva
              elif columna < len (linea.text()):  # No es fin de línea, añade antes
                entrada.insert (posicion - 2, lineaNueva)
              else:  # Es fin de línea, añade después
                entrada.insert (posicion - 1, lineaNueva)
            else:  # Añadir al final de la entrada
              entrada.append (lineaNueva)
              if not condacto[1]:  # El nuevo condacto no tiene parámetros
                cursor.movePosition (QTextCursor.Down)
                cursor.movePosition (QTextCursor.EndOfLine)
            if condacto[1]:  # Si el nuevo condacto tiene parámetros, mueve cursor al primero
              cursor.movePosition (QTextCursor.StartOfBlock)
              cursor.movePosition (QTextCursor.WordRight, n = 2)
            self.setTextCursor (cursor)
      elif linea.userState() > -1:  # Estamos en la cabecera
        prn ('En cabecera')
    elif evento.key() in (Qt.Key_At, Qt.Key_BracketLeft) and mod_actual.INDIRECCION:
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      colsValidas = self._daColsValidas (linea.text())
      if not linea.text().trimmed() or linea.userState() > -1:
        return  # Intentando cambiar indirección en línea sin condacto
      numEntrada, posicion = self._daNumEntradaYLinea (linea)
      numProceso = pestanyas.currentIndex()
      proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
      entrada    = proceso[1][numEntrada]  # La entrada seleccionada
      condacto   = entrada[posicion - 2]
      lineaNueva = (condacto[0] ^ 128, condacto[1])  # Alternamos indirección en el condacto
      entrada[posicion - 2] = lineaNueva  # Código y parámetros de la nueva línea
      cursor.movePosition (QTextCursor.EndOfBlock)
      cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
      cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
      self.setTextCursor (cursor)
      imprimeCondacto (*lineaNueva)
      if columna in colsValidas:  # Recuperamos posición anterior correcta
        indice = colsValidas.index (columna)
        linea  = cursor.block()
        colsValidas = self._daColsValidas (linea.text())
        columna  = cursor.positionInBlock()
        colNueva = colsValidas[indice]
        cursor.setPosition (cursor.position() + (colNueva - columna))
        self.setTextCursor (cursor)
    elif evento.key() >= Qt.Key_0 and evento.key() <= Qt.Key_9:  # Números
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      if str (cursor.selectedText()).isdigit():
        columna -= len (cursor.selectedText())  # Inicio del parámetro
      elif cursor.hasSelection():
        return  # Intentando escribir número donde no es posible
      colsValidas = self._daColsValidas (linea.text())
      columna     = self._daColValida (columna, linea.text(), colsValidas)
      if columna == colsValidas[0] or (columna == colsValidas[-1] and len (colsValidas) < 3) or linea.text()[columna - 1] == '"':
        return  # Intentando escribir número donde no es posible
      if columna == colsValidas[-1]:  # Está al final del último parámetro
        columna = colsValidas[-2]
      numParam  = colsValidas.index (columna)
      parametro = str (linea.text()[columna:])
      if ',' in parametro:
        parametro = parametro[: parametro.find (',')]
      dialogo = ModalEntrada (self, 'Valor del parámetro:', evento.text(), parametro)
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
        if numParam == 1 and len (condacto[1]) > 1:  # Hemos cambiado el primer parámetro y hay segundo parámetro
          cursor = self.textCursor()
          cursor.movePosition (QTextCursor.StartOfBlock)
          cursor.movePosition (QTextCursor.WordRight, n = 4)  # Vamos al segundo parámetro
          self.setTextCursor (cursor)

  def mousePressEvent (self, evento):
    if evento.button() & Qt.LeftButton or evento.button() & Qt.RightButton:
      cursor     = self.cursorForPosition (evento.pos())
      bloque     = cursor.block()
      columna    = cursor.positionInBlock()
      textoLinea = bloque.text()
      colNueva   = self._daColValida (columna, textoLinea)
      cursor.setPosition (cursor.position() + (colNueva - columna))
      self.setTextCursor (cursor)
      if evento.button() & Qt.LeftButton:
        if evento.modifiers() & Qt.ControlModifier:  # Puede ser Ctrl+click en un enlace
          enlace = self.anchorAt (evento.pos())
          if enlace and enlace[:8] == 'proceso:':
            self.quitaFormatoEnlace()  # Quitamos el formato anterior
            pestanyas.setCurrentIndex (int (enlace[8:]))
        else:
          return
    super (CampoTexto, self).mousePressEvent (evento)

  def quitaFormatoEnlace (self):
    """Quita el formato de enlace a la posición del cursor actual"""
    cursor  = self.textCursor()
    formato = cursor.charFormat()
    formato.setAnchor (False)
    formato.setFontUnderline (False)
    formato.setToolTip ('')
    campo_txt.setCurrentCharFormat (formato)

  def resizeEvent (self, evento):
    super (CampoTexto, self).resizeEvent (evento)
    if accMostrarRec.isChecked():  # Recortar al ancho de línea disponible
      try:
        self.anchoAntes
      except:
        self.anchoAntes     = evento.oldSize().width()
        self.cuentaDifAncho = {}    # Diccionario para contar cuántas veces se encuentra cada diferencia de anchura
        self.difAutoAjuste  = None  # Valor de diferencia en los autoajustes al redibujar el campo de texto
      # Ocurre un bucle de redimensiones por autoajustes al redibujar el campo de texto, en el cual la diferencia es siempre la misma, pero es dependiente del sistema (seguramente del estilo de la interfaz)
      # Detectaremos cuál es esa diferencia por los autoajustes, y en cuanto la sepamos ignoraremos cambios de anchura de ese valor
      diferencia = abs (evento.size().width() - self.anchoAntes)
      if not diferencia or diferencia == self.difAutoAjuste:  # No cambia o es el valor de la diferencia detectada
        return  # Evitamos bucle de redimensiones por autoajustes al redibujar el campo de texto
      if diferencia <= 25:
        if diferencia in self.cuentaDifAncho:
          if self.cuentaDifAncho[diferencia] >= 14:  # Debe ser éste el valor de diferencia de los autoajustes
            self.cuentaDifAncho.clear()
            self.difAutoAjuste = diferencia
            return
          self.cuentaDifAncho[diferencia] += 1
        else:
          self.cuentaDifAncho[diferencia] = 1
      self.actualizandoProceso.start (100)
      self.anchoAntes = evento.size().width()

  def wheelEvent (self, evento):
    if evento.modifiers() & Qt.ControlModifier:
      if (evento.delta() if vers_pyqt < 5 else evento.angleDelta().y()) < 0:
        self.zoomOut (2)
      else:
        self.zoomIn (2)
      if self.overwriteMode():
        self.setCursorWidth (self.font().pointSize() * 0.8)
      if accMostrarRec.isChecked():  # Recortar al ancho de línea disponible
        self.actualizandoProceso.start (100)
    else:
      super (CampoTexto, self).wheelEvent (evento)

class ManejoInterprete (QThread):
  """Maneja la comunicación con el intérprete ejecutando la base de datos"""
  cambiaBanderas = pyqtSignal (object)
  cambiaImagen   = pyqtSignal()
  cambiaPila     = pyqtSignal()

  def __init__ (self, procInterprete, padre):
    QThread.__init__ (self, parent = padre)
    self.procInterprete = procInterprete

  def run (self):
    """Lee del proceso del intérprete, obteniendo por dónde va la ejecución"""
    global proc_interprete
    if sys.version_info[0] < 3:
      inicioLista     = '['
      finLista        = ']'
      imagenCambiada  = 'img'
      banderasCambian = 'flg'
      esTeclaEntrada  = 'key'
      esTeclaPasos    = 'stp'
    else:
      inicioLista     = ord ('[')
      finLista        = ord (']')
      imagenCambiada  = b'img'
      banderasCambian = b'flg'
      esTeclaEntrada  = b'key'
      esTeclaPasos    = b'stp'
    pilaProcs = []
    while True:
      linea = self.procInterprete.stdout.readline()
      if not linea:
        break  # Ocurre cuando el proceso ha terminado
      tituloJuego = 'Ejecución ' + mod_actual.NOMBRE_SISTEMA  # Título para la ventana de juego
      if linea[0] == inicioLista and finLista in linea:  # Si es actualización del estado de la pila, avisamos de ella
        pilaProcs = eval (linea)
        pilas_pendientes.append (pilaProcs)
        self.cambiaPila.emit()
      elif linea[:3] == imagenCambiada:
        self.cambiaImagen.emit()
      elif linea[:3] == banderasCambian:
        cambiosBanderas = eval (linea[4:])
        self.cambiaBanderas.emit (cambiosBanderas)
      elif linea[:3] == esTeclaEntrada:
        acc1Paso.setEnabled     (False)
        acc10Pasos.setEnabled   (False)
        acc100Pasos.setEnabled  (False)
        acc1000Pasos.setEnabled (False)
        accBanderas.setEnabled  (False)
        tituloJuego += ' - Esperando tecla'
      elif linea[:3] == esTeclaPasos:
        acc1Paso.setEnabled     (True)
        acc10Pasos.setEnabled   (True)
        acc100Pasos.setEnabled  (True)
        acc1000Pasos.setEnabled (True)
        accBanderas.setEnabled  (True)
        tituloJuego += ' - Parada'
      if mdi_juego:  # Porque puede no estar lista todavía
        mdi_juego.widget().setWindowTitle (tituloJuego)
    # El proceso ha terminado
    acc1Paso.setEnabled     (False)
    acc10Pasos.setEnabled   (False)
    acc100Pasos.setEnabled  (False)
    acc1000Pasos.setEnabled (False)
    accBanderas.setEnabled  (False)
    accPasoAPaso.setEnabled (True)
    proc_interprete = None
    if mdi_juego:
      mdi_juego.close()
    if pilaProcs:
      ultimaEntrada = [pilaProcs[-1][0]]
      if len (pilaProcs[-1]) > 1:
        ultimaEntrada.extend ([pilaProcs[-1][1], -2])
      pilas_pendientes.append ([ultimaEntrada])
      self.cambiaPila.emit()

class ModalEntrada (QInputDialog):
  """Modal de entrada QInputDialog con el primer carácter ya introducido, para continuar en siguiente pulsación sin machacarlo"""
  def __init__ (self, parent, etiqueta, textoInicial, textoOriginal = ''):
    QInputDialog.__init__ (self, parent)
    self.textoInicial  = textoInicial
    self.textoOriginal = textoOriginal
    self.setLabelText (etiqueta)
    self.setWindowTitle ('Modal')
    # Si los descomento, no funciona la introducción del valor inicial
    # self.setCancelButtonText ('&Cancelar')
    # self.setOkButtonText ('&Aceptar')

  def _valorInicial (self):
    combo = self.findChild (QComboBox)
    if combo:
      campo = combo.lineEdit()
    else:
      campo = self.findChild (QLineEdit)
    if self.textoOriginal:
      campo.setText (self.textoOriginal)
      campo.selectAll()
      campo.insert (self.textoInicial)
    else:
      campo.setText (self.textoInicial)

  def showEvent (self, evento):
    QTimer.singleShot (0, self._valorInicial)

class ModalEntradaTexto (QDialog):
  """Modal de entrada de texto multilínea"""
  def __init__ (self, parent, texto):
    QDialog.__init__ (self, parent)
    self.campo = QPlainTextEdit (daTextoImprimible (texto).replace ('\\n', '\n'), self)
    layout = QVBoxLayout (self)
    layout.addWidget (self.campo)
    layoutBotones = QHBoxLayout()
    botonAceptar  = QPushButton ('&Aceptar',  self)
    botonCancelar = QPushButton ('&Cancelar', self)
    botonAceptar.clicked.connect (self.accept)
    botonCancelar.clicked.connect (self.reject)
    layoutBotones.addWidget (botonAceptar)
    layoutBotones.addWidget (botonCancelar)
    layout.addLayout (layoutBotones)
    self.setWindowTitle ('Edita el texto')

  def daTexto (self):
    """Devuelve el texto editado"""
    return mod_actual.escribe_secs_ctrl (str (self.campo.toPlainText()))

class ModeloTextos (QAbstractTableModel):
  """Modelo para las tablas de mensajes y de descripciones"""
  def __init__ (self, parent, listaTextos):
    QAbstractTableModel.__init__ (self, parent)
    self.listaTextos = listaTextos

  def columnCount (self, parent):
    return 1

  def data (self, index, role):
    if role == Qt.DisplayRole:
      return daTextoImprimible (self.listaTextos[index.row()])

  def flags (self, index):
    return Qt.ItemIsSelectable | Qt.ItemIsEnabled

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      if self.listaTextos in (mod_actual.msgs_sys, mod_actual.msgs_sys):
        return 'Texto del mensaje'
      return 'Texto de la descripción'
    if orientation == Qt.Vertical and role == Qt.DisplayRole:
      return section  # Cuenta el número de mensaje desde 0
    return QAbstractTableModel.headerData (self, section, orientation, role)

  def rowCount (self, parent):
    return len (self.listaTextos)

class ModeloVocabulario (QAbstractTableModel):
  """Modelo para la tabla de vocabulario"""
  def __init__ (self, parent):
    QAbstractTableModel.__init__ (self, parent)
    self.tituloCols = ('Palabra', 'Código', 'Tipo')
    self.tipos      = mod_actual.TIPOS_PAL

  def columnCount (self, parent):
    return 3

  def data (self, index, role):
    if role == Qt.DisplayRole:
      if index.column() == 0:
        return mod_actual.vocabulario[index.row()][0]  # Palabra
      if index.column() == 1:
        return mod_actual.vocabulario[index.row()][1]  # Código
      # Si llega aquí, es la tercera columna: el tipo
      tipo = mod_actual.vocabulario[index.row()][2]
      if tipo == 255:
        return 'Reservado'
      if tipo > len (self.tipos):
        return 'Desconocido (' + str (tipo) + ')'
      return self.tipos[tipo].replace ('cion', 'ción')

  def flags (self, index):
    return Qt.ItemIsSelectable | Qt.ItemIsEnabled

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.tituloCols[section]
    return QAbstractTableModel.headerData(self, section, orientation, role)

  def rowCount (self, parent):
    return len (mod_actual.vocabulario)

class PantallaJuego (QMdiSubWindow):
  """Subventana MDI para la pantalla de juego del intérprete"""
  def __init__ (self, parent):
    QMdiSubWindow.__init__ (self, parent)
    self.nivelZoom  = 1
    self.rutaImagen = os.path.join (os.path.dirname (os.path.realpath (__file__)), 'ventanaJuegoActual.bmp')
    self.pixmap     = QPixmap (self.rutaImagen)
    self.tamInicial = None
    widget = QLabel (self)
    widget.setPixmap (self.pixmap)
    widget.setWindowTitle ('Ejecución ' + mod_actual.NOMBRE_SISTEMA + ' - Parada')
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
    # En cuanto tenga tamaño adecuado, ponemos ese tamaño como mínimo, para que muestre la pantalla de juego entera
    if not self.tamInicial and self.sizeHint().width() > self.pixmap.width():
      self.anchoBorde = (self.sizeHint().width() - self.pixmap.width()) / 2
      self.altoTitulo = QApplication.style().pixelMetric (QStyle.PM_TitleBarHeight)
      if self.sizeHint().height() == self.pixmap.height() + self.anchoBorde * 2 + self.altoTitulo:
        self.altoTitulo += self.anchoBorde  # pixelMetric no incluía el borde al dar el alto de la barra de título
      if self.sizeHint().height() == self.pixmap.height() + self.anchoBorde + self.altoTitulo:
        self.tamInicial = self.sizeHint()
        selector.centralWidget().tileSubWindows()
        self.setMinimumSize (self.tamInicial)
        self.setMaximumSize (QSize (self.anchoBorde * 2 + self.pixmap.size().width() * 3,
                                    self.anchoBorde + self.altoTitulo + self.pixmap.size().height() * 3))

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
      return  # Ignoramos teclas modificadoras, de bloqueo y de función
    enviar = '\n' if sys.version_info[0] < 3 else b'\n'
    if evento.key() in conversion_teclas:
      if sys.version_info[0] < 3:
        enviar = chr (0) + chr (conversion_teclas[evento.key()]) + enviar
      else:
        enviar = bytes ([0, conversion_teclas[evento.key()]]) + enviar
    elif evento.key() not in (Qt.Key_Enter, Qt.Key_Return):
      if sys.version_info[0] < 3:
        enviar = str (evento.text()) + enviar
      else:
        enviar = bytes (str (evento.text()), locale.getpreferredencoding()) + enviar
    proc_interprete.stdin.write (enviar)
    proc_interprete.stdin.flush()

  def resizeEvent (self, evento):
    """Ajusta la redimensión de la pantalla de juego a los niveles de zoom permitidos"""
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
    self.tamAntes = None  # Tamaño anterior del layout

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
    anchoCol = 0
    colEsPar = True
    x        = 0
    y        = 0
    for item in self.items:
      if y + item.sizeHint().height() > dimensiones.height():  # Sobrepasará por abajo
        x       += anchoCol
        y        = 0
        anchoCol = item.sizeHint().width()
        colEsPar = not colEsPar
      else:
        anchoCol = max (anchoCol, item.sizeHint().width())
      item.setGeometry (QRect (QPoint (x, y), item.sizeHint()))
      item.widget().setStyleSheet (estilo_fila_par if colEsPar else estilo_fila_impar)
      y += item.sizeHint().height()

  def redibuja (self):
    self.tamAntes = None


def actualizaBanderas (cambiosBanderas):
  """Actualiza el valor de las banderas"""
  global banderas
  for numBandera in cambiosBanderas:
    banderas[numBandera] = cambiosBanderas[numBandera]
    if dlg_banderas:
      botonBandera = dlg_banderas.layout().items[numBandera].widget()
      botonBandera.setText (str (numBandera % 100) + ': ' + str (banderas[numBandera]))
      botonBandera.setToolTip ('Valor de la bandera ' + str (numBandera) + ': ' + str (banderas[numBandera]))
  if dlg_banderas:
    dlg_banderas.layout().redibuja()

def actualizaProceso ():
  """Redibuja el proceso actualmente mostrado, si hay alguno"""
  if dlg_procesos:
    cursor = campo_txt.textCursor()
    linea  = cursor.block()
    numEntrada, posicion = campo_txt._daNumEntradaYLinea (linea)
    cambiaProceso (pestanyas.currentIndex(), numEntrada)

def actualizaPosProcesos ():
  """Refleja la posición de ejecución paso a paso actual en el diálogo de tablas de proceso"""
  global inicio_debug, pila_procs
  pilaAnterior = pila_procs
  if len (pilas_pendientes) > 4:
    # Se están acumulando, por lo que tomamos la última y descartamos las demás
    pila_procs = pilas_pendientes[-1]
    del pilas_pendientes[:]
  elif pilas_pendientes:
    pila_procs = pilas_pendientes.pop (0)
  else:  # No queda nada más por actualizar
    return
  muestraProcesos()
  if not pila_procs:
    cambiaProceso (pestanyas.currentIndex())
  elif pestanyas.currentIndex() == pila_procs[-1][0]:  # La línea ejecutándose actualmente es del proceso seleccionado
    proceso = mod_actual.tablas_proceso[pila_procs[-1][0]]
    # Desmarcamos la línea marcada anteriormente
    if pilaAnterior and len (pilaAnterior[-1]) > 1:
      campo_txt.irAEntradaYCondacto (pilaAnterior[-1][1], pilaAnterior[-1][2])
      cursor = campo_txt.textCursor()
      cursor.movePosition (QTextCursor.EndOfBlock)
      cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
      if pilaAnterior[-1][2] > -1:  # Es línea de condacto
        cursor.movePosition (QTextCursor.Left, QTextCursor.KeepAnchor)
      cursor.removeSelectedText()
      campo_txt.setTextBackgroundColor (color_base)
      if pilaAnterior[-1][2] == -1:  # Es línea de cabecera
        cabecera = proceso[0][pilaAnterior[-1][1]]
        imprimeCabecera (cabecera[0], cabecera[1], pilaAnterior[-1][1])
      else:
        entrada  = proceso[1][pilaAnterior[-1][1]]
        condacto = entrada[pilaAnterior[-1][2]]
        imprimeCondacto (*condacto)
    # Marcamos la línea ejecutándose actualmente
    if len (pila_procs[-1]) > 1:
      campo_txt.irAEntradaYCondacto (pila_procs[-1][1], pila_procs[-1][2])
      cursor = campo_txt.textCursor()
      cursor.movePosition (QTextCursor.EndOfBlock)
      cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
      if pila_procs[-1][2] > -1:  # Es línea de condacto
        cursor.movePosition (QTextCursor.Left, QTextCursor.KeepAnchor)
      cursor.removeSelectedText()
      campo_txt.setTextBackgroundColor (color_tope_pila)
      if pila_procs[-1][2] == -1:  # Es línea de cabecera
        cabecera = proceso[0][pila_procs[-1][1]]
        imprimeCabecera (cabecera[0], cabecera[1], pila_procs[-1][1])
      else:
        entrada  = proceso[1][pila_procs[-1][1]]
        condacto = entrada[pila_procs[-1][2]]
        imprimeCondacto (*condacto)
    campo_txt.centraLineaCursor()
  else:
    pestanyas.setCurrentIndex (pila_procs[-1][0])
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
      # Colocamos el diálogo de procesos a la derecha del de juego, tomando todo el alto disponible
      mdi_procesos.resize (selector.centralWidget().width() - anchoJuego, selector.centralWidget().height())
      mdi_procesos.move (anchoJuego, 0)
      muestraBanderas()
      selector.centralWidget().setActiveSubWindow (mdi_juego)

def actualizaVentanaJuego ():
  """Muestra o actualiza la pantalla actual de juego del intérprete en el diálogo de ventana de juego"""
  global mdi_juego
  if mdi_juego:  # Subventana MDI ya creada
    try:
      mdi_juego.actualizaImagen()
      return
    except RuntimeError:  # Subventana borrada por Qt
      pass  # La crearemos de nuevo
  # Creamos la subventana
  mdi_juego = PantallaJuego (selector)

# FIXME: Diferencias entre PAWS estándar y DAAD
def cambiaProceso (numero, numEntrada = None):
  """Llamada al cambiar de pestaña en el diálogo de procesos"""
  global pals_no_existen
  selector.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
  proceso   = mod_actual.tablas_proceso[numero]  # El proceso seleccionado
  cabeceras = proceso[0]  # Las cabeceras del proceso seleccionado
  entradas  = proceso[1]  # Las entradas del proceso seleccionado
  posicion  = None  # Posición donde ir al terminar de cargar el contenido del proceso
  if numEntrada == None and pila_procs and len (pila_procs[-1]) > 1 and pila_procs[-1][0] == numero:
    numEntrada = pila_procs[-1][1]
  campo_txt.clear()  # Borramos el texto anterior
  for i in range (len (cabeceras)):
    if i == numEntrada:
      posicion = campo_txt.textCursor().position()
    if [numero, i, -1] in pila_procs:
      campo_txt.setTextBackgroundColor (color_tope_pila if pila_procs[-1] == [numero, i, -1] else color_pila)
    else:
      campo_txt.setTextBackgroundColor (color_base)
    imprimeCabecera (cabeceras[i][0], cabeceras[i][1], i)
    campo_txt.insertPlainText ('\n     ')
    inalcanzable = False  # Marca de código inalcanzable
    for c in range (len (entradas[i])):
      condacto, parametros = entradas[i][c]
      if [numero, i, c] in pila_procs:
        if pila_procs[-1] == [numero, i, c]:
          posicion = campo_txt.textCursor().position()
          campo_txt.setTextBackgroundColor (color_tope_pila)
        else:
          campo_txt.setTextBackgroundColor (color_pila)
      inalcanzable = imprimeCondacto (condacto, parametros, inalcanzable)
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
  selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def cargaInfoModulos ():
  """Carga la información de los módulos de librería válidos que encuentre en el directorio"""
  # TODO: Informar de los errores
  # TODO: No permitir entradas con igual conjunto de extensiones y descripción,
  # pero distinta función a llamar (aunque sean de módulos distintos)
  # Nombres de los módulos de librería en el directorio
  nombres = [f[:-3] for f in os.listdir (os.path.dirname (os.path.realpath (__file__)))
             if (f[:9] == 'libreria_' and f[-3:] == '.py')]
  for nombre_modulo in nombres:
    try:
      modulo = __import__ (nombre_modulo)
    except SyntaxError as excepcion:
      prn ('Error al importar el módulo:', excepcion)
      continue
    # Apaño para que funcione las librerías de DAAD, PAW y SWAN tal y como están (con lista unificada de condactos)
    if comprueba_nombre (modulo, 'condactos', dict) and not comprueba_nombre (modulo, 'acciones', dict):
      modulo.acciones    = {}
      modulo.condiciones = {}
    # Comprobamos que el módulo tenga todos los nombres necesarios
    for nombre, tipo in nombres_necesarios:
      if not comprueba_nombre (modulo, nombre, tipo):
        modulo = None  # Módulo de librería inválido, lo liberamos
        break
    if modulo == None:
      continue
    for entrada in modulo.funcs_importar:
      if comprueba_nombre (modulo, entrada[0], types.FunctionType):
        info_importar.append ((nombre_modulo, entrada[0], entrada[1], entrada[2]))
    if comprueba_nombre (modulo, modulo.func_nueva, types.FunctionType):
      info_nueva.append ((nombre_modulo, modulo.func_nueva))
      accion = QAction ('Base de datos ' + modulo.NOMBRE_SISTEMA, menuBDNueva)
      accion.setStatusTip ('Crea una nueva base de datos de ' + modulo.NOMBRE_SISTEMA)
      accion.triggered.connect (lambda: nuevaBD (len (info_nueva) - 1))
      menuBDNueva.addAction (accion)
    del modulo
  # Actualizamos las distintas acciones y menús, según corresponda
  accExportar.setEnabled (False)
  accImportar.setEnabled (len (info_importar) > 0)
  menuBDNueva.setEnabled (len (info_nueva) > 0)

def cierraDialogos ():
  """Cierra todos los diálogos no modales"""
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
  """Crea las acciones de menú y barra de botones"""
  global acc1Paso, acc10Pasos, acc100Pasos, acc1000Pasos, accAcercaDe, accBanderas, accContadores, accDescLocs, accDescObjs, accDireccs, accExportar, accImportar, accMostrarLoc, accMostrarObj, accMostrarRec, accMostrarSys, accMostrarUsr, accMsgSys, accMsgUsr, accPasoAPaso, accSalir, accTblProcs, accTblVocab
  acc1Paso      = QAction (icono ('pasos_1'),    '1 paso',     selector)
  acc10Pasos    = QAction (icono ('pasos_10'),   '10 pasos',   selector)
  acc100Pasos   = QAction (icono ('pasos_100'),  '100 pasos',  selector)
  acc1000Pasos  = QAction (icono ('pasos_1000'), '1000 pasos', selector)
  accAcercaDe   = QAction (icono_ide, '&Acerca de NAPS IDE', selector)
  accBanderas   = QAction (icono ('banderas'), '&Banderas', selector)
  accContadores = QAction (icono ('contadores'), '&Contadores', selector)
  accDescLocs   = QAction (icono ('desc_localidad'), 'Descripciones de &localidades', selector)
  accDescObjs   = QAction (icono ('desc_objeto'),    'Descripciones de &objetos',     selector)
  accDireccs    = QAction (icono ('direccion'), '&Direcciones', selector)
  accExportar   = QAction (icono ('exportar'), '&Exportar', selector)
  accImportar   = QAction (icono ('importar'), '&Importar', selector)
  accMostrarLoc = QAction ('Descripciones de &localidades', selector)
  accMostrarObj = QAction ('Descripciones de &objetos',     selector)
  accMostrarRec = QAction ('&Recortar al ancho de línea',   selector)
  accMostrarSys = QAction ('Mensajes de &sistema', selector)
  accMostrarUsr = QAction ('Mensajes de &usuario', selector)
  accMsgSys     = QAction (icono ('msg_sistema'), 'Mensajes de &sistema', selector)
  accMsgUsr     = QAction (icono ('msg_usuario'), 'Mensajes de &usuario', selector)
  accPasoAPaso  = QAction (icono ('pasoapaso'), '&Paso a paso', selector)
  accSalir      = QAction (icono ('salir'), '&Salir', selector)
  accTblProcs   = QAction (icono ('proceso'), '&Tablas', selector)
  accTblVocab   = QAction (icono ('vocabulario'), '&Tabla', selector)
  accMostrarLoc.setCheckable (True)
  accMostrarObj.setCheckable (True)
  accMostrarRec.setCheckable (True)
  accMostrarSys.setCheckable (True)
  accMostrarUsr.setCheckable (True)
  accMostrarLoc.setChecked (True)
  accMostrarObj.setChecked (True)
  accMostrarRec.setChecked (True)
  accMostrarSys.setChecked (True)
  accMostrarUsr.setChecked (True)
  acc1Paso.setEnabled      (False)
  acc10Pasos.setEnabled    (False)
  acc100Pasos.setEnabled   (False)
  acc1000Pasos.setEnabled  (False)
  accBanderas.setEnabled   (False)
  accContadores.setEnabled (False)
  accDescLocs.setEnabled   (False)
  accDescObjs.setEnabled   (False)
  accDireccs.setEnabled    (False)
  accMostrarLoc.setEnabled (False)
  accMostrarObj.setEnabled (False)
  accMostrarRec.setEnabled (False)
  accMostrarSys.setEnabled (False)
  accMostrarUsr.setEnabled (False)
  accMsgSys.setEnabled     (False)
  accMsgUsr.setEnabled     (False)
  accPasoAPaso.setEnabled  (False)
  accTblProcs.setEnabled   (False)
  accTblVocab.setEnabled   (False)
  acc1Paso.setShortcut     ('F1')
  acc10Pasos.setShortcut   ('F2')
  acc100Pasos.setShortcut  ('F3')
  acc1000Pasos.setShortcut ('F4')
  accSalir.setShortcut     ('Ctrl+Q')
  acc1Paso.setStatusTip      ('Ejecuta un paso de la base de datos y después para')
  acc10Pasos.setStatusTip    ('Ejecuta hasta diez pasos de la base de datos y después para')
  acc100Pasos.setStatusTip   ('Ejecuta hasta cien pasos de la base de datos y después para')
  acc1000Pasos.setStatusTip  ('Ejecuta hasta mil pasos de la base de datos y después para')
  accAcercaDe.setStatusTip   ('Muestra información del programa')
  accBanderas.setStatusTip   ('Permite consultar y modificar las banderas')
  accContadores.setStatusTip ('Muestra el número de elementos de cada tipo')
  accDescLocs.setStatusTip   ('Permite consultar y modificar las descripciones de las localidades')
  accDescObjs.setStatusTip   ('Permite consultar y modificar las descripciones de los objetos')
  accDireccs.setStatusTip    ('Permite añadir y editar las palabras de dirección')
  accExportar.setStatusTip   ('Exporta la base de datos a un fichero')
  accImportar.setStatusTip   ('Importa una base de datos desde un fichero')
  accMostrarLoc.setStatusTip ('Mostrar descripciones de localidades cuando los condactos las referencien')
  accMostrarObj.setStatusTip ('Mostrar descripciones de objetos cuando los condactos los referencien')
  accMostrarRec.setStatusTip ('Recortar textos a la anchura de línea disponible')
  accMostrarSys.setStatusTip ('Mostrar texto de mensajes de sistema cuando los condactos los referencien')
  accMostrarUsr.setStatusTip ('Mostrar texto de mensajes de usuario cuando los condactos los referencien')
  accMsgSys.setStatusTip     ('Permite consultar y modificar los mensajes de sistema')
  accMsgUsr.setStatusTip     ('Permite consultar y modificar los mensajes de usuario')
  accPasoAPaso.setStatusTip  ('Depura la base de datos ejecutándola paso a paso')
  accSalir.setStatusTip      ('Sale de la aplicación')
  accTblProcs.setStatusTip   ('Permite consultar y modificar las tablas de proceso')
  accTblVocab.setStatusTip   ('Permite consultar el vocabulario')
  accTblProcs.setToolTip ('Tablas de proceso')
  accTblVocab.setToolTip ('Tabla de vocabulario')
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
  accMostrarUsr.triggered.connect (actualizaProceso)
  accMsgSys.triggered.connect     (muestraMsgSys)
  accMsgUsr.triggered.connect     (muestraMsgUsr)
  accPasoAPaso.triggered.connect  (ejecutaPorPasos)
  accSalir.triggered.connect      (selector.close)
  accTblProcs.triggered.connect   (muestraProcesos)
  accTblVocab.triggered.connect   (muestraVistaVocab)

def creaBarraBotones ():
  """Crea la barra de botones"""
  barraBotones = selector.addToolBar ('Barra de botones')
  barraBotones.addAction (accImportar)
  barraBotones.addSeparator()
  barraBotones.addAction (accTblProcs)
  barraBotones.addAction (accTblVocab)
  barraBotones.addAction (accMsgSys)
  barraBotones.addAction (accMsgUsr)
  barraBotones.addAction (accDescLocs)
  barraBotones.addAction (accDescObjs)
  barraBotones.setIconSize (QSize (16, 16))

def creaMenus ():
  """Crea y organiza los menús"""
  global menuBDNueva
  menuBD      = selector.menuBar().addMenu ('&Base de datos')
  menuBDNueva = QMenu ('&Nueva', menuBD)
  menuBDNueva.setIcon (icono ('nueva'))
  menuBD.addMenu   (menuBDNueva)
  menuBD.addAction (accImportar)
  menuBD.addAction (accExportar)
  menuBD.addSeparator()
  menuBD.addAction (accContadores)
  menuBD.addSeparator()
  menuBD.addAction (accSalir)
  menuEjecutar = selector.menuBar().addMenu ('&Ejecución')
  menuEjecutar.addAction (accPasoAPaso)
  menuEjecutar.addSeparator()
  menuEjecutar.addAction (acc1Paso)
  menuEjecutar.addAction (acc10Pasos)
  menuEjecutar.addAction (acc100Pasos)
  menuEjecutar.addAction (acc1000Pasos)
  menuEjecutar.addSeparator()
  menuEjecutar.addAction (accBanderas)
  menuProcesos     = selector.menuBar().addMenu ('&Procesos')
  menuProcsMostrar = QMenu ('&Mostrar textos', menuProcesos)
  menuProcsMostrar.addAction (accMostrarLoc)
  menuProcsMostrar.addAction (accMostrarObj)
  menuProcsMostrar.addAction (accMostrarSys)
  menuProcsMostrar.addAction (accMostrarUsr)
  menuProcsMostrar.addSeparator()
  menuProcsMostrar.addAction (accMostrarRec)
  menuProcesos.addAction (accTblProcs)
  menuProcesos.addSeparator()
  menuProcesos.addMenu (menuProcsMostrar)
  menuTextos = selector.menuBar().addMenu ('&Textos')
  menuTextos.addAction (accDescLocs)
  menuTextos.addAction (accDescObjs)
  menuTextos.addSeparator()
  menuTextos.addAction (accMsgSys)
  menuTextos.addAction (accMsgUsr)
  menuVocabulario = selector.menuBar().addMenu ('&Vocabulario')
  menuVocabulario.addAction (accDireccs)
  menuVocabulario.addAction (accTblVocab)
  menuAyuda = selector.menuBar().addMenu ('&Ayuda')
  menuAyuda.addAction (accAcercaDe)

def creaSelector ():
  """Crea y organiza la ventana del selector"""
  global icono_ide, selector
  icono_ide = icono ('ide')
  selector  = QMainWindow()
  selector.resize (630, 460)
  selector.setCentralWidget (QMdiArea (selector))
  selector.setWindowIcon    (icono_ide)
  selector.setWindowTitle   ('NAPS IDE')
  creaAcciones()
  creaMenus()
  creaBarraBotones()
  barraEstado = selector.statusBar()  # Queremos una barra de estado

def daTextoComoParrafoHtml (texto):
  """Devuelve el texto dado metido en un párrafo html, con los caracteres que usa html correctamente escapados"""
  texto = texto.replace ('&', '&amp;').replace ('<', '&lt;').replace ('>', '&gt;')
  return '<p>' + texto + '</p>'

def daTextoImprimible (texto):
  """Da la representación imprimible del texto dado según la librería de la plataforma PAW-like"""
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
  return convertido

def dialogoImportaBD ():
  """Deja al usuario elegir un fichero de base datos, y lo intenta importar"""
  global dlg_abrir
  filtro = []
  for modulo, funcion, extensiones, descripcion in info_importar:
    filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
  if not dlg_abrir:  # Diálogo no creado aún
    dlg_abrir = QFileDialog (selector, 'Importar base de datos', os.curdir, ';;'.join (sorted (filtro)))
    dlg_abrir.setFileMode  (QFileDialog.ExistingFile)
    dlg_abrir.setLabelText (QFileDialog.LookIn,   'Lugares')
    dlg_abrir.setLabelText (QFileDialog.FileName, '&Nombre:')
    dlg_abrir.setLabelText (QFileDialog.FileType, 'Filtro:')
    dlg_abrir.setLabelText (QFileDialog.Accept,   '&Abrir')
    dlg_abrir.setLabelText (QFileDialog.Reject,   '&Cancelar')
    dlg_abrir.setOption    (QFileDialog.DontUseNativeDialog)
  if dlg_abrir.exec_():  # No se ha cancelado
    selector.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    cierraDialogos()
    indiceFiltro  = filtro.index (dlg_abrir.selectedNameFilter())
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_abrir.selectedFiles()[0])
    importaBD (nombreFichero, indiceFiltro)
    selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def editaBandera (numBandera):
  """Permite editar el valor de una bandera"""
  dialogo = ModalEntrada (dlg_banderas, 'Valor de la bandera ' + str (numBandera) + ':', str (banderas[numBandera]))
  dialogo.setInputMode   (QInputDialog.IntInput)
  dialogo.setIntRange    (0, 255)
  dialogo.setWindowTitle ('Editar')
  if dialogo.exec_() == QDialog.Accepted:
    if dialogo.intValue() != banderas[numBandera]:
      banderas[numBandera] = dialogo.intValue()
      botonBandera = dlg_banderas.layout().items[numBandera].widget()
      botonBandera.setText (str (numBandera % 100) + ': ' + str (banderas[numBandera]))
      botonBandera.setToolTip ('Valor de la bandera ' + str (numBandera) + ': ' + str (banderas[numBandera]))
      dlg_banderas.layout().redibuja()
      if sys.version_info[0] < 3:
        proc_interprete.stdin.write ('#' + str (numBandera) + '=' + str (banderas[numBandera]) + '\n')
      else:  # Python 3+
        proc_interprete.stdin.write (bytes ('#' + str (numBandera) + '=' + str (banderas[numBandera]) + '\n', locale.getpreferredencoding()))

def editaDescLoc (indice):
  """Permite editar el texto de una descripción de localidad, tras hacer doble click en su tabla"""
  dialogo = ModalEntradaTexto (dlg_desc_locs, mod_actual.desc_locs[indice.row()])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.desc_locs[indice.row()] = dialogo.daTexto()

def editaDescObj (indice):
  """Permite editar el texto de una descripción de objeto, tras hacer doble click en su tabla"""
  dialogo = ModalEntradaTexto (dlg_desc_objs, mod_actual.desc_objs[indice.row()])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.desc_objs[indice.row()] = dialogo.daTexto()

def editaMsgSys (indice):
  """Permite editar el texto de un mensaje de sistema, tras hacer doble click en su tabla"""
  dialogo = ModalEntradaTexto (dlg_msg_sys, mod_actual.msgs_sys[indice.row()])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.msgs_sys[indice.row()] = dialogo.daTexto()

def editaMsgUsr (indice):
  """Permite editar el texto de un mensaje de usuario, tras hacer doble click en su tabla"""
  dialogo = ModalEntradaTexto (dlg_msg_usr, mod_actual.msgs_usr[indice.row()])
  if dialogo.exec_() == QDialog.Accepted:
    mod_actual.msgs_usr[indice.row()] = dialogo.daTexto()

def editaVocabulario (indice):
  """Permite editar una entrada de vocabulario, tras hacer doble click en su tabla"""
  dlg_vocabulario.indiceDobleClick = indice  # Para descartar evento activated posterior
  nuevaPal = None  # Entrada de vocabulario modificada
  numFila  = indice.row()
  palVocab = mod_actual.vocabulario[numFila]
  if indice.column() == 0:  # Palabra
    dialogo = ModalEntrada (dlg_vocabulario, 'Texto de la palabra:', palVocab[0])
    dialogo.setWindowTitle ('Editar')
    if dialogo.exec_() == QDialog.Accepted:
      nuevaPal = (str (dialogo.textValue())[:mod_actual.LONGITUD_PAL].lower(), ) + palVocab[1:]
  elif indice.column() == 1:  # Código
    dialogo = ModalEntrada (dlg_vocabulario, 'Código de la palabra:', str (palVocab[1]))
    dialogo.setInputMode   (QInputDialog.IntInput)
    dialogo.setIntRange    (0, 255)
    dialogo.setWindowTitle ('Editar')
    if dialogo.exec_() == QDialog.Accepted:
      nuevaPal = (palVocab[0], dialogo.intValue(), palVocab[2])
  else:  # indice.column() == 2:  # Tipo
    tiposPalabra = {255: 'Reservado'}
    for i in range (len (mod_actual.TIPOS_PAL)):
      tiposPalabra[i] = mod_actual.TIPOS_PAL[i].replace ('cion', 'ción')
    dialogo = ModalEntrada (dlg_vocabulario, 'Tipo de palabra:', tiposPalabra[palVocab[2]])
    dialogo.setComboBoxEditable (True)
    dialogo.setComboBoxItems    (sorted (tiposPalabra.values()))
    dialogo.setWindowTitle      ('Editar')
    if dialogo.exec_() == QDialog.Accepted and dialogo.textValue() in tiposPalabra.values():
      nuevaPal = (palVocab[0], palVocab[1],
                  list (tiposPalabra.keys())[list (tiposPalabra.values()).index (dialogo.textValue())])
  if not nuevaPal or mod_actual.vocabulario[numFila] == nuevaPal:
    return  # No se ha modificado
  nuevaEntradaVocabulario (nuevaPal, numFila)

def ejecutaPasos (indicePasos):
  """Pide al intérprete ejecutar cierto número de pasos"""
  teclasPasos = '1 \t\n'
  proc_interprete.stdin.write (teclasPasos[indicePasos] if sys.version_info[0] < 3 else bytes ([ord (teclasPasos[indicePasos])]))
  if indicePasos < 3:  # Nueva línea final
    proc_interprete.stdin.write ('\n' if sys.version_info[0] < 3 else b'\n')
  proc_interprete.stdin.flush()

def ejecutaPorPasos ():
  """Ejecuta la base de datos para depuración paso a paso"""
  global banderas, pilas_pendientes, inicio_debug, proc_interprete
  banderas     = [0] * mod_actual.NUM_BANDERAS  # Inicializamos las banderas
  inicio_debug = True
  accBanderas.setEnabled  (True)
  accPasoAPaso.setEnabled (False)
  rutaInterprete = os.path.join (os.path.dirname (os.path.realpath (__file__)), 'interprete.py')
  argumentos     = ['python', rutaInterprete, '--ide', nombre_fich_bd]
  if nombre_fich_gfx:
    argumentos.append (nombre_fich_gfx)
  devnull = open (os.devnull, 'w')
  proc_interprete  = subprocess.Popen (argumentos, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = devnull)
  pilas_pendientes = []
  hilo = ManejoInterprete (proc_interprete, aplicacion)
  hilo.cambiaBanderas.connect (actualizaBanderas)
  hilo.cambiaImagen.connect   (actualizaVentanaJuego)
  hilo.cambiaPila.connect     (actualizaPosProcesos)
  hilo.start()

def exportaBD ():
  """Exporta la base de datos a fichero"""
  global dlg_guardar, mod_actual
  if not dlg_guardar:  # Diálogo no creado aún
    filtro = []
    for funcion, extensiones, descripcion in info_exportar:
      filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
    dlg_guardar = QFileDialog (selector, 'Exportar base de datos', os.curdir,
        ';;'.join (filtro))
    dlg_guardar.setAcceptMode (QFileDialog.AcceptSave)
    dlg_guardar.setLabelText  (QFileDialog.LookIn,   'Lugares')
    dlg_guardar.setLabelText  (QFileDialog.FileName, '&Nombre:')
    dlg_guardar.setLabelText  (QFileDialog.FileType, 'Filtro:')
    dlg_guardar.setLabelText  (QFileDialog.Accept,   '&Guardar')
    dlg_guardar.setLabelText  (QFileDialog.Reject,   '&Cancelar')
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
      dlgSiNo.addButton ('&Sí', QMessageBox.YesRole)
      dlgSiNo.addButton ('&No', QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle ('Sobreescritura')
      dlgSiNo.setText ('Ya existe un fichero con ruta y nombre:\n\n' + nombreFichero)
      dlgSiNo.setInformativeText ('\n¿Quieres sobreescribirlo?')
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el botón Sí
        return
    selector.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    try:
      fichero = open (nombreFichero, 'w')
    except IOError as excepcion:
      muestraFallo ('No se puede abrir el fichero:\n' + nombreFichero,
                    'Causa:\n' + excepcion.args[1])
      selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal
      return
    mod_actual.__dict__[info_exportar[indiceFiltro][0]] (fichero)
    fichero.close()
    selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

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
    muestraFallo ('No se puede abrir el fichero:\n' + nombreFicheroBD,
                  'Causa:\n' + excepcion.args[1])
    return
  if '.' not in nombreFicheroBD:
    muestraFallo ('No se puede importar una base datos de:\n' + nombreFicheroBD,
                  'Causa:\nNo tiene extensión')
    return
  modulos = []  # Módulos que soportan la extensión, junto con su función de carga
  if indiceFuncion != None:
    modulo, funcion, extensiones, descripcion = info_importar[indiceFuncion]
    modulos.append ((modulo, funcion))
  else:
    extension = nombreFicheroBD[nombreFicheroBD.rindex ('.') + 1 :].lower()
    for modulo, funcion, extensiones, descripcion in info_importar:
      if extension in extensiones:
        modulos.append ((modulo, funcion))
    if not modulos:
      muestraFallo ('No se puede importar una base datos de:\n' + nombreFicheroBD,
                    'Causa:\nExtensión no reconocida')
      return
  # Importamos la BD y damos acceso al módulo a funciones del IDE
  hayFallo = True
  for modulo, funcion in modulos:
    recargar   = modulo in sys.modules
    mod_actual = __import__ (modulo)
    if recargar:
      mod_actual = reload (mod_actual)
    mod_actual.muestraFallo = muestraFallo
    mod_actual.nada_tras_flujo.append (True)
    # Solicitamos la importación
    if mod_actual.__dict__[funcion] (fichero, os.path.getsize (nombreFicheroBD)) != False:
      hayFallo = False
      break
    fichero.seek (0)
  fichero.close()
  if hayFallo:
    muestraFallo ('No se puede importar una base datos de:\n' +
                  nombreFicheroBD, 'Causa:\nFormato de fichero incompatible o base de datos corrupta')
    mod_actual = None
    return
  nombre_fich_bd  = nombreFicheroBD
  nombre_fich_gfx = nombreFicheroGfx
  postCarga (os.path.basename (nombreFicheroBD))
  return True

def imprimeCabecera (verbo, nombre, numEntrada):
  """Imprime la cabecera de la entrada numEntrada del proceso, con el verbo y nombre de códigos dados, en campo_txt en la posición del cursor actual"""
  campo_txt.setTextColor (QColor (200, 200, 200))  # Color gris claro
  campo_txt.setFontItalic (True)  # Cursiva activada
  if verbo == 255:
    campo_txt.insertPlainText ('  _  ')
  elif verbo == 1 and (1, 255) in pal_sinonimo:
    campo_txt.insertPlainText ('  *  ')
  elif (verbo, tipo_verbo) in pal_sinonimo:  # Hay un verbo con ese código
    campo_txt.insertPlainText (pal_sinonimo[(verbo, tipo_verbo)].center (5))
  elif verbo < 20 and (verbo, tipo_nombre) in pal_sinonimo:  # Es nombre convertible en verbo
    campo_txt.insertPlainText (pal_sinonimo[(verbo, tipo_nombre)].center (5))
  else:
    campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    if (numero, verbo, tipo_verbo) not in pals_no_existen:
      muestraFallo ('Verbo no existente', 'Verbo de código ' + str (verbo) + ' no encontrado en el vocabulario')
      pals_no_existen.append ((numero, verbo, tipo_verbo))
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
    if (numero, nombre, tipo_nombre) not in pals_no_existen:
      muestraFallo ('Nombre no existente', 'Nombre de código ' + str (nombre) + ' no encontrado en el vocabulario')
      pals_no_existen.append ((numero, nombre, tipo_nombre))
    campo_txt.insertPlainText (str (nombre).center (5).rstrip())
  campo_txt.setFontItalic (False)  # Cursiva desactivada
  campo_txt.setTextBackgroundColor (color_base)
  campo_txt.textCursor().block().setUserState (numEntrada)  # Guardamos el número de la entrada

def imprimeCondacto (condacto, parametros, inalcanzable = False):
  """Imprime el condacto de código y parámetros dados en campo_txt en la posición del cursor actual, opcionalmente indicando si era código inalcanzable. Devuelve True si el parámetro inalcanzable era True o el condacto cambia el flujo incondicionalmente"""
  if inalcanzable:
    campo_txt.setTextColor (QColor (60, 60, 60))  # Color gris muy oscuro
  campo_txt.insertPlainText ('\n  ')
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
  else:  # No debería ocurrir
    if not inalcanzable:
      prn ('FIXME: Condacto', condacto, 'no reconocido por la librería')
      campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    nombre      = str (condacto)
    tiposParams = '?' * len (parametros)
  if parametros:  # Imprimiremos los parámetros
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
        if (tiposParams[p] in 'bw' and parametro >= 8)                    or \
           (tiposParams[p] == '%'  and (parametro < 1 or parametro > 99)) or \
           (tiposParams[p] == 'l'  and parametro >= len (mod_actual.desc_locs)) or \
           (tiposParams[p] == 'L'  and parametro >= len (mod_actual.desc_locs) and parametro not in range (252, 256)) or \
           (tiposParams[p] == 'm'  and parametro >= len (mod_actual.msgs_usr))       or \
           (tiposParams[p] == 'o'  and parametro >= len (mod_actual.desc_objs))      or \
           (tiposParams[p] == 'p'  and parametro >= len (mod_actual.tablas_proceso)) or \
           (tiposParams[p] == 's'  and parametro >= len (mod_actual.msgs_sys)):
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
        elif tiposParams[p] == 'i' and parametro > 128:  # Es un número entero negativo
          parametro -= 256
        elif not inalcanzable and tiposParams == 'p':  # Es un proceso
          cursor  = campo_txt.textCursor()
          formato = cursor.charFormat()
          formato.setAnchor (True)
          formato.setAnchorHref ('proceso:' + str (parametro))
          formato.setFontUnderline (True)
          formato.setToolTip ('Haz Ctrl+click aquí para abrir el proceso ' + str (parametro))
      if formato:
        parametro = str (parametro)
        campo_txt.insertPlainText (' ' * (4 - len (parametro)))
        cursor.insertText (parametro, formato)
        campo_txt.quitaFormatoEnlace()
      else:
        campo_txt.insertPlainText (str (parametro).rjust (4))
    if not inalcanzable and mensaje != None:
      if accMostrarRec.isChecked():  # Recortar al ancho de línea disponible
        qfm = QFontMetrics (campo_txt.font())
        columnasVisibles = int (campo_txt.size().width() // (qfm.size (0, '#').width()))
      if not accMostrarRec.isChecked() or columnasVisibles > 26:  # No recortamos o hay espacio suficiente para mostrar algo de texto
        mensaje = daTextoImprimible (mensaje)
        if not inalcanzable:
          campo_txt.setTextColor (QColor (100, 100, 100))  # Color gris oscuro
        campo_txt.insertPlainText ('       "')
        campo_txt.setFontItalic (True)  # Cursiva activada
        if accMostrarRec.isChecked() and len (mensaje) > columnasVisibles - 26:  # Se recortará al ancho de línea disponible
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
  else:  # Condacto sin parámetros
    campo_txt.insertPlainText ((nombre + indirecto).rstrip().center (7).rstrip())
  if inalcanzable or mod_actual.condactos[condacto][3]:
    return True
  return False

def irAEntradaProceso ():
  """Mueve el cursor a la entrada del proceso actual que elija el usuario"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  dialogo    = ModalEntrada (dlg_procesos, 'Número de entrada:', '')
  dialogo.setInputMode   (QInputDialog.IntInput)
  dialogo.setIntRange    (0, len (proceso[0]) - 1)
  dialogo.setWindowTitle ('Ir a')
  if dialogo.exec_() == QDialog.Accepted:
    campo_txt.irAEntrada (dialogo.intValue())
    campo_txt.centraLineaCursor()

def muestraAcercaDe ():
  """Muestra el diálogo 'Acerca de'"""
  global dlg_acerca_de
  if not dlg_acerca_de:  # Diálogo no creado aún
    # Cogeremos sólo los números de la versión de Python
    fin = sys.version.find (' (')
    dlg_acerca_de = QMessageBox (selector)
    dlg_acerca_de.addButton ('&Aceptar', QMessageBox.AcceptRole)
    dlg_acerca_de.setIconPixmap (icono_ide.pixmap (96))
    dlg_acerca_de.setText ('NAPS: The New Age PAW-like System\n' +
        'Entorno de desarrollo integrado (IDE)\n' +
        'Copyright © 2010, 2018-2023 José Manuel Ferrer Ortiz')
    dlg_acerca_de.setInformativeText ('Versión de PyQt: ' +
        PYQT_VERSION_STR + '\nVersión de Qt: ' + QT_VERSION_STR +
        '\nVersión de Python: ' + sys.version[:fin])
    dlg_acerca_de.setWindowTitle ('Acerca de NAPS IDE')
  dlg_acerca_de.exec_()

def muestraBanderas ():
  """Muestra el diálogo de banderas"""
  global dlg_banderas, mdi_banderas
  if dlg_banderas and mdi_banderas in selector.centralWidget().subWindowList():
    # Diálogo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (mdi_banderas)
      return
    except RuntimeError:  # Diálogo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el diálogo
  dlg_banderas = QWidget (selector)
  layout       = VFlowLayout (dlg_banderas)
  for b in range (mod_actual.NUM_BANDERAS):
    botonBandera = QPushButton (str (b % 100) + ': ' + str (banderas[b]), dlg_banderas)
    botonBandera.clicked.connect (lambda estado, numBandera = b: editaBandera (numBandera))
    botonBandera.setStyleSheet (estilo_fila_par)
    botonBandera.setToolTip ('Valor de la bandera ' + str (b) + ': ' + str (banderas[b]))
    layout.addWidget (botonBandera)
  dlg_banderas.setLayout      (layout)
  dlg_banderas.setWindowTitle ('Banderas')
  mdi_banderas = selector.centralWidget().addSubWindow (dlg_banderas)
  mdi_banderas.setOption (QMdiSubWindow.RubberBandResize)
  dlg_banderas.show()

def muestraContadores ():
  """Muestra el diálogo de contadores"""
  global dlg_contadores
  if not dlg_contadores:  # Diálogo no creado aún
    dlg_contadores = QMessageBox (selector)
    dlg_contadores.addButton ('&Aceptar', QMessageBox.AcceptRole)
    num_palabras = len (mod_actual.vocabulario)
    dlg_contadores.setText ('Procesos: ' + str (len (mod_actual.tablas_proceso))
      + ' tablas\nVocabulario: ' + str (num_palabras) + ' palabra' + \
      ('s' * (num_palabras > 1)))
    dlg_contadores.setWindowTitle ('Contadores')
  dlg_contadores.exec_()

def muestraDescLocs ():
  """Muestra el diálogo para consultar las descripciones de localidades"""
  muestraTextos (dlg_desc_locs, mod_actual.desc_locs, 'desc_localidades', mdi_desc_locs)

def muestraDescObjs ():
  """Muestra el diálogo para consultar las descripciones de objetos"""
  muestraTextos (dlg_desc_objs, mod_actual.desc_objs, 'desc_objetos', mdi_desc_objs)

def muestraFallo (mensaje, detalle):
  """Muestra un diálogo de fallo leve"""
  global dlg_fallo
  if not dlg_fallo:  # Diálogo no creado aún
    dlg_fallo = QMessageBox (selector)
    dlg_fallo.addButton ('&Aceptar', QMessageBox.AcceptRole)
    dlg_fallo.setIcon (QMessageBox.Warning)
    dlg_fallo.setWindowTitle ('Fallo')
  dlg_fallo.setText (mensaje)
  dlg_fallo.setInformativeText (detalle)
  dlg_fallo.exec_()

def muestraMsgSys ():
  """Muestra el diálogo para consultar los mensajes de sistema"""
  muestraTextos (dlg_msg_sys, mod_actual.msgs_sys, 'msgs_sistema', mdi_msg_sys)

def muestraMsgUsr ():
  """Muestra el diálogo para consultar los mensajes de usuario"""
  muestraTextos (dlg_msg_usr, mod_actual.msgs_usr, 'msgs_usuario', mdi_msg_usr)

def muestraProcesos ():
  """Muestra el diálogo para las tablas de proceso"""
  global campo_txt, dlg_procesos, mdi_procesos, pestanyas
  if dlg_procesos and mdi_procesos in selector.centralWidget().subWindowList():  # Diálogo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (mdi_procesos)
      return
    except RuntimeError:  # Diálogo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el diálogo
  dlg_procesos = QWidget (selector)
  layout       = QVBoxLayout (dlg_procesos)
  pestanyas    = QTabBar (dlg_procesos)
  campo_txt    = CampoTexto (dlg_procesos)
  layout.addWidget (pestanyas)
  layout.addWidget (campo_txt)
  pestanyas.currentChanged.connect (cambiaProceso)
  num_procesos = len (mod_actual.tablas_proceso)
  for numero in range (num_procesos):
    str_numero = str (numero)
    if 'NOMBRES_PROCS' in mod_actual.__dict__ and numero < len (mod_actual.NOMBRES_PROCS):
      titulo = mod_actual.NOMBRES_PROCS[numero]
    else:
      titulo = 'Proceso ' + str_numero
    if num_procesos < 6:  # Hay pocos procesos, espacio de sobra
      pestanyas.addTab (titulo)
    else:
      pestanyas.addTab (str_numero)
      pestanyas.setTabToolTip (numero, titulo)
  paleta = QPalette (campo_txt.palette())
  paleta.setColor (QPalette.Base, color_base)              # Color de fondo gris oscuro
  paleta.setColor (QPalette.Text, QColor (255, 255, 255))  # Color de frente (para el cursor) blanco
  fuente = QFont ('Courier')  # Fuente que usaremos
  fuente.setStyleHint (QFont.TypeWriter)  # Como alternativa, usar una fuente monoespaciada
  campo_txt.setFont            (fuente)
  campo_txt.setPalette         (paleta)
  campo_txt.setUndoRedoEnabled (False)
  dlg_procesos.setLayout      (layout)
  dlg_procesos.setWindowTitle ('Tablas de proceso')
  mdi_procesos = selector.centralWidget().addSubWindow (dlg_procesos)
  mdi_procesos.setOption (QMdiSubWindow.RubberBandResize)
  dlg_procesos.showMaximized()

def muestraTextos (dialogo, listaTextos, tipoTextos, subventanaMdi):
  """Muestra uno de los diálogos para consultar los textos"""
  global dlg_desc_locs, dlg_desc_objs, dlg_msg_sys, dlg_msg_usr, mdi_desc_locs, mdi_desc_objs, mdi_msg_sys, mdi_msg_usr
  if dialogo:  # Diálogo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (subventanaMdi)
      return
    except RuntimeError:  # Diálogo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el diálogo
  selector.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
  dialogo = QTableView (selector)
  dialogo.horizontalHeader().setStretchLastSection(True)
  dialogo.setModel (ModeloTextos (dialogo, listaTextos))
  titulo = ('Mensaj' if tipoTextos[0] == 'm' else 'Descripcion') + 'es de ' + tipoTextos[5:]
  dialogo.setWindowTitle (titulo)
  subventanaMdi = selector.centralWidget().addSubWindow (dialogo)
  if tipoTextos == 'desc_localidades':
    dialogo.doubleClicked.connect (editaDescLoc)
    dlg_desc_locs = dialogo
    mdi_desc_locs = subventanaMdi
  elif tipoTextos == 'desc_objetos':
    dialogo.doubleClicked.connect (editaDescObj)
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
  selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def muestraVistaVocab ():
  """Muestra el diálogo para consultar el vocabulario"""
  global dlg_vocabulario, mdi_vocabulario
  if dlg_vocabulario:  # Diálogo ya creado
    try:
      selector.centralWidget().setActiveSubWindow (mdi_vocabulario)
      return
    except RuntimeError:  # Diálogo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el diálogo
  selector.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
  dlg_vocabulario = QTableView (selector)
  dlg_vocabulario.setModel (ModeloVocabulario (dlg_vocabulario))
  # dlg_vocabulario.setHorizontalHeaderLabels (('Palabra', 'Número', 'Tipo'))
  dlg_vocabulario.setWindowTitle ('Vocabulario')
  dlg_vocabulario.activated.connect     (nuevaFilaVocabulario)
  dlg_vocabulario.doubleClicked.connect (editaVocabulario)
  mdi_vocabulario = selector.centralWidget().addSubWindow (dlg_vocabulario)
  dlg_vocabulario.showMaximized()
  selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def nuevaBD (posicion):
  """Ejecuta la función de índice posicion para crear una nueva base de datos vacía"""
  global mod_actual
  selector.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
  mod_actual = __import__ (info_nueva[posicion][0])
  mod_actual.__dict__[info_nueva[posicion][1]]()
  postCarga ('Sin nombre')

def nuevaEntradaProceso (posicion):
  """Añade una entrada de proceso vacía en la posición dada como parámetro"""
  if posicion < 0:
    posicion = 0
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  proceso[0].insert (posicion, [255, 255])
  proceso[1].insert (posicion, [])
  cambiaProceso (numProceso, posicion)

def nuevaEntradaVocabulario (entrada, numFilaAntes = None):
  """Añade al vocabulario la entrada dada, en la posición que le corresponda"""
  # TODO: comprobar si ya existe otra palabra así y pedir confirmar en ese caso (pero permitirlo)
  pos = 0
  while pos < len (mod_actual.vocabulario) and mod_actual.cadena_es_mayor (entrada[0], mod_actual.vocabulario[pos][0]):
    pos += 1
  modeloVocab = dlg_vocabulario.model()
  if numFilaAntes:
    modeloVocab.beginRemoveRows (QModelIndex(), numFilaAntes, numFilaAntes)
    del mod_actual.vocabulario[numFilaAntes]
    modeloVocab.endRemoveRows()
  modeloVocab.beginInsertRows (QModelIndex(), pos, pos)
  mod_actual.vocabulario.insert (pos, entrada)
  modeloVocab.endInsertRows()

def nuevaFilaVocabulario (indice):
  """Permite añadir una entrada de vocabulario, tras pulsar Enter en la tabla"""
  try:
    if dlg_vocabulario.indiceDobleClick == indice:
      dlg_vocabulario.indiceDobleClick = None
      return  # Descartamos el evento por ocurrir tras un doble click anterior
  except:
    pass
  nuevaPal = []  # Entrada de vocabulario a añadir
  # Obtenemos el texto de la palabra
  dialogo = ModalEntrada (dlg_vocabulario, 'Texto de la palabra:', '')
  dialogo.setWindowTitle ('Añadir')
  if dialogo.exec_() != QDialog.Accepted:
    return
  nuevaPal.append (str (dialogo.textValue())[:mod_actual.LONGITUD_PAL].lower())
  # Obtenemos el código de la palabra
  dialogo = ModalEntrada (dlg_vocabulario, 'Código de la palabra:', '')
  dialogo.setInputMode   (QInputDialog.IntInput)
  dialogo.setIntRange    (0, 255)
  dialogo.setWindowTitle ('Añadir')
  if dialogo.exec_() != QDialog.Accepted:
    return
  nuevaPal.append (dialogo.intValue())
  # Obtenemos el tipo de la palabra
  tiposPalabra = {255: 'Reservado'}
  for i in range (len (mod_actual.TIPOS_PAL)):
    tiposPalabra[i] = mod_actual.TIPOS_PAL[i]
  dialogo = ModalEntrada (dlg_vocabulario, 'Tipo de palabra:', '')
  dialogo.setComboBoxEditable (True)
  dialogo.setComboBoxItems    (sorted (tiposPalabra.values()))
  dialogo.setWindowTitle      ('Añadir')
  if dialogo.exec_() != QDialog.Accepted or dialogo.textValue() not in tiposPalabra.values():
    return
  nuevaPal.append (list (tiposPalabra.keys())[list (tiposPalabra.values()).index (dialogo.textValue())])
  nuevaEntradaVocabulario (tuple (nuevaPal))

def quitaEntradaProceso (posicion):
  """Quita la entrada de proceso de la posición dada como parámetro"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  del proceso[0][posicion]
  del proceso[1][posicion]
  cambiaProceso (numProceso, max (0, posicion - 1))

def quitaEntradasProceso ():
  """Quita la entradas del proceso seleccionado"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  del proceso[0][:]
  del proceso[1][:]
  cambiaProceso (numProceso)

def postCarga (nombre):
  """Realiza las acciones convenientes tras la carga satisfactoria de una BD

  Recibe como parámetro el nombre de la base de datos"""
  global tipo_nombre, tipo_verbo
  # Apaño para que funcionen tal y como están las librerías con lista unificada de condactos
  # Lo hacemos aquí, porque la lista de condactos se puede extender tras cargar una BD
  if comprueba_nombre (mod_actual, 'condactos', dict) and (not comprueba_nombre (mod_actual, 'acciones', dict) or not mod_actual.acciones):
    for codigo in mod_actual.condactos:
      if mod_actual.condactos[codigo][2]:  # Es acción
        mod_actual.acciones[codigo] = mod_actual.condactos[codigo]
      else:  # Es condición
        mod_actual.condiciones[codigo] = mod_actual.condactos[codigo]
  # Cogemos la primera palabra de cada tipo y número como sinónimo preferido
  if 'Verbo' in mod_actual.TIPOS_PAL:
    tipo_nombre = mod_actual.TIPOS_PAL.index ('Nombre')
    tipo_verbo  = mod_actual.TIPOS_PAL.index ('Verbo')
  else:
    tipo_nombre = 0
    tipo_verbo  = 0
  for palabra, codigo, tipo in mod_actual.vocabulario:
    idYtipo = (codigo, tipo)
    # Preferiremos terminación en R para verbos (heurística para que sean en forma infinitiva)
    if idYtipo not in pal_sinonimo or \
        (tipo == tipo_verbo and palabra[-1] == 'r' and pal_sinonimo[idYtipo][-1] != 'r'):
      pal_sinonimo[idYtipo] = palabra
  # Preparamos las funciones de exportación
  for entrada in mod_actual.funcs_exportar:
    if comprueba_nombre (mod_actual, entrada[0], types.FunctionType):
      info_exportar.append ((entrada[0], entrada[1], entrada[2]))
  # Habilitamos las acciones que requieran tener una base de datos cargada
  accContadores.setEnabled (True)
  accDescLocs.setEnabled   (True)
  accDescObjs.setEnabled   (True)
  accDireccs.setEnabled    (True)
  accExportar.setEnabled   (len (info_exportar) > 0)
  accMostrarLoc.setEnabled (True)
  accMostrarObj.setEnabled (True)
  accMostrarRec.setEnabled (True)
  accMostrarSys.setEnabled (True)
  accMostrarUsr.setEnabled (True)
  accMsgSys.setEnabled     (True)
  accMsgUsr.setEnabled     (True)
  accPasoAPaso.setEnabled  (True)
  accTblProcs.setEnabled   (True)
  accTblVocab.setEnabled   (True)
  selector.setWindowTitle ('NAPS IDE - ' + nombre + ' (' + mod_actual.NOMBRE_SISTEMA + ')')
  selector.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal


if sys.version_info[0] < 3:
  import codecs
  reload (sys)  # Necesario para poder ejecutar sys.setdefaultencoding
  sys.stderr = codecs.getwriter (locale.getpreferredencoding()) (sys.stderr)  # Locale del sistema para la salida de error
  sys.stdout = codecs.getwriter (locale.getpreferredencoding()) (sys.stdout)  # Locale del sistema para la salida estándar
  sys.setdefaultencoding ('iso-8859-15')  # Nuestras cadenas están en esta codificación, no en ASCII
elif sys.version_info[1] < 4:  # Python 3.x < 3.4
  from imp import reload
else:  # Python > 3.3
  from importlib import reload

aplicacion = QApplication (sys.argv)

creaSelector()
selector.showMaximized()
cargaInfoModulos()

argsParser = argparse.ArgumentParser (sys.argv[0], description = 'Entorno de Desarrollo Integrado para Quill/PAWS/SWAN/DAAD en Python')
argsParser.add_argument ('-ne', '--no-entry-end', action = 'store_true', help = 'omitir condactos en entradas de proceso detrás de los que cambian el flujo de ejecución incondicionalmente')
argsParser.add_argument ('-r', '--run', action = 'store_true', help = 'ejecutar base_de_datos por pasos directamente')
argsParser.add_argument ('bbdd',     metavar = 'base_de_datos',         nargs = '?', help = 'base de datos de Quill/PAWS/SWAN/DAAD a ejecutar')
argsParser.add_argument ('graficos', metavar = 'bd_o_carpeta_gráficos', nargs = '?', help = 'base de datos gráfica o carpeta de la que tomar las imágenes (con nombre pic###.png)')
args = argsParser.parse_args()

if args.bbdd:
  if args.graficos and not os.path.exists (args.graficos):
    muestraFallo ('Ruta inexistente',
                  'No existe ningún fichero ni carpeta con la ruta dada desde la línea de comandos para gráficos:\n\n' + (args.graficos.decode ('utf8') if sys.version_info[0] < 3 else args.graficos))
    args.graficos = None
  if args.graficos:
    todoBien = importaBD (args.bbdd, nombreFicheroGfx = args.graficos)
  else:
    todoBien = importaBD (args.bbdd)
  if todoBien and args.run:
    ejecutaPorPasos()

sys.exit (aplicacion.exec_())
