# file-explorer.py
# main file, main class

import os
from .fetch_info import *
from .command_handler import *
from .filesystem_base import *


class fileexplorerCommand(filesystembaseCommand):

    #   --------------------------------
    #
    #   Attributes
    #
    #   --------------------------------

    # plugin settings
    info_offset = 2

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

        # generate filepath
        previous_path = self.check_active_view()

        # handle special case (choose from open project folders)
        if(previous_path == "..."):
            text = self.find_folder(text)

        # get filepath and flags
        (filepath, flags) = compute_filepath(
            previous_path, self.div, self.root_dir, text)

        # open the filepath
        self.open_path(filepath, flags)

    #   --------------------------------
    #
    #   Find filepath from last directory name
    #
    #   --------------------------------
    def find_folder(self, text):
        for folder in self.window.folders():
            if(folder.rfind(text) + len(text) == len(folder)):
                filepath = folder
                return(filepath)
        return(text)

    #   --------------------------------
    #
    #   Check if current view should be closed
    #
    #   --------------------------------
    def check_active_view(self):
        # check if view is in database
        self.window.run_command(
            "viewmanager", {"method": "is_registered_view", "label": ""})
        view_id = self.get_return("view_id")
        previous_path = self.get_return("label")

        # view in db
        if(view_id != 0):
            # close view
            self.window.run_command(
                "viewmanager", {"method": "close_view", "label": ""})

        # view not in db
        else:
            # list of open project folders is not empty
            if(len(self.window.folders()) > 0):
                previous_path = self.window.folders()[0]
            # still no luck, go to default
            else:
                previous_path = self.default_path

        return(previous_path)

    #   --------------------------------
    #
    #   Display open folders
    #
    #   --------------------------------
    def display_open_folders(self, flags):

        # label tab as 'Open Folders'
        self.window.active_view().set_name("Open Folders")

        # print out description
        self.window.active_view().run_command(
            "insertline",
            {"line": "Currently Open Project Folders: \n", "point": 0})

        row = 0
        for folder in self.window.folders():

            file = folder[folder.rfind(self.div) + 1:]

            fileinfo = generate_file_info(folder, file, flags)

            # generate the correct point
            point = self.window.active_view().text_point(
                row + self.info_offset, 0)
            row += 1

            # write file info
            self.window.active_view().run_command(
                "insertline", {"line": fileinfo, "point": point})

    #   --------------------------------
    #
    #   Open the path
    #
    #   --------------------------------
    def open_path(self, filepath, flags):

        # Special control command: list open files
        if(filepath == "..."):
            self.create_new_view(filepath)
            self.display_open_folders(flags)

        # Normal control command
        else:
            exception_type = check_for_exceptions(self.illegal_chars, filepath)

            # The file passes the exception test.
            if(exception_type == "pass"):
                # file => open it
                if(os.path.isfile(filepath)):
                    self.window.open_file(filepath)

                # directory => display contents
                elif(os.path.isdir(filepath)):
                    self.create_new_view(filepath)
                    self.display_directory_contents(filepath, flags)

                # neither file nor directory, so create a file
                else:
                    self.window.open_file(filepath)

            # raise error message
            else:
                self.window.run_command(
                    "displayerrormessage",
                    {"filepath": filepath, "errortype": exception_type})

    #   --------------------------------
    #
    #   Create new view
    #
    #   --------------------------------
    def create_new_view(self, filepath):
            self.window.run_command(
                "viewmanager",
                {"method": "create_new_view", "label": filepath})

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
            "insertline", {"line": filepath + "\n\n", "point": 0})

        # display files in directory
        row = 0
        for file in directory_contents:

            # don't display hidden files unless the 'a' flag is passed
            if(file[0] != '.' or 'a' in flags):
                # get file info (each line in the output view)
                fileinfo = generate_file_info(
                    filepath + self.div + file, file, flags)

                # generate the correct point
                point = self.window.active_view().text_point(
                    row + self.info_offset, 0)
                row += 1

                # write file info
                self.window.active_view().run_command(
                    "insertline", {"line": fileinfo, "point": point})

    #   --------------------------------
    #
    #   set file name
    #
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
