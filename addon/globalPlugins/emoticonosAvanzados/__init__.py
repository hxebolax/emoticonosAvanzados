# -*- coding: utf-8 -*-
# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulte el archivo COPYING.txt para más detalles.

"""
Complemento EmoticonosAvanzados para NVDA.

Proporciona detección avanzada de emojis Unicode y emoticonos clásicos
utilizando las librerías emoji y emot. Permite configurar cómo NVDA
anuncia los emoticonos: uno por uno, agrupados o eliminados del habla.
"""

import os
import re
import sys
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
import textInfos
import gui
import addonHandler
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from scriptHandler import script
from logHandler import log

# Añadir la carpeta de librerías empaquetadas al path temporalmente
_libsPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "libs")
_libsPathAgregado = False
if os.path.isdir(_libsPath) and _libsPath not in sys.path:
	sys.path.insert(0, _libsPath)
	_libsPathAgregado = True

from .motor import MotorEmoticonos
from .traducciones import EMOTICONOS_MANUALES

# Limpiar sys.path: ya no necesitamos la ruta una vez importados los módulos
if _libsPathAgregado and _libsPath in sys.path:
	sys.path.remove(_libsPath)

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
	"usarLibreriaEmoji": "boolean(default=True)",
	"usarLibreriaEmot": "boolean(default=True)",
	"usarTraduccionesManual": "boolean(default=True)",
	"prefijo": 'string(default="")',
	"separadorAgrupado": 'string(default=", ")',
	"nivelLog": "integer(default=0)",
}
config.conf.spec["emoticonosAvanzados"] = confspec

# Instancia global del motor
_motor = None
# Diccionario de habla temporal
_dicHabla = speechDictHandler.SpeechDict()
# Estado del filtro de habla
_filtroRegistrado = False


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
			usar_emoji=config.conf["emoticonosAvanzados"]["usarLibreriaEmoji"],
			usar_emot=config.conf["emoticonosAvanzados"]["usarLibreriaEmot"],
			usar_manual=config.conf["emoticonosAvanzados"]["usarTraduccionesManual"],
		)
	return _motor


def _recargarMotor():
	"""
	Recarga el motor con la configuración actual.
	"""
	global _motor
	_motor = MotorEmoticonos(
		ignorar_mayusculas=config.conf["emoticonosAvanzados"]["ignorarMayusculas"],
		usar_emoji=config.conf["emoticonosAvanzados"]["usarLibreriaEmoji"],
		usar_emot=config.conf["emoticonosAvanzados"]["usarLibreriaEmot"],
		usar_manual=config.conf["emoticonosAvanzados"]["usarTraduccionesManual"],
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
				patron = r"(?<!\w)" + re.escape(emoticono) + r"(?!\w)"
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
				patron = r"(?<!\w)" + re.escape(emoticono) + r"(?!\w)"
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

		# Librerías
		# Translators: Etiqueta para activar la librería emoji.
		self.usarEmojiCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Usar librería e&moji (Unicode completo)"))
		)
		self.usarEmojiCheckBox.Value = config.conf["emoticonosAvanzados"]["usarLibreriaEmoji"]

		# Translators: Etiqueta para activar la librería emot.
		self.usarEmotCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Usar librería emo&t (emoticonos ASCII)"))
		)
		self.usarEmotCheckBox.Value = config.conf["emoticonosAvanzados"]["usarLibreriaEmot"]

		# Translators: Etiqueta para activar las traducciones manuales.
		self.usarManualCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Usar traducciones ma&nuales en español"))
		)
		self.usarManualCheckBox.Value = config.conf["emoticonosAvanzados"]["usarTraduccionesManual"]

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
		config.conf["emoticonosAvanzados"]["usarLibreriaEmoji"] = self.usarEmojiCheckBox.Value
		config.conf["emoticonosAvanzados"]["usarLibreriaEmot"] = self.usarEmotCheckBox.Value
		config.conf["emoticonosAvanzados"]["usarTraduccionesManual"] = self.usarManualCheckBox.Value
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
