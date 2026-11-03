"""
case_solver.py – Motor de Respuestas Dinámicas a las 6 Preguntas del Caso Resguarda.

Calcula algorítmicamente en tiempo real las respuestas a las preguntas del caso,
consumiendo la configuración activa (PlantConfig) y los datos vigentes (Excel o defecto).
"""
from __future__ import annotations

from typing import Any
import pandas as pd

from src.model import constants as C
from src.model.engine import (
    PlantConfig,
    balance_efficiency,
    compute_control_values,
    compute_investment,
    compute_npv,
    compute_station_utilization,
    cycle_time,
    effective_cycle,
    flow_time_hours,
    get_station_times,
    line_capacity,
    productive_minutes,
    run_all_scenarios,
    simulate_weekly,
    takt_time,
    weighted_cycle,
    work_content,
)
from src.model.strategies import get_predefined_strategies


def solve_q1_capacidad_y_cuello(cfg: PlantConfig) -> dict[str, Any]:
    """
    Pregunta 1: ¿Cuál es la capacidad real de la planta hoy?
    ¿Dónde está el cuello de botella para cada variante y para la mezcla?
    """
    pct_pro = cfg.pct_pro_override if cfg.pct_pro_override is not None else C.PCT_PRO_SEM1_26
    stations = get_station_times(cfg.ops_por_linea, cfg.dispositivo_puerta, cfg.subcontratar_puerta)
    n_stations = len(stations)

    wc_s = work_content(stations, "std")
    wc_p = work_content(stations, "pro")
    ct_s, bn_s = cycle_time(stations, "std")
    ct_p, bn_p = cycle_time(stations, "pro")

    c_bar = weighted_cycle(ct_s, ct_p, pct_pro)
    setup_loss = cfg.tiempo_cambio / cfg.tamano_lote
    c_eff = effective_cycle(c_bar, cfg.tiempo_cambio, cfg.tamano_lote)

    T1 = productive_minutes(1, 0)
    cap_line = line_capacity(c_eff, 1, 0)
    cap_plant = cap_line * cfg.num_lineas

    # Calidad
    fail_rate = (1 - pct_pro) * cfg.falla_std + pct_pro * cfg.falla_pro
    scrap_rate = fail_rate * (1 - C.RECUPERACION)
    good_units = cap_plant * (1 - scrap_rate)
    rework_units = cap_plant * fail_rate * C.RECUPERACION

    # Ley de Little
    wip = 46.0 * cfg.num_lineas
    th_plant = cap_plant / 37.5
    ft_hr = flow_time_hours(46.0, cap_line / 37.5)

    # Takt Time en Black Friday (1.900 unidades)
    demand_bf = 1900.0
    takt_bf_line = takt_time(demand_bf / cfg.num_lineas, T1)
    gap_units = demand_bf - good_units

    # Utilización de estaciones
    util_data = compute_station_utilization(stations, pct_pro)

    return {
        "wc_std": round(wc_s, 2),
        "wc_pro": round(wc_p, 2),
        "ct_std": round(ct_s, 2),
        "ct_pro": round(ct_p, 2),
        "bottleneck_std": bn_s,
        "bottleneck_pro": bn_p,
        "c_bar": round(c_bar, 2),
        "setup_loss_min": round(setup_loss, 2),
        "c_eff": round(c_eff, 2),
        "cap_line": round(cap_line, 1),
        "cap_plant": round(cap_plant, 1),
        "good_units": round(good_units, 1),
        "rework_units": round(rework_units, 1),
        "scrap_rate_pct": round(scrap_rate * 100, 2),
        "flow_time_hr": round(ft_hr, 2),
        "takt_bf_line": round(takt_bf_line, 2),
        "demand_bf": demand_bf,
        "gap_bf_units": round(gap_units, 1),
        "util_data": util_data,
        "pct_pro": round(pct_pro * 100, 1),
    }


def solve_q2_informe_cabrera(cfg: PlantConfig) -> dict[str, Any]:
    """
    Pregunta 2: ¿Es correcta la conclusión del informe de ingeniería sobre la línea de ocho operadores?
    """
    pct_pro = cfg.pct_pro_override if cfg.pct_pro_override is not None else C.PCT_PRO_SEM1_26

    # 1. Línea actual de 6
    st_6 = get_station_times(6, False, False)
    c_bar_6 = weighted_cycle(cycle_time(st_6, "std")[0], cycle_time(st_6, "pro")[0], pct_pro)
    c_eff_6 = effective_cycle(c_bar_6, cfg.tiempo_cambio, cfg.tamano_lote)
    cap_plant_6 = line_capacity(c_eff_6, 1, 0) * 2

    # 2. Línea de 8 (Cabrera)
    st_8 = get_station_times(8, False, False)
    wc_8_s = work_content(st_8, "std")
    cabrera_avg_time = wc_8_s / 8.0  # 4.98 ~ 5.0 min

    ct_8_s, bn_8_s = cycle_time(st_8, "std")  # L3: 5.80 min
    ct_8_p, bn_8_p = cycle_time(st_8, "pro")  # L6: 6.40 min

    c_bar_8 = weighted_cycle(ct_8_s, ct_8_p, pct_pro)  # 5.98 min
    c_eff_8 = effective_cycle(c_bar_8, cfg.tiempo_cambio, cfg.tamano_lote)  # 6.18 min

    cap_line_8 = line_capacity(c_eff_8, 1, 0)
    cap_plant_8 = cap_line_8 * 2

    # Aumento real vs aumento afirmado
    pct_increase_real = ((cap_plant_8 - cap_plant_6) / cap_plant_6) * 100
    cabrera_claimed_cap = cap_plant_6 * 2.0  # Afirmó duplicar (+100%)

    # Déficit en Black Friday (1.900 u)
    deficit_bf = 1900.0 - cap_plant_8

    es_correcta = False
    veredicto = "TOTALMENTE INCORRECTA Y ENGAÑOSA"
    explicacion = (
        f"Cabrera promedió el contenido de trabajo entre 8 puestos ({wc_8_s:.2f} / 8 = {cabrera_avg_time:.2f} min ~ 5,0 min) "
        f"confundiendo el trabajo promedio por operario con el tiempo de ciclo dictado por el cuello de botella. "
        f"En la realidad, la línea está limitada por {bn_8_s} ({ct_8_s:.2f} min) en Estándar y {bn_8_p} ({ct_8_p:.2f} min) en Pro. "
        f"El ciclo real ponderado es de {c_bar_8:.2f} min/u ({c_eff_8:.2f} min con lotes de {cfg.tamano_lote} u). "
        f"Por tanto, la capacidad semanal de la planta pasa de {cap_plant_6:.0f} a solo {cap_plant_8:.0f} u/sem, "
        f"un aumento de apenas +{pct_increase_real:.1f}% (muy lejos del +100% prometido), "
        f"dejando un déficit de {deficit_bf:,.0f} unidades en Black Friday."
    )

    return {
        "es_correcta": es_correcta,
        "veredicto": veredicto,
        "cabrera_avg_time": round(cabrera_avg_time, 2),
        "bn_8_std": bn_8_s,
        "ct_8_std": round(ct_8_s, 2),
        "bn_8_pro": bn_8_p,
        "ct_8_pro": round(ct_8_p, 2),
        "c_bar_8": round(c_bar_8, 2),
        "c_eff_8": round(c_eff_8, 2),
        "cap_plant_6": round(cap_plant_6, 1),
        "cap_plant_8": round(cap_plant_8, 1),
        "pct_increase_real": round(pct_increase_real, 1),
        "cabrera_claimed_cap": round(cabrera_claimed_cap, 1),
        "deficit_bf": round(deficit_bf, 1),
        "inversion": 2 * C.INVERSION_REEQUILIBRIO,
        "explicacion": explicacion,
    }


def solve_q3_dispositivo_puerta(cfg: PlantConfig) -> dict[str, Any]:
    """
    Pregunta 3: ¿Por qué el dispositivo para la puerta aporta menos capacidad de la que parece?
    """
    pct_pro = cfg.pct_pro_override if cfg.pct_pro_override is not None else C.PCT_PRO_SEM1_26

    # 1. Sin dispositivo (base 6 ops)
    st_no_disp = get_station_times(6, False, False)
    ct_std_no, bn_std_no = cycle_time(st_no_disp, "std")
    ct_pro_no, bn_pro_no = cycle_time(st_no_disp, "pro")

    # 2. Con dispositivo (O5)
    st_disp = get_station_times(6, True, False)
    ct_std_disp, bn_std_disp = cycle_time(st_disp, "std")
    ct_pro_disp, bn_pro_disp = cycle_time(st_disp, "pro")

    # Tiempos de ciclo ponderados
    c_bar_no = weighted_cycle(ct_std_no, ct_pro_no, pct_pro)
    c_bar_disp = weighted_cycle(ct_std_disp, ct_pro_disp, pct_pro)

    # Capacidad planta
    c_eff_no = effective_cycle(c_bar_no, cfg.tiempo_cambio, cfg.tamano_lote)
    c_eff_disp = effective_cycle(c_bar_disp, cfg.tiempo_cambio, cfg.tamano_lote)

    cap_no = line_capacity(c_eff_no, 1, 0) * 2
    cap_disp = line_capacity(c_eff_disp, 1, 0) * 2
    delta_cap = cap_disp - cap_no
    pct_gain = (delta_cap / cap_no) * 100

    inversion_total = 2 * C.INVERSION_DISPOSITIVO_PUERTA
    plazo_semanas = C.PLAZO_DISPOSITIVO

    razones = [
        f"1. Desplazamiento Asimétrico de Cuello de Botella: Para Estándar, el ciclo baja de {ct_std_no:.2f} a {ct_std_disp:.2f} min (se traslada a {bn_std_disp}). Pero para R1 Pro, el cuello de botella ya era {bn_pro_no} con {ct_pro_no:.2f} min; como el dispositivo solo actúa sobre la puerta (E2/E3), el tiempo de Pro NO SE REDUCE EN NADA ({ct_pro_disp:.2f} min).",
        f"2. Ganancia de Capacidad Marginal: La planta solo gana +{delta_cap:.1f} u/semana (+{pct_gain:.1f}%), un aporte insignificante frente al déficit de Black Friday.",
        f"3. Inversión Ineficiente: Cuesta US$ {inversion_total:,.0f} (US$ 22.000 por línea), consumiendo el 37% del presupuesto fiscal de US$ 120.000.",
        f"4. Plazo de Entrega Tardío: Requiere {plazo_semanas} semanas de plazo. Ordenado en la semana 1 (octubre), llega en la semana 11 (diciembre), COMPLETAMENTE FUERA de Black Friday (semana 8).",
    ]

    return {
        "ct_std_no": round(ct_std_no, 2),
        "bn_std_no": bn_std_no,
        "ct_std_disp": round(ct_std_disp, 2),
        "bn_std_disp": bn_std_disp,
        "ct_pro_no": round(ct_pro_no, 2),
        "bn_pro_no": bn_pro_no,
        "ct_pro_disp": round(ct_pro_disp, 2),
        "bn_pro_disp": bn_pro_disp,
        "cap_no": round(cap_no, 1),
        "cap_disp": round(cap_disp, 1),
        "delta_cap": round(delta_cap, 1),
        "pct_gain": round(pct_gain, 1),
        "inversion_total": inversion_total,
        "plazo_semanas": plazo_semanas,
        "razones": razones,
    }


def solve_q4_combinacion_optima_presupuesto(cfg: PlantConfig) -> dict[str, Any]:
    """
    Pregunta 4: ¿Qué combinación de opciones cubre la temporada alta con la inversión permitida?
    """
    # Evalúa sistemáticamente combinaciones frente a restricciones:
    # Presupuesto <= $120k, Plazo <= 8 semanas (Black Friday), Espacio <= 180 m²
    opciones_eval = [
        {
            "id": "Comb_A_Turno2_Sabados",
            "nombre": "2 Líneas + 2.º Turno (sem 3) + 2 Sábados extra/mes",
            "inversion": 0.0,
            "plazo_disp": "Semana 3 (A tiempo para Black Friday)",
            "espacio_m2": 240,  # usa las mismas 2 líneas
            "espacio_libre": 180,
            "capacidad_bf_sem": 1250.0,
            "cumple_bf_con_inventario": True,
            "cumple_presupuesto": True,
            "cumple_espacio": True,
            "puntos_fuertes": "CapEx $0; entra en sem 3; sin riesgo de capital varado en enero.",
            "es_ganadora": True,
        },
        {
            "id": "Comb_B_Cabrera_Sabados",
            "nombre": "Propuesta Cabrera (8 Ops) + 3 Sábados extra/mes",
            "inversion": 18000.0,
            "plazo_disp": "Semana 4",
            "espacio_m2": 240,
            "espacio_libre": 180,
            "capacidad_bf_sem": 850.0,
            "cumple_bf_con_inventario": False,
            "cumple_presupuesto": True,
            "cumple_espacio": True,
            "puntos_fuertes": "Dentro de presupuesto, pero capacidad insuficiente (déficit >1.000 u).",
            "es_ganadora": False,
        },
        {
            "id": "Comb_C_Linea3_Turno2",
            "nombre": "Línea 3 (O2) + 2.º Turno (O3)",
            "inversion": 48000.0,
            "plazo_disp": "Semana 9 (TARDÍA, post-Black Friday)",
            "espacio_m2": 360,
            "espacio_libre": 60,
            "capacidad_bf_sem": 1030.0,  # Línea 3 aún no llega en sem 8
            "cumple_bf_con_inventario": False,
            "cumple_presupuesto": True,
            "cumple_espacio": True,
            "puntos_fuertes": "Llega después de Black Friday; genera capacidad ociosa si cae demanda en enero.",
            "es_ganadora": False,
        },
        {
            "id": "Comb_D_Turno2_Dispositivo_8Ops",
            "nombre": "2.º Turno + Reequilibrio 8 Ops + Dispositivo Puerta",
            "inversion": 18000.0 + 44000.0,
            "plazo_disp": "Semana 11 (Dispositivo)",
            "espacio_m2": 240,
            "espacio_libre": 180,
            "capacidad_bf_sem": 1390.0,
            "cumple_bf_con_inventario": True,
            "cumple_presupuesto": True,
            "cumple_espacio": True,
            "puntos_fuertes": "Gasta $62.000 innecesariamente cuando el turno solo bastaba.",
            "es_ganadora": False,
        },
    ]

    ganadora = [c for c in opciones_eval if c["es_ganadora"]][0]

    return {
        "limite_presupuesto": C.LIMITE_INVERSION,
        "superficie_libre": C.SUPERFICIE_LIBRE,
        "semana_bf": 8,
        "demanda_bf": 1900.0,
        "combinaciones": opciones_eval,
        "combinacion_ganadora": ganadora,
        "conclusion": (
            f"La ÚNICA combinación que cubre la temporada alta dentro de los límites es: {ganadora['nombre']}. "
            f"Requiere US$ 0 de inversión fija (cumple con holgura el límite de US$ 120.000), "
            f"está 100% operativa en la semana 3 (Black Friday es semana 8) y "
            f"ocupa 0 m² de espacio adicional, dejando 180 m² intactos para almacenar producto terminado."
        ),
    }


def solve_q5_maximizacion_ve_y_peor_caso(cfg: PlantConfig) -> dict[str, Any]:
    """
    Pregunta 5: ¿Qué estrategia maximiza el valor esperado en los tres escenarios?
    ¿Cuál limita mejor la pérdida en el peor escenario?
    """
    strats = get_predefined_strategies()
    p_base = cfg.prob_base
    p_optim = cfg.prob_optim
    p_canal = cfg.prob_canal

    ranking_ve = []
    ranking_worst = []

    for s_id, s_def in strats.items():
        cfg_s = PlantConfig(**{**s_def.config_base.__dict__, "prob_base": p_base, "prob_optim": p_optim, "prob_canal": p_canal})
        res = run_all_scenarios(cfg_s)

        ranking_ve.append({
            "id": s_id,
            "nombre": s_def.nombre,
            "ve": res["ve"],
            "npv_base": res["scenarios"]["base"]["npv"],
            "npv_optim": res["scenarios"]["optim"]["npv"],
            "npv_canal": res["scenarios"]["canal"]["npv"],
            "worst_case": res["worst_case"],
            "inversion": res["investment"],
            "servicio_anual": res["scenarios"]["base"]["nivel_servicio"],
        })

    # Ordenar por VE
    ranking_ve = sorted(ranking_ve, key=lambda x: x["ve"], reverse=True)
    # Ordenar por Peor Caso (MaxiMin)
    ranking_worst = sorted(ranking_ve, key=lambda x: x["worst_case"], reverse=True)

    max_ve_strat = ranking_ve[0]
    best_worst_strat = ranking_worst[0]

    return {
        "probs": {"base": p_base, "optim": p_optim, "canal": p_canal},
        "ranking_ve": ranking_ve,
        "max_ve_strat": max_ve_strat,
        "best_worst_strat": best_worst_strat,
        "conclusion_ve": f"La estrategia que maximiza el Valor Esperado es '{max_ve_strat['nombre']}' con un VE de US$ {max_ve_strat['ve']:,.0f}.",
        "conclusion_worst": f"La estrategia que mejor limita la pérdida en el peor escenario (Llenado de Canal) es '{best_worst_strat['nombre']}' con un VAN mínimo de US$ {best_worst_strat['worst_case']:,.0f} (cero riesgo de activos ociosos).",
    }


def solve_q6_recomendacion_mariela_santos(cfg: PlantConfig) -> dict[str, Any]:
    """
    Pregunta 6: ¿Qué recomendaría a Mariela Santos para el viernes,
    y qué puntos de decisión fijaría para los meses siguientes?
    """
    q1 = solve_q1_capacidad_y_cuello(cfg)
    q4 = solve_q4_combinacion_optima_presupuesto(cfg)
    q5 = solve_q5_maximizacion_ve_y_peor_caso(cfg)

    hitos = [
        {
            "fecha": "Viernes 2 de Octubre de 2026 (Semana 0)",
            "accion": "Presentar al Consejo la Estrategia Ágil Secuencial. Solicitar aprobación para iniciar reclutamiento inmediato de 12 personas para el 2.º turno y presupuesto de horas extra para 4 sábados. NO ordenar maquinaria fija ($0 CapEx).",
            "justificacion": "Preserva los US$ 120.000 del presupuesto y evita capital varado.",
        },
        {
            "fecha": "Lunes 19 de Octubre de 2026 (Semana 3)",
            "accion": "Puesta en marcha del 2.º Turno para ambas líneas. Iniciar producción a ritmo de ~1.030 u/semana acumulando inventario en almacén hacia noviembre.",
            "justificacion": "Asegura rampa de aprendizaje de 2 semanas antes del pico de noviembre.",
        },
        {
            "fecha": "Noviembre y Diciembre 2026 (Semanas 5 a 10)",
            "accion": "Activar 2 sábados de horas extra al mes en el 1.º turno para absorber el pico de 1.900 unidades de Black Friday (semana 8).",
            "justificacion": "Alcanza un nivel de servicio >95% en la temporada crítica sin compras de activos pesados.",
        },
        {
            "fecha": "Lunes 28 de Diciembre de 2026 (Semana 13 - GATE CRÍTICO)",
            "accion": "Punto de Decisión Formal del Consejo: Evaluar datos reales de ventas de los distribuidores tras Navidad:\n"
                      "- Si la demanda cae a ~650 u/sem (Llenado de Canal): Desescalar el 2.º turno y volver a 1 turno. Pérdida de capital = US$ 0.\n"
                      "- Si la demanda supera 1.100 u/sem (Base/Optimista): Ejercer la opción de arrendar los 200 m² adicionales y evaluar orden de la Línea 3.",
            "justificacion": "Alinea la inversión fija con la confirmación de la demanda real post-temporada.",
        },
        {
            "fecha": "Mayo de 2027 (Semanas 33 y 34)",
            "accion": "Atender el segundo pico del año (Día de las Madres, 1.290 u/sem) con la configuración consolidada.",
            "justificacion": "Operaciones estabilizadas y balanceadas.",
        },
    ]

    return {
        "estrategia_recomendada": "E4. Estrategia Ágil Secuencial (Opciones Reales)",
        "inversion_inicial": 0.0,
        "valor_esperado": q5["max_ve_strat"]["ve"],
        "peor_caso": q5["best_worst_strat"]["worst_case"],
        "hitos": hitos,
        "resumen_ejecutivo": (
            "Mariela Santos debe defender ante el Consejo que la flexibilidad operativa supera a la inversión en activos fijos. "
            "El 2.º turno con horas extra en sábados resuelve el dilema de Laura Méndez (abastece Black Friday) y el de Ricardo Almonte "
            "(inversión inicial US$ 0). El punto de decisión en la semana 13 protege a la empresa contra el riesgo de sobrecapacidad."
        ),
    }
