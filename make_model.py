import bpy
import bmesh
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


def view3d_find(return_area=False):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area:
                        return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None


region, rv3d, v3d, area = view3d_find(True)
override = {
    'scene': bpy.context.scene,
    'screen': bpy.context.screen,
    'active_object': bpy.context.active_object,
    'window': bpy.context.window,
    'blend_data': bpy.context.blend_data,
    'region': region,
    'area': area,
    'space': v3d
}

name = bpy.context.active_object.name
bpy.ops.object.editmode_toggle()
with bpy.context.temp_override(**override):
    bpy.ops.object.emboss_plane(**config['emboss_plane_keywords'])
bpy.ops.object.editmode_toggle()

base_path = os.path.join(
    config['output_path'],
    config['output_name']
)

bpy.ops.file.pack_all()
blend_file_path = '{0}.blend'.format(base_path)
bpy.ops.wm.save_mainfile(
    filepath=blend_file_path,
    check_existing=False
)

stl_file_path = '{0}.stl'.format(base_path)
bpy.ops.wm.stl_export(
    filepath=stl_file_path,
    check_existing=False,
    **config['stl_keywords']
)

bpy.ops.wm.quit_blender()
