# -*- coding: utf-8 -*-
# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulte el archivo COPYING.txt para más detalles.

"""
Motor de detección de emoticonos y emojis.

Módulo central que utiliza los diccionarios CLDR de NVDA para detectar,
clasificar, agrupar y describir emojis Unicode y emoticonos clásicos.
"""

import re

from logHandler import log

from .traducciones import TRADUCCIONES_EMOJIS, EMOTICONOS_MANUALES


def _es_alfanumerico(char):
	"""
	Comprueba si un carácter es alfanumérico (letra o dígito).

	Se usa para la verificación de límites de palabra: un emoticono
	no debería detectarse si está rodeado de letras o dígitos.

	:param char: Carácter a comprobar.
	:type char: str
	:return: True si es alfanumérico.
	:rtype: bool
	"""
	return char.isalnum()


class MotorEmoticonos:
	"""
	Motor avanzado para identificar emojis Unicode y emoticonos clásicos.

	Utiliza el diccionario CLDR de NVDA en español junto con emoticonos
	ASCII manuales para ofrecer detección exhaustiva con descripciones localizadas.

	:param ignorar_mayusculas: Si True, trata variantes como XD/xD como iguales.
	:type ignorar_mayusculas: bool
	:param usar_manual: Si True, utiliza las traducciones manuales.
	:type usar_manual: bool
	"""

	def __init__(self, ignorar_mayusculas=True, usar_manual=True):
		"""
		Inicializa el motor con la configuración dada.
		"""
		self.ignorar_mayusculas = ignorar_mayusculas
		self.usar_manual = usar_manual

		self._traducciones_emojis = TRADUCCIONES_EMOJIS
		self._emoticonos_manual = EMOTICONOS_MANUALES

		# Compilar patrones para detección
		self._patron_manual = self._crear_patron_manual()
		self._patron_emojis = self._crear_patron_emojis()

	def _crear_patron_manual(self):
		"""
		Crea un patrón regex para los emoticonos manuales ASCII.

		:return: Patrón regex compilado.
		:rtype: re.Pattern
		"""
		if not self.usar_manual or not self._emoticonos_manual:
			return re.compile(r"(?!x)x")

		claves = list(self._emoticonos_manual.keys())
		claves_escapadas = [re.escape(c) for c in claves]
		claves_ordenadas = sorted(claves_escapadas, key=len, reverse=True)
		patron = "|".join(claves_ordenadas)

		if self.ignorar_mayusculas:
			return re.compile(patron, re.IGNORECASE)
		return re.compile(patron)

	def _crear_patron_emojis(self):
		"""
		Crea un patrón regex para detectar emojis Unicode del diccionario CLDR.

		Ordena los emojis por longitud descendente para que las secuencias
		compuestas (como emojis con modificadores de tono de piel o ZWJ)
		se detecten antes que sus componentes individuales.

		:return: Patrón regex compilado.
		:rtype: re.Pattern
		"""
		if not self._traducciones_emojis:
			return re.compile(r"(?!x)x")

		try:
			claves = list(self._traducciones_emojis.keys())
			claves_escapadas = [re.escape(c) for c in claves]
			claves_ordenadas = sorted(claves_escapadas, key=len, reverse=True)
			patron = "|".join(claves_ordenadas)
			return re.compile(patron)
		except Exception as e:
			log.warning("EmoticonosAvanzados: Error creando patrón de emojis: %s" % str(e))
			return re.compile(r"(?!x)x")

	def _validar_limites(self, texto, inicio, fin):
		"""
		Verifica que un emoticono detectado no esté dentro de una palabra
		ni en un contexto de URL u otra secuencia especial.

		Un emoticono es válido solo si:
		- Está al inicio del texto O el carácter anterior NO es alfanumérico.
		- Está al final del texto O el carácter siguiente NO es alfanumérico.
		- No está dentro de una secuencia URL (como http://).

		:param texto: Texto completo.
		:type texto: str
		:param inicio: Índice de inicio de la coincidencia.
		:type inicio: int
		:param fin: Índice de fin de la coincidencia.
		:type fin: int
		:return: True si el emoticono está correctamente delimitado.
		:rtype: bool
		"""
		# Comprobar carácter anterior
		if inicio > 0 and _es_alfanumerico(texto[inicio - 1]):
			return False

		# Comprobar carácter siguiente
		if fin < len(texto) and _es_alfanumerico(texto[fin]):
			return False

		# Comprobar contexto de URL: si el emoticono :/ está seguido de /
		# o si el emoticono está precedido por ":" + algo que forme ://
		emoticono = texto[inicio:fin]
		if emoticono in (":/", ":-/"):
			# Si hay otro / justo después, es parte de una URL (://)
			if fin < len(texto) and texto[fin] == "/":
				return False
			# Si hay esquema de URL antes (http:, https:, ftp:, etc.)
			if inicio >= 4:
				antes = texto[max(0, inicio - 8):inicio].lower()
				if any(antes.endswith(s) for s in ("http:", "https:", "ftp:", "ftps:", "file:")):
					return False

		return True

	def _normalizar_clave(self, valor):
		"""
		Normaliza un emoticono para comparaciones o agrupaciones.

		:param valor: Emoticono original.
		:type valor: str
		:return: Emoticono normalizado.
		:rtype: str
		"""
		if self.ignorar_mayusculas:
			return valor.lower()
		return valor

	def _obtener_descripcion_emoji(self, valor):
		"""
		Obtiene la descripción de un emoji Unicode desde el diccionario CLDR.

		:param valor: Carácter emoji.
		:type valor: str
		:return: Descripción en español.
		:rtype: str
		"""
		if valor in self._traducciones_emojis:
			return self._traducciones_emojis[valor]

		return "emoji sin descripción"

	def _obtener_descripcion_emoticono(self, valor):
		"""
		Obtiene la descripción de un emoticono clásico ASCII.

		:param valor: Emoticono clásico (ej: :) ;D).
		:type valor: str
		:return: Descripción en español.
		:rtype: str
		"""
		# Buscar en emoticonos manuales
		if valor in self._emoticonos_manual:
			return self._emoticonos_manual[valor]

		if self.ignorar_mayusculas:
			for clave in self._emoticonos_manual:
				if clave.lower() == valor.lower():
					return self._emoticonos_manual[clave]

		return "emoticono sin descripción"

	def _agregar_item(self, resultados, tipo, valor, inicio, fin, descripcion, valor_agrupacion=None):
		"""
		Agrega un resultado detectado a la lista.

		:param resultados: Lista de resultados.
		:type resultados: list
		:param tipo: Tipo del elemento ("emoji" o "emoticono").
		:type tipo: str
		:param valor: Valor encontrado.
		:type valor: str
		:param inicio: Índice de inicio en el texto.
		:type inicio: int
		:param fin: Índice de fin en el texto.
		:type fin: int
		:param descripcion: Descripción del elemento.
		:type descripcion: str
		:param valor_agrupacion: Clave para agrupar elementos iguales.
		:type valor_agrupacion: str or None
		"""
		item = {
			"tipo": tipo,
			"valor": valor,
			"inicio": inicio,
			"fin": fin,
			"descripcion": descripcion,
			"clave_agrupacion": valor_agrupacion if valor_agrupacion is not None else valor,
		}
		resultados.append(item)

	def detectar_emojis(self, texto):
		"""
		Detecta emojis Unicode en un texto usando el diccionario CLDR.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Lista de resultados con posiciones y descripciones.
		:rtype: list
		"""
		resultados = []
		if not self._traducciones_emojis:
			return resultados

		try:
			for coincidencia in self._patron_emojis.finditer(texto):
				valor = coincidencia.group(0)
				inicio = coincidencia.start()
				fin = coincidencia.end()
				descripcion = self._obtener_descripcion_emoji(valor)
				self._agregar_item(resultados, "emoji", valor, inicio, fin, descripcion, valor)
		except Exception as e:
			log.debug("EmoticonosAvanzados: Error detectando emojis: %s" % str(e))

		return resultados

	def detectar_emoticonos(self, texto):
		"""
		Detecta emoticonos clásicos ASCII en un texto.

		Aplica verificación de límites de palabra para evitar
		falsos positivos (por ejemplo, no detectar ':P' dentro de 'Explorador').

		:param texto: Texto a analizar.
		:type texto: str
		:return: Lista de resultados con posiciones y descripciones.
		:rtype: list
		"""
		resultados = []

		# Buscar emoticonos manuales
		if self.usar_manual:
			for coincidencia in self._patron_manual.finditer(texto):
				inicio = coincidencia.start()
				fin = coincidencia.end()
				# Verificar que no esté dentro de una palabra
				if not self._validar_limites(texto, inicio, fin):
					continue
				valor = coincidencia.group(0)
				descripcion = self._obtener_descripcion_emoticono(valor)
				clave = self._normalizar_clave(valor)
				self._agregar_item(resultados, "emoticono", valor, inicio, fin, descripcion, clave)

		resultados.sort(key=lambda item: item["inicio"])
		return resultados

	def detectar_todo(self, texto):
		"""
		Detecta todos los emojis y emoticonos en un texto.

		:param texto: Texto a analizar.
		:type texto: str
		:return: Lista combinada y ordenada por posición.
		:rtype: list
		"""
		resultados = []
		resultados.extend(self.detectar_emojis(texto))
		resultados.extend(self.detectar_emoticonos(texto))
		resultados.sort(key=lambda item: item["inicio"])
		return resultados

	def agrupar_resultados(self, resultados):
		"""
		Agrupa resultados repetidos y cuenta cuántas veces aparecen.

		:param resultados: Lista de resultados detectados.
		:type resultados: list
		:return: Lista agrupada con cantidades.
		:rtype: list
		"""
		agrupados = {}
		orden = []

		for item in resultados:
			clave = (item["tipo"], item["clave_agrupacion"])
			if clave not in agrupados:
				agrupados[clave] = {
					"tipo": item["tipo"],
					"valor": item["valor"],
					"descripcion": item["descripcion"],
					"cantidad": 0,
					"posiciones": [],
				}
				orden.append(clave)
			agrupados[clave]["cantidad"] += 1
			agrupados[clave]["posiciones"].append((item["inicio"], item["fin"]))

		return [agrupados[clave] for clave in orden]

	def generar_texto_agrupado(self, texto, formato="[{}]", separador=", "):
		"""
		Genera un texto accesible con emoticonos agrupados.

		Ejemplo: "Hola 😀😀😀" → "Hola 3x [cara sonriendo]"

		:param texto: Texto original.
		:type texto: str
		:param formato: Formato de reemplazo.
		:type formato: str
		:param separador: Separador entre grupos.
		:type separador: str
		:return: Texto con emoticonos agrupados.
		:rtype: str
		"""
		resultados = self.detectar_todo(texto)
		if not resultados:
			return texto

		# Identificar secuencias consecutivas de emoticonos iguales
		partes = []
		ultimo = 0
		i = 0
		while i < len(resultados):
			item = resultados[i]
			partes.append(texto[ultimo:item["inicio"]])

			# Contar cuántos iguales hay seguidos
			clave = item["clave_agrupacion"]
			cantidad = 1
			j = i + 1
			while j < len(resultados) and resultados[j]["clave_agrupacion"] == clave:
				cantidad += 1
				j += 1

			if cantidad > 1:
				partes.append(" %dx %s " % (cantidad, formato.format(item["descripcion"])))
			else:
				partes.append(" " + formato.format(item["descripcion"]) + " ")

			ultimo = resultados[j - 1]["fin"]
			i = j

		partes.append(texto[ultimo:])
		return "".join(partes)

	def obtener_todos_emojis(self):
		"""
		Obtiene un diccionario de todos los emojis conocidos con sus descripciones.

		Usado internamente para construir el diccionario de habla.

		:return: Diccionario emoji→descripción.
		:rtype: dict
		"""
		return dict(self._traducciones_emojis)

	def obtener_descripcion(self, valor):
		"""
		Obtiene la descripción de un emoji o emoticono.

		Busca primero en emojis Unicode y luego en emoticonos manuales.

		:param valor: Emoji Unicode o emoticono clásico.
		:type valor: str
		:return: Descripción en español, o None si no se encuentra.
		:rtype: str | None
		"""
		# Buscar en emojis
		if valor in self._traducciones_emojis:
			return self._traducciones_emojis[valor]
		# Buscar en emoticonos manuales
		if valor in self._emoticonos_manual:
			return self._emoticonos_manual[valor]
		if self.ignorar_mayusculas:
			for clave in self._emoticonos_manual:
				if clave.lower() == valor.lower():
					return self._emoticonos_manual[clave]
		return None
