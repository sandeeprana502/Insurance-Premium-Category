import streamlit as st
import requests
import pandas

API_URL = "http://localhost:8000/predict" 

st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below:")

# Input fields
age = st.number_input("Age", min_value=1, max_value=119, value=30)
weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)
smoker = st.selectbox("Are you a smoker?", options=[True, False])
city = st.text_input("City", value="Mumbai")
occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job']
)

if st.button("Predict Premium Category"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data)
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content: {response.text}")
        result = response.json()
        # st.write(result)

        if response.status_code == 200:
            prediction = result['predicted_category']
            st.success(f"Predicted Insurance Premium Category: **{prediction}**")
            st.write("🔍 Confidence:", result["confidence"])
            st.write("📊 Class Probabilities:")
            # st.write(result["class_probabilities"])
            # st.write(pandas.DataFrame(result["class_probabilities"], columns=["Low"]))
            prob_df = pandas.DataFrame.from_dict(
            result["class_probabilities"], 
            orient='index', 
            columns=['Probability']
            )
            st.write(prob_df)

        else:
            st.error(f"API Error: {response.status_code}")
            st.write(result)

    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the FastAPI server. Make sure it's running.")