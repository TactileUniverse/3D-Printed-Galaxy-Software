import bpy
import json
import sys
import os

# argument checking
argv = sys.argv
if '--' not in argv:
    raise ValueError('You must pass a configuration file on the command line after ` -- `')

argv = argv[argv.index('--') + 1:]

if len(argv) == 0:
    raise ValueError('No configuration file passed in')
elif len(argv) > 1:
    raise ValueError('Only pass in one configuration file')

with open(argv[0]) as config_file:
    config = json.load(config_file)

# set defaults
config.setdefault('holder_keywords', {})
config.setdefault('output_path', os.getcwd())
config.setdefault('ouput_name', 'holder')

# make default object
bpy.ops.object.tu_holder()

# get the holder and lid
holder = bpy.data.objects['Holder']
lid = bpy.data.objects['Lid']

# apply vales from input config file
for k, v in config['holder_keywords'].items():
    setattr(holder.tu_holder_group, k, v)

base_path = os.path.join(
    config['output_path'],
    config['output_name']
)

# select only the holder
holder.select_set(True)
lid.select_set(False)
bpy.context.view_layer.objects.active = holder

# export as stl
stl_base_file_path = '{0}_base.stl'.format(base_path)
bpy.ops.wm.stl_export(
    filepath=stl_base_file_path,
    check_existing=False,
    export_selected_objects=True
)

# select only the lid
holder.select_set(False)
lid.select_set(True)
bpy.context.view_layer.objects.active = lid

# export as stl
stl_lid_file_path = '{0}_lid.stl'.format(base_path)
bpy.ops.wm.stl_export(
    filepath=stl_lid_file_path,
    check_existing=False,
    export_selected_objects=True
)

# select only the holder
holder.select_set(True)
lid.select_set(False)
bpy.context.view_layer.objects.active = holder

# save the blender file
bpy.ops.file.pack_all()
blend_file_path = '{0}.blend'.format(base_path)
bpy.ops.wm.save_mainfile(
    filepath=blend_file_path,
    check_existing=False
)
bpy.ops.wm.quit_blender()
