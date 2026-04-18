# -*- coding: utf-8 -*-
# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulte el archivo COPYING.txt para más detalles.

"""
Script para importar descripciones desde los diccionarios CLDR y symbols de NVDA.

Lee los archivos cldr.dic y symbols.dic de la carpeta
adjuntos/nvda_emoticonos_diccionarios/ y genera automáticamente el contenido
del diccionario TRADUCCIONES_EMOJIS en traducciones.py.

Solo importa entradas que sean emojis/símbolos especiales (no caracteres ASCII
comunes como letras, números, puntuación básica, ni patrones Braille).

Uso:
    python importar_diccionarios.py
"""

import os
import re
import unicodedata


# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_DIR = os.path.join(BASE_DIR, "adjuntos", "nvda_emoticonos_diccionarios")
CLDR_PATH = os.path.join(DICT_DIR, "cldr.dic")
SYMBOLS_PATH = os.path.join(DICT_DIR, "symbols.dic")
TRADUCCIONES_PATH = os.path.join(
	BASE_DIR, "addon", "globalPlugins", "emoticonosAvanzados", "traducciones.py"
)


def es_emoji_o_simbolo_especial(char):
	"""
	Determina si un carácter es un emoji o símbolo especial que debemos incluir.

	Excluye caracteres ASCII básicos, puntuación estándar, letras con acentos,
	caracteres de control, espacios, y patrones Braille.

	:param char: Carácter a evaluar.
	:type char: str
	:return: True si es un emoji o símbolo especial.
	:rtype: bool
	"""
	if not char:
		return False

	# Si es un solo carácter
	if len(char) == 1:
		cp = ord(char)

		# Excluir ASCII básico (0-127)
		if cp <= 0x7F:
			return False

		# Excluir acentuados latinos extendidos comunes (Latin-1 Supplement, Latin Extended)
		if 0x80 <= cp <= 0x024F:
			return False

		# Excluir caracteres de control y formato
		cat = unicodedata.category(char)
		if cat.startswith('C'):  # Control, formato, etc.
			return False

		# Excluir letras modificadoras y combinantes
		if cat.startswith('M'):  # Marcas combinantes
			return False

		# Excluir patrones Braille (U+2800 - U+28FF)
		if 0x2800 <= cp <= 0x28FF:
			return False
		# Excluir patrones Braille extendidos (U+2900+)
		if 0x2900 <= cp <= 0x2BFF:
			# Solo excluir si son Braille extendidos, mantener otros
			pass

		# Excluir espacios especiales
		if cat == 'Zs':
			return False

		return True

	# Si son múltiples caracteres (emoji compuesto), siempre incluir
	return True


def es_emoji_unicode(char):
	"""
	Determina si un carácter es un emoji propiamente dicho (caras, gestos, objetos, etc).
	
	Esto identifica los caracteres que están en rangos de emoji conocidos,
	excluyendo símbolos matemáticos, geométricos, flechas, etc. que ya son
	manejados por NVDA de forma nativa.

	:param char: Carácter a evaluar.
	:type char: str
	:return: True si es un emoji Unicode.
	:rtype: bool
	"""
	if not char:
		return False

	# Los emojis compuestos (con ZWJ, variantes, modificadores) siempre son emojis
	if len(char) > 1:
		return True

	cp = ord(char)

	# Rangos principales de emoji
	emoji_ranges = [
		(0x1F600, 0x1F64F),  # Emoticons (caras)
		(0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
		(0x1F680, 0x1F6FF),  # Transport and Map
		(0x1F700, 0x1F77F),  # Alchemical Symbols
		(0x1F780, 0x1F7FF),  # Geometric Shapes Extended
		(0x1F800, 0x1F8FF),  # Supplemental Arrows-C
		(0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
		(0x1FA00, 0x1FA6F),  # Chess Symbols
		(0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
		(0x2702, 0x27B0),    # Dingbats
		(0x2600, 0x26FF),    # Misc symbols (sol, nubes, etc.)
		(0xFE00, 0xFE0F),    # Variation Selectors
		(0x200D, 0x200D),    # Zero Width Joiner
		(0x20E3, 0x20E3),    # Combining Enclosing Keycap
		(0xE0020, 0xE007F),  # Tags
		(0x1F1E0, 0x1F1FF),  # Regional Indicator Symbols (banderas)
	]

	# Caracteres sueltos que son emoji
	emoji_singles = {
		0x00A9,  # © copyright
		0x00AE,  # ® registered
		0x203C,  # ‼ double exclamation
		0x2049,  # ⁉ exclamation question
		0x2122,  # ™ trade mark
		0x2139,  # ℹ information
		0x2194, 0x2195, 0x2196, 0x2197, 0x2198, 0x2199,  # flechas
		0x21A9, 0x21AA,  # flechas curvas
		0x231A, 0x231B,  # reloj, reloj de arena
		0x2328,  # teclado
		0x23CF,  # eject
		0x23E9, 0x23EA, 0x23EB, 0x23EC, 0x23ED, 0x23EE, 0x23EF,
		0x23F0, 0x23F1, 0x23F2, 0x23F3,
		0x23F8, 0x23F9, 0x23FA,
		0x24C2,  # Ⓜ
		0x25AA, 0x25AB, 0x25B6, 0x25C0, 0x25FB, 0x25FC, 0x25FD, 0x25FE,
		0x2614, 0x2615,  # paraguas, café
		0x2648, 0x2649, 0x264A, 0x264B, 0x264C, 0x264D,
		0x264E, 0x264F, 0x2650, 0x2651, 0x2652, 0x2653,  # zodíaco
		0x267F,  # silla de ruedas
		0x2693,  # ancla
		0x26A1,  # rayo
		0x26AA, 0x26AB,
		0x26BD, 0x26BE,
		0x26C4, 0x26C5,
		0x26CE,  # ofiuco
		0x26D4,  # prohibido
		0x26EA,  # iglesia
		0x26F2, 0x26F3, 0x26F5,
		0x26F7, 0x26F8, 0x26F9, 0x26FA,
		0x26FD,  # gasolinera
		0x2702,  # tijeras
		0x2705,  # check verde
		0x2708, 0x2709,
		0x270A, 0x270B, 0x270C, 0x270D,
		0x270F,  # lápiz
		0x2712,  # pluma negra
		0x2714,  # check
		0x2716,  # X
		0x271D,  # cruz
		0x2721,  # estrella David
		0x2728,  # chispas
		0x2733, 0x2734,
		0x2744,  # nieve
		0x2747,
		0x274C, 0x274E,
		0x2753, 0x2754, 0x2755, 0x2757,
		0x2763, 0x2764,  # corazón
		0x2795, 0x2796, 0x2797,
		0x27A1,  # flecha derecha
		0x27B0,
		0x2934, 0x2935,
		0x2B05, 0x2B06, 0x2B07,
		0x2B1B, 0x2B1C,
		0x2B50,  # estrella
		0x2B55,  # círculo
		0x3030,  # guión ondulado
		0x303D,  # marca alternación
		0x3297, 0x3299,
	}

	for start, end in emoji_ranges:
		if start <= cp <= end:
			return True

	if cp in emoji_singles:
		return True

	return False


def parsear_cldr(ruta):
	"""
	Parsea un archivo cldr.dic y extrae pares (símbolo, descripción).

	El formato es:
		símbolo\\tdescripción\\t-

	Solo se procesan líneas después de la cabecera "symbols:".

	:param ruta: Ruta al archivo cldr.dic.
	:type ruta: str
	:return: Diccionario de símbolo → descripción.
	:rtype: dict
	"""
	resultado = {}
	en_simbolos = False

	with open(ruta, "r", encoding="utf-8-sig") as f:
		for linea in f:
			linea = linea.rstrip("\r\n")

			# Detectar inicio de sección de símbolos
			if linea.strip() == "symbols:":
				en_simbolos = True
				continue

			if not en_simbolos:
				continue

			# Ignorar líneas vacías y comentarios
			if not linea.strip() or linea.strip().startswith("#"):
				continue

			# Parsear: símbolo\tdescripción\t[-|nivel]
			partes = linea.split("\t")
			if len(partes) >= 2:
				simbolo = partes[0]
				descripcion = partes[1]

				if simbolo and descripcion:
					resultado[simbolo] = descripcion

	return resultado


def parsear_symbols(ruta):
	"""
	Parsea un archivo symbols.dic y extrae pares (símbolo, descripción).

	El formato tiene dos secciones:
	- complexSymbols: (se ignora)
	- symbols: símbolo\\tdescripción\\t[nivel]\\t[preserve]

	:param ruta: Ruta al archivo symbols.dic.
	:type ruta: str
	:return: Diccionario de símbolo → descripción.
	:rtype: dict
	"""
	resultado = {}
	en_simbolos = False

	with open(ruta, "r", encoding="utf-8-sig") as f:
		for linea in f:
			linea = linea.rstrip("\r\n")

			if linea.strip() == "symbols:":
				en_simbolos = True
				continue

			if linea.strip() == "complexSymbols:":
				en_simbolos = False
				continue

			if not en_simbolos:
				continue

			# Ignorar líneas vacías y comentarios
			if not linea.strip() or linea.strip().startswith("#"):
				continue

			# Parsear: símbolo\tdescripción\t[nivel]\t[preserve]
			partes = linea.split("\t")
			if len(partes) >= 2:
				simbolo = partes[0]
				descripcion = partes[1]

				# Ignorar secuencias de escape especiales
				if simbolo.startswith("\\"):
					continue

				# Ignorar entradas sin descripción real
				if not descripcion.strip():
					continue

				# Ignorar entradas con nombres como "sentence ending", "phrase ending", etc.
				if " " in simbolo and not es_emoji_o_simbolo_especial(simbolo):
					continue

				if simbolo and descripcion:
					resultado[simbolo] = descripcion

	return resultado


def filtrar_solo_emojis(diccionario):
	"""
	Filtra un diccionario para incluir solo emojis y símbolos especiales,
	excluyendo caracteres ASCII básicos, puntuación, Braille, etc.

	:param diccionario: Diccionario completo de símbolo → descripción.
	:type diccionario: dict
	:return: Diccionario filtrado.
	:rtype: dict
	"""
	filtrado = {}
	for simbolo, descripcion in diccionario.items():
		if es_emoji_o_simbolo_especial(simbolo):
			filtrado[simbolo] = descripcion
	return filtrado


def generar_traducciones_py(emojis_dict):
	"""
	Genera el contenido del archivo traducciones.py con el diccionario de emojis.

	:param emojis_dict: Diccionario de emoji → descripción.
	:type emojis_dict: dict
	:return: Contenido completo del archivo traducciones.py.
	:rtype: str
	"""
	lineas = []
	lineas.append("# -*- coding: utf-8 -*-")
	lineas.append("# Copyright (C) 2026 Héctor J. Benítez Corredera <xebolax@gmail.com>")
	lineas.append("# Este archivo está cubierto por la Licencia Pública General de GNU.")
	lineas.append("# Consulte el archivo COPYING.txt para más detalles.")
	lineas.append("")
	lineas.append('"""')
	lineas.append("Diccionarios de traducciones para emoticonos y emojis.")
	lineas.append("")
	lineas.append("Contiene:")
	lineas.append("- Diccionario de emojis Unicode con descripciones en español (generado desde CLDR de NVDA).")
	lineas.append("- Diccionario de emoticonos clásicos ASCII.")
	lineas.append("")
	lineas.append("NOTA: El diccionario TRADUCCIONES_EMOJIS es generado automáticamente")
	lineas.append("por el script importar_diccionarios.py a partir de los archivos")
	lineas.append("cldr.dic y symbols.dic de NVDA en español.")
	lineas.append('"""')
	lineas.append("")
	lineas.append("# Diccionario de emojis Unicode con descripciones en español")
	lineas.append("# Generado automáticamente desde los diccionarios CLDR de NVDA")
	lineas.append("TRADUCCIONES_EMOJIS = {")

	# Ordenar por valor Unicode del primer carácter para consistencia
	items_ordenados = sorted(emojis_dict.items(), key=lambda x: [ord(c) for c in x[0]])

	for emoji, descripcion in items_ordenados:
		# Escapar comillas en la descripción
		descripcion_escapada = descripcion.replace("\\", "\\\\").replace('"', '\\"')
		lineas.append('\t"%s": "%s",' % (emoji, descripcion_escapada))

	lineas.append("}")
	lineas.append("")
	lineas.append("# Emoticonos clásicos ASCII con descripciones en español")
	lineas.append("EMOTICONOS_MANUALES = {")
	
	# Emoticonos ASCII manuales (estos se mantienen hardcodeados)
	emoticonos_ascii = [
		(':)', 'cara feliz'),
		(':-)', 'cara feliz'),
		('=)', 'cara feliz'),
		(':]', 'cara feliz'),
		('(:', 'cara feliz'),
		('(-:', 'cara feliz'),
		(':D', 'risa'),
		(':-D', 'risa'),
		('=D', 'risa'),
		('XD', 'risa fuerte'),
		('X-D', 'risa fuerte'),
		('xD', 'risa fuerte'),
		('xd', 'risa fuerte'),
		(':(', 'cara triste'),
		(':-(', 'cara triste'),
		('=(', 'cara triste'),
		(':[', 'cara triste'),
		('):', 'cara triste'),
		(')-:', 'cara triste'),
		(';)', 'guiño'),
		(';-)', 'guiño'),
		(';D', 'guiño con risa'),
		(';-D', 'guiño con risa'),
		(':P', 'sacando la lengua'),
		(':-P', 'sacando la lengua'),
		(':p', 'sacando la lengua'),
		(':-p', 'sacando la lengua'),
		('=P', 'sacando la lengua'),
		('=p', 'sacando la lengua'),
		(';P', 'guiño con lengua'),
		(';-P', 'guiño con lengua'),
		(';p', 'guiño con lengua'),
		(';-p', 'guiño con lengua'),
		(':O', 'sorpresa'),
		(':-O', 'sorpresa'),
		(':o', 'sorpresa'),
		(':-o', 'sorpresa'),
		(':|', 'cara seria'),
		(':-|', 'cara seria'),
		(':/', 'duda o incomodidad'),
		(':-/', 'duda o incomodidad'),
		(':\\', 'duda o incomodidad'),
		(':-\\', 'duda o incomodidad'),
		(':S', 'confusión'),
		(':-S', 'confusión'),
		(':s', 'confusión'),
		(':-s', 'confusión'),
		(':$', 'vergüenza'),
		(':-$', 'vergüenza'),
		(':*', 'beso'),
		(':-*', 'beso'),
		('<3', 'corazón'),
		('</3', 'corazón roto'),
		(":'(", 'llanto'),
		(":'-(" , 'llanto'),
		(":')", 'llorando de alegría'),
		(":'-)", 'llorando de alegría'),
		('^^', 'alegría'),
		('^_^', 'alegría'),
		('-_-', 'aburrimiento'),
		('o_O', 'sorpresa o desconcierto'),
		('O_o', 'sorpresa o desconcierto'),
		('._.', 'expresión apagada'),
		('>:(', 'enfado'),
		('>:-(', 'enfado'),
		(':3', 'cara tierna'),
		(':-3', 'cara tierna'),
	]

	for emoticono, descripcion in emoticonos_ascii:
		# Escapar backslashes y comillas
		emoticono_escapado = emoticono.replace("\\", "\\\\").replace('"', '\\"')
		lineas.append('\t"%s": "%s",' % (emoticono_escapado, descripcion))

	lineas.append("}")
	lineas.append("")

	return "\n".join(lineas)


def main():
	"""
	Función principal: lee los diccionarios CLDR y symbols.dic, combina las
	entradas, filtra solo emojis/símbolos especiales, y reescribe traducciones.py.
	"""
	print("=" * 60)
	print("Importador de diccionarios NVDA -> traducciones.py")
	print("=" * 60)

	# Verificar que los archivos existen
	if not os.path.exists(CLDR_PATH):
		print("ERROR: No se encuentra %s" % CLDR_PATH)
		return

	# Parsear diccionario CLDR (contiene las descripciones de emojis)
	print("\nParseando cldr.dic...")
	cldr = parsear_cldr(CLDR_PATH)
	print("  Entradas totales en cldr.dic: %d" % len(cldr))

	# Nota: symbols.dic NO se usa porque contiene datos nativos de NVDA
	# (puntuacion, matematicas, braille) que NVDA ya maneja por si mismo.
	# Solo usamos cldr.dic que tiene las descripciones de emojis.

	# Filtrar solo emojis y simbolos especiales
	emojis = filtrar_solo_emojis(cldr)
	print("Entradas despues de filtrar (solo emojis/simbolos especiales): %d" % len(emojis))

	# Mostrar algunas estadisticas
	un_char = sum(1 for k in emojis if len(k) == 1)
	multi_char = sum(1 for k in emojis if len(k) > 1)
	print("\n  - Emojis de un caracter: %d" % un_char)
	print("  - Emojis compuestos (multi-caracter): %d" % multi_char)

	# Generar traducciones.py
	print("\nGenerando traducciones.py...")
	contenido = generar_traducciones_py(emojis)

	# Escribir archivo
	with open(TRADUCCIONES_PATH, "w", encoding="utf-8") as f:
		f.write(contenido)

	# Contar entradas en el archivo generado
	num_emojis = len(emojis)
	print("\nArchivo traducciones.py generado correctamente:")
	print("  Ruta: %s" % TRADUCCIONES_PATH)
	print("  Emojis/simbolos: %d entradas" % num_emojis)
	print("  Emoticonos ASCII: 66 entradas (hardcodeadas)")
	print("\n" + "=" * 60)
	print("Importacion completada!")
	print("=" * 60)


if __name__ == "__main__":
	main()
