import sublime_plugin
import os
import getpass
import datetime


class fileexplorerCommand(sublime_plugin.WindowCommand):

    #   --------------------------------
    #
    #   Attributes
    #
    #   --------------------------------

    # OS secific paths
    default_linux_path = "/home"
    default_windows_path = "C:\\Users"
    unrecognized_os_path = ""
    windows_root = "C:\\"
    linux_root = "/"

    # OS specific file divisions
    div_posix = "/"
    div_nt = "\\"
    div_unkn = "/"

    # plugin data
    active_explorer_windows = {}

    # plugin settings
    info_offset = 2

    #   --------------------------------
    #
    #   Set up OS localization
    #
    #   --------------------------------
    def set_up_os(self):

        username = getpass.getuser()

        # detect operating system
        if (os.name == 'posix'):
            self.default_path = (
                self.default_linux_path + self.div_posix + username)
            self.div = self.div_posix
            self.root_dir = self.linux_root
        elif (os.name == 'nt'):
            self.default_path = (
                self.default_windows_path + self.div_nt + username)
            self.div = self.div_nt
            self.root_dir = self.windows_root
        else:
            self.default_path = self.unrecognized_os_path
            self.div = self.div_unkn
            self.root_dir = self.unrecognized_os_path

    #   --------------------------------
    #
    #   Show input window
    #
    #   --------------------------------
    def run(self):
        self.window.show_input_panel(
            "Find file:", "", self.on_done, None, None)

    #   --------------------------------
    #
    #   Main function
    #
    #   --------------------------------
    def on_done(self, text):

        # set up operating system compatibility
        self.set_up_os()

        # process command and separate flags
        processed_command = self.identify_flags(text)
        text = processed_command[0]
        flags = processed_command[1]

        # generate filepath
        filepath = self.compute_filepath(text)

        # open the filepath
        self.open_path(filepath, flags)

    #   --------------------------------
    #
    #   Compute filepath
    #
    #   --------------------------------
    def compute_filepath(self, text):
        previous_path = self.check_active_view()

        # Special case: ".." (go up one directory)
        # if statement provides protection for going up too far
        if(text == ".."):
            lastdirindex = previous_path.rfind(
                self.div, 0, len(previous_path) - 1)
            if(lastdirindex >= 0):
                filepath = previous_path[:lastdirindex]
            else:
                filepath = previous_path
            # empty filepath protection
            if(filepath == ""):
                filepath = self.root_dir

        # Special case: "." (do nothing)
        elif(text == "."):
            filepath = previous_path

        # and the input is to be appended to the existing path
        elif(text[0] != self.div):
            # add dividing '\' if one does not already exist
            if(previous_path[-1:] != self.div):
                previous_path += self.div
            filepath = previous_path + text

        # otherwise, use the input file path.
        else:
            filepath = text

        # collapse '/../' operator
        filepath = self.collapse_parent_dir(filepath)

        return(filepath)

    #   --------------------------------
    #
    #   Collapse parent directory operators
    #
    #   --------------------------------
    def collapse_parent_dir(self, filepath):
        location = filepath.find(self.div + "..")
        while(location > 0):
            elimstart = filepath.rfind(self.div, 0, location)
            if(elimstart <= 0):
                elimstart = location
            filepath = filepath[0:elimstart] + filepath[location + 3:]
            location = filepath.find(self.div + "..")

        return(filepath)

    #   --------------------------------
    #
    #   Check if current view should be closed
    #
    #   --------------------------------
    def check_active_view(self):

        active_view = self.window.active_view().id()

        # close an existing directory list of a new one is being opened on top.
        # set the previous path to the saved one
        try:
            previous_path = self.active_explorer_windows[active_view]
            self.window.run_command("close")
        except KeyError:
            # otherwise, set to the first open folder
            try:
                previous_path = self.window.folders()[0]
            # still no luck, go to default
            except ValueError:
                previous_path = self.default_path

        return(previous_path)

    #   --------------------------------
    #
    #   Show input window
    #
    #   --------------------------------
    def identify_flags(self, text):
        lastslash = text.rfind(self.div)
        lastdash = text.rfind(" -")

        if(lastdash > lastslash and lastdash > 0):
            flags = text[lastdash + 2:]
            text = text[0:lastdash]
        else:
            flags = ""

        return((text, flags))

    #   --------------------------------
    #
    #   Open the path
    #
    #   --------------------------------
    def open_path(self, filepath, flags):
        # file => open it
        if(os.path.isfile(filepath)):
            self.window.open_file(filepath)

        # is file name, but file doesn't exist
        elif(not os.path.isdir(filepath)):
            self.window.open_file(filepath)

        # otherwise, create the output file.
        else:
            # create new file, and set to scratch for silent closings.
            self.window.new_file()
            self.window.active_view().set_scratch(True)
            # log the ID and filepath of the new window
            self.active_explorer_windows.update({
                self.window.active_view().id(): filepath})

            # directory => display contents
            if(os.path.isdir(filepath)):
                self.display_directory_contents(filepath, flags)

            # neither => display error message
            else:
                self.display_error_message(filepath)

    #   --------------------------------
    #
    #   Display directory contents
    #
    #   --------------------------------
    def display_directory_contents(self, filepath, flags):

        # normalize filepath
        if(filepath[-1] != self.div):
            filepath = filepath + self.div

        # get directory contents
        directory_contents = os.listdir(filepath)

        # set file name
        self.set_file_name(filepath, flags)

        # add title and information
        self.window.active_view().run_command(
            "insertfilename", {"line": filepath + "\n\n", "point": 0})

        # display files in directory
        row = 0
        for file in directory_contents:

            # get file info (each line in the output view)
            fileinfo = self.generate_file_info(filepath, file, flags)

            # generate the correct point
            point = self.window.active_view().text_point(
                row + self.info_offset, 0)
            row += 1

            # write file info
            self.window.active_view().run_command(
                "insertfilename", {"line": fileinfo, "point": point})

    #   --------------------------------
    #
    #   generate file info
    #
    #   --------------------------------
    def generate_file_info(self, filepath, file, flags):
            # c (clean) flag: just display file name
            if(flags == "c"):
                fileinfo = file

            # v flag - output as comma separated values
            elif(flags == "v"):
                filesize = os.stat(
                    filepath + self.div + file).st_size
                filedate = os.stat(
                    filepath + self.div + file).st_mtime
                fileinfo = (str(filedate) + "," +
                            str(filesize) + "," +
                            file + ",")

            # normal operation: display file sizes and file names
            else:
                # get filesize
                filesizestr = self.get_filesize_string(
                    filepath + self.div + file)

                # get date
                filedatestr = self.get_filedate_string(
                    filepath + self.div + file)

                # add to file info
                fileinfo = (filedatestr + (" " * 4) +
                            filesizestr +
                            file)

            return(fileinfo)

    #   --------------------------------
    #
    #   set file name
    #
    #   --------------------------------
    def set_file_name(self, filepath, flags):
        # set output file name
        lastdir = filepath[filepath.rfind(self.div, 0, -1):]

        # in csv mode, name the file appropriately
        if(flags == "v"):
            self.window.active_view().set_name(lastdir + "_contents.csv")
        # otherwise, make the current directory clear
        else:
            if(lastdir != filepath):
                lastdir = "..." + lastdir
            self.window.active_view().set_name(lastdir)

    #   --------------------------------
    #
    #   Get filesizestring
    #
    #   --------------------------------
    def get_filesize_string(self, filepath):
        # get filesize
        filesize = os.stat(filepath).st_size

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
        else:
            filesizestr = str(filesize) + " bytes"

        # align file names at 12 columns (4 tabs)
        filesizestr += " " * (12 - len(filesizestr))

        return(filesizestr)

    #   --------------------------------
    #
    #   Get filedatestring
    #
    #   --------------------------------
    def get_filedate_string(self, filepath):

        months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

        filedate = os.stat(filepath).st_mtime
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
        filedatestr += str(filedatelist.minute)

        return(filedatestr)

    #   --------------------------------
    #
    #   Display error message
    #
    #   --------------------------------
    def display_error_message(self, filepath):

        self.window.active_view().set_name("Error")
        self.window.active_view().run_command(
            "insertfilename",
            {"line": filepath +
             "\nError: not a valid file or directory path\n",
             "point": 0})


#   --------------------------------
#
#   Insert line
#
#   --------------------------------

# for some reason, sublime requires a separate command.
class insertfilenameCommand(sublime_plugin.TextCommand):
    def run(self, edit, line, point):
        self.view.insert(edit, point, line + "\n")
