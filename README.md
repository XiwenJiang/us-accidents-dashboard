# us-accidents-dashboard

## Project Goal
The primary goal of the project is to build an interactive Streamlit dashboard that provides insights and visualizations related to traffic accidents across the United States. Specifically, the dashboard should:

1. *Analyze accident trends* by severity, location (city, state), time, and other factors (such as weather, time of day, etc.).
   
2. Provide *interactive visualizations* for users to explore patterns such as:
    - Accident severity distribution across different states.
    - Time-of-day and day-of-week patterns.
    - Geospatial distribution of accidents.

3. Allow stakeholders (e.g., government agencies, researchers, businesses) to interactively explore accident data to identify hotspots, high-severity areas, or factors contributing to accidents.
   
4. Provide actionable insights for decision-makers such as policy makers, transportation authorities, or traffic safety professionals to improve road safety.

## Nature of the US-Accident Dataset:
1. The data is a tabular dataset containing information about traffic accidents across 49 U.S. states, with columns representing accident-specific attributes (e.g., Start_Lat, Start_Lng, Severity, Start_Time, City, State, Distance, etc.).
2. It includes both geospatial data (latitude and longitude), temporal data (timestamps of accidents), and categorical data (severity levels, city, state, etc.).
3. The dataset is relatively large, containing millions of records, and covers multiple years (from February 2016 to March 2023).
4. The dataset is real-time and comes from multiple APIs that stream accident data, sourced from transportation departments, law enforcement, and other traffic entities.

## Delivery and Audience:
- Delivery: The dashboard will be delivered as an interactive web application built with *Streamlit*, which will be hosted on a cloud platform (Streamlit Cloud)

- Audience: 
  - *Researchers* interested in studying the causes and patterns of accidents for their academic work or policy suggestions.
  - *Businesses*, especially in the insurance and logistics industries, who need insights to improve operations and assess risk factors based on accident trends.
  - *General public* who may want to explore accident data by location or time to make informed decisions about travel.


# Statiscial Analysis

## Geospatial analysis 
    using maps, highlighting accident hotspots.


## Time-based analysis 
Time series analysis for accident trends (e.g., hour of day, day of week).
Discovery the seasonality.

## Severity analysis 
Based on accident impact levels.
