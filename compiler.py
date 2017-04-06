import os, sys, subprocess, re, json, psutil, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ProjectSettingsWindow(Gtk.Window):
    def __init__(self, parent):

        super(ProjectSettingsWindow, self).__init__()

        self.parent = parent

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

        self.hb.pack_start(self.cancelBtn)
        self.hb.pack_end(self.continueBtn)
        self.set_titlebar(self.hb)

        self.set_transient_for(self.parent)

        ## ListBox

        self.listBox = Gtk.ListBox()
        self.listBox.set_selection_mode(Gtk.SelectionMode.NONE)

        v = Gtk.VBox()
        v.pack_start(Gtk.Label('Language'), True, True, 0)
        r1 = Gtk.RadioButton.new_with_label(None, 'C')
        r2 = Gtk.RadioButton.new_with_label_from_widget(r1, 'C++')
        r3 = Gtk.RadioButton.new_with_label_from_widget(r2, 'Python')
        r4 = Gtk.RadioButton.new_with_label_from_widget(r3, 'Other')
        r1.set_mode(False)
        r2.set_mode(False)
        r3.set_mode(False)
        r4.set_mode(False)

        h = Gtk.HBox()
        h.get_style_context().add_class('linked')
        h.pack_start(r1, True, True, 0)
        h.pack_start(r2, True, True, 0)
        h.pack_start(r3, True, True, 0)
        h.pack_start(r4, True, True, 0)

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

    def _quit(self, *args):
        self.destroy()

class Compiler:

    def __init__(self, parent, path):

        self.path = os.path.abspath(path) ## Currently working path
        self.settings = None

        self.parent = parent


    def compile(self, *args):

        if os.path.isfile(os.path.join(self.path, '.pyide-project.json')):

            with open(os.path.join(self.path, '.pyide-project.json'), 'r') as f:
                ## Do stuff
                print('')

        else:

            p = ProjectSettingsWindow(self.parent)

            ## Create the file and then compile
            # pyideProject = json.JSONEncoder({
            #     ''
            # })