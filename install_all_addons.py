import bpy
import os

# get current directory
current_dir = os.getcwd()

# install and activate `emboss plane`
tu_plugin_filepath = os.path.join(current_dir, 'tactile_universe_plugin.zip')
bpy.ops.extensions.package_install_files(
    filepath=tu_plugin_filepath,
    repo='user_default',
    overwrite=True,
    enable_on_install=True
)

# save user preferences
bpy.ops.wm.save_userpref()
