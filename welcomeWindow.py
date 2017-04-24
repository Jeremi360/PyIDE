# Had to install libgtksourceview-3.0-dev

import gi, os, sys, subprocess, json
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Gdk, GtkSource, Pango
from os import listdir
from os.path import isfile, join

class WelcomeWindow(Gtk.Window):
    """docstring for WelcomeWindow."""

    def __init__(self):
        super(WelcomeWindow, self).__init__()

        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.set_title("Py IDE")
        self.set_titlebar(self.hb)

        self.currentPage = None
        self.hbButtons = []

        self.language = ''

        self.showHome()

        ##################################################################

        
        self.set_size_request(800, 400)
        self.set_resizable(False)

        self.loadSettings()

        self.connect('destroy', Gtk.main_quit)

        self.show_all()

        Gtk.main()

    def showHome(self, *args):
        v = Gtk.VBox()
        self.banner = Gtk.Label('Welcome to PyIDE')
        self.banner.modify_font(Pango.FontDescription.from_string("Ubuntu 26"))

        v.pack_start(self.banner, False, False, 0)

        ##################################################################

        h = Gtk.HBox()
        h.set_margin_top(20)

        self.openProjectBtn = Gtk.Button('Open Project')
        self.openProjectBtn.connect('clicked', self.openProject)
        # self.openProjectBtn.set_margin_right(10)
        self.newProjectBtn = Gtk.Button('New Project')
        self.newProjectBtn.connect('clicked', self.showProjectCreation)        
        # self.newProjectBtn.set_margin_left(10)

        h.pack_start(self.openProjectBtn, True, True, 0)
        h.pack_start(self.newProjectBtn, True, True, 0)

        v.pack_start(h, False, False, 0)

        ##################################################################

        _hb = Gtk.HBox()
        _vb = Gtk.VBox()
        _vb.pack_start(v, True, False, 0)
        _hb.pack_start(_vb, True, False, 0)

        ## REMOVE OLD STUFF

        if not self.currentPage is None: self.remove(self.currentPage)

        self.currentPage = _hb
        self.add(self.currentPage)

        for child in self.hbButtons:
            self.hb.remove(child)
        
        self.hbButtons = []

        ##

        self.show_all()

    def showProjectCreation(self, *args):

        v = Gtk.VBox(spacing=6)

        v.pack_start(Gtk.Label('Language'), True, True, 0)
        ##

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

        ##################################################################

        _hb = Gtk.HBox()
        _vb = Gtk.VBox()
        _vb.pack_start(v, True, False, 0)
        _hb.pack_start(_vb, True, False, 0)

        ## REMOVE OLD STUFF

        if not self.currentPage is None: self.remove(self.currentPage)

        self.currentPage = _hb
        self.add(self.currentPage)

        for child in self.hbButtons:
            self.hb.remove(child)
        
        self.hbButtons = []

        ##

        a = Gtk.Button()
        a.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        a.connect('clicked', self.showHome)
        self.hbButtons.append(a)
        self.hb.pack_start(a)

        b = Gtk.Button('Create')
        self.createButton = b
        self.createButton.connect('clicked', self.createProject)
        self.hbButtons.append(self.createButton)
        self.hb.pack_end(self.createButton)

        self.show_all()

    def createMainFile(self, *args):
        text = ''
        hasMakefile = False
        makefile = ''
        if self.language == 'other':
            return
        elif self.language == 'c':
            text = '''#include <stdio.h>

/* Created with PyIDE */

int main(int argv, const char **argc)
{
        printf("Hello World\\n");
        return 0;
}
'''
            hasMakefile = True
            makefile = '''all:
        gcc -o out *.c
        ./out
'''
        elif self.language == 'cpp':
            text = '''#include <iostream>

/* Created with PyIDE */

using namespace std;

int main(int argc, char const *argv[])
{
        cout << "Hello World" << endl;
        return 0;
}
'''

            hasMakefile = True
            makefile = '''all:
        g++ -o out *.cpp
        ./out
'''
        elif self.language == 'py':
            text = '''

""" Created with PyIDE """

print("Hello World\\n")
'''
            hasMakefile = True
            makefile = '''all:
        python3 main.py
'''
        else:
            return

        with open(os.path.join(self.projectPath, 'main.' + self.language), 'w+') as f:
            f.write(text)

        if hasMakefile:
            with open(os.path.join(self.projectPath, 'Makefile'), 'w+') as f:
                f.write(makefile)

    def getLang(self, *args):
        self.language = 'c' if self.cLang.get_active() else 'cpp' if self.cppLang.get_active() else 'py' if self.pyLang.get_active() else 'other'
        self.createButton.get_style_context().add_class('suggested-action')

    def openProject(self, *args):
        dialog = Gtk.FileChooserDialog('Select a project folder', self, Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        

        if response == Gtk.ResponseType.OK:
            projectPath = dialog.get_filename()

            os.execl(sys.executable, *([sys.executable]+sys.argv+[projectPath]))

        dialog.destroy()

    def createProject(self, *args):
        self.getLang()
        dialog = Gtk.FileChooserDialog("Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
        response = dialog.run()
        

        if response == Gtk.ResponseType.OK:
            
            projectPath = dialog.get_filename()
            self.projectPath = projectPath
            with open(os.path.join(projectPath, '.pyide-project.json'), 'w+') as f:
                defaultSettings = {
                    'path': projectPath,
                    'name': projectPath.split('/')[len(projectPath.split('/')) - 1],
                    'language': self.language
                }
                json.dump(defaultSettings, f, indent=4, sort_keys=True, separators=(',', ':'))

            self.createMainFile()

            os.execl(sys.executable, *([sys.executable]+sys.argv+[projectPath]))

        dialog.destroy()

    def loadSettings(self, *args):

        defaultSettings = {'highlight-matching-brackets': True,'show-line-numbers': True,'word-wrap': True, 'dark-mode': False}

        curSettings = None

        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyide-settings.json')):
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyide-settings.json'), 'r') as f:
                curSettings = json.load(f)
        else:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyide-settings.json'), 'w+') as f:
                json.dump(defaultSettings, f, indent=4, sort_keys=True, separators=(',', ':'))
                curSettings = defaultSettings

        self.curSettings = curSettings

        self.darkMode = curSettings['dark-mode']

        self.applySettings()

    def applySettings(self, *args):

        Gtk.Settings.get_default().set_property('gtk-application-prefer-dark-theme', self.darkMode)
