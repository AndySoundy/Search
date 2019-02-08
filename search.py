'''Command line tool that uses a process pool to parrallelise searches'''

import os
import sys
from time import time
from multiprocessing import Pool, cpu_count, freeze_support

def text_search_file_list(files, text_string, file_suffix, case_less, root=None):
    '''Takes the given file list and returns a list of files with the text string inside'''

    # For case-insensitive searches we use the lower case by convention
    if case_less:
        text_string = text_string.lower()

    # Now search the given files
    matched = []
    for file_name in files:

        # Is it the file type you want?
        if (file_name[-len(file_suffix):] == file_suffix) or (file_suffix == '.*'):
            if root:
                file_name = os.path.join(root, file_name)
            try:
                with open(file_name, "r") as open_file:
                    try:
                        file_lines = open_file.readlines()
                        for line in file_lines:
                            if case_less:
                                line = line.lower()

                            if text_string in line:
                                matched += [text_string + " found in "+file_name+"."]
                                break # Only list the file once total, not for every entry
                    except UnicodeDecodeError:
                        # Can't decode files into a string, e.g. image file
                        pass
            except PermissionError:
                # You are not allowed
                pass
            except FileNotFoundError:
                # I've only encountered this for the Linux subsystem files on Windows 10
                pass
            except OSError:
                # I've only encountered this on Linux systems when encountering sockets
                pass

    return matched

def look_for_text(start_dir, text_string, file_suffix='.py', case_less=False, extra_files=None):
    '''Recursively walks through start_dir, printing files that have text_string in'''
    try:
        # Recursively search through start_dir
        matched = []
        for root, _, files in os.walk(start_dir):
            matched += text_search_file_list(files, text_string, file_suffix, case_less, root=root)

        # Search any extra files given
        if extra_files:
            matched += text_search_file_list(extra_files, text_string, file_suffix, case_less)

        return matched
    except KeyboardInterrupt:
        return

def count_lines_file_list(files, name, file_suffix, case_less, verbatim, root=None):
    '''Takes the given file list and returns the number of lines in matched files'''

    # For case-insensitive searches we use the lower case by convention
    if case_less:
        name = name.lower()

    # Now start counting
    num_lines = 0
    for file_name in files:
        if case_less:
            file_name = file_name.lower()

        # Is it the file type you want?
        if (file_name[-len(file_suffix):] == file_suffix) or (file_suffix == '.*'):
            if name == '' or\
                verbatim and file_name == name or\
                verbatim and len(file_name) > len(file_suffix) and file_name[:-len(file_suffix)] == name or\
                not verbatim and name in file_name:

                # Matched file
                if root:
                    file_name = os.path.join(root, file_name)
                try:
                    with open(file_name, "r") as open_file:
                        try:
                            file_lines = open_file.readlines()
                            num_lines += len(file_lines)
                        except UnicodeDecodeError:
                            #Can't decode files into a string, e.g. image file
                            pass
                except PermissionError:
                    #You are not allowed
                    pass
                except FileNotFoundError:
                    #I've only encountered this for the Linux subsystem files on Windows 10
                    pass
                except OSError:
                    # I've only encountered this on Linux systems when encountering sockets
                    pass

    return num_lines

def count_lines(start_dir, name='', file_suffix='.*', case_less=False, verbatim=False,
                extra_files=None):
    '''Recursively walks through start_dir, printing files that have text_string in'''
    try:
        if case_less:
            name = name.lower()

        num_lines = 0
        for root, _, files in os.walk(start_dir):
            num_lines += count_lines_file_list(files, name, file_suffix, case_less, verbatim, root)

        if extra_files:
            num_lines += count_lines_file_list(extra_files, name, file_suffix, case_less, verbatim)

        return num_lines
    except KeyboardInterrupt:
        return

def file_search_file_list(files, name, file_suffix, case_less, verbatim, root=None):
    '''Takes the given file list and returns a list of matched files'''

    # For case-insensitive searches we use the lower case by convention
    if case_less:
        name = name.lower()

    # Now search the given files
    matched = []
    for file_name in files:

        # We just want to look at the file name, not the directory
        if not root:
            directory = os.path.dirname(file_name)
            file_name = os.path.basename(file_name)

        if case_less:
            file_name = file_name.lower()

        #For most searches .* is used, so put that first and avoid checking the suffix
        if (file_suffix == '.*') or (file_name[-len(file_suffix):] == file_suffix):
            #Verbatim searches only match for file_names that are exactly right
            if verbatim and file_name == name or\
               verbatim and len(file_name) > len(file_suffix) and file_name[:-len(file_suffix)] == name or\
               not verbatim and name in file_name:
                if root:
                    matched += ['Root: {}. File name: {}'.format(root, file_name)]
                else:
                    matched += ['Root: {}. File name: {}'.format(directory, file_name)]

    return matched

def look_for_file(start_dir, name, file_suffix='.*', case_less=False, verbatim=False, extra_files=None):
    '''Recursively walks through start_dir, printing files that have text_string in the name'''
    try:
        if case_less:
            name = name.lower()

        matched = []
        for root, _, files in os.walk(start_dir):
            matched += file_search_file_list(files, name, file_suffix, case_less, verbatim, root)

        if extra_files:
            matched += file_search_file_list(extra_files, name, file_suffix, case_less, verbatim)

        return matched
    except KeyboardInterrupt:
        return

def look_for_file_type(start_dir, file_suffix, extra_files=None):
    '''Check the given files and append files with matching extensions to res before returning'''
    try:
        matched = []
        for root, _, files in os.walk(start_dir):
            for file_name in files:
                if file_name[-len(file_suffix):] == file_suffix:
                    matched += ['Root: {}. File name: {}'.format(root, file_name)]

        if extra_files:
            for file_name in extra_files:
                if file_name[-len(file_suffix):] == file_suffix:
                    directory = os.path.dirname(file_name)
                    file_name = os.path.basename(file_name)
                    matched += ['Root: {}. File name: {}'.format(directory, file_name)]

        return matched
    except KeyboardInterrupt:
        return

def param_maker(start_dir, params, max_dirs=cpu_count()*2):
    '''Prepares the thread_params and post_thread_params for pool_processor'''

    # Get the starting directories to feed to the thread function
    files = []
    thread_params = []

    # Initially just search start_dir
    for thing in os.listdir(start_dir):
        joined_thing = os.path.join(start_dir, thing)

        if os.path.isfile(joined_thing):
            files += [joined_thing]
        else:
            new_param = [joined_thing] + params
            thread_params += [tuple(new_param)]

    # Now if you need to, go further down the directory tree to get more tasks
    while thread_params and len(thread_params) < max_dirs:
        new_dir = thread_params[0][0]
        thread_params = thread_params[1:]  # If you keep this you'll count files twice

        # Now look in the new subdirectory for new files and directories
        for thing in os.listdir(new_dir):
            joined_thing = os.path.join(new_dir, thing)

            if os.path.isfile(joined_thing):
                files += [joined_thing]
            else:
                new_param = [joined_thing] + params
                thread_params += [tuple(new_param)]

    # If there are no subdirectories
    if not thread_params:
        thread_params = [tuple([start_dir] + params)]

    # If there are subdirectories
    else:
        # Now split files up and add it evenly to thread_params
        thread_param_len = len(thread_params) # No need to do this for every file
        param_len = len(params)
        for file_num, file_name in enumerate(files):
            thread_num = file_num % thread_param_len

            # If it's the first extra file
            if len(thread_params[thread_num]) == param_len + 1:
                thread_params[thread_num] = thread_params[thread_num] + ([file_name],)

            else:
                files = thread_params[thread_num][-1]
                files += [file_name]
                thread_params[thread_num] = thread_params[thread_num][:-1] + (files,)
    return thread_params

def pool_processor(thread_fntn, thread_params):
    '''Runs a pool of threads on thread_fntn then runs post_thread_fntn'''

    # Only the main thread handles KeyboardInterrupts, not the child threads
    with Pool(cpu_count()) as pool:
        try:
            ret_obj = pool.starmap_async(thread_fntn, thread_params)
            res = ret_obj.get(9999) #A timeout is required for smooth exit on interrupt
        except KeyboardInterrupt:
            print('KeyboardInterrupt, terminating search')
            return

    return res

def print_result(matched_list):
    '''Sensibly print the results of the search'''

    #For count lines results
    if matched_list and isinstance(matched_list[0], int):
        #It's a small thing to add the non-plural
        lines = 'lines'
        if matched_list == 1:
            lines = 'line'
        print('Matched files had {} {}.'.format(sum(matched_list), lines))

    else:
        num_matches = 0
        for entry in matched_list:
            if isinstance(entry, list):
                for sub_entry in entry:
                    if sub_entry:
                        print(sub_entry)
                        num_matches += 1
            else:
                print(entry)
                num_matches += 1

        #It's a small thing to add the non-plural
        word = 'matches'
        if num_matches == 1:
            word = 'match'
        print('Found {} {} for your search.'.format(num_matches, word))

def save_result(matched_list, output_file):
    '''Save the search result in the given file'''

    try:
        with open(output_file, 'w') as open_file:
            #For count lines results
            if isinstance(matched_list, int):
                #It's a small thing to add the non-plural
                lines = 'lines'
                if matched_list == 1:
                    lines = 'line'
                print('Matched files had {} {}.'.format(matched_list, lines))

            else:
                num_matches = 0
                for entry in matched_list:
                    if isinstance(entry, list):
                        for sub_entry in entry:
                            if sub_entry:
                                open_file.write(sub_entry + '\n')
                                num_matches += 1
                    else:
                        open_file.write(entry)
                        num_matches += 1
        print('Results saved to: {}'.format(output_file))
    except PermissionError:
        print('PermissionError during save. Save somewhere else or run as admin.')

def extract_parameter(search_str, arguments):
    '''Take the argument and extract the given parameter'''
    for argument in arguments:
        if argument in search_str:
            index = search_str.find(argument)
            extended_arg = search_str[index+len(argument):]

            # Get rid of stuff at the start
            if extended_arg[0] == '=' or extended_arg[0] == ' ':
                extended_arg = extended_arg[1:]

            # And get rid of any trailing stuff
            for num, char in enumerate(extended_arg):
                if char == '-':
                    if num == 0 or num > len(extended_arg) or extended_arg[num - 1] == ' ':
                        extended_arg = extended_arg[:num]
                        break

                elif char == ' ' and num < len(extended_arg) - 1 and extended_arg[num+1] == '-':
                    extended_arg = extended_arg[:num]

                elif char == ' ' and num == len(extended_arg) - 1:
                    extended_arg = extended_arg[:-1]

            break

    return extended_arg

def main():
    '''Take the arguments manually and parse them'''

    # Argparse can't be used when compiling an executable so we have to manually parse arguments
    search_str = ''
    for i, arg in enumerate(sys.argv):
        if i > 0:
            search_str = search_str + " " + arg

    # For the help document
    if '-h' in search_str or '--help' in search_str or search_str is None:
        print('-d or --dir              Where to start your search')
        print('-e or --file-extension   The file extension of your file')
        print('-t or --text             The text string to search for')
        print('-n or --file-name        The name of the file to search for')
        print('-i or --case             Case insensitive search for text')
        print('-c or --count            Count the lines of matched lines')
        print('-o or --output-file      Save the results of the search to the given file')
        print('-v or --verbatim         Look for exactly this file name')

    # Get the search directory
    if ' -d' in search_str or ' --dir' in search_str:
        search_dir = extract_parameter(search_str, [' -d', ' --dir'])
        if not os.path.isdir(search_dir):
            print('Input directory "{}" is invalid.'.format(search_dir))

    elif os.name == 'nt': # Windows default search directory
        search_dir = 'C:\\'
    else:
        search_dir = '/'  # Unix default search directory

    # Get the file extension
    if ' -e' in search_str or ' --file-extension' in search_str:
        file_ext = extract_parameter(search_str, [' -e', ' --file-extension'])
    else:
        file_ext = '.*'

    # Get the text string to search for
    text = None
    if ' -t' in search_str or ' --text' in search_str:
        text = extract_parameter(search_str, [' -t', ' --text'])

    # Get the file name to search for
    file_name = None
    if ' -n' in search_str or ' --file-name' in search_str:
        file_name = extract_parameter(search_str, [' -n', ' --file-name'])

    # Is it a case insensitive search?
    if ' -i' in search_str or ' --case-insensitive' in search_str:
        case_insensitive = True
    else:
        case_insensitive = False

    # Are we counting lines?
    if ' -c' in search_str or ' --count-lines' in search_str:
        count = True
    else:
        count = False

    # Are we saving to a file?
    output_file = None
    if ' -o' in search_str or ' --output-file' in search_str:
        output_file = extract_parameter(search_str, [' -o', ' --output-file'])

    # Are we looking for exactly the given file type?
    if ' -v' in search_str or ' --verbatim' in search_str:
        verbatim = True
    else:
        verbatim = False

    start_time = time()
    result = []

    # Count lines
    if count:
        if file_name is None: # Need an empty string for search, not None
            file_name = ''
        thread_params = param_maker(search_dir, [file_name, file_ext, case_insensitive, verbatim])
        result = pool_processor(count_lines, thread_params)

    # Search for text string
    elif text:
        thread_params = param_maker(search_dir, [text, file_ext, case_insensitive])
        result = pool_processor(look_for_text, thread_params)

    # Search for file name
    elif file_name:
        thread_params = param_maker(search_dir, [file_name, file_ext, case_insensitive, verbatim])
        result = pool_processor(look_for_file, thread_params)

    # Search for file type
    elif file_ext != '.*':
        thread_params = param_maker(search_dir, [file_ext])
        result = pool_processor(look_for_file_type, thread_params)

    # User error
    else:
        print('Invalid selection, consult --help for more information.')
        result = ()

    # If you search, then try to quit search_str can still have the value from the first search
    search_str = ''

    # Output results
    if not isinstance(result, tuple) and result is not None:
        if output_file is not None:
            save_result(result, output_file)
        else:
            print_result(result)
        print('Search took {} seconds.'.format(time() - start_time))

if __name__ == '__main__':
    freeze_support() # Allow the code to be compiled into an executable
    main()
