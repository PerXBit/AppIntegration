"""
styles.py – Inyección de estilos CSS corporativos para Streamlit.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

def apply_corporate_styles():
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Top header bar */
        .header-container {
            background: linear-gradient(135deg, #1B4F72 0%, #2874A6 100%);
            padding: 1.2rem 1.8rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(27, 79, 114, 0.15);
        }
        .header-title {
            font-size: 1.6rem;
            font-weight: 700;
            margin: 0;
            color: #FFFFFF;
        }
        .header-subtitle {
            font-size: 0.95rem;
            color: #D4E6F1;
            margin-top: 0.2rem;
        }

        /* Metric Card styling */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            transition: all 0.2s ease;
        }
        .metric-card:hover {
            box-shadow: 0 4px 10px rgba(0,0,0,0.07);
            border-color: #CBD5E1;
        }
        .metric-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 1.55rem;
            font-weight: 700;
            color: #1E293B;
            margin: 0.25rem 0;
        }
        .metric-delta {
            font-size: 0.8rem;
            font-weight: 500;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 20px;
        }
        .badge-success { background-color: #DCFCE7; color: #166534; }
        .badge-warning { background-color: #FEF3C7; color: #92400E; }
        .badge-danger  { background-color: #FEE2E2; color: #991B1B; }
        .badge-info    { background-color: #E0F2FE; color: #075985; }

        /* Custom Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px;
            font-weight: 500;
            font-size: 0.95rem;
            border-radius: 6px 6px 0 0;
        }
        .stTabs [aria-selected="true"] {
            color: #1B4F72 !important;
            font-weight: 700 !important;
            border-bottom: 3px solid #1B4F72 !important;
        }

        /* Callout alert cards */
        .alert-card {
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 5px solid;
        }
        .alert-info {
            background-color: #F0F9FF;
            border-color: #0284C7;
            color: #0C4A6E;
        }
        .alert-warning {
            background-color: #FFFBEB;
            border-color: #D97706;
            color: #78350F;
        }
        .alert-success {
            background-color: #F0FDF4;
            border-color: #16A34A;
            color: #14532D;
        }
        .alert-danger {
            background-color: #FEF2F2;
            border-color: #DC2626;
            color: #7F1D1D;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE COLORIZACIÓN CONDICIONAL (SEMÁFORO: VERDE, AMARILLO, ROJO)
# ═══════════════════════════════════════════════════════════════════════════

def _apply_map(styler, func, subset):
    """Aplica una función de mapeo al Styler de pandas compatible con pandas >= 2.0."""
    if hasattr(styler, "map"):
        return styler.map(func, subset=subset)
    elif hasattr(styler, "applymap"):
        return styler.applymap(func, subset=subset)
    return styler


def color_service_level(v: float) -> str:
    """Semáforo para Nivel de Servicio (%): Verde >= 90%, Amarillo 75-89%, Rojo < 75%."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val >= 90.0:
        return "background-color: #E8F8F5; color: #145A32; font-weight: 600;"
    elif val >= 75.0:
        return "background-color: #FEF9E7; color: #7D6608; font-weight: 600;"
    else:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 600;"


def color_npv(v: float) -> str:
    """Semáforo para VAN / Resultados Económicos en US$: Verde alto > 2.5M, Verde > 0, Rojo < 0."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val >= 2_800_000:
        return "background-color: #D4EFDF; color: #145A32; font-weight: 700;"
    elif val > 0:
        return "background-color: #E8F8F5; color: #196F3D; font-weight: 600;"
    elif val == 0:
        return "background-color: #F8F9F9; color: #5D6D7E;"
    else:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 700;"


def color_lost_sales(v: float) -> str:
    """Semáforo para Ventas Perdidas: Verde = 0, Amarillo <= 1.000, Rojo > 1.000."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val <= 0.001:
        return "background-color: #E8F8F5; color: #145A32; font-weight: 600;"
    elif val <= 1000.0:
        return "background-color: #FEF9E7; color: #7D6608; font-weight: 600;"
    else:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 700;"


def color_backlog(v: float) -> str:
    """Semáforo para Backlog (pedidos pendientes): Verde = 0, Amarillo <= 250, Rojo > 250."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val <= 0.001:
        return "background-color: #E8F8F5; color: #145A32; font-weight: 600;"
    elif val <= 250.0:
        return "background-color: #FEF9E7; color: #7D6608; font-weight: 600;"
    else:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 700;"


def color_utilization(v: float) -> str:
    """Semáforo para Utilización (%): Rojo >= 98% (Cuello/Saturación), Amarillo 80-97%, Verde 60-79%, Azul <60%."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val >= 98.0:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 700;"
    elif val >= 80.0:
        return "background-color: #FEF9E7; color: #7D6608; font-weight: 600;"
    elif val >= 60.0:
        return "background-color: #E8F8F5; color: #145A32; font-weight: 600;"
    else:
        return "background-color: #EBF5FB; color: #1B4F72;"


def color_capex(v: float) -> str:
    """Semáforo para CapEx Invertido: Verde = $0 (Cero capital varado), Amarillo <= $50k, Rojo > $50k."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val == 0:
        return "background-color: #E8F8F5; color: #145A32; font-weight: 700;"
    elif val <= 50_000:
        return "background-color: #FEF9E7; color: #7D6608; font-weight: 600;"
    else:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 700;"


def color_swing(v: float) -> str:
    """Semáforo para variación del VAN en análisis de tornado."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val > 0:
        return "background-color: #E8F8F5; color: #145A32; font-weight: 600;"
    elif val < 0:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 600;"
    else:
        return "background-color: #F8F9F9; color: #5D6D7E;"


def color_regret(v: float) -> str:
    """Semáforo para Matriz de Arrepentimiento: Verde = 0 (Opción óptima), Rojo si > 500k."""
    try:
        val = float(v)
    except (ValueError, TypeError):
        return ""
    if val == 0:
        return "background-color: #D4EFDF; color: #145A32; font-weight: 700;"
    elif val <= 250_000:
        return "background-color: #E8F8F5; color: #196F3D;"
    elif val <= 750_000:
        return "background-color: #FEF9E7; color: #7D6608;"
    else:
        return "background-color: #FDEDEC; color: #78281F; font-weight: 600;"


def style_comparador_df(df: pd.DataFrame) -> any:
    """Aplica formato semáforo a la tabla comparativa multicriterio de estrategias."""
    styler = df.style

    # Formatos de texto
    formats = {}
    for col in ["Inversión CapEx", "VAN Base (50%)", "VAN Optimista (25%)", "VAN Canal (25%)", "Valor Esperado (VE)", "Peor Caso (MaxiMin)", "Volatilidad (σ)", "Downside Risk"]:
        if col in df.columns:
            formats[col] = "US$ {:,.0f}"
    for col in ["Servicio Anual", "Servicio Black Friday"]:
        if col in df.columns:
            formats[col] = "{:.1f}%"
    for col in ["Ventas Perdidas", "Ventas Perdidas Optimista", "Unidades Atendidas"]:
        if col in df.columns:
            formats[col] = "{:,.0f} u"
    for col in ["Espacio Planta"]:
        if col in df.columns:
            formats[col] = "{:.0f} m²"

    styler = styler.format(formats)

    # Semáforos
    if "Inversión CapEx" in df.columns:
        styler = _apply_map(styler, color_capex, subset=["Inversión CapEx"])
    for van_col in ["VAN Base (50%)", "VAN Optimista (25%)", "VAN Canal (25%)", "Valor Esperado (VE)", "Peor Caso (MaxiMin)"]:
        if van_col in df.columns:
            styler = _apply_map(styler, color_npv, subset=[van_col])
    for srv_col in ["Servicio Anual", "Servicio Black Friday"]:
        if srv_col in df.columns:
            styler = _apply_map(styler, color_service_level, subset=[srv_col])
    for lost_col in ["Ventas Perdidas", "Ventas Perdidas Optimista"]:
        if lost_col in df.columns:
            styler = _apply_map(styler, color_lost_sales, subset=[lost_col])

    return styler


def style_weekly_df(df: pd.DataFrame) -> any:
    """Aplica formato semáforo a la tabla de simulación semanal (semanas 1 a 52)."""
    styler = df.style

    formats = {
        "Demanda": "{:,.0f}",
        "Cap. Bruta": "{:,.0f}",
        "Producción": "{:,.0f}",
        "Atendido": "{:,.0f}",
        "Inv. Final": "{:,.0f}",
        "Backlog": "{:,.0f}",
        "Ventas Perdidas": "{:,.0f}",
        "Nivel Servicio %": "{:.1f}%",
        "Costo MO": "US$ {:,.0f}",
        "Margen Bruto": "US$ {:,.0f}",
        "Flujo Descontado": "US$ {:,.0f}",
    }
    present_formats = {k: v for k, v in formats.items() if k in df.columns}
    styler = styler.format(present_formats)

    if "Nivel Servicio %" in df.columns:
        styler = _apply_map(styler, color_service_level, subset=["Nivel Servicio %"])
    if "Backlog" in df.columns:
        styler = _apply_map(styler, color_backlog, subset=["Backlog"])
    if "Ventas Perdidas" in df.columns:
        styler = _apply_map(styler, color_lost_sales, subset=["Ventas Perdidas"])

    return styler


def style_utilization_df(df: pd.DataFrame, col_name: str = "Utilización %") -> any:
    """Aplica formato semáforo a la tabla de utilización por estación."""
    styler = df.style
    if col_name in df.columns:
        styler = styler.format({col_name: "{:.1f}%"})
        styler = _apply_map(styler, color_utilization, subset=[col_name])
    return styler


def style_tornado_df(df: pd.DataFrame) -> any:
    """Aplica formato semáforo a la tabla del diagrama de tornado."""
    styler = df.style
    formats = {}
    for col in ["Valor Base", "Min_Swing", "Max_Swing", "Rango_Total"]:
        if col in df.columns:
            formats[col] = "US$ {:,.0f}"
    if "Elasticidad" in df.columns:
        formats["Elasticidad"] = "{:+.2f}"

    styler = styler.format(formats)
    for col in ["Min_Swing", "Max_Swing"]:
        if col in df.columns:
            styler = _apply_map(styler, color_swing, subset=[col])
    return styler


def style_regret_matrix_df(df: pd.DataFrame) -> any:
    """Aplica semáforo a la matriz de arrepentimiento (Savage)."""
    styler = df.style
    cols = [c for c in df.columns if c not in ["Estrategia"]]
    formats = {c: "US$ {:,.0f}" for c in cols}
    styler = styler.format(formats)
    for c in cols:
        styler = _apply_map(styler, color_regret, subset=[c])
    return styler

