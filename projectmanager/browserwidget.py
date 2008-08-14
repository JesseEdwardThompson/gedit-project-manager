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

import os
import gtk
import gobject
import gedit
from xml.dom import minidom

class ProjectBrowser( gtk.VBox ):
    """ A widget that resides in gedits side panel. """

    def __init__(self, geditwindow):
        """ geditwindow -- an instance of gedit.Window """
        
        gtk.VBox.__init__(self)
        self.geditwindow = geditwindow

        self.build_toolbar()

        # add a treeview
        self.treestore = gtk.TreeStore(gobject.TYPE_STRING,  # short name
                                       gobject.TYPE_STRING,  # long name
                                       gtk.gdk.Pixbuf)       # file/folder icon
        
        # build a list of all project files
        self.filelist = []
        self.load_filelist()

        # get the common prefix of all project files
        self.prefix = os.path.commonprefix(self.filelist)
        self.prefixlen = len(self.prefix)
        
        # Create a (filename, [list of directories in path) list
        # to pass to self.add_dir_to_tree
        dirlist = []
        for project_file in self.filelist:
            separated_dirs = project_file[self.prefixlen:].split(os.sep)
            dirlist.append((project_file, separated_dirs))
        
        # Add all files to self.treestore
        root_iter = self.treestore.get_iter_root()        
        self.add_dir_to_tree(root_iter, self.prefix, self.prefix, dirlist)
        
        # Put a scrolled window in the widget, and fill it with a treeview
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_IN)
        self.browser = gtk.TreeView(self.treestore)
        self.browser.set_headers_visible(False)
        self.browser.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        sw.add(self.browser)
        
        self.pack_start(sw)

        # add a column to the treeview
        self.column = gtk.TreeViewColumn("File")
        self.browser.append_column(self.column)

        # add a pixbuf cell to the column (for file/directory/missing icon)
        self.cpb = gtk.CellRendererPixbuf()
        self.column.pack_start(self.cpb,False)
        self.column.add_attribute(self.cpb, 'pixbuf', 2)
        
        # add a text cell to the column (for short filename)
        self.crt = gtk.CellRendererText()
        self.column.pack_start(self.crt,True)
        self.column.add_attribute(self.crt, 'text', 0)
        
        # add a text cell to the column (for long filename)
        #self.long_crt = gtk.CellRendererText()
        #self.column.pack_start(self.long_crt,True)
        #self.column.add_attribute(self.long_crt, 'text', 1)
        
        # expand root project folder
        self.browser.expand_row((0,), False)

        self.show_all()
        
    def build_toolbar(self):
        """Creates a toolbar with project related actions"""
        tb = gtk.Toolbar()
        new_button = gtk.ToolButton(gtk.STOCK_NEW)
        new_button.set_tooltip_text("Create a new project")
        
        open_button = gtk.ToolButton(gtk.STOCK_OPEN)
        open_button.set_tooltip_text("Open a project")
        
        add_button = gtk.ToolButton(gtk.STOCK_ADD)
        add_button.set_tooltip_text("Add file(s) to project")

        remove_button = gtk.ToolButton(gtk.STOCK_REMOVE)
        remove_button.set_tooltip_text("Remove selected file(s) from project")

        tb.insert(new_button, 0)
        tb.insert(open_button, 1)
        tb.insert(gtk.SeparatorToolItem(), 2)
        tb.insert(add_button, 3)
        tb.insert(remove_button, 4)

        tb.set_style(gtk.TOOLBAR_ICONS)
        self.pack_start(tb, False, False)

    def load_filelist(self):
        """Loads all files from a project file.
        Stores them in self.filelist.
        """
        xml = minidom.parse(os.path.expanduser("~/test.gedit-project"))
        for subfile in xml.getElementsByTagName('file'):
            if os.path.isfile(subfile.childNodes[0].data.strip()):
                self.filelist.append(subfile.childNodes[0].data.strip())
        self.filelist.sort(self.insensitive_cmp)
        
    def save_filelist(self):
        """Saves all files in self.filelist into a project file"""
        out_xml = minidom.Document()
        out_xml.version = 1.0

        gedit_project_element = minidom.Element( 'gedit-project' )

        for filename in self.filelist:
            file_element = minidom.Element( 'file' )
            text_node = minidom.Text()
            text_node.data = filename
            file_element.childNodes.append( text_node )
            gedit_project_element.childNodes.append( file_element )

        out_xml.childNodes.append( gedit_project_element )

        #outfile = file(#we need a filename here, "w")
        #outfile.writelines( out_xml.toprettyxml() )
        out_xml.unlink()
        #outfile.close()

    def add_file_to_tree(self, dir_iter, project_file):
        """Adds project_file to the project browser filetree
        at position specified by dir_iter.
        """
        file_icon = 0
        if os.path.isfile(project_file):
            file_icon = self.render_icon(gtk.STOCK_FILE, 
                                         gtk.ICON_SIZE_SMALL_TOOLBAR)
        else:
            file_icon = self.render_icon(gtk.STOCK_DIRECTORY, 
                                         gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.treestore.append(dir_iter, [project_file.split(os.sep).pop(), 
                                         project_file, file_icon])

    def add_dir_to_tree(self, piter, dir_to_add, dir_full_path, dirlist):
        """Recursively adds directories in dirlist to the project
        browser filetree at position specified by dir_iter.
        Calls add_file_to_tree for any files in dirlist.
        """
        dir_iter = self.treestore.append(piter, 
            [dir_to_add, dir_full_path, self.render_icon(gtk.STOCK_DIRECTORY,
            gtk.ICON_SIZE_SMALL_TOOLBAR)])
        dirmap = {}
        
        dir_filelist = []
        
        for (project_file, separated_dirs) in dirlist:
            if len(separated_dirs) > 1:
                if separated_dirs[0] not in dirmap:
                    dirmap[separated_dirs[0]] = \
                        [(project_file, separated_dirs[1:])]
                else:
                    dirmap[separated_dirs[0]].append(
                        (project_file, separated_dirs[1:]))
            else:
                dir_filelist.append(project_file)

        for key in sorted(dirmap.keys(), self.insensitive_cmp):
            self.add_dir_to_tree(dir_iter, key, 
                                 os.path.join(dir_full_path, key), 
                                 dirmap[key])
                
        for project_file in sorted(dir_filelist, self.insensitive_cmp):
            self.add_file_to_tree(dir_iter, project_file)

    def insensitive_cmp(self, str_1, str_2):
        """A case-insensitive comparison method used for sorting"""
        return cmp(str_1.lower(), str_2.lower())

