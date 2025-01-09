import streamlit as st
from feedbacks_app import h1checker, alt_title_checker

menu = st.sidebar.radio("Selecciona una opción:", ["Inicio", "Comprobador de etiquetas <h1>", "Verificador de alt/title en imágenes"])

if menu == "Inicio":
    st.title("Bienvenido a Feedbacks")
    st.write("Selecciona una herramienta del menú lateral.")
elif menu == "Comprobador de etiquetas <h1>":
    h1checker.run()
elif menu == "Verificador de alt/title en imágenes":
    alt_title_checker.run()
