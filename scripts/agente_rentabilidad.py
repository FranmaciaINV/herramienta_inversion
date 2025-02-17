IPC = 0.025  # IPC anual del 2.5%

def calcular_rentabilidad_inmueble(valor_inmueble, renta_mensual, gastos_mensuales):
    """
    Calcula la rentabilidad del inmueble proyectada a 5 años.
    """
    anios = [1, 2, 3, 4, 5]
    valor_inmueble_anual = []
    gastos_anual = []
    rentabilidad_anual = []

    for anio in anios:
        # Incremento del valor del inmueble
        valor_inmueble *= (1 + IPC)
        valor_inmueble_anual.append(round(valor_inmueble, 2))

        # Incremento de gastos y renta
        renta_anual = renta_mensual * 12 * (1 + IPC) ** anio
        gastos_anual_total = gastos_mensuales * 12 * (1 + IPC) ** anio
        rentabilidad = renta_anual - gastos_anual_total
        rentabilidad_anual.append(round(rentabilidad, 2))
        gastos_anual.append(round(gastos_anual_total, 2))

    return {
        "anios": ["Año 1", "Año 2", "Año 3", "Año 4", "Año 5"],
        "valorInmueble": valor_inmueble_anual,
        "gastos": gastos_anual,
        "rentabilidad": rentabilidad_anual
    }
