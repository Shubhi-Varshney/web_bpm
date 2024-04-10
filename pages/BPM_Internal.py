#######################
# Import libraries

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import requests

import hmac

###################
# Password login

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.markdown('<p style="text-align: center; font-size: 28px; color: #723aff;">If you are visiting from our community please go to our other page: BPM Community Dashboard</p>', unsafe_allow_html=True)

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


#################
# Internal page code



#####################
# Local
# df_reshaped = pd.read_csv('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/cleaned_data_for_ml.csv')
# df_analytics = pd.read_csv('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/data_for_analytics.csv')
# df_line = pd.read_excel('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/Community Growth.xlsx', header = 1)
# df_events = pd.read_excel('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/BPM Events list people .xlsx')

# GCS

### GCS


# https://console.cloud.google.com/storage/browser/bpm_bucket/cleaned_data_for_analysis.csv
bucket_name = 'bpm_buckt'
file_path_analytics = "cleaned_data_for_analysis.csv"
file_path_ml = "cleaned_data_for_ml.csv"
file_path_cg = "Community Growth.xlsx"
file_path_ev = "BPM Events list people .xlsx"

@st.cache_data
def load_csv(url):
    df = pd.read_csv(url)
    return df

@st.cache_data(ttl="1d")
def load_excel(url, header_num=0):
    df = pd.read_excel(url, header=header_num)
    return df


df_gcs_an = load_csv(f'gs://{bucket_name}/{file_path_analytics}')
df_gcs_ml = load_csv(f'gs://{bucket_name}/{file_path_ml}')
df_gcs_cg = load_excel(f'gs://{bucket_name}/{file_path_cg}', header_num=1)
df_gcs_ev = load_excel(f'gs://{bucket_name}/{file_path_ev}')

df_analytics = df_gcs_an
df_reshaped = df_gcs_ml
df_line = df_gcs_cg
df_events = df_gcs_ev


# Sidebar

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 200px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("# BPM Internal")


    event_list = sorted(list(df_analytics.Event.unique()))

    selected_event = st.selectbox('Select an event', event_list, index=5)

    # with.st.sidebar.beta_container()
    with st.expander('About', expanded=False):
        st.write('''
                Made with 🖤 from Berlin,\n
    Shubhi Jain, Dominic Hodal, Yulia Vilensky
                ''')

st.markdown('<p style="text-align: center; font-size: 40px; color: #4778FF;">BPM | Internal Dashboard</p>', unsafe_allow_html=True)




col = st.columns((4, 6), gap='large',)

with col[0]:

    # df_attendees = pd.DataFrame(df_reshaped["company"].value_counts().reset_index())
    col_to_drop = ['Event', 'Attendee Status',
       'Your Job Position', 'Choose your role', 'Choose your role.1',
       'Seniority', 'How did you hear from us?', 'Company', 'Rain', 'Day',
       'Location']
    
    df_email_count = pd.DataFrame(df_events["Email"].value_counts().reset_index())
    df_email_count_merged = pd.merge(df_email_count, df_events, how='left',on="Email")
    df_e = df_email_count_merged.drop(col_to_drop, axis=1).drop_duplicates(subset=['Email'])
    
    st.markdown('<span style="font-size: 30px; color: #383971;">Top 30 Attendees</span>', unsafe_allow_html=True)

    st.dataframe(df_e.iloc[:30],
                 column_order=("First Name", "count"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "First Name": st.column_config.TextColumn(
                        "Attendee",
                    ),
                    "count": st.column_config.ProgressColumn(
                        "Events attended",
                        format="%f",
                        min_value=0,
                        max_value=max(df_e["count"]),
                     )}
                 )


with col[0]:
    st.markdown('<span style="font-size: 30px; color: #383971;">Referral Breakdown</span>', unsafe_allow_html=True)

    mask = df_analytics["Event"] == selected_event
    df_analytics_masked = df_analytics[mask]
    df_job_position = pd.DataFrame(df_analytics_masked['How did you hear from us?'].value_counts().reset_index())
    
    pie_colors =  ["#81D3C1", "#717c89","#8aa2a9","#90baad","#a1e5ab","#adf6b1", "#C1F9C4"]
    
    fig_pie = px.pie(df_job_position.iloc[:7], values='count', names='How did you hear from us?', ) # 
    fig_pie.update_layout(showlegend=True, )
    fig_pie.update_traces(hoverinfo='label+percent',
                  marker=dict(colors=pie_colors, ))
  
    st.plotly_chart(fig_pie, use_container_width=True,sharing="streamlit", )







with col[1]:
    st.markdown('<span style="font-size: 30px; color: #4778FF;">Registration Flow</span>', unsafe_allow_html=True)
     
    event_mask = df_analytics["Event"] == selected_event
    df_event_masked = df_analytics[event_mask]
    df_event_status = df_event_masked["Attendee Status"].value_counts()
    attended  = df_event_status["Checked In"]
    no_show  = df_event_status["Attending"]
    cancelled = df_event_status["Not Attending"]
    registered = attended + no_show + cancelled
    # Overbooking ticket capacity
    event_ticket_opened = df_line['Ticket opened'].iloc[selected_event + 1]
    # Registered for event
    san_registered = registered
    # Got event ticket
    san_ticketed = event_ticket_opened
    # On event wait-list
    san_wait_list = san_registered - san_ticketed
    # Cancelled event ticket before event
    cancelled = cancelled
    # Had event ticket on day of event
    confirmed = attended + no_show
    # Actually attended the event
    admitted = attended
    # Didn't attend but had a ticket
    no_show = confirmed - admitted
    
    label = ["Registered", "Ticket", "Wait list", "Confirmed", "Cancelled", "Admitted", "No show"]
    source = [0, 0, 1, 1, 2, 3, 3]
    target = [1, 2, 3, 4, 3, 5, 6]
    value = [san_registered, event_ticket_opened, san_wait_list, confirmed, cancelled, admitted, no_show]

    
    color_san = ["#00487c","#4bb3fd","#3e6680","#0496ff", "#F82274", "#00FFE1", "#225DFF",]
    
   # colors from pie chart -  ["#81D3C1", "#717c89","#8aa2a9","#90baad","#a1e5ab","#adf6b1", "#C1F9C4"] 
    
    link= dict(source = source, target = target, value = value, color="#90baad")
    node = dict(label = label, pad = 35, thickness = 10, color=color_san)
    data = go.Sankey(link = link, node = node)

    fig_san = go.Figure(data)
    fig_san.update_layout(
    hovermode = "x",
    title = "Event ticket breakdown",
)

    st.plotly_chart(fig_san, use_container_width=True, sharing="streamlit",)





###### ~Predictive elements from lewagon DS project~ #################

## Function to call predict API
 ## Update URL as needed ##
  ## local:   "http://127.0.0.1:8000/predict"
  ## docker:  "https://databpm-y72gx2bd7a-ew.a.run.app/predict"

# @st.cache_resource
# def call_predict_api(payload):
#     url = "https://databpm-dev-14-y72gx2bd7a-ew.a.run.app/predict"
#     response = requests.post(url, files={"File": payload})
#     if response.status_code == 200:
#         return response.json()
#     else:
#         st.error(f"Prediction failed with status code {response.status_code}")
#         return None

# def call_fbf_api(payload):
#     url_2 = "https://databpm-dev-14-y72gx2bd7a-ew.a.run.app/get_similar_users"
#     response_2 = requests.post(url_2, files={"File": payload})
#     if response_2.status_code == 200:
#         return response_2.json()
#     else:
#         st.error(f"Prediction failed with status code {response_2.status_code}")
#         return None

# ## List to check if csv is correct shape and data
# col_names = ['headline','description', 'jobTitle' ,'jobDescription','jobDuration', 'jobDateRange', 'jobTitle2', 'jobDuration2', 'schoolDateRange', 'skill1', 'skill2', 'skill3']

# ## Loop variables
# pred_button = False
# col_check = False

# # Streamlit columning
# col_title = st.columns((1.8, 4.4, 1.8), gap="medium")


# with col_title[1]:
#     st.markdown('<span style="text-align: center; font-size: 35px; color: #519FFF;">Upload LinkedIn data here:</span>', unsafe_allow_html=True)
    
#     uploaded_file = st.file_uploader("CSV file", type=["csv"])
    
    
#     if uploaded_file is not None:
        
#         df = pd.read_csv(uploaded_file)
        
#         for col in col_names:
#             if col not in df.columns:
#                 st.markdown('<p style="text-align: center; font-size: 25px; color: #d8313a;">Please upload a csv file scraped from LinkedIn</p>', unsafe_allow_html=True)
#                 col_check =True
#                 break
            
#         if col_check == False:
#             df_col = df[col_names]
#             st.markdown(f"Number of entries in csv: {df_col.shape[0]}")
#             if df_col.shape != (1, 12):
#                 st.markdown('<p style="text-align: center; font-size: 25px; color: #d8313a;">Please upload a csv file with a single entry</p>', unsafe_allow_html=True)

#             if df_col.shape == (1, 12):
#                 pred_button = True
#                 df_byte = df_col.to_json().encode()
#                 # st.write(df)
                
#         if pred_button == True:
#             if st.button("Predict"):
#                 if uploaded_file is None:
#                     st.markdown('<p style="text-align: center; font-size: 30px; color: #d8313a;">Please upload a csv file first</p>', unsafe_allow_html=True)
                    
#                 if uploaded_file is not None:
#                     prediction = call_predict_api(df_byte)
#                     pred_per = round((prediction["probability_to_attend"] * 100), 1)
#                     st.markdown(f'''### :green[This person is {pred_per}% likely to attend a BPM event]:sunflower:''')

#         if pred_button == True:
#             if st.button("Future Best Buddy"):
#                 if uploaded_file is None:
#                     st.markdown('<p style="text-align: center; font-size: 30px; color: #d8313a;">Please upload a csv file first</p>', unsafe_allow_html=True)
                
#                 if uploaded_file is not None:
#                     fbf_prediction = call_fbf_api(df_byte)
#                     pred_fbf = pd.read_json(fbf_prediction)
#                     pred_fbf.index.name = "User_ID"
#                     st.write(pred_fbf)
