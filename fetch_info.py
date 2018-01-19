# fetch_info.py
# file/directory info fetch functions

import os
import datetime


#   --------------------------------
#
#   generate file info
#
#   --------------------------------
def generate_file_info(filepath, file, flags):
        # c (clean) flag: just display file name
        if(flags == "c"):
            fileinfo = file

        # v flag - output as comma separated values
        elif(flags == "v"):
            try:
                filesize = os.stat(
                    filepath).st_size
                filedate = os.stat(
                    filepath).st_mtime
                fileinfo = (str(filedate) + "," +
                            str(filesize) + "," +
                            file + ",")
            except PermissionError:
                fileinfo = ("ERR,ERR," + file + ",")

        # normal operation: display file sizes and file names
        else:
            # get filesize
            filesizestr = get_filesize_string(filepath)

            # get date
            filedatestr = get_filedate_string(filepath)

            # add to file info
            fileinfo = (filedatestr +
                        filesizestr +
                        file)

        return(fileinfo)


#   --------------------------------
#
#   Get file size and format filesizestring
#
#   --------------------------------
def get_filesize_string(filepath):
    # get filesize
    try:
        filesize = os.stat(filepath).st_size
    except PermissionError:
        filesize = -1

    # filesize > 1GB -> use GB suffix
    if(filesize >= 1000000000):
        filesizestr = str(round(filesize / 1000000000., 1)) + " GB"
    # 1GB > filesize > 1MB
    elif(filesize >= 1000000):
        filesizestr = str(round(filesize / 1000000., 1)) + " MB"
    # 1MB > filesize > 1KB
    elif(filesize >= 1000):
        filesizestr = str(round(filesize / 1000, 1)) + " KB"
    # 1KB > filesize
    elif(filesize >= 0):
        filesizestr = str(filesize) + " bytes"
    # Error state
    else:
        filesizestr = ""

    # align file names at 12 columns (4 tabs)
    filesizestr += " " * (12 - len(filesizestr))

    return(filesizestr)

#   --------------------------------
#
#   Get filedatestring
#
#   --------------------------------
def get_filedate_string(filepath):

    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

    try:
        filedate = os.stat(filepath).st_mtime
    except PermissionError:
        filedate = -1

    if(filedate >= 0):
        filedatelist = datetime.datetime.fromtimestamp(filedate)

        # format date as MMM DD HH:MM
        filedatestr = months[filedatelist.month - 1] + " "
        if(filedatelist.day < 10):
            filedatestr += "0"
        filedatestr += str(filedatelist.day) + " "
        if(filedatelist.hour < 10):
            filedatestr += "0"
        filedatestr += str(filedatelist.hour) + ":"
        if(filedatelist.minute < 10):
            filedatestr += "0"
        filedatestr += str(filedatelist.minute) + " " * 4

    else:
        filedatestr = "PermissionError "

    return(filedatestr)