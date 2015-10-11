import sublime
import sublime_plugin
import xml.etree.ElementTree as ET
import re
import os
import threading

GoDefinitionXbaseCommandFile = False
GoDefinitionXbaseCommandSize = 0

# def plugin_loaded():


class IbsLoader(threading.Thread):
    def __init__(self, file_name):
        self.result = None
        self.file_name = file_name
        self.file = None
        self.file_size = None
        threading.Thread.__init__(self)
 
    def run(self):
        try:
            print("run start")
            self.file = ET.parse(self.file_name)
            self.file_size = os.path.getsize(self.file_name)
            self.result = True
            print("run finish")
        except Exception:
            print("run except")
            self.result = False


class GoDefinitionXbaseCommand(sublime_plugin.TextCommand):
    def __init__(self, p):
        super().__init__(p)
        print('__init__ GoDefinitionXbaseCommand')
        self.loader = None

    def run(self, edit):

        self.view.run_command('single_selection')
        self.view.run_command('expand_selection', {'to': 'word'})
        
        word = False
        for s in reversed(self.view.sel()):
            word = self.view.substr(s)
         
        if word:
            print('looking ....', word)

            word = word.lower()

            self.loading(word)

    # def loading_file():

    def loading(self, word):
        if self.loader == None:
            file_name = "S:/IBS/prg/NSense.Lex.xml"
            if GoDefinitionXbaseCommandFile == False or GoDefinitionXbaseCommandSize != os.path.getsize(file_name):
                self.loader = IbsLoader(file_name)
                self.loader.start()
                sublime.set_timeout(lambda: self.loading(word), 100)
            else:
                self.find_lines(word)
        else:
            if self.loader.is_alive():
                sublime.set_timeout(lambda: self.loading(word), 100)
            else:
                if self.loader.result == True:
                    self.assign_new_file(self.loader.file, self.loader.file_size)
                    self.find_lines(word)
                else:
                    print('file not load')
                self.loader = None


    def find_lines(self, word):
        file = GoDefinitionXbaseCommandFile
        if file == None:
            print("file not loaded")
            return
        result = []
        mask = re.compile(":")
        for o in file.findall("./object"):
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
        #   self.view.set_status('error', 'can\'t find declaration')
        
    def proc(self, data, x = 0):
        print('proc...', x)
        if x != -1:
            file = self.select_file(data[x])
            print(">>>>", file)
            self.view.window().open_file(file, sublime.ENCODED_POSITION)

    def assign_new_file(self, file, size):
        global GoDefinitionXbaseCommandFile
        global GoDefinitionXbaseCommandSize
        GoDefinitionXbaseCommandFile = file
        GoDefinitionXbaseCommandSize = size
        
    def select_file(self, remote_file):
        return GoDefinitionXbaseCommand.match_file(self.view.file_name(), remote_file)

    def match_file(local_file, remote_file):

        # rf = "S:\\IBS\\prg\\post\\rlake\\session\\xxx.prg:22:33"
        # rf = "S:\\IBS\\prg\\post\\rlake\\rlSendDoc.prg:11:22"
        # lo = "C:\\Users\\ako\\Documents\\prj\\post\\rlake\\rlSendDoc.prg"
        # print("!!!!", remote_file)

        rf = remote_file
        lo = local_file

        red, ret_p = os.path.splitdrive(rf)
        lod, lot_p = os.path.splitdrive(lo)
        
        mask = re.compile(":")
        ret = mask.split(ret_p)

        path = GoDefinitionXbaseCommand.iterate_path(lo, os.path.join(red,ret[0]))
        if not path:
            return remote_file
        result = path+":"+ret[1]+":"+ret[2]
        print('result', result)
        return result

    # подбирает локальный файл по имени похожий на файл из репозитория
    def iterate_path(p_local, p_remote):
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
                    res = os.path.join(lo, os.path.relpath(p_remote, re))
                    if os.path.exists(res):
                        return res

        return p_remote