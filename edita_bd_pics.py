#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Editor de bases de datos gráficas de DAAD
# Copyright (C) 2022 José Manuel Ferrer Ortiz
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

import math
import os
import sys

try:
  from PyQt4.QtCore import *
  from PyQt4.QtGui  import *
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtGui     import *
  from PyQt5.QtWidgets import *

import graficos_daad


dlg_importar = None  # Diálogo de importar base de datos gráfica
dlg_guardar  = None  # Diálogo de guardar fichero

filtro_img_def = 1  # Índice en filtros_img del formato de imagen por defecto
filtros_img    = (('Imágenes BMP', ['bmp'])), ('Imágenes PNG', ['png'])  # Filtros de formatos de imagen soportados para abrir y guardar


class Recurso (QPushButton):
  """Botón para cada recurso"""
  def __init__ (self, numRecurso, imagen = None):
    if imagen:
      super (Recurso, self).__init__ (QIcon (QPixmap (imagen)), str (numRecurso))
      self.setIconSize (imagen.rect().size())
    else:
      super (Recurso, self).__init__ (str (numRecurso))
    self.imagen     = imagen
    self.numRecurso = numRecurso

  def contextMenuEvent (self, evento):
    if self.imagen:
      contextual     = QMenu (self)
      accImgExportar = QAction ('&Exportar imagen', contextual)
      accImgExportar.triggered.connect (self.exportarImagen)
      contextual.addAction (accImgExportar)
      contextual.exec_ (evento.globalPos())

  def exportarImagen (self):
    global dlg_guardar
    if not dlg_guardar:  # Diálogo no creado aún
      filtro = []
      for descripcion, extensiones in filtros_img:
        filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
      dlg_guardar = QFileDialog (ventana, 'Exportar imagen', os.curdir, ';;'.join (filtro))
      dlg_guardar.setAcceptMode (QFileDialog.AcceptSave)
      dlg_guardar.setLabelText  (QFileDialog.LookIn,   'Lugares')
      dlg_guardar.setLabelText  (QFileDialog.FileName, '&Nombre:')
      dlg_guardar.setLabelText  (QFileDialog.FileType, 'Filtro:')
      dlg_guardar.setLabelText  (QFileDialog.Accept,   '&Guardar')
      dlg_guardar.setLabelText  (QFileDialog.Reject,   '&Cancelar')
      dlg_guardar.setOption     (QFileDialog.DontConfirmOverwrite)
      dlg_guardar.setOption     (QFileDialog.DontUseNativeDialog)
    dlg_guardar.selectNameFilter (filtro[filtro_img_def])  # Elegimos el formato por defecto
    if dlg_guardar.exec_():  # No se ha cancelado
      indiceFiltro  = list (dlg_guardar.nameFilters()).index (dlg_guardar.selectedNameFilter())
      nombreFichero = str (dlg_guardar.selectedFiles()[0])
      extension     = '.' + filtros_img[indiceFiltro][1][0]
      if nombreFichero[- len (extension):].lower() != extension:
        nombreFichero += extension
      if os.path.isfile (nombreFichero):
        dlgSiNo = QMessageBox (ventana)
        dlgSiNo.addButton ('&Sí', QMessageBox.YesRole)
        dlgSiNo.addButton ('&No', QMessageBox.NoRole)
        dlgSiNo.setIcon (QMessageBox.Warning)
        dlgSiNo.setWindowTitle ('Sobreescritura')
        dlgSiNo.setText ('Ya existe un fichero con ruta y nombre:\n\n' + nombreFichero)
        dlgSiNo.setInformativeText ('\n¿Quieres sobreescribirlo?')
        if dlgSiNo.exec_() != 0:  # No se ha pulsado el botón Sí
          return
      ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
      self.imagen.save (nombreFichero)
      ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

class Ventana (QMainWindow):
  """Ventana principal"""
  def __init__ (self):
    super (Ventana, self).__init__()
    accImportar = QAction ('&Importar', self)
    accSalir    = QAction ('&Salir',    self)
    accImportar.triggered.connect (dialogoImportaBD)
    accSalir.setShortcut ('Ctrl+Q')
    menuArchivo = self.menuBar().addMenu ('&Archivo')
    menuArchivo.addAction (accImportar)
    menuArchivo.addSeparator()
    menuArchivo.addAction (accSalir)
    scroll = QScrollArea (self)
    self.rejilla = QWidget (scroll)
    self.rejilla.setLayout (QGridLayout (self.rejilla))
    scroll.setWidget (self.rejilla)
    accSalir.triggered.connect (self.close)
    self.setCentralWidget (scroll)
    self.setWindowTitle ('Editor de bases de datos gráficas')
    self.showMaximized()


def dialogoImportaBD ():
  """Deja al usuario elegir un fichero de base datos gráfica, y lo intenta importar"""
  global dlg_importar
  if not dlg_importar:  # Diálogo no creado aún
    dlg_importar = QFileDialog (ventana, 'Importar base de datos gráfica', os.curdir, 'Bases de datos gráficas DAAD (*.cga *.dat *.ega *.pcw)')
    dlg_importar.setFileMode  (QFileDialog.ExistingFile)
    dlg_importar.setLabelText (QFileDialog.LookIn,   'Lugares')
    dlg_importar.setLabelText (QFileDialog.FileName, '&Nombre:')
    dlg_importar.setLabelText (QFileDialog.FileType, 'Filtro:')
    dlg_importar.setLabelText (QFileDialog.Accept,   '&Abrir')
    dlg_importar.setLabelText (QFileDialog.Reject,   '&Cancelar')
    dlg_importar.setOption    (QFileDialog.DontUseNativeDialog)
  if dlg_importar.exec_():  # No se ha cancelado
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    nombreFichero = str (dlg_importar.selectedFiles()[0])
    importaBD (nombreFichero)
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def importaBD (nombreFichero):
  """Importa una base de datos desde el fichero de nombre dado"""
  global le
  error = graficos_daad.carga_bd_pics (nombreFichero)
  if error:
    muestraFallo ('No se puede abrir el fichero:\n' + nombreFichero, error)
    return

  altoMax  = 0  # Alto  de imagen máximo
  anchoMax = 0  # Ancho de imagen máximo
  imagenes = []
  for numImg in range (256):
    recurso = graficos_daad.recursos[numImg]
    if not recurso:
      imagenes.append (None)
      continue
    paleta = []
    for rojo, verde, azul in recurso['paleta']:
      paleta.append (qRgb (rojo, verde, azul))
    ancho, alto = recurso['dimensiones']
    col    = 0  # Columna actual
    fila   = 0  # Fila actual
    imagen = QImage (ancho, alto, QImage.Format_Indexed8)
    imagen.setColorTable (paleta)
    for indicePaleta in recurso['imagen']:
      imagen.setPixel (col, fila, indicePaleta)
      col += 1
      if col == ancho:
        col   = 0
        fila += 1
    imagenes.append (imagen)
    if alto > altoMax:
      altoMax = alto
    if ancho > anchoMax:
      anchoMax = ancho

  # Borramos botones anteriores si los había
  if ventana.rejilla.layout().count():
    for i in range (255, -1, -1):
      ventana.rejilla.layout().itemAt (i).widget().setParent (None)
    ventana.rejilla.setMinimumSize (0, 0)
    ventana.rejilla.resize (0, 0)

  dtWidget  = QDesktopWidget()  # Para obtener el ancho de la pantalla (dado que el de la ventana no se correspondía con el real)
  geometria = dtWidget.availableGeometry (ventana)
  margen    = 8
  columnas  = geometria.width() // (anchoMax + margen)
  filas     = math.ceil (256. / columnas)
  ventana.rejilla.setMinimumSize (geometria.width() - 20, (filas * (altoMax + margen) + ((filas + 1) * 6)))

  col  = 0  # Columna actual
  fila = 0  # Fila actual
  for i in range (256):
    imagen = imagenes[i]
    widget = Recurso (i, imagen)
    widget.setMinimumSize (anchoMax + margen, altoMax + margen)
    ventana.rejilla.layout().addWidget (widget, fila, col)
    col += 1
    if col == columnas:
      col   = 0
      fila += 1

def muestraFallo (mensaje, detalle = '', parent = None):
  """Muestra un diálogo de fallo leve"""
  # TODO: sacar a módulo común con el IDE
  global dlg_fallo, ventana_principal
  try:
    dlg_fallo
  except:  # Diálogo no creado aún
    if parent == None:
      parent = ventana_principal
    dlg_fallo = QMessageBox (parent)
    dlg_fallo.addButton ('&Aceptar', QMessageBox.AcceptRole)
    dlg_fallo.setIcon (QMessageBox.Warning)
    dlg_fallo.setWindowTitle ('Fallo')
  dlg_fallo.setText (mensaje)
  if detalle:
    dlg_fallo.setInformativeText ('Causa:\n' + detalle)
  dlg_fallo.exec_()


aplicacion = QApplication (sys.argv)
ventana    = Ventana()
ventana_principal = ventana  # Para muestraFallo

if len (sys.argv) > 1:
  importaBD (sys.argv[1])

sys.exit (aplicacion.exec_())
