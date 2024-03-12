#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import requests

COLUMN_NAMES_RAW = [ 'headline','description', 'jobTitle' ,'jobDescription','jobDuration', 'jobDateRange', 'jobTitle2', 'jobDuration2', 'schoolDateRange', 'skill1', 'skill2', 'skill3']

pred_button = False

# st.markdown("# Prediction")
st.sidebar.markdown("# Prediction")
st.markdown('<p style="text-align: center; font-size: 60px; color: #F171A2;">Predict if someone will attend a BPM event!</p>', unsafe_allow_html=True)


# Function to call predict API
 ## Update URL as needed ##
  ## local:   "http://127.0.0.1:8000/predict" 
  ## docker:  "https://databpm-y72gx2bd7a-ew.a.run.app/predict"  
@st.cache_resource
def call_predict_api(payload):
    url =  "http://127.0.0.1:8000/predict" 
    response = requests.post(url, files={"File": payload})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Prediction failed with status code {response.status_code}")
        return None


col_title = st.columns((2, 4, 2), gap="medium")

with col_title[1]: 
    st.markdown('<span style="text-align: center; font-size: 35px; color: #519FFF;">Upload scrapped LinkedIn data here:</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df_col = df[COLUMN_NAMES_RAW]
        st.markdown(f"{df_col.shape}")
        if df_col.shape != (1, 12):
            st.markdown('<p style="text-align: center; font-size: 25px; color: #d8313a;">Please upload a csv file with a single entry</p>', unsafe_allow_html=True)
            
        if df_col.shape == (1, 12):
            pred_button = True
            df_byte = df_col.to_json().encode()
            st.write(df)
    if pred_button == True:   
        if st.button("Predict"):
            if uploaded_file is None:
                st.markdown('<p style="text-align: center; font-size: 30px; color: #d8313a;">Please upload a csv file first</p>', unsafe_allow_html=True)
            if uploaded_file is not None:
                prediction = call_predict_api(df_byte)
                pred_per = round((prediction["probability_to_attend"] * 100), 1)
                st.markdown(f'''### :green[You are {pred_per}% likely to attend a BPM event]:sunflower:''')


