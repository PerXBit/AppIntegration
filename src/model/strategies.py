"""
strategies.py – Definición de las 4 estrategias base del caso y catálogo de opciones.

Estrategias:
1. E1: Inercia / Statu Quo (2 líneas, 1 turno, sin inversiones)
2. E2: Propuesta Cabrera (Reequilibrio a 8 operadores + sábados extras)
3. E3: Expansión Fija Agresiva (3.ª línea desde sem 8 + 2.º turno desde sem 1)
4. E4: Estrategia Ágil Secuencial / Recomendada (Fase 1: Turno 2 sem 3 + sábados Q4;
       Punto de decisión sem 13: si optimista, mantener/expandir; si canal, replegar sin costos hundidos)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from src.model.engine import PlantConfig, build_plant_config


@dataclass
class StrategyDefinition:
    id: str
    nombre: str
    subtitulo: str
    descripcion: str
    config_base: PlantConfig
    enfoque: str            # "Riesgosa", "Conservadora", "Inerte", "Ágil Recomendada"
    badge_color: str        # Hex color para UI
    ventajas: list[str]
    desventajas: list[str]
    inversion_estimada: float
    es_recomendada: bool = False


def get_predefined_strategies() -> dict[str, StrategyDefinition]:
    """Retorna el diccionario con las 4 estrategias analizadas en el caso."""
    return {
        "E1": StrategyDefinition(
            id="E1",
            nombre="E1. Inercia (Statu Quo)",
            subtitulo="Mantener 2 líneas, 6 operadores, 1 turno",
            descripcion="No realizar ninguna inversión ni contratar turnos adicionales. Opera a capacidad estándar de 537 unidades/semana.",
            enfoque="Inerte / Muy Alto Riesgo Comercial",
            badge_color="#E74C3C",
            inversion_estimada=0.0,
            ventajas=[
                "Inversión de capital cero ($0).",
                "Sin complejidad operativa de gestión de nuevos turnos.",
                "Costes fijos mínimos.",
            ],
            desventajas=[
                "Colapso en Black Friday: Nivel de servicio menor al 30%.",
                "Pérdida masiva de clientes hacia competidores en el Caribe y Florida.",
                "Ventas perdidas anuales superiores a 30.000 unidades.",
            ],
            config_base=build_plant_config(
                num_lineas=2,
                ops_por_linea=6,
                num_turnos=1,
                sabados_mes=0,
                tamano_lote=100,
                tiempo_cambio=20.0,
            ),
            es_recomendada=False,
        ),
        "E2": StrategyDefinition(
            id="E2",
            nombre="E2. Propuesta Cabrera (8 Operadores + Sábados)",
            subtitulo="Reequilibrar a 8 operadores + 3 sábados/mes de horas extra",
            descripcion="Implementa la recomendación del Jefe de Ingeniería Industrial invirtiendo $18.000 en plantillas y rebalanceando a 8 operadores por línea desde la semana 4, complementando con 3 sábados de horas extra al mes.",
            enfoque="Parcial / Sesgo de Ingeniería",
            badge_color="#F39C12",
            inversion_estimada=18000.0,
            ventajas=[
                "Inversión moderada ($18.000 dentro del presupuesto de $120.000).",
                "Aumenta la capacidad bruta por línea a ~364 u/sem (con sábados ~425 u/sem).",
                "Implementable en 3 semanas de preparación.",
            ],
            desventajas=[
                "Error de cálculo de Cabrera: la capacidad no se duplica (+35.6% real debido al cuello de botella en L3/L6).",
                "Insuficiente para cubrir el pico de Black Friday (1.900 unidades requeridas vs ~850 alcanzables).",
                "Alto desgaste y sobrecosto por horas extra recurrentes.",
            ],
            config_base=build_plant_config(
                num_lineas=2,
                ops_por_linea=8,
                num_turnos=1,
                sabados_mes=3,
                tamano_lote=100,
                tiempo_cambio=20.0,
            ),
            es_recomendada=False,
        ),
        "E3": StrategyDefinition(
            id="E3",
            nombre="E3. Expansión Fija Agresiva (Línea 3 + Doble Turno)",
            subtitulo="Comprar Línea 3 ($48.000) e iniciar 2.º turno en sem 1",
            descripcion="Estrategia estática orientada a maximizar volumen: ordena de inmediato la 3.ª línea (llega sem 9) y contrata el 2.º turno desde la semana 1 para ambas líneas.",
            enfoque="Agresiva / Riesgo de Capital Hundido",
            badge_color="#9B59B6",
            inversion_estimada=48000.0,
            ventajas=[
                "Alta capacidad bruta en 2027 (>1.500 u/sem).",
                "Cubre con holgura el crecimiento continuo si se da el escenario optimista.",
                "Inversión ($48.000) menor al límite de $120.000.",
            ],
            desventajas=[
                "La Línea 3 tarda 8 semanas: llega DESPUÉS de Black Friday (semana 9), perdiendo el pico crítico.",
                "En el escenario de llenado de canal (demanda cae a 650 en enero), genera enorme capacidad ociosa y altos costos fijos.",
                "Consume 120 m² de los 180 m² disponibles, limitando almacén de producto terminado.",
            ],
            config_base=build_plant_config(
                num_lineas=2,
                ops_por_linea=6,
                semana_linea3=9,
                num_turnos=2,
                semana_turno2=1,
                sabados_mes=1,
                tamano_lote=100,
                tiempo_cambio=20.0,
            ),
            es_recomendada=False,
        ),
        "E4": StrategyDefinition(
            id="E4",
            nombre="E4. Estrategia Ágil Secuencial (Recomendada)",
            subtitulo="Fase 1: 2.º Turno (sem 3) + Horas Extra Q4. Fase 2: Punto de decisión sem 13",
            descripcion="Enfoque de opciones reales: cubre la temporada alta con contratación ágil del 2.º turno (2 semanas de rampa) y horas extra los sábados en noviembre/diciembre sin comprar activos fijos pesados ($0 CapEx inicial). En la semana 13, con datos reales del canal, decide si mantener el turno o ajustarlo.",
            enfoque="Ágil / Opciones Reales (Recomendada)",
            badge_color="#27AE60",
            inversion_estimada=0.0,
            ventajas=[
                "CapEx inicial $0 en maquinaria pesada: satisface completamente al Director Financiero.",
                "Llega a tiempo para Black Friday (Turno 2 operativo en sem 3).",
                "Con horas extra en sábados cubre la demanda pico con nivel de servicio >95%.",
                "Flexibilidad asimétrica: si la demanda colapsa en enero (canal), se ajusta el turno sin activos varados; si sube (optimista), se expande con el espacio adicional.",
            ],
            desventajas=[
                "Exige disciplina de reclutamiento (incorporar hasta 12 operadores en sem 1-2).",
                "Prima de turno del 8% y curva de aprendizaje durante las primeras 4 semanas.",
            ],
            config_base=build_plant_config(
                num_lineas=2,
                ops_por_linea=6,
                num_turnos=2,
                semana_turno2=3,
                sabados_mes=2,
                tamano_lote=100,
                tiempo_cambio=20.0,
            ),
            es_recomendada=True,
        ),
    }
