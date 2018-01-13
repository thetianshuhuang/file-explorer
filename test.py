import sublime
import sublime_plugin
import os

class emacsstyleopenCommand(sublime_plugin.WindowCommand):
	def run(self):

		self.window.show_input_panel("Find file:", "", self.on_done, None, None)

	def on_done(self, text):

		region = sublime.Region(0,self.window.active_view().text_point(1,0)-1)
		previous_path = self.window.active_view().substr(region)

		# if there is no previous path, set it to the first open folder.
		if(previous_path == "" or previous_path[0] != "/"):
			previous_path = self.window.folders()[0]

		# Special case: ".." (go up one directory)
		if(text == ".."):
			filepath = previous_path[:previous_path.rfind("/")]

		# Special case: "." (do nothing)
		elif(text == "."):
			filepath = previous_path

		# A path has already be selected,
		# and the input is to be appended to the existing path
		elif(text[0] != "/"):
			# add dividing '\' if one does not already exist
			if(previous_path[-1:] != "/"):
				previous_path += "/"
			filepath = previous_path + text

		# otherwise, use the input file path.
		else:
			filepath = text



		# file => open it
		if(os.path.isfile(filepath)):
			self.window.open_file(filepath)

		# directory => display contents
		elif(os.path.isdir(filepath)):
			# get directory contents
			directory_contents = os.listdir(filepath)

			# create output file
			self.window.new_file()

			self.window.active_view().run_command("insertfilename",
				{"line": filepath + "\nDirectory contents:\n\n", 
				"point": 0})

			info_offset = 3
			for x in range(0,len(directory_contents)):
				point = self.window.active_view().text_point(x + info_offset,0)
				self.window.active_view().run_command("insertfilename", 
					{"line": directory_contents[x], 
					"point": point})

		# neither => display error message
		else:
			self.window.active_view().run_command("insertfilename",
				{"line": filepath + "\nError: not a valid file or directory path\n",
				"point": 0})


class insertfilenameCommand(sublime_plugin.TextCommand):
	def run(self, edit, line, point):
		self.view.insert(edit, point, line + "\n")
