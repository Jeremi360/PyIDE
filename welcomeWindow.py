#!/usr/bin/env python3

# Had to install libgtksourceview-3.0-dev

import gi, os, sys
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

        builder = Gtk.Builder()

        builder.add_from_file("WelcomeWindow.glade")

        self = builder.get_object("wWindow")

        self.banner = builder.get_object("textview1")
        self.banner.modify_font(Pango.FontDescription.from_string("Ubuntu 26"))
        self.banner.set_pixels_above_lines(20)

        self.buffer = Gtk.TextBuffer()
        self.buffer.set_text("Welcome to Py IDE")
        self.banner.set_buffer(self.buffer)
        self.banner.set_sensitive(False)
        self.banner.set_editable(False)

        self.banner.set_name("banner")

        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.set_title("Py IDE")

        self.set_titlebar(self.hb)
        self.set_default_size(800, 400)

        self.styleProvider = Gtk.CssProvider()

        css = """

            GtkWindow {
                background: white;
            }

            #banner {
                background: transparent;
            }
        """

        self.styleProvider.load_from_data(bytes(css.encode()))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.connect('destroy', Gtk.main_quit)

        self.show_all()

        Gtk.main()
