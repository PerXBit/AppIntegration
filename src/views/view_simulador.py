"""
view_simulador.py – Simulador Interactivo Semana a Semana (52 Semanas).

Permite al usuario mover todas las palancas operativas en tiempo real, visualizar
las curvas de demanda vs capacidad, monitorear inventarios y restricciones de espacio/presupuesto,
consultar los 5 Grupos de Indicadores Normativos (Capacidad, Flujo, Servicio, Economía y Riesgo),
y exportar la simulación completa en PDF, Excel y CSV.
"""
from __future__ import annotations

import io
import streamlit as st
import pandas as pd

from src.components.cards import render_alert, render_kpi
from src.components.charts import plot_demand_vs_capacity, plot_inventory_and_backlog
from src.components.parameter_editor import render_parameter_editor
from src.components.styles import style_utilization_df, style_weekly_df
from src.model import constants as C
from src.model.case_solver import (
    solve_q1_capacidad_y_cuello,
    solve_q2_informe_cabrera,
    solve_q3_dispositivo_puerta,
    solve_q4_combinacion_optima_presupuesto,
    solve_q5_maximizacion_ve_y_peor_caso,
    solve_q6_recomendacion_mariela_santos,
)
from src.model.data_loader import get_active_parameters_dict
from src.model.engine import (
    PlantConfig,
    build_plant_config,
    compute_control_values,
    compute_investment,
    compute_npv,
    compute_station_utilization,
    get_station_times,
    run_all_scenarios,
    simulate_weekly,
)
from src.reports.pdf_generator import generate_simulation_pdf


def render_view_simulador():
    st.subheader("⚡ Simulador Dinámico Semana a Semana (Horizonte 52 Semanas)")
    st.markdown(
        """
        Experimenta con las **siete palancas de capacidad** identificadas por Mariela Santos.
        Observa en tiempo real el cumplimiento del programa en Black Friday, el nivel de servicio y el impacto económico.
        """
    )

    # ═══════════════════════════════════════════════
    # Palancas de Entrada (Sidebar o Paneles Expandibles)
    # ═══════════════════════════════════════════════
    with st.expander("🎛️ Panel de Palancas de Simulación", expanded=True):
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            st.markdown("##### 📈 Demanda y Escenario")
            escenario = st.selectbox(
                "Escenario de Demanda",
                ["base", "optim", "canal"],
                format_func=lambda x: "Base (50% prob)" if x == "base" else ("Optimista (25% prob)" if x == "optim" else "Llenado de Canal (25% prob)"),
                index=0,
            )
            prob_base = st.number_input("Prob. Base", 0.0, 1.0, C.PROB_BASE, 0.05)
            prob_optim = st.number_input("Prob. Optimista", 0.0, 1.0, C.PROB_OPTIMISTA, 0.05)
            prob_canal = st.number_input("Prob. Canal", 0.0, 1.0, C.PROB_CANAL, 0.05)

        with col_p2:
            st.markdown("##### 🏭 Líneas y Operadores")
            num_lineas = st.selectbox("Número de Líneas Inicial", [2, 3], index=0)
            ops_por_linea = st.selectbox("Operadores por Línea", [6, 8], index=0)
            agregar_l3 = st.checkbox("Instalar 3.ª Línea durante el año", value=(num_lineas == 3))
            if agregar_l3 and num_lineas == 2:
                semana_linea3 = int(st.number_input(
                    "Semana entrada Línea 3",
                    min_value=1, max_value=52, value=9,
                    help="Plazo de entrega: 8 semanas. Si se ordena en sem 1, llega en sem 9.",
                ))
            elif num_lineas == 3:
                semana_linea3 = 1
            else:
                semana_linea3 = 99
            subc_puerta = st.checkbox("Subcontratar Puerta (O6)", value=False)
            disp_puerta = st.checkbox("Dispositivo Puerta (O5)", value=False)

        with col_p3:
            st.markdown("##### ⏱️ Turnos y Sábados")
            num_turnos = st.selectbox("Turnos a Activar", [1, 2, 3], index=1)
            if num_turnos >= 2:
                semana_t2 = int(st.number_input("Semana Inicio 2.º Turno", min_value=1, max_value=52, value=3))
            else:
                semana_t2 = 99

            if num_turnos >= 3:
                semana_t3 = int(st.number_input("Semana Inicio 3.er Turno", min_value=1, max_value=52, value=8))
            else:
                semana_t3 = 99

            sabados_mes = st.slider("Sábados Horas Extra / Mes", 0, 3, 2, help="Máximo 3 al mes; 6,5 h productivas")

        with col_p4:
            st.markdown("##### 📦 Lotes y Células")
            active_params = get_active_parameters_dict()
            default_lote = int(active_params.get("lote_produccion_defecto", C.LOTE_DEFAULT))
            default_cambio = float(active_params.get("tiempo_cambio_lote", C.CAMBIO_VARIANTE_DEFAULT))

            tam_lote = st.slider("Tamaño de Lote (Q)", 25, 400, default_lote, 25)
            t_cambio = st.slider("Tiempo Cambio (min)", 5, 40, int(default_cambio), 5)
            num_celulas = st.slider("Células de Trabajo (O4)", 0, 6, 0, 1)
            if num_celulas > 0:
                semana_celulas = int(st.number_input("Semana Entrada Células", min_value=1, max_value=52, value=5))
            else:
                semana_celulas = 99
            penaliz_cel = st.slider("Penalización Polivalencia (%)", 0, 20, 8, 2) / 100.0

    # Panel Expandible de Edición Rápida de Parámetros del Modelo
    with st.expander("⚙️ Modificar Parámetros Económicos y Técnicos del Modelo (22 Parámetros)", expanded=False):
        render_parameter_editor(
            key_prefix="sim",
            title="Ajuste Rápido de Parámetros Económicos y Técnicos",
            show_header=False,
        )

    # Construir objeto de configuración integrando parámetros activos
    cfg = build_plant_config(
        num_lineas=num_lineas,
        ops_por_linea=ops_por_linea,
        semana_linea3=semana_linea3,
        num_turnos=num_turnos,
        semana_turno2=semana_t2,
        semana_turno3=semana_t3,
        sabados_mes=sabados_mes,
        num_celulas=num_celulas,
        semana_celulas=semana_celulas,
        penalizacion_polivalencia=penaliz_cel,
        dispositivo_puerta=disp_puerta,
        semana_dispositivo=10 if disp_puerta else 99,
        subcontratar_puerta=subc_puerta,
        semana_subcontratacion=4 if subc_puerta else 99,
        tamano_lote=tam_lote,
        tiempo_cambio=t_cambio,
        escenario=escenario,
        prob_base=prob_base,
        prob_optim=prob_optim,
        prob_canal=prob_canal,
    )

    # ═══════════════════════════════════════════════
    # Ejecución de la Simulación Reactiva
    # ═══════════════════════════════════════════════
    with st.spinner("Simulando 52 semanas..."):
        df_sim = simulate_weekly(cfg)
        ctrl_vals = compute_control_values(cfg)
        inversion = compute_investment(cfg)
        npv = compute_npv(df_sim, inversion)
        multi = run_all_scenarios(cfg)

    # ═══════════════════════════════════════════════
    # Monitoreo de Restricciones del Caso
    # ═══════════════════════════════════════════════
    espacio_usado = 0
    lineas_max = 3 if semana_linea3 <= 52 or num_lineas == 3 else 2
    espacio_usado += lineas_max * C.ESPACIO_LINEA
    espacio_usado += num_celulas * C.ESPACIO_CELULA
    espacio_total_disp = C.SUPERFICIE_ACTUAL  # 420 m²
    espacio_libre = espacio_total_disp - espacio_usado

    col_alert1, col_alert2 = st.columns(2)
    with col_alert1:
        if inversion > cfg.limite_inversion_fiscal:
            render_alert(
                "🚨 ALERTA: PRESUPUESTO DE INVERSIÓN EXCEDIDO",
                f"La inversión total es de <b>US$ {inversion:,.0f}</b>, superando el límite de <b>US$ {cfg.limite_inversion_fiscal:,.0f}</b> sin aprobación del consejo.",
                "danger",
            )
        else:
            render_alert(
                "✅ PRESUPUESTO DE INVERSIÓN CUMPLIDO",
                f"Inversión de capital: <b>US$ {inversion:,.0f}</b> / US$ {cfg.limite_inversion_fiscal:,.0f} disponibles (Holgura: US$ {cfg.limite_inversion_fiscal - inversion:,.0f}).",
                "success",
            )

    with col_alert2:
        if espacio_libre < 0:
            render_alert(
                "🚨 ALERTA: ESPACIO FÍSICO EXCEDIDO",
                f"La configuración requiere {espacio_usado} m² (Déficit de {-espacio_libre} m²). Se requiere activar la ampliación de 200 m² (US$ 6/m²-sem).",
                "danger",
            )
        else:
            render_alert(
                "✅ ESPACIO FÍSICO DENTRO DE LÍMITES",
                f"Espacio en uso: {espacio_usado} m² de 420 m² totales ({espacio_libre} m² libres para almacén de producto terminado).",
                "info",
            )

    # ═══════════════════════════════════════════════
    # CUADRO DE MANDO INTEGRAL: 5 GRUPOS DE INDICADORES (Págs 8-9)
    # ═══════════════════════════════════════════════
    st.markdown("### 📋 Cuadro de Mando Integral: Indicadores Normativos del Caso")

    tot_dem = df_sim["Demanda"].sum()
    tot_prod = df_sim["Producción"].sum()
    tot_atend = df_sim["Atendido"].sum()
    tot_perd = df_sim["Ventas Perdidas"].sum()
    ns_global = (tot_atend / tot_dem * 100) if tot_dem > 0 else 100.0

    row_sem8 = df_sim[df_sim["Semana"] == 8].iloc[0]
    ns_sem8 = row_sem8["Nivel Servicio %"]

    stations_active = get_station_times(cfg.ops_por_linea, cfg.dispositivo_puerta, cfg.subcontratar_puerta)
    pct_pro_val = cfg.pct_pro_override if cfg.pct_pro_override is not None else C.PCT_PRO_SEM1_26
    util_active = compute_station_utilization(stations_active, pct_pro_val)

    tab_ind_cap, tab_ind_flujo, tab_ind_serv, tab_ind_econ, tab_ind_riesgo = st.tabs([
        "🏭 1. Capacidad",
        "🔄 2. Flujo",
        "📦 3. Servicio",
        "💰 4. Economía",
        "⚖️ 5. Riesgo",
    ])

    with tab_ind_cap:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi("Ciclo Estándar", f"{ctrl_vals.ct_std:.2f} min", f"Cuello: {ctrl_vals.bottleneck_std[:12]}")
        with c2:
            render_kpi("Ciclo Pro", f"{ctrl_vals.ct_pro:.2f} min", f"Cuello: {ctrl_vals.bottleneck_pro[:12]}")
        with c3:
            render_kpi("Capacidad Bruta Sem.", f"{ctrl_vals.cap_plant:.1f} u/sem", f"Por línea: {ctrl_vals.cap_line:.1f} u")
        with c4:
            render_kpi("Unidades Buenas Sem.", f"{ctrl_vals.good_units:.1f} u/sem", f"Retrabajo: {ctrl_vals.rework_units:.1f} u")
        with c5:
            render_kpi("Takt Time Black Friday", f"{ctrl_vals.takt_wk8:.2f} min", f"Demanda: 1.900 u/sem")

        st.caption("🔍 **Utilización por estación:** Las estaciones al 100% representan los cuellos de botella de la línea.")
        df_ut_mini = pd.DataFrame(util_active)[["operacion", "t_ponderado", "util_ponderada_pct", "tiempo_ocio_ponderado", "estado"]]
        df_ut_mini.columns = ["Estación / Puesto", "Tiempo Mezcla (min)", "Utilización (%)", "Tiempo Ocio (min/u)", "Estado"]
        st.dataframe(style_utilization_df(df_ut_mini, "Utilización (%)"), use_container_width=True, hide_index=True)

    with tab_ind_flujo:
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            render_kpi("Eficiencia del Balance", f"{ctrl_vals.eff_std*100:.1f}%", f"Pro: {ctrl_vals.eff_pro*100:.1f}%")
        with f2:
            render_kpi("Inventario en Proceso", "46 u / línea", "WIP Observado")
        with f3:
            render_kpi("Tiempo de Flujo (Little)", f"{ctrl_vals.flow_time_hr:.2f} horas", "T_flujo = WIP / TH")
        with f4:
            render_kpi("Inventario Final PT", f"{df_sim['Inv. Final'].mean():.0f} u (prom)", f"Máx año: {df_sim['Inv. Final'].max():.0f} u / 1.500 u")

    with tab_ind_serv:
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            render_kpi("Demanda Total Atendida", f"{tot_atend:,.0f} u", f"De {tot_dem:,.0f} u demandadas")
        with s2:
            render_kpi("Pedidos Pendientes (Backlog)", f"{df_sim['Backlog'].mean():.0f} u (prom)", f"Pico: {df_sim['Backlog'].max():.0f} u")
        with s3:
            render_kpi("Ventas Perdidas Totales", f"{tot_perd:,.0f} u", "Demanda irrecuperable", delta_color="inverse" if tot_perd > 3000 else "normal")
        with s4:
            render_kpi("Nivel de Servicio Global", f"{ns_global:.1f} %", f"Black Friday: {ns_sem8:.0f}%", delta_color="normal" if ns_global >= 90 else "inverse")

    with tab_ind_econ:
        e1, e2, e3, e4, e5 = st.columns(5)
        with e1:
            render_kpi("Coste MO por Unidad Buena", f"US$ {ctrl_vals.labor_per_good:.2f}", "Incluye cargas y supervisor")
        with e2:
            render_kpi("Coste MO Semanal", f"US$ {ctrl_vals.labor_weekly:,.0f}", "Base 1er turno")
        with e3:
            render_kpi("Margen Contribución Total", f"US$ {df_sim['Margen Bruto'].sum():,.0f}", f"Margen unitario: US$ {ctrl_vals.margin_avg:.2f}")
        with e4:
            render_kpi("Inversión Acumulada", f"US$ {inversion:,.0f}", f"Tope: US$ {C.LIMITE_INVERSION:,.0f}")
        with e5:
            render_kpi("Valor Actual Neto (VAN)", f"US$ {npv:,.0f}", "Tasa anual 12% (52 sem)", delta_color="normal" if npv > 0 else "inverse")

    with tab_ind_riesgo:
        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            render_kpi("VAN Base (50%)", f"US$ {multi['scenarios']['base']['npv']:,.0f}", "Escenario Base")
        with r2:
            render_kpi("VAN Optimista (25%)", f"US$ {multi['scenarios']['optim']['npv']:,.0f}", "+20% Demanda")
        with r3:
            render_kpi("VAN Canal (25%)", f"US$ {multi['scenarios']['canal']['npv']:,.0f}", "Caída en enero")
        with r4:
            render_kpi("Valor Esperado (VE)", f"US$ {multi['ve']:,.0f}", "Ponderado por probabilidades")
        with r5:
            render_kpi("Peor Caso (MaxiMin)", f"US$ {multi['worst_case']:,.0f}", "Protección de cola baja")

    st.markdown("---")

    # ═══════════════════════════════════════════════
    # Visualizaciones Interactivas
    # ═══════════════════════════════════════════════
    st.plotly_chart(plot_demand_vs_capacity(df_sim), use_container_width=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(plot_inventory_and_backlog(df_sim), use_container_width=True)
    with col_g2:
        df_cf = df_sim[["Semana", "Margen Bruto", "Flujo Descontado", "Costo MO"]]
        st.markdown("##### 💵 Desglose Financiero Semanal")
        st.dataframe(
            df_cf.style.format({
                "Margen Bruto": "US$ {:,.0f}",
                "Flujo Descontado": "US$ {:,.0f}",
                "Costo MO": "US$ {:,.0f}",
            }),
            height=280,
            use_container_width=True,
            hide_index=True,
        )

    # ═══════════════════════════════════════════════
    # Centro de Exportación de Resultados
    # ═══════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 📥 Centro de Exportación de Resultados de Simulación")

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        pdf_bytes = generate_simulation_pdf(
            cfg=cfg,
            df_weekly=df_sim,
            control_vals=ctrl_vals,
            multi_scenarios=multi,
            strategy_name=f"Configuración Personalizada ({escenario.upper()})",
        )
        st.download_button(
            label="📄 Exportar Simulación Completa en PDF",
            data=pdf_bytes,
            file_name=f"Informe_Simulacion_Resguarda_{escenario.upper()}.pdf",
            mime="application/pdf",
            help="Genera un informe ejecutivo de 5 páginas con portada, diagnóstico, matriz de decisión y las 52 semanas.",
            use_container_width=True,
        )

    with col_exp2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df_sim.to_excel(writer, sheet_name="Resultados_52_Sem", index=False)
            resumen_data = {
                "Métrica": ["Demanda Total", "Demanda Atendida", "Ventas Perdidas", "Nivel Servicio %", "Inversión CapEx", "VAN a 52 Semanas", "Valor Esperado VE"],
                "Valor": [tot_dem, tot_atend, tot_perd, f"{ns_global:.1f}%", inversion, npv, multi["ve"]],
            }
            pd.DataFrame(resumen_data).to_excel(writer, sheet_name="Resumen_KPIs", index=False)

        st.download_button(
            label="📊 Exportar Datos en Excel (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name=f"Resultados_Simulacion_Resguarda_{escenario}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Libro con la tabla semana a semana y hoja de KPIs consolidados.",
            use_container_width=True,
        )

    with col_exp3:
        csv_bytes = df_sim.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📋 Exportar CSV de las 52 Semanas",
            data=csv_bytes,
            file_name=f"simulacion_resguarda_52sem_{escenario}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Tabla detallada navegable
    with st.expander("🔍 Ver Tabla Completa de las 52 Semanas de Simulación (Semáforo de Servicio y Backlog)", expanded=False):
        st.dataframe(
            style_weekly_df(df_sim),
            use_container_width=True,
            hide_index=True,
        )
