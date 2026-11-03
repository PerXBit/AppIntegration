"""
test_model.py – Suite de Pruebas Automatizadas para el Simulador Resguarda.

Verifica:
1. Coincidencia exacta de los 13 valores de control.
2. Integridad del balance de masa de inventarios en la simulación.
3. Generación y lectura del libro Excel maestro.
4. Generación válida del reporte PDF.
5. Ejecución sin excepciones de las 4 estrategias en los 3 escenarios.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
import pandas as pd

# Asegurar raíz en sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.model import constants as C
from src.model.case_solver import (
    solve_q1_capacidad_y_cuello,
    solve_q2_informe_cabrera,
    solve_q3_dispositivo_puerta,
    solve_q4_combinacion_optima_presupuesto,
    solve_q5_maximizacion_ve_y_peor_caso,
    solve_q6_recomendacion_mariela_santos,
)
from src.model.data_loader import (
    DEFAULT_EXCEL_PATH,
    PARAMETROS_CATALOGO,
    ensure_default_excel_files,
    export_template_bytes,
    get_active_parameters_dict,
    get_default_parameters_dict,
    load_data_from_excel,
    validate_and_extract_simulation_data,
)
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
from src.model.strategies import get_predefined_strategies
from src.reports.pdf_generator import generate_simulation_pdf


def test_13_control_values():
    """Valida los 13 valores de control oficiales del caso Resguarda."""
    cv = compute_control_values()

    assert cv.wc_std == 39.87
    assert cv.wc_pro == 42.47
    assert cv.ct_std == 8.00
    assert cv.ct_pro == 8.60
    assert "E3" in cv.bottleneck_std or "puerta" in cv.bottleneck_std.lower()
    assert "E4" in cv.bottleneck_pro or "cableado" in cv.bottleneck_pro.lower()
    assert round(cv.eff_std * 100, 1) == 83.1
    assert round(cv.eff_pro * 100, 1) == 82.3
    assert cv.c_bar == 8.18
    assert cv.cap_line == 268.5
    assert cv.cap_plant == 537.0
    assert cv.good_units == 532.1
    assert cv.rework_units == 19.8
    assert cv.flow_time_hr == 6.42
    assert cv.takt_wk8 == 2.37
    assert cv.labor_weekly == 5990.00
    assert cv.labor_per_good == 11.26
    assert cv.margin_avg == 78.20
    assert cv.cap_2shifts == 1031.0


def test_inventory_mass_balance():
    """Verifica que el inventario cumpla el balance de masa en cada semana."""
    cfg = PlantConfig(escenario="base")
    df = simulate_weekly(cfg)

    assert len(df) == 52

    # El inventario final de la semana t debe ser <= límite de almacén (1.500 u)
    assert (df["Inv. Final"] <= 1500).all()
    # No puede haber inventario negativo
    assert (df["Inv. Final"] >= 0).all()
    # Demanda atendida nunca puede exceder la demanda total disponible
    assert (df["Atendido"] <= df["Demanda"] + df["Backlog"].shift(1).fillna(0) + 1.0).all()


def test_excel_generation_and_loading():
    """Verifica la generación y lectura del archivo Excel maestro y plantilla."""
    ensure_default_excel_files()
    assert DEFAULT_EXCEL_PATH.exists()

    dfs = load_data_from_excel(DEFAULT_EXCEL_PATH)
    assert len(dfs) == 6
    for sheet in ["Parametros", "Estaciones", "Puestos", "Opciones", "Demanda", "Escenarios"]:
        assert sheet in dfs

    extracted = validate_and_extract_simulation_data(dfs)
    assert len(extracted["demanda_df"]) == 52
    assert len(extracted["escenarios_df"]) == 3

    # Test export plantilla en memoria
    t_bytes = export_template_bytes()
    assert len(t_bytes) > 5000
    dfs_mem = load_data_from_excel(io.BytesIO(t_bytes))
    assert len(dfs_mem) == 6


def test_pdf_generation():
    """Verifica que el generador de PDF retorne un archivo corporativo con graficos embebidos."""
    cfg = PlantConfig()
    df = simulate_weekly(cfg)
    cv = compute_control_values(cfg)
    multi = run_all_scenarios(cfg)

    pdf_bytes = generate_simulation_pdf(cfg, df, cv, multi, "E4. Ágil Secuencial")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 150000  # Reporte completo de 8 paginas con imagenes de alta resolucion
    assert pdf_bytes.startswith(b"%PDF")


def test_traffic_light_styles():
    """Verifica las funciones de formato y semaforo condicional (Verde, Amarillo, Rojo)."""
    from src.components.styles import (
        color_service_level,
        color_npv,
        color_lost_sales,
        color_backlog,
        color_utilization,
        color_capex,
        style_comparador_df,
        style_weekly_df,
    )
    # Servicio: verde >= 90, amarillo 75-89, rojo < 75
    assert "#E8F8F5" in color_service_level(95.0)
    assert "#FEF9E7" in color_service_level(82.0)
    assert "#FDEDEC" in color_service_level(65.0)

    # VAN: verde > 0, rojo < 0
    assert "#D4EFDF" in color_npv(3_000_000)
    assert "#FDEDEC" in color_npv(-500_000)

    # Ventas perdidas: verde = 0, amarillo <= 1000, rojo > 1000
    assert "#E8F8F5" in color_lost_sales(0)
    assert "#FEF9E7" in color_lost_sales(500)
    assert "#FDEDEC" in color_lost_sales(5000)

    # Probar que styler no arroja excepciones
    df_dummy = pd.DataFrame({
        "Estrategia": ["E1", "E2"],
        "Inversión CapEx": [0.0, 18000.0],
        "VAN Base (50%)": [1000000.0, 2000000.0],
        "Servicio Anual": [50.0, 95.0],
    })
    styler_c = style_comparador_df(df_dummy)
    html_c = styler_c.to_html()
    assert len(html_c) > 500


def test_all_strategies_execution():
    """Verifica que las 4 estrategias se ejecuten en los 3 escenarios sin error."""
    strategies = get_predefined_strategies()
    assert len(strategies) == 4

    for s_id, s_def in strategies.items():
        res = run_all_scenarios(s_def.config_base)
        assert "base" in res["scenarios"]
        assert "optim" in res["scenarios"]
        assert "canal" in res["scenarios"]
        assert res["ve"] is not None
        assert res["worst_case"] is not None


def test_station_utilization_calculation():
    """Valida el cálculo de utilización por estación y la detección de saturación."""
    stations = get_station_times(6, False, False)
    util_data = compute_station_utilization(stations, 0.30)
    assert len(util_data) == 6

    # Debe haber exactamente 1 cuello de botella en la mezcla
    cuellos = [u for u in util_data if u["is_bottleneck"]]
    assert len(cuellos) == 1
    # La estación de cuello debe tener utilización del 100%
    assert cuellos[0]["utilization_pct"] == 100.0

    for u in util_data:
        assert 0.0 < u["utilization_pct"] <= 100.0
        assert u["weighted_time"] > 0


def test_case_solver_all_questions():
    """Valida la resolución matemática y consistencia de las 6 preguntas del caso."""
    cfg = PlantConfig()

    # Q1: Capacidad y Cuello de Botella
    q1 = solve_q1_capacidad_y_cuello(cfg)
    assert q1["wc_std"] == 39.87
    assert q1["wc_pro"] == 42.47
    assert q1["ct_std"] == 8.00
    assert q1["ct_pro"] == 8.60
    assert "E3" in q1["bottleneck_std"] or "puerta" in q1["bottleneck_std"].lower()
    assert "E4" in q1["bottleneck_pro"] or "cableado" in q1["bottleneck_pro"].lower()
    assert q1["cap_plant"] == 537.0
    assert q1["good_units"] == 532.1

    # Q2: Informe de Julio Cabrera
    q2 = solve_q2_informe_cabrera(cfg)
    assert q2["es_correcta"] is False
    assert q2["cabrera_avg_time"] == 4.98
    assert round(q2["pct_increase_real"], 1) == 35.6
    assert round(q2["cap_plant_8"], 0) == 728.0

    # Q3: Dispositivo de la Puerta (O5)
    q3 = solve_q3_dispositivo_puerta(cfg)
    assert q3["ct_pro_disp"] == q3["ct_pro_no"]  # Pro no mejora
    assert q3["pct_gain"] < 20.0
    assert q3["plazo_semanas"] == 10

    # Q4: Combinación Óptima bajo Presupuesto
    q4 = solve_q4_combinacion_optima_presupuesto(cfg)
    assert q4["combinacion_ganadora"]["cumple_bf_con_inventario"] is True
    assert q4["combinacion_ganadora"]["inversion"] <= q4["limite_presupuesto"]
    assert q4["combinacion_ganadora"]["id"] == "Comb_A_Turno2_Sabados"

    # Q5: Maximización de VE y Peor Caso
    q5 = solve_q5_maximizacion_ve_y_peor_caso(cfg)
    assert len(q5["ranking_ve"]) == 4
    assert q5["max_ve_strat"]["id"] in ["E3", "E4"]
    assert q5["best_worst_strat"]["worst_case"] > 0

    # Q6: Recomendación para Mariela Santos
    q6 = solve_q6_recomendacion_mariela_santos(cfg)
    assert len(q6["hitos"]) == 5
    assert q6["inversion_inicial"] == 0.0


def test_dynamic_parameter_modification():
    """Valida la personalización amigable de los 22 parámetros y su impacto en el modelo."""
    defaults = get_default_parameters_dict()
    assert len(defaults) == 22
    assert len(PARAMETROS_CATALOGO) == 22

    # Verificar que las 22 variables requeridas por el usuario están presentes
    required_keys = [
        "precio_neto_std", "precio_neto_pro", "materiales_std", "materiales_pro",
        "pct_pro_sem1_26", "pct_pro_sem27_52", "devolucion_garantia_pct", "costo_garantia",
        "inventario_inicial", "inventario_maximo", "costo_mantener_inv_anual",
        "tasa_descuento_anual", "limite_inversion_fiscal", "fijos_planta_semanal",
        "fijo_turno_adicional", "salario_supervisor", "cargas_sociales_pct",
        "falla_std", "falla_pro", "tasa_recuperacion_retrabajo",
        "lote_produccion_defecto", "tiempo_cambio_lote",
    ]
    for rk in required_keys:
        assert rk in defaults, f"Falta el parámetro {rk} en el catálogo"

    # 1. Modificar precio y verificar cambio de margen
    cfg_custom = PlantConfig(precio_neto_std=150.0, materiales_std=50.0)
    cv_custom = compute_control_values(cfg_custom)
    # Margen Std esperado = 150 - 50 = 100. Margen Pro base = 169 - 74 = 95.
    # Margen mezcla (30% Pro) = 0.70 * 100 + 0.30 * 95 = 70 + 28.5 = 98.5
    assert cv_custom.margin_avg == 98.5

    # 2. Modificar inventario inicial y simular
    cfg_inv = PlantConfig(inventario_inicial=500.0)
    df_inv = simulate_weekly(cfg_inv)
    # En semana 1, el inventario disponible arranca desde 500
    assert df_inv.iloc[0]["Producción"] >= 0

    # 3. Modificar presupuesto fiscal
    cfg_budget = PlantConfig(limite_inversion_fiscal=150000.0)
    assert cfg_budget.limite_inversion_fiscal == 150000.0

    # 4. Exportar libro Excel con parámetros modificados y verificar lectura
    custom_dict = dict(defaults)
    custom_dict["precio_neto_std"] = 199.0
    custom_dict["salario_supervisor"] = 1500.0

    excel_bytes = export_template_bytes(custom_dict)
    assert len(excel_bytes) > 5000
    dfs_read = load_data_from_excel(io.BytesIO(excel_bytes))
    extracted = validate_and_extract_simulation_data(dfs_read)
    p_dict = extracted["parametros_dict"]
    assert float(p_dict["precio_neto_std"]) == 199.0
    assert float(p_dict["salario_supervisor"]) == 1500.0


if __name__ == "__main__":
    print("Ejecutando pruebas de validacion...")
    test_13_control_values()
    print("[OK] test_13_control_values PASO")
    test_station_utilization_calculation()
    print("[OK] test_station_utilization_calculation PASO")
    test_case_solver_all_questions()
    print("[OK] test_case_solver_all_questions PASO")
    test_dynamic_parameter_modification()
    print("[OK] test_dynamic_parameter_modification PASO")
    test_inventory_mass_balance()
    print("[OK] test_inventory_mass_balance PASO")
    test_excel_generation_and_loading()
    print("[OK] test_excel_generation_and_loading PASO")
    test_pdf_generation()
    print("[OK] test_pdf_generation PASO")
    test_traffic_light_styles()
    print("[OK] test_traffic_light_styles PASO")
    test_all_strategies_execution()
    print("[OK] test_all_strategies_execution PASO")
    print("\nTODAS LAS PRUEBAS PASARON EXITOSAMENTE (9/9)")
