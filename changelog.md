# Registro de cambios

## 1.3.1 (2026-04-18)

### Novedades

* **Descripciones CLDR nativas**: El complemento ahora utiliza los diccionarios CLDR (Common Locale Data Repository) de NVDA en español para las descripciones de emojis. Esto proporciona **más de 3900 descripciones** oficiales en español, incluyendo emojis con modificadores de tono de piel, secuencias ZWJ y emojis compuestos. Se excluyen deliberadamente símbolos tipográficos (puntuación, monedas, flechas, comillas especiales) que NVDA ya maneja de forma nativa.
* **Script de importación**: Nuevo script `importar_diccionarios.py` que permite regenerar automáticamente el diccionario de emojis desde los archivos `cldr.dic` de NVDA.

### Correcciones

* **Corregido bug del cursor en Braille**: Al escribir un emoji y pulsar espacio, el cursor no avanzaba correctamente. Ahora se calcula un mapa de posiciones que traduce correctamente la posición del cursor del texto original al texto con descripciones de emojis, evitando que el cursor se quede atascado.

### Mejoras

* **Eliminadas dependencias externas**: Se han eliminado las librerías `emoji` y `emot` que se incluían empaquetadas. El complemento es ahora completamente autocontenido y más ligero (~680KB menos).
* **Simplificada la configuración**: Eliminadas las opciones "Usar librería emoji", "Usar librería emot" y "Usar traducciones manuales" del panel de configuración, ya que no son necesarias con el nuevo sistema CLDR.
* **Motor de detección reescrito**: Detección basada en regex compilada desde el diccionario CLDR, con ordenación por longitud descendente para detectar correctamente secuencias compuestas antes que componentes individuales.
* Limpieza de claves de configuración obsoletas al actualizar el complemento.

## 1.3.0 (2026-04-18)

### Novedades

* **Soporte para línea Braille**: Nueva opción para mostrar las descripciones de emojis y emoticonos directamente en la línea Braille. Cuando está activada, los caracteres Unicode de emojis se reemplazan por sus descripciones textuales en la salida Braille, permitiendo que los usuarios de línea Braille lean las descripciones en lugar de celdas vacías o caracteres no representables.
* Nueva opción "Mostrar descripciones de emoticonos en línea Braille" en el panel de configuración.

### Detalles técnicos

* Implementado mediante monkey-patching de `braille.Region.update` para interceptar el texto antes de la traducción a celdas Braille.
* El parche se instala al cargar el complemento y se desinstala al desactivarlo, sin afectar al rendimiento cuando la opción está deshabilitada.
* Incluye ajuste automático de posición de cursor y selección para evitar errores cuando el texto cambia de longitud.

## 1.2.0 (2026-04-18)

### Correcciones

* Corregido falso positivo en modo individual: se añaden límites de palabra a los patrones regex del speech dict para evitar que emoticonos se detecten dentro de palabras comunes.

### Novedades

* Traducciones manuales ampliadas de ~500 a **más de 1200 emojis** con descripciones en español. Nuevas categorías: zodíaco, relojes, flechas, ropa, herramientas, hogar, cuerpo, seres fantásticos, profesiones, deportes, más banderas, más comida, más naturaleza, símbolos japoneses y más.

### Mejoras

* Eliminado import no utilizado (`globalCommands.SCRCAT_TOOLS`).
* Todos los scripts del complemento aparecen bajo la categoría "Emoticonos Avanzados" en Gestos de entrada.

## 1.1.0 (2026-04-18)

### Correcciones

* Corregido falso positivo en modo agrupado: ya no detecta emoticonos dentro de palabras (por ejemplo, `:P` dentro de "Explorador").

### Novedades

* Nueva opción "Suprimir la lectura de símbolos de NVDA" para silenciar símbolos como ₧, ©, ®, etc.
* Nueva opción "Nivel de registro (logging)" para controlar cuánta información muestra el complemento en el visor de registro de NVDA.
* Los comandos del complemento ya no tienen atajo de teclado predefinido. El usuario puede asignarlos desde Gestos de entrada.
* Modo "Desactivado" renombrado a "Complemento desactivado" para mayor claridad.
* Limpieza de `sys.path`: la ruta de librerías se elimina tras la importación.

### Mejoras

* Limpieza de código: eliminados imports y funciones no utilizadas.
* Documentación reescrita completamente para usuario final.
* Verificación de límites de palabra al detectar emoticonos clásicos para evitar falsos positivos.

## 1.0.0 (2026-04-18)

### Novedades

* Versión inicial del complemento.
* Detección de emojis Unicode mediante la librería emoji.
* Detección de emoticonos clásicos ASCII mediante la librería emot y diccionarios manuales.
* Tres modos de anuncio: individual, agrupado y eliminado.
* Más de 200 emojis con traducciones manuales al español.
* Panel de configuración avanzado integrado en las opciones de NVDA.
* Soporte para internacionalización (traducible a otros idiomas).
* Script de gestión (`gestionar.bat`) para compilación automatizada.
* Compatible con NVDA 2024.1 y posteriores.
