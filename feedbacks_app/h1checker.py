import requests
from bs4 import BeautifulSoup
import streamlit as st

def check_h1_tag(url, pages_with_h1, pages_without_h1):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            pages_without_h1.add(url)
        else:
            pages_with_h1.add(url)
    else:
        st.warning(f"No se pudo acceder a la página: {url}")

def run():
    st.title("Comprobador de etiquetas <h1>")
    subdomain_url = st.text_input("Introduce la URL del subdominio:")

    if st.button("Comprobar"):
        if not subdomain_url:
            st.error("Por favor, introduce una URL válida.")
            return

        response = requests.get(subdomain_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            st.info("Comprobando contenidos...")
            pages_with_h1 = set()
            pages_without_h1 = set()
            
            for link in links:
                url = link['href']
                if url.startswith(subdomain_url):
                    check_h1_tag(url, pages_with_h1, pages_without_h1)

            # Mostrar resultados en Streamlit
            st.subheader("Resultados:")
            
            st.write("### Páginas con la etiqueta <h1>:")
            for page in pages_with_h1:
                st.write(f"- {page}")
            
            st.write("\n### Páginas sin la etiqueta <h1>:")
            for page in pages_without_h1:
                st.write(f"- {page}")

            st.write(f"**Total de páginas con la etiqueta <h1>:** {len(pages_with_h1)}")
            st.write(f"**Total de páginas sin la etiqueta <h1>:** {len(pages_without_h1)}")

            total_documents = len(pages_with_h1) + len(pages_without_h1)
            st.write(f"**Total de documentos analizados:** {total_documents}")
            
        else:
            st.error(f"No se pudo acceder al subdominio: {subdomain_url}")
