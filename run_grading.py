"""
ECOR 1041/1042 batch grading file, easily modifiable to the individual lab grading files created by course instructors

Designed to add feedback to each students file based on grading file output. Checks for matching student numbers based
on D2L brightspace format. Lastly will create a CSV document in D2L format to upload student grades.

Any erroneous submissions will be reported in the console as error to the user and will inform you of student name, ID
and folder name
"""
from os import listdir, system
import sys
import os
import shutil
import time
import importlib
import pathlib
import csv
import logging
import grade_lab_4
from grade_lab_4 import *


__author__ = "Boaz Aharony"
__copyright__ = "Copyright 2023, Boaz Aharony"
__maintainer__ = "Boaz Aharony"
__email__ = "boazaharony@cmail.carleton.ca"
__status__ = "Dev"



LAB_NAME = 'lab4'
SAVE_GRADES_TO = 'Merge ECOR1041EECOR1041FECOR1041GECOR1041H Computation and Programming (LEC) [12024120251202612027] Winter 2023_Grades.csv'
GRADES_CSV_HEADER = 'Lab 4 Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>'

# print to txt file to read it after
original_stdout = sys.stdout
original_stderr = sys.stderr


def filter_folders(names: list):
    """Filters given folder name list to only folders formatted as student downloads
    """
    temp_names = names.copy()
    for filename in temp_names:
        if not ('0' <= filename[0] <= '9'):
            names.remove(filename)


def copy_outside(folder: str):
    """Copy lab folder outside
    """
    src_folder = os.path.abspath(os.getcwd()) + '\\' + folder
    dst_folder = os.path.abspath(os.getcwd())

    # file names
    src_file = src_folder + "\\" + LAB_NAME + ".py"
    dst_file = dst_folder + "\\" + LAB_NAME + ".py"

    shutil.copyfile(src_file, dst_file)


def add_feedback_text(folder: str, specific_feedback: str):
    """move feedback to top of student's submitted file
    """

    # Find student file
    src_file = list(pathlib.Path(os.path.abspath(os.getcwd()) + '\\' + folder).glob('*.py'))[0]
    # add # to first line and after every \n
    specific_feedback = '################### FEEDBACK ############################\n' + \
                        '# ' + specific_feedback.replace('\n', '\n# ') + \
                        '\n################### FEEDBACK ############################\n\n'
    # read python file
    file = open(src_file, 'r')
    file_contents = file.read()
    file.close()

    # Remove previous feedback, if any exists
    file_contents = file_contents.split('\n################### FEEDBACK ############################\n\n')[-1]

    # Add feedback
    new_file_contents = specific_feedback + file_contents

    # Write to file
    file = open(src_file, 'w')
    file.write(new_file_contents)
    file.close()


def grade():
    """Run grading script
    """
    importlib.reload(grade_lab_4)
    if __name__ == '__main__':
        result = unittest.main(verbosity=2, exit=False).result

        print("\nLab 4 grading summary for {0}, {1}:".format(
            __author__, __student_number__))

        print('No. of tests run:', result.testsRun)
        print('No. of errors:', len(result.errors))
        print('No. of failures:', len(result.failures))
        passes = result.testsRun - len(result.errors) - len(result.failures)
        print("No. of tests passed:", passes)

        # Calculate an integer score out of 10.
        print("Score = {0} / 10".format(round(passes / result.testsRun * 10)))

        score = round(passes / result.testsRun * 10)
    else:
        print('error in grading')
        score = -1
        print('Review student: ' + name + ', ID#: ' + student_id, file=original_stderr)
    return score


def parse_name_and_student_id(folder_name: str):
    """get name and student id from folder
    """
    split_folder = folder_name.split("- ")
    split_folder_dash_correction = len(split_folder)
    if split_folder_dash_correction == 3:
        name_and_id = split_folder[1]
    else:
        name_and_id = split_folder[2]
    student_id = name_and_id[-9:]
    name = name_and_id[:-10]

    name = fix_name_order(name)

    return name, student_id


def fix_name_order(name: str):
    name_first_last = name.split(' ')
    if len(name_first_last) == 2:
        name = name_first_last[-1]+' '+name_first_last[0]
    elif len(name_first_last) == 1:
        name = ' - '+ name_first_last[0]
        print('odd name check proper copy of name', file=original_stdout)
    elif len(name_first_last) > 2:
        name = name_first_last[-1]+' '+' '.join(name_first_last[:-1])
    else:
        print('debug: '+name, file=original_stderr)
    return name

def update_file_and_check_syntax():
    """update file in cache to new file in folder and check that it works
    """
    can_mark = True
    try:
        import lab4
        importlib.reload(lab4)
    except:
        can_mark = False
    return can_mark


def save_grade_to_CSV(grades: list, fieldnames: list):
    """Saves list of grades with fieldnames to a csv file"""
    with open(SAVE_GRADES_TO, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(grades)


# main script
folders = listdir()
filter_folders(folders)
scores = []

for folder in folders:

    # Get name and ID
    name, student_id = parse_name_and_student_id(folder)

    # Start print to file
    new_location_write = open("output.txt", 'w')
    sys.stderr = new_location_write
    sys.stdout = new_location_write

    print(name)
    print(student_id)
    print('\ngrading software summary:')

    correct_filename = os.path.exists(folder + "/" + LAB_NAME + ".py")

    if correct_filename:

        copy_outside(folder)
        good_syntax = update_file_and_check_syntax()

        if good_syntax:
            from lab4 import __author__, __student_number__

            if __student_number__.replace(' ', '') == student_id:
                # Grade lab
                score = grade()

            else:
                # possible plagiarism
                print('ID doesn\'t match', 'expected:', student_id, ' but received', __student_number__)
                print('File Author name:', __author__, '- Expected Author name:', name)
                print('FURTHER REVIEW REQUIRED')
                score = -1
                print('Review student: ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'',
                      file=original_stderr)

        else:
            score = 0
            print('Syntax error in code (0/10)')

    else:
        # give 0
        print('wrong file name: (0/10) -> should be ' + LAB_NAME + '.py')
        score = 0

    # Close print saving
    new_location_write.close()
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    scores.append({'Name':name,'OrgDefinedId': student_id,
                   'Lab 4 Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>': score,
                   "End-of-Line Indicator": '#'})

    new_location_read = open("output.txt", 'r')
    feedback = new_location_read.read()
    new_location_read.close()

    # Add feedback to students file
    add_feedback_text(folder, feedback)

# csv header
field_names = ['Name','OrgDefinedId',
               GRADES_CSV_HEADER,
               'End-of-Line Indicator']

# save as CSV
save_grade_to_CSV(scores, field_names)
