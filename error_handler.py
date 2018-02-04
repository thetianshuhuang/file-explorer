# error_handler.py
# Common error message API

import sublime_plugin


#   --------------------------------
#
#   Display error message
#
#   --------------------------------
class displayerrormessageCommand(sublime_plugin.WindowCommand):

    #   --------------------------------
    #
    #   Error dictionary
    #
    #   --------------------------------
    error_descriptions = {
        "PermissionError":
            "Insufficient permissions. "
            " Run as root to see the contents of this filepath.",
        "IllegalPathError":
            "Illegal filepath. "
            "One or more characters in this filepath is forbidden.",
        "UnknownError":
            "Unknown error. "
            "Something's wrong with this filepath in an unanticipated manner"
    }

    #   --------------------------------
    #
    #   Create error message view
    #
    #   --------------------------------
    def run(self, filepath, errortype):
        self.window.run_command(
            "viewmanager", {"method": "create_new_view", "label": filepath})

        self.window.active_view().set_name(errortype)
        self.window.active_view().run_command(
            "insertline",
            {"line": filepath + "\n" +
             errortype + "\n" +
             self.error_descriptions[errortype],
             "point": 0})
