# Project Manager -- a plugin for gedit
# Copyright (C) 2008 Jeff Shipley (jeffquiparle@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gedit
import gtk
from browserwidget import ProjectBrowser

icon = [
"16 16 2 1",
" 	c None",
".	c #000000",
" ........       ",
".        .      ",
".        ...    ",
".  ...   .  .   ",
".        .   .  ",
".  ....  .   .  ",
".        .   .  ",
".  ....  .  ..  ",
".        .  . . ",
".        . .   .",
" ........  .   .",
"    . .   .   . ",
"     . ...  ..  ",
"     .     .    ",
"      .  ..     ",
"       ..       "]
       
#-------------------------------------------------------------------------------
class ProjectManagerPlugin(gedit.Plugin):

    def __init__(self):
        gedit.Plugin.__init__(self)
        

    def is_configurable(self):
        return False
        

    def activate(self, window):
        # create the browser pane
        panel = window.get_side_panel()
        image = gtk.Image()
        drawable = gtk.gdk.get_default_root_window()
        colormap = drawable.get_colormap()
        pixmap, mask = gtk.gdk.pixmap_colormap_create_from_xpm_d(drawable, 
            colormap, None, icon)
        image.set_from_pixmap(pixmap, mask)
        self.projectbrowser = ProjectBrowser(window)
        panel.add_item(self.projectbrowser, "Project Browser", image)
          

    def deactivate(self, window):
        pane = window.get_side_panel()
        pane.remove_item(self.projectbrowser)
        

    def update_ui(self, window):
        view = window.get_active_view()

