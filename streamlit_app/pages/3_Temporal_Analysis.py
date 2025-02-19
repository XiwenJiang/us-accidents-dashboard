import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import get_temporal_data, get_top_10_states_by_quarter, get_racing_bar_tooltip

st.title("Temporal Analysis")
st.write("Analyze accident trends over time.")
st.write("This page will feature visualizations for time-based trends.")

data = st.session_state.data


# Extract year and quarter from Start_Time
data['Quarter'] = data['Start_Time'].dt.quarter
data['YearQuarter'] = data['Year'].astype(str) + '-Q' + data['Quarter'].astype(str)

# Group by state and time period
state_time_counts = data.groupby(['State', 'Year', 'Quarter', 'YearQuarter'])['ID'].count().reset_index(name='Count')

# Get top 10 states for each time period and sort them
top_10_states_by_yr_ = (state_time_counts.groupby('YearQuarter')
                 .apply(lambda x: x.nlargest(10, 'Count')
                       .sort_values('Count', ascending=True))
                 .reset_index(drop=True))

# Get severity counts for each state and time period
severity_counts = (data.groupby(['State', 'YearQuarter', 'Severity'])
                      .size()
                      .reset_index(name='Severity_Count'))

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
states_list = ["All States"] + sorted(data['State'].unique().tolist())
selected_state = st.sidebar.selectbox(
    "Select State",
    options=states_list,
    index=0  # Default to "All States"
)

# Filter data based on state selection
if selected_state == "All States":
    filtered_data = data
else:
    filtered_data = data[data['State'] == selected_state]

# Add title with selected state
if selected_state != "All States":
    st.title(f"{selected_state}")

# Update all plots with filtered data
col1, col2 = st.columns(2)



with col1:
    # Define the desired order for severity levels
    severity_order = ['Critical', 'High', 'Medium', 'Low']

    # Convert the 'Severity' column to a categorical type with the specified order
    filtered_data['Severity'] = pd.Categorical(filtered_data['Severity'], categories=severity_order, ordered=True)

    # Ensure 'Start_Time' is in datetime format
    filtered_data['Start_Time'] = pd.to_datetime(filtered_data['Start_Time'], errors='coerce')

    # Extract year from 'Start_Time'
    filtered_data['Year'] = filtered_data['Start_Time'].dt.year

    # Group by year and severity, and count the number of accidents
    accidents_per_year_severity = filtered_data.groupby(['Year', 'Severity']).size().reset_index(name='Count')

    # Plotting the data using Plotly
    yr_svrt_fig = px.bar(accidents_per_year_severity, x='Year', y='Count', color='Severity', 
                title='Number of Accidents per Year by Severity',
                labels={'Year': 'Year', 'Count': 'Number of Accidents', 'Severity': 'Severity'},
                category_orders={'Severity': severity_order},
                barmode='group')

    # Group by year to get the total number of accidents per year
    accidents_per_year = filtered_data.groupby('Year').size().reset_index(name='Total_Count')

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
    filtered_data['YearMonth'] = pd.to_datetime(filtered_data['Start_Time'].dt.strftime('%Y-%m'))
    accidents_per_month = filtered_data.groupby('YearMonth').size().reset_index(name='Count')

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
    accidents_per_weekday = filtered_data.groupby('Day of Week').size().reset_index(name = 'Total_Count')

    dayofweek = {
        0: 'Monday',
        1: 'Tuesday', 
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    accidents_per_weekday['Day of Week'] = accidents_per_weekday['Day of Week'].map(dayofweek)
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    wkdy_barfig = px.bar(accidents_per_weekday,
                        x = 'Day of Week',
                        y = 'Total_Count',
                        color= 'Day of Week',
                        category_orders={'Day of Week': weekday_order},
                        title='Accidents by Day of Week',
                        labels={'Day of Week': 'Day of Week', 'Total_Count': 'Number of Accidents'})
    wkdy_barfig.update_layout(showlegend=False)
    st.plotly_chart(wkdy_barfig)


    accidents_per_hr = filtered_data.groupby('Hour').size().reset_index(name = "Total_Count")

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

