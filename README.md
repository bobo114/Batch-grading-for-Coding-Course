# Batch-grading-for-Coding-Course
used to complement the grading file of each lab and run a batch student grading script on all students at once. Made as a teaching assistant for first year python course.
May not be used outside carleton university without permission.

To use follow these steps:
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
