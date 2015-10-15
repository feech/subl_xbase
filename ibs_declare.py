import sublime
import sublime_plugin
import xml.etree.ElementTree as ET
import re
import os
import threading

IbsFiles = {}


class IbsLoader(threading.Thread):
    def __init__(self, file_name):
        self.result = None
        self.file_name = file_name
        self.file = None
        self.file_size = None
        threading.Thread.__init__(self)
 
    def run(self):
        try:
            with open(self.file_name) as f:
                buf = re.sub(r'(&#x(.){1,5};)', '', str(f.read()))
                self.file = ET.fromstring(buf)
                self.file_size = os.path.getsize(self.file_name)
                self.result = True
        except Exception as ex:
            print('Exception is happend', ex)
            self.result = False


class GoDefinitionXbaseCommand(sublime_plugin.TextCommand):
    def __init__(self, p):
        super().__init__(p)
        print('__init__ GoDefinitionXbaseCommand')
        self.loader = None
        self.loading_progress = 0
        self.mode = None

    def run(self, edit, **args):

        self.view.run_command('single_selection')
        self.view.run_command('expand_selection', {'to': 'word'})
        
        word = None
        for s in reversed(self.view.sel()):
            word = self.view.substr(s)
         
        if word:
            self.mode = args.get('mode')
            if self.mode == None:
                self.mode = 'decl'
            print('looking ' + self.mode + '....', word)

            word = word.lower()

            self.looking(word)

    def next_loading_char(self):
        seq = '|/-\\'
        self.loading_progress = (self.loading_progress+1) % len(seq)
        return '...' + seq[self.loading_progress]

    def looking(self, word):
        """
            # находит слово в словаре
            # загружает в отдельном потоке
            # показывает меню
        """
        file_name = self.get_filename_m()
        if self.loader == None:
            
            if self.is_need_to_load():
                self.loader = IbsLoader(file_name)
                self.loader.start()
                sublime.set_timeout(lambda: self.looking(word), 100)
                self.view.set_status('load', file_name)
            else:
                self.find_lines(word)
        else:
            if self.loader.is_alive():
                self.view.set_status('load', file_name+ self.next_loading_char())
                sublime.set_timeout(lambda: self.looking(word), 100)
            else:
                self.view.erase_status('load')
                if self.loader.result == True:
                    self.assign_new_file_m(self.loader.file, self.loader.file_size)
                    self.find_lines(word)
                else:
                    print('file not load')
                self.loader = None

    def find_lines(self, word):
        if self.mode == 'decl':
            self.find_lines_d(word)
        if self.mode == 'usage':
            self.find_lines_u(word)

    
    def find_lines_d(self, word):
        file = self.get_file_m()
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

    def find_lines_u(self, word):
        file = self.get_file_m()
        if file == None:
            print("file not loaded")
            return
        result = []
        text = []
        mask = re.compile(":")
        for o in file.findall("./object"):
            if word == mask.split(o.attrib['name'])[-1]:
                for file in o.findall("./file"):
                    text.append(str(len(file.findall("./line")))+"x "+file.attrib['name'])
                    result.append(file.attrib['name']+":"+file.find('line').attrib['number'])

        if len(text) > 0:
            self.view.show_popup_menu(text,
                lambda x: self.proc(result, x))
        else:
            print('not found')
        
    def proc(self, data, x = 0):
        if x != -1:
            file = self.select_file(data[x])
            print(data[x], ">>>>", file)
            self.view.window().open_file(file, sublime.ENCODED_POSITION)

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
        result = path
        if len(ret)>1:
            result += ":"+ret[1]
        if len(ret)>2:
            result += ":"+ret[2]
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

    def get_filename_m(self):
        if self.mode == 'decl':
            return "S:/IBS/prg/NSense.Lex.xml"
        if self.mode == 'usage':
            return "S:/IBS/prg/NSense.Ref.xml"
        if self.mode == 'load':
            return "S:/IBS/prg/NSense.Ref.xml"

    def get_file_m(self):
        if self.mode == 'decl':
            return IbsFiles.get('declare_file')
        if self.mode == 'usage':
            return IbsFiles.get('usage_file')
        if self.mode == 'load':
            return IbsFiles.get('usage_file')

    def get_file_size_m(self):
        if self.mode == 'decl':
            return IbsFiles.get('declare_file_size')
        if self.mode == 'usage':
            return IbsFiles.get('usage_file_size')
        if self.mode == 'load':
            return IbsFiles.get('usage_file_size')
            
    def assign_new_file_m(self, file, file_size):
        global IbsFiles
        if self.mode == 'decl':
            IbsFiles['declare_file'] = file
            IbsFiles['declare_file_size'] = file_size
        if self.mode == 'usage':
            IbsFiles['usage_file'] = file
            IbsFiles['usage_file_size'] = file_size
        if self.mode == 'load':
            IbsFiles['usage_file'] = file
            IbsFiles['usage_file_size'] = file_size

    def is_need_to_load(self):
        if self.mode == 'decl':
            return self.get_file_m() == None or self.get_file_size_m() != os.path.getsize(file_name)
        if self.mode == 'usage':
            return self.get_file_m() == None
        if self.mode == 'load':
            return True

