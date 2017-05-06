## When creating the sbuff please pass in a TextTagTable like this

self.stable = Gtk.TextTagTable()
self.sbuff = Gtk.TextBuffer(self.stable)

## Found tag for search and replace

tag = Gtk.TextTag('error_tag')
tag.set_property('background-rgba', Gdk.RGBA(red=0.99,green=0.99,blue=0.99,alpha=0.4))
self.stable.add(tag)

## Error tag for linter

tag = Gtk.TextTag('error_tag', underline=Pango.Underline.ERROR)
self.stable.add(tag)

## Search tool

self.searchBar = Gtk.Toolbar()


def search(self, *args):
