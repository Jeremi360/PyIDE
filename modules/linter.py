import os, gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')

from gi.repository import Gtk, GtkSource, Pango
from modules.linters.linterClang import LinterClang

class Linter:

    def __init__(self, parent):
        self.parent = parent
        self.language = 'Plain'
        self.curLinter = None

        self.lintersObj = {
            'c': LinterClang(self.parent, self)
        }

        self.linterPopover = Gtk.Popover()

        self.errorsLbl = Gtk.Label('Errors: 0')
        self.statusLbl = Gtk.Label('Status: OK')
        self.linterPopoverBox = Gtk.VBox()
        self.linterPopoverBox.set_border_width(10)

        self.linterPopoverBox.pack_start(self.errorsLbl, False, False, 0)
        self.linterPopoverBox.pack_start(self.statusLbl, False, False, 0)

        self.linterPopover.add(self.linterPopoverBox)

        ##

    def set_errors(self, errors):
        self.errorsLbl.set_text('Errors: {}'.format(errors))

    def set_status(self, status):
        self.statusLbl.set_text('Errors: {}'.format(status))

    def show_linter_pop(self, *args):
        self.linterPopover.show_all()

    def setLanguage(self, *args):
        self.language = self.parent.currentLanguage.get_name() if not self.parent.currentLanguage is None else 'Plain'
        self.currentFile = self.parent.hb.get_subtitle()

        if self.language.lower() in ['c', 'cpp', 'c++']:

            self.chooseLinter()
        else:
            print('not supported')
            self.do_deactivate()

    def chooseLinter(self, *args):

        if self.language.lower() in ['c','cpp', 'c++','c/objc header']:
            
            self.curLinter = self.lintersObj['c']
            self.curLinter.set_file(self.currentFile)
            self.curLinter.do_activate()    

    def do_activate(self, *args):

        #lintersPath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linters'))
        #linters = [name for name in os.listdir(lintersPath) if os.path.isfile(os.path.join(lintersPath, name))]
        # print('Found {} linters'.format(len(linters)))

        print('Linter Module active')

    def do_deactivate(self, *args):
        if not self.curLinter is None:
            print('Linter Module disabled')
            self.curLinter.do_deactivate()

    def on_document_load(self, *args):
        self.do_activate()
        self.setLanguage()
