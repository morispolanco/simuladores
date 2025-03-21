import streamlit as st
import requests
import json
from datetime import datetime
import plotly.express as px
import pandas as pd
import re

# Configuración de la clave API desde los secretos de Streamlit
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

# Función para extraer datos numéricos para gráficos (devuelve un diccionario)
def extract_data_for_chart(text):
    data = {}
    lines = text.split("\n")
    for line in lines:
        match = re.search(r"(\w+[\w\s]*):\s*\$?(\d+\.?\d*)", line)
        if match:
            data[match.group(1)] = float(match.group(2))
    return data if data else None

# Función para extraer datos para tabla y gráfico (devuelve una lista de diccionarios)
def extract_data_for_table_and_chart(text):
    data = []
    lines = text.split("\n")
    for line in lines:
        match = re.search(r"(\w+[\w\s]*):\s*\$?(\d+\.?\d*)\s*(?:por\s*(\d+\.?\d*)\s*semanas)?", line)
        if match:
            platform = match.group(1).strip()
            investment = float(match.group(2))
            weeks = float(match.group(3)) if match.group(3) else None
            data.append({"Plataforma": platform, "Inversión": investment, "Semanas": weeks})
    return data if data else None

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Simuladores Inversos de Marketing", layout="wide")
st.title("Simuladores Inversos de Marketing")
st.markdown("Optimiza tus estrategias con simulaciones inversas y visualizaciones interactivas.")

# Menú en la barra lateral con explicación
st.sidebar.header("Menú de Simuladores")
st.sidebar.markdown("""
### ¿Qué es esta aplicación?
Esta es un **Simulador Inverso de Marketing** creado por xAI. Te ayuda a planificar estrategias de marketing trabajando hacia atrás desde tus objetivos. Ingresa los detalles de tu producto y metas (por ejemplo, ventas, interacciones, tráfico) y obtén recomendaciones personalizadas con visualizaciones.

### ¿Qué hace?
- Ofrece herramientas para segmentación de audiencia, precios, SEO y más.
- Calcula estrategias óptimas basadas en tus entradas.
- Proporciona gráficos y tablas para un análisis fácil.
- Soporta metas personalizadas y plataformas digitales.
""")
simulator_options = [
    "Segmentación de Audiencia",
    "Campañas de Contenido",
    "Precios",
    "Embudos de Conversión",
    "Crisis de Marca",
    "SEO y Posicionamiento",
    "Lanzamiento de Producto",
    "Marketing de Influencers",
    "Inversión en Plataformas Digitales"
]
selected_simulator = st.sidebar.selectbox("Selecciona un Simulador", simulator_options, help="Elige una herramienta para comenzar.")

# Campos comunes para detalles del producto/servicio
st.subheader("Detalles del Producto o Servicio")
with st.expander("Ingresa los detalles (obligatorios)", expanded=True):
    product_name = st.text_input("Nombre del producto o servicio", "Ejemplo: Café Premium", help="Ingresa un nombre específico.")
    product_category = st.selectbox("Categoría", ["Alimentos", "Tecnología", "Moda", "Servicios", "Otros"])
    target_audience = st.text_input("Audiencia objetivo", "Ejemplo: Jóvenes de 18-35 años")
    unique_feature = st.text_input("Característica única", "Ejemplo: Sostenibilidad")
    price = st.number_input("Precio (en USD)", min_value=0.0, value=10.0, step=0.1, help="Para software/apps, ingresa el precio de suscripción mensual.")
    locality = st.text_input("Localidad", "Ejemplo: México o Global", help="Especifica un país o 'Global' si aplica a todo el mundo.")
    details_complete = product_name and target_audience and unique_feature and price > 0 and locality and product_name != "Ejemplo: Café Premium"

# Lógica para cada simulador con gráficos
if not details_complete:
    st.warning("Por favor, completa todos los detalles del producto o servicio antes de continuar.")
else:
    if selected_simulator == "Segmentación de Audiencia":
        st.header("Simulador Inverso de Segmentación de Audiencia")
        cpa_goal = st.number_input("Costo por Adquisición (CPA) objetivo", min_value=0.0, value=10.0, step=0.1)
        if st.button("Calcular Segmentos", key="seg"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un CPA objetivo de {cpa_goal}, ¿cuáles deberían ser los segmentos de mercado óptimos (edad, intereses, ubicación, comportamiento)? Proporciona datos numéricos si es posible (ejemplo: Edad 18-24: 30%)."
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
        engagement_goal = st.number_input("Objetivo de Interacciones", min_value=0, value=10000, step=100)
        if st.button("Calcular Estrategia", key="cont"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {engagement_goal} interacciones, ¿qué formatos, tonos y calendario de publicación debo usar? Incluye estimaciones numéricas si es posible (ejemplo: Video: 5000 interacciones)."
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

    elif selected_simulator == "Precios":
        st.header("Simulador Inverso de Precios")
        sales_goal = st.number_input("Objetivo de Ventas (unidades)", min_value=0, value=1000, step=10)
        if st.button("Calcular Precios", key="price"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio actual de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {sales_goal} unidades vendidas, ¿qué estrategia de precios debo emplear? Incluye ejemplos numéricos si es posible (ejemplo: Precio $10: 800 unidades)."
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
        conversion_goal = st.number_input("Tasa de Conversión Objetivo (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        if st.button("Calcular Estrategia", key="funnel"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dada una tasa de conversión objetivo de {conversion_goal}%, ¿qué tácticas debo usar en cada etapa del embudo? Incluye tasas por etapa si es posible (ejemplo: Conciencia: 50%)."
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
        damage_goal = st.number_input("Daño Máximo Aceptable a la Reputación (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        if st.button("Calcular Respuesta", key="crisis"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un daño máximo aceptable de {damage_goal}% a la reputación, ¿qué respuesta de comunicación debo usar en una crisis?"
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)

    elif selected_simulator == "SEO y Posicionamiento":
        st.header("Simulador Inverso de SEO y Posicionamiento")
        traffic_goal = st.number_input("Tráfico Orgánico Mensual Objetivo", min_value=0, value=50000, step=1000)
        if st.button("Calcular Estrategia", key="seo"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {traffic_goal} visitas orgánicas mensuales, ¿qué palabras clave y estrategias debo usar? Incluye estimaciones de tráfico por palabra si es posible (ejemplo: 'café sostenible': 20000 visitas)."
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
        adoption_goal = st.number_input("Objetivo de Adopción Inicial (unidades)", min_value=0, value=1000, step=10)
        if st.button("Calcular Plan", key="launch"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {adoption_goal} unidades vendidas en el lanzamiento, ¿qué plan debo seguir? Incluye estimaciones por canal si es posible (ejemplo: Redes Sociales: 400 unidades)."
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

    elif selected_simulator == "Marketing de Influencers":
        st.header("Simulador Inverso de Marketing de Influencers")
        reach_goal = st.number_input("Objetivo de Alcance (personas)", min_value=0, value=500000, step=1000)
        if st.button("Calcular Estrategia", key="influencer"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de alcance de {reach_goal} personas, ¿qué tipo de influencers debo usar? Incluye estimaciones de alcance por tipo si es posible (ejemplo: Micro-influencers: 100000 personas)."
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
        sales_goal = st.number_input("Objetivo de Ventas (unidades)", min_value=0, value=1000, step=10)
        budget_limit = st.number_input("Presupuesto Total (en USD)", min_value=0.0, value=5000.0, step=100.0, help="Límite máximo de inversión total.")
        platforms_available = [
            "Google Ads", "Facebook", "Instagram", "Pinterest", "LinkedIn",
            "YouTube", "TikTok", "Influencers", "Twitter (X)", "Email Marketing"
        ]
        selected_platforms = st.multiselect(
            "Selecciona plataformas digitales",
            platforms_available,
            default=["Google Ads", "Facebook", "Instagram"],
            help="Elige las plataformas en las que deseas invertir."
        )
        custom_platforms = st.text_input("Añade plataformas personalizadas (separadas por comas)", "", help="Ejemplo: Snapchat, WhatsApp")
        if custom_platforms:
            custom_list = [p.strip() for p in custom_platforms.split(",") if p.strip()]
            selected_platforms.extend(custom_list)

        if not selected_platforms:
            st.warning("Por favor, selecciona o añade al menos una plataforma.")
        elif st.button("Calcular Inversión", key="digital"):
            with st.spinner("Calculando..."):
                platforms_str = ", ".join(selected_platforms)
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {sales_goal} unidades vendidas y un presupuesto total máximo de ${budget_limit}, ¿cuánto debo invertir y por cuánto tiempo en las siguientes plataformas digitales: {platforms_str}? Proporciona estimaciones numéricas en dólares y tiempo en semanas (ejemplo: Google Ads: $500 por 4 semanas)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(data)
                st.subheader("Detalles de Inversión")
                st.table(df)
                fig = px.pie(df, names="Plataforma", values="Inversión", title="Distribución de Inversión por Plataforma")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para mostrar tabla o gráfica.")

# Pie de página
st.sidebar.markdown("---")
st.sidebar.write(f"Desarrollado por xAI - {datetime.now().strftime('%B %Y')}")
st.sidebar.info("Versión 1.6 - Contacto: support@xai.com")
