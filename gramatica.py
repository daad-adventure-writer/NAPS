# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Analizador sint�ctico para cargar r�pida y c�modamente c�digo fuente SCE y DSF
# Copyright (C) 2023-2025 Jos� Manuel Ferrer Ortiz

import re

from sys import version_info

from prn_func import prn


# Variables que se pueden utilizar fuera del m�dulo

NULLWORD = ['_']

terminales = {
  'car�cter de NULLWORD':   re.compile ('(_)'),  # Puede cambiar al procesar la entrada de NULLWORD
  'espacio en blanco':      re.compile ('[ \t]+'),
  'n�mero entero':          re.compile (r'([+\-]?[0-9]+)'),
  'n�mero entero positivo': re.compile ('([0-9]+)'),
  'fin de l�nea opcionalmente tras espacio en blanco y/o comentario': re.compile ('[ \t]*(?:;([^\n]*))?\n'),
  # De la secci�n CTL
  '/CTL':     re.compile ('(/CTL)'),
  'DBDRIVE':  re.compile ('([A-Q])'),  # Unidad de la base de datos en CP/M de la A a la P, o Q para indicar c�digo fuente de Quill
  'NULLWORD': re.compile (r'([!-\*,-.<-@\[-`{-~])'),
  # De la secci�n TOK
  '/TOK':  re.compile ('(/TOK)'),
  'token': re.compile ('([^ ;/\n\t][^ ;\n\t]+)(?:[ \t]*(?:;[^\n]*)?\n)+'),
  # De la secci�n VOC
  '/VOC':                           re.compile ('(/VOC)'),
  'palabra de vocabulario':         re.compile ('([0-9A-Za-z������������]+)'),  # TODO: a�adir caracteres restantes que permite el idioma espa�ol
  'tipo de palabra de vocabulario': re.compile ('(ADJECTIVE|ADVERB|CONJUGATION|CONJUNCTION|NOUN|PREPOSITION|PRONOUN|VERB)', re.IGNORECASE),
  # De las secciones STX, MTX, OTX y LTX
  '/LTX':                   re.compile ('(/LTX)'),
  '/MTX':                   re.compile ('(/MTX)'),
  '/OTX':                   re.compile ('(/OTX)'),
  '/STX':                   re.compile ('(/STX)'),
  'car�cter /':             re.compile ('(/)'),
  'l�nea de texto':         re.compile ('(?!/)([^\n]*)\n'),
  'operador':               re.compile ('([+-])'),
  's�mbolo':                re.compile ('([A-Z_a-z��][0-9A-Z_a-z��]*)'),
  's�mbolo que no sea CON': re.compile ('(?!CON)([A-Z_a-z][0-9A-Z_a-z]*)'),
  's�mbolo que no sea LTX': re.compile ('(?!LTX)([A-Z_a-z][0-9A-Z_a-z]*)'),
  's�mbolo que no sea MTX': re.compile ('(?!MTX)([A-Z_a-z][0-9A-Z_a-z]*)'),
  's�mbolo que no sea OTX': re.compile ('(?!OTX)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'cadena de texto entre comillas dobles':  re.compile ('"(.*)"'),
  'cadena de texto entre comillas simples': re.compile ("'(.*)'"),
  # De la secci�n CON
  '/CON':                   re.compile ('(/CON)'),
  's�mbolo que no sea OBJ': re.compile ('(?!OBJ)([A-Z_a-z][0-9A-Z_a-z]*)'),
  # De la secci�n OBJ
  '/OBJ':                   re.compile ('(/OBJ)'),
  's�mbolo que no sea PRO': re.compile ('(?!PRO)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'CARRIED':                re.compile ('(CARRIED)'),
  'WORN':                   re.compile ('(WORN)'),
  'car�cter Y':             re.compile ('(Y)'),
  # De la secci�n PRO
  '/PRO':               re.compile ('(/PRO)'),
  'car�cter @':         re.compile ('(@)'),
  'car�cter [':         re.compile (r'(\[)'),
  'car�cter ]':         re.compile (r'(\])'),
  'etiqueta':           re.compile (r'\$([A-Za-z�][0-9A-Za-z�]*)'),
  'nombre de condacto': re.compile ('([A-Z][0-9A-Z]*)', re.IGNORECASE),
  'signo mayor que':    re.compile ('(>)'),
  'HERE':               re.compile ('(HERE)'),
  # Marcador de fin de c�digo en formato DSF
  '/END':               re.compile ('(/END)'),
}

# Listas [] implican condici�n Y, tuplas () implican condici�n O. En estas �ltimas se puede usar None para volver opcional la regla padre
reglas = {
  'c�digo fuente SCE gen�rico': [
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario*',
    'secci�n CTL?',
    'secci�n TOK?',
    'secci�n VOC',
    'secci�n STX',
    'secci�n MTX',
    'secci�n OTX',
    'secci�n LTX',
    'secci�n CON',
    'secci�n OBJ',
    'secci�n PRO+',
  ],
  'c�digo fuente QSE': [
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario*',
    'secci�n CTL',
    'secci�n VOC en formato QSE',
    'secci�n STX',
    'secci�n MTX',
    'secci�n OTX',
    'secci�n LTX',
    'secci�n CON',
    'secci�n OBJ en formato QSE',
    'secci�n PRO+',
  ],
  'c�digo fuente DSF': [
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario*',
    'secci�n CTL en formato DSF?',
    'secci�n TOK?',
    'secci�n VOC',
    'secci�n STX en formato DSF',
    'secci�n MTX en formato DSF',
    'secci�n OTX en formato DSF',
    'secci�n LTX en formato DSF',
    'secci�n CON',
    'secci�n OBJ',
    'secci�n PRO en formato DSF+',
    '/END',
  ],
  'secci�n CTL': [
    '/CTL',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'opci�n DBDRIVE?',  # Usado en formato QSE y en CP/M para indicar la letra de unidad donde guardar la base de datos
    'NULLWORD',
    'opci�n llevables?',  # N�mero de objetos llevables en formato QSE
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'opci�n DBDRIVE': [
    'DBDRIVE',  # Unidad de la base de datos en CP/M de la A a la P, o Q para indicar c�digo fuente de Quill
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'secci�n CTL en formato DSF': [
    '/CTL',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'opci�n NULLWORD?',
  ],
  'opci�n NULLWORD': [
    'NULLWORD',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'opci�n llevables': [
    'n�mero entero positivo',  # N�mero de objetos llevables
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'secci�n TOK': [
    '/TOK',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'token*',
  ],
  'secci�n VOC': [
    '/VOC',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de vocabulario*',
  ],
  'entrada de vocabulario': [
    'espacio en blanco?',
    'palabra de vocabulario',
    'espacio en blanco',
    'n�mero entero positivo',
    'espacio en blanco',
    'tipo de palabra de vocabulario',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'secci�n VOC en formato QSE': [
    '/VOC',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de vocabulario en formato QSE*',
  ],
  'entrada de vocabulario en formato QSE': [
    'espacio en blanco?',
    'palabra de vocabulario',
    'espacio en blanco',
    'n�mero entero positivo',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'secci�n STX': [
    '/STX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de STX*'
  ],
  'entrada de STX': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea MTX',
    ),
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario',
    'l�nea de texto*',
  ],
  'secci�n STX en formato DSF': [
    '/STX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de STX en formato DSF*'
  ],
  'entrada de STX en formato DSF': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea MTX',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresi�n que no sea MTX': [
    's�mbolo que no sea MTX',
    'operaci�n*',
  ],
  'cadena de texto entre comillas': (
    'cadena de texto entre comillas dobles',
    'cadena de texto entre comillas simples',
  ),
  'secci�n MTX': [
    '/MTX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de MTX*'
  ],
  'entrada de MTX': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea OTX',
    ),
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario',
    'l�nea de texto*',
  ],
  'secci�n MTX en formato DSF': [
    '/MTX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de MTX en formato DSF*'
  ],
  'entrada de MTX en formato DSF': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea OTX',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresi�n que no sea OTX': [
    's�mbolo que no sea OTX',
    'operaci�n*',
  ],
  'secci�n OTX': [
    '/OTX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de OTX*'
  ],
  'entrada de OTX': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea LTX',
    ),
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario',
    'l�nea de texto*',
  ],
  'secci�n OTX en formato DSF': [
    '/OTX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de OTX en formato DSF*'
  ],
  'entrada de OTX en formato DSF': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea LTX',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresi�n que no sea LTX': [
    's�mbolo que no sea LTX',
    'operaci�n*',
  ],
  'secci�n LTX': [
    '/LTX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de LTX*'
  ],
  'entrada de LTX': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea CON',
    ),
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario',
    'l�nea de texto*',
  ],
  'secci�n LTX en formato DSF': [
    '/LTX',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de LTX en formato DSF*'
  ],
  'entrada de LTX en formato DSF': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea CON',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresi�n que no sea CON': [
    's�mbolo que no sea CON',
    'operaci�n*',
  ],
  'operaci�n': [
    'espacio en blanco?',
    'operador',
    'espacio en blanco?',
    'entero positivo o s�mbolo',
  ],
  'entero positivo o s�mbolo': (
    's�mbolo',
    'n�mero entero positivo',
  ),
  'secci�n CON': [
    '/CON',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'grupo de conexi�n*',
  ],
  'grupo de conexi�n': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea OBJ',
    ),
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de conexi�n*',
  ],
  'expresi�n que no sea OBJ': [
    's�mbolo que no sea OBJ',
    'operaci�n*',
  ],
  'entrada de conexi�n': [
    'espacio en blanco?',
    'palabra de vocabulario',
    'espacio en blanco',
    'expresi�n',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'palabra': (
    'palabra de vocabulario',
    'car�cter de NULLWORD',
  ),
  'secci�n OBJ': [
    '/OBJ',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de objeto*',
  ],
  'entrada de objeto': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea PRO',
    ),
    'espacio en blanco',
    (  # Localidad inicial
      'CARRIED',
      'WORN',
      'car�cter de NULLWORD',  # No creados
      'expresi�n',
    ),
    'espacio en blanco',
    'n�mero entero positivo',  # Peso
    # XXX: considerar hacer esto mejor, como especificando n�mero de veces que debe aparecer una regla, pero sin perjudicar la eficiencia
    (
      [  # Variante con dos atributos
        'atributo',  # Contenedor
        'atributo',  # Llevable
        'espacio en blanco',
        'palabra',  # Nombre
        'espacio en blanco',
        'palabra',  # Adjetivo
        'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
      ], [  # Variante con 18 atributos
        'atributo',  # Contenedor
        'atributo',  # Llevable
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'atributo',
        'espacio en blanco',
        'palabra',  # Nombre
        'espacio en blanco',
        'palabra',  # Adjetivo
        'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
      ],
    ),
  ],
  'secci�n OBJ en formato QSE': [
    '/OBJ',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de objeto en formato QSE*',
  ],
  'entrada de objeto en formato QSE': [
    'car�cter /',
    (
      'n�mero entero positivo',
      'expresi�n que no sea PRO',
    ),
    'espacio en blanco',
    (  # Localidad inicial
      'CARRIED',
      'WORN',
      'car�cter de NULLWORD',  # No creados
      'expresi�n',
    ),
    'espacio en blanco',
    'palabra',  # Nombre
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresi�n que no sea PRO': [
    's�mbolo que no sea PRO',
    'operaci�n*',
  ],
  'atributo': [
    'espacio en blanco',
    (
      'car�cter Y',
      'car�cter de NULLWORD',
    ),
  ],
  'secci�n PRO': [
    '/PRO',
    'espacio en blanco',
    'expresi�n',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de proceso*',
  ],
  'entrada de proceso': [
    'l�nea de etiqueta?',
    'palabra',  # Verbo
    'espacio en blanco',
    'palabra',  # Nombre
    'condacto en misma l�nea?',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'condacto*'
  ],
  'condacto en misma l�nea': [
    'espacio en blanco',
    'nombre de condacto',
    'par�metro*',
  ],
  'condacto': [
    'espacio en blanco',
    'nombre de condacto',
    'par�metro*',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'secci�n PRO en formato DSF': [
    'espacio en blanco?',
    '/PRO',
    'espacio en blanco',
    'expresi�n',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de proceso en formato DSF*',
  ],
  'entrada de proceso en formato DSF': [
    'l�nea de etiqueta?',
    'espacio en blanco?',
    'signo mayor que',
    (
      'fin de l�nea opcionalmente tras espacio en blanco y/o comentario',
      'espacio en blanco',
    ),
    'palabra',  # Verbo
    'espacio en blanco',
    'palabra',  # Nombre
    'condacto en misma l�nea en formato DSF?',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
    'condacto en formato DSF*'
  ],
  'condacto en misma l�nea en formato DSF': [
    'espacio en blanco',
    'nombre de condacto',
    'par�metro en formato DSF*',
  ],
  'condacto en formato DSF': [
    'espacio en blanco',
    'nombre de condacto',
    'par�metro en formato DSF*',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'l�nea de etiqueta': [
    'etiqueta',
    'fin de l�nea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'par�metro': [
    'espacio en blanco',
    (  # Mantener este orden o adaptar c�digo de procesado de par�metros en alto_nivel
      'expresi�n>',
      'palabra',
      'indirecci�n',
      'etiqueta',
      'n�mero entero',  # Para capturar n�meros negativos
      'CARRIED',  # Se listan aqu� los siguientes aunque encajar�n como expresi�n, como si fueran s�mbolos
      'HERE',
      'WORN',
    ),
  ],
  'expresi�n': [
    'entero positivo o s�mbolo',
    'operaci�n*',
  ],
  'indirecci�n': [
    'car�cter [',
    'expresi�n',
    'car�cter ]',
  ],
  'par�metro en formato DSF': [
    'espacio en blanco?',
    (  # Mantener este orden o adaptar c�digo de procesado de par�metros en alto_nivel
      'expresi�n>',
      'palabra',
      'indirecci�n en formato DSF',
      'etiqueta',
      'n�mero entero',  # Para capturar n�meros negativos
      'cadena de texto entre comillas',
      'CARRIED',  # Se listan aqu� los siguientes aunque encajar�n como expresi�n, como si fueran s�mbolos
      'HERE',
      'WORN',
    ),
  ],
  'indirecci�n en formato DSF': [
    'car�cter @',
    'expresi�n',
  ],
}


# Funciones que se utilizan fuera del m�dulo

def analizaCadena (cadena, reglaEntrada, condicionY = True, posEnCadena = 0):
  """Analiza sint�cticamente la cadena dada a partir de la regla de entrada o reglas dadas. Devuelve un mensaje de error explicativo si la cadena no encaj� por completo, vac�o si encaj� por completo, y luego la posici�n por la que se qued� analizando, y finalmente el �rbol de encajes desde el punto de entrada"""
  global errorAC, NULLWORD, nivelAnidacion, posErrorAC
  try:
    nivelAnidacion
  except:
    errorAC        = ''
    nivelAnidacion = 0
    posErrorAC     = -1
  arbolDatos = []
  if type (reglaEntrada) not in (list, tuple):
    reglaEntrada = [reglaEntrada]
  nuevaPosEnCadena = posEnCadena
  for e in range (len (reglaEntrada)):
    entrada        = reglaEntrada[e]
    algunResultado = False
    multiple       = False
    opcional       = False
    probarSig      = False  # Si se prueba la siguiente regla por si el encaje es m�s largo
    if type (entrada) in (list, tuple):
      error, posDevuelta, arbolDevuelto = analizaCadena (cadena, entrada, type (entrada) == list, nuevaPosEnCadena)
      arbolDatos.append (arbolDevuelto)
      if error:
        if posDevuelta > posErrorAC:
          errorAC    = error
          posErrorAC = posDevuelta
      else:
        algunResultado   = True
        nuevaPosEnCadena = posDevuelta
    elif type (entrada) == str or (version_info[0] < 3 and type (entrada) == unicode):
      if entrada[-1] in '*+>?':
        if entrada[-1] in '*+':
          multiple = True
          opcional = entrada[-1] == '*'
        else:
          if entrada[-1] == '?':
            opcional = True
          elif entrada[-1] == '>':
            probarSig = True
        entrada = entrada[:-1]
      if entrada in reglas:
        # prn ((' ' * nivelAnidacion) + 'Regla', '"' + entrada + '"', 'opcional' if opcional else 'obligatoria', 'y', 'm�ltiple' if multiple else '�nica')
        gruposRegla = []
        while True:
          nivelAnidacion += 1
          error, posDevuelta, arbolDevuelto = analizaCadena (cadena, reglas[entrada], type (reglas[entrada]) == list, nuevaPosEnCadena)
          nivelAnidacion -= 1
          if error:
            if posDevuelta > posErrorAC:
              errorAC    = error
              posErrorAC = posDevuelta
          else:
            algunResultado = True
            if probarSig:  # Vemos si la siguiente regla da un encaje m�s largo
              errorSig, posDevueltaSig, arbolDevueltoSig = analizaCadena (cadena, reglas[reglaEntrada[e + 1]], False, nuevaPosEnCadena)
              if not errorSig and posDevueltaSig > posDevuelta:
                error, posDevuelta, arbolDevuelto = errorSig, posDevueltaSig, arbolDevueltoSig
                arbolDatos.append ([[]])
            nuevaPosEnCadena = posDevuelta
          gruposRegla.append (arbolDevuelto)
          if error or not multiple:
            break
          # if error:
          #   prn ((' ' * nivelAnidacion) + 'Regla', '"' + entrada + '" completamente encajada')
        arbolDatos.append (gruposRegla)
      else:  # No es una regla
        if entrada in terminales:
          algunEncaje = False
          grupos      = []
          while True:
            encaje = terminales[entrada].match (cadena[nuevaPosEnCadena:])
            if encaje:
              algunEncaje  = True
              gruposEncaje = encaje.groups()
              grupos.append ((encaje.groups(), nuevaPosEnCadena))
              nuevaPosEnCadena += encaje.end()
              if entrada == 'NULLWORD':
                NULLWORD[0] = encaje.group (1)
                terminales['car�cter de NULLWORD'] = re.compile ('(' + NULLWORD[0] + ')')
              if not multiple:
                break
            else:
              break
          arbolDatos.append (grupos)
          # if algunEncaje:
          #   prn ((' ' * nivelAnidacion) + 'Terminal', '"' + entrada + '"', 'opcional' if opcional else 'obligatorio', 'y', 'm�ltiple' if multiple else '�nico', '->', grupos)
          if not algunEncaje and condicionY and not opcional:
            return entrada, nuevaPosEnCadena, []
          if algunEncaje and not condicionY:
            return '', nuevaPosEnCadena, arbolDatos
        else:
          errorAC    = 'Gram�tica inv�lida, elemento de regla desconocido: ' + entrada
          posErrorAC = 999999999
          return errorAC, posErrorAC, []
        continue
    elif entrada == None and not condicionY:
      # prn ('Encaja regla vac�a (opcional)')
      return '', posEnCadena, arbolDatos
    else:
      errorAC    = 'Gram�tica inv�lida, tipo de regla desconocido: ' + type (entrada).__name__
      posErrorAC = 999999999
      return errorAC, posErrorAC, []
    if (algunResultado or opcional) and not condicionY:
      return '', nuevaPosEnCadena, arbolDatos
    if not algunResultado and condicionY:
      if opcional:
        continue
      return errorAC, posErrorAC, []
    if not condicionY:
      nuevaPosEnCadena = posEnCadena  # Hacemos backtracking para intentar con la siguiente regla
  if condicionY:
    if nivelAnidacion == 0 and nuevaPosEnCadena < len (cadena) and cadena[nuevaPosEnCadena:].strip():  # Queda algo al final sin procesar
      return errorAC, posErrorAC, []
    return '', nuevaPosEnCadena, arbolDatos  # Todo encaj�
  # Era una condici�n O donde nada encaj�
  if type (reglaEntrada[0]) == str:  # Porque podr�a ser una lista como en la regla entrada de objeto
    errorAC = ''
    for e in range (len (reglaEntrada)):
      errorAC += (', ' if e else '') + ('o ' if e == len (reglaEntrada) - 1 else '') + reglaEntrada[e].rstrip ('>')
    posErrorAC = posEnCadena
  return errorAC, posErrorAC, []


if __name__ == '__main__':
  cadena = '''
/CTL ; Secci�n de control
 ; 		Comentario 
P

#			
;
/TOK;Tokens

Abc;prueba

hola
/VOC

patata	50   Noun

 ; Hola

  tortilla  51  noun

/STX

/CERO ;Comentario 1
;Comentario 2
Texto
;Comentario 3
/1;Comentario 4
Hola
/2 ;sdsfd
Prueba

/MTX
/0
/1

/2
/OTX
/100
Objeto 100
/LTX
/0     ; Localidad 0
Descripci�n
/1

/CON
/0   ; de la localidad 0

   n   1
norte  LOC_DOS
/OBJ
/NUM_OBJ      #  50  Y  #  caja  #
/NUM_OBJ + 1  #  50  Y  #  #  #
/PielX    #       1    # #   # # # # # Y # # # # Y # Y # # #   #        #

/PRO 0
# #
  DONE
# nada
  DESC 0
  INPUT 1  4
  SKIP  $etiqueta
'''
  error, pos, arbol = analizaCadena (cadena, 'c�digo fuente SCE gen�rico')
  if error:
    if error[0] == '/' or error[0].islower() or error[1].isupper():
      error = 'Se esperaba ' + error
    prn ('No ha encajado, pos:', pos, 'motivo:', error)
  else:
    prn ('S� ha encajado. Caracteres sin procesar:', len (cadena) - pos)
    prn (arbol[0][0])
