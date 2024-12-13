# Archivo: app.py
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

    # Botón para reiniciar el estado
    if st.button("Reiniciar"):
        st.session_state.uploaded_files = None

    # Subir múltiples archivos
    uploaded_files = st.file_uploader("Sube tus archivos aquí", type=["txt"], accept_multiple_files=True)

    # Manejo de estado para reiniciar
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    # Procesar los archivos si ya están cargados
    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        st.write("Archivos cargados correctamente. Procesando...")
        
        # Procesar archivos
        totals = process_files(st.session_state.uploaded_files)
        
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
