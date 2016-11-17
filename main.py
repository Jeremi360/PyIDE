#!/usr/bin/env python3

# Had to install libgtksourceview-3.0-dev

import gi, os, sys
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Gdk,GtkSource
from os import listdir
from os.path import isfile, join

wW = __import__('welcomeWindow')

class IDEWindow(Gtk.Window):
    """docstring for IDEWindow."""
    def __init__(self, openPath):
        super(IDEWindow, self).__init__()

        ## Win General

        self.set_title('IDE')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 400)
        self.connect('destroy', Gtk.main_quit)

        ## Editor General

        self.projectPath = None
        self.projectName = None
        self.curFileName = None
        self.curLanguage = None
        self.files = []
        self.compilerOptions = []

        ## Header Bar

        self.hb = Gtk.HeaderBar()

        # system-run = engine icon, media-playback-start = red play icon, gtk-media-play = white play
        self.compileBtn = Gtk.Button.new_from_icon_name('media-playback-start', Gtk.IconSize.MENU)
        self.compileBtn.set_tooltip_text('Compile + Run')
        self.compileBtn.connect('clicked', self.compile)
        self.compileBtn.set_sensitive(False)
        #self.folderBtn = Gtk.Button.new_from_icon_name('folder-new', Gtk.IconSize.MENU)
        #self.folderBtn.set_tooltip_text('Open Project Folder')
        #self.folderBtn.connect('clicked', self.openProject)
        #self.hb.pack_start(self.folderBtn)
        self.hb.pack_start(self.compileBtn)
        self.hb.set_title('Py IDE')
        self.hb.set_show_close_button(True)

        self.searchEntry = Gtk.Entry()
        self.searchEntry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'system-search')
        self.hb.pack_end(self.searchEntry)

        ## Views And Buffers

        self.sview = GtkSource.View()
        self.sbuff = GtkSource.Buffer()
        self.lmngr = GtkSource.LanguageManager()
        self.sviewScroll = Gtk.ScrolledWindow()

        self.sview.set_buffer(self.sbuff)
        self.sview.set_auto_indent(True)
        self.sview.set_indent_on_tab(True)
        self.sview.set_tab_width(8)
        self.sview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.sview.set_pixels_above_lines(5)
        self.sview.set_show_line_numbers(True)

        ## TreeView

        self.treeView = None # Turn this into a Gtk.TreeView(self.fileStore) when fileStore has something
        self.fileList = []
        self.fileStore = None # Turn this into a Gtk.ListStore (lists that TreeView can display)

        self.pane = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        self.sideView = Gtk.ListBox()
        self.sideScroller = Gtk.ScrolledWindow()
        self.sideScroller.add(self.sideView)

        self.sviewScroll.add(self.sview)
        self.pane.add1(self.sideScroller)
        self.pane.add2(self.sviewScroll)
        self.add(self.pane)
        self.set_titlebar(self.hb)

        self.show_all()

        self.openProject(openPath)

        Gtk.main()

    def openProject(self, __file=None, *args):

        if __file is None: # in case no path is set (use chooser dialog)
            dialog = Gtk.FileChooserDialog('Select a project folder', self, Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                self.projectPath = dialog.get_filename()
                self.hb.set_subtitle(self.projectPath)
                files = os.listdir(self.projectPath)
                self.files = None
                self.files = []

                self.compilerOptions = None
                self.compilerOptions = []


                for item in files:
                    self.files.append(item)
                    if not os.path.isdir(item):
                        self.compilerOptions.append('')
                        self.openFile(self.projectPath + '/' + self.files[0]) # Until I create a working TreeView
                self.buildTree(self)

                if len(self.compilerOptions) >= 1:
                    self.compileBtn.set_sensitive(True)

            dialog.destroy()
        else: # in case a path is set
            if __file == '.':
                self.projectPath = os.path.dirname(os.path.abspath(__file__))
            else:
                if not os.path.isdir(__file):
                    print("{} is not a directory!".format(__file))
                    sys.exit()
                else:
                    self.projectPath = __file
            self.hb.set_subtitle(self.projectPath)
            files = os.listdir(self.projectPath)
            self.files = None
            self.files = []

            self.compilerOptions = None
            self.compilerOptions = []

            i = 0
            for item in files:
                self.files.append(item)
                if not os.path.isdir(item):
                    self.compilerOptions.append('')
                    self.openFile(self.projectPath + '/' + self.files[i]) # Until I create a working TreeView
                i += 1
            self.buildTree(self)

            if len(self.compilerOptions) >= 1:
                self.compileBtn.set_sensitive(True)

    def openFile(self, filePath,*args):
        with open(filePath) as f:
            self.sbuff.set_text(f.read())
            lang = self.lmngr.guess_language(filePath)
            self.sbuff.set_language(lang)
            self.hb.set_subtitle(filePath)

    def saveFile(self, *args):
        print('Finish this function')

    def buildTree(self, *args):

        for item in self.files:
            a = Gtk.Label(item)
            if os.path.isdir(item):
                i = Gtk.Image.new_from_icon_name('folder', Gtk.IconSize.MENU) # change this for recursive function
            else:
                i = Gtk.Image.new_from_icon_name('text-x-script', Gtk.IconSize.MENU)
            hb = Gtk.HBox(spacing=6)
            hb.pack_start(i, False, False, 0)
            hb.pack_start(a, False, False, 0)

            row = Gtk.ListBoxRow()
            row.add(hb)
            self.sideView.add(row)

        self.sideView.show_all()

    def entryDialog(self, message, title=''):
        # Returns user input as a string or None
        # If user does not input text it returns None, NOT AN EMPTY STRING.
        dialogWindow = Gtk.MessageDialog(self,
                              Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                              Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.OK_CANCEL,
                              message)

        dialogWindow.set_title(title)

        dialogBox = dialogWindow.get_content_area()
        userEntry = Gtk.Entry()
        dialogBox.pack_end(userEntry, False, False, 0)

        dialogWindow.show_all()
        response = dialogWindow.run()
        text = userEntry.get_text()
        dialogWindow.destroy()
        if (response == Gtk.ResponseType.OK) and (text != ''):
            return text
        else:
            return None

    def compile(self, *args):

        # Replace all 0 by curFile index

        if self.compilerOptions[0] == None or self.compilerOptions[0] == '':
            en = self.entryDialog('Compiling command', 'Compiler')
            if en != None:
                # print ("compile: {}".format(en))
                bashCommand = en.replace('_localfile_', self.projectPath + '/' + self.files[0])
                self.compilerOptions[0] = bashCommand
                import subprocess
                process = subprocess.Popen(bashCommand, shell=True)
                output, error = process.communicate()
                print(output)
                print(error)
        else:
            import subprocess
            process = subprocess.Popen(self.compilerOptions[0], shell=True)
            output, error = process.communicate()
            print(output)
            print(error)

if len(sys.argv) == 1:
    w = wW.WelcomeWindow()
elif len(sys.argv) == 2:
    a = IDEWindow(sys.argv[1])
