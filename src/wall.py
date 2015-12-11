#!/usr/bin/env python
import gtk
import os
import cairo
import Image
import StringIO
import glib
import sys

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
		self.surface2 = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
		self.wp_files = []
		self.wp_dir = ''
		self.wp_index = 0
		self.time_out = None
		self.fade_time_out = None
		self.fade_interval = 15
		self.fade_delay = 10000
		self.alpha = 0
		self.alpha_delta = 0.01

	def set_directory(self, path):
		self.wp_dir = path
		self.wp_files = [f for f in os.listdir(self.wp_dir) if os.path.isfile(os.path.join(self.wp_dir, f))]
		self.set_wallpaper(self.wp_files[self.wp_index])

	def get_surface(self, path):
		img = Image.open(os.path.join(self.wp_dir, path))
		buf = StringIO.StringIO()
		img.save(buf, format="PNG")
		buf.seek(0)
		return cairo.ImageSurface.create_from_png(buf)

	def set_wallpaper(self, path):
		self.surface = self.get_surface(path)

	def on_expose(self, widget, ev):
		cr = widget.window.cairo_create()
		cr.set_source_surface(self.surface, 0, 0)
		cr.paint()
		
		if self.alpha > 0:
			cr.set_source_surface(self.surface2, 0, 0)
			cr.paint_with_alpha(self.alpha)
	

	def get_next_index(self):
		if self.wp_index < (len(self.wp_files) - 1):
			self.wp_index = self.wp_index + 1
		else:
			self.wp_index = 0
		return self.wp_index

	def shuffle(self):
		self.set_wallpaper(self.wp_files[self.get_next_index()])
		self.queue_draw()
		return True

	def set_shuffle(self, msec):
		self.set_wallpaper(self.wp_files[self.wp_index])
		self.queue_draw()
		self.time_out = glib.timeout_add(msec, self.fade_next, self.fade_interval, self.get_next_index())

	def inc_alpha(self):
		self.alpha = self.alpha + self.alpha_delta
		if self.alpha >= 1.0:
			self.surface = self.surface2
			self.set_shuffle(self.fade_delay)
			self.alpha = 0.0
			return False
		self.queue_draw()
		return True

	def fade_next(self, msec, index):
		self.fade_time_out = glib.timeout_add(msec, self.inc_alpha)
		self.surface2 = self.get_surface(self.wp_files[index])

if len(sys.argv) >= 2:
	wallpaper_dir = sys.argv[1] # "/home/odroid/Pictures/Wallpapers"

	win = gg_wall()
	win.set_directory(wallpaper_dir)
	win.set_shuffle(10000)
	win.show_all()
	gtk.main()
else:
	print("gg-wall needs a dirtectory to read wallpaper files from\nUsage: gg-wall <path>\n")

