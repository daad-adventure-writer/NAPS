# -*- coding: iso-8859-15 -*-

# NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like
#
# Analizador sintáctico para cargar rápida y cómodamente código fuente SCE y DSF
# Copyright (C) 2023-2025 José Manuel Ferrer Ortiz

import re

from sys import version_info

from prn_func import prn


# Variables que se pueden utilizar fuera del módulo

NULLWORD = ['_']

terminales = {
  'carácter de NULLWORD':   re.compile ('(_)'),  # Puede cambiar al procesar la entrada de NULLWORD
  'espacio en blanco':      re.compile ('[ \t]+'),
  'número entero':          re.compile (r'([+\-]?[0-9]+)'),
  'número entero positivo': re.compile ('([0-9]+)'),
  'fin de línea opcionalmente tras espacio en blanco y/o comentario': re.compile ('[ \t]*(?:;([^\n]*))?\n'),
  # De la sección CTL
  '/CTL':     re.compile ('(/CTL)'),
  'DBDRIVE':  re.compile ('([A-Q])'),  # Unidad de la base de datos en CP/M de la A a la P, o Q para indicar código fuente de Quill
  'NULLWORD': re.compile (r'([!-\*,-.<-@\[-`{-~])'),
  # De la sección TOK
  '/TOK':  re.compile ('(/TOK)'),
  'token': re.compile ('([^ ;/\n\t][^ ;\n\t]+)(?:[ \t]*(?:;[^\n]*)?\n)+'),
  # De la sección VOC
  '/VOC':                           re.compile ('(/VOC)'),
  'palabra de vocabulario':         re.compile ('([0-9A-Za-záéíóúñÁÉÍÓÚÑ]+)'),  # TODO: añadir caracteres restantes que permite el idioma español
  'tipo de palabra de vocabulario': re.compile ('(ADJECTIVE|ADVERB|CONJUGATION|CONJUNCTION|NOUN|PREPOSITION|PRONOUN|VERB)', re.IGNORECASE),
  # De las secciones STX, MTX, OTX y LTX
  '/LTX':                   re.compile ('(/LTX)'),
  '/MTX':                   re.compile ('(/MTX)'),
  '/OTX':                   re.compile ('(/OTX)'),
  '/STX':                   re.compile ('(/STX)'),
  'carácter /':             re.compile ('(/)'),
  'línea de texto':         re.compile ('(?!/)([^\n]*)\n'),
  'operador':               re.compile ('([+-])'),
  'símbolo':                re.compile ('([A-Z_a-zñÑ][0-9A-Z_a-zñÑ]*)'),
  'símbolo que no sea CON': re.compile ('(?!CON)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'símbolo que no sea LTX': re.compile ('(?!LTX)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'símbolo que no sea MTX': re.compile ('(?!MTX)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'símbolo que no sea OTX': re.compile ('(?!OTX)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'cadena de texto entre comillas dobles':  re.compile ('"(.*)"'),
  'cadena de texto entre comillas simples': re.compile ("'(.*)'"),
  # De la sección CON
  '/CON':                   re.compile ('(/CON)'),
  'símbolo que no sea OBJ': re.compile ('(?!OBJ)([A-Z_a-z][0-9A-Z_a-z]*)'),
  # De la sección OBJ
  '/OBJ':                   re.compile ('(/OBJ)'),
  'símbolo que no sea PRO': re.compile ('(?!PRO)([A-Z_a-z][0-9A-Z_a-z]*)'),
  'CARRIED':                re.compile ('(CARRIED)'),
  'WORN':                   re.compile ('(WORN)'),
  'carácter Y':             re.compile ('(Y)'),
  # De la sección PRO
  '/PRO':               re.compile ('(/PRO)'),
  'carácter @':         re.compile ('(@)'),
  'carácter [':         re.compile (r'(\[)'),
  'carácter ]':         re.compile (r'(\])'),
  'etiqueta':           re.compile (r'\$([A-Za-zÑ][0-9A-Za-zÑ]*)'),
  'nombre de condacto': re.compile ('([A-Z][0-9A-Z]*)', re.IGNORECASE),
  'signo mayor que':    re.compile ('(>)'),
  'HERE':               re.compile ('(HERE)'),
  # Marcador de fin de código en formato DSF
  '/END':               re.compile ('(/END)'),
}

# Listas [] implican condición Y, tuplas () implican condición O. En estas últimas se puede usar None para volver opcional la regla padre
reglas = {
  'código fuente SCE genérico': [
    'fin de línea opcionalmente tras espacio en blanco y/o comentario*',
    'sección CTL?',
    'sección TOK?',
    'sección VOC',
    'sección STX',
    'sección MTX',
    'sección OTX',
    'sección LTX',
    'sección CON',
    'sección OBJ',
    'sección PRO+',
  ],
  'código fuente QSE': [
    'fin de línea opcionalmente tras espacio en blanco y/o comentario*',
    'sección CTL',
    'sección VOC en formato QSE',
    'sección STX',
    'sección MTX',
    'sección OTX',
    'sección LTX',
    'sección CON',
    'sección OBJ en formato QSE',
    'sección PRO+',
  ],
  'código fuente DSF': [
    'fin de línea opcionalmente tras espacio en blanco y/o comentario*',
    'sección CTL en formato DSF?',
    'sección TOK?',
    'sección VOC',
    'sección STX en formato DSF',
    'sección MTX en formato DSF',
    'sección OTX en formato DSF',
    'sección LTX en formato DSF',
    'sección CON',
    'sección OBJ',
    'sección PRO en formato DSF+',
    '/END',
  ],
  'sección CTL': [
    '/CTL',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'opción DBDRIVE?',  # Usado en formato QSE y en CP/M para indicar la letra de unidad donde guardar la base de datos
    'NULLWORD',
    'opción llevables?',  # Número de objetos llevables en formato QSE
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'opción DBDRIVE': [
    'DBDRIVE',  # Unidad de la base de datos en CP/M de la A a la P, o Q para indicar código fuente de Quill
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'sección CTL en formato DSF': [
    '/CTL',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'opción NULLWORD?',
  ],
  'opción NULLWORD': [
    'NULLWORD',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'opción llevables': [
    'número entero positivo',  # Número de objetos llevables
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'sección TOK': [
    '/TOK',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'token*',
  ],
  'sección VOC': [
    '/VOC',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de vocabulario*',
  ],
  'entrada de vocabulario': [
    'espacio en blanco?',
    'palabra de vocabulario',
    'espacio en blanco',
    'número entero positivo',
    'espacio en blanco',
    'tipo de palabra de vocabulario',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'sección VOC en formato QSE': [
    '/VOC',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de vocabulario en formato QSE*',
  ],
  'entrada de vocabulario en formato QSE': [
    'espacio en blanco?',
    'palabra de vocabulario',
    'espacio en blanco',
    'número entero positivo',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'sección STX': [
    '/STX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de STX*'
  ],
  'entrada de STX': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea MTX',
    ),
    'fin de línea opcionalmente tras espacio en blanco y/o comentario',
    'línea de texto*',
  ],
  'sección STX en formato DSF': [
    '/STX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de STX en formato DSF*'
  ],
  'entrada de STX en formato DSF': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea MTX',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresión que no sea MTX': [
    'símbolo que no sea MTX',
    'operación*',
  ],
  'cadena de texto entre comillas': (
    'cadena de texto entre comillas dobles',
    'cadena de texto entre comillas simples',
  ),
  'sección MTX': [
    '/MTX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de MTX*'
  ],
  'entrada de MTX': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea OTX',
    ),
    'fin de línea opcionalmente tras espacio en blanco y/o comentario',
    'línea de texto*',
  ],
  'sección MTX en formato DSF': [
    '/MTX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de MTX en formato DSF*'
  ],
  'entrada de MTX en formato DSF': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea OTX',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresión que no sea OTX': [
    'símbolo que no sea OTX',
    'operación*',
  ],
  'sección OTX': [
    '/OTX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de OTX*'
  ],
  'entrada de OTX': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea LTX',
    ),
    'fin de línea opcionalmente tras espacio en blanco y/o comentario',
    'línea de texto*',
  ],
  'sección OTX en formato DSF': [
    '/OTX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de OTX en formato DSF*'
  ],
  'entrada de OTX en formato DSF': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea LTX',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresión que no sea LTX': [
    'símbolo que no sea LTX',
    'operación*',
  ],
  'sección LTX': [
    '/LTX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de LTX*'
  ],
  'entrada de LTX': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea CON',
    ),
    'fin de línea opcionalmente tras espacio en blanco y/o comentario',
    'línea de texto*',
  ],
  'sección LTX en formato DSF': [
    '/LTX',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de LTX en formato DSF*'
  ],
  'entrada de LTX en formato DSF': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea CON',
    ),
    'espacio en blanco',
    'cadena de texto entre comillas',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresión que no sea CON': [
    'símbolo que no sea CON',
    'operación*',
  ],
  'operación': [
    'espacio en blanco?',
    'operador',
    'espacio en blanco?',
    'entero positivo o símbolo',
  ],
  'entero positivo o símbolo': (
    'símbolo',
    'número entero positivo',
  ),
  'sección CON': [
    '/CON',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'grupo de conexión*',
  ],
  'grupo de conexión': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea OBJ',
    ),
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de conexión*',
  ],
  'expresión que no sea OBJ': [
    'símbolo que no sea OBJ',
    'operación*',
  ],
  'entrada de conexión': [
    'espacio en blanco?',
    'palabra de vocabulario',
    'espacio en blanco',
    'expresión',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'palabra': (
    'palabra de vocabulario',
    'carácter de NULLWORD',
  ),
  'sección OBJ': [
    '/OBJ',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de objeto*',
  ],
  'entrada de objeto': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea PRO',
    ),
    'espacio en blanco',
    (  # Localidad inicial
      'CARRIED',
      'WORN',
      'carácter de NULLWORD',  # No creados
      'expresión',
    ),
    'espacio en blanco',
    'número entero positivo',  # Peso
    # XXX: considerar hacer esto mejor, como especificando número de veces que debe aparecer una regla, pero sin perjudicar la eficiencia
    (
      [  # Variante con dos atributos
        'atributo',  # Contenedor
        'atributo',  # Llevable
        'espacio en blanco',
        'palabra',  # Nombre
        'espacio en blanco',
        'palabra',  # Adjetivo
        'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
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
        'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
      ],
    ),
  ],
  'sección OBJ en formato QSE': [
    '/OBJ',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de objeto en formato QSE*',
  ],
  'entrada de objeto en formato QSE': [
    'carácter /',
    (
      'número entero positivo',
      'expresión que no sea PRO',
    ),
    'espacio en blanco',
    (  # Localidad inicial
      'CARRIED',
      'WORN',
      'carácter de NULLWORD',  # No creados
      'expresión',
    ),
    'espacio en blanco',
    'palabra',  # Nombre
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'expresión que no sea PRO': [
    'símbolo que no sea PRO',
    'operación*',
  ],
  'atributo': [
    'espacio en blanco',
    (
      'carácter Y',
      'carácter de NULLWORD',
    ),
  ],
  'sección PRO': [
    '/PRO',
    'espacio en blanco',
    'expresión',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de proceso*',
  ],
  'entrada de proceso': [
    'línea de etiqueta?',
    'palabra',  # Verbo
    'espacio en blanco',
    'palabra',  # Nombre
    'condacto en misma línea?',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'condacto*'
  ],
  'condacto en misma línea': [
    'espacio en blanco',
    'nombre de condacto',
    'parámetro*',
  ],
  'condacto': [
    'espacio en blanco',
    'nombre de condacto',
    'parámetro*',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'sección PRO en formato DSF': [
    'espacio en blanco?',
    '/PRO',
    'espacio en blanco',
    'expresión',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'entrada de proceso en formato DSF*',
  ],
  'entrada de proceso en formato DSF': [
    'línea de etiqueta?',
    'espacio en blanco?',
    'signo mayor que',
    (
      'fin de línea opcionalmente tras espacio en blanco y/o comentario',
      'espacio en blanco',
    ),
    'palabra',  # Verbo
    'espacio en blanco',
    'palabra',  # Nombre
    'condacto en misma línea en formato DSF?',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
    'condacto en formato DSF*'
  ],
  'condacto en misma línea en formato DSF': [
    'espacio en blanco',
    'nombre de condacto',
    'parámetro en formato DSF*',
  ],
  'condacto en formato DSF': [
    'espacio en blanco',
    'nombre de condacto',
    'parámetro en formato DSF*',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'línea de etiqueta': [
    'etiqueta',
    'fin de línea opcionalmente tras espacio en blanco y/o comentario+',
  ],
  'parámetro': [
    'espacio en blanco',
    (  # Mantener este orden o adaptar código de procesado de parámetros en alto_nivel
      'expresión>',
      'palabra',
      'indirección',
      'etiqueta',
      'número entero',  # Para capturar números negativos
      'CARRIED',  # Se listan aquí los siguientes aunque encajarán como expresión, como si fueran símbolos
      'HERE',
      'WORN',
    ),
  ],
  'expresión': [
    'entero positivo o símbolo',
    'operación*',
  ],
  'indirección': [
    'carácter [',
    'expresión',
    'carácter ]',
  ],
  'parámetro en formato DSF': [
    'espacio en blanco?',
    (  # Mantener este orden o adaptar código de procesado de parámetros en alto_nivel
      'expresión>',
      'palabra',
      'indirección en formato DSF',
      'etiqueta',
      'número entero',  # Para capturar números negativos
      'cadena de texto entre comillas',
      'CARRIED',  # Se listan aquí los siguientes aunque encajarán como expresión, como si fueran símbolos
      'HERE',
      'WORN',
    ),
  ],
  'indirección en formato DSF': [
    'carácter @',
    'expresión',
  ],
}


# Funciones que se utilizan fuera del módulo

def analizaCadena (cadena, reglaEntrada, condicionY = True, posEnCadena = 0):
  """Analiza sintácticamente la cadena dada a partir de la regla de entrada o reglas dadas. Devuelve un mensaje de error explicativo si la cadena no encajó por completo, vacío si encajó por completo, y luego la posición por la que se quedó analizando, y finalmente el árbol de encajes desde el punto de entrada"""
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
    probarSig      = False  # Si se prueba la siguiente regla por si el encaje es más largo
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
        # prn ((' ' * nivelAnidacion) + 'Regla', '"' + entrada + '"', 'opcional' if opcional else 'obligatoria', 'y', 'múltiple' if multiple else 'única')
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
            if probarSig:  # Vemos si la siguiente regla da un encaje más largo
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
                terminales['carácter de NULLWORD'] = re.compile ('(' + NULLWORD[0] + ')')
              if not multiple:
                break
            else:
              break
          arbolDatos.append (grupos)
          # if algunEncaje:
          #   prn ((' ' * nivelAnidacion) + 'Terminal', '"' + entrada + '"', 'opcional' if opcional else 'obligatorio', 'y', 'múltiple' if multiple else 'único', '->', grupos)
          if not algunEncaje and condicionY and not opcional:
            return entrada, nuevaPosEnCadena, []
          if algunEncaje and not condicionY:
            return '', nuevaPosEnCadena, arbolDatos
        else:
          errorAC    = 'Gramática inválida, elemento de regla desconocido: ' + entrada
          posErrorAC = 999999999
          return errorAC, posErrorAC, []
        continue
    elif entrada == None and not condicionY:
      # prn ('Encaja regla vacía (opcional)')
      return '', posEnCadena, arbolDatos
    else:
      errorAC    = 'Gramática inválida, tipo de regla desconocido: ' + type (entrada).__name__
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
    return '', nuevaPosEnCadena, arbolDatos  # Todo encajó
  # Era una condición O donde nada encajó
  if type (reglaEntrada[0]) == str:  # Porque podría ser una lista como en la regla entrada de objeto
    errorAC = ''
    for e in range (len (reglaEntrada)):
      errorAC += (', ' if e else '') + ('o ' if e == len (reglaEntrada) - 1 else '') + reglaEntrada[e].rstrip ('>')
    posErrorAC = posEnCadena
  return errorAC, posErrorAC, []


if __name__ == '__main__':
  cadena = '''
/CTL ; Sección de control
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
Descripción
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
  error, pos, arbol = analizaCadena (cadena, 'código fuente SCE genérico')
  if error:
    if error[0] == '/' or error[0].islower() or error[1].isupper():
      error = 'Se esperaba ' + error
    prn ('No ha encajado, pos:', pos, 'motivo:', error)
  else:
    prn ('Sí ha encajado. Caracteres sin procesar:', len (cadena) - pos)
    prn (arbol[0][0])
