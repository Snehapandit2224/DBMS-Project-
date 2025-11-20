import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import base64
import os

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'astro_observatory',
    'user': 'root',
    'password': 'password'  # change this to your MySQL password
}

# ===================================================
# Background Music Function - REPLACE YOUR EXISTING ONE
# ===================================================
def add_background_music(audio_file):
    """Add looping background music in the footer"""
    if os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Create a footer music player that spans the bottom of the page
        audio_html = f"""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999; 
                    background: rgba(0, 0, 0, 0.85); padding: 15px 0; 
                    backdrop-filter: blur(15px);
                    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
                    border-top: 1px solid rgba(255, 255, 255, 0.2);
                    display: flex; justify-content: center; align-items: center; gap: 15px;">
            <p style="color: white; margin: 0; font-size: 14px; 
                      font-weight: 600; letter-spacing: 0.5px;">
                🎵 Interstellar Soundtrack
            </p>
            <audio controls loop id="background-music" style="height: 35px;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            <script>
                // Set volume to 50%
                var audio = document.getElementById('background-music');
                audio.volume = 0.5;
                
                // Try autoplay, but gracefully handle if blocked
                var playPromise = audio.play();
                if (playPromise !== undefined) {{
                    playPromise.catch(function(error) {{
                        console.log("Autoplay prevented. User needs to click play.");
                    }});
                }}
                
                // Store play state in localStorage to persist across reruns
                audio.addEventListener('play', function() {{
                    localStorage.setItem('musicPlaying', 'true');
                }});
                
                audio.addEventListener('pause', function() {{
                    localStorage.setItem('musicPlaying', 'false');
                }});
                
                // Resume if it was playing before
                if (localStorage.getItem('musicPlaying') === 'true') {{
                    audio.play().catch(e => console.log('Resume blocked'));
                }}
            </script>
        </div>
        
        <style>
            /* Add padding to bottom of page content so it doesn't hide behind footer */
            .block-container {{
                padding-bottom: 80px !important;
            }}
        </style>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Audio file '{audio_file}' not found. Current directory: {os.getcwd()}")


# ===================================================
# Utility Functions
# ===================================================

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        st.error(f"❌ Failed to connect to MySQL: {e}")
        return None

def execute_sql(conn, sql, params=None, fetch=False):
    if not conn:
        return [] if fetch else False
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params if params else ())
        if fetch:
            columns = [i[0] for i in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        else:
            conn.commit()
            return True
    except Error as e:
        st.error(f"⚠️ SQL Error: {e}")
        return [] if fetch else False
    finally:
        if cursor:
            cursor.close()

def record_exists(conn, table, column, value):
    sql = f"SELECT 1 FROM {table} WHERE {column} = %s LIMIT 1"
    cols, rows = execute_sql(conn, sql, params=(value,), fetch=True)
    return bool(rows)

def insert_celestial_object(conn,object_id,name,obj_type,magnitude,ra,dec,last_obs,distance_parsecs,redshift,diameter_km,mass_solar):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO CELESTIALOBJECTS 
            (ObjectID, ObjectName, ObjectType, Magnitude, RightAscension, Declination, LastObservedDate, Distance_Parsecs, Redshift, Diameter_km, Mass_SolarMass)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (object_id, name, obj_type, magnitude, ra, dec, last_obs, distance_parsecs, redshift, diameter_km, mass_solar)
        )
        conn.commit()
        cursor.close()
        return True, None
    except Error as e:
        try:
            conn.rollback()
        except:
            pass
        return False, e


def insert_telescope(conn, telescope_id, name, location, aperture_size, material, mount_type):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO TELESCOPES (TelescopeID, Name, Location, ApertureSize, PrimaryMirrorMaterial, MountType)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (telescope_id, name, location, aperture_size, material, mount_type)
        )
        conn.commit()
        cursor.close()
        return True, None
    except Error as e:
        try:
            conn.rollback()
        except:
            pass
        return False, e


def execute_commit(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    except Error:
        pass

# ===================================================
# Streamlit Layout & Styling
# ===================================================

st.set_page_config(page_title="PESU Astronomy DB", layout="wide")

BACKGROUND_URL = "https://i.pinimg.com/1200x/07/81/67/078167a5bf75852d60ab4b81b1b0091f.jpg"

st.markdown(
    f"""
    <style>
    /* ---- Page background ---- */
    .stApp {{
        background-image: url("{BACKGROUND_URL}");
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        color: white;
    }}

    /* ---- Frosted container ---- */
    .block-container {{
        background: rgba(0, 0, 0, 0.55); /* translucent black overlay */
        backdrop-filter: blur(10px);      /* adds the frosted glass effect */
        border-radius: 20px;
        padding: 2rem 3rem;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.1);
    }}

    /* ---- Headings ---- */
    h1, h2, h3, h4, h5 {{
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
        font-weight: 600;
    }}

    /* ---- Buttons ---- */
    div.stButton > button {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: rgba(255, 255, 255, 0.25);
        border-color: white;
        transform: scale(1.03);
    }}

    /* ---- Inputs ---- */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stNumberInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
    }}

    /* ---- Info boxes ---- */
    .info-box {{
        background-color: rgba(0,0,0,0.45);
        padding: 10px 16px;
        border-radius: 12px;
        color: #f5f5f5;
        font-size: 0.9rem;
        margin-bottom: 10px;
        border-left: 3px solid rgba(255,255,255,0.4);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ===================================================
# 🎵 ADD BACKGROUND MUSIC HERE 🎵
# ===================================================
add_background_music("Interstellar_BGM.mp3")



st.title("🌌 Astronomy Database Management System")

conn = get_db_connection()
if not conn:
    st.stop()

tabs = st.tabs([
    "1️⃣ CRUD & Trigger Demo",
    "2️⃣ Analytical Queries",
    "3️⃣ Stored Procedures / Functions",
    "4️⃣ Data Entry (Observations)"
])

# ===================================================
# TAB 1: CRUD & Trigger
# ===================================================
with tabs[0]:
    st.header("🧑‍🚀 A. Create New Researcher")
    st.markdown('<div class="info-box">Add new researcher records to the database with basic profile information and experience level.</div>', unsafe_allow_html=True)

    with st.form("create_researcher_form"):
        col1, col2 = st.columns(2)
        researcher_id = col1.text_input("Researcher ID (PK)")
        name = col2.text_input("Name")
        email = col1.text_input("Email")
        institution = col2.text_input("Institution")
        dob = col1.text_input("Date of Birth (YYYY-MM-DD)")
        experience = col2.number_input("Experience (Years)", min_value=0, step=1)
        submitted = st.form_submit_button("➕ Create Researcher")

        if submitted:
            if not (researcher_id and name and email):
                st.error("ID, Name, and Email are required!")
            elif record_exists(conn, "RESEARCHERS", "ResearcherID", researcher_id):
                st.warning(f"ResearcherID {researcher_id} already exists.")
            else:
                sql = """INSERT INTO RESEARCHERS (ResearcherID, Name, Email, Institution, DOB, InitialExperience)
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                params = (researcher_id, name, email, institution, dob, experience)
                if execute_sql(conn, sql, params):
                    st.success(f"✅ Researcher '{name}' created successfully!")

    st.divider()
    st.header("🚀 B. Trigger Test (Update Observation)")
    st.markdown('<div class="info-box">Update an observation rating to test triggers that log changes into the audit table.</div>', unsafe_allow_html=True)

    with st.form("trigger_form"):
        obs_id = st.number_input("Observation ID to Update", min_value=1, step=1)
        new_rating = st.number_input("New Quality Rating (1–5)", min_value=1, max_value=5, step=1)
        trigger_submit = st.form_submit_button("🔁 Update & Fire Trigger")

        if trigger_submit:
                        # ---- Fixed Trigger Test ----
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE OBSERVATIONS SET DataQualityRating = %s WHERE ObservationID = %s",
                    (new_rating, obs_id)
                )
                affected = cursor.rowcount
                conn.commit()
                cursor.close()

                if affected == 0:
                    st.warning(f"⚠️ No observation found with ID {obs_id}/ Nothing was updated.")
                else:
                    st.success(f"✅ Observation {obs_id} updated successfully — Trigger fired!")
            except Error as e:
                st.error(f"❌ SQL Error: {e}")


    if st.button("📜 View Audit Log (Last 5 Entries)"):
        sql = "SELECT LogID, ObservationID, OldDataQuality, ChangeTimestamp FROM OBSERVATION_LOG ORDER BY LogID DESC LIMIT 5"
        cols, rows = execute_sql(conn, sql, fetch=True)
        if rows:
            df = pd.DataFrame(rows, columns=cols)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No audit logs found.")

# ===================================================
# TAB 2: Analytical Queries
# ===================================================
with tabs[1]:
    st.header("🔍 Analytical Queries")
    st.markdown('<div class="info-box">Explore insightful analytical queries combining multiple tables, aggregations, and nested subqueries.</div>', unsafe_allow_html=True)

    # -----------------------------
    # Nested Query — Observers of a Discoverer
    # -----------------------------
    st.subheader("1️⃣ Nested Query — Observers of a Discoverer")
    st.markdown('<div class="info-box">Returns researchers who observed objects discovered by a given discoverer.</div>', unsafe_allow_html=True)
    discoverer = st.text_input("Enter Discoverer Name", "Galileo Galilei")
    if st.button("Run Nested Query"):
        sql = """
        SELECT R.Name FROM RESEARCHERS AS R
        WHERE R.ResearcherID IN (
            SELECT OS.ResearcherID FROM OBSERVATIONSESSIONS AS OS
            JOIN OBSERVATIONS AS O ON OS.SessionID = O.SessionID
            WHERE O.ObjectID IN (
                SELECT OD.ObjectID FROM OBJECTDISCOVERY AS OD
                WHERE OD.DiscovererName = %s
            )
        );"""
        cols, rows = execute_sql(conn, sql, params=(discoverer,), fetch=True)
        if rows:
            df = pd.DataFrame(rows, columns=cols)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No matching researchers found.")

    st.divider()
    # -----------------------------
    # Join Query — Observations by Seeing Condition
    # -----------------------------
    st.subheader("2️⃣ Join Query — Observations by Seeing Condition")
    st.markdown('<div class="info-box">Displays celestial objects, session details, and telescopes for a selected seeing condition.</div>', unsafe_allow_html=True)
    seeing = st.selectbox("Select Seeing Condition", ["Poor", "Fair", "Good", "Excellent"])
    if st.button("Run Join Query"):
        sql = """
        SELECT CO.ObjectName, OS.Date, T.Name AS TelescopeName, OS.SeeingCondition
        FROM OBSERVATIONS AS O
        JOIN OBSERVATIONSESSIONS AS OS ON O.SessionID = OS.SessionID
        JOIN TELESCOPES AS T ON OS.TelescopeID = T.TelescopeID
        JOIN CELESTIALOBJECTS AS CO ON O.ObjectID = CO.ObjectID
        WHERE OS.SeeingCondition = %s;
        """
        cols, rows = execute_sql(conn, sql, params=(seeing,), fetch=True)
        if rows:
            st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
        else:
            st.info("No records found for this condition.")

    st.divider()
    # -----------------------------
    # Aggregate Query — Telescope Usage > N
    # -----------------------------
    st.subheader("3️⃣ Aggregate Query — Telescope Usage > N")
    st.markdown('<div class="info-box">Lists telescopes used in more than N observations along with average duration.</div>', unsafe_allow_html=True)
    min_obs = st.number_input("Min Observation Count (N)", min_value=0, value=5, step=1)
    if st.button("Run Aggregate Query"):
        sql = f"""
        SELECT T.Name, AVG(O.DurationMinutes) AS AvgDuration, COUNT(O.ObservationID) AS ObsCount
        FROM TELESCOPES AS T
        JOIN OBSERVATIONSESSIONS AS OS ON T.TelescopeID = OS.TelescopeID
        JOIN OBSERVATIONS AS O ON OS.SessionID = O.SessionID
        GROUP BY T.Name
        HAVING COUNT(O.ObservationID) > {min_obs};
        """
        cols, rows = execute_sql(conn, sql, fetch=True)
        if rows:
            st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
        else:
            st.info("No telescopes match the criteria.")

    st.divider()
    # -----------------------------
    # Farthest / Nearest Celestial Object
    # -----------------------------
    st.subheader("4️⃣ Farthest / Nearest Celestial Object")
    # Celestial Object Type
    obj_type_main = st.selectbox(
        "Object Type",
        ["Star", "Planet", "Galaxy", "Nebula", "Asteroid", "Other"]
    )

    # If "Other" is selected, show text input for user to specify
    if obj_type_main == "Other":
        obj_type_custom = st.text_input("Specify Object Type", "")
        obj_type_final = obj_type_custom.strip() if obj_type_custom.strip() != "" else "Other"
    else:
        obj_type_final = obj_type_main

    # Later, use obj_type_final when inserting into CELESTIALOBJECTS table
    # Example:
    # insert_celestial_object(conn, object_id, obj_name, obj_type_final, obj_magnitude, obj_distance)

    distance_order = st.radio("Find:", ["Farthest", "Nearest"], key="distance_order")
    if st.button("Show Result for Distance"):
        order_dir = "DESC" if distance_order == "Farthest" else "ASC"
        sql = f"""
        SELECT ObjectName, Distance_Parsecs
        FROM CELESTIALOBJECTS
        WHERE ObjectType = '{obj_type_final}'
        ORDER BY Distance_Parsecs {order_dir}
        LIMIT 1;
        """
        cols, rows = execute_sql(conn, sql, fetch=True)
        if rows:
            st.success(f"{distance_order} {obj_type_final}: {rows[0][0]} ({rows[0][1]} parsecs)")
        else:
            st.warning(f"No {obj_type_final} found in the database.")

    st.divider()
    # -----------------------------
    # Brightest / Dimmest Celestial Object
    # -----------------------------
    st.subheader("5️⃣ Brightest / Dimmest Celestial Object")
    mag_order = st.radio("Find:", ["Brightest", "Dimmest"], key="mag_order")
    if st.button("Show Result for Magnitude"):
        order_dir = "ASC" if mag_order == "Brightest" else "DESC"
        sql = f"""
        SELECT ObjectName, Magnitude
        FROM CELESTIALOBJECTS
        ORDER BY Magnitude {order_dir}
        LIMIT 1;
        """
        cols, rows = execute_sql(conn, sql, fetch=True)
        if rows:
            st.success(f"{mag_order} object: {rows[0][0]} (Magnitude: {rows[0][1]})")
        else:
            st.warning("No objects found in the database.")

    st.divider()
    # -----------------------------
    # Telescope Utilization Hours
    # -----------------------------
    st.subheader("6️⃣ Telescope Utilization Hours")
    tel_id = st.number_input("Enter Telescope ID", min_value=1, step=1, key="util_tel_id")
    if st.button("Show Telescope Hours"):
        # check telescope exists
        check_sql = f"SELECT Name FROM TELESCOPES WHERE TelescopeID={tel_id}"
        _, tel_rows = execute_sql(conn, check_sql, fetch=True)
        if not tel_rows:
            st.warning(f"TelescopeID {tel_id} not found.")
        else:
            sql = f"SELECT get_telescope_utilization_hours({tel_id}) AS HoursUsed;"
            cols, rows = execute_sql(conn, sql, fetch=True)
            if rows:
                st.success(f"Telescope '{tel_rows[0][0]}' has been used for {rows[0][0]:.2f} hours.")
            else:
                st.warning("Calculation failed.")


# ===================================================
# TAB 3: Stored Procedures / Functions
# ===================================================

with tabs[2]:
    st.header("⚙️ Stored Procedures and Functions")
    st.markdown(
        '<div class="info-box">Execute predefined stored procedures and SQL functions from the database to perform computations or updates.</div>',
        unsafe_allow_html=True
    )

    # ----------------------------
    # A. Procedure — Update Researcher Stats
    # ----------------------------
    st.subheader("A. Procedure — Update Researcher Stats")
    rid_proc = st.number_input("Enter Researcher ID", min_value=1, step=1)

    if st.button("Run Procedure"):
        # Pre-check if researcher exists
        check_sql = f"SELECT 1 FROM RESEARCHERS WHERE ResearcherID = {rid_proc}"
        _, rows_check = execute_sql(conn, check_sql, fetch=True)
        
        if not rows_check:
            st.error(f"❌ Researcher ID {rid_proc} not found. Procedure not run.")
        else:
            sql = f"CALL update_researcher_total_time({rid_proc})"
            if execute_sql(conn, sql):
                st.success(f"✅ Researcher {rid_proc} stats updated!")

    if st.button("Check Updated Stats"):
        sql = f"SELECT Name, TotalObservationMinutes FROM RESEARCHERS WHERE ResearcherID = {rid_proc}"
        cols, rows = execute_sql(conn, sql, fetch=True)
        if rows:
            st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
        else:
            st.warning("Researcher not found.")

    st.divider()

    # ----------------------------
    # B. SQL Function — Calculate Effective Magnitude
    # ----------------------------
     # -------------------------
    # B. SQL Function — Calculate Effective Magnitude (by ObservationID)
    # -------------------------
    st.subheader("B. SQL Function — Calculate Effective Magnitude (by Observation ID)")
    st.markdown('<div class="info-box">Fetches magnitude and redshift for a given observation, then calculates the effective magnitude using the stored SQL function <code>calculate_effective_magnitude(M, z)</code>.</div>', unsafe_allow_html=True)

    obs_id_input = st.number_input("Enter Observation ID", min_value=1, step=1, key="obs_effmag")
    if st.button("Calculate Effective Magnitude", key="calc_effmag_btn"):
        # Step 1: Fetch magnitude & redshift for this observation
        sql_fetch = """
        SELECT CO.Magnitude, CO.Redshift
        FROM CELESTIALOBJECTS AS CO
        JOIN OBSERVATIONS AS O ON CO.ObjectID = O.ObjectID
        WHERE O.ObservationID = %s;
        """
        cols, rows = execute_sql(conn, sql_fetch, params=(obs_id_input,), fetch=True)

        if not rows:
            st.warning(f"⚠️ Observation ID {obs_id_input} does not exist or has no linked celestial object.")
        else:
            mag, redshift = rows[0]
            st.info(f"📊 Magnitude: **{mag}**, Redshift: **{redshift}**")

            # Step 2: Calculate effective magnitude using the stored function
            sql_calc = f"SELECT calculate_effective_magnitude({mag}, {redshift}) AS EffectiveMagnitude;"
            cols2, rows2 = execute_sql(conn, sql_calc, fetch=True)

            if rows2 and rows2[0][0] is not None:
                eff_mag = rows2[0][0]
                st.success(f"🌟 Effective Magnitude = **{eff_mag:.3f}**")
            else:
                st.error("❌ Calculation failed or returned NULL.")

    st.divider()

    # ----------------------------
    # C. SQL Function — Telescope Utilization Hours
    # ----------------------------
    st.subheader("C. SQL Function — Telescope Utilization Hours")
    st.markdown(
        '<div class="info-box">Determines total hours a telescope has been active. SUM of DurationMinutes for the TelescopeID converted to hours.</div>',
        unsafe_allow_html=True
    )
    tel_id = st.number_input("Enter Telescope ID", min_value=1, step=1, key="tel_usage")

    if st.button("Get Telescope Usage Hours"):
        # Pre-check if telescope exists
        check_sql = f"SELECT 1 FROM TELESCOPES WHERE TelescopeID = {tel_id}"
        _, tel_rows = execute_sql(conn, check_sql, fetch=True)
        if not tel_rows:
            st.warning(f"❌ Telescope ID {tel_id} not found. Cannot calculate usage hours.")
        else:
            sql = f"SELECT get_telescope_utilization_hours({tel_id}) AS HoursUsed"
            cols, rows = execute_sql(conn, sql, fetch=True)
            if rows and rows[0][0] is not None:
                st.success(f"🛰️ Telescope {tel_id} has been used for {rows[0][0]:.2f} hours.")
            else:
                st.warning(f"No usage records found for Telescope ID {tel_id}.")


# ===================================================
# TAB 4: DATA ENTRY — NEW OBSERVATION (robust with session_state)
# ===================================================
with tabs[3]:
    st.header("🛰️ Record New Observation")
    st.markdown('<div class="info-box">Insert a new observation session and observation. If referenced Telescope/Object records are missing, you can add them inline; the app will retry automatically.</div>', unsafe_allow_html=True)

    # --- Form to collect user input ---
    with st.form("new_obs_form"):
        st.subheader("Session Details")
        st.markdown('<div class="info-box">Create a new observation session. Researcher and Telescope IDs must exist or be created first.</div>', unsafe_allow_html=True)
        session_id = st.number_input("Session ID (New PK)", min_value=1, step=1, key="ui_session_id")
        researcher_id = st.number_input("Researcher ID (FK)", min_value=1, step=1, key="ui_researcher_id")
        telescope_id = st.number_input("Telescope ID (FK)", min_value=1, step=1, key="ui_telescope_id")
        date = st.text_input("Date (YYYY-MM-DD)", key="ui_date")

        st.subheader("Observation Record")
        st.markdown('<div class="info-box">Provide ObservationID, ObjectID (FK), duration, and quality rating. If missing, Telescope/Object can be added inline.</div>', unsafe_allow_html=True)
        obs_id = st.number_input("Observation ID (New PK)", min_value=1, step=1, key="ui_obs_id")
        object_id = st.number_input("Object ID (FK)", min_value=1, step=1, key="ui_object_id")
        duration = st.number_input("Duration (Minutes)", min_value=1, step=1, key="ui_duration")
        quality = st.number_input("Quality Rating (1–5)", min_value=1, max_value=5, step=1, key="ui_quality")

        submitted = st.form_submit_button("💾 Insert Observation")

    # --- Initialize session_state pending_obs structure if not present ---
    if "pending_obs" not in st.session_state:
        st.session_state.pending_obs = None

    # Helper: try to perform the insert using data in dict `d`
    def _attempt_insert(d):
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO OBSERVATIONSESSIONS (SessionID, ResearcherID, TelescopeID, Date, WeatherCondition, SeeingCondition) "
                "VALUES (%s, %s, %s, %s, 'Clear', 'Good')",
                (d["session_id"], d["researcher_id"], d["telescope_id"], d["date"])
            )
            cursor.execute(
                "INSERT INTO OBSERVATIONS (ObservationID, SessionID, ObjectID, DurationMinutes, DataQualityRating) "
                "VALUES (%s, %s, %s, %s, %s)",
                (d["obs_id"], d["session_id"], d["object_id"], d["duration"], d["quality"])
            )
            conn.commit()
            cursor.close()
            # clear pending_obs on success
            st.session_state.pending_obs = None
            st.success(f"✅ Session {d['session_id']} and Observation {d['obs_id']} recorded successfully!")
            # call stored procedure to update researcher stats
            execute_commit(conn, f"CALL update_researcher_total_time({d['researcher_id']})")
            return True, None
        except Error as e:
            try:
                conn.rollback()
            except:
                pass
            return False, e

    # When user clicks Insert Observation — create pending_obs with validation
    if submitted:
        problems = []
        # quick existence checks
        researcher_ok = record_exists(conn, "RESEARCHERS", "ResearcherID", researcher_id)
        tel_ok = record_exists(conn, "TELESCOPES", "TelescopeID", telescope_id)
        obj_ok = record_exists(conn, "CELESTIALOBJECTS", "ObjectID", object_id)
        sess_dup = record_exists(conn, "OBSERVATIONSESSIONS", "SessionID", session_id)
        obs_dup = record_exists(conn, "OBSERVATIONS", "ObservationID", obs_id)

        if not researcher_ok:
            problems.append(f"ResearcherID {researcher_id} does not exist.")
        if not tel_ok:
            problems.append(f"TelescopeID {telescope_id} does not exist.")
        if not obj_ok:
            problems.append(f"ObjectID {object_id} does not exist.")
        if sess_dup:
            problems.append(f"SessionID {session_id} already exists.")
        if obs_dup:
            problems.append(f"ObservationID {obs_id} already exists.")

        if problems:
            st.warning("Cannot insert due to: " + "; ".join(problems))
            # store pending_obs so the expanders appear persistently
            st.session_state.pending_obs = {
                "session_id": session_id,
                "researcher_id": researcher_id,
                "telescope_id": telescope_id,
                "date": date,
                "obs_id": obs_id,
                "object_id": object_id,
                "duration": duration,
                "quality": quality,
                "tel_missing": not tel_ok,
                "obj_missing": not obj_ok,
                "researcher_missing": not researcher_ok,
                "sess_dup": sess_dup,
                "obs_dup": obs_dup,
            }
            st.info("Use the inline forms below to add missing Telescope or Celestial Object. After successful addition the app will retry the insertion automatically.")
        else:
            # no pre-check problems — try to insert immediately
            d = {
                "session_id": session_id, "researcher_id": researcher_id, "telescope_id": telescope_id,
                "date": date, "obs_id": obs_id, "object_id": object_id, "duration": duration, "quality": quality
            }
            ok, err = _attempt_insert(d)
            if not ok:
                errno = getattr(err, "errno", None)
                if errno == 1452:
                    st.warning("Foreign key error during insert. Creating pending state so you can add missing FK items.")
                    # set pending flags to show inline forms
                    st.session_state.pending_obs = {
                        **d,
                        "tel_missing": "TELESCOPES" in str(err) or "TelescopeID" in str(err),
                        "obj_missing": "CELESTIALOBJECTS" in str(err) or "ObjectID" in str(err),
                        "researcher_missing": False,
                        "sess_dup": False,
                        "obs_dup": False
                    }
                elif errno == 1062:
                    st.warning("Duplicate primary key detected. Please choose unique SessionID/ObservationID.")
                else:
                    st.error(f"SQL Error during insert: {err}")

    # If there is a pending observation stored in session_state, show inline forms for missing items
    if st.session_state.pending_obs:
        d = st.session_state.pending_obs

        # Show what is pending
        st.info(f"Pending insert — Session {d['session_id']}, Observation {d['obs_id']}.")
        if d.get("researcher_missing"):
            st.warning(f"Researcher {d['researcher_id']} is missing. Please create researcher via the 'Create Researcher' tab first.")

        # Inline add Telescope if missing
        if d.get("tel_missing"):
            st.info(f"Telescope {d['telescope_id']} missing — add it below.")
            with st.expander("➕ Add Telescope"):
                tel_name = st.text_input("Telescope Name", key="ss_tel_name")
                tel_location = st.text_input("Telescope Location", key="ss_tel_loc")
                tel_aperture = st.number_input("Aperture Size (meters)", min_value=0.1, step=0.1, key="ss_tel_ap")
                tel_material = st.text_input("Primary Mirror Material", value="Glass", key="ss_tel_mat")
                tel_mount = st.text_input("Mount Type", value="Equatorial", key="ss_tel_mount")

                if st.button("Add Telescope", key="ss_add_tel_btn"):
                    ok_tel, err_tel = insert_telescope(
                        conn,
                        d["telescope_id"],
                        tel_name,
                        tel_location,
                        tel_aperture,
                        tel_material,
                        tel_mount
                    )
                    if ok_tel:
                        st.success(f"Telescope {d['telescope_id']} added.")
                        st.session_state.pending_obs["tel_missing"] = False
                        if not st.session_state.pending_obs.get("obj_missing"):
                            ok_insert, err_insert = _attempt_insert(st.session_state.pending_obs)
                            if not ok_insert:
                                st.error(f"Retry failed: {err_insert}")
                    else:
                        if getattr(err_tel, "errno", None) == 1062:
                            st.warning("Telescope ID already exists (race).")
                        else:
                            st.error(f"Failed to add telescope: {err_tel}")


        # Inline add Celestial Object if missing
        if d.get("obj_missing"):
            st.info(f"Celestial Object {d['object_id']} missing — add it below.")
            with st.expander("➕ Add Celestial Object"):
                obj_name = st.text_input("Object Name", key="obj_name")
                obj_type = st.text_input("Object Type (e.g., Star, Planet, Comet, Galaxy)", key="obj_type")
                obj_mag = st.number_input("Magnitude", value=0.0, step=0.1, key="obj_mag")
                obj_ra = st.text_input("Right Ascension (e.g., 08h 00m 00s)", key="obj_ra")
                obj_dec = st.text_input("Declination (e.g., +30d 00m 00s)", key="obj_dec")
                obj_lastobs = st.text_input("Last Observed Date (YYYY-MM-DD or leave blank)", key="obj_lastobs")
                obj_dist = st.number_input("Distance (parsecs)", value=0.0, step=0.1, key="obj_dist")
                obj_red = st.number_input("Redshift (z)", value=0.0, step=0.000001, key="obj_red")
                obj_diam = st.number_input("Diameter (km)", value=0.0, step=0.1, key="obj_diam")
                obj_mass = st.number_input("Mass (in Solar Masses)", value=0.0, step=0.1, key="obj_mass")

                if st.button("Add Celestial Object", key="add_obj_btn"):
                    ok_obj, err_obj = insert_celestial_object(
                        conn,
                        object_id,
                        obj_name,
                        obj_type,
                        obj_mag,
                        obj_ra,
                        obj_dec,
                        obj_lastobs if obj_lastobs else None,
                        obj_dist,
                        obj_red,
                        obj_diam,
                        obj_mass
                    )
                    if ok_obj:
                        st.success(f"Celestial Object {object_id} added successfully.")
                        obj_exists = True
                    else:
                        if getattr(err_obj, "errno", None) == 1062:
                            st.warning("Object ID already exists (race condition).")
                        else:
                            st.error(f"Failed to add object: {err_obj}")


        # If both missing flags are now false, attempt insert automatically (safety check)
        if not st.session_state.pending_obs.get("tel_missing") and not st.session_state.pending_obs.get("obj_missing"):
            # attempt insert (only once)
            ok_insert, err_insert = _attempt_insert(st.session_state.pending_obs)
            if ok_insert:
                # success message already shown by _attempt_insert
                pass
            else:
                # show helpful message and clear pending if duplicate or unrecoverable
                errno = getattr(err_insert, "errno", None)
                if errno == 1062:
                    st.warning("Duplicate key on retry — choose unique IDs and try again.")
                    st.session_state.pending_obs = None
                else:
                    st.error(f"Retry failed: {err_insert}")

