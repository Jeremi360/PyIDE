import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Gdk, GtkSource

class AutoBracket:
    def __init__(self, parent):

        self.parent = parent

        self.sview = parent.sview
        self.sbuff = parent.sbuff

        self.chars = {
            'parenleft': ')',
            'bracketleft': ']',
            'braceleft': '}',
            'quotedbl': '"',
            'apostrophe': '\'',
            'less': '>'
        }

    def do_activate(self, *args):
        print('Auto Bracket module activated')
        self.sview.connect('event-after', self.complete)

    def complete(self, view, event):
        self.hasSelection = self.sbuff.props.has_selection

        if self.hasSelection:
            bounds = self.sbuff.get_selection_bounds()
            self.start, self.end = bounds
            self.selectionText = self.sbuff.get_text(self.start, self.end, False)

        ignore = Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK

        if (event.type != Gdk.EventType.KEY_PRESS or event.state & ignore or Gdk.keyval_name(event.key.keyval) not in self.chars):
            self.hadSelection = self.hasSelection
            return

        insert = self.get_insert()
        closing = self.chars[Gdk.keyval_name(event.key.keyval)]

        if Gdk.keyval_name(event.key.keyval) == 'less' and not self.sbuff.get_language() is None and self.sbuff.get_language().get_name().lower() != 'html':
            return

        if not self.hadSelection and not self.hasSelection:
            self.sbuff.begin_user_action()
            self.sbuff.insert(insert, closing)
            self.sbuff.end_user_action()
            insert.backward_chars(1)
            self.sbuff.place_cursor(insert)

        else:
            self.sbuff.begin_user_action()
            self.selectionText += closing
            self.sbuff.insert(insert, self.selectionText)
            self.sbuff.end_user_action()
            insert.backward_chars(1)
            self.sbuff.place_cursor(insert)

    def get_insert(self, *args):
        mark = self.sbuff.get_insert()
        return self.sbuff.get_iter_at_mark(mark)