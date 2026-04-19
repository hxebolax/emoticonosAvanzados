# -*- coding: utf-8 -*-
# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulte el archivo COPYING.txt para más detalles.

"""
Complemento EmoticonosAvanzados para NVDA.

Proporciona detección avanzada de emojis Unicode y emoticonos clásicos
utilizando los diccionarios CLDR de NVDA. Permite configurar cómo NVDA
anuncia los emoticonos: uno por uno, agrupados o eliminados del habla.
"""

import re
import wx

import globalPluginHandler
import globalVars
import config
import api
import speechDictHandler
import ui
import characterProcessing
import languageHandler
import speech
import braille
import textInfos
import gui
import addonHandler
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from scriptHandler import script
from logHandler import log

from .motor import MotorEmoticonos
from .traducciones import EMOTICONOS_MANUALES

addonHandler.initTranslation()

# Constantes
ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]
ADDON_PANEL_TITLE = ADDON_SUMMARY

# Modos de anuncio
MODO_DESACTIVADO = 0
MODO_INDIVIDUAL = 1
MODO_AGRUPADO = 2
MODO_ELIMINADO = 3

# Niveles de logging del complemento
LOG_DESACTIVADO = 0
LOG_INFO = 1
LOG_DEBUG = 2
LOG_COMPLETO = 3

# Especificación de configuración
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

# Instancia global del motor
_motor = None
# Diccionario de habla temporal
_dicHabla = speechDictHandler.SpeechDict()
# Estado del filtro de habla
_filtroRegistrado = False
# Referencia al método original de braille.Region.update para monkey-patching
_original_region_update = None


def _log(mensaje, nivel=LOG_INFO):
	"""
	Registra un mensaje en el visor de registro de NVDA.

	Solo registra si el nivel de logging configurado es igual o superior
	al nivel del mensaje.

	:param mensaje: Texto a registrar.
	:type mensaje: str
	:param nivel: Nivel mínimo requerido (LOG_INFO, LOG_DEBUG, LOG_COMPLETO).
	:type nivel: int
	"""
	try:
		nivel_configurado = config.conf["emoticonosAvanzados"]["nivelLog"]
	except Exception:
		nivel_configurado = LOG_DESACTIVADO

	if nivel_configurado < nivel:
		return

	prefijo = "EmoticonosAvanzados"
	if nivel == LOG_COMPLETO:
		log.info("%s [DETALLE]: %s" % (prefijo, mensaje))
	elif nivel == LOG_DEBUG:
		log.info("%s [DEBUG]: %s" % (prefijo, mensaje))
	else:
		log.info("%s: %s" % (prefijo, mensaje))


def _obtenerMotor():
	"""
	Obtiene o crea la instancia global del motor de emoticonos.

	:return: Instancia del motor.
	:rtype: MotorEmoticonos
	"""
	global _motor
	if _motor is None:
		_motor = MotorEmoticonos(
			ignorar_mayusculas=config.conf["emoticonosAvanzados"]["ignorarMayusculas"],
		)
	return _motor


def _recargarMotor():
	"""
	Recarga el motor con la configuración actual.
	"""
	global _motor
	_motor = MotorEmoticonos(
		ignorar_mayusculas=config.conf["emoticonosAvanzados"]["ignorarMayusculas"],
	)
	_log("Motor recargado con configuración actualizada.", LOG_DEBUG)


def _obtenerSimbolosNVDA():
	"""
	Obtiene los símbolos que NVDA lee mediante su diccionario de símbolos.

	Accede a los procesadores de símbolos de NVDA para obtener
	la lista completa de caracteres que serían verbalizados.

	:return: Diccionario de carácter → descripción.
	:rtype: dict
	"""
	simbolos = {}
	try:
		locale = languageHandler.getLanguage()
		processor = characterProcessing._localeSpeechSymbolProcessors.fetchLocaleData(locale)
		for char, info in processor.computedSymbols.items():
			if len(char) <= 2 and info.replacement:
				simbolos[char] = info.replacement
	except Exception as e:
		log.debug("EmoticonosAvanzados: Error obteniendo símbolos NVDA: %s" % str(e))
	return simbolos


def _construirPatronEmoticono(emoticono):
	"""
	Construye el patrón regex para un emoticono con detección de contexto.

	Para emoticonos como :/ y :-/ se añaden restricciones adicionales
	para evitar detección dentro de URLs (http://, https://, etc.).

	:param emoticono: El emoticono para el que construir el patrón.
	:type emoticono: str
	:return: Patrón regex como string.
	:rtype: str
	"""
	if emoticono in (":/", ":-/"):
		return r"(?<!\w)(?<!http:)(?<!https:)(?<!ftp:)(?<!file:)" + re.escape(emoticono) + r"(?!/)"
	return r"(?<!\w)" + re.escape(emoticono) + r"(?!\w)"


def _construirDiccionario():
	"""
	Construye el diccionario de habla temporal con las entradas de emoticonos.

	En modo individual y eliminado, usa el diccionario de habla temporal.
	En modo agrupado, el procesamiento de emojis se hace mediante un filtro de habla.
	La supresión de símbolos NVDA se aplica siempre mediante el diccionario.
	"""
	global _dicHabla
	_dicHabla = speechDictHandler.SpeechDict()

	modo = config.conf["emoticonosAvanzados"]["modo"]
	if modo == MODO_DESACTIVADO:
		return

	motor = _obtenerMotor()
	formato = config.conf["emoticonosAvanzados"]["formatoDescripcion"]
	prefijo = config.conf["emoticonosAvanzados"]["prefijo"]
	detectarEmojis = config.conf["emoticonosAvanzados"]["detectarEmojis"]
	detectarEmoticonos = config.conf["emoticonosAvanzados"]["detectarEmoticonos"]
	suprimirSimbolos = config.conf["emoticonosAvanzados"]["suprimirSimbolosNVDA"]

	# Suprimir símbolos de NVDA (funciona en todos los modos no desactivados)
	if suprimirSimbolos:
		simbolos = _obtenerSimbolosNVDA()
		for char, descripcion in simbolos.items():
			patron = re.escape(char)
			_dicHabla.append(
				speechDictHandler.SpeechDictEntry(
					patron,
					" ",
					"",
					True,
					speechDictHandler.ENTRY_TYPE_REGEXP,
				)
			)
		_log("Supresión de símbolos NVDA activada: %d símbolos suprimidos." % len(simbolos), LOG_DEBUG)

	# En modo agrupado, los emojis se manejan con el filtro de habla
	if modo == MODO_AGRUPADO:
		return

	if modo == MODO_ELIMINADO:
		# Reemplazar emojis y emoticonos por espacio vacío
		if detectarEmojis:
			for emoji_char, descripcion in motor.obtener_todos_emojis().items():
				patron = re.escape(emoji_char)
				_dicHabla.append(
					speechDictHandler.SpeechDictEntry(
						patron,
						" ",
						"",
						True,
						speechDictHandler.ENTRY_TYPE_REGEXP,
					)
				)
		if detectarEmoticonos:
			for emoticono, descripcion in EMOTICONOS_MANUALES.items():
				patron = _construirPatronEmoticono(emoticono)
				_dicHabla.append(
					speechDictHandler.SpeechDictEntry(
						patron,
						" ",
						"",
						True,
						speechDictHandler.ENTRY_TYPE_REGEXP,
					)
				)
		return

	# Modo individual: cada emoticono se reemplaza por su descripción
	if modo == MODO_INDIVIDUAL:
		texto_prefijo = prefijo + " " if prefijo else ""
		if detectarEmojis:
			for emoji_char, descripcion in motor.obtener_todos_emojis().items():
				patron = re.escape(emoji_char)
				reemplazo = " " + texto_prefijo + formato.format(descripcion) + " "
				_dicHabla.append(
					speechDictHandler.SpeechDictEntry(
						patron,
						reemplazo,
						"",
						True,
						speechDictHandler.ENTRY_TYPE_REGEXP,
					)
				)
		if detectarEmoticonos:
			for emoticono, descripcion in EMOTICONOS_MANUALES.items():
				patron = _construirPatronEmoticono(emoticono)
				reemplazo = " " + texto_prefijo + formato.format(descripcion) + " "
				_dicHabla.append(
					speechDictHandler.SpeechDictEntry(
						patron,
						reemplazo,
						"",
						True,
						speechDictHandler.ENTRY_TYPE_REGEXP,
					)
				)


def _filtroHablaAgrupado(speechSequence):
	"""
	Filtro de habla para el modo agrupado.

	Intercepta las secuencias de habla de NVDA y reemplaza
	los emoticonos repetidos por versiones con conteo.

	:param speechSequence: Secuencia de habla de NVDA.
	:type speechSequence: list
	:return: Secuencia modificada.
	:rtype: list
	"""
	modo = config.conf["emoticonosAvanzados"]["modo"]
	if modo != MODO_AGRUPADO:
		return speechSequence

	motor = _obtenerMotor()
	formato = config.conf["emoticonosAvanzados"]["formatoDescripcion"]
	prefijo = config.conf["emoticonosAvanzados"]["prefijo"]
	texto_prefijo = prefijo + " " if prefijo else ""

	nuevaSecuencia = []
	for item in speechSequence:
		if isinstance(item, str) and item.strip():
			textoModificado = motor.generar_texto_agrupado(
				item,
				formato=texto_prefijo + formato,
			)
			if textoModificado != item:
				_log("Agrupado: '%s' → '%s'" % (item[:50], textoModificado[:50]), LOG_COMPLETO)
			nuevaSecuencia.append(textoModificado)
		else:
			nuevaSecuencia.append(item)

	return nuevaSecuencia


def _activarAnuncio():
	"""
	Activa el anuncio de emoticonos.

	Para modos individual y eliminado, usa el diccionario de habla temporal.
	Para modo agrupado, registra un filtro en speech.extensions.filter_speechSequence.
	"""
	global _filtroRegistrado
	modo = config.conf["emoticonosAvanzados"]["modo"]

	# El diccionario de habla se usa en todos los modos (para emojis y/o símbolos)
	if len(_dicHabla) > 0:
		speechDictHandler.dictionaries["temp"].extend(_dicHabla)

	# El filtro de habla solo se usa en modo agrupado
	if modo == MODO_AGRUPADO:
		if not _filtroRegistrado:
			try:
				from speech.extensions import filter_speechSequence
				filter_speechSequence.register(_filtroHablaAgrupado)
				_filtroRegistrado = True
				_log("Filtro de habla agrupado registrado.", LOG_DEBUG)
			except Exception as e:
				log.warning("EmoticonosAvanzados: No se pudo registrar filtro de habla: %s" % str(e))


def _desactivarAnuncio():
	"""
	Desactiva el anuncio de emoticonos.

	Quita entradas del diccionario temporal y desregistra el filtro de habla.
	"""
	global _filtroRegistrado
	# Quitar del diccionario temporal
	for entrada in _dicHabla:
		if entrada in speechDictHandler.dictionaries["temp"]:
			speechDictHandler.dictionaries["temp"].remove(entrada)

	# Desregistrar filtro de habla
	if _filtroRegistrado:
		try:
			from speech.extensions import filter_speechSequence
			filter_speechSequence.unregister(_filtroHablaAgrupado)
		except Exception:
			pass
		_filtroRegistrado = False


def _obtenerDescripcionBraille(char, motor, formato, texto_prefijo):
	"""
	Obtiene la representación braille de la descripción de un carácter emoji.

	Busca la descripción del emoji en el motor y la traduce a celdas Braille
	usando louisHelper.translate con la tabla actualmente configurada.

	:param char: Carácter emoji a describir.
	:type char: str
	:param motor: Instancia del motor de emoticonos.
	:type motor: MotorEmoticonos
	:param formato: Formato de descripción (ej: "[{}]").
	:type formato: str
	:param texto_prefijo: Prefijo antes de la descripción.
	:type texto_prefijo: str
	:return: Lista de celdas Braille para la descripción, o None si no hay descripción.
	:rtype: list[int] | None
	"""
	import louisHelper
	import louis
	descripcion = motor.obtener_descripcion(char)
	if not descripcion:
		return None
	texto_desc = " " + texto_prefijo + formato.format(descripcion) + " "
	try:
		celdas, _, _, _ = louisHelper.translate(
			[braille.handler.table.fileName, "braille-patterns.cti"],
			texto_desc,
			mode=louis.dotsIO,
		)
		return celdas
	except Exception:
		return None

def _es_modificador_emoji(char):
	"""
	Comprueba si un carácter es un modificador de emoji.

	Estos caracteres modifican emojis adyacentes (variation selectors,
	zero-width joiners, modificadores de tono de piel, etc.) y deben
	absorberse en el reemplazo braille del emoji al que acompañan.

	:param char: Carácter a comprobar.
	:type char: str
	:return: True si es un modificador de emoji.
	:rtype: bool
	"""
	code = ord(char)
	return (
		# Variation Selectors (VS1-VS16)
		0xFE00 <= code <= 0xFE0F
		# Zero-Width Joiner
		or code == 0x200D
		# Combining Enclosing Keycap
		or code == 0x20E3
		# Fitzpatrick Skin Tone Modifiers
		or 0x1F3FB <= code <= 0x1F3FF
	)


def _procesarBrailleEmojis(region):
	"""
	Reemplaza celdas Braille de emojis por las de sus descripciones textuales.

	Sigue el patrón de BrailleExtender: opera DESPUÉS de que Region.update()
	haya completado la traducción a Braille. No modifica rawText ni ninguna
	estructura interna de NVDA. Solo reconstruye brailleCells, brailleToRawPos,
	rawToBraillePos y brailleCursorPos.

	Además absorbe variation selectors, ZWJ y modificadores de tono de piel
	que sigan al emoji detectado, evitando que sus celdas hex aparezcan
	en la línea Braille junto a la descripción.

	:param region: Región Braille ya actualizada por NVDA.
	:type region: braille.Region
	"""
	if not region.rawText or not region.rawText.strip():
		return
	if not region.brailleCells:
		return

	motor = _obtenerMotor()
	formato = config.conf["emoticonosAvanzados"]["formatoDescripcion"]
	prefijo = config.conf["emoticonosAvanzados"]["prefijo"]
	texto_prefijo = prefijo + " " if prefijo else ""

	# Buscar emojis en rawText y preparar reemplazos
	reemplazos = {}
	resultados = motor.detectar_todo(region.rawText)
	if not resultados:
		return

	modo = config.conf["emoticonosAvanzados"]["modo"]
	for item in resultados:
		inicio = item["inicio"]
		fin = item["fin"]

		# Extender fin para absorber modificadores de emoji que siguen
		# (variation selectors, ZWJ, skin tones, keycap)
		while fin < len(region.rawText) and _es_modificador_emoji(region.rawText[fin]):
			fin += 1

		if modo == MODO_ELIMINADO:
			# En modo eliminado: reemplazar por espacio en braille
			import louisHelper
			import louis
			try:
				celdas, _, _, _ = louisHelper.translate(
					[braille.handler.table.fileName, "braille-patterns.cti"],
					" ",
					mode=louis.dotsIO,
				)
			except Exception:
				continue
		else:
			celdas = _obtenerDescripcionBraille(
				region.rawText[inicio:item["fin"]],
				motor, formato, texto_prefijo,
			)
		if celdas is not None:
			reemplazos[inicio] = {
				"fin": fin,
				"celdas": celdas,
			}

	if not reemplazos:
		return

	# Reconstruir las tres estructuras: brailleCells, brailleToRawPos,
	# rawToBraillePos, siguiendo el patrón de BrailleExtender.
	nuevosCeldas = []
	nuevoBrailleToRaw = []
	nuevoRawToBraille = [0] * len(region.rawText)

	# Iterar por rawText posición a posición
	i = 0
	while i < len(region.rawText):
		if i in reemplazos:
			# Esta posición es un emoji → reemplazar sus celdas
			reemplazo = reemplazos[i]
			celdas_desc = reemplazo["celdas"]
			fin_emoji = reemplazo["fin"]

			# El rawToBraillePos para todas las posiciones del emoji
			# (incluyendo modificadores absorbidos) apunta al inicio
			# de las celdas de la descripción
			pos_braille_inicio = len(nuevosCeldas)
			for k in range(i, fin_emoji):
				if k < len(nuevoRawToBraille):
					nuevoRawToBraille[k] = pos_braille_inicio

			# Las celdas de la descripción mapean al primer carácter del emoji
			nuevosCeldas.extend(celdas_desc)
			nuevoBrailleToRaw.extend([i] * len(celdas_desc))

			i = fin_emoji
		else:
			# Carácter normal → copiar celdas originales
			if i < len(region.rawToBraillePos):
				orig_braille_start = region.rawToBraillePos[i]
				# Encontrar el final de las celdas para este carácter
				if i + 1 < len(region.rawToBraillePos):
					orig_braille_end = region.rawToBraillePos[i + 1]
				else:
					orig_braille_end = len(region.brailleCells)

				nuevoRawToBraille[i] = len(nuevosCeldas)
				for bpos in range(orig_braille_start, orig_braille_end):
					if bpos < len(region.brailleCells):
						nuevosCeldas.append(region.brailleCells[bpos])
						nuevoBrailleToRaw.append(i)
			i += 1

	# Actualizar la región con las nuevas estructuras
	region.brailleCells = nuevosCeldas
	region.brailleToRawPos = nuevoBrailleToRaw
	region.rawToBraillePos = nuevoRawToBraille

	# Recalcular brailleCursorPos a partir de cursorPos y el nuevo mapa
	if region.cursorPos is not None and region.cursorPos < len(nuevoRawToBraille):
		region.brailleCursorPos = nuevoRawToBraille[region.cursorPos]




def _parcheado_region_update(self):
	"""
	Versión parcheada de braille.Region.update.

	Llama al método original de NVDA PRIMERO para que complete toda la
	traducción interna (rawText → brailleCells, mapeos, cursor, selección).
	Después, si hay emojis activos, reemplaza las celdas Braille de los
	emojis por las de sus descripciones textuales.

	No modifica rawText, rawTextTypeforms, _rawToContentPos, cursorPos
	ni selectionStart/End. Solo modifica brailleCells, brailleToRawPos,
	rawToBraillePos y brailleCursorPos.
	"""
	# Ejecutar el update original de NVDA completo
	_original_region_update(self)

	# Aplicar reemplazos de emojis en Braille si procede
	try:
		modo = config.conf["emoticonosAvanzados"]["modo"]
		mostrar = config.conf["emoticonosAvanzados"]["mostrarEnBraille"]
		if modo != MODO_DESACTIVADO and mostrar:
			_procesarBrailleEmojis(self)
	except Exception:
		pass


def _instalarParcheBraille():
	"""
	Instala el monkey-patch en braille.Region.update.

	Sigue el patrón de BrailleExtender: parchea Region.update para
	procesar emojis DESPUÉS de la traducción completa de NVDA.
	"""
	global _original_region_update
	if _original_region_update is None:
		_original_region_update = braille.Region.update
		braille.Region.update = _parcheado_region_update
		_log("Parche de Braille (Region.update) instalado.", LOG_DEBUG)


def _desinstalarParcheBraille():
	"""
	Desinstala el monkey-patch de braille.Region.update.

	Restaura el método original de actualización de regiones Braille.
	"""
	global _original_region_update
	if _original_region_update is not None:
		braille.Region.update = _original_region_update
		_original_region_update = None
		_log("Parche de Braille (Region.update) desinstalado.", LOG_DEBUG)


def deshabilitarEnModoSeguro(claseDecorada):
	"""
	Decorador que deshabilita el complemento en modo seguro de NVDA.

	:param claseDecorada: La clase GlobalPlugin a decorar.
	:return: La clase original o una versión vacía si estamos en modo seguro.
	"""
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return claseDecorada


@deshabilitarEnModoSeguro
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""
	Plugin global principal de EmoticonosAvanzados.

	Gestiona la activación/desactivación del complemento, la integración
	con el sistema de habla de NVDA y la interfaz de usuario.
	"""
	# Translators: Categoría de scripts del complemento.
	scriptCategory = _("Emoticonos Avanzados")

	def __init__(self):
		"""
		Inicializa el complemento.
		"""
		super(GlobalPlugin, self).__init__()

		# Inicializar el motor
		try:
			_obtenerMotor()
			_log("Motor de emoticonos inicializado correctamente.")
		except Exception as e:
			log.error("EmoticonosAvanzados: Error al inicializar motor: %s" % str(e))

		# Construir diccionario inicial
		_construirDiccionario()

		# Crear menú
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.menuItem = self.toolsMenu.Append(
			wx.ID_ANY,
			# Translators: Nombre del menú de herramientas.
			_("&Emoticonos Avanzados..."),
			# Translators: Descripción del menú de herramientas.
			_("Abre la configuración de Emoticonos Avanzados"),
		)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onAbrirConfiguracion, self.menuItem)

		# Registrar panel de configuración
		NVDASettingsDialog.categoryClasses.append(PanelConfiguracion)

		# Activar si es necesario
		modo = config.conf["emoticonosAvanzados"]["modo"]
		if modo != MODO_DESACTIVADO:
			_activarAnuncio()

		# Registrar cambio de perfil
		config.post_configProfileSwitch.register(self.alCambiarPerfil)

		# Instalar parche de Braille
		_instalarParcheBraille()

	def terminate(self):
		"""
		Finaliza el complemento limpiando recursos.
		"""
		try:
			self.toolsMenu.Remove(self.menuItem)
			NVDASettingsDialog.categoryClasses.remove(PanelConfiguracion)
		except Exception:
			pass
		_desactivarAnuncio()
		_desinstalarParcheBraille()
		try:
			config.post_configProfileSwitch.unregister(self.alCambiarPerfil)
		except Exception:
			pass

	def alCambiarPerfil(self):
		"""
		Maneja el cambio de perfil de configuración de NVDA.
		"""
		_desactivarAnuncio()
		_recargarMotor()
		_construirDiccionario()
		modo = config.conf["emoticonosAvanzados"]["modo"]
		if modo != MODO_DESACTIVADO:
			_activarAnuncio()

	def onAbrirConfiguracion(self, evt):
		"""
		Abre el diálogo de configuración del complemento.

		:param evt: Evento de menú.
		"""
		gui.mainFrame.popupSettingsDialog(NVDASettingsDialog, PanelConfiguracion)

	@script(
		# Translators: Descripción del gesto para alternar el modo de emoticonos.
		description=_("Alterna entre los modos de anuncio de emoticonos: desactivado, individual, agrupado y eliminado."),
	)
	def script_alternarModo(self, gesture):
		"""
		Alterna entre los modos de anuncio de emoticonos.

		:param gesture: Gesto que activó el script.
		"""
		_desactivarAnuncio()
		modo = config.conf["emoticonosAvanzados"]["modo"]
		modo = (modo + 1) % 4
		config.conf["emoticonosAvanzados"]["modo"] = modo

		_construirDiccionario()
		if modo != MODO_DESACTIVADO:
			_activarAnuncio()

		# Translators: Nombres de los modos de anuncio.
		nombres_modos = [
			_("Complemento desactivado"),
			_("Emoticonos modo individual"),
			_("Emoticonos modo agrupado"),
			_("Emoticonos eliminados del habla"),
		]
		ui.message(nombres_modos[modo])

	@script(
		# Translators: Descripción del gesto para mostrar información del símbolo actual.
		description=_("Muestra información sobre el símbolo o emoticono en la posición del cursor de revisión."),
	)
	def script_mostrarSimboloActual(self, gesture):
		"""
		Muestra la información del símbolo en la posición del cursor de revisión.

		:param gesture: Gesto que activó el script.
		"""
		info = api.getReviewPosition().copy()
		info.expand(textInfos.UNIT_CHARACTER)
		texto = info.text

		if not texto:
			# Translators: Mensaje cuando no hay texto en la posición actual.
			ui.message(_("No hay texto en esta posición"))
			return

		motor = _obtenerMotor()
		resultados = motor.detectar_todo(texto)

		if resultados:
			item = resultados[0]
			# Translators: Formato para mostrar información de un emoticono detectado.
			mensaje = _("Carácter: {caracter}\nTipo: {tipo}\nDescripción: {descripcion}").format(
				caracter=item["valor"],
				tipo=item["tipo"],
				descripcion=item["descripcion"],
			)
			# Translators: Título del diálogo de información del emoticono.
			titulo = _("Información del emoticono")
			ui.browseableMessage(mensaje, titulo, closeButton=True)
		else:
			curLanguage = speech.getCurrentLanguage()
			expandedSymbol = characterProcessing.processSpeechSymbol(curLanguage, texto)
			if expandedSymbol != texto:
				# Translators: Formato para mostrar el reemplazo de un símbolo NVDA.
				mensaje = _("Carácter: {caracter}\nReemplazo: {reemplazo}").format(
					caracter=texto,
					reemplazo=expandedSymbol,
				)
				languageDescription = languageHandler.getLanguageDescription(curLanguage)
				# Translators: Título del diálogo mostrando información del símbolo.
				titulo = _("Símbolo en posición del cursor ({idioma})").format(idioma=languageDescription)
				ui.browseableMessage(mensaje, titulo, closeButton=True)
			else:
				# Translators: Mensaje cuando no hay reemplazo disponible para el símbolo.
				ui.message(_("Sin reemplazo de símbolo"))

	@script(
		# Translators: Descripción del gesto para analizar el portapapeles.
		description=_("Analiza el contenido del portapapeles y muestra los emoticonos encontrados."),
	)
	def script_analizarPortapapeles(self, gesture):
		"""
		Analiza el contenido del portapapeles en busca de emoticonos.

		:param gesture: Gesto que activó el script.
		"""
		try:
			texto = api.getClipData()
		except Exception:
			# Translators: Mensaje cuando no se puede acceder al portapapeles.
			ui.message(_("No se puede acceder al portapapeles"))
			return

		if not texto:
			# Translators: Mensaje cuando el portapapeles está vacío.
			ui.message(_("El portapapeles está vacío"))
			return

		motor = _obtenerMotor()
		resultados = motor.detectar_todo(texto)

		if not resultados:
			# Translators: Mensaje cuando no se encuentran emoticonos en el portapapeles.
			ui.message(_("No se encontraron emoticonos en el portapapeles"))
			return

		agrupados = motor.agrupar_resultados(resultados)
		lineas = []
		for item in agrupados:
			if item["cantidad"] > 1:
				lineas.append(
					# Translators: Formato para emoticono agrupado con cantidad.
					_("{cantidad}x {valor} ({descripcion})").format(
						cantidad=item["cantidad"],
						valor=item["valor"],
						descripcion=item["descripcion"],
					)
				)
			else:
				lineas.append(
					# Translators: Formato para emoticono individual.
					_("{valor} ({descripcion})").format(
						valor=item["valor"],
						descripcion=item["descripcion"],
					)
				)

		# Translators: Estadísticas del portapapeles.
		resumen = _("Total: {total} emoticonos ({unicos} únicos)").format(
			total=len(resultados),
			unicos=len(agrupados),
		)
		mensaje = "\n".join(lineas) + "\n\n" + resumen
		# Translators: Título del diálogo de análisis del portapapeles.
		titulo = _("Análisis de emoticonos del portapapeles")
		ui.browseableMessage(mensaje, titulo, closeButton=True)


class PanelConfiguracion(SettingsPanel):
	"""
	Panel de configuración del complemento en las opciones de NVDA.
	"""
	# Translators: Título del panel de configuración del complemento.
	title = ADDON_PANEL_TITLE

	def makeSettings(self, settingsSizer):
		"""
		Construye los controles del panel de configuración.

		:param settingsSizer: Sizer del panel de configuración.
		"""
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		# Modo de anuncio
		# Translators: Etiqueta para seleccionar el modo de anuncio.
		modoLabel = _("&Modo de anuncio de emoticonos:")
		self.modoChoices = [
			# Translators: Opción de modo desactivado.
			_("Complemento desactivado"),
			# Translators: Opción de modo individual.
			_("Individual (uno por uno)"),
			# Translators: Opción de modo agrupado.
			_("Agrupado (contar repetidos)"),
			# Translators: Opción de modo eliminado.
			_("Eliminado (no leer emoticonos)"),
		]
		self.modoList = sHelper.addLabeledControl(modoLabel, wx.Choice, choices=self.modoChoices)
		self.modoList.Selection = config.conf["emoticonosAvanzados"]["modo"]

		# Detección
		# Translators: Etiqueta para activar la detección de emojis Unicode.
		self.detectarEmojisCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Detectar &emojis Unicode"))
		)
		self.detectarEmojisCheckBox.Value = config.conf["emoticonosAvanzados"]["detectarEmojis"]

		# Translators: Etiqueta para activar la detección de emoticonos clásicos.
		self.detectarEmoticonosCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Detectar emoticonos &clásicos (ej: :) ;D)"))
		)
		self.detectarEmoticonosCheckBox.Value = config.conf["emoticonosAvanzados"]["detectarEmoticonos"]

		# Translators: Etiqueta para suprimir la lectura de símbolos de NVDA.
		self.suprimirSimbolosCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("&Suprimir la lectura de símbolos de NVDA (₧, ©, ®, etc.)"))
		)
		self.suprimirSimbolosCheckBox.Value = config.conf["emoticonosAvanzados"]["suprimirSimbolosNVDA"]

		# Braille
		# Translators: Etiqueta para activar la salida de descripciones en línea Braille.
		self.mostrarBrailleCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Mostrar descripciones de emoticonos en línea &Braille"))
		)
		self.mostrarBrailleCheckBox.Value = config.conf["emoticonosAvanzados"]["mostrarEnBraille"]

		# Translators: Etiqueta para ignorar mayúsculas en emoticonos.
		self.ignorarMayusculasCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("&Ignorar mayúsculas en emoticonos clásicos"))
		)
		self.ignorarMayusculasCheckBox.Value = config.conf["emoticonosAvanzados"]["ignorarMayusculas"]

		# Formato
		# Translators: Etiqueta para el formato de descripción.
		formatoLabel = _("&Formato de descripción (usar {} para el nombre):")
		self.formatoEdit = sHelper.addLabeledControl(formatoLabel, wx.TextCtrl)
		self.formatoEdit.Value = config.conf["emoticonosAvanzados"]["formatoDescripcion"]

		# Translators: Etiqueta para el prefijo del anuncio.
		prefijoLabel = _("&Prefijo al anunciar (vacío para ninguno):")
		self.prefijoEdit = sHelper.addLabeledControl(prefijoLabel, wx.TextCtrl)
		self.prefijoEdit.Value = config.conf["emoticonosAvanzados"]["prefijo"]

		# Nivel de logging
		# Translators: Etiqueta para seleccionar el nivel de registro.
		logLabel = _("Nivel de &registro (logging):")
		self.logChoices = [
			# Translators: Logging desactivado.
			_("Desactivado"),
			# Translators: Logging informativo.
			_("Informativo"),
			# Translators: Logging de depuración.
			_("Depuración"),
			# Translators: Logging completo.
			_("Completo (todo)"),
		]
		self.logList = sHelper.addLabeledControl(logLabel, wx.Choice, choices=self.logChoices)
		self.logList.Selection = config.conf["emoticonosAvanzados"]["nivelLog"]

	def onSave(self):
		"""
		Guarda la configuración del panel.
		"""
		# Desactivar anuncio actual
		_desactivarAnuncio()

		# Guardar configuración
		config.conf["emoticonosAvanzados"]["modo"] = self.modoList.GetSelection()
		config.conf["emoticonosAvanzados"]["detectarEmojis"] = self.detectarEmojisCheckBox.Value
		config.conf["emoticonosAvanzados"]["detectarEmoticonos"] = self.detectarEmoticonosCheckBox.Value
		config.conf["emoticonosAvanzados"]["suprimirSimbolosNVDA"] = self.suprimirSimbolosCheckBox.Value
		config.conf["emoticonosAvanzados"]["mostrarEnBraille"] = self.mostrarBrailleCheckBox.Value
		config.conf["emoticonosAvanzados"]["ignorarMayusculas"] = self.ignorarMayusculasCheckBox.Value
		config.conf["emoticonosAvanzados"]["formatoDescripcion"] = self.formatoEdit.Value
		config.conf["emoticonosAvanzados"]["prefijo"] = self.prefijoEdit.Value
		config.conf["emoticonosAvanzados"]["nivelLog"] = self.logList.GetSelection()

		# Recargar motor y diccionario
		_recargarMotor()
		_construirDiccionario()

		# Reactivar si es necesario
		modo = config.conf["emoticonosAvanzados"]["modo"]
		if modo != MODO_DESACTIVADO:
			_activarAnuncio()
