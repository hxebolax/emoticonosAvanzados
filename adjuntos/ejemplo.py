# -*- coding: utf-8 -*-

"""
Módulo para detectar emojis Unicode y emoticonos clásicos en texto.

Características principales:
- Detecta emojis Unicode.
- Detecta emoticonos clásicos.
- Devuelve posiciones y descripciones.
- Permite agrupar repetidos.
- Genera texto accesible.
- Ofrece resúmenes y estadísticas.

Requisitos:
	pip install emoji emot
"""

import re
import emoji
from emot.emo_unicode import EMOTICONS_EMO


class IdentificadorEmoticonosAvanzado:
	"""
	Clase avanzada para identificar emojis Unicode y emoticonos clásicos.

	La clase permite:
	- Detectar emojis Unicode.
	- Detectar emoticonos clásicos.
	- Obtener descripciones en español.
	- Contar ocurrencias.
	- Agrupar elementos repetidos.
	- Reemplazar por descripciones.
	- Convertir un texto en una versión accesible.
	- Obtener resúmenes y estadísticas detalladas.
	"""

	def __init__(self, ignorar_mayusculas_emoticonos=True):
		"""
		Inicializa la clase y prepara todos los recursos necesarios.

		:param ignorar_mayusculas_emoticonos: Indica si debe detectar variantes como XD y xD como equivalentes.
		:type ignorar_mayusculas_emoticonos: bool
		"""
		self.ignorar_mayusculas_emoticonos = ignorar_mayusculas_emoticonos
		self._intentar_cargar_idioma_espanol_emoji()
		self._traducciones_emoticonos = self._crear_traducciones_emoticonos()
		self._traducciones_emojis = self._crear_traducciones_emojis_manual()
		self._emoticonos_manual = self._crear_emoticonos_manual()
		self._patron_emoticonos_manual = self._crear_patron_emoticonos_manual()
		self._patron_emoticonos_emot = self._crear_patron_emoticonos_emot()

	def _intentar_cargar_idioma_espanol_emoji(self):
		"""
		Intenta cargar el idioma español en la librería emoji.
		"""
		try:
			emoji.config.load_language("es")
		except Exception:
			pass

	def _crear_traducciones_emoticonos(self):
		"""
		Crea el diccionario de traducciones de descripciones de emoticonos.

		:return: Diccionario de traducciones.
		:rtype: dict
		"""
		return {
			"Happy face smiley": "cara feliz",
			"Happy face or smiley": "cara feliz",
			"Laughing": "risa",
			"Wink or smirk": "guiño o sonrisa pícara",
			"Sad face": "cara triste",
			"Cry": "llanto",
			"Tongue sticking out, cheeky, playful or blowing a raspberry": "sacando la lengua, juguetón o burlón",
			"Surprise": "sorpresa",
			"Confused": "confundido",
			"Sealed lips or kiss": "labios sellados o beso",
			"Angel, saint or innocent": "ángel o inocente",
			"Evil or devilish": "diabólico",
			"Cool": "genial",
			"Embarrassed": "avergonzado",
			"Shy": "tímido",
			"Skeptical, annoyed, undecided, uneasy or hesitant": "escéptico o indeciso",
			"Straight face": "cara seria",
			"Grin": "sonrisa amplia",
			"Very happy": "muy feliz",
			"Love": "amor",
			"Kiss": "beso",
			"Cat face": "cara de gato",
			"Robot": "robot",
			"Rose": "rosa",
			"Heart": "corazón",
			"Broken heart": "corazón roto",
			"Sleeping": "durmiendo",
			"Rolling on the floor laughing": "riendo a carcajadas",
			"Disapproval": "desaprobación",
			"Yum or happy": "feliz o saboreando",
			"Silence": "silencio",
			"Thinking": "pensando",
			"Shock": "impacto",
			"Unsure": "inseguro",
			"Party": "fiesta",
			"Music": "música",
			"Happy crying": "llorando de alegría",
			"Dead": "muerto o agotado",
			"Strong laughter": "risa fuerte",
			"Plain": "expresión neutra",
			"Sarcasm": "sarcasmo",
			"Angry": "enfadado",
			"Very sad": "muy triste",
			"Applause": "aplausos",
			"High five": "choca esos cinco",
			"Peace": "paz",
			"Ok": "de acuerdo",
			"Thumbs up": "pulgar arriba",
			"Thumbs down": "pulgar abajo"
		}

	def _crear_traducciones_emojis_manual(self):
		"""
		Crea un diccionario manual de traducciones para emojis frecuentes.

		:return: Diccionario de traducciones.
		:rtype: dict
		"""
		return {
			"😀": "cara sonriendo",
			"😃": "cara sonriendo con boca abierta",
			"😄": "cara sonriendo con ojos sonrientes",
			"😁": "cara radiante",
			"😆": "cara riendo con ojos cerrados",
			"😅": "cara sonriendo con sudor",
			"🤣": "riendo a carcajadas",
			"😂": "cara llorando de risa",
			"🙂": "cara sonriente",
			"🙃": "cara al revés",
			"😉": "cara guiñando un ojo",
			"😊": "cara sonriente con rubor",
			"😇": "cara de ángel",
			"🥰": "cara con corazones",
			"😍": "cara enamorada",
			"🤩": "cara fascinada",
			"😘": "cara lanzando un beso",
			"😗": "cara de beso",
			"😚": "cara besando con ojos cerrados",
			"😙": "cara besando con ojos sonrientes",
			"😋": "cara saboreando",
			"😛": "cara sacando la lengua",
			"😜": "cara guiñando y sacando la lengua",
			"🤪": "cara alocada",
			"😝": "cara con lengua y ojos cerrados",
			"🤑": "cara con dinero",
			"🤗": "cara abrazando",
			"🤭": "cara tapándose la boca",
			"🤫": "cara pidiendo silencio",
			"🤔": "cara pensando",
			"🤐": "cara con boca cerrada",
			"🤨": "cara con ceja levantada",
			"😐": "cara neutra",
			"😑": "cara inexpresiva",
			"😶": "cara sin boca",
			"😏": "cara pícara",
			"😒": "cara de desagrado",
			"🙄": "ojos en blanco",
			"😬": "cara de mueca",
			"🤥": "cara mentirosa",
			"😌": "cara aliviada",
			"😔": "cara pensativa",
			"😪": "cara somnolienta",
			"🤤": "cara babeando",
			"😴": "cara durmiendo",
			"😷": "cara con mascarilla",
			"🤒": "cara enferma",
			"🤕": "cara con vendaje",
			"🤢": "cara mareada",
			"🤮": "cara vomitando",
			"🤧": "cara estornudando",
			"🥵": "cara acalorada",
			"🥶": "cara congelada",
			"🥴": "cara mareada",
			"😵": "cara aturdida",
			"🤯": "cabeza explotando",
			"😕": "cara confundida",
			"😟": "cara preocupada",
			"🙁": "cara ligeramente triste",
			"☹️": "cara triste",
			"😮": "cara sorprendida",
			"😯": "cara asombrada",
			"😲": "cara impactada",
			"😳": "cara sonrojada",
			"🥺": "cara suplicando",
			"😦": "cara triste",
			"😧": "cara angustiada",
			"😨": "cara asustada",
			"😰": "cara con ansiedad",
			"😥": "cara triste con alivio",
			"😢": "cara llorando",
			"😭": "cara llorando mucho",
			"😱": "cara gritando de miedo",
			"😖": "cara frustrada",
			"😣": "cara sufriendo",
			"😞": "cara decepcionada",
			"😓": "cara abatida con sudor",
			"😩": "cara agotada",
			"😫": "cara exhausta",
			"🥱": "bostezo",
			"😤": "cara resoplando",
			"😡": "cara enfadada",
			"😠": "cara molesta",
			"🤬": "cara insultando",
			"😈": "cara diabólica sonriente",
			"👿": "cara diabólica enfadada",
			"💀": "calavera",
			"☠️": "calavera con huesos",
			"💩": "caca sonriente",
			"🤡": "payaso",
			"👹": "ogro",
			"👺": "duende",
			"👻": "fantasma",
			"👽": "alienígena",
			"🤖": "robot",
			"❤️": "corazón rojo",
			"🧡": "corazón naranja",
			"💛": "corazón amarillo",
			"💚": "corazón verde",
			"💙": "corazón azul",
			"💜": "corazón morado",
			"🖤": "corazón negro",
			"🤍": "corazón blanco",
			"🤎": "corazón marrón",
			"💔": "corazón roto",
			"❣️": "exclamación de corazón",
			"💕": "dos corazones",
			"💞": "corazones girando",
			"💓": "corazón latiendo",
			"💗": "corazón creciendo",
			"💖": "corazón brillante",
			"💘": "corazón con flecha",
			"💝": "corazón con lazo",
			"👍": "pulgar hacia arriba",
			"👎": "pulgar hacia abajo",
			"👌": "gesto de acuerdo",
			"✌️": "victoria",
			"🤞": "dedos cruzados",
			"👏": "aplausos",
			"🙌": "manos levantadas",
			"🙏": "manos juntas",
			"💪": "bíceps",
			"🔥": "fuego",
			"⭐": "estrella",
			"🌟": "estrella brillante",
			"✨": "destellos",
			"⚡": "rayo",
			"💯": "cien puntos",
			"✔️": "marca de verificación",
			"✅": "marca verde",
			"❌": "marca de cierre",
			"⚠️": "advertencia",
			"🚀": "cohete",
			"🎉": "fiesta",
			"🎊": "confeti",
			"🎵": "nota musical",
			"🎶": "notas musicales",
			"🔊": "altavoz alto",
			"🔇": "sonido silenciado"
		}

	def _crear_emoticonos_manual(self):
		"""
		Crea un diccionario manual de emoticonos clásicos comunes.

		:return: Diccionario con emoticono y descripción.
		:rtype: dict
		"""
		return {
			":)": "cara feliz",
			":-)": "cara feliz",
			"=)": "cara feliz",
			":]": "cara feliz",
			"(:": "cara feliz",
			"(-:": "cara feliz",
			":D": "risa",
			":-D": "risa",
			"=D": "risa",
			"XD": "risa fuerte",
			"X-D": "risa fuerte",
			"xD": "risa fuerte",
			"xd": "risa fuerte",
			":(": "cara triste",
			":-(": "cara triste",
			"=(": "cara triste",
			":[": "cara triste",
			"):" : "cara triste",
			")-:": "cara triste",
			";)": "guiño",
			";-)": "guiño",
			";D": "guiño con risa",
			";-D": "guiño con risa",
			":P": "sacando la lengua",
			":-P": "sacando la lengua",
			":p": "sacando la lengua",
			":-p": "sacando la lengua",
			"=P": "sacando la lengua",
			"=p": "sacando la lengua",
			";P": "guiño con lengua",
			";-P": "guiño con lengua",
			";p": "guiño con lengua",
			";-p": "guiño con lengua",
			":O": "sorpresa",
			":-O": "sorpresa",
			":o": "sorpresa",
			":-o": "sorpresa",
			":|": "cara seria",
			":-|": "cara seria",
			":/": "duda o incomodidad",
			":-/": "duda o incomodidad",
			":\\": "duda o incomodidad",
			":-\\": "duda o incomodidad",
			":S": "confusión",
			":-S": "confusión",
			":s": "confusión",
			":-s": "confusión",
			":$": "vergüenza",
			":-$": "vergüenza",
			":*": "beso",
			":-*": "beso",
			"<3": "corazón",
			"</3": "corazón roto",
			":'(": "llanto",
			":'-(": "llanto",
			":')": "llorando de alegría",
			":'-)": "llorando de alegría",
			"^^": "alegría",
			"^_^": "alegría",
			"-_-": "aburrimiento",
			"o_O": "sorpresa o desconcierto",
			"O_o": "sorpresa o desconcierto",
			"._.": "expresión apagada",
			">:(": "enfado",
			">:-(": "enfado",
			":3": "cara tierna",
			":-3": "cara tierna"
		}

	def _crear_patron_emoticonos_manual(self):
		"""
		Crea un patrón regex para los emoticonos manuales.

		:return: Patrón compilado.
		:rtype: re.Pattern
		"""
		claves = list(self._emoticonos_manual.keys())
		claves_escapadas = [re.escape(clave) for clave in claves]
		claves_ordenadas = sorted(claves_escapadas, key=len, reverse=True)
		patron = "|".join(claves_ordenadas)

		if self.ignorar_mayusculas_emoticonos:
			return re.compile(patron, re.IGNORECASE)

		return re.compile(patron)

	def _crear_patron_emoticonos_emot(self):
		"""
		Crea un patrón regex usando los emoticonos conocidos por la librería emot.

		:return: Patrón compilado.
		:rtype: re.Pattern
		"""
		try:
			claves = list(EMOTICONS_EMO.keys())
			claves_escapadas = [re.escape(clave) for clave in claves]
			claves_ordenadas = sorted(claves_escapadas, key=len, reverse=True)
			patron = "|".join(claves_ordenadas)

			if self.ignorar_mayusculas_emoticonos:
				return re.compile(patron, re.IGNORECASE)

			return re.compile(patron)
		except Exception:
			return re.compile(r"(?!x)x")

	def _normalizar_clave_emoticono(self, valor):
		"""
		Normaliza un emoticono para comparaciones o agrupaciones.

		:param valor: Emoticono original.
		:type valor: str
		:return: Emoticono normalizado.
		:rtype: str
		"""
		if self.ignorar_mayusculas_emoticonos:
			return valor.lower()

		return valor

	def _obtener_descripcion_emoji(self, valor):
		"""
		Obtiene la descripción de un emoji Unicode.

		:param valor: Emoji.
		:type valor: str
		:return: Descripción en español o aproximada.
		:rtype: str
		"""
		if valor in self._traducciones_emojis:
			return self._traducciones_emojis[valor]

		if valor in emoji.EMOJI_DATA:
			datos = emoji.EMOJI_DATA[valor]
			nombre_es = datos.get("es")

			if nombre_es:
				return nombre_es.replace("_", " ").strip(":")

			nombre_en = datos.get("en")

			if nombre_en:
				return nombre_en.replace("_", " ").strip(":")

		return "emoji sin descripción"

	def _obtener_descripcion_emoticono(self, valor):
		"""
		Obtiene la descripción de un emoticono clásico.

		:param valor: Emoticono clásico.
		:type valor: str
		:return: Descripción en español.
		:rtype: str
		"""
		if valor in self._emoticonos_manual:
			return self._emoticonos_manual[valor]

		if self.ignorar_mayusculas_emoticonos:
			for clave in self._emoticonos_manual:
				if clave.lower() == valor.lower():
					return self._emoticonos_manual[clave]

		descripcion_original = EMOTICONS_EMO.get(valor)

		if descripcion_original is None and self.ignorar_mayusculas_emoticonos:
			for clave in EMOTICONS_EMO:
				if clave.lower() == valor.lower():
					descripcion_original = EMOTICONS_EMO[clave]
					break

		if descripcion_original is None:
			return "emoticono sin descripción"

		if descripcion_original in self._traducciones_emoticonos:
			return self._traducciones_emoticonos[descripcion_original]

		return descripcion_original.lower()

	def _agregar_item(self, resultados, tipo, valor, inicio, fin, descripcion, valor_agrupacion=None):
		"""
		Agrega un resultado a la lista.

		:param resultados: Lista donde añadir el elemento.
		:type resultados: list
		:param tipo: Tipo del elemento.
		:type tipo: str
		:param valor: Valor encontrado.
		:type valor: str
		:param inicio: Índice inicial.
		:type inicio: int
		:param fin: Índice final.
		:type fin: int
		:param descripcion: Descripción del elemento.
		:type descripcion: str
		:param valor_agrupacion: Clave de agrupación.
		:type valor_agrupacion: str or None
		"""
		item = {
			"tipo": tipo,
			"valor": valor,
			"inicio": inicio,
			"fin": fin,
			"descripcion": descripcion,
			"clave_agrupacion": valor_agrupacion if valor_agrupacion is not None else valor
		}
		resultados.append(item)

	def detectar_emojis(self, texto):
		"""
		Detecta emojis Unicode en un texto.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Lista de resultados.
		:rtype: list
		"""
		resultados = []

		try:
			for token in emoji.analyze(texto):
				valor = token.chars
				inicio = token.value.start
				fin = token.value.end
				descripcion = self._obtener_descripcion_emoji(valor)
				self._agregar_item(
					resultados,
					"emoji",
					valor,
					inicio,
					fin,
					descripcion,
					valor
				)
		except Exception:
			pass

		return resultados

	def detectar_emoticonos(self, texto):
		"""
		Detecta emoticonos clásicos en un texto.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Lista de resultados.
		:rtype: list
		"""
		resultados = []
		usados = set()

		for coincidencia in self._patron_emoticonos_manual.finditer(texto):
			inicio = coincidencia.start()
			fin = coincidencia.end()
			valor = coincidencia.group(0)
			descripcion = self._obtener_descripcion_emoticono(valor)
			clave = self._normalizar_clave_emoticono(valor)
			usados.add((inicio, fin))
			self._agregar_item(
				resultados,
				"emoticono",
				valor,
				inicio,
				fin,
				descripcion,
				clave
			)

		for coincidencia in self._patron_emoticonos_emot.finditer(texto):
			inicio = coincidencia.start()
			fin = coincidencia.end()

			if (inicio, fin) in usados:
				continue

			valor = coincidencia.group(0)
			descripcion = self._obtener_descripcion_emoticono(valor)
			clave = self._normalizar_clave_emoticono(valor)
			self._agregar_item(
				resultados,
				"emoticono",
				valor,
				inicio,
				fin,
				descripcion,
				clave
			)

		resultados.sort(key=lambda item: item["inicio"])

		return resultados

	def detectar_todo(self, texto):
		"""
		Detecta emojis y emoticonos en un texto.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Lista ordenada por posición.
		:rtype: list
		"""
		resultados = []
		resultados.extend(self.detectar_emojis(texto))
		resultados.extend(self.detectar_emoticonos(texto))
		resultados.sort(key=lambda item: item["inicio"])
		return resultados

	def detectar(self, texto, incluir_emojis=True, incluir_emoticonos=True):
		"""
		Detecta elementos según los filtros indicados.

		:param texto: Texto a analizar.
		:type texto: str
		:param incluir_emojis: Indica si se deben incluir emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se deben incluir emoticonos.
		:type incluir_emoticonos: bool
		:return: Lista de resultados.
		:rtype: list
		"""
		resultados = []

		if incluir_emojis:
			resultados.extend(self.detectar_emojis(texto))

		if incluir_emoticonos:
			resultados.extend(self.detectar_emoticonos(texto))

		resultados.sort(key=lambda item: item["inicio"])

		return resultados

	def agrupar_resultados(self, resultados, separar_por_tipo=True):
		"""
		Agrupa resultados repetidos y cuenta cuántas veces aparecen.

		:param resultados: Lista de resultados detectados.
		:type resultados: list
		:param separar_por_tipo: Indica si se debe separar por tipo al agrupar.
		:type separar_por_tipo: bool
		:return: Lista agrupada.
		:rtype: list
		"""
		agrupados = {}
		orden = []

		for item in resultados:
			clave_base = item["clave_agrupacion"]

			if separar_por_tipo:
				clave = (item["tipo"], clave_base)
			else:
				clave = clave_base

			if clave not in agrupados:
				agrupados[clave] = {
					"tipo": item["tipo"],
					"valor": item["valor"],
					"descripcion": item["descripcion"],
					"cantidad": 0,
					"posiciones": []
				}
				orden.append(clave)

			agrupados[clave]["cantidad"] += 1
			agrupados[clave]["posiciones"].append((item["inicio"], item["fin"]))

		resultado_final = []

		for clave in orden:
			resultado_final.append(agrupados[clave])

		return resultado_final

	def analizar(self, texto, agrupar_repetidos=False, incluir_emojis=True, incluir_emoticonos=True):
		"""
		Analiza un texto y devuelve resultados normales o agrupados.

		:param texto: Texto a analizar.
		:type texto: str
		:param agrupar_repetidos: Indica si se deben agrupar los repetidos.
		:type agrupar_repetidos: bool
		:param incluir_emojis: Indica si se deben incluir emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se deben incluir emoticonos.
		:type incluir_emoticonos: bool
		:return: Resultados del análisis.
		:rtype: list
		"""
		resultados = self.detectar(
			texto,
			incluir_emojis=incluir_emojis,
			incluir_emoticonos=incluir_emoticonos
		)

		if agrupar_repetidos:
			return self.agrupar_resultados(resultados)

		return resultados

	def contar_emojis(self, texto):
		"""
		Cuenta cuántos emojis hay en un texto.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Cantidad de emojis.
		:rtype: int
		"""
		return len(self.detectar_emojis(texto))

	def contar_emoticonos(self, texto):
		"""
		Cuenta cuántos emoticonos clásicos hay en un texto.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Cantidad de emoticonos.
		:rtype: int
		"""
		return len(self.detectar_emoticonos(texto))

	def contar_todo(self, texto):
		"""
		Cuenta todos los emojis y emoticonos encontrados.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Cantidad total.
		:rtype: int
		"""
		return len(self.detectar_todo(texto))

	def contar_repetidos(self, texto, incluir_emojis=True, incluir_emoticonos=True):
		"""
		Cuenta elementos repetidos agrupándolos.

		Ejemplo:
		Si el texto tiene '😀😀😀 :) :)'
		devuelve algo como:
		[
			{'valor': '😀', 'cantidad': 3},
			{'valor': ':)', 'cantidad': 2}
		]

		:param texto: Texto a analizar.
		:type texto: str
		:param incluir_emojis: Indica si se deben incluir emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se deben incluir emoticonos.
		:type incluir_emoticonos: bool
		:return: Lista agrupada con cantidades.
		:rtype: list
		"""
		resultados = self.detectar(
			texto,
			incluir_emojis=incluir_emojis,
			incluir_emoticonos=incluir_emoticonos
		)
		return self.agrupar_resultados(resultados)

	def hay_emojis(self, texto):
		"""
		Indica si un texto contiene emojis.

		:param texto: Texto a analizar.
		:type texto: str
		:return: True si contiene emojis.
		:rtype: bool
		"""
		return self.contar_emojis(texto) > 0

	def hay_emoticonos(self, texto):
		"""
		Indica si un texto contiene emoticonos clásicos.

		:param texto: Texto a analizar.
		:type texto: str
		:return: True si contiene emoticonos.
		:rtype: bool
		"""
		return self.contar_emoticonos(texto) > 0

	def hay_cualquier_elemento(self, texto):
		"""
		Indica si el texto contiene emojis o emoticonos.

		:param texto: Texto a analizar.
		:type texto: str
		:return: True si contiene alguno.
		:rtype: bool
		"""
		return self.contar_todo(texto) > 0

	def extraer_valores(self, texto, incluir_emojis=True, incluir_emoticonos=True, agrupar_repetidos=False):
		"""
		Extrae solo los valores detectados.

		:param texto: Texto a analizar.
		:type texto: str
		:param incluir_emojis: Indica si se incluyen emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se incluyen emoticonos.
		:type incluir_emoticonos: bool
		:param agrupar_repetidos: Indica si deben agruparse.
		:type agrupar_repetidos: bool
		:return: Lista de valores o lista agrupada.
		:rtype: list
		"""
		resultados = self.analizar(
			texto,
			agrupar_repetidos=agrupar_repetidos,
			incluir_emojis=incluir_emojis,
			incluir_emoticonos=incluir_emoticonos
		)

		if agrupar_repetidos:
			return [
				{
					"valor": item["valor"],
					"cantidad": item["cantidad"],
					"tipo": item["tipo"]
				}
				for item in resultados
			]

		return [item["valor"] for item in resultados]

	def extraer_descripciones(self, texto, incluir_emojis=True, incluir_emoticonos=True, agrupar_repetidos=False):
		"""
		Extrae solo las descripciones detectadas.

		:param texto: Texto a analizar.
		:type texto: str
		:param incluir_emojis: Indica si se incluyen emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se incluyen emoticonos.
		:type incluir_emoticonos: bool
		:param agrupar_repetidos: Indica si deben agruparse.
		:type agrupar_repetidos: bool
		:return: Lista de descripciones o lista agrupada.
		:rtype: list
		"""
		resultados = self.analizar(
			texto,
			agrupar_repetidos=agrupar_repetidos,
			incluir_emojis=incluir_emojis,
			incluir_emoticonos=incluir_emoticonos
		)

		if agrupar_repetidos:
			return [
				{
					"descripcion": item["descripcion"],
					"cantidad": item["cantidad"],
					"tipo": item["tipo"],
					"valor": item["valor"]
				}
				for item in resultados
			]

		return [item["descripcion"] for item in resultados]

	def reemplazar_por_descripciones(self, texto, formato="[{}]", incluir_emojis=True, incluir_emoticonos=True):
		"""
		Reemplaza emojis y emoticonos por sus descripciones.

		:param texto: Texto original.
		:type texto: str
		:param formato: Formato del reemplazo.
		:type formato: str
		:param incluir_emojis: Indica si se reemplazan emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se reemplazan emoticonos.
		:type incluir_emoticonos: bool
		:return: Texto reemplazado.
		:rtype: str
		"""
		resultados = self.detectar(
			texto,
			incluir_emojis=incluir_emojis,
			incluir_emoticonos=incluir_emoticonos
		)

		if not resultados:
			return texto

		partes = []
		ultimo_indice = 0

		for item in resultados:
			partes.append(texto[ultimo_indice:item["inicio"]])
			partes.append(formato.format(item["descripcion"]))
			ultimo_indice = item["fin"]

		partes.append(texto[ultimo_indice:])

		return "".join(partes)

	def convertir_a_texto_accesible(self, texto):
		"""
		Convierte un texto a una versión más accesible.

		:param texto: Texto original.
		:type texto: str
		:return: Texto accesible.
		:rtype: str
		"""
		return self.reemplazar_por_descripciones(texto, formato="[{}]")

	def obtener_estadisticas(self, texto):
		"""
		Obtiene estadísticas detalladas del texto analizado.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Diccionario de estadísticas.
		:rtype: dict
		"""
		emojis = self.detectar_emojis(texto)
		emoticonos = self.detectar_emoticonos(texto)
		todos = []
		todos.extend(emojis)
		todos.extend(emoticonos)
		todos.sort(key=lambda item: item["inicio"])
		agrupados = self.agrupar_resultados(todos)

		return {
			"cantidad_emojis": len(emojis),
			"cantidad_emoticonos": len(emoticonos),
			"cantidad_total": len(todos),
			"cantidad_unicos": len(agrupados),
			"hay_emojis": len(emojis) > 0,
			"hay_emoticonos": len(emoticonos) > 0,
			"hay_elementos": len(todos) > 0
		}

	def obtener_resumen(self, texto, agrupar_repetidos=False):
		"""
		Obtiene un resumen completo del análisis.

		:param texto: Texto a analizar.
		:type texto: str
		:param agrupar_repetidos: Indica si deben agruparse los repetidos.
		:type agrupar_repetidos: bool
		:return: Diccionario resumen.
		:rtype: dict
		"""
		elementos = self.analizar(texto, agrupar_repetidos=agrupar_repetidos)
		estadisticas = self.obtener_estadisticas(texto)

		return {
			"texto_original": texto,
			"texto_accesible": self.convertir_a_texto_accesible(texto),
			"estadisticas": estadisticas,
			"elementos": elementos
		}

	def formatear_agrupados_como_texto(self, texto, incluir_tipo=True):
		"""
		Devuelve un resumen legible de elementos agrupados.

		Ejemplo de salida:
		3 😀
		2 :)
		1 ❤️

		:param texto: Texto a analizar.
		:type texto: str
		:param incluir_tipo: Indica si se debe mostrar el tipo.
		:type incluir_tipo: bool
		:return: Cadena formateada.
		:rtype: str
		"""
		agrupados = self.contar_repetidos(texto)
		lineas = []

		for item in agrupados:
			if incluir_tipo:
				linea = f"{item['cantidad']} {item['valor']} ({item['tipo']})"
			else:
				linea = f"{item['cantidad']} {item['valor']}"

			lineas.append(linea)

		return "\n".join(lineas)

	def obtener_diccionario_repetidos(self, texto, incluir_emojis=True, incluir_emoticonos=True):
		"""
		Devuelve un diccionario simple con valor y cantidad.

		:param texto: Texto a analizar.
		:type texto: str
		:param incluir_emojis: Indica si se incluyen emojis.
		:type incluir_emojis: bool
		:param incluir_emoticonos: Indica si se incluyen emoticonos.
		:type incluir_emoticonos: bool
		:return: Diccionario valor -> cantidad.
		:rtype: dict
		"""
		agrupados = self.contar_repetidos(
			texto,
			incluir_emojis=incluir_emojis,
			incluir_emoticonos=incluir_emoticonos
		)
		resultado = {}

		for item in agrupados:
			resultado[item["valor"]] = item["cantidad"]

		return resultado


if __name__ == "__main__":
	"""
	Bloque de prueba y demostración.
	"""
	texto = "Hola 😀😀😀 :) :-) XD xD <3 </3 😄😄 ;P ;p :'( :')"

	identificador = IdentificadorEmoticonosAvanzado()

	print("=== DETECCIÓN NORMAL ===")
	print()

	for item in identificador.analizar(texto, agrupar_repetidos=False):
		print(
			f"Tipo: {item['tipo']} | "
			f"Valor: {item['valor']} | "
			f"Inicio: {item['inicio']} | "
			f"Fin: {item['fin']} | "
			f"Descripción: {item['descripcion']}"
		)

	print()
	print("=== DETECCIÓN AGRUPADA ===")
	print()

	for item in identificador.analizar(texto, agrupar_repetidos=True):
		print(
			f"Tipo: {item['tipo']} | "
			f"Valor: {item['valor']} | "
			f"Cantidad: {item['cantidad']} | "
			f"Descripción: {item['descripcion']}"
		)

	print()
	print("=== SOLO CANTIDADES ===")
	print()
	print(identificador.formatear_agrupados_como_texto(texto, incluir_tipo=False))

	print()
	print("=== ESTADÍSTICAS ===")
	print()
	print(identificador.obtener_estadisticas(texto))

	print()
	print("=== TEXTO ACCESIBLE ===")
	print()
	print(identificador.convertir_a_texto_accesible(texto))