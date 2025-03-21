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

# Función para llamar a la API de OpenRouter usando requests
def call_openrouter(prompt):
    try:
        payload = {
            "model": "qwen/qwq-32b:free",
            "messages": [
                {"role": "user", "content": prompt}
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

# Instrucciones generales desplegables
with st.expander("Instrucciones Generales", expanded=False):
    st.markdown("""
    ### Guía Básica
    1. Selecciona un simulador en la barra lateral.
    2. Completa los detalles del producto/servicio.
    3. Define tu objetivo y haz clic en "Calcular".
    4. Revisa las recomendaciones y visualizaciones.
    **Nota**: Completa todos los campos obligatorios para evitar errores.
    """)

# Menú en la barra lateral sin instrucciones generales
st.sidebar.header("Menú de Simuladores")
simulator_options = sorted([
    "Campañas de Contenido", "Competencia", "Crisis de Marca", "Embudos de Conversión",
    "Eventos y Promociones", "Expansión de Mercado", "Experiencia del Cliente",
    "Gestión de Presupuesto Total", "Innovación de Producto", "Inversión en Plataformas Digitales",
    "Lanzamiento de Producto", "Marketing de Influencers", "Precios", "Publicidad Offline",
    "Retención de Clientes", "Segmentación de Audiencia", "SEO y Posicionamiento"
])
selected_simulator = st.sidebar.radio("Selecciona un Simulador", simulator_options, help="Elige una herramienta para comenzar.")

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

# Lógica para cada simulador
if not details_complete:
    st.warning("Por favor, completa todos los detalles del producto o servicio antes de continuar.")
else:
    if selected_simulator == "Segmentación de Audiencia":
        st.header("Simulador Inverso de Segmentación de Audiencia")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador identifica los segmentos de mercado óptimos (edad, intereses, ubicación, comportamiento) para alcanzar un Costo por Adquisición (CPA) objetivo, basado en los detalles de tu producto y audiencia.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador recomienda formatos, tonos y un calendario de publicación para alcanzar un número específico de interacciones, optimizando tu estrategia de contenido según tu producto y audiencia.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador sugiere una estrategia de precios para alcanzar un objetivo de ventas en unidades, considerando las características de tu producto y el mercado objetivo.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador propone tácticas para cada etapa del embudo de conversión (conciencia, interés, decisión, acción) para lograr una tasa de conversión objetivo, adaptada a tu producto.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador ofrece una estrategia de comunicación para limitar el daño a la reputación de tu marca en una crisis, basado en un porcentaje máximo aceptable de daño.
            """)
        damage_goal = st.number_input("Daño Máximo Aceptable a la Reputación (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        if st.button("Calcular Respuesta", key="crisis"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un daño máximo aceptable de {damage_goal}% a la reputación, ¿qué respuesta de comunicación debo usar en una crisis?"
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)

    elif selected_simulator == "SEO y Posicionamiento":
        st.header("Simulador Inverso de SEO y Posicionamiento")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador recomienda palabras clave y estrategias SEO para alcanzar un objetivo de tráfico orgánico mensual, optimizando la visibilidad de tu producto en buscadores.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador diseña un plan de lanzamiento para alcanzar un objetivo de adopción inicial en unidades, sugiriendo canales y tácticas basadas en tu producto.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador recomienda tipos de influencers y estrategias para alcanzar un objetivo de alcance en personas, optimizando la promoción de tu producto.
            """)
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
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador calcula cuánto invertir y por cuánto tiempo en plataformas digitales seleccionadas para alcanzar un objetivo de ventas, respetando un presupuesto máximo.
            """)
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

    elif selected_simulator == "Retención de Clientes":
        st.header("Simulador Inverso de Retención de Clientes")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador calcula estrategias para alcanzar un porcentaje objetivo de retención de clientes, sugiriendo tácticas como programas de lealtad o emails personalizados.
            """)
        retention_goal = st.number_input("Porcentaje de Retención Objetivo (%)", min_value=0.0, max_value=100.0, value=80.0, step=0.1)
        if st.button("Calcular Estrategias", key="retention"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de retención de {retention_goal}%, ¿qué estrategias debo usar para retener clientes? Incluye estimaciones numéricas si es posible (ejemplo: Programa de lealtad: 20%)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Estrategia", "Impacto"])
                fig = px.bar(df, x="Estrategia", y="Impacto", title="Impacto en Retención por Estrategia")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Publicidad Offline":
        st.header("Simulador Inverso de Publicidad Offline")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador diseña una estrategia de publicidad tradicional (TV, radio, vallas publicitarias, etc.) para alcanzar un objetivo de alcance o ventas, considerando el presupuesto y la localidad.
            """)
        reach_goal = st.number_input("Objetivo de Alcance (personas)", min_value=0, value=100000, step=1000)
        budget_limit = st.number_input("Presupuesto Total (en USD)", min_value=0.0, value=5000.0, step=100.0)
        if st.button("Calcular Estrategia", key="offline"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de alcance de {reach_goal} personas y un presupuesto máximo de ${budget_limit}, ¿qué estrategia de publicidad offline (TV, radio, vallas, etc.) debo usar? Incluye estimaciones numéricas si es posible (ejemplo: TV: $2000 para 50000 personas)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Canal", "Alcance"])
                fig = px.pie(df, names="Canal", values="Alcance", title="Distribución de Alcance por Canal Offline")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Experiencia del Cliente":
        st.header("Simulador Inverso de Experiencia del Cliente")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador propone mejoras en puntos de contacto (atención al cliente, sitio web, entrega) para lograr un puntaje objetivo de satisfacción (como NPS o CSAT).
            """)
        satisfaction_goal = st.number_input("Puntaje de Satisfacción Objetivo (NPS)", min_value=-100, max_value=100, value=50, step=1)
        if st.button("Calcular Mejoras", key="cx"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de NPS de {satisfaction_goal}, ¿qué mejoras en la experiencia del cliente debo implementar? Incluye estimaciones numéricas si es posible (ejemplo: Chat en vivo: +15 puntos NPS)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Mejora", "Impacto"])
                fig = px.bar(df, x="Mejora", y="Impacto", title="Impacto en NPS por Mejora")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Expansión de Mercado":
        st.header("Simulador Inverso de Expansión de Mercado")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador sugiere estrategias para entrar en nuevos mercados o regiones, alcanzando un objetivo de ventas o cuota de mercado en una nueva localidad.
            """)
        sales_goal = st.number_input("Objetivo de Ventas (unidades)", min_value=0, value=1000, step=10)
        new_locality = st.text_input("Nueva Localidad", "Ejemplo: España")
        if st.button("Calcular Estrategia", key="expansion"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad actual '{locality}', dado un objetivo de {sales_goal} unidades vendidas en la nueva localidad '{new_locality}', ¿qué estrategias debo usar para expandir el mercado? Incluye estimaciones numéricas si es posible (ejemplo: Alianzas locales: 300 unidades)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Estrategia", "Ventas"])
                fig = px.bar(df, x="Estrategia", y="Ventas", title="Ventas por Estrategia de Expansión")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Gestión de Presupuesto Total":
        st.header("Simulador Inverso de Gestión de Presupuesto Total")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador distribuye un presupuesto total de marketing entre canales digitales y offline para maximizar un objetivo combinado (ventas, tráfico, alcance).
            """)
        total_budget = st.number_input("Presupuesto Total (en USD)", min_value=0.0, value=10000.0, step=100.0)
        goal_type = st.selectbox("Objetivo Principal", ["Ventas (unidades)", "Alcance (personas)", "Tráfico (visitas)"])
        goal_value = st.number_input(f"Valor del Objetivo ({goal_type.split()[0]})", min_value=0, value=5000, step=100)
        if st.button("Calcular Distribución", key="budget"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un presupuesto total de ${total_budget} y un objetivo de {goal_value} {goal_type.split()[0].lower()}, ¿cómo debo distribuir el presupuesto entre canales digitales y offline? Incluye estimaciones numéricas si es posible (ejemplo: Google Ads: $2000)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Canal", "Inversión"])
                fig = px.pie(df, names="Canal", values="Inversión", title="Distribución del Presupuesto")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Eventos y Promociones":
        st.header("Simulador Inverso de Eventos y Promociones")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador planea eventos o promociones (descuentos, ferias) para alcanzar un objetivo de ventas o asistencia, ajustándose a un presupuesto.
            """)
        sales_goal = st.number_input("Objetivo de Ventas (unidades)", min_value=0, value=500, step=10)
        budget_limit = st.number_input("Presupuesto Total (en USD)", min_value=0.0, value=2000.0, step=100.0)
        if st.button("Calcular Plan", key="events"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {sales_goal} unidades vendidas y un presupuesto máximo de ${budget_limit}, ¿qué eventos o promociones debo realizar? Incluye estimaciones numéricas si es posible (ejemplo: Feria local: 200 ventas)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Evento", "Ventas"])
                fig = px.bar(df, x="Evento", y="Ventas", title="Ventas por Evento o Promoción")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Competencia":
        st.header("Simulador Inverso de Competencia")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador analiza cómo superar a un competidor específico en ventas, visibilidad o cuota de mercado, sugiriendo estrategias diferenciadoras.
            """)
        competitor_name = st.text_input("Nombre del Competidor", "Ejemplo: Competidor X")
        sales_increase = st.number_input("Incremento de Ventas Objetivo (%)", min_value=0.0, value=10.0, step=0.1)
        if st.button("Calcular Estrategia", key="competition"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de superar al competidor '{competitor_name}' en un {sales_increase}% de ventas, ¿qué estrategias debo usar? Incluye estimaciones numéricas si es posible (ejemplo: Campaña diferenciadora: +5%)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Estrategia", "Incremento"])
                fig = px.bar(df, x="Estrategia", y="Incremento", title="Incremento de Ventas por Estrategia")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

    elif selected_simulator == "Innovación de Producto":
        st.header("Simulador Inverso de Innovación de Producto")
        with st.expander("¿Qué hace este simulador?", expanded=False):
            st.markdown("""
            Este simulador propone mejoras o nuevas características para tu producto que cumplan un objetivo de adopción o satisfacción, basado en las necesidades de la audiencia.
            """)
        adoption_goal = st.number_input("Objetivo de Adopción (unidades)", min_value=0, value=1000, step=10)
        if st.button("Calcular Innovaciones", key="innovation"):
            with st.spinner("Calculando..."):
                prompt = f"Para un producto '{product_name}' en la categoría '{product_category}', dirigido a '{target_audience}' con la característica única '{unique_feature}', con un precio de ${price} ({'suscripción mensual' if product_category == 'Tecnología' else 'precio unitario'}) y en la localidad '{locality}', dado un objetivo de {adoption_goal} unidades adoptadas, ¿qué mejoras o nuevas características debo implementar? Incluye estimaciones numéricas si es posible (ejemplo: Envase ecológico: 300 unidades)."
                result = call_openrouter(prompt)
            st.subheader("Recomendación")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Innovación", "Adopción"])
                fig = px.bar(df, x="Innovación", y="Adopción", title="Adopción por Innovación")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron datos numéricos para graficar.")

# Pie de página
st.sidebar.markdown("---")
st.sidebar.write(f"Desarrollado por xAI - {datetime.now().strftime('%B %Y')}")
st.sidebar.info("Versión 1.6 - Contacto: mp@ufm.edu")
