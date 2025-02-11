import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from millify import millify
from datetime import datetime


# Centralized Streamlit Configuration and Introduction
logo_url = "Images/LCY3 Logo.png"
logo_url_2 = "Images/Amazon RME Logo.png"
st.set_page_config(page_title="Tote Analysis", page_icon=logo_url, layout="wide")
cols1, cols2,cols3 = st.columns([1,4,5],vertical_alignment="center",gap= 'small')  # This creates a 10% and 80% split
with cols1:
    st.image(logo_url, width=300)
with cols2:
    # Vertically center title
    title_html = """
    <div style="justify-content:bottom; align-items:center;">
        <h1 style='font-size: 60px; margin-left: 10%;'>
            <span style='color: #6CB4EE;'>Amazon LCY3</span> 
            <span style='color: #1D2951;'>Tote Analysis Dashboard</span>
        </h1>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
with cols3:
    st.image(logo_url_2,width=300)

# Load the data into a DataFrame
data = pd.read_csv("data_transformed.csv")

df = pd.DataFrame(data)
# print(df.head(50))
# Specify the format of the Timestamp column
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S")

# Calculate additional metrics
df["Percentage of Bad Totes"] = (df["Bad Totes"] / df["Total Totes"]) * 100
df["Percentage of Good Totes"] = (
    df["Actual Good Totes"] / df["Actual Total Totes"]
) * 100
df["Cumulative Total Totes"] = df["Total Totes"].cumsum()
df["Cumulative Bad Totes"] = df["Bad Totes"].cumsum()
df["Cumulative Actual Total Totes"] = df["Actual Total Totes"].cumsum()
df["Cumulative Actual Bad Totes"] = df["Actual Bad Totes"].cumsum()
df["Cumulative Actual Good Totes"] = df["Actual Good Totes"].cumsum()
df["Average Total Totes"] = df["Total Totes"].expanding().mean()
df["Average Bad Totes"] = df["Bad Totes"].expanding().mean()
df["Average Actual Total Totes"] = df["Actual Total Totes"].expanding().mean()
df["Average Actual Bad Totes"] = df["Actual Bad Totes"].expanding().mean()
df["Average Actual Good Totes"] = df["Actual Good Totes"].expanding().mean()
df["Cumulative Good Totes"] = df["Cumulative Total Totes"] - df["Cumulative Bad Totes"]


df["Date"] = df["Timestamp"].dt.date  # Extract date for filtering
df["Hour"] = df["Timestamp"].dt.hour  # Extract hour for x-axis
# # Create an empty container for the progress bar
# progress_container = st.empty()


# # Select the metric to display
# metric = st.selectbox("Select Metric", df.columns[1:])

# # Plot the selected metric
# st.line_chart(df.set_index("Timestamp")[metric])

# # Display the data
# st.write("Data Summary:")
# st.dataframe(df)

# Calculate the total good totes and bad totes
total_good_totes = df["Actual Good Totes"].sum()
total_bad_totes = df["Actual Bad Totes"].sum()
total_totes = df["Actual Total Totes"].sum()

# Create a DataFrame for the pie chart
pie_data = pd.DataFrame(
    {
        "Tote Type": ["Good Totes", "Bad Totes"],
        "Count": [total_good_totes, total_bad_totes],
    }
)

# Create an interactive pie chart
fig = px.pie(
    pie_data,
    values="Count",
    names="Tote Type",
    title="Good Totes vs Bad Totes",
    color_discrete_sequence=["#4CAF50", "#FF5722"],
    hole=0.8,
    labels={"Count": "Total Count", "Tote Type": "Type of Tote"},
)

utilization = ((total_totes - total_bad_totes) / total_totes) * 100
# Determine progress bar color based on utilization value
if utilization < 85:
    color = "red"
else:
    color = "green"

# # Display the utilization percentage
# st.metric(label="Warehouse Utilization", value=f"{utilization:.2f}%")

# Create a gauge chart
fig_1 = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=utilization,
        title={"text": "Tote Compliance Score"},
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [{"range": [0, 100], "color": "lightgray"}],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": utilization,
            },
        },
    )
)
delta = 100 - utilization

# Extract date from timestamp
df["Date"] = df["Timestamp"].dt.date

# Aggregate Actuals per day
daily_actuals = df.groupby("Date")[
    ["Actual Total Totes", "Actual Bad Totes", "Actual Good Totes"]
].sum()

# Create Plotly figure
fig_3 = go.Figure()

# Add traces for each metric
fig_3.add_trace(
    go.Scatter(
        x=daily_actuals.index,
        y=daily_actuals["Actual Total Totes"],
        name="Actual Total Totes",
        mode="lines+markers",
        marker_color="blue",
        visible="legendonly",  # Hides initially
    )
)

fig_3.add_trace(
    go.Scatter(
        x=daily_actuals.index,
        y=daily_actuals["Actual Bad Totes"],
        name="Actual Bad Totes",
        mode="lines+markers",
        marker_color="red",
    )
)

fig_3.add_trace(
    go.Scatter(
        x=daily_actuals.index,
        y=daily_actuals["Actual Good Totes"],
        mode="lines+markers",
        name="Actual Good Totes",
        marker_color="green",
        visible="legendonly",  # Hides initially
    )
)

# Update layout
fig_3.update_layout(
    xaxis_title="Date",
    yaxis_title="Totes Count",
    legend=dict(
        title="Metrics",
        orientation="h",
        x=0.5,
        xanchor="center",
        y=-0.5,
        yanchor="bottom",
    ),
    template="plotly_white",
)


column1, column2 = st.columns(2, gap="large", border=True)
with column1:
    st.header("Overall Processed Totes")
    (
        card_1,
        card_2,
        card_3,
    ) = st.columns(3, gap="large", border=True, vertical_alignment="center")
    with card_1:
        st.metric(
            label="Total Totes Processed", value=millify(total_totes, precision=2)
        )
        # st.line_chart(df.set_index("Timestamp")["Cumulative Total Totes"])

    with card_2:
        st.metric(label="Total Good Totes", value=millify(total_good_totes, 2))
        # st.bar_chart(df.set_index("Timestamp")["Cumulative Bad Totes"])

    with card_3:
        st.metric(
            label="Total Bad Totes",
            value=millify(total_bad_totes, 2),
            delta=f"{-delta:.0f}%",
        )
        # st.line_chart(df.set_index("Timestamp")["Cumulative Good Totes"])

with column2:
    # Initialize session state for date and time selectors
    if "start_date" not in st.session_state:
        st.session_state["start_date"] = datetime.now().date()
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.now().time()
    if "end_date" not in st.session_state:
        st.session_state["end_date"] = datetime.now().date()
    if "end_time" not in st.session_state:
        st.session_state["end_time"] = datetime.now().time()

    # Layout for start date/time and end date/time selectors in a single row
    start_col, end_col = st.columns(2)

    with start_col:
        st.session_state["start_date"] = st.date_input(
            "Start Date", value=st.session_state["start_date"]
        )
        st.session_state["start_time"] = st.time_input(
            "Start Time", value=st.session_state["start_time"]
        )

    with end_col:
        st.session_state["end_date"] = st.date_input(
            "End Date", value=st.session_state["end_date"]
        )
        st.session_state["end_time"] = st.time_input(
            "End Time", value=st.session_state["end_time"]
        )

    # Combine start and end date/time into single datetime objects
    start_datetime = datetime.combine(
        st.session_state["start_date"], st.session_state["start_time"]
    )
    end_datetime = datetime.combine(
        st.session_state["end_date"], st.session_state["end_time"]
    )

    # Filter data based on selected date and time range
    filtered_df = df[
        (df["Timestamp"] >= start_datetime) & (df["Timestamp"] <= end_datetime)
    ]

    # If no data is available for the selected date and time range, use default values
    if filtered_df.empty:
        total_totes = 0
        total_good_totes = 0
        total_bad_totes = 0
    else:
        total_totes = filtered_df["Actual Total Totes"].sum()
        total_good_totes = filtered_df["Actual Good Totes"].sum()
        total_bad_totes = filtered_df["Actual Bad Totes"].sum()

    # Display the filtered metrics
    card_1, card_2, card_3 = st.columns(3, gap="large")
    with card_1:
        st.metric(
            label="Total Totes Processed", value=millify(total_totes, precision=2)
        )

    with card_2:
        st.metric(label="Total Good Totes", value=millify(total_good_totes, 2))

    with card_3:
        st.metric(label="Total Bad Totes", value=millify(total_bad_totes, 2))

# Create three columns with custom widths
col_1, col_2, col_3 = st.columns([1.5, 1.5, 7], gap="large")
with col_1:
    st.plotly_chart(fig)
with col_2:
    # Display the gauge chart in Streamlit
    st.plotly_chart(fig_1)
with col_3:
    st.subheader("Total totes processed during the week")
    st.line_chart(df.set_index("Timestamp")["Actual Total Totes"])




# **Available Dates & Default Selection**
available_dates = df["Date"].unique()

if "selected_date" not in st.session_state:
    st.session_state.selected_date = available_dates[-1]  # Default to latest date

# **Sidebar Date Selection (Maintains Focus & Prevents Reload)**
col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_date = st.selectbox(
        "Select a Date",
        available_dates,
        index=len(available_dates) - 1,
        key="selected_date",
    )

# **Filter Data for Selected Date**
filtered_df = df[df["Date"] == selected_date]
st.subheader(f"Hour over Hour Analysis for {selected_date}")
# **Create Plotly Figure**
fig_4 = go.Figure()

# Total Totes (Hidden by default)
fig_4.add_trace(
    go.Scatter(
        x=filtered_df["Hour"],
        y=filtered_df["Actual Total Totes"],
        mode="lines+markers",
        name="Actual Total Totes",
        line=dict(color="blue", width=2),
        visible="legendonly",  # Hide by default
    )
)

# Bad Totes (Default visible)
fig_4.add_trace(
    go.Scatter(
        x=filtered_df["Hour"],
        y=filtered_df["Actual Bad Totes"],
        mode="lines+markers",
        name="Actual Bad Totes",
        line=dict(color="red", width=2),
        marker=dict(size=8),
    )
)

# Good Totes (Hidden by default)
fig_4.add_trace(
    go.Scatter(
        x=filtered_df["Hour"],
        y=filtered_df["Actual Good Totes"],
        mode="lines+markers",
        name="Actual Good Totes",
        line=dict(color="green", width=2),
        visible="legendonly",  # Hide by default
    )
)

# **Add Animation Frames**
frames = [
    go.Frame(
        data=[
            go.Scatter(
                x=filtered_df["Hour"][:i],
                y=filtered_df["Actual Bad Totes"][:i],
                mode="lines+markers",
                line=dict(color="red"),
                marker=dict(color="red"),
            ),
            go.Scatter(
                x=filtered_df["Hour"][:i],
                y=filtered_df["Actual Total Totes"][:i],
                mode="lines+markers",
                line=dict(color="blue"),
                marker=dict(color="blue"),
            ),
            go.Scatter(
                x=filtered_df["Hour"][:i],
                y=filtered_df["Actual Good Totes"][:i],
                mode="lines+markers",
                line=dict(color="green"),
                marker=dict(color="green"),
            ),
        ],
        name=f"frame{i}",
    )
    for i in range(1, len(filtered_df) + 1)
]

fig_4.update(frames=frames)

# **Prevent Zoom Reset on Date Change**
fig_4.update_layout(
    xaxis_title="Hour",
    yaxis_title="Totes",
    uirevision="static",  # 🔥 Maintains zoom & pan state when changing dates
    # updatemenus=[{
    #     "buttons": [
    #         {
    #             "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
    #             "label": "Play",
    #             "method": "animate"
    #         },
    #         {
    #             "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
    #             "label": "Pause",
    #             "method": "animate"
    #         }
    #     ],
    #     "direction": "left",
    #     "pad": {"r": 10, "t": 87},
    #     "showactive": False,
    #     "type": "buttons",
    #     "x": 0.1,
    #     "xanchor": "right",
    #     "y": 0,
    #     "yanchor": "top"
    # }],
    legend=dict(
        title="Category",
        orientation="h",
        x=0.5,
        xanchor="center",
        y=-0.5,
        yanchor="bottom",
    ),
)

# **Show Graph in Streamlit**
st.plotly_chart(fig_4)

st.subheader("Day over Day Analysis for selected time period")
# Add a note to inform users about clicking the legend
st.info("**Note: Click on the legend items to toggle their visibility on the chart.**")
col_1, col_2 = st.columns(2)
with col_1:

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        start_date_1 = st.date_input("Start Date", df["Timestamp"].min().date(), key=2)
    with col2:
        start_time_1 = st.time_input("Start Time", df["Timestamp"].min().time(), key=3)
    with col3:
        end_date_1 = st.date_input("End Date", df["Timestamp"].max().date(), key=4)
    with col4:
        end_time_1 = st.time_input("End Time", df["Timestamp"].max().time(), key=5)
    # Combine date and time inputs into datetime objects
    start_datetime = pd.to_datetime(f"{start_date_1} {start_time_1}")
    end_datetime = pd.to_datetime(f"{end_date_1} {end_time_1}")

    # Filter the DataFrame based on the selected date and time range
    filtered_df = df[
        (df["Timestamp"] >= start_datetime) & (df["Timestamp"] <= end_datetime)
    ]

    # Create an interactive line chart with Plotly
    fig_2 = go.Figure()

    # Add traces for each series with specified colors
    fig_2.add_trace(
        go.Scatter(
            x=filtered_df["Timestamp"],
            y=filtered_df["Actual Total Totes"],
            mode="lines",
            name="Actual Total Totes",
            line=dict(color="blue"),
            visible="legendonly",  # Hides initially
        )
    )
    fig_2.add_trace(
        go.Scatter(
            x=filtered_df["Timestamp"],
            y=filtered_df["Actual Bad Totes"],
            mode="lines",
            name="Actual Bad Totes",
            line=dict(color="red"),
        )
    )
    fig_2.add_trace(
        go.Scatter(
            x=filtered_df["Timestamp"],
            y=filtered_df["Actual Good Totes"],
            mode="lines",
            name="Actual Good Totes",
            line=dict(color="green"),
            visible="legendonly",  # Hides initially
        )
    )

    # Update layout to include a legend at the bottom
    fig_2.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Totes",
        legend=dict(
            title="Category",
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.2,
            yanchor="bottom",
        ),
        hovermode="x",
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig_2)
with col_2:
    st.header("Day Over Day Analysis")
    # Display in Streamlit
    st.plotly_chart(fig_3)
