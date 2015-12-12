using Gtk;
using GLib;
using Cairo;

class GgWall : Gtk.Window {

	int screenWidth = 1024;
	int screenHeight = 768;

	Cairo.ImageSurface surface = null;

	string[] files;

	private int index = 0;

	public GgWall() {
		Gdk.Window rootWin = Gdk.get_default_root_window();
		this.screenWidth = rootWin.get_width();
		this.screenHeight = rootWin.get_height();
		this.set_default_size(screenWidth, screenHeight);
		this.set_keep_below(true);
		this.set_resizable(false);
		this.move(0, 0);
		this.decorated = false;
		this.set_type_hint(Gdk.WindowTypeHint.DESKTOP);
		this.create_drawing_area();

		this.surface = new Cairo.ImageSurface(Cairo.Format.RGB24, this.screenWidth, this.screenHeight);
	}

	private void create_drawing_area() {
		Gtk.DrawingArea area = new Gtk.DrawingArea();
		area.set_size_request(this.screenWidth, this.screenHeight);
		area.draw.connect(on_draw);
		this.add(area);
	}

	private bool on_draw (Widget widget, Context ctx) {
		ctx.save();
		if (null == this.surface) {		
			ctx.set_source_rgb(0, 0.3, 0.1);
			ctx.move_to(0, 0);
			ctx.rel_line_to(this.screenWidth, 0);
			ctx.rel_line_to(0, this.screenHeight);
			ctx.rel_line_to(-this.screenWidth, 0);
			ctx.close_path();
			ctx.fill();
			ctx.restore();
			return true;
		}
		ctx.set_source_surface(this.surface, 0, 0);
		ctx.paint();
		ctx.restore();
		return false;
	}

	private void draw_surface(Gdk.Pixbuf buffer) {
		var ctx = new Cairo.Context(this.surface);		
		Gdk.cairo_set_source_pixbuf(ctx, buffer, 0, 0);
		ctx.paint();
	}

	private void blend_buffer(Gdk.Pixbuf buffer, double alpha) {
		var ctx = new Cairo.Context(this.surface);		
		Gdk.cairo_set_source_pixbuf(ctx, buffer, 0, 0);
		ctx.paint_with_alpha(alpha);
	}

	private string[] enum_files(string path) {
		var result = new GenericArray<string>();
		var dir = File.new_for_path(path);
		var enumerator = 
			dir.enumerate_children (FileAttribute.STANDARD_NAME + "," + FileAttribute.STANDARD_CONTENT_TYPE, 0);
		FileInfo info;
		while ((info = enumerator.next_file()) != null) {
			string contentType = info.get_content_type();
			if (contentType.contains("image")) { 
				string filePath = path + "/" + info.get_name();
				stdout.printf("Added file " + filePath + " : " + contentType + "\n");
				result.add (filePath);		
			}
		}
		stdout.flush();
		return result.data;
	}

	private int get_next_index() {
		if (this.index < this.files.length -1) {
			return this.index + 1;
		}
		return 0;
	}

	public delegate void OnFadeFinished();

	public void fade_show(int fade_time, double alpha_delta, OnFadeFinished onFinished) {
		if (this.files.length == 0) return;
		var buffer = new Gdk.Pixbuf.from_file(this.files[this.index]);	
		this.draw_surface(buffer);
		var buffer2 = new Gdk.Pixbuf.from_file(this.files[this.get_next_index()]);
		double alpha = 0.0;
		Timeout.add(fade_time, () => {
			if (alpha < 1.0) {
				this.blend_buffer(buffer2, alpha);
				alpha += alpha_delta;
				this.queue_draw(); // slow???
				return true;
			}
			this.draw_surface(buffer2);
			this.index = this.get_next_index();
			onFinished();
			return false;
		});
	}

	private bool load_dir(string path) {
    try {
			this.files = enum_files(path);
			var buffer = new Gdk.Pixbuf.from_file(this.files[0]);
			this.draw_surface(buffer);
			this.queue_draw();
			return true;
		} catch (Error ex) {
			return false;
		}
	}

	static int main(string[] args) {
		int delay = 30000; // When to switch pictures
		int fade_time = 50; // Speed of fade
		double fade_delta = 0.05; // intensity of fade		
		Gtk.init(ref args);
		var self = new GgWall();
		self.load_dir(args[1]);
		if (null != args[2]) {
			delay = int.parse(args[2]);
		}
		if (null != args[3]) {
			fade_time = int.parse(args[3]);
		}
		if (null != args[4]) {
			fade_delta = double.parse(args[4]);
		}
		OnFadeFinished done = () => Timeout.add(delay, () => { 
			self.fade_show(fade_time, fade_delta, () => {}); 
			return true; 
		} );

		done();

		self.show_all();


		Gtk.main();
		return 0;	
	}
}
