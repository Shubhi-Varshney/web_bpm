#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import requests

COLUMN_NAMES_RAW = [ 'headline','description', 'jobTitle' ,'jobDescription','jobDuration', 'jobDateRange', 'jobTitle2', 'jobDuration2', 'schoolDateRange', 'skill1', 'skill2', 'skill3']


st.markdown("# Prediction")
st.sidebar.markdown("# Prediction")

app.state.model = load_model()

# Function to call predict API
def call_predict_api(payload):
    url = "http://localhost:8000/predict"  # Update URL as needed
    response = requests.post(url, files={"File": payload})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Prediction failed with status code {response.status_code}")
        return None



    


st.header("Make Prediction")


st.header("Upload CSV file")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df_byte = df.to_json().encode()
    st.write(df)

if st.button("Predict"):
    prediction = call_predict_api(df_byte)


        # # Check if required columns are present
        # if set(COLUMN_NAMES_RAW).issubset(df.columns):
        #     # Display uploaded data
        #     st.write("Uploaded Data:")
        #     st.write(df)

        #     # Predict button
        #     if st.button("Yes"):
        #         # Call predict API for each row
        #         st.write("Predictions:")
        #         for _, row in df.iterrows():
        #             payload = row[COLUMN_NAMES_RAW].to_dict()
        #             prediction = call_predict_api(payload)
        #             if prediction is not None:
        #                 pred = prediction
        # else:
        #     st.error("CSV file does not contain all required columns.")
    


        # y_pred_proba = app.state.model.predict_proba(X_processed)
        # # Assuming y_pred_proba is a single probability value for positive class
        # positive_probability = float(y_pred_proba[0, 1])
        # return {'probability_to_attend': positive_probability}


# ml_data = pd.read_csv('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/ml_data_clusters.csv')

# fig_scatter = px.scatter_3d(ml_data,
#                     x = 'jobTitle',
#                     y = 'jobTitle2',
#                     z = 'jobDuration',
#                     opacity=0.7, width=500, height=500,
#                     color='dbscan_cluster',
#            )

# st.plotly_chart(fig_scatter, use_container_width=True, )