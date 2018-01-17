import sublime
import sublime_plugin
import os
import getpass
import datetime

class emacs_style_file_explorerCommand(sublime_plugin.WindowCommand):


	#	--------------------------------
	#
	#	Attributes
	#	
	#	--------------------------------

	# OS secific paths
	default_linux_path = "/home"
	default_windows_path = "C:\\Users"
	unrecognized_os_path = ""

	# OS specific file divisions
	div_posix = "/"
	div_nt = "\\"
	div_unkn = "/"

	# plugin data
	active_explorer_windows = []


	#	--------------------------------
	#
	#	Set up OS localization
	#	
	#	--------------------------------
	def set_up_os(self):

		username = getpass.getuser()

		print(self.active_explorer_windows)

		# detect operating system
		if (os.name == 'posix'):
			self.default_path = self.default_linux_path + self.div_posix + username
			self.div = self.div_posix
		elif (os.name == 'nt'):
			self.default_path = self.default_windows_path + self.div_nt + username
			self.div = self.div_nt
		else:
			self.default_path = self.unrecognized_os_path
			self.div = self.div_unkn
		

	#	--------------------------------
	#
	#	Show input window
	#	
	#	--------------------------------
	def run(self):

		self.window.show_input_panel("Find file:", "", self.on_done, None, None)


	#	--------------------------------
	#
	#	Main function
	#	
	#	--------------------------------
	def on_done(self, text):

		# set up operating system compatibility
		self.set_up_os()

		# process command and separate flags
		processed_command = self.identify_flags(text)
		text = processed_command[0]
		flags = processed_command[1]

		# close an existing directory list of a new one is being opened on top.
		if(self.check_active_view()):
			region = sublime.Region(0,self.window.active_view().text_point(1,0)-1)
			previous_path = self.window.active_view().substr(region)
			self.window.run_command("close")

		# if there is no previous path, set it to the first open folder.
		# if that still isn't available, open the defualt path.
		else:
			try:
				previous_path = self.window.folders()[0]
			except:
				previous_path = self.default_path

		# Special case: ".." (go up one directory)
		# if statement provides protection for going up too far
		if(text == ".."):
			lastdirindex = previous_path.rfind(self.div)
			if(lastdirindex != 0):
				filepath = previous_path[:lastdirindex]
			else:
				filepath = previous_path

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

		# find "directory/../" and collapse them.
		location = filepath.find(self.div + "..")
		while(location > 0):
			elimstart = filepath.rfind(self.div,0,location)
			if(elimstart <= 0):
				elimstart = location
			filepath = filepath[0:elimstart] + filepath[location+3:]
			location = filepath.find(self.div + "..")

		self.open_path(filepath,flags)


	#	--------------------------------
	#
	#	Check if current view should be closed
	#	
	#	--------------------------------
	def check_active_view(self):
		for view in self.active_explorer_windows: 
			if(view == self.window.active_view().id()):
				self.active_explorer_windows.remove(view)
				return True
		return False


	#	--------------------------------
	#
	#	Show input window
	#	
	#	--------------------------------
	def identify_flags(self,text):
		lastslash = text.rfind(self.div)
		lastdash = text.rfind(" -")

		if(lastdash > lastslash and lastdash > 0):
			flags = text[lastdash+2:]
			text = text[0:lastdash]
		else:
			flags = ""

		return((text,flags))


	#	--------------------------------
	#
	#	Open the path
	#	
	#	--------------------------------
	def open_path(self,filepath,flags):
		# file => open it
		if(os.path.isfile(filepath)):
			self.window.open_file(filepath)

		# is file name, but file doesn't exist
		elif(filepath.rfind(".") > filepath.rfind(self.div) and filepath.rfind(".") != -1):
			self.window.open_file(filepath)

		# otherwise, create the output file.
		else:
			# create new file, and set to scratch for silent closings.
			self.window.new_file()
			self.window.active_view().set_scratch(True)
			# log the ID of the new window
			self.active_explorer_windows += [self.window.active_view().id()]

			# directory => display contents
			if(os.path.isdir(filepath)):
				self.display_directory_contents(filepath,flags)

			# neither => display error message
			else:
				self.display_error_message(filepath)


	#	--------------------------------
	#
	#	Display directory contents
	#	
	#	--------------------------------
	def display_directory_contents(self,filepath,flags):
		# get directory contents
		directory_contents = os.listdir(filepath)

		# set output file name
		lastdir = filepath[filepath.rfind(self.div):]

		# in csv mode, name the file appropriately
		if(flags == "v"):
			self.window.active_view().set_name(lastdir + "_contents.csv")
		# otherwise, make the current directory clear
		else:
			if(lastdir != filepath):
				lastdir = "..." + lastdir
			self.window.active_view().set_name(lastdir)

		# add title and information
		self.window.active_view().run_command("insertfilename",
			{"line": filepath + "\n\n", 
			"point": 0})

		# display files in directory
		info_offset = 2
		for x in range(0,len(directory_contents)):
			point = self.window.active_view().text_point(x + info_offset,0)
			
			# c (clean) flag: just display file name
			if(flags == "c"):
				fileinfo = directory_contents[x]

			# v flag - output as comma separated values
			elif(flags == "v"):
				filesize = os.stat(filepath + self.div + directory_contents[x]).st_size
				filedate = os.stat(filepath + self.div + directory_contents[x]).st_mtime
				fileinfo = str(filedate) + "," + str(filesize) + "," + directory_contents[x] + ","

			# normal operation: display file sizes and file names
			else:
				# get filesize
				filesize = os.stat(filepath + self.div + directory_contents[x]).st_size
				
				# filesize > 1GB -> use GB suffix
				if(filesize >= 1000000000):
					filesizestr = str(round(filesize / 1000000000.,1)) + " GB"
				# 1GB > filesize > 1MB
				elif(filesize >= 1000000):
					filesizestr = str(round(filesize / 1000000.,1)) + " MB"
				# 1MB > filesize > 1KB
				elif(filesize >= 1000):
					filesizestr = str(round(filesize / 1000,1)) + " KB"	
				# 1KB > filesize
				else:
					filesizestr = str(filesize) + " bytes"

				# align file names at 12 columns (4 tabs)
				filesizestr += " " * (12 - len(filesizestr))
				fileinfo = filesizestr + directory_contents[x]

				# get date
				months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

				filedate = os.stat(filepath + self.div+ directory_contents[x]).st_mtime
				filedatelist = datetime.datetime.fromtimestamp(filedate)
				
				# format date as MMM DD HH:MM
				filedatestr = months[filedatelist.month-1] + " " 
				if(filedatelist.day < 10):
					filedatestr += "0" 
				filedatestr += str(filedatelist.day) + " "
				if(filedatelist.hour < 10):
					filedatestr += "0" 
				filedatestr += str(filedatelist.hour) + ":"
				if(filedatelist.minute < 10): 
					filedatestr += "0" 
				filedatestr += str(filedatelist.minute)
				
				# add to file info
				fileinfo = filedatestr + "    " + fileinfo

			# write file info	
			self.window.active_view().run_command("insertfilename", 
				{"line": fileinfo, 
				"point": point})


	#	--------------------------------
	#
	#	Display error message
	#	
	#	--------------------------------
	def display_error_message(self,filepath):

		self.window.active_view().set_name("Error")
		self.window.active_view().run_command("insertfilename",
			{"line": filepath + "\nError: not a valid file or directory path\n",
			"point": 0})


class insertfilenameCommand(sublime_plugin.TextCommand):
	def run(self, edit, line, point):	
		self.view.insert(edit, point, line + "\n")
