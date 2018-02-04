# view_manager.py
# common view management API for sharing sets of views between classes

import sublime
import sublime_plugin


class viewmanagerCommand(sublime_plugin.WindowCommand):

    #   --------------------------------
    #
    #   Attributes
    #
    #   --------------------------------

    # plugin data
    active_explorer_windows = {}

    #   --------------------------------
    #
    #   Main function:
    #
    #   --------------------------------

    # Get the requested method name, run the method, and pass the output
    def run(self, method, label):

        return_drop_file = sublime.load_settings(
            'return_drop_file.sublime-settings')

        (return_id, return_label) = getattr(self, method)(label)

        return_drop_file.set("view_id", return_id)
        return_drop_file.set("label", return_label)
        return_drop_file.set("teststr", "asdf\\")

    #   --------------------------------
    #
    #   Create new vieww
    #
    #   --------------------------------
    def create_new_view(self, label):
        # create new file, and set to scratch for silent closing.
        self.window.new_file()
        self.window.active_view().set_scratch(True)

        view_id = self.window.active_view().id()

        # log the ID and label in the database
        self.active_explorer_windows.update(
            {view_id: label})

        return((view_id, label))

    #   --------------------------------
    #
    #   Check if current view is in database
    #
    #   --------------------------------
    def is_registered_view(self, label):
        # get current view ID
        current_view = self.window.active_view().id()

        # current_view found => provide the corresponding filepath
        if(current_view in self.active_explorer_windows):
            return((current_view, self.active_explorer_windows[current_view]))
        else:
            return((0, ""))

    #   --------------------------------
    #
    #   Close the currently open view.
    #
    #   --------------------------------
    def close_view(self, label):
        view_id = self.window.active_view().id()
        # deregister view_id
        del(self.active_explorer_windows[view_id])
        # close current view.
        self.window.run_command("close")

        return((view_id, label))


#   --------------------------------
#
#   Insert line command
#
#   --------------------------------
class insertlineCommand(sublime_plugin.TextCommand):
    def run(self, edit, line, point):
        self.view.insert(edit, point, line + "\n")
