import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Narae AI",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 Narae AI")

st.markdown("### K-Entertainment Merchandise Import Assistant")

st.info(
    """
Analyze K-pop merchandise using AI.

This prototype estimates:

✅ HS Classification

✅ Import Duty

✅ Required Documents

✅ Customs Risks

Built as the first prototype of **Narae**, an AI logistics platform for the global entertainment industry.
"""
)

product = st.text_input(
    "Product Name",
    placeholder="Example: BTS Cotton Hoodie"
)

country = st.selectbox(
    "Destination Country",
    [
        "United States",
        "India",
        "United Kingdom",
        "Germany",
        "Japan",
        "Australia",
        "Singapore"
    ]
)

shipment_value = st.number_input(
    "Shipment Value (USD)",
    min_value=0.0,
    value=100.0,
    step=10.0
)

if st.button("Analyze Shipment"):

    if product == "":
        st.warning("Please enter a product.")
        st.stop()

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    prompt = f"""
You are an international customs and logistics expert.

Product:
{product}

Destination:
{country}

Shipment Value:
{shipment_value}

Provide the following sections:

1. Likely HS Code

2. Estimated Import Duty

3. Required Shipping Documents

4. Customs Risks

5. AI Logistics Summary

Use headings and bullet points.
"""

    with st.spinner("Analyzing shipment..."):

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a customs classification and logistics specialist."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    st.success("✅ Analysis Complete")

    st.markdown(response.choices[0].message.content)
