''' 
A Tkinter Vertical Scroll Wheel Class for making canvases that are scrollable.

Based on:
  https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
'''
import tkinter as tk # abbrev

class VerticalScrolledFrame(tk.Frame):
    """A Tkinter scrollable frame.
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    __slots__ = ['_interior', '_canvas']

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.parent = parent

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self._canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self._canvas.yview)

        # mousewheel scrolling
        self.parent.bind_all("<MouseWheel>", self._on_mousewheel)

        # Reset the view
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self._interior = _interior = tk.Frame(self._canvas)
        interior_id = self._canvas.create_window(0, 0, window=_interior, anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (_interior.winfo_reqwidth(), _interior.winfo_reqheight())
            self._canvas.config(scrollregion="0 0 %s %s" % size)
            if _interior.winfo_reqwidth() != self._canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                self._canvas.config(width=_interior.winfo_reqwidth())
        self._interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if _interior.winfo_reqwidth() != self._canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                self._canvas.itemconfigure(interior_id, width=self._canvas.winfo_width())
        self._canvas.bind('<Configure>', _configure_canvas)
    
    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1*(event.delta)), "units")
        # On Windows: self._canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    @property
    def interior(self) -> str:
        return self._interior
    @interior.setter
    def interior(self, i):
        self._interior = i