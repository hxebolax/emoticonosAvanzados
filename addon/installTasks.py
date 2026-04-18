# -*- coding: utf-8 -*-
# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulte el archivo COPYING.txt para más detalles.

"""
Tareas de instalación del complemento EmoticonosAvanzados.

Se ejecuta al instalar o actualizar el complemento en NVDA.
"""

import config
import addonHandler

# Registrar la especificación de configuración
confspec = {
	"modo": "integer(default=0)",
	"detectarEmojis": "boolean(default=True)",
	"detectarEmoticonos": "boolean(default=True)",
	"suprimirSimbolosNVDA": "boolean(default=False)",
	"formatoDescripcion": 'string(default="[{}]")',
	"ignorarMayusculas": "boolean(default=True)",
	"prefijo": 'string(default="")',
	"separadorAgrupado": 'string(default=", ")',
	"nivelLog": "integer(default=0)",
	"mostrarEnBraille": "boolean(default=False)",
}
config.conf.spec["emoticonosAvanzados"] = confspec

addonHandler.initTranslation()


def onInstall():
	"""
	Se ejecuta al instalar el complemento.

	Preserva la configuración existente del usuario si la hay.
	Elimina claves obsoletas de versiones anteriores.
	"""
	try:
		if "emoticonosAvanzados" in config.conf:
			# Eliminar claves obsoletas de versiones anteriores
			claves_obsoletas = [
				"detectarCldr",
				"usarLibreriaEmoji",
				"usarLibreriaEmot",
				"usarTraduccionesManual",
			]
			for clave in claves_obsoletas:
				if clave in config.conf["emoticonosAvanzados"]:
					del config.conf["emoticonosAvanzados"][clave]
	except Exception:
		pass

