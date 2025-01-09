import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st

# Función para obtener las URLs de las imágenes de una página
def get_image_urls(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.warning(f"Error al intentar acceder a la URL: {e}")
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
    except requests.exceptions.RequestException as e:
        st.warning(f"Error al intentar acceder a la URL: {e}")
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

# Función principal para rastrear y analizar el sitio
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

        st.info("Analizando el sitio web, esto puede tardar un momento...")
        progress_bar = st.progress(0)
        total_urls = len(urls_to_visit)

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            img_tags = get_image_urls(current_url)
            if not img_tags:
                continue

            for img_tag in img_tags:
                alt_absent, title_absent = check_alt_title(img_tag)
                if alt_absent and title_absent:
                    total_no_both += 1
                elif alt_absent:
                    total_no_alt += 1
                elif title_absent:
                    total_no_title += 1

            new_links = get_all_links(current_url, base_url)
            urls_to_visit.update(new_links - visited_urls)

            # Actualizar el total de URLs dinámicamente
            total_urls = len(visited_urls) + len(urls_to_visit)

            # Actualizar progreso de forma segura
            progress_bar.progress(min(len(visited_urls) / total_urls, 1.0))


        # Mostrar resultados en Streamlit
        st.subheader("Resumen del análisis:")
        st.write(f"**Total de imágenes sin alt:** {total_no_alt}")
        st.write(f"**Total de imágenes sin title:** {total_no_title}")
        st.write(f"**Total de imágenes sin ambos atributos:** {total_no_both}")
        st.success("Análisis completado.")
