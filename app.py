import streamlit as st
import requests
import json
from datetime import datetime
import plotly.express as px
import pandas as pd
import re

# Configuración de la API Key desde los Secrets de Streamlit
API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Función para llamar a la API de OpenRouter
def call_openrouter(prompt):
    try:
        payload = {
            "model": "mistralai/mistral-small-3.1-24b-instruct:free",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
        }
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la API: {str(e)}"
    except (KeyError, IndexError):
        return "Error: Respuesta de la API no válida."

# Función para extraer datos numéricos de la respuesta
def extract_data_for_chart(text):
    data = {}
    lines = text.split("\n")
    for line in lines:
        match = re.search(r"(\w+[\w\s]*):\s*\$?(\d+\.?\d*)", line)
        if match:
            data[match.group(1)] = float(match.group(2))
    return data if data else None

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Simuladores Inversos de Marketing", layout="wide")
st.title("Simuladores Inversos de Marketing")
st.markdown("Optimiza tus estrategias con simulaciones inversas y visualizaciones interactivas.")

# Menú en la barra lateral
st.sidebar.header("Menú de Simuladores")
simulator_options = [
    "Segmentación de Audiencia",
    "Campañas de Contenido",
    "Pricing o Precios",
    "Embudos de Conversión",
    "Crisis de Marca",
    "SEO y Posicionamiento",
    "Lanzamiento de Producto",
    "Influencer Marketing",
    "Inversión en Plataformas Digitales"
]
selected_simulator = st.sidebar.selectbox("Selecciona un Simulador", simulator_options, help="Elige una herramienta.")

# Campos comunes para detalles del producto/servicio
st.subheader("Detalles del Producto o Servicio")
with st.expander("Ingresa los detalles (obligatorios)", expanded=True):
    product_name = st.text_input("Nombre del producto o servicio", "Ejemplo: Café Premium", help="Ingresa un nombre específico.")
    product_category = st.selectbox("Categoría", ["Alimentos", "Tecnología", "Moda", "Servicios", "Otros"])
    target_audience = st.text_input("Audiencia objetivo", "Ejemplo: Jóvenes de 18-35 años")
    unique_feature = st.text_input("Característica única", "Ejemplo: Sostenibilidad")
    details_complete = product_name and target_audience and unique_feature and product_name != "Ejemplo: Café Premium"

# Lógica para cada simulador con gráficas
if not details_complete:
    st.warning("Por favor, completa todos los detalles del producto o servicio antes de continuar.")
else:
    if selected_simulator == "Segmentación de Audiencia":
        st.header("Simulador Inverso de Segmentación de Audiencia")
        cpa_goal = st.number_input("Costo por Adquisición (CPA) objetivo", min_value=0.0, value=10.0, step=0.1)
        if st.button("Calcular Segmentos", key="seg"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un CPA objetivo de {cpa_goal}, ¿cuáles deberían ser los segmentos de mercado óptimos (edad, intereses, ubicación, comportamiento)? Proporciona datos numéricos si es posible (ejemplo: Edad 18-24: 30%)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Segmento", "Porcentaje"])
                fig = px.pie(df, names="Segmento", values="Porcentaje", title="Distribución de Segmentos")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Campañas de Contenido":
        st.header("Simulador Inverso de Campañas de Contenido")
        engagement_goal = st.number_input("Objetivo de interacciones", min_value=0, value=10000, step=100)
        if st.button("Calcular Estrategia", key="cont"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un objetivo de {engagement_goal} interacciones, ¿qué formatos, tonos y calendario de publicación debo usar? Incluye estimaciones numéricas si es posible (ejemplo: Video: 5000 interacciones)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Formato", "Interacciones"])
                fig = px.bar(df, x="Formato", y="Interacciones", title="Interacciones por Formato")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Pricing o Precios":
        st.header("Simulador Inverso de Pricing")
        sales_goal = st.number_input("Objetivo de unidades vendidas", min_value=0, value=1000, step=10)
        if st.button("Calcular Precios", key="price"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un objetivo de {sales_goal} unidades vendidas, ¿qué estrategia de precios debo emplear? Incluye ejemplos numéricos si es posible (ejemplo: Precio $10: 800 unidades)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Precio", "Unidades"])
                fig = px.line(df, x="Precio", y="Unidades", title="Ventas por Estrategia de Precio")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Embudos de Conversión":
        st.header("Simulador Inverso de Embudos de Conversión")
        conversion_goal = st.number_input("Tasa de conversión objetivo (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        if st.button("Calcular Estrategia", key="funnel"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dada una tasa de conversión objetivo de {conversion_goal}%, ¿qué tácticas debo usar en cada etapa del embudo? Incluye tasas por etapa si es posible (ejemplo: Conciencia: 50%)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Etapa", "Tasa"])
                fig = px.funnel(df, x="Tasa", y="Etapa", title="Embudo de Conversión")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Crisis de Marca":
        st.header("Simulador Inverso de Crisis de Marca")
        damage_goal = st.number_input("Daño máximo aceptable a la reputación (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        if st.button("Calcular Respuesta", key="crisis"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un daño máximo aceptable de {damage_goal}% a la reputación, ¿qué respuesta de comunicación debo usar en una crisis?"
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)

    elif selected_simulator == "SEO y Posicionamiento":
        st.header("Simulador Inverso de SEO")
        traffic_goal = st.number_input("Objetivo de tráfico orgánico mensual", min_value=0, value=50000, step=1000)
        if st.button("Calcular Estrategia", key="seo"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un objetivo de {traffic_goal} visitas orgánicas mensuales, ¿qué palabras clave y estrategias debo usar? Incluye estimaciones de tráfico por palabra si es posible (ejemplo: 'café sostenible': 20000 visitas)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Palabra Clave", "Tráfico"])
                fig = px.bar(df, x="Palabra Clave", y="Tráfico", title="Tráfico por Palabra Clave")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Lanzamiento de Producto":
        st.header("Simulador Inverso de Lanzamiento de Producto")
        adoption_goal = st.number_input("Objetivo de adopción inicial (unidades)", min_value=0, value=1000, step=10)
        if st.button("Calcular Plan", key="launch"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un objetivo de {adoption_goal} unidades vendidas en el lanzamiento, ¿qué plan debo seguir? Incluye estimaciones por canal si es posible (ejemplo: Redes Sociales: 400 unidades)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Canal", "Unidades"])
                fig = px.pie(df, names="Canal", values="Unidades", title="Adopción por Canal")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Influencer Marketing":
        st.header("Simulador Inverso de Influencer Marketing")
        reach_goal = st.number_input("Objetivo de alcance (personas)", min_value=0, value=500000, step=1000)
        if st.button("Calcular Estrategia", key="influencer"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un objetivo de alcance de {reach_goal} personas, ¿qué tipo de influencers debo usar? Incluye estimaciones de alcance por tipo si es posible (ejemplo: Micro-influencers: 100000 personas)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Tipo de Influencer", "Alcance"])
                fig = px.bar(df, x="Tipo de Influencer", y="Alcance", title="Alcance por Tipo de Influencer")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Inversión en Plataformas Digitales":
        st.header("Simulador Inverso de Inversión en Plataformas Digitales")
        sales_goal = st.number_input("Objetivo de ventas (unidades)", min_value=0, value=1000, step=10)
        if st.button("Calcular Inversión", key="digital"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', y dado un objetivo de {sales_goal} unidades vendidas, ¿cuánto debo invertir y por cuánto tiempo en las siguientes plataformas digitales: Google Ads, Facebook, Instagram, Pinterest, LinkedIn, YouTube, TikTok, Influencers, Twitter (X), Email Marketing? Proporciona estimaciones numéricas en dólares y tiempo en semanas si es posible (ejemplo: Google Ads: $500 por 4 semanas)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            # Intentar graficar
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Plataforma", "Inversión"])
                fig = px.pie(df, names="Plataforma", values="Inversión", title="Distribución de Inversión por Plataforma")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

# Pie de página
st.sidebar.markdown("---")
st.sidebar.write(f"Desarrollado por xAI - {datetime.now().strftime('%B %Y')}")
st.sidebar.info("Versión 1.3 - Contacto: support@xai.com")
