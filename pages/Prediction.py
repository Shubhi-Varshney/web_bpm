#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import requests

# def load_custom_css(file_path):
#     with open(file_path) as f:
#         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# load_custom_css('css_styles/style.css')

# st.write('<div id="cubed_2">hi again</div>', unsafe_allow_html=True)



col_names = ['headline','description', 'jobTitle' ,'jobDescription','jobDuration', 'jobDateRange', 'jobTitle2', 'jobDuration2', 'schoolDateRange', 'skill1', 'skill2', 'skill3']

pred_button = False
col_check = False
# st.markdown("# Prediction")
st.sidebar.markdown("# Prediction")
st.markdown('<p style="text-align: center; font-size: 40px; color: #4778FF;">Predict if someone will attend a BPM event, and suggest 10 people to network with</p>', unsafe_allow_html=True)


# Function to call predict API
 ## Update URL as needed ##
  ## local:   "http://127.0.0.1:8000/predict"
  ## docker:  "https://databpm-y72gx2bd7a-ew.a.run.app/predict"

@st.cache_resource
def call_predict_api(payload):
    # url =  "https://databpm-dev-13-y72gx2bd7a-ew.a.run.app/predict"
    # url =  "http://127.0.0.1:8000/predict" #"https://databpm-dev-14-y72gx2bd7a-ew.a.run.app/get_similar_users" #
    url = "https://databpm-dev-14-y72gx2bd7a-ew.a.run.app/predict"
    response = requests.post(url, files={"File": payload})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Prediction failed with status code {response.status_code}")
        return None

def call_fbf_api(payload):
    # url_2 = "http://127.0.0.1:8000/get_similar_users"
    # url =  "https://databpm-dev-13-y72gx2bd7a-ew.a.run.app/get_similar_users" ## <-- Change ME
    url_2 = "https://databpm-dev-14-y72gx2bd7a-ew.a.run.app/get_similar_users"
    response_2 = requests.post(url_2, files={"File": payload})
    if response_2.status_code == 200:
        return response_2.json()
    else:
        st.error(f"Prediction failed with status code {response_2.status_code}")
        return None


col_title = st.columns((1.8, 4.4, 1.8), gap="medium")


with col_title[1]:
    st.markdown('<span style="text-align: center; font-size: 35px; color: #519FFF;">Upload LinkedIn data here:</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        for col in col_names:
            if col not in df.columns:
                st.markdown('<p style="text-align: center; font-size: 25px; color: #d8313a;">Please upload a csv file scraped from LinkedIn</p>', unsafe_allow_html=True)
                col_check =True
                break
        if col_check == False:
            df_col = df[col_names]
            st.markdown(f"Number of entries in csv: {df_col.shape[0]}")
            if df_col.shape != (1, 12):
                st.markdown('<p style="text-align: center; font-size: 25px; color: #d8313a;">Please upload a csv file with a single entry</p>', unsafe_allow_html=True)

            if df_col.shape == (1, 12):
                pred_button = True
                df_byte = df_col.to_json().encode()
                # st.write(df)
        if pred_button == True:
            if st.button("Predict"):
                if uploaded_file is None:
                    st.markdown('<p style="text-align: center; font-size: 30px; color: #d8313a;">Please upload a csv file first</p>', unsafe_allow_html=True)
                if uploaded_file is not None:
                    prediction = call_predict_api(df_byte)
                    pred_per = round((prediction["probability_to_attend"] * 100), 1)
                    st.markdown(f'''### :green[This person is {pred_per}% likely to attend a BPM event]:sunflower:''')

        if pred_button == True:
            if st.button("Future Best Buddy"):
                if uploaded_file is None:
                    st.markdown('<p style="text-align: center; font-size: 30px; color: #d8313a;">Please upload a csv file first</p>', unsafe_allow_html=True)
                if uploaded_file is not None:
                    fbf_prediction = call_fbf_api(df_byte)
                    pred_fbf = pd.read_json(fbf_prediction)
                    pred_fbf.index.name = "User_ID"
                    st.write(pred_fbf)

