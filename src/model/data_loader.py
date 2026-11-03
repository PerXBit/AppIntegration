"""
data_loader.py – Módulo de carga y exportación de datos desde/hacia Excel.

Funcionalidades:
1. Generar y exportar la Plantilla Oficial de Excel (con formato, estilos y comentarios).
2. Cargar datos desde Excel (archivo local o BytesIO subido por el usuario en Streamlit).
3. Validar esquema y columnas requeridas de las 6 hojas del modelo.
4. Generar el archivo maestro oficial `data/resguarda_datos_caso.xlsx` si no existe.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any, BinaryIO

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd

from src.model import constants as C


DATA_DIR = Path("data")
DEFAULT_EXCEL_PATH = DATA_DIR / "resguarda_datos_caso.xlsx"
TEMPLATE_EXCEL_PATH = DATA_DIR / "plantilla_template.xlsx"


# ═══════════════════════════════════════════════
# Catálogo Maestro de los 22 Parámetros Editables
# ═══════════════════════════════════════════════
PARAMETROS_CATALOGO: list[dict[str, Any]] = [
    {
        "key": "precio_neto_std",
        "label": "Precio Neto R1 Estándar",
        "categoria": "💰 Precios y Materiales",
        "default": C.PRECIO_STD,
        "min_val": 50.0,
        "max_val": 300.0,
        "step": 1.0,
        "unit": "US$/u",
        "desc": "Precio neto medio canal R1 Estándar (antes de MO y costos fijos)",
        "is_int": False,
    },
    {
        "key": "precio_neto_pro",
        "label": "Precio Neto R1 Pro",
        "categoria": "💰 Precios y Materiales",
        "default": C.PRECIO_PRO,
        "min_val": 50.0,
        "max_val": 350.0,
        "step": 1.0,
        "unit": "US$/u",
        "desc": "Precio neto medio canal R1 Pro",
        "is_int": False,
    },
    {
        "key": "materiales_std",
        "label": "Costo Materiales Estándar",
        "categoria": "💰 Precios y Materiales",
        "default": C.MATERIAL_STD,
        "min_val": 20.0,
        "max_val": 150.0,
        "step": 0.50,
        "unit": "US$/u",
        "desc": "Costo directo de materiales para variante R1 Estándar",
        "is_int": False,
    },
    {
        "key": "materiales_pro",
        "label": "Costo Materiales Pro",
        "categoria": "💰 Precios y Materiales",
        "default": C.MATERIAL_PRO,
        "min_val": 20.0,
        "max_val": 180.0,
        "step": 0.50,
        "unit": "US$/u",
        "desc": "Costo directo de materiales para variante R1 Pro",
        "is_int": False,
    },
    {
        "key": "pct_pro_sem1_26",
        "label": "% Mezcla Pro (Semanas 1 a 26)",
        "categoria": "📊 Mezcla y Calidad",
        "default": C.PCT_PRO_SEM1_26,
        "min_val": 0.05,
        "max_val": 0.80,
        "step": 0.01,
        "unit": "Ratio",
        "desc": "Participación del modelo Pro en el primer semestre (30% base)",
        "is_int": False,
    },
    {
        "key": "pct_pro_sem27_52",
        "label": "% Mezcla Pro (Semanas 27 a 52)",
        "categoria": "📊 Mezcla y Calidad",
        "default": C.PCT_PRO_SEM27_52,
        "min_val": 0.05,
        "max_val": 0.80,
        "step": 0.01,
        "unit": "Ratio",
        "desc": "Participación del modelo Pro en el segundo semestre (35% base)",
        "is_int": False,
    },
    {
        "key": "falla_std",
        "label": "Tasa de Falla Estándar (E5)",
        "categoria": "📊 Mezcla y Calidad",
        "default": C.FALLA_STD,
        "min_val": 0.005,
        "max_val": 0.15,
        "step": 0.005,
        "unit": "Ratio",
        "desc": "Defectos en prueba eléctrica final para Estándar (3,5% base)",
        "is_int": False,
    },
    {
        "key": "falla_pro",
        "label": "Tasa de Falla Pro (E5)",
        "categoria": "📊 Mezcla y Calidad",
        "default": C.FALLA_PRO,
        "min_val": 0.005,
        "max_val": 0.15,
        "step": 0.005,
        "unit": "Ratio",
        "desc": "Defectos en prueba eléctrica final para Pro (4,0% base)",
        "is_int": False,
    },
    {
        "key": "tasa_recuperacion_retrabajo",
        "label": "Tasa Recuperación Retrabajo",
        "categoria": "📊 Mezcla y Calidad",
        "default": C.RECUPERACION,
        "min_val": 0.30,
        "max_val": 0.99,
        "step": 0.01,
        "unit": "Ratio",
        "desc": "Porcentaje de unidades defectuosas recuperadas en retrabajo (75% base)",
        "is_int": False,
    },
    {
        "key": "devolucion_garantia_pct",
        "label": "Tasa Devolución en Garantía",
        "categoria": "📦 Inventario y Garantías",
        "default": C.DEVOLUCION_PCT,
        "min_val": 0.001,
        "max_val": 0.05,
        "step": 0.001,
        "unit": "Ratio",
        "desc": "Tasa de devoluciones por fallas de cliente en garantía (0,8% base)",
        "is_int": False,
    },
    {
        "key": "costo_garantia",
        "label": "Costo por Reclamo Garantía",
        "categoria": "📦 Inventario y Garantías",
        "default": C.DEVOLUCION_COSTO,
        "min_val": 20.0,
        "max_val": 250.0,
        "step": 5.0,
        "unit": "US$/u",
        "desc": "Costo promedio por unidad tramitada en garantía ($85)",
        "is_int": False,
    },
    {
        "key": "inventario_inicial",
        "label": "Inventario Inicial (Semana 1)",
        "categoria": "📦 Inventario y Garantías",
        "default": C.INVENTARIO_INICIAL,
        "min_val": 0.0,
        "max_val": 1500.0,
        "step": 25.0,
        "unit": "Unidades",
        "desc": "Stock de producto terminado al inicio de la semana 1 (200 u)",
        "is_int": False,
    },
    {
        "key": "inventario_maximo",
        "label": "Capacidad Máxima Almacén PT",
        "categoria": "📦 Inventario y Garantías",
        "default": C.INVENTARIO_MAX_PT,
        "min_val": 300.0,
        "max_val": 4000.0,
        "step": 50.0,
        "unit": "Unidades",
        "desc": "Capacidad máxima física de producto terminado en almacén (1.500 u)",
        "is_int": False,
    },
    {
        "key": "costo_mantener_inv_anual",
        "label": "Costo Mantener Inventario Anual",
        "categoria": "📦 Inventario y Garantías",
        "default": C.COSTO_MANTENER_INV,
        "min_val": 0.05,
        "max_val": 0.50,
        "step": 0.01,
        "unit": "Ratio",
        "desc": "Tasa de posesión de inventario anual sobre el costo de materiales (20%)",
        "is_int": False,
    },
    {
        "key": "salario_supervisor",
        "label": "Salario Semanal Supervisor",
        "categoria": "🏢 Estructura Laboral y Fijos",
        "default": C.SUPERVISOR_SEMANAL,
        "min_val": 400.0,
        "max_val": 3000.0,
        "step": 50.0,
        "unit": "US$/sem",
        "desc": "Salario fijo semanal del supervisor de planta ($1.050)",
        "is_int": False,
    },
    {
        "key": "cargas_sociales_pct",
        "label": "Cargas Sociales y Prestaciones",
        "categoria": "🏢 Estructura Laboral y Fijos",
        "default": C.CARGAS_SOCIALES,
        "min_val": 0.10,
        "max_val": 0.60,
        "step": 0.02,
        "unit": "Ratio",
        "desc": "Recargo por beneficios laborales sobre salarios brutos (30%)",
        "is_int": False,
    },
    {
        "key": "fijos_planta_semanal",
        "label": "Costos Fijos Planta Base / Sem.",
        "categoria": "🏢 Estructura Laboral y Fijos",
        "default": C.FIJOS_PLANTA_SEMANAL,
        "min_val": 1000.0,
        "max_val": 10000.0,
        "step": 100.0,
        "unit": "US$/sem",
        "desc": "Alquiler, energía base, seguros y gastos generales fijos ($3.500/sem)",
        "is_int": False,
    },
    {
        "key": "fijo_turno_adicional",
        "label": "Fijo Adicional por Turno Extra",
        "categoria": "🏢 Estructura Laboral y Fijos",
        "default": C.COSTO_FIJO_TURNO_EXTRA,
        "min_val": 100.0,
        "max_val": 3000.0,
        "step": 50.0,
        "unit": "US$/sem",
        "desc": "Costo fijo semanal por cada turno extra adicional ($600/sem)",
        "is_int": False,
    },
    {
        "key": "lote_produccion_defecto",
        "label": "Tamaño de Lote Estándar (Q)",
        "categoria": "⚙️ Lotes, Finanzas y Presupuesto",
        "default": C.LOTE_DEFAULT,
        "min_val": 25,
        "max_val": 500,
        "step": 25,
        "unit": "Unidades",
        "desc": "Tamaño de lote base de corrida por variante (100 u)",
        "is_int": True,
    },
    {
        "key": "tiempo_cambio_lote",
        "label": "Tiempo de Cambio de Lote (s)",
        "categoria": "⚙️ Lotes, Finanzas y Presupuesto",
        "default": C.CAMBIO_VARIANTE_DEFAULT,
        "min_val": 2.0,
        "max_val": 60.0,
        "step": 1.0,
        "unit": "Minutos",
        "desc": "Tiempo de parada de línea por cambio de variante (20 min)",
        "is_int": False,
    },
    {
        "key": "limite_inversion_fiscal",
        "label": "Límite Presupuestario Inversión",
        "categoria": "⚙️ Lotes, Finanzas y Presupuesto",
        "default": C.LIMITE_INVERSION,
        "min_val": 20000.0,
        "max_val": 400000.0,
        "step": 5000.0,
        "unit": "US$",
        "desc": "Presupuesto máximo de inversión sin aprobación de la Junta ($120.000)",
        "is_int": False,
    },
    {
        "key": "tasa_descuento_anual",
        "label": "Tasa de Descuento Anual (WACC)",
        "categoria": "⚙️ Lotes, Finanzas y Presupuesto",
        "default": C.TASA_DESCUENTO_ANUAL,
        "min_val": 0.04,
        "max_val": 0.30,
        "step": 0.01,
        "unit": "Ratio",
        "desc": "Tasa de descuento anual de la empresa para calcular el VAN (12%)",
        "is_int": False,
    },
]


def get_default_parameters_dict() -> dict[str, float | int]:
    """Retorna un diccionario con los 22 parámetros oficiales del caso."""
    return {
        p["key"]: (int(p["default"]) if p["is_int"] else float(p["default"]))
        for p in PARAMETROS_CATALOGO
    }


def get_active_parameters_dict() -> dict[str, float | int]:
    """
    Retorna el diccionario de parámetros activos en la sesión actual de Streamlit.
    Si aún no están inicializados, toma los del Excel cargado (si existe) o los valores oficiales.
    Funciona tanto dentro como fuera de Streamlit (p. ej. en scripts de test).
    """
    defaults = get_default_parameters_dict()
    try:
        import streamlit as st
        if "active_parameters" not in st.session_state:
            if "custom_extracted" in st.session_state and st.session_state["custom_extracted"]:
                excel_p = st.session_state["custom_extracted"].get("parametros_dict", {})
                active = dict(defaults)
                for k, v in excel_p.items():
                    if k in active:
                        active[k] = int(v) if isinstance(active[k], int) else float(v)
                st.session_state["active_parameters"] = active
                st.session_state["excel_parameters"] = dict(active)
            else:
                st.session_state["active_parameters"] = dict(defaults)
                st.session_state["excel_parameters"] = dict(defaults)
        return dict(st.session_state["active_parameters"])
    except Exception:
        return defaults


def set_active_parameter(key: str, value: float | int):
    """Actualiza un parámetro activo en st.session_state."""
    try:
        import streamlit as st
        if "active_parameters" not in st.session_state:
            get_active_parameters_dict()
        st.session_state["active_parameters"][key] = value
    except Exception:
        pass


def reset_active_parameters_to_excel():
    """Restablece los parámetros activos a los valores del archivo Excel cargado (o base)."""
    try:
        import streamlit as st
        base = st.session_state.get("excel_parameters") or get_default_parameters_dict()
        st.session_state["active_parameters"] = dict(base)
    except Exception:
        pass


def reset_active_parameters_to_defaults():
    """Restablece los parámetros activos a los valores oficiales de los Anexos 1-11."""
    try:
        import streamlit as st
        defaults = get_default_parameters_dict()
        st.session_state["active_parameters"] = dict(defaults)
    except Exception:
        pass


# ═══════════════════════════════════════════════
# Estilos Corporativos para Excel
# ═══════════════════════════════════════════════
HEADER_FILL = PatternFill(start_color="1B4F72", end_color="1B4F72", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ZEBRA_FILL = PatternFill(start_color="F2F4F4", end_color="F2F4F4", fill_type="solid")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1B4F72")
SUBTITLE_FONT = Font(name="Calibri", size=10, italic=True, color="5D6D7E")
BORDER_THIN = Border(
    left=Side(style="thin", color="BDC3C7"),
    right=Side(style="thin", color="BDC3C7"),
    top=Side(style="thin", color="BDC3C7"),
    bottom=Side(style="thin", color="BDC3C7"),
)


def _apply_table_styles(ws, start_row: int = 1):
    """Aplica formato profesional de tabla a una hoja de openpyxl."""
    # Estilo de encabezado
    max_col = ws.max_column
    max_row = ws.max_row

    for col in range(1, max_col + 1):
        cell = ws.cell(row=start_row, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Estilo de datos
    for r in range(start_row + 1, max_row + 1):
        is_even = (r % 2 == 0)
        for col in range(1, max_col + 1):
            cell = ws.cell(row=r, column=col)
            cell.border = BORDER_THIN
            if is_even:
                cell.fill = ZEBRA_FILL
            # Alineación numérica
            if isinstance(cell.value, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Ajuste automático de ancho de columna
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


def generate_master_workbook(custom_params: dict[str, Any] | None = None) -> openpyxl.Workbook:
    """Construye en memoria el libro Excel completo con las 6 hojas del modelo."""
    wb = openpyxl.Workbook()

    # ── Hoja 1: Parametros ──
    ws_param = wb.active
    ws_param.title = "Parametros"
    ws_param.append(["Parametro", "Valor", "Unidad", "Minimo", "Maximo", "Descripcion"])
    for p in PARAMETROS_CATALOGO:
        k = p["key"]
        val = custom_params.get(k, p["default"]) if custom_params else p["default"]
        val = int(val) if p["is_int"] else float(val)
        ws_param.append([k, val, p["unit"], p["min_val"], p["max_val"], p["desc"]])
    _apply_table_styles(ws_param)

    # ── Hoja 2: Estaciones ──
    ws_est = wb.create_sheet(title="Estaciones")
    ws_est.append(["Configuracion", "Estacion", "Operacion", "Tiempo_Estandar_min", "Tiempo_Pro_min", "CV_Variabilidad"])
    # Estaciones Línea 6
    for est_id, info in C.ESTACIONES_6.items():
        ws_est.append(["Linea_6_Ops", est_id, info["op"], info["t_std"], info["t_pro"], info.get("cv", 0.10)])
    # Estaciones Línea 8
    for est_id, info in C.ESTACIONES_8.items():
        ws_est.append(["Linea_8_Ops", est_id, info["op"], info["t_std"], info["t_pro"], 0.10])
    _apply_table_styles(ws_est)

    # ── Hoja 3: Puestos ──
    ws_puestos = wb.create_sheet(title="Puestos")
    ws_puestos.append(["Puesto", "Salario_Hora_USD", "Cargas_Sociales_Pct", "Por_Linea", "Por_Turno", "Observaciones"])
    puestos_data = [
        ["Operador de línea (E1-E4, E6)", C.SALARIO_OPERADOR, C.CARGAS_SOCIALES, 5, 0, "5 operadores por línea en esquema actual"],
        ["Técnico de pruebas (E5)", C.SALARIO_TECNICO, C.CARGAS_SOCIALES, 1, 0, "1 por línea en estación E5"],
        ["Manipulador de materiales", C.SALARIO_MANIPULADOR, C.CARGAS_SOCIALES, 0, 1, "Atiende hasta 3 líneas o 6 células"],
        ["Técnico de retrabajo", C.SALARIO_RETRABAJO, C.CARGAS_SOCIALES, 0, 1, "Fuera de línea; 1 por turno"],
        ["Líder de turno (2.º y 3.º)", C.SALARIO_LIDER_TURNO, C.CARGAS_SOCIALES, 0, 1, "Sustituye al manipulador en turnos extra"],
        ["Trabajador célula", C.SALARIO_CELULA, C.CARGAS_SOCIALES, 0, 3, "Polivalente; 3 por célula y turno"],
    ]
    for row in puestos_data:
        ws_puestos.append(row)
    _apply_table_styles(ws_puestos)

    # ── Hoja 4: Opciones ──
    ws_opc = wb.create_sheet(title="Opciones")
    ws_opc.append(["Opcion", "Inversion_USD", "Plazo_Semanas", "Efecto_Proceso", "Personal_Adicional", "Restricciones"])
    opciones_data = [
        ["O1. Ocho operadores por línea", C.INVERSION_REEQUILIBRIO, C.PLAZO_REEQUILIBRIO, "Tiempos Anexo 4", "+2 operadores/línea", "US$ 9.000 por línea"],
        ["O2. Tercera línea", C.INVERSION_TERCERA_LINEA, C.PLAZO_TERCERA_LINEA, "Línea idéntica Anexo 3", "+6 operadores en línea", "Ocupa 120 m²"],
        ["O3. Turnos 2.º y 3.º", 0.0, 2, "Turno 2 (92%), Turno 3 (88%)", "Plantilla completa por turno", "Curva de aprendizaje 4 semanas"],
        ["O4. Células de trabajo", C.INVERSION_CELULA, C.PLAZO_CELULA, "Ensamble completo x trabajador", "+3 por célula/turno", "Ocupa 40 m²; penalización 8%"],
        ["O5. Dispositivo para puerta", C.INVERSION_DISPOSITIVO_PUERTA, C.PLAZO_DISPOSITIVO, "Reduce E2 y E3 en línea", "Sin cambio", "US$ 22.000 por línea; 10 semanas"],
        ["O6. Subcontratar puerta", 0.0, 4, "Elimina E2; reduce E3", "-1 operador por línea", "+US$ 4,80/u; máx 1.200 u/sem"],
        ["O7. Sábados con horas extra", 0.0, 0, "6,5 h productivas turno 1", "Personal existente", "Máximo 3 sábados/mes, +50% recargo"],
    ]
    for row in opciones_data:
        ws_opc.append(row)
    _apply_table_styles(ws_opc)

    # ── Hoja 5: Demanda ──
    ws_dem = wb.create_sheet(title="Demanda")
    ws_dem.append(["Semana", "Fecha_Inicio", "Demanda_Base", "Demanda_Optimista", "Demanda_Canal", "Pct_Pro"])
    for d in C.DEMANDA_SEMANAL:
        sem = d["sem"]
        pct_pro = C.PCT_PRO_SEM1_26 if sem <= 26 else C.PCT_PRO_SEM27_52
        ws_dem.append([sem, d["fecha"], d["base"], d["optim"], d["canal"], pct_pro])
    _apply_table_styles(ws_dem)

    # ── Hoja 6: Escenarios ──
    ws_esc = wb.create_sheet(title="Escenarios")
    ws_esc.append(["Escenario", "Probabilidad", "Total_Anual_Unidades", "Descripcion"])
    esc_data = [
        ["Base", C.PROB_BASE, 60720, "Pico de 1.900 en Black Friday, modera en enero y sube 0,8%/sem"],
        ["Optimista", C.PROB_OPTIMISTA, 72170, "+20% sobre base desde noviembre; expansión regional"],
        ["Canal", C.PROB_CANAL, 42870, "Fuerte en temporada, colapsa a 650 u/sem en enero"],
    ]
    for row in esc_data:
        ws_esc.append(row)
    _apply_table_styles(ws_esc)

    return wb


def export_template_bytes(custom_params: dict[str, Any] | None = None) -> bytes:
    """Genera y retorna en memoria los bytes del archivo Excel plantilla."""
    wb = generate_master_workbook(custom_params)
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def ensure_default_excel_files():
    """Crea la carpeta data/ y los archivos maestros por defecto si no existen."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_EXCEL_PATH.exists() or not TEMPLATE_EXCEL_PATH.exists():
        wb = generate_master_workbook()
        wb.save(DEFAULT_EXCEL_PATH)
        wb.save(TEMPLATE_EXCEL_PATH)


def load_data_from_excel(source: str | Path | BinaryIO) -> dict[str, pd.DataFrame]:
    """
    Lee un archivo Excel (ruta o BytesIO) y retorna un diccionario de DataFrames
    con las 6 hojas del modelo.
    """
    xls = pd.ExcelFile(source)
    required_sheets = ["Parametros", "Estaciones", "Puestos", "Opciones", "Demanda", "Escenarios"]
    
    missing_sheets = [s for s in required_sheets if s not in xls.sheet_names]
    if missing_sheets:
        raise ValueError(
            f"El archivo Excel subido no contiene las hojas obligatorias: {', '.join(missing_sheets)}. "
            f"Por favor descargue la plantilla oficial y mantenga los nombres de hojas."
        )

    dfs = {
        sheet: pd.read_excel(xls, sheet_name=sheet)
        for sheet in required_sheets
    }
    return dfs


def validate_and_extract_simulation_data(dfs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """
    Valida las columnas requeridas y extrae los parámetros hacia un formato
    fácilmente consumible por el motor de simulación.
    """
    # 1. Validar Demanda
    df_demanda = dfs["Demanda"]
    req_dem_cols = ["Semana", "Demanda_Base", "Demanda_Optimista", "Demanda_Canal"]
    for col in req_dem_cols:
        if col not in df_demanda.columns:
            raise ValueError(f"Falta la columna obligatoria '{col}' en la hoja 'Demanda'.")

    # 2. Validar Escenarios
    df_esc = dfs["Escenarios"]
    if "Escenario" not in df_esc.columns or "Probabilidad" not in df_esc.columns:
        raise ValueError("La hoja 'Escenarios' debe contener las columnas 'Escenario' y 'Probabilidad'.")

    # 3. Validar Parámetros
    df_params = dfs["Parametros"]
    param_dict = {}
    if "Parametro" in df_params.columns and "Valor" in df_params.columns:
        for _, row in df_params.iterrows():
            param_dict[str(row["Parametro"]).strip()] = row["Valor"]

    return {
        "demanda_df": df_demanda,
        "escenarios_df": df_esc,
        "parametros_dict": param_dict,
        "estaciones_df": dfs["Estaciones"],
        "puestos_df": dfs["Puestos"],
        "opciones_df": dfs["Opciones"],
    }
