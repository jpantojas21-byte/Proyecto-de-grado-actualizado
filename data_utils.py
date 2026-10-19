"""
Módulo de Utilidades de Datos Financieros (data_utils.py)
Proyecto de Grado — Especialización en Analítica de Datos
Fuente de datos: Superintendencia de Sociedades de Colombia
Formulario 310030: Estado de resultado integral, resultado del periodo, por función de gasto

Este módulo implementa las funciones de carga, normalización, control de calidad,
desduplicación y cálculo de indicadores financieros NIIF bajo reglas rigurosas y transparentes.
"""

from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

# Diccionario oficial de macrosectores según la letra de clasificación CIIU Rev. 4 A.C. (DANE / Supersociedades)
# NOTA SOBRE SECTOR/INDUSTRIA: El dataset oficial de la Superintendencia de Sociedades
# no contiene una columna denominada explícitamente "Sector" o "Industria". En su lugar,
# contiene la columna oficial "Clasificación Industrial Internacional Uniforme Versión 4 A.C (CIIU)".
# Para brindar una agrupación analítica de alto nivel sin alterar la veracidad de los datos,
# se extrae la letra inicial del código CIIU y se mapea con la nomenclatura estandarizada nacional.
# Si en el futuro se incorpora un clasificador sectorial alternativo (ej. sectores bursátiles o GICS),
# este puede añadirse en esta sección sin romper la estructura analítica del dashboard.
DICCIONARIO_MACROSECTORES = {
    'A': 'A — Agricultura, ganadería, caza, silvicultura y pesca',
    'B': 'B — Explotación de minas y canteras',
    'C': 'C — Industrias manufactureras',
    'D': 'D — Suministro de electricidad, gas, vapor y aire acondicionado',
    'E': 'E — Distribución de agua, saneamiento y gestión de desechos',
    'F': 'F — Construcción',
    'G': 'G — Comercio al por mayor y al por menor; reparación de vehículos',
    'H': 'H — Transporte y almacenamiento',
    'I': 'I — Alojamiento y servicios de comida',
    'J': 'J — Información y comunicaciones',
    'K': 'K — Actividades financieras y de seguros',
    'L': 'L — Actividades inmobiliarias',
    'M': 'M — Actividades profesionales, científicas y técnicas',
    'N': 'N — Actividades de servicios administrativos y de apoyo',
    'O': 'O — Administración pública y defensa',
    'P': 'P — Educación',
    'Q': 'Q — Actividades de atención de la salud humana y de asistencia social',
    'R': 'R — Actividades artísticas, de entretenimiento y recreación',
    'S': 'S — Otras actividades de servicios'
}


def get_data_filepath() -> Path:
    """
    Retorna la ruta al archivo oficial de datos de forma robusta y portable.
    Busca tanto en /data como en la raíz del proyecto, manejando diferencias
    de mayúsculas/minúsculas o nombres de archivo en Linux (Streamlit Cloud).
    """
    base_dir = Path(__file__).resolve().parent
    nombre_oficial = "310030_Estado de resultado integral, resultado del periodo, por funcion de gasto.xlsx"
    
    # 1. Candidatos directos más comunes
    candidatos = [
        base_dir / "data" / nombre_oficial,
        base_dir / nombre_oficial,
        base_dir / "data" / "datos.xlsx",
        base_dir / "datos.xlsx"
    ]
    for c in candidatos:
        if c.exists():
            return c
            
    # 2. Búsqueda insensible a mayúsculas/minúsculas y por coincidencia de patrón
    directorios_busqueda = [base_dir / "data", base_dir]
    for d in directorios_busqueda:
        if d.exists() and d.is_dir():
            for archivo in d.iterdir():
                if archivo.is_file() and archivo.suffix.lower() in ['.xlsx', '.xls', '.csv']:
                    nombre_lower = archivo.name.lower()
                    if '310030' in nombre_lower or 'resultado' in nombre_lower or 'estado' in nombre_lower:
                        return archivo

    # 3. Si no se encontró por patrón, buscar el primer archivo Excel disponible en data o raíz
    for d in directorios_busqueda:
        if d.exists() and d.is_dir():
            for archivo in d.iterdir():
                if archivo.is_file() and archivo.suffix.lower() in ['.xlsx', '.xls']:
                    return archivo

    # Si definitivamente no existe, retornar la ruta por defecto para el mensaje de error
    return base_dir / "data" / nombre_oficial


def load_raw_dataset(filepath: Optional[Path] = None) -> pd.DataFrame:
    """
    Carga el dataset oficial del archivo Excel de la Superintendencia de Sociedades.
    Normaliza los nombres de columnas para subsanar inconsistencias de codificación (caracteres de reemplazo)
    sin modificar el significado original de ningún campo contable reportado.
    """
    if filepath is None:
        filepath = get_data_filepath()
    
    if not filepath.exists():
        base_dir = Path(__file__).resolve().parent
        archivos_raiz = [f.name for f in base_dir.iterdir() if f.is_file()] if base_dir.exists() else []
        dir_data = base_dir / "data"
        archivos_data = [f.name for f in dir_data.iterdir() if f.is_file()] if dir_data.exists() else ["(la carpeta data/ no existe)"]
        raise FileNotFoundError(
            f"No se encontró el archivo de datos en la ruta esperada: {filepath}. "
            f"Archivos en raíz: {archivos_raiz}. "
            f"Archivos en data/: {archivos_data}. "
            "Asegúrate de haber subido la carpeta data/ con el archivo .xlsx a tu repositorio en GitHub."
        )
    
    # Carga desde Excel con tipos de datos adecuados
    df = pd.read_excel(filepath)
    
    # Normalización de nombres de columnas
    # En el archivo original, algunas tildes aparecen con caracter de reemplazo por temas de encoding de la fuente.
    # Mapeamos rigurosamente cada una de las 35 columnas a un nombre canónico en español limpio.
    col_mapping = {}
    for col in df.columns:
        col_str = str(col).strip()
        if 'Punto de Entrada' in col_str:
            col_mapping[col] = 'punto_entrada'
        elif 'Nombre Formulario' in col_str:
            col_mapping[col] = 'nombre_formulario'
        elif col_str == 'NIT':
            col_mapping[col] = 'nit'
        elif 'Fecha de Corte' in col_str:
            col_mapping[col] = 'fecha_corte'
        elif 'social' in col_str.lower():
            col_mapping[col] = 'razon_social'
        elif 'CIIU' in col_str:
            col_mapping[col] = 'ciiu'
        elif 'Tipo societario' in col_str:
            col_mapping[col] = 'tipo_societario'
        elif 'notificaci' in col_str.lower():
            col_mapping[col] = 'direccion'
        elif 'Departamento' in col_str:
            col_mapping[col] = 'departamento'
        elif 'Ciudad' in col_str:
            col_mapping[col] = 'ciudad'
        elif col_str == 'Periodo':
            col_mapping[col] = 'periodo'
        elif 'Revenue' in col_str:
            col_mapping[col] = 'ingresos'
        elif 'CostOfSales' in col_str:
            col_mapping[col] = 'costo_ventas'
        elif 'GrossProfit' in col_str:
            col_mapping[col] = 'ganancia_bruta'
        elif 'OtherIncome' in col_str and 'Subsidiaries' not in col_str:
            col_mapping[col] = 'otros_ingresos'
        elif 'DistributionCosts' in col_str:
            col_mapping[col] = 'costos_distribucion'
        elif 'AdministrativeExpense' in col_str:
            col_mapping[col] = 'gastos_administracion'
        elif 'OtherExpenseByFunction' in col_str:
            col_mapping[col] = 'otros_gastos'
        elif 'ProfitLossFromOperatingActivities' in col_str:
            col_mapping[col] = 'ganancia_operacional'
        elif 'FinanceIncome' in col_str:
            col_mapping[col] = 'ingresos_financieros'
        elif 'FinanceCosts' in col_str:
            col_mapping[col] = 'costos_financieros'
        elif 'ProfitLossBeforeTax' in col_str:
            col_mapping[col] = 'ganancia_antes_impuestos'
        elif 'IncomeTaxExpenseContinuingOperations' in col_str:
            col_mapping[col] = 'gasto_impuestos'
        elif 'ProfitLossFromContinuingOperations' in col_str:
            col_mapping[col] = 'ganancia_operaciones_continuadas'
        elif 'ProfitLossFromDiscontinuedOperations' in col_str:
            col_mapping[col] = 'ganancia_operaciones_discontinuadas'
        elif col_str.endswith('(ProfitLoss)'):
            col_mapping[col] = 'ganancia_neta'
    
    df = df.rename(columns=col_mapping)
    
    # Asegurar formato de fechas y textos
    df['fecha_corte'] = pd.to_datetime(df['fecha_corte']).dt.strftime('%Y-%m-%d')
    df['nit'] = df['nit'].astype(str).str.strip()
    df['razon_social'] = df['razon_social'].astype(str).str.strip()
    
    # Extraer código y macrosector a partir de la columna CIIU
    if 'ciiu' in df.columns:
        df['ciiu'] = df['ciiu'].astype(str).str.strip()
        df['ciiu_letra'] = df['ciiu'].str.extract(r'^([A-Z])')[0].fillna('Otros')
        df['macrosector'] = df['ciiu_letra'].map(DICCIONARIO_MACROSECTORES).fillna('Otras actividades económicas')
    else:
        df['ciiu'] = 'No especificado'
        df['ciiu_letra'] = 'N/A'
        df['macrosector'] = 'Sector no disponible en dataset'
    
    return df


def audit_and_calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica las reglas rigurosas de calidad de datos exigidas por el proyecto:
    
    1. VALORES NULOS EN INGRESOS Y COSTOS:
       Se auditan explícitamente y se clasifican como 'Sin reporte'.
       Bajo ninguna circunstancia se reemplazan con cero silenciosamente.
       
    2. INGRESOS EN CERO Y CÁLCULO DE MARGEN BRUTO:
       Margen Bruto = (Ganancia Bruta / Ingresos) * 100
       Si Ingresos == 0, la división no es matemáticamente válida ni financieramente representativa.
       El indicador se clasifica taxativamente como 'No aplica / No comparable',
       evitando asignar 0% o arrojar un error de ejecución.
       
    3. MARGEN BRUTO COMPARABLE:
       Únicamente se calcula el porcentaje de margen si los Ingresos son mayores que cero
       y la Ganancia Bruta tiene un valor numérico reportado.
    """
    df = df.copy()
    
    # 1. Auditoría de Ingresos
    def clasificar_ingresos(val):
        if pd.isna(val):
            return "Sin reporte"
        elif val == 0:
            return "Ingresos en cero"
        else:
            return "Reportado"
            
    df['calidad_ingresos'] = df['ingresos'].apply(clasificar_ingresos)
    
    # 2. Auditoría de Costo de Ventas
    def clasificar_costo(val):
        if pd.isna(val):
            return "Sin reporte"
        elif val == 0:
            return "Costo en cero"
        else:
            return "Reportado"
            
    df['calidad_costo'] = df['costo_ventas'].apply(clasificar_costo)
    
    # 3. Auditoría de Ganancia Bruta
    def clasificar_ganancia(val):
        if pd.isna(val):
            return "Sin reporte"
        else:
            return "Reportado"
            
    df['calidad_ganancia_bruta'] = df['ganancia_bruta'].apply(clasificar_ganancia)
    
    # 4. Cálculo y Auditoría del Margen Bruto
    # Regla: Si ingresos es nulo o ganancia es nula -> 'Sin reporte'
    # Regla: Si ingresos == 0 -> 'No aplica / No comparable'
    # Regla: Si ingresos > 0 y ganancia válida -> Margen % numérico y 'Comparable'
    def clasificar_margen(row):
        ing = row['ingresos']
        gb = row['ganancia_bruta']
        if pd.isna(ing) or pd.isna(gb):
            return "Sin reporte"
        if ing == 0:
            return "No aplica / No comparable"
        return "Comparable"
        
    df['calidad_margen'] = df.apply(clasificar_margen, axis=1)
    
    # Cálculo del margen bruto porcentual (solo para comparables)
    mask_comparable = df['calidad_margen'] == 'Comparable'
    df['margen_bruto_pct'] = np.nan
    df.loc[mask_comparable, 'margen_bruto_pct'] = (
        df.loc[mask_comparable, 'ganancia_bruta'] / df.loc[mask_comparable, 'ingresos']
    ) * 100
    
    # Texto representativo para la interfaz de usuario
    def texto_margen(row):
        estado = row['calidad_margen']
        if estado == 'Comparable':
            return f"{row['margen_bruto_pct']:.2f}%"
        return estado
        
    df['margen_bruto_texto'] = df.apply(texto_margen, axis=1)
    
    return df


def apply_cut_rule(df: pd.DataFrame, rule_mode: str = "most_recent") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    REGLA DE TRATAMIENTO PARA NITS CON MÁS DE UNA FECHA DE CORTE:
    
    Problema detectado en los datos reales:
    Existen 8 empresas (NITs) que reportan en más de una fecha de corte dentro del dataset
    para el mismo periodo contable (por ejemplo, reportes intermedios trimestrales o semestrales
    a 2025-03-31, 2025-04-30, 2025-06-30 junto al reporte de cierre a 2025-12-31).
    
    Regla aplicada:
    - 'most_recent' (Por defecto / Recomendado):
      Para cada empresa (NIT) y para cada Periodo contable ('Periodo Actual' y 'Periodo Anterior'),
      se selecciona de manera unívoca el registro correspondiente a la Fecha de Corte cronológicamente
      más reciente disponible. Esto garantiza que se analice el cierre anual definitivo o el corte
      más actualizado, previniendo el doble conteo de magnitudes financieras en agregados y rankings.
      
    - 'all_records':
      Conserva todos los registros brutos sin desduplicar, permitiendo auditar la totalidad de
      reportes radicados ante la Superintendencia con su respectiva advertencia de multiplicidad.
    """
    total_antes = len(df)
    nits_con_multiples_cortes = (
        df.groupby(['nit', 'periodo'])['fecha_corte'].nunique()
    )
    nits_afectados = nits_con_multiples_cortes[nits_con_multiples_cortes > 1].index.get_level_values('nit').unique().tolist()
    
    if rule_mode == "most_recent":
        # Ordenamos por fecha de corte de forma ascendente y nos quedamos con el último (más reciente)
        df_sorted = df.sort_values(by=['nit', 'periodo', 'fecha_corte'], ascending=True)
        df_result = df_sorted.groupby(['nit', 'periodo'], as_index=False).last()
    else:
        df_result = df.copy()
        
    total_despues = len(df_result)
    registros_descartados = total_antes - total_despues
    
    metadata_regla = {
        'regla_aplicada': rule_mode,
        'descripcion_corta': 'Corte más reciente por NIT y Periodo' if rule_mode == 'most_recent' else 'Todos los cortes disponibles (sin filtro de corte)',
        'total_original': total_antes,
        'total_filtrado': total_despues,
        'registros_descartados': registros_descartados,
        'nits_con_multiples_cortes_conteo': len(nits_afectados),
        'nits_afectados': nits_afectados
    }
    
    return df_result, metadata_regla


def calculate_global_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula los indicadores clave de desempeño (KPIs) sobre el conjunto de datos filtrado:
    - Ingresos totales (sumando únicamente registros reportados)
    - Costo de ventas total (sumando únicamente registros reportados)
    - Ganancia bruta total (sumando únicamente registros reportados)
    - Margen bruto promedio simple (sobre registros con margen comparable)
    - Margen bruto ponderado del agregado (Ganancia Bruta Total / Ingresos Totales * 100)
    - Conteo de empresas únicas
    - Total de registros
    - Conteo de registros con 'Sin reporte' y 'No aplica / No comparable'
    """
    total_registros = len(df)
    empresas_unicas = df['nit'].nunique() if 'nit' in df.columns else 0
    
    ingresos_validos = df['ingresos'].dropna()
    costos_validos = df['costo_ventas'].dropna()
    ganancias_validas = df['ganancia_bruta'].dropna()
    
    total_ingresos = float(ingresos_validos.sum()) if len(ingresos_validos) > 0 else 0.0
    total_costos = float(costos_validos.sum()) if len(costos_validos) > 0 else 0.0
    total_ganancia_bruta = float(ganancias_validas.sum()) if len(ganancias_validas) > 0 else 0.0
    
    # Margen promedio simple sobre comparables
    margenes_comparables = df.loc[df['calidad_margen'] == 'Comparable', 'margen_bruto_pct']
    if len(margenes_comparables) > 0:
        margen_promedio_simple = float(margenes_comparables.mean())
        margen_mediana = float(margenes_comparables.median())
    else:
        margen_promedio_simple = None
        margen_mediana = None
        
    # Margen ponderado agregado
    if total_ingresos > 0:
        margen_ponderado = (total_ganancia_bruta / total_ingresos) * 100
    else:
        margen_ponderado = None
        
    sin_reporte_ingresos = int((df['calidad_ingresos'] == 'Sin reporte').sum())
    sin_reporte_costos = int((df['calidad_costo'] == 'Sin reporte').sum())
    no_comparables_margen = int((df['calidad_margen'] == 'No aplica / No comparable').sum())
    sin_reporte_margen = int((df['calidad_margen'] == 'Sin reporte').sum())
    comparables_margen = int((df['calidad_margen'] == 'Comparable').sum())
    
    return {
        'total_registros': total_registros,
        'empresas_unicas': empresas_unicas,
        'total_ingresos': total_ingresos,
        'total_costos': total_costos,
        'total_ganancia_bruta': total_ganancia_bruta,
        'margen_promedio_simple': margen_promedio_simple,
        'margen_mediana': margen_mediana,
        'margen_ponderado': margen_ponderado,
        'sin_reporte_ingresos': sin_reporte_ingresos,
        'sin_reporte_costos': sin_reporte_costos,
        'no_comparables_margen': no_comparables_margen,
        'sin_reporte_margen': sin_reporte_margen,
        'comparables_margen': comparables_margen
    }


def format_currency_cop(val: Optional[float]) -> str:
    """
    Formatea cifras monetarias en Pesos Colombianos (COP) usando sufijos legibles
    (Billones, Millones, Mil) para facilitar la lectura ejecutiva sin perder precisión.
    """
    if val is None or pd.isna(val):
        return "Sin reporte"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    
    if abs_val >= 1e12:
        return f"{sign}${abs_val / 1e12:,.2f} B (COP)"
    elif abs_val >= 1e9:
        return f"{sign}${abs_val / 1e9:,.2f} M (COP)"
    elif abs_val >= 1e6:
        return f"{sign}${abs_val / 1e6:,.2f} M (COP)"
    else:
        return f"{sign}${abs_val:,.0f} COP"


def format_percentage(val: Optional[float]) -> str:
    """Formatea porcentajes financieros de manera estandarizada."""
    if val is None or pd.isna(val):
        return "No aplica / No comparable"
    return f"{val:,.2f}%"
