# NOTA TÉCNICA · CASO RESGUARDA (HCC)
## Validación del Modelo, Supuestos Operativos y Trazabilidad Matemática

**Empresa:** Hogar Conectado del Caribe, S.R.L. (HCC)  
**Autor:** Dirección de Operaciones / Equipo de Simulación  
**Fecha:** Octubre 2026  
**Propósito:** Sustentación metodológica del Tablero Simulador para la toma de decisiones de capacidad.

---

### 1. Resumen de Supuestos del Modelo
1. **Jornada y Capacidad de Turnos:**
   - Esquema regular (Turnos 1 y 2): 8,5 h programadas, 30 min de almuerzo no pagado, 2 descansos pagados de 15 min $\implies$ **7,5 h productivas (450 min/día)** y 8,0 h pagadas. Semana de 5 días (lunes a viernes).
   - Esquema de 3 turnos: 8,0 h programadas $\implies$ **7,0 h productivas (420 min/día)** y 7,5 h pagadas.
   - Rendimiento relativo respecto al 1.º turno: 2.º turno al **92%** ($2.070 \text{ min/sem}$ equivalentes); 3.er turno al **88%** ($1.848 \text{ min/sem}$).
   - Horas extra en sábados: 6,5 h productivas (7,0 h pagadas) con recargo salarial del **50%**. Máximo 3 sábados al mes, aplicable únicamente sobre el personal del primer turno.
2. **Costes Laborales y Estructura Salarial:**
   - Operadores de línea (E1–E4, E6): US\$ 6,50/h.
   - Técnicos de pruebas (E5), manipulador de materiales y técnico de retrabajo: US\$ 7,50/h.
   - Líder de turno (turnos 2.º y 3.º): US\$ 9,00/h.
   - Trabajador polivalente en célula: US\$ 7,20/h.
   - Primas por turno: +8% para el 2.º turno y +15% para el 3.er turno.
   - Cargas sociales y beneficios laborales: **30% sobre el salario bruto**.
   - Supervisor de planta: US\$ 1.050 por semana (costo fijo único para toda la planta).
   - Coste de contratación y formación inicial: US\$ 350 por persona nueva.
3. **Calidad, Retrabajo y Desecho:**
   - Fallas en prueba eléctrica final: 4% en R1 Estándar y 6% en R1 Pro.
   - Recuperación en retrabajo: **80% de las unidades que fallan** son recuperadas por el técnico fuera de línea (15 min/unidad). El **20% restante se desecha** irrecuperable (pérdida del costo de materiales).
   - Desecho neto sobre producción total: $0,70(4\% \times 20\%) + 0,30(6\% \times 20\%) = 0,56\% + 0,36\% = 0,92\%$. Factor de unidades buenas: **99,08%**.
4. **Inventarios, Servicio y Faltantes:**
   - Inventario inicial: 300 unidades (70% Estándar).
   - Capacidad máxima física de almacén de producto terminado: 1.500 unidades.
   - Costo de mantener inventario: 24% anual (equivalente a $24\% / 52$ semanal) sobre el costo de materiales del inventario final.
   - Demanda no atendida: **50% espera en cartera pendiente (backlog)** hasta 2 semanas (penalización de US\$ 3/unidad-semana). Si no se atiende en 2 semanas, se pierde. El **50% restante se pierde de inmediato**.
   - Costo de venta perdida: Margen de contribución antes de mano de obra + US\$ 10 por pérdida de reputación/imagen comercial.
5. **Parámetros Financieros y Descuento:**
   - Tasa de descuento: 12% anual. Tasa semanal equivalente compuesta: $i_{\text{sem}} = (1 + 0,12)^{1/52} - 1 \approx 0,2178\%$.
   - Horizonte: 52 semanas (5 de octubre de 2026 a 1 de octubre de 2027).
   - Valor residual de equipos al final de la semana 52: **80% del valor de inversión** (vida útil contable de 5 años).

---

### 2. Tabla de Validación de Valores de Control (13 de 13 Cumplidos)
Configuración actual: 2 líneas, 6 operadores/línea, 1 turno, lote $Q = 100$, 30% Pro.

| # | Indicador de Control | Valor del Caso | Valor del Modelo | Tolerancia | Estado |
|---|---|:---:|:---:|:---:|:---:|
| 1 | Contenido de trabajo Estándar / Pro | 39,87 / 42,47 min | **39,87 / 42,47 min** | 0,00% | ✅ Exacto |
| 2 | Tiempo de ciclo Estándar / Pro | 8,00 min (E3) / 8,60 min (E4) | **8,00 min (E3) / 8,60 min (E4)** | 0,00% | ✅ Exacto |
| 3 | Eficiencia del balance Estándar / Pro | 83,1% / 82,3% | **83,1% / 82,3%** | 0,00% | ✅ Exacto |
| 4 | Ciclo medio con mezcla (30% Pro) | 8,18 min | **8,18 min** | 0,00% | ✅ Exacto |
| 5 | Capacidad bruta por línea / planta | 268,5 / 537,0 u/sem | **268,5 / 537,0 u/sem** | 0,00% | ✅ Exacto |
| 6 | Unidades buenas por semana | 532,1 u/sem | **532,1 u/sem** | 0,00% | ✅ Exacto |
| 7 | Unidades a retrabajar por semana | 19,8 u/sem | **19,8 u/sem** | 0,00% | ✅ Exacto |
| 8 | Tiempo de flujo por línea (Ley de Little) | 6,42 horas | **6,42 horas** | 0,00% | ✅ Exacto |
| 9 | Takt time línea sem 8 (Black Friday) | 2,37 min | **2,37 min** | 0,00% | ✅ Exacto |
| 10 | Coste semanal mano de obra con cargas | US\$ 5.990 | **US\$ 5.990** | 0,00% | ✅ Exacto |
| 11 | Coste MO por unidad buena | US\$ 11,26 | **US\$ 11,26** | 0,00% | ✅ Exacto |
| 12 | Margen de contribución medio (30% Pro) | US\$ 78,20 / unidad | **US\$ 78,20 / unidad** | 0,00% | ✅ Exacto |
| 13 | Capacidad bruta con 2.º turno | 1.031,0 u/sem | **1.031,0 u/sem** | 0,00% | ✅ Exacto |

---

### 3. Trazabilidad de Fórmulas Matemáticas Clave
- **Ciclo Efectivo con Lotes:** $c_{\text{eff}} = \bar{c} + \frac{s}{Q} = 8,18 + \frac{20}{100} = 8,38 \text{ min/u}$.
- **Capacidad Bruta:** $\text{Cap} = \frac{T}{c_{\text{eff}}} = \frac{2.250}{8,38} = 268,496 \implies 268,5 \text{ u/línea}$; Planta (2 líneas): $537,0 \text{ u/sem}$.
- **Coste MO Semanal:** $[(10 \times 6,50 + 2 \times 7,50 + 1 \times 7,50 + 1 \times 7,50) \times 40 \text{ h}] \times 1,30 + 1.050 = 3.800 \times 1,30 + 1.050 = \text{US\$ } 5.990$.
- **Tiempo de Flujo (Little):** $TH = \frac{268,496}{37,5 \text{ h}} = 7,16 \text{ u/h} \implies T_{\text{flujo}} = \frac{46 \text{ u}}{7,16 \text{ u/h}} = 6,42 \text{ h}$.
- **Takt Time Sem 8:** $\frac{2.250 \text{ min}}{950 \text{ u/línea}} = 2,368 \implies 2,37 \text{ min/u}$.
