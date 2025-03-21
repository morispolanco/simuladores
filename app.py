import streamlit as st
import requests
import json
import os

# Configuración de la API Key desde los Secrets de Streamlit
API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Función para llamar a la API de OpenRouter
def call_openrouter(prompt):
    payload = {
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Configuración de la interfaz de Streamlit
st.title("Simuladores Inversos de Marketing")

# Menú en la barra lateral
simulator_options = [
    "Segmentación de Audiencia",
    "Campañas de Contenido",
    "Pricing o Precios",
    "Embudos de Conversión",
    "Crisis de Marca",
    "SEO y Posicionamiento",
    "Lanzamiento de Producto",
    "Influencer Marketing"
]
selected_simulator = st.sidebar.selectbox("Selecciona un Simulador", simulator_options)

# Lógica para cada simulador
if selected_simulator == "Segmentación de Audiencia":
    st.header("Simulador Inverso de Segmentación de Audiencia")
    cpa_goal = st.number_input("Ingresa el Costo por Adquisición (CPA) objetivo", min_value=0.0, value=10.0)
    if st.button("Calcular Segmentos"):
        prompt = f"Dado un CPA objetivo de {cpa_goal}, ¿cuáles deberían ser los segmentos de mercado óptimos (edad, intereses, ubicación, comportamiento)?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "Campañas de Contenido":
    st.header("Simulador Inverso de Campañas de Contenido")
    engagement_goal = st.number_input("Ingresa el objetivo de interacciones", min_value=0, value=10000)
    if st.button("Calcular Estrategia"):
        prompt = f"Dado un objetivo de {engagement_goal} interacciones, ¿qué formatos, tonos y calendario de publicación debo usar?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "Pricing o Precios":
    st.header("Simulador Inverso de Pricing")
    sales_goal = st.number_input("Ingresa el objetivo de unidades vendidas", min_value=0, value=1000)
    if st.button("Calcular Precios"):
        prompt = f"Dado un objetivo de {sales_goal} unidades vendidas, ¿qué estrategia de precios debo emplear?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "Embudos de Conversión":
    st.header("Simulador Inverso de Embudos de Conversión")
    conversion_goal = st.number_input("Ingresa la tasa de conversión objetivo (%)", min_value=0.0, max_value=100.0, value=5.0)
    if st.button("Calcular Estrategia"):
        prompt = f"Dada una tasa de conversión objetivo de {conversion_goal}%, ¿qué tácticas debo usar en cada etapa del embudo?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "Crisis de Marca":
    st.header("Simulador Inverso de Crisis de Marca")
    damage_goal = st.number_input("Ingresa el daño máximo aceptable a la reputación (%)", min_value=0.0, max_value=100.0, value=10.0)
    if st.button("Calcular Respuesta"):
        prompt = f"Dado un daño máximo aceptable de {damage_goal}% a la reputación, ¿qué respuesta de comunicación debo usar?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "SEO y Posicionamiento":
    st.header("Simulador Inverso de SEO")
    traffic_goal = st.number_input("Ingresa el objetivo de tráfico orgánico mensual", min_value=0, value=50000)
    if st.button("Calcular Estrategia"):
        prompt = f"Dado un objetivo de {traffic_goal} visitas orgánicas mensuales, ¿qué palabras clave y estrategias debo usar?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "Lanzamiento de Producto":
    st.header("Simulador Inverso de Lanzamiento de Producto")
    adoption_goal = st.number_input("Ingresa el objetivo de adopción inicial (unidades)", min_value=0, value=1000)
    if st.button("Calcular Plan"):
        prompt = f"Dado un objetivo de {adoption_goal} unidades vendidas en el lanzamiento, ¿qué plan debo seguir?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

elif selected_simulator == "Influencer Marketing":
    st.header("Simulador Inverso de Influencer Marketing")
    reach_goal = st.number_input("Ingresa el objetivo de alcance (personas)", min_value=0, value=500000)
    if st.button("Calcular Estrategia"):
        prompt = f"Dado un objetivo de alcance de {reach_goal} personas, ¿qué tipo de influencers debo usar?"
        result = call_openrouter(prompt)
        st.write("**Recomendación:**")
        st.write(result)

# Pie de página
st.sidebar.write("Desarrollado por xAI - Marzo 2025")
