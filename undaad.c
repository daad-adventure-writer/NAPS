/*
  NAPS: The New Age PAW-like System - Herramientas para sistemas PAW-like

  unDAAD: Extrae código fuente de bases de datos DAAD
  Copyright (C) 2008-2010, 2013-2014 José Manuel Ferrer Ortiz

  *****************************************************************************
  *                                                                           *
  *  This program is free software; you can redistribute it and/or modify it  *
  *  under the terms of the GNU General Public License version 2, as          *
  *  published by the Free Software Foundation.                               *
  *                                                                           *
  *  This program is distributed in the hope that it will be useful, but      *
  *  WITHOUT ANY WARRANTY; without even the implied warranty of               *
  *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU         *
  *  General Public License version 2 for more details.                       *
  *                                                                           *
  *  You should have received a copy of the GNU General Public License        *
  *  version 2 along with this program; if not, write to the Free Software    *
  *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA  *
  *                                                                           *
  *****************************************************************************
*/ 

#include <stdio.h>
#include <stdlib.h>
//#include <unistd.h>

/* DAAD codifica los caracteres haciendo un XOR con 255 como máscara.
   El nombre de la codificación original de éstos la desconozco (creo que no es
   ibm-cp850).
   Los textos de las abreviaturas no usan dicha codificación con XOR.
*/


#include "condactos.h"

// Cabecera en los ficheros ddb
// POSICION  LONGITUD  SIGNIFICADO
// 3         1 byte    Número de descripciones de objetos
// 4         1 byte    Número de descripciones de localidades
// 5         1 byte    Número de mensajes de usuario
// 6         1 byte    Número de mensajes de sistema
// 7         1 byte    Número de procesos
// 8         2 bytes   Posición de abreviaturas
// 10        2 bytes   Posición lista de posiciones de procesos
// 12        2 bytes   Posición lista de posiciones de objetos
// 14        2 bytes   Posición lista de posiciones de localidades
// 16        2 bytes   Posición lista de posiciones de mensajes de usuario
// 18        2 bytes   Posición lista de posiciones de mensajes de sistema
// 20        2 bytes   Posición lista de posiciones de conexiones
// 22        2 bytes   Posición de vocabulario
// 24        2 bytes   Posición de localidades iniciales de objetos
// 26        2 bytes   Posición de nombres de objetos
// 28        2 bytes   Posición de atributos de objetos
// 30        2 bytes   Longitud del fichero

// Desplazamientos (offsets/posiciones) en la cabecera
#define CAB_NUM_OBJS             3
#define CAB_NUM_LOCS             4
#define CAB_NUM_MSGS_USR         5
#define CAB_NUM_MSGS_SYS         6
#define CAB_NUM_PROCS            7
#define CAB_POS_ABREVS           8
#define CAB_POS_LST_POS_PROCS    10
#define CAB_POS_LST_POS_OBJS     12
#define CAB_POS_LST_POS_LOCS     14
#define CAB_POS_LST_POS_MSGS_USR 16
#define CAB_POS_LST_POS_MSGS_SYS 18
#define CAB_POS_LST_POS_CNXS     20
#define CAB_POS_VOCAB            22
#define CAB_POS_LOCS_OBJS        24
#define CAB_POS_NOMS_OBJS        26
#define CAB_POS_ATRIBS_OBJS      28
#define CAB_LONG_FICH            30

const unsigned char abrev_a_iso8859_15 [128] =
  {
      0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  //   0 -   9
     10,  11,  12,  13,  14,  15, 170, 161, 191, 171,  //  10 -  19
    187, 225, 233, 237, 243, 250, 241, 209, 231, 199,  //  20 -  29
    252, 220,  32,  33,  34,  35,  36,  37,  38,  39,  //  30 -  39
     40,  41,  42,  43,  44,  45,  46,  47,  48,  49,  //  40 -  49
     50,  51,  52,  53,  54,  55,  56,  57,  58,  59,  //  50 -  59
     60,  61,  62,  63,  64,  65,  66,  67,  68,  69,  //  60 -  69
     70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  //  70 -  79
     80,  81,  82,  83,  84,  85,  86,  87,  88,  89,  //  80 -  89
     90,  91,  92,  93,  94,  95,  96,  97,  98,  99,  //  90 -  99
    100, 101, 102, 103, 104, 105, 106, 107, 108, 109,  // 100 - 109
    110, 111, 112, 113, 114, 115, 116, 117, 118, 119,  // 110 - 119
    120, 121, 122, 123, 124, 125, 126, 127             // 120 - 127
  };

const unsigned char daad_a_iso8859_15 [256] =
  {
    255, 254, 253, 252, 251, 250, 249, 248, 247, 246,  //   0 -   9
    245, 244, 243, 242, 241, 240, 239, 238, 237, 236,  //  10 -  19
    235, 234, 233, 232, 231, 230, 229, 228, 227, 226,  //  20 -  29
    225, 224, 223, 222, 221, 220, 219, 218, 217, 216,  //  30 -  39
    215, 214, 213, 212, 211, 210, 209, 208, 207, 206,  //  40 -  49
    205, 204, 203, 202, 201, 200, 199, 198, 197, 196,  //  50 -  59
    195, 194, 193, 192, 191, 190, 189, 188, 187, 186,  //  60 -  69
    185, 184, 183, 182, 181, 180, 179, 178, 177, 176,  //  70 -  79
    175, 174, 173, 172, 171, 170, 169, 168, 167, 166,  //  80 -  89
    165, 164, 163, 162, 161, 160, 159, 158, 157, 156,  //  90 -  99
    155, 154, 153, 152, 151, 150, 149, 148, 147, 146,  // 100 - 109
    145, 144, 143, 142, 141, 140, 139, 138, 137, 136,  // 110 - 119
    135, 134, 133, 132, 131, 130, 129, 128, 127, 126,  // 120 - 129
    125, 124, 123, 122, 121, 120, 119, 118, 117, 116,  // 130 - 139
    115, 114, 113, 112, 111, 110, 109, 108, 107, 106,  // 140 - 149
    105, 104, 103, 102, 101, 100,  99,  98,  97,  96,  // 150 - 159
     95,  94,  93,  92,  91,  90,  89,  88,  87,  86,  // 160 - 169
     85,  84,  83,  82,  81,  80,  79,  78,  77,  76,  // 170 - 179
     75,  74,  73,  72,  71,  70,  69,  68,  67,  66,  // 180 - 189
     65,  64,  63,  62,  61,  60,  59,  58,  57,  56,  // 190 - 199
     55,  54,  53,  52,  51,  50,  49,  48,  47,  46,  // 200 - 209
     45,  44,  43,  42,  41,  40,  39,  38,  37,  36,  // 210 - 219
     35,  34,  33,  32, 220, 252, 199, 231, 209, 241,  // 220 - 229
    250, 243, 237, 233, 225, 187, 171, 191, 161, 170,  // 230 - 239
     15,  14,  13,  12,  11,  10,   9,   8,   7,   6,  // 240 - 249
      5,   4,   3,   2,   1,   0                       // 250 - 255
  };

// Tipos de palabras de vocabulario
const char *tipos [7] = {"Verb", "Adverb", "Noun", "Adjective", "Preposition",
                         "Conjunction", "Pronoun"};


/* __attribute__ ((pure)) void CompruebaParametros (const int argc,
                                                   const char *argv0) */
void CompruebaParametros (const int argc, const char *argv0)
{
  if (argc == 2)
    return;

  fprintf (stderr, "%s: Número de parámetros incorrecto\n\nUso: %s "
           "fichero_de_base_de_datos_de_DAAD\n", argv0, argv0);
  exit (1);
}

FILE *AbreFichero (const char *nombre, const char *argv0)
{
  FILE *fichero;

  fichero = fopen (nombre, "r");
  if (fichero != NULL)
    return fichero;

  fprintf (stderr, "%s: ", argv0);
  perror ("fopen()");
  exit (2);
}

int main (int argc, char *argv[])
{
  FILE *fichero;

  CompruebaParametros (argc, argv[0]);
  fichero = AbreFichero (argv[1], argv[0]);

  // Leemos los valores que nos interesan de la cabecera
  fseek (fichero, CAB_NUM_OBJS, SEEK_SET);
  const unsigned char num_objs     = fgetc (fichero);
  const unsigned char num_locs     = fgetc (fichero);
  const unsigned char num_msgs_usr = fgetc (fichero);
  const unsigned char num_msgs_sys = fgetc (fichero);
  const unsigned char num_procs    = fgetc (fichero);
  const unsigned short pos_abrevs = (fgetc (fichero) << 8) | (fgetc (fichero));
  const unsigned short pos_lst_pos_procs = (fgetc (fichero) << 8) |
                                           (fgetc (fichero));
  const unsigned short pos_lst_pos_objs = (fgetc (fichero) << 8) |
                                          (fgetc (fichero));
  const unsigned short pos_lst_pos_locs = (fgetc (fichero) << 8) |
                                          (fgetc (fichero));
  const unsigned short pos_lst_pos_msgs_usr = (fgetc (fichero) << 8) |
                                              (fgetc (fichero));
  const unsigned short pos_lst_pos_msgs_sys = (fgetc (fichero) << 8) |
                                              (fgetc (fichero));
  const unsigned short pos_lst_pos_cnxs = (fgetc (fichero) << 8) |
                                          (fgetc (fichero));
  const unsigned short pos_vocab = (fgetc (fichero) << 8) | (fgetc (fichero));
  const unsigned short pos_locs_objs = (fgetc (fichero) << 8) |
                                       (fgetc (fichero));
  const unsigned short pos_noms_objs = (fgetc (fichero) << 8) |
                                       (fgetc (fichero));
  const unsigned short pos_atribs_objs = (fgetc (fichero) << 8) |
                                         (fgetc (fichero));

  // Leemos e imprimimos el vocabulario
  fseek (fichero, pos_vocab, SEEK_SET);
  printf ("/CTL\n\n\n/VOC\n\n");
  unsigned short num_palabras = 0;
  char *palabra = NULL;
  unsigned char *id = NULL, *tipo = NULL;

  while (1)
  {
    unsigned char c = fgetc (fichero);
    if (c == 0)  // Fin del vocabulario
      break;

    num_palabras += 1;
    palabra = (char *) realloc (palabra, num_palabras * 5);
    id      = (char *) realloc (id,      num_palabras);
    tipo    = (char *) realloc (tipo,    num_palabras);

    palabra[(num_palabras - 1) * 5] = putchar (daad_a_iso8859_15[c]);
    for (unsigned char i = 1; i < 5; i++)
      palabra[((num_palabras - 1) * 5) + i] = putchar (
        daad_a_iso8859_15[fgetc (fichero)]);
    id[num_palabras - 1]   = fgetc (fichero);
    tipo[num_palabras - 1] = fgetc (fichero);
    printf ("     %3d",  id[num_palabras - 1]);
    printf ("     %s\n", tipos[tipo[num_palabras - 1]]);
  }

  // Leemos e imprimimos los mensajes del sistema
  printf ("\n\n/STX\n");
  for (unsigned char i = 0; i < num_msgs_sys; i++)
  {
    printf ("\n/%d\n", i);
    fseek (fichero, pos_lst_pos_msgs_sys + (2 * i), SEEK_SET);
    fseek (fichero, (fgetc (fichero) << 8) | (fgetc (fichero)), SEEK_SET);
    unsigned char c;
    while ((c = daad_a_iso8859_15[fgetc (fichero)]) != '\n')
      putchar (c);
  }

  // Leemos e imprimimos los mensajes de usuario
  printf ("\n\n\n/MTX\n");
  for (unsigned char i = 0; i < num_msgs_usr; i++)
  {
    printf ("\n/%d\n", i);
    fseek (fichero, pos_lst_pos_msgs_usr + (2 * i), SEEK_SET);
    fseek (fichero, (fgetc (fichero) << 8) | (fgetc (fichero)), SEEK_SET);
    unsigned char c;
    while ((c = daad_a_iso8859_15[fgetc (fichero)]) != '\n')
      putchar (c);
  }

  // Leemos e imprimimos las descripciones de los objetos
  printf ("\n\n\n/OTX\n");
  for (unsigned char i = 0; i < num_objs; i++)
  {
    printf ("\n/%d\n", i);
    fseek (fichero, pos_lst_pos_objs + (2 * i), SEEK_SET);
    fseek (fichero, (fgetc (fichero) << 8) | (fgetc (fichero)), SEEK_SET);
    unsigned char c;
    while ((c = daad_a_iso8859_15[fgetc (fichero)]) != '\n')
      putchar (c);
  }

  // Leemos e imprimimos las descripciones de las localidades
  printf ("\n\n\n/LTX\n");
  for (unsigned char i = 0; i < num_locs; i++)
  {
    unsigned short pos;
    unsigned char c;

    printf ("\n/%d\n", i);

    fseek (fichero, pos_lst_pos_locs + (2 * i), SEEK_SET);
    pos = (fgetc (fichero) << 8) | (fgetc (fichero));
    fseek (fichero, pos, SEEK_SET);

    while ((c = fgetc (fichero)) != ('\n' ^ 255))
    {
      pos++;
      if ((pos_abrevs != 0) && (c < 128))  // Es una abreviatura
      {
        fseek (fichero, pos_abrevs, SEEK_SET);
        for (c = (c ^ 255) - 127; c > 0; c--)
          while (fgetc (fichero) < 128);
        while ((c = fgetc (fichero)) < 128)
          putchar (abrev_a_iso8859_15[c]);
        putchar (abrev_a_iso8859_15[c - 128]);
        fseek (fichero, pos, SEEK_SET);
      }
      else
        putchar (daad_a_iso8859_15[c]);
    }
  }

  // Leemos e imprimimos las conexiones
  printf ("\n\n\n/CON\n");
  for (unsigned char i = 0; i < num_locs; i++)
  {
    printf ("\n/%d\n", i);
    fseek (fichero, pos_lst_pos_cnxs + (2 * i), SEEK_SET);
    fseek (fichero, (fgetc (fichero) << 8) | (fgetc (fichero)), SEEK_SET);
    unsigned char c;
    while ((c = fgetc (fichero)) != 255)
    {
      unsigned short s;
      for (s = 0; s < num_palabras; s++)
        if ((id[s] == c) && ((tipo[s] == 0) || ((tipo[s] == 2) && (c < 20))))
          break;
      for (unsigned char j = 0; j < 5; j++)
        putchar (palabra[(s * 5) + j]);
      printf ("   %d\n", fgetc (fichero));
    }
  }

  // Leemos e imprimimos las propiedades de los objetos
  printf ("\n\n\n/OBJ\n");
  for (unsigned char i = 0; i < num_objs; i++)
  {
    fseek (fichero, pos_locs_objs + i, SEEK_SET);
    printf ("\n/%d %d 0 ", i, fgetc (fichero));
    fseek (fichero, pos_noms_objs, SEEK_SET);
    for (unsigned char j = 0; j < i; j++)
      while ((fgetc (fichero)) != 255);  // Es bastante probable que esto sea
        // incorrecto, sólo sirve cuando no se asignan adjetivos a los objetos.
        // Lo correcto es, o así supongo ahora, que se guarda igual que en PAWS:
        // para cada objeto, un par de bytes: el primero es el nombre y el
        // segundo, el adjetivo.
    unsigned char c = fgetc (fichero);
    if (c == 255)
      putchar ('_');
    else
    {
      unsigned short s;
      for (s = 0; s < num_palabras; s++)
        if ((id[s] == c) && (tipo[s] == 2))
          break;
      //if (s == num_palabras)
      //  printf ("error, c = %d\n", c);
      for (unsigned char j = 0; j < 5; j++)
        putchar (palabra[(s * 5) + j]);
    }
    if (i == 0)  // El objeto 0 siempre emite luz
      printf (" _ 1");
    else
      printf (" _ 0");
    fseek (fichero, pos_atribs_objs + i, SEEK_SET);
    c = fgetc (fichero);
    if ((c & 128) != 0)  // Prenda
      putchar ('1');
    else
      putchar ('0');
    if ((c & 64) != 0)  // Contenedor
      putchar ('1');
    else
      putchar ('0');
    printf ("00000000000000000000000000000 00000000000000000000000000000000\n");
  }

  // Leemos e imprimimos los procesos
  for (unsigned char i = 0; i < num_procs; i++)
  {
    printf ("\n\n\n/PRO %d\n", i);
    for (unsigned short s = 0; ; s++)
    {
      fseek (fichero, pos_lst_pos_procs + (2 * i), SEEK_SET);
      fseek (fichero, (fgetc (fichero) << 8) | (fgetc (fichero)), SEEK_SET);
      fseek (fichero, 4 * s, SEEK_CUR);
      unsigned char c = fgetc (fichero);
      if (c == 0)  // Fin de este proceso
        break;
      if (c == 255)
        printf ("\n_");
      else
      {
        putchar ('\n');
        unsigned short s;
        for (s = 0; s < num_palabras; s++)
          if ((id[s] == c) && ((tipo[s] == 0) || ((tipo[s] == 2) && (c < 20))))
            break;
        //if (s == num_palabras)
        //  printf ("error, c = %d\n", c);
        for (unsigned char j = 0; j < 5; j++)
          putchar (palabra[(s * 5) + j]);
      }
      c = fgetc (fichero);
      if (c == 255)
        printf (" _\n");
      else
      {
        putchar (' ');
        unsigned short s;
        for (s = 0; s < num_palabras; s++)
          if ((id[s] == c) && (tipo[s] == 2))
            break;
        //if (s == num_palabras)
        //  printf ("error, c = %d\n", c);
        for (unsigned char j = 0; j < 5; j++)
          putchar (palabra[(s * 5) + j]);
        putchar ('\n');
      }
      unsigned short borrame_pos = (fgetc (fichero) << 8) | (fgetc (fichero));
      printf (";%d\n", borrame_pos);
      //fseek (fichero, (fgetc (fichero) << 8) | (fgetc (fichero)), SEEK_SET);
      fseek (fichero, borrame_pos, SEEK_SET);
      while ((c = fgetc (fichero)) != 255)
      {
        unsigned char indirecto = 0;
        if (c > 127)
        {
          c -= 128;
          indirecto = 1;
        }
        if (c >= NUM_CONDACTOS)  // Condacto no reconocido
        {
          printf (";error, condacto número %d no reconocido\n", c);
          break;
        }
        char *pal = (char *) &condactos[c * 8];
        printf (" %c%c%c%c%c%c%c   %c", pal[1], pal[2], pal[3], pal[4], pal[5],
                pal[6], pal[7], indirecto ? '@' : ' ');
        for (unsigned char j = 0; j < pal[0]; j++)
          printf ("%d ", fgetc (fichero));
        putchar ('\n');
      }
    }
  }

  fclose (fichero);
  putchar ('\n');
}
