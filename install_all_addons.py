import bpy
import os

# get current directory
current_dir = os.getcwd()

# install and activate `emboss plane`
emboss_plane_filepath = os.path.join(current_dir, 'emboss_plane.py')
bpy.ops.wm.addon_install(filepath=emboss_plane_filepath)
bpy.ops.wm.addon_enable(module='emboss_plane')

# install and activate `name plate`
name_plate_filepath = os.path.join(current_dir, 'name_plate.py')
bpy.ops.wm.addon_install(filepath=name_plate_filepath)
bpy.ops.wm.addon_enable(module='name_plate')

# install and activate `holder`
holder_filepath = os.path.join(current_dir, 'holder.py')
bpy.ops.wm.addon_install(filepath=name_plate_filepath)
bpy.ops.wm.addon_enable(module='holder')

# enable import images as plane
bpy.ops.wm.addon_enable(module='io_import_images_as_planes')

# save user preferences
bpy.ops.wm.save_userpref()
