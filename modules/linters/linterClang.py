import os, gi, sys, subprocess, re, shlex
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource, Pango
from distutils import dir_util
from threading import Timer

class LinterClang:

    def __init__(self, parent, linter):
        self.parent = parent
        self.curFile = None

        self.linterModule = linter

        # Activate Linting on file saved
        self.activateOnSave = False

        # Live linting
        self.live = True

        # Live linting delay
        self.liveDelay = 1.0

        self.task = None

        self.errors = 0
        self.fileChanged = True

        self.enabled = False

    def do_live_linting(self, *args):

        #print('Lint called and: {}, has file? {}'.format(self.fileChanged, self.curFile is not None))

        if self.fileChanged and self.curFile is not None:

            self.fileChanged = False

            # Stuff

            # command = "clang-check /tmp/pyidetmp/*.* --"
            # process = subprocess.Popen(command.split(), cwd=self.parent.projectPath, stdout=subprocess.PIPE)
            #
            # output, error = process.communicate()


            with open('/tmp/pyidetmp/' + self.curFile.replace(self.parent.projectPath, ''), 'w+') as f:
                f.write(self.parent.getCurrentText())

            #output = os.system("clang-check `find /tmp/pyidetmp | egrep '\.(c|h|cpp)$'` --")

            files = subprocess.check_output("find /tmp/pyidetmp | egrep '\.(c|h|cpp)$'", shell=True)


            files = list(filter(None, files.decode('utf-8').split('\n'))) # Get the files filtering possible empty results

            filesStr = ' '.join(files) # files array to string separated by spaces

            self.parent.sbuff.remove_tag_by_name('error-tag', self.parent.sbuff.get_start_iter(), self.parent.sbuff.get_end_iter())

            try:
                res = subprocess.check_output("clang-check " + filesStr + ' --', stderr=subprocess.STDOUT, shell=True)

                self.errors = 0
                self.parent.stateEntry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'emblem-ok-symbolic')
                self.linterModule.set_errors(self.errors)

            except subprocess.CalledProcessError as e:
                output = e.output.decode('utf-8')

                output = output.replace('/tmp/pyidetmp', self.parent.projectPath)

                lin = [l for l in output.split('\n') if re.match('[0-9]+ (error|errors) generated.', l)]

                #print('Output: {},,,, Lin: {}'.format(output, lin))

                errors = None

                if len(lin) > 0:
                    errors = lin[0].split(' ')[0]
                else:
                    errors = 0

                print(self.parent.projectPath + '/[a-zA-Z0-9.]')

                errorPos = [[l.split(':')[1], l.split(':')[2]] for l in output.split('\n') if re.match(self.parent.projectPath + '/[a-zA-Z0-9.]', l)]

                errorMark = GtkSource.Mark.new('error', 'error-category')
                errorMarkAttr = GtkSource.MarkAttributes()
                errorMarkAttr.set_icon_name('dialog-warning-symbolic')

                for arr in errorPos:
                    sit = self.parent.sbuff.get_iter_at_line_offset(int(arr[0]) - 1, 0)
                    eit = self.parent.sbuff.get_iter_at_line_offset(int(arr[0]) - 1, int(arr[1]))
                    self.parent.sbuff.apply_tag_by_name('error-tag', sit, eit)


                print(errorPos)

                self.errors = errors

                self.parent.stateEntry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'dialog-error-symbolic')
                self.parent.stateEntry.set_icon_activatable(Gtk.EntryIconPosition.SECONDARY, True)
                self.parent.stateEntry.connect('icon-press', self.linterModule.show_linter_pop)

                self.linterModule.set_errors(errors)

                print('Errors: {}'.format(errors))

            self.parent.stateEntry.set_text('{} error found.'.format(self.errors) if int(self.errors) == 1 else 'No errors found.' if self.errors == 0 else '{} errors found.'.format(self.errors))

            if not self.task is None:
                self.task.cancel()

            self.task = Timer(self.liveDelay, self.do_live_linting)
            self.task.start()



    def set_file_changed(self, *args):
        #print('File changed')
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
