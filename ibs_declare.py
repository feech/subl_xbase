import sublime
import sublime_plugin
import xml.etree.ElementTree as ET
import re

GoDefinitionXbaseCommandFile = False

class GoDefinitionXbaseCommand(sublime_plugin.TextCommand):
	def __init__(self, p):
		super().__init__(p)
		self.file = GoDefinitionXbaseCommandFile
		print('__init__ GoDefinitionXbaseCommand')

	def plugin_loaded():
		print("i'm ready")

	def run(self, edit):

		self.view.run_command('single_selection')
		self.view.run_command('expand_selection', {'to': 'word'})
		
		word = False
		for s in reversed(self.view.sel()):
			word = self.view.substr(s)
		 
		if word:
			print('looking ....', word)

			word = word.lower()

			result = []
			mask = re.compile(":")
			for o in self.load_file().findall("./object"):
				if word == mask.split(o.attrib['name'])[-1]:
					for detail in o.findall("./details"):
						result.append(detail.attrib['file']+":"+detail.attrib['line']+":"+detail.attrib['col'])

			if len(result)>1:
				self.view.show_popup_menu(result,  
					lambda x: self.proc(result, x))
			elif len(result) == 1:
				self.proc(result)
			# else:
				# print("not found")
			# 	self.view.set_status('error', 'can\'t find declaration')
		
	def proc(self, data, x = 0):
		print('proc...', x)
		if x != -1:
			self.view.window().open_file(data[x], sublime.ENCODED_POSITION)

	def load_file(self):
		if self.file == False:
			print('!!!! load file !!!!')
			self.file = ET.parse("S:/IBS/prg/NSense.Lex.xml")
			global GoDefinitionXbaseCommandFile
			GoDefinitionXbaseCommandFile = self.file
		return self.file

