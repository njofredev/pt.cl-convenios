import streamlit as st
import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MEDILINK_TOKEN")
BASE_URL = os.getenv("MEDILINK_BASE_URL", "https://api.medilink.healthatom.com/api/v1")

st.set_page_config(page_title="Medilink MVP - Tabancura", layout="wide")

def get_headers():
    return {
        "Authorization": f"Token {API_KEY}",
        "Accept": "application/json"
    }

def fetch_all_pacientes(id_conv):
    all_data = []
    current_page = 1
    status_container = st.empty()
    
    while True:
        # Formato EXACTO que pide el error: un JSON string dentro de la URL
        # Probamos con id_convenio y con convenio_id por si acaso
        filter_str = json.dumps({"id_convenio": {"eq": str(id_conv)}})
        
        # URL construida manualmente para evitar que 'requests' doble-codifique el JSON
        url = f"{BASE_URL}/pacientes?q={filter_str}&page={current_page}"
        
        try:
            status_container.info(f"Cargando página {current_page}...")
            
            # Petición limpia sin el dict de params para que no se altere el string q
            response = requests.get(url, headers=get_headers())

            if response.status_code != 200:
                st.error(f"Error {response.status_code}: {response.text}")
                # Si falla con id_convenio, intentamos con 'convenio' a secas
                filter_alt = json.dumps({"convenio": {"eq": str(id_conv)}})
                url_alt = f"{BASE_URL}/pacientes?q={filter_alt}&page={current_page}"
                response = requests.get(url_alt, headers=get_headers())
                
                if response.status_code != 200:
                    break
            
            res_json = response.json()
            data_pagina = res_json.get('data', [])
            
            if not data_pagina:
                break
                
            all_data.extend(data_pagina)
            if len(data_pagina) < 20: 
                break
                
            current_page += 1
            
        except Exception as e:
            st.error(f"Error: {e}")
            break
            
    status_container.empty()
    return all_data

# --- UI ---
st.title("🏥 Explorador de Convenios - Tabancura")

id_conv = st.number_input("ID Convenio", min_value=1, value=4)

if st.button("Consultar Todo", type="primary"):
    with st.spinner("Buscando en Medilink..."):
        pacientes = fetch_all_pacientes(id_conv)
        
        if pacientes:
            df = pd.DataFrame(pacientes)
            st.success(f"Se cargaron {len(df)} pacientes.")
            st.dataframe(df[['rut', 'nombre', 'apellidos']], use_container_width=True)
        else:
            st.warning("No se encontraron resultados. Es posible que el campo de filtro sea distinto.")