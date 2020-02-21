import bpy
import copy
import math
from mathutils import Vector, Matrix
from bpy.props import FloatProperty, BoolProperty, StringProperty

bl_info = {
    'name': 'Tactile Universe Name plate',
    'description': 'Make a name plate for Tactile Universe model',
    'author': 'Coleman Krawczyk',
    'version': (1, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Add > Mesh > New Object',
    'category': 'Mesh',
}


class NamePlate(bpy.types.Operator):
    '''Name Plate'''

    bl_idname = 'object.name_plate'
    bl_label = 'Make a name plate for Tactile Universe model'
    bl_options = {'REGISTER', 'UNDO'}
    class_counter = 0

    Size_x: FloatProperty(
        name='Size X',
        default=112,
        min=0,
        unit='LENGTH',
        description='Size of name plate in the X direction'
    )
    Size_y: FloatProperty(
        name='Size Y',
        default=20,
        min=0,
        unit='LENGTH',
        description='Size of name plate in the Y direction'
    )
    Size_z: FloatProperty(
        name='Size Z',
        default=6,
        min=0,
        unit='LENGTH',
        description='Size of name plate in the Z direction'
    )
    Text: StringProperty(
        name='Text',
        default='Example',
        description='Text to put on the name plate'
    )
    Text_size: FloatProperty(
        name='Text size',
        default=18,
        min=0,
        description='Size of the text'
    )
    Notches: BoolProperty(
        name='Notches',
        default=False,
        description='Add notches to the name plate for attaching to the base model'
    )
    Base_height: FloatProperty(
        name='Base height',
        default=3,
        min=0,
        unit='LENGTH',
        description='This should match the "Base Thickness" value from Emboss Plane'
    )
    Border_width: FloatProperty(
        name='Border width',
        default=3,
        min=0,
        unit='LENGTH',
        description='This should match the "Border width" value from Emboss Plane'
    )
    Object_name: StringProperty(
        name='Base object name',
        default='NamePlate',
        description='Base name used for the name plate objects created'
    )

    def remove_name_plate(self):
        if self.name_plate_object_key in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[self.name_plate_object_key], do_unlink=True)
        if self.name_plate_mesh_key in bpy.data.meshes.keys():
            bpy.data.meshes.remove(bpy.data.meshes[self.name_plate_mesh_key], do_unlink=True)

    def remove_text(self):
        if self.text_object_key in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[self.text_object_key], do_unlink=True)
        if self.text_cure_key in bpy.data.curves.keys():
            bpy.data.curves.remove(bpy.data.curves[self.text_cure_key], do_unlink=True)

    def make_name_plate_flat(self):
        self.remove_name_plate()
        x = [
            -0.5 * self.Size_x,
            0.5 * self.Size_x
        ]
        y = [
            0.5 * self.Size_y,
            -0.5 * self.Size_y
        ]
        z = [
            0.5 * self.Size_z,
            -0.5 * self.Size_z
        ]
        verts = [
            Vector((x[0], y[0], z[0])),
            Vector((x[1], y[0], z[0])),
            Vector((x[1], y[1], z[0])),
            Vector((x[0], y[1], z[0])),

            Vector((x[0], y[0], z[1])),
            Vector((x[1], y[0], z[1])),
            Vector((x[1], y[1], z[1])),
            Vector((x[0], y[1], z[1])),
        ]
        faces = [
            (3, 2, 1, 0),
            (4, 5, 6, 7),
            (1, 2, 6, 5),
            (3, 0, 4, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6)
        ]
        me = bpy.data.meshes.new(self.name_plate_mesh_key)
        self.name_plate = bpy.data.objects.new(self.name_plate_object_key, me)
        bpy.context.scene.collection.objects.link(self.name_plate)
        me.from_pydata(verts, [], faces)
        me.update()

    def make_name_plate_notches(self):
        self.remove_name_plate()
        x = [
            -0.5 * self.Size_x,
            0.5 * self.Size_x,
            (0.25 * self.Size_x) - 1.75,
            (0.25 * self.Size_x) + 1.75,
            (0.25 * self.Size_x) - 3.5,
            (0.25 * self.Size_x) + 3.5,
            -(0.25 * self.Size_x) - 1.75,
            -(0.25 * self.Size_x) + 1.75,
            -(0.25 * self.Size_x) - 3.5,
            -(0.25 * self.Size_x) + 3.5
        ]
        y = [
            0.5 * self.Size_y,
            -0.5 * self.Size_y,
            (0.5 * self.Size_y) - (self.Border_width * 2 / 3)
        ]
        z = [
            0.5 * self.Size_z,
            -0.5 * self.Size_z,
            -(0.5 * self.Size_z) + self.Base_height
        ]
        verts = [
            Vector((x[0], y[0], z[0])),
            Vector((x[1], y[0], z[0])),
            Vector((x[1], y[1], z[0])),
            Vector((x[0], y[1], z[0])),

            Vector((x[0], y[0], z[1])),
            Vector((x[1], y[0], z[1])),
            Vector((x[1], y[1], z[1])),
            Vector((x[0], y[1], z[1])),

            Vector((x[2], y[0], z[1])),
            Vector((x[3], y[0], z[1])),
            Vector((x[3], y[2], z[1])),
            Vector((x[2], y[2], z[1])),

            Vector((x[4], y[0], z[2])),
            Vector((x[5], y[0], z[2])),
            Vector((x[5], y[2], z[2])),
            Vector((x[4], y[2], z[2])),

            Vector((x[6], y[0], z[1])),
            Vector((x[7], y[0], z[1])),
            Vector((x[7], y[2], z[1])),
            Vector((x[6], y[2], z[1])),

            Vector((x[8], y[0], z[2])),
            Vector((x[9], y[0], z[2])),
            Vector((x[9], y[2], z[2])),
            Vector((x[8], y[2], z[2])),
        ]
        faces = [
            (3, 2, 1, 0),
            (4, 7, 3, 0),
            (1, 2, 6, 5),
            (7, 6, 2, 3),
            (12, 13, 14, 15),
            (9, 10, 14, 13),
            (12, 15, 11, 8),
            (15, 14, 10, 11),
            (20, 21, 22, 23),
            (17, 18, 22, 21),
            (20, 23, 19, 16),
            (23, 22, 18, 19),
            (4, 16, 19, 18, 17, 8, 11, 10, 9, 5, 6, 7),
            (0, 1, 5, 9, 13, 12, 8, 17, 21, 20, 16, 4)
        ]
        me = bpy.data.meshes.new(self.name_plate_mesh_key)
        self.name_plate = bpy.data.objects.new(self.name_plate_object_key, me)
        bpy.context.scene.collection.objects.link(self.name_plate)
        me.from_pydata(verts, [], faces)
        me.update()
        R = Matrix.Rotation(math.radians(180), 4, Vector((0, 0, 1)))
        self.name_plate.rotation_euler.rotate(R)

    def make_font(self):
        self.remove_text()
        self.font_curve = bpy.data.curves.new(type="FONT", name=self.text_cure_key)
        self.font_curve.extrude = 1
        self.font_object = bpy.data.objects.new(self.text_object_key, self.font_curve)
        bpy.context.scene.collection.objects.link(self.font_object)
        self.font_curve.size = self.Text_size
        self.font_object.data.body = self.Text
        self.font_object.data.align_x = 'CENTER'
        self.font_object.data.align_y = 'CENTER'
        self.font_object.location = Vector((
            0,
            0,
            (0.5 * self.Size_z)
        ))

    def execute(self, context):
        self.name_plate_object_key = '{0}Plate'.format(self.Object_name)
        self.name_plate_mesh_key = '{0}Mesh'.format(self.Object_name)
        self.text_cure_key = '{0}FontCurve'.format(self.Object_name)
        self.text_object_key = '{0}FontObject'.format(self.Object_name)
        if self.Notches:
            self.make_name_plate_notches()
        else:
            self.make_name_plate_flat()
        self.make_font()
        self.name_plate.location += bpy.context.scene.cursor.location
        self.name_plate.rotation_euler.rotate(bpy.context.scene.cursor.rotation_euler)
        self.font_object.location += bpy.context.scene.cursor.location
        self.font_object.rotation_euler.rotate(bpy.context.scene.cursor.rotation_euler)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        NamePlate.bl_idname,
        text=NamePlate.__doc__,
        icon='PLUGIN'
    )


def register():
    bpy.utils.register_class(NamePlate)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(NamePlate)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == '__main__':
    register()
