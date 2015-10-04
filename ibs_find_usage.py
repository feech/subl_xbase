import sublime
import sublime_plugin
import xml.etree.ElementTree as ET
import re

FindUsageCommandXbaseCommandFile = False

class FindUsageCommandXbaseCommand(sublime_plugin.TextCommand):
	def __init__(self, p):
		super().__init__(p)
		self.file = FindUsageCommandXbaseCommandFile
		print('__init__ FindUsageCommandXbaseCommand')


	def run(self, edit):
		self.view.run_command('single_selection')
		self.view.run_command('expand_selection', {'to': 'word'})
		
		word = False
		for s in reversed(self.view.sel()):
			word = self.view.substr(s)
		 
		if word:
			print('looking ....', word)

			word = word.lower()
			# print('find using of: :', word)

			text = []
			result = []
			mask = re.compile(":")
			for o in self.load_file().findall("./object"):
				if word == mask.split(o.attrib['name'])[-1]:
					for file in o.findall("./file"):
						text.append(str(len(file.findall("./line")))+"x "+file.attrib['name'])
						result.append(file.attrib['name']+":"+file.find('line').attrib['number'])

						# print('x', )
			if len(text) > 0:
				self.view.show_popup_menu(text,
					lambda x: self.proc(result, x))
			else:
				print('not found')

	def proc(self, data, x = 0):
		print('proc...', x)
		if x != -1:
			self.view.window().open_file(data[x], sublime.ENCODED_POSITION)


	def load_file(self):
		if self.file == False:
			# filename = 'C:/Users/ako/Downloads/NSense.Ref.xml'
			filename = 'S:/IBS/prg/NSense.Ref.xml'
			print('!!!! load file !!!!', filename)
			with open(filename) as f:
				buf = re.sub(r'(&#x(.){1,5};)', '', str(f.read()))
				self.file = ET.fromstring(buf)
				global FindUsageCommandXbaseCommandFile
				FindUsageCommandXbaseCommandFile = self.file
		return self.file