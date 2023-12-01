# -*- coding: utf-8 -*-
import os
import subprocess
import bpy
import addon_utils

"""addon_utils
https://github.com/dfelinto/blender/blob/master/release/scripts/modules/addon_utils.py
"""


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


def _test():
    pass


def _my_addons_set_enable():
    # pref info
    preferences = bpy.context.preferences

    # addon list
    my_addons = ["sj_tests", "sj_util_tools", "sj_show_icon", "sj_set_bone_nator", "sj_selection_set", "sj_change_viewportdisplay_nator", "sj_phaser", "sj_delete_keyframe_by_interval", "sj_bioskin"]
    # current
    curt_addons = [addon.module for addon in preferences.addons]

    for addon_name in my_addons:
        if addon_name not in curt_addons:
            addon_utils.enable(addon_name, default_set=True)
        # else:
        #     addon_utils.disable(addon_name, default_set=True)
