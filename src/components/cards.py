"""
cards.py – Componentes de tarjetas métricas corporativas y alertas.
"""
from typing import Any
import streamlit as st


def render_header(
    title: str = "Resguarda: Simulador de Capacidad y Demanda",
    subtitle: str = "Hogar Conectado del Caribe, S.R.L. · Dirección de Operaciones",
    badge_text: str | None = None,
    badge_type: str = "info",
):
    """Renderiza la barra de cabecera institucional."""
    badge_html = ""
    if badge_text:
        badge_html = f'<span class="badge badge-{badge_type}" style="margin-left: 10px;">{badge_text}</span>'
    
    st.markdown(
        f"""
        <div class="header-container">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h1 class="header-title">{title} {badge_html}</h1>
                    <div class="header-subtitle">{subtitle}</div>
                </div>
                <div style="text-align: right; font-size: 0.8rem; color: #EBF5FB;">
                    <div>Modelo V1.0 · Caso Ivey 2020</div>
                    <div>Santo Domingo Oeste, R.D.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(
    label: str,
    value: str,
    delta: str | None = None,
    delta_color: str = "normal",
    help_text: str | None = None,
):
    """Muestra una tarjeta KPI estilizada."""
    delta_html = ""
    if delta:
        color = "#16A34A" if delta_color == "normal" else "#DC2626"
        delta_html = f'<div class="metric-delta" style="color: {color};">{delta}</div>'
    
    help_attr = f'title="{help_text}"' if help_text else ""
    st.markdown(
        f"""
        <div class="metric-card" {help_attr}>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert(title: str, text: str, alert_type: str = "info"):
    """Muestra una tarjeta de alerta informativa/advertencia/éxito."""
    st.markdown(
        f"""
        <div class="alert-card alert-{alert_type}">
            <div style="font-weight: 700; margin-bottom: 0.2rem;">{title}</div>
            <div style="font-size: 0.9rem; line-height: 1.4;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
