import main

import mysql.connector

#Database connection created
conn = mysql.connector.connect(
    host="localhost",
    database="hrms",
    user="root",
    password="" )

mycursor = conn.cursor(buffered=True)

"""
Infinite While loop is created that continuously checkes where colum resume_parsed has any False value. If there is not any matching
value, the loop will terminate else it will extract the resume name and join it with s3 bucket path to extract data from that resume.
After extracting data from resume it will update value to hrms_candidates table. and set resume_parsed value True.

"""
parsed = True

while parsed:
    #fetch id and resume column from tabel
    mycursor.execute("SELECT id, resume FROM hrms_candidates WHERE resume_parsed = FALSE" ) 
    # Fetch pending records 
    pending_resume = mycursor.fetchone()

    #Ckeck if any pending records
    if pending_resume is None:
        parsed = False

    else:
        # extract resume id from table
        resume_id = str(pending_resume[0])
        print("---------- calling Resume ---------- ", pending_resume[1])
        
        print("---------- Extracting Data ----------")
        resume_prefix = "https://wappnet-systems.s3.amazonaws.com/public/hrms/"   
        s3_path = resume_prefix + pending_resume[1]  #create s3 bucket link of resume
        data = main.resume_data(s3_path)  #Extract data from resume and store it

        # extract required table data to update in table
    
        data = {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": data.get("email"),
            "mobile": data.get("mobile"),
            "skills": data.get("skills"),
            "experience_details": data.get("experience_details"),
            "educational_details": data.get("educational_details"),
            "resume_id": resume_id,
        }

        # Update the parsed data to the table
        sql = """
            UPDATE hrms_candidates 
            SET 
                first_name = %(first_name)s,
                last_name = %(last_name)s,
                email = %(email)s,
                mobile = %(mobile)s,
                skills = %(skills)s, 
                experience_details = %(experience_details)s,
                educational_details = %(educational_details)s,     
                resume_parsed = TRUE
            WHERE 
                id = %(resume_id)s
            """
        mycursor.execute(sql,data)  # execute query to update records
        conn.commit() #update changes in table

# Close the database connection
mycursor.close()
conn.close()
