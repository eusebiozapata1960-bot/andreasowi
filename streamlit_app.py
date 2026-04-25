import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero SWT 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Financiero y Operativo 2026")
st.markdown("Análisis detallado de costos, escenarios y proyecciones.")

# Función para cargar y limpiar datos
@st.cache_data
def load_data(file):
    try:
        # Leer todas las hojas
        xls = pd.ExcelFile(file)
        sheet_names = xls.sheet_names
        
        all_data = {}
        monthly_data = []
        hq_data = None

        for sheet in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            
            # Detectar hojas mensuales (Feb, Mar, etc.) o resumen
            if sheet in ['Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct', 'Nov', 'Dic', 
                         'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']:
                # Limpieza específica para hojas mensuales
                # Buscamos filas con ITEM, COP, USD
                # Normalmente están en la fila 4 o 5
                df_clean = df.copy()
                
                # Intentar identificar las columnas de valores
                # Asumimos estructura: [Descripcion, ValorCOP, ValorUSD, Notas]
                # Filtramos filas vacías
                df_clean = df_clean.dropna(how='all')
                
                # Buscar la fila de encabezados
                header_row = df_clean[df_clean[0].astype(str).str.contains('ITEM', na=False)].index
                if len(header_row) > 0:
                    df_clean.columns = df_clean.iloc[header_row[0]].tolist()
                    df_clean = df_clean.iloc[header_row[0]+1:]
                
                # Renombrar columnas si es necesario para estandarizar
                cols = df_clean.columns.tolist()
                if len(cols) >= 3:
                    df_clean.columns = ['Item', 'COP', 'USD'] + [f'Nota_{i}' for i in range(3, len(cols))]
                    df_clean['Mes'] = sheet
                    monthly_data.append(df_clean)

            # Hoja principal de escenarios
            if 'Escenarios' in sheet or 'HQ' in sheet:
                hq_data = df.copy()

            all_data[sheet] = df

        df_monthly_combined = pd.concat(monthly_data, ignore_index=True) if monthly_data else pd.DataFrame()

        # Limpieza de tipos de datos para montos
        for col in ['COP', 'USD']:
            if col in df_monthly_combined.columns:
                # Eliminar símbolos de moneda y comas, convertir a numérico
                df_monthly_combined[col] = df_monthly_combined[col].astype(str).str.replace('$', '', regex=False)\
                    .str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df_monthly_combined[col] = pd.to_numeric(df_monthly_combined[col], errors='coerce')

        return all_data, df_monthly_combined, hq_data

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None, None, None

# Sidebar para carga de archivo
with st.sidebar:
    st.header("📂 Cargar Datos")
    uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        st.success("Archivo cargado correctamente")
        all_data, df_monthly, df_hq = load_data(uploaded_file)
    else:
        st.info("Esperando archivo...")
        all_data, df_monthly, df_hq = None, None, None

# Lógica principal si hay datos
if all_data is not None and df_monthly is not None:
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Resumen General", "💰 Costos Mensuales", "🌍 Escenarios HQ", "📋 Explorador de Datos"])

    with tab1:
        st.subheader("Resumen de Costos Operativos")
        
        # KPIs principales
        total_cop = df_monthly['COP'].sum()
        total_usd = df_monthly['USD'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Costo Proyectado (COP)", f"${total_cop:,.0f}")
        with col2:
            st.metric("Total Costo Proyectado (USD)", f"${total_usd:,.0f}")
        with col3:
            st.metric("Hojas Analizadas", len(all_data))

        st.divider()

        # Gráfico de Torta: Distribución de Costos por Mes
        st.markdown("### 🥧 Distribución de Costos por Mes")
        monthly_totals = df_monthly.groupby('Mes')[['COP', 'USD']].sum().reset_index()
        
        # Ordenar meses cronológicamente (aproximado)
        month_order = ['Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct', 'Nov', 'Dic']
        monthly_totals['Mes_Orden'] = monthly_totals['Mes'].apply(lambda x: month_order.index(x) if x in month_order else 99)
        monthly_totals = monthly_totals.sort_values('Mes_Orden')

        fig_pie = px.pie(monthly_totals, values='COP', names='Mes', 
                         title='Proporción de Gastos por Mes',
                         hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("Análisis Mensual de Costos")
        
        # Gráfico de Barras
        st.markdown("### 📊 Comparativa Mensual")
        fig_bar = px.bar(monthly_totals, x='Mes', y=['COP', 'USD'], 
                         title='Evolución de Costos Mensuales',
                         labels={'value': 'Monto', 'variable': 'Moneda'},
                         barmode='group',
                         color_discrete_map={'COP': '#FF6B6B', 'USD': '#4ECDC4'})
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gráfico de Líneas
        st.markdown("### 📈 Tendencia Acumulada")
        df_line = monthly_totals.copy()
        df_line['COP_Acum'] = df_line['COP'].cumsum()
        df_line['USD_Acum'] = df_line['USD'].cumsum()
        
        fig_line = px.line(df_line, x='Mes', y=['COP_Acum', 'USD_Acum'], 
                           title='Gasto Acumulado en el Año',
                           labels={'value': 'Total Acumulado', 'variable': 'Moneda'},
                           markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        # Tabla de desglose por categoría (Top items)
        st.markdown("### 🔍 Desglose por Categoría (Top 10 en COP)")
        # Agrupar items a lo largo de todos los meses para ver qué gasta más
        top_items = df_monthly.groupby('Item')['COP'].sum().sort_values(ascending=False).head(10).reset_index()
        st.dataframe(top_items, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Escenarios Devolución HQ")
        st.info("Esta sección muestra la estructura de la hoja de escenarios. Debido a la complejidad del formato, se presenta la vista limpia.")
        
        if df_hq is not None:
            # Mostrar la tabla cruda pero limpia de filas vacías
            st.write("**Vista preliminar de datos financieros HQ:**")
            
            # Eliminamos filas completamente vacías
            df_hq_clean = df_hq.dropna(how='all').dropna(axis=1, how='all')
            
            # Intentar mostrar solo las primeras 20 filas para no saturar si es muy grande
            st.dataframe(df_hq_clean.head(20), use_container_width=True)
            
            # Opción de búsqueda
            st.markdown("### 🔍 Buscador en Escenarios")
            search_term = st.text_input("Buscar texto en la hoja de escenarios (ej. 'P&L', 'Giro', 'Impuesto'):")
            if search_term:
                # Buscar en todo el dataframe
                mask = df_hq_clean.apply(lambda col: col.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                results = df_hq_clean[mask]
                st.dataframe(results, use_container_width=True)
        else:
            st.warning("No se detectó una hoja de Escenarios válida.")

    with tab4:
        st.subheader("Explorador de Datos Completo")
        sheet_name = st.selectbox("Selecciona una hoja para ver:", list(all_data.keys()))
        
        if sheet_name:
            df_selected = all_data[sheet_name].dropna(how='all').dropna(axis=1, how='all')
            st.dataframe(df_selected, use_container_width=True)
            
            st.markdown("### 📥 Descargar hoja como CSV")
            csv = df_selected.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Descargar {sheet_name}.csv",
                data=csv,
                file_name=f'{sheet_name}.csv',
                mime='text/csv',
            )

else:
    st.warning("⚠️ Por favor, carga el archivo Excel en el menú lateral para visualizar el análisis.")
