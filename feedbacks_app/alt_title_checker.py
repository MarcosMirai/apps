import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st
import time  # Para medir el tiempo de ejecución
import io    # Para generar archivos descargables

# Función para obtener las URLs de las imágenes de una página
def get_image_urls(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all('img')

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
    
    if st.button("Iniciar análisis"):
        if not base_url:
            st.error("Por favor, introduce una URL válida.")
            return
        
        urls_to_visit = set([base_url])
        visited_urls = set()

        total_no_alt = 0
        total_no_title = 0
        total_no_both = 0
        total_404_errors = 0
        total_images = 0

        # Listados de URLs
        urls_no_alt = []
        urls_no_title = []
        urls_no_both = []
        urls_404 = []
        urls_images = []

        # Tiempo de inicio
        start_time = time.time()

        st.info("Analizando el sitio web, esto puede tardar un momento...")
        progress_bar = st.progress(0)
        total_urls = len(urls_to_visit)

        # Contenedor para el tiempo transcurrido
        time_placeholder = st.empty()

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            img_tags = get_image_urls(current_url)
            if img_tags == []:
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

            # Actualizar tiempo transcurrido dinámicamente
            elapsed_time = time.time() - start_time
            time_placeholder.text(f"Tiempo transcurrido: {elapsed_time:.2f} segundos")

            # Pequeña pausa para prevenir timeouts
            time.sleep(0.1)

        # Mostrar resultados en Streamlit
        st.subheader("Resumen del análisis:")
        st.write(f"**Total de imágenes analizadas:** {total_images}")
        st.write(f"**Total de imágenes sin alt:** {total_no_alt}")
        st.write(f"**Total de imágenes sin title:** {total_no_title}")
        st.write(f"**Total de imágenes sin ambos atributos:** {total_no_both}")
        st.write(f"**Total de errores 404 encontrados:** {total_404_errors}")

        # Mostrar expanders y enlaces para descargar archivos
        def create_download_button(file_content, label):
            file = io.StringIO("\n".join(file_content))
            st.download_button(label=f"Descargar listado {label}", data=file.getvalue(), file_name=f"{label}.txt")

        with st.expander("Ver listado de imágenes sin alt"):
            st.write(urls_no_alt if urls_no_alt else "Ninguna")
            create_download_button(urls_no_alt, "sin_alt")

        with st.expander("Ver listado de imágenes sin title"):
            st.write(urls_no_title if urls_no_title else "Ninguna")
            create_download_button(urls_no_title, "sin_title")

        with st.expander("Ver listado de imágenes sin ambos atributos"):
            st.write(urls_no_both if urls_no_both else "Ninguna")
            create_download_button(urls_no_both, "sin_ambos_atributos")

        with st.expander("Ver listado de errores 404"):
            st.write(urls_404 if urls_404 else "Ninguno")
            create_download_button(urls_404, "errores_404")

        with st.expander("Ver listado total de imágenes analizadas"):
            st.write(urls_images if urls_images else "Ninguna")
            create_download_button(urls_images, "total_imagenes")

        st.success("Análisis completado.")
