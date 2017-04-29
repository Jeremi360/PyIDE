import os, gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')

from gi.repository import Gtk, GtkSource

class Linter:

    def __init__(self, parent):
        self.parent = parent
        self.language = 'Plain'
        self.curLinter = None
        self.enabled = True

    def setLanguage(self, *args):
        self.language = self.parent.currentLanguage.get_name() if not self.parent.currentLanguage is None else 'Plain'
        self.currentFile = self.parent.hb.get_subtitle()

        if self.language.lower() in ['c', 'cpp']:

            self.chooseLinter()
        else:
            print('not supported')
            self.do_deactivate()
            self.disableLinter()

    def chooseLinter(self, *args):

        if self.language.lower() in ['c','cpp','c/objc header']:
            from modules.linters.linterClang import LinterClang
            self.curLinter = LinterClang(self.parent, self.currentFile)
            self.curLinter.do_activate()
            self.do_activate()

    def disableLinter(self, *args):
        if not self.curLinter is None:
            del self.curLinter
            self.curLinter = None

        self.enabled = False

    def do_activate(self, *args):

        lintersPath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linters'))
        linters = [name for name in os.listdir(lintersPath) if os.path.isfile(os.path.join(lintersPath, name))]

        print('Linter Enabled')
        # print('Found {} linters'.format(len(linters)))

        self.enabled = True

    def do_deactivate(self, *args):
        print('Linter Disabled')
        if not self.curLinter is None:
            self.curLinter.do_deactivate()
            self.curLinter

        self.enabled = False

    def on_document_load(self, *args):
        self.do_activate()
        self.setLanguage()
