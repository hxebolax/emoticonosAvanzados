# -*- coding: utf-8 -*-
# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulte el archivo COPYING.txt para más detalles.

"""
Variables de compilación del complemento EmoticonosAvanzados.

Este archivo configura toda la información del complemento utilizada
por SCons para generar el archivo .nvda-addon.
"""

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _


# Información del complemento
addon_info = AddonInfo(
	addon_name="emoticonosAvanzados",
	# Translators: Resumen del complemento.
	addon_summary=_("Emoticonos Avanzados"),
	# Translators: Descripción del complemento.
	addon_description=_(
		"""Complemento avanzado para la detección y anuncio de emojis Unicode y emoticonos clásicos.
Permite configurar cómo NVDA anuncia los emoticonos: uno por uno, agrupando repetidos o eliminándolos del habla.
Utiliza los diccionarios CLDR de NVDA para una detección exhaustiva con más de 3900 descripciones en español."""
	),
	addon_version="1.3.4",
	# Translators: Registro de cambios del complemento.
	addon_changelog=_(
		"""* Versión inicial.
* Detección de emojis Unicode y emoticonos clásicos.
* Modos: individual, agrupado y eliminado.
* Configuración avanzada desde las opciones de NVDA.
* Compatible con NVDA 2024.1 y posteriores."""
	),
	addon_author="Héctor J. Benítez Corredera <xebolax@gmail.com>",
	addon_url="https://github.com/hxebolax/emoticonosAvanzados",
	addon_sourceURL="https://github.com/hxebolax/emoticonosAvanzados",
	addon_docFileName="readme.html",
	addon_minimumNVDAVersion="2024.1",
	addon_lastTestedNVDAVersion="2026.1",
	addon_updateChannel=None,
	addon_license="GPL v2",
	addon_licenseURL="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
)

# Archivos fuente de Python del complemento
pythonSources: list[str] = [
	"addon/globalPlugins/*.py",
	"addon/globalPlugins/**/*.py",
]

# Archivos con cadenas traducibles
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Archivos excluidos de la compilación
excludedFiles: list[str] = []

# Idioma base del complemento (español)
baseLanguage: str = "es"

# Extensiones de Markdown
markdownExtensions: list[str] = []

# Tablas braille personalizadas
brailleTables: BrailleTables = {}

# Diccionarios de símbolos de habla
symbolDictionaries: SymbolDictionaries = {}
