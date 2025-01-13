import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st
import time
import io

# Prefijo común para filtrar imágenes
COMMON_IMAGE_PREFIX = "https://static-resources-elementor.mirai.com/wp-content/uploads/sites/"

# Función para obtener las URLs de las imágenes de una página
def get_image_urls(page_url, image_prefix):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
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

# Función para encontrar todas las URLs en una página
def get_all_links(page_url, base_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
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

        urls_to_visit = set([base_url])
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

        st.info("Analizando el sitio web, esto puede tardar un momento...")
        progress_bar = st.progress(0)
        total_urls = len(urls_to_visit)

        time_placeholder = st.empty()
        status_placeholder = st.empty()

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            # Evitar demasiadas actualizaciones dinámicas
            if len(visited_urls) % 10 == 0:  # Actualizar cada 10 URLs
                status_placeholder.text(f"Procesando: {current_url}")
                elapsed_time = time.time() - start_time
                hours, rem = divmod(elapsed_time, 3600)
                minutes, seconds = divmod(rem, 60)
                time_placeholder.text(f"Tiempo transcurrido: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

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
            urls_to_visit.update(new_links - visited_urls)

            total_urls = len(visited_urls) + len(urls_to_visit)
            progress_bar.progress(min(len(visited_urls) / total_urls, 1.0))

            time.sleep(0.1)  # Pausa breve para liberar recursos

        progress_bar.progress(1.0)  # Asegurar que la barra llegue al 100%
        status_placeholder.text("Análisis completado.")
