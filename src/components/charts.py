"""
charts.py – Generador de gráficos interactivos Plotly con paleta corporativa.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


CORPORATE_COLORS = {
    "primary": "#1B4F72",      # Azul marino
    "secondary": "#2874A6",    # Azul medio
    "accent": "#27AE60",       # Verde esmeralda
    "warning": "#F39C12",      # Ámbar
    "danger": "#C0392B",       # Rojo oscuro
    "gray": "#7F8C8D",         # Gris neutro
    "light_gray": "#BDC3C7",
    "background": "#FAFBFC",
    "std_color": "#2980B9",    # Azul estándar
    "pro_color": "#8E44AD",    # Púrpura pro
}


def plot_station_bottlenecks(
    stations: list[dict],
    takt_time_val: float | None = None,
    title: str = "Tiempos por Estación y Detección de Cuellos de Botella",
) -> go.Figure:
    """Gráfico de barras horizontal que compara tiempos de estación para Estándar vs Pro."""
    labels = [f"{s.get('op', s.get('operacion', ''))}" for s in stations]
    t_std = [s.get("t_std", s.get("tiempo_std", 0)) for s in stations]
    t_pro = [s.get("t_pro", s.get("tiempo_pro", 0)) for s in stations]

    # Identificar cuellos de botella
    max_std = max(t_std)
    max_pro = max(t_pro)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=t_std,
        name="R1 Estándar (min)",
        orientation="h",
        marker=dict(
            color=[CORPORATE_COLORS["danger"] if t == max_std else CORPORATE_COLORS["std_color"] for t in t_std],
            line=dict(color="#1B4F72", width=1),
        ),
        text=[f"<b>{t:.2f} min (CUELLO)</b>" if t == max_std else f"{t:.2f} min" for t in t_std],
        textposition="inside",
        insidetextanchor="middle",
    ))

    fig.add_trace(go.Bar(
        y=labels,
        x=t_pro,
        name="R1 Pro (min)",
        orientation="h",
        marker=dict(
            color=[CORPORATE_COLORS["danger"] if t == max_pro else CORPORATE_COLORS["pro_color"] for t in t_pro],
            line=dict(color="#512E5F", width=1),
        ),
        text=[f"<b>{t:.2f} min (CUELLO)</b>" if t == max_pro else f"{t:.2f} min" for t in t_pro],
        textposition="inside",
        insidetextanchor="middle",
    ))

    if takt_time_val and takt_time_val > 0 and takt_time_val < 20:
        fig.add_vline(
            x=takt_time_val,
            line_width=2.5,
            line_dash="dash",
            line_color=CORPORATE_COLORS["warning"],
            annotation_text=f"Takt Time Black Friday: {takt_time_val:.2f} min",
            annotation_position="top right",
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1B4F72", family="Inter")),
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Minutos por unidad", gridcolor="#F2F4F4"),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def plot_demand_vs_capacity(df_weekly: pd.DataFrame) -> go.Figure:
    """Gráfico interactivo de Demanda vs Capacidad vs Producción a 52 semanas."""
    fig = go.Figure()

    # Demanda
    fig.add_trace(go.Scatter(
        x=df_weekly["Semana"],
        y=df_weekly["Demanda"],
        name="Demanda Pronosticada",
        line=dict(color="#1B4F72", width=3),
        mode="lines",
    ))

    # Capacidad Bruta
    fig.add_trace(go.Scatter(
        x=df_weekly["Semana"],
        y=df_weekly["Cap. Bruta"],
        name="Capacidad Bruta de Planta",
        line=dict(color="#27AE60", width=2.5, dash="dash"),
        mode="lines",
    ))

    # Producción Real
    fig.add_trace(go.Bar(
        x=df_weekly["Semana"],
        y=df_weekly["Atendido"],
        name="Demanda Atendida (Ventas)",
        marker=dict(color="#2980B9", opacity=0.7),
    ))

    # Ventas Perdidas
    if df_weekly["Ventas Perdidas"].sum() > 0:
        fig.add_trace(go.Bar(
            x=df_weekly["Semana"],
            y=df_weekly["Ventas Perdidas"],
            name="Ventas Perdidas",
            marker=dict(color="#C0392B", opacity=0.85),
        ))

    # Resaltar Black Friday (Semana 8)
    fig.add_vrect(
        x0=7.5, x1=8.5,
        fillcolor="#F9E79F", opacity=0.4,
        layer="below", line_width=1,
        line_color="#F39C12",
        annotation_text="Sem 8: Black Friday (1.900 u)",
        annotation_position="top left",
    )

    # Resaltar Día de las Madres (Semanas 33-34)
    fig.add_vrect(
        x0=32.5, x1=34.5,
        fillcolor="#E8F8F5", opacity=0.4,
        layer="below", line_width=1,
        line_color="#1ABC9C",
        annotation_text="Sems 33-34: Madres",
        annotation_position="top left",
    )

    fig.update_layout(
        title=dict(text="Demanda vs Capacidad y Nivel de Atención Semanal (52 Semanas)", font=dict(size=14, color="#1B4F72")),
        barmode="overlay",
        height=420,
        margin=dict(l=20, r=20, t=50, b=30),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Semana del Año (1 a 52)", dtick=4, gridcolor="#F2F4F4"),
        yaxis=dict(title="Unidades por Semana", gridcolor="#F2F4F4"),
    )
    return fig


def plot_inventory_and_backlog(df_weekly: pd.DataFrame) -> go.Figure:
    """Gráfico de Inventario de PT, Backlog y Ventas Perdidas."""
    fig = go.Figure()

    # Inventario PT
    fig.add_trace(go.Scatter(
        x=df_weekly["Semana"],
        y=df_weekly["Inv. Final"],
        name="Inventario Final PT",
        line=dict(color="#2980B9", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(41, 128, 185, 0.15)",
    ))

    # Línea de capacidad máxima de almacén (1.500 u)
    fig.add_hline(
        y=1500,
        line_dash="dot",
        line_color="#E74C3C",
        line_width=1.5,
        annotation_text="Límite Almacén: 1.500 u",
        annotation_position="top right",
    )

    # Backlog (pedidos pendientes)
    fig.add_trace(go.Bar(
        x=df_weekly["Semana"],
        y=df_weekly["Backlog"],
        name="Backlog (Pedidos Pendientes)",
        marker_color="#F39C12",
        opacity=0.8,
    ))

    fig.update_layout(
        title=dict(text="Dinámica de Inventario de Producto Terminado y Pedidos Pendientes", font=dict(size=14, color="#1B4F72")),
        barmode="group",
        height=320,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Semana", dtick=4, gridcolor="#F2F4F4"),
        yaxis=dict(title="Unidades", gridcolor="#F2F4F4"),
    )
    return fig


def plot_tornado_chart(sens_df: pd.DataFrame) -> go.Figure:
    """
    Genera un diagrama de tornado para análisis de sensibilidad.
    sens_df debe tener columnas: Variable, Min_Swing, Max_Swing, Base_Value.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=sens_df["Variable"],
        x=sens_df["Min_Swing"],
        name="Escenario Desfavorable",
        orientation="h",
        marker=dict(color="#C0392B"),
    ))

    fig.add_trace(go.Bar(
        y=sens_df["Variable"],
        x=sens_df["Max_Swing"],
        name="Escenario Favorable",
        orientation="h",
        marker=dict(color="#27AE60"),
    ))

    fig.add_vline(x=0, line_width=1.5, line_color="#2C3E50")

    fig.update_layout(
        title=dict(text="Diagrama de Tornado: Impacto en el Valor Actual Neto (VAN en US$)", font=dict(size=14, color="#1B4F72")),
        barmode="relative",
        height=380,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Variación del VAN respecto al Caso Base (US$)", gridcolor="#F2F4F4"),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def plot_radar_strategies(strategies_metrics: list[dict]) -> go.Figure:
    """
    Radar Chart multicriterio comparando las estrategias.
    Dimensiones: Rentabilidad, Servicio, Flexibilidad, Eficiencia CapEx, Control Riesgo.
    """
    categories = [
        "Rentabilidad (VAN)",
        "Nivel Servicio Peak",
        "Flexibilidad Operativa",
        "Eficiencia de CapEx",
        "Control de Riesgo (Worst-Case)",
    ]

    fig = go.Figure()

    colors = ["#E74C3C", "#F39C12", "#9B59B6", "#27AE60"]

    for idx, strat in enumerate(strategies_metrics):
        fig.add_trace(go.Scatterpolar(
            r=strat["scores"],
            theta=categories,
            fill="toself",
            name=strat["name"],
            line=dict(color=colors[idx % len(colors)], width=2),
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E2E8F0"),
        ),
        showlegend=True,
        title=dict(text="Evaluación Multicriterio de Estrategias (Puntaje 0-100)", font=dict(size=14, color="#1B4F72")),
        height=380,
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    return fig


def plot_station_utilization(
    util_data: list[dict],
    title: str = "Utilización por Estación respecto al Cuello de Botella (%)",
) -> go.Figure:
    """Gráfico de barras con la utilización porcentual por estación y línea de saturación al 100%."""
    labels = [d["operacion"] for d in util_data]
    u_w = [d["util_ponderada_pct"] for d in util_data]

    bar_colors = []
    for u in u_w:
        if u >= 99.5:
            bar_colors.append(CORPORATE_COLORS["danger"])
        elif u >= 80.0:
            bar_colors.append(CORPORATE_COLORS["warning"])
        elif u >= 65.0:
            bar_colors.append(CORPORATE_COLORS["accent"])
        else:
            bar_colors.append(CORPORATE_COLORS["light_gray"])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=u_w,
        name="Utilización Mezcla Ponderada (%)",
        marker=dict(color=bar_colors, line=dict(color="#1B4F72", width=1)),
        text=[f"<b>{u:.1f}%</b>" for u in u_w],
        textposition="outside",
    ))

    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=CORPORATE_COLORS["danger"],
        line_width=2,
        annotation_text="Límite Cuello de Botella (100%)",
        annotation_position="top right",
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1B4F72", family="Inter")),
        height=360,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(title="Estación de Trabajo", gridcolor="#F2F4F4"),
        yaxis=dict(title="Utilización (%)", range=[0, 118], gridcolor="#F2F4F4"),
    )
    return fig


def plot_scenario_payoffs(payoffs_data: list[dict]) -> go.Figure:
    """
    Gráfico de barras agrupadas que compara los resultados (VAN) de cada estrategia
    a través de los tres escenarios de demanda (Base, Optimista, Canal) y su Valor Esperado.
    """
    names = [d["name"] for d in payoffs_data]
    van_base = [d["base_npv"] for d in payoffs_data]
    van_optim = [d["optim_npv"] for d in payoffs_data]
    van_canal = [d["canal_npv"] for d in payoffs_data]
    ve_vals = [d["ve"] for d in payoffs_data]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=names,
        y=van_base,
        name="Escenario Base (50%)",
        marker_color="#2980B9",
        text=[f"US$ {v/1e6:.2f}M" for v in van_base],
        textposition="outside",
    ))

    fig.add_trace(go.Bar(
        x=names,
        y=van_optim,
        name="Escenario Optimista (25%)",
        marker_color="#27AE60",
        text=[f"US$ {v/1e6:.2f}M" for v in van_optim],
        textposition="outside",
    ))

    fig.add_trace(go.Bar(
        x=names,
        y=van_canal,
        name="Llenado de Canal (25%)",
        marker_color="#E74C3C",
        text=[f"US$ {v/1e6:.2f}M" for v in van_canal],
        textposition="outside",
    ))

    # Línea con marcadores para el Valor Esperado (VE)
    fig.add_trace(go.Scatter(
        x=names,
        y=ve_vals,
        name="Valor Esperado (VE Ponderado)",
        mode="lines+markers+text",
        line=dict(color="#1B4F72", width=3, dash="dot"),
        marker=dict(size=12, color="#1B4F72", symbol="diamond"),
        text=[f"<b>VE: US$ {v/1e6:.2f}M</b>" for v in ve_vals],
        textposition="top center",
    ))

    fig.update_layout(
        title=dict(text="Matriz de Resultados Económicos (VAN en Millones US$) por Escenario", font=dict(size=14, color="#1B4F72")),
        barmode="group",
        height=400,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Estrategia Evaluada", gridcolor="#F2F4F4"),
        yaxis=dict(title="Valor Actual Neto (US$)", gridcolor="#F2F4F4"),
    )
    return fig


def plot_risk_return_scatter(risk_data: list[dict]) -> go.Figure:
    """
    Gráfico de dispersión de Riesgo vs Retorno:
    Eje Y: Retorno Esperado (VE en US$)
    Eje X: Riesgo / Volatilidad (Desviación estándar σ del VAN o Downside Risk)
    Tamaño de burbuja: Nivel de servicio en Black Friday (%)
    """
    fig = go.Figure()

    for item in risk_data:
        fig.add_trace(go.Scatter(
            x=[item["risk"]],
            y=[item["ve"]],
            mode="markers+text",
            name=item["name"],
            text=[f"<b>{item['name']}</b><br>VE: US$ {item['ve']/1e6:.2f}M<br>Riesgo: US$ {item['risk']/1e6:.2f}M"],
            textposition="top right",
            marker=dict(
                size=max(min(item.get("service_level", 80) * 0.4, 45), 18),
                color=item.get("color", "#2980B9"),
                line=dict(color="#1B4F72", width=2),
                opacity=0.85,
            ),
        ))

    fig.update_layout(
        title=dict(text="Plano Estratégico: Retorno Esperado (VE) vs Riesgo / Incertidumbre", font=dict(size=14, color="#1B4F72")),
        height=380,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(title="Incertidumbre / Desviación Estándar σ (US$)", gridcolor="#F2F4F4"),
        yaxis=dict(title="Valor Esperado VE (US$)", gridcolor="#F2F4F4"),
        showlegend=True,
    )
    return fig


def plot_sensitivity_heatmap(
    x_vals: list[float | str],
    y_vals: list[float | str],
    z_matrix: list[list[float]],
    x_label: str,
    y_label: str,
    title: str = "Matriz de Sensibilidad Bivariada (What-If)",
) -> go.Figure:
    """
    Genera un Heatmap bidimensional para análisis de qué pasaría si cambian dos variables simultáneamente.
    """
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=x_vals,
        y=y_vals,
        colorscale="Blues",
        text=[[f"US$ {val/1e6:.2f}M" for val in row] for row in z_matrix],
        texttemplate="%{text}",
        colorbar=dict(title="VAN (US$)"),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1B4F72")),
        height=380,
        margin=dict(l=20, r=20, t=50, b=40),
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
    )
    return fig

