import bpy
import json
import sys
import os

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
config.setdefault('name_plate_keywords', {})
config.setdefault('stl_keywords', {})
config.setdefault('output_path', os.getcwd())
config.setdefault('output_name', 'output')

# create name plate
bpy.ops.object.name_plate(
    **config['name_plate_keywords']
)

base_path = os.path.join(
    config['output_path'],
    config['output_name']
)

stl_file_path = '{0}.stl'.format(base_path)
bpy.ops.export_mesh.stl(
    filepath=stl_file_path,
    check_existing=False,
    **config['stl_keywords']
)

bpy.ops.file.pack_all()
blend_file_path = '{0}.blend'.format(base_path)
bpy.ops.wm.save_mainfile(
    filepath=blend_file_path,
    check_existing=False
)
bpy.ops.wm.quit_blender()
