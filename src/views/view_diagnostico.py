"""
view_diagnostico.py – Diagnóstico de Capacidad, Balance de Línea, Utilización y Cuellos de Botella.

Responde las Preguntas 1, 2 y 3 del caso Resguarda de forma 100% DINÁMICA:
1. Capacidad real y ubicación del cuello de botella por variante y mezcla.
2. Desmitificación matemática del informe de Julio Cabrera (8 operadores).
3. Análisis de desplazamiento del cuello de botella y efecto real del dispositivo para la puerta.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.components.cards import render_alert, render_kpi
from src.components.charts import plot_station_bottlenecks, plot_station_utilization
from src.components.styles import _apply_map, color_utilization
from src.model import constants as C
from src.model.case_solver import (
    solve_q1_capacidad_y_cuello,
    solve_q2_informe_cabrera,
    solve_q3_dispositivo_puerta,
)
from src.model.engine import (
    PlantConfig,
    build_plant_config,
    compute_station_utilization,
    get_station_times,
    productive_minutes,
    takt_time,
)


def render_view_diagnostico():
    st.subheader("🔬 Diagnóstico de Planta, Balance de Línea y Cuellos de Botella")
    st.markdown(
        """
        Analiza en profundidad la dinámica de ensamble de Resguarda. Identifica cómo el **cuello de botella cambia
        dinámicamente** entre la versión Estándar y Pro, examina la **utilización porcentual por estación**
        y evalúa con datos en vivo el impacto real de las propuestas de ingeniería.
        """
    )

    # Controles interactivos de diagnóstico
    with st.expander("⚙️ Palancas de Configuración del Balance de Línea", expanded=True):
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            cfg_line = st.selectbox(
                "Diseño de Línea",
                ["Línea Actual (6 operadores)", "Propuesta Cabrera (8 operadores)", "Con Subcontratación de Puerta (5 ops)"],
                index=0,
            )
            ops = 8 if "8" in cfg_line else (5 if "Subcontratación" in cfg_line else 6)
            subc = "Subcontratación" in cfg_line

        with col_c2:
            disp_puerta = st.checkbox(
                "Dispositivo Puerta (O5)",
                value=False,
                help="Dispositivo semiautomático de $22.000 que reduce tiempos en E2 y E3 (o L3 y L5).",
            )
            pct_pro = st.slider(
                "Participación R1 Pro (%)",
                min_value=10, max_value=60, value=30, step=5,
                help="El caso fija 30% en sem 1-26 y 35% en sem 27-52.",
            ) / 100.0

        with col_c3:
            tam_lote = st.slider(
                "Tamaño de Lote (Q)",
                min_value=25, max_value=400, value=100, step=25,
                help="Unidades consecutivas de la misma variante antes del cambio.",
            )

        with col_c4:
            t_cambio = st.slider(
                "Tiempo de Cambio (min)",
                min_value=5, max_value=40, value=20, step=5,
                help="Minutos de parada de línea por cambio de plantillas y programa.",
            )

    # Configuración activa
    cfg = build_plant_config(
        num_lineas=2,
        ops_por_linea=ops,
        dispositivo_puerta=disp_puerta,
        subcontratar_puerta=subc,
        pct_pro_override=pct_pro,
        tamano_lote=tam_lote,
        tiempo_cambio=t_cambio,
    )

    # Ejecución de resolvedores dinámicos
    q1 = solve_q1_capacidad_y_cuello(cfg)
    q2 = solve_q2_informe_cabrera(cfg)
    q3 = solve_q3_dispositivo_puerta(cfg)

    # Fila de métricas clave dinámicas (Grupo: Capacidad)
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    with col_m1:
        render_kpi("Ciclo Estándar", f"{q1['ct_std']:.2f} min", f"Cuello: {q1['bottleneck_std'][:15]}")
    with col_m2:
        render_kpi("Ciclo Pro", f"{q1['ct_pro']:.2f} min", f"Cuello: {q1['bottleneck_pro'][:15]}")
    with col_m3:
        render_kpi("Ciclo Medio Efectivo", f"{q1['c_eff']:.2f} min", f"Setup: +{q1['setup_loss_min']:.2f} min/u")
    with col_m4:
        render_kpi("Capacidad Planta (1T)", f"{q1['cap_plant']:.1f} u/sem", f"Buenas: {q1['good_units']:.1f} u")
    with col_m5:
        render_kpi("Takt Time Black Friday", f"{q1['takt_bf_line']:.2f} min", f"Déficit: {q1['gap_bf_units']:.0f} u", delta_color="inverse")

    st.markdown("---")

    # Gráficos de Balance de Línea y Utilización
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(
            plot_station_bottlenecks(
                get_station_times(ops, disp_puerta, subc),
                takt_time_val=q1["takt_bf_line"],
                title=f"Carga por Estación vs Takt Time (Línea de {ops} Ops)",
            ),
            use_container_width=True,
        )

    with col_g2:
        st.plotly_chart(
            plot_station_utilization(
                q1["util_data"],
                title="Utilización por Estación respecto al Cuello (%)",
            ),
            use_container_width=True,
        )

    # Tabla de Utilización por Estación
    st.markdown("##### 📊 Tabla de Balanceo y Utilización por Estación")
    df_util = pd.DataFrame(q1["util_data"])[["operacion", "t_std", "t_pro", "t_ponderado", "util_std_pct", "util_pro_pct", "util_ponderada_pct", "tiempo_ocio_ponderado", "estado"]]
    df_util.columns = ["Operación / Puesto", "T. Estándar (min)", "T. Pro (min)", "T. Mezcla (min)", "Util. Estándar", "Util. Pro", "Util. Mezcla", "Ocio (min/u)", "Estado de Carga"]
    styler_util = df_util.style.format({
        "T. Estándar (min)": "{:.2f}",
        "T. Pro (min)": "{:.2f}",
        "T. Mezcla (min)": "{:.2f}",
        "Util. Estándar": "{:.1f}%",
        "Util. Pro": "{:.1f}%",
        "Util. Mezcla": "{:.1f}%",
        "Ocio (min/u)": "{:.2f}",
    })
    for col in ["Util. Estándar", "Util. Pro", "Util. Mezcla"]:
        styler_util = _apply_map(styler_util, color_utilization, subset=[col])
    st.dataframe(
        styler_util,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Bloque de Análisis Pedagógico y Respuestas Dinámicas al Caso
    st.markdown("### 📋 Respuestas Dinámicas a las Preguntas del Caso")

    tab_q1, tab_q2, tab_q3, tab_little = st.tabs([
        "1. Capacidad Real y Cuello de Botella Dinámico",
        "2. Evaluación del Informe de Julio Cabrera (8 Ops)",
        "3. Efecto Real del Dispositivo de Puerta (O5)",
        "4. Dinámica de Flujo y Ley de Little",
    ])

    with tab_q1:
        st.markdown(
            f"""
            #### ¿Cuál es la capacidad real de la planta hoy? ¿Dónde está el cuello de botella para cada variante y para la mezcla?
            *(Calculado en tiempo real con % Pro = {q1['pct_pro']}%, Lote Q = {cfg.tamano_lote} u, Cambio s = {cfg.tiempo_cambio} min)*

            - **Para R1 Estándar**:
              - Contenido de trabajo: **{q1['wc_std']} minutos**.
              - Estación cuello de botella: **{q1['bottleneck_std']}** con **{q1['ct_std']:.2f} minutos**.
            - **Para R1 Pro**:
              - Contenido de trabajo: **{q1['wc_pro']} minutos**.
              - Estación cuello de botella: **{q1['bottleneck_pro']}** con **{q1['ct_pro']:.2f} minutos** (la instalación de la segunda cámara y módulo celular desplaza la cola).
            - **Con la mezcla actual ({q1['pct_pro']}% Pro)**:
              - Ciclo ponderado puro: **{q1['c_bar']:.2f} minutos/unidad**.
              - Penalización por cambio de lote ($s/Q = {cfg.tiempo_cambio}/{cfg.tamano_lote}$): **+{q1['setup_loss_min']:.2f} min/u**.
              - **Tiempo de ciclo medio efectivo ($c_{{\\text{{eff}}}}$)**: **{q1['c_eff']:.2f} minutos/unidad**.
            - **Capacidad resultante de la planta (2 líneas, 1 turno)**:
              - Capacidad bruta semanal: **{q1['cap_plant']:.1f} unidades/semana** ({q1['cap_line']:.1f} u/línea).
              - Tasa neta de desecho: **{q1['scrap_rate_pct']:.2f}%** (tras recuperar el 80% en retrabajo).
              - **Unidades buenas por semana**: **{q1['good_units']:.1f} unidades/semana** ({q1['rework_units']:.1f} enviadas a retrabajo).
            - **Brecha frente al Takt Time de Black Friday**:
              - Demanda pico semana 8: **{q1['demand_bf']:,.0f} unidades** ($950$ u/línea).
              - Takt time requerido: **{q1['takt_bf_line']:.2f} minutos/unidad** (frente a un ciclo de {q1['c_eff']:.2f} min).
              - **Déficit semanal directo**: **{q1['gap_bf_units']:,.0f} unidades faltantes**, confirmando que operar en 1 turno provocaría un colapso de servicio.
            """
        )

    with tab_q2:
        render_alert(
            f"⚠️ DICTAMEN DINÁMICO: {q2['veredicto']}",
            f"Julio Cabrera promedió los tiempos ({q2['cabrera_avg_time']} min) y asumió que la capacidad se duplicaría a {q2['cabrera_claimed_cap']:.0f} u/sem. "
            f"La realidad matemática calculada demuestra que la capacidad solo sube a <b>{q2['cap_plant_8']:.0f} u/sem (+{q2['pct_increase_real']:.1f}%)</b>, "
            f"dejando un déficit de <b>{q2['deficit_bf']:,.0f} unidades en Black Friday</b>.",
            "warning",
        )
        st.markdown(
            f"""
            #### ¿Es correcta la conclusión del informe de ingeniería sobre la línea de ocho operadores?
            **Demostración y desglose matemático en tiempo real:**
            1. **La falacia del promedio**: Cabrera sumó los tiempos de estación y los dividió entre 8 ({q2['cabrera_avg_time']} min/u). En una línea de ensamble, la producción no la determina el promedio de los operarios, sino **la estación más lenta (el cuello de botella)**.
            2. **Cuellos de botella reales en la línea de 8**:
               - Para Estándar: **{q2['bn_8_std']}** con **{q2['ct_8_std']:.2f} min**.
               - Para Pro: **{q2['bn_8_pro']}** con **{q2['ct_8_pro']:.2f} min**.
               - Ciclo ponderado de la mezcla: **{q2['c_bar_8']:.2f} min** (efectivo con lotes: **{q2['c_eff_8']:.2f} min**).
            3. **Capacidad Real vs Promesa de Cabrera**:
               - Capacidad actual (6 ops): **{q2['cap_plant_6']:.0f} u/semana**.
               - Capacidad con 8 ops: **{q2['cap_plant_8']:.0f} u/semana**.
               - Incremento real: **+{q2['pct_increase_real']:.1f}%** (¡Lejos de duplicar / +100%!).
               - Inversión requerida: **US$ {q2['inversion']:,.0f}**.
            
            > ❌ **Conclusión Ejecutiva**: La propuesta de Cabrera cuesta US$ 18.000, no resuelve el pico de noviembre (faltan {q2['deficit_bf']:,.0f} unidades) y nace de un grave error conceptual en el cálculo del cuello de botella.
            """
        )

    with tab_q3:
        st.markdown(
            f"""
            #### ¿Por qué el dispositivo para la puerta aporta menos capacidad de la que parece?
            *(Evaluación de la Opción O5 con datos simulados en vivo)*

            - **Efecto Asimétrico por Variante**:
              - En **R1 Estándar**: Reduce el cuello de botella de E3 ({q3['ct_std_no']:.2f} min) a {q3['ct_std_disp']:.2f} min (se desplaza a {q3['bn_std_disp']}). Hay una ganancia de {q3['ct_std_no'] - q3['ct_std_disp']:.2f} min.
              - En **R1 Pro**: El cuello de botella ya era **{q3['bn_pro_disp']} con {q3['ct_pro_no']:.2f} min**. Como el dispositivo solo acelera las estaciones de la puerta (E2/E3), **¡el tiempo de ciclo de Pro no se reduce en absoluto ({q3['ct_pro_disp']:.2f} min)!**
            - **Ganancia Neta Marginal**:
              - Capacidad sin dispositivo: **{q3['cap_no']:.1f} u/semana**.
              - Capacidad con dispositivo: **{q3['cap_disp']:.1f} u/semana**.
              - Incremento neto: apenas **+{q3['delta_cap']:.1f} u/semana (+{q3['pct_gain']:.1f}%)**.
            - **Restricción de Tiempo Fatal**:
              - Plazo de entrega: **{q3['plazo_semanas']} semanas**. Si se ordena hoy (semana 1 de octubre), llega en la semana 11 (mediados de diciembre), **completamente fuera de Black Friday (semana 8)**.
              - Inversión total: **US$ {q3['inversion_total']:,.0f}** para solo 2 líneas.
            
            > ❌ **Recomendación para Mariela Santos**: Descartar el dispositivo de la puerta. Es costoso, no ayuda a la variante Pro y llega demasiado tarde.
            """
        )

    with tab_little:
        st.markdown(
            f"""
            #### Dinámica de Flujo y Ley de Little ($WIP = TH \\times CT$)
            - **Inventario en Proceso Observado (WIP)**: 46 unidades por línea.
            - **Tasa de Producción por Hora**: $\\frac{{{q1['cap_line']:.1f} \\text{{ u}}}}{{37,5 \\text{{ h}}}} = {q1['cap_line']/37.5:.2f}$ unidades/hora por línea.
            - **Tiempo de Flujo por Línea**:
              $$T_{{\\text{{flujo}}}} = \\frac{{WIP}}{{TH}} = \\frac{{46}}{{{q1['cap_line']/37.5:.2f}}} = {q1['flow_time_hr']:.2f} \\text{{ horas}}$$
            - **Diagnóstico Operativo**: Una unidad requiere apenas ~41 minutos de trabajo activo pero tarda {q1['flow_time_hr']:.2f} horas en cruzar la línea. Más del **89% del tiempo es espera en colas inter-estaciones**, demostrando que antes de agregar más operadores a la misma línea se deben estabilizar los buffers y balancear la estación E4.
            """
        )
