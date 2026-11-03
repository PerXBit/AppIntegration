"""
constants.py – Todos los parámetros del caso Resguarda (Anexos 1-11).
Fuente única de verdad para datos por defecto.
"""
from __future__ import annotations

# ──────────────────────────────────────────────
# ANEXO 1 – Producto, precios y costes variables
# ──────────────────────────────────────────────
PRECIO_STD = 129.00   # US$/u
PRECIO_PRO = 169.00
MATERIAL_STD = 58.00  # US$/u
MATERIAL_PRO = 74.00
MARGEN_CONTRIB_STD = 71.00  # antes de MO
MARGEN_CONTRIB_PRO = 95.00
PCT_PRO_SEM1_26 = 0.30
PCT_PRO_SEM27_52 = 0.35
DEVOLUCION_PCT = 0.008
DEVOLUCION_COSTO = 85.00

# ──────────────────────────────────────────────
# ANEXO 2 – Plantilla y costes laborales
# ──────────────────────────────────────────────
SALARIO_OPERADOR = 6.50      # US$/h
SALARIO_TECNICO  = 7.50
SALARIO_MANIPULADOR = 7.50
SALARIO_RETRABAJO = 7.50
SALARIO_LIDER_TURNO = 9.00
SALARIO_CELULA = 7.20
SUPERVISOR_SEMANAL = 1050.00
CARGAS_SOCIALES = 0.30
COSTO_CONTRATACION = 350.00  # US$/persona nueva

# ──────────────────────────────────────────────
# ANEXO 3 – Estaciones línea de 6
# ──────────────────────────────────────────────
ESTACIONES_6 = {
    "E1": {"op": "Gabinete: montaje y soldadura", "t_std": 6.50, "t_pro": 6.50, "cv": 0.10},
    "E2": {"op": "Subconjunto de puerta",         "t_std": 6.20, "t_pro": 6.20, "cv": 0.18},
    "E3": {"op": "Instalación puerta y arnés",    "t_std": 8.00, "t_pro": 8.00, "cv": 0.15},
    "E4": {"op": "Cableado y montaje eléctrico",  "t_std": 7.00, "t_pro": 8.60, "cv": 0.12},
    "E5": {"op": "Inspección y prueba eléctrica", "t_std": 6.50, "t_pro": 7.50, "cv": 0.05},
    "E6": {"op": "Empaque y paletizado",          "t_std": 5.67, "t_pro": 5.67, "cv": 0.08},
}

# ──────────────────────────────────────────────
# ANEXO 4 – Estaciones línea de 8
# ──────────────────────────────────────────────
ESTACIONES_8 = {
    "L1": {"op": "Ensamblaje de gabinete",           "t_std": 5.00, "t_pro": 5.00},
    "L2": {"op": "Soldadura de gabinete",            "t_std": 5.20, "t_pro": 5.20},
    "L3": {"op": "Ensamblaje de puerta",             "t_std": 5.80, "t_pro": 5.80},
    "L4": {"op": "Cableado",                         "t_std": 4.10, "t_pro": 4.10},
    "L5": {"op": "Instalación de puerta",            "t_std": 4.30, "t_pro": 4.30},
    "L6": {"op": "Montaje eléctrico e inspección",   "t_std": 4.80, "t_pro": 6.40},
    "L7": {"op": "Pruebas",                          "t_std": 5.00, "t_pro": 6.00},
    "L8": {"op": "Embalaje",                         "t_std": 5.67, "t_pro": 5.67},
}

# ──────────────────────────────────────────────
# ANEXO 5 – Jornada, turnos y calendario
# ──────────────────────────────────────────────
HORAS_PROG_1_2 = 8.5
HORAS_PRODUCTIVAS_1_2 = 7.5
HORAS_PAGADAS_1_2 = 8.0
HORAS_PRODUCTIVAS_3T = 7.0
HORAS_PAGADAS_3T = 7.5
RENDIMIENTO_T2 = 0.92
RENDIMIENTO_T3 = 0.88
PRIMA_T2 = 0.08
PRIMA_T3 = 0.15
COSTO_FIJO_TURNO_EXTRA = 600.0   # US$/semana por turno adicional
DIAS_SEMANA = 5

# Sábados
HORAS_PROD_SABADO = 6.5
HORAS_PAG_SABADO = 7.0
RECARGO_SABADO = 0.50
MAX_SABADOS_MES = 3

# Costes fijos planta
FIJOS_PLANTA_SEMANAL = 3200.0

# ──────────────────────────────────────────────
# ANEXO 6 – Opciones de capacidad
# ──────────────────────────────────────────────
INVERSION_REEQUILIBRIO = 9000.0     # por línea
PLAZO_REEQUILIBRIO = 3              # semanas
INVERSION_TERCERA_LINEA = 48000.0
PLAZO_TERCERA_LINEA = 8
ESPACIO_LINEA = 120                 # m²
INVERSION_CELULA = 15000.0
PLAZO_CELULA = 5
ESPACIO_CELULA = 40                 # m²
TRABAJADORES_CELULA = 3
PENALIZACION_POLIVALENCIA = 0.08    # central
CAMBIO_VARIANTE_CELULA = 5          # min
INVERSION_DISPOSITIVO_PUERTA = 22000.0
PLAZO_DISPOSITIVO = 10
SOBRECOSTO_SUBCONTRATACION = 4.80   # US$/u
LIMITE_SUBCONTRATACION = 1200       # u/semana

# Tiempos con dispositivo para puerta (O5)
# Línea 6: E2 → 5.6, E3 → 6.0
# Línea 8: L3 → 5.2, L5 → 3.3
TIEMPOS_O5_LINEA6 = {"E2": 5.6, "E3": 6.0}
TIEMPOS_O5_LINEA8 = {"L3": 5.2, "L5": 3.3}

# Subcontratación (O6): desaparece E2; E3 baja a 7.2
TIEMPOS_O6 = {"E3": 7.2}  # E2 se elimina

# Lotes
LOTE_DEFAULT = 100
CAMBIO_VARIANTE_DEFAULT = 20  # min

# Valor residual
VALOR_RESIDUAL_PCT = 0.80

# ──────────────────────────────────────────────
# ANEXO 7 – Calidad y retrabajo
# ──────────────────────────────────────────────
FALLA_STD = 0.04
FALLA_PRO = 0.06
RECUPERACION = 0.80
TIEMPO_RETRABAJO = 15  # min/unidad
EFECTO_CELULA_FALLA = -0.01  # reducción de 1 punto porcentual

# ──────────────────────────────────────────────
# ANEXO 8 – Inventario, nivel de servicio y faltantes
# ──────────────────────────────────────────────
INVENTARIO_INICIAL = 300
INVENTARIO_INICIAL_PCT_STD = 0.70
COSTO_MANTENER_INV = 0.24       # anual sobre costo materiales
DEMANDA_ESPERA_PCT = 0.50       # 50% espera hasta 2 sem
MAX_SEMANAS_ESPERA = 2
PENALIZACION_BACKORDER = 3.0    # US$/u/semana
COSTO_VENTA_PERDIDA_EXTRA = 10.0  # US$ pérdida de imagen
INVENTARIO_MAX_PT = 1500

# ──────────────────────────────────────────────
# ANEXO 9 – Parámetros financieros
# ──────────────────────────────────────────────
HORIZONTE = 52
TASA_DESCUENTO_ANUAL = 0.12
TASA_SEMANAL = (1 + TASA_DESCUENTO_ANUAL) ** (1 / 52) - 1
LIMITE_INVERSION = 120000.0
PROB_BASE = 0.50
PROB_OPTIMISTA = 0.25
PROB_CANAL = 0.25

# ──────────────────────────────────────────────
# ANEXO 10 – Espacio y RRHH
# ──────────────────────────────────────────────
SUPERFICIE_ACTUAL = 420
SUPERFICIE_LINEAS = 240
SUPERFICIE_LIBRE = 180
AMPLIACION_M2 = 200
AMPLIACION_SEMANA = 11
AMPLIACION_COSTO_M2_SEM = 6.0
AMPLIACION_CONTRATO_MIN = 26  # semanas
MAX_CONTRATACION_SEM = 12
CURVA_APRENDIZAJE = {1: 0.70, 2: 0.80, 3: 0.90, 4: 0.95}  # sem 5+: 1.0
ROTACION_MENSUAL = 0.02  # opcional

# ──────────────────────────────────────────────
# ANEXO 11 – Pronóstico de demanda semanal
# ──────────────────────────────────────────────
DEMANDA_SEMANAL: list[dict] = [
    # fmt: off
    {"sem": 1,  "fecha": "05/10", "base": 700,  "optim": 700,  "canal": 700},
    {"sem": 2,  "fecha": "12/10", "base": 800,  "optim": 800,  "canal": 800},
    {"sem": 3,  "fecha": "19/10", "base": 950,  "optim": 950,  "canal": 950},
    {"sem": 4,  "fecha": "26/10", "base": 1050, "optim": 1050, "canal": 1050},
    {"sem": 5,  "fecha": "02/11", "base": 1150, "optim": 1380, "canal": 1150},
    {"sem": 6,  "fecha": "09/11", "base": 1300, "optim": 1560, "canal": 1300},
    {"sem": 7,  "fecha": "16/11", "base": 1550, "optim": 1860, "canal": 1550},
    {"sem": 8,  "fecha": "23/11", "base": 1900, "optim": 2280, "canal": 1900},
    {"sem": 9,  "fecha": "30/11", "base": 1750, "optim": 2100, "canal": 1750},
    {"sem": 10, "fecha": "07/12", "base": 1700, "optim": 2040, "canal": 1700},
    {"sem": 11, "fecha": "14/12", "base": 1650, "optim": 1980, "canal": 1300},
    {"sem": 12, "fecha": "21/12", "base": 1300, "optim": 1560, "canal": 1000},
    {"sem": 13, "fecha": "28/12", "base": 900,  "optim": 1080, "canal": 650},
    {"sem": 14, "fecha": "04/01", "base": 960,  "optim": 1150, "canal": 650},
    {"sem": 15, "fecha": "11/01", "base": 970,  "optim": 1160, "canal": 650},
    {"sem": 16, "fecha": "18/01", "base": 970,  "optim": 1160, "canal": 660},
    {"sem": 17, "fecha": "25/01", "base": 980,  "optim": 1180, "canal": 660},
    {"sem": 18, "fecha": "01/02", "base": 990,  "optim": 1190, "canal": 660},
    {"sem": 19, "fecha": "08/02", "base": 1000, "optim": 1200, "canal": 660},
    {"sem": 20, "fecha": "15/02", "base": 1000, "optim": 1200, "canal": 660},
    {"sem": 21, "fecha": "22/02", "base": 1010, "optim": 1210, "canal": 670},
    {"sem": 22, "fecha": "01/03", "base": 1020, "optim": 1220, "canal": 670},
    {"sem": 23, "fecha": "08/03", "base": 1030, "optim": 1240, "canal": 670},
    {"sem": 24, "fecha": "15/03", "base": 1040, "optim": 1250, "canal": 670},
    {"sem": 25, "fecha": "22/03", "base": 1050, "optim": 1260, "canal": 670},
    {"sem": 26, "fecha": "29/03", "base": 1050, "optim": 1260, "canal": 680},
    {"sem": 27, "fecha": "05/04", "base": 1060, "optim": 1270, "canal": 680},
    {"sem": 28, "fecha": "12/04", "base": 1070, "optim": 1280, "canal": 680},
    {"sem": 29, "fecha": "19/04", "base": 1080, "optim": 1300, "canal": 680},
    {"sem": 30, "fecha": "26/04", "base": 1090, "optim": 1310, "canal": 680},
    {"sem": 31, "fecha": "03/05", "base": 1100, "optim": 1320, "canal": 690},
    {"sem": 32, "fecha": "10/05", "base": 1110, "optim": 1330, "canal": 690},
    {"sem": 33, "fecha": "17/05", "base": 1280, "optim": 1540, "canal": 760},
    {"sem": 34, "fecha": "24/05", "base": 1290, "optim": 1550, "canal": 760},
    {"sem": 35, "fecha": "31/05", "base": 1130, "optim": 1360, "canal": 690},
    {"sem": 36, "fecha": "07/06", "base": 1140, "optim": 1370, "canal": 700},
    {"sem": 37, "fecha": "14/06", "base": 1150, "optim": 1380, "canal": 700},
    {"sem": 38, "fecha": "21/06", "base": 1160, "optim": 1390, "canal": 700},
    {"sem": 39, "fecha": "28/06", "base": 1170, "optim": 1400, "canal": 700},
    {"sem": 40, "fecha": "05/07", "base": 1180, "optim": 1420, "canal": 700},
    {"sem": 41, "fecha": "12/07", "base": 1190, "optim": 1430, "canal": 710},
    {"sem": 42, "fecha": "19/07", "base": 1200, "optim": 1440, "canal": 710},
    {"sem": 43, "fecha": "26/07", "base": 1210, "optim": 1450, "canal": 710},
    {"sem": 44, "fecha": "02/08", "base": 1220, "optim": 1460, "canal": 710},
    {"sem": 45, "fecha": "09/08", "base": 1230, "optim": 1480, "canal": 720},
    {"sem": 46, "fecha": "16/08", "base": 1240, "optim": 1490, "canal": 720},
    {"sem": 47, "fecha": "23/08", "base": 1250, "optim": 1500, "canal": 720},
    {"sem": 48, "fecha": "30/08", "base": 1260, "optim": 1510, "canal": 720},
    {"sem": 49, "fecha": "06/09", "base": 1270, "optim": 1520, "canal": 720},
    {"sem": 50, "fecha": "13/09", "base": 1280, "optim": 1540, "canal": 730},
    {"sem": 51, "fecha": "20/09", "base": 1290, "optim": 1550, "canal": 730},
    {"sem": 52, "fecha": "27/09", "base": 1300, "optim": 1560, "canal": 730},
    # fmt: on
]
