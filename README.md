# 🛡️ Tablero Simulador de Operaciones "Resguarda" (HCC)
> **Capacidad, Cuello de Botella y Crecimiento en una Planta de Ensamblaje**  
> Caso de estudio docente inspirado en *«Parcel Guard: Keeping Up with Demand»* (Ivey Publishing, 2020), con datos y supuestos desarrollados por Félix J. Rodríguez P.

---

## 📋 Descripción del Proyecto
Aplicación analítica interactiva desarrollada en **Streamlit** y gestionada con **uv** para simular y optimizar las operaciones de **Hogar Conectado del Caribe, S.R.L. (HCC)** en Santo Domingo Oeste.

El simulador permite evaluar el impacto de siete palancas de capacidad frente a una demanda estacional que escala desde 700 unidades en octubre hasta un pico de **1.900 unidades/semana en Black Friday**, bajo restricciones de capital (US\$ 120.000) y espacio físico (180 m² disponibles).

---

## 🌟 Características Principales
1. **Exactitud Matemática Garantizada (25%)**: Reproduce con tolerancia cero los **13 valores de control** del caso oficial. Fórmulas trazables documentadas en KaTeX.
2. **Profundidad de Análisis Operativo (25%)**:
   - Detección dinámica de cuello de botella: Estándar en E3 (8,00 min) y Pro en E4 (8,60 min).
   - Desmitificación del informe de Julio Cabrera (demostración de que 8 operadores solo aumentan capacidad un +35,6% y no se duplica).
   - Análisis de Ley de Little ($T_{\text{flujo}} = 6,42 \text{ horas}$ con 46 unidades en proceso).
   - Calidad, retrabajo y desecho diferenciado por variante y células.
3. **Calidad de Decisión y Gestión de Riesgo (25%)**:
   - Comparación en paralelo de 4 estrategias en 3 escenarios de demanda (Base 50%, Optimista 25%, Canal 25%).
   - Cálculo de **Valor Esperado (VE)** y criterio de protección **MaxiMin (Peor Caso)**.
   - Enfoque de **Opciones Reales**: Punto de decisión secuencial en semana 13 para evitar capital varado.
4. **Diseño Corporativo e Interactividad (15%)**:
   - Interfaz moderna para nivel directivo con paleta institucional, tarjetas KPI, gráficos Plotly y alertas de holgura.
   - Visualización semana a semana (52 semanas) de demanda, capacidad, inventarios y ventas perdidas.
5. **Carga y Plantillas Excel**:
   - Inicio automático desde el libro maestro oficial `data/resguarda_datos_caso.xlsx`.
   - Botón para **descargar la Plantilla Oficial (Excel .xlsx)** con estilos profesionales.
   - Cargador Drag & Drop para subir datos propios con validación automática de esquema.
6. **Exportación Integral de Reportes**:
   - 📄 **Exportación Completa en PDF** (usando `fpdf2`, 100% Python puro sin binarios externos de C).
   - 📊 **Exportación en Excel (.xlsx)** con datos de las 52 semanas y resumen ejecutivo.
   - 📋 **Exportación en CSV**.

---

## 🚀 Guía de Instalación y Ejecución Local

### Prerrequisitos
- Tener instalado [uv](https://docs.astral.sh/uv/) (recomendado) o Python 3.11 / 3.12.

### 1. Ejecución con `uv` (Recomendada y Ultrarrápida)
```bash
# Clonar o ubicarse en el directorio del proyecto
cd "INTEGRACION DE APLICACIONES"

# Sincronizar dependencias automáticamente
uv sync

# Iniciar la aplicación
uv run streamlit run app.py
```
La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### 2. Ejecución con entorno virtual estándar (pip)
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/macOS
.venv\Scripts\activate     # En Windows

pip install -r requirements.txt
streamlit run app.py
```

### 3. Ejecución de la Suite de Pruebas Automatizadas
```bash
uv run python tests/test_model.py
```
Ejecuta las pruebas de los 13 valores de control, balance de masa de inventarios, generación Excel y reporte PDF.

---

## 🐳 Despliegue con Docker y Ubuntu 24.04 LTS

El proyecto incluye un `Dockerfile` multietapa optimizado con `uv` y un archivo `docker-compose.yml`.

### Despliegue con Docker Compose
```bash
docker compose up --build -d
```
El contenedor compilará e iniciará el servicio en el puerto `8501`. Accede desde tu navegador en `http://localhost:8501`.

Para detener el contenedor:
```bash
docker compose down
```

---

## ☁️ Despliegue en Streamlit Community Cloud
1. Sube este repositorio a GitHub.
2. Ingresa a [share.streamlit.io](https://share.streamlit.io/).
3. Selecciona tu repositorio y rama principal.
4. Indica como archivo principal: `app.py`.
5. Selecciona Python **3.11** o **3.12**.
6. Haz clic en **Deploy**. Streamlit Cloud detectará automáticamente `requirements.txt` o `pyproject.toml` y desplegará la aplicación en segundos.

---

## 📂 Estructura del Proyecto
```
INTEGRACION DE APLICACIONES/
├── app.py                        # Punto de entrada de la aplicación Streamlit
├── pyproject.toml                # Configuración de dependencias y proyecto uv
├── requirements.txt              # Requisitos compilados para Streamlit Cloud
├── Dockerfile                    # Contenedor para Ubuntu 24.04 / producción
├── docker-compose.yml            # Orquestación lista para Docker
├── NOTA_TECNICA.md               # Entregable 2: Supuestos y validación de 13 valores de control
├── RECOMENDACION_CONSEJO.md      # Entregable 3: Memorando ejecutivo para el Consejo (2 págs.)
├── data/
│   ├── resguarda_datos_caso.xlsx # Libro maestro oficial del caso (6 hojas)
│   └── plantilla_template.xlsx   # Plantilla descargable para el usuario
├── src/
│   ├── model/
│   │   ├── constants.py          # Parámetros oficiales de los Anexos 1 al 11
│   │   ├── engine.py             # Motor analítico: capacidad, Little, calidad, inventarios y finanzas
│   │   ├── strategies.py         # Definición de las 4 estrategias analizadas
│   │   └── data_loader.py        # Generador de plantillas y lector/validador de Excel
│   ├── reports/
│   │   └── pdf_generator.py      # Generador del informe corporativo en PDF (fpdf2)
│   ├── components/
│   │   ├── cards.py              # Tarjetas KPI, encabezados y alertas
│   │   ├── charts.py             # Gráficos interactivos Plotly (cuello de botella, tornado, radar, líneas)
│   │   └── styles.py             # Inyección de estilos CSS corporativos
│   └── views/
│       ├── view_simulador.py     # Vista 1: Simulador interactivo semana a semana con palancas
│       ├── view_diagnostico.py   # Vista 2: Balance de línea, Little y desmitificación de Cabrera
│       ├── view_escenarios.py    # Vista 3: Matriz de decisión, Valor Esperado (VE) y Peor Caso
│       ├── view_sensibilidad.py  # Vista 4: Diagrama de tornado y umbrales de decisión
│       ├── view_recomendacion.py # Vista 5: Memorando ejecutivo para Andrés Peña y el Consejo
│       ├── view_nota_tecnica.py  # Vista 6: Nota técnica y tabla de auditoría (13 valores)
│       └── view_gestion_datos.py # Vista 0: Carga de Excel personalizado y descarga de plantilla
└── tests/
    └── test_model.py             # Suite de pruebas automatizadas
```

---

## 📝 Documentos Entregables Incluidos
- **[NOTA_TECNICA.md](NOTA_TECNICA.md)**: Documento de una página con la validación de los 13 valores de control, supuestos operativos y trazabilidad de fórmulas.
- **[RECOMENDACION_CONSEJO.md](RECOMENDACION_CONSEJO.md)**: Memorando ejecutivo de dos páginas para el Consejo de Administración con la justificación de la Estrategia Ágil Secuencial.
