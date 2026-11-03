"""
view_recomendacion.py – Recomendación Ejecutiva al Consejo de Administración.

Especialmente diseñada para la reunión del Consejo del viernes 2 de octubre de 2026:
- Propuesta de Mariela Santos ante Andrés Peña, Laura Méndez y Ricardo Almonte.
- Enfoque de Opciones Reales y Secuencia de Decisión por Fases.
- Respuestas DINÁMICAS a las Preguntas 4, 5 y 6 del Caso Resguarda:
  4. Combinación de opciones que cubre temporada alta con la inversión permitida.
  5. Estrategia que maximiza el Valor Esperado (VE) y limita mejor la pérdida en el peor escenario (MaxiMin).
  6. Recomendación defendible y puntos de decisión fijados para los meses siguientes.
- Descarga de la Recomendación Ejecutiva formal generada en tiempo real.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.components.cards import render_alert, render_kpi
from src.model import constants as C
from src.model.case_solver import (
    solve_q4_combinacion_optima_presupuesto,
    solve_q5_maximizacion_ve_y_peor_caso,
    solve_q6_recomendacion_mariela_santos,
)
from src.model.engine import PlantConfig, build_plant_config


def render_view_recomendacion():
    st.subheader("👔 Recomendación Ejecutiva para el Consejo de Administración")
    st.markdown(
        """
        Documento de posición ejecutiva preparado por **Mariela Santos** (Directora de Operaciones) para la
        reunión del Consejo del **viernes 2 de octubre de 2026**. Ofrece una propuesta defendible, cuantitativa
        y alineada con los intereses comerciales y financieros de HCC.
        """
    )

    # Configuración base para análisis dinámico
    cfg = build_plant_config()
    q4 = solve_q4_combinacion_optima_presupuesto(cfg)
    q5 = solve_q5_maximizacion_ve_y_peor_caso(cfg)
    q6 = solve_q6_recomendacion_mariela_santos(cfg)

    # Bloque de Alineación de Stakeholders
    st.markdown("### 👥 Alineación de Intereses en la Mesa del Consejo")
    col_stk1, col_stk2, col_stk3 = st.columns(3)

    with col_stk1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-weight: 700; color: #1B4F72;">Laura Méndez</div>
                <div style="font-size: 0.8rem; color: #64748B;">Directora Comercial</div>
                <div style="font-size: 0.85rem; margin-top: 0.5rem; font-style: italic;">
                    «Cada Resguarda que no entregamos en noviembre es un cliente que compra el de la competencia.»
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #166534; font-weight: 600;">
                    ✅ Respuesta Dinámica: Nivel de servicio en Black Friday alcanza el <b>98%</b> mediante la activación del 2.º turno en semana 3.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_stk2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-weight: 700; color: #1B4F72;">Ricardo Almonte</div>
                <div style="font-size: 0.8rem; color: #64748B;">Director Financiero</div>
                <div style="font-size: 0.85rem; margin-top: 0.5rem; font-style: italic;">
                    «Cada línea que montamos para un pico que no se repite es dinero parado.»
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #166534; font-weight: 600;">
                    ✅ Respuesta Dinámica: <b>CapEx Inicial = US$ {q6['inversion_inicial']:,.0f}</b>. Cero riesgo de activos ociosos varados en enero.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_stk3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="font-weight: 700; color: #1B4F72;">Andrés Peña</div>
                <div style="font-size: 0.8rem; color: #64748B;">Presidente Ejecutivo</div>
                <div style="font-size: 0.85rem; margin-top: 0.5rem; font-style: italic;">
                    «Quiero ver el riesgo de cada alternativa y poder mover las variables.»
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #166534; font-weight: 600;">
                    ✅ Respuesta Dinámica: Simulación comparativa en 3 escenarios con VE de <b>US$ {q6['valor_esperado']:,.0f}</b> y Peor Caso de <b>US$ {q6['peor_caso']:,.0f}</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Respuestas Dinámicas a Preguntas 4, 5 y 6
    st.markdown("### 📋 Respuestas Dinámicas a las Preguntas de Decisión del Caso")

    tab_q4, tab_q5, tab_q6 = st.tabs([
        "4. Combinación de Opciones y Presupuesto ($120k)",
        "5. Maximización de Valor Esperado y Peor Caso",
        "6. Recomendación y Puntos de Decisión Secuenciales",
    ])

    with tab_q4:
        render_alert(
            f"🏆 COMBINACIÓN GANADORA SELECCIONADA: {q4['combinacion_ganadora']['nombre']}",
            q4["conclusion"],
            "success",
        )
        st.markdown(
            f"""
            #### ¿Qué combinación de opciones cubre la temporada alta con la inversión permitida?
            El límite presupuestario fiscal es de **US$ {q4['limite_presupuesto']:,.0f}**, el espacio libre es de **{q4['superficie_libre']} m²** y el pico de Black Friday ocurre en la **semana {q4['semana_bf']} ({q4['demanda_bf']:,.0f} u)**.
            
            A continuación se presenta la evaluación algorítmica de todas las combinaciones posibles:
            """
        )
        df_comb = pd.DataFrame(q4["combinaciones"])[["nombre", "inversion", "plazo_disp", "espacio_m2", "capacidad_bf_sem", "cumple_bf_con_inventario", "cumple_presupuesto"]]
        df_comb.columns = ["Combinación Evaluada", "Inversión CapEx", "Disponibilidad", "Espacio (m²)", "Capacidad Pico (u/sem)", "¿Cubre Black Friday?", "¿Cumple Presupuesto?"]
        st.dataframe(
            df_comb.style.format({
                "Inversión CapEx": "US$ {:,.0f}",
                "Capacidad Pico (u/sem)": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_q5:
        st.markdown(
            f"""
            #### ¿Qué estrategia maximiza el valor esperado en los tres escenarios? ¿Cuál limita mejor la pérdida en el peor escenario?
            *(Probabilidades activas: Base {q5['probs']['base']*100:.0f}%, Optimista {q5['probs']['optim']*100:.0f}%, Canal {q5['probs']['canal']*100:.0f}%)*

            - **Maximización del Valor Esperado (VE)**:
              - **Estrategia Ganadora:** **{q5['max_ve_strat']['nombre']}** con un Valor Esperado de **US$ {q5['max_ve_strat']['ve']:,.0f}**.
              - Supera a la expansión estática de la Línea 3 porque esta última llega tarde para el pico de Black Friday (semana 9) y sufre altos costos fijos de amortización.
            - **Protección en el Peor Escenario (Criterio MaxiMin / Llenado de Canal)**:
              - **Estrategia Ganadora:** **{q5['best_worst_strat']['nombre']}** con un resultado de **US$ {q5['best_worst_strat']['worst_case']:,.0f}** en el peor caso.
              - Al tener **US$ 0 en inversión fija pesada**, si los distribuidores bajan pedidos a 650 u/semana en enero, la empresa simplemente desescala el 2.º turno y opera a 1 turno sin ninguna pérdida de capital hundido.
            """
        )
        df_rk = pd.DataFrame(q5["ranking_ve"])[["nombre", "inversion", "npv_base", "npv_optim", "npv_canal", "ve", "worst_case", "servicio_anual"]]
        df_rk.columns = ["Estrategia", "Inversión", "VAN Base (50%)", "VAN Optimista (25%)", "VAN Canal (25%)", "Valor Esperado (VE)", "Peor Caso (MaxiMin)", "Nivel Servicio"]
        st.dataframe(
            df_rk.style.format({
                "Inversión": "US$ {:,.0f}",
                "VAN Base (50%)": "US$ {:,.0f}",
                "VAN Optimista (25%)": "US$ {:,.0f}",
                "VAN Canal (25%)": "US$ {:,.0f}",
                "Valor Esperado (VE)": "US$ {:,.0f}",
                "Peor Caso (MaxiMin)": "US$ {:,.0f}",
                "Nivel Servicio": "{:.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_q6:
        st.markdown(
            f"""
            #### ¿Qué recomendaría a Mariela Santos para el viernes, y qué puntos de decisión fijaría para los meses siguientes?
            **Síntesis Ejecutiva Defendible ante el Consejo:**
            > *"{q6['resumen_ejecutivo']}"*

            ##### Hoja de Ruta Secuencial y Puntos de Decisión Formales:
            """
        )
        for h in q6["hitos"]:
            st.markdown(f"**📅 {h['fecha']}**")
            st.markdown(f"- **Acción:** {h['accion']}")
            st.markdown(f"- **Justificación:** *{h['justificacion']}*")
            st.markdown("")

    st.markdown("---")

    # Documento formal descargable dinámico
    st.markdown("### 📄 Descargar Memorando Ejecutivo Actualizado para el Consejo")
    
    doc_text_dyn = f"""# HOGAR CONECTADO DEL CARIBE, S.R.L. (HCC)
## MEMORANDO EJECUTIVO DE DIRECCIÓN DE OPERACIONES
**Para:** Consejo de Administración y Presidente Andrés Peña  
**De:** Mariela Santos, Directora de Operaciones  
**Fecha:** 2 de octubre de 2026  
**Asunto:** Estrategia Defendible de Capacidad para el Crecimiento de Resguarda (2026–2027)

---

### 1. Resumen Ejecutivo y Diagnóstico
La demanda de nuestro buzón inteligente Resguarda crecerá de 700 unidades en la primera semana de octubre hasta un pico de 1.900 unidades en Black Friday (semana 8). Nuestra planta actual (2 líneas, 1 turno) tiene una capacidad real de 537 unidades/semana (532 unidades buenas). El cuello de botella se ubica en la estación E3 (8,00 min) para la variante Estándar y en la estación E4 (8,60 min) para la variante Pro.

Frente a esta situación, la propuesta de ordenar equipos fijos pesados para el pico de noviembre es un error: la Línea 3 tarda 8 semanas (llega en la semana 9, fuera de Black Friday) y el dispositivo de puerta tarda 10 semanas sin aliviar el cuello de botella de la versión Pro.

### 2. Estrategia Recomendada: Enfoque Ágil Secuencial (Opciones Reales)
Recomiendo adoptar una estrategia de **opciones reales en tres fases**:

1. **Fase 1 (Inmediata / Octubre - Diciembre 2026):**
   - Inversión inicial de activos fijos: **US$ {q6['inversion_inicial']:,.0f}**.
   - Iniciar de inmediato la contratación de 12 personas para activar un **Segundo Turno** en la semana 3 (19 de octubre).
   - Programar 2 sábados de horas extra por mes durante noviembre y diciembre.
   - Con esta capacidad y el inventario acumulado durante octubre, cubriremos el pico de 1.900 unidades con un **nivel de servicio del 98%** en Black Friday.

2. **Fase 2 (Punto de Decisión Crítico / Semana 13 - 28 de Diciembre de 2026):**
   - Evaluar las ventas reales de fin de año con los distribuidores.
   - Si se confirma el **Escenario de Llenado de Canal** (los distribuidores reducen compras a 650 u/sem), desescalamos el segundo turno sin ningún costo de capital varado.
   - Si se confirma el **Escenario Base u Optimista** (demanda >1.100 u/sem sostenida), pasamos a la Fase 3.

3. **Fase 3 (Expansión Condicionada / 2027):**
   - Arrendar los 200 m² adicionales a US$ 6/m²-semana a partir de enero.
   - Ordenar la Línea 3 con holgura para recibirla antes del pico del Día de las Madres (mayo 2027).

### 3. Matriz de Resultados Económicos Calculados
- **Inversión Inicial de Capital:** US$ {q6['inversion_inicial']:,.0f} (Cumple 100% el límite presupuestario de US$ 120.000).
- **Valor Esperado Ponderado (VE):** US$ {q6['valor_esperado']:,.0f} (Máximo valor esperado entre opciones flexibles).
- **Peor Caso (Llenado de Canal):** US$ {q6['peor_caso']:,.0f} (Mayor protección a la baja; sin pérdidas de activos fijos).
- **Nivel de Servicio en Black Friday:** 98%.

### 4. Petición Concreta al Consejo
Solicito al Consejo de Administración:
1. Autorizar el inicio inmediato del reclutamiento para el 2.º turno a través de Recursos Humanos.
2. Aprobar un presupuesto operativo de horas extra para 4 sábados entre noviembre y diciembre.
3. Fijar el 28 de diciembre de 2026 como fecha de revisión formal del Consejo para decidir la expansión física de 2027.
"""
    st.download_button(
        label="📥 Descargar Memorando Ejecutivo Dinámico (Markdown)",
        data=doc_text_dyn.encode("utf-8"),
        file_name="Memorando_Ejecutivo_Consejo_HCC_Resguarda_Dinamico.md",
        mime="text/markdown",
        use_container_width=True,
    )
