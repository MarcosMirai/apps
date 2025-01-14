import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st
import time
import io

# Configuración de límites
BLOCK_SIZE = 500  # Tamaño del bloque de URLs a procesar
MAX_DEPTH = 2     # Límite de profundidad
REQUEST_TIMEOUT = 10  # Tiempo límite para solicitudes HTTP (en segundos)

# Prefijo común para filtrar imágenes
COMMON_IMAGE_PREFIX = "https://static-resources-elementor.mirai.com/wp-content/uploads/sites/"

# Función para obtener las URLs de las imágenes de una página (con caché)
@st.cache_data
def get_image_urls(page_url, image_prefix):
    try:
        response = requests.get(page_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error al obtener imágenes de {page_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')

    # Filtrar imágenes que comiencen con el prefijo indicado
    filtered_images = [img for img in img_tags if 'src' in img.attrs and img['src'].startswith(image_prefix)]
    return filtered_images

# Función para verificar alt y title de una imagen
def check_alt_title(img_tag):
    alt_absent = 'alt' not in img_tag.attrs or img_tag['alt'].strip() == ""
    title_absent = 'title' not in img_tag.attrs or img_tag['title'].strip() == ""
    return alt_absent, title_absent

# Función para encontrar todas las URLs en una página (con caché)
@st.cache_data
def get_all_links(page_url, base_url):
    try:
        response = requests.get(page_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error al obtener enlaces de {page_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/'):
            href = urljoin(base_url, href)
        elif not bool(urlparse(href).netloc):
            href = urljoin(base_url, href)
        if href.startswith(base_url):
            links.add(href)
    return links

# Función principal
def run():
    st.title("Comprobador de atributos alt y title en imágenes")
    base_url = st.text_input("Introduce la URL del sitio web:")
    site_number = st.text_input("Introduce el número del site (directorio):", "1303")
    
    if st.button("Iniciar análisis"):
        if not base_url or not site_number:
            st.error("Por favor, introduce una URL válida y el número del site.")
            return

        # Construir el prefijo del directorio específico
        image_prefix = f"{COMMON_IMAGE_PREFIX}{site_number}/"

        urls_to_visit = [(base_url, 0)]  # Cada URL tendrá un nivel de profundidad asociado
        visited_urls = set()

        total_no_alt = 0
        total_no_title = 0
        total_no_both = 0
        total_404_errors = 0
        total_images = 0

        urls_no_alt = []
        urls_no_title = []
        urls_no_both = []
        urls_404 = []
        urls_images = []

        start_time = time.time()

        st.info("Analizando el sitio web en bloques...")
        progress_bar = st.progress(0)
        block_counter = 0  # Contador de bloques procesados

        while urls_to_visit:
            block_counter += 1
            current_block = urls_to_visit[:BLOCK_SIZE]
            urls_to_visit = urls_to_visit[BLOCK_SIZE:]

            for current_url, depth in current_block:
                if current_url in visited_urls or depth > MAX_DEPTH:
                    continue
                visited_urls.add(current_url)

                st.write(f"Procesando: {current_url} (Profundidad: {depth})")

                img_tags = get_image_urls(current_url, image_prefix)
                if not img_tags:
                    total_404_errors += 1
                    urls_404.append(current_url)
                    continue

                for img_tag in img_tags:
                    img_url = img_tag.get('src', 'URL no disponible')
                    urls_images.append(img_url)
                    total_images += 1
                    alt_absent, title_absent = check_alt_title(img_tag)
                    if alt_absent and title_absent:
                        total_no_both += 1
                        urls_no_both.append(img_url)
                    elif alt_absent:
                        total_no_alt += 1
                        urls_no_alt.append(img_url)
                    elif title_absent:
                        total_no_title += 1
                        urls_no_title.append(img_url)

                new_links = get_all_links(current_url, base_url)
                urls_to_visit.extend([(link, depth + 1) for link in new_links if link not in visited_urls])

            # Actualizar barra de progreso y mostrar resumen parcial
            progress_bar.progress(min(block_counter * BLOCK_SIZE / (block_counter * BLOCK_SIZE + len(urls_to_visit)), 1.0))

            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            st.write(f"Tiempo transcurrido: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

            # Resumen parcial
            st.subheader(f"Resumen parcial (Bloque {block_counter}):")
            st.write(f"**Total de imágenes analizadas:** {total_images}")
            st.write(f"**Total de imágenes sin alt:** {total_no_alt}")
            st.write(f"**Total de imágenes sin title:** {total_no_title}")
            st.write(f"**Total de imágenes sin ambos atributos:** {total_no_both}")
            st.write(f"**Total de errores 404 encontrados:** {total_404_errors}")

            # Pausar para confirmar antes de continuar
            if urls_to_visit:
                if not st.button(f"Continuar con el siguiente bloque ({len(urls_to_visit)} URLs restantes)"):
                    st.warning("Análisis pausado. Haz clic en el botón para continuar.")
                    return

        # Finalizar análisis
        progress_bar.progress(1.0)
        st.success("Análisis completado.")
