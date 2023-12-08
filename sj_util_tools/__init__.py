# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# from bpy.props import (
#         StringProperty,
#         BoolProperty,
#         FloatProperty,
#         EnumProperty,
#         CollectionProperty,
#         )

# from bpy_extras.io_utils import (
#         ImportHelper,
#         ExportHelper,
#         orientation_helper,
#         path_reference_mode,
#         axis_conversion,
#         )


bl_info = {
    "name": "SJ Util Tools",
    "author": "CaptainHansode",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location":  "View3D > Sidebar > Item Tab",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

# reload modules
if "bpy" in locals():
    import importlib
    if "util" in locals():
        importlib.reload(locals()["util"])


import bpy
import bpy.utils.previews
import os
import importlib

from . import util


def register():
    util.register()


def unregister():
    util.unregister()


if __name__ == "__main__":
    register()
