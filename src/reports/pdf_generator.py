"""
pdf_generator.py – Generador de reportes ejecutivos en PDF para Resguarda (HCC).

Utiliza fpdf2 y matplotlib para generar un informe corporativo de nivel C-Suite:
- Portada ejecutiva y resumen de decisión.
- Gráficos operacionales de alta resolución (Demanda vs Capacidad y Evolución de Inventario/Backlog).
- Diagnóstico del proceso, valores de control y perfil gráfico de utilización de estaciones.
- Respuestas dinámicas completas a las 6 preguntas clave del caso.
- Matriz de decisión multicriterio con gráfico comparativo de escenarios y síntesis de los 5 grupos de indicadores.
- Análisis de sensibilidad con diagrama de tornado y hoja de ruta secuencial de puntos de decisión.
- Tabla detallada semana a semana (semanas 1 a 52) con formato tabular profesional.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from fpdf import FPDF
import pandas as pd

from src.model import constants as C
from src.model.case_solver import (
    solve_q1_capacidad_y_cuello,
    solve_q2_informe_cabrera,
    solve_q3_dispositivo_puerta,
    solve_q4_combinacion_optima_presupuesto,
    solve_q5_maximizacion_ve_y_peor_caso,
    solve_q6_recomendacion_mariela_santos,
)
from src.model.engine import (
    ControlValues,
    PlantConfig,
    compute_investment,
    compute_npv,
    compute_station_utilization,
    get_station_times,
    run_all_scenarios,
    simulate_weekly,
)
from src.model.strategies import get_predefined_strategies
from src.reports.pdf_charts import (
    create_demand_capacity_chart_image,
    create_inventory_backlog_chart_image,
    create_scenarios_comparison_chart_image,
    create_station_utilization_chart_image,
    create_tornado_chart_image,
)


def _clean_str(text: Any) -> str:
    """Sanitiza texto para fuentes estándar latin-1 de PDF."""
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "\u2013": "-",    # en-dash
        "\u2014": "--",   # em-dash
        "\u2018": "'",    # curly single quote
        "\u2019": "'",
        "\u201c": '"',    # curly double quote
        "\u201d": '"',
        "\u2022": "-",    # bullet
        "\u00b7": "*",    # middle dot
        "–": "-",
        "—": "--",
        "•": "-",
        "·": "*",
        "º": "o",
        "ª": "a",
        "²": "2",
        "³": "3",
        "σ": "sigma",
        "±": "+/-",
    }
    for orig, rep in replacements.items():
        s = s.replace(orig, rep)
    return s.encode("latin-1", errors="replace").decode("latin-1")


class CorporateReportPDF(FPDF):
    """Clase personalizada con encabezado y pie de página corporativo."""

    def __init__(self, title_text: str = "INFORME EJECUTIVO DE SIMULACION"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.title_text = title_text

    def header(self):
        if self.page_no() == 1:
            return  # La portada tiene su propio diseño
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(27, 79, 114)  # Azul corporativo #1B4F72
        self.cell(0, 6, _clean_str("HOGAR CONECTADO DEL CARIBE, S.R.L. * RESGUARDA"), align="L", ln=False)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 6, _clean_str("Simulacion de Capacidad y Demanda 2026-2027"), align="R", ln=True)
        self.set_draw_color(189, 195, 199)
        self.set_line_width(0.3)
        self.line(10, 16, 200, 16)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(149, 165, 166)
        self.cell(0, 5, _clean_str(f"Caso Resguarda (Ivey 2020) * Direccion de Operaciones | Pagina {self.page_no()}/{{nb}}"), align="C")


def generate_simulation_pdf(
    cfg: PlantConfig,
    df_weekly: pd.DataFrame,
    control_vals: ControlValues,
    multi_scenarios: dict[str, Any] | None = None,
    strategy_name: str = "Estrategia Activa",
) -> bytes:
    """
    Compila el informe corporativo visual de alta fidelidad en PDF y retorna los bytes listos para descarga.
    """
    pdf = CorporateReportPDF()
    pdf.alias_nb_pages()

    # Precalcular datos para gráficos si no vienen suministrados
    if multi_scenarios is None:
        multi_scenarios = run_all_scenarios(cfg)

    strategies = get_predefined_strategies()
    payoffs_data = []
    for s_id, s_def in strategies.items():
        res_s = run_all_scenarios(s_def.config_base)
        sc = res_s["scenarios"]
        payoffs_data.append({
            "name": s_def.nombre.split(".")[0],
            "base_npv": sc["base"]["npv"],
            "optim_npv": sc["optim"]["npv"],
            "canal_npv": sc["canal"]["npv"],
            "ve": res_s["ve"],
            "worst": res_s["worst_case"],
        })

    # Datos para el tornado chart
    inv_base = compute_investment(cfg)
    npv_base = compute_npv(df_weekly, inv_base)
    tornado_tests = [
        {"Variable": "Precios Netos (+/-15%)", "cfg_l": PlantConfig(**{**cfg.__dict__, "precio_neto_std": cfg.precio_neto_std*0.85, "precio_neto_pro": cfg.precio_neto_pro*0.85}), "cfg_h": PlantConfig(**{**cfg.__dict__, "precio_neto_std": cfg.precio_neto_std*1.15, "precio_neto_pro": cfg.precio_neto_pro*1.15})},
        {"Variable": "Costos Materiales (+/-15%)", "cfg_l": PlantConfig(**{**cfg.__dict__, "materiales_std": cfg.materiales_std*1.15, "materiales_pro": cfg.materiales_pro*1.15}), "cfg_h": PlantConfig(**{**cfg.__dict__, "materiales_std": cfg.materiales_std*0.85, "materiales_pro": cfg.materiales_pro*0.85})},
        {"Variable": "Tamano de Lote Q (25 vs 200)", "cfg_l": PlantConfig(**{**cfg.__dict__, "tamano_lote": 25}), "cfg_h": PlantConfig(**{**cfg.__dict__, "tamano_lote": 200})},
        {"Variable": "Tiempo Setup s (30 vs 10 min)", "cfg_l": PlantConfig(**{**cfg.__dict__, "tiempo_cambio": 30.0}), "cfg_h": PlantConfig(**{**cfg.__dict__, "tiempo_cambio": 10.0})},
        {"Variable": "Mezcla % R1 Pro (20% vs 45%)", "cfg_l": PlantConfig(**{**cfg.__dict__, "pct_pro_override": 0.45}), "cfg_h": PlantConfig(**{**cfg.__dict__, "pct_pro_override": 0.20})},
        {"Variable": "Tasa Fallas (7% vs 2%)", "cfg_l": PlantConfig(**{**cfg.__dict__, "falla_std": 0.07, "falla_pro": 0.09}), "cfg_h": PlantConfig(**{**cfg.__dict__, "falla_std": 0.02, "falla_pro": 0.03})},
        {"Variable": "Costos Fijos Semanales (+/-15%)", "cfg_l": PlantConfig(**{**cfg.__dict__, "fijos_planta_semanal": cfg.fijos_planta_semanal*1.15}), "cfg_h": PlantConfig(**{**cfg.__dict__, "fijos_planta_semanal": cfg.fijos_planta_semanal*0.85})},
    ]
    tornado_rows = []
    for t in tornado_tests:
        df_l = simulate_weekly(t["cfg_l"])
        df_h = simulate_weekly(t["cfg_h"])
        nl = compute_npv(df_l, inv_base)
        nh = compute_npv(df_h, inv_base)
        sw_l = nl - npv_base
        sw_h = nh - npv_base
        tornado_rows.append({
            "Variable": t["Variable"],
            "Min_Swing": min(sw_l, sw_h),
            "Max_Swing": max(sw_l, sw_h),
            "Rango_Total": abs(sw_h - sw_l),
        })
    df_tornado = pd.DataFrame(tornado_rows)

    # ═══════════════════════════════════════════════
    # PÁGINA 1: Portada y Resumen Ejecutivo
    # ═══════════════════════════════════════════════
    pdf.add_page()

    # Franja superior
    pdf.set_fill_color(27, 79, 114)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_xy(10, 5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, _clean_str("HOGAR CONECTADO DEL CARIBE, S.R.L. | CONSEJO DE ADMINISTRACION"), ln=True)

    pdf.ln(12)

    # Título principal
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 9, _clean_str("INFORME EJECUTIVO DE SIMULACION"), ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(0, 7, _clean_str("Caso Resguarda: Producir al Ritmo de la Demanda (2026-2027)"), ln=True)

    pdf.set_draw_color(41, 128, 185)
    pdf.set_line_width(0.8)
    pdf.line(10, 48, 200, 48)
    pdf.ln(8)

    # Ficha de Metadatos
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("1. FICHA TECNICA DE LA CONFIGURACION EVALUADA"), ln=True)

    pdf.set_fill_color(235, 240, 245)
    pdf.rect(10, 58, 190, 26, "F")
    pdf.set_xy(12, 60)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(32, 5, "Estrategia:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(60, 5, _clean_str(strategy_name), ln=False)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(35, 5, "Escenario Demanda:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(50, 5, _clean_str(cfg.escenario.upper()), ln=True)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(32, 5, "Lineas ensamble:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(60, 5, _clean_str(f"{cfg.num_lineas} lineas ({cfg.ops_por_linea} ops/linea)"), ln=False)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(35, 5, "Turnos de trabajo:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(50, 5, _clean_str(f"{cfg.num_turnos} turnos (sabados: {cfg.sabados_mes}/mes)"), ln=True)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(32, 5, "Lote / Setup:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(60, 5, _clean_str(f"Q = {cfg.tamano_lote} u | {cfg.tiempo_cambio} min cambio"), ln=False)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(35, 5, "Fecha Emision:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(50, 5, datetime.now().strftime("%d/%m/%Y %H:%M"), ln=True)

    pdf.ln(14)

    # Bloque de KPIs Principales
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("2. INDICADORES CLAVE DE DESEMPEÑO (KPIs ANUALES)"), ln=True)
    pdf.ln(1)

    total_dem = df_weekly["Demanda"].sum()
    total_atend = df_weekly["Atendido"].sum()
    total_perd = df_weekly["Ventas Perdidas"].sum()
    srv_pct = (total_atend / total_dem * 100) if total_dem > 0 else 100.0
    van_tot = df_weekly["Flujo Descontado"].sum()
    inversion_tot = multi_scenarios["investment"]
    if multi_scenarios and "scenarios" in multi_scenarios and cfg.escenario in multi_scenarios["scenarios"]:
        van_tot = multi_scenarios["scenarios"][cfg.escenario]["npv"]

    kpi_boxes = [
        ("Demanda Total Anual", f"{total_dem:,.0f} u", "#EBF5FB"),
        ("Unidades Atendidas", f"{total_atend:,.0f} u", "#E8F8F5"),
        ("Nivel Servicio Global", f"{srv_pct:.1f} %", "#E8F8F5" if srv_pct >= 90 else "#FDEDEC"),
        ("Ventas Perdidas", f"{total_perd:,.0f} u", "#FDEDEC" if total_perd > 5000 else "#E8F8F5"),
        ("Inversion CapEx", f"US$ {inversion_tot:,.0f}", "#F4F6F6"),
        ("Valor Actual Neto (VAN)", f"US$ {van_tot:,.0f}", "#E8F8F5" if van_tot > 0 else "#FDEDEC"),
    ]

    col_w = 60
    box_h = 16
    start_y = pdf.get_y()
    for idx, (label, val, bg_hex) in enumerate(kpi_boxes):
        row = idx // 3
        col = idx % 3
        bx = 10 + col * (col_w + 5)
        by = start_y + row * (box_h + 4)

        r = int(bg_hex[1:3], 16)
        g = int(bg_hex[3:5], 16)
        b = int(bg_hex[5:7], 16)
        pdf.set_fill_color(r, g, b)
        pdf.rect(bx, by, col_w, box_h, "F")
        pdf.set_draw_color(189, 195, 199)
        pdf.rect(bx, by, col_w, box_h, "D")

        pdf.set_xy(bx + 2, by + 2)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(120, 144, 156)
        pdf.cell(col_w - 4, 4, _clean_str(label.upper()), align="C")

        pdf.set_xy(bx + 2, by + 7)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(27, 79, 114)
        pdf.cell(col_w - 4, 7, _clean_str(val), align="C")

    pdf.set_y(start_y + 2 * (box_h + 4) + 6)

    # Resumen Ejecutivo de la Decisión
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("3. CONCLUSION Y RECOMENDACION PARA EL CONSEJO"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(44, 62, 80)
    recomendacion_texto = (
        "HCC se enfrenta a un desafio de escala inminente: la demanda del buzon Resguarda en Black Friday "
        "(1.900 unidades/semana) triplica la capacidad actual de planta en un turno (537 u/semana). "
        "La evaluacion cuantitativa concluye que ordenar maquinaria fija (Linea 3 a $48.000) es ineficaz "
        "para el pico porque su plazo de 8 semanas la hace llegar despues de la temporada alta y genera "
        "riesgo de capacidad ociosa si el canal se satura en enero. "
        "Por el contrario, la Estrategia Agil Secuencial recomendada añade el 2.º turno en la semana 3 "
        "con horas extra los sabados en noviembre/diciembre: requiere $0 en inversion en activos fijos, "
        "alcanza un nivel de servicio superior al 95% en la temporada critica y preserva la opcion de "
        "ajustar o consolidar capacidad en la semana 13 sin costos hundidos."
    )
    pdf.multi_cell(0, 5, _clean_str(recomendacion_texto))

    # ═══════════════════════════════════════════════
    # PÁGINA 2: Curvas Operativas y Dinámica de Flujo (Gráficos)
    # ═══════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("CURVAS OPERATIVAS Y DINAMICA DE FLUJO A 52 SEMANAS"), ln=True)
    pdf.set_line_width(0.4)
    pdf.line(10, 24, 200, 24)
    pdf.ln(3)

    # Gráfico 1: Demanda vs Capacidad
    img_demanda = create_demand_capacity_chart_image(df_weekly)
    pdf.image(img_demanda, x=10, y=pdf.get_y(), w=190)
    pdf.set_y(pdf.get_y() + 82)

    # Gráfico 2: Inventario vs Backlog
    img_inv = create_inventory_backlog_chart_image(df_weekly)
    pdf.image(img_inv, x=10, y=pdf.get_y(), w=190)
    pdf.set_y(pdf.get_y() + 75)

    # Comentario Operacional
    pdf.set_fill_color(245, 247, 248)
    pdf.rect(10, pdf.get_y(), 190, 20, "F")
    pdf.set_xy(12, pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 4, _clean_str("OBSERVACIONES DE CAPACIDAD Y CONTROL DE INVENTARIO:"), ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(44, 62, 80)
    obs_txt = (
        "- Black Friday (Semana 8, 1.900 u) exige anticipar produccion desde las semanas 4 a 7 para acumular hasta "
        "1.200 u en inventario de producto terminado sin vulnerar el limite de bodega de 1.500 u.\n"
        "- En mayo (Semanas 33-34, Dia de las Madres), el pico secundario de 1.100 u se absorbe de forma equilibrada "
        "gracias a la flexibilidad del 2.o turno sin generar inventario ocioso posterior."
    )
    pdf.multi_cell(186, 3.8, _clean_str(obs_txt))

    # ═══════════════════════════════════════════════
    # PÁGINA 3: Diagnóstico de Proceso y Capacidad
    # ═══════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("DIAGNOSTICO DEL PROCESO Y BALANCE DE CAPACIDAD"), ln=True)
    pdf.set_line_width(0.4)
    pdf.line(10, 24, 200, 24)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(0, 4.5, _clean_str("Valores de Control del Sistema Actual (2 lineas, 6 operadores, 1 turno, 30% Pro):"), ln=True)

    ctrl_rows = [
        ("Contenido de Trabajo (min/u)", f"Estandar: {control_vals.wc_std} min", f"Pro: {control_vals.wc_pro} min"),
        ("Tiempo Ciclo y Cuello Botella", f"{control_vals.ct_std} min ({control_vals.bottleneck_std})", f"{control_vals.ct_pro} min ({control_vals.bottleneck_pro})"),
        ("Eficiencia del Balance", f"{control_vals.eff_std * 100:.1f} %", f"{control_vals.eff_pro * 100:.1f} %"),
        ("Tiempo Ciclo Medio con Mezcla", f"{control_vals.c_bar} min/u", f"Efectivo c_bar + s/Q: {control_vals.c_eff} min/u"),
        ("Capacidad Bruta Semanal", f"Linea: {control_vals.cap_line} u/sem", f"Planta (2 lineas): {control_vals.cap_plant} u/sem"),
        ("Unidades Buenas / Retrabajo", f"Buenas: {control_vals.good_units} u/sem", f"A retrabajo: {control_vals.rework_units} u/sem"),
        ("Ley de Little (WIP obs = 46 u)", f"Tasa: {control_vals.cap_line / 37.5:.2f} u/hora", f"Tiempo de flujo: {control_vals.flow_time_hr} horas"),
        ("Takt Time en Black Friday (sem 8)", f"Linea: {control_vals.takt_wk8} min/u", "Gap vs Ciclo Actual: -5,81 min"),
        ("Costo Laboral y Margen", f"Costo MO/buena: US$ {control_vals.labor_per_good:.2f}", f"Margen Contrib. Medio: US$ {control_vals.margin_avg:.2f}"),
        ("Capacidad con 2.º Turno (sin rampa)", f"Planta: {control_vals.cap_2shifts} u/sem", "Incremento capacidad: +92%"),
    ]

    pdf.set_fill_color(27, 79, 114)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(70, 4.2, "INDICADOR DE PROCESO", 1, 0, "L", True)
    pdf.cell(60, 4.2, "DETALLE / ESTANDAR", 1, 0, "C", True)
    pdf.cell(60, 4.2, "VERIFICACION / PRO", 1, 1, "C", True)

    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(44, 62, 80)
    for idx, (ind, d1, d2) in enumerate(ctrl_rows):
        is_even = (idx % 2 == 0)
        pdf.set_fill_color(245, 247, 248) if is_even else pdf.set_fill_color(255, 255, 255)
        pdf.cell(70, 3.8, _clean_str(ind), 1, 0, "L", True)
        pdf.cell(60, 3.8, _clean_str(d1), 1, 0, "C", True)
        pdf.cell(60, 3.8, _clean_str(d2), 1, 1, "C", True)

    pdf.ln(3)

    # Gráfico 3: Utilización de Estaciones
    pct_pro = cfg.pct_pro_override if cfg.pct_pro_override is not None else C.PCT_PRO_SEM1_26
    stations_active = get_station_times(cfg.ops_por_linea, cfg.dispositivo_puerta, cfg.subcontratar_puerta)
    util_data = compute_station_utilization(stations_active, pct_pro)
    img_util = create_station_utilization_chart_image(util_data)
    pdf.image(img_util, x=10, y=pdf.get_y(), w=190)
    pdf.set_y(pdf.get_y() + 78)

    # Tabla de Utilización por Estación
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 6.8)
    pdf.cell(20, 4, "ESTACION", 1, 0, "C", True)
    pdf.cell(60, 4, "DESCRIPCION / OPERACION", 1, 0, "L", True)
    pdf.cell(26, 4, "T. EST. (min)", 1, 0, "C", True)
    pdf.cell(26, 4, "T. PRO (min)", 1, 0, "C", True)
    pdf.cell(26, 4, "T. POND (min)", 1, 0, "C", True)
    pdf.cell(32, 4, "UTILIZACION %", 1, 1, "C", True)

    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(44, 62, 80)
    for idx, u in enumerate(util_data):
        is_even = (idx % 2 == 0)
        is_bottleneck = "Cuello" in u.get("estado", "") or u.get("is_bottleneck", False)
        if is_bottleneck:
            pdf.set_fill_color(254, 237, 236)
        elif is_even:
            pdf.set_fill_color(245, 247, 248)
        else:
            pdf.set_fill_color(255, 255, 255)

        st_id = u.get("station_id", f"E{idx+1}")
        st_name = u.get("name", u.get("operacion", ""))
        t_s = u.get("time_std", u.get("t_std", 0.0))
        t_p = u.get("time_pro", u.get("t_pro", 0.0))
        t_w = u.get("weighted_time", u.get("t_ponderado", 0.0))
        u_pct = u.get("utilization_pct", u.get("util_ponderada_pct", 0.0))

        pdf.cell(20, 3.8, _clean_str(st_id), 1, 0, "C", True)
        pdf.cell(60, 3.8, _clean_str(st_name), 1, 0, "L", True)
        pdf.cell(26, 3.8, f"{t_s:.2f}", 1, 0, "C", True)
        pdf.cell(26, 3.8, f"{t_p:.2f}", 1, 0, "C", True)
        pdf.cell(26, 3.8, f"{t_w:.2f}", 1, 0, "C", True)
        tag_bn = " (Cuello)" if is_bottleneck else ""
        pdf.cell(32, 3.8, f"{u_pct:.1f}%{tag_bn}", 1, 1, "C", True)

    # ═══════════════════════════════════════════════
    # PÁGINA 4: Respuestas Dinámicas a las 6 Preguntas del Caso
    # ═══════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("RESPUESTAS DINAMICAS A LAS PREGUNTAS CLAVE DEL CASO"), ln=True)
    pdf.set_line_width(0.4)
    pdf.line(10, 24, 200, 24)
    pdf.ln(3)

    q1 = solve_q1_capacidad_y_cuello(cfg)
    q2 = solve_q2_informe_cabrera(cfg)
    q3 = solve_q3_dispositivo_puerta(cfg)
    q4 = solve_q4_combinacion_optima_presupuesto(cfg)
    q5 = solve_q5_maximizacion_ve_y_peor_caso(cfg)
    q6 = solve_q6_recomendacion_mariela_santos(cfg)

    preguntas_respuestas = [
        (
            "1. ¿Cual es la capacidad real de la planta hoy y donde esta el cuello de botella?",
            f"Capacidad semanal de planta: {q1['cap_plant']:.1f} u/sem brutas ({q1['good_units']:.1f} u/sem de unidades buenas). "
            f"Cuellos de botella: Para Estandar es {q1['bottleneck_std']} ({q1['ct_std']:.2f} min); para Pro es {q1['bottleneck_pro']} ({q1['ct_pro']:.2f} min). "
            f"El ciclo medio ponderado con la mezcla es {q1['c_bar']:.2f} min/u ({q1['c_eff']:.2f} min/u efectivo con lotes de {cfg.tamano_lote} u). "
            f"En Black Friday (1.900 u/sem), el takt time es {q1['takt_bf_line']:.2f} min/u por linea, dejando un deficit de {q1['gap_bf_units']:.0f} u/sem."
        ),
        (
            "2. ¿Es correcta la conclusion del informe de ingenieria sobre la linea de 8 operadores?",
            f"Veredicto: {q2['veredicto']}. Cabrera promedio los tiempos ({q2['cabrera_avg_time']:.2f} min ~ 5,0 min) afirmando que duplicaria la capacidad. "
            f"En realidad, el ciclo real queda dictado por {q2['bn_8_std']} ({q2['ct_8_std']:.2f} min) y {q2['bn_8_pro']} ({q2['ct_8_pro']:.2f} min). "
            f"La capacidad solo sube de {q2['cap_plant_6']:.0f} a {q2['cap_plant_8']:.0f} u/sem (+{q2['pct_increase_real']:.1f}%), generando un deficit de {q2['deficit_bf']:,.0f} u en Black Friday."
        ),
        (
            "3. ¿Por que el dispositivo para la puerta aporta menos capacidad de la que parece?",
            f"El dispositivo reduce E2 a 5,6 min y E3 a 6,0 min, mejorando Estandar a {q3['ct_std_disp']:.2f} min. "
            f"Sin embargo, para el modelo Pro el cuello de botella ya era {q3['bn_pro_no']} ({q3['ct_pro_no']:.2f} min) y NO cambia en absoluto. "
            f"La ganancia neta de planta es de apenas +{q3['delta_cap']:.1f} u/sem (+{q3['pct_gain']:.1f}%), cuesta US$ {q3['inversion_total']:,.0f} y su plazo de {q3['plazo_semanas']} semanas llega tarde para Black Friday."
        ),
        (
            "4. ¿Que combinacion de opciones cubre la temporada alta con la inversion permitida?",
            f"La combinacion optima es: {q4['combinacion_ganadora']['nombre']}. "
            f"Inversion fija: US$ {q4['combinacion_ganadora']['inversion']:,.0f} (limite US$ {q4['limite_presupuesto']:,.0f}). "
            f"Entra en servicio en la {q4['combinacion_ganadora']['plazo_disp']}, no consume espacio adicional (quedan {q4['combinacion_ganadora']['espacio_libre']} m2 libres) y abastece plenamente la temporada alta combinada con el inventario previo."
        ),
        (
            "5. ¿Que estrategia maximiza el Valor Esperado y cual limita mejor la perdida en el peor caso?",
            f"Estrategia que maximiza el VE: '{q5['max_ve_strat']['nombre']}' con VE de US$ {q5['max_ve_strat']['ve']:,.0f}. "
            f"Estrategia que mejor protege en el peor escenario (Llenado de Canal): '{q5['best_worst_strat']['nombre']}' con un VAN de US$ {q5['best_worst_strat']['worst_case']:,.0f} al tener cero capital varado en activos fijos."
        ),
        (
            "6. ¿Que recomendaria a Mariela Santos para el viernes y que puntos de decision fijaria?",
            f"Recomendacion para el Consejo: Defender la {q6['estrategia_recomendada']} (US$ 0 CapEx inicial). "
            f"Hito 1: Sem 0 (Aprobar 2.º turno y horas extra). Hito 2: Sem 3 (Puesta en marcha del turno y acumular stock). "
            f"Hito 3: Sem 8 (Absorber Black Friday). Hito 4: Sem 13 (GATE CRITICO de evaluacion de canal para decidir desescalar o expandir)."
        ),
    ]

    for q_title, q_body in preguntas_respuestas:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(27, 79, 114)
        pdf.cell(0, 4.5, _clean_str(q_title), ln=True)
        pdf.set_font("Helvetica", "", 7.2)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 3.8, _clean_str(q_body))
        pdf.ln(1.5)

    # ═══════════════════════════════════════════════
    # PÁGINA 5: Matriz de Decisión Multicriterio y Valor Esperado
    # ═══════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("MATRIZ DE DECISION MULTICRITERIO Y VALOR ESPERADO"), ln=True)
    pdf.set_line_width(0.4)
    pdf.line(10, 24, 200, 24)
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 4, _clean_str("Comparacion cuantitativa en los tres escenarios de demanda (Base 50%, Optimista 25%, Canal 25%):"), ln=True)
    pdf.ln(1)

    pdf.set_fill_color(27, 79, 114)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(45, 5, "ESCENARIO", 1, 0, "L", True)
    pdf.cell(25, 5, "PROB.", 1, 0, "C", True)
    pdf.cell(30, 5, "DEMANDA", 1, 0, "R", True)
    pdf.cell(30, 5, "ATENDIDO", 1, 0, "R", True)
    pdf.cell(25, 5, "NIVEL SERV.", 1, 0, "C", True)
    pdf.cell(35, 5, "VAN (US$)", 1, 1, "R", True)

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(44, 62, 80)
    scens = multi_scenarios["scenarios"]
    probs = multi_scenarios["probs"]
    for esc_key, esc_name in [("base", "Escenario Base"), ("optim", "Escenario Optimista"), ("canal", "Llenado de Canal")]:
        s_data = scens[esc_key]
        p_val = probs[esc_key] * 100
        pdf.cell(45, 4.8, _clean_str(esc_name), 1, 0, "L")
        pdf.cell(25, 4.8, f"{p_val:.0f} %", 1, 0, "C")
        pdf.cell(30, 4.8, f"{s_data['total_demanda']:,.0f}", 1, 0, "R")
        pdf.cell(30, 4.8, f"{s_data['total_atendido']:,.0f}", 1, 0, "R")
        pdf.cell(25, 4.8, f"{s_data['nivel_servicio']:.1f} %", 1, 0, "C")
        pdf.cell(35, 4.8, f"US$ {s_data['npv']:,.0f}", 1, 1, "R")

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(235, 245, 251)
    pdf.cell(155, 5, "VALOR ESPERADO PONDERADO (VE):", 1, 0, "R", True)
    pdf.cell(35, 5, f"US$ {multi_scenarios['ve']:,.0f}", 1, 1, "R", True)

    pdf.set_fill_color(253, 237, 236)
    pdf.cell(155, 5, "PEOR CASO (MAXIMIN / CANAL):", 1, 0, "R", True)
    pdf.cell(35, 5, f"US$ {multi_scenarios['worst_case']:,.0f}", 1, 1, "R", True)

    pdf.ln(3)

    # Gráfico 4: Comparativa de Escenarios
    img_payoffs = create_scenarios_comparison_chart_image(payoffs_data)
    pdf.image(img_payoffs, x=10, y=pdf.get_y(), w=190)
    pdf.set_y(pdf.get_y() + 78)

    # Síntesis de los 5 Grupos de Indicadores
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 5, _clean_str("SINTESIS DE LOS 5 GRUPOS DE INDICADORES OFICIALES:"), ln=True)

    avg_mo_good = df_weekly["Costo MO"].sum() / total_atend if total_atend > 0 else 0
    inv_mean = df_weekly["Inv. Final"].mean()

    ind_groups = [
        ("Capacidad", "Tiempo ciclo std/pro, cuello botella, cap. bruta y buenas, takt time, utilizacion estaciones",
         f"Ciclo: {control_vals.ct_std}/{control_vals.ct_pro}m | Cap: {control_vals.cap_plant:.0f} u/sem ({control_vals.good_units:.0f} buenas)"),
        ("Flujo", "Eficiencia de balance, inventario en proceso (WIP), tiempo de flujo (Little), inventario PT",
         f"Eficiencia: {control_vals.eff_std*100:.1f}% | WIP: 46 u/lin | Flujo: {control_vals.flow_time_hr:.2f}h | Inv. Prom: {inv_mean:.0f} u"),
        ("Servicio", "Demanda atendida, pedidos pendientes (backlog), ventas perdidas, nivel de servicio %",
         f"Atendido: {total_atend:,.0f} u ({srv_pct:.1f}%) | Perdidas: {total_perd:,.0f} u | Nivel Serv: {srv_pct:.1f}%"),
        ("Economia", "Coste MO/unidad buena, coste total semanal medio, margen contribucion, inversion, VAN",
         f"MO: US$ {avg_mo_good:.2f}/u | Margen: US$ {control_vals.margin_avg:.2f}/u | CapEx: US$ {inversion_tot:,.0f} | VAN: US$ {van_tot:,.0f}"),
        ("Riesgo", "Resultado por escenario, valor esperado (VE), peor caso (MaxiMin), sensibilidad",
         f"VE: US$ {multi_scenarios['ve']:,.0f} | Peor caso: US$ {multi_scenarios['worst_case']:,.0f} (Llenado de Canal)"),
    ]

    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 6.8)
    pdf.cell(24, 4.2, "GRUPO", 1, 0, "L", True)
    pdf.cell(86, 4.2, "INDICADORES DEL TABLERO", 1, 0, "L", True)
    pdf.cell(80, 4.2, "VALOR CALCULADO (ESTA SIMULACION)", 1, 1, "L", True)

    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(44, 62, 80)
    for idx, (grp, defs, vals) in enumerate(ind_groups):
        is_even = (idx % 2 == 0)
        pdf.set_fill_color(245, 247, 248) if is_even else pdf.set_fill_color(255, 255, 255)
        pdf.cell(24, 3.8, _clean_str(grp), 1, 0, "L", True)
        pdf.cell(86, 3.8, _clean_str(defs), 1, 0, "L", True)
        pdf.cell(80, 3.8, _clean_str(vals), 1, 1, "L", True)

    # ═══════════════════════════════════════════════
    # PÁGINA 6: Análisis de Sensibilidad y Hoja de Ruta
    # ═══════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("ANALISIS DE SENSIBILIDAD (TORNADO) Y HOJA DE RUTA SECUENCIAL"), ln=True)
    pdf.set_line_width(0.4)
    pdf.line(10, 24, 200, 24)
    pdf.ln(3)

    # Gráfico 5: Tornado Chart
    img_tornado = create_tornado_chart_image(df_tornado)
    pdf.image(img_tornado, x=10, y=pdf.get_y(), w=190)
    pdf.set_y(pdf.get_y() + 80)

    # Hoja de ruta secuencial
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 5, _clean_str("PUNTOS DE DECISION SECUENCIALES (HOJA DE RUTA RECOMENDADA):"), ln=True)
    pdf.ln(1)

    roadmap = [
        ("Semana 0 (Hoy - 2 Oct):", "Aprobar el 2.º turno para ambas lineas. Iniciar contratacion de 12 personas ($0 CapEx en activos fijos)."),
        ("Semana 3 (19 Oct):", "Puesta en marcha del 2.º turno. Acumular inventario de producto terminado hacia noviembre."),
        ("Semanas 5-9 (Pico Nov):", "Activar 2 sabados de horas extra por mes en el 1.º turno para cubrir las 1.900 u de Black Friday con nivel de servicio >95%."),
        ("Semana 13 (28 Dic):", "PUNTO DE DECISION CRITICO (GATE): Evaluar ventas reales de Navidad. Si se confirma canal, replegar 2.º turno sin costos hundidos. Si optimista, evaluar expansion de espacio."),
        ("Semanas 33-34 (Mayo):", "Atender pico del Dia de las Madres con flexibilidad de turnos y lotes ampliados a Q=150 u."),
    ]
    for hito, desc in roadmap:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(38, 4.5, _clean_str(hito), ln=0)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(pdf.epw - 38, 4.5, _clean_str(desc))
        pdf.ln(0.5)

    # ═══════════════════════════════════════════════
    # PÁGINAS 7–8: Tabla Detallada 52 Semanas
    # ═══════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(27, 79, 114)
    pdf.cell(0, 6, _clean_str("SIMULACION SEMANA A SEMANA (SEMANAS 1 A 52)"), ln=True)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 4, _clean_str(f"Cifras en unidades y US$ | Escenario: {cfg.escenario.upper()} | Lote: {cfg.tamano_lote} u"), ln=True)
    pdf.ln(3)

    col_widths = [8, 11, 13, 14, 14, 14, 13, 13, 13, 12, 17, 18, 20]
    headers = ["Sem", "Fec", "Dem", "Cap.B", "Prod", "Aten", "Inv.F", "Bcklog", "V.Perd", "NS%", "Costo MO", "Margen", "Flujo Desc"]

    def print_weekly_header():
        pdf.set_fill_color(27, 79, 114)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 6.5)
        for w, h in zip(col_widths, headers):
            pdf.cell(w, 5, _clean_str(h), 1, 0, "C", True)
        pdf.ln(5)

    print_weekly_header()

    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(44, 62, 80)

    for idx, row in df_weekly.iterrows():
        if pdf.get_y() > 270:
            pdf.add_page()
            print_weekly_header()
            pdf.set_font("Helvetica", "", 6)
            pdf.set_text_color(44, 62, 80)

        is_even = (idx % 2 == 0)
        is_peak = row["Semana"] in [8, 33, 34]
        if is_peak:
            pdf.set_fill_color(254, 249, 231)
        elif is_even:
            pdf.set_fill_color(245, 247, 248)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(col_widths[0], 4.2, str(int(row["Semana"])), 1, 0, "C", True)
        pdf.cell(col_widths[1], 4.2, str(row["Fecha"]), 1, 0, "C", True)
        pdf.cell(col_widths[2], 4.2, f"{row['Demanda']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[3], 4.2, f"{row['Cap. Bruta']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[4], 4.2, f"{row['Producción']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[5], 4.2, f"{row['Atendido']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[6], 4.2, f"{row['Inv. Final']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[7], 4.2, f"{row['Backlog']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[8], 4.2, f"{row['Ventas Perdidas']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[9], 4.2, f"{row['Nivel Servicio %']:.0f}%", 1, 0, "C", True)
        pdf.cell(col_widths[10], 4.2, f"{row['Costo MO']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[11], 4.2, f"{row['Margen Bruto']:,.0f}", 1, 0, "R", True)
        pdf.cell(col_widths[12], 4.2, f"{row['Flujo Descontado']:,.0f}", 1, 1, "R", True)

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_fill_color(235, 240, 245)
    pdf.cell(col_widths[0] + col_widths[1], 5, "TOTAL ANUAL", 1, 0, "C", True)
    pdf.cell(col_widths[2], 5, f"{df_weekly['Demanda'].sum():,.0f}", 1, 0, "R", True)
    pdf.cell(col_widths[3], 5, "-", 1, 0, "C", True)
    pdf.cell(col_widths[4], 5, f"{df_weekly['Producción'].sum():,.0f}", 1, 0, "R", True)
    pdf.cell(col_widths[5], 5, f"{df_weekly['Atendido'].sum():,.0f}", 1, 0, "R", True)
    pdf.cell(col_widths[6], 5, "-", 1, 0, "C", True)
    pdf.cell(col_widths[7], 5, "-", 1, 0, "C", True)
    pdf.cell(col_widths[8], 5, f"{df_weekly['Ventas Perdidas'].sum():,.0f}", 1, 0, "R", True)
    pdf.cell(col_widths[9], 5, f"{df_weekly['Atendido'].sum() / df_weekly['Demanda'].sum() * 100:.1f}%", 1, 0, "C", True)
    pdf.cell(col_widths[10], 5, f"{df_weekly['Costo MO'].sum():,.0f}", 1, 0, "R", True)
    pdf.cell(col_widths[11], 5, f"{df_weekly['Margen Bruto'].sum():,.0f}", 1, 0, "R", True)
    pdf.cell(col_widths[12], 5, f"{df_weekly['Flujo Descontado'].sum():,.0f}", 1, 1, "R", True)

    return bytes(pdf.output())
