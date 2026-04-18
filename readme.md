# Emoticonos Avanzados para NVDA

## ¿Qué es este complemento?

Emoticonos Avanzados es un complemento para el lector de pantallas NVDA que te permite controlar cómo se leen los emojis (😀❤️🚀) y los emoticonos clásicos (:) ;D XD) mientras navegas por aplicaciones, páginas web, chats y documentos.

Utiliza los diccionarios CLDR (Common Locale Data Repository) de NVDA para ofrecer más de 4000 descripciones de emojis en español.

Con este complemento puedes:

* **Escuchar descripciones en español** de los emojis que encuentres.
* **Agrupar emojis repetidos** para no escuchar la misma descripción varias veces.
* **Silenciar emojis completamente** para leer solo el texto.
* **Silenciar también los símbolos especiales** que NVDA lee por defecto (como ₧, ©, ®, etc.).

## Modos de funcionamiento

El complemento tiene cuatro modos que puedes cambiar en cualquier momento:

### Complemento desactivado

El complemento queda completamente desactivado. NVDA funciona de forma normal, exactamente igual que si el complemento no estuviera instalado. No se modifica ni se intercepta ningún texto del habla.

### Individual (uno por uno)

Cada emoji se reemplaza por su descripción en español. Por ejemplo:

* `Hola 😀` se lee como `Hola cara sonriendo`
* `Me encanta ❤️❤️` se lee como `Me encanta corazón rojo corazón rojo`

### Agrupado (contar repetidos)

Cuando hay varios emojis iguales seguidos, se cuentan en lugar de repetir la descripción. Por ejemplo:

* `😀😀😀` se lee como `3x cara sonriendo`
* `❤️❤️❤️❤️❤️` se lee como `5x corazón rojo`

Esto es muy útil en chats donde las personas envían muchos emojis seguidos.

### Eliminado (no leer emoticonos)

Todos los emojis y emoticonos se eliminan del habla. NVDA solo lee el texto. Por ejemplo:

* `Hola 😀😀😀 ¿cómo estás?` se lee como `Hola ¿cómo estás?`

## Comandos del complemento

Este complemento no viene con atajos de teclado predefinidos. Puedes asignar los atajos que prefieras desde el menú de NVDA.

### Cómo asignar atajos

1. Abre el menú de NVDA (pulsa `NVDA+N`).
2. Ve a **Preferencias** y luego a **Gestos de entrada**.
3. Busca la categoría **Emoticonos Avanzados**.
4. Encontrarás tres comandos disponibles:
   * **Alternar modo de emoticonos**: Cambia rápidamente entre los cuatro modos (desactivado, individual, agrupado y eliminado). Cada vez que lo pulses, pasará al siguiente modo y NVDA te dirá cuál está activo.
   * **Información del símbolo actual**: Muestra un diálogo con información detallada sobre el emoji o símbolo que esté en la posición del cursor de revisión. Te dice qué carácter es, de qué tipo y su descripción.
   * **Analizar emoticonos del portapapeles**: Analiza el texto que hayas copiado al portapapeles, busca todos los emojis y emoticonos que contenga, y muestra un resumen con la lista completa y estadísticas.
5. Selecciona el comando y pulsa **Añadir** para asignar el atajo de teclado que desees.

## Configuración

Hay dos formas de acceder a la configuración del complemento:

* **Menú de NVDA → Herramientas → Emoticonos Avanzados**
* **Menú de NVDA → Preferencias → Opciones → Emoticonos Avanzados**

### Opciones disponibles

#### Modo de anuncio de emoticonos

Selecciona cómo quieres que se lean los emoticonos. Puedes elegir entre: Complemento desactivado, Individual, Agrupado o Eliminado. Esta opción hace lo mismo que el comando de alternar modo, pero desde la configuración.

#### Detectar emojis Unicode

Cuando está activado, el complemento detecta emojis Unicode como 😀, ❤️, 🚀, 📕, etc. Desactívalo si solo quieres procesar emoticonos clásicos de texto.

#### Detectar emoticonos clásicos

Cuando está activado, el complemento detecta emoticonos escritos con caracteres de texto como :) ;D XD :P :'( etc. Desactívalo si solo quieres procesar emojis Unicode.

#### Suprimir la lectura de símbolos de NVDA

Cuando está activado, se silencian los símbolos especiales que NVDA lee por defecto, como signos de moneda (₧, ¥, ¢), símbolos matemáticos (÷, ×), marcas registradas (©, ®, ™) y otros caracteres especiales.

Esta opción funciona en todos los modos excepto Desactivado. Es útil cuando quieres una lectura completamente limpia de texto sin interrupciones por símbolos.

**Nota importante:** Al activar esta opción, NVDA dejará de leer TODOS los símbolos especiales, incluidos los que podrían ser útiles como €, $, @, etc. Úsala con precaución.

#### Mostrar descripciones de emoticonos en línea Braille

Cuando está activado, las descripciones de emojis y emoticonos se muestran también en la línea Braille. Los caracteres Unicode de emojis (que normalmente aparecen como celdas vacías o no representables en Braille) se reemplazan por sus descripciones textuales.

Por ejemplo, si un texto contiene el emoji 😀, en la línea Braille aparecerá `[cara sonriendo]` en lugar del carácter Unicode original.

Esta opción respeta el modo de anuncio seleccionado:

* En modo **Individual**, cada emoji se muestra con su descripción.
* En modo **Agrupado**, los emojis repetidos se cuentan (ej: `3x [cara sonriendo]`).
* En modo **Eliminado**, los emojis se eliminan también de la línea Braille.

**Nota:** Esta opción es independiente de la salida por voz. Puedes tener activado el modo individual por voz y también ver las descripciones en Braille simultáneamente, o activar solo la salida Braille sin modificar el comportamiento del habla.

#### Ignorar mayúsculas en emoticonos clásicos

Cuando está activado, XD, Xd, xD y xd se tratan como el mismo emoticono. Desactívalo si quieres distinguir entre mayúsculas y minúsculas.

#### Formato de descripción

Permite personalizar cómo se muestra la descripción de cada emoticono. Usa `{}` como marcador para el nombre del emoticono.

Ejemplos:

* `[{}]` se convierte en `[cara sonriendo]` (formato por defecto)
* `({})` se convierte en `(cara sonriendo)`
* `emoticono: {}` se convierte en `emoticono: cara sonriendo`

#### Prefijo al anunciar

Añade un texto antes de cada descripción de emoticono. Déjalo vacío si no quieres ningún prefijo.

Ejemplo: Si pones `emoji` como prefijo, `😀` se leería como `emoji cara sonriendo`.

#### Nivel de registro (logging)

Permite controlar cuánta información muestra el complemento en el visor de registro de NVDA (menú NVDA → Herramientas → Ver registro). Es útil para diagnosticar problemas o simplemente ver qué está haciendo el complemento.

Niveles disponibles:

* **Desactivado**: No muestra ningún mensaje en el registro. Es lo recomendado para uso normal.
* **Informativo**: Muestra mensajes básicos como la inicialización del complemento.
* **Depuración**: Muestra información adicional como la cantidad de entradas del diccionario cargadas, el estado del filtro de habla y la supresión de símbolos.
* **Completo (todo)**: Muestra todos los detalles, incluyendo cada texto que se procesa en modo agrupado. Puede generar muchos mensajes en el registro, usar solo para diagnosticar problemas concretos.

## Tipos de emoticonos que detecta

### Emojis Unicode

Son los emojis gráficos estándar que se usan en todas las aplicaciones y sistemas operativos. Ejemplos: 😀 😂 ❤️ 👍 🎉 🚀 🌈 🐱 🍕 ⚡

El complemento detecta más de 4000 emojis Unicode con descripciones en español provenientes del diccionario CLDR de NVDA, incluyendo emojis con modificadores de tono de piel y secuencias compuestas.

### Emoticonos clásicos

Son combinaciones de caracteres de texto que representan expresiones. Ejemplos: :) :( ;) :D :P XD :'( :O <3 ^_^ -_-

## Requisitos

* NVDA 2024.1 o posterior.

## Licencia

Este complemento se distribuye bajo la Licencia Pública General de GNU v2. Es software libre y gratuito.

## Créditos

* **Autor**: Héctor J. Benítez Corredera
* **Descripciones de emojis**: Diccionarios CLDR (Common Locale Data Repository) de NVDA en español
