# Dashboard Financiero Comparativo — Superintendencia de Sociedades de Colombia

**Proyecto de Grado — Especialización en Analítica de Datos**  
**Autor:** Candidato a Especialista en Analítica de Datos  
**Despliegue en la Nube:** [Ver Dashboard en Streamlit Community Cloud](https://dashboard-financiero-supersociedades.streamlit.app) *(Marcador de posición para el despliegue final)*

---

## 1. Descripción del Proyecto

Este proyecto consiste en un **dashboard analítico e interactivo desarrollado en Streamlit (Python)** para el análisis comparativo del **Estado de Resultado Integral** de las sociedades comerciales que reportan sus estados financieros bajo normas NIIF ante la Superintendencia de Sociedades de Colombia.

### Problema que Resuelve
Históricamente, los analistas de riesgo crediticio, evaluadores de inversiones y supervisores gubernamentales se han enfrentado a una seria dificultad operativa: la información financiera pública se difunde dispersa entre múltiples archivos y sin homologación metodológica entre periodos contables. Esto obligaba a realizar un cruce manual en hojas de cálculo, proceso lento, repetitivo y altamente susceptible a errores aritméticos (como divisiones por cero o doble conteo de facturación cuando una misma sociedad radica reportes en fechas de corte intermedias).

### Solución Aportada
Este dashboard centraliza, audita y homogeniza la información del **Formulario 310030 (Estado de resultado integral, resultado del periodo, por función de gasto)**, permitiendo a los analistas:
- Comparar de forma instantánea el desempeño operativo y márgenes brutos entre **1.257 empresas colombianas**.
- Manejar con transparencia algorítmica los valores nulos, registros con ingresos en cero y múltiples fechas de corte sin enmascarar ni alterar la veracidad de los datos.
- Filtrar en tiempo real por periodo contable, actividad económica (CIIU Rev. 4) y búsqueda directa por NIT o Razón Social.
- Exportar conjuntos de datos filtrados y auditados a formatos CSV y Microsoft Excel (.xlsx).

---

## 2. Reglas de Negocio y Calidad de Datos

1. **Valores nulos en Ingresos y Costo de Ventas:**  
   Se identificaron 269 registros con ingresos nulos y 678 con costo nulo. Bajo ninguna circunstancia se convierten en cero silenciosamente; el sistema los clasifica y visualiza explícitamente como **"Sin reporte"**.
2. **Ingresos en Cero y Cálculo de Margen:**  
   Para 55 registros con ingresos iguales a cero, el cálculo de margen bruto no se fuerza ni se asigna 0%; se clasifica y muestra como **"No aplica / No comparable"**, protegiendo los cálculos de divisiones por cero.
3. **Múltiples Fechas de Corte para un mismo NIT:**  
   Existen 8 empresas que reportaron en fechas intermedias (marzo, abril, junio, octubre) y al cierre anual (diciembre 2025). La **Regla de Corte más Reciente** selecciona de forma unívoca el reporte cronológicamente más actualizado por periodo contable, eliminando duplicidades y evitando el doble conteo de facturación en rankings y KPIs. El usuario puede alternar entre la regla recomendada y la vista completa desde la barra lateral.
4. **Clasificación Sectorial:**  
   Dado que el dataset no posee una columna literal de "Sector", se empleó la columna oficial `Clasificación Industrial Internacional Uniforme Versión 4 A.C (CIIU)` para mapear las divisiones alfabéticas oficiales (A a la S) en 18 macrosectores estandarizados por el DANE.

---

## 3. Estructura del Repositorio

```text
PROYECTO DE GRADO/
├── app.py                  # Aplicación principal de Streamlit con las 12 secciones y navegación por pestañas
├── data_utils.py           # Módulo de funciones de carga, normalización, control de calidad y cálculo de KPIs
├── requirements.txt        # Dependencias estrictas de Python (streamlit, pandas, plotly, openpyxl, etc.)
├── runtime.txt             # Versión de entorno Python para Streamlit Community Cloud (python-3.11)
├── .gitignore              # Configuración de exclusiones para Git (entornos virtuales, temporales, etc.)
├── README.md               # Documentación integral del proyecto
├── assets/                 # Diagramas estáticos de alta resolución embebidos en el dashboard
│   ├── flujo_datos.png     # Diagrama de arquitectura del flujo de datos
│   └── ciclo_crisp_dm.png  # Diagrama de las fases metodológicas CRISP-DM
└── data/                   # Carpeta de datos oficiales con ruta relativa portable
    └── 310030_Estado de resultado integral, resultado del periodo, por funcion de gasto.xlsx
```

---

## 4. Instrucciones para Ejecutar Localmente

### Requisitos Previos
- Tener instalado **Python 3.10 o superior** (se recomienda Python 3.11).
- Git instalado en el equipo.

### Paso a Paso

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd "PROYECTO DE GRADO"
   ```

2. **Crear y activar un entorno virtual:**
   - En Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - En Linux / macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar las dependencias requeridas:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el dashboard interactivo:**
   ```bash
   streamlit run app.py
   ```
   *(Si el comando `streamlit` no se encuentra en el PATH global, ejecute: `python -m streamlit run app.py`)*

5. **Acceder en el navegador:**
   La aplicación se abrirá automáticamente en:
   ```text
   http://localhost:8501
   ```

---

## 5. Metodología Aplicada: CRISP-DM

El proyecto se estructuró siguiendo las seis fases del estándar **CRISP-DM**:
1. **Comprensión del Negocio:** Definición de requerimientos para analistas de riesgo y supervisión.
2. **Comprensión de los Datos:** Exploración y auditoría de 2.524 registros y 35 columnas del formulario 310030.
3. **Preparación de los Datos:** Homologación de variables, desduplicación cronológica por corte y asignación de etiquetas de calidad.
4. **Modelado y Construcción de Indicadores:** Fórmulas financieras con control zero-div y agrupaciones sectoriales CIIU.
5. **Evaluación:** Validación cruzada de totales contables y consistencia lógica de márgenes negativos.
6. **Despliegue:** Implementación en Streamlit con visualizaciones interactivas Plotly y despliegue en Streamlit Community Cloud.

---

## 6. Despliegue en Streamlit Community Cloud

Para desplegar este repositorio en [share.streamlit.io](https://share.streamlit.io):
- **Repository:** `<tu-usuario>/<tu-repositorio>`
- **Branch:** `main`
- **Main file path:** `app.py`
- El servicio detectará automáticamente `requirements.txt` y `runtime.txt` para configurar el entorno en la nube.

---

## 7. Aviso Legal y Regulatorio

Este aplicativo y sus análisis tienen una finalidad exclusivamente académica y pedagógica para la **Especialización en Analítica de Datos**. Las métricas, rankings y gráficos resultantes **no constituyen aval oficial, certificación de auditoría contable, dictamen de insolvencia ni calificación de riesgo crediticio** vinculante para ninguna de las sociedades reportantes.
