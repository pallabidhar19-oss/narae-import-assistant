import json
import streamlit as st
from openai import OpenAI


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Narae AI",
    page_icon="🎵",
    layout="centered"
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🎵 Narae AI")
st.markdown("### K-Entertainment Merchandise Import Assistant")

st.info(
    """
    Analyze K-entertainment merchandise using AI.

    Narae helps organize:
    • Product classification
    • HS / HTS classification guidance
    • Import-duty estimation
    • Required documentation
    • Customs and IP risks

    ⚠️ Narae is an early-stage decision-support prototype.
    Final customs classifications should be verified against
    the applicable tariff schedule and customs authority.
    """
)


# ---------------------------------------------------------
# PRODUCT INFORMATION
# ---------------------------------------------------------

st.markdown("## 📦 Product Information")

product = st.text_input(
    "Product Name",
    placeholder="Example: BTS Cotton Pullover Hoodie"
)

description = st.text_area(
    "Detailed Product Description",
    placeholder=(
        "Example: Adult pullover hoodie featuring BTS branding, "
        "80% cotton and 20% polyester, knitted construction."
    )
)

col1, col2 = st.columns(2)

with col1:
    product_type = st.selectbox(
        "Product Type",
        [
            "Apparel / Hoodie",
            "T-Shirt",
            "Sweatshirt",
            "Album / CD",
            "Photocard",
            "Light Stick",
            "Poster / Printed Material",
            "Cosmetics",
            "Accessory",
            "Toy / Character Merchandise",
            "Other"
        ]
    )

with col2:
    construction = st.selectbox(
        "Construction",
        [
            "Knitted / Crocheted",
            "Woven",
            "Plastic / Rigid",
            "Electronic",
            "Printed Paper",
            "Liquid / Cosmetic",
            "Unknown / Not Applicable"
        ]
    )

col3, col4 = st.columns(2)

with col3:
    material = st.text_input(
        "Primary Material / Composition",
        placeholder="Example: 80% cotton, 20% polyester"
    )

with col4:
    wearer = st.selectbox(
        "Intended Wearer",
        [
            "Men's",
            "Women's",
            "Boys'",
            "Girls'",
            "Unisex / Unknown",
            "Not Applicable"
        ]
    )


# ---------------------------------------------------------
# SHIPMENT INFORMATION
# ---------------------------------------------------------

st.markdown("## 🌏 Shipment Information")

col5, col6 = st.columns(2)

with col5:
    origin = st.selectbox(
        "Country of Origin",
        [
            "South Korea",
            "China",
            "Japan",
            "United States",
            "India",
            "Vietnam",
            "Other"
        ]
    )

with col6:
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


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

if st.button("🔎 Analyze Shipment", use_container_width=True):

    if not product.strip():
        st.warning("Please enter a product name.")
        st.stop()

    if not description.strip():
        st.warning("Please provide a detailed product description.")
        st.stop()

    if not material.strip() and product_type in [
        "Apparel / Hoodie",
        "T-Shirt",
        "Sweatshirt"
    ]:
        st.warning(
            "For apparel classification, please provide the material "
            "or fiber composition."
        )
        st.stop()

    # -----------------------------------------------------
    # OPENAI CLIENT
    # -----------------------------------------------------

    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )


    # -----------------------------------------------------
    # CLASSIFICATION GUARDRAIL
    # -----------------------------------------------------

    system_prompt = """
You are Narae, an AI logistics decision-support assistant
specialized in K-entertainment merchandise.

Your most important responsibility is NOT to invent an HS/HTS code.

You must reason through product characteristics before suggesting
a classification.

IMPORTANT CLASSIFICATION RULES:

1. Distinguish knitted/crocheted garments from woven garments.

2. Knitted/crocheted sweaters, pullovers, sweatshirts and similar
   articles generally begin under HS heading 6110.

3. Woven garments may fall under different chapters/headings,
   including Chapter 62.

4. For cotton knitted/crocheted garments under heading 6110,
   consider the cotton branch (6110.20) before suggesting a
   more specific U.S. HTS classification.

5. Do NOT provide a precise 8- or 10-digit HTS code when the
   available product information is insufficient to support it.

6. If information is missing, explicitly say:
   "Verification Required."

7. Never fabricate tariff rates.

8. Duty estimates must be described as estimates unless the
   applicable tariff rate is actually known.

9. Separate:
   - classification reasoning
   - duty estimation
   - documentation
   - customs risk
   - entertainment/IP risk

10. A product containing an entertainment brand, artist name,
    logo, character or other intellectual property may create
    IP/licensing/counterfeit considerations. Do not claim that
    infringement exists; flag it as a risk requiring verification.

11. The United States uses the Harmonized Tariff Schedule (HTS),
    which extends the international HS system with additional
    U.S.-specific digits.

12. For a U.S. apparel classification, if the product is a
    knitted/crocheted cotton sweatshirt/hoodie, identify the
    likely heading/subheading family first. Only provide a
    specific statistical suffix if the product characteristics
    support it.

13. If the wearer is unisex/unknown and a sex-specific tariff
    suffix may be required, do not guess. Mark the final
    classification as requiring verification.

Your objective is to be useful without creating false certainty.
"""


    # -----------------------------------------------------
    # USER PROMPT
    # -----------------------------------------------------

    user_prompt = f"""
Analyze this import shipment.

PRODUCT
Product name: {product}

Detailed description:
{description}

Product type:
{product_type}

Construction:
{construction}

Primary material / composition:
{material}

Intended wearer:
{wearer}

SHIPMENT
Country of origin:
{origin}

Destination:
{country}

Shipment value:
USD {shipment_value:.2f}

Return your analysis as valid JSON with exactly these fields:

{{
  "classification": {{
    "likely_hs_heading": "",
    "likely_hts_code": "",
    "classification_status": "",
    "confidence": "",
    "reasoning": "",
    "verification_needed": [],
    "classification_warnings": []
  }},

  "duty": {{
    "status": "",
    "estimated_rate": "",
    "estimated_duty_usd": "",
    "reasoning": ""
  }},

  "documents": [],

  "customs_risks": [],

  "ip_risks": [],

  "next_steps": [],

  "summary": ""
}}

IMPORTANT:

- If you cannot confidently determine the exact HTS code,
  leave "likely_hts_code" empty.
- Use "Verification Required" for classification_status
  when appropriate.
- Never invent a tariff rate.
- Explain why the classification belongs to the suggested
  chapter/heading.
- If the product is a knitted/crocheted cotton hoodie or
  sweatshirt destined for the United States, consider
  heading 6110 and the cotton branch 6110.20.
- Do not confuse knitted apparel in Chapter 61 with woven
  apparel in Chapter 62.
"""


    # -----------------------------------------------------
    # RUN MODEL
    # -----------------------------------------------------

    with st.spinner("Analyzing shipment..."):

        try:

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0
            )

            raw_result = response.choices[0].message.content

            result = json.loads(raw_result)

        except Exception as e:

            st.error(
                "Narae could not complete the analysis."
            )

            st.exception(e)

            st.stop()


    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    st.success("✅ Analysis Complete")

    st.markdown("---")

    st.markdown("## 📋 Narae Import Analysis")


    # -----------------------------------------------------
    # CLASSIFICATION
    # -----------------------------------------------------

    classification = result.get(
        "classification",
        {}
    )

    st.markdown("### 🧾 HS / HTS Classification")

    status = classification.get(
        "classification_status",
        "Verification Required"
    )

    confidence = classification.get(
        "confidence",
        "Unknown"
    )

    col7, col8 = st.columns(2)

    with col7:
        st.metric(
            "Classification Status",
            status
        )

    with col8:
        st.metric(
            "Confidence",
            confidence
        )


    heading = classification.get(
        "likely_hs_heading",
        ""
    )

    code = classification.get(
        "likely_hts_code",
        ""
    )


    if heading:

        st.markdown(
            f"**Likely HS Heading:** `{heading}`"
        )


    if code:

        st.markdown(
            f"**Candidate HTS Code:** `{code}`"
        )

    else:

        st.warning(
            "Narae is not assigning a precise final HTS code "
            "because the available information is insufficient "
            "to support that level of precision."
        )


    reasoning = classification.get(
        "reasoning",
        ""
    )

    if reasoning:

        st.markdown("#### Why?")

        st.write(reasoning)


    warnings = classification.get(
        "classification_warnings",
        []
    )

    if warnings:

        st.markdown("#### ⚠️ Classification Warnings")

        for warning in warnings:
            st.warning(warning)


    verification = classification.get(
        "verification_needed",
        []
    )

    if verification:

        st.markdown(
            "#### 🔍 Information Needed for Verification"
        )

        for item in verification:
            st.write(f"• {item}")


    # -----------------------------------------------------
    # DUTY
    # -----------------------------------------------------

    duty = result.get(
        "duty",
        {}
    )

    st.markdown("---")
    st.markdown("### 💰 Import Duty")

    duty_status = duty.get(
        "status",
        "Estimate only"
    )

    st.write(
        f"**Status:** {duty_status}"
    )

    estimated_rate = duty.get(
        "estimated_rate",
        ""
    )

    estimated_duty = duty.get(
        "estimated_duty_usd",
        ""
    )

    if estimated_rate:
        st.write(
            f"**Estimated Rate:** {estimated_rate}"
        )

    if estimated_duty:
        st.write(
            f"**Estimated Duty:** {estimated_duty}"
        )

    duty_reasoning = duty.get(
        "reasoning",
        ""
    )

    if duty_reasoning:
        st.write(duty_reasoning)


    # -----------------------------------------------------
    # DOCUMENTS
    # -----------------------------------------------------

    documents = result.get(
        "documents",
        []
    )

    st.markdown("---")
    st.markdown("### 📄 Required Documentation")

    for document in documents:
        st.write(f"• {document}")


    # -----------------------------------------------------
    # CUSTOMS RISKS
    # -----------------------------------------------------

    customs_risks = result.get(
        "customs_risks",
        []
    )

    st.markdown("---")
    st.markdown("### ⚠️ Customs Risks")

    if customs_risks:

        for risk in customs_risks:
            st.warning(risk)

    else:

        st.write(
            "No major customs risks identified from the "
            "information provided."
        )


    # -----------------------------------------------------
    # IP RISKS
    # -----------------------------------------------------

    ip_risks = result.get(
        "ip_risks",
        []
    )

    st.markdown("---")
    st.markdown("### ™️ Entertainment / IP Risks")

    if ip_risks:

        for risk in ip_risks:
            st.warning(risk)

    else:

        st.write(
            "No significant entertainment/IP risks identified "
            "from the information provided."
        )


    # -----------------------------------------------------
    # NEXT STEPS
    # -----------------------------------------------------

    next_steps = result.get(
        "next_steps",
        []
    )

    st.markdown("---")
    st.markdown("### 🚚 Recommended Next Steps")

    for step in next_steps:
        st.write(f"• {step}")


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    summary = result.get(
        "summary",
        ""
    )

    st.markdown("---")
    st.markdown("### 🧠 Narae Logistics Summary")

    st.info(summary)


    # -----------------------------------------------------
    # DISCLAIMER
    # -----------------------------------------------------

    st.markdown("---")

    st.caption(
        "Narae is an AI-powered logistics decision-support "
        "prototype. Classification and duty information should "
        "be verified against the current applicable tariff "
        "schedule and customs authority before commercial use."
    )
