import streamlit as st
import config
import pymysql
import pandas as pd
import datetime
from datetime import datetime
connection = pymysql.connect(
    host = config.DB_HOST,
    user = config.DB_USER,
    password = config.DB_PASSWORD,
    database = config.DB_NAME
)
cursor = connection.cursor()
st.title("🚀 NASA Near-Earth Object (NEO) Tracking & Insights using Public API 🌍")
with st.expander("ℹ️ About"):
    st.markdown("""
        This app tracks **Near-Earth Objects (NEOs)** using NASA's API🛰️.  

        👩‍💻 Use the filters in the sidebar to explore **more**...😉 
        """)
st.sidebar.header("🔍 Filters")
tab1, tab2, tab3 = st.tabs(["Predefined  Queries📝","Asteroids🌑", "Close Approaches☄️ "])
with tab1:
    query_options = st.sidebar.selectbox(
        "Predefined Queries✍ ",
        [
            "NULL",
            "1. Count how many times each asteroid has approached Earth",
            "2. Average velocity of each asteroid over multiple approaches",
            "3. List top 10 fastest asteroids",
            "4. Find potentially hazardous asteroids that have approached Earth more than 3 times",
            "5. Find the month with the most asteroid approaches",
            "6. Get the asteroid with the fastest ever approach speed",
            "7. Sort asteroids by maximum estimated diameter (descending)",
            "8. An asteroid whose closest approach is getting nearer over time",
            "9. Display the name of each asteroid along with the date and miss distance of its closest approach to Earth",
            "10. List names of asteroids that approached Earth with velocity > 50,000 km/h",
            "11. Count how many approaches happened per month",
            "12. Find asteroid with the highest brightness (lowest magnitude value)",
            "13. Get number of hazardous vs non-hazardous asteroids",
            "14. Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance",
            "15. Find asteroids that came within 0.05 AU(astronomical distance)"
        ]
    )
    with st.sidebar.expander("📂 Queries"):
        st.write(query_options)
    if query_options == "1. Count how many times each asteroid has approached Earth":
        cursor.execute(
            """
            SELECT id, name, count(*) as count
            FROM asteroids
            GROUP BY id, name;
            """
            )
        result1 = cursor.fetchall()
        df1 = pd.DataFrame(result1, columns=["ID", "Name", "Count"])
        st.subheader("Asteroid Appearance Count")
        st.dataframe(df1)
    elif query_options == "2. Average velocity of each asteroid over multiple approaches":
        cursor.execute(
            """
            SELECT a.id, a.name, AVG(c.relative_velocity_kmph) AS average_velocity
            FROM close_approach AS c
            JOIN asteroids AS a
            ON a.id = c.neo_reference_id
            GROUP BY c.neo_reference_id, a.name, a.id;
            """
            )
        result2 = cursor.fetchall()
        df2 = pd.DataFrame(result2, columns=["ID", "Name", "Average Velocity"])
        st.subheader("Average Velocity Of Each Asteroid")
        st.dataframe(df2)
    elif query_options == "3. List top 10 fastest asteroids":
        cursor.execute(
            """
            SELECT DISTINCT a.id, a.name, c.relative_velocity_kmph, DENSE_RANK() OVER(ORDER BY c.relative_velocity_kmph DESC) AS velocity_rank
            FROM close_approach AS c 
            JOIN asteroids AS a
            ON a.id = c.neo_reference_id
            """
            )
        result3 = cursor.fetchall()
        df3 = pd.DataFrame(result3, columns=["ID", "Name", "Velocity", "Rank"])
        st.subheader("Top 10 fastest asteroids")
        st.dataframe(df3.head(10))
    elif query_options == "4. Find potentially hazardous asteroids that have approached Earth more than 3 times":
        cursor.execute(
            """
            SELECT id, name, COUNT(*) AS count
            FROM asteroids
            WHERE is_potentially_hazardous_asteroid = 1
            GROUP BY id, name
            HAVING count > 3;
            """
            )
        result4 = cursor.fetchall()
        df4 = pd.DataFrame(result4, columns=["ID", "Name", "Count"])
        st.subheader("Hazardous Asteroids That Have Approached Earth More Than 3 Times")
        st.dataframe(df4)
    elif query_options == "5. Find the month with the most asteroid approaches":
        cursor.execute(
            """
            SELECT YEAR(close_approach_date) AS year, MONTH(close_approach_date) AS month, COUNT(*) AS count
            FROM close_approach
            GROUP BY YEAR(close_approach_date), MONTH(close_approach_date)
            ORDER BY count DESC
            """
            )
        result5 = cursor.fetchall()
        df5 = pd.DataFrame(result5, columns=["Year", "Month", "Count"])
        st.subheader("Month With The Most Asteroid Approaches")
        st.dataframe(df5.head(1))
    elif query_options == "6. Get the asteroid with the fastest ever approach speed":
        cursor.execute(
            """
            SELECT a.id, a.name, c.relative_velocity_kmph, RANK() OVER(ORDER BY c.relative_velocity_kmph DESC) AS velocity_rank
            FROM close_approach AS c
            JOIN asteroids AS a
            ON a.id = c.neo_reference_id
            """
    )
        result6 = cursor.fetchall()
        df6 = pd.DataFrame(result6, columns=["ID", "Name", "Speed", "Rank"])
        st.subheader("Fastest Asteriod")
        st.dataframe(df6.head(1))
    elif query_options == "7. Sort asteroids by maximum estimated diameter (descending)":
        cursor.execute(
            """
            SELECT DISTINCT id, name, estimated_diameter_max_km, DENSE_RANK() OVER(ORDER BY estimated_diameter_max_km DESC) AS rank_estimated_diameter_max_km
            FROM asteroids
            """
            )
        result7 = cursor.fetchall()
        df7 = pd.DataFrame(result7, columns=["ID", "Name", "Diameter in Kilometers", "Rank"])
        st.subheader("Diameter in Descending")
        st.dataframe(df7)
    elif query_options == "8. An asteroid whose closest approach is getting nearer over time":
        cursor.execute(
            """
            SELECT * FROM
            (
            SELECT a.id, a.name, c.miss_distance_km,
            LAG(c.miss_distance_km) OVER (PARTITION BY c.neo_reference_id ORDER BY c.close_approach_date) AS previous_miss_distance
            FROM close_approach AS c
            JOIN asteroids AS a
            ON a.id = c.neo_reference_id
            ) AS subquery
            WHERE previous_miss_distance IS NOT NULL
            AND miss_distance_km < previous_miss_distance
            ORDER BY id;
            """
            )
        result8 = cursor.fetchall()
        df8 = pd.DataFrame(result8, columns = ["ID", "Name","Miss Distance in Kilometers", "Previous Miss Distance in Kilometers"])
        st.subheader("An Asteroid Whose Closest Approach Is Getting Nearer Over Time")
        st.dataframe(df8)
    elif query_options == "9. Display the name of each asteroid along with the date and miss distance of its closest approach to Earth":
        cursor.execute(
            """
            SELECT name, close_approach_date, miss_distance_km FROM 
            (
            SELECT a.name, c.close_approach_date, c.miss_distance_km,
            ROW_NUMBER() OVER (PARTITION BY c.neo_reference_id ORDER BY c.miss_distance_km ASC) AS row_no
            FROM close_approach AS c
            JOIN asteroids AS a 
            ON a.id = c.neo_reference_id
            ) AS subquery
            WHERE row_no = 1;
            """
            )
        result9 = cursor.fetchall()
        df9 = pd.DataFrame(result9, columns = ["Name","Close Approach Date","Miss Distance in Kilometers"])
        st.subheader("Names Of Each Asteroid Along With The Close Approach Date And Miss Distance")
        st.dataframe(df9)
    elif query_options == "10. List names of asteroids that approached Earth with velocity > 50,000 km/h":
        cursor.execute(
            """
            SELECT a.name, c.relative_velocity_kmph
            FROM close_approach AS c
            JOIN asteroids AS a 
            ON a.id = c.neo_reference_id
            WHERE c.relative_velocity_kmph > 50000;
            """
            )
        result10 = cursor.fetchall()
        df10 = pd.DataFrame(result10, columns = ["Name","Velocity"])
        st.subheader("Names Of Asteroids That Approached Earth With Velocity > 50,000 km/h")
        st.dataframe(df10)
    elif query_options == "11. Count how many approaches happened per month":
        cursor.execute(
            """
            SELECT YEAR(close_approach_date) AS year, MONTH(close_approach_date) AS month, COUNT(*) AS approaches 
            FROM close_approach
            GROUP BY YEAR(close_approach_date), MONTH(close_approach_date)
            ORDER BY year, month;
            """
            )
        result11 = cursor.fetchall()
        df11 = pd.DataFrame(result11, columns = ["Year","Month","Count"])
        st.subheader("How Many Approaches Per Month")
        st.dataframe(df11)
    elif query_options == "12. Find asteroid with the highest brightness (lowest magnitude value)":
        cursor.execute(
            """
            SELECT id, name, absolute_magnitude_h
            FROM asteroids
            ORDER BY absolute_magnitude_h;
            """
            )
        result12 = cursor.fetchall()
        df12 = pd.DataFrame(result12, columns = ["ID","Name","Absolute Magnitude"])
        st.subheader("Asteroid With The Highest Brightness")
        st.dataframe(df12.head(1))
    elif query_options == "13. Get number of hazardous vs non-hazardous asteroids":
        cursor.execute(
            """
            SELECT is_potentially_hazardous_asteroid, COUNT(*) AS haz_vs_nonhaz 
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid
            ORDER BY is_potentially_hazardous_asteroid DESC;
            """
            )
        result13 = cursor.fetchall()
        df13 = pd.DataFrame(result13, columns = ["Is Potentially Hazardous","Count"])
        df13.iloc[0, 0] = "Hazardous"
        df13.iloc[1, 0] = "Non-Hazardous"
        st.subheader("Number Of Hazardous Vs Non-Hazardous Asteroids")
        st.dataframe(df13)
    elif query_options == "14. Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance":
        cursor.execute(
            """
            SELECT a.id, a.name, c.miss_distance_lunar, c.close_approach_date, c.miss_distance_km
            FROM close_approach AS c
            JOIN asteroids AS a 
            ON a.id = c.neo_reference_id
            WHERE c.miss_distance_lunar < 1;
            """
            )
        result14 = cursor.fetchall()
        df14 = pd.DataFrame(result14, columns = ["ID","Name","Miss Distance Lunar","Close Approach Date","Miss Distance in Kilometers"])
        st.subheader("Asteroids That Passed Closer Than The Moon")
        st.dataframe(df14)
    elif query_options == "15. Find asteroids that came within 0.05 AU(astronomical distance)":
        cursor.execute(
            """
            SELECT a.id, a.name, c.astronomical
            FROM close_approach AS c
            JOIN asteroids AS a 
            ON a.id = c.neo_reference_id
            WHERE c.astronomical < 0.05;
            """
            )
        result15 = cursor.fetchall()
        df15 = pd.DataFrame(result15, columns = ["ID","Name","Astronomical Distance (AU)"])
        st.subheader("Asteroids That Came Within 0.05 AU")
        st.dataframe(df15)
with tab2:
    st.subheader("Asteroids🌑")
    cursor.execute("SELECT * FROM asteroids")
    result_asteroids = cursor.fetchall()
    df_asteroids = pd.DataFrame(result_asteroids, columns = ["ID","Name","Absolute_magnitude_h","Estimated_diameter_min_km","Estimated_diameter_max_km","Is_potentially_hazardous_asteroid"])
    filtered_df = df_asteroids.copy()

    st.sidebar.subheader("Filters for Table Asteroids📊")
    selected_id = st.sidebar.selectbox("Filter by Asteroid 🆔", options=["NULL"] + list(filtered_df["ID"]))
    selected_name = st.sidebar.selectbox("Filter by Asteroid Name🌌", options=["NULL"]+list(filtered_df["Name"]))
    min_absolute_magnitude_h = float(filtered_df["Absolute_magnitude_h"].min())
    max_absolute_magnitude_h = float(filtered_df["Absolute_magnitude_h"].max())
    magnitude_range = st.sidebar.slider(
        "Filter by Absolute Magnitude H🌟",
        min_value=min_absolute_magnitude_h,
        max_value=max_absolute_magnitude_h,
        value=(min_absolute_magnitude_h, max_absolute_magnitude_h),
        step=0.1
    )
    min_estimated_diameter_min_km = float(filtered_df["Estimated_diameter_min_km"].min())
    max_estimated_diameter_min_km = float(filtered_df["Estimated_diameter_min_km"].max())
    estimated_diameter_min_km_range = st.sidebar.slider(
        "Filter by Estimated Diameter Min Km📏",
        min_value=min_estimated_diameter_min_km,
        max_value=max_estimated_diameter_min_km,
        value=(min_estimated_diameter_min_km, max_estimated_diameter_min_km),
        step=0.1
        )
    min_estimated_diameter_max_km = float(filtered_df["Estimated_diameter_max_km"].min())
    max_estimated_diameter_max_km = float(filtered_df["Estimated_diameter_max_km"].max())
    estimated_diameter_max_km_range = st.sidebar.slider(
        "Filter by Estimated Diameter Max Km📏",
        min_value=min_estimated_diameter_max_km,
        max_value=max_estimated_diameter_max_km,
        value=(min_estimated_diameter_max_km, max_estimated_diameter_max_km),
        step=0.1
    )
    filter_hazardous = st.sidebar.checkbox("Show Only Potentially Hazardous Asteroids⚠️")

    if selected_id != "NULL":
        filtered_df= filtered_df[filtered_df["ID"] == selected_id]

    if selected_name != "NULL":
        filtered_df = filtered_df[filtered_df["Name"] == selected_name]

    filtered_df = filtered_df[(filtered_df["Absolute_magnitude_h"] >= magnitude_range[0]) &
    (filtered_df["Absolute_magnitude_h"] <= magnitude_range[1])]

    filtered_df = filtered_df[(filtered_df["Estimated_diameter_min_km"] >= estimated_diameter_min_km_range [0]) &
    (filtered_df["Estimated_diameter_min_km"] <= estimated_diameter_min_km_range [1])]

    filtered_df = filtered_df[(filtered_df["Estimated_diameter_max_km"] >= estimated_diameter_max_km_range [0]) &
    (filtered_df["Estimated_diameter_max_km"] <= estimated_diameter_max_km_range [1])]

    if filter_hazardous:
        filtered_df = filtered_df[filtered_df["Is_potentially_hazardous_asteroid"] == 1]

    st.dataframe(filtered_df)


with tab3:
    st.subheader("Close Approach☄️")
    cursor.execute("SELECT * FROM close_approach")
    result_close_approach = cursor.fetchall()
    df_close_approach = pd.DataFrame(result_close_approach, columns = ["Neo Reference ID","Close Approach Date","Relative Velocity Kmph","Astronomical (AU)","Miss Distance Km","Miss Distance Lunar","Orbiting Body"])
    filtered_df1 = df_close_approach.copy()

    st.sidebar.subheader("Filters for Table Close Approach📊")
    selected_neo_reference_id = st.sidebar.selectbox("Filter by Neo Reference 🆔", options=["NULL"] + list(filtered_df1["Neo Reference ID"]))
    filtered_df1["Close Approach Date"] = pd.to_datetime(filtered_df1["Close Approach Date"], errors="coerce")
    filtered_df1["Close Approach Date"] = filtered_df1["Close Approach Date"].dt.date
    if st.sidebar.checkbox("📅 Enable Date Filter"):
        date_range = st.sidebar.date_input(
            "📅 Select Date Range for Close Approach",[filtered_df1["Close Approach Date"].min(), filtered_df1["Close Approach Date"].max()])
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            st.error("⚠️ Please select a valid date range.")
            st.stop()
    else:
        start_date = datetime.strptime("2024-01-01", "%Y-%m-%d").date()
        end_date = datetime.strptime("2025-05-23", "%Y-%m-%d").date()
    min_relative_velocity_kmph = float(filtered_df1["Relative Velocity Kmph"].min())
    max_relative_velocity_kmph = float(filtered_df1["Relative Velocity Kmph"].max())
    relative_velocity_kmph_range = st.sidebar.slider(
        "Filter by Relative Velocity Kmph⚡",
        min_value=min_relative_velocity_kmph,
        max_value=max_relative_velocity_kmph,
        value=(min_relative_velocity_kmph, max_relative_velocity_kmph),
        step=0.1
    )
    min_astronomical = float(filtered_df1["Astronomical (AU)"].min())
    max_astronomical = float(filtered_df1["Astronomical (AU)"].max())
    astronomical_range = st.sidebar.slider(
        "Filter by Astronomical (AU)🔭",
        min_value=min_astronomical,
        max_value=max_astronomical,
        value=(min_astronomical, max_astronomical),
        step=0.1
    )
    min_miss_distance_km = float(filtered_df1["Miss Distance Km"].min())
    max_miss_distance_km = float(filtered_df1["Miss Distance Km"].max())
    miss_distance_km_range = st.sidebar.slider(
        "Filter by Miss Distance Km📏",
        min_value=min_miss_distance_km,
        max_value=max_miss_distance_km,
        value=(min_miss_distance_km, max_miss_distance_km),
        step=0.1
    )
    min_miss_distance_Lunar = float(filtered_df1["Miss Distance Lunar"].min())
    max_miss_distance_Lunar = float(filtered_df1["Miss Distance Lunar"].max())
    miss_distance_Lunar_range = st.sidebar.slider(
        "Filter by Miss Distance Lunar🌙",
        min_value=min_miss_distance_Lunar,
        max_value=max_miss_distance_Lunar,
        value=(min_miss_distance_Lunar, max_miss_distance_Lunar),
        step=0.1
    )

    if selected_neo_reference_id != "NULL":
         filtered_df1= filtered_df1[filtered_df1["Neo Reference ID"] == selected_neo_reference_id]
    filtered_df1 = filtered_df1[(filtered_df1["Close Approach Date"] >= start_date) &
    (filtered_df1["Close Approach Date"] <= end_date)]
    filtered_df1 = filtered_df1[(filtered_df1["Relative Velocity Kmph"] >= relative_velocity_kmph_range[0]) &
    (filtered_df1["Relative Velocity Kmph"] <= relative_velocity_kmph_range[1])]
    filtered_df1 = filtered_df1[(filtered_df1["Astronomical (AU)"] >= astronomical_range[0]) &
    (filtered_df1["Astronomical (AU)"] <= astronomical_range[1])]
    filtered_df1 = filtered_df1[(filtered_df1["Miss Distance Km"] >= miss_distance_km_range[0]) &
    (filtered_df1["Miss Distance Km"] <= miss_distance_km_range[1])]
    filtered_df1 = filtered_df1[(filtered_df1["Miss Distance Lunar"] >= miss_distance_Lunar_range[0]) &
    (filtered_df1["Miss Distance Lunar"] <= miss_distance_Lunar_range[1])]

    st.dataframe(filtered_df1)

cursor.close()
connection.close()