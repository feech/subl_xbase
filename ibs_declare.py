import sublime
import sublime_plugin
import xml.sax

class GoDefinitionXbaseCommand(sublime_plugin.TextCommand):
	def __init__(self, p):
		super().__init__(p)
		self.file = False
		print('__init__')

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
			result = decl_selector(word)

			# загрузить файл если нужен
			xml.sax.parseString(self.load_file(), result)
			print(result.result(), len(result.result()))

			if len(result.result())>1:
				self.view.show_popup_menu(result.result(),  
					lambda x: self.proc(x))
			elif len(result.result()) == 1:
				self.proc(result.result()[0])
		
	def proc(self, x):
		print('proc...', x)
		if x != -1:
			self.view.window().open_file(x, sublime.ENCODED_POSITION)

	def load_file(self):
		if self.file == False:
			print('open')
			f = open("S:/IBS/prg/NSense.Lex.xml", 'rb')
			self.file = f.read()
		return self.file


class decl_selector(xml.sax.handler.ContentHandler):
	def __init__(self, word):
		self.word = word
		self.files = []

	def startElement(self, name, attr):
		if(name=="details" and attr.getValue("name")==self.word):
			self.files.append(attr.getValue("file")+":"+attr.getValue("line")+":"+attr.getValue("col"))

	def result(self):
		return self.files