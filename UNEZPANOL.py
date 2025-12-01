# --- INTÉRPRETE SIMPLE: UNEZPAÑOL ---
import re  # Importa el módulo de Expresiones Regulares para el análisis de patrones.

# Diccionario global que actúa como la "Tabla de Símbolos" del intérprete.
# Almacena los nombres de las variables declaradas y sus valores.
variables = {}


def evaluar(expr):
    """
    Evalúa expresiones con variables, números, strings y operadores +, -, >=, <=, ==, <, >.
    Esta función usa el motor de evaluación de Python (eval) para ejecutar la lógica.
    """
    # --- FASE DE SUSTITUCIÓN DE VARIABLES ---
    # Reemplaza los nombres de las variables en la expresión (ej. 'x + 5') por
    # sus valores reales (ej. '18 + 5') antes de la evaluación.
    for nombre, valor in variables.items():
        # \b{nombre}\b asegura que solo se reemplace la variable completa y no parte de otra palabra.
        # repr(valor) asegura que los valores (especialmente las cadenas) se envuelvan en comillas
        # para que eval() las procese correctamente.
        expr = re.sub(rf'\b{nombre}\b', repr(valor), expr)
    try:
        # Ejecuta la expresión transformada usando la función nativa eval() de Python.
        return eval(expr)
    except Exception as e:
        # Manejo de errores durante la evaluación de la expresión.
        raise ValueError(f"Error al evaluar '{expr}': {e}")


def interpretar(codigo):
    """
    Función principal que interpreta el programa fuente línea por línea.
    'codigo' es una lista de strings, donde cada string es una línea del programa.
    """
    i = 0  # Puntero de instrucción, índice de la línea actual.
    while i < len(codigo):
        linea = codigo[i].strip()

        # Ignorar líneas vacías y líneas que comienzan con '#' (comentarios).
        if linea == "" or linea.startswith("#"):
            i += 1
            continue

        # ----------------------------------------
        # --- Análisis de Declaraciones (Asignación) ---
        # Patrón: (entero|cadena) [nombre_variable] = [valor];
        # m.groups() obtiene: (tipo, nombre, valor)
        m = re.match(r'(entero|cadena)\s+(\w+)\s*=\s*(.+);', linea)
        if m:
            tipo, nombre, valor = m.groups()

            # Limpia el valor y quita comillas externas si existen.
            valor = valor.strip().strip('"')

            # Ejecución semántica de la asignación:
            if tipo == "entero":
                # Convierte a entero antes de almacenar en la tabla de símbolos.
                variables[nombre] = int(valor)
            elif tipo == "cadena":
                variables[nombre] = valor

            i += 1
            continue

        # ----------------------------------------
        # --- Análisis de Imprimir ---
        # Patrón: Imprimir([expresión]);
        m = re.match(r'Imprimir\((.+)\);', linea)
        if m:
            expr = m.group(1)  # Captura la expresión dentro de Imprimir().
            resultado = evaluar(expr)  # Evalúa la expresión (puede incluir variables).
            print(resultado)
            i += 1
            continue

        # ----------------------------------------
        # --- Análisis de Instrucción Pausar ---
        # Patrón: Pausar(); - Detiene la ejecución hasta la intervención del usuario (ENTER).
        m = re.match(r'Pausar\(\);', linea)
        if m:
            print("\nCódigo pausado\n")
            # Usa input() para detener el flujo y esperar la señal de reanudación.
            input(">>> Presiona ENTER para continuar <<<")
            print("\nContinuando\n")
            i += 1
            continue

        # ----------------------------------------
        # --- Análisis de Estructura Condicional (Si...Entonces...FinSi) ---
        if linea.startswith("Si") and "Entonces" in linea:
            # 1. Extracción de la condición
            # Busca lo que está entre 'Si ' y ' Entonces'.
            condicion = re.findall(r'Si\s+(.+)\s+Entonces', linea)[0]

            bloque = []
            i += 1
            nivel = 1  # Inicia el nivel de anidamiento para el bloque Si actual.

            # 2. Captura del Bloque de Código
            while i < len(codigo) and nivel > 0:
                l = codigo[i].strip()

                # Si encuentra otro 'Si', incrementa el nivel de anidamiento.
                if l.startswith("Si") and "Entonces" in l:
                    nivel += 1
                # Si encuentra 'FinSi', decrementa el nivel.
                elif l == "FinSi":
                    nivel -= 1
                    # Si el nivel llega a 0, se encontró el FinSi que cierra el bloque.
                    if nivel == 0:
                        i += 1
                        break

                # Agrega la línea al bloque (solo si no es el FinSi de cierre).
                if nivel > 0:
                    bloque.append(codigo[i])

                i += 1

            # 3. Ejecución Condicional
            # Si la condición evaluada es True, ejecuta el bloque capturado.
            if evaluar(condicion):
                interpretar(bloque)  # Llamada recursiva para interpretar el sub-bloque.

            continue  # Continúa la interpretación después del bloque Si.


        # --- Análisis de Estructura Repetitiva (Mientras...Hacer...FinMientras) ---
        if linea.startswith("Mientras") and "Hacer" in linea:
            # 1. Extraer la condición entre 'Mientras' y 'Hacer'
            condicion = re.findall(r'Mientras\s+(.+)\s+Hacer', linea)[0]

            # 2. Capturar el bloque interno del ciclo
            bloque = []
            i += 1
            nivel = 1  # Nivel de anidamiento (por si hay ciclos dentro de otros)

            while i < len(codigo) and nivel > 0:
                l = codigo[i].strip()

                # Si se encuentra otro "Mientras", aumenta el nivel
                if l.startswith("Mientras") and "Hacer" in l:
                    nivel += 1
                # Si se encuentra "FinMientras", disminuye el nivel
                elif l == "FinMientras":
                    nivel -= 1
                    if nivel == 0:
                        i += 1
                        break

                if nivel > 0:
                    bloque.append(codigo[i])
                i += 1

            # 3. Ejecutar mientras la condición sea verdadera
            while evaluar(condicion):
                interpretar(bloque)  # Ejecuta el bloque
            continue
                # ----------------------------------------
        # Si la línea no coincide con ninguna instrucción conocida, lanza un error sintáctico.
        raise SyntaxError(f"Línea no reconocida: {linea}")

# ----------------------------------------
# --- Código a interpretar (Programa Fuente) ---
codigo = [
    'entero x = 18;',
    'entero y = 25;',
    'entero z = 5;',
    'cadena nombre = "Juan";',
    'cadena apellido = "Pérez";',
    'cadena otronombre = "pepe";',
    'cadena hola = "Hola";',
    '',
    'Si x >= 18 Entonces',
    '    Imprimir("Nivel 1: Mayor de edad");',
    '    Si y > x Entonces',
    '        Imprimir("Nivel 2: y > x");',
    '        Si z < 10 Entonces',
    '            Imprimir("Nivel 3: z < 10");',
    '            Si nombre == "Juan" Entonces',
    '                Imprimir("Nivel 4: nombre es Juan");',
    '            FinSi',
    '        FinSi',
    '    FinSi',
    'FinSi',
    '',
    'Si otronombre == "pepe" Entonces',
    '    Imprimir("Nivel 1: otronombre es pepe");',
    '    Si x + y > 40 and z < 10 Entonces',
    '        Imprimir("Nivel 2: x+y>40 y z<10");',
    '        Si apellido == "Pérez" Entonces',
    '            Imprimir("Nivel 3: apellido es Pérez");',
    '        FinSi',
    '    FinSi',
    'FinSi',
    '',
    'Si x < 10 or y > 20 Entonces',
    '    Imprimir("Nivel 1: alguna condición combinada se cumple");',
    'FinSi',
    '',
   'Mientras x < 5 Hacer',
    '    Imprimir("x vale: " + str(x));',
    '    x = x + 1;',
    'FinMientras',
    '',
    'Imprimir("Fin del ciclo, x=" + str(x));',
    'Pausar();',
    'Imprimir("Fin del programa. Variables: " + nombre + ", " + otronombre + ", " + apellido + ", x=" + str(x) + ", y=" + str(y) + ", z=" + str(z));',
]

# Inicia la interpretación del programa
interpretar(codigo)
