"""
view_gestion_datos.py – Centro de Gestión de Datos, Carga de Archivos Excel y Descarga de Plantillas.
"""
from __future__ import annotations

import io
import streamlit as st
import pandas as pd

from src.components.cards import render_alert, render_kpi
from src.components.parameter_editor import render_parameter_editor
from src.model.data_loader import (
    DEFAULT_EXCEL_PATH,
    export_template_bytes,
    get_active_parameters_dict,
    get_default_parameters_dict,
    load_data_from_excel,
    reset_active_parameters_to_defaults,
    validate_and_extract_simulation_data,
)


def render_view_gestion_datos():
    st.subheader("📁 Centro de Gestión de Datos y Plantillas Excel")
    st.markdown(
        """
        Este módulo permite **iniciar la simulación desde un archivo Excel** estructurado según el modelo de datos
        del caso *Resguarda*. Puedes descargar la **Plantilla Oficial**, modificar los supuestos o demandas con tus propios datos,
        y subirlos para que todo el simulador se recalcule automáticamente.
        """
    )

    # Estado actual
    is_custom = st.session_state.get("is_custom_data", False)
    custom_filename = st.session_state.get("custom_filename", "")

    col_stat1, col_stat2 = st.columns([2, 1])
    with col_stat1:
        if is_custom:
            render_alert(
                "🟢 MODO DE DATOS ACTIVADO: DATOS PERSONALIZADOS",
                f"La aplicación está ejecutando los cálculos con el archivo subido: <b>{custom_filename}</b>. "
                "Todas las vistas y simulaciones reflejan estos datos.",
                "info",
            )
        else:
            render_alert(
                "🟢 MODO DE DATOS ACTIVADO: DATOS OFICIALES DEL CASO",
                "La aplicación está utilizando el libro maestro oficial <code>data/resguarda_datos_caso.xlsx</code> "
                "con las cifras validadas de los Anexos 1 al 11.",
                "success",
            )

    with col_stat2:
        template_bytes = export_template_bytes()
        st.download_button(
            label="📥 Descargar Plantilla Oficial (Excel)",
            data=template_bytes,
            file_name="plantilla_simulador_resguarda.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Descarga el libro Excel preformateado con las 6 hojas del modelo",
            use_container_width=True,
        )
        if is_custom:
            if st.button("🔄 Restablecer a Datos Oficiales", use_container_width=True):
                st.session_state["is_custom_data"] = False
                st.session_state["custom_data"] = None
                st.session_state["custom_filename"] = ""
                st.session_state["custom_extracted"] = None
                reset_active_parameters_to_defaults()
                st.rerun()

    st.markdown("---")

    # Subida de archivo
    st.markdown("### 📤 Cargar Archivo Excel con Datos Propios")
    uploaded_file = st.file_uploader(
        "Arrastra o selecciona un archivo Excel (.xlsx)",
        type=["xlsx"],
        help="El archivo debe conservar la estructura de las 6 hojas de la plantilla oficial.",
    )

    if uploaded_file is not None:
        try:
            with st.spinner("Validando esquema del libro Excel..."):
                dfs = load_data_from_excel(uploaded_file)
                extracted = validate_and_extract_simulation_data(dfs)

            st.session_state["is_custom_data"] = True
            st.session_state["custom_data"] = dfs
            st.session_state["custom_extracted"] = extracted
            st.session_state["custom_filename"] = uploaded_file.name

            # Inicializar los parámetros con los del Excel subido
            defaults = get_default_parameters_dict()
            excel_p = extracted.get("parametros_dict", {})
            active = dict(defaults)
            for k, v in excel_p.items():
                if k in active:
                    active[k] = int(v) if isinstance(active[k], int) else float(v)
            st.session_state["active_parameters"] = active
            st.session_state["excel_parameters"] = dict(active)

            render_alert(
                "✅ Archivo Excel cargado y validado exitosamente",
                f"Se han procesado las 6 hojas de <b>{uploaded_file.name}</b>. "
                f"Los 22 parámetros y la demanda ({len(extracted['demanda_df'])} semanas) se han cargado en memoria. "
                "Puedes modificarlos directamente abajo si deseas evaluar sensibilidades adicionales.",
                "success",
            )
            st.rerun()

        except Exception as e:
            render_alert(
                "❌ Error al procesar el archivo Excel",
                f"Detalle del error: {str(e)}.<br>Por favor verifica que el archivo siga el formato de la plantilla oficial descargable.",
                "danger",
            )

    # ═══════════════════════════════════════════════
    # Editor Interactivo de Parámetros (22 Parámetros)
    # ═══════════════════════════════════════════════
    st.markdown("---")
    render_parameter_editor(
        key_prefix="gestion",
        title="🎛️ Editor Interactivo de Parámetros del Modelo (Modificación Amigable)",
        show_header=True,
    )

    # Botón para descargar Excel con los parámetros actualmente modificados
    current_active_params = get_active_parameters_dict()
    custom_excel_bytes = export_template_bytes(current_active_params)
    st.download_button(
        label="💾 Descargar Plantilla Excel con Parámetros Modificados Actuales",
        data=custom_excel_bytes,
        file_name="resguarda_parametros_personalizados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Descarga un nuevo libro Excel que incluye en la hoja 'Parametros' todos los ajustes que realizaste en pantalla.",
    )

    # Vista previa de datos cargados
    active_dfs = st.session_state.get("custom_data")
    if active_dfs is None:
        # Cargar datos base para inspección
        try:
            active_dfs = load_data_from_excel(DEFAULT_EXCEL_PATH)
        except Exception:
            active_dfs = {}

    if active_dfs:
        st.markdown("---")
        st.markdown("### 🔍 Inspección de Datos Activos en Memoria")
        tab_p, tab_e, tab_pu, tab_o, tab_d, tab_esc = st.tabs([
            "Parametros", "Estaciones", "Puestos", "Opciones", "Demanda (52 sem)", "Escenarios"
        ])

        with tab_p:
            st.dataframe(active_dfs.get("Parametros"), use_container_width=True, hide_index=True)
        with tab_e:
            st.dataframe(active_dfs.get("Estaciones"), use_container_width=True, hide_index=True)
        with tab_pu:
            st.dataframe(active_dfs.get("Puestos"), use_container_width=True, hide_index=True)
        with tab_o:
            st.dataframe(active_dfs.get("Opciones"), use_container_width=True, hide_index=True)
        with tab_d:
            st.dataframe(active_dfs.get("Demanda"), use_container_width=True, hide_index=True)
        with tab_esc:
            st.dataframe(active_dfs.get("Escenarios"), use_container_width=True, hide_index=True)
