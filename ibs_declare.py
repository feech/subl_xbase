import sublime
import sublime_plugin
import xml.etree.ElementTree as ET
import re
import os

GoDefinitionXbaseCommandFile = False

def plugin_loaded():
	print('OK')
	# select_file(None)







class GoDefinitionXbaseCommand(sublime_plugin.TextCommand):
	def __init__(self, p):
		super().__init__(p)
		self.file = GoDefinitionXbaseCommandFile
		print('__init__ GoDefinitionXbaseCommand')

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
			file = self.select_file(data[x])
			print(">>>>", file)
			self.view.window().open_file(file, sublime.ENCODED_POSITION)

	def load_file(self):
		if self.file == False:
			print('!!!! load file !!!!')
			self.file = ET.parse("S:/IBS/prg/NSense.Lex.xml")
			global GoDefinitionXbaseCommandFile
			GoDefinitionXbaseCommandFile = self.file
		return self.file

	def select_file(self, remote_file):

		# rf = "S:\\IBS\\prg\\post\\rlake\\session\\xxx.prg:22:33"
		# rf = "S:\\IBS\\prg\\post\\rlake\\rlSendDoc.prg:11:22"
		# lo = "C:\\Users\\ako\\Documents\\prj\\post\\rlake\\rlSendDoc.prg"
		# print("!!!!", remote_file)

		rf = remote_file
		lo = self.view.file_name()

		red, ret_p = os.path.splitdrive(rf)
		lod, lot_p = os.path.splitdrive(lo)
		# print('pair', lod, lot_p)
		
		mask = re.compile(":")
		ret = mask.split(ret_p)

		path = mm(lo, os.path.join(red,ret[0]))
		if not path:
			return remote_file
		result = path+":"+ret[1]+":"+ret[2]
		print('result', result)
		return result

	def mm(self, p_local, p_remote):
		lo = p_local
		while True:
			lo, lot = os.path.split(lo)
			if not lot:
				return ''
			re = p_remote
			while True:
				re, ret = os.path.split(re)
				if not ret:
					break
				if ret == lot:
					print('before check', p_remote, re, os.path.relpath(p_remote, re))
					res = os.path.join(lo, os.path.relpath(p_remote, re))
					print('check: ', res)
					if os.path.exists(res):
						print("we found", res)
						return res
					else:
						print("failed: ", res)
					print("LOOP")

		return p_remote