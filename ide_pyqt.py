#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Entorno de desarrollo integrado (IDE), hecho con PyQt4
# Copyright (C) 2010, 2018-2022 Jos� Manuel Ferrer Ortiz
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

from prn_func import prn

import codecs
import locale
import os          # Para curdir, listdir y path
import subprocess  # Para ejecutar el int�rprete
import sys
import types       # Para poder comprobar si algo es una funci�n

try:
  from aPyQt4.QtCore import *
  from PyQt4.QtGui  import *
  vers_pyqt = 4
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtGui     import *
  from PyQt5.QtWidgets import *
  vers_pyqt = 5


# TODO: Hacerlo internacionalizable:
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qcoreapplication.html#translate


dlg_abrir       = None  # Di�logo de abrir fichero
dlg_acerca_de   = None  # Di�logo "Acerca de"
dlg_contadores  = None  # Di�logo de contadores
dlg_guardar     = None  # Di�logo de guardar fichero
dlg_fallo       = None  # Di�logo para mostrar fallos leves
dlg_msg_sys     = None  # Di�logo para consultar los mensajes de sistema
dlg_msg_usr     = None  # Di�logo para consultar los mensajes de usuario
dlg_procesos    = None  # Di�logo para consultar y modificar las tablas de proceso
dlg_vista_vocab = None  # Di�logo para consultar el vocabulario

campo_txt = None  # El campo de texto    del di�logo de procesos
pestanyas = None  # La barra de pesta�as del di�logo de procesos

mod_actual   = None    # M�dulo de librer�a activo
pal_sinonimo = dict()  # Sin�nimos preferidos para cada par c�digo y tipo v�lido

color_base      = QColor (10, 10, 10)   # Color de fondo gris oscuro
color_pila      = QColor (60, 35, 110)  # Color de fondo azul brillante
color_tope_pila = QColor (35, 40, 110)  # Color de fondo morado oscuro
pila_procs      = []    # Pila con estado de los procesos en ejecuci�n
proc_interprete = None  # Proceso del int�rprete


# Funciones de exportaci�n e importaci�n, con sus m�dulos, extensiones y descripciones
info_exportar = []
info_importar = []
# Funciones de nueva base de datos, con sus m�dulos
info_nueva = []

# Pares nombre y tipos posibles que deben tener los m�dulos de librer�a
nombres_necesarios = (('acciones',       dict),
                      ('condiciones',    dict),
                      ('func_nueva',     str),
                      ('funcs_exportar', tuple),
                      ('funcs_importar', tuple),
                      ('INDIRECCION',    bool),
                      ('msgs_sys',       list),
                      ('msgs_usr',       list),
                      ('NOMBRE_SISTEMA', str),
                      ('tablas_proceso', list),
                      ('TIPOS_PAL',      tuple),
                      ('vocabulario',    list))


class CampoTexto (QTextEdit):
  """Campo de texto para las tablas de proceso"""
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

  def contextMenuEvent (self, evento):
    linea      = self.cursorForPosition (evento.pos()).block()
    numEntrada = self._daNumEntradaYLinea (linea)[0]
    # prn ('N� l�nea:', linea.blockNumber())
    # prn ('N� entrada guardado en la l�nea:', linea.userState())
    # prn ('N� entrada guardado en cabecera:', cabecera.userState())
    # prn ('Texto de la l�nea:', linea.text())
    contextual   = self.createStandardContextMenu()
    menuEliminar = QMenu ('Eliminar', contextual)
    accionAntes    = QAction ('A�adir entrada &antes',   contextual)
    accionDespues  = QAction ('A�adir entrada &despu�s', contextual)
    accionElimEnt  = QAction ('Esta entrada',       selector)  # Necesario poner como padre selector...
    accionElimTodo = QAction ('Todas las entradas', selector)  # ... para que funcionen los status tips
    if numEntrada == -1:
      accionElimEnt.setEnabled (False)
    accionElimTodo.setStatusTip ('Elimina todas las entradas del proceso')
    accionElimEnt.triggered.connect  (lambda: quitaEntrada (numEntrada))
    accionElimTodo.triggered.connect (quitaEntradas)
    accionAntes.triggered.connect    (lambda: nuevaEntrada (numEntrada))
    accionDespues.triggered.connect  (lambda: nuevaEntrada (numEntrada + 1))
    menuEliminar.addAction (accionElimEnt)
    menuEliminar.addAction (accionElimTodo)
    contextual.addSeparator()
    contextual.addAction (accionAntes)
    contextual.addAction (accionDespues)
    contextual.addMenu (menuEliminar)
    contextual.exec_ (evento.globalPos())

  def keyPressEvent (self, evento):
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
        columna     = cursor.positionInBlock()
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
    elif evento.key() == Qt.Key_Insert:
      if self.overwriteMode():
        self.setCursorWidth   (1)
        self.setOverwriteMode (False)
      else:
        self.setCursorWidth   (self.font().pointSize() * 0.7)
        self.setOverwriteMode (True)
    elif proc_interprete:
      return  # No se puede modificar nada cuando la BD est� en ejecuci�n
    elif str (evento.text()).isalpha():  # Letras
      cursor  = self.textCursor()
      columna = cursor.positionInBlock()
      linea   = cursor.block()
      colsValidas = self._daColsValidas (linea.text())
      if columna not in (colsValidas[0], colsValidas[-1]):
        return  # Intentando escribir texto donde no es posible
      if linea.text() and linea.userState() == -1:  # Una l�nea de entrada que no es la cabecera
        numEntrada, posicion = self._daNumEntradaYLinea (linea)
        try:
          self.condactos
        except:
          self.condactos       = {}  # Informaci�n completa de los condactos indexada por nombre
          self.condactosPorCod = {}  # Nombre de condactos indexado por c�digo
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
        combo = dialogo.findChild (QComboBox)
        if dialogo.exec_() == QDialog.Accepted:
          nomCondacto = str (dialogo.textValue()).upper()
          if nomCondacto in self.condactos:
            condacto   = self.condactos[nomCondacto]
            lineaNueva = [condacto[3], [0] * condacto[1]]  # C�digo y par�metros de la nueva l�nea
            if posicion > 1:  # Si no a�ade al inicio de la entrada
              if self.overwriteMode():
                cursor.movePosition (QTextCursor.EndOfBlock)
                cursor.movePosition (QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                cursor.movePosition (QTextCursor.Left,         QTextCursor.KeepAnchor)
                parametros    = entrada[posicion - 2][1]  # Conservaremos par�metros anteriores
                lineaNueva[1] = parametros[: condacto[1]] + ([0] * (max (0, condacto[1] - len (parametros))))
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
      colsValidas = self._daColsValidas (linea.text())
      if columna in (colsValidas[0], colsValidas[-1]) or linea.text()[columna - 1] == '"':
        return  # Intentando escribir n�mero donde no es posible
      numParam  = colsValidas.index (columna)
      parametro = str (linea.text()[columna:])
      if ',' in parametro:
        parametro = parametro[: parametro.find (',')]
      dialogo = ModalEntrada (self, 'Valor del par�metro:', evento.text(), parametro)
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

  def mousePressEvent (self, evento):
    if evento.button() & Qt.LeftButton or evento.button() & Qt.RightButton:
      cursor      = self.cursorForPosition (evento.pos())
      bloque      = cursor.block()
      columna     = cursor.positionInBlock()
      textoLinea  = bloque.text()
      colsValidas = self._daColsValidas (textoLinea)
      if columna not in colsValidas:
        # Buscamos la columna v�lida m�s cercana
        for c in range (len (colsValidas)):
          if colsValidas[c] < columna:
            continue
          if c:  # No es la primera
            # Nos quedamos con la m�s cercana de entre la de la posici�n actual y la anterior
            if abs (columna - colsValidas[c]) > abs (columna - colsValidas[c - 1]):
              colNueva = colsValidas[c - 1]
            else:
              colNueva = colsValidas[c]
          else:  # Es la primera
            colNueva = colsValidas[c]
          break
        cursor.setPosition (cursor.position() + (colNueva - columna))
      self.setTextCursor (cursor)
      if evento.button() & Qt.LeftButton:
        return
    super (CampoTexto, self).mousePressEvent (evento)

  def wheelEvent (self, evento):
    if evento.modifiers() & Qt.ControlModifier:
      if (evento.delta() if vers_pyqt < 5 else evento.angleDelta().y()) < 0:
        self.zoomOut (2)
      else:
        self.zoomIn (2)
      if self.overwriteMode():
        self.setCursorWidth (self.font().pointSize() * 0.75)
    else:
      super (CampoTexto, self).wheelEvent (evento)

class ManejoInterprete (QThread):
  """Maneja la comunicaci�n con el int�rprete ejecutando la base de datos"""
  cambiaPila = pyqtSignal (list)

  def __init__ (self, procInterprete, padre):
    QThread.__init__ (self, parent = padre)
    self.procInterprete = procInterprete

  def run (self):
    """Lee del proceso del int�rprete, obteniendo por d�nde va la ejecuci�n"""
    global proc_interprete
    if sys.version_info[0] < 3:
      inicioLista = '['
      finLista    = ']'
    else:
      inicioLista = ord ('[')
      finLista    = ord (']')
    pilaProcs = []
    while True:
      linea = self.procInterprete.stdout.readline()
      if not linea:
        break  # Ocurre cuando el proceso ha terminado
      if linea[0] == inicioLista and finLista in linea:
        pilaProcs = eval (linea)
        self.cambiaPila.emit (pilaProcs)
    accPasoAPaso.setEnabled (True)
    proc_interprete = None
    if pilaProcs:
      ultimaEntrada = [pilaProcs[-1][0]]
      if len (pilaProcs[-1]) > 1:
        ultimaEntrada.extend ([pilaProcs[-1][1], -2])
      self.cambiaPila.emit ([ultimaEntrada])

class ModalEntrada (QInputDialog):
  """Modal de entrada QInputDialog con el primer car�cter ya introducido, para continuar en siguiente pulsaci�n sin machacarlo"""
  def __init__ (self, parent, etiqueta, textoInicial, textoOriginal = ''):
    QInputDialog.__init__ (self, parent)
    self.textoInicial  = textoInicial
    self.textoOriginal = textoOriginal
    self.setLabelText (etiqueta)
    self.setWindowTitle ('Modal')
    # Si los descomento, no funciona la introducci�n del valor inicial
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

class ModeloMensajes (QAbstractTableModel):
  """Modelo para las tablas de mensajes"""
  def __init__ (self, parent, listaMensajes):
    QAbstractTableModel.__init__ (self, parent)
    self.listaMensajes = listaMensajes

  def columnCount (self, parent):
    return 1

  def data (self, index, role):
    if role == Qt.DisplayRole:
      return self.listaMensajes[index.row()]

  def flags (self, index):
    return Qt.ItemIsSelectable | Qt.ItemIsEnabled

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return 'Texto del mensaje'
    if orientation == Qt.Vertical and role == Qt.DisplayRole:
      return section  # Cuenta el n�mero de mensaje desde 0
    return QAbstractTableModel.headerData(self, section, orientation, role)

  def rowCount (self, parent):
    return len (self.listaMensajes)

class ModeloVocabulario (QAbstractTableModel):
  """Modelo para la tabla de vocabulario"""
  def __init__ (self, parent):
    QAbstractTableModel.__init__ (self, parent)
    self.tituloCols = ('Palabra', 'C�digo', 'Tipo')
    self.tipos      = mod_actual.TIPOS_PAL

  def columnCount (self, parent):
    return 3

  def data (self, index, role):
    if role == Qt.DisplayRole:
      if index.column() == 0:
        return mod_actual.vocabulario[index.row()][0]  # Palabra
      if index.column() == 1:
        return mod_actual.vocabulario[index.row()][1]  # C�digo
      # Si llega aqu�, es la tercera columna: el tipo
      tipo = mod_actual.vocabulario[index.row()][2]
      if tipo == 255:
        return 'Reservado'
      if tipo > len (self.tipos):
        return 'Desconocido (' + str (tipo) + ')'
      return self.tipos[tipo]

  def flags (self, index):
    return Qt.ItemIsSelectable | Qt.ItemIsEnabled

  def headerData (self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.tituloCols[section]
    return QAbstractTableModel.headerData(self, section, orientation, role)

  def rowCount (self, parent):
    return len (mod_actual.vocabulario)


def actualizaPosProcesos (pilaProcs):
  """Refleja la posici�n de ejecuci�n paso a paso actual en el di�logo de tablas de proceso"""
  global pila_procs
  pila_procs = pilaProcs
  muestraProcesos()
  if pestanyas.currentIndex() == pilaProcs[-1][0]:
    cambiaProceso (pilaProcs[-1][0], pilaProcs[-1][1] if len (pilaProcs[-1]) > 1 else None)
  else:
    pestanyas.setCurrentIndex (pilaProcs[-1][0])

# FIXME: Diferencias entre PAWS est�ndar y DAAD
def cambiaProceso (numero, numEntrada = None):
  """Llamada al cambiar de pesta�a en el di�logo de procesos"""
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  proceso   = mod_actual.tablas_proceso[numero]  # El proceso seleccionado
  cabeceras = proceso[0]  # Las cabeceras del proceso seleccionado
  entradas  = proceso[1]  # Las entradas del proceso seleccionado
  noExisten = []
  posicion  = None  # Posici�n donde ir al terminar de cargar el contenido del proceso
  campo_txt.clear()  # Borramos el texto anterior
  for i in range (len (cabeceras)):
    if i == numEntrada:
      posicion = campo_txt.textCursor().position()
    if [numero, i, -1] in pila_procs:
      campo_txt.setTextBackgroundColor (color_tope_pila if pila_procs[-1] == [numero, i, -1] else color_pila)
    else:
      campo_txt.setTextBackgroundColor (color_base)
    campo_txt.setTextColor (QColor (200, 200, 200))  # Color gris claro
    campo_txt.setFontItalic (True)  # Cursiva activada
    verbo = cabeceras[i][0]  # C�digo del verbo (de esta cabecera)
    if verbo == 255:
      campo_txt.insertPlainText ('  _  ')
    elif verbo == 1 and (1, 255) in pal_sinonimo:
      campo_txt.insertPlainText ('  *  ')
    elif (verbo, 0) in pal_sinonimo:  # Hay un verbo con ese c�digo
      campo_txt.insertPlainText (pal_sinonimo[(verbo, 0)].center (5))
    elif verbo < 20 and (verbo, 2) in pal_sinonimo:  # Es un nombre convertible en verbo
      campo_txt.insertPlainText (pal_sinonimo[(verbo, 2)].center (5))
    else:
      campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
      if (verbo, 0) not in noExisten:
        muestraFallo ('Verbo no existente', 'Verbo de c�digo ' + str (verbo) + ' no encontrado en el vocabulario')
        noExisten.append ((verbo, 0))
      campo_txt.insertPlainText (str (verbo).center (5))
      campo_txt.setTextColor (QColor (200, 200, 200))  # Color gris claro
    campo_txt.insertPlainText ('  ')
    nombre = cabeceras[i][1]  # C�digo del nombre (de esta cabecera)
    if nombre == 255:
      campo_txt.insertPlainText ('  _')
    elif nombre == 1 and (1, 255) in pal_sinonimo:
      campo_txt.insertPlainText ('  *')
    elif (nombre, 2) in pal_sinonimo:
      campo_txt.insertPlainText (pal_sinonimo[(nombre, 2)].center (5).rstrip())
    else:
      campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
      if (nombre, 2) not in noExisten:
        muestraFallo ('Nombre no existente', 'Nombre de c�digo ' + str (nombre) + ' no encontrado en el vocabulario')
        noExisten.append ((nombre, 2))
      campo_txt.insertPlainText (str (nombre).center (5).rstrip())
    campo_txt.setFontItalic (False)  # Cursiva desactivada
    campo_txt.setTextBackgroundColor (color_base)
    campo_txt.textCursor().block().setUserState (i)  # Guardamos el n�mero de la entrada
    campo_txt.insertPlainText ('\n     ')
    for c in range (len (entradas[i])):
      condacto, parametros = entradas[i][c]
      if [numero, i, c] in pila_procs:
        campo_txt.setTextBackgroundColor (color_tope_pila if pila_procs[-1] == [numero, i, c] else color_pila)
      imprimeCondacto (condacto, parametros)
      campo_txt.setTextBackgroundColor (color_base)
    campo_txt.insertPlainText ('\n     ')
    if i < (len (cabeceras) - 1):
      campo_txt.insertPlainText ('\n\n')
  if posicion != None:
    campo_txt.moveCursor (QTextCursor.End)  # Vamos al final, para que al ir a la l�nea que toca, esa quede arriba
    cursor = campo_txt.textCursor()
    cursor.setPosition  (posicion)
    cursor.movePosition (QTextCursor.Right, n = 2)
    campo_txt.setTextCursor (cursor)
  else:
    campo_txt.moveCursor (QTextCursor.Start)  # Movemos el cursor al principio
  selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def cargaInfoModulos ():
  """Carga la informaci�n de los m�dulos de librer�a v�lidos que encuentre en el directorio"""
  # TODO: Informar de los errores
  # TODO: No permitir entradas con igual conjunto de extensiones y descripci�n,
  # pero distinta funci�n a llamar (aunque sean de m�dulos distintos)
  # Nombres de los m�dulos de librer�a en el directorio
  nombres = [f[:-3] for f in os.listdir (os.curdir)
             if (f[:9] == 'libreria_' and f[-3:] == '.py')]
  for nombre_modulo in nombres:
    try:
      modulo = __import__ (nombre_modulo)
    except SyntaxError as excepcion:
      prn ('Error al importar el m�dulo:', excepcion)
      continue
    # Apa�o para que funcione las librer�as de DAAD y SWAN tal y como est�n (con lista unificada de condactos)
    if compruebaNombre (modulo, 'condactos', dict):
      modulo.acciones    = {}
      modulo.condiciones = {}
    # Comprobamos que el m�dulo tenga todos los nombres necesarios
    for nombre, tipo in nombres_necesarios:
      if not compruebaNombre (modulo, nombre, tipo):
        modulo = None  # M�dulo de librer�a inv�lido, lo liberamos
        break
    if modulo == None:
      continue
    for entrada in modulo.funcs_importar:
      if compruebaNombre (modulo, entrada[0], types.FunctionType):
        info_importar.append ((nombre_modulo, entrada[0], entrada[1], entrada[2]))
    if compruebaNombre (modulo, modulo.func_nueva, types.FunctionType):
      info_nueva.append ((nombre_modulo, modulo.func_nueva))
      accion = QAction ('Base de datos ' + modulo.NOMBRE_SISTEMA, menuBDNueva)
      accion.setStatusTip ('Crea una nueva base de datos de ' + modulo.NOMBRE_SISTEMA)
      accion.triggered.connect (lambda: nuevaBD (len (info_nueva) - 1))
      menuBDNueva.addAction (accion)
    del modulo
  # Actualizamos las distintas acciones y men�s, seg�n corresponda
  accExportar.setEnabled (False)
  accImportar.setEnabled (len (info_importar) > 0)
  menuBDNueva.setEnabled (len (info_nueva) > 0)

def compruebaNombre (modulo, nombre, tipo):
  """Devuelve True si un nombre est� en un m�dulo, y es del tipo correcto"""
  if (nombre in modulo.__dict__) and (type (modulo.__dict__[nombre]) == tipo):
    return True
  return False

def creaAcciones ():
  """Crea las acciones de men� y barra de botones"""
  global accAcercaDe, accContadores, accDireccs, accExportar, accImportar, accMsgSys, \
         accMsgUsr, accPasoAPaso, accSalir, accTblProcs, accTblVocab
  accAcercaDe   = QAction (icono_ide, '&Acerca de NAPS IDE', selector)
  accContadores = QAction (icono ('contadores'), '&Contadores', selector)
  accDireccs    = QAction (icono ('direccion'), '&Direcciones', selector)
  accExportar   = QAction (icono ('exportar'), '&Exportar', selector)
  accImportar   = QAction (icono ('importar'), '&Importar', selector)
  accMsgSys     = QAction (icono ('msg_sistema'), '&Sistema', selector)
  accMsgUsr     = QAction (icono ('msg_usuario'), '&Usuario', selector)
  accPasoAPaso  = QAction (icono ('pasoapaso'), '&Paso a paso', selector)
  accSalir      = QAction (icono ('salir'), '&Salir', selector)
  accTblProcs   = QAction (icono ('proceso'), '&Tablas', selector)
  accTblVocab   = QAction (icono ('vocabulario'), '&Tabla', selector)
  accContadores.setEnabled (False)
  accDireccs.setEnabled    (False)
  accMsgSys.setEnabled     (False)
  accMsgUsr.setEnabled     (False)
  accPasoAPaso.setEnabled  (False)
  accTblProcs.setEnabled   (False)
  accTblVocab.setEnabled   (False)
  accSalir.setShortcut ('Ctrl+Q')
  accAcercaDe.setStatusTip   ('Muestra informaci�n del programa')
  accContadores.setStatusTip ('Muestra el n�mero de elementos de cada tipo')
  accDireccs.setStatusTip    ('Permite a�adir y editar las palabras de direcci�n')
  accExportar.setStatusTip   ('Exporta la base de datos a un fichero')
  accImportar.setStatusTip   ('Importa una base de datos desde un fichero')
  accMsgSys.setStatusTip     ('Permite consultar los mensajes de sistema')
  accMsgUsr.setStatusTip     ('Permite consultar los mensajes de usuario')
  accPasoAPaso.setStatusTip  ('Depura la base de datos ejecut�ndola paso a paso')
  accSalir.setStatusTip      ('Sale de la aplicaci�n')
  accTblProcs.setStatusTip   ('Permite consultar las tablas de proceso')
  accTblVocab.setStatusTip   ('Permite consultar el vocabulario')
  accTblProcs.setToolTip ('Tablas de proceso')
  accTblVocab.setToolTip ('Tabla de vocabulario')
  accAcercaDe.triggered.connect   (muestraAcercaDe)
  accContadores.triggered.connect (muestraContadores)
  accExportar.triggered.connect   (exportaBD)
  accImportar.triggered.connect   (dialogoImportaBD)
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
  barraBotones.setIconSize (QSize (16, 16))

def creaMenus ():
  """Crea y organiza los men�s"""
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
  menuEjecutar = selector.menuBar().addMenu ('&Ejecutar')
  menuEjecutar.addAction (accPasoAPaso)
  menuMensajes = selector.menuBar().addMenu ('&Mensajes')
  menuMensajes.addAction (accMsgSys)
  menuMensajes.addAction (accMsgUsr)
  menuProcesos = selector.menuBar().addMenu ('&Procesos')
  menuProcesos.addAction (accTblProcs)
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

def dialogoImportaBD ():
  """Deja al usuario elegir un fichero de base datos, y lo intenta importar"""
  global dlg_abrir
  filtro = []
  for modulo, funcion, extensiones, descripcion in info_importar:
    filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
  if not dlg_abrir:  # Di�logo no creado a�n
    dlg_abrir = QFileDialog (selector, 'Importar base de datos', os.curdir, ';;'.join (sorted (filtro)))
    dlg_abrir.setFileMode  (QFileDialog.ExistingFile)
    dlg_abrir.setLabelText (QFileDialog.LookIn,   'Lugares')
    dlg_abrir.setLabelText (QFileDialog.FileName, '&Nombre:')
    dlg_abrir.setLabelText (QFileDialog.FileType, 'Filtro:')
    dlg_abrir.setLabelText (QFileDialog.Accept,   '&Abrir')
    dlg_abrir.setLabelText (QFileDialog.Reject,   '&Cancelar')
  if dlg_abrir.exec_():  # No se ha cancelado
    selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
    nombreFichero = str (dlg_abrir.selectedFiles()[0])
    importaBD (nombreFichero)
    selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def ejecutaPorPasos ():
  """Ejecuta la base de datos para depuraci�n paso a paso"""
  global proc_interprete
  accPasoAPaso.setEnabled (False)
  rutaInterprete = os.curdir + '/interprete.py'
  argumentos     = ['python', rutaInterprete, '--ide', nombre_fich_bd]
  if nombre_fich_gfx:
    argumentos.append (nombre_fich_gfx)
  devnull = open (os.devnull, 'w')
  proc_interprete = subprocess.Popen (argumentos, stdout = subprocess.PIPE, stderr = devnull)
  hilo = ManejoInterprete (proc_interprete, aplicacion)
  hilo.cambiaPila.connect (actualizaPosProcesos)
  hilo.start()

def exportaBD ():
  """Exporta la base de datos a fichero"""
  global dlg_guardar, mod_actual
  if not dlg_guardar:  # Di�logo no creado a�n
    filtro = []
    for funcion, extensiones, descripcion in info_exportar:
      filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
    dlg_guardar = QFileDialog (selector, 'Exportar base de datos', os.curdir,
        ';;'.join (filtro))
    dlg_guardar.setAcceptMode (QFileDialog.AcceptSave)
    dlg_guardar.setLabelText (QFileDialog.LookIn,   'Lugares')
    dlg_guardar.setLabelText (QFileDialog.FileName, '&Nombre:')
    dlg_guardar.setLabelText (QFileDialog.FileType, 'Filtro:')
    dlg_guardar.setLabelText (QFileDialog.Accept,   '&Guardar')
    dlg_guardar.setLabelText (QFileDialog.Reject,   '&Cancelar')
    dlg_guardar.setOption (QFileDialog.DontConfirmOverwrite)
  if dlg_guardar.exec_():  # No se ha cancelado
    indiceFiltro  = dlg_guardar.filters().indexOf (dlg_guardar.selectedFilter())
    nombreFichero = str (dlg_guardar.selectedFiles()[0])
    extension     = '.' + info_exportar[indiceFiltro][1][0]
    if extension not in nombreFichero:
      nombreFichero += extension
    if os.path.isfile (nombreFichero):
      dlgSiNo = QMessageBox (selector)
      dlgSiNo.addButton ('&S�', QMessageBox.YesRole)
      dlgSiNo.addButton ('&No', QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle ('Sobreescritura')
      dlgSiNo.setText ('Ya existe un fichero con ruta y nombre:\n\n' + nombreFichero)
      dlgSiNo.setInformativeText ('\n�Quieres sobreescribirlo?')
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el bot�n S�
        return
    selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
    try:
      fichero = open (nombreFichero, 'w')
    except IOError as excepcion:
      muestraFallo ('No se puede abrir el fichero:\n' + nombreFichero,
                    'Causa:\n' + excepcion.args[1])
      selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
      return
    mod_actual.__dict__[info_exportar[indiceFiltro][0]] (fichero)
    fichero.close()
    selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def icono (nombre):
  """Devuelve un QIcon, sacando la imagen de la carpeta de iconos"""
  return QIcon (os.path.join ('iconos_ide', nombre + '.png'))

def importaBD (nombreFicheroBD, nombreFicheroGfx = None):
  """Importa una base de datos desde el fichero de nombre dado"""
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
                  'Causa:\nNo tiene extensi�n')
    return
  extension = nombreFicheroBD[nombreFicheroBD.rindex ('.') + 1 :].lower()
  for modulo, funcion, extensiones, descripcion in info_importar:
    if extension in extensiones:
      mod_actual = __import__ (modulo)
      break
  else:
    muestraFallo ('No se puede importar una base datos de:\n' + nombreFicheroBD,
                  'Causa:\nExtensi�n no reconocida')
    return
  # Damos acceso al m�dulo a funciones del IDE
  mod_actual.muestraFallo = muestraFallo
  # Solicitamos la importaci�n
  if mod_actual.__dict__[funcion] (fichero, os.path.getsize (nombreFicheroBD)) == False:
    muestraFallo ('No se puede importar una base datos de:\n' +
                  nombreFicheroBD, 'Causa:\nFormato de fichero incompatible o base de datos corrupta')
    mod_actual = None
    return
  fichero.close()
  nombre_fich_bd  = nombreFicheroBD
  nombre_fich_gfx = nombreFicheroGfx
  postCarga (os.path.basename (nombreFicheroBD))

def imprimeCondacto (condacto, parametros):
  campo_txt.insertPlainText ('\n  ')
  if condacto > 127 and mod_actual.INDIRECCION:  # Condacto indirecto
    condacto -= 128
    indirecto = '@'  # Condacto indirecto
  else:
    indirecto = ' '  # Condacto no indirecto
  if condacto in mod_actual.acciones:
    campo_txt.setTextColor (QColor (100, 200, 255))  # Color azul claro
    nombre = mod_actual.acciones[condacto][0]
    if nombre == 'NEWTEXT' and indirecto == '@':
      indirecto = ' '
      nombre    = 'DEBUG'
  elif condacto in mod_actual.condiciones:
    campo_txt.setTextColor (QColor (100, 255, 50))  # Color verde claro
    nombre = mod_actual.condiciones[condacto][0]
  else:  # No deber�a ocurrir
    prn ('FIXME: Condacto', condacto, 'no reconocido por la librer�a')
    campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    nombre = str (condacto)
  if parametros:  # Imprimiremos los par�metros
    campo_txt.insertPlainText (nombre.center (7))
    campo_txt.setTextColor (QColor (255, 160, 32))  # Color anaranjado
    if indirecto == ' ' and nombre in ('MES', 'MESSAGE', 'SYSMESS'):
      if (nombre == 'SYSMESS' and parametros[0] >= len (mod_actual.msgs_sys)) or \
         (nombre != 'SYSMESS' and parametros[0] >= len (mod_actual.msgs_usr)):
        campo_txt.setTextColor (QColor (255, 0, 0))  # Color rojo
    campo_txt.insertPlainText ((indirecto + str (parametros[0])).rjust (5))
    for parametro in parametros[1:]:
      campo_txt.insertPlainText (',' + str (parametro).rjust (4))
  else:  # Condacto sin par�metros
    campo_txt.insertPlainText ((nombre + indirecto).center (7).rstrip())
  if indirecto == ' ' and nombre in ('MES', 'MESSAGE', 'SYSMESS'):
    if nombre == 'SYSMESS' and parametros[0] < len (mod_actual.msgs_sys):
      mensaje = mod_actual.msgs_sys[parametros[0]]
    elif nombre != 'SYSMESS' and parametros[0] < len (mod_actual.msgs_usr):
      mensaje = mod_actual.msgs_usr[parametros[0]]
    else:
      return
    # TODO: que la librer�a proporcione informaci�n sobre secuencias de escape
    if mod_actual.NOMBRE_SISTEMA == 'DAAD' and mod_actual.nueva_version:
      mensaje = mensaje.replace ('\x0b', '\\b').replace ('\x0c', '\\k')
    mensaje = mensaje.replace ('\n', '\\n')
    campo_txt.setTextColor (QColor (100, 100, 100))  # Color gris oscuro
    campo_txt.insertPlainText ('       "')
    campo_txt.setFontItalic (True)  # Cursiva activada
    campo_txt.insertPlainText (str (mensaje))
    campo_txt.setFontItalic (False)  # Cursiva desactivada
    campo_txt.insertPlainText ('"')

def muestraAcercaDe ():
  """Muestra el di�logo 'Acerca de'"""
  global dlg_acerca_de
  if not dlg_acerca_de:  # Di�logo no creado a�n
    # Cogeremos s�lo los n�meros de la versi�n de Python
    fin = sys.version.find (' (')
    dlg_acerca_de = QMessageBox (selector)
    dlg_acerca_de.addButton ('&Aceptar', QMessageBox.AcceptRole)
    dlg_acerca_de.setIconPixmap (icono_ide.pixmap (96))
    dlg_acerca_de.setText ('NAPS: The New Age PAW-like System\n' +
        'Entorno de desarrollo integrado (IDE)\n' +
        'Copyright � 2010, 2018-2022 Jos� Manuel Ferrer Ortiz')
    dlg_acerca_de.setInformativeText ('Versi�n de PyQt: ' +
        PYQT_VERSION_STR + '\nVersi�n de Qt: ' + QT_VERSION_STR +
        '\nVersi�n de Python: ' + sys.version[:fin])
    dlg_acerca_de.setWindowTitle ('Acerca de NAPS IDE')
  dlg_acerca_de.exec_()

def muestraContadores ():
  """Muestra el di�logo de contadores"""
  global dlg_contadores
  if not dlg_contadores:  # Di�logo no creado a�n
    dlg_contadores = QMessageBox (selector)
    dlg_contadores.addButton ('&Aceptar', QMessageBox.AcceptRole)
    num_palabras = len (mod_actual.vocabulario)
    dlg_contadores.setText ('Procesos: ' + str (len (mod_actual.tablas_proceso))
      + ' tablas\nVocabulario: ' + str (num_palabras) + ' palabra' + \
      ('s' * (num_palabras > 1)))
    dlg_contadores.setWindowTitle ('Contadores')
  dlg_contadores.exec_()

def muestraFallo (mensaje, detalle):
  """Muestra un di�logo de fallo leve"""
  global dlg_fallo
  if not dlg_fallo:  # Di�logo no creado a�n
    dlg_fallo = QMessageBox (selector)
    dlg_fallo.addButton ('&Aceptar', QMessageBox.AcceptRole)
    dlg_fallo.setIcon (QMessageBox.Warning)
    dlg_fallo.setWindowTitle ('Fallo')
  dlg_fallo.setText (mensaje)
  dlg_fallo.setInformativeText (detalle)
  dlg_fallo.exec_()

def muestraMensajes (dialogo, listaMensajes, tipoMensajes):
  """Muestra uno de los di�logos para consultar los mensajes"""
  global dlg_msg_sys, dlg_msg_usr
  if dialogo:  # Di�logo ya creado
    try:
      dialogo.showMaximized()
      return
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  dialogo = QTableView (selector)
  dialogo.horizontalHeader().setStretchLastSection(True)
  dialogo.setModel (ModeloMensajes (dialogo, listaMensajes))
  dialogo.setWindowTitle ('Mensajes de ' + tipoMensajes)
  selector.centralWidget().addSubWindow (dialogo)
  dialogo.showMaximized()
  selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal
  if tipoMensajes == 'sistema':
    dlg_msg_sys = dialogo
  else:
    dlg_msg_usr = dialogo

def muestraMsgSys ():
  """Muestra el di�logo para consultar los mensajes de sistema"""
  muestraMensajes (dlg_msg_sys, mod_actual.msgs_sys, 'sistema')

def muestraMsgUsr ():
  """Muestra el di�logo para consultar los mensajes de usuario"""
  muestraMensajes (dlg_msg_usr, mod_actual.msgs_usr, 'usuario')

def muestraProcesos ():
  """Muestra el di�logo para las tablas de proceso"""
  global campo_txt, dlg_procesos, pestanyas
  if dlg_procesos:  # Di�logo ya creado
    try:
      dlg_procesos.showMaximized()
      return
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
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
    if num_procesos < 5:  # Hay pocos procesos, espacio de sobra
      pestanyas.addTab (titulo)
    else:
      pestanyas.addTab (str_numero)
      pestanyas.setTabToolTip (numero, titulo)
  paleta = QPalette (campo_txt.palette())
  paleta.setColor (QPalette.Base, color_base)              # Color de fondo gris oscuro
  paleta.setColor (QPalette.Text, QColor (255, 255, 255))  # Color de frente (para el cursor) blanco
  campo_txt.setFont            (QFont ('Courier'))  # Fuente que usaremos
  campo_txt.setPalette         (paleta)
  campo_txt.setUndoRedoEnabled (False)
  dlg_procesos.setLayout      (layout)
  dlg_procesos.setWindowTitle ('Tablas de proceso')
  selector.centralWidget().addSubWindow (dlg_procesos)
  dlg_procesos.showMaximized()

def muestraVistaVocab ():
  """Muestra el di�logo para consultar el vocabulario"""
  global dlg_vista_vocab
  if dlg_vista_vocab:  # Di�logo ya creado
    try:
      dlg_vista_vocab.showMaximized()
      return
    except RuntimeError:  # Di�logo borrado por Qt
      pass  # Lo crearemos de nuevo
  # Creamos el di�logo
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  dlg_vista_vocab = QTableView (selector)
  dlg_vista_vocab.setModel (ModeloVocabulario (dlg_vista_vocab))
  # dlg_vista_vocab.setHorizontalHeaderLabels (('Palabra', 'N�mero', 'Tipo'))
  dlg_vista_vocab.setWindowTitle ('Vocabulario')
  selector.centralWidget().addSubWindow (dlg_vista_vocab)
  dlg_vista_vocab.showMaximized()
  selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal

def nuevaBD (posicion):
  """Ejecuta la funci�n de �ndice posicion para crear una nueva base de datos vac�a"""
  global mod_actual
  selector.setCursor (Qt.WaitCursor)  # Puntero de rat�n de espera
  mod_actual = __import__ (info_nueva[posicion][0])
  mod_actual.__dict__[info_nueva[posicion][1]]()
  postCarga ('Sin nombre')

def nuevaEntrada (posicion):
  """A�ade una entrada de proceso vac�a en la posici�n dada como par�metro"""
  if posicion < 0:
    posicion = 0
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  proceso[0].insert (posicion, [255, 255])
  proceso[1].insert (posicion, [])
  cambiaProceso (numProceso, posicion)

def quitaEntrada (posicion):
  """Quita la entrada de proceso de la posici�n dada como par�metro"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  del proceso[0][posicion]
  del proceso[1][posicion]
  cambiaProceso (numProceso, max (0, posicion - 1))

def quitaEntradas ():
  """Quita la entradas del proceso seleccionado"""
  numProceso = pestanyas.currentIndex()
  proceso    = mod_actual.tablas_proceso[numProceso]  # El proceso seleccionado
  del proceso[0][:]
  del proceso[1][:]
  cambiaProceso (numProceso)

def postCarga (nombre):
  """Realiza las acciones convenientes tras la carga satisfactoria de una BD

  Recibe como par�metro el nombre de la base de datos"""
  # Apa�o para que funcione la librer�a DAAD tal y como est� (con lista unificada de condactos)
  # Lo hacemos aqu�, porque la lista de condactos se puede extender tras cargar una BD
  if compruebaNombre (mod_actual, 'condactos', dict):
    for codigo in mod_actual.condactos:
      if mod_actual.condactos[codigo][2]:  # Es acci�n
        mod_actual.acciones[codigo] = mod_actual.condactos[codigo]
      else:
        mod_actual.condiciones[codigo] = mod_actual.condactos[codigo]
  # Cogemos la primera palabra de cada tipo y n�mero como sin�nimo preferido
  if 'Verbo' in mod_actual.TIPOS_PAL:
    tipoVerbo = mod_actual.TIPOS_PAL.index('Verbo')
  else:
    tipoVerbo = -1
  for palabra, codigo, tipo in mod_actual.vocabulario:
    idYtipo = (codigo, tipo)
    # Preferiremos terminaci�n en R para verbos (heur�stica para que sean en forma infinitiva)
    if idYtipo not in pal_sinonimo or \
        (tipo == tipoVerbo and palabra[-1] == 'r' and pal_sinonimo[idYtipo][-1] != 'r'):
      pal_sinonimo[idYtipo] = palabra
  # Preparamos las funciones de exportaci�n
  for entrada in mod_actual.funcs_exportar:
    if compruebaNombre (mod_actual, entrada[0], types.FunctionType):
      info_exportar.append ((entrada[0], entrada[1], entrada[2]))
  # Habilitamos las acciones que requieran tener una base de datos cargada
  accContadores.setEnabled (True)
  accDireccs.setEnabled    (True)
  accExportar.setEnabled   (len (info_exportar) > 0)
  accMsgSys.setEnabled     (True)
  accMsgUsr.setEnabled     (True)
  accPasoAPaso.setEnabled  (True)
  accTblProcs.setEnabled   (True)
  accTblVocab.setEnabled   (True)
  selector.setWindowTitle ('NAPS IDE - ' + nombre + ' (' + mod_actual.NOMBRE_SISTEMA + ')')
  selector.setCursor (Qt.ArrowCursor)  # Puntero de rat�n normal


if sys.version_info[0] < 3:
  reload (sys)  # Necesario para poder ejecutar sys.setdefaultencoding
  sys.stdout = codecs.getwriter (locale.getpreferredencoding()) (sys.stdout)  # Locale del sistema para la salida est�ndar
  sys.setdefaultencoding ('iso-8859-15')  # Nuestras cadenas est�n en esta codificaci�n, no en ASCII

aplicacion = QApplication (sys.argv)

creaSelector()
selector.showMaximized()
cargaInfoModulos()

if len (sys.argv) > 1:
  if len (sys.argv) > 2:
    importaBD (sys.argv[1], sys.argv[2])
  else:
    importaBD (sys.argv[1])

sys.exit (aplicacion.exec_())