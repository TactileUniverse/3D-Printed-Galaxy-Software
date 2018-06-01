import bpy

# install and activate `emboss plane`
bpy.ops.wm.addon_install(filepath='emboss_plane.py')
bpy.ops.wm.addon_enable(module='emboss_plane')

# install and activate `name plate`
bpy.ops.wm.addon_install(filepath='name_plate.py')
bpy.ops.wm.addon_enable(module='name_plate')

# save user preferences
bpy.ops.wm.save_userpref()
