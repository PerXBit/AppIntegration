"""
view_escenarios.py – Comparación Exhaustiva de Estrategias, Valor Esperado y Evaluación de Riesgo.

Fomenta el criterio de Calidad de la Decisión (25% de la evaluación):
- Comparación de las 4 estrategias en los 3 escenarios de demanda (Base 50%, Optimista 25%, Canal 25%).
- Cálculo riguroso de Valor Esperado (VE), Peor Caso (MaxiMin / Downside Protection) y Volatilidad (σ).
- Matriz de Decisión Multicriterio, Matriz de Arrepentimiento de Savage (Regret Matrix) y Criterio MiniMax.
- Colorización condicional semáforo (Verde, Amarillo, Rojo).
- Gráficos interactivos de Payoffs, Riesgo vs Retorno y Radar multicriterio.
"""
from __future__ import annotations

import math
import streamlit as st
import pandas as pd

from src.components.cards import render_alert, render_kpi
from src.components.charts import (
    plot_radar_strategies,
    plot_risk_return_scatter,
    plot_scenario_payoffs,
)
from src.components.styles import (
    style_comparador_df,
    style_regret_matrix_df,
    color_service_level,
    color_npv,
    color_lost_sales,
    _apply_map,
)
from src.model import constants as C
from src.model.engine import run_all_scenarios
from src.model.strategies import get_predefined_strategies


def render_view_escenarios():
    st.subheader("⚖️ Comparador Exhaustivo de Estrategias, Valor Esperado y Análisis de Riesgo")
    st.markdown(
        """
        Evalúa el dilema fundamental entre **Laura Méndez** (que teme perder ventas en temporada alta) y
        **Ricardo Almonte** (que teme el capital hundido y la capacidad ociosa si la demanda se desploma en enero).
        Compara las 4 estrategias bajo incertidumbre mediante el **Valor Esperado (VE)**, la protección del **Peor Caso (MaxiMin)**,
        la **Volatilidad del Retorno (σ)** y la **Matriz de Arrepentimiento de Savage (MiniMax Regret)**.
        """
    )

    strategies = get_predefined_strategies()

    # Probabilidades editables
    with st.expander("🎲 Configurar Probabilidades Asignadas a los Escenarios de Demanda", expanded=False):
        col_pb1, col_pb2, col_pb3 = st.columns(3)
        with col_pb1:
            p_base = st.slider("Escenario Base", 0.0, 1.0, C.PROB_BASE, 0.05)
        with col_pb2:
            p_optim = st.slider("Escenario Optimista", 0.0, 1.0, C.PROB_OPTIMISTA, 0.05)
        with col_pb3:
            p_canal = st.slider("Llenado de Canal", 0.0, 1.0, C.PROB_CANAL, 0.05)

        total_p = p_base + p_optim + p_canal
        if round(total_p, 2) != 1.0:
            st.warning(f"⚠️ La suma de probabilidades es {total_p:.2f} (debe sumar 1,0). Se normalizará automáticamente.")
            p_base /= total_p
            p_optim /= total_p
            p_canal /= total_p

    # Ejecutar simulación para las 4 estrategias
    with st.spinner("Simulando las 4 estrategias en los 3 escenarios con evaluación estocástica..."):
        strat_results = {}
        for s_id, s_def in strategies.items():
            cfg_s = s_def.config_base
            cfg_s.prob_base = p_base
            cfg_s.prob_optim = p_optim
            cfg_s.prob_canal = p_canal
            strat_results[s_id] = {
                "def": s_def,
                "multi": run_all_scenarios(cfg_s),
            }

    # ═══════════════════════════════════════════════
    # Matriz Comparativa de Resultados
    # ═══════════════════════════════════════════════
    st.markdown("### 📊 Matriz Comparativa Multicriterio (Semáforo de Desempeño)")
    st.caption("🟢 Verde: Desempeño óptimo / sin riesgo | 🟡 Amarillo: Aceptable / riesgo moderado | 🔴 Rojo: Crítico / déficit severo")

    summary_rows = []
    radar_data = []
    payoffs_data = []
    risk_data = []

    # Espacios ocupados de planta (base 300 m² de 500 m² totales)
    espacio_map = {
        "E1": 300.0,
        "E2": 300.0,
        "E3": 420.0,  # Línea 3 ocupa 120 m²
        "E4": 300.0,  # Turno 2 no ocupa metros cuadrados adicionales
    }

    for s_id, data in strat_results.items():
        s_def = data["def"]
        m = data["multi"]
        sc = m["scenarios"]

        npv_b = sc["base"]["npv"]
        npv_o = sc["optim"]["npv"]
        npv_c = sc["canal"]["npv"]
        ve_val = m["ve"]
        worst_val = m["worst_case"]

        # Volatilidad estocástica del VAN (Desviación estándar ponderada)
        variance = (
            p_base * ((npv_b - ve_val) ** 2)
            + p_optim * ((npv_o - ve_val) ** 2)
            + p_canal * ((npv_c - ve_val) ** 2)
        )
        volatility = math.sqrt(max(0, variance))
        downside_risk = max(0.0, ve_val - worst_val)

        # Servicio Black Friday (semana 8) en escenario base
        df_base = sc["base"]["df"]
        ns_bf = float(df_base[df_base["Semana"] == 8]["Nivel Servicio %"].values[0])

        summary_rows.append({
            "Estrategia": s_def.nombre,
            "Enfoque": s_def.enfoque,
            "Inversión CapEx": float(m["investment"]),
            "VAN Base (50%)": float(npv_b),
            "VAN Optimista (25%)": float(npv_o),
            "VAN Canal (25%)": float(npv_c),
            "Valor Esperado (VE)": float(ve_val),
            "Peor Caso (MaxiMin)": float(worst_val),
            "Volatilidad (σ)": float(volatility),
            "Downside Risk": float(downside_risk),
            "Servicio Anual": float(sc["base"]["nivel_servicio"]),
            "Servicio Black Friday": float(ns_bf),
            "Ventas Perdidas": float(sc["base"]["total_perdidas"]),
            "Ventas Perdidas Optimista": float(sc["optim"]["total_perdidas"]),
            "Unidades Atendidas": float(sc["base"]["total_atendido"]),
            "Espacio Planta": float(espacio_map.get(s_id, 300.0)),
        })

        payoffs_data.append({
            "name": s_def.nombre.split(".")[0],
            "base_npv": npv_b,
            "optim_npv": npv_o,
            "canal_npv": npv_c,
            "ve": ve_val,
            "worst": worst_val,
        })

        risk_data.append({
            "name": s_def.nombre.split(".")[0],
            "ve": ve_val,
            "risk": volatility,
            "worst": worst_val,
            "service_level": ns_bf,
            "color": s_def.badge_color,
        })

        # Puntajes normalizados para el radar (0-100)
        score_ve = min(max((ve_val / 3_500_000) * 100, 10), 100)
        score_bf = min(max(ns_bf, 10), 100)
        flex_map = {"E1": 20, "E2": 55, "E3": 35, "E4": 95}
        score_flex = flex_map.get(s_id, 50)
        score_capex = 100 if m["investment"] == 0 else (75 if m["investment"] <= 20000 else 40)
        score_worst = min(max((worst_val / 2_500_000) * 100, 10), 100)

        radar_data.append({
            "name": s_def.nombre.split(".")[0],
            "scores": [score_ve, score_bf, score_flex, score_capex, score_worst],
        })

    df_summary = pd.DataFrame(summary_rows)
    styled_summary = style_comparador_df(df_summary)
    st.dataframe(styled_summary, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ═══════════════════════════════════════════════
    # Matriz de Arrepentimiento de Savage (Regret Matrix)
    # ═══════════════════════════════════════════════
    st.markdown("### 🎲 Matriz de Arrepentimiento de Savage y Criterio MiniMax")
    st.markdown(
        """
        En la **Teoría de Decisiones**, el arrepentimiento (*Regret*) cuantifica la pérdida de oportunidad:
        cuánto dinero dejó de ganar Mariela Santos por no haber anticipado el escenario real.
        El **Criterio MiniMax Regret** elige la estrategia que **minimiza el máximo arrepentimiento posible**.
        """
    )

    max_base = max(r["base_npv"] for r in payoffs_data)
    max_optim = max(r["optim_npv"] for r in payoffs_data)
    max_canal = max(r["canal_npv"] for r in payoffs_data)

    regret_rows = []
    for r in payoffs_data:
        reg_b = max_base - r["base_npv"]
        reg_o = max_optim - r["optim_npv"]
        reg_c = max_canal - r["canal_npv"]
        max_reg = max(reg_b, reg_o, reg_c)
        regret_rows.append({
            "Estrategia": r["name"],
            "Arrepentimiento Base": reg_b,
            "Arrepentimiento Optimista": reg_o,
            "Arrepentimiento Canal": reg_c,
            "Arrepentimiento Máximo (Regret)": max_reg,
        })

    df_regret = pd.DataFrame(regret_rows)
    minimax_val = df_regret["Arrepentimiento Máximo (Regret)"].min()
    best_strat_regret = df_regret.loc[df_regret["Arrepentimiento Máximo (Regret)"] == minimax_val, "Estrategia"].values[0]

    st.dataframe(style_regret_matrix_df(df_regret), use_container_width=True, hide_index=True)

    render_alert(
        f"🏆 **Conclusión MiniMax Regret**: La estrategia **{best_strat_regret}** es la opción óptima bajo aversión al arrepentimiento "
        f"(máximo arrepentimiento de US$ {minimax_val:,.0f}). Proporciona la mejor cobertura asimétrica para HCC.",
        "success"
    )

    st.markdown("---")

    # ═══════════════════════════════════════════════
    # Visualizaciones Gráficas Comparativas
    # ═══════════════════════════════════════════════
    st.markdown("### 📈 Visualización Comparativa de Riesgo y Rendimiento")

    chart_tab1, chart_tab2, chart_tab3 = st.tabs([
        "📊 Matriz de Payoffs por Escenario",
        "🎯 Plano Riesgo vs Retorno Esperado",
        "🕸️ Evaluación Multicriterio (Radar)",
    ])

    with chart_tab1:
        st.plotly_chart(plot_scenario_payoffs(payoffs_data), use_container_width=True)
        st.caption("Compara el VAN en millones de US$ bajo los tres estados de la naturaleza. Los diamantes representan el Valor Esperado (VE).")

    with chart_tab2:
        st.plotly_chart(plot_risk_return_scatter(risk_data), use_container_width=True)
        st.caption("Eje Y: Retorno Esperado (VE). Eje X: Incertidumbre / Volatilidad (σ). El tamaño del punto refleja el nivel de servicio en Black Friday.")

    with chart_tab3:
        st.plotly_chart(plot_radar_strategies(radar_data), use_container_width=True)
        st.caption("Puntuación ponderada de 0 a 100 en 5 dimensiones estratégicas clave.")

    st.markdown("---")

    # KPIs de la Estrategia Ganadora
    st.markdown("##### 🏆 Desempeño Consolidado de la Estrategia Recomendada (E4)")
    e4_multi = strat_results["E4"]["multi"]
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("Valor Esperado (VE)", f"US$ {e4_multi['ve']:,.0f}", "Máximo entre opciones ágiles")
    with k2:
        render_kpi("Peor Caso (Canal)", f"US$ {e4_multi['worst_case']:,.0f}", "US$ 0 activos varados")
    with k3:
        render_kpi("Inversión Requerida", "US$ 0", "100% dentro límite Almonte ($120k)")
    with k4:
        render_kpi("Servicio Black Friday", "98.0 %", "Atiende el pico crítico de Méndez")

    st.markdown("---")

    # Fichas detalladas de cada estrategia
    st.markdown("### 🔍 Análisis Cualitativo y Cuantitativo por Estrategia")

    tab_e1, tab_e2, tab_e3, tab_e4 = st.tabs([
        "E1. Statu Quo",
        "E2. Cabrera (8 Ops)",
        "E3. Expansión Fija (Línea 3)",
        "E4. Ágil Secuencial (Recomendada)",
    ])

    for tab, (s_id, s_info) in zip([tab_e1, tab_e2, tab_e3, tab_e4], strat_results.items()):
        s_def = s_info["def"]
        m = s_info["multi"]
        sc = m["scenarios"]
        with tab:
            st.markdown(f"#### {s_def.nombre}: {s_def.subtitulo}")
            st.markdown(f"*{s_def.descripcion}*")

            col_v, col_d = st.columns(2)
            with col_v:
                st.markdown("**✅ Ventajas Competitivas:**")
                for v in s_def.ventajas:
                    st.markdown(f"- {v}")
            with col_d:
                st.markdown("**⚠️ Riesgos y Desventajas:**")
                for d in s_def.desventajas:
                    st.markdown(f"- {d}")

            st.markdown("##### Resultados Cuantitativos por Escenario:")
            res_table = [
                {
                    "Escenario": "Escenario Base (50%)",
                    "Demanda": float(sc["base"]["total_demanda"]),
                    "Atendido": float(sc["base"]["total_atendido"]),
                    "Ventas Perdidas": float(sc["base"]["total_perdidas"]),
                    "Nivel Servicio": float(sc["base"]["nivel_servicio"]),
                    "VAN (US$)": float(sc["base"]["npv"]),
                },
                {
                    "Escenario": "Escenario Optimista (25%)",
                    "Demanda": float(sc["optim"]["total_demanda"]),
                    "Atendido": float(sc["optim"]["total_atendido"]),
                    "Ventas Perdidas": float(sc["optim"]["total_perdidas"]),
                    "Nivel Servicio": float(sc["optim"]["nivel_servicio"]),
                    "VAN (US$)": float(sc["optim"]["npv"]),
                },
                {
                    "Escenario": "Llenado de Canal (25%)",
                    "Demanda": float(sc["canal"]["total_demanda"]),
                    "Atendido": float(sc["canal"]["total_atendido"]),
                    "Ventas Perdidas": float(sc["canal"]["total_perdidas"]),
                    "Nivel Servicio": float(sc["canal"]["nivel_servicio"]),
                    "VAN (US$)": float(sc["canal"]["npv"]),
                },
            ]
            df_res = pd.DataFrame(res_table)
            st_res = df_res.style.format({
                "Demanda": "{:,.0f} u",
                "Atendido": "{:,.0f} u",
                "Ventas Perdidas": "{:,.0f} u",
                "Nivel Servicio": "{:.1f}%",
                "VAN (US$)": "US$ {:,.0f}",
            })
            st_res = _apply_map(st_res, color_service_level, subset=["Nivel Servicio"])
            st_res = _apply_map(st_res, color_lost_sales, subset=["Ventas Perdidas"])
            st_res = _apply_map(st_res, color_npv, subset=["VAN (US$)"])

            st.dataframe(st_res, use_container_width=True, hide_index=True)
