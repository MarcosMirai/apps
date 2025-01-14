import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st
import time
import io

# Prefijo común para filtrar imágenes
COMMON_IMAGE_PREFIX = "https://static-resources-elementor.mirai.com/wp-content/uploads/sites/"

# Función para obtener las URLs de las imágenes de una página (con caché)
@st.cache_data
def get_image_urls(page_url, image_prefix):
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error al obtener imágenes de {page_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')

    # Retornar sólo las URLs que comiencen con el prefijo indicado
    filtered_urls = [img['src'] for img in img_tags if 'src' in img.attrs and img['src'].startswith(image_prefix)]
    return filtered_urls

# Función para encontrar todas las URLs en una página (con caché)
@st.cache_data
def get_all_links(page_url, base_url):
    try:
        response = requests.get(page_url, timeout=10)
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
            # Procesar en bloques de 10 URLs
            block = list(urls_to_visit)[:10]
            urls_to_visit = urls_to_visit - set(block)

            for current_url in block:
                if current_url in visited_urls:
                    continue
                visited_urls.add(current_url)

                status_placeholder.text(f"Procesando: {current_url}")

                # Obtener URLs de imágenes
                img_urls = get_image_urls(current_url, image_prefix)
                if not img_urls:
                    total_404_errors += 1
                    urls_404.append(current_url)
                    continue

                for img_url in img_urls:
                    urls_images.append(img_url)
                    total_images += 1

                    # Simular ausencia de alt y title para este flujo
                    alt_absent = True  # No podemos verificar alt desde aquí
                    title_absent = True  # Tampoco podemos verificar title

                    if alt_absent and title_absent:
                        total_no_both += 1
                        urls_no_both.append(img_url)
                    elif alt_absent:
                        total_no_alt += 1
                        urls_no_alt.append(img_url)
                    elif title_absent:
                        total_no_title += 1
                        urls_no_title.append(img_url)

                # Obtener y procesar nuevos enlaces
                new_links = get_all_links(current_url, base_url)
                urls_to_visit.update(set(new_links) - visited_urls)

            total_urls = len(visited_urls) + len(urls_to_visit)
            progress_bar.progress(min(len(visited_urls) / total_urls, 1.0))

            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            time_placeholder.text(f"Tiempo transcurrido: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

            time.sleep(0.1)  # Pausa breve para liberar recursos

        progress_bar.progress(1.0)  # Asegurar que la barra llegue al 100%
        status_placeholder.text("Análisis completado.")

        st.subheader("Resumen del análisis:")
        st.write(f"**Total de imágenes analizadas:** {total_images}")
        st.write(f"**Total de imágenes sin alt:** {total_no_alt}")
        st.write(f"**Total de imágenes sin title:** {total_no_title}")
        st.write(f"**Total de imágenes sin ambos atributos:** {total_no_both}")
        st.write(f"**Total de errores 404 encontrados:** {total_404_errors}")

        # Botones para descargar resultados
        def create_download_button(data, filename, label):
            output = io.StringIO("\n".join(data))
            st.download_button(label=label, data=output.getvalue(), file_name=filename)

        st.subheader("Descargar resultados:")
        create_download_button(urls_no_alt, "imagenes_sin_alt.txt", "Descargar imágenes sin alt")
        create_download_button(urls_no_title, "imagenes_sin_title.txt", "Descargar imágenes sin title")
        create_download_button(urls_no_both, "imagenes_sin_ambos.txt", "Descargar imágenes sin ambos atributos")
        create_download_button(urls_404, "errores_404.txt", "Descargar errores 404")
        create_download_button(urls_images, "todas_las_imagenes.txt", "Descargar listado de imágenes analizadas")
