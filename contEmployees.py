# Archivo: contEmployees.py
import streamlit as st
from collections import defaultdict

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

def main():
    st.title("Calculador de Días por Empleado")
    st.write("Sube tus archivos de texto con el formato adecuado para calcular el total de días por empleado.")
    
    # Subir múltiples archivos
    uploaded_files = st.file_uploader("Sube tus archivos aquí", type=["txt"], accept_multiple_files=True)
    
    if uploaded_files:
        st.write("Archivos cargados correctamente. Procesando...")
        
        # Procesar archivos
        totals = process_files(uploaded_files)
        
        # Mostrar resultados en la interfaz
        st.write("### Resultados:")
        for name, days in totals.items():
            st.write(f"{name}: {days} días")
        
        # Generar archivo de salida
        result_text = "\n".join(f"{name}: {days} días" for name, days in totals.items())
        st.download_button(
            label="Descargar resultados",
            data=result_text,
            file_name="totales_empleados.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()