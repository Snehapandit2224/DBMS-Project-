Here is a comprehensive README file for your Astronomy Observation and Research Management System project, covering all the necessary sections for professional documentation and academic submission.

🌌 Astronomy Observation and Research Management System
This project is a complete, web-based database management system (DBMS) designed to manage the entire lifecycle of astronomical observations, inventory, and research data for an observatory.

The application adheres to the highest standards of relational database design (3NF) and demonstrates advanced server-side logic (Triggers, Procedures, Functions) required for the UE23CS351A Miniproject.

✨ Features
The application is organized into four main tabs, each demonstrating a key component of the project:

Full CRUD Operations: Allows secure insertion, viewing, and manipulation of records for core entities (Researchers, Telescopes).

Advanced Analytics: Executes complex Nested, Join, and Aggregate queries directly from the UI to provide valuable scientific insights.

Server-Side Logic Demonstration: Provides direct interfaces to call Stored Procedures and Functions.

Data Integrity & Recovery: Implements robust transaction logic, including auditing via triggers and graceful handling of missing Foreign Keys during data entry.

🛠️ Technology Stack
Component             Technology                 Role
--------------------- -------------------------- -------------------------------------------------------------
Database              MySQL                      Backend data storage and execution of complex logic.
Frontend/GUI          Python (Streamlit)         Creates the interactive, web-based Graphical User Interface (GUI).
Connector             mysql.connector            Python library for communication between the application and MySQL.
Analysis/Data Handling pandas                    Used for structured data handling, manipulation, and efficient tabular display in the Streamlit UI.

🚀 Setup and Installation
Follow these steps to set up the project locally.

Step 1: Database Setup (MySQL)
Execute the DDL/DML: Open your MySQL client (Workbench or CLI).

Run the Table_Creation.sql file: This script creates the astro_observatory database, all 11 tables, and inserts the necessary sample data.

Execute Stored Routines: Run the contents of the layer2.sql file to create the Functions, Procedures, and Triggers (e.g., update_researcher_total_time, trg_log_data_quality_update).

Step 2: Configure Python Environment
Install Libraries: Install all necessary Python dependencies:
pip install streamlit mysql-connector-python pandas

Step 3: Configure Credentials
Open the main application file (astro_app_streamlit.py).

Update the DB_CONFIG dictionary with your specific MySQL credentials:
DB_CONFIG = {
    'host': 'localhost',
    'database': 'astro_observatory',
    'user': 'root',
    'password': 'YOUR_PASSWORD_HERE' 
}

Step 4: Run the Application
Open your terminal in the directory where astro_app_streamlit.py is located.

Run the following command:
streamlit run astro_app_streamlit.py
The application will automatically open in your default web browser.

🧪 Demonstration Highlights
The following features should be highlighted during evaluation:
# Tab 1: CRUD & Trigger DemoTrigger Test: Updating the DataQualityRating for Obs ID 202 proves the trg_log_data_quality_update trigger works by inserting an entry into the OBSERVATION_LOG table.
# Tab 2: Analytical QueriesAggregate Query: Running the query with $N=5$ should show the Lick 1m telescope used 10 times, demonstrating AVG(), COUNT(), and the critical HAVING clause.Nested Query: Running the query for 'Galileo Galilei' should return Dr. Amelia Jones, demonstrating multi-level subquery logic.
# Tab 3: Stored Procedures / FunctionsProcedure: Calling Run Procedure for Researcher ID 2 executes update_researcher_total_time, updating the TotalObservationMinutes column from 0 to 210 (7 sessions $\times$ 30 min) in the database.Function: Calculating Effective Magnitude demonstrates the execution of the complex scientific formula stored as a UDF on the server.
# Tab 4:The "Data Entry (Observations)" is the application's critical transactional interface, allowing the user to initiate a new observation session and its associated observation record in a single submission. The application is programmed to be robust against common data errors by first performing validity checks on foreign keys (FKs) like ResearcherID, TelescopeID, and ObjectID, and then, if any FK is missing, it displays inline forms that allow the user to add the missing resource (e.g., a new Telescope or Celestial Object) on the fly before automatically retrying the original transaction. Upon successful insertion, the tab triggers the stored procedure update_researcher_total_time to immediately update the researcher's aggregate statistics in the background.

