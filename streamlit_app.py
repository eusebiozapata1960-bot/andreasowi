import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def crear_tabla_resumen(resumen_mensual):
    data = [resumen_mensual.columns.tolist()] + resumen_mensual.values.tolist()
    tabla = Table(data)
    # Aquí puedes agregar estilos a la tabla después, si quieres
    return tabla
    
# Configuración de la página
st.set_page_config(page_title="Asistente Financiero MERY", layout="wide")

st.title("📊 Asistente de Optimización Fiscal")
st.subheader("Solución inmediata para operaciones en Alemania")

# 1. Carga de archivos
uploaded_file = st.file_uploader("Sube el archivo de transacciones (CSV o Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Leer el archivo
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file,sheet_name=Nome)
    
    st.write("Datos cargados correctamente:")
    st.dataframe(df.head())
    df_consolidado = pd.concat(df.values(), ignore_index=True)
    st.write(df_consolidado.columns)
    df_consolidado['fecha'] = pd.to_datetime(df_consolidado['fecha'])
    df_consolidado['mes'] = df_consolidado['fecha'].dt.month_name()
    resumen_mensual = df_consolidado.groupby('mes')[['gastos', 'ingresos']].sum().reset_index()
    
    # 2. Botón de acción
if st.button("Analizar datos con IA"):
    with st.spinner('El agente está procesando la información...'):
        
        # Procesamos el resumen real
        resumen_mensual = df_consolidado.groupby('mes')[['gastos', 'ingresos']].sum().reset_index()
        
        # Mostramos los resultados reales en pantalla
        st.write("### Análisis de Ingresos y Gastos por Mes")
        st.dataframe(resumen_mensual)
        
        # Opcional: Si quieres un gráfico automático
        st.bar_chart(resumen_mensual.set_index('mes'))
        st.line_chart(resumen_mensual.set_index('mes'))
        import plotly.express as px
        fig_pastel = px.pie(resumen_mensual, values='gastos', names='mes', title='Distribución de Gastos por Mes')
        st.plotly_chart(fig_pastel)

        st.success(resultado)
        st.download_button("Descargar Reporte Final", data=resultado, file_name="reporte.txt")

else:
    st.info("Por favor, sube un archivo para comenzar.")
