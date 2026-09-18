"""
Utilidades de formularios.

Los formularios web envían TODO como texto. Aquí convertimos ese texto al tipo
correcto (número, fecha, booleano…) según la especificación de cada campo
(ver `field_specs.py`) y validamos lo obligatorio.

Función principal: `aplicar_formulario(obj, campos, form)`
  - Lee cada campo desde `form` (request.form).
  - Lo convierte al tipo adecuado.
  - Lo asigna al objeto `obj`.
  - Devuelve una lista de errores (vacía si todo salió bien).
"""
from datetime import datetime


def _a_valor(campo, crudo):
    """
    Convierte el texto `crudo` al tipo indicado por `campo["tipo"]`.
    Lanza ValueError con un mensaje claro si el formato es inválido.
    Devuelve None cuando el campo viene vacío (excepto en booleanos).
    """
    tipo = campo["tipo"]

    # Booleano: en un formulario, la casilla solo llega si está marcada.
    if tipo == "bool":
        return bool(crudo)

    # Para el resto, limpiamos espacios y tratamos "" como vacío (None).
    crudo = (crudo or "").strip()
    if crudo == "":
        return None

    if tipo in ("text", "textarea"):
        return crudo

    if tipo == "select":
        opciones = campo.get("opciones") or []
        if crudo not in opciones:
            raise ValueError(f"«{campo['label']}»: opción no válida.")
        return crudo

    if tipo == "int":
        try:
            return int(crudo)
        except ValueError:
            raise ValueError(f"«{campo['label']}»: debe ser un número entero.")

    if tipo in ("money", "float"):
        try:
            # Aceptamos comas como separador decimal por comodidad.
            return float(crudo.replace(",", "."))
        except ValueError:
            raise ValueError(f"«{campo['label']}»: debe ser un número.")

    if tipo == "date":
        try:
            return datetime.strptime(crudo, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"«{campo['label']}»: fecha inválida.")

    if tipo == "datetime":
        # El input HTML datetime-local manda "AAAA-MM-DDTHH:MM".
        try:
            return datetime.strptime(crudo, "%Y-%m-%dT%H:%M")
        except ValueError:
            raise ValueError(f"«{campo['label']}»: fecha y hora inválidas.")

    # Tipo desconocido: lo guardamos tal cual.
    return crudo


def aplicar_formulario(obj, campos, form):
    """
    Vuelca los datos del formulario sobre `obj`. Devuelve lista de errores.
    """
    errores = []
    for campo in campos:
        nombre = campo["name"]
        crudo = form.get(nombre)
        try:
            valor = _a_valor(campo, crudo)
        except ValueError as e:
            errores.append(str(e))
            continue

        # Validación de obligatorios.
        if campo.get("requerido") and campo["tipo"] != "bool" and valor is None:
            errores.append(f"«{campo['label']}» es obligatorio.")
            continue

        setattr(obj, nombre, valor)
    return errores


def valores_para_formulario(obj, campos):
    """
    Prepara un diccionario {campo: valor} listo para pre-llenar un formulario de
    edición, dando formato a fechas para que los inputs HTML las acepten.
    """
    valores = {}
    for campo in campos:
        nombre = campo["name"]
        valor = getattr(obj, nombre, None)
        if valor is None:
            valores[nombre] = ""
        elif campo["tipo"] == "date":
            valores[nombre] = valor.strftime("%Y-%m-%d")
        elif campo["tipo"] == "datetime":
            valores[nombre] = valor.strftime("%Y-%m-%dT%H:%M")
        else:
            valores[nombre] = valor
    return valores


def valores_por_defecto(campos):
    """Diccionario de valores iniciales para un formulario de creación."""
    valores = {}
    for campo in campos:
        pre = campo.get("predeterminado")
        valores[campo["name"]] = pre if pre is not None else ""
    return valores
