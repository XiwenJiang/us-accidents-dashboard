import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import state_code
st.set_page_config(layout="wide")

S3_BASE = "s3://us-accidents-dashboard-1445/processed"

@st.cache_data(ttl=3600)
def load_table(name: str) -> pd.DataFrame:
    return pd.read_parquet(f"{S3_BASE}/{name}/")

def filter_by_selected_state(df: pd.DataFrame, selected_state: str, state_col: str = "State") -> pd.DataFrame:
    """df[state_col] is state code; selected_state is full name. Return filtered df."""
    if selected_state == "All States":
        return df
    # convert code -> full name for filtering
    tmp = df.copy()
    tmp[state_col] = tmp[state_col].apply(state_code)
    return tmp[tmp[state_col] == selected_state]

st.title("Temporal Analysis")
st.write("Analyze accident trends over time.")
st.write("This page will feature visualizations for time-based trends.")

state_time_counts = load_table("state_quarter_counts").rename(columns={
    "State": "State_Code",
    "year": "Year",
    "quarter": "Quarter",
    "accident_count": "Count"
})

state_time_counts["State"] = state_time_counts["State_Code"].apply(state_code)

state_time_counts["YearQuarter"] = (
    state_time_counts["Year"].astype(str) + "-Q" + state_time_counts["Quarter"].astype(str)
)

# Get top 10 states for each time period and sort them
top_10_states_by_yr_ = (state_time_counts.groupby('YearQuarter')
                 .apply(lambda x: x.nlargest(10, 'Count')
                       .sort_values('Count', ascending=True))
                 .reset_index(drop=True))

# Get severity counts for each state and time period
severity_counts = load_table("state_yearquarter_severity_counts")
severity_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
severity_counts["Severity"] = severity_counts["Severity"].map(severity_map)
severity_counts["State"] = severity_counts["State"].apply(state_code)

# Create base figure
racing_bar = go.Figure()

# Add initial data
initial_data = top_10_states_by_yr_[top_10_states_by_yr_['YearQuarter'] == top_10_states_by_yr_['YearQuarter'].iloc[0]]
racing_bar.add_trace(
    go.Bar(
        x=initial_data['Count'],
        y=initial_data['State'],
        orientation='h',
        marker_color=px.colors.qualitative.Set3
    )
)

# Create tooltip function
def get_racing_tooltip(state, yearquarter):
    state_data = severity_counts[(severity_counts['State'] == state) & 
                               (severity_counts['YearQuarter'] == yearquarter)]
    tooltip = f"State: {state}<br>"
    tooltip += f"Time: {yearquarter}<br>"
    total = state_data['Severity_Count'].sum()
    tooltip += f"Total Accidents: {total}<br>"
    
    for _, row in state_data.iterrows():
        pct = (row['Severity_Count'] / total * 100)
        tooltip += f"{row['Severity']}: {row['Severity_Count']} ({pct:.1f}%)<br>"
    
    return tooltip

# Create and add frames
frames = []
for yearquarter in top_10_states_by_yr_['YearQuarter'].unique():
    frame_data = top_10_states_by_yr_[top_10_states_by_yr_['YearQuarter'] == yearquarter].sort_values('Count', ascending=True)
    
    # Create tooltips for each state in frame
    tooltips = [get_racing_tooltip(state, yearquarter) for state in frame_data['State']]
    
    # Format total count for text display
    text_display = frame_data['Count'].apply(lambda x: f'{x:,}')
    
    frames.append(
        go.Frame(
            data=[go.Bar(
                x=frame_data['Count'],
                y=frame_data['State'],
                orientation='h',
                marker_color=px.colors.qualitative.Set3,
                text=text_display,  # Display total count
                textposition='outside',  # Show text at end of bars
                hovertext=tooltips,  # Show detailed info on hover
                hoverinfo='text'
            )],
            name=yearquarter,
            layout=go.Layout(
                yaxis=dict(
                    categoryarray=frame_data['State'].tolist()
                )
            )
        )
    )

racing_bar.frames = frames

# Get max count for x-axis range
max_count = top_10_states_by_yr_['Count'].max()

# Update layout with x-axis range
racing_bar.update_layout(
    title='Top 10 States with Most Accidents (2016-2023)',
    xaxis_title='Number of Accidents',
    yaxis_title='State',
    showlegend=False,
    xaxis=dict(range=[0, max_count * 1.1]),
    updatemenus=[dict(
        type='buttons',
        showactive=False,
        buttons=[
            dict(
                label='Play',
                method='animate',
                args=[None, dict(
                    frame=dict(duration=1000, redraw=False),
                    fromcurrent=True,
                    mode='immediate'
                )]
            ),
            dict(
                label='Stop',
                method='animate',
                args=[[None], dict(
                    frame=dict(duration=0, redraw=False),
                    mode='immediate',
                    transition=dict(duration=0)
                )]
            )
        ]
    )],
    sliders=[{
        'currentvalue': {'prefix': 'Year-Quarter: ', 'font':{"size": 20}, 'xanchor':"right"},
        'steps': [
            {'args': [[f], {'frame': {'duration': 1000, 'redraw': True, "easing": "cubic-in-out"},
                            "pad": {"b": 10, "t": 50},  "len": 0.9,
                            "x": 0.1,
                            "y": 1,
                          'mode': 'immediate'}],
             'label': f,
             'method': 'animate'} for f in top_10_states_by_yr_['YearQuarter'].unique()
        ]
    }]
)

st.plotly_chart(racing_bar)

# Add state selection in sidebar
states_list = ["All States"] + sorted(state_time_counts["State"].unique().tolist())


selected_state = st.sidebar.selectbox(
    "Select State",
    options=states_list,
    index=0  # Default to "All States"
)

# Filter data based on state selection
if selected_state == "All States":
    state_time_counts_f = state_time_counts
    top_10_states_by_yr_f = top_10_states_by_yr_
else:
    state_time_counts_f = state_time_counts[state_time_counts["State"] == selected_state]
    top_10_states_by_yr_f = top_10_states_by_yr_[top_10_states_by_yr_["State"] == selected_state]
    st.title(selected_state)


# Update all plots with filtered data
col1, col2 = st.columns(2)



with col1:
    severity_order = ['Critical', 'High', 'Medium', 'Low']

    if selected_state == "All States":
        accidents_per_year_severity = load_table("accidents_by_year_severity").rename(columns={
            "year": "Year",
            "accident_count": "Count"
        })
        accidents_per_year = load_table("accidents_by_year_total").rename(columns={
            "year": "Year",
            "accident_count": "Total_Count"
        })
    else:
        accidents_per_year_severity = load_table("state_year_severity_counts")
        accidents_per_year_severity = filter_by_selected_state(accidents_per_year_severity, selected_state, "State")
        accidents_per_year_severity = accidents_per_year_severity.rename(columns={
            "year": "Year",
            "accident_count": "Count"
        })

        accidents_per_year = load_table("state_year_total_counts")
        accidents_per_year = filter_by_selected_state(accidents_per_year, selected_state, "State")
        accidents_per_year = accidents_per_year.rename(columns={
            "year": "Year",
            "accident_count": "Total_Count"
        })

    # map severity and set order
    accidents_per_year_severity["Severity"] = accidents_per_year_severity["Severity"].map(severity_map)
    accidents_per_year_severity["Severity"] = pd.Categorical(
        accidents_per_year_severity["Severity"],
        categories=severity_order,
        ordered=True
    )
    
    # Plotting the data using Plotly
    yr_svrt_fig = px.bar(accidents_per_year_severity, x='Year', y='Count', color='Severity', 
                title='Number of Accidents per Year by Severity',
                labels={'Year': 'Year', 'Count': 'Number of Accidents', 'Severity': 'Severity'},
                category_orders={'Severity': severity_order},
                barmode='group')


    # Add a line chart on top of the bar chart
    yr_svrt_fig.add_trace(go.Scatter(x=accidents_per_year['Year'], 
                            y=accidents_per_year['Total_Count'],
                            mode='lines+markers', 
                            name='Total Accidents', 
                            line=dict(color='green', dash = 'dashdot', width = 2)
                            ))


    # Display the plot in Streamlit
    st.plotly_chart(yr_svrt_fig)

    # Extract year and month, create datetime series
    if selected_state == "All States":
        accidents_per_month = load_table("accidents_by_year_month").rename(columns={
            "year": "Year",
            "month": "Month",
            "accident_count": "Count"
        })
    else:
        accidents_per_month = load_table("state_year_month_counts")
        accidents_per_month = filter_by_selected_state(accidents_per_month, selected_state, "State")
        accidents_per_month = accidents_per_month.rename(columns={
            "year": "Year",
            "month": "Month",
            "accident_count": "Count"
        })

    accidents_per_month["YearMonth"] = pd.to_datetime(
        accidents_per_month["Year"].astype(str) + "-" + accidents_per_month["Month"].astype(str).str.zfill(2)
    )
    accidents_per_month = accidents_per_month.sort_values("YearMonth")

    # Create monthly trend plot
    monthly_trend = px.line(accidents_per_month, 
                        x='YearMonth', 
                        y='Count',
                        title='Monthly Accident Trends (2016-2023)',
                        markers=True)

    # Update layout
    monthly_trend.update_layout(
        xaxis_title='Year-Month',
        yaxis_title='Number of Accidents',
        xaxis=dict(
            tickformat='%Y-%m',
            tickangle=45,
            tickmode='auto',
            nticks=30
        )
    )

    # Display plot
    st.plotly_chart(monthly_trend)


with col2:
    if selected_state == "All States":
        wk = load_table("accidents_by_weekday").rename(columns={"accident_count": "Total_Count"})
        # national table uses day_of_week 1..7
        wk["Day of Week"] = wk["day_of_week"].map({2:0, 3:1, 4:2, 5:3, 6:4, 7:5, 1:6})
    else:
        wk = load_table("state_weekday_counts").rename(columns={"accident_count": "Total_Count"})
        wk = filter_by_selected_state(wk, selected_state, "State")
        wk["Day of Week"] = wk["day_of_week"].map({2:0, 3:1, 4:2, 5:3, 6:4, 7:5, 1:6})

    accidents_per_weekday = wk[["Day of Week", "Total_Count"]].sort_values("Day of Week")

    # hour
    if selected_state == "All States":
        hr = load_table("accidents_by_hour").rename(columns={
            "hour": "Hour",
            "accident_count": "Total_Count"
        })
    else:
        hr = load_table("state_hour_counts")
        hr = filter_by_selected_state(hr, selected_state, "State")
        hr = hr.rename(columns={
            "hour": "Hour",
            "accident_count": "Total_Count"
        })

    accidents_per_hr = hr.sort_values("Hour")


    wkdy_barfig = px.bar(accidents_per_weekday,
                        x = 'Day of Week',
                        y = 'Total_Count',
                        color= 'Day of Week',
                        category_orders={'Day of Week': weekday_order},
                        title='Accidents by Day of Week',
                        labels={'Day of Week': 'Day of Week', 'Total_Count': 'Number of Accidents'})
    wkdy_barfig.update_layout(showlegend=False)
    st.plotly_chart(wkdy_barfig)

    hour_barfig = px.bar(accidents_per_hr,
                         x = 'Hour',
                         y = 'Total_Count',
                         title = 'Accident by Hour',
                         color='Hour',
                         color_continuous_scale='Tealgrn')
    
    hour_barfig.update_layout(
        annotations=[
            dict(
                x=7,  # Text position x
                y=accidents_per_hr['Total_Count'].max() * 1.1,  # Text position y
                text="Morning Peak",
                showarrow=False,
                arrowhead=1
            ),
            dict(
                x=16,  # Text position x
                y=accidents_per_hr['Total_Count'].max() * 1.1,  # Text position y
                text="Evening Peak",
                showarrow=False,
                arrowhead=1
            ),
            dict(
                ax=4,  # Text position x
                ay=accidents_per_hr['Total_Count'].max() * 0.7,  # Text position y
                text="go to work",
                showarrow=True,
                arrowhead=2,
                x=6,  # Arrow end x
                y=10,  # Arrow end y
                axref='x',  # Use x-axis coordinates
                ayref='y'   # Use y-axis coordinates
            ),
            dict(
                ax=20,  # Text position x
                ay=accidents_per_hr['Total_Count'].max() * 0.7,  # Text position y
                text="get off work",
                showarrow=True,
                arrowhead=2,
                x=16,  # Arrow end x
                y=10,   # Arrow end y
                axref='x',  # Use x-axis coordinates
                ayref='y'   # Use y-axis coordinates
            )
        ]
    )

    hour_barfig.update_layout(
        showlegend = False,
        xaxis=dict(
        tickmode='array',
        ticktext=[f'{i:02d}:00' for i in range(24)],  # Format as HH:00
        tickvals=list(range(24)),
        title='Hour of Day'
        ),
        yaxis=dict(title='Number of Accidents')
    )

    st.plotly_chart(hour_barfig)

