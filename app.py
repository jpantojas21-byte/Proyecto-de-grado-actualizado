"""
DASHBOARD FINANCIERO INTERACTIVO — SUPERINTENDENCIA DE SOCIEDADES DE COLOMBIA
Proyecto de Grado para la Especialización en Analítica de Datos
Autor: Candidato a Especialista en Analítica de Datos

Tecnologías: Python, Streamlit, Plotly, Pandas, NumPy, OpenPyXL.
"""

from pathlib import Path
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import data_utils

# ==============================================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Financiero — Superintendencia de Sociedades",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos CSS profesionales (sin emojis, tipografía Inter, estética ejecutiva)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, .stText, p, span, h1, h2, h3, h4, button, input {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Contenedor principal */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1380px;
    }
    
    /* Tarjetas de Indicadores KPI */
    .kpi-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.4rem;
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.76rem;
        color: #64748b;
        margin-top: 0.35rem;
    }
    
    /* Iconos vectoriales minimalistas */
    .icon-badge {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #f1f5f9;
        color: #475569;
    }
    
    /* Cajas de notas y advertencias */
    .info-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 0.9rem 1.1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.5;
    }
    .warning-box {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 0.9rem 1.1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.88rem;
        color: #78350f;
        line-height: 1.5;
    }
    .rule-box {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 0.9rem 1.1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.88rem;
        color: #14532d;
        line-height: 1.5;
    }
    
    /* Pie de sección con fuente y fecha */
    .data-footer {
        border-top: 1px solid #e2e8f0;
        padding-top: 0.6rem;
        margin-top: 1.6rem;
        font-size: 0.74rem;
        color: #64748b;
        text-align: right;
    }
    
    /* Texto explicativo superior de gráficos */
    .chart-guide {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.8rem;
        font-size: 0.83rem;
        color: #475569;
        line-height: 1.45;
    }
    
    /* Ajustes pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 8px;
        padding-bottom: 8px;
        font-size: 0.88rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# CARGA Y GESTIÓN DE DATOS EN SESIÓN (SESSION STATE & CACHE)
# ==============================================================================
@st.cache_data(show_spinner=False)
def get_processed_data():
    """
    Carga el dataset oficial y aplica las reglas de auditoría y cálculo de márgenes.
    Utiliza st.cache_data para garantizar alto rendimiento en interacciones.
    """
    df_raw = data_utils.load_raw_dataset()
    df_audited = data_utils.audit_and_calculate_indicators(df_raw)
    return df_audited

# Carga de datos base
df_base = get_processed_data()

# Inicialización de estado de sesión para filtros dinámicos
if 'selected_period' not in st.session_state:
    st.session_state['selected_period'] = 'Todos los periodos'
if 'selected_cut_rule' not in st.session_state:
    st.session_state['selected_cut_rule'] = 'most_recent'
if 'selected_sector' not in st.session_state:
    st.session_state['selected_sector'] = 'Todos los sectores'
if 'search_company' not in st.session_state:
    st.session_state['search_company'] = []


# ==============================================================================
# SECCIÓN 3: FILTROS GLOBALES (BARRA LATERAL)
# ==============================================================================
with st.sidebar:
    st.markdown("### Filtros de Análisis")
    st.markdown(
        "<p style='font-size: 0.8rem; color: #64748b; margin-top: -8px;'>"
        "Los parámetros seleccionados actualizan en tiempo real todas las vistas y KPIs del dashboard."
        "</p>",
        unsafe_allow_html=True
    )
    
    # 1. Filtro de Periodo
    periodos_disponibles = ['Todos los periodos'] + sorted(list(df_base['periodo'].unique()))
    periodo_idx = periodos_disponibles.index(st.session_state['selected_period']) if st.session_state['selected_period'] in periodos_disponibles else 0
    selected_period = st.selectbox(
        "Periodo Contable:",
        options=periodos_disponibles,
        index=periodo_idx,
        help="El dataset reporta dos periodos: 'Periodo Actual' y 'Periodo Anterior' de acuerdo con el formato NIIF de la Supersociedades."
    )
    st.session_state['selected_period'] = selected_period

    # 2. Regla de Tratamiento de Fechas de Corte (Visible para el usuario)
    st.markdown("---")
    st.markdown(
        "<span style='font-size: 0.82rem; font-weight: 600; color: #1e293b;'>Tratamiento de Múltiples Cortes:</span>",
        unsafe_allow_html=True
    )
    cut_rule_options = {
        'most_recent': 'Corte más reciente por NIT (Recomendado)',
        'all_records': 'Todos los cortes (Sin desduplicar)'
    }
    selected_cut_rule_label = st.radio(
        "Regla de corte:",
        options=list(cut_rule_options.keys()),
        format_func=lambda x: cut_rule_options[x],
        index=0 if st.session_state['selected_cut_rule'] == 'most_recent' else 1,
        help="Permite resolver casos donde una empresa tiene múltiples reportes (ej. corte semestral y de fin de año) para el mismo periodo."
    )
    st.session_state['selected_cut_rule'] = selected_cut_rule_label

    # 3. Filtro por Macrosector / Clasificación CIIU
    st.markdown("---")
    # NOTA SOBRE SECTOR/INDUSTRIA: El dataset original de la Superintendencia de Sociedades
    # no incluye una columna llamada textualmente 'Sector' o 'Industria'. En su lugar,
    # contiene el campo formal 'Clasificación Industrial Internacional Uniforme Versión 4 A.C (CIIU)'.
    # Se extrajo la división/macrosector económico oficial a partir del prefijo alfabético del código CIIU.
    # Si a futuro se incorpora una columna externa con otra categorización de sector, puede integrarse aquí.
    sectores_disponibles = ['Todos los sectores'] + sorted(list(df_base['macrosector'].unique()))
    sector_idx = sectores_disponibles.index(st.session_state['selected_sector']) if st.session_state['selected_sector'] in sectores_disponibles else 0
    selected_sector = st.selectbox(
        "Sector Económico (CIIU Rev. 4):",
        options=sectores_disponibles,
        index=sector_idx,
        help="Clasificación derivada oficialmente del código CIIU presente en el formulario de la Supersociedades."
    )
    st.session_state['selected_sector'] = selected_sector

    # 4. Filtro por Empresa (Búsqueda por Razón Social o NIT)
    st.markdown("---")
    lista_empresas = sorted(list(df_base['razon_social'].unique()))
    selected_companies = st.multiselect(
        "Filtrar por Empresa (Nombre):",
        options=lista_empresas,
        default=st.session_state['search_company'],
        placeholder="Seleccione o escriba nombres...",
        help="Deje vacío para incluir todas las empresas del corte/sector seleccionado."
    )
    st.session_state['search_company'] = selected_companies

    # Búsqueda directa por NIT
    busqueda_nit = st.text_input(
        "O buscar por NIT específico:",
        value="",
        placeholder="Ejemplo: 800251163",
        help="Filtra inmediatamente por coincidencia exacta o parcial de NIT."
    ).strip()

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.72rem; color: #64748b; line-height: 1.4;'>"
        "<strong>Resumen del Filtro Activo:</strong><br>"
        f"Periodo: {st.session_state['selected_period']}<br>"
        f"Regla: {'Corte más reciente' if st.session_state['selected_cut_rule'] == 'most_recent' else 'Todos los cortes'}<br>"
        f"Sector: {'Todos' if st.session_state['selected_sector'] == 'Todos los sectores' else st.session_state['selected_sector'][:32] + '...'}"
        "</div>",
        unsafe_allow_html=True
    )


# ==============================================================================
# APLICACIÓN DE FILTROS AL DATASET
# ==============================================================================
# 1. Aplicar regla de corte seleccionada
df_cortes, meta_cortes = data_utils.apply_cut_rule(df_base, st.session_state['selected_cut_rule'])

# 2. Filtrar por periodo
df_filtrado = df_cortes.copy()
if st.session_state['selected_period'] != 'Todos los periodos':
    df_filtrado = df_filtrado[df_filtrado['periodo'] == st.session_state['selected_period']]

# 3. Filtrar por sector
if st.session_state['selected_sector'] != 'Todos los sectores':
    df_filtrado = df_filtrado[df_filtrado['macrosector'] == st.session_state['selected_sector']]

# 4. Filtrar por empresas seleccionadas
if len(st.session_state['search_company']) > 0:
    df_filtrado = df_filtrado[df_filtrado['razon_social'].isin(st.session_state['search_company'])]

# 5. Filtrar por NIT si fue ingresado
if busqueda_nit:
    df_filtrado = df_filtrado[df_filtrado['nit'].str.contains(busqueda_nit, case=False, na=False)]

# Cálculo de KPIs para el conjunto filtrado
kpis = data_utils.calculate_global_kpis(df_filtrado)


# ==============================================================================
# ENCABEZADO PRINCIPAL DEL DASHBOARD
# ==============================================================================
st.markdown(
    """
    <div style='margin-bottom: 1.2rem;'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <div>
                <h1 style='font-size: 1.95rem; font-weight: 800; color: #0f172a; margin-bottom: 0.25rem;'>
                    Dashboard Comparativo de Desempeño Financiero
                </h1>
                <p style='font-size: 0.95rem; color: #475569; margin: 0;'>
                    Análisis del Estado de Resultado Integral — Empresas reportantes a la Superintendencia de Sociedades de Colombia
                </p>
            </div>
            <div style='text-align: right; font-size: 0.78rem; color: #64748b;'>
                <span>Especialización en Analítica de Datos</span><br>
                <span style='font-weight: 600; color: #0284c7;'>Proyecto de Grado Aplicado</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Banner visible de la Regla de Corte aplicada
if meta_cortes['regla_aplicada'] == 'most_recent' and meta_cortes['registros_descartados'] > 0:
    st.markdown(
        f"""
        <div class='rule-box'>
            <strong>Regla de Corte Activa:</strong> Se consolidó el <em>corte más reciente</em> por empresa y periodo. 
            Se depuraron {meta_cortes['registros_descartados']} registros intermedios de {meta_cortes['nits_con_multiples_cortes_conteo']} NITs 
            con múltiples reportes para evitar duplicidades en los agregados. Esta regla puede ajustarse en el panel lateral.
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# NAVEGACIÓN PRINCIPAL MEDIANTE PESTAÑAS (TABS)
# ==============================================================================
tab_inicio, tab_alcance, tab_kpis, tab_comparacion, tab_evolucion, tab_distribucion, tab_dispersion, tab_tabla, tab_metodologia, tab_logros, tab_limitaciones = st.tabs([
    "1. Inicio",
    "2. Fuente y Alcance",
    "3. Panel de KPIs",
    "4. Comparación",
    "5. Evolución",
    "6. Distribución de Márgenes",
    "7. Ingresos vs. Margen",
    "8. Tabla Detallada",
    "9. Metodología CRISP-DM",
    "10. Qué se logró con el dashboard",
    "11. Limitaciones y Advertencias"
])


# ==============================================================================
# 1. INICIO / PRESENTACIÓN
# ==============================================================================
with tab_inicio:
    st.markdown("### Presentación del Proyecto")
    
    st.markdown("""
    Este dashboard interactivo nace como respuesta a un desafío crítico en la práctica de la analítica financiera corporativa en Colombia: 
    los analistas de riesgo de crédito, analistas de inversión y especialistas de supervisión institucional carecen de herramientas 
    ágiles y centralizadas para contrastar de forma confiable el desempeño financiero de las sociedades comerciales que reportan sus estados 
    financieros bajo normas NIIF ante la Superintendencia de Sociedades. Tradicionalmente, esta información se difunde en archivos planos 
    o planillas dispersas y sin homologación metodológica entre cortes temporales, lo cual somete al analista a procesos de cruce manual 
    artesanales, lentos y altamente susceptibles a sesgos o errores de cálculo.
    
    El objetivo central de esta solución es facilitar la exploración y el análisis comparativo del Estado de Resultado Integral 
    (formulario oficial 310030) reportado durante los ejercicios contables recientes (2023-2025). A través de indicadores financieros rigurosos, 
    advertencias explícitas sobre la calidad y comparabilidad del dato, y una visualización analítica integral, el sistema permite evaluar en 
    cuestión de segundos márgenes brutos, estructuras de costo y dimensiones operativas sin falsear ni enmascarar las limitaciones intrínsecas 
    del reporte público.
    
    **¿Cómo utilizar esta herramienta?**
    1. Utilice los controles de la barra lateral izquierda para acotar el análisis según el **Periodo Contable**, la **Actividad Económica (CIIU)** 
       o empresas individuales por **Razón Social o NIT**.
    2. Revise la regla de desduplicación de cortes activa para comprender cómo se unifican las fechas de reporte múltiple.
    3. Navegue entre las diferentes pestañas temáticas para evaluar desde métricas macroeconómicas consolidadas (KPIs) hasta rankings de empresas, 
       análisis de dispersión sectorial y la tabla de auditoría con descarga directa de datos en CSV y Excel.
    """)
    
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Estado de Resultado Integral (NIIF Plenas)
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 2. FUENTE Y ALCANCE DE LOS DATOS
# ==============================================================================
with tab_alcance:
    st.markdown("### Fuente Oficial y Cobertura Verificada")
    
    c_f1, c_f2 = st.columns([1, 1])
    
    with c_f1:
        st.markdown("""
        **Ficha Técnica del Dataset Oficial:**
        - **Entidad emisora:** Superintendencia de Sociedades de Colombia (Portal de Información Empresarial - SIREM).
        - **Formulario contable:** *310030 — Estado de resultado integral, resultado del periodo, por función de gasto* (Marco Técnico NIIF Plenas / Grupo 1).
        - **Total de registros brutos disponibles:** **2.524 filas** correspondientes a **1.257 empresas colombianas** (NITs únicos).
        - **Periodos contables reportados:** `Periodo Actual` (1.262 registros) y `Periodo Anterior` (1.262 registros), permitiendo un análisis comparativo bienal.
        - **Fechas de corte registradas:** La fecha predominante de reporte es el cierre anual a `2025-12-31` (2.512 registros), existiendo cortes intermedios a `2025-06-30` (6 registros), `2025-03-31` (2 registros), `2025-04-30` (2 registros) y `2025-10-31` (2 registros).
        - **Clasificación sectorial disponible:** Se dispone del campo oficial *Clasificación Industrial Internacional Uniforme Versión 4 A.C (CIIU)* con 214 actividades económicas representadas en 18 macrosectores nacionales.
        """)
        
        st.markdown(
            """
            <div class='warning-box'>
                <strong>Advertencia de Uso y Alcance Regulatorio:</strong><br>
                La información procesada en este dashboard tiene un propósito estrictamente académico, analítico e investigativo. 
                Los indicadores, comparaciones y ordenamientos aquí mostrados <strong>no constituyen aval oficial, certificación de auditoría, 
                juicio de insolvencia ni calificación formal de riesgo crediticio</strong> de ninguna de las personas jurídicas referenciadas.
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with c_f2:
        st.markdown("**Diagrama del Flujo de Datos Financieros:**")
        diagram_path = Path(__file__).resolve().parent / "assets" / "flujo_datos.png"
        if diagram_path.exists():
            st.image(str(diagram_path), caption="Arquitectura del flujo de datos: desde la fuente oficial hasta el dashboard interactivo.", width='stretch')
        else:
            st.info("El diagrama de arquitectura de datos se encuentra en proceso de carga.")
            
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Formulario Oficial 310030 | Fechas de corte: 2025-03-31 a 2025-12-31
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 4. PANEL DE INDICADORES CLAVE (KPIS)
# ==============================================================================
with tab_kpis:
    st.markdown("### Panel de Indicadores Clave de Desempeño (KPIs)")
    st.markdown(
        "<div class='chart-guide'>"
        "<strong>Guía de interpretación de los KPIs:</strong> "
        "Las siguientes tarjetas consolidan las magnitudes financieras del grupo de empresas filtrado actualmente. "
        "El <em>Margen Bruto Ponderado</em> divide la Ganancia Bruta Total entre los Ingresos Totales de todo el grupo, "
        "mientras que el <em>Margen Promedio Simple</em> refleja la media aritmética de los márgenes individuales exclusivamente "
        "para aquellos registros donde el indicador es comparable (ingresos estrictamente superiores a cero)."
        "</div>",
        unsafe_allow_html=True
    )
    
    # Fila 1 de KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-header'>
                    <span class='kpi-title'>Ingresos Totales</span>
                    <span class='icon-badge'>COP</span>
                </div>
                <div class='kpi-value'>{data_utils.format_currency_cop(kpis['total_ingresos'])}</div>
                <div class='kpi-subtitle'>{kpis['sin_reporte_ingresos']} registros sin reporte</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-header'>
                    <span class='kpi-title'>Costo de Ventas Total</span>
                    <span class='icon-badge'>CV</span>
                </div>
                <div class='kpi-value'>{data_utils.format_currency_cop(kpis['total_costos'])}</div>
                <div class='kpi-subtitle'>{kpis['sin_reporte_costos']} registros sin reporte</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-header'>
                    <span class='kpi-title'>Ganancia Bruta Total</span>
                    <span class='icon-badge'>GB</span>
                </div>
                <div class='kpi-value'>{data_utils.format_currency_cop(kpis['total_ganancia_bruta'])}</div>
                <div class='kpi-subtitle'>Ingresos menos Costo de Ventas</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col4:
        margen_p_txt = f"{kpis['margen_ponderado']:.2f}%" if kpis['margen_ponderado'] is not None else "No comparable"
        margen_s_txt = f"{kpis['margen_promedio_simple']:.2f}%" if kpis['margen_promedio_simple'] is not None else "No comparable"
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-header'>
                    <span class='kpi-title'>Margen Bruto Ponderado</span>
                    <span class='icon-badge'>%</span>
                </div>
                <div class='kpi-value'>{margen_p_txt}</div>
                <div class='kpi-subtitle'>Promedio simple: {margen_s_txt}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col5:
        st.markdown(
            f"""
            <div class='kpi-container'>
                <div class='kpi-header'>
                    <span class='kpi-title'>Empresas en Filtro</span>
                    <span class='icon-badge'>N</span>
                </div>
                <div class='kpi-value'>{kpis['empresas_unicas']:,}</div>
                <div class='kpi-subtitle'>{kpis['total_registros']:,} registros analizados</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # Fila de auditoría de calidad de datos
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    c_aud1, c_aud2, c_aud3 = st.columns(3)
    with c_aud1:
        st.markdown(
            f"<div class='info-box'>"
            f"<strong>Registros Comparables de Margen:</strong> {kpis['comparables_margen']:,} registros con ingresos válidos y mayores a cero."
            f"</div>",
            unsafe_allow_html=True
        )
    with c_aud2:
        st.markdown(
            f"<div class='warning-box'>"
            f"<strong>Registros 'No Aplica / No Comparable':</strong> {kpis['no_comparables_margen']:,} empresas con ingresos reportados en cero (evita división por cero)."
            f"</div>",
            unsafe_allow_html=True
        )
    with c_aud3:
        st.markdown(
            f"<div class='info-box'>"
            f"<strong>Registros 'Sin Reporte':</strong> {kpis['sin_reporte_margen']:,} registros con campo de ingresos o ganancia bruta nulos (no convertidos a cero)."
            f"</div>",
            unsafe_allow_html=True
        )
        
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Estado de Resultado Integral (NIIF) | Cálculos propios
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 5. COMPARACIÓN ENTRE EMPRESAS (RANKING HORIZONTAL)
# ==============================================================================
with tab_comparacion:
    st.markdown("### Comparación y Ranking de Empresas")
    
    st.markdown(
        """
        <div class='chart-guide'>
            <strong>¿Qué muestra este gráfico y cómo leerlo?</strong><br>
            Este gráfico de barras horizontales responde a la pregunta medular del analista: <em>¿Qué empresas presentan el mayor o menor nivel de desempeño?</em> 
            Permite clasificar las organizaciones del filtro de mayor a menor según el indicador financiero elegido (Margen Bruto porcentual o Ingresos brutos). 
            Las barras orientadas hacia la derecha representan márgenes positivos o mayor volumen de facturación. Si una empresa registra margen bruto negativo 
            (costo de ventas superior al ingreso), su barra se extenderá hacia la izquierda con coloración de alerta. Los registros sin ingresos o no comparables 
            se excluyen automáticamente del ranking porcentual para salvaguardar la veracidad estadística.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    c_ctrl1, c_ctrl2 = st.columns([1, 1])
    with c_ctrl1:
        criterio_orden = st.radio(
            "Criterio de Ordenamiento:",
            options=["Margen Bruto (%)", "Ingresos de Actividades Ordinarias (COP)"],
            horizontal=True
        )
    with c_ctrl2:
        top_n = st.slider("Número de empresas a visualizar en el ranking:", min_value=5, max_value=50, value=15, step=5)
        
    if criterio_orden == "Margen Bruto (%)":
        df_ranking = df_filtrado[df_filtrado['calidad_margen'] == 'Comparable'].copy()
        df_ranking = df_ranking.sort_values(by='margen_bruto_pct', ascending=False).head(top_n)
        
        if len(df_ranking) == 0:
            st.info("No se encontraron empresas con margen bruto comparable para los filtros seleccionados.")
        else:
            # Colores según si es positivo o negativo
            df_ranking['color_margen'] = df_ranking['margen_bruto_pct'].apply(lambda x: '#10b981' if x >= 0 else '#ef4444')
            
            fig_ranking = go.Figure()
            fig_ranking.add_trace(go.Bar(
                y=df_ranking['razon_social'],
                x=df_ranking['margen_bruto_pct'],
                orientation='h',
                marker=dict(color=df_ranking['color_margen']),
                text=df_ranking['margen_bruto_pct'].apply(lambda x: f"{x:.2f}%"),
                textposition='outside',
                hovertemplate="<b>%{y}</b><br>NIT: %{customdata[0]}<br>Margen Bruto: %{x:.2f}%<br>Ingresos: %{customdata[1]}<br>Ganancia Bruta: %{customdata[2]}<extra></extra>",
                customdata=np.stack((
                    df_ranking['nit'],
                    df_ranking['ingresos'].apply(data_utils.format_currency_cop),
                    df_ranking['ganancia_bruta'].apply(data_utils.format_currency_cop)
                ), axis=-1)
            ))
            
            fig_ranking.update_layout(
                title=f"Top {len(df_ranking)} Empresas por Margen Bruto Porcentual",
                xaxis_title="Margen Bruto (%)",
                yaxis_title="",
                yaxis=dict(autorange="reversed"),
                height=max(450, len(df_ranking) * 28),
                margin=dict(l=10, r=40, t=50, b=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#e2e8f0', zeroline=True, zerolinecolor='#64748b')
            )
            st.plotly_chart(fig_ranking, width='stretch')
            
    else:
        df_ranking = df_filtrado[df_filtrado['ingresos'].notna()].copy()
        df_ranking = df_ranking.sort_values(by='ingresos', ascending=False).head(top_n)
        
        if len(df_ranking) == 0:
            st.info("No se encontraron empresas con ingresos reportados para los filtros seleccionados.")
        else:
            fig_ranking = go.Figure()
            fig_ranking.add_trace(go.Bar(
                y=df_ranking['razon_social'],
                x=df_ranking['ingresos'],
                orientation='h',
                marker=dict(color='#3b82f6'),
                text=df_ranking['ingresos'].apply(data_utils.format_currency_cop),
                textposition='outside',
                hovertemplate="<b>%{y}</b><br>NIT: %{customdata[0]}<br>Ingresos: %{text}<br>Margen Bruto: %{customdata[1]}<extra></extra>",
                customdata=np.stack((
                    df_ranking['nit'],
                    df_ranking['margen_bruto_texto']
                ), axis=-1)
            ))
            
            fig_ranking.update_layout(
                title=f"Top {len(df_ranking)} Empresas por Volumen de Ingresos Ordinarios",
                xaxis_title="Ingresos de Actividades Ordinarias (COP)",
                yaxis_title="",
                yaxis=dict(autorange="reversed"),
                height=max(450, len(df_ranking) * 28),
                margin=dict(l=10, r=60, t=50, b=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#e2e8f0')
            )
            st.plotly_chart(fig_ranking, width='stretch')
            
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Estado de Resultado Integral (NIIF) | Fecha de corte del filtro activo
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 6. EVOLUCIÓN Y VARIACIÓN INTERANUAL
# ==============================================================================
with tab_evolucion:
    st.markdown("### Evolución y Variación Interanual (Periodo Anterior vs. Periodo Actual)")
    
    st.markdown(
        """
        <div class='chart-guide'>
            <strong>¿Qué muestra este gráfico y cómo leerlo?</strong><br>
            Este gráfico contrasta el comportamiento temporal de las empresas entre el <em>Periodo Anterior</em> y el <em>Periodo Actual</em> 
            reportados en el formulario contable NIIF. Permite comparar una o múltiples entidades simultáneamente para identificar trayectorias 
            de crecimiento o contracción en ingresos y rentabilidad. Cuando una empresa carece de reporte o presenta ingresos en cero en alguno de los 
            periodos, el sistema marca explícitamente el punto como <em>'No comparable'</em> o <em>'Sin reporte'</em> mediante notas visuales, 
            evitando distorsionar la pendiente de la línea con valores falsos de cero.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    c_ev1, c_ev2 = st.columns([2, 1])
    with c_ev1:
        # Selector de empresas específicas para la comparación temporal
        empresas_en_filtro = sorted(list(df_filtrado['razon_social'].unique()))
        default_evo = empresas_en_filtro[:3] if len(empresas_en_filtro) >= 3 else empresas_en_filtro
        empresas_evo = st.multiselect(
            "Seleccionar empresas para contrastar evolución temporal:",
            options=empresas_en_filtro,
            default=default_evo,
            help="Seleccione una o varias empresas para trazar sus líneas de tendencia comparativa."
        )
    with c_ev2:
        metrica_evo = st.selectbox(
            "Métrica a comparar:",
            options=["Ingresos de Actividades Ordinarias", "Margen Bruto (%)", "Ganancia Bruta"],
            index=0
        )
        
    if len(empresas_evo) == 0:
        st.info("Por favor seleccione al menos una empresa para generar la comparativa interanual.")
    else:
        # Filtrar datos de las empresas seleccionadas sobre el dataset con regla de corte
        df_evo = df_cortes[df_cortes['razon_social'].isin(empresas_evo)].copy()
        
        # Orden cronológico contable
        period_order = ['Periodo Anterior', 'Periodo Actual']
        df_evo['periodo_cat'] = pd.Categorical(df_evo['periodo'], categories=period_order, ordered=True)
        df_evo = df_evo.sort_values(by=['razon_social', 'periodo_cat'])
        
        fig_evo = go.Figure()
        
        for comp in empresas_evo:
            sub = df_evo[df_evo['razon_social'] == comp].sort_values(by='periodo_cat')
            
            if metrica_evo == "Ingresos de Actividades Ordinarias":
                y_vals = sub['ingresos']
                text_vals = sub['ingresos'].apply(data_utils.format_currency_cop)
                hovertemp = f"<b>{comp}</b><br>Periodo: %{{x}}<br>Ingresos: %{{text}}<extra></extra>"
            elif metrica_evo == "Margen Bruto (%)":
                y_vals = sub['margen_bruto_pct']
                text_vals = sub['margen_bruto_texto']
                hovertemp = f"<b>{comp}</b><br>Periodo: %{{x}}<br>Margen: %{{text}}<extra></extra>"
            else:
                y_vals = sub['ganancia_bruta']
                text_vals = sub['ganancia_bruta'].apply(data_utils.format_currency_cop)
                hovertemp = f"<b>{comp}</b><br>Periodo: %{{x}}<br>Ganancia Bruta: %{{text}}<extra></extra>"
                
            fig_evo.add_trace(go.Scatter(
                x=sub['periodo'],
                y=y_vals,
                mode='lines+markers+text',
                name=comp[:30] + ('...' if len(comp) > 30 else ''),
                text=text_vals,
                textposition='top center',
                hovertemplate=hovertemp,
                line=dict(width=2.5),
                marker=dict(size=8)
            ))
            
            # Anotaciones visuales explícitas para puntos no comparables o sin reporte
            for _, r in sub.iterrows():
                if metrica_evo == "Margen Bruto (%)" and r['calidad_margen'] != 'Comparable':
                    fig_evo.add_annotation(
                        x=r['periodo'],
                        y=0,
                        text=f"[{r['calidad_margen']}]",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor="#f59e0b",
                        font=dict(color="#b45309", size=9)
                    )
                elif metrica_evo != "Margen Bruto (%)" and pd.isna(r['ingresos']):
                    fig_evo.add_annotation(
                        x=r['periodo'],
                        y=0,
                        text="[Sin reporte]",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor="#f59e0b",
                        font=dict(color="#b45309", size=9)
                    )

        fig_evo.update_layout(
            title=f"Tendencia Interanual — {metrica_evo}",
            xaxis_title="Periodo Contable",
            yaxis_title=metrica_evo,
            height=480,
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_evo, width='stretch')
        
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Estado de Resultado Integral (NIIF) | Cobertura comparativa bienal
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 7. DISTRIBUCIÓN DE MÁRGENES (BOXPLOT / DISPERSIÓN SECTORIAL)
# ==============================================================================
with tab_distribucion:
    st.markdown("### Distribución y Dispersión de Márgenes Brutos")
    
    st.markdown(
        """
        <div class='chart-guide'>
            <strong>¿Qué muestra este gráfico y cómo leerlo?</strong><br>
            Este diagrama de caja (Boxplot) visualiza la dispersión estructural de la rentabilidad bruta en el conjunto de empresas analizado. 
            Permite apreciar no solo la mediana central (línea divisoria de la caja) y los cuartiles intermedios (rango del 50% central de las empresas), 
            sino también la amplitud de los límites y los valores atípicos (outliers). 
            <em>Justificación analítica:</em> Permite al supervisor y analista comprender la heterogeneidad del sector sin señalar a una empresa en particular 
            como 'anómala' de forma injusta o apresurada, entendiendo que ciertos modelos de negocio operan legítimamente con estructuras de costo atípicas.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Filtrar únicamente registros comparables
    df_box = df_filtrado[df_filtrado['calidad_margen'] == 'Comparable'].copy()
    
    if len(df_box) == 0:
        st.info("No existen suficientes registros con márgenes comparables para trazar la distribución.")
    else:
        c_bx1, c_bx2 = st.columns([1, 1])
        with c_bx1:
            agrupar_por_sector = st.checkbox("Desglosar por Macrosector Económico (CIIU)", value=False)
        with c_bx2:
            limitar_zoom = st.checkbox("Enfocar rango intercuartílico (-50% a 100%)", value=True, help="Oculta temporalmente casos extremos extremos para evaluar con claridad el grueso de la distribución.")
            
        fig_box = go.Figure()
        
        if agrupar_por_sector:
            # Seleccionar los sectores con al menos 5 empresas para que el boxplot tenga sentido estadístico
            sectores_conteo = df_box['macrosector'].value_counts()
            sectores_validos = sectores_conteo[sectores_conteo >= 5].index.tolist()
            df_box_sub = df_box[df_box['macrosector'].isin(sectores_validos)]
            
            for sec in sorted(sectores_validos):
                sec_data = df_box_sub[df_box_sub['macrosector'] == sec]
                fig_box.add_trace(go.Box(
                    y=sec_data['margen_bruto_pct'],
                    name=sec[:25] + ('...' if len(sec) > 25 else ''),
                    boxpoints='outliers',
                    jitter=0.2,
                    pointpos=-1.5,
                    hovertemplate=f"<b>{sec}</b><br>Margen Bruto: %{{y:.2f}}%<extra></extra>"
                ))
            title_bx = "Distribución de Margen Bruto por Macrosector Económico (CIIU)"
        else:
            fig_box.add_trace(go.Box(
                y=df_box['margen_bruto_pct'],
                name="Todas las empresas del filtro",
                boxpoints='outliers',
                jitter=0.2,
                pointpos=-1.5,
                marker=dict(color='#6366f1'),
                hovertemplate="Margen Bruto: %{y:.2f}%<extra></extra>"
            ))
            title_bx = "Distribución General del Margen Bruto Porcentual"
            
        fig_box.update_layout(
            title=title_bx,
            yaxis_title="Margen Bruto (%)",
            xaxis_title="",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', zeroline=True, zerolinecolor='#64748b')
        )
        if limitar_zoom:
            fig_box.update_layout(yaxis=dict(range=[-60, 110]))
            
        st.plotly_chart(fig_box, width='stretch')
        
        # Estadísticas descriptivas del boxplot
        st.markdown(
            f"""
            <div style='font-size: 0.82rem; color: #475569; background: #f8fafc; padding: 0.6rem 0.9rem; border-radius: 6px;'>
                <strong>Métricas de Dispersión del Filtro:</strong> Mediana: {df_box['margen_bruto_pct'].median():.2f}% | 
                Promedio: {df_box['margen_bruto_pct'].mean():.2f}% | 
                Percentil 25 (Q1): {df_box['margen_bruto_pct'].quantile(0.25):.2f}% | 
                Percentil 75 (Q3): {df_box['margen_bruto_pct'].quantile(0.75):.2f}% | 
                Márgenes negativos (pérdida bruta): {(df_box['margen_bruto_pct'] < 0).sum()} empresas.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Estado de Resultado Integral (NIIF) | Muestra comparable
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 8. RELACIÓN INGRESOS VS. MARGEN (SCATTER PLOT)
# ==============================================================================
with tab_dispersion:
    st.markdown("### Relación entre Escala de Ingresos y Margen Bruto")
    
    st.markdown(
        """
        <div class='chart-guide'>
            <strong>¿Qué muestra este gráfico y cómo leerlo?</strong><br>
            Este gráfico de dispersión bidimensional cruza la <em>Escala de Facturación (Ingresos Ordinarios)</em> en el eje horizontal 
            frente a la <em>Rentabilidad Bruta (Margen %)</em> en el eje vertical. 
            Las líneas punteadas indican las medianas de ambas variables, dividiendo el espacio en cuatro cuadrantes de análisis:
            <br>• <strong>Cuadrante Superior Derecho:</strong> Alta facturación y alto margen (Líderes de rentabilidad a escala).
            <br>• <strong>Cuadrante Superior Izquierdo:</strong> Menor escala y alto margen (Empresas de nicho o servicios intensivos).
            <br>• <strong>Cuadrante Inferior Derecho:</strong> Gran escala y bajo margen (Modelos de volumen, distribución o retail).
            <br>• <strong>Cuadrante Inferior Izquierdo:</strong> Menor escala y bajo margen (Empresas en consolidación o reestructuración).
            <br><em>Nota explicativa sobre neutralidad valorativa:</em> La ubicación, tamaño o color de una empresa en este plano cartográfico 
            responde estrictamente a su modelo de negocio contable y <strong>no implica ningún juicio de valor moral, solvencia o idoneidad jurídica</strong>.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    df_scat = df_filtrado[df_filtrado['calidad_margen'] == 'Comparable'].copy()
    
    if len(df_scat) == 0:
        st.info("No se encontraron registros comparables para elaborar el gráfico de dispersión.")
    else:
        c_sc1, c_sc2 = st.columns([1, 1])
        with c_sc1:
            escala_log = st.checkbox("Aplicar escala logarítmica en Ingresos", value=True, help="Facilita comparar simultáneamente empresas medianas junto a gigantes corporativos sin que se agrupen en el origen.")
        with c_sc2:
            color_por_sector = st.checkbox("Colorear por Macrosector Económico", value=True)
            
        mediana_ing = df_scat['ingresos'].median()
        mediana_mar = df_scat['margen_bruto_pct'].median()
        
        fig_scatter = px.scatter(
            df_scat,
            x='ingresos',
            y='margen_bruto_pct',
            color='macrosector' if color_por_sector else None,
            hover_name='razon_social',
            log_x=escala_log,
            labels={
                'ingresos': 'Ingresos de Actividades Ordinarias (COP)',
                'margen_bruto_pct': 'Margen Bruto (%)',
                'macrosector': 'Sector CIIU'
            },
            title="Matriz de Desempeño: Volumen de Ingresos vs. Margen Bruto",
            opacity=0.75
        )
        
        # Líneas de referencia de medianas
        fig_scatter.add_hline(
            y=mediana_mar,
            line_dash="dot",
            line_color="#94a3b8",
            annotation_text=f"Mediana Margen: {mediana_mar:.1f}%",
            annotation_position="bottom right"
        )
        fig_scatter.add_vline(
            x=mediana_ing,
            line_dash="dot",
            line_color="#94a3b8",
            annotation_text=f"Mediana Ingresos: {data_utils.format_currency_cop(mediana_ing)}",
            annotation_position="top left"
        )
        
        fig_scatter.update_layout(
            height=540,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', zeroline=True, zerolinecolor='#64748b'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.32, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_scatter, width='stretch')
        
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Estado de Resultado Integral (NIIF) | Escala comparativa
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 9. TABLA DETALLADA Y AUDITORÍA DE DATOS
# ==============================================================================
with tab_tabla:
    st.markdown("### Tabla Detallada de Estados Financieros y Calidad de Dato")
    
    st.markdown(
        """
        <div class='chart-guide'>
            <strong>Visualización y auditoría registro por registro:</strong><br>
            Esta tabla incluye la totalidad de los registros que cumplen con los filtros activos. Para garantizar absoluta transparencia analítica, 
            se presentan de forma explícita las columnas de calidad de dato: <em>Calidad Margen</em> (indicando si es Comparable, Sin reporte o No aplica), 
            <em>Calidad Ingresos</em> y <em>Calidad Costo</em>. Puede exportar el conjunto completo a formato CSV o Microsoft Excel (.xlsx).
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Preparación de columnas para la tabla de visualización
    cols_tabla = [
        'nit', 'razon_social', 'periodo', 'fecha_corte', 'macrosector',
        'ingresos', 'costo_ventas', 'ganancia_bruta', 'margen_bruto_texto',
        'calidad_margen', 'calidad_ingresos', 'calidad_costo'
    ]
    
    df_mostrar = df_filtrado[cols_tabla].rename(columns={
        'nit': 'NIT',
        'razon_social': 'Razón Social',
        'periodo': 'Periodo',
        'fecha_corte': 'Fecha de Corte',
        'macrosector': 'Macrosector CIIU',
        'ingresos': 'Ingresos (COP)',
        'costo_ventas': 'Costo de Ventas (COP)',
        'ganancia_bruta': 'Ganancia Bruta (COP)',
        'margen_bruto_texto': 'Margen Bruto',
        'calidad_margen': 'Estado Margen',
        'calidad_ingresos': 'Estado Ingresos',
        'calidad_costo': 'Estado Costo'
    })
    
    # Botones de exportación
    c_exp1, c_exp2, c_exp3 = st.columns([1, 1, 2])
    
    with c_exp1:
        csv_data = df_mostrar.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Descargar datos en CSV",
            data=csv_data,
            file_name="estados_financieros_supersociedades_filtrados.csv",
            mime="text/csv"
        )
        
    with c_exp2:
        # Generar buffer en memoria para Excel usando openpyxl
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_mostrar.to_excel(writer, index=False, sheet_name='Reporte_Financiero')
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="Descargar datos en Excel (.xlsx)",
            data=excel_data,
            file_name="estados_financieros_supersociedades_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with c_exp3:
        st.markdown(
            f"<div style='text-align: right; font-size: 0.82rem; color: #64748b; padding-top: 8px;'>"
            f"Mostrando <strong>{len(df_mostrar):,}</strong> filas filtradas de <strong>{len(df_base):,}</strong> totales."
            f"</div>",
            unsafe_allow_html=True
        )
        
    st.dataframe(
        df_mostrar,
        width='stretch',
        height=450,
        column_config={
            "Ingresos (COP)": st.column_config.NumberColumn(format="$%.2f"),
            "Costo de Ventas (COP)": st.column_config.NumberColumn(format="$%.2f"),
            "Ganancia Bruta (COP)": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Formulario 310030 NIIF | Exportación auditable
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 10. METODOLOGÍA (CRISP-DM)
# ==============================================================================
with tab_metodologia:
    st.markdown("### Metodología de Desarrollo: Ciclo CRISP-DM")
    
    st.markdown("""
    La concepción, estructuración y despliegue de esta solución analítica se condujo rigurosamente bajo el estándar 
    **CRISP-DM (Cross-Industry Standard Process for Data Mining)**, adaptado a la analítica de estados financieros corporativos:
    """)
    
    c_m1, c_m2 = st.columns([1, 1])
    
    with c_m1:
        st.markdown("""
        **1. Comprensión del Negocio (Business Understanding):**
        Identificación del cuello de botella analítico: analistas de riesgo y supervisores deben evaluar la solvencia y eficiencia operativa 
        de sociedades comerciales en Colombia, pero se enfrentan a depósitos de información no homologados, con dispersión temporal y falta 
        de estándares de comparabilidad rápida. Se definió como objetivo central construir una herramienta interactiva, veraz y reproducible.
        
        **2. Comprensión de los Datos (Data Understanding):**
        Auditoría técnica del Formulario 310030 (Estado de resultado integral) de la Superintendencia de Sociedades. 
        Se identificaron 35 columnas originales, detectando 269 registros con ingresos nulos, 678 con costos nulos y 55 con ingresos en cero, 
        además de 8 empresas con multiplicidad de fechas de corte radicadas.
        
        **3. Preparación de los Datos (Data Preparation):**
        Normalización de nomenclaturas contables y sanitización de problemas de codificación. 
        Implementación de la **Regla de Selección del Corte Más Reciente** para desduplicar registros y evitar el doble conteo de magnitudes. 
        Creación de etiquetas explícitas de calidad de dato (*Sin reporte*, *No aplica / No comparable*, *Comparable*).
        
        **4. Modelado y Construcción de Indicadores (Modeling):**
        Formulación de funciones financieras: cálculo de Margen Bruto Porcentual con salvaguarda algorítmica ante división por cero, 
        extracción jerárquica de macrosectores a partir del clasificador CIIU Rev. 4 A.C., y agregación de KPIs ponderados y simples.
        
        **5. Evaluación (Evaluation):**
        Contraste de consistencia lógica contable: validación de márgenes negativos (pérdidas brutas legítimas), verificación de la cobertura 
        bienal (1.110 empresas con reporte completo en ambos periodos) y auditoría cruzada de totales contra las cifras maestras de la fuente.
        
        **6. Despliegue (Deployment):**
        Construcción de la aplicación web interactiva en Streamlit, con persistencia de estado mediante `st.session_state`, visualizaciones 
        vectoriales Plotly dinámicas, módulos independientes en Python (`data_utils.py`) y arquitectura portable mediante rutas relativas (`pathlib`).
        """)
        
    with c_m2:
        diagram_crisp_path = Path(__file__).resolve().parent / "assets" / "ciclo_crisp_dm.png"
        if diagram_crisp_path.exists():
            st.image(str(diagram_crisp_path), caption="Ciclo de vida metodológico CRISP-DM aplicado a la analítica de estados financieros.", width='stretch')
        else:
            st.info("Diagrama metodológico en proceso de visualización.")
            
    st.markdown(
        """
        <div class='data-footer'>
            Marco Metodológico: CRISP-DM | Proyecto de Grado — Especialización en Analítica de Datos
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 11. QUÉ SE LOGRÓ CON EL DASHBOARD (SECCIÓN OBLIGATORIA)
# ==============================================================================
with tab_logros:
    st.markdown("### Qué se logró con el dashboard")
    
    st.markdown("""
    Esta sección sintetiza de forma objetiva y medible el impacto del dashboard desarrollado frente al proceso analítico tradicional, 
    vinculándolo directamente con las cifras reales arrojadas por el dataset de la Superintendencia de Sociedades:
    """)
    
    # Comparativa Antes vs Ahora
    c_comp1, c_comp2 = st.columns(2)
    with c_comp1:
        st.markdown(
            """
            <div style='background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1.1rem; height: 100%;'>
                <h4 style='color: #991b1b; margin-top: 0;'>Proceso Tradicional (Antes)</h4>
                <ul style='font-size: 0.86rem; color: #7f1d1d; line-height: 1.5; padding-left: 1.2rem;'>
                    <li><strong>Cruce manual lento y propenso a errores:</strong> Los analistas debían descargar archivos independientes de la Superintendencia, unificar nombres de columnas inconsistentes y construir fórmulas en hojas de cálculo.</li>
                    <li><strong>Riesgo de división por cero y sesgo numérico:</strong> Al calcular el margen bruto en hojas de cálculo tradicionales, las celdas con valor cero o vacías solían provocar errores <code>#¡DIV/0!</code> o eran transformadas erróneamente en 0%, distorsionando promedios.</li>
                    <li><strong>Doble conteo por multiplicidad de cortes:</strong> Si una empresa radicaba estados intermedios y de fin de año, el cruce manual solía sumar ambas filas, inflando artificialmente ingresos y costos.</li>
                    <li><strong>Tiempo de análisis:</strong> Horas o días dedicados exclusivamente a la limpieza antes de emitir la primera conclusión.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_comp2:
        st.markdown(
            """
            <div style='background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1.1rem; height: 100%;'>
                <h4 style='color: #166534; margin-top: 0;'>Con el Dashboard Desarrollado (Ahora)</h4>
                <ul style='font-size: 0.86rem; color: #14532d; line-height: 1.5; padding-left: 1.2rem;'>
                    <li><strong>Comparación instantánea y centralizada:</strong> En cuestión de segundos, el analista puede filtrar y ordenar las <strong>1.257 empresas</strong> por margen o facturación con trazabilidad completa.</li>
                    <li><strong>Manejo honesto de limitaciones del dato:</strong> Se auditaron con precisión los <strong>269 registros con ingresos nulos</strong> (clasificados como <em>'Sin reporte'</em>) y los <strong>55 registros con ingresos en cero</strong> (clasificados como <em>'No aplica / No comparable'</em>).</li>
                    <li><strong>Regla de desduplicación cronológica verificable:</strong> Se implementó un algoritmo transparente que consolidó el corte más reciente de <strong>4 NITs</strong> con reportes múltiples, eliminando 10 filas intermedias de forma auditable.</li>
                    <li><strong>Tiempo de análisis:</strong> Reducción de horas a segundos, liberando el tiempo del analista para la evaluación estratégica de riesgo.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    **Decisiones analíticas y de negocio que apoya este dashboard:**
    1. **Para Analistas de Riesgo de Crédito:** Permite contextualizar si una solicitud crediticia proviene de una empresa cuyo margen bruto se ubica en el cuartil superior o inferior de su macrosector CIIU, identificando si los costos de ventas amenazan su capacidad de cobertura operativa.
    2. **Para Analistas Financieros y de Inversión:** Identifica con rapidez organizaciones de escala media que logran márgenes superiores a la media nacional (empresas con ventajas competitivas o alto poder de fijación de precios), así como grandes conglomerados con márgenes estrechos pero alto volumen.
    3. **Para Especialistas de Supervisión Institucional:** Ofrece una herramienta de monitoreo oportuno para detectar empresas con márgenes brutos negativos persistentes (75 casos identificados en el dataset), lo que constituye una señal temprana de alerta en la estructura de costos directos.
    """)
    
    st.markdown(
        """
        <div class='data-footer'>
            Balance Metodológico y Operativo | Especialización en Analítica de Datos
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# 12. LIMITACIONES Y ADVERTENCIAS
# ==============================================================================
with tab_limitaciones:
    st.markdown("### Limitaciones de los Datos y Advertencias Regulatorias")
    
    st.markdown("""
    En concordancia con los principios éticos y metodológicos de la analítica de datos, se listan de forma abierta y transparente 
    las limitaciones identificadas en la fuente de información y su tratamiento técnico en esta solución:
    """)
    
    st.markdown("""
    1. **Presencia de Valores Nulos (Sin reporte):**
       - *Evidencia:* Se hallaron 269 registros con campo de Ingresos nulo (10,66% del dataset) y 678 con Costo de Ventas nulo (26,86%).
       - *Tratamiento:* Ningún valor nulo fue reemplazado silenciosamente por cero. En su lugar, el sistema asigna la etiqueta textual *"Sin reporte"*, 
         excluyendo el registro del cálculo de promedios para no alterar indebidamente las medias sectoriales.
         
    2. **Registros con Ingresos en Cero (No aplica / No comparable):**
       - *Evidencia:* 55 registros presentan un valor contable de cero en Ingresos de Actividades Ordinarias.
       - *Tratamiento:* Para el cálculo del Margen Bruto $(Ganancia / Ingresos)$, una división por cero generaría un error matemático o un valor indefinido. 
         Se estableció taxativamente que estos registros muestren *"No aplica / No comparable"*, evitando imputar 0% (lo cual sugeriría equivocadamente que la empresa vendió pero no obtuvo ganancia).
         
    3. **Multiplicidad de Fechas de Corte para un mismo NIT:**
       - *Evidencia:* Empresas de gran envergadura (como *Oleoducto Central S.A.*, *D1 S.A.S.*, *Colgener S.A.* e *Iinvermeyer S.A.S.*) registraron reportes tanto en fechas intermedias (marzo, abril, junio, octubre) como al cierre anual (diciembre 2025).
       - *Tratamiento:* Se diseñó e implementó la regla algorítmica de seleccionar el corte cronológicamente más reciente para cada NIT y Periodo. La interfaz informa permanentemente al usuario la cantidad de filas descartadas y permite alternar a la vista sin desduplicar si se requiere auditoría completa.
       
    4. **Cobertura Temporal Parcial:**
       - *Evidencia:* El dataset oficial concentra el 99,5% de sus registros en el año de corte 2025, integrando los campos NIIF comparativos *'Periodo Actual'* y *'Periodo Anterior'*.
       - *Tratamiento:* No se extrapolaron ni simularon series de tiempo ficticias. Los filtros exponen honestamente los periodos efectivamente disponibles en la fuente oficial.
    """)
    
    st.markdown(
        """
        <div class='warning-box'>
            <strong>DECLARACIÓN DE NO CALIFICACIÓN DE RIESGO:</strong><br>
            Este dashboard y los indicadores aquí expuestos son producto de un ejercicio académico para el Proyecto de Grado de la Especialización en Analítica de Datos. 
            Bajo ninguna circunstancia la información contenida en esta plataforma debe utilizarse como dictamen de insolvencia, acusación de fraude contable, 
            calificación de riesgo crediticio vinculante ni asesoría financiera profesional para la toma de decisiones contractuales.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class='data-footer'>
            Fuente: Superintendencia de Sociedades de Colombia | Transparencia Metodológica y Calidad del Dato
        </div>
        """,
        unsafe_allow_html=True
    )
