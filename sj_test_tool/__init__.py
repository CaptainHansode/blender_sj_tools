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


import bpy
import copy
import os
from mathutils import Vector

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

# memo:https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo
bl_info = {
    "name": "SJ Test Tools",
    "author": "CaptainHansode",
    "version": (0, 8, 0),
    "blender": (2, 80, 0),
    "location":  "View3D > Sidebar > Item Tab",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}


class VIEW3D_OT_grid_switch(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "view3d.grid_switch"
    bl_label = "Grid Switch"

    scale = bpy.props.FloatProperty(default=1.0, subtype='UNSIGNED')
    subdivisions = bpy.props.IntProperty(default=10, min=1, max=1024)

    @classmethod
    def poll(cls, context):
        return 'VIEW_3D' in (a.type for a in context.screen.areas)

    def execute(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].grid_scale = self.scale
                area.spaces[0].grid_subdivisions = self.subdivisions
        return {'FINISHED'}


class SJTestToolsProperties(bpy.types.PropertyGroup):
    r""""""
    set_name: bpy.props.StringProperty(name="Name", default="")


class SJTestToolsLeftSideBar(bpy.types.Panel):
    r"""Creates a Panel in the Object properties window"""
    bl_label = "GRID SWITCH"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        # col.label("Scale / Subdivisions")

        prop = col.operator(VIEW3D_OT_grid_switch.bl_idname, text="0.125 / 10")
        prop.scale = 0.125
        prop.subdivisions = 10

        prop = col.operator(VIEW3D_OT_grid_switch.bl_idname, text="0.156 / 8")
        prop.scale = 0.156
        prop.subdivisions = 8


class SJTmApply(bpy.types.Operator):
    r"""トランスフォーム適応"""
    bl_idname = "sj_test_tools.tm_apply"
    bl_label = "Tm Apply"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {'FINISHED'}


class SJCenterToObjVolume(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.c_to_obj_vol"
    bl_label = "Center To Obj Volume"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {'FINISHED'}


class SJSetName(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.set_name"
    bl_label = "SJ Set Name"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        sjtp = context.scene.sj_test_tools_props
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH":
                continue
            obj.name = sjtp.set_name
        # bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {'FINISHED'}


class SJRemoveMat(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.remove_mat"
    bl_label = "Remove Mat"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        for obj in context.selected_objects:
            if obj.type != "MESH":
                continue
            bpy.context.window.view_layer.objects.active = obj
            bpy.ops.object.material_slot_remove()
        return {'FINISHED'}


def get_edge_pos(axis='x', pos_type='min', current_obj=None):
    r"""オブジェクトの端っこの頂点位置を出す"""
    c_obj = current_obj
    verts_pos = [c_obj.matrix_world @ v.co for v in c_obj.data.vertices]
    edge_pos = 0.0
    if axis.lower() == 'x':
        verts_pos = [pos.x for pos in verts_pos]
    if axis.lower() == 'y':
        verts_pos = [pos.y for pos in verts_pos]
    if axis.lower() == 'z':
        verts_pos = [pos.z for pos in verts_pos]

    if pos_type.lower() == 'min':
        edge_pos = min(verts_pos)
    else:
        edge_pos = max(verts_pos)
    return edge_pos


def get_edge_pos_from_view(axis='x', pos_type='min', current_obj=None):
    r"""オブジェクトの端っこの頂点位置を出す"""
    # 3D view matrix
    for area in bpy.context.window.screen.areas:
        if area.type == "VIEW_3D":
            v_mt = area.spaces.active.region_3d.view_matrix
            # print(area.spaces.active.region_3d.view_matrix)
    edge_pos = 0.0    
    c_obj = current_obj
    # 一端ワールドmatrixにしてからViewマトリクスへ変換
    verts_pos = [v_mt @ c_obj.matrix_world @ v.co for v in c_obj.data.vertices]

    if axis.lower() == 'x':
        verts_pos = [pos.x for pos in verts_pos]
    if axis.lower() == 'y':
        verts_pos = [pos.y for pos in verts_pos]
    if axis.lower() == 'z':
        verts_pos = [pos.z for pos in verts_pos]

    if pos_type.lower() == 'min':
        edge_pos = min(verts_pos)
    else:
        edge_pos = max(verts_pos)
    return edge_pos


class SJCenterToObjTop(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.c_to_obj_top"
    bl_label = "Top"
    bl_description = "Move pivot to object top"
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        context.scene.tool_settings.use_transform_data_origin = True
        context.scene.tool_settings.use_transform_skip_children = True

        objs = [obj for obj in context.selected_objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')  # 選択解除
        
        for obj in objs:
            obj.select_set(True)  # 選択してセンター移動オンリーにしてムーブ
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            pos = get_edge_pos("z", "max", obj)

            mov_val = obj.matrix_world.transposed()[3].z - pos  # woeld
            bpy.ops.transform.translate(
                value=(0, 0, -mov_val),
                orient_type='VIEW',
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                orient_matrix_type='VIEW',
                constraint_axis=(False, False, True),
                mirror=True)
            obj.select_set(False)
        context.scene.tool_settings.use_transform_data_origin = False
        context.scene.tool_settings.use_transform_skip_children = False

        for obj in objs:
            obj.select_set(True)
        return {'FINISHED'}


class SJCenterToObjBotm(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.c_to_obj_botm"
    bl_label = "Bottom"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        context.scene.tool_settings.use_transform_data_origin = True
        context.scene.tool_settings.use_transform_skip_children = True

        objs = [obj for obj in context.selected_objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')  # 選択解除
        
        for obj in objs:
            obj.select_set(True)  # 選択してセンター移動オンリーにしてムーブ
            # バウンディングboxより
            # bbox_cnr = [
            #     obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            # z_botm = min([pos.z for pos in bbox_cnr])  # z底面座標

            # 頂点で
            # verts_pos = [obj.matrix_world @ v.co for v in obj.data.vertices]
            # z_botm = min([pos.z for pos in verts_pos])
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            z_botm = get_edge_pos(axis="z", pos_type="min", current_obj=obj)
            mov_val = obj.matrix_world.transposed()[3].z - z_botm  # woeld
            bpy.ops.transform.translate(
                value=(0, 0, -mov_val),
                orient_type='GLOBAL',
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                orient_matrix_type='GLOBAL',
                constraint_axis=(False, False, True),
                mirror=True)
            obj.select_set(False)

        context.scene.tool_settings.use_transform_data_origin = False
        context.scene.tool_settings.use_transform_skip_children = False

        for obj in objs:
            obj.select_set(True)
        return {'FINISHED'}

class SJCenterToObjCenter(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.c_to_obj_center"
    bl_label = "Center"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        objs = [obj for obj in context.selected_objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')  # 選択解除
        for obj in objs:
            obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        return {'FINISHED'}

class SJCenterToObjLeft(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.c_to_obj_left"
    bl_label = "Left"
    bl_description = "Move pivot to object Left"
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        # 3D view matrix
        for area in bpy.context.window.screen.areas:
            if area.type == "VIEW_3D":
                v_mt = area.spaces.active.region_3d.view_matrix
        v_mt_3x3 = v_mt.to_3x3()

        context.scene.tool_settings.use_transform_data_origin = True
        context.scene.tool_settings.use_transform_skip_children = True

        objs = [obj for obj in context.selected_objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')  # 選択解除

        for obj in objs:
            obj.select_set(True)  # 選択してセンター移動オンリーにしてムーブ
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            pos = get_edge_pos_from_view("x", "min", obj)
            v_mt_obj = v_mt @ obj.matrix_world
            mov_val = v_mt_obj.transposed()[3].x - pos  # woeld
            # 移動はView軸で移動させる
            bpy.ops.transform.translate(
                value=(-mov_val, 0, 0),
                orient_type='VIEW',
                orient_matrix=(v_mt_3x3[0], v_mt_3x3[1], v_mt_3x3[2]),
                orient_matrix_type='VIEW',
                constraint_axis=(True, False, False),
                mirror=True)
            obj.select_set(False)
        context.scene.tool_settings.use_transform_data_origin = False
        context.scene.tool_settings.use_transform_skip_children = False

        for obj in objs:
            obj.select_set(True)
        return {'FINISHED'}


class SJCenterToObjRight(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.c_to_obj_right"
    bl_label = "Right"
    bl_description = "Move pivot to object Right"
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        # 3D view matrix
        for area in bpy.context.window.screen.areas:
            if area.type == "VIEW_3D":
                v_mt = area.spaces.active.region_3d.view_matrix
        v_mt_3x3 = v_mt.to_3x3()

        context.scene.tool_settings.use_transform_data_origin = True
        context.scene.tool_settings.use_transform_skip_children = True

        objs = [obj for obj in context.selected_objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')  # 選択解除

        for obj in objs:
            obj.select_set(True)  # 選択してセンター移動オンリーにしてムーブ
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            pos = get_edge_pos_from_view("x", "max", obj)
            v_mt_obj = v_mt @ obj.matrix_world
            mov_val = v_mt_obj.transposed()[3].x - pos  # woeld
            # 移動はView軸で移動させる
            bpy.ops.transform.translate(
                value=(-mov_val, 0, 0),
                orient_type='VIEW',
                orient_matrix=(v_mt_3x3[0], v_mt_3x3[1], v_mt_3x3[2]),
                orient_matrix_type='VIEW',
                constraint_axis=(True, False, False),
                mirror=True)
            obj.select_set(False)
        context.scene.tool_settings.use_transform_data_origin = False
        context.scene.tool_settings.use_transform_skip_children = False

        for obj in objs:
            obj.select_set(True)
        return {'FINISHED'}


sj_def_props = {
    "a": True,
    "b": True,
    "items": {
        "test_props": "myprops"
    }
}


class SJTestRun(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.test_run"
    bl_label = "Make null median point"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        if len(bpy.context.selected_objects) is 0:
            return {'FINISHED'}
        obj_vec = [obj.matrix_world.translation for obj in bpy.context.selected_objects]

        # 全ての平均点
        piv = sum(obj_vec, Vector()) / len(obj_vec)
        
        emp = bpy.data.objects.new("empty", None)
        emp.matrix_world.translation = piv
        if len(bpy.data.collections) is 0:
            bpy.context.scene.collection.objects.link(emp)
        else:
            bpy.data.collections[0].objects.link(emp)
        w_mt = bpy.context.selected_objects[0].matrix_world
        for obj in bpy.context.selected_objects:
            w_mt = copy.copy(obj.matrix_world)
            obj.parent = emp
            obj.matrix_world = w_mt
        bpy.context.selected_objects[0].users_collection

        # コレクションをつくる
        # col = bpy.data.collections.new('nils')
        # bpy.context.scene.collection.children.link(col)
        # import bpy
        # from mathutils import Vector

        # ob = bpy.context.object
        # ob.update_from_editmode()

        # me = ob.data
        # verts_sel = [v.co for v in me.vertices if v.select]

        # pivot = sum(verts_sel, Vector()) / len(verts_sel)

        # print("Local:", pivot)
        # print("Global:", ob.matrix_world * pivot)

        return {'FINISHED'}


class SJTestDefPropsA(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.def_props_a"
    bl_label = "Test A"
    bl_description = ""
    bl_options = {'UNDO', 'PRESET'}

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""
        sj_def_props["items"]["test_props"] = "Push A"
        print(sj_def_props["items"]["test_props"])
        

        if sj_def_props["a"]:
            sj_def_props["a"] = False
        print(sj_def_props["a"])
        return {'FINISHED'}


class SJTestDefPropsB(bpy.types.Operator):
    r""""""
    bl_idname = "sj_test_tools.def_props_b"
    bl_label = "Test B"
    bl_description = ""
    # bl_options = {'UNDO', 'PRESET'}
    bl_options = {'UNDO'}

    msg: bpy.props.StringProperty(name="Message", default="")    

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def execute(self, context):
        r""""""

        sj_def_props["items"]["test_props"] = "Push B"
        print(sj_def_props["items"]["test_props"])

        if sj_def_props["a"] is False:
            sj_def_props["a"] = True
        print(sj_def_props["a"])
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        layout = self.layout
        layout.label(text="Test")
        self.msg = "aaaa\naaaa"
        layout.prop(self, "msg")


class SJTestToolsPanel(bpy.types.Panel):
    r""""""
    bl_label = "SJ Test"
    bl_idname = "SJTESTTOOLS_PT_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_context = "posemode"  # どのモードでも出したい場合はcontextを指定しない
    bl_category = "Item"

    def draw(self, context):
        sjtp = context.scene.sj_test_tools_props
        layout = self.layout
        layout.label(text="Test")
        col = layout.column(align=True)
        
        col.operator("sj_test_tools.test_run")
        col.operator("sj_test_tools.def_props_a")
        col.operator("sj_test_tools.def_props_b")

        row = col.row(align=True)
        row.label(text=" ")
        row.operator("sj_test_tools.c_to_obj_top")
        row.label(text=" ")

        row = col.row(align=True)
        row.operator("sj_test_tools.c_to_obj_left")
        row.operator("sj_test_tools.c_to_obj_center")
        row.operator("sj_test_tools.c_to_obj_right")

        row = col.row(align=True)
        row.label(text=" ")
        row.operator("sj_test_tools.c_to_obj_botm")
        row.label(text=" ")
        # row.separator(factor=1.0)
        
        # col = layout.column(align=True)
        # col.operator("sj_test_tools.tm_apply")
        # col.operator("sj_test_tools.c_to_obj_vol")
        # col.operator("sj_test_tools.c_to_obj_botm")
        
        # col.prop(sjtp, "set_name")
        # col.operator("sj_test_tools.set_name")
        # col.operator("sj_test_tools.remove_mat")

        # col.separator(factor=1.3)
        # col.operator("sj_test_tools.export_fbx")


class SJTestToolsAllIconPanel(bpy.types.Panel):
    r""""""
    bl_label = "SJ All ICON LIST"
    bl_idname = "SJTestToolsAllIconPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = "posemode"  # どのモードでも出したい場合はcontextを指定しない
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        # icons = ['NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_RIGHT', 'DISCLOSURE_TRI_DOWN', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'DUPLICATE', 'TRASH', 'COLLECTION_NEW', 'OPTIONS', 'NODE', 'NODE_SEL', 'WINDOW', 'WORKSPACE', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ADD', 'REMOVE', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'CHECKMARK', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'FCURVE_SNAPSHOT', 'OBJECT_HIDDEN', 'TOPBAR', 'STATUSBAR', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'UNLINKED', 'LINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'DRIVER_DISTANCE', 'DRIVER_ROTATIONAL_DIFFERENCE', 'DRIVER_TRANSFORM', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'FILE_NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'THREE_DOTS', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'BRUSHES_ALL', 'LIGHT', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'OUTPUT', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TOOL_SETTINGS', 'SHADERFX', 'MODIFIER', 'BLANK1', 'FAKE_USER_OFF', 'FAKE_USER_ON', 'VIEW3D', 'GRAPH', 'OUTLINER', 'PROPERTIES', 'FILEBROWSER', 'IMAGE', 'INFO', 'SEQUENCE', 'TEXT', 'SOUND', 'ACTION', 'NLA', 'PREFERENCES', 'TIME', 'NODETREE', 'CONSOLE', 'TRACKER', 'ASSET_MANAGER', 'NODE_COMPOSITING', 'NODE_TEXTURE', 'NODE_MATERIAL', 'UV', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'UV_DATA', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'TRACKING', 'TRACKING_BACKWARDS', 'TRACKING_FORWARDS', 'TRACKING_BACKWARDS_SINGLE', 'TRACKING_FORWARDS_SINGLE', 'TRACKING_CLEAR_BACKWARDS', 'TRACKING_CLEAR_FORWARDS', 'TRACKING_REFINE_BACKWARDS', 'TRACKING_REFINE_FORWARDS', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LIGHT_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'COMMUNITY', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'CAMERA_STEREO', 'PACKAGE', 'UGLYPACKAGE', 'EXPERIMENTAL', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'PRESET', 'RENDER_ANIMATION', 'RENDER_STILL', 'LIBRARY_DATA_BROKEN', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'LINE_DATA', 'LIBRARY_DATA_OVERRIDE', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'FACE_MAPS', 'RNA', 'RNA_ADD', 'MOUSE_LMB', 'MOUSE_MMB', 'MOUSE_RMB', 'MOUSE_MOVE', 'MOUSE_LMB_DRAG', 'MOUSE_MMB_DRAG', 'MOUSE_RMB_DRAG', 'MEMORY', 'PRESET_NEW', 'DECORATE', 'DECORATE_KEYFRAME', 'DECORATE_ANIMATE', 'DECORATE_DRIVER', 'DECORATE_LINKED', 'DECORATE_LIBRARY_OVERRIDE', 'DECORATE_UNLOCKED', 'DECORATE_LOCKED', 'DECORATE_OVERRIDE', 'FUND', 'TRACKER_DATA', 'HEART', 'ORPHAN_DATA', 'USER', 'SYSTEM', 'SETTINGS', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LIGHT', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'OUTLINER_OB_SPEAKER', 'OUTLINER_OB_FORCE_FIELD', 'OUTLINER_OB_GROUP_INSTANCE', 'OUTLINER_OB_GREASEPENCIL', 'OUTLINER_OB_LIGHTPROBE', 'OUTLINER_OB_IMAGE', 'RESTRICT_COLOR_OFF', 'RESTRICT_COLOR_ON', 'HIDE_ON', 'HIDE_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_RENDER_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_INSTANCED_OFF', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LIGHT', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_SPEAKER', 'OUTLINER_DATA_LIGHTPROBE', 'OUTLINER_DATA_GP_LAYER', 'OUTLINER_DATA_GREASEPENCIL', 'GP_SELECT_POINTS', 'GP_SELECT_STROKES', 'GP_MULTIFRAME_EDITING', 'GP_ONLY_SELECTED', 'GP_SELECT_BETWEEN_STROKES', 'MODIFIER_OFF', 'MODIFIER_ON', 'ONIONSKIN_OFF', 'ONIONSKIN_ON', 'RESTRICT_VIEW_ON', 'RESTRICT_VIEW_OFF', 'RESTRICT_INSTANCED_ON', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'MESH_CAPSULE', 'EMPTY_SINGLE_ARROW', 'LIGHT_POINT', 'LIGHT_SUN', 'LIGHT_SPOT', 'LIGHT_HEMI', 'LIGHT_AREA', 'CUBE', 'SPHERE', 'CONE', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'EMPTY_AXIS', 'STROKE', 'EMPTY_ARROWS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'LIGHTPROBE_CUBEMAP', 'LIGHTPROBE_PLANAR', 'LIGHTPROBE_GRID', 'COLOR_RED', 'COLOR_GREEN', 'COLOR_BLUE', 'TRIA_RIGHT_BAR', 'TRIA_DOWN_BAR', 'TRIA_LEFT_BAR', 'TRIA_UP_BAR', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'FORCE_FLUIDFLOW', 'RIGID_BODY', 'RIGID_BODY_CONSTRAINT', 'IMAGE_PLANE', 'IMAGE_BACKGROUND', 'IMAGE_REFERENCE', 'NODE_INSERT_ON', 'NODE_INSERT_OFF', 'NODE_TOP', 'NODE_SIDE', 'NODE_CORNER', 'ANCHOR_TOP', 'ANCHOR_BOTTOM', 'ANCHOR_LEFT', 'ANCHOR_RIGHT', 'ANCHOR_CENTER', 'SELECT_SET', 'SELECT_EXTEND', 'SELECT_SUBTRACT', 'SELECT_INTERSECT', 'SELECT_DIFFERENCE', 'ALIGN_LEFT', 'ALIGN_CENTER', 'ALIGN_RIGHT', 'ALIGN_JUSTIFY', 'ALIGN_FLUSH', 'ALIGN_TOP', 'ALIGN_MIDDLE', 'ALIGN_BOTTOM', 'BOLD', 'ITALIC', 'UNDERLINE', 'SMALL_CAPS', 'CON_ACTION', 'HOLDOUT_OFF', 'HOLDOUT_ON', 'INDIRECT_ONLY_OFF', 'INDIRECT_ONLY_ON', 'CON_CAMERASOLVER', 'CON_FOLLOWTRACK', 'CON_OBJECTSOLVER', 'CON_LOCLIKE', 'CON_ROTLIKE', 'CON_SIZELIKE', 'CON_TRANSLIKE', 'CON_DISTLIMIT', 'CON_LOCLIMIT', 'CON_ROTLIMIT', 'CON_SIZELIMIT', 'CON_SAMEVOL', 'CON_TRANSFORM', 'CON_TRANSFORM_CACHE', 'CON_CLAMPTO', 'CON_KINEMATIC', 'CON_LOCKTRACK', 'CON_SPLINEIK', 'CON_STRETCHTO', 'CON_TRACKTO', 'CON_ARMATURE', 'CON_CHILDOF', 'CON_FLOOR', 'CON_FOLLOWPATH', 'CON_PIVOT', 'CON_SHRINKWRAP', 'MODIFIER_DATA', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'MOD_TINT', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_FLUID', 'MOD_SOLIDIFY', 'MOD_SCREW', 'MOD_VERTEX_WEIGHT', 'MOD_DYNAMICPAINT', 'MOD_REMESH', 'MOD_OCEAN', 'MOD_WARP', 'MOD_SKIN', 'MOD_TRIANGULATE', 'MOD_WIREFRAME', 'MOD_DATA_TRANSFER', 'MOD_NORMALEDIT', 'MOD_PARTICLE_INSTANCE', 'MOD_HUE_SATURATION', 'MOD_NOISE', 'MOD_OFFSET', 'MOD_SIMPLIFY', 'MOD_THICKNESS', 'MOD_INSTANCE', 'MOD_TIME', 'MOD_OPACITY', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_SOUND', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'ACTION_TWEAK', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'KEYFRAME_HLT', 'KEYFRAME', 'KEYINGSET', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'DRIVER', 'SOLO_OFF', 'SOLO_ON', 'FRAME_PREV', 'FRAME_NEXT', 'NLA_PUSHDOWN', 'IPO_CONSTANT', 'IPO_LINEAR', 'IPO_BEZIER', 'IPO_SINE', 'IPO_QUAD', 'IPO_CUBIC', 'IPO_QUART', 'IPO_QUINT', 'IPO_EXPO', 'IPO_CIRC', 'IPO_BOUNCE', 'IPO_ELASTIC', 'IPO_BACK', 'IPO_EASE_IN', 'IPO_EASE_OUT', 'IPO_EASE_IN_OUT', 'NORMALIZE_FCURVES', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'CURSOR', 'PIVOT_BOUNDBOX', 'PIVOT_CURSOR', 'PIVOT_INDIVIDUAL', 'PIVOT_MEDIAN', 'PIVOT_ACTIVE', 'CENTER_ONLY', 'ROOTCURVE', 'SMOOTHCURVE', 'SPHERECURVE', 'INVERSESQUARECURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'PROP_PROJECTED', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'SNAP_FACE_CENTER', 'SNAP_PERPENDICULAR', 'SNAP_MIDPOINT', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_GRID', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'SNAP_INCREMENT', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'OBJECT_ORIGIN', 'ORIENTATION_GLOBAL', 'ORIENTATION_GIMBAL', 'ORIENTATION_LOCAL', 'ORIENTATION_NORMAL', 'ORIENTATION_VIEW', 'COPYDOWN', 'PASTEDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'VIS_SEL_11', 'VIS_SEL_10', 'VIS_SEL_01', 'VIS_SEL_00', 'AUTOMERGE_OFF', 'AUTOMERGE_ON', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'TRANSFORM_ORIGINS', 'GIZMO', 'ORIENTATION_CURSOR', 'NORMALS_VERTEX', 'NORMALS_FACE', 'NORMALS_VERTEX_FACE', 'SHADING_BBOX', 'SHADING_WIRE', 'SHADING_SOLID', 'SHADING_RENDERED', 'SHADING_TEXTURE', 'OVERLAY', 'XRAY', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'LAYER_USED', 'LAYER_ACTIVE', 'OUTLINER_OB_HAIR', 'OUTLINER_DATA_HAIR', 'HAIR_DATA', 'OUTLINER_OB_POINTCLOUD', 'OUTLINER_DATA_POINTCLOUD', 'POINTCLOUD_DATA', 'OUTLINER_OB_VOLUME', 'OUTLINER_DATA_VOLUME', 'VOLUME_DATA', 'HOME', 'DOCUMENTS', 'TEMP', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'SHORTDISPLAY', 'LONGDISPLAY', 'IMGDISPLAY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'FOLDER_REDIRECT', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'FILE_TEXT', 'SORT_DESC', 'SORT_ASC', 'LINK_BLEND', 'APPEND_BLEND', 'IMPORT', 'EXPORT', 'LOOP_BACK', 'LOOP_FORWARDS', 'BACK', 'FORWARD', 'FILE_ARCHIVE', 'FILE_CACHE', 'FILE_VOLUME', 'FILE_3D', 'FILE_HIDDEN', 'FILE_BACKUP', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'MATSHADERBALL', 'MATCLOTH', 'MATFLUID', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'DISC', 'DESKTOP', 'EXTERNAL_DRIVE', 'NETWORK_DRIVE', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'SEQ_STRIP_META', 'SEQ_STRIP_DUPLICATE', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'HANDLE_AUTOCLAMPED', 'HANDLE_AUTO', 'HANDLE_ALIGNED', 'HANDLE_VECTOR', 'HANDLE_FREE', 'VIEW_PERSPECTIVE', 'VIEW_ORTHO', 'VIEW_CAMERA', 'VIEW_PAN', 'VIEW_ZOOM', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLAY_STRIPS', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_MASK', 'BRUSH_MIX', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_TEXDRAW', 'BRUSH_TEXFILL', 'BRUSH_TEXMASK', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'GPBRUSH_SMOOTH', 'GPBRUSH_THICKNESS', 'GPBRUSH_STRENGTH', 'GPBRUSH_GRAB', 'GPBRUSH_PUSH', 'GPBRUSH_TWIST', 'GPBRUSH_PINCH', 'GPBRUSH_RANDOMIZE', 'GPBRUSH_CLONE', 'GPBRUSH_WEIGHT', 'GPBRUSH_PENCIL', 'GPBRUSH_PEN', 'GPBRUSH_INK', 'GPBRUSH_INKNOISE', 'GPBRUSH_BLOCK', 'GPBRUSH_MARKER', 'GPBRUSH_FILL', 'GPBRUSH_AIRBRUSH', 'GPBRUSH_CHISEL', 'GPBRUSH_ERASE_SOFT', 'GPBRUSH_ERASE_HARD', 'GPBRUSH_ERASE_STROKE', 'SMALL_TRI_RIGHT_VEC', 'KEYTYPE_KEYFRAME_VEC', 'KEYTYPE_BREAKDOWN_VEC', 'KEYTYPE_EXTREME_VEC', 'KEYTYPE_JITTER_VEC', 'KEYTYPE_MOVING_HOLD_VEC', 'HANDLETYPE_FREE_VEC', 'HANDLETYPE_ALIGNED_VEC', 'HANDLETYPE_VECTOR_VEC', 'HANDLETYPE_AUTO_VEC', 'HANDLETYPE_AUTO_CLAMP_VEC', 'COLORSET_01_VEC', 'COLORSET_02_VEC', 'COLORSET_03_VEC', 'COLORSET_04_VEC', 'COLORSET_05_VEC', 'COLORSET_06_VEC', 'COLORSET_07_VEC', 'COLORSET_08_VEC', 'COLORSET_09_VEC', 'COLORSET_10_VEC', 'COLORSET_11_VEC', 'COLORSET_12_VEC', 'COLORSET_13_VEC', 'COLORSET_14_VEC', 'COLORSET_15_VEC', 'COLORSET_16_VEC', 'COLORSET_17_VEC', 'COLORSET_18_VEC', 'COLORSET_19_VEC', 'COLORSET_20_VEC', 'EVENT_A', 'EVENT_B', 'EVENT_C', 'EVENT_D', 'EVENT_E', 'EVENT_F', 'EVENT_G', 'EVENT_H', 'EVENT_I', 'EVENT_J', 'EVENT_K', 'EVENT_L', 'EVENT_M', 'EVENT_N', 'EVENT_O', 'EVENT_P', 'EVENT_Q', 'EVENT_R', 'EVENT_S', 'EVENT_T', 'EVENT_U', 'EVENT_V', 'EVENT_W', 'EVENT_X', 'EVENT_Y', 'EVENT_Z', 'EVENT_SHIFT', 'EVENT_CTRL', 'EVENT_ALT', 'EVENT_OS', 'EVENT_F1', 'EVENT_F2', 'EVENT_F3', 'EVENT_F4', 'EVENT_F5', 'EVENT_F6', 'EVENT_F7', 'EVENT_F8', 'EVENT_F9', 'EVENT_F10', 'EVENT_F11', 'EVENT_F12', 'EVENT_ESC', 'EVENT_TAB', 'EVENT_PAGEUP', 'EVENT_PAGEDOWN', 'EVENT_RETURN', 'EVENT_SPACEKEY']
        icons = ['NONE', 'QUESTION', 'ERROR']
        icons = sorted(icons)
        
        layout.label(text="ICON LIST")

        col = layout.column(align=True)
        # col.operator(VIEW3D_OT_grid_switch.bl_idname, text="0.125 / 10", icon="COLOR_RED")
        row = col.row(align=True)
        cnt = 0
        for icn in icons:
            if cnt > 4:
                cnt = 0
                row = col.row(align=True)
                # p = bpy.props.StringProperty(default=icn)
            try:
                row.label(text=icn, icon=icn)
            except:
                pass
            # row.label(text_ctxt=)
            # row.prop(p, icon=icn)
            cnt += 1


classes = (
    VIEW3D_OT_grid_switch,
    SJTestToolsProperties,
    SJTmApply,
    SJCenterToObjVolume,
    SJSetName,
    SJRemoveMat,
    # SJExportFBX,
    SJTestRun,
    SJTestDefPropsA,
    SJTestDefPropsB,
    SJCenterToObjTop,
    SJCenterToObjBotm,
    SJCenterToObjCenter,
    SJCenterToObjLeft,
    SJCenterToObjRight,
    # SJTestToolsLeftSideBar,
    SJTestToolsPanel,
    SJTestToolsAllIconPanel
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sj_test_tools_props = bpy.props.PointerProperty(type=SJTestToolsProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.sj_test_tools_props


if __name__ == "__main__":
    register()
