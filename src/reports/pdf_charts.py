"""
pdf_charts.py – Generador de gráficos de alta resolución para el reporte ejecutivo en PDF.

Utiliza matplotlib en modo headless ('Agg') para renderizar imágenes en memoria (io.BytesIO)
con estética corporativa profesional (paleta #1B4F72, #27AE60, #C0392B).
"""
from __future__ import annotations

import io
from typing import Any
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Paleta corporativa
C_PRIMARY = "#1B4F72"
C_SECONDARY = "#2980B9"
C_ACCENT = "#27AE60"
C_WARNING = "#F39C12"
C_DANGER = "#C0392B"
C_MUTED = "#7F8C8D"
C_LIGHT_BG = "#F8F9F9"
C_GRID = "#E5E8E8"


def create_demand_capacity_chart_image(df_weekly: pd.DataFrame) -> io.BytesIO:
    """Genera gráfico de Demanda vs Capacidad y Producción a 52 semanas."""
    fig, ax = plt.subplots(figsize=(8.5, 3.6), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor(C_LIGHT_BG)

    sems = df_weekly["Semana"]
    demanda = df_weekly["Demanda"]
    cap_bruta = df_weekly["Cap. Bruta"]
    atendido = df_weekly["Atendido"]
    perdidas = df_weekly["Ventas Perdidas"]

    # Barras de atendido y perdidas
    ax.bar(sems, atendido, color=C_SECONDARY, alpha=0.8, width=0.8, label="Demanda Atendida (Ventas)")
    if perdidas.sum() > 0:
        ax.bar(sems, perdidas, bottom=atendido, color=C_DANGER, alpha=0.9, width=0.8, label="Ventas Perdidas")

    # Líneas de demanda y capacidad
    ax.plot(sems, demanda, color=C_PRIMARY, linewidth=2.2, label="Demanda Pronosticada")
    ax.plot(sems, cap_bruta, color=C_ACCENT, linewidth=2.0, linestyle="--", label="Capacidad Bruta Planta")

    # Resaltar Black Friday (Semana 8)
    ax.axvspan(7.5, 8.5, color="#F9E79F", alpha=0.4, label="Sem 8: Black Friday (1.900 u)")

    ax.set_title("Curva Semanal de Demanda vs Capacidad de Planta (52 Semanas)", fontsize=11, fontweight="bold", color=C_PRIMARY, pad=10)
    ax.set_xlabel("Semana del Año (1 a 52)", fontsize=8, color=C_PRIMARY)
    ax.set_ylabel("Unidades por Semana", fontsize=8, color=C_PRIMARY)
    ax.set_xlim(0.5, 52.5)
    ax.grid(True, linestyle=":", color=C_GRID, alpha=0.8)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    ax.tick_params(axis="both", labelsize=7)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.9, facecolor="#FFFFFF")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def create_inventory_backlog_chart_image(df_weekly: pd.DataFrame) -> io.BytesIO:
    """Genera gráfico de evolución de Inventario de PT y Backlog semanal."""
    fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor(C_LIGHT_BG)

    sems = df_weekly["Semana"]
    inv_final = df_weekly["Inv. Final"]
    backlog = df_weekly["Backlog"]

    # Área de inventario
    ax.plot(sems, inv_final, color=C_SECONDARY, linewidth=2.0, label="Inventario Final PT")
    ax.fill_between(sems, inv_final, color=C_SECONDARY, alpha=0.2)

    # Límite de almacén (1.500 u)
    ax.axhline(1500, color=C_DANGER, linestyle=":", linewidth=1.8, label="Límite Almacén PT (1.500 u)")

    # Barras de backlog
    if backlog.sum() > 0:
        ax.bar(sems, backlog, color=C_WARNING, alpha=0.7, width=0.8, label="Pedidos Pendientes (Backlog)")

    ax.set_title("Dinámica de Inventario de Producto Terminado y Pedidos Pendientes", fontsize=11, fontweight="bold", color=C_PRIMARY, pad=10)
    ax.set_xlabel("Semana del Año", fontsize=8, color=C_PRIMARY)
    ax.set_ylabel("Unidades", fontsize=8, color=C_PRIMARY)
    ax.set_xlim(0.5, 52.5)
    ax.grid(True, linestyle=":", color=C_GRID, alpha=0.8)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    ax.tick_params(axis="both", labelsize=7)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.9, facecolor="#FFFFFF")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def create_station_utilization_chart_image(util_data: list[dict[str, Any]]) -> io.BytesIO:
    """Genera gráfico de barras de utilización porcentual por estación."""
    fig, ax = plt.subplots(figsize=(8.5, 3.4), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor(C_LIGHT_BG)

    labels = [d.get("operacion", d.get("name", f"E{i+1}")) for i, d in enumerate(util_data)]
    # Invertir para que la primera estación aparezca arriba
    labels = labels[::-1]
    u_vals = [d.get("util_ponderada_pct", d.get("utilization_pct", 0.0)) for d in util_data][::-1]

    colors = []
    for u in u_vals:
        if u >= 99.0:
            colors.append(C_DANGER)
        elif u >= 80.0:
            colors.append(C_WARNING)
        elif u >= 60.0:
            colors.append(C_ACCENT)
        else:
            colors.append(C_MUTED)

    y_pos = range(len(labels))
    bars = ax.barh(y_pos, u_vals, color=colors, height=0.55, edgecolor="#1B4F72", linewidth=0.8)

    # Línea al 100% de saturación
    ax.axvline(100.0, color=C_DANGER, linestyle="--", linewidth=1.5, label="Límite Cuello de Botella (100%)")

    # Etiquetas de texto sobre las barras
    for bar, val in zip(bars, u_vals):
        tag = " (CUELLO)" if val >= 99.0 else ""
        ax.text(
            bar.get_width() + 1.5,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%{tag}",
            va="center",
            ha="left",
            fontsize=7,
            fontweight="bold" if val >= 99.0 else "normal",
            color=C_PRIMARY,
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_title("Perfil de Utilización Ponderada por Estación de Trabajo", fontsize=11, fontweight="bold", color=C_PRIMARY, pad=10)
    ax.set_xlabel("Utilización Porcentual (%)", fontsize=8, color=C_PRIMARY)
    ax.set_xlim(0, 118)
    ax.grid(True, axis="x", linestyle=":", color=C_GRID, alpha=0.8)
    ax.tick_params(axis="both", labelsize=7)
    ax.legend(loc="lower right", fontsize=7, framealpha=0.9, facecolor="#FFFFFF")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def create_scenarios_comparison_chart_image(payoffs_data: list[dict[str, Any]]) -> io.BytesIO:
    """Genera gráfico comparativo de barras de VAN por escenario y Valor Esperado."""
    fig, ax = plt.subplots(figsize=(8.5, 3.5), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor(C_LIGHT_BG)

    names = [d["name"] for d in payoffs_data]
    van_base = [d["base_npv"] / 1e6 for d in payoffs_data]
    van_optim = [d["optim_npv"] / 1e6 for d in payoffs_data]
    van_canal = [d["canal_npv"] / 1e6 for d in payoffs_data]
    ve_vals = [d["ve"] / 1e6 for d in payoffs_data]

    x = range(len(names))
    width = 0.22

    ax.bar([i - width for i in x], van_base, width=width, color=C_SECONDARY, label="Base (50%)")
    ax.bar([i for i in x], van_optim, width=width, color=C_ACCENT, label="Optimista (25%)")
    ax.bar([i + width for i in x], van_canal, width=width, color=C_DANGER, label="Canal (25%)")

    # Puntos de Valor Esperado
    ax.plot(x, ve_vals, color=C_PRIMARY, marker="D", markersize=7, linewidth=2.0, linestyle=":", label="Valor Esperado (VE)")

    for i, ve in enumerate(ve_vals):
        ax.annotate(
            f"VE: ${ve:.2f}M",
            (i, ve),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=7,
            fontweight="bold",
            color=C_PRIMARY,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8, fontweight="bold")
    ax.set_title("Comparativa de Rentabilidad (VAN en Millones US$) por Escenario de Demanda", fontsize=11, fontweight="bold", color=C_PRIMARY, pad=10)
    ax.set_ylabel("VAN (Millones US$)", fontsize=8, color=C_PRIMARY)
    ax.grid(True, linestyle=":", color=C_GRID, alpha=0.8)
    ax.tick_params(axis="both", labelsize=7)
    ax.legend(loc="upper left", fontsize=7, framealpha=0.9, facecolor="#FFFFFF")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def create_tornado_chart_image(tornado_df: pd.DataFrame) -> io.BytesIO:
    """Genera diagrama de tornado ordenado por impacto total en el VAN."""
    fig, ax = plt.subplots(figsize=(8.5, 3.6), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor(C_LIGHT_BG)

    # Tomar top 6 o 7 variables si hay muchas
    df_sorted = tornado_df.sort_values("Rango_Total", ascending=True).tail(7)
    variables = df_sorted["Variable"].tolist()
    min_swings = [s / 1e3 for s in df_sorted["Min_Swing"].tolist()]
    max_swings = [s / 1e3 for s in df_sorted["Max_Swing"].tolist()]

    y_pos = range(len(variables))
    ax.barh(y_pos, min_swings, color=C_DANGER, height=0.55, label="Escenario Desfavorable")
    ax.barh(y_pos, max_swings, color=C_ACCENT, height=0.55, label="Escenario Favorable")

    ax.axvline(0, color=C_PRIMARY, linewidth=1.2)

    # Etiquetas de texto
    for idx, (l, h) in enumerate(zip(min_swings, max_swings)):
        ax.text(l - 15, idx, f"${l:,.0f}k", va="center", ha="right", fontsize=6.5, color=C_DANGER, fontweight="bold")
        ax.text(h + 15, idx, f"+${h:,.0f}k", va="center", ha="left", fontsize=6.5, color=C_ACCENT, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(variables, fontsize=6.8)
    ax.set_title("Diagrama de Tornado: Sensibilidad del VAN (Miles de US$)", fontsize=11, fontweight="bold", color=C_PRIMARY, pad=10)
    ax.set_xlabel("Variación del VAN respecto al Caso Base (Miles de US$)", fontsize=8, color=C_PRIMARY)
    ax.grid(True, axis="x", linestyle=":", color=C_GRID, alpha=0.8)
    ax.tick_params(axis="both", labelsize=7)
    ax.legend(loc="lower right", fontsize=7, framealpha=0.9, facecolor="#FFFFFF")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf
