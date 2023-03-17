# Batch-grading-for-Coding-Course
used to complement the grading file of each lab and run a batch student grading script on all students at once. Made as a teaching assistant for first year python course.
May not be used outside carleton university without permission.


To use the multiple tests grading script follow these steps:
1. Download student submissions from brightspace as a batch
2. add run_grading_multiple_tests.py into a folder containing student submission folders (keep them in the zip file you downloaded)
3. add a folder with all grading scripts and their additional data files to the folder
4. rename the strings between line 33 to 41 in the following region  

       LAB_NAME_GRADING_SOFTWARE_INDEX = {'student_age_list': 'student_age_list_test',
                                          'student_failures_list': 'student_failures_list_test',
                                          'student_health_list': 'student_health_list_test',
                                          'student_school_list': 'student_school_list_test'}  # Add lab name, and its associated grading software, DO NOT ADD .py
       SAVE_GRADES_TO = 'labx_Grades.csv'
       GRADES_CSV_HEADER = 'Lab x Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>'
       SCORE_CODE = 'round(passes / result.testsRun * 4, 2)'  # Code used to calculate score (copy from grading file)
       GRADING_MATERIAL_LOCATION = 'grading material'  # The name of the folder that contains the grading script
       FEEDBACK_ZIP_FOLDER_NAME = 'feedback for brightspace'  # Name of folder to which student feedback will be zipped into
 
5. run run_grading_multiple_tests.py, this will add feedback to students .py file and add FEEDBACK_ to the beggining of the name, you can zip them up and reupload them to brightspace as a batch but DO NOT CHANGE ANY STUDENT'S FOLDERS NAME or brightspace will not be able to read it.
7. DO NOT RERUN THE CODE OR IT WILL GIVE STUDENTS A 0 AS THE FILES HAVE NOW BEEN RENAMED OR COMPRESSED
8. The code will now generate a folder to upload to brightspace
9. The code will also generate a CSV file in brightspace format, you must however ensure that GRADES_CSV_HEADER is set to the proper brightspace format name.

Your setup to grade should look like this:


![image](https://user-images.githubusercontent.com/19933465/225781343-ef46e279-efd6-4eec-993e-64f5da4da48e.png)


-------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------

To use the single test grading script follow these steps:
1. Download student submissions from brightspace as a batch
2. add run_grading.py into a folder containing student submission folders
3. add grading script to folder
4. rename the strings between line 25 to 30 in the following region  
       
       LAB_NAME = 'labX' # DO NOT ADD .py
       LAB_GRADING_SOFTWARE_NAME = 'grade_lab_X.py'
       SAVE_GRADES_TO = 'filename.csv '
       GRADES_CSV_HEADER = 'Lab X Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>'
       
5. run run_grading.py, this will add feedback to students .py file, you can zip them up and reupload them to brightspace as a batch but DO NOT CHANGE ANY STUDENT'S FOLDERS NAME or brightspace will not be able to read it.
6. The code will also generate a CSV file in brightspace format, you must however ensure that GRADES_CSV_HEADER is set to the proper brightspace format name.
