# This script pulls data from the NLP/other tables and dumps it into a
# format for all the other analyses.  This should be the only script
# that applies filters in the database.  All other scripts that touch
# the database should only touch the tables
#
# * time_window_table_nlp
#
# * time_window_table_icd
#
# That way, we can make sure that all of the analysis that occurs
# afterward is using the same core set of data, and the differences in
# the outputs of the analysis are due to differences in the analysis
# and not due to differences in the input/filters.

# ---- Filters on the data ---- #
# The minimum age for a patient
min_age = 365.25 * 15;

# Number of unique dates that we must have within 0 to min_age
min_visit_count = 4;

# How many time-windows to split the data
age_window = 365.25 * .5;
max_time_window = round( min_age / age_window );

# Are there codes to ignore?  The table "ignore" in the db was
# hand-created by Susan and Pete to leave out things that we know are
# bugs (e.g. some of the cancer codes)
use_ignore = True

# Include negations?
use_negations = False

# Include family history?
use_family_history = False

# Include past history?
use_history = False

# Include probable status?
use_probable = False

# ---- Initializations ---- #
# Imports
import pyodbc

# Connect to DB
cnxn = pyodbc.connect( "DRIVER={Vertica};SERVER=localhost;" + \
                           "DATABASE=i2b2tools;"+ \
                           "UID=autism_urop;PWD=B4y3s4tw" )
cursor = cnxn.cursor()

# ---- Processing ---- #
# Compute number of visits using just the ICD9 table -- this should be
# okay because every visit should generate an ICD9 for billing, and we
# only care about the number of unique dates
cursor.execute("DROP TABLE IF EXISTS visit_table" )
cursor.execute("""
SELECT chb_demographics_table.patient_id , 
  COUNT( DISTINCT chb_icd9_table.date ) as visit_count 
INTO visit_table 
FROM chb_demographics_table
INNER JOIN chb_icd9_table  
ON chb_icd9_table.patient_id=chb_demographics_table.patient_id 
WHERE datediff( 'day' ,  chb_demographics_table.birth_date, chb_icd9_table.date ) < """ + str( min_age ) + """ 
GROUP BY chb_demographics_table.patient_id 
""")

# Collect all the patients that we want to include
cursor.execute( "DROP TABLE IF EXISTS patient_cohort_table" )
cursor.execute( """
SELECT chb_demographics_table.patient_id INTO patient_cohort_table  
FROM chb_demographics_table 
INNER JOIN visit_table 
  ON visit_table.patient_id = chb_demographics_table.patient_id 
WHERE 
  datediff( 'day' , chb_demographics_table.birth_date , '2012-03-01' ) < """ + str( min_age ) + """ 
AND 
  visit_table.visit_count > """ + str( min_visit_count ) + """

""")

# Time windows: right now, we create separate time-window tables for
# the ICD9s and for the SNOMEDs so we can compare... everything is
# converted into CUIs so we can easily combine the two tables in
# down-stream analyses.
cursor.execute("DROP TABLE IF EXISTS time_window_table_nlp" )
nlp_call = """
SELECT chb_nlp_snomed_table.patient_num , chb_nlp_snomed_table.cui_cd , ceil( datediff( 'day' , chb_demographics_table.birth_date , chb_nlp_snomed_table.start_date ) / """ + str( age_window ) + """) AS time_window , count( 0 ) AS total_count  
INTO time_window_table_nlp 
FROM chb_nlp_snomed_table
JOIN chb_demographics_table 
  ON chb_nlp_snomed_table.patient_num = chb_demographics_table.patient_id 
JOIN patient_cohort_table 
  ON patient_cohort_table.patient_id = chb_nlp_snomed_table.patient_num
JOIN mrsty
  ON mrsty.cui = chb_nlp_snomed_table.cui_cd
WHERE 
  ceil( datediff( 'day' , chb_demographics_table.birth_date , chb_nlp_snomed_table.start_date ) / """ + str( age_window ) + """) <= """ + str( max_time_window ) + """
AND 
  mrsty.sty in ('Pathologic Function', 'Disease or Syndrome', 'Mental or Behavioral Dysfunction', 'Neoplastic Process', 'Cell or Molecular Dysfunction','Experimental Model of Disease', 'Finding', 'Laboratory or Test Result', 'Sign or Symptom','Clinical Attribute', 'Clinical Drug', 'Anatomical Abnormality', 'Congenital Abnormality', 'Acquired Abnormality','Behavior', 'Social Behavior', 'Individual Behavior', 'Injury of Poisoning','Biologically Active Substance', 'Neuroreactive Substance or Biogenic Amine', 'Hormone', 'Enzyme', 'Vitamin', 'Immunologic Factor', 'Receptor')
"""
if use_ignore:
    nlp_call = nlp_call + """ AND chb_nlp_snomed_table.cui_cd not in ( Select cui from Ignore ) """
if not use_negations:
    nlp_call = nlp_call + """ AND chb_nlp_snomed_table.concept_polarity = 0 """
if not use_family_history:
    nlp_call = nlp_call + """ AND chb_nlp_snomed_table.concept_status != 2 """
if not use_history:
    nlp_call = nlp_call + """ AND chb_nlp_snomed_table.concept_status != 1 """
if not use_probable:
    nlp_call = nlp_call + """ AND chb_nlp_snomed_table.concept_status != 3 """
nlp_call = nlp_call + """
GROUP BY chb_nlp_snomed_table.cui_cd , time_window , chb_nlp_snomed_table.patient_num 
ORDER BY chb_nlp_snomed_table.cui_cd , time_window , chb_nlp_snomed_table.patient_num , total_count 
"""
cursor.execute( nlp_call )

# Create a temporary table with the time windows ONLY for patients
# that match the criteria for the ICD-9 codes
cursor.execute("DROP TABLE IF EXISTS time_window_table_icd" )
cursor.execute("""
SELECT chb_icd9_table.patient_id ,
  ceil( datediff( 'day' , chb_demographics_table.birth_date , chb_icd9_table.date ) / """ + str( age_window ) + """) AS time_window ,
  cui , count( 0 ) AS total_count  
INTO time_window_table_icd
FROM chb_icd9_table 
JOIN chb_demographics_table 
  ON chb_icd9_table.patient_id = chb_demographics_table.patient_id 
JOIN patient_cohort_table 
  ON patient_cohort_table.patient_id = chb_icd9_table.patient_id
JOIN mrconso 
  ON mrconso.CODE = chb_icd9_table.icd9 
WHERE ceil( datediff( 'day' , chb_demographics_table.birth_date , chb_icd9_table.date ) / """ + str( age_window ) + """) <= """ + str( max_time_window ) + """
  AND mrconso.SAB = 'ICD9CM' 
  AND mrconso.ISPREF= 'Y'
  AND mrconso.STT = 'PF'
  AND mrconso.TTY = 'PT'
GROUP BY cui , time_window , chb_icd9_table.patient_id 
ORDER BY cui , time_window , chb_icd9_table.patient_id , total_count 
""")

# clean up
cursor.execute( "DROP TABLE IF EXISTS patient_cohort_table" )
cursor.execute("DROP TABLE IF EXISTS visit_table" )
# cursor.execute("DROP TABLE IF EXISTS time_window_table_icd" )
# cursor.execute("DROP TABLE IF EXISTS time_window_table_nlp" )
