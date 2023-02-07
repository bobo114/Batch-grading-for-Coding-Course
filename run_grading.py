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
import importlib
import pathlib
import csv

__author__ = "Boaz Aharony"
__copyright__ = "Copyright 2023, Boaz Aharony"
__maintainer__ = "Boaz Aharony"
__email__ = "boazaharony@cmail.carleton.ca"
__status__ = "Dev"

########################## CHANGE EVERY LAB ###########################################################################
LAB_NAME = 'lab5'  # DO NOT ADD .py
LAB_GRADING_SOFTWARE_NAME = 'grade_lab_5.py'
SAVE_GRADES_TO = 'lab4_Grades.csv'
GRADES_CSV_HEADER = 'Lab 4 Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>'
########################## CHANGE EVERY LAB ###########################################################################

########################## GENERAL CONDITIONS ###########################################################################
FIX_NAME_ORDER = True  # make program print first name then last name onto sheet and feedback when set to true
########################## GENERAL CONDITIONS ###########################################################################

# save original print streams
original_stdout = sys.stdout
original_stderr = sys.stderr


def filter_folders(names: list):
    """Filters given folder name list to only folders formatted as student downloads
    """
    temp_names = names.copy()
    for filename in temp_names:
        if not ('0' <= filename[0] <= '9'):
            names.remove(filename)


def copy_outside(student_folder: str):
    """Copy lab folder outside
    """
    src_folder = os.path.abspath(os.getcwd()) + '\\' + student_folder
    dst_folder = os.path.abspath(os.getcwd())

    # file names
    src_file = src_folder + "\\" + LAB_NAME + ".py"
    dst_file = dst_folder + "\\" + LAB_NAME + ".py"

    if os.path.exists(dst_file):
        os.remove(dst_file)

    shutil.copyfile(src_file, dst_file)


def add_feedback_text(student_folder: str):
    """move feedback to top of student's submitted file
    """
    # read the feedback
    new_location_read = open("output.txt", 'r')
    specific_feedback = new_location_read.read()
    new_location_read.close()

    # Find student file
    src_file = list(pathlib.Path(os.path.abspath(os.getcwd()) + '\\' + student_folder).glob('*.py'))[0]
    # add # to first line and after every \n
    specific_feedback_for_code = '################### FEEDBACK ############################\n' + \
                                 '# ' + specific_feedback.replace('\n', '\n# ') + \
                                 '\n################### FEEDBACK ############################\n\n'
    # read python file
    cannot_read_original = False
    try:
        file = open(src_file, 'r')
        file_contents = file.read()
        file.close()
    except:
        cannot_read_original = True
        print(
            'Review student (odd file encoding format -> feedback saved to seperate feedback.txt file in student\'s folder): ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'\n',
            file=original_stderr)
    if not cannot_read_original:
        # Remove previous feedback, if any exists
        file_contents = file_contents.split('\n################### FEEDBACK ############################\n\n')[-1]

        # Add feedback
        new_file_contents = specific_feedback_for_code + file_contents

        # Write to file
        file = open(src_file, 'w')
        file.write(new_file_contents)
        file.close()
    else:
        src_file = os.path.abspath(os.getcwd()) + '\\' + student_folder + '\\' + 'feedback.txt'
        file = open(src_file, 'w')
        new_file_contents = 'ERROR WRITING TO ORIGINAL CODE, FEEDBACK BELOW:\n\n' + specific_feedback
        file.write(new_file_contents)
        file.close()


def parse_name_and_student_id(folder_name: str, fix_order: bool):
    """get name and student id from folder
    """
    split_folder = folder_name.split("- ")
    split_folder_dash_correction = len(split_folder)
    if split_folder_dash_correction == 3:
        name_and_id = split_folder[1]
    else:
        name_and_id = split_folder[2]
    student_id_part = name_and_id[-9:]
    name_part = name_and_id[:-10]

    if fix_order:
        name_part = fix_name_order(name_part)

    return name_part, student_id_part


def fix_name_order(name_part: str):
    """Puts first name then last name as opposed to the brightspace order of last first
    """
    name_first_last = name_part.split(' ')
    if len(name_first_last) == 2:
        name_part = name_first_last[-1] + ' ' + name_first_last[0]
    elif len(name_first_last) == 1:
        name_part = ' - ' + name_first_last[0]
    elif len(name_first_last) > 2:
        name_part = name_first_last[-1] + ' ' + ' '.join(name_first_last[:-1])
    else:
        print('debug: ' + name_part, file=original_stderr)
    return name_part


def update_file_and_check_syntax():
    """update file in cache to new file in folder and check that it works
    """
    can_mark = True
    try:
        exec('import ' + LAB_NAME)
    except:
        can_mark = False
    return can_mark


def save_grade_to_CSV(grades: list, fieldnames: list):
    """Saves list of grades with fieldnames to a csv file"""
    with open(SAVE_GRADES_TO, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(grades)


def start_print_to_file():
    """prints to output file to save all print
    """
    write_location = open("output.txt", 'w')
    sys.stderr = write_location
    sys.stdout = write_location
    return write_location


def end_print_to_file(write_location):
    """Ends printing to textfile
    """
    write_location.close()
    sys.stdout = original_stdout
    sys.stderr = original_stderr


def delete_unnecessary_files():
    """Cleans up folder prior to finish
    """
    os.remove(os.path.abspath(os.getcwd()) + '\\output.txt')

    if os.path.exists(os.path.abspath(os.getcwd()) + '\\' + LAB_NAME + '.py'):
        os.remove(os.path.abspath(os.getcwd()) + '\\' + LAB_NAME + '.py')


# main script

# Get student folder list
folders = listdir()
filter_folders(folders)
scores = []

# Grade each file
for folder in folders:

    # Get name and ID
    name, student_id = parse_name_and_student_id(folder, fix_order=FIX_NAME_ORDER)
    print('grading folder', '\''+folder+'\'','.......................')
    try:  # In case an error is caused here, change print stream back to console
        # Start print to file
        new_location_write = start_print_to_file()

        print(name)
        print(student_id)
        print('\ngrading software summary:')

        correct_filename = os.path.exists(folder + "/" + LAB_NAME + ".py")

        if correct_filename:

            copy_outside(folder)
            good_syntax = update_file_and_check_syntax()

            if good_syntax:

                exec('import ' + LAB_NAME)

                try:
                    exec('given_id = ' + LAB_NAME + ".__student_number__.replace(' ', '')")  # imports the student ID
                except:
                    given_id = None

                try:
                    exec('given_author = ' + LAB_NAME + ".__author__")
                except:
                    given_author = None

                if given_id == student_id and given_author is not None:  # if the expected ID matches
                    # Grade lab
                    exec(open(LAB_GRADING_SOFTWARE_NAME).read())
                    score = round(passes / result.testsRun * 10)

                else:
                    # mismatching or missing name/ID, tell TA to further review

                    # add to file
                    print('File ID#:', given_id, '-> Expected ID#:', student_id)
                    print('File Author name:', given_author, '-> Expected Author name:', name)
                    print('FURTHER REVIEW REQUIRED')

                    # Tell TA on console
                    print(
                        'Review student (issue with name or ID): ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'',
                        file=original_stderr)
                    print('File ID#:', given_id, '-> Expected ID#:', student_id, file=original_stderr)
                    print('File Author name:', given_author, '-> Expected Author name:', name, file=original_stderr)
                    print(file=original_stderr)

                    score = -1  # to highlight student on csv when opened in excel

                del sys.modules[LAB_NAME]  # delete the current lab

            else:
                score = 0
                print('Syntax error in code (0/10)')

        else:
            print('wrong file name: (0/10) -> should be ' + LAB_NAME + '.py')
            score = 0

        # Close print saving to txt file
        end_print_to_file(new_location_write)

    except Exception as e:
        # In case of bug that was not caught
        sys.stderr = original_stderr
        print('ERROR, CONTACT', __maintainer__, 'at:', __email__, file=original_stderr)
        print(e, file=original_stderr)
        sys.exit("CANNOT CONTINUE GRADING DUE TO STUDENT: "+ name)

    # Add score to dictionary
    scores.append({'Name': name, 'OrgDefinedId': student_id,
                   GRADES_CSV_HEADER: score,
                   "End-of-Line Indicator": '#'})

    # Add feedback to students file
    add_feedback_text(folder)

# delete unnecessary files
delete_unnecessary_files()

# csv header
field_names = ['Name', 'OrgDefinedId',
               GRADES_CSV_HEADER,
               'End-of-Line Indicator']
# save grades to CSV
save_grade_to_CSV(scores, field_names)
