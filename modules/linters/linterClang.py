import os, gi, sys, subprocess
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource
from distutils import dir_util
from threading import Timer

class LinterClang:

    def __init__(self, parent):
        self.parent = parent
        self.curFile = None

        # Activate Linting on file saved
        self.activateOnSave = False

        # Live linting
        self.live = True

        # Live linting delay
        self.liveDelay = 2.0

        self.task = None

        self.errors = 0
        self.fileChanged = True

        self.enabled = False

    def do_live_linting(self, *args):

        print('Lint called and: {}, has file? {}'.format(self.fileChanged, self.curFile is not None))

        if self.fileChanged and self.curFile is not None:

            self.fileChanged = False

            # Stuff

            # command = "clang-check /tmp/pyidetmp/*.* --"
            # process = subprocess.Popen(command.split(), cwd=self.parent.projectPath, stdout=subprocess.PIPE)
            #
            # output, error = process.communicate()


            with open('/tmp/pyidetmp/' + self.curFile.replace(self.parent.projectPath, ''), 'w+') as f:
                f.write(self.parent.getCurrentText())

            output = os.system("clang-check `find /tmp/pyidetmp | egrep '\.(c|h|cpp)$'` --")

            if not output == 0 and not output == '0':
                print(output)
                self.parent.stateEntry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'emblem-important-symbolic')
            else:
                self.errors = 0
                self.parent.stateEntry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'emblem-ok-symbolic')

            if not self.task is None:
                self.task.cancel()

            self.task = Timer(self.liveDelay, self.do_live_linting)
            self.task.start()



    def set_file_changed(self, *args):
        print('File changed')
        self.fileChanged = True
        if not self.task is None:
            self.task.cancel()
        self.task = Timer(self.liveDelay, self.do_live_linting)
        self.task.start()

    def set_file(self, _file=None):
        self.curFile = _file

    def do_activate(self, *args):

        print('LinterClang activated')
        self.enabled = True
        dir_util.copy_tree(self.parent.projectPath, '/tmp/pyidetmp')

        if self.live:
            self.connection = self.parent.sbuff.connect('changed', self.set_file_changed)
            self.do_live_linting()

    def do_deactivate(self, *args):
        if not self.task is None:
            self.task.cancel()
        if not self.connection is None:
            self.parent.sbuff.disconnect(self.connection)
            self.connection = None

        print('LinterClang deactivated')
        self.enabled = False

    def __del__(self, *args):
        self.do_deactivate()
