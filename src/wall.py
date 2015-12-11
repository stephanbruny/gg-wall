#!/usr/bin/python
import gtk
import os
import cairo
import Image
import StringIO
import glib

class gg_wall(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		# gather some data from root window
		root = gtk.gdk.get_default_root_window()
		width, height = root.get_size()
		
		self.set_default_size(width, height)

		# always below all other windows
		self.set_keep_below(True)

		self.set_decorated(False)

		self.move(0, 0)
		self.set_resizable(False)
		# self.maximize()
		self.set_has_frame(False)
		self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DESKTOP)

		# set up drawing area for wallpapers
		self.drawing_area = gtk.DrawingArea()
		self.drawing_area.set_size_request(width, height)
		self.drawing_area.connect("expose-event", self.on_expose)
		self.add(self.drawing_area)

		self.wallpaper = gtk.Image()
		self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)

	def set_wallpaper(self, path):
		img = Image.open(path)
		buf = StringIO.StringIO()
		img.save(buf, format="PNG")
		buf.seek(0)
		self.surface = cairo.ImageSurface.create_from_png(buf)

	def on_expose(self, widget, ev):
		cr = widget.window.cairo_create()
		cr.set_source_surface(self.surface, 0, 0)
		cr.paint()
		# cr.restore()


wallpaper_dir = "/home/odroid/Pictures/Wallpapers"

files = [f for f in os.listdir(wallpaper_dir) if os.path.isfile(os.path.join(wallpaper_dir, f))]

wallpaper_path = os.path.join(wallpaper_dir, files[1])

win = gg_wall()
win.set_wallpaper(wallpaper_path)
win.show_all()

gtk.main()
