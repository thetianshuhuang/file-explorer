# filesystem_base
# base class for filesystem handling

import sublime_plugin
import os
import getpass


class filesystembaseCommand(sublime_plugin.WindowCommand):

    #   --------------------------------
    #
    #   Attributes
    #
    #   --------------------------------

    # OS secific path information
    default_linux_path = "/home"
    default_windows_path = "C:\\Users"
    unrecognized_os_path = ""

    windows_root = "C:\\"
    linux_root = "/"

    linux_illegal_chars = ["\0"]
    windows_illegal_chars = ["<", ">", ":", '"', "/", "|", "?", "*"]
    default_illegal_chars = []

    # OS specific file divisions
    div_posix = "/"
    div_nt = "\\"
    div_unkn = "/"

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
            self.illegal_chars = self.linux_illegal_chars
        elif (os.name == 'nt'):
            self.default_path = (
                self.default_windows_path + self.div_nt + username)
            self.div = self.div_nt
            self.root_dir = self.windows_root
            self.illegal_chars = self.windows_illegal_chars
        else:
            self.default_path = self.unrecognized_os_path
            self.div = self.div_unkn
            self.root_dir = self.unrecognized_os_path
            self.illegal_chars = self.default_illegal_chars


#   --------------------------------
#
#   Insert line command
#
#   --------------------------------
class insertlineCommand(sublime_plugin.TextCommand):
    def run(self, edit, line, point):
        self.view.insert(edit, point, line + "\n")
