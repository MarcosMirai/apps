import requests
import json
import streamlit as st

def obtener_datos(url_base, endpoint):
    """
    Función para obtener datos de un endpoint específico en la API REST.
    """
    url = f"{url_base}/wp-json/wp/v2/{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si el código de estado no es 200
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener datos del endpoint {endpoint}: {e}")
        return None

# Título de la aplicación en Streamlit
st.title("Descargar datos de WordPress")

# Input para la URL base de la API de WordPress
url_base = st.text_input("Introduce la URL de tu sitio WordPress:", "")

# Si el usuario proporciona una URL
if url_base:
    # Obtener páginas
    st.subheader("Obteniendo páginas...")
    paginas = obtener_datos(url_base, "pages")
    if paginas:
        st.write(f"Se encontraron {len(paginas)} páginas.")
        # Guardar las páginas en un archivo JSON
        with open("paginas.json", "w", encoding="utf-8") as f:
            json.dump(paginas, f, ensure_ascii=False, indent=4)
        st.success("Datos guardados en paginas.json.")

    # Obtener plantillas (si están disponibles en tu instalación de Elementor)
    st.subheader("Obteniendo plantillas...")
    plantillas = obtener_datos(url_base, "templates")  # Cambia "templates" si usas un endpoint diferente
    if plantillas:
        st.write(f"Se encontraron {len(plantillas)} plantillas.")
        # Guardar las plantillas en un archivo JSON
        with open("plantillas.json", "w", encoding="utf-8") as f:
            json.dump(plantillas, f, ensure_ascii=False, indent=4)
        st.success("Datos guardados en plantillas.json.")
else:
    st.warning("Por favor, ingresa una URL base válida.")
