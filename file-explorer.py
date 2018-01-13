import sublime
import sublime_plugin
import os

class emacs_style_file_explorerCommand(sublime_plugin.WindowCommand):

	def run(self):

		self.window.show_input_panel("Find file:", "", self.on_done, None, None)

	def on_done(self, text):

		region = sublime.Region(0,self.window.active_view().text_point(1,0)-1)
		previous_path = self.window.active_view().substr(region)

		# close an existing directory list of a new one is being opened on top.
		if(previous_path != "" and previous_path[0] == "/"):
			self.window.run_command("close")

		# if there is no previous path, set it to the first open folder.
		if(previous_path == "" or previous_path[0] != "/"):
			previous_path = self.window.folders()[0]

		# Special case: ".." (go up one directory)
		# if statement provides protection for going up too far
		if(text == ".."):
			lastdirindex = previous_path.rfind("/")
			if(lastdirindex != 0):
				filepath = previous_path[:lastdirindex]
			else:
				filepath = previous_path

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
			self.window.active_view().set_scratch(True)
			lastdir = filepath[filepath.rfind("/"):]
			if(lastdir != filepath):
				lastdir = "..." + lastdir
			self.window.active_view().set_name(lastdir)

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
			self.window.new_file()
			self.window.active_view().set_scratch(True)
			self.window.active_view().set_name("Error")
			self.window.active_view().run_command("insertfilename",
				{"line": filepath + "\nError: not a valid file or directory path\n",
				"point": 0})

class insertfilenameCommand(sublime_plugin.TextCommand):
	def run(self, edit, line, point):
		self.view.insert(edit, point, line + "\n")
