import requests
import json
import streamlit as st

def obtener_datos(url_base, endpoint, api_token):
    """
    Función para obtener datos de un endpoint específico en la API REST usando autenticación con un token de aplicación.
    """
    # Asegúrate de que la URL no tenga slash final
    url_base = url_base.rstrip("/")  # Elimina el slash al final si existe
    url = f"{url_base}/wp-json/wp/v2/{endpoint}"

    try:
        # Usar el token de aplicación para la autenticación
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza un error si el código de estado no es 200
        
        return response.json()

    except requests.exceptions.RequestException as e:
        # Mostrar el error completo para ayudar en la depuración
        st.error(f"Error al obtener datos del endpoint {endpoint}: {e}")
        st.write("Detalles de la respuesta:")
        st.write(response.text)  # Muestra el mensaje completo de error
        return None

# Título de la aplicación en Streamlit
st.title("Descargar datos de WordPress")

# Input para la URL base de la API de WordPress
url_base = st.text_input("Introduce la URL de tu sitio WordPress:", "")

# Input para el token de aplicación de WordPress (en lugar de usuario y contraseña)
api_token = st.text_input("Introduce tu token de aplicación de WordPress:", type="password")

# Si el usuario proporciona la URL y el token de la API
if url_base and api_token:
    # Obtener páginas
    st.subheader("Obteniendo páginas...")
    paginas = obtener_datos(url_base, "pages", api_token)
    if paginas:
        st.write(f"Se encontraron {len(paginas)} páginas.")
        # Guardar las páginas en un archivo JSON
        with open("paginas.json", "w", encoding="utf-8") as f:
            json.dump(paginas, f, ensure_ascii=False, indent=4)
        st.success("Datos guardados en paginas.json.")

    # Obtener plantillas (si están disponibles en tu instalación de Elementor)
    st.subheader("Obteniendo plantillas...")
    plantillas = obtener_datos(url_base, "templates", api_token)
    if plantillas:
        st.write(f"Se encontraron {len(plantillas)} plantillas.")
        # Guardar las plantillas en un archivo JSON
        with open("plantillas.json", "w", encoding="utf-8") as f:
            json.dump(plantillas, f, ensure_ascii=False, indent=4)
        st.success("Datos guardados en plantillas.json.")
else:
    st.warning("Por favor, ingresa una URL base válida y tu token de aplicación de WordPress.")
