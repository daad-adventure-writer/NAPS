Convenciones de estilo
======================

Comentarios
-----------

Los comentarios al inicio de cada clase y cada método explicando qué son, qué hacen y/o cómo se usan, se pondrán como docstrings de Python con tres comillas dobles tras los dos puntos de su definición.

Nombre de clases
----------------

Los nombres de clase usarán CamelCase iniciando en mayúscula.

Nombre de métodos
-----------------

Los métodos para ser usados solamente en su módulo tendrán su nombre con CamelCase iniciando en minúscula. Los nombres de métodos de clase de uso interno, empezarán por guión bajo. Los métodos que pueden ser usados fuera de su módulo tendrán su nombre todo en minúsculas separando con guión bajo sus palabras.

Nombre de variables
-------------------

Se usará CamelCase iniciando en minúscula para variables locales incluyendo parámetros. Las variables globales o de módulo tendrán su nombre todo en minúsculas separando con guión bajo sus palabras.

Llamadas a métodos
------------------

Se espaciará entre el nombre del método y el paréntesis de apertura de sus parámetros si se llama con algún parámetro. No se espaciará entre el nombre del método y el paréntesis de apertura cuando se llame al método sin parámetros, ni cuando sea el método de traducción de textos con gettext (método cuyo nombre es el carácter de guión bajo).

Se espaciará tras los separadores de los parámetros, antes y después de los signos "igual que" de los parámetros asignados por nombre, y no se espaciará tras el paréntesis de apertura ni antes del paréntesis de cierre.
