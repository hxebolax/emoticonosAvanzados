# 💡 EmoticonosAvanzados — Ideas y Mejoras Futuras

> [!NOTE]
> Este documento recopila ideas de mejora que podrían dar un plus significativo al complemento. Están organizadas por prioridad y dificultad estimada de implementación.

---

## 🔴 Prioridad Alta — Mayor Impacto para el Usuario

### 1. Diccionario de Emoticonos Personalizable por el Usuario

**Descripción**: Permitir al usuario añadir, editar y eliminar emoticonos y sus descripciones desde un diálogo accesible en NVDA.

**Beneficio**: Los usuarios podrán personalizar traducciones, corregir las que no les gusten, o añadir emoticonos específicos de sus comunidades (Discord, Twitch, etc).

**Implementación sugerida**:
- Nuevo diálogo wx con lista editable (similar al gestor de diccionarios de NVDA)
- Almacenar diccionario personalizado en un JSON en la carpeta de configuración del addon
- Prioridad: usuario → manual → librería

**Dificultad**: ⭐⭐⭐ Media  
**Archivos afectados**: `__init__.py` (nuevo diálogo), `motor.py` (carga de diccionario custom), nuevo archivo `diccionario_usuario.py`

---

### 2. Soporte Multiidioma Real para Descripciones

**Descripción**: Actualmente las traducciones manuales solo están en español. Crear archivos de traducción separados por idioma o integrar mejor el sistema de gettext para las descripciones.

**Beneficio**: Abre el complemento a la comunidad internacional de NVDA (inglés, francés, portugués, etc).

**Implementación sugerida**:
- Extraer las descripciones de `traducciones.py` a archivos `.po` traducibles
- O crear archivos JSON por idioma (`traducciones_en.json`, `traducciones_fr.json`, etc.)
- Cargar automáticamente según el idioma de NVDA (`languageHandler.getLanguage()`)

**Dificultad**: ⭐⭐⭐⭐ Alta  
**Archivos afectados**: `traducciones.py` (refactorización mayor), `motor.py`, sistema de build

---

### 3. Buscador de Emojis Integrado

**Descripción**: Un diálogo donde el usuario pueda buscar emojis por nombre o descripción, ver su representación y copiarlos al portapapeles.

**Beneficio**: Muy útil para personas ciegas que quieren usar emojis en sus mensajes pero no saben cuáles existen o cómo encontrarlos.

**Implementación sugerida**:
- Nuevo diálogo wx con campo de búsqueda, lista de resultados y botón "Copiar"
- Búsqueda en tiempo real sobre `TRADUCCIONES_EMOJIS_MANUAL`
- Filtros por categoría (caras, animales, comida, etc.)
- Historial de emojis usados recientemente

**Dificultad**: ⭐⭐⭐ Media  
**Archivos afectados**: `__init__.py` (nuevo diálogo y script), `traducciones.py` (metadata de categorías)

---

### 4. Actualización Automática de la Base de Traducciones

**Descripción**: Mecanismo para actualizar las traducciones manuales sin reinstalar el complemento completo.

**Beneficio**: Permite publicar correcciones y nuevas traducciones de forma ágil.

**Implementación sugerida**:
- Archivo JSON remoto con las traducciones versionadas
- Botón "Buscar actualizaciones de traducciones" en el panel de configuración
- Descarga y merge con el diccionario local
- Respetar personalizaciones del usuario

**Dificultad**: ⭐⭐⭐⭐ Alta  
**Archivos afectados**: `__init__.py`, nuevo módulo `actualizador.py`

---

## 🟡 Prioridad Media — Mejora Significativa

### 5. Perfiles Rápidos de Configuración

**Descripción**: Permitir guardar y cargar conjuntos de configuración con nombres personalizados (ej: "Chat", "Lectura", "Trabajo").

**Beneficio**: Los usuarios podrían tener configuraciones diferentes para distintos contextos con un solo atajo de teclado.

**Implementación sugerida**:
- Usar los perfiles de configuración nativos de NVDA como base
- O implementar perfiles propios con presets guardados en JSON
- Script para cambiar de perfil rápidamente

**Dificultad**: ⭐⭐ Baja (si se usan perfiles nativos NVDA)  

---

### 6. Estadísticas de Uso

**Descripción**: Registro de los emojis más encontrados por el usuario, con opción de ver un resumen.

**Beneficio**: Los usuarios curiosos pueden ver qué emojis les envían más. También útil para debug.

**Implementación sugerida**:
- Contador en memoria (no persistente por defecto, opción para guardar)
- Nuevo script "Ver estadísticas" que muestre un `browseableMessage`
- Top 10 emojis, total detectados por sesión, distribución por tipo

**Dificultad**: ⭐⭐ Baja  
**Archivos afectados**: `motor.py` o `__init__.py` (tracking), nuevo diálogo

---

### 7. Modo "Solo Emojis Relevantes"

**Descripción**: Un modo que solo anuncia los emojis que NO son de caras (reacciones), priorizando los emojis "informativos" (banderas, objetos, símbolos).

**Beneficio**: En chats llenos de caritas, el usuario podría filtrar y solo escuchar los emojis que aportan información contextual.

**Implementación sugerida**:
- Clasificar emojis por categoría en `traducciones.py`
- Opciones de checkboxes por categoría en el panel de configuración
- Filtro en `_construirDiccionario()` basado en categorías habilitadas

**Dificultad**: ⭐⭐⭐ Media  

---

### 8. Soporte para Tonos de Piel en Emojis

**Descripción**: Detectar y describir los modificadores de tono de piel (🏻🏼🏽🏾🏿) que se aplican a emojis de personas.

**Beneficio**: Proporciona información completa sobre el emoji exacto que se muestra.

**Implementación sugerida**:
- Detectar secuencias de emoji + modificador Fitzpatrick
- Añadir descripción del tono: "pulgar arriba tono de piel claro"
- Opción configurable para activar/desactivar la descripción del tono

**Dificultad**: ⭐⭐⭐ Media  
**Archivos afectados**: `motor.py` (detección de modificadores), `traducciones.py` (descripciones de tonos)

---

### 9. Atajos Rápidos por Modo

**Descripción**: Permitir asignar un atajo directo a cada modo en lugar de tener solo el script de "alternar" que rota por los 4 modos.

**Beneficio**: Acceso inmediato al modo deseado sin tener que rotar.

**Implementación sugerida**:
- 4 scripts adicionales: `script_modoDesactivado`, `script_modoIndividual`, `script_modoAgrupado`, `script_modoEliminado`
- Cada uno establece directamente el modo sin rotar

**Dificultad**: ⭐ Muy Baja  
**Archivos afectados**: `__init__.py`

---

### 10. Detección de Emojis en Braille

**Descripción**: Mostrar las descripciones de emojis también en la línea Braille, con formato configurable.

**Beneficio**: Los usuarios de línea Braille también se beneficiarían del complemento.

**Implementación sugerida**:
- Investigar `braille.handler.handleUpdate` y `brailleRegions`
- Posiblemente usar los mismos reemplazos del speech dict, que según la API de NVDA deberían afectar también al Braille
- Verificar y ajustar si el formato `[descripción]` se muestra correctamente en Braille

**Dificultad**: ⭐⭐⭐ Media (requiere investigación)  

---

## 🟢 Prioridad Baja — Nice to Have

### 11. Sonidos Personalizados al Detectar Emojis

**Descripción**: Reproducir un breve sonido (beep o wav) antes o en lugar de la descripción de ciertos emojis.

**Beneficio**: Experiencia más inmersiva, especialmente para emojis muy comunes que el usuario ya reconoce.

**Implementación sugerida**:
- Carpeta `sounds/` con archivos .wav
- Mapa emoji → sonido configurable
- Usar `nvwave.playWaveFile()` de NVDA

**Dificultad**: ⭐⭐ Baja  

---

### 12. Modo Didáctico / Aprendizaje

**Descripción**: Un modo especial que, al pasar por un emoji, muestra información extendida: categoría, variantes, código Unicode, etc.

**Beneficio**: Útil para personas que quieren aprender sobre emojis o para desarrolladores.

**Implementación sugerida**:
- Ampliar `script_mostrarSimboloActual` con más información
- Añadir código Unicode (U+xxxx), categoría del emoji, subcategoría
- Mostrar emojis relacionados

**Dificultad**: ⭐⭐ Baja  

---

### 13. Copiar Texto Sin Emojis

**Descripción**: Un script que copie al portapapeles el texto seleccionado pero sin emojis (o con emojis reemplazados por sus descripciones).

**Beneficio**: Útil al compartir textos con personas que no tienen soporte de emojis o al pegar en campos de texto plano.

**Implementación sugerida**:
- Nuevo script que lea la selección actual
- Procesar con el motor
- Copiar al portapapeles la versión procesada

**Dificultad**: ⭐⭐ Baja  
**Archivos afectados**: `__init__.py` (nuevo script)

---

### 14. Compatibilidad con Emojis Personalizados de Plataformas

**Descripción**: Detectar emojis personalizados de Discord (`:nombre_custom:`), Slack, Twitch, etc.

**Beneficio**: Millones de usuarios usan estas plataformas y sus emojis personalizados no son detectados.

**Implementación sugerida**:
- Regex para detectar patrones `:texto:` que no sean emoticonos clásicos
- Base de datos de emojis comunes de Discord/Twitch
- Opción configurable por plataforma

**Dificultad**: ⭐⭐⭐⭐ Alta  

---

### 15. Exportar/Importar Configuración

**Descripción**: Permitir exportar la configuración completa del complemento (incluyendo diccionarios personalizados) a un archivo, e importarla en otra instalación.

**Beneficio**: Facilita la migración entre equipos y el compartir configuraciones entre usuarios.

**Implementación sugerida**:
- Exportar a JSON con todas las opciones + diccionario personalizado
- Botones "Exportar" e "Importar" en el panel de configuración

**Dificultad**: ⭐⭐ Baja  

---

## 🔵 Ideas Innovadoras — Diferencial

### 16. Integración con IA para Descripciones Contextuales

**Descripción**: Usar un modelo local pequeño (o API) para generar descripciones contextuales de secuencias de emojis. Por ejemplo, "😂😂😂👍" → "riendo mucho y aprobando".

**Beneficio**: Comprensión más natural de las intenciones detrás de combinaciones de emojis.

**Implementación sugerida**:
- Integración opcional con un modelo local pequeño
- Patrón: detectar secuencia → generar descripción → cachear resultado
- Solo activable manualmente (no en tiempo real por rendimiento)

**Dificultad**: ⭐⭐⭐⭐⭐ Muy Alta  

---

### 17. Emojis Favoritos / Acceso Rápido

**Descripción**: Panel de emojis favoritos que el usuario puede configurar y acceder rápidamente para insertar en cualquier campo de texto.

**Beneficio**: Panel de emojis accesible propio de NVDA, sin depender del selector de emojis de Windows (que puede no ser completamente accesible).

**Implementación sugerida**:
- Lista de favoritos almacenada en configuración
- Diálogo wx con lista de favoritos
- Doble enter o botón para insertar en el foco actual
- Organización por categorías o por uso frecuente

**Dificultad**: ⭐⭐⭐ Media  

---

### 18. Tests Unitarios Automatizados

**Descripción**: Suite de tests para el motor de detección que pueda ejecutarse sin NVDA.

**Beneficio**: Asegura que los cambios no introducen regresiones, especialmente en la detección de falsos positivos.

**Implementación sugerida**:
- `tests/` con pytest
- Mockear las APIs de NVDA (`logHandler`, etc.)
- Tests para: detección de emojis, detección de emoticonos, boundary checking, agrupación, traducciones
- CI/CD con GitHub Actions

**Dificultad**: ⭐⭐⭐ Media  

---

### 19. Documentación Web del Complemento

**Descripción**: Crear una página web accesible con documentación, FAQ, y selector de descargas.

**Beneficio**: Presencia profesional del complemento, facilita la distribución.

**Implementación sugerida**:
- GitHub Pages con tema accesible
- Misma documentación del readme.md pero con navegación
- Sección de FAQ respondiendo dudas comunes
- Enlace de descarga directa

**Dificultad**: ⭐⭐ Baja  

---

### 20. Modo de Lectura Continua Inteligente

**Descripción**: En modo lectura continua (NVDA+flecha abajo), agrupar todos los emojis de un párrafo al final en lugar de intercalarlos con el texto.

**Beneficio**: Lectura más fluida en textos con muchos emojis intercalados.

**Implementación sugerida**:
- Filtro de habla que detecte modo lectura continua
- Recopilar emojis del fragmento y añadirlos al final como resumen
- Ejemplo: "Me encanta esto 😍 es genial 🔥" → "Me encanta esto es genial. Emojis: cara enamorada, fuego"

**Dificultad**: ⭐⭐⭐⭐ Alta (requiere hooks avanzados de NVDA)  

---

## Resumen por Dificultad

| Dificultad | Ideas |
|------------|-------|
| ⭐ Muy Baja | #9 Atajos rápidos por modo |
| ⭐⭐ Baja | #5 Perfiles rápidos, #6 Estadísticas, #11 Sonidos, #12 Didáctico, #13 Copiar sin emojis, #15 Export/Import, #19 Web |
| ⭐⭐⭐ Media | #1 Diccionario custom, #3 Buscador, #7 Solo relevantes, #8 Tonos de piel, #10 Braille, #17 Favoritos, #18 Tests |
| ⭐⭐⭐⭐ Alta | #2 Multiidioma, #4 Actualización auto, #14 Emojis custom, #20 Lectura inteligente |
| ⭐⭐⭐⭐⭐ Muy Alta | #16 IA contextual |

---

> [!TIP]
> **Recomendación de implementación por fases:**
> - **Fase 1** (quick wins): #9, #13, #12 — poco esfuerzo, buen valor añadido
> - **Fase 2** (valor alto): #1, #3, #6 — funcionalidades que los usuarios pedirán
> - **Fase 3** (profesionalización): #18, #19, #15 — calidad y mantenibilidad
> - **Fase 4** (expansión): #2, #8, #10 — alcance internacional y completitud
> - **Fase 5** (innovación): #16, #17, #20 — diferenciales únicos
