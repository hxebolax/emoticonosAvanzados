# Registro de cambios

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
