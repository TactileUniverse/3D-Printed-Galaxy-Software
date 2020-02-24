import bpy
import os

# get current directory
current_dir = os.getcwd()

# install and activate `emboss plane`
tu_plugin_filepath = os.path.join(current_dir, 'tactile_universe_plugin.zip')
bpy.ops.preferences.addon_install(filepath=tu_plugin_filepath)
bpy.ops.preferences.addon_enable(module='tactile_universe_plugin')

# enable import images as plane
bpy.ops.preferences.addon_enable(module='io_import_images_as_planes')

# save user preferences
bpy.ops.wm.save_userpref()
