import streamlit as st
from feedbacks_app import h1checker

# Título de la app
st.sidebar.title("Menú de Feedbacks")

# Menú lateral
menu = st.sidebar.radio("Selecciona una opción:", ["Inicio", "Comprobador de etiquetas <h1>"])

# Opciones del menú
if menu == "Inicio":
    st.title("Bienvenido a Feedbacks")
    st.write("Selecciona una herramienta del menú lateral para comenzar.")
elif menu == "Comprobador de etiquetas <h1>":
    h1checker.run()
