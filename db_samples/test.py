min_age = 15
min_visit_count = 4

cursor.execute("DROP TABLE IF EXISTS joy_visits_table")
cursor.execute("""
      SELECT DISTINCT chb_icd9_table.date, chb_demographics_table.patient_id,
              chb_demographics_table.row_id
      INTO joy_visits_table
      FROM chb_demographics_table
      INNER JOIN chb_icd9_table  
      ON chb_icd9_table.patient_id=chb_demographics_table.patient_id 
""")

cursor.execute("DROP TABLE IF EXISTS joy_patients_table")
cursor.execute( """
SELECT chb_demographics_table.patient_id, joy_visits_table.row_id INTO joy_patients_table 
FROM chb_demographics_table 
INNER JOIN joy_visits_table 
 ON joy_visits_table.patient_id = chb_demographics_table.patient_id 
WHERE 
 datediff( 'day' , chb_demographics_table.birth_date , '2012-03-01' ) < """ + str( min_age ) + """ 
AND 
 joy_visits_table.visit_count > """ + str( min_visit_count ) + """
""")

patients = cursor.execute("SELECT DISTINCT patient_id from joy_patients_table")
print 'n patients', len(patients)

cursor.execute("DROP TABLE IF EXISTS joy_posts_table")
cursor.execute("""
SELECT patient_num, cui_cd, mrconso.STR, MAX(mrconso.SUI), start_date
FROM chb_nlp_snomed_table 
INNER JOIN mrconso 
        ON chb_nlp_snomed_table.cui_cd = mrconso.CUI
	INNER JOIN joy_patients_table
       ON chb_nlp_snomed_table.patient_num = joy_patients_table.row_id
INTO joy_posts_table
""")

posts = cursor.execute("SELECT * from joy_posts_table")
print 'n posts', len(posts)

cursor.execute("DROP TABLE IF EXISTS joy_visits_table")
cursor.execute("DROP TABLE IF EXISTS joy_patients_table")
cursor.execute("DROP TABLE IF EXISTS joy_posts_table")