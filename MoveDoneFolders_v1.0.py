import fnmatch
import os, shutil, time
import ConfigParser
import logging
from distutils.dir_util import copy_tree


init_log_name = 'MoveDoneFolders.log'

def init():
    if read_config_file()[1] != 1:
        return read_config_file()[0], 1
    else:
        log_name = init_log_name
        create_log(log_name)
        add_to_log(str(read_config_file()))
        return 0, 0

def create_log(log_name):
    logging.basicConfig(filename=log_name,level=logging.DEBUG)

def add_to_log(log_message):
    logging.info(time.strftime("%m-%d-%Y_%H:%M:%S") + " " + log_message)

def read_config_file():
    config = ConfigParser.ConfigParser()
    config.read('MoveDoneFolders.config')
    try:
        parse_config_dict = {}
        for section in config.sections():
            # if section == 'LOAD_MONITORED_FOLDERS':
            for(each_key, each_val) in config.items(section):
                #print each_key
                parse_config_dict[each_key]= each_val
                #print each_val
        #print parse_config_dict
        return parse_config_dict, 0
        #input_folder_dict
    except ConfigParser.Error as e:
        return e, 1



def clear_log():
    with open(log_name, 'w'):
        pass

def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        f_size = file_info.st_size / 1024
        return f_size


def move_selected_folders(Path_to_move, OutputFolder):
    if not os.path.exists(OutputFolder):
        os.makedirs(OutputFolder)
    try:
        #Copy the sub folder
        os.chmod(os.path.dirname(Path_to_move), 444)
        copy_tree(os.path.dirname(Path_to_move), OutputFolder)
        add_to_log("Just copied: " + str(Path_to_move) + " to " + OutputFolder)

        #Delete orginal folder
        shutil.rmtree(Path_to_move)

    except shutil.Error as e:
        print e.message
        add_to_log(str(e))
        pass
    except WindowsError as e:
       add_to_log(e.message)
    except IOError as e:
        print e.message
        add_to_log(e.message)

def move_folders(InputFolder, OutputFolder):
    try:
        folder_list = os.listdir(InputFolder)
        add_to_log("This current folders list: " + str(folder_list) + " in input folder " + str(InputFolder))
        filter = fnmatch.filter(folder_list, "??-??-????")
        #Insert condition folder is from todays date
        #print filter
        current_date = (time.strftime("%d-%m-%Y"))
        for Folder in filter:
            if Folder == current_date:
                inside_folders_list = os.listdir(InputFolder + '\\' + Folder)
                inside_filter = fnmatch.filter(inside_folders_list, "???")
                print inside_filter[:-1]
                for inside_folder in inside_filter[:-1]:
                    FolderPath = os.path.join(InputFolder, Folder, str(inside_folder))
                    full_output_folder = os.path.join(OutputFolder,Folder)
                    move_selected_folders(FolderPath, full_output_folder)
                add_to_log("This is the current folder so we move all folders except the current working folder: " + str(inside_filter))
            else:
                inside_folders_list = os.listdir(InputFolder + '\\' + Folder)
                inside_filter = fnmatch.filter(inside_folders_list, "???")
                for inside_folder in inside_filter:
                    ############################################################################
                    FolderPath = os.path.join(InputFolder, Folder, str(inside_folder))
                    full_output_folder = os.path.join(OutputFolder,Folder)
                    move_selected_folders(FolderPath, full_output_folder)
    except WindowsError as e:
        add_to_log("ERROR({0}): {1} {2}".format(e.winerror, e.strerror, e.filename))


        #add_to_log("ERROR({0}): {1}".format(e.errno, e.strerror))
        #add_to_log(e.message)
        #pass






#Starting the code!

if init()[1] == 1:
    #print init()[0]

    #print read_config_file()[0]
    #This is were we parse INPUT FOLDER
    input_folder_paths = []
    for key in read_config_file()[0]:
        if key.startswith('input'):
            #print key
            input_folder_paths.append(read_config_file()[0][key])
    #print input_folder_paths

    # This is were we parse FILE TYPES
    file_type_names = []
    for key in read_config_file()[0]:
        if key.startswith('file'):
            #print key
            file_type_names.append(read_config_file()[0][key])
    #print file_type_names

    log_name = read_config_file()[0]['log_name']
    output_folder = read_config_file()[0]['output_folder']
    value_to_move = read_config_file()[0]['value_to_move']
    max_log_size = int(read_config_file()[0]['max_log_size'])
    scan_interval = int(read_config_file()[0]['scan_interval'])
    create_log(log_name)
    add_to_log("Initiating start, Read Sccess!")
    add_to_log("Config file dict == " + str(read_config_file()[0]))
    ############################# AT THIS POINT INIT PASSED!!!!!##################################################
    while True:
        for input_path in input_folder_paths:
            current_output_folder = output_folder + '\\' + os.path.basename(input_path)
            add_to_log("Working directory is: " + current_output_folder)
            move_folders(input_path, current_output_folder)
        add_to_log("Checking log size")
        current_log_size = file_size(log_name)
        #print log_size
        if  current_log_size >= max_log_size:
            add_to_log("Clearing log file")
            clear_log()
        add_to_log("Going to sleep for %s sec" % str(scan_interval))
        time.sleep(scan_interval)


else:
    add_to_log("Error in init function")


