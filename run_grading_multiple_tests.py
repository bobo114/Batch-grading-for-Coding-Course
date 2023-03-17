"""
ECOR 1041/1042 batch grading file, easily modifiable to the individual lab grading files created by course instructors

This version is also capable of running different tests based on the file submitted. There MUST be a grading material
folder with tests, and each possible part must have a test for it made.

Designed to add feedback to each student's file based on grading file output. Checks for matching student numbers based
on D2L brightspace format. Lastly will create a CSV document in D2L format to upload student grades as well as
zip files with feedback.

To run, ensure you have the following files in one folder: run_grading_multiple_tests.py,
grading material folder (with its tests and additional files enclosed),
and the zip file directly downloaded from brightspace (THIS VERSION ALLOWS YOU TO HAVE MORE THAN 1 zip AT ONCE).

Any erroneous submissions with mismatching student IDs or infinite loops will be reported in the console
as error to the user and will inform you of student name, ID and folder name
"""

import csv
import os
import shutil
import subprocess
import sys
import zipfile

__author__ = "Boaz Aharony"
__copyright__ = "Copyright 2023, Boaz Aharony"
__maintainer__ = "Boaz Aharony"
__email__ = "boazaharony@cmail.carleton.ca"
__status__ = "Dev"

########################## CHANGE EVERY LAB ###########################################################################
LAB_NAME_GRADING_SOFTWARE_INDEX = {'student_age_list': 'student_age_list_test',
                                   'student_failures_list': 'student_failures_list_test',
                                   'student_health_list': 'student_health_list_test',
                                   'student_school_list': 'student_school_list_test'}  # Add lab name, and its associated grading software, DO NOT ADD .py
SAVE_GRADES_TO = 'labx_Grades.csv'  # name of csv file
GRADES_CSV_HEADER = 'Lab x Points Grade <Numeric MaxPoints:10 Weight:16.66666667 Category:Labs CategoryWeight:10>'  # header of grades column
SCORE_CODE = 'round(passes / result.testsRun * 4, 2)'  # Code used to calculate score (copy from grading file)
GRADING_MATERIAL_LOCATION = 'grading material'  # The name of the folder that contains the grading script
FEEDBACK_ZIP_FOLDER_NAME = 'feedback for brightspace'  # Name of folder to which student feedback will be zipped into, DO NOT ADD .zip
ADD_NAME_TO_CSV = False  # Set to True if you want a name column to show up on the CSV
########################## CHANGE EVERY LAB ###########################################################################

########################## GENERAL CONDITIONS ###########################################################################
FIX_NAME_ORDER = True  # make program print first name then last name onto csv and student feedback when set to true
PRINT_ALL_STUDENTS = False  # Prints student that it is currently grading (use for debugging)
TIMEOUT = 2  # set for limiting maximum runtime of a students code check (in seconds)
########################## GENERAL CONDITIONS ###########################################################################

# Constants
INDEX_FILE_NAME = 'index.html'

# save original print streams
original_stderr = sys.stderr


def add_feedback_text(student_folder: str, specific_feedback: str, file_name: str):
    """move feedback to top of student's submitted file
    """

    # Find student file
    src_file = os.path.join(os.getcwd(), student_folder + '\\' + file_name + '.py')

    # add # to first line and after every \n
    specific_feedback_for_code = '################### FEEDBACK ############################\n' + \
                                 '# ' + specific_feedback.replace('\n', '\n# ') + \
                                 '\n################### FEEDBACK ############################\n\n'
    # read python file
    cannot_read_original = False
    try:
        with open(src_file, 'r', encoding='utf-8') as file:
            file_contents = file.read()
    except Exception as err:
        cannot_read_original = True
        print(f"An error occurred: {err}")
        print(
            'Review student (odd file encoding format -> feedback saved to seperate feedback.txt file in student\'s folder): ' + name + ', ID#: ' + student_id + ', Folder name:\'' + folder + '\'\n',
            file=original_stderr)
    if not cannot_read_original:
        # Add feedback
        new_file_contents = specific_feedback_for_code + file_contents

        # Write to file
        file = open(src_file, 'w')
        file.write(new_file_contents)
        file.close()
        rename_file(src_file, 'FEEDBACK_' + file_name + '.py')

    else:
        os.remove(src_file)
        src_file = os.path.abspath(os.getcwd()) + '\\' + student_folder + '\\' + 'feedback.txt'
        file = open(src_file, 'w')
        new_file_contents = 'ERROR WRITING TO ORIGINAL CODE, FEEDBACK BELOW:\n\n' + specific_feedback
        file.write(new_file_contents)
        file.close()


def rename_file(file_path, new_name) -> bool:
    """
    Rename the file at the given file path with the new name.

    Args:
    file_path (str): The file path.
    new_name (str): The new name for the file.

    Returns:
    bool: True if the file was renamed successfully, False otherwise.
    """
    try:
        # Get the directory and the current name of the file
        directory = os.path.dirname(file_path)

        # Generate the new file path with the new name
        new_path = os.path.join(directory, new_name)

        # Rename the file
        os.rename(file_path, new_path)

        return True
    except Exception as e:
        print("Error renaming file:", e)
        return False


def parse_name_and_student_id(folder_name: str, fix_order: bool) -> tuple:
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


def fix_name_order(name_part: str) -> str:
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


def get_id_and_author(lab_name: str) -> tuple:
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


def grade(lab_grading_software_name: str) -> tuple:
    """
    Runs the grading script on the student's code, returns a tuple of score, feedback
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
    feedback_for_file += 'File Author name:' + given_author + '-> Expected Author name:' + name + '\n'
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


def list_files(directory: str) -> list:
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


def check_list_for_matching_key(lst: list) -> str:
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


def filter_py_files(file_list: list) -> list:
    """
    Given a list of strings, return a new list containing only those strings
    that end with '.py', with the '.py' extension removed.
    """
    filtered_list = []
    for file_name in file_list:
        if file_name.endswith('.py'):
            filtered_list.append(file_name[:-3])
    return filtered_list


def copy_files_to_grading_folder(folder_name: str, files_in_folder: str):
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
    for filename in files_in_folder:
        source_path = os.path.join(folder_path, filename)
        if os.path.isfile(source_path):
            destination_path = os.path.join(grading_folder_path, filename)
            if os.path.exists(destination_path):
                raise ValueError(f'File {filename} already exists in the grading folder')
            shutil.copyfile(source_path, destination_path)


def format_keys_dict(d: dict) -> str:
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


def change_to_grading_dir(current_dir: str):
    """Change the current working directory to the directory specified by the global constant GRADING_MATERIAL_LOCATION."""
    new_dir = os.path.join(current_dir, GRADING_MATERIAL_LOCATION)
    os.chdir(new_dir)


def delete_files(file_names: list):
    """
    Deletes all files with the names specified in a list from the current working directory.
    Throws an error if a file name from the list is not found in the directory.
    """
    cwd = os.getcwd()
    for name in file_names:
        if not os.path.isfile(os.path.join(cwd, name)):
            raise FileNotFoundError(f"File '{name}' not found in directory '{cwd}'.")
        os.remove(os.path.join(cwd, name))


def delete_files_except(directory_path: str, keep_files: list):
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path) and file_name not in keep_files:
            os.remove(file_path)


def zip_folders(folder_names: list, zip_name: str, root_files: list = None) -> str:
    if not zip_name.endswith('.zip'):
        zip_name += '.zip'
    zip_path = os.path.join(os.getcwd(), zip_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name in folder_names:
            folder_path = os.path.join(os.getcwd(), folder_name)
            if os.path.isdir(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, os.path.join(folder_name, rel_path))
                shutil.rmtree(folder_path)
        if root_files:
            for file in root_files:
                if os.path.isfile(file):
                    zipf.write(file, os.path.basename(file))
                    os.remove(file)
    return zip_path


def get_zip_filenames(exclude_prefix: str) -> list:
    zip_filenames = []
    for filename in os.listdir():
        if filename.endswith('.zip') and not filename.startswith(exclude_prefix + '-'):
            zip_filenames.append(filename)
    return zip_filenames


def unzip_single_zip(zip_file_name: str, index_file_name: str) -> list:
    """
    Extracts all files and folders from a zipped folder to a destination directory.
    The extracted folder will be renamed with a "DO_NOT_UPLOAD_" prefix.
    Returns list of all folders extracted (assuming the only non folder file is global variable INDEX_FILE_NAME)
    """
    extracted_folder = os.path.splitext(zip_file_name)[0] + '.zip'
    extracted_folder_with_prefix = extracted_folder if extracted_folder.startswith(
        "DO_NOT_UPLOAD_") else f"DO_NOT_UPLOAD_{extracted_folder}"

    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall('.')
        unzipped_files = zip_ref.namelist()

    unzipped_folders = []
    for file_name in unzipped_files:
        if '/' in file_name:
            folder_name = file_name.split('/')[0]
            if folder_name not in unzipped_folders:
                unzipped_folders.append(folder_name)
        else:
            if file_name not in unzipped_folders:
                unzipped_folders.append(file_name)
    unzipped_folders.remove(index_file_name)

    os.rename(extracted_folder, extracted_folder_with_prefix)
    print(f"{zip_file_name} has been unzipped and renamed to {extracted_folder_with_prefix} successfully.")

    return list(set(unzipped_folders))


def list_to_string(lst: list) -> str:
    """
    Converts a list of strings into a comma-separated string with the last
    element separated by "and".

    Args:
        lst (List[str]): A list of strings.

    Returns:
        str: A comma-separated string with the last element separated by "and".
    """
    if len(lst) == 0:
        return ""
    elif len(lst) == 1:
        return lst[0]
    else:
        return f"{', '.join(lst[:-1])} and {lst[-1]}"

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


# main script
# Find zip files
brightspace_submission_download_zip_names = get_zip_filenames(FEEDBACK_ZIP_FOLDER_NAME)
print(f"found {len(brightspace_submission_download_zip_names)} zip folders to grade")
print(f"grading zip folders: {list_to_string(brightspace_submission_download_zip_names)}")
scores = []

folder_counter = 0
issues_counter = 0
for i in range(len(brightspace_submission_download_zip_names)):
    # Unzip student folders and get their names list
    folders = unzip_single_zip(brightspace_submission_download_zip_names[i], INDEX_FILE_NAME)
    folder_counter += len(folders)
    # Save original files of grading material folder to avoid modification in case of code failure
    original_grading_material_files = list_files(GRADING_MATERIAL_LOCATION)
    original_dir = os.getcwd()

    print(f"Beginning grading folder '{brightspace_submission_download_zip_names[i]}', detected {len(folders)} students")
    # Grade each file
    for folder in folders:
        # Get name and ID
        if PRINT_ALL_STUDENTS:
            print('grading folder', '\'' + folder + '\'', '.......................')
        name, student_id = parse_name_and_student_id(folder, fix_order=FIX_NAME_ORDER)

        try:  # In case an error is caused here, let marker know the student who caused it
            files_in_student_folder = list_files(folder)  # list of files in student folder
            py_files_without_extension = filter_py_files(files_in_student_folder)  # python files without their extension
            py_files_with_extension = [file_name + ".py" for file_name in py_files_without_extension]

            # Begin writing feedback
            feedback_for_student = name + '\n' \
                                   + student_id + '\n' \
                                   + '\ngrading software summary:' + '\n'

            # Check if file is one of the possible valid names
            try:
                file_to_grade = check_list_for_matching_key(py_files_without_extension)
            except ValueError:
                feedback_for_student += more_then_one_file_prints() + '\n'  # more than one VALID file exits
                continue

            if file_to_grade is not None:  # attempt to grade if name is valid

                # Copy and get a list of the files that were copied
                copy_files_to_grading_folder(folder, py_files_with_extension)

                # Get ID and name, check if this causes issues
                change_to_grading_dir(original_dir)
                given_id, given_author = get_id_and_author(file_to_grade)

                # Check for errors
                infinite_loop = given_id == 'TimeoutExpired' and given_author == 'TimeoutExpired'
                syntax_error = given_id == 'syntaxError' and given_author == 'syntaxError'
                name_on_file_incorrect = not (given_id == student_id and given_author != 'missing')

                # This one checks if the name is either missing or empty
                name_on_file_missing = given_id == 'missing' or given_author == 'missing'
                name_on_file_missing = name_on_file_missing or len(given_id) == 0 or len(given_author) == 0

                # Act on errors if any, otherwise grade
                if infinite_loop:
                    score = -1
                    issues_counter += 1
                    feedback_for_student += infinite_loop_prints() + '\n'

                elif syntax_error:
                    score = 0
                    feedback_for_student += 'Syntax error in code (0/10)' + '\n'

                elif name_on_file_missing:
                    score = 0
                    feedback_for_student += 'No name or student ID in code (0/10)\n' + \
                                            'You must define __author__ and __student_number__ !!\n'
                elif name_on_file_incorrect:
                    score = -1
                    issues_counter += 1
                    feedback_for_student += mismatching_name_prints() + '\n'

                else:
                    score, feedback_addition = grade(LAB_NAME_GRADING_SOFTWARE_INDEX[file_to_grade] + '.py')
                    feedback_for_student += feedback_addition

                # delete files from grading material folder and go back outside of it
                delete_files(py_files_with_extension)
                os.chdir(original_dir)

            else:  # if file is not a correct name
                score = 0
                feedback_for_student = 'wrong file name: (0/10) -> should be ' + format_keys_dict(
                    LAB_NAME_GRADING_SOFTWARE_INDEX) + '\n'
                file_to_grade = py_files_without_extension[0]

        except Exception as e:
            # In case of bug that was not caught

            print('ERROR, CONTACT', __maintainer__, 'at:', __email__,
                  '\nDO NOT ATTEMPT TO GRADE AGAIN WITHOUT DELETING AND RECOPYING STUDENT FOLDERS',
                  file=original_stderr)
            print(e, file=original_stderr)

            # reset the grading folder
            os.chdir(original_dir)
            delete_files_except(GRADING_MATERIAL_LOCATION, original_grading_material_files)

            # end run
            sys.exit("CANNOT CONTINUE GRADING DUE TO STUDENT: " + name)

        # Add score to dictionary
        score_dict = {'OrgDefinedId': student_id,
                       GRADES_CSV_HEADER: score,
                       "End-of-Line Indicator": '#'}
        if ADD_NAME_TO_CSV:
            score_dict['Name'] = name
        scores.append(score_dict)

        # Add feedback to students file
        add_feedback_text(folder, feedback_for_student, file_to_grade)

    print(f"Done grading '{brightspace_submission_download_zip_names[i]}', Saving feedback to zip folder '{FEEDBACK_ZIP_FOLDER_NAME}-{i + 1}'")
    zip_folders(folders, f"{FEEDBACK_ZIP_FOLDER_NAME}-{i + 1}", [INDEX_FILE_NAME])

if len(scores) != folder_counter:
    raise ValueError("Length of grades does not match folders, results invalidated")
print(f"Done grading all folders, there were {folder_counter} students, {issues_counter} could not be graded")
# csv header
field_names = list(scores[0].keys())

# save grades to CSV
print('Saving grades to CSV')
save_grade_to_CSV(scores, field_names)
print('Grading Complete')
