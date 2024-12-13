# Archivo: app.py
import streamlit as st
import subprocess
import sys
from collections import defaultdict

# Verificar si matplotlib está instalado y, si no, instalarlo
try:
    import matplotlib.pyplot as plt
except ImportError:
    st.warning("Matplotlib no está instalado. Instalando ahora...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

def process_files(uploaded_files):
    """Procesar los archivos cargados y calcular los totales."""
    employee_totals = defaultdict(int)
    
    for uploaded_file in uploaded_files:
        lines = uploaded_file.getvalue().decode('utf-8').splitlines()
        for line in lines:
            # Buscar líneas con formato "Nombre empleado: X días"
            if ": " in line and "días" in line:
                name, days = line.split(":")
                days = int(days.strip().replace(" días", ""))
                employee_totals[name.strip()] += days
                
    return employee_totals

def plot_results(employee_totals):
    """Mostrar un gráfico de barras de los resultados."""
    # Ordenar los empleados por número de días (de mayor a menor)
    sorted_totals = sorted(employee_totals.items(), key=lambda x: x[1], reverse=True)
    names, days = zip(*sorted_totals)
    
    # Crear el gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(names, days, color='skyblue')
    ax.set_xlabel('Días')
    ax.set_title('Total de Días por Empleado')
    plt.gca().invert_yaxis()  # Invertir el eje Y para mostrar el empleado con más días arriba
    st.pyplot(fig)

def main():
    st.title("Calculador de Días por Empleado")

    # Instrucción para descargar y usar el archivo JavaScript
    st.markdown(
        """
        ### Primer Paso: Descargar y Ejecutar el Script
        Para comenzar, descarga el siguiente archivo JavaScript y ejecútalo en la consola de tu navegador para exportar los datos:
        - [Descargar Script JS](https://github.com/MarcosMirai/apps/blob/main/daysFactorial.js)

        **Instrucciones:**
        1. Abre la consola de tu navegador (F12 o clic derecho -> Inspeccionar -> Consola).
        2. Copia y pega el contenido del script descargado.
        3. Ejecútalo para obtener los datos necesarios.
        4. Guarda el resultado en un archivo `.txt` y súbelo aquí.
        """
    )

    # Subir múltiples archivos
    uploaded_files = st.file_uploader("Sube tus archivos aquí", type=["txt"], accept_multiple_files=True)

    if uploaded_files:
        st.write("Archivos cargados correctamente. Procesando...")
        
        # Procesar archivos
        totals = process_files(uploaded_files)
        
        # Ordenar los resultados de mayor a menor
        sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        
        # Mostrar resultados en la interfaz
        st.write("### Resultados:")
        for name, days in sorted_totals:
            st.write(f"{name}: {days} días")
        
        # Mostrar gráfico de barras
        plot_results(totals)
        
        # Generar archivo de salida
        result_text = "\n".join(f"{name}: {days} días" for name, days in sorted_totals)
        st.download_button(
            label="Descargar resultados",
            data=result_text,
            file_name="totales_empleados.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
