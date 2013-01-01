#coding:utf-8
import sublime
import sublime_plugin
import os,threading
import locale,codecs
import subprocess

code = codecs.lookup(locale.getpreferredencoding()).name
settings = sublime.load_settings('TortoiseSVN.sublime-settings')
tortoiseproc = settings.get('tortoiseproc_path');

def findFile(folders, file_name):
	if folders is None:
		return False

	for folder in folders:
		if os.path.exists(os.path.join(folder, file_name)) is True:
			return True

	return False


def getFolders(file_path):
	if file_path is None:
		return []

	folders = [file_path]
	limit = 5

	while True:
		split = os.path.split(file_path)

		# nothing found
		if len(split) == 0:
			break

		# get filepath
		file_path = split[0]
		limit -= 1

		# nothing else remains
		if len(split[1]) == 0 or limit < 0:
			break

		folders.append(split[0])

	return folders

class SvnUpdateCommand(sublime_plugin.TextCommand):
	def run(self, edit, paths=None):
		if paths:
			dir = '*'.join(paths)
		else:
			dir = self.view.file_name()

		thread = ThreadAPI('update',dir)
		thread.start()
		self.handle_thread(thread)

	def handle_thread(self,thread):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread), 1000)
			return
		if thread.result == True:
			sublime.status_message("Update Success!")

	def is_visible(self,paths = []):
		paths=paths[0]
		is_visible = False
		if findFile(getFolders(paths),'.svn') == True:
			is_visible = True
		return is_visible

class SvnCommitCommand(sublime_plugin.TextCommand):
	def run(self, edit, paths=None):
		if paths:
			dir = '*'.join(paths)
		else:
			dir = self.view.file_name()
		thread = ThreadAPI('commit',dir)
		thread.start()
		self.handle_thread(thread)

	def handle_thread(self,thread):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread), 1000)
			return
		if thread.result == True:
			sublime.status_message("commit success!")

	def is_visible(self,paths = []):
		paths=paths[0]
		is_visible = False
		if findFile(getFolders(paths),'.svn') == True:
			is_visible = True
		return is_visible

class ThreadAPI(threading.Thread):
	def __init__(self,command,dir):
		threading.Thread.__init__(self);
		self.dir = dir
		self.command = command
		self.result = None
	def run(self):
		
		cmd = [tortoiseproc.encode(code), '/closeonend:3', ('/command:' + self.command), ('/path:' + self.dir.encode(code))]
		#cmd = '"%s" /closeonend:3 /command:%s /path:%s' % (tortoiseproc, command, path)
		popen = subprocess.Popen(cmd)
		popen.communicate()
		self.result = True