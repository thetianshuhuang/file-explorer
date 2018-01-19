# command_handler
# parses commands, separates flags, etc

import os


#   --------------------------------
#
#   Separate flags from command
#
#   --------------------------------
def identify_flags(div, text):
    lastslash = text.rfind(div)
    lastdash = text.rfind(" -")

    if(lastdash > lastslash and lastdash > 0):
        flags = text[lastdash + 2:]
        text = text[0:lastdash]
    else:
        flags = ""

    return(text, flags)


#   --------------------------------
#
#   Check for exceptions in the filepath
#
#   --------------------------------
def check_for_exceptions(illegal_chars, filepath):
    # if it is a directory, we can automatically scan for errors
    if(os.path.isdir(filepath)):
        try:
            os.listdir(filepath)
            return("pass")
        except PermissionError:
            return("PermissionError")
        return("UnkownError")

    # otherwise, manually check for forbidden characters
    else:
        for char in illegal_chars:
            if(filepath.find(char) > 1):
                return("IllegalPathError")
        return("pass")


#   --------------------------------
#
#   Collapse parent directory operators
#
#   --------------------------------
def collapse_parent_dir(div, filepath):
    location = filepath.find(div + "..")
    while(location > 0):
        elimstart = filepath.rfind(div, 0, location)
        if(elimstart <= 0):
            elimstart = location
        filepath = filepath[0:elimstart] + filepath[location + 3:]
        location = filepath.find(div + "..")

    return(filepath)


#   --------------------------------
#
#   Check if the filepath is absolute
#
#   --------------------------------
def is_absolute(div, text):

    # on linux, check if the first character is "/"
    if(os.name == "posix"):
        if(text[0] == div):
            return(True)
        else:
            return(False)

    # on windows, check if the first three chars are "X:/"
    # for an arbitrary (capital) drive letter X
    elif(os.name == "nt"):
        if(text[0].isupper() and text[1] == ":"):
            return(True)
        else:
            return(False)

    # on unknown systems, assume that it has linux-like behavior
    else:
        if(text[0] == div):
            return(True)
        else:
            return(False)


#   --------------------------------
#
#   Compute filepath
#
#   --------------------------------
def compute_filepath(previous_path, div, root_dir, text):

    # process command and separate flags
    (text, flags) = identify_flags(div, text)

    # Special case: "..." (list currently open folders and choose one)
    if(text == "..."):
        # return "..."
        filepath = "..."

    # Special case: ".." (go up one directory)
    # if statement provides protection for going up too far
    elif(text == ".."):
        lastdirindex = previous_path.rfind(
            div, 0, len(previous_path) - 1)
        if(lastdirindex >= 0):
            filepath = previous_path[:lastdirindex]
        else:
            filepath = previous_path
        # empty filepath protection
        if(filepath == ""):
            filepath = root_dir

    # Special case: "." (do nothing)
    elif(text == "."):
        filepath = previous_path

    # If the input filepath is absolute:
    elif(is_absolute(div, text)):
        filepath = text

    # Else, the input should be appended to the existing path
    else:
        # add dividing '\' if one does not already exist
        if(previous_path[-1:] != div):
            previous_path += div
        filepath = previous_path + text

    # collapse '/../' operator
    filepath = collapse_parent_dir(div, filepath)

    return((filepath, flags))
