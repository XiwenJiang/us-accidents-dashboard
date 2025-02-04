import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Time Analysis")
st.write("Analyze accident trends over time.")
st.write("This page will feature visualizations for time-based trends.")

data = st.session_state.data


# Define the desired order for severity levels
severity_order = ['Critical', 'High', 'Medium', 'Low']

# Convert the 'Severity' column to a categorical type with the specified order
data['Severity'] = pd.Categorical(data['Severity'], categories=severity_order, ordered=True)

# Ensure 'Start_Time' is in datetime format
data['Start_Time'] = pd.to_datetime(data['Start_Time'], errors='coerce')

# Extract year from 'Start_Time'
data['Year'] = data['Start_Time'].dt.year

# Group by year and severity, and count the number of accidents
accidents_per_year_severity = data.groupby(['Year', 'Severity']).size().reset_index(name='Count')

# Plotting the data using Plotly
yr_svrt_fig = px.bar(accidents_per_year_severity, x='Year', y='Count', color='Severity', 
             title='Number of Accidents per Year by Severity',
             labels={'Year': 'Year', 'Count': 'Number of Accidents', 'Severity': 'Severity'},
             category_orders={'Severity': severity_order},
             barmode='group')

# Group by year to get the total number of accidents per year
accidents_per_year = data.groupby('Year').size().reset_index(name='Total_Count')

# Add a line chart on top of the bar chart
yr_svrt_fig.add_trace(go.Scatter(x=accidents_per_year['Year'], 
                         y=accidents_per_year['Total_Count'],
                         mode='lines+markers', 
                         name='Total Accidents', 
                         line=dict(color='green', dash = 'dashdot', width = 2)
                         ))


# Display the plot in Streamlit
st.plotly_chart(yr_svrt_fig)



# Extract year and quarter from Start_Time
data['Quarter'] = data['Start_Time'].dt.quarter
data['YearQuarter'] = data['Year'].astype(str) + '-Q' + data['Quarter'].astype(str)

# Group by state and time period
state_time_counts = data.groupby(['State', 'Year', 'Quarter', 'YearQuarter'])['ID'].count().reset_index(name='Count')

# Get top 10 states for each time period and sort them
top_10_states = (state_time_counts.groupby('YearQuarter')
                 .apply(lambda x: x.nlargest(10, 'Count')
                       .sort_values('Count', ascending=True))
                 .reset_index(drop=True))

# Create base figure
racing_bar = go.Figure()

# Add initial data
initial_data = top_10_states[top_10_states['YearQuarter'] == top_10_states['YearQuarter'].iloc[0]]
racing_bar.add_trace(
    go.Bar(
        x=initial_data['Count'],
        y=initial_data['State'],
        orientation='h',
        marker_color=px.colors.qualitative.Set3
    )
)

# Create and add frames
frames = []
for yearquarter in top_10_states['YearQuarter'].unique():
    frame_data = top_10_states[top_10_states['YearQuarter'] == yearquarter].sort_values('Count', ascending=True)
    frames.append(
        go.Frame(
            data=[go.Bar(
                x=frame_data['Count'],
                y=frame_data['State'],
                orientation='h',
                marker_color=px.colors.qualitative.Set3
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
max_count = top_10_states['Count'].max()

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
                    frame=dict(duration=1000, redraw=True),
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
        'currentvalue': {'prefix': 'Year-Quarter: '},
        'steps': [
            {'args': [[f], {'frame': {'duration': 1000, 'redraw': True},
                          'mode': 'immediate'}],
             'label': f,
             'method': 'animate'} for f in top_10_states['YearQuarter'].unique()
        ]
    }]
)

st.plotly_chart(racing_bar)

col1, col2 = st.columns(2)

with col1:
    # Extract year and month, create datetime series
    data['YearMonth'] = pd.to_datetime(data['Start_Time'].dt.strftime('%Y-%m'))
    accidents_per_month = data.groupby('YearMonth').size().reset_index(name='Count')

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
    accidents_per_weekday = data.groupby('Day of Week').size().reset_index(name = 'Total_Count')

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


    accidents_per_hr = data.groupby('Hour').size().reset_index(name = "Total_Count")

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
                y=1000,  # Arrow end y
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
                y=1000,   # Arrow end y
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