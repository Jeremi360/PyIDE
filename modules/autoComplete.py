import os
import tempfile
import subprocess

from jedi.api import Script
from gi.repository import GObject, Gtk, GtkSource

#FIXME: find real icon names
icon_names = {'import': 'object-straighten-symbolic',
              'module': 'object-straighten-symbolic',
              'class': 'object-straighten-symbolic',
              'function': 'func',
              'statement': '',
              'param': ''}

class Jedi:
    def get_script(document):
        doc_text = document.get_text(document.get_start_iter(), document.get_end_iter(), False)
        iter_cursor = document.get_iter_at_mark(document.get_insert())
        linenum = iter_cursor.get_line() + 1
        charnum = iter_cursor.get_line_index()

        return Script(doc_text, linenum, charnum, 'py')


class GediPlugin(GObject.Object):
    __gtype_name__ = "GediPlugin"
    py_extension = ".py"
    view = None

    def __init__(self, parent):
        GObject.Object.__init__(self)
        self.completion_provider = None
        self.view = parent.sview
        self.parent = parent

    def do_activate(self):
        print("Gedi activated.")
        # document = self.view.get_buffer()
        # self.on_document_load(document)

        self.completion_provider = GediCompletionProvider()
        self.view.get_completion().add_provider(self.completion_provider)

    def do_deactivate(self):
        print("Gedi module deactivated.")

    def on_document_load(self, *args):

        lang = self.parent.sbuff.get_language().get_name() if not self.parent.sbuff.get_language() is None else "Plain"

        if lang.lower() == 'python':
            if self.completion_provider is None:
                self.completion_provider = GediCompletionProvider()
                self.view.get_completion().add_provider(self.completion_provider)
                self.do_activate()
        else:
            if self.completion_provider is not None:
                self.view.get_completion().remove_provider(self.completion_provider)
                self.completion_provider = None
                self.do_deactivate()


class GediCompletionProvider(GObject.Object, GtkSource.CompletionProvider):
    __gtype_name__ = 'GediProvider'

    def __init__(self):
        GObject.Object.__init__(self)

    def do_get_name(self):
        return "PyIDE Code Completion"

    def do_match(self, context):
        #FIXME: check for strings and comments
        _, iter = context.get_iter()
        iter.backward_char()
        ch = iter.get_char()
        if not (ch in ('_', '.') or ch.isalnum()):
            return False

        return True

    def do_get_priority(self):
        return 1

    def do_get_activation(self):
        return GtkSource.CompletionActivation.INTERACTIVE

    def do_populate(self, context):
        #TODO: do async maybe?
        _, it = context.get_iter()
        document = it.get_buffer()
        proposals = []
        
        for completion in Jedi.get_script(document).completions():
            complete = completion.name
            proposals.append(GtkSource.CompletionItem.new(completion.name,
                                                            completion.name,
                                                            self.get_icon_for_type(completion.type),
                                                            completion.docstring()))


        context.add_proposals(self, proposals, True)

    def get_icon_for_type(self, _type):
        theme = Gtk.IconTheme.get_default()
        try:
            if 'symbolic' in icon_names[_type.lower()]:
                print('Symbolic')
                return theme.load_icon(icon_names[_type.lower()], 16, 0)
            else:
                print('Not symbolic')
                path = os.path.abspath(__file__).replace('modules/autoComplete.py')
                path = os.path.join(path, 'res/icons/' + icon_names[_type.lower()] + '.svg')
                print(path)
                a = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 16, 16)
                return a
        except:
            try:
                return theme.load_icon(Gtk.STOCK_ADD, 16, 0)
            except:
                return None


GObject.type_register(GediCompletionProvider)