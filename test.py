import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Window(Gtk.Window):
    def __init__(self, *args):
        super(Window, self).__init__()

        self.set_default_size(800, 300)
        self.hb = Gtk.HeaderBar()
        self.hb.set_title('Test Window')
        self.hb.set_show_close_button(True)

        i = Gtk.Image.new_from_icon_name('gnome-mime-text-x-python', Gtk.IconSize.MENU)
        b = Gtk.Image.new_from_pixbuf(i.get_pixbuf())
        self.add(b)

        self.set_titlebar(self.hb)

        self.connect('destroy', Gtk.main_quit)

        self.show_all()

        Gtk.main()

a = Window()

#######

#######

