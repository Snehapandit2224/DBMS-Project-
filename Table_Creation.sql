create database astro_observatory;
USE astro_observatory;


-- 1. RESEARCHERS (Independent)
CREATE TABLE RESEARCHERS (
    ResearcherID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Institution VARCHAR(100),
    Email VARCHAR(100) UNIQUE NOT NULL,
    DOB DATE,
    InitialExperience INT,
    TotalObservationMinutes INT DEFAULT 0
);

-- 2. TELESCOPES (Independent)
CREATE TABLE TELESCOPES (
    TelescopeID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Location VARCHAR(100),
    ApertureSize FLOAT CHECK (ApertureSize > 0),
    PrimaryMirrorMaterial VARCHAR(50),
    MountType VARCHAR(50)
);

-- 3. CELESTIALOBJECTS (Independent)
CREATE TABLE CELESTIALOBJECTS (
    ObjectID INT PRIMARY KEY,
    ObjectName VARCHAR(100) UNIQUE NOT NULL,
    ObjectType VARCHAR(50),
    Magnitude FLOAT CHECK (Magnitude >= -30 AND Magnitude <= 30),
    RightAscension VARCHAR(20),
    Declination VARCHAR(20),
    LastObservedDate DATE,
    Distance_Parsecs FLOAT,
    Redshift FLOAT,
    Diameter_km FLOAT,
    Mass_SolarMass FLOAT
);


-- 2. LEVEL 1 DEPENDENT TABLES
-- 4. RESEARCHERPHONES (FK -> RESEARCHERS)
CREATE TABLE RESEARCHERPHONES (
    ResearcherID INT,
    PhoneNumber VARCHAR(20),
    PRIMARY KEY (ResearcherID, PhoneNumber),
    FOREIGN KEY (ResearcherID) REFERENCES RESEARCHERS(ResearcherID)
);

-- 5. OBJECTDISCOVERY (FK -> CELESTIALOBJECTS)
CREATE TABLE OBJECTDISCOVERY (
    ObjectID INT PRIMARY KEY,
    DiscovererName VARCHAR(100),
    DiscoveryDate DATE,
    FOREIGN KEY (ObjectID) REFERENCES CELESTIALOBJECTS(ObjectID)
);

-- 6. INSTRUMENTS (FK -> TELESCOPES)
CREATE TABLE INSTRUMENTS (
    InstrumentID INT PRIMARY KEY,
    TelescopeID INT,
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(50),
    WavelengthRange VARCHAR(50),
    Resolution VARCHAR(50),
    FOREIGN KEY (TelescopeID) REFERENCES TELESCOPES(TelescopeID)
);


-- 3. LEVEL 2 DEPENDENT TABLES
-- 7. OBSERVATIONSESSIONS (FKs -> RESEARCHERS, TELESCOPES)
CREATE TABLE OBSERVATIONSESSIONS (
    SessionID INT PRIMARY KEY,
    Date DATE NOT NULL, -- CORRECTED: Removed DEFAULT CURRENT_DATE
    WeatherCondition VARCHAR(50),
    SeeingCondition VARCHAR(50),
    ResearcherID INT,
    TelescopeID INT,
    FOREIGN KEY (ResearcherID) REFERENCES RESEARCHERS(ResearcherID),
    FOREIGN KEY (TelescopeID) REFERENCES TELESCOPES(TelescopeID)
);

-- 8. RESEARCHERINSTRUMENTS (FKs -> RESEARCHERS, INSTRUMENTS)
CREATE TABLE RESEARCHERINSTRUMENTS (
    ResearcherID INT,
    InstrumentID INT,
    PRIMARY KEY (ResearcherID, InstrumentID),
    FOREIGN KEY (ResearcherID) REFERENCES RESEARCHERS(ResearcherID),
    FOREIGN KEY (InstrumentID) REFERENCES INSTRUMENTS(InstrumentID)
);

-- 9. RESEARCHSTUDIES (FKs -> RESEARCHERS, CELESTIALOBJECTS)
CREATE TABLE RESEARCHSTUDIES (
    ResearcherID INT,
    ObjectID INT,
    Role VARCHAR(50),
    PRIMARY KEY (ResearcherID, ObjectID),
    FOREIGN KEY (ResearcherID) REFERENCES RESEARCHERS(ResearcherID),
    FOREIGN KEY (ObjectID) REFERENCES CELESTIALOBJECTS(ObjectID)
);


-- 4. LEVEL 3 DEPENDENT TABLES
-- 10. OBSERVATIONS (FKs -> OBSERVATIONSESSIONS, CELESTIALOBJECTS)
CREATE TABLE OBSERVATIONS (
    ObservationID INT PRIMARY KEY,
    SessionID INT,
    ObjectID INT,
    DurationMinutes INT CHECK (DurationMinutes > 0),
    Notes TEXT,
    AcquisitionTime TIME,
    DataQualityRating INT,
    FOREIGN KEY (SessionID) REFERENCES OBSERVATIONSESSIONS(SessionID),
    FOREIGN KEY (ObjectID) REFERENCES CELESTIALOBJECTS(ObjectID)
);

-- 11. OBSERVATION_LOG (FK -> OBSERVATIONS)
CREATE TABLE OBSERVATION_LOG (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    ObservationID INT,
    ChangeType VARCHAR(10) NOT NULL,
    ChangeTimestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    OldDataQuality INT,
    FOREIGN KEY (ObservationID) REFERENCES OBSERVATIONS(ObservationID)
);


-- DML for RESEARCHERS (10 Records)
INSERT INTO RESEARCHERS (ResearcherID, Name, Institution, Email, DOB, InitialExperience) VALUES
(1, 'Dr. Amelia Jones', 'PESU Astro Lab', 'jones@pesu.edu', '1978-08-15', 15),
(2, 'Dr. Elias Vance', 'Stellar Dynamics Inst.', 'vance@dynamics.org', '1990-03-22', 8),
(3, 'Dr. Cai Rourke', 'Nebula Research Group', 'rourke@galaxy.com', '1982-11-01', 12),
(4, 'Prof. D. Schmidt', 'Max Planck Institute', 'schmidt@univ.edu', '1970-05-10', 25),
(5, 'S. Kaur (PhD Cand.)', 'PESU Astro Lab', 'kaur@pesu.edu', '1995-07-01', 3),
(6, 'Dr. M. Singh', 'Indian Institute of Space', 'singh@iis.in', '1980-01-15', 18),
(7, 'R. Gupta (MSc)', 'Advanced Tech Center', 'gupta@tech.org', '1992-06-20', 5),
(8, 'Dr. J. Chen', 'Beijing Observatory', 'chen@china.edu', '1975-10-25', 20),
(9, 'L. Brown', 'NASA JPL', 'brown@nasa.gov', '1988-12-05', 10),
(10, 'A. Perez', 'Complutense Univ.', 'perez@spain.es', '1998-04-12', 7);

-- DML for TELESCOPES (10 Records)
INSERT INTO TELESCOPES (TelescopeID, Name, Location, ApertureSize, PrimaryMirrorMaterial, MountType) VALUES
(101, 'Kepler''s Eye', 'Chile, Atacama', 4.0, 'Zerodur Glass', 'Altazimuth'),
(102, 'Chronos Transit', 'Hawaii, Mauna Kea', 8.1, 'Fused Silica', 'Equatorial'),
(103, 'VISTA', 'Chile, Paranal', 4.1, 'Zerodur Glass', 'Altazimuth'),
(104, 'Arecibo (Radio)', 'Puerto Rico', 305.0, 'Aluminum', 'Fixed Reflector'),
(105, 'MeerKAT Array', 'South Africa', 13.5, 'Steel', 'Altazimuth'),
(106, 'SALT', 'South Africa', 11.0, 'Borosilicate', 'Fixed-Altitude'),
(107, 'Hubble (Simulated)', 'Orbit', 2.4, 'Fused Silica', 'Equatorial'),
(108, 'Lick 1m', 'California', 1.0, 'Glass', 'Equatorial'),
(109, 'ALMA Array (Sim.)', 'Chile', 0.5, 'Aluminum', 'Altazimuth'),
(110, 'James Webb (Sim.)', 'Orbit', 6.5, 'Beryllium', 'Equatorial');

-- DML for CELESTIALOBJECTS (12 Records)
INSERT INTO CELESTIALOBJECTS (ObjectID, ObjectName, ObjectType, Magnitude, RightAscension, Declination, LastObservedDate, Distance_Parsecs, Redshift, Diameter_km, Mass_SolarMass) VALUES
(1001, 'Andromeda Galaxy', 'Galaxy', 3.40, '00h 42m 44s', '+41d 16m 09s', '2025-01-20', 780000.0, 0.001, 2.2e18, 1.5e12),
(1002, 'Barnard''s Star', 'Star', 9.54, '17h 57m 48s', '+04d 21m 36s', '2024-11-10', 1.82, 0.000002, 120000.0, 0.14),
(1003, 'Crab Nebula', 'Nebula', 8.4, '05h 34m 31s', '+22d 00m 52s', '2025-05-01', 2000.0, 0.005, 1.1e15, 10.0),
(1004, 'Proxima Centauri', 'Star', 11.05, '14h 29m 43s', '-62d 40m 46s', '2025-08-01', 1.30, 0.0000007, 200000.0, 0.12),
(1005, 'Quasar 3C 273', 'Quasar', 12.9, '12h 29m 06s', '+02d 03m 08s', '2024-12-15', 7.4e8, 0.158, 1.0e15, 8.0e8),
(1006, 'Cygnus X-1', 'Black Hole', 8.9, '00h 42m 44s', '+41d 16m 09s', '2025-08-20', 2200.0, 0.0002, 60.0, 21.0),
(1007, 'M87', 'Galaxy', 9.6, '12h 30m 49s', '+12d 23m 28s', '2024-10-10', 1.6e7, 0.004, 3.0e18, 6.0e12),
(1008, 'Sirius A/B', 'Binary Star', -1.46, '06h 45m 08s', '-16d 42m 58s', '2025-09-01', 2.64, 0.0000002, 2.4e6, 2.02),
(1009, 'Alpha Centauri A', 'Star', 0.01, '14h 39m 36s', '-60d 50m 02s', '2025-09-10', 1.34, 0.000007, 1.7e6, 1.10),
(1010, 'Orion Nebula (M42)', 'Nebula', 4.0, '05h 35m 17s', '-05d 23m 28s', '2025-08-05', 412.0, 0.00008, 2.4e14, 2000.0),
(1011, 'Betelgeuse', 'Star', 0.5, '05h 55m 10s', '+07d 24m 25s', '2025-07-25', 197.0, 0.00007, 1.2e9, 15.0),
(1012, 'Triangulum Galaxy', 'Galaxy', 5.7, '01h 33m 50s', '+30d 39m 36s', '2024-09-01', 850000.0, 0.0005, 3.0e18, 5.0e10);

-- DML for INSTRUMENTS (10 Records)
INSERT INTO INSTRUMENTS (InstrumentID, TelescopeID, Name, Type, WavelengthRange, Resolution) VALUES
(301, 102, 'Chronos Spectrometer', 'Spectrometer', 'Visible/IR', 'High'),
(302, 101, 'Kepler''s Imager', 'Camera', 'Visible', 'Ultra-High'),
(303, 102, 'Chronos Photometer', 'Photometer', 'Visible', 'Medium'),
(304, 103, 'VISTA IR Cam', 'Camera', 'Infrared (IR)', 'High'),
(305, 103, 'VISTA Spectro', 'Spectrometer', 'Near-IR', 'Medium'),
(306, 108, 'Lick CCD', 'Camera', 'Visible', 'Medium'),
(307, 107, 'Hubble UV Imager', 'Camera', 'Ultraviolet (UV)', 'Ultra-High'),
(308, 106, 'SALTICAM', 'Camera', 'Visible', 'High'),
(309, 109, 'ALMA Receiver 3', 'Receiver', 'Radio', 'High'),
(310, 110, 'NIRSpec', 'Spectrometer', 'Near-Infrared', 'Ultra-High');

-- DML for OBJECTDISCOVERY (10 Records)
INSERT INTO OBJECTDISCOVERY (ObjectID, DiscovererName, DiscoveryDate) VALUES
(1001, 'Charles Messier', '1764-08-03'), (1003, 'Galileo Galilei', '1604-07-04'),
(1005, 'Cyril Hazard', '1963-01-14'), (1006, 'Louise Webster', '1972-04-18'),
(1007, 'Edwin Hubble', '1934-01-01'), (1008, 'Friedrich Bessel', '1844-01-01'),
(1010, 'Charles Messier', '1774-03-04'), (1011, 'Johann Bayer', '1603-01-01'),
(1012, 'Charles Messier', '1764-09-11'), (1002, 'Robert P. Aitken', '1916-01-01');

-- DML for OBSERVATIONSESSIONS (10 Records)
INSERT INTO OBSERVATIONSESSIONS (SessionID, Date, WeatherCondition, SeeingCondition, ResearcherID, TelescopeID) VALUES
(1, '2025-09-01', 'Clear', 'Excellent', 1, 102), (2, '2025-09-05', 'Cloudy', 'Poor', 3, 101),
(3, '2025-09-10', 'Good', 'Good', 1, 108), (4, '2025-09-11', 'Clear', 'Good', 2, 108),
(5, '2025-09-12', 'Clear', 'Good', 2, 108), (6, '2025-09-13', 'Clear', 'Good', 2, 108),
(7, '2025-09-14', 'Clear', 'Good', 2, 108), (8, '2025-09-15', 'Clear', 'Good', 2, 108),
(9, '2025-09-16', 'Excellent', 'Excellent', 4, 102), (10, '2025-09-17', 'Fair', 'Fair', 5, 102);

-- DML for OBSERVATIONS (15 Records)
INSERT INTO OBSERVATIONS (ObservationID, SessionID, ObjectID, DurationMinutes, Notes, AcquisitionTime, DataQualityRating) VALUES
(201, 1, 1001, 120, 'Deep Andromeda image.', '20:00:00', 5), (202, 2, 1006, 90, 'Cygnus X-1 spectroscopy, poor signal.', '22:30:00', 2),
(203, 3, 1003, 60, 'Crab Nebula transit.', '21:00:00', 4), (204, 4, 1004, 30, 'Proxima Centauri attempt 1.', '20:00:00', 5),
(205, 5, 1008, 30, 'Sirius A/B photometry.', '20:00:00', 5), (206, 6, 1009, 30, 'Alpha Centauri A attempt 1.', '20:00:00', 5),
(207, 7, 1010, 30, 'Orion Nebula wide field.', '20:00:00', 5), (208, 8, 1011, 30, 'Betelgeuse magnitude check.', '20:00:00', 5),
(209, 9, 1001, 10, 'Andromeda quick check.', '20:00:00', 4), (210, 10, 1005, 15, 'Quasar 3C 273 flux.', '20:00:00', 3),
(211, 1, 1009, 50, 'Alpha Centauri A attempt 2.', '20:00:00', 5), (212, 3, 1012, 10, 'Triangulum Galaxy transit.', '20:00:00', 4),
(213, 4, 1008, 20, 'Sirius A/B check 2.', '20:00:00', 5), (214, 5, 1009, 20, 'Alpha Centauri A check 3.', '20:00:00', 5),
(215, 6, 1008, 20, 'Sirius A/B check 3.', '20:00:00', 5);

-- DML for RESEARCHERPHONES (10 Records)
INSERT INTO RESEARCHERPHONES (ResearcherID, PhoneNumber) VALUES (1, '555-1010'), (2, '555-2020'), (3, '555-3030'), (4, '555-4040'), (5, '555-5050'), (6, '555-6060'), (7, '555-7070'), (8, '555-8080'), (9, '555-9090'), (10, '555-1111');

-- DML for RESEARCHERINSTRUMENTS (M:N Link)
INSERT INTO RESEARCHERINSTRUMENTS (ResearcherID, InstrumentID) VALUES (1, 301), (2, 302), (3, 303), (4, 304), (5, 305), (6, 306), (7, 307), (8, 308), (9, 309), (10, 310);

-- DML for RESEARCHSTUDIES (M:N Link)
INSERT INTO RESEARCHSTUDIES (ResearcherID, ObjectID, Role) VALUES (1, 1001, 'PI'), (2, 1004, 'Co-I'), (3, 1006, 'Lead'), (4, 1007, 'PI'), (5, 1008, 'Co-I'), (6, 1009, 'Lead'), (7, 1010, 'PI'), (8, 1011, 'Co-I'), (9, 1012, 'Lead'), (10, 1005, 'PI');






"
-- Function 1: Calculate Effective Magnitude
-- Used to convert measured magnitude (Magnitude) into an effective one based on Redshift (a complex calculation).

DELIMITER //
CREATE FUNCTION calculate_effective_magnitude (
    mag_in FLOAT,
    redshift_in FLOAT
)
RETURNS FLOAT READS SQL DATA
BEGIN
    DECLARE effective_mag FLOAT;
    -- Formula: Effective Mag = Apparent Mag + 5 * LOG10(Redshift * 1000)
    -- This calculation simulates a K-correction or similar luminosity adjustment.
    SET effective_mag = mag_in + (5 * LOG10(redshift_in * 1000.0));
    RETURN effective_mag;
END //
DELIMITER ;

-- Test Query:
-- SELECT calculate_effective_magnitude(12.9, 0.158); -- Uses Quasar 3C 273 data (ObjectID 1005)


-- Function 2: Get Telescope Utilization Hours
-- Returns the total hours a telescope (by ID) has been used.

DELIMITER //
CREATE FUNCTION get_telescope_utilization_hours (
    telescope_id_in INT
)
RETURNS FLOAT READS SQL DATA
BEGIN
    DECLARE total_minutes INT;
    DECLARE total_hours FLOAT;

    SELECT SUM(O.DurationMinutes) INTO total_minutes
    FROM OBSERVATIONSESSIONS AS OS
    JOIN OBSERVATIONS AS O ON OS.SessionID = O.SessionID
    WHERE OS.TelescopeID = telescope_id_in;

    SET total_hours = IFNULL(total_minutes, 0) / 60.0;
    RETURN total_hours;
END //
DELIMITER ;

-- Test Query:
-- SELECT get_telescope_utilization_hours(108); -- Should return (60+30+30+30+30+20+20) / 60 = 3.167 hours



-- Procedure 1: Update Researcher Total Time
-- Calculates and updates the aggregated observation time for a given researcher ID.

DELIMITER //
CREATE PROCEDURE update_researcher_total_time (
    IN researcher_id_in INT
)
BEGIN
    DECLARE total_minutes INT;

    -- 1. Calculate sum of observation minutes for the researcher
    SELECT SUM(O.DurationMinutes) INTO total_minutes
    FROM OBSERVATIONS AS O
    JOIN OBSERVATIONSESSIONS AS OS ON O.SessionID = OS.SessionID
    WHERE OS.ResearcherID = researcher_id_in;

    -- 2. Update the dedicated column in the RESEARCHERS table
    UPDATE RESEARCHERS
    SET TotalObservationMinutes = IFNULL(total_minutes, 0)
    WHERE ResearcherID = researcher_id_in;
END //
DELIMITER ;

-- Execution Example (Run after DML):
-- CALL update_researcher_total_time(2); -- Researcher 2 had sessions 4, 5, 6, 7, 8 (30*5 + 20*2 = 190 min)
-- SELECT ResearcherID, TotalObservationMinutes FROM RESEARCHERS WHERE ResearcherID = 2;


-- Procedure 2: Archive Old Observations (Data Management)
-- Finds and removes/archives observations older than a specific date and with a low quality rating.

DELIMITER //
CREATE PROCEDURE archive_old_observations (
    IN cutoff_date DATE,
    IN min_quality_rating INT
)
BEGIN
    -- NOTE: In a real database, you would INSERT INTO Archive_Table SELECT... before deleting.
    
    DELETE FROM OBSERVATIONS
    WHERE DataQualityRating < min_quality_rating
    AND ObservationID IN (
        SELECT O.ObservationID
        FROM OBSERVATIONS AS O
        JOIN OBSERVATIONSESSIONS AS OS ON O.SessionID = OS.SessionID
        WHERE OS.Date < cutoff_date
    );
    -- Log the action (optional, but good practice)
    SELECT ROW_COUNT() AS Rows_Archived;
END //
DELIMITER ;

-- Execution Example:
-- CALL archive_old_observations('2025-09-02', 3); -- Should remove ObsID 202 (Date 2025-09-05, Rating 2)



-- Trigger 1: Log Data Quality Rating updates (Audit Trail)
-- Fires AFTER an UPDATE on the OBSERVATIONS table.

DELIMITER //
CREATE TRIGGER trg_log_data_quality_update
AFTER UPDATE ON OBSERVATIONS
FOR EACH ROW
BEGIN
    IF OLD.DataQualityRating <> NEW.DataQualityRating THEN
        INSERT INTO OBSERVATION_LOG (ObservationID, ChangeType, OldDataQuality)
        VALUES (NEW.ObservationID, 'UPDATE', OLD.DataQualityRating);
    END IF;
END //
DELIMITER ;

-- Test Action:
-- UPDATE OBSERVATIONS SET DataQualityRating = 5 WHERE ObservationID = 202;
-- SELECT * FROM OBSERVATION_LOG; -- Should show the logged change.


-- Trigger 2: Update Last Observed Date (Data Consistency)
-- Fires AFTER an INSERT into the OBSERVATIONS table.

DELIMITER //
CREATE TRIGGER trg_update_last_observed_date
AFTER INSERT ON OBSERVATIONS
FOR EACH ROW
BEGIN
    -- Get the date of the new observation session
    DECLARE session_date DATE;
    SELECT Date INTO session_date
    FROM OBSERVATIONSESSIONS
    WHERE SessionID = NEW.SessionID;

    -- Update the CELESTIALOBJECTS table with the latest date
    UPDATE CELESTIALOBJECTS
    SET LastObservedDate = session_date
    WHERE ObjectID = NEW.ObjectID
    AND LastObservedDate < session_date; -- Only update if the new date is later
END //
DELIMITER ;
"
-- Test Action:
-- INSERT INTO OBSERVATIONSESSIONS (SessionID, Date, ResearcherID, TelescopeID) VALUES (11, '2026-01-01', 1, 102);
-- INSERT INTO OBSERVATIONS (ObservationID, SessionID, ObjectID, DurationMinutes, DataQualityRating) VALUES (216, 11, 1001, 10, 5);
-- SELECT ObjectName, LastObservedDate FROM CELESTIALOBJECTS WHERE ObjectID = 1001; -- Should show '2026-01-01'
