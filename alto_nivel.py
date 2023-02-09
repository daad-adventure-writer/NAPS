# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funciones de apoyo de alto nivel
# Copyright (C) 2010, 2021, 2023 José Manuel Ferrer Ortiz
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

import os
import sys


# Código de cada tipo de palabra por nombre en el código fuente
tipos_pal_dict = {'verb': 0, 'adverb': 1, 'noun': 2, 'adjective': 3, 'preposition': 4, 'conjugation': 5, 'conjunction': 5, 'pronoun': 6}

# Identificadores (para hacer el código más legible) predefinidos
IDS_LOCS = {'WORN': 253, 'CARRIED': 254, 'HERE': 255}


def carga_sce (fichero, longitud, LONGITUD_PAL, atributos, atributos_extra, condactos, condactos_nuevos, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, nueva_version, num_objetos, tablas_proceso, vocabulario):
  """Carga la base de datos desde el código fuente SCE del fichero de entrada, con y sobre las variables pasadas como parámetro

  Para compatibilidad con el IDE:
  - Recibe como primer parámetro un fichero abierto
  - Recibe como segundo parámetro la longitud del fichero abierto
  - Devuelve False si ha ocurrido algún error"""
  try:
    import lark
  except:
    prn ('Para poder importar código fuente, se necesita la librería Lark', 'versión <1.0' if sys.version_info[0] < 3 else '', file = sys.stderr)
    return False
  try:
    import re
    codigoSCE = fichero.read().replace (b'\r\n', b'\n').decode()
    # Procesamos carga de ficheros externos con directivas de preprocesador /LNK
    # TODO: extraer el código común con abreFichXMessages, a función en bajo_nivel
    # TODO: indicar nombre del fichero externo en errores ocurridos en él, con número de línea relativo a él
    encaje = True
    while encaje:
      encaje = re.search ('\n/LNK[ \t]+([^ \n\t]+)', codigoSCE)
      if not encaje:
        break
      nombreFich = encaje.group (1).lower()
      if '.' not in nombreFich:
        nombreFich += '.sce'
      # Buscamos el fichero con independencia de mayúsculas y minúsculas
      rutaCarpeta = os.path.dirname (fichero.name)
      for nombreFichero in os.listdir (rutaCarpeta if rutaCarpeta else '.'):
        if nombreFichero.lower() == nombreFich:
          nombreFich = nombreFichero
          break
      else:
        prn ('No se encuentra el fichero "' + nombreFich + '" requerido por una directiva de preprocesador /LNK', encaje.group (1), file = sys.stderr)
        return False
      try:
        ficheroLnk = open (os.path.join (os.path.dirname (fichero.name), nombreFich), 'rb')
      except:
        prn ('No se puede abrir el fichero "' + nombreFich + '" requerido por una directiva de preprocesador /LNK', encaje.group (1), file = sys.stderr)
        return False
      codigoSCE = codigoSCE[:encaje.start (0)] + ficheroLnk.read().replace (b'\r\n', b'\n').decode()
      ficheroLnk.close()
    parserSCE = lark.Lark.open ('gramatica_sce.lark', __file__, propagate_positions = True)
    arbolSCE  = parserSCE.parse (codigoSCE)
    # Cargamos cada tipo de textos
    for idSeccion, listaCadenas in (('stx', msgs_sys), ('mtx', msgs_usr), ('otx', desc_objs), ('ltx', desc_locs)):
      for seccion in arbolSCE.find_data (idSeccion):
        numEntrada = 0
        for entrada in seccion.find_data ('textentry'):
          numero = int (entrada.children[0])
          if numero != numEntrada:
            raise TabError ('número de entrada %d en lugar de %d', (numEntrada, numero), entrada.meta)
          lineas = []
          for lineaTexto in entrada.children[1:]:
            if lineaTexto.type == 'COMMENT':
              continue  # Omitimos comentarios reconocidos por la gramática
            linea = str (lineaTexto)
            if not lineas and linea[:2] == '\n;':
              continue  # Omitimos comentarios iniciales
            lineas.append (linea[1:])  # El primer carácter siempre será \n
          # Evitamos tomar nueva línea antes de comentario final como línea de texto en blanco
          if lineas and not linea and codigoSCE[lineaTexto.meta.start_pos + 1] == ';':
            del lineas[-1]
          for l in range (len (lineas) - 1, 0, -1):
            if lineas[l][:1] == ';':
              del lineas[l]  # Eliminamos comentarios finales
            else:
              break
          # Unimos las cadenas como corresponde
          cadena = ''
          for linea in lineas:
            if linea:
              cadena += ('' if cadena[-1:] in ('\n', '') else ' ') + linea
            else:
              cadena += '\n'
          listaCadenas.append (cadena)
          numEntrada += 1
    # Cargamos el vocabulario
    adjetivos     = {'_': 255}
    adverbios     = {}
    nombres       = {'_': 255}
    preposiciones = {}
    verbos        = {'_': 255}
    tipoParametro = {'j': (adjetivos, 'adjetivo'), 'n': (nombres, 'nombre'), 'r': (preposiciones, 'preposición'), 'v': (adverbios, 'adverbio'), 'V': (verbos, 'verbo')}
    for seccion in arbolSCE.find_data ('vocentry'):
      palabra = str (seccion.children[0])[:LONGITUD_PAL].lower()
      codigo  = int (seccion.children[1])
      tipo    = tipos_pal_dict[str (seccion.children[2].children[0]).lower()]
      vocabulario.append ((palabra, codigo, tipo))
      # Dejamos preparados diccionarios de códigos de palabra para verbos, nombres y adjetivos
      if tipo == 0:
        verbos[palabra] = codigo
      elif tipo == 1:
        adverbios[palabra] = codigo
      elif tipo == 2:
        nombres[palabra] = codigo
        if codigo < 20:
          verbos[palabra] = codigo
      elif tipo == 3:
        adjetivos[palabra] = codigo
      elif tipo == 4:
        preposiciones[palabra] = codigo
    # Cargamos las conexiones entre localidades
    numEntrada = 0
    for seccion in arbolSCE.find_data ('conentry'):
      numero = int (seccion.children[0])
      if numero != numEntrada:
        raise TabError ('número de localidad %d en lugar de %d', (numEntrada, numero), seccion.meta)
      salidas = []
      for conexion in seccion.find_data ('conitem'):
        verbo = str (conexion.children[0].children[0])[:LONGITUD_PAL].lower()
        if verbo not in verbos:
          raise TabError ('una palabra de vocabulario de tipo verbo', (), conexion.children[0])
        destino = int (conexion.children[1])
        if destino >= len (desc_locs):
          raise TabError ('número de localidad entre %d y %d', (0, len (desc_locs) - 1), conexion.children[1])
        salidas.append ((verbos[verbo], destino))
      conexiones.append (salidas)
      numEntrada += 1
    if numEntrada != len (desc_locs):
      raise TabError ('el mismo número de entradas de conexión (%d) que de descripciones de localidades (%d)', (numEntrada, len (desc_locs)))
    # Cargamos datos de los objetos
    numEntrada = 0
    for seccion in arbolSCE.find_data ('objentry'):
      numero = int (seccion.children[0])
      if numero != numEntrada:
        raise TabError ('número de objeto %d en lugar de %d', (numEntrada, numero), seccion.meta)
      # Cargamos la localidad inicial del objeto
      if seccion.children[1].children:
        localidad = seccion.children[1].children[0]
        if localidad.type == 'INT':
          locs_iniciales.append (int (localidad))
        else:  # Valor no numérico (p.ej. CARRIED)
          locs_iniciales.append (IDS_LOCS[str (localidad)])
      else:
        locs_iniciales.append (252)
      # Cargamos el peso del objeto
      entero = seccion.children[2]
      peso   = int (entero)
      if peso < 0 or peso > 63:
        raise TabError ('valor de peso del objeto %d entre 0 y 63', numEntrada, entero)
      # Cargamos los atributos del objeto
      valorAttrs = ''
      for atributo in seccion.find_data ('attr'):
        valorAttrs += '1' if atributo.children else '0'
      if len (valorAttrs) > 18:
        raise TabError ('Número de atributos para el objeto %d excesivo, NAPS sólo soporta hasta 18', numEntrada, entero, 1)
      # Soportamos entre 2 y 18 atributos dejando a cero los que no se indiquen
      valorAttrs += '0' * (18 - len (valorAttrs))
      atributos.append (peso + ((valorAttrs[0] == '1') << 6) + ((valorAttrs[1] == '1') << 7))
      atributos_extra.append (int (valorAttrs[2:], 2))
      # Cargamos el vocabulario del objeto
      palabras = []
      for word in seccion.find_data ('word'):
        palabra = str (word.children[0])[:LONGITUD_PAL].lower() if word.children else '_'
        palabras.append (palabra)
        if len (palabras) == 1 and palabra not in nombres:
          break  # Para conservar la posición de la primera palabra inexistente
      if palabras[0] not in nombres or palabras[1] not in adjetivos:
        raise TabError ('una palabra de vocabulario de tipo %s', 'adjetivo' if len (palabras) > 1 else 'nombre', word.meta)
      nombres_objs.append ((nombres[palabras[0]], adjetivos[palabras[1]]))
      numEntrada += 1
    if numEntrada != len (desc_objs):
      raise TabError ('el mismo número de objetos (%d) que de descripciones de objetos (%d)', (numEntrada, len (desc_objs)))
    num_objetos[0] = numEntrada
    # Preparamos código y parámetros en cada versión, de los condactos, indexando por nombre
    datosCondactos = {}
    for listaCondactos in (condactos, condactos_nuevos):
      for codigo in listaCondactos:
        condacto = listaCondactos[codigo]
        if condacto[0] not in datosCondactos:
          datosCondactos[condacto[0]] = [None, None]
        datosCondacto = (codigo, condacto[1])
        if not condactos_nuevos:  # Para sistemas distintos a DAAD
          datosCondactos[condacto[0]][0] = datosCondacto
        elif condacto[4] == 3:  # El condacto es igual en ambas versiones
          datosCondactos[condacto[0]] = (datosCondacto, datosCondacto)
        else:
          datosCondactos[condacto[0]][condacto[4] - 1] = datosCondacto
    # Cargamos las tablas de proceso
    numProceso = 0
    version    = 0  # Versión de DAAD necesaria, 0 significa compatibilidad con ambas
    for seccion in arbolSCE.find_data ('pro'):
      entero = seccion.children[0]
      numero = int (entero)
      if numero != numProceso:
        raise TabError ('número de proceso %d en lugar de %d', (numProceso, numero), entero)
      cabeceras = []
      entradas  = []
      for procentry in seccion.find_data ('procentry'):
        palabras = []
        for word in procentry.find_data ('word'):
          palabra = str (word.children[0])[:LONGITUD_PAL].lower() if word.children else '_'
          palabras.append (palabra)
          if len (palabras) == 1 and palabra not in verbos:
            break  # Para conservar la posición de la primera palabra inexistente
        if palabras[0] not in verbos or palabras[1] not in nombres:
          raise TabError ('una palabra de vocabulario de tipo %s', 'nombre' if len (palabras) > 1 else 'verbo', word.meta)
        cabeceras.append ((verbos[palabras[0]], nombres[palabras[1]]))
        entrada = []
        for condacto in procentry.find_data ('condact'):
          for condactname in condacto.find_data ('condactname'):
            nombre = str (condactname.children[0])
          if nombre not in datosCondactos:
            raise TabError ('Condacto de nombre %s inexistente', nombre, condacto.meta)
          parametros = []
          for param in condacto.find_data ('param'):
            if param.children:
              parametro = param.children[0]
              if parametro.type == 'INT':
                parametros.append (int (parametro))
              elif parametro.type == 'VOCWORD':
                # TODO: tolerar esto en caso que la palabra del parámetro sea única en el vocabulario
                if version:
                  if not datosCondactos[nombre][version - 1]:
                    break  # Se comprueba esto de nuevo más adelante
                  tipoParam       = datosCondactos[nombre][version - 1][1][len (parametros) : len (parametros) + 1]
                  palabraAdmitida = tipoParam in tipoParametro
                else:
                  palabraAdmitida = False
                  for datoCondacto in datosCondactos[nombre]:
                    if datosCondacto and datoCondacto[1][len (parametros) : len (parametros) + 1] in tipoParametro:
                      palabraAdmitida = True
                      break
                if not palabraAdmitida:
                  raise TabError ('El condacto %s no admite una palabra de vocabulario como parámetro aquí', nombre, parametro)
                # Los condactos con este tipo de parámetro sólo tienen un parámetro de igual tipo en ambas versiones de DAAD
                palabra      = str (parametro)[:LONGITUD_PAL].lower()
                letraTipoPal = datosCondactos[nombre][0][1][0]
                listaVocab, tipoPalabra = tipoParametro[letraTipoPal]
                if palabra not in listaVocab:
                  raise TabError ('una palabra de vocabulario de tipo %s', tipoPalabra, parametro)
                parametros.append (listaVocab[palabra])
              else:  # Valores preestablecidos (p.ej. CARRIED)
                parametros.append (IDS_LOCS[str (parametro)])
            else:
              parametros.append (255)  # Es _
          # Detectamos incompatibilidades por requerirse versiones de DAAD diferentes
          versionAntes = version
          if version:
            if not datosCondactos[nombre][version - 1]:
              raise TabError ('Condacto de nombre %s inexistente en DAAD versión %d (asumida por condactos anteriores)', (nombre, version), condacto.meta)
            # La comprobación del número de parámetros se hace abajo
            entrada.append ((datosCondactos[nombre][version - 1][0], parametros))
          else:
            # Fijamos versión de DAAD si el condacto con ese nombre sólo está en una
            if not datosCondactos[nombre][0] or not datosCondactos[nombre][1]:
              version = 1 if datosCondactos[nombre][0] else 2
              if version == 2:
                nueva_version.append (True)
            elif len (parametros) != len (datosCondactos[nombre][0][1]) and len (parametros) != len (datosCondactos[nombre][1][1]):
              if len (datosCondactos[nombre][0][1]) == len (datosCondactos[nombre][1][1]):
                requerido = len (datosCondactos[nombre][0][1])
              else:
                requerido = ' o '.join (sorted ((len (datosCondactos[nombre][0][1]), len (datosCondactos[nombre][1][1]))))
              raise TabError ('El condacto %s requiere %d parámetro%s', (nombre, requerido, '' if requerido == 1 else 's'), condacto.meta)
            # Fijamos versión de DAAD si el condacto con ese número de parámetros sólo está en una
            elif len (datosCondactos[nombre][0][1]) != len (datosCondactos[nombre][1][1]):
              version = 1 if len (parametros) == len (datosCondactos[nombre][0][1]) else 2
              if version == 2:
                nueva_version.append (True)
            entrada.append ((datosCondactos[nombre][0][0], parametros))
            # TODO: poner a condactos anteriores con código diferente entre versiones, el de la versión 2
            if version == 2:
              pass
          # Comprobamos el número de parámetros
          if version and len (parametros) != len (datosCondactos[nombre][version - 1][1]):
            requerido = len (datosCondactos[nombre][version - 1][1])
            raise TabError ('El condacto %s requiere %d parámetro%s en DAAD versión %d (asumida por %s)', (nombre, requerido, '' if requerido == 1 else 's', version, 'condactos anteriores' if version == versionAntes else ('este mismo condacto, que sólo existe en la versión ' + str (version))), condacto.meta)
        entradas.append (entrada)
      tablas_proceso.append ((cabeceras, entradas))
      numProceso += 1
    return
  except (TabError, lark.UnexpectedCharacters, lark.UnexpectedInput) as e:
    if type (e) == TabError:
      descripcion   = e.args[0]
      paramsFormato = e.args[1]
      if descripcion[0].islower():
        descripcion = 'Se esperaba ' + descripcion
      if len (e.args) > 2:
        posicion     = e.args[2]
        descripcion += ', en línea %d'
        if type (paramsFormato) == tuple:
          paramsFormato += (posicion.line, )
        else:
          paramsFormato = (paramsFormato, posicion.line)
        if len (e.args) == 3:
          descripcion   += ' columna %d'
          paramsFormato += (posicion.column, )
      texto = descripcion % paramsFormato
    else:
      texto = e
    prn ('Formato del código fuente inválido o no soportado:', texto, file = sys.stderr, sep = '\n')
  except:
    pass
  return False

def comprueba_nombre (modulo, nombre, tipo):
  """Devuelve True si un nombre está en un módulo, y es del tipo correcto"""
  if (nombre in modulo.__dict__) and (type (modulo.__dict__[nombre]) == tipo):
    return True
  return False
