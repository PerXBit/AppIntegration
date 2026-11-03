"""
parameter_editor.py – Componente visual interactivo y amigable para la edición de parámetros.

Permite modificar los 22 parámetros técnicos, operativos y económicos del modelo
tanto sobre los datos oficiales del caso como sobre un archivo Excel personalizado subido.
"""
from __future__ import annotations

from typing import Any
import streamlit as st

from src.components.cards import render_alert, render_kpi
from src.model.data_loader import (
    PARAMETROS_CATALOGO,
    get_active_parameters_dict,
    get_default_parameters_dict,
    reset_active_parameters_to_defaults,
    reset_active_parameters_to_excel,
    set_active_parameter,
)


def render_parameter_editor(
    key_prefix: str = "gestion",
    title: str = "🎛️ Editor y Ajuste de Parámetros del Modelo (22 Parámetros)",
    show_header: bool = True,
) -> dict[str, float | int]:
    """
    Renderiza un panel interactivo y categorizado para editar los 22 parámetros del modelo.
    Retorna el diccionario de parámetros activos actualizados.
    """
    active_params = get_active_parameters_dict()
    defaults = get_default_parameters_dict()
    excel_base = st.session_state.get("excel_parameters") or defaults
    is_custom_file = st.session_state.get("is_custom_data", False)
    custom_filename = st.session_state.get("custom_filename", "")

    # Contar cuántos parámetros han sido modificados respecto al Excel base
    diff_count = 0
    for k, v in active_params.items():
        base_v = excel_base.get(k, defaults.get(k))
        if base_v is not None and abs(float(v) - float(base_v)) > 1e-5:
            diff_count += 1

    if show_header:
        st.markdown(f"### {title}")
        st.caption(
            "Modifica en tiempo real cualquiera de las variables económicas, de mezcla, calidad o estructura de costes. "
            "Los cambios se aplican automáticamente a la simulación sin alterar tu archivo original."
        )

    # Barra de estado y botones de restablecimiento
    col_st1, col_st2, col_st3 = st.columns([2, 1, 1])
    with col_st1:
        if diff_count > 0:
            st.info(f"✏️ **{diff_count} parámetro(s) modificado(s)** respecto al origen de datos activo ({custom_filename or 'Oficial'}).")
        else:
            st.success(f"✅ Todos los 22 parámetros coinciden con el origen de datos activo ({custom_filename or 'Oficial'}).")

    with col_st2:
        btn_label = "🔄 Restaurar al Excel" if is_custom_file else "🔄 Restaurar a Valores Base"
        if st.button(btn_label, key=f"{key_prefix}_btn_reset_excel", use_container_width=True, help="Restaura los valores al archivo Excel actualmente cargado"):
            reset_active_parameters_to_excel()
            st.toast("Parámetros restaurados a los valores del Excel activo", icon="🔄")
            st.rerun()

    with col_st3:
        if st.button("🏭 Valores Oficiales", key=f"{key_prefix}_btn_reset_official", use_container_width=True, help="Restaura a las cifras oficiales de los Anexos 1 a 11"):
            reset_active_parameters_to_defaults()
            st.toast("Parámetros restaurados a los valores oficiales de los Anexos 1–11", icon="🏭")
            st.rerun()

    # Mini KPIs dinámicos del editor
    p_std = float(active_params.get("precio_neto_std", 129.0))
    m_std = float(active_params.get("materiales_std", 58.0))
    p_pro = float(active_params.get("precio_neto_pro", 169.0))
    m_pro = float(active_params.get("materiales_pro", 74.0))
    pct_pro = float(active_params.get("pct_pro_sem1_26", 0.30))

    margen_std = p_std - m_std
    margen_pro = p_pro - m_pro
    margen_mix = (1 - pct_pro) * margen_std + pct_pro * margen_pro
    limite_inv = float(active_params.get("limite_inversion_fiscal", 120000.0))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Margen Estándar", f"US$ {margen_std:.2f}/u", f"Precio ${p_std:.0f} - Mat ${m_std:.0f}")
    with k2:
        st.metric("Margen Pro", f"US$ {margen_pro:.2f}/u", f"Precio ${p_pro:.0f} - Mat ${m_pro:.0f}")
    with k3:
        st.metric("Margen Mezcla (S1-26)", f"US$ {margen_mix:.2f}/u", f"{pct_pro*100:.0f}% Pro")
    with k4:
        st.metric("Presupuesto Fiscal", f"US$ {limite_inv:,.0f}", "CapEx sin junta")

    st.markdown("---")

    # Agrupar catálogo por categorías
    categorias: dict[str, list[dict[str, Any]]] = {}
    for p in PARAMETROS_CATALOGO:
        cat = p["categoria"]
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(p)

    tab_titles = list(categorias.keys())
    tabs = st.tabs(tab_titles)

    for tab, cat_name in zip(tabs, tab_titles):
        with tab:
            param_list = categorias[cat_name]
            # Mostrar parámetros en 2 columnas
            col_left, col_right = st.columns(2)

            for idx, p in enumerate(param_list):
                col_target = col_left if (idx % 2 == 0) else col_right
                k = p["key"]
                label = p["label"]
                unit = p["unit"]
                desc = p["desc"]
                curr_val = active_params.get(k, p["default"])
                base_val = excel_base.get(k, p["default"])
                is_diff = abs(float(curr_val) - float(base_val)) > 1e-5

                diff_badge = f" · ⚠️ *Modificado (Base: {base_val})*" if is_diff else ""
                help_text = f"{desc}\n\nUnidad: {unit} | Valor base: {base_val} | Rango: [{p['min_val']}, {p['max_val']}]"

                with col_target:
                    st.markdown(f"**{label}** ({unit}){diff_badge}")
                    widget_key = f"{key_prefix}_param_{k}"

                    # Ratios como porcentajes o sliders amigables
                    if unit == "Ratio":
                        # Sliders intuitivos de 0% a 100%
                        min_pct = float(p["min_val"]) * 100.0
                        max_pct = float(p["max_val"]) * 100.0
                        step_pct = float(p["step"]) * 100.0
                        val_pct = float(curr_val) * 100.0

                        new_pct = st.slider(
                            label=label,
                            min_value=round(min_pct, 2),
                            max_value=round(max_pct, 2),
                            value=round(val_pct, 2),
                            step=round(step_pct, 2),
                            format="%.1f%%",
                            key=widget_key,
                            help=help_text,
                            label_visibility="collapsed",
                        )
                        new_val = round(new_pct / 100.0, 4)

                    elif p["is_int"]:
                        new_val = int(st.number_input(
                            label=label,
                            min_value=int(p["min_val"]),
                            max_value=int(p["max_val"]),
                            value=int(curr_val),
                            step=int(p["step"]),
                            key=widget_key,
                            help=help_text,
                            label_visibility="collapsed",
                        ))
                    else:
                        new_val = float(st.number_input(
                            label=label,
                            min_value=float(p["min_val"]),
                            max_value=float(p["max_val"]),
                            value=float(curr_val),
                            step=float(p["step"]),
                            format="%.2f",
                            key=widget_key,
                            help=help_text,
                            label_visibility="collapsed",
                        ))

                    # Actualizar en sesión si hubo cambio
                    if abs(float(new_val) - float(curr_val)) > 1e-5:
                        set_active_parameter(k, new_val)
                        active_params[k] = new_val
                        st.rerun()

                    st.caption(desc)
                    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    return active_params
