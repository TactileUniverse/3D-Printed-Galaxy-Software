from . import holder
from . import name_plate
from . import back_frame
from . import emboss_plane

bl_info = {
    'name': 'Tactile Universe',
    'description': 'Various plugins for making Tactile Universe models',
    'author': 'Coleman Krawczyk',
    'version': (5, 0),
    'blender': (4, 0, 0),
    'location': 'View3D > Menu > Mesh Edit',
    'category': 'Mesh',
}


def register():
    holder.register()
    name_plate.register()
    back_frame.register()
    emboss_plane.register()


def unregister():
    holder.unregister()
    name_plate.unregister()
    back_frame.unregister()
    emboss_plane.unregister()


if __name__ == '__main__':
    register()
