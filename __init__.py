# -*- coding: utf-8 -*-
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

from . import util
import bpy

from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
        CollectionProperty,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        path_reference_mode,
        axis_conversion,
        )


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


# class SJTestToolsProperties(bpy.types.PropertyGroup):
#     r""""""
#     set_name: bpy.props.StringProperty(name="Name", default="")


class SJReloadScripts(bpy.types.Operator):
    r""""""
    bl_idname = "sj_util_tools.reload_scripts"
    bl_label = "Reload Scripts"
    bl_description = "Reload Scripts."
    # bl_options = {'UNDO', 'PRESET'}

    def execute(self, context):
        r""""""
        # bpy.utils.load_scripts(reload_scripts=True, refresh_scripts=False)
        bpy.ops.script.reload()
        return {'FINISHED'}


class SJReflashScripts(bpy.types.Operator):
    r""""""
    bl_idname = "sj_util_tools.reflash_script"
    bl_label = "Reflash Scripts"
    bl_description = "Reflash Scripts."
    # bl_options = {'UNDO', 'PRESET'}

    def execute(self, context):
        r""""""
        # bpy.ops.script.reload()
        bpy.utils.load_scripts(refresh_scripts=True)
        return {'FINISHED'}


class SJOpenSceneFileDir(bpy.types.Operator):
    r""""""
    bl_idname = "sj_util_tools.open_scene_file_dir"
    bl_label = "Open file dir"
    bl_description = "Open file dir"
    # bl_options = {'UNDO', 'PRESET'}

    def execute(self, context):
        r""""""
        print("aaaa")
        util.open_exproler(bpy.data.filepath)
        return {'FINISHED'}


class SJUtilToolsPanel(bpy.types.Panel):
    r""""""
    bl_label = "SJ"
    bl_idname = "sj_util_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("sj_util_tools.reload_scripts", text="", icon="FILE_REFRESH")
        col.operator("sj_util_tools.open_scene_file_dir", text="", icon="FILE_FOLDER")
        # col.operator("sj_util_tools.reflash_script")


class SJUtilToolsNodePanel(bpy.types.Panel):
    r""""""
    bl_label = "SJ"
    bl_idname = "sj_util_node_panel"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("sj_util_tools.reload_scripts", text="", icon="FILE_REFRESH")
        col.operator("sj_util_tools.open_scene_file_dir", text="", icon="FILE_FOLDER")
        # col.operator("sj_util_tools.reflash_script")


classes = (
    SJReloadScripts,
    SJReflashScripts,
    SJOpenSceneFileDir,
    SJUtilToolsPanel,
    SJUtilToolsNodePanel
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.types.Scene.sj_test_tools_props = bpy.props.PointerProperty(type=SJTestToolsProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # del bpy.types.Scene.sj_test_tools_props


if __name__ == "__main__":
    register()
