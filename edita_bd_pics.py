#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Editor de bases de datos gráficas de DAAD
# Copyright (C) 2022-2023 José Manuel Ferrer Ortiz
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

import gettext
import math
import os
import re
import sys

try:
  from PyQt4.QtCore import *
  from PyQt4.QtGui  import *
except:
  from PyQt5.QtCore    import *
  from PyQt5.QtGui     import *
  from PyQt5.QtWidgets import *

import graficos_bitmap


acc_exportar          = None  # Acción de exportar base de datos gráfica
acc_exportar_todo     = None  # Acción de exportar todos los recursos
acc_importar_masa     = None  # Acción de importar múltiples imágenes
acc_importar_masa_sin = None  # Acción de importar múltiples imágenes, conservando la paleta de las de número ya existente en la BD
dlg_abrir             = None  # Diálogo de abrir imagen/importar múltiples imágenes
dlg_exportar          = None  # Diálogo de exportar base de datos gráfica
dlg_exportar_todo     = None  # Diálogo de exportar todos los recursos
dlg_importar          = None  # Diálogo de importar base de datos gráfica
dlg_guardar           = None  # Diálogo de guardar imagen


def traduceConGettext (cadena):
  return unicode (gettext.gettext (cadena).decode ('utf8'))

gettext.bindtextdomain ('naps', os.path.join (os.path.abspath (os.path.dirname (__file__)), 'locale'))
gettext.textdomain ('naps')
_ = traduceConGettext if sys.version_info[0] < 3 else gettext.gettext


filtro_img_def = 1  # Índice en filtros_img del formato de imagen por defecto
filtros_img    = ((_('BMP images'), ['bmp'])), (_('PNG images'), ['png'])  # Filtros de formatos de imagen soportados para abrir y guardar


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
    contextual = QMenu (self)
    if self.imagen:
      accImgExportar     = QAction (_('&Export image'),                     contextual)
      accImgSustituir    = QAction (_('&Replace image'),                    contextual)
      accImgSustituirSin = QAction (_('Replace image &preserving palette'), contextual)
      accImgExportar.triggered.connect (self.exportarImagen)
      accImgSustituir.triggered.connect (self.importarImagen)
      accImgSustituirSin.triggered.connect (lambda: self.importarImagen (conservarPaleta = True))
      contextual.addAction (accImgExportar)
      contextual.addAction (accImgSustituir)
      contextual.addAction (accImgSustituirSin)
    else:
      accImgAnyadir = QAction (_('&Add image'), contextual)
      accImgAnyadir.triggered.connect (self.importarImagen)
      contextual.addAction (accImgAnyadir)
    contextual.exec_ (evento.globalPos())

  def exportarImagen (self, nombreFichero = None):
    global dlg_guardar
    if not nombreFichero:
      filtro = []
      for descripcion, extensiones in filtros_img:
        filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
      if not dlg_guardar:  # Diálogo no creado aún
        dlg_guardar = QFileDialog (ventana, _('Export image'), os.curdir, ';;'.join (filtro))
        dlg_guardar.setAcceptMode (QFileDialog.AcceptSave)
        dlg_guardar.setLabelText  (QFileDialog.LookIn,   _('Places'))
        dlg_guardar.setLabelText  (QFileDialog.FileName, _('&Name:'))
        dlg_guardar.setLabelText  (QFileDialog.FileType, _('Filter:'))
        dlg_guardar.setLabelText  (QFileDialog.Accept,   _('&Save'))
        dlg_guardar.setLabelText  (QFileDialog.Reject,   _('&Cancel'))
        dlg_guardar.setOption     (QFileDialog.DontConfirmOverwrite)
        dlg_guardar.setOption     (QFileDialog.DontUseNativeDialog)
      dlg_guardar.selectNameFilter (filtro[filtro_img_def])  # Elegimos el formato por defecto
      if not dlg_guardar.exec_():  # Se ha cancelado
        return
      indiceFiltro  = list (dlg_guardar.nameFilters()).index (dlg_guardar.selectedNameFilter())
      nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_guardar.selectedFiles()[0])
      extension     = '.' + filtros_img[indiceFiltro][1][0]
      if nombreFichero[- len (extension):].lower() != extension:
        nombreFichero += extension
    if os.path.isfile (nombreFichero):
      dlgSiNo = QMessageBox (ventana)
      dlgSiNo.addButton (_('&Yes'), QMessageBox.YesRole)
      dlgSiNo.addButton (_('&No'), QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle (_('Overwrite'))
      dlgSiNo.setText (_('A file already exists with path and name:\n\n') + nombreFichero)
      dlgSiNo.setInformativeText (_('\nDo you want to overwrite it?'))
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el botón Sí
        return
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    self.imagen.save (nombreFichero)
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

  def importarImagen (self, conservarPaleta = False, nombreFichero = None):
    if not nombreFichero:
      preparaDialogoAbrir (multiple = False)
      if not dlg_abrir.exec_():  # Se ha cancelado
        return
      nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_abrir.selectedFiles()[0])
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    imagen = QImage (nombreFichero)
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal
    if imagen.isNull():
      muestraFallo (_('Unable to open image from file:\n') + nombreFichero)
      return
    if imagen.height() < 1 or imagen.width() < 1:
      muestraFallo (_('Invalid dimensions'), _('The chosen image (%s) has invalid dimensions, both its width and its height should be bigger than zero') % nombreFichero)
      return
    if imagen.height() > graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][1]:
      muestraFallo (_('Excessive image height'), _('The chosen image (%(fileName)s) has a height of %(imageHeight)d pixels, while the mode %(graphicMode)s of the graphic database only supports up to %(maxHeight)d') % {'fileName': nombreFichero, 'imageHeight': imagen.height(), 'graphicMode': graficos_bitmap.modo_gfx, 'maxHeight': graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][1]})
      return
    if imagen.width() > graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][0]:
      muestraFallo (_('Excessive image width'), _('The chosen image (%(fileName)s) has a width of %(imageWidth)d pixels, while the mode %(graphicMode)s of the graphic database only supports up to %(maxWidth)d') % {'fileName': nombreFichero, 'imageWidth': imagen.width(), 'graphicMode': graficos_bitmap.modo_gfx, 'maxWidth': graficos_bitmap.resolucion_por_modo[graficos_bitmap.modo_gfx][0]})
      return
    if imagen.height() % 8:
      muestraFallo (_('Incorrect image height'), _('The chosen image (%(fileName)s) has a height of %(imageHeight)d pixels, when it should be a multiple of 8') % {'fileName': nombreFichero, 'imageHeight': imagen.height()})
      return
    if imagen.width() % 8:
      muestraFallo (_('Incorrect image width'), _('The chosen image (%(fileName)s) has a width of %(imageWidth)d pixels, when it should be a multiple of 8') % {'fileName': nombreFichero, 'imageWidth': imagen.width()})
      return
    # Calculamos el número de colores que utiliza la imagen
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    coloresUsados = set()
    if imagen.depth() > 8:  # No usa paleta indexada
      for fila in range (imagen.height()):
        for columna in range (imagen.width()):
          coloresUsados.add (imagen.pixel (columna, fila))
      coloresUsados = list (coloresUsados)
      numColores    = len (coloresUsados)
    else:  # Usa paleta indexada
      paletaImagen = imagen.colorTable()
      for fila in range (imagen.height()):
        for columna in range (imagen.width()):
          coloresUsados.add (imagen.pixel (columna, fila))
      numColores    = len (coloresUsados)
      coloresUsados = paletaImagen
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal
    if numColores > graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx]:
      muestraFallo (_('High number of colors'), _('The chosen image (%(fileName)s) uses %(colorCount)d different colors, while the mode %(graphicMode)s of the graphic database only supports %(maxColorCount)d') % {'fileName': nombreFichero, 'colorCount': numColores, 'graphicMode': graficos_bitmap.modo_gfx, 'maxColorCount': graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx]})
    if self.imagen and graficos_bitmap.recurso_es_unico (self.numRecurso):
      dlgSiNo = QMessageBox (ventana)
      dlgSiNo.addButton (_('&Yes'), QMessageBox.YesRole)
      dlgSiNo.addButton (_('&No'), QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle (_('Replace image'))
      dlgSiNo.setText (_("Image #%d isn't used by any other resource") % self.numRecurso)
      dlgSiNo.setInformativeText (_('\nAre you sure you want to replace it with the image from the chosen file?'))
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el botón Sí
        return
    paletas = graficos_bitmap.da_paletas_del_formato()
    if len (paletas) > 1:
      if self.imagen and conservarPaleta:
        paletas = [graficos_bitmap.recursos[self.numRecurso]['paleta']]
      else:
        if numColores > graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx]:
          muestraFallo (_('Trimmed palette'), _('The format of the graphic database supports variable palette, the first %d colors from the image will be taken as the palette') % graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx])
          coloresUsados = coloresUsados[:graficos_bitmap.colores_por_modo[graficos_bitmap.modo_gfx]]
        paletas = [[]]
        for c in range (len (coloresUsados)):
          color = QColor (coloresUsados[c])
          paletas[0].append ((color.red(), color.green(), color.blue()))
    else:
      paletas = paletas[list (paletas.keys())[0]]

    # Buscamos los colores más cercanos de entre las paletas para los colores de la imagen
    masCercanos = []  # Índice en paleta del color más cercano a los usados en la imagen, y su cercanía, para ambas paletas
    for p in range (len (paletas)):
      masCercanos.append ([])
    for c in range (len (coloresUsados)):
      color = QColor (coloresUsados[c])
      for p in range (len (masCercanos)):
        masCercano = [-1, 999999]  # Índice de color en paleta, y cercanía del color más cercano en la paleta a éste
        paleta     = paletas[p]
        for cp in range (len (paleta)):
          rojoPaleta, verdePaleta, azulPaleta = paleta[cp]
          if color.red() == rojoPaleta and color.green() == verdePaleta and color.blue() == azulPaleta:  # Coincidencia exacta
            masCercanos[p].append ((cp, 0))
            break
          else:
            if (color.red() + rojoPaleta) / 2 < 128:
              cercania = math.sqrt (1 * ((color.red() - rojoPaleta) ** 2) + 1 * ((color.green() - verdePaleta) ** 2) + 2 * ((color.blue() - azulPaleta) ** 2))
            else:
              cercania = math.sqrt (2 * ((color.red() - rojoPaleta) ** 2) + 1 * ((color.green() - verdePaleta) ** 2) + 1 * ((color.blue() - azulPaleta) ** 2))
            if cercania < masCercano[1]:
              masCercano = [cp, cercania]
        else:
          masCercanos[p].append (masCercano)

    # Buscamos la paleta más adecuada para los colores de la imagen
    if len (masCercanos) > 1:
      mejorCercania = 999999
      mejorPaleta   = None
      for p in range (len (masCercanos)):
        cercania = 0
        for masCercano in masCercanos[p]:
          cercania += masCercano[1]
        if cercania < mejorCercania:
          mejorCercania = cercania
          mejorPaleta   = p
    else:
      mejorPaleta = 0

    # Convertimos la imagen a los colores de la paleta más adecuada y la asignamos a este recurso
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    paleta = []
    for rojo, verde, azul in paletas[mejorPaleta]:
      paleta.append (qRgb (rojo, verde, azul))
    imgConvertida = QImage (imagen.width(), imagen.height(), QImage.Format_Indexed8)
    imgConvertida.setColorTable (paleta)
    imgComoIndices = []  # Imagen como índices en la paleta
    for fila in range (imagen.height()):
      for columna in range (imagen.width()):
        indiceEnPaleta = masCercanos[mejorPaleta][coloresUsados.index (imagen.pixel (columna, fila))][0]
        imgConvertida.setPixel (columna, fila, indiceEnPaleta)
        imgComoIndices.append (indiceEnPaleta)
    self.imagen = imgConvertida
    self.setIcon (QIcon (QPixmap (imgConvertida)))
    self.setIconSize (imagen.rect().size())
    graficos_bitmap.cambia_imagen (self.numRecurso, imagen.width(), imagen.height(), imgComoIndices, paletas[mejorPaleta])
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

class Ventana (QMainWindow):
  """Ventana principal"""
  def __init__ (self):
    global acc_exportar, acc_exportar_todo, acc_importar_masa, acc_importar_masa_sin
    super (Ventana, self).__init__()
    acc_exportar          = QAction (_('&Export graphic DB'), self)
    acc_exportar_todo     = QAction (_('&Export all'), self)
    acc_importar_masa     = QAction (_('&Add/replace images'), self)
    acc_importar_masa_sin = QAction (_('Add/replace images &preserving palette'), self)
    accImportar           = QAction (_('&Import graphic DB'), self)
    accSalir              = QAction (_('&Quit'), self)
    acc_exportar.setEnabled (False)
    acc_exportar_todo.setEnabled (False)
    acc_importar_masa.setEnabled (False)
    acc_importar_masa_sin.setEnabled (False)
    acc_exportar.triggered.connect (dialogoExportaBD)
    acc_exportar_todo.triggered.connect (dialogoExportarTodo)
    acc_importar_masa.triggered.connect (dialogoImportarImagenes)
    acc_importar_masa_sin.triggered.connect (lambda: dialogoImportarImagenes (conservarPaleta = True))
    accImportar.triggered.connect (dialogoImportaBD)
    accSalir.setShortcut (_('Ctrl+Q'))
    menuArchivo = self.menuBar().addMenu (_('&File'))
    menuArchivo.addAction (accImportar)
    menuArchivo.addAction (acc_exportar)
    menuArchivo.addSeparator()
    menuArchivo.addAction (accSalir)
    menuMasa = self.menuBar().addMenu (_('&Mass operations'))
    menuMasa.addAction (acc_importar_masa)
    menuMasa.addAction (acc_importar_masa_sin)
    menuMasa.addAction (acc_exportar_todo)
    scroll = QScrollArea (self)
    self.rejilla = QWidget (scroll)
    self.rejilla.setLayout (QGridLayout (self.rejilla))
    scroll.setWidget (self.rejilla)
    accSalir.triggered.connect (self.close)
    self.setCentralWidget (scroll)
    self.setWindowTitle (_('Graphic database editor'))
    self.showMaximized()


def dialogoExportaBD ():
  """Exporta la base de datos gráfica al fichero elegido por el usuario"""
  global dlg_exportar
  if graficos_bitmap.modo_gfx == 'CGA':
    extensiones   = ('.cga',)
    formatoFiltro = _('DAAD graphic databases for CGA (*.cga)')
  elif graficos_bitmap.modo_gfx == 'EGA':
    extensiones   = ('.ega',)
    formatoFiltro = _('DAAD graphic databases for EGA (*.ega)')
  elif graficos_bitmap.modo_gfx == 'PCW':
    extensiones   = ('.pcw', '.dat')
    formatoFiltro = _('DAAD graphic databases for PCW (*.dat *.pcw)')
  elif graficos_bitmap.modo_gfx in ('ST', 'VGA'):
    extensiones   = ('.dat',)
    formatoFiltro = _('DAAD v3 graphic databases for Amiga/PC (*.dat);;DAAD v3 graphic databases for Atari ST/STE (*.dat)')
  if not dlg_exportar:  # Diálogo no creado aún
    dlg_exportar = QFileDialog (ventana, _('Export graphic database'), os.curdir, formatoFiltro)
    dlg_exportar.setAcceptMode (QFileDialog.AcceptSave)
    dlg_exportar.setLabelText  (QFileDialog.LookIn,   _('Places'))
    dlg_exportar.setLabelText  (QFileDialog.FileName, _('&Name:'))
    dlg_exportar.setLabelText  (QFileDialog.FileType, _('Filter:'))
    dlg_exportar.setLabelText  (QFileDialog.Accept,   _('&Save'))
    dlg_exportar.setLabelText  (QFileDialog.Reject,   _('&Cancel'))
    dlg_exportar.setOption     (QFileDialog.DontConfirmOverwrite)
    dlg_exportar.setOption     (QFileDialog.DontUseNativeDialog)
  if dlg_exportar.exec_():  # No se ha cancelado
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_exportar.selectedFiles()[0])
    for extension in extensiones:
      if nombreFichero[-4:].lower() == extension:
        break
    else:  # No tenía extensión de las permitidas, se la añadimos
      nombreFichero += extensiones[0]
    if os.path.isfile (nombreFichero):
      dlgSiNo = QMessageBox (ventana)
      dlgSiNo.addButton (_('&Yes'), QMessageBox.YesRole)
      dlgSiNo.addButton (_('&No'), QMessageBox.NoRole)
      dlgSiNo.setIcon (QMessageBox.Warning)
      dlgSiNo.setWindowTitle (_('Overwrite'))
      dlgSiNo.setText (_('A file already exists with path and name:\n\n') + nombreFichero)
      dlgSiNo.setInformativeText (_('\nDo you want to overwrite it?'))
      if dlgSiNo.exec_() != 0:  # No se ha pulsado el botón Sí
        return
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    try:
      fichero = open (nombreFichero, 'wb')
    except IOError as excepcion:
      muestraFallo (_('Unable to open the file:\n') + nombreFichero,
                    excepcion.args[1])
      ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal
      return
    graficos_bitmap.guarda_bd_pics (fichero, ordenAmiga = 'Amiga' in dlg_exportar.selectedNameFilter())
    fichero.close()
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def dialogoExportarTodo ():
  """Deja al usuario elegir una carpeta donde exportar todos los recursos"""
  global dlg_exportar_todo
  if not dlg_exportar_todo:  # Diálogo no creado aún
    dlg_exportar_todo = QFileDialog (ventana, _('Folder to export to'), os.curdir)
    dlg_exportar_todo.setFileMode  (QFileDialog.Directory)
    dlg_exportar_todo.setLabelText (QFileDialog.LookIn,   _('Places'))
    dlg_exportar_todo.setLabelText (QFileDialog.FileName, _('&Name:'))
    dlg_exportar_todo.setLabelText (QFileDialog.FileType, _('Filter:'))
    dlg_exportar_todo.setLabelText (QFileDialog.Accept,   _('&Open'))
    dlg_exportar_todo.setLabelText (QFileDialog.Reject,   _('&Cancel'))
    dlg_exportar_todo.setOption    (QFileDialog.DontUseNativeDialog)
    dlg_exportar_todo.setOption    (QFileDialog.ShowDirsOnly)
  if not dlg_exportar_todo.exec_():  # Se ha cancelado
    return
  rutaFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_exportar_todo.selectedFiles()[0])
  for numRecurso in range (256):
    widget = ventana.rejilla.layout().itemAt (numRecurso).widget()
    if not widget.imagen:
      continue
    # TODO: exportación de sonidos
    nombreFichero = 'pic' + str (numRecurso).zfill (3) + '.png'
    widget.exportarImagen (os.path.join (rutaFichero, nombreFichero))

def dialogoImportaBD ():
  """Deja al usuario elegir un fichero de base datos gráfica, y lo intenta importar"""
  global dlg_importar
  if not dlg_importar:  # Diálogo no creado aún
    dlg_importar = QFileDialog (ventana, _('Import graphic database'), os.curdir, _('DAAD graphic databases (*.cga *.dat *.ega *.pcw)'))
    dlg_importar.setFileMode  (QFileDialog.ExistingFile)
    dlg_importar.setLabelText (QFileDialog.LookIn,   _('Places'))
    dlg_importar.setLabelText (QFileDialog.FileName, _('&Name:'))
    dlg_importar.setLabelText (QFileDialog.FileType, _('Filter:'))
    dlg_importar.setLabelText (QFileDialog.Accept,   _('&Open'))
    dlg_importar.setLabelText (QFileDialog.Reject,   _('&Cancel'))
    dlg_importar.setOption    (QFileDialog.DontUseNativeDialog)
  if dlg_importar.exec_():  # No se ha cancelado
    ventana.setCursor (Qt.WaitCursor)  # Puntero de ratón de espera
    nombreFichero = (str if sys.version_info[0] > 2 else unicode) (dlg_importar.selectedFiles()[0])
    importaBD (nombreFichero)
    ventana.setCursor (Qt.ArrowCursor)  # Puntero de ratón normal

def dialogoImportarImagenes (conservarPaleta = False):
  """Deja al usuario elegir ficheros de imágenes, las intenta cargar, y si todo es correcto añade/sustituye las imágenes"""
  muestraFallo (_('Each selected file will be tried to be loaded as an image, and its image will be applied to the corresponding resources with all the numbers found on the file name separated by non-digit characters.\n\nFor example:\n"pic08.png" "8" "image 8.bmp" will apply the image to resource #8\n"location 1, 7 and 28.png" "image 28 (1).7.bmp" will apply it over resources #1, #7 and #28'), icono = QMessageBox.Information)
  preparaDialogoAbrir (multiple = True)
  if not dlg_abrir.exec_():  # Se ha cancelado
    return
  for rutaFichero in dlg_abrir.selectedFiles():
    rutaFichero   = (str if sys.version_info[0] > 2 else unicode) (rutaFichero)
    nombreFichero = os.path.basename (rutaFichero)
    for numRecurso in re.findall (r'\d+', nombreFichero):
      numRecurso = int (numRecurso)
      if numRecurso > 255:
        muestraFallo (_('Invalid number'), _('File name "%(fileName)s" contains a number %(resourceNumber)d that is invalid as a resource, so that number will be ignored. If the name only had that number, the file will be ignored') % {'fileName': nombreFichero, 'resourceNumber': numRecurso})
        continue
      ventana.rejilla.layout().itemAt (numRecurso).widget().importarImagen (conservarPaleta, rutaFichero)

def importaBD (nombreFichero):
  """Importa una base de datos gráfica desde el fichero de nombre dado"""
  error = graficos_bitmap.carga_bd_pics (nombreFichero)
  if error:
    if graficos_bitmap.recursos:
      muestraFallo (_('Loading of one or more resources in the graphic database failed:\n') + nombreFichero, error)
    else:
      muestraFallo (_('Unable to open the file:\n') + nombreFichero, error, QMessageBox.Critical)
      return

  global acc_exportar
  if (graficos_bitmap.modo_gfx in ('CGA', 'EGA', 'PCW')  # Modos gráficos de la versión 1 de DMG
      or graficos_bitmap.modo_gfx in ('ST', 'VGA') and graficos_bitmap.version > 1):  # Versión 3+ de DMG
    acc_exportar.setEnabled (True)
    acc_exportar_todo.setEnabled (True)
    acc_importar_masa.setEnabled (True)
    acc_importar_masa_sin.setEnabled (True)
  else:
    acc_exportar.setEnabled (False)
    acc_exportar_todo.setEnabled (False)
    acc_importar_masa.setEnabled (False)
    acc_importar_masa_sin.setEnabled (False)

  altoMax  = 0  # Alto  de imagen máximo
  anchoMax = 0  # Ancho de imagen máximo
  imagenes = []
  for numImg in range (256):
    recurso = graficos_bitmap.recursos[numImg]
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

def muestraFallo (mensaje, detalle = '', icono = QMessageBox.Warning, parent = None):
  """Muestra un diálogo de fallo"""
  # TODO: sacar a módulo común con el IDE
  global dlg_fallo, ventana_principal
  try:
    dlg_fallo
  except:  # Diálogo no creado aún
    if parent == None:
      parent = ventana_principal
    dlg_fallo = QMessageBox (parent)
    dlg_fallo.addButton (_('&Accept'), QMessageBox.AcceptRole)
    dlg_fallo.setIcon (icono)
    if icono == QMessageBox.Critical:
      dlg_fallo.setWindowTitle (_('Failure'))
    elif icono == QMessageBox.Information:
      dlg_fallo.setWindowTitle (_('Information'))
    else:
      dlg_fallo.setWindowTitle (_('Warning'))
  dlg_fallo.setText (mensaje)
  if detalle:
    dlg_fallo.setInformativeText (_('Cause:\n') + detalle.decode ('iso-8859-15') if sys.version_info[0] < 3 else detalle)
  else:
    dlg_fallo.setInformativeText ('')
  dlg_fallo.exec_()

def preparaDialogoAbrir (multiple):
  global dlg_abrir
  extSoportadas = []  # Todas las extensiones de imágenes soportadas
  filtro        = []
  for descripcion, extensiones in filtros_img:
    filtro.append (descripcion + ' (*.' + ' *.'.join (extensiones) + ')')
    extSoportadas.extend (extensiones)
  filtro.append (_('All supported images (*.') + ' *.'.join (extSoportadas) + ')')
  if not dlg_abrir:  # Diálogo no creado aún
    dlg_abrir = QFileDialog (ventana, _('Open image'), os.curdir, ';;'.join (filtro))
    dlg_abrir.setLabelText (QFileDialog.LookIn,   _('Places'))
    dlg_abrir.setLabelText (QFileDialog.FileName, _('&Name:'))
    dlg_abrir.setLabelText (QFileDialog.FileType, _('Filter:'))
    dlg_abrir.setLabelText (QFileDialog.Accept,   _('&Open'))
    dlg_abrir.setLabelText (QFileDialog.Reject,   _('&Cancel'))
    dlg_abrir.setOption    (QFileDialog.DontUseNativeDialog)
  if multiple:
    dlg_abrir.setFileMode    (QFileDialog.ExistingFiles)
    dlg_abrir.setWindowTitle (_('Open images'))
  else:
    dlg_abrir.setFileMode    (QFileDialog.ExistingFile)
    dlg_abrir.setWindowTitle (_('Open image'))
  dlg_abrir.selectNameFilter (filtro[len (filtro) - 1])  # Elegimos el filtro de todas las imágenes soportadas


aplicacion = QApplication (sys.argv)
ventana    = Ventana()
ventana_principal = ventana  # Para muestraFallo

if len (sys.argv) > 1:
  importaBD (sys.argv[1])

sys.exit (aplicacion.exec_())
