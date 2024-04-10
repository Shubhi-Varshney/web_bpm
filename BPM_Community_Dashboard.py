#######################
import streamlit as st
# import streamlit_extras.bottom as ste
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
# import gcsfs


#######################
# Page configuration
st.set_page_config(
    page_title="BPM Community Breakdown",
    # page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data

### Local
df_reshaped = pd.read_csv('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/cleaned_data_for_ml.csv')
df_analytics = pd.read_csv('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/data_for_analytics.csv')
df_line = pd.read_excel('/home/dhodal/code/Shubhi-Varshney/data-bpm/raw_data/Community Growth.xlsx', header = 1)

### GCS
# Shubi updated file names: "cleaned_data_for_analysis.csv"
# "cleaned_data_for_ml.csv"

# https://console.cloud.google.com/storage/browser/bpm_bucket/cleaned_data_for_analysis.csv
bucket_name = 'bpm_buckt'
file_path_analytics = "cleaned_data_for_analysis.csv"
file_path_ml = "cleaned_data_for_ml.csv"
file_path_cg = "Community Growth.xlsx"


@st.cache_data
def load_csv(url):
    df = pd.read_csv(url)
    return df

@st.cache_data(ttl="1d")
def load_excel(url, header_num=0):
    df = pd.read_excel(url, header=header_num)
    return df


# df_gcs_an = load_csv(f'gs://{bucket_name}/{file_path_analytics}')
# df_gcs_ml = load_csv(f'gs://{bucket_name}/{file_path_ml}')
# df_gcs_cg = load_excel(f'gs://{bucket_name}/{file_path_cg}', header_num=1)


# df_analytics = df_gcs_an
# df_reshaped = df_gcs_ml
# df_line = df_gcs_cg


#######################
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
    st.markdown("# BPM Community Dashboard")





    event_list = sorted(list(df_analytics.Event.unique()))

    selected_event = st.selectbox('Select an event', event_list, index=5)

    # with.st.sidebar.beta_container()
    with st.expander('About', expanded=False):
        st.write('''
                Made with 🖤 from Berlin,\n
    Shubhi Jain, Dominic Hodal, Yulia Vilensky
                ''')


# (https://www.linkedin.com/in/email-shubhi-jain/)
# (https://www.linkedin.com/in/yulia-vilensky/)

# Contents of ~/my_app/main_page.py

col_title = st.columns((1 ,6), gap="small")
with col_title[1]:
    st.markdown('<span style="text-align: center; font-size: 40px; color: #000F40;">Berlin Product Managers |  Community Dashboard</span>', unsafe_allow_html=True)
    



# event_name = df_line['Event Name'].iloc[selected_event]


#######################
# Dashboard Main Panel
col = st.columns((3, 4, 2.5), gap='medium',)

with col[0]:
    st.markdown('<span style="font-size: 30px; color: #383971;">Event Attendance</span>', unsafe_allow_html=True)
     #st.markdown("<h1 style='text-align: center; color: red;'>Some title</h1>", unsafe_allow_html=True)


    event_mask = df_analytics["Event"] == selected_event
    df_event_masked = df_analytics[event_mask]
    df_event_status = df_event_masked["Attendee Status"].value_counts()
   # attended  = df_event_status["Attending"]
    attended = df_event_status["Checked In"]
    venue_size = int(df_line['Venue size'].iloc[selected_event])

    at_percent_ = (attended / venue_size)*100
    at_percent = round(at_percent_, 1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Participants", f"{attended}")
    col2.metric("Venue Capacity", f"{venue_size}")
    col3.metric("Attandance Rate", f"{at_percent}%")


with col[2]:
    st.markdown('<span style="font-size: 30px; color: #383971;">Participant Breakdown</span>', unsafe_allow_html=True)

    mask = df_analytics["Event"] == selected_event
    df_analytics_masked = df_analytics[mask]
    df_job_position = pd.DataFrame(df_analytics_masked["Your Job Position"].value_counts().reset_index())
    
    pie_colors =  ["#81D3C1", "#717c89","#8aa2a9","#90baad","#a1e5ab","#adf6b1", "#C1F9C4"]
    
    fig_pie = px.pie(df_job_position, values='count', names='Your Job Position', ) # 
    fig_pie.update_layout(showlegend=True, title= dict(text =str("Role"), font =dict(family="source sans pro", size=20, color = '#383971')))
    fig_pie.update_traces(hoverinfo='label+percent',
                  marker=dict(colors=pie_colors, ))

    st.plotly_chart(fig_pie, use_container_width=True,sharing="streamlit", )


    pod_mask = df_analytics_masked["Your Job Position"] == "Product"
    df_analytics_masked["Your Job Position"] = df_analytics_masked["Your Job Position"].fillna("Not given")
    df_seniority = df_analytics_masked[pod_mask]
    df_seniority["Choose your role"].value_counts()
    df_pod_list = pd.DataFrame(df_seniority["Choose your role"].value_counts().reset_index())


   #  st.markdown('<span style="font-size: 30px; color: #383971;">Seniority Breakdown</span>', unsafe_allow_html=True)
    
    pie_colors_2 =   ["#00C895","#39DEB6","#00B5B5", "#008AAB","#005F92",] # ["#005F92","#008AAB","#00B5B5", "#39DEB6","#00C895",]
    
    fig_pie_2 = px.pie(df_pod_list.iloc[:5], values='count', names='Choose your role', ) # 
    fig_pie_2.update_layout(showlegend=True, title= dict(text =str("Seniority"), font =dict(family="source sans pro", size=20, color = '#383971')))
    fig_pie_2.update_traces(hoverinfo='label+percent',
                  marker=dict(colors=pie_colors_2, ))
  
    st.plotly_chart(fig_pie_2, use_container_width=True,sharing="streamlit", )




with col[1]:
    st.markdown('<span style="font-size: 30px; color: #4778FF;">Social Media Growth</span>', unsafe_allow_html=True)


    df_line['Newsletter'] = df_line['Newsletter'].fillna(0)
    df_line['Socials'] = pd.to_datetime(df_line['Socials'], format='%d%b%Y:%H:%M:%S.%f')
    df_line['month'] = pd.DatetimeIndex(df_line['Socials']).month
    month_num = int(df_line['month'].iloc[(selected_event+ 1)])
    
    months = ["August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July" ]
    

    list_l = list(df_line['LinkedIn'].iloc[:(selected_event+ 1)])
    list_2 = list(df_line['Newsletter'].iloc[:(selected_event+ 1)])
    list_3 = list(df_line['Instagram'].iloc[:(selected_event+ 1)])
    list_4 = months[:(selected_event + 1)]
  
    
    dict_growth = {
        "LinkedIn": list_l,
        "Mailing list": list_2,
        "Instagram": list_3,
        "Month": list_4
    }
    df_com_growth = pd.DataFrame(dict_growth)
    
    fig_line = go.Figure(data=go.Scatter(x=df_com_growth["Month"], y=df_com_growth["LinkedIn"], name="LinkedInS", line_color="#0A66C2",))
    fig_line.add_scatter(x=df_com_growth["Month"], y=df_com_growth["Mailing list"], name="Newsletter", line_color="#F76519")
    fig_line.add_scatter(x=df_com_growth["Month"], y=df_com_growth["Instagram"], name="Instagram", line_color="#E1306C")

# Update layout to change x-axis labels
    fig_line.update_layout(xaxis=dict(
        tickvals=[0, 1, 2, 3, 4, 5, 6, 7],  # Positions of the ticks on the axis
        ticktext=months  # Labels for the ticks
))

    st.plotly_chart(fig_line, use_container_width=True,)
    


# with col[1]:
    
#     #Sankey graph
#     st.markdown('<span style="font-size: 30px; color: #4778FF;">Registration Flow</span>', unsafe_allow_html=True)
     

#     df_event_status = df_event_masked["Attendee Status"].value_counts()
#     attended  = df_event_status["Checked In"]
#     no_show  = df_event_status["Attending"]
#     cancelled = df_event_status["Not Attending"]
#     registered = attended + no_show + cancelled
#     # Overbooking ticket capacity
#     event_ticket_opened = df_line['Ticket opened'].iloc[selected_event + 1]
#     # Registered for event
#     san_registered = registered
#     # Got event ticket
#     san_ticketed = event_ticket_opened
#     # On event wait-list
#     san_wait_list = san_registered - san_ticketed
#     # Cancelled event ticket before event
#     cancelled = cancelled
#     # Had event ticket on day of event
#     confirmed = attended + no_show
#     # Actually attended the event
#     admitted = attended
#     # Didn't attend but had a ticket
#     no_show = confirmed - admitted
    
#     label = ["Registered", "Ticket", "Wait list", "Confirmed", "Cancelled", "Admitted", "No show"]
#     source = [0, 0, 1, 1, 2, 3, 3]
#     target = [1, 2, 3, 4, 3, 5, 6]
#     value = [san_registered, event_ticket_opened, san_wait_list, confirmed, cancelled, admitted, no_show]

    
#     color_san = ["#00487c","#4bb3fd","#3e6680","#0496ff", "#F82274", "#00FFE1", "#225DFF",]
    
#    # colors from pie chart -  ["#81D3C1", "#717c89","#8aa2a9","#90baad","#a1e5ab","#adf6b1", "#C1F9C4"] 
    
#     link= dict(source = source, target = target, value = value, color="#90baad")
#     node = dict(label = label, pad = 35, thickness = 10, color=color_san)
#     data = go.Sankey(link = link, node = node)

#     fig_san = go.Figure(data)
#     fig_san.update_layout(
#     hovermode = "x",
#     title = "Event ticket breakdown",
# )

#     st.plotly_chart(fig_san, use_container_width=True, sharing="streamlit",)




with col[0]:
    df_attendees = pd.DataFrame(df_reshaped["company"].value_counts().reset_index())
    st.markdown('<span style="font-size: 30px; color: #383971;">Top 10 Companies</span>', unsafe_allow_html=True)

    st.dataframe(df_attendees.iloc[:10],
                 column_order=("company", "count"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "company": st.column_config.TextColumn(
                        "Companies",
                    ),
                    "count": st.column_config.ProgressColumn(
                        "Attendees",
                        format="%f",
                        min_value=0,
                        max_value=max(df_attendees["count"]),
                     )}
                 )
