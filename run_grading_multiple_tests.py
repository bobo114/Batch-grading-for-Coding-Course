"""
ECOR 1041/1042 batch grading file, easily modifiable to the individual lab grading files created by course instructors

Designed to add feedback to each students file based on grading file output. Checks for matching student numbers based
on D2L brightspace format. Lastly will create a CSV document in D2L format to upload student grades.

Any erroneous submissions will be reported in the console as error to the user and will inform you of student name, ID
and folder name
"""

from os import listdir
import sys
import os
import shutil
import pathlib
import csv
import subprocess

__author__ = "Boaz Aharony"
__copyright__ = "Copyright 2023, Boaz Aharony"
__maintainer__ = "Boaz Aharony"
__email__ = "boazaharony@cmail.carleton.ca"
__status__ = "Dev"

########################## CHANGE EVERY LAB ###########################################################################
# LAB_NAME = 'lab4'  # DO NOT ADD .py
# LAB_GRADING_SOFTWARE_NAME = 'grade_lab_4.py'
LAB_NAME_GRADING_SOFTWARE_INDEX = {'student_age_list': 'student_age_list_test',
                                   'student_failures_list': 'student_failures_list_test',
                                   'student_health_list': 'student_health_list_test',
                                   'student_school_list':'student_school_list_test'}  # Add lab name, and its associated grading software, DO NOT ADD .py
SAVE_GRADES_TO = 'lab4_Grades.csv'
GRADES_CSV_HEADER = 'Lab 4 Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>'
########################## CHANGE EVERY LAB ###########################################################################

########################## GENERAL CONDITIONS ###########################################################################
FIX_NAME_ORDER = True  # make program print first name then last name onto sheet and feedback when set to true
PRINT_ALL_STUDENTS = True  # Prints student that it is currently grading (use for debugging)
TIMEOUT = 2  # set for limiting maximum runtime of a students code check (in seconds)
SCORE_CODE = 'round(passes / result.testsRun * 10)'  # Code used to calculate score (copy from grading file)
GRADING_MATERIAL_LOCATION = 'grading material'
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


def copy_outside(student_folder: str, file_to_copy: str):
    """Copy lab folder outside
    """
    src_folder = os.path.abspath(os.getcwd()) + '\\' + student_folder
    dst_folder = os.path.abspath(os.getcwd())

    # file names
    src_file = src_folder + "\\" + file_to_copy
    dst_file = dst_folder + "\\" + file_to_copy

    if os.path.exists(dst_file):
        os.remove(dst_file)

    shutil.copyfile(src_file, dst_file)


def add_feedback_text(student_folder: str, specific_feedback: str, file_name: str):
    """move feedback to top of student's submitted file
    """

    # Find student file
    src_file = os.path.join(os.getcwd(),  student_folder + '\\' + file_name+'.py')

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
    print(split_folder)
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

    # TODO remove files from grading folder

    # if os.path.exists(os.path.abspath(os.getcwd()) + '\\' + LAB_NAME + '.py'):
    #     os.remove(os.path.abspath(os.getcwd()) + '\\' + LAB_NAME + '.py')


def get_id_and_author(lab_name: str):
    """Returns the current name and id of the lab, 'syntaxError' if the file can't run
    and 'TimeoutExpired' if the file takes too long to load
    """
    name_exist_check_code = 'import ' + lab_name + '\n' + \
                            'if hasattr(' + lab_name + ', \'__student_number__\'):\n' \
                                                       '\tprint(' + lab_name + '.__student_number__)\n' \
                                                                               'else:\n' \
                                                                               '\tprint(\'missing\')\n\n' \
                                                                               'if hasattr(' + lab_name + ', \'__author__\'):\n' \
                                                                                                          '\tprint(' + lab_name + '.__author__)\n' \
                                                                                                                                  'else:\n' \
                                                                                                                                  '\tprint(\'missing\')'
    try:
        name_and_id_check = subprocess.run([sys.executable, '-c', name_exist_check_code], capture_output=True,
                                           text=True, timeout=TIMEOUT)
        if name_and_id_check.stderr != '':
            return 'syntaxError', 'syntaxError'
        name_and_id_exist = name_and_id_check.stdout.split('\n')
        given_name = name_and_id_exist[-2]
        given_number = name_and_id_exist[-3].replace(' ', '')
    except subprocess.TimeoutExpired:  # Possible infinite loop
        return 'TimeoutExpired', 'TimeoutExpired'

    return given_number, given_name


def grade(lab_grading_software_name: str):
    """
    Runs the grading script on the student's code
    """
    try:

        # Slightly modify the grading file
        code = 'import sys\n' \
               'sys.stderr = sys.stdout\n' \
               + open(lab_grading_software_name).read() + '\n' \
               + 'print(' + SCORE_CODE + ', end=\'\')'

        # will throw timeout error if exceeds TIMEOUT seconds
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
                                timeout=TIMEOUT)

        # Split code output
        output = result.stdout.split('\n')

        # get score
        gscore = float(output[-1])

        # Add the rest to the feedback
        feedback_for_file = '\n'.join(output[:-1])

    except subprocess.TimeoutExpired:  # Possible infinite loop
        gscore = -1  # to highlight student on csv when opened in excel
        feedback_for_file = infinite_loop_prints()
    return gscore, feedback_for_file  # named gscore to not interfere with score


def mismatching_name_prints():
    """Prints necessary mismatching name actions
    """
    # add to file
    feedback_for_file = 'File ID#:' + given_id + '-> Expected ID#:' + student_id + '\n'
    feedback_for_file += 'File Author name:' + given_author + '-> Expected Author name:' + name +'\n'
    feedback_for_file += 'FURTHER REVIEW REQUIRED' + '\n'

    # Tell TA on console
    print(
        'Review student (issue with name or ID): ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'',
        file=original_stderr)
    print('File ID#:', given_id, '-> Expected ID#:', student_id, file=original_stderr)
    print('File Author name:', given_author, '-> Expected Author name:', name, file=original_stderr)
    print(file=original_stderr)
    return feedback_for_file


def infinite_loop_prints():
    """Prints necessary infinite loop actions
    """
    feedback_for_file = 'Possible infinite loop or input in code' + '\n'
    feedback_for_file += 'FURTHER REVIEW REQUIRED' + '\n'
    print(
        'Review student (possible infinite loop or input): ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'',
        file=original_stderr)
    print(file=original_stderr)
    return feedback_for_file


def more_then_one_file_prints():
    """Prints necessary infinite loop actions
    """
    feedback_for_file = 'Student has more than 1 file matching the possible submissions' + '\n' + \
                        'FURTHER REVIEW REQUIRED' + '\n'
    print(
        'Review student (more than 1 possible submission file): ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'',
        file=original_stderr)
    print(file=original_stderr)
    return feedback_for_file


def list_files(directory):
    """
    Returns a list of all the files held in a given directory
    that is contained in the same folder as the script is in.
    """
    path = os.path.join(os.path.dirname(__file__), directory)
    # Use os.path.dirname(__file__) to get the directory of the script,
    # and os.path.join to create a path to the desired directory
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            files.append(file)
    return files


def check_list_for_matching_key(lst: list):
    """
    Checks if any element in the given list matches a key in the
    global constant LAB_NAME_GRADING_SOFTWARE_INDEX dictionary.
    Returns the matching element, or None if no elements match.
    Raises an error if more than one element matches.
    """
    matching_element = None
    for element in lst:
        if element in LAB_NAME_GRADING_SOFTWARE_INDEX:
            if matching_element:
                raise ValueError("More than one element matches a key in the dictionary.")
            matching_element = element
    return matching_element


def copy_files_to_grading_folder(file_list):
    """
    Copies the files in the given list to a folder with the name of
    the global constant GRADING_MATERIAL_LOCATION that is located
    in the same directory as the script.
    """
    script_directory = os.path.dirname(os.path.realpath(__file__))
    grading_folder_path = os.path.join(script_directory, GRADING_MATERIAL_LOCATION)
    os.makedirs(grading_folder_path, exist_ok=True)
    for file in file_list:
        shutil.copy2(file, grading_folder_path)


def filter_py_files(file_list):
    """
    Given a list of strings, return a new list containing only those strings
    that end with '.py', with the '.py' extension removed.
    """
    filtered_list = []
    for file_name in file_list:
        if file_name.endswith('.py'):
            filtered_list.append(file_name[:-3])
    return filtered_list


def copy_files_to_grading_folder(folder_name):
    """
    Given a folder name, copy all files in that folder to a new folder
    named 'GRADING_MATERIAL_LOCATION' in the same directory as the original folder.
    Raise an error if the grading folder contains a file with the same name as a file
    in the original folder.
    """
    folder_path = os.path.join(os.getcwd(), folder_name)
    grading_folder_path = os.path.join(os.getcwd(), GRADING_MATERIAL_LOCATION)

    # Create the grading folder if it doesn't already exist
    if not os.path.exists(grading_folder_path):
        os.mkdir(grading_folder_path)

    # Copy all files from the original folder to the grading folder
    for filename in os.listdir(folder_path):
        source_path = os.path.join(folder_path, filename)
        if os.path.isfile(source_path):
            destination_path = os.path.join(grading_folder_path, filename)
            if os.path.exists(destination_path):
                raise ValueError(f'File {filename} already exists in the grading folder')
            shutil.copyfile(source_path, destination_path)


def format_keys_dict(d):
    """
    Takes a dictionary and returns all keys in a string with a seperation of ', ' between each key,
    with the space between the last and second last key being 'or', and to return just the string of the one key if only one key exists.
    Adds '.py' to every key name.
    """
    keys = [f"{key}.py" for key in d.keys()]
    num_keys = len(keys)
    if num_keys == 1:
        return keys[0]
    elif num_keys == 2:
        return f"{keys[0]} or {keys[1]}"
    else:
        last_key = keys[-1]
        other_keys = ", ".join(keys[:-1])
        return f"{other_keys}, or {last_key}"


def change_to_grading_dir():
    """Change the current working directory to the directory specified by the global constant GRADING_MATERIAL_LOCATION."""
    current_dir = os.getcwd()
    new_dir = os.path.join(current_dir, GRADING_MATERIAL_LOCATION)
    os.chdir(new_dir)
    return current_dir


def delete_files(file_names):
    """
    Deletes all files with the names specified in a list from the current working directory.
    Throws an error if a file name from the list is not found in the directory.
    """
    cwd = os.getcwd()
    for name in file_names:
        if not os.path.isfile(os.path.join(cwd, name)):
            raise FileNotFoundError(f"File '{name}' not found in directory '{cwd}'.")
        os.remove(os.path.join(cwd, name))


# main script

# Get student folder list
folders = listdir()
filter_folders(folders)
scores = []
# Grade each file
for folder in folders.copy():

    # Get name and ID
    if PRINT_ALL_STUDENTS:
        print('grading folder', '\'' + folder + '\'', '.......................')
    name, student_id = parse_name_and_student_id(folder, fix_order=FIX_NAME_ORDER)



# try:  # In case an error is caused here, change print stream back to console
    files = list_files(folder)
    py_files_without_extension = filter_py_files(files)


    feedback_for_student = name + '\n'
    feedback_for_student += student_id + '\n'
    feedback_for_student += '\ngrading software summary:' + '\n'

    try:
        file_to_grade = check_list_for_matching_key(py_files_without_extension)
    except ValueError:
        feedback_for_student += more_then_one_file_prints() + '\n'
        continue

    if file_to_grade is not None:

        files_copied = copy_files_to_grading_folder(folder)

        # Get ID and name, check if this causes issues
        original_dir = change_to_grading_dir()
        given_id, given_author = get_id_and_author(file_to_grade)  # TODO from here

        # Check for errors
        infinite_loop = given_id == 'TimeoutExpired' and given_author == 'TimeoutExpired'
        syntax_error = given_id == 'syntaxError' and given_author == 'syntaxError'
        name_on_file_incorrect = not (given_id == student_id and given_author != 'missing')

        # Act on errors if any, otherwise grade
        if infinite_loop:
            score = -1
            feedback_for_student += infinite_loop_prints() + '\n'

        elif syntax_error:
            score = 0
            feedback_for_student += 'Syntax error in code (0/10)' + '\n'

        elif name_on_file_incorrect:
            score = -1
            feedback_for_student += mismatching_name_prints() + '\n'
        else:
            score, feedback_addition = grade(LAB_NAME_GRADING_SOFTWARE_INDEX[file_to_grade]+'.py')
            feedback_for_student += feedback_addition

        delete_files(files)
        os.chdir(original_dir)  # change back to the outside folder

    else:
        score = 0
        feedback_for_student = 'wrong file name: (0/10) -> should be ' + format_keys_dict(LAB_NAME_GRADING_SOFTWARE_INDEX) + '.py' +'\n'
        file_to_grade = py_files_without_extension[0]+'.py'

    # Close print saving to txt file
    # end_print_to_file(new_location_write)

    # except Exception as e:
    #     # In case of bug that was not caught
    #     sys.stderr = original_stderr
    #     print('ERROR, CONTACT', __maintainer__, 'at:', __email__, file=original_stderr)
    #     print(e, file=original_stderr)
    #     sys.exit("CANNOT CONTINUE GRADING DUE TO STUDENT: " + name)

    # Add score to dictionary
    scores.append({'Name': name, 'OrgDefinedId': student_id,
                   GRADES_CSV_HEADER: score,
                   "End-of-Line Indicator": '#'})

    # Add feedback to students file
    add_feedback_text(folder, feedback_for_student, file_to_grade)


# csv header
field_names = ['Name', 'OrgDefinedId',
               GRADES_CSV_HEADER,
               'End-of-Line Indicator']
# save grades to CSV
save_grade_to_CSV(scores, field_names)