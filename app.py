import streamlit as st
import requests
import json
from datetime import datetime
import plotly.express as px
import pandas as pd
import re

# Configuration of the API Key from Streamlit Secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Function to call the OpenRouter API
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
        return f"Error connecting to the API: {str(e)}"
    except (KeyError, IndexError):
        return "Error: Invalid API response."

# Function to extract numeric data from the response (investment and time)
def extract_data_for_table_and_chart(text):
    data = []
    lines = text.split("\n")
    for line in lines:
        match = re.search(r"(\w+[\w\s]*):\s*\$?(\d+\.?\d*)\s*(?:for\s*(\d+\.?\d*)\s*weeks)?", line)
        if match:
            platform = match.group(1).strip()
            investment = float(match.group(2))
            weeks = float(match.group(3)) if match.group(3) else None
            data.append({"Platform": platform, "Investment": investment, "Weeks": weeks})
    return data if data else None

# Streamlit interface configuration
st.set_page_config(page_title="Inverse Marketing Simulators", layout="wide")
st.title("Inverse Marketing Simulators")
st.markdown("Optimize your strategies with inverse simulations and interactive visualizations.")

# Sidebar menu
st.sidebar.header("Simulator Menu")
simulator_options = [
    "Audience Segmentation",
    "Content Campaigns",
    "Pricing",
    "Conversion Funnels",
    "Brand Crisis",
    "SEO and Positioning",
    "Product Launch",
    "Influencer Marketing",
    "Digital Platforms Investment"
]
selected_simulator = st.sidebar.selectbox("Select a Simulator", simulator_options, help="Choose a tool to start.")

# Common fields for product/service details
st.subheader("Product or Service Details")
with st.expander("Enter details (required)", expanded=True):
    product_name = st.text_input("Product or service name", "Example: Premium Coffee", help="Enter a specific name.")
    product_category = st.selectbox("Category", ["Food", "Technology", "Fashion", "Services", "Others"])
    target_audience = st.text_input("Target audience", "Example: Young people aged 18-35")
    unique_feature = st.text_input("Unique feature", "Example: Sustainability")
    price = st.number_input("Price (in USD)", min_value=0.0, value=10.0, step=0.1, help="For software/apps, enter the monthly subscription price.")
    locality = st.text_input("Locality", "Example: Mexico or Global", help="Specify a country or 'Global' if applicable worldwide.")
    details_complete = product_name and target_audience and unique_feature and price > 0 and locality and product_name != "Example: Premium Coffee"

# Logic for each simulator with charts
if not details_complete:
    st.warning("Please complete all product or service details before proceeding.")
else:
    if selected_simulator == "Audience Segmentation":
        st.header("Inverse Audience Segmentation Simulator")
        cpa_goal = st.number_input("Target Cost per Acquisition (CPA)", min_value=0.0, value=10.0, step=0.1)
        if st.button("Calculate Segments", key="seg"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target CPA of {cpa_goal}, what should be the optimal market segments (age, interests, location, behavior)? Provide numeric data if possible (e.g., Age 18-24: 30%)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Segment", "Percentage"])
                fig = px.pie(df, names="Segment", values="Percentage", title="Segment Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Content Campaigns":
        st.header("Inverse Content Campaigns Simulator")
        engagement_goal = st.number_input("Target Engagement (interactions)", min_value=0, value=10000, step=100)
        if st.button("Calculate Strategy", key="cont"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target of {engagement_goal} interactions, what formats, tones, and publishing schedule should I use? Include numeric estimates if possible (e.g., Video: 5000 interactions)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Format", "Interactions"])
                fig = px.bar(df, x="Format", y="Interactions", title="Interactions by Format")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Pricing":
        st.header("Inverse Pricing Simulator")
        sales_goal = st.number_input("Target Sales (units)", min_value=0, value=1000, step=10)
        if st.button("Calculate Pricing", key="price"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', current price of ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target of {sales_goal} units sold, what pricing strategy should I use? Include numeric examples if possible (e.g., Price $10: 800 units)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Price", "Units"])
                fig = px.line(df, x="Price", y="Units", title="Sales by Pricing Strategy")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Conversion Funnels":
        st.header("Inverse Conversion Funnels Simulator")
        conversion_goal = st.number_input("Target Conversion Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
        if st.button("Calculate Strategy", key="funnel"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target conversion rate of {conversion_goal}%, what tactics should I use at each funnel stage? Include stage rates if possible (e.g., Awareness: 50%)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Stage", "Rate"])
                fig = px.funnel(df, x="Rate", y="Stage", title="Conversion Funnel")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Brand Crisis":
        st.header("Inverse Brand Crisis Simulator")
        damage_goal = st.number_input("Maximum Acceptable Reputation Damage (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        if st.button("Calculate Response", key="crisis"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a maximum acceptable reputation damage of {damage_goal}%, what communication response should I use in a crisis?"
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)

    elif selected_simulator == "SEO and Positioning":
        st.header("Inverse SEO and Positioning Simulator")
        traffic_goal = st.number_input("Target Monthly Organic Traffic", min_value=0, value=50000, step=1000)
        if st.button("Calculate Strategy", key="seo"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target of {traffic_goal} monthly organic visits, what keywords and strategies should I use? Include traffic estimates per keyword if possible (e.g., 'sustainable coffee': 20000 visits)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Keyword", "Traffic"])
                fig = px.bar(df, x="Keyword", y="Traffic", title="Traffic by Keyword")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Product Launch":
        st.header("Inverse Product Launch Simulator")
        adoption_goal = st.number_input("Target Initial Adoption (units)", min_value=0, value=1000, step=10)
        if st.button("Calculate Plan", key="launch"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target of {adoption_goal} units sold at launch, what plan should I follow? Include channel estimates if possible (e.g., Social Media: 400 units)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Channel", "Units"])
                fig = px.pie(df, names="Channel", values="Units", title="Adoption by Channel")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Influencer Marketing":
        st.header("Inverse Influencer Marketing Simulator")
        reach_goal = st.number_input("Target Reach (people)", min_value=0, value=500000, step=1000)
        if st.button("Calculate Strategy", key="influencer"):
            with st.spinner("Calculating..."):
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target reach of {reach_goal} people, what type of influencers should I use? Include reach estimates by type if possible (e.g., Micro-influencers: 100000 people)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(list(data.items()), columns=["Influencer Type", "Reach"])
                fig = px.bar(df, x="Influencer Type", y="Reach", title="Reach by Influencer Type")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to plot.")

    elif selected_simulator == "Digital Platforms Investment":
        st.header("Inverse Digital Platforms Investment Simulator")
        sales_goal = st.number_input("Target Sales (units)", min_value=0, value=1000, step=10)
        budget_limit = st.number_input("Total Budget (in USD)", min_value=0.0, value=5000.0, step=100.0, help="Maximum total investment limit.")
        platforms_available = [
            "Google Ads", "Facebook", "Instagram", "Pinterest", "LinkedIn",
            "YouTube", "TikTok", "Influencers", "Twitter (X)", "Email Marketing"
        ]
        selected_platforms = st.multiselect(
            "Select digital platforms",
            platforms_available,
            default=["Google Ads", "Facebook", "Instagram"],
            help="Choose the platforms you want to invest in."
        )
        custom_platforms = st.text_input("Add custom platforms (comma-separated)", "", help="Example: Snapchat, WhatsApp")
        if custom_platforms:
            custom_list = [p.strip() for p in custom_platforms.split(",") if p.strip()]
            selected_platforms.extend(custom_list)

        if not selected_platforms:
            st.warning("Please select or add at least one platform.")
        elif st.button("Calculate Investment", key="digital"):
            with st.spinner("Calculating..."):
                platforms_str = ", ".join(selected_platforms)
                prompt = f"For a product '{product_name}' in the category '{product_category}', targeting '{target_audience}' with the unique feature '{unique_feature}', priced at ${price} ({'monthly subscription' if product_category == 'Technology' else 'unit price'}) and in the locality '{locality}', given a target of {sales_goal} units sold and a maximum total budget of ${budget_limit}, how much should I invest and for how long in the following digital platforms: {platforms_str}? Provide numeric estimates in dollars and time in weeks (e.g., Google Ads: $500 for 4 weeks)."
                result = call_openrouter(prompt)
            st.subheader("Recommendation")
            st.markdown(result, unsafe_allow_html=True)
            
            # Extract data for table and chart
            data = extract_data_for_table_and_chart(result)
            if data:
                df = pd.DataFrame(data)
                # Show table
                st.subheader("Investment Details")
                st.table(df)
                # Chart
                fig = px.pie(df, names="Platform", values="Investment", title="Investment Distribution by Platform")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric data found to display table or chart.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write(f"Developed by xAI - {datetime.now().strftime('%B %Y')}")
st.sidebar.info("Version 1.6 - Contact: support@xai.com")
