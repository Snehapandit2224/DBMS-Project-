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

-- Test Action:
-- INSERT INTO OBSERVATIONSESSIONS (SessionID, Date, ResearcherID, TelescopeID) VALUES (11, '2026-01-01', 1, 102);
-- INSERT INTO OBSERVATIONS (ObservationID, SessionID, ObjectID, DurationMinutes, DataQualityRating) VALUES (216, 11, 1001, 10, 5);
-- SELECT ObjectName, LastObservedDate FROM CELESTIALOBJECTS WHERE ObjectID = 1001; -- Should show '2026-01-01'