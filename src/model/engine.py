"""
engine.py – Motor analítico de simulación para Resguarda.

Calcula capacidad, cuello de botella, calidad, inventarios y flujo
financiero semanal para cualquier combinación de palancas.

Todos los valores de control del caso se reproducen con exactitud.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.model import constants as C


# ═══════════════════════════════════════════════
# Data-classes de configuración
# ═══════════════════════════════════════════════
@dataclass
class PlantConfig:
    """Configuración completa de la planta para una simulación."""
    # Líneas
    num_lineas: int = 2
    ops_por_linea: int = 6          # 6 u 8
    semana_linea3: int = 99         # semana en que entra la 3.ª línea (99=nunca)

    # Turnos
    num_turnos: int = 1
    semana_turno2: int = 99
    semana_turno3: int = 99

    # Sábados
    sabados_mes: int = 0            # 0–3

    # Células
    num_celulas: int = 0
    semana_celulas: int = 99
    penalizacion_polivalencia: float = C.PENALIZACION_POLIVALENCIA

    # Opciones de mejora
    dispositivo_puerta: bool = False
    semana_dispositivo: int = 99
    subcontratar_puerta: bool = False
    semana_subcontratacion: int = 99

    # Lotes y cambio de variante
    tamano_lote: int = C.LOTE_DEFAULT
    tiempo_cambio: float = C.CAMBIO_VARIANTE_DEFAULT

    # Mezcla y calidad
    pct_pro_override: float | None = None   # None usa el default por semana
    falla_std: float = C.FALLA_STD
    falla_pro: float = C.FALLA_PRO

    # Escenario
    escenario: str = "base"   # base | optim | canal

    # Probabilidades editables
    prob_base: float = C.PROB_BASE
    prob_optim: float = C.PROB_OPTIMISTA
    prob_canal: float = C.PROB_CANAL

    # ── Parámetros Económicos y Técnicos Editables (22 Parámetros del Modelo) ──
    precio_neto_std: float = C.PRECIO_STD
    precio_neto_pro: float = C.PRECIO_PRO
    materiales_std: float = C.MATERIAL_STD
    materiales_pro: float = C.MATERIAL_PRO
    pct_pro_sem1_26: float = C.PCT_PRO_SEM1_26
    pct_pro_sem27_52: float = C.PCT_PRO_SEM27_52
    devolucion_garantia_pct: float = C.DEVOLUCION_PCT
    costo_garantia: float = C.DEVOLUCION_COSTO
    inventario_inicial: float = C.INVENTARIO_INICIAL
    inventario_maximo: float = C.INVENTARIO_MAX_PT
    costo_mantener_inv_anual: float = C.COSTO_MANTENER_INV
    tasa_descuento_anual: float = C.TASA_DESCUENTO_ANUAL
    limite_inversion_fiscal: float = C.LIMITE_INVERSION
    fijos_planta_semanal: float = C.FIJOS_PLANTA_SEMANAL
    fijo_turno_adicional: float = C.COSTO_FIJO_TURNO_EXTRA
    salario_supervisor: float = C.SUPERVISOR_SEMANAL
    cargas_sociales_pct: float = C.CARGAS_SOCIALES
    tasa_recuperacion_retrabajo: float = C.RECUPERACION
    lote_produccion_defecto: int = C.LOTE_DEFAULT
    tiempo_cambio_lote: float = C.CAMBIO_VARIANTE_DEFAULT


def build_plant_config(**overrides) -> PlantConfig:
    """
    Construye una instancia de PlantConfig integrando los 22 parámetros activos
    de la sesión o del Excel, permitiendo sobreescribir palancas operativas puntuales.
    """
    try:
        from src.model.data_loader import get_active_parameters_dict
        active_p = get_active_parameters_dict()
    except Exception:
        active_p = {}

    valid_fields = set(PlantConfig.__dataclass_fields__.keys())
    filtered = {k: v for k, v in active_p.items() if k in valid_fields}
    filtered.update(overrides)
    return PlantConfig(**filtered)


# ═══════════════════════════════════════════════
# Funciones de cálculo de capacidad instantánea
# ═══════════════════════════════════════════════

def get_station_times(ops: int, dispositivo: bool, subcontratacion: bool) -> list[dict]:
    """Devuelve la lista de estaciones con tiempos según la configuración."""
    if ops == 8:
        base = {k: {**v, "id": k} for k, v in C.ESTACIONES_8.items()}
        if dispositivo:
            for key, val in C.TIEMPOS_O5_LINEA8.items():
                if key in base:
                    base[key]["t_std"] = val
                    base[key]["t_pro"] = val
        return list(base.values())
    else:
        # Línea de 6 (o 5 si se subcontrata puerta)
        base = {k: {**v, "id": k} for k, v in C.ESTACIONES_6.items()}
        if dispositivo:
            for key, val in C.TIEMPOS_O5_LINEA6.items():
                if key in base:
                    base[key]["t_std"] = val
                    base[key]["t_pro"] = val
        if subcontratacion:
            # Desaparece E2; E3 baja
            base.pop("E2", None)
            for key, val in C.TIEMPOS_O6.items():
                if key in base:
                    base[key]["t_std"] = val
                    base[key]["t_pro"] = val
        return list(base.values())


def work_content(stations: list[dict], variant: str) -> float:
    """Contenido de trabajo total (suma de tiempos) para una variante."""
    key = "t_std" if variant == "std" else "t_pro"
    return sum(s[key] for s in stations)


def cycle_time(stations: list[dict], variant: str) -> tuple[float, str]:
    """Tiempo de ciclo (estación cuello de botella) y nombre de esa estación."""
    key = "t_std" if variant == "std" else "t_pro"
    bottleneck = max(stations, key=lambda s: s[key])
    return bottleneck[key], bottleneck["op"]


def compute_station_utilization(stations: list[dict], pct_pro: float = 0.30) -> list[dict]:
    """
    Calcula la utilización de cada estación respecto al cuello de botella de la línea.
    U_i = t_i / ct_bottleneck * 100%
    Para Estándar, Pro y Mezcla Ponderada.
    """
    ct_std, _ = cycle_time(stations, "std")
    ct_pro, _ = cycle_time(stations, "pro")

    weighted_station_times = [
        (1 - pct_pro) * s["t_std"] + pct_pro * s["t_pro"]
        for s in stations
    ]
    ct_weighted = max(weighted_station_times) if weighted_station_times else 1.0

    result = []
    for idx, s in enumerate(stations, 1):
        t_w = (1 - pct_pro) * s["t_std"] + pct_pro * s["t_pro"]
        u_std = (s["t_std"] / ct_std * 100) if ct_std > 0 else 0
        u_pro = (s["t_pro"] / ct_pro * 100) if ct_pro > 0 else 0
        u_weighted = (t_w / ct_weighted * 100) if ct_weighted > 0 else 0
        is_bn = (abs(t_w - ct_weighted) < 1e-6) or (round(u_weighted, 1) >= 99.9)

        if is_bn:
            estado = "🔴 Cuello de Botella (100%)"
        elif u_weighted >= 80.0:
            estado = "🟡 Alta Carga"
        elif u_weighted >= 65.0:
            estado = "🟢 Balanceada"
        else:
            estado = "⚪ Subutilizada"

        op_name = s.get("op", f"Estación {idx}")
        st_id = s.get("id", f"E{idx}")
        result.append({
            "operacion": op_name,
            "name": op_name,
            "station_id": st_id,
            "t_std": s["t_std"],
            "t_pro": s["t_pro"],
            "time_std": s["t_std"],
            "time_pro": s["t_pro"],
            "t_ponderado": round(t_w, 2),
            "weighted_time": round(t_w, 2),
            "util_std_pct": round(u_std, 1),
            "util_pro_pct": round(u_pro, 1),
            "util_ponderada_pct": round(u_weighted, 1),
            "utilization_pct": round(u_weighted, 1),
            "tiempo_ocio_ponderado": round(ct_weighted - t_w, 2),
            "estado": estado,
            "is_bottleneck": is_bn,
        })
    return result


def weighted_cycle(c_std: float, c_pro: float, pct_pro: float) -> float:
    """Ciclo medio ponderado por mezcla."""
    return (1 - pct_pro) * c_std + pct_pro * c_pro


def effective_cycle(c_bar: float, setup: float, lot: int) -> float:
    """Ciclo efectivo incluyendo pérdida por cambio de variante."""
    return c_bar + setup / lot


def productive_minutes(
    turno: int = 1,
    sabados_mes: float = 0,
) -> float:
    """Minutos productivos semanales por línea para un turno dado."""
    if turno == 1:
        base = C.HORAS_PRODUCTIVAS_1_2 * 60 * C.DIAS_SEMANA
    elif turno == 2:
        base = C.HORAS_PRODUCTIVAS_1_2 * 60 * C.DIAS_SEMANA * C.RENDIMIENTO_T2
    else:
        base = C.HORAS_PRODUCTIVAS_3T * 60 * C.DIAS_SEMANA * C.RENDIMIENTO_T3
    # Sábados solo aplican al turno 1
    if turno == 1 and sabados_mes > 0:
        sabados_sem = sabados_mes * 12 / 52  # sábados promedio por semana
        base += sabados_sem * C.HORAS_PROD_SABADO * 60
    return base


def line_capacity(
    c_eff: float,
    turno: int = 1,
    sabados_mes: float = 0,
) -> float:
    """Capacidad bruta de UNA línea en UN turno (unidades/semana)."""
    T = productive_minutes(turno, sabados_mes if turno == 1 else 0)
    return T / c_eff


def cell_capacity_per_worker(
    wc_avg: float,
    penalizacion: float,
    turno: int = 1,
) -> float:
    """Capacidad de un trabajador de célula por semana."""
    T = productive_minutes(turno, 0)
    return T / (wc_avg * (1 + penalizacion))


def balance_efficiency(wc: float, n_stations: int, ct: float) -> float:
    """Eficiencia del balance de línea."""
    return wc / (n_stations * ct)


def good_units_factor(
    pct_pro: float,
    falla_std: float,
    falla_pro: float,
    recuperacion: float = C.RECUPERACION,
) -> float:
    """Factor de unidades buenas (multiplicar por capacidad bruta)."""
    fail_rate = (1 - pct_pro) * falla_std + pct_pro * falla_pro
    return 1 - fail_rate * (1 - recuperacion)


def rework_units_factor(
    pct_pro: float,
    falla_std: float,
    falla_pro: float,
    recuperacion: float = C.RECUPERACION,
) -> float:
    """Factor de unidades a retrabajar."""
    fail_rate = (1 - pct_pro) * falla_std + pct_pro * falla_pro
    return fail_rate * recuperacion


def flow_time_hours(wip: float, throughput_per_hour: float) -> float:
    """Tiempo de flujo por Ley de Little (horas)."""
    if throughput_per_hour <= 0:
        return 0.0
    return wip / throughput_per_hour


def takt_time(demand_per_line: float, minutes_available: float) -> float:
    """Takt time en minutos."""
    if demand_per_line <= 0:
        return float("inf")
    return minutes_available / demand_per_line


# ═══════════════════════════════════════════════
# Cálculo de costes laborales
# ═══════════════════════════════════════════════

def labor_cost_weekly(
    num_lineas: int,
    ops_por_linea: int,
    num_turnos: int,
    num_celulas: int,
    subcontratar_puerta: bool,
    sabados_mes: float,
    cargas_sociales: float = C.CARGAS_SOCIALES,
    supervisor_semanal: float = C.SUPERVISOR_SEMANAL,
) -> float:
    """Coste semanal total de mano de obra (con cargas + supervisor)."""
    # Operadores y técnicos por línea
    if subcontratar_puerta:
        ops_line = ops_por_linea - 1  # -1 por E2
    else:
        ops_line = ops_por_linea

    if ops_por_linea == 8:
        tecnicos_line = 1
        operadores_line = 7
    else:
        tecnicos_line = 1
        operadores_line = ops_line - 1  # E5 es técnico

    total_wage = 0.0

    for t in range(1, num_turnos + 1):
        if t == 1:
            prima = 0.0
            h_pag = C.HORAS_PAGADAS_1_2
        elif t == 2:
            prima = C.PRIMA_T2
            h_pag = C.HORAS_PAGADAS_1_2
        else:
            prima = C.PRIMA_T3
            h_pag = C.HORAS_PAGADAS_3T

        h_sem = h_pag * C.DIAS_SEMANA

        # Operadores de línea
        total_wage += num_lineas * operadores_line * C.SALARIO_OPERADOR * (1 + prima) * h_sem
        # Técnicos de prueba
        total_wage += num_lineas * tecnicos_line * C.SALARIO_TECNICO * (1 + prima) * h_sem
        # Manipulador (1 por turno, atiende hasta 3 líneas / 6 células)
        manip = 1
        total_wage += manip * C.SALARIO_MANIPULADOR * (1 + prima) * h_sem
        # Técnico de retrabajo (1 por turno)
        total_wage += 1 * C.SALARIO_RETRABAJO * (1 + prima) * h_sem
        # Líder de turno (turnos 2 y 3)
        if t >= 2:
            total_wage += 1 * C.SALARIO_LIDER_TURNO * (1 + prima) * h_sem
        # Trabajadores de célula
        total_wage += num_celulas * C.TRABAJADORES_CELULA * C.SALARIO_CELULA * (1 + prima) * h_sem

    # Cargas sociales
    total_wage *= (1 + cargas_sociales)
    # Supervisor (fijo, 1 para toda la planta)
    total_wage += supervisor_semanal

    # Sábados (recargo sobre turno 1 solamente)
    if sabados_mes > 0:
        sab_sem = sabados_mes * 12 / 52
        h_sab = C.HORAS_PAG_SABADO
        # Solo personal del turno 1
        wage_sab = 0.0
        wage_sab += num_lineas * operadores_line * C.SALARIO_OPERADOR * h_sab
        wage_sab += num_lineas * tecnicos_line * C.SALARIO_TECNICO * h_sab
        wage_sab += 1 * C.SALARIO_MANIPULADOR * h_sab
        wage_sab += 1 * C.SALARIO_RETRABAJO * h_sab
        wage_sab += num_celulas * C.TRABAJADORES_CELULA * C.SALARIO_CELULA * h_sab
        wage_sab *= (1 + cargas_sociales) * (1 + C.RECARGO_SABADO)
        total_wage += wage_sab * sab_sem

    return total_wage


# ═══════════════════════════════════════════════
# Métricas estáticas (valores de control)
# ═══════════════════════════════════════════════

@dataclass
class ControlValues:
    """Valores de control calculados para una configuración dada."""
    wc_std: float = 0.0
    wc_pro: float = 0.0
    ct_std: float = 0.0
    ct_pro: float = 0.0
    bottleneck_std: str = ""
    bottleneck_pro: str = ""
    eff_std: float = 0.0
    eff_pro: float = 0.0
    c_bar: float = 0.0
    c_eff: float = 0.0
    cap_line: float = 0.0
    cap_plant: float = 0.0
    good_units: float = 0.0
    rework_units: float = 0.0
    flow_time_hr: float = 0.0
    takt_wk8: float = 0.0
    labor_weekly: float = 0.0
    labor_per_good: float = 0.0
    margin_avg: float = 0.0
    cap_2shifts: float = 0.0


def compute_control_values(cfg: PlantConfig | None = None) -> ControlValues:
    """Calcula los valores de control para la configuración dada (o por defecto)."""
    if cfg is None:
        cfg = PlantConfig()

    pct_pro = cfg.pct_pro_override if cfg.pct_pro_override is not None else cfg.pct_pro_sem1_26

    stations = get_station_times(cfg.ops_por_linea, cfg.dispositivo_puerta, cfg.subcontratar_puerta)
    n_stations = len(stations)

    wc_s = work_content(stations, "std")
    wc_p = work_content(stations, "pro")
    ct_s, bn_s = cycle_time(stations, "std")
    ct_p, bn_p = cycle_time(stations, "pro")
    eff_s = balance_efficiency(wc_s, n_stations, ct_s)
    eff_p = balance_efficiency(wc_p, n_stations, ct_p)
    c_bar = weighted_cycle(ct_s, ct_p, pct_pro)
    c_eff = effective_cycle(c_bar, cfg.tiempo_cambio, cfg.tamano_lote)

    T1 = productive_minutes(1, 0)
    cap_line = T1 / c_eff
    cap_plant = cap_line * cfg.num_lineas

    gf = good_units_factor(pct_pro, cfg.falla_std, cfg.falla_pro, recuperacion=cfg.tasa_recuperacion_retrabajo)
    rf = rework_units_factor(pct_pro, cfg.falla_std, cfg.falla_pro, recuperacion=cfg.tasa_recuperacion_retrabajo)
    good = cap_plant * gf
    rework = cap_plant * rf

    throughput_hr = cap_line / (C.HORAS_PRODUCTIVAS_1_2 * C.DIAS_SEMANA)
    wip = 46.0
    ft = flow_time_hours(wip, throughput_hr)

    # Takt semana 8
    demand_wk8 = 1900
    takt_wk8 = takt_time(demand_wk8 / cfg.num_lineas, T1)

    labor = labor_cost_weekly(
        cfg.num_lineas, cfg.ops_por_linea, 1,
        0, cfg.subcontratar_puerta, 0,
        cargas_sociales=cfg.cargas_sociales_pct,
        supervisor_semanal=cfg.salario_supervisor,
    )
    lpu = labor / good if good > 0 else 0

    margin_std = cfg.precio_neto_std - cfg.materiales_std
    margin_pro = cfg.precio_neto_pro - cfg.materiales_pro
    margin = (1 - pct_pro) * margin_std + pct_pro * margin_pro

    # Cap con 2 turnos
    T2 = productive_minutes(2, 0)
    cap_2 = cfg.num_lineas * (T1 + T2) / c_eff

    return ControlValues(
        wc_std=round(wc_s, 2),
        wc_pro=round(wc_p, 2),
        ct_std=round(ct_s, 2),
        ct_pro=round(ct_p, 2),
        bottleneck_std=bn_s,
        bottleneck_pro=bn_p,
        eff_std=round(eff_s, 4),
        eff_pro=round(eff_p, 4),
        c_bar=round(c_bar, 2),
        c_eff=round(c_eff, 2),
        cap_line=round(cap_line, 1),
        cap_plant=round(cap_plant, 1),
        good_units=round(good, 1),
        rework_units=round(rework, 1),
        flow_time_hr=round(ft, 2),
        takt_wk8=round(takt_wk8, 2),
        labor_weekly=round(labor, 2),
        labor_per_good=round(lpu, 2),
        margin_avg=round(margin, 2),
        cap_2shifts=round(cap_2, 1),
    )


# ═══════════════════════════════════════════════
# Simulación semanal (52 semanas)
# ═══════════════════════════════════════════════

def simulate_weekly(cfg: PlantConfig) -> pd.DataFrame:
    """Ejecuta la simulación semana a semana y devuelve un DataFrame con los resultados."""
    demand_data = C.DEMANDA_SEMANAL
    rows = []

    inv_pt = cfg.inventario_inicial
    backlog = 0.0
    backlog_age = 0       # semanas que lleva el backlog más antiguo
    total_investment = 0.0

    tasa_semanal = (1 + cfg.tasa_descuento_anual) ** (1 / 52) - 1

    for wk_data in demand_data:
        sem = wk_data["sem"]
        fecha = wk_data["fecha"]

        # Demanda del escenario
        if cfg.escenario == "optim":
            demand = wk_data["optim"]
        elif cfg.escenario == "canal":
            demand = wk_data["canal"]
        else:
            demand = wk_data["base"]

        # % Pro según semana
        if cfg.pct_pro_override is not None:
            pct_pro = cfg.pct_pro_override
        else:
            pct_pro = cfg.pct_pro_sem1_26 if sem <= 26 else cfg.pct_pro_sem27_52

        # ── Configuración dinámica de la semana ──
        # Líneas activas
        n_lineas = cfg.num_lineas
        if sem >= cfg.semana_linea3:
            n_lineas = max(n_lineas, 3)

        # ¿Dispositivo activo?
        disp = cfg.dispositivo_puerta and sem >= cfg.semana_dispositivo
        subc = cfg.subcontratar_puerta and sem >= cfg.semana_subcontratacion

        stations = get_station_times(cfg.ops_por_linea, disp, subc)

        ct_s, _ = cycle_time(stations, "std")
        ct_p, _ = cycle_time(stations, "pro")
        c_bar_w = weighted_cycle(ct_s, ct_p, pct_pro)

        # Cambio de variante en células: 5 min
        if cfg.ops_por_linea == 6 and not subc:
            c_eff_line = effective_cycle(c_bar_w, cfg.tiempo_cambio, cfg.tamano_lote)
        elif subc:
            c_eff_line = effective_cycle(c_bar_w, cfg.tiempo_cambio, cfg.tamano_lote)
        else:
            c_eff_line = effective_cycle(c_bar_w, cfg.tiempo_cambio, cfg.tamano_lote)

        # ── Turnos activos ──
        turnos_activos = 1
        if sem >= cfg.semana_turno2:
            turnos_activos = max(turnos_activos, 2)
        if sem >= cfg.semana_turno3:
            turnos_activos = max(turnos_activos, 3)

        # ── Capacidad de líneas ──
        cap_lineas = 0.0
        for t in range(1, turnos_activos + 1):
            sab = cfg.sabados_mes if t == 1 else 0
            cap_lineas += n_lineas * line_capacity(c_eff_line, t, sab)

        # ── Capacidad de células ──
        cap_celulas = 0.0
        if cfg.num_celulas > 0 and sem >= cfg.semana_celulas:
            wc_s = work_content(stations, "std")
            wc_p = work_content(stations, "pro")
            wc_avg = (1 - pct_pro) * wc_s + pct_pro * wc_p
            c_eff_cell = effective_cycle(
                wc_avg * (1 + cfg.penalizacion_polivalencia),
                C.CAMBIO_VARIANTE_CELULA,
                cfg.tamano_lote,
            )
            for t in range(1, turnos_activos + 1):
                T_cell = productive_minutes(t, cfg.sabados_mes if t == 1 else 0)
                cap_celulas += cfg.num_celulas * C.TRABAJADORES_CELULA * (T_cell / (wc_avg * (1 + cfg.penalizacion_polivalencia)))

        cap_bruta = cap_lineas + cap_celulas

        # Límite de subcontratación
        if subc and cap_bruta > C.LIMITE_SUBCONTRATACION:
            pass  # El límite es sobre la puerta; la línea sigue operando normalmente

        # Calidad
        falla_s = cfg.falla_std
        falla_p = cfg.falla_pro
        if cfg.num_celulas > 0 and sem >= cfg.semana_celulas:
            falla_s = max(0, falla_s + C.EFECTO_CELULA_FALLA)
            falla_p = max(0, falla_p + C.EFECTO_CELULA_FALLA)

        gf = good_units_factor(pct_pro, falla_s, falla_p, recuperacion=cfg.tasa_recuperacion_retrabajo)
        rf = rework_units_factor(pct_pro, falla_s, falla_p, recuperacion=cfg.tasa_recuperacion_retrabajo)
        cap_buenas = cap_bruta * gf
        unidades_retrabajo = cap_bruta * rf

        # ── Balance de inventario y demanda ──
        demand_total = demand + backlog
        produccion = min(cap_buenas, max(demand_total, 0))

        # Disponible para vender = producción + inventario
        disponible = produccion + inv_pt
        atendido = min(disponible, demand_total)

        # Demanda no atendida
        no_atendido = max(demand_total - atendido, 0)

        # Separar demanda nueva no atendida del backlog
        demanda_nueva_no_atendida = max(demand - atendido + backlog, 0)
        if demanda_nueva_no_atendida < 0:
            demanda_nueva_no_atendida = 0

        # 50% espera (hasta 2 semanas), 50% se pierde
        nuevo_backlog_in = no_atendido * C.DEMANDA_ESPERA_PCT
        ventas_perdidas = no_atendido * (1 - C.DEMANDA_ESPERA_PCT)

        # Envejecimiento del backlog
        if backlog_age >= C.MAX_SEMANAS_ESPERA and backlog > 0:
            ventas_perdidas += backlog
            backlog = 0
            backlog_age = 0

        backlog = nuevo_backlog_in
        if backlog > 0:
            backlog_age += 1
        else:
            backlog_age = 0

        # Inventario final
        inv_pt = max(disponible - atendido, 0)
        inv_pt = min(inv_pt, cfg.inventario_maximo)

        # Nivel de servicio
        nivel_servicio = atendido / demand if demand > 0 else 1.0

        # ── Costes ──
        # Mano de obra
        n_cel_activas = cfg.num_celulas if sem >= cfg.semana_celulas else 0
        costo_mo = labor_cost_weekly(
            n_lineas, cfg.ops_por_linea, turnos_activos,
            n_cel_activas, subc, cfg.sabados_mes,
            cargas_sociales=cfg.cargas_sociales_pct,
            supervisor_semanal=cfg.salario_supervisor,
        )

        # Materiales
        costo_mat_unit = (1 - pct_pro) * cfg.materiales_std + pct_pro * cfg.materiales_pro
        costo_materiales = produccion * costo_mat_unit
        if subc:
            costo_materiales += produccion * C.SOBRECOSTO_SUBCONTRATACION

        # Fijos de planta
        costo_fijos = cfg.fijos_planta_semanal
        # Turnos extra
        if turnos_activos >= 2:
            costo_fijos += cfg.fijo_turno_adicional
        if turnos_activos >= 3:
            costo_fijos += cfg.fijo_turno_adicional

        # Inventario holding
        costo_inv = inv_pt * costo_mat_unit * (cfg.costo_mantener_inv_anual / 52)

        # Backorder penalty
        costo_backorder = backlog * C.PENALIZACION_BACKORDER

        # Ventas perdidas
        margen_unitario = (1 - pct_pro) * (cfg.precio_neto_std - cfg.materiales_std) + pct_pro * (cfg.precio_neto_pro - cfg.materiales_pro)
        costo_venta_perdida = ventas_perdidas * (margen_unitario + C.COSTO_VENTA_PERDIDA_EXTRA)

        # Garantías
        costo_garantias = atendido * cfg.devolucion_garantia_pct * cfg.costo_garantia

        # Ingresos
        precio_avg = (1 - pct_pro) * cfg.precio_neto_std + pct_pro * cfg.precio_neto_pro
        ingresos = atendido * precio_avg

        # Costos totales
        costos_totales = costo_mo + costo_materiales + costo_fijos + costo_inv + costo_backorder + costo_garantias

        # Margen bruto
        margen_bruto = ingresos - costos_totales

        # Flujo neto (sin inversiones)
        flujo_neto = margen_bruto - costo_venta_perdida

        # Descuento
        factor_desc = 1 / (1 + tasa_semanal) ** sem
        flujo_descontado = flujo_neto * factor_desc

        rows.append({
            "Semana": sem,
            "Fecha": fecha,
            "Demanda": demand,
            "% Pro": round(pct_pro * 100, 1),
            "Líneas": n_lineas,
            "Turnos": turnos_activos,
            "Cap. Bruta": round(cap_bruta, 1),
            "Cap. Buenas": round(cap_buenas, 1),
            "Producción": round(produccion, 1),
            "Atendido": round(atendido, 1),
            "Inv. Final": round(inv_pt, 1),
            "Backlog": round(backlog, 1),
            "Ventas Perdidas": round(ventas_perdidas, 1),
            "Nivel Servicio %": round(nivel_servicio * 100, 1),
            "Costo MO": round(costo_mo, 2),
            "Costo Materiales": round(costo_materiales, 2),
            "Costo Fijos": round(costo_fijos, 2),
            "Costo Inventario": round(costo_inv, 2),
            "Costo Backorder": round(costo_backorder, 2),
            "Costo Vta Perdida": round(costo_venta_perdida, 2),
            "Costo Garantías": round(costo_garantias, 2),
            "Ingresos": round(ingresos, 2),
            "Costos Totales": round(costos_totales, 2),
            "Margen Bruto": round(margen_bruto, 2),
            "Flujo Neto": round(flujo_neto, 2),
            "Flujo Descontado": round(flujo_descontado, 2),
            "Retrabajo": round(unidades_retrabajo, 1),
        })

    return pd.DataFrame(rows)


def compute_npv(df: pd.DataFrame, investment: float) -> float:
    """Valor Actual Neto a 52 semanas."""
    total_discounted = df["Flujo Descontado"].sum()
    residual = investment * C.VALOR_RESIDUAL_PCT / (1 + C.TASA_SEMANAL) ** C.HORIZONTE
    return total_discounted + residual - investment


def compute_investment(cfg: PlantConfig) -> float:
    """Inversión total de una configuración."""
    inv = 0.0
    if cfg.ops_por_linea == 8:
        inv += cfg.num_lineas * C.INVERSION_REEQUILIBRIO
    if cfg.semana_linea3 <= C.HORIZONTE:
        inv += C.INVERSION_TERCERA_LINEA
    if cfg.num_celulas > 0:
        inv += cfg.num_celulas * C.INVERSION_CELULA
    if cfg.dispositivo_puerta:
        inv += cfg.num_lineas * C.INVERSION_DISPOSITIVO_PUERTA
    return inv


def expected_value(results: dict[str, float], probs: dict[str, float]) -> float:
    """Valor esperado ponderado por escenarios."""
    return sum(results.get(k, 0) * probs.get(k, 0) for k in probs)


def run_all_scenarios(cfg: PlantConfig) -> dict:
    """Ejecuta la simulación en los 3 escenarios y devuelve resumen."""
    investment = compute_investment(cfg)
    probs = {"base": cfg.prob_base, "optim": cfg.prob_optim, "canal": cfg.prob_canal}
    results = {}

    for esc in ["base", "optim", "canal"]:
        cfg_esc = PlantConfig(**{**cfg.__dict__, "escenario": esc})
        df = simulate_weekly(cfg_esc)
        npv = compute_npv(df, investment)
        total_atendido = df["Atendido"].sum()
        total_demanda = df["Demanda"].sum()
        total_perdidas = df["Ventas Perdidas"].sum()
        nivel_servicio = total_atendido / total_demanda * 100 if total_demanda > 0 else 100
        margen_total = df["Margen Bruto"].sum()

        results[esc] = {
            "df": df,
            "npv": round(npv, 2),
            "total_atendido": round(total_atendido, 0),
            "total_demanda": round(total_demanda, 0),
            "total_perdidas": round(total_perdidas, 0),
            "nivel_servicio": round(nivel_servicio, 1),
            "margen_total": round(margen_total, 2),
            "inversion": investment,
        }

    npvs = {k: v["npv"] for k, v in results.items()}
    ve = expected_value(npvs, probs)
    worst = min(npvs.values())

    return {
        "scenarios": results,
        "ve": round(ve, 2),
        "worst_case": round(worst, 2),
        "investment": investment,
        "probs": probs,
    }
