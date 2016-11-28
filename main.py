#!/usr/bin/env python3

# Had to install libgtksourceview-3.0-dev
# Will need pygit2 (python3-pygit2) for git integration

import gi, os, sys, subprocess, re, json, pygit2
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Gdk,GtkSource, Vte, GLib
from os import listdir
from os.path import isfile, join
from pygit2 import Repository

wW = __import__('welcomeWindow')

def isTextFile(fn):
    msg = subprocess.Popen(["file", fn], stdout=subprocess.PIPE).communicate()[0]
    return 'text' in str(msg) or 'source' in str(msg)

def isImageFile(fn):
    msg = subprocess.Popen(["file", fn], stdout=subprocess.PIPE).communicate()[0]
    return 'image' in str(msg)

class IDEWindow(Gtk.Window):
    """docstring for IDEWindow."""
    def __init__(self, openPath):
        super(IDEWindow, self).__init__()

        ## Win General

        self.set_title('IDE')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(1000, 500)
        #self.set_border_width(10)
        self.connect('destroy', Gtk.main_quit)

        ### Win Accels

        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('s'), Gdk.ModifierType.CONTROL_MASK, 0, self.saveFile)
        accel.connect(Gdk.keyval_from_name('b'), Gdk.ModifierType.CONTROL_MASK, 0, self.compile)
        #accel.connect(Gdk.keyval_from_name('p'), Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, 0, self.command) #future Ctrl + Shift + P command popup
        self.add_accel_group(accel)

        ## Editor General

        self.projectPath = None
        self.projectName = None
        self.curFileName = None
        self.curFileIndex = None
        self.curLanguage = None
        self.curSettings = None
        self.files = []
        self.tempFilesText = []
        self.langs = []
        self.compilerOptions = []

        ## Header Bar

        self.hb = Gtk.HeaderBar()

        # system-run = engine icon, media-playback-start = red play icon, gtk-media-play = white play
        self.compileBtn = Gtk.Button.new_from_icon_name('media-playback-start', Gtk.IconSize.MENU)
        self.compileBtn.set_tooltip_text('Compile + Run')
        self.compileBtn.connect('clicked', self.compile)
        self.compileBtn.set_sensitive(False)

        self.terminalBtn = Gtk.Button.new_from_icon_name('utilities-terminal', Gtk.IconSize.MENU)
        self.terminalBtn.set_tooltip_text('Toggle terminal')
        self.terminalBtn.connect('clicked', self.toggleTerminal)

        ### Creating popup menu

        self.menuBtn = Gtk.MenuButton()
        self.mBBtn = Gtk.Button.new_from_icon_name('format-justify-fill', Gtk.IconSize.MENU)
        self.menuBtn.add(self.mBBtn)

        self.menu = Gtk.Menu()

        self.menuItem1 = Gtk.MenuItem.new_with_label("New File")
        self.menuItem2 = Gtk.MenuItem.new_with_label("New Folder")
        self.menuItem3 = Gtk.SeparatorMenuItem()
        self.menuItem4 = Gtk.MenuItem.new_with_label("Preferences")

        self.menu.add(self.menuItem1)
        self.menu.add(self.menuItem2)
        self.menu.add(self.menuItem3)
        self.menu.add(self.menuItem4)

        self.menu.show_all()
        self.menuBtn.set_popup(self.menu)

        ###

        self.menuBtn.set_tooltip_text('Menu')
        #self.hb.pack_end(self.menuBtn)

        #self.folderBtn = Gtk.Button.new_from_icon_name('folder-new', Gtk.IconSize.MENU)
        #self.folderBtn.set_tooltip_text('Open Project Folder')
        #self.folderBtn.connect('clicked', self.openProject)
        #self.hb.pack_start(self.folderBtn)
        self.hb.pack_start(self.compileBtn)
        self.hb.pack_start(self.terminalBtn)
        self.hb.set_title('Py IDE')
        self.hb.set_show_close_button(True)

        self.searchEntry = Gtk.Entry()
        self.searchEntry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'system-search')
        #self.hb.pack_end(self.searchEntry)

        ## Views And Buffers

        self.sview = GtkSource.View()
        self.sbuff = GtkSource.Buffer()
        self.lmngr = GtkSource.LanguageManager()
        self.sviewScroll = Gtk.ScrolledWindow()

        self.sview.set_buffer(self.sbuff)
        self.sview.set_auto_indent(True)
        self.sview.set_indent_on_tab(True)
        self.sview.set_tab_width(8)
        self.sview.set_pixels_above_lines(5)

        ### Testing completion

        self.sview_completion = self.sview.get_completion()
        self.sview_provider = GtkSource.CompletionWords.new('Suggestion')
        self.sview_provider.register(self.sbuff)
        self.sview_completion.add_provider(self.sview_provider)

        ## TreeView

        self.treeView = None # Turn this into a Gtk.TreeView(self.fileStore) when fileStore has something
        self.fileList = []
        self.fileStore = None # Turn this into a Gtk.ListStore (lists that TreeView can display)

        hb = Gtk.HBox()
        self.sideNewFileBtn = Gtk.Button.new_from_icon_name('document-new', Gtk.IconSize.MENU)
        self.sideNewFolderBtn = Gtk.Button.new_from_icon_name('folder-new', Gtk.IconSize.MENU)
        hb.pack_start(self.sideNewFileBtn, False, False, 0)
        hb.pack_start(self.sideNewFolderBtn, False, False, 0)

        self.pane = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.pane.set_wide_handle(False)
        self.terminalPane = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        #self.terminalPane.set_wide_handle(True)

        self.terminal = Vte.Terminal()

        self.sideVBox = Gtk.VBox()
        self.sideVBox.pack_start(hb, False, False, 0)

        self.sideView = Gtk.ListBox()
        self.sideView.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sideView.set_activate_on_single_click(True)
        self.sideView.connect('row-selected', self.handleSideClick)
        self.sideScroller = Gtk.ScrolledWindow()
        self.sideScroller.add(self.sideView)
        self.sideScroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.sideVBox.pack_start(self.sideScroller, True, True, 0)

        self.sviewScroll.add(self.sview)
        self.pane.pack1(self.sideVBox, False, True)
        self.pane.add2(self.sviewScroll)

        self.terminalPane.pack1(self.pane, True, True)
        self.terminalPane.add2(self.terminal)

        self.add(self.terminalPane)
        self.set_titlebar(self.hb)

        self.loadSettings()

        self.applyCSS()

        self.show_all()

        self.openProject(openPath)

        Gtk.main()

    def loadSettings(self, *args):

        defaultSettings = {'highlight-matching-brackets': True,'show-line-numbers': True,'word-wrap': True, 'dark-mode': False}

        curSettings = None

        if os.path.exists('pyide-settings.json'):
            with open('pyide-settings.json', 'r') as f:
                curSettings = json.load(f)
        else:
            with open('pyide-settings.json', 'w+') as f:
                json.dump(defaultSettings, f, indent=4, sort_keys=True, separators=(',', ':'))
                curSettings = defaultSettings

        self.curSettings = curSettings

        self.highlightMatchingBrackets = curSettings['highlight-matching-brackets']
        self.showLineNumbers = curSettings['show-line-numbers']
        self.wordWrap = curSettings['word-wrap']
        self.darkMode = curSettings['dark-mode']

        self.applySettings()

    def applySettings(self, *args):
        self.sview.set_show_line_numbers(self.showLineNumbers)
        self.sbuff.set_highlight_matching_brackets(self.highlightMatchingBrackets)

        if self.wordWrap:
            self.sview.set_wrap_mode(Gtk.WrapMode.WORD)

        self.applyCSS()


    def applyCSS(self, *args):
        self.styleProvider = Gtk.CssProvider()

        def_css = """

            GtkWindow {
                background: white;
            }

            GtkWindow, GtkListBox, GtkListBoxRow, GtkTextView, GtkSourceView {
                background: #FFFFFF;
                color: #5C616C;
            }

            GtkSourceView {
                padding: 10px;
                margin: 10px;
            }

            GtkPaned {
                border-color: #DCDFE3;
                color: #5C616C;
            }

        """

        dark_css = """

            GtkWindow, GtkListBox, GtkListBoxRow, GtkTextView, GtkSourceView {
                background: #282C34;
                color: #ABB2BF;
            }

            GtkPaned {
                border-color: #181A1F;
                color: #181A1F;
            }

        """

        css = None

        if self.darkMode:
            css = dark_css
        else:
            css = def_css

        self.styleProvider.load_from_data(bytes(css.encode()))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def getCurrentText(self, *args):
        return self.sbuff.get_text(self.sbuff.get_start_iter(), self.sbuff.get_end_iter(), False)

    def saveOnChangeFile(self, *args):
        self.tempFilesText[self.curFileIndex] = self.getCurrentText()
        #print("Saved on change, {}".format(self.curFileIndex))

    def handleSideClick(self, *args):

        # This corrects the "AttributeError: 'NoneType' object has no attribute 'get_index'" error on close
        if self.sideView.get_selected_row() is None:
            return

        if isImageFile(self.projectPath + '/' + self.files[self.sideView.get_selected_row().get_index()]):
            os.system('xdg-open ' + self.projectPath + '/' + self.files[self.sideView.get_selected_row().get_index()])
            return

        if not isTextFile(self.projectPath + '/' + self.files[self.sideView.get_selected_row().get_index()]):
            print('Not text')
            return

        if type(self.curFileIndex) is int:
            self.saveOnChangeFile()

        row = self.sideView.get_selected_row()
        selected = row.get_index()
        #print(selected)
        self.curFileIndex = selected
        self.curFileName = self.files[selected]

        if type(self.tempFilesText[self.curFileIndex]) is not str:
            self.openFile(self.projectPath + '/' + self.files[selected])
        else:
            self.openFileFromTemp()

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
                if item.startswith('.') or item.startswith('__') or '~' in item:
                    continue
                self.files.append(item)
                if not os.path.isdir(item):
                    if isTextFile(str(item)) == False: # Checking if file is text file
                        continue
                    self.compilerOptions.append('')
                    #self.openFile(self.projectPath + '/' + self.files[i]) # Until I create a working TreeView
                i += 1

            self.langs = None
            self.langs = [None] * len(self.files)
            #print(len(self.langs))

            self.tempFilesText = None
            self.tempFilesText = [None] * len(self.files)
            #print(len(self.tempFilesText))

            self.buildTree(self)

            if len(self.compilerOptions) >= 1:
                self.compileBtn.set_sensitive(True)

            curShell = os.environ.get('SHELL')

            self.terminal.spawn_sync(
                    Vte.PtyFlags.DEFAULT, #default is fine
                    self.projectPath, #where to start the command?
                    [curShell], #where is the emulator?
                    [], #it's ok to leave this list empty
                    GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                    None, #at least None is required
                    None,
                    )
            self.terminal.hide()

            if os.path.isdir(self.projectPath + '/.git'):
                text = Repository(self.projectPath).head.shorthand
                repo = Gtk.HBox(spacing=6)
                img = Gtk.Image.new_from_file('resources/icons/git-branch.svg')
                repo.pack_start(img, False, False, 0)
                repo.pack_start(Gtk.Label(text), False, False, 0)
                repo.show_all()

                btn = Gtk.Button()
                btn.add(repo)
                btn.show_all()
                btn.set_tooltip_text("On branch " + text)

                self.hb.pack_end(btn)

    def openFileFromTemp(self, *args):
        text = self.tempFilesText[self.curFileIndex]
        self.sbuff.set_text(text)
        self.sbuff.set_language(self.langs[self.curFileIndex])
        self.hb.set_subtitle(self.projectPath + '/' + self.files[self.curFileIndex])

    def openFile(self, filePath,*args):
        with open(filePath) as f:
            self.sbuff.set_text(f.read())
            lang = self.lmngr.guess_language(filePath)
            self.langs[self.curFileIndex] = lang
            self.sbuff.set_language(lang)
            self.hb.set_subtitle(filePath)

    def saveFile(self, *args):
        if type(self.curFileIndex) is not int:
            print('no files open')
            return
        _f = self.projectPath + '/' + self.files[self.curFileIndex]
        with open(_f, 'w') as f:
            text = self.getCurrentText()
            f.write(text)
        print("Tried to save {}".format(_f))

        curSettings = None

        if os.path.exists('pyide-settings.json'):
            with open('pyide-settings.json', 'r') as f:
                curSettings = json.load(f)
                #print(self.curSettings == curSettings)
            if self.curSettings != curSettings:
                self.loadSettings()

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
                              Gtk.MessageType.INFO,
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

        if type(self.curFileIndex) is not int: # if no file is open
            print('No file selected')
            return

        if self.compilerOptions[self.curFileIndex] == None or self.compilerOptions[self.curFileIndex] == '':
            en = self.entryDialog('Compiling command', 'Compiler')
            if en != None:
                # print ("compile: {}".format(en))
                bashCommand = en.replace('_localfile_', self.projectPath + '/' + self.files[self.curFileIndex])
                self.compilerOptions[self.curFileIndex] = bashCommand
                import subprocess
                process = subprocess.Popen(bashCommand, shell=True)
                output, error = process.communicate()
                print(output)
                print(error)
        else:
            import subprocess
            process = subprocess.Popen(self.compilerOptions[self.curFileIndex], shell=True)
            output, error = process.communicate()
            print(output)
            print(error)

    def toggleTerminal(self, *args):
        if self.terminal.props.visible:
            self.terminal.hide()
        else:
            self.terminal.show()

if len(sys.argv) == 1:
    w = wW.WelcomeWindow()
elif len(sys.argv) == 2:
    a = IDEWindow(sys.argv[1])
