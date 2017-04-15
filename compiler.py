import os, sys, subprocess, re, json, psutil, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from time import sleep

class ProjectSettingsWindow(Gtk.Window):
    def __init__(self, parent, btn, entry, path, compiler):

        super(ProjectSettingsWindow, self).__init__()

        self.parent = parent
        self.compileBtn = btn
        self.stateEntry = entry
        self.path = path
        self.compiler = compiler

        self.set_default_size(400, 600)
        self.connect('destroy', self._quit)

        self.buildInterface()

        self.show_all()
    
    def buildInterface(self, *args):

        self.hb = Gtk.HeaderBar()
        self.hb.set_title('Run options')

        self.cancelBtn = Gtk.Button('Cancel')
        self.cancelBtn.connect('clicked', self._quit)
        self.continueBtn = Gtk.Button('Continue')
        self.continueBtn.connect('clicked', self.createMake)

        self.hb.pack_start(self.cancelBtn)
        self.hb.pack_end(self.continueBtn)
        self.set_titlebar(self.hb)

        self.set_transient_for(self.parent)

        ## ListBox

        self.listBox = Gtk.ListBox()
        self.listBox.set_selection_mode(Gtk.SelectionMode.NONE)

        v = Gtk.VBox()
        v.pack_start(Gtk.Label('Language'), True, True, 0)
        
        self.cLang = Gtk.RadioButton.new_with_label(None, 'C')
        self.cLang.connect('toggled', self.getLang)
        self.cppLang = Gtk.RadioButton.new_with_label_from_widget(self.cLang, 'C++')
        self.cppLang.connect('toggled', self.getLang)
        self.pyLang = Gtk.RadioButton.new_with_label_from_widget(self.cppLang, 'Python')
        self.pyLang.connect('toggled', self.getLang)
        self.otherLang = Gtk.RadioButton.new_with_label_from_widget(self.pyLang, 'Other')
        self.otherLang.connect('toggled', self.getLang)

        ##
        self.cLang.set_mode(False)
        self.cppLang.set_mode(False)
        self.pyLang.set_mode(False)
        self.otherLang.set_mode(False)

        h = Gtk.HBox()
        h.get_style_context().add_class('linked')
        h.pack_start(self.cLang, True, True, 0)
        h.pack_start(self.cppLang, True, True, 0)
        h.pack_start(self.pyLang, True, True, 0)
        h.pack_start(self.otherLang, True, True, 0)

        v.pack_start(h, False, False, 0)

        # r.add(v)
        # self.listBox.insert(r, -1)

        ## Boxes

        # self.hbox = Gtk.HBox()
        # self.vbox = Gtk.VBox()

        # self.vbox.pack_start(self.listBox, True, True, 0)

        # self.hbox.pack_start(self.listBox, True, True, 0)

        _hb = Gtk.HBox()
        _vb = Gtk.VBox()
        _vb.pack_start(v, True, False, 0)
        _hb.pack_start(_vb, True, False, 0)

        self.add(_hb)

    def createMake(self, *args):
        self.getLang()
        with open(os.path.join(self.path, '.pyide-project.json'), 'w+') as f:
            defaultSettings = {
                'path': self.path,
                'language': self.language,
                'name': self.path.split('/')[len(self.path.split('/')) - 1]
            }
            json.dump(defaultSettings, f, indent=4, sort_keys=True, separators=(',', ':'))

        cmake = '''all:
    gcc -o out *.c
    ./out
'''
        cppmake = '''all:
    g++ -o out *.cpp
    ./out
'''

        pymake = '''all:
    python3 main.py
'''

        if not self.language == 'other':
            with open(os.path.join(self.path, 'Makefile'), 'w+') as f:
                text = cmake if self.language == 'c' else cppmake if self.language == 'cpp' else pymake
                f.write(text)

        self.compiler.compile()
        self.destroy()
        
    def getLang(self, *args):
        self.language = 'c' if self.cLang.get_active() else 'cpp' if self.cppLang.get_active() else 'py' if self.pyLang.get_active() else 'other'

    def _quit(self, *args):
        self.parent.running = False
        self.stateEntry.set_text('Finished')
        self.compileBtn.set_image(Gtk.Image.new_from_icon_name('media-playback-start-symbolic', Gtk.IconSize.MENU))
        self.destroy()

class Compiler:

    def __init__(self, parent, path, entry, btn):

        self.path = os.path.abspath(path) ## Currently working path
        self.settings = None

        self.parent = parent

        self.compileBtn = btn
        self.stateEntry = entry

        self.compileBtn.set_image(Gtk.Image.new_from_icon_name('media-playback-stop-symbolic', Gtk.IconSize.MENU))
        self.stateEntry.set_text('Build in progress...')
        self.compileBtn.show_all()   

        self.p = None


    def compile(self, *args):

        self.parent.running = True

        if os.path.isfile(os.path.join(self.path, '.pyide-project.json')):

            with open(os.path.join(self.path, '.pyide-project.json'), 'r') as f:
                ## Do stuff
                print('Found file')
                project = json.load(f)
                if os.path.exists(os.path.join(self.path, 'Makefile')):
                    self.stateEntry.set_text('Running...')
                    Gtk.main_iteration()
                    self.parent.openTerminal()
                    # with open(os.path.join(self.path, 'Makefile'), 'r') as f:
                    #     command = f.readlines()
                    #     for l in command:
                    #         self.parent.terminal.feed_child(l, len(l))
                    self.parent.terminal.feed_child("make all\n", len("make all\n"))
                    self._quit()
                        
        else:

            self.p = ProjectSettingsWindow(self.parent, self.compileBtn, self.stateEntry, self.path, self)

            ## Create the file and then compile
            # pyideProject = json.JSONEncoder({
            #     ''
            # })

    def _quit(self, *args):
        if not self.p is None:
            self.p._quit()
        else:
            self.parent.running = False
            self.stateEntry.set_text('Finished')
            self.compileBtn.set_image(Gtk.Image.new_from_icon_name('media-playback-start-symbolic', Gtk.IconSize.MENU))