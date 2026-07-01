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

if 'input_file_path' not in config:
    raise ValueError('the config file must contain the keyword `input_file_path`')

# set defaults
config.setdefault('plane_height', 112)
config.setdefault('emboss_plane_keywords', {})
config.setdefault('output_path', os.getcwd())
config.setdefault('output_name', 'output')
config.setdefault('stl_keywords', {})

input_name = os.path.basename(config['input_file_path'])
input_dir = os.path.dirname(config['input_file_path'])

if input_dir == '':
    input_dir = os.getcwd()

# import image as plane
bpy.ops.image.import_as_mesh_planes(
    files=[{'name': input_name}],
    directory=input_dir,
    height=config['plane_height'],
    relative=False
)

# there is only one object, select it
plane = bpy.data.objects[0]
plane.select_set(True)
bpy.context.view_layer.objects.active = plane

# emboss plane
bpy.ops.object.tu_emboss_plane()

# apply vales from input config file
for k, v in config['emboss_plane_keywords'].items():
    setattr(plane.tu_emboss_plane_group, k, v)

base_path = os.path.join(
    config['output_path'],
    config['output_name']
)

# save the blender file
bpy.ops.file.pack_all()
blend_file_path = '{0}.blend'.format(base_path)
bpy.ops.wm.save_mainfile(
    filepath=blend_file_path,
    check_existing=False
)

# export as stl
stl_file_path = '{0}.stl'.format(base_path)
bpy.ops.wm.stl_export(
    filepath=stl_file_path,
    check_existing=False,
    **config['stl_keywords']
)

bpy.ops.wm.quit_blender()
