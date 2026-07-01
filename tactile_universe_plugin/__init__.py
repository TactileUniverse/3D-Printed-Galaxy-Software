import bpy

from . import holder
from . import name_plate
from . import back_frame
from . import emboss_plane
from bpy.types import Menu

bl_info = {
    'name': 'Tactile Universe',
    'description': 'Various plugins for making Tactile Universe models',
    'author': 'Coleman Krawczyk',
    'version': (6, 0),
    'blender': (4, 0, 0),
    'location': 'View3D > Menu > Mesh Edit',
    'category': 'Mesh',
}



class VIEW3D_MT_add_tu(Menu):
    bl_idname = "VIEW3D_MT_add_tu"
    bl_label = "Tactile Universe"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.operator(
            holder.DefaultHolder.bl_idname,
            text=holder.DefaultHolder.__doc__,
            icon='PLUGIN'
        )
        layout.operator(
            name_plate.DefaultNamePlate.bl_idname,
            text=name_plate.DefaultNamePlate.__doc__,
            icon='PLUGIN'
        )
        layout.operator(
            back_frame.DefaultBackFrame.bl_idname,
            text=back_frame.DefaultBackFrame.__doc__,
            icon='PLUGIN'
        )


def add_menu_items(self, context):
    layout = self.layout
    layout.separator()
    layout.operator_context = "INVOKE_REGION_WIN"
    layout.menu(VIEW3D_MT_add_tu.bl_idname)



def register():
    holder.register()
    name_plate.register()
    back_frame.register()
    emboss_plane.register()
    bpy.utils.register_class(VIEW3D_MT_add_tu)
    bpy.types.VIEW3D_MT_mesh_add.append(add_menu_items)


def unregister():
    holder.unregister()
    name_plate.unregister()
    back_frame.unregister()
    emboss_plane.unregister()
    bpy.types.VIEW3D_MT_mesh_add.remove(add_menu_items)
    bpy.utils.unregister_class(VIEW3D_MT_add_tu)


if __name__ == '__main__':
    register()
