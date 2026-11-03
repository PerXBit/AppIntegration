"""
app.py – Punto de Entrada Principal del Tablero Simulador de Operaciones "Resguarda" (HCC).

Desarrollado para la Dirección de Operaciones de Hogar Conectado del Caribe, S.R.L.
Inspirado en el caso «Parcel Guard: Keeping Up with Demand» (Ivey Publishing, 2020).
"""
from __future__ import annotations

import streamlit as st

# Configuración inicial de página de Streamlit (debe ser la primera llamada)
st.set_page_config(
    page_title="Resguarda · Tablero Simulador de Operaciones",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.components.cards import render_header
from src.components.styles import apply_corporate_styles
from src.model.data_loader import ensure_default_excel_files
from src.views.view_diagnostico import render_view_diagnostico
from src.views.view_escenarios import render_view_escenarios
from src.views.view_gestion_datos import render_view_gestion_datos
from src.views.view_nota_tecnica import render_view_nota_tecnica
from src.views.view_recomendacion import render_view_recomendacion
from src.views.view_sensibilidad import render_view_sensibilidad
from src.views.view_simulador import render_view_simulador


def main():
    # Asegurar estilos y datos por defecto
    apply_corporate_styles()
    ensure_default_excel_files()

    # Estado de datos
    is_custom = st.session_state.get("is_custom_data", False)
    custom_filename = st.session_state.get("custom_filename", "")

    # Barra lateral de navegación
    with st.sidebar:
        st.markdown("### 🛡️ HCC RESGUARDA")
        st.markdown("**Simulador de Capacidad y Demanda**")
        st.caption("Dirección de Operaciones · 2026–2027")

        if is_custom:
            st.success(f"🔵 Datos: {custom_filename}")
        else:
            st.info("🟢 Datos: Oficiales del Caso")

        st.markdown("---")
        st.markdown("#### 🧭 Navegación")
        
        view_selected = st.radio(
            "Selecciona un módulo:",
            [
                "⚡ Simulador Semana a Semana",
                "🔬 Diagnóstico y Cuello de Botella",
                "⚖️ Comparación de Estrategias y Riesgo",
                "🌪️ Análisis de Sensibilidad (Tornado)",
                "👔 Recomendación Ejecutiva al Consejo",
                "📐 Nota Técnica y Validación (13 Control)",
                "📁 Gestión de Datos y Plantilla Excel",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("#### 📌 Parámetros Clave")
        st.markdown(
            """
            - **Horizonte**: 52 semanas
            - **Black Friday**: Semana 8 (1.900 u)
            - **Día de las Madres**: Semanas 33–34
            - **Tope Inversión**: US$ 120.000
            - **Superficie Libre**: 180 m²
            - **Tasa Descuento**: 12% anual
            """
        )
        st.markdown("---")
        st.caption("Basado en el caso *Parcel Guard* (Ivey 2020) adaptado por Félix J. Rodríguez P.")

    # Encabezado corporativo institucional
    badge_label = "Datos Personalizados" if is_custom else "Datos Oficiales"
    badge_type = "info" if is_custom else "success"
    render_header(
        title="Resguarda: Producir al Ritmo de la Demanda",
        subtitle="Hogar Conectado del Caribe, S.R.L. · Tablero de Simulación para Decisión del Consejo",
        badge_text=badge_label,
        badge_type=badge_type,
    )

    # Enrutamiento de vistas
    if view_selected.startswith("⚡"):
        render_view_simulador()
    elif view_selected.startswith("🔬"):
        render_view_diagnostico()
    elif view_selected.startswith("⚖️"):
        render_view_escenarios()
    elif view_selected.startswith("🌪️"):
        render_view_sensibilidad()
    elif view_selected.startswith("👔"):
        render_view_recomendacion()
    elif view_selected.startswith("📐"):
        render_view_nota_tecnica()
    elif view_selected.startswith("📁"):
        render_view_gestion_datos()


if __name__ == "__main__":
    main()
