# This script uses the time window tables to compute the similarity
# between patients (within the database) and then dumps to file that
# can be analyzed in Matlab 

# Import
import pyodbc

# Connect to DB
cnxn = pyodbc.connect( "DRIVER={Vertica};SERVER=localhost;" + \
                           "DATABASE=i2b2tools;"+ \
                           "UID=autism_urop;PWD=B4y3s4tw" )
cursor = cnxn.cursor()

# ---- Preparation ---- #
# Join the NLP and the ICD tables into one table 
cursor.execute("DROP TABLE IF EXISTS time_window_table" )
cursor.execute("""
SELECT patient_id , cui , time_window , sum( total_count ) as total_count  
INTO time_window_table 
FROM ( SELECT patient_id , cui , time_window , total_count 
       FROM time_window_table_nlp 
       UNION ALL 
       SELECT patient_id , cui , time_window , total_count 
       FROM time_window_table_icd ) concat 
WHERE time_window > 0 
GROUP BY cui , time_window , patient_id 
ORDER BY cui , time_window , patient_id , total_count 
""")

# Finale! this is a hack!) Add a row to the table that everyone has,
# so we'll get a full join of things
for row in cursor.execute("SELECT DISTINCT( patient_id ) FROM time_window_table").fetchall():
    cursor.execute("""
INSERT INTO time_window_table 
( patient_id , cui , time_window , total_count ) 
VALUES ( """ + row[0] + """, 'None' , -1 , 0 )""" )
cursor.execute( "COMMIT" )

# ---- Compute Similarities ---- #
max_count_list = [ 1 , 50 , 1000000 ]
for max_count in max_count_list:
    print 'On max count ' , max_count
    cursor.execute("DROP TABLE IF EXISTS similarity_table_L2_maxcount" + str( max_count ) )
    cursor.execute("DROP TABLE IF EXISTS censor_table" )
    cursor.execute("""
SELECT patient_id , cui , time_window , total_count 
INTO censor_table 
FROM time_window_table 
""")
    cursor.execute("""
UPDATE censor_table 
SET total_count = """ + str( max_count ) + """
WHERE total_count > """ + str( max_count ) + """  
""")
    cursor.execute( "COMMIT" )
    cursor.execute("""
SELECT patient_id1 , patient_id2 , distance 
INTO similarity_table_L2_maxcount""" + str( max_count ) + """  
FROM (
    SELECT patient_id1 , patient_id2 ,
    ( squares1.sum_square_value + diffs.diff + squares2.sum_square_value ) as distance 
    FROM
       ( SELECT source.patient_id as patient_id1 ,
                destination.patient_id as patient_id2,
                sum( -2 * source.total_count * destination.total_count ) as diff
                FROM censor_table source
                JOIN censor_table destination
                  ON source.cui = destination.cui
                     AND source.time_window = destination.time_window 
                     AND source.patient_id != destination.patient_id
                GROUP BY patient_id1 , patient_id2
                ORDER BY patient_id1 , patient_id2 ) diffs
       JOIN ( SELECT patient_id , sum( total_count * total_count ) AS sum_square_value
              FROM censor_table GROUP BY patient_id) squares1
         ON squares1.patient_id = diffs.patient_id1
       JOIN ( SELECT patient_id , sum( total_count * total_count ) AS sum_square_value
              FROM censor_table GROUP BY patient_id ) squares2
         ON squares2.patient_id = diffs.patient_id2
  ) all_distances
ORDER BY patient_id1 , distance
""")

# --- Dump --- #
for max_count in max_count_list:
    print 'Dumping max count ' , max_count
    out_fid = open( 'out' + str( max_count ) + '.txt' , 'w' )
    cursor.execute("""
SELECT patient_id1 , patient_id2 , distance 
FROM similarity_table_L2_maxcount""" + str( max_count ) + """  
""")
    row_set = cursor.fetchall()
    for row in row_set:
        out_fid.write( str( row.patient_id1 ) + ' ' + str( row.patient_id2 ) + ' ' + str( row.distance ) + '\n' )
    out_fid.close()

# clean up
cursor.execute("DROP TABLE IF EXISTS time_window_table" )
cursor.execute("DROP TABLE IF EXISTS censor_table" )
for max_count in max_count_list:
    cursor.execute("DROP TABLE IF EXISTS similarity_table_L2_maxcount" + str( max_count ) )
