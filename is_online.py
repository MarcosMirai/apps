import streamlit as st
import socket
import requests

def check_dns(domain):
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None

def check_connectivity(domain):
    try:
        response = requests.get(f"http://{domain}", timeout=5)
        return response.status_code == 200, response.status_code
    except requests.exceptions.RequestException:
        return False, None

def main():
    st.title("Comprobador de Dominio")
    st.write("Introduce un nombre de dominio para verificar si no responde por cuestiones de DNS u otros problemas.")

    domain = st.text_input("Dominio", placeholder="ejemplo.com")

    if st.button("Comprobar"):
        if not domain:
            st.error("Por favor, introduce un dominio válido.")
        else:
            st.info(f"Comprobando el dominio: {domain}")
            
            # Comprobación de DNS
            dns_ok, ip = check_dns(domain)
            if dns_ok:
                st.success(f"DNS resuelto correctamente. IP: {ip}")
            else:
                st.error("El dominio no tiene resolución DNS.")
                return

            # Comprobación de conectividad
            connectivity_ok, status_code = check_connectivity(domain)
            if connectivity_ok:
                st.success(f"El dominio responde correctamente. Código HTTP: {status_code}")
            else:
                st.warning("El dominio tiene resolución DNS pero no responde a las solicitudes HTTP.")

if __name__ == "__main__":
    main()
