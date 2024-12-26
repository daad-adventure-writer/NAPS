# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Funciones de apoyo de alto nivel
# Copyright (C) 2010, 2021, 2023-2024 José Manuel Ferrer Ortiz
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

import gramatica


validar = False  # Si queremos validar el funcionamiento correcto del código

# Código de cada tipo de palabra por nombre en el código fuente
tipos_pal_dict = {'verb': 0, 'adverb': 1, 'noun': 2, 'adjective': 3, 'preposition': 4, 'conjugation': 5, 'conjunction': 5, 'pronoun': 6}

# Identificadores (para hacer el código más legible) predefinidos
IDS_LOCS = {'WORN': 253, 'CARRIED': 254, 'HERE': 255}


def carga_codigo_fuente (fichero, longitud, LONGITUD_PAL, atributos, atributos_extra, condactos, condactos_nuevos, conexiones, desc_locs, desc_objs, locs_iniciales, msgs_usr, msgs_sys, nombres_objs, nueva_version, num_objetos, tablas_proceso, vocabulario):
  """Carga la base de datos desde el código fuente SCE o DSF del fichero de entrada, con y sobre las variables pasadas como parámetro

  Para compatibilidad con el IDE:
  - Recibe como primer parámetro un fichero abierto
  - Recibe como segundo parámetro la longitud del fichero abierto
  - Devuelve False si ha ocurrido algún error"""
  global erExpresiones, erSimbolo, simbolos
  try:
    import re
    formato      = os.path.splitext (fichero.name)[1][1:].lower()  # Formato del código fuente, con valores posibles 'sce' o 'dsf'
    codigoFuente = fichero.read().replace (b'\r\n', b'\n').rstrip (b'\x1a').decode ('cp437' if formato == 'sce' else 'iso-8859-1')
    origenLineas = [[0, 0, codigoFuente.count ('\n') + 1, fichero.name, 0]]  # Inicio en código, inicio en fichero, nº líneas, ruta, nivel indentanción
    # Procesamos carga de ficheros externos con directivas de preprocesador /LNK e #include
    # TODO: extraer el código común con abreFichXMessages, a función en bajo_nivel
    encaje = True
    erLnk  = re.compile ('\n(/LNK|[ \t]*#include)[ \t]+([^ \n\t]+)', re.IGNORECASE)
    while encaje:
      encaje = erLnk.search (codigoFuente)
      if not encaje:
        break
      directiva  = encaje.group (1)
      nombreFich = encaje.group (2).lower().replace ('\\', os.sep)
      if '.' not in nombreFich:
        nombreFich += '.' + formato
      # Buscamos el fichero con independencia de mayúsculas y minúsculas
      rutaCarpeta = os.path.join (os.path.dirname (fichero.name), os.path.dirname (nombreFich))
      nombreFich  = os.path.basename (nombreFich)
      try:
        causa = 'No se encuentra la ruta "' + encaje.group (2)[:- len (nombreFich)] + '" requerida'
        for nombreFichero in os.listdir (rutaCarpeta):
          if os.path.basename (nombreFichero).lower() == nombreFich:
            nombreFich = nombreFichero
            break
        else:
          causa = 'No se encuentra el fichero "' + nombreFich + '" requerido'
          raise TabError
        causa      = 'No se puede abrir el fichero "' + nombreFich + '" requerido'
        ficheroLnk = open (os.path.join (rutaCarpeta, nombreFich), 'rb')
      except:
        prn (causa, 'por la directiva de preprocesador', directiva, encaje.group (2), file = sys.stderr)
        return False
      codigoIncluir = ficheroLnk.read().replace (b'\r\n', b'\n').rstrip (b'\x1a').decode ('cp437')
      lineaInicio   = codigoFuente[:encaje.start (0) + 1].count ('\n')  # Línea donde estaba la directiva, contando desde 0
      lineasIncluir = codigoIncluir.count ('\n') + 1  # Número de líneas del fichero a incluir
      restante      = ''  # Código restante detrás de la directiva
      # Buscamos el bloque de origenLineas donde está la línea de la directiva
      o = 0
      while o < len (origenLineas) and lineaInicio >= (origenLineas[o][0] + origenLineas[o][2]):
        o += 1
      nivelDirectiva = 0  # Nivel de indentación/anidación de esta directiva
      if len (directiva) == 4:  # Es una directiva /LNK
        if lineaInicio > origenLineas[o]:  # Quedará alguna línea en el bloque o de origenLineas
          origenLineas = origenLineas[:o + 1]  # Eliminamos desde este bloque en adelante exclusive
          origenLineas[o][2] = lineaInicio - origenLineas[o][0]  # Reducimos longitud del bloque
        else:  # La directiva estaba en la primera línea del bloque
          origenLineas = origenLineas[:o]  # Eliminamos desde este bloque en adelante inclusive
      else:  # Es una directiva include
        nivelDirectiva = origenLineas[o][4]
        if o < len (origenLineas) - 1:  # Hay más bloques detrás de éste, así que los extraemos
          finalOrigLineas = origenLineas[o + 1:]
          origenLineas    = origenLineas[:o + 1]
        else:  # Era el último bloque
          finalOrigLineas = []
        # Guardamos las líneas restantes en el fichero de este bloque, omitiendo la línea del include
        lineasRestantes     = origenLineas[o][2] - (lineaInicio + 1 - origenLineas[o][0])
        origenLineas[o][2] -= lineasRestantes + 1  # Reducimos longitud del bloque, el resto irá en otro
        # FIXME: caso cuando la directiva está en la primera línea del bloque
        nlTrasDirectiva     = codigoFuente.find ('\n', encaje.end (0))
        if nlTrasDirectiva > -1:  # Hay más código detrás de la directiva
          restante = codigoFuente[nlTrasDirectiva + (1 if codigoIncluir[-1] == '\n' else 0):]
      # Añadimos bloque del fichero que se incluye
      if codigoIncluir[-1] == '\n':  # La última línea del fichero a incluir es en blanco
        lineasIncluir -= 1
      nivelIncluir = nivelDirectiva + codigoFuente.find ('#', encaje.start (0) + 1) - (encaje.start (0) + 1)  # Nivel de indentación del fichero a incluir
      origenLineas.append ([lineaInicio, 0, lineasIncluir, os.path.normpath (ficheroLnk.name), nivelIncluir])
      # Añadimos los bloques posteriores
      if len (directiva) > 4:  # Es una directiva include
        origenLineas.append ([lineaInicio + lineasIncluir, origenLineas[o][1] + origenLineas[o][2] + 1, lineasRestantes, origenLineas[o][3], nivelDirectiva])
        # Incrementamos la posición de los demás y los añadimos al final
        for origenLinea in finalOrigLineas:
          origenLinea[0] = origenLineas[-1][0] + origenLineas[-1][2]
          origenLineas.append (origenLinea)
      # Añadimos si corresponde espacios antes de cada directiva del fichero a incluir
      erDirect = re.compile ('\n([ \t]*)#')  # Expresión regular para detectar directivas de preprocesador con #
      if nivelIncluir:
        codigoIncluir = erDirect.sub ('\n' + (' ' * nivelIncluir) + '\g<1>#', codigoIncluir)
      codigoFuente = codigoFuente[:encaje.start (0) + 1] + codigoIncluir + restante
      ficheroLnk.close()
      # Comprobamos que las líneas de codigoFuente corresponden con las líneas de los ficheros según origenLineas
      if validar:
        lineasCodigo = codigoFuente.split ('\n')
        for inicioCod, inicioFich, numLineas, rutaFichero, nivelIndent in origenLineas:
          ficheroPrueba = open (rutaFichero, 'rb')
          lineasFichero = ficheroPrueba.read().replace (b'\r\n', b'\n').rstrip (b'\x1a').decode ('cp437').split ('\n')
          for n in range (numLineas):
            if inicioFich + n == len (lineasFichero):
              prn ('El fichero', rutaFichero, 'sale en origenLineas con más líneas de las que tiene', file = sys.stderr)
              break
            lineaCodigo  = lineasCodigo[inicioCod + n]
            lineaFichero = lineasFichero[inicioFich + n]
            if erDirect.match ('\n' + lineasFichero[inicioFich + n]):
              lineaFichero = (' ' * nivelIndent) + lineaFichero
            if lineaCodigo != lineaFichero:
              prn (origenLineas, file = sys.stderr)
              prn ('La línea', inicioCod + n + 1, 'cargada no corresponde con la línea', inicioFich + n + 1, 'del fichero', rutaFichero, file = sys.stderr)
              contexto = 1  # Líneas de contexto que mostrar
              prn (lineasCodigo[inicioCod + n - contexto : inicioCod + n + contexto + 1], file = sys.stderr)
              prn ('versus', file = sys.stderr)
              prn (lineasFichero[inicioFich + n - contexto : inicioFich + n + contexto + 1], file = sys.stderr)
              sys.exit()
          ficheroPrueba.close()
    # Procesamos las demás directivas de preprocesador
    erExpresiones = re.compile ('([^ +-]+|[+-])')    # Expresión regular para partir expresiones de #define
    erPartirPals  = re.compile ('[ \t]+([^ \t]+)')   # Expresión regular para partir por palabras
    erSimbolo     = gramatica.terminales['símbolo']  # Expresión regular para detectar etiquetas de símbolos
    simbolos      = {'AMIGA': 0, 'C40': 0, 'C42': 0, 'C53': 1, 'CBM64': 0, 'CGA': 0, 'COLS': 53, 'CPC': 0, 'DEBUG': 0, 'DRAW': 0, 'EGA': 0, 'ENGLISH': 0, 'MSX': 0, 'PC': 1, 'PCW': 0, 'S48': 0, 'SP3': 0, 'SPANISH': 1, 'SPE': 0, 'ST': 0, 'VGA': 1}
    lineasCodigo  = codigoFuente.split ('\n')
    bloqueOrigen  = 0  # Número de bloque en origenLineas de la línea actual
    for numLinea in range (len (lineasCodigo)):
      if numLinea == origenLineas[bloqueOrigen][0] + origenLineas[bloqueOrigen][2]:
        bloqueOrigen += 1
      lineaCodigo = lineasCodigo[numLinea].lstrip()
      if not lineaCodigo or lineaCodigo[0] == ';' or lineaCodigo[0] != '#':
        continue  # Saltamos líneas vacías y sin directivas de preprocesador
      nivelDirect = len (lineasCodigo[numLinea]) - len (lineaCodigo)  # Nivel de indentación/anidación de la directiva
      if ';' in lineaCodigo:  # Quitamos comentarios
        lineaCodigo = lineaCodigo[: lineaCodigo.find (';')]
      if lineaCodigo[:7].lower() == '#define' or lineaCodigo[:4].lower() == '#var':
        encajesLinea = []
        for encaje in erPartirPals.finditer (lineaCodigo[4 if lineaCodigo[:4] == '#var' else 7:]):
          encajesLinea.append (encaje)
          if len (encajesLinea) > 1:
            break
        if not encajesLinea or encajesLinea[0].start():
          raise TabError ('espacio en blanco' + ('' if encajesLinea else ' y una etiqueta de símbolo'), (), (numLinea + 1, 8))
        simbolo = encajesLinea[0].group (1)
        if not erSimbolo.match (simbolo):
          raise TabError ('una etiqueta de símbolo válida', (), (numLinea + 1, 8 + encajesLinea[0].start (1)))
        if simbolo in simbolos and lineaCodigo[:4] != '#var':
          raise TabError ('El símbolo "%s" ya estaba definido', simbolo, (numLinea + 1, 8 + encajesLinea[0].start (1)))
        if len (encajesLinea) < 2:
          raise TabError ('expresión para definir el valor del símbolo', (), (numLinea + 1, len (lineaCodigo) + 1))
        valorExpr = daValorExpresion (lineaCodigo[7 + encajesLinea[1].start (1):], numLinea + 1, 8 + encajesLinea[1].start (1))
        # Asignamos el valor al símbolo, y comentamos la línea
        # TODO: cuando el IDE muestre líneas con comentarios y directivas de preprocesador, marcar diferenciando entre líneas deshabilitadas y procesadas
        simbolos[simbolo]      = valorExpr
        lineasCodigo[numLinea] = ';NAPS;' + lineasCodigo[numLinea]  # Ya procesada esta línea
      elif lineaCodigo[:3].lower() == '#if':
        encajesLinea = []
        for encaje in erPartirPals.finditer (lineaCodigo[3:]):
          encajesLinea.append (encaje)
          if len (encajesLinea) > 1:
            break
        if not encajesLinea or encajesLinea[0].start():
          raise TabError ('espacio en blanco' + ('' if encajesLinea else ' y una etiqueta de símbolo'), (), (numLinea + 1, 4))
        simbolo = encajesLinea[0].group (1)
        if simbolo[0] == '!':
          negado  = True
          simbolo = simbolo[1:]
        else:
          negado = False
        if not erSimbolo.match (simbolo):
          raise TabError ('una etiqueta de símbolo válida', (), (numLinea + 1, 4 + encajesLinea[0].start (1) + (1 if negado else 0)))
        if simbolo in simbolos:
          satisfecho = simbolos[simbolo]
          if negado:
            satisfecho = not satisfecho
          bloqueCond = bloqueOrigen  # Número de bloque en origenLineas de la línea condicional
          for numLineaCond in range (numLinea + 1, len (lineasCodigo)):
            if numLineaCond == origenLineas[bloqueCond][0] + origenLineas[bloqueCond][2]:
              bloqueCond += 1
            lineaCond = lineasCodigo[numLineaCond].lstrip()
            nivelCond = len (lineasCodigo[numLineaCond]) - len (lineaCond)  # Nivel de indentación/anidación de esta línea
            if nivelCond == nivelDirect:
              if lineaCond[:6].lower() == '#endif':
                lineasCodigo[numLineaCond] = ';NAPS;' + lineasCodigo[numLineaCond]  # Ya procesada esta línea
                break
              if lineaCond[:5].lower() == '#else':
                lineasCodigo[numLineaCond] = ';NAPS;' + lineasCodigo[numLineaCond]  # Ya procesada esta línea
                satisfecho = not satisfecho
                continue
            if satisfecho:  # Se cumple la condición de la directiva #if
              if (lineaCond[:1] != '#' and lineasCodigo[numLineaCond][:1] == ' ' and  # No es directiva y empieza por espacio
                  origenLineas[bloqueCond][3] == origenLineas[bloqueOrigen][3]):  # Es una línea del mismo fichero que la directiva if
                # Quitamos un nivel de indentación para que se pueda procesar correctamente la sintaxis de la línea
                lineasCodigo[numLineaCond] = lineasCodigo[numLineaCond][1:]
            else:  # No se cumple la condición de la directiva #if
              lineasCodigo[numLineaCond] = ';NAPS;' + lineasCodigo[numLineaCond]  # Deshabilitada esta línea
        else:
          raise TabError ('un símbolo ya definido', (), (numLinea + 1, 4 + encajesLinea[0].start (1)))
        lineasCodigo[numLinea] = ';NAPS;' + lineasCodigo[numLinea]  # Ya procesada la línea de la directiva #if
      elif lineaCodigo[:5].lower() == '#echo':
        prn (lineaCodigo[6:], file = sys.stderr)
        lineasCodigo[numLinea] = ';NAPS;' + lineasCodigo[numLinea]  # Ya procesada esta línea
      else:
        raise TabError ('una directiva de preprocesador válida', (), (numLinea + 1, 1))
    lineasCodigoUnidas = '\n'.join (lineasCodigo)
    reglaEntrada       = 'código fuente ' + formato.upper() + (' genérico' if formato == 'sce' else '')
    error, posicion, arbolCodigo = gramatica.analizaCadena (lineasCodigoUnidas, reglaEntrada)
    if error:
      raise TabError (error, (), posicion)
    # Cargamos cada tipo de textos
    sufijoFormato = ' en formato DSF' if formato == 'dsf' else ''
    for idSeccion, listaCadenas in (('STX', msgs_sys), ('MTX', msgs_usr), ('OTX', desc_objs), ('LTX', desc_locs)):
      nombreEntrada = 'entrada de ' + idSeccion + sufijoFormato
      nombreSeccion = 'sección '    + idSeccion + sufijoFormato
      posSeccion    = gramatica.reglas[reglaEntrada].index (nombreSeccion)
      posEntrada    = gramatica.reglas[nombreSeccion].index (nombreEntrada + '*')
      posNumero     = gramatica.reglas[nombreEntrada].index ('carácter /') + 1
      posLineas     = gramatica.reglas[nombreEntrada].index ('línea de texto*' if formato == 'sce' else 'cadena de texto entre comillas')
      numEntrada = 0
      for entrada in arbolCodigo[0][0][posSeccion][0][posEntrada]:
        if entrada:  # XXX: sólo debería estar vacía como mucho la última entrada
          numero, posicion = daValorArbolNumero (entrada[posNumero])
          if numero != numEntrada:
            raise TabError ('número de entrada %d en lugar de %d', (numEntrada, numero), posicion)
          if formato == 'sce':
            lineas = []
            for lineaTexto in entrada[posLineas]:
              linea = lineaTexto[0][0]
              if not lineas and linea[:1] == ';':
                continue  # Omitimos comentarios iniciales
              linea = linea.replace ('\\b', '\x0b').replace ('\\k', '\x0c').replace ('\\s', ' ').replace ('\\\\', '\\')
              lineas.append (linea)
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
          else:  # Es formato DSF
            cadena = entrada[posLineas][0][0][0][0][0] if entrada[posLineas][0][0] else entrada[posLineas][0][1][0][0][0]
            # XXX: ver si #b lo convierte DRC en espacio
            cadena = cadena.replace ('#b', '\x0b').replace ('#e', '€').replace ('#k', '\x0c').replace ('#n', '\n').replace ('#s', ' ').replace ('##', '#')
            cadena = cadena.replace ('\\b', '\x0b').replace ('\\k', '\x0c').replace ('\\s', ' ').replace ('\\\\', '\\')
          listaCadenas.append (str (cadena))  # Con str para que no sean cadenas unicode en Python 2, y así se pueda ejecutar translate sobre ellas
          numEntrada += 1
    # Cargamos el vocabulario
    adjetivos     = {gramatica.NULLWORD[0]: 255}
    adverbios     = {}
    nombres       = {gramatica.NULLWORD[0]: 255}
    preposiciones = {}
    verbos        = {gramatica.NULLWORD[0]: 255}
    tipoParametro = {'j': (adjetivos, 'adjetivo'), 'n': (nombres, 'nombre'), 'r': (preposiciones, 'preposición'), 'v': (adverbios, 'adverbio'), 'V': (verbos, 'verbo')}
    posSeccion = gramatica.reglas[reglaEntrada].index ('sección VOC')
    posEntrada = gramatica.reglas['sección VOC'].index ('entrada de vocabulario*')
    posPalabra = gramatica.reglas['entrada de vocabulario'].index ('palabra de vocabulario')
    posCodigo  = gramatica.reglas['entrada de vocabulario'].index ('número entero positivo')
    posTipo    = gramatica.reglas['entrada de vocabulario'].index ('tipo de palabra de vocabulario')
    for entrada in arbolCodigo[0][0][posSeccion][0][posEntrada]:
      if not entrada:
        continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
      palabra = entrada[posPalabra][0][0][0][:LONGITUD_PAL].lower()
      codigo  = int (entrada[posCodigo][0][0][0])
      tipo    = tipos_pal_dict[entrada[posTipo][0][0][0].lower()]
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
    posSeccion  = gramatica.reglas[reglaEntrada].index ('sección CON')
    posGrupo    = gramatica.reglas['sección CON'].index ('grupo de conexión*')
    posLocOrig  = gramatica.reglas['grupo de conexión'].index ('carácter /') + 1
    posConexion = gramatica.reglas['grupo de conexión'].index ('entrada de conexión*')
    posVerbo    = gramatica.reglas['entrada de conexión'].index ('palabra de vocabulario')
    posLocDest  = gramatica.reglas['entrada de conexión'].index ('expresión')
    numEntrada = 0
    for entrada in arbolCodigo[0][0][posSeccion][0][posGrupo]:
      if not entrada:
        continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
      numero, posicion = daValorArbolNumero (entrada[posLocOrig])
      if numero != numEntrada:
        raise TabError ('número de localidad %d en lugar de %d', (numEntrada, numero), posicion)
      salidas = []
      for conexion in entrada[posConexion]:
        if not conexion:
          continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
        encajesVerbo, posicion = conexion[posVerbo][0]
        verbo = encajesVerbo[0][:LONGITUD_PAL].lower()
        if verbo not in verbos:
          raise TabError ('una palabra de vocabulario de tipo verbo', (), posicion)
        destino, posicion = daValorArbolExpresion (conexion[posLocDest])
        if destino >= len (desc_locs):
          raise TabError ('número de localidad entre 0 y %d', len (desc_locs) - 1, posicion)
        salidas.append ((verbos[verbo], destino))
      conexiones.append (salidas)
      numEntrada += 1
    if numEntrada != len (desc_locs):
      raise TabError ('el mismo número de entradas de conexión (hay %d) que de descripciones de localidades (hay %d)', (numEntrada, len (desc_locs)))
    # Cargamos datos de los objetos
    posSeccion = gramatica.reglas[reglaEntrada].index ('sección OBJ')
    posEntrada = gramatica.reglas['sección OBJ'].index ('entrada de objeto*')
    posNumero  = gramatica.reglas['entrada de objeto'].index ('carácter /') + 1
    posLocIni  = posNumero + 2
    posPeso    = gramatica.reglas['entrada de objeto'].index ('número entero positivo')
    posResto   = len (gramatica.reglas['entrada de objeto']) - 1
    posEspacio = gramatica.reglas['atributo'].index ('espacio en blanco')
    posNombre  = -4  # Dónde está la palabra del nombre del objeto en la lista del resto de la entrada de objeto
    numEntrada = 0
    for entrada in arbolCodigo[0][0][posSeccion][0][posEntrada]:
      if not entrada:
        continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
      numero, posicion = daValorArbolNumero (entrada[posNumero])
      if numero != numEntrada:
        raise TabError ('número de objeto %d en lugar de %d', (numEntrada, numero), posicion)
      # Cargamos la localidad inicial del objeto
      for opcion in entrada[posLocIni]:
        if not opcion:
          continue
        if type (opcion[0][0][0]) == list:  # Es una expresión
          localidad, posicion = daValorArbolExpresion (opcion)
        elif opcion[0][0][0] == gramatica.NULLWORD[0]:
          localidad = 252
        else:  # Valor no numérico (p.ej. CARRIED)
          localidad = IDS_LOCS[opcion[0][0][0]]
      locs_iniciales.append (localidad)
      # Cargamos el peso del objeto
      encajesPeso, posicion = entrada[posPeso][0]
      peso = int (encajesPeso[0])
      if peso < 0 or peso > 63:
        raise TabError ('valor de peso del objeto %d entre 0 y 63', numEntrada, posicion)
      # Cargamos los atributos del objeto
      if entrada[posResto][0]:
        numAtributos = 2
        restoEntrada = entrada[posResto][0]
      else:
        numAtributos = 18
        restoEntrada = entrada[posResto][1]
      valorAttrs = ''
      for arbolAtributo in restoEntrada[:numAtributos]:
        arbolAtributo = arbolAtributo[0][1 - posEspacio][0] if arbolAtributo[0][1 - posEspacio][0] else arbolAtributo[0][1 - posEspacio][1]
        valorAttrs   += '1' if arbolAtributo[0][0][0] == 'Y' else '0'
      atributos.append (peso + ((valorAttrs[0] == '1') << 6) + ((valorAttrs[1] == '1') << 7))
      if valorAttrs[2:]:
        atributos_extra.append (int (valorAttrs[2:], 2))
      # Cargamos el vocabulario del objeto
      palabras = []
      for posPalabra in range (posNombre, posNombre + 3, 2):
        arbolPalabra = restoEntrada[posPalabra][0][0] if restoEntrada[posPalabra][0][0] else restoEntrada[posPalabra][0][1]
        encajesPalabra, posicion = arbolPalabra[0]
        palabra = encajesPalabra[0][:LONGITUD_PAL].lower()
        palabras.append (palabra)
        if len (palabras) == 1 and palabra not in nombres:
          break  # Para conservar la posición de la primera palabra inexistente
      if palabras[0] not in nombres or palabras[1] not in adjetivos:
        raise TabError ('una palabra de vocabulario de tipo %s', 'adjetivo' if len (palabras) > 1 else 'nombre', posicion)
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
        if not condactos_nuevos or condacto[4] == 3:  # Para sistemas distintos a DAAD o si el condacto es igual en ambas versiones
          datosCondactos[condacto[0]] = (datosCondacto, datosCondacto)
        else:  # Condacto para una versión específica
          datosCondactos[condacto[0]][condacto[4] - 1] = datosCondacto
    if condactos_nuevos:  # Sólo para DAAD
      datosCondactos['DEBUG'] = ((220, ''), (220, ''))  # NEWTEXT con indirección
    # Cargamos las tablas de proceso
    posSeccion   = gramatica.reglas[reglaEntrada].index ('sección PRO' + sufijoFormato + '+')
    posNumero    = gramatica.reglas['sección PRO' + sufijoFormato].index ('expresión')
    posEntrada   = gramatica.reglas['sección PRO' + sufijoFormato].index ('entrada de proceso' + sufijoFormato + '*')
    posEtiqueta  = gramatica.reglas['entrada de proceso' + sufijoFormato].index ('línea de etiqueta?')
    posVerbo     = gramatica.reglas['entrada de proceso' + sufijoFormato].index ('palabra')
    posCondacto  = gramatica.reglas['entrada de proceso' + sufijoFormato].index ('condacto en misma línea' + sufijoFormato + '?')
    posCondactos = gramatica.reglas['entrada de proceso' + sufijoFormato].index ('condacto' + sufijoFormato + '*')
    posNombre    = gramatica.reglas['condacto' + sufijoFormato].index ('nombre de condacto')
    posParametro = gramatica.reglas['condacto' + sufijoFormato].index ('parámetro' + sufijoFormato + '*')
    assert gramatica.reglas['condacto en misma línea' + sufijoFormato][:3] == gramatica.reglas['condacto' + sufijoFormato][:3]
    numProceso = 0
    version    = 0  # Versión de DAAD necesaria, 0 significa compatibilidad con ambas
    listaCadenasPorPrefijo   = {'D': desc_locs, 'M': msgs_usr, 'S': msgs_sys}  # TODO: XMessages
    nombreListaCadPorPrefijo = {'D': 'descripciones de localidad', 'M': 'mensajes de usuario', 'S': 'mensajes de sistema'}
    for seccion in arbolCodigo[0][0][posSeccion]:
      if not seccion:
        continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
      numero, posicion = daValorArbolExpresion (seccion[posNumero])
      if numero != numProceso:
        raise TabError ('número de proceso %d en lugar de %d', (numProceso, numero), posicion)
      # Guardamos las posiciones de las etiquetas de entrada
      etiquetas  = {}
      numEntrada = 0
      for arbolEntrada in seccion[posEntrada]:
        if not arbolEntrada:
          continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
        if arbolEntrada[posEtiqueta][0]:  # Tiene etiqueta
          encajesEtiqueta, posicion = arbolEntrada[posEtiqueta][0][0][0]
          etiqueta = encajesEtiqueta[0]
          if etiqueta in etiquetas:
            raise TabError ('Etiqueta %s ya existente para el proceso %d', (etiqueta, numero), posicion)
          etiquetas[etiqueta] = numEntrada
        numEntrada += 1
      # Cargamos cada entrada del proceso
      cabeceras = []
      entradas  = []
      for arbolEntrada in seccion[posEntrada]:
        if not arbolEntrada:
          continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
        palabras = []
        for posPalabra in range (posVerbo, posVerbo + 3, 2):
          arbolPalabra = arbolEntrada[posPalabra][0][0] if arbolEntrada[posPalabra][0][0] else arbolEntrada[posPalabra][0][1]
          encajesPalabra, posicion = arbolPalabra[0]
          palabra = encajesPalabra[0][:LONGITUD_PAL].lower()
          palabras.append (palabra)
          if len (palabras) == 1 and palabra not in verbos:
            break  # Para conservar la posición de la primera palabra inexistente
        if palabras[0] not in verbos or palabras[1] not in nombres:
          raise TabError ('una palabra de vocabulario de tipo %s', 'nombre' if len (palabras) > 1 else 'verbo', posicion)
        cabeceras.append ((verbos[palabras[0]], nombres[palabras[1]]))
        # Juntamos en una lista el condacto en la misma línea si hay, y los condactos posteriores si los hay
        arbolCondactos = []
        if arbolEntrada[posCondacto][0]:
          arbolCondactos.append (arbolEntrada[posCondacto][0])
        if arbolEntrada[posCondactos]:
          arbolCondactos.extend (arbolEntrada[posCondactos])
        entrada = []
        for arbolCondacto in arbolCondactos:
          if not arbolCondacto:
            continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
          indireccion = 0  # Tomará valor 128 cuando el condacto se use con indirección
          encajesNombre, posicionCondacto = arbolCondacto[posNombre][0]
          nombre = encajesNombre[0].upper()
          if nombre not in datosCondactos:
            raise TabError ('Condacto de nombre %s inexistente', nombre, posicionCondacto)
          parametros = []
          for arbolParametro in arbolCondacto[posParametro]:
            if arbolParametro:  # XXX: sólo debería estar vacía como mucho la última entrada
              o      = len (arbolParametro[1]) - 1
              opcion = arbolParametro[1][o]
              if o == 2:  # Es una regla de indirección
                if not condactos_nuevos:
                  raise TabError ('Este sistema no soporta indirección de parámetros', (), opcion[0][0][0][1])
                if parametros:
                  raise TabError ('Sólo se soporta indirección en el primer parámetro', (), opcion[0][0][0][1])
                indireccion = 128
                parametros.append (daValorArbolExpresion (opcion[0][1])[0])
              elif o == 0:  # Es una expresión
                valor, posicion = daValorArbolExpresion (opcion, False)
                if valor == None:
                  o = 1  # Considerarlo como palabra de vocabulario, CARRIED, HERE o WORN
                else:
                  parametros.append (valor)
              if o == 1:  # Es una palabra (de vocabulario o NULLWORD)
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
                  if len (arbolParametro[1]) == 1:  # Se había llegado aquí desde el caso anterior, habiéndose considerado ya como expresión, sin éxito
                    if opcion[0][0][0][0][0][0][0] in IDS_LOCS:  # CARRIED, HERE o WORN
                      parametros.append (IDS_LOCS[opcion[0][0][0][0][0][0][0]])
                      continue
                    raise TabError ('un símbolo ya definido', (), posicion)
                  raise TabError ('El condacto %s no admite una palabra de vocabulario como parámetro aquí', nombre, opcion[0][0][0][1])
                # Salvo SYNONYM, los condactos con este tipo de parámetro sólo tienen uno de igual tipo en ambas versiones de DAAD, por lo que podemos
                # revisar sólo el tipo de parámetros de la versión 2 del condacto
                encajesPalabra, posicion = opcion[0][0][0] if len (arbolParametro[1]) > 1 else opcion[0][0][0][0][0]
                palabra      = encajesPalabra[0][:LONGITUD_PAL].lower()
                letraTipoPal = datosCondactos[nombre][1][1][len (parametros)]
                listaVocab, tipoPalabra = tipoParametro[letraTipoPal]
                if palabra not in listaVocab:
                  raise TabError ('una palabra de vocabulario de tipo %s', tipoPalabra, posicion)
                parametros.append (listaVocab[palabra])
              elif o == 3:  # Es una etiqueta
                encajesEtiqueta, posicion = opcion[0]
                etiqueta = encajesEtiqueta[0]
                if etiqueta not in etiquetas:
                  raise TabError ('una etiqueta existente en este proceso', (), posicion)
                salto = etiquetas[etiqueta] - len (entradas) - 1
                if salto < -127 or salto > 128:
                  raise TabError ('una etiqueta más cercana', (), posicion)
                if salto < 0:
                  salto += 256
                parametros.append (salto)
              elif o == 4:  # Es un número entero (negativo o se habría detectado como expresión)
                parametros.append (int (opcion[0][0][0]))
              elif o == 5:  # Es una cadena de texto
                encajesCadena, posicion = opcion[0][0][0]
                for c in range (len (listaCadenasPorPrefijo[nombre[0]])):
                  if listaCadenasPorPrefijo[nombre[0]][c] == encajesCadena[0]:
                    parametros.append (c)
                    break
                else:
                  if len (listaCadenasPorPrefijo[nombre[0]]) == 256:
                    raise TabError ('La lista de ' + nombreListaCadPorPrefijo[nombre[0]] + ' ya tiene 256 entradas, no cabe esta cadena', (), posicion)
                  parametros.append (len (listaCadenasPorPrefijo[nombre[0]]))
                  listaCadenasPorPrefijo[nombre[0]].append (encajesCadena[0])
          # Detectamos incompatibilidades por requerirse versiones de DAAD diferentes
          versionAntes = version
          if version:
            if not datosCondactos[nombre][version - 1]:
              raise TabError ('Condacto de nombre %s inexistente en DAAD versión %d (asumida por condactos anteriores)', (nombre, version), posicionCondacto)
            # La comprobación del número de parámetros se hace abajo
            entrada.append ((datosCondactos[nombre][version - 1][0] + indireccion, parametros))
          else:
            # Fijamos versión de DAAD si el condacto con ese nombre sólo está en una
            if not datosCondactos[nombre][0] or not datosCondactos[nombre][1]:
              version = 1 if datosCondactos[nombre][0] else 2
            elif len (parametros) != len (datosCondactos[nombre][0][1]) and len (parametros) != len (datosCondactos[nombre][1][1]):
              if len (datosCondactos[nombre][0][1]) == len (datosCondactos[nombre][1][1]):
                requerido = len (datosCondactos[nombre][0][1])
              else:
                requerido = ' o '.join (sorted ((len (datosCondactos[nombre][0][1]), len (datosCondactos[nombre][1][1]))))
              raise TabError ('El condacto %s requiere %d parámetro%s', (nombre, requerido, '' if requerido == 1 else 's'), posicionCondacto)
            # Fijamos versión de DAAD si el condacto con ese número de parámetros sólo está en una
            elif len (datosCondactos[nombre][0][1]) != len (datosCondactos[nombre][1][1]):
              version = 1 if len (parametros) == len (datosCondactos[nombre][0][1]) else 2
            entrada.append ((datosCondactos[nombre][0][0] + indireccion, parametros))
            # TODO: poner a condactos anteriores con código diferente entre versiones, el de la versión 2
            if version == 2:
              pass
          # Comprobamos el número de parámetros
          if version and len (parametros) != len (datosCondactos[nombre][version - 1][1]):
            requerido = len (datosCondactos[nombre][version - 1][1])
            raise TabError ('El condacto %s requiere %d parámetro%s en DAAD versión %d (asumida por %s)', (nombre, requerido, '' if requerido == 1 else 's', version, 'condactos anteriores' if version == versionAntes else ('este mismo condacto, que sólo existe en la versión ' + str (version))), posicionCondacto)
        entradas.append (entrada)
      tablas_proceso.append ((cabeceras, entradas))
      numProceso += 1
    if version == 2:
      condactos.update (condactos_nuevos)
      nueva_version.append (True)
    return
  except TabError as e:
    detalles      = ''
    numColumna    = None
    numLinea      = None
    textoPosicion = ''
    descripcion   = e.args[0]
    paramsFormato = e.args[1]
    if descripcion[0] == '/' or descripcion[0].islower() or descripcion[1].isupper():
      if formato == 'dsf':
        descripcion = descripcion.replace (' en formato DSF', '')
      descripcion = 'Se esperaba ' + descripcion
    descripcion = descripcion % paramsFormato
    if len (e.args) > 2:
      posicion = e.args[2]
      if type (posicion) == tuple:
        numLinea = posicion[0]
        if len (e.args) == 3:
          numColumna = posicion[1]
      elif type (posicion) == int and posicion != 999999999:
        codigoHastaError = lineasCodigoUnidas[:posicion]
        numLinea         = codigoHastaError.count ('\n') + 1
        ultimaNL         = codigoHastaError.rfind ('\n')
        numColumna       = posicion - (ultimaNL if numLinea > 1 else 0)
    if numLinea != None:  # Disponemos del número de línea del error
      # Buscamos el bloque de origenLineas donde está la línea del error
      o = 0
      while o < len (origenLineas) and numLinea > (origenLineas[o][0] + origenLineas[o][2]):
        o += 1
      inicioCod, inicioFich, numLineas, rutaFichero, nivelIndent = origenLineas[o]
      textoPosicion = (';' if ',' in descripcion else ',') + ' en línea ' + str (inicioFich + numLinea - inicioCod)
      if numColumna != None:
        textoPosicion += ' columna ' + str (numColumna)
      textoPosicion += ' de ' + rutaFichero
    prn ('Formato del código fuente inválido o no soportado:', descripcion + textoPosicion + detalles, file = sys.stderr, sep = '\n')
  except UnicodeDecodeError as e:
    prn ('Error de codificación en el código fuente, que debe usar codificación cp437:', e, file = sys.stderr, sep = '\n')
  except Exception as e:
    prn ('Error imprevisto:', e, file = sys.stderr, sep = '\n')
    import traceback
    traceback.print_exc()
  return False

def comprueba_nombre (modulo, nombre, tipo):
  """Devuelve True si un nombre está en un módulo, y es del tipo correcto"""
  if (nombre in modulo.__dict__) and (type (modulo.__dict__[nombre]) == tipo):
    return True
  return False


# Funciones auxiliares que sólo se usan en este módulo

def daValorArbolExpresion (arbolExpresion, errorSimbolo = True):
  """Evalúa y devuelve el valor de un arbol de expresión, compuesta por símbolos, operadores y/o números; y la posición en el código fuente donde empieza

  errorSimbolo indica si se desea producir excepción si la expresión no tiene operaciones y no existe símbolo con el nombre contenido en la expresión, o por el contrario se devuelve None como valor
  """
  global posOperadorEnOperacion, posSimboloEnEnteroOSimbolo, posSimboloEnOperacion
  try:
    posOperadorEnOperacion
  except:
    posOperadorEnOperacion = gramatica.reglas['operación'].index ('operador')
    posSimboloEnOperacion  = gramatica.reglas['operación'].index ('entero positivo o símbolo')
  arbolEnteroOSimbolo, arbolOperaciones = arbolExpresion[0]
  if arbolEnteroOSimbolo[0][0] == []:  # Ocurre con enteros detectados como expresión
    enteroComoExpresion = True
    arbolEnteroOSimbolo = arbolEnteroOSimbolo[0]
  else:
    enteroComoExpresion = False
  arbolEnteroOSimbolo = arbolEnteroOSimbolo[0] if arbolEnteroOSimbolo[0] else arbolEnteroOSimbolo[1]
  if type (arbolEnteroOSimbolo[0][0]) == tuple:  # Ocurre así en las expresiones genéricas (las que no impiden ningún símbolo específico)
    if enteroComoExpresion:
      arbolEnteroOSimbolo = arbolEnteroOSimbolo[0]
    else:
      arbolEnteroOSimbolo = arbolEnteroOSimbolo[0][0]
  listaEncajes, posicionInicio = arbolEnteroOSimbolo
  if arbolEnteroOSimbolo[0][0].isnumeric():
    valorExpr = int (listaEncajes[0])
  else:
    if listaEncajes[0] in simbolos:
      valorExpr = simbolos[listaEncajes[0]]
    else:
      if errorSimbolo or arbolOperaciones[0]:
        raise TabError ('un símbolo ya definido', (), posicionInicio)
      return None, posicionInicio
  for arbolOperacion in arbolOperaciones:
    if not arbolOperacion:
      continue  # Continuamos aunque sólo debería estar vacía como mucho la última entrada
    listaEncajes, posicion = arbolOperacion[posOperadorEnOperacion][0]
    operador = listaEncajes[0][0]
    arbolEnteroOSimbolo = arbolOperacion[posSimboloEnOperacion][0]
    if arbolEnteroOSimbolo[0]:  # Tiene valor la primera posición
      arbolEnteroOSimbolo = arbolEnteroOSimbolo[0]
    else:
      arbolEnteroOSimbolo = arbolEnteroOSimbolo[1]
    if arbolEnteroOSimbolo[0][0][0].isnumeric():  # Es un entero
      numero = int (arbolEnteroOSimbolo[0][0][0])
    else:
      listaEncajes, posicion = arbolEnteroOSimbolo[0]
      if listaEncajes[0] in simbolos:
        numero = simbolos[listaEncajes[0]]
      else:
        raise TabError ('un símbolo ya definido', (), posicion)
    if operador == '+':  # Ya teníamos valor y operador
      valorExpr += numero
    else:
      valorExpr -= numero
  return valorExpr, posicionInicio

def daValorArbolNumero (arbolNumero):
    """Devuelve el valor entero resultante a partir de un árbol con un valor entero, símbolo o expresión; y la posición en el código fuente donde empieza"""
    arbolNumero = arbolNumero[0] if arbolNumero[0] else arbolNumero[1]
    if type (arbolNumero[0][0][0]) == tuple:  # Es una expresión
      numero, posicion = daValorArbolExpresion (arbolNumero)
    else:  # Es un entero
      numero   = int (arbolNumero[0][0][0])
      posicion = arbolNumero[0][1]
    return numero, posicion

def daValorExpresion (exprOpartesExpr, numLinea = None, colInicial = None):
  """Evalúa y devuelve el valor de una expresión compuesta por símbolos, operadores y/o números"""
  operador   = None  # Operador pendiente de aplicar
  valorExpr  = None  # Valor hasta el momento de la expresión
  paramEsStr = type (exprOpartesExpr) in (str, str if sys.version_info[0] > 2 else unicode)
  partesExpresion = erExpresiones.finditer (exprOpartesExpr) if paramEsStr else exprOpartesExpr
  for parte in partesExpresion:
    parteExpr = parte.group (0) if paramEsStr else str (parte)
    if valorExpr == None or operador != None:  # No tenemos valor o bien ya tenemos valor y operador
      if parteExpr.isdigit():
        numero = int (parteExpr)
      elif erSimbolo.match (parteExpr):
        if parteExpr in simbolos:
          numero = simbolos[parteExpr]
        else:
          raise TabError ('un símbolo ya definido', (), (numLinea, colInicial + parte.start()) if paramEsStr else parte)
      else:
        raise TabError ('número o etiqueta de símbolo', (), (numLinea, colInicial + parte.start()) if paramEsStr else parte)
      if valorExpr == None:  # No teníamos valor
        valorExpr = numero
      elif operador == '+':  # Ya teníamos valor y operador
        valorExpr += numero
      else:
        valorExpr -= numero
      operador = None
    else:  # Tenemos valor pero no hay operador
      if parteExpr in '+-':
        operador = parteExpr
      else:
        raise TabError ('operador de suma o resta', (), (numLinea, colInicial + parte.start()) if paramEsStr else parte)
  return valorExpr
