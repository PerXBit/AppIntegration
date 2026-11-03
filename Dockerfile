# Dockerfile para Tablero Simulador Resguarda (HCC)
# Compatible con Ubuntu 24.04 LTS y Streamlit Cloud

FROM python:3.12-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

# Instalar uv para gestión ultrarrápida de dependencias
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar archivos de dependencias
COPY pyproject.toml requirements.txt ./

# Instalar dependencias en el entorno del sistema
RUN uv pip install --system -r requirements.txt

# Copiar código fuente y datos
COPY . .

# Generar archivos de datos maestros si no existen
RUN python -c "from src.model.data_loader import ensure_default_excel_files; ensure_default_excel_files()"

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py"]
