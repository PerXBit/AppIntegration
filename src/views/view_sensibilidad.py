"""
view_sensibilidad.py – Análisis de Sensibilidad Dinámico, Diagrama de Tornado y Umbrales de Decisión.

Permite al usuario evaluar la robustez del plan ante desviaciones en variables críticas:
- Variación dinámica porcentual configurable (±5% a ±35%) sobre los valores activos del catálogo.
- Métricas objetivo seleccionables: VAN (US$), Margen de Contribución, Capacidad Semanal, Nivel de Servicio, Ventas Perdidas.
- Diagrama de Tornado ordenado dinámicamente de mayor a menor impacto en el negocio.
- Clasificación de elasticidad y sensibilidad unitaria.
- Matriz de Sensibilidad Bivariada (Heatmap 2D What-If) entre pares de variables clave.
- Umbrales críticos de decisión operativa para Mariela Santos y el equipo directivo.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np

from src.components.cards import render_alert, render_kpi
from src.components.charts import plot_sensitivity_heatmap, plot_tornado_chart
from src.components.styles import style_tornado_df
from src.model import constants as C
from src.model.data_loader import get_active_parameters_dict, get_default_parameters_dict
from src.model.engine import (
    PlantConfig,
    build_plant_config,
    compute_control_values,
    compute_investment,
    compute_npv,
    simulate_weekly,
)
from src.model.strategies import get_predefined_strategies


def _evaluate_metric(cfg: PlantConfig, metric_name: str) -> float:
    """Evalúa la métrica seleccionada para una configuración dada."""
    inv = compute_investment(cfg)
    df = simulate_weekly(cfg)

    if metric_name == "VAN (Valor Actual Neto en US$)":
        return float(compute_npv(df, inv))
    elif metric_name == "Margen de Contribución Total (US$)":
        return float(df["Margen Bruto"].sum())
    elif metric_name == "Capacidad Semanal de Planta (u/sem)":
        cv = compute_control_values(cfg)
        return float(cv.cap_plant)
    elif metric_name == "Nivel de Servicio Global (%)":
        dem_tot = df["Demanda"].sum()
        atend_tot = df["Atendido"].sum()
        return float((atend_tot / dem_tot * 100) if dem_tot > 0 else 100.0)
    elif metric_name == "Ventas Perdidas Totales (u)":
        return float(df["Ventas Perdidas"].sum())
    return float(compute_npv(df, inv))


def render_view_sensibilidad():
    st.subheader("🌪️ Análisis de Sensibilidad Dinámico y Diagrama de Tornado")
    st.markdown(
        """
        Identifica cuáles supuestos operativos y de mercado tienen el **mayor impacto en el Valor Actual Neto (VAN)**,
        en los márgenes y en el nivel de servicio. Los análisis se recalculan dinámicamente a partir de los
        **valores actualmente activos en la plataforma** (modificados por el usuario o cargados desde Excel).
        """
    )

    strategies = get_predefined_strategies()
    active_params = get_active_parameters_dict()

    # Controles de Configuración del Análisis Dinámico
    with st.expander("⚙️ Controles del Análisis de Sensibilidad Dinámico", expanded=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            strat_options = {
                "E4. Ágil Secuencial (Recomendada)": "E4",
                "E1. Inercia (Statu Quo)": "E1",
                "E2. Cabrera (8 Operadores)": "E2",
                "E3. Expansión Fija (Línea 3)": "E3",
            }
            selected_strat_label = st.selectbox(
                "Estrategia Base para la Sensibilidad",
                options=list(strat_options.keys()),
                index=0,
            )
            base_strategy_id = strat_options[selected_strat_label]
            base_cfg = strategies[base_strategy_id].config_base

        with col_c2:
            metric_options = [
                "VAN (Valor Actual Neto en US$)",
                "Margen de Contribución Total (US$)",
                "Capacidad Semanal de Planta (u/sem)",
                "Nivel de Servicio Global (%)",
                "Ventas Perdidas Totales (u)",
            ]
            selected_metric = st.selectbox("Métrica Objetivo de Evaluación", options=metric_options, index=0)

        with col_c3:
            delta_pct = st.slider("Rango de Variación Dinámica (± %)", min_value=5, max_value=35, value=15, step=5) / 100.0
            st.caption(f"Cada parámetro clave se evaluará a un **-{delta_pct*100:.0f}%** y **+{delta_pct*100:.0f}%** de su valor activo.")

    # ═══════════════════════════════════════════════
    # Ejecución Dinámica del Tornado
    # ═══════════════════════════════════════════════
    with st.spinner(f"Calculando sensibilidad multidimensional (±{delta_pct*100:.0f}%) para {selected_metric}..."):
        val_base = _evaluate_metric(base_cfg, selected_metric)

        defaults = get_default_parameters_dict()

        # Definición de variables a evaluar dinámicamente en función de los parámetros activos
        p_std_base = active_params.get("precio_neto_std", defaults.get("precio_neto_std", C.PRECIO_STD))
        p_pro_base = active_params.get("precio_neto_pro", defaults.get("precio_neto_pro", C.PRECIO_PRO))
        mat_std_base = active_params.get("materiales_std", defaults.get("materiales_std", C.MATERIAL_STD))
        mat_pro_base = active_params.get("materiales_pro", defaults.get("materiales_pro", C.MATERIAL_PRO))
        lote_base = float(base_cfg.tamano_lote)
        setup_base = float(base_cfg.tiempo_cambio)
        pct_pro_base = active_params.get("pct_pro_sem1_26", defaults.get("pct_pro_sem1_26", C.PCT_PRO_SEM1_26))
        falla_std_base = active_params.get("falla_std", defaults.get("falla_std", C.FALLA_STD))
        falla_pro_base = active_params.get("falla_pro", defaults.get("falla_pro", C.FALLA_PRO))
        fijos_base = active_params.get("fijos_planta_semanal", defaults.get("fijos_planta_semanal", C.FIJOS_PLANTA_SEMANAL))
        wacc_base = active_params.get("tasa_descuento_anual", defaults.get("tasa_descuento_anual", C.TASA_DESCUENTO_ANUAL))
        recup_base = active_params.get("tasa_recuperacion_retrabajo", defaults.get("tasa_recuperacion_retrabajo", C.RECUPERACION))

        tests = [
            {
                "var": f"Precios Netos de Venta (STD ${p_std_base:.0f} / PRO ${p_pro_base:.0f})",
                "param_name": "Precios Netos",
                "val_str": f"${p_std_base:.0f} / ${p_pro_base:.0f}",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "precio_neto_std": p_std_base * (1 - delta_pct), "precio_neto_pro": p_pro_base * (1 - delta_pct)}),
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "precio_neto_std": p_std_base * (1 + delta_pct), "precio_neto_pro": p_pro_base * (1 + delta_pct)}),
            },
            {
                "var": f"Costos de Materiales (STD ${mat_std_base:.0f} / PRO ${mat_pro_base:.0f})",
                "param_name": "Costos Materiales",
                "val_str": f"${mat_std_base:.0f} / ${mat_pro_base:.0f}",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "materiales_std": mat_std_base * (1 + delta_pct), "materiales_pro": mat_pro_base * (1 + delta_pct)}), # más costo es peor
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "materiales_std": mat_std_base * (1 - delta_pct), "materiales_pro": mat_pro_base * (1 - delta_pct)}), # menos costo es mejor
            },
            {
                "var": f"Tamaño de Lote Q ({lote_base:.0f} u)",
                "param_name": "Tamaño de Lote",
                "val_str": f"{lote_base:.0f} u",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "tamano_lote": max(15, int(lote_base * (1 - delta_pct)))}),
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "tamano_lote": int(lote_base * (1 + delta_pct))}),
            },
            {
                "var": f"Tiempo de Cambio Setup s ({setup_base:.1f} min)",
                "param_name": "Tiempo Setup",
                "val_str": f"{setup_base:.1f} min",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "tiempo_cambio": setup_base * (1 + delta_pct)}), # más tiempo cambio es peor
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "tiempo_cambio": max(4.0, setup_base * (1 - delta_pct))}), # menos es mejor
            },
            {
                "var": f"Participación Mezcla R1 Pro ({pct_pro_base*100:.0f}%)",
                "param_name": "% Mezcla Pro",
                "val_str": f"{pct_pro_base*100:.0f}%",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "pct_pro_override": min(0.70, pct_pro_base * (1 + delta_pct))}), # pro consume más ciclo
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "pct_pro_override": max(0.05, pct_pro_base * (1 - delta_pct))}),
            },
            {
                "var": f"Tasa de Fallas Eléctricas ({falla_std_base*100:.1f}% / {falla_pro_base*100:.1f}%)",
                "param_name": "Tasa Fallas",
                "val_str": f"{falla_std_base*100:.1f}% / {falla_pro_base*100:.1f}%",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "falla_std": falla_std_base * (1 + delta_pct), "falla_pro": falla_pro_base * (1 + delta_pct)}), # más fallas es peor
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "falla_std": max(0.01, falla_std_base * (1 - delta_pct)), "falla_pro": max(0.01, falla_pro_base * (1 - delta_pct))}),
            },
            {
                "var": f"Costos Fijos Planta Semanales (${fijos_base:,.0f})",
                "param_name": "Costos Fijos",
                "val_str": f"${fijos_base:,.0f}/sem",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "fijos_planta_semanal": fijos_base * (1 + delta_pct)}), # más fijos es peor
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "fijos_planta_semanal": fijos_base * (1 - delta_pct)}),
            },
            {
                "var": f"Tasa de Descuento WACC ({wacc_base*100:.1f}%)",
                "param_name": "Tasa Descuento",
                "val_str": f"{wacc_base*100:.1f}%",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "tasa_descuento_anual": wacc_base * (1 + delta_pct)}), # mayor wacc reduce van
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "tasa_descuento_anual": max(0.04, wacc_base * (1 - delta_pct))}),
            },
            {
                "var": f"Tasa Recuperación Retrabajo ({recup_base*100:.0f}%)",
                "param_name": "Recuperación Retrabajo",
                "val_str": f"{recup_base*100:.0f}%",
                "cfg_low": PlantConfig(**{**base_cfg.__dict__, "tasa_recuperacion_retrabajo": max(0.40, recup_base * (1 - delta_pct))}),
                "cfg_high": PlantConfig(**{**base_cfg.__dict__, "tasa_recuperacion_retrabajo": min(0.98, recup_base * (1 + delta_pct))}),
            },
        ]

        tornado_rows = []
        for t in tests:
            val_low = _evaluate_metric(t["cfg_low"], selected_metric)
            val_high = _evaluate_metric(t["cfg_high"], selected_metric)

            swing_l = val_low - val_base
            swing_h = val_high - val_base
            rango = abs(val_high - val_low)

            # Elasticidad normalizada (% cambio output / % cambio input)
            pct_delta_output = (rango / abs(val_base)) if abs(val_base) > 0.001 else 0.0
            elasticity = pct_delta_output / (2 * delta_pct)

            tornado_rows.append({
                "Variable": t["var"],
                "Parámetro": t["param_name"],
                "Valor Activo": t["val_str"],
                "Valor Base": val_base,
                "Min_Swing": min(swing_l, swing_h),
                "Max_Swing": max(swing_l, swing_h),
                "Rango_Total": rango,
                "Elasticidad": elasticity,
            })

        df_tornado = pd.DataFrame(tornado_rows).sort_values("Rango_Total", ascending=True)

    # ═══════════════════════════════════════════════
    # Diagrama de Tornado Interactivo
    # ═══════════════════════════════════════════════
    st.plotly_chart(plot_tornado_chart(df_tornado), use_container_width=True)

    # Tabla Resumen Clasificada con Formato Semáforo
    st.markdown("### 📊 Clasificación de Sensibilidad por Impacto en el Negocio")
    df_table_tornado = df_tornado.sort_values("Rango_Total", ascending=False)[[
        "Variable", "Valor Activo", "Min_Swing", "Max_Swing", "Rango_Total", "Elasticidad"
    ]]
    st.dataframe(style_tornado_df(df_table_tornado), use_container_width=True, hide_index=True)

    # Insights automáticos de sensibilidad
    top_var = df_table_tornado.iloc[0]
    sec_var = df_table_tornado.iloc[1]
    render_alert(
        f"💡 **Insight Estratégico Clave**: El factor con mayor palanca sobre el desempeño es **{top_var['Variable']}**, "
        f"con un rango de variación de **US$ {top_var['Rango_Total']:,.0f}** (Elasticidad {top_var['Elasticidad']:.2f}). "
        f"En segundo lugar se encuentra **{sec_var['Variable']}** (Rango: US$ {sec_var['Rango_Total']:,.0f}). "
        f"Cualquier negociación de precios o compras de componentes tendrá un impacto financiero órdenes de magnitud mayor que ajustes menores de ingeniería.",
        "info"
    )

    st.markdown("---")

    # ═══════════════════════════════════════════════
    # Matriz de Sensibilidad Bivariada (What-If 2D Heatmap)
    # ═══════════════════════════════════════════════
    st.markdown("### 🗺️ Matriz de Sensibilidad Bivariada (Análisis What-If 2D)")
    st.markdown(
        """
        Evalúa el impacto simultáneo del cruce entre **dos palancas operativas** manteniendo las demás constantes.
        Esto permite modelar compensaciones: por ejemplo, ¿cuánto tiempo de cambio de lote ($s$) se puede tolerar
        si se aumenta el tamaño de lote ($Q$)?
        """
    )

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        eje_x = st.selectbox(
            "Variable Eje Horizontal (X)",
            options=["Tamaño de Lote (Q)", "Tiempo de Cambio (s)", "Participación R1 Pro (%)", "Tasa de Fallas (%)"],
            index=0,
        )
    with col_h2:
        eje_y = st.selectbox(
            "Variable Eje Vertical (Y)",
            options=["Tiempo de Cambio (s)", "Tamaño de Lote (Q)", "Participación R1 Pro (%)", "Tasa Descuento WACC (%)"],
            index=0,
        )

    # Valores para la cuadrícula 5x5
    if eje_x == "Tamaño de Lote (Q)":
        x_vals = [25, 50, 100, 150, 200]
        x_label = "Tamaño de Lote Q (unidades)"
    elif eje_x == "Tiempo de Cambio (s)":
        x_vals = [10.0, 15.0, 20.0, 25.0, 30.0]
        x_label = "Tiempo Setup s (min)"
    elif eje_x == "Participación R1 Pro (%)":
        x_vals = [0.15, 0.25, 0.30, 0.40, 0.50]
        x_label = "% R1 Pro"
    else:
        x_vals = [0.02, 0.04, 0.06, 0.08, 0.10]
        x_label = "Tasa de Fallas Eléctricas"

    if eje_y == "Tiempo de Cambio (s)":
        y_vals = [10.0, 15.0, 20.0, 25.0, 30.0]
        y_label = "Tiempo Setup s (min)"
    elif eje_y == "Tamaño de Lote (Q)":
        y_vals = [25, 50, 100, 150, 200]
        y_label = "Tamaño de Lote Q (unidades)"
    elif eje_y == "Participación R1 Pro (%)":
        y_vals = [0.15, 0.25, 0.30, 0.40, 0.50]
        y_label = "% R1 Pro"
    else:
        y_vals = [0.08, 0.10, 0.12, 0.14, 0.16]
        y_label = "Tasa Descuento WACC"

    z_matrix = []
    for y_v in y_vals:
        row = []
        for x_v in x_vals:
            # Construir config modificada
            overrides = {}
            if "Lote" in eje_x:
                overrides["tamano_lote"] = int(x_v)
            elif "Setup" in eje_x or "Tiempo" in eje_x:
                overrides["tiempo_cambio"] = float(x_v)
            elif "Pro" in eje_x:
                overrides["pct_pro_override"] = float(x_v)
            elif "Fallas" in eje_x:
                overrides["falla_std"] = float(x_v)
                overrides["falla_pro"] = float(x_v) * 1.25

            if "Lote" in eje_y:
                overrides["tamano_lote"] = int(y_v)
            elif "Setup" in eje_y or "Tiempo" in eje_y:
                overrides["tiempo_cambio"] = float(y_v)
            elif "Pro" in eje_y:
                overrides["pct_pro_override"] = float(y_v)
            elif "Descuento" in eje_y:
                overrides["tasa_descuento_anual"] = float(y_v)

            cfg_mod = PlantConfig(**{**base_cfg.__dict__, **overrides})
            val_xy = _evaluate_metric(cfg_mod, selected_metric)
            row.append(val_xy)
        z_matrix.append(row)

    st.plotly_chart(
        plot_sensitivity_heatmap(
            x_vals=[f"{v:.0f}" if isinstance(v, (int, float)) and v >= 10 else f"{v*100:.0f}%" if v < 1 else f"{v}" for v in x_vals],
            y_vals=[f"{v:.0f}" if isinstance(v, (int, float)) and v >= 10 else f"{v*100:.0f}%" if v < 1 else f"{v}" for v in y_vals],
            z_matrix=z_matrix,
            x_label=x_label,
            y_label=y_label,
            title=f"Matriz Bivariada de {selected_metric}: {x_label} vs {y_label}",
        ),
        use_container_width=True,
    )

    st.markdown("---")

    # ═══════════════════════════════════════════════
    # Umbrales Críticos de Decisión Operativa
    # ═══════════════════════════════════════════════
    st.markdown("### 🎯 Umbrales Críticos de Decisión Operativa")

    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown("#### 1. ¿Cuándo conviene pasar de Horas Extra a 2.º Turno?")
        st.markdown(
            """
            - **Costo de Horas Extra en Sábados**:
              - 6,5 h productivas (7 h pagadas) con **50% de recargo**.
              - Costo semanal adicional: ~US$ 1.250 por sábado trabajado.
              - Máximo de 3 sábados/mes aporta **~116 unidades adicionales por semana**.
            - **Costo del Segundo Turno**:
              - 7,5 h productivas al **92% de rendimiento**, con **8% de prima**.
              - Requiere líder de turno ($9/h) y técnico de retrabajo.
              - Costo fijo adicional: US$ 600/semana.
              - Aporta **~494 unidades adicionales por semana**.
            
            > 📌 **Umbral de Indiferencia**:
            > Si la demanda semanal requerida supera la capacidad de 1 turno en más de **120 unidades/semana de forma sostenida por más de 3 semanas**, el **Segundo Turno es más económico por unidad y más viable operativamente** que sobrecargar sábados con horas extra.
            """
        )

    with col_u2:
        st.markdown("#### 2. Tamaño de Lote Mínimo vs Flexibilidad")
        st.markdown(
            """
            - Producir en lotes pequeños ($Q < 50$) mejora la respuesta al cliente pero multiplica las paradas:
              - Si $Q=25$, la penalización es $\\frac{20}{25} = 0,80$ min/u (Capacidad cae a 250 u/línea).
              - Si $Q=100$, la penalización es $\\frac{20}{100} = 0,20$ min/u (Capacidad estándar de 268,5 u/línea).
              - Si $Q=200$, la penalización se reduce a $0,10$ min/u (+1,2% de capacidad extra).
            
            > 📌 **Recomendación para Temporada Alta**:
            > En las semanas 5 a 10 (noviembre y diciembre), elevar temporalmente el tamaño de lote a **$Q = 150-200$ unidades**. Esto ahorra paradas de línea y libera hasta **40 unidades extra por semana** sin requerir horas extra adicionales.
            """
        )
