import os
import subprocess
import datetime as dt
import hashlib
import random
import importlib
import bpy
import addon_utils


def _debug():
    pass


def msg_box(message="", title="Message", icon="INFO"):
    r"""messagebox"""
    def draw(self, context):
        if type(message) is list:
            for msg in message:
                if msg == "":
                    continue
                self.layout.label(text=msg)
        if type(message) is str:
            self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def console_print(*msg):
    r"""
    https://blender.stackexchange.com/questions/6173/where-does-console-output-go
    https://docs.blender.org/api/blender_python_api_2_70a_release/bpy.ops.html#overriding-context
    https://blenderartists.org/t/why-not-excute-this-command-bpy-ops-console-clear-scrollback-true-history-false/612332/4
    """
    msg = str(" ".join([str(m) for m in msg]))
    print(msg)
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == "CONSOLE":
                override = {"window": window, "screen": screen, "area": area}
                bpy.ops.console.scrollback_append(override, text=msg, type="OUTPUT")


def open_exproler(file_path):
    r"""Open exproler for win"""
    if file_path == "":
        return None

    if os.path.exists(file_path) is False:
        file_path = os.path.dirname(file_path)

    # ファイルかどうかを判断する
    if os.path.isfile(file_path):
        cmd = "explorer /select,\"{}\"".format(file_path.replace("/", os.sep))
    else:
        cmd = 'explorer \"{}\"'.format(file_path.replace("/", os.sep))
    subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return None


def _my_addons_set_enable():
    """addon_utils
    https://github.com/dfelinto/blender/blob/master/release/scripts/modules/addon_utils.py
    """
    # pref info
    preferences = bpy.context.preferences

    # addon list
    my_addons = ["sj_tests", "sj_util_tools", "sj_show_icon", "sj_set_bone_nator", "sj_selection_set", "sj_change_viewportdisplay_nator", "sj_phaser", "sj_delete_keyframe_by_interval", "sj_bioskin"]
    # current
    curt_addons = [addon.module for addon in preferences.addons]

    for addon_name in my_addons:
        # Addon確認する方法
        # bpy.context.preferences.addons.get("sj_util_tools", (None, False))
        if addon_name not in curt_addons:
            addon_utils.enable(addon_name, default_set=True)
        # else:
        #     addon_utils.disable(addon_name, default_set=True)


# class SJTestToolsProperties(bpy.types.PropertyGroup):
#     r""""""
#     set_name: bpy.props.StringProperty(name="Name", default="")


class SJReloadScripts(bpy.types.Operator):
    r""""""
    # SJ_UTIL_TOOLS_OT_reload_scripts
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
        open_exproler(bpy.data.filepath)
        return {'FINISHED'}


class SJUtilToolsPanel(bpy.types.Panel):
    """"""
    bl_label = "SJ Util"
    bl_idname = "SJUTIL_PT_panel"  # idnameは接続語(_PT_)を含んだ名前にすること
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # bl_context = 'WINDOW'
    # bl_parent_id = "sj_util_panel.main_panel"
    # bl_category = "SJ"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(SJReloadScripts.bl_idname, text="", icon="FILE_REFRESH")
        col.operator(SJOpenSceneFileDir.bl_idname, text="", icon="FILE_FOLDER")
        # col.operator("sj_util_tools.reflash_script")


class SJUtilToolsNodePanel(bpy.types.Panel):
    """"""
    bl_label = "SJ Util"
    bl_idname = "SJUTIL_PT_node_panel"   # idnameは接続語(_PT_)を含んだ名前にすること
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    # bl_region_type = "UI"
    # bl_parent_id = "sj_util_node_panel.node_panel"
    # bl_category = "SJ"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(SJReloadScripts.bl_idname, text="", icon="FILE_REFRESH")
        col.operator(SJOpenSceneFileDir.bl_idname, text="", icon="FILE_FOLDER")
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
        # if cls.__name__ in dir(bpy.types):
        bpy.utils.unregister_class(cls)
    # del bpy.types.Scene.sj_test_tools_props
