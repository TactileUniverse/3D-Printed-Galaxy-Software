import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from bpy.props import FloatProperty, BoolProperty, StringProperty
from bpy.types import Menu


def update_object_mesh(obj, me):
    old_me = obj.data
    me_name = old_me.name
    obj.data = me
    bpy.data.meshes.remove(old_me)
    obj.data.rename(me_name)


def build_name_plate_flat(props, context):
    if props.editing:
        return None
    
    props.editing = True
    x = [
        -0.5 * props.Size_x,
        0.5 * props.Size_x
    ]
    y = [
        0.5 * props.Size_y,
        -0.5 * props.Size_y
    ]
    z = [
        0.5 * props.Size_z,
        -0.5 * props.Size_z
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
    nameplate = props.id_data
    me = bpy.data.meshes.new(nameplate.data.name)
    me.from_pydata(verts, [], faces)
    me.update()
    update_object_mesh(nameplate, me)
    props.editing = False
    return None


def build_name_plate_notches(props, context):
    if props.editing:
        return None
    
    props.editing = True
    x = [
        -0.5 * props.Size_x,
        0.5 * props.Size_x,
        (0.25 * props.Size_x) - 1.75,
        (0.25 * props.Size_x) + 1.75,
        (0.25 * props.Size_x) - 3.5,
        (0.25 * props.Size_x) + 3.5,
        -(0.25 * props.Size_x) - 1.75,
        -(0.25 * props.Size_x) + 1.75,
        -(0.25 * props.Size_x) - 3.5,
        -(0.25 * props.Size_x) + 3.5
    ]
    y = [
        0.5 * props.Size_y,
        -0.5 * props.Size_y,
        (0.5 * props.Size_y) - (props.Border_width * 2 / 3)
    ]
    z = [
        0.5 * props.Size_z,
        -0.5 * props.Size_z,
        -(0.5 * props.Size_z) + props.Base_height
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

    nameplate = props.id_data
    # old_me = nameplate.data
    # me_name = old_me.name
    me = bpy.data.meshes.new(nameplate.data.name)
    me.from_pydata(verts, [], faces)
    me.update()
    update_object_mesh(nameplate, me)
    # nameplate.data = me
    # bpy.data.meshes.remove(old_me)
    # nameplate.data.rename(me_name)
    props.editing = False
    return None


def build_text(props, context):
    if props.editing:
        return None
    
    props.editing = True
    nameplate = props.id_data

    font_object = nameplate.children[0]
    font_curve = font_object.data
    font_curve.size = props.Text_size

    font_curve.body = props.Text
    font_curve.align_x = 'CENTER'
    font_curve.align_y = 'CENTER'
    font_object.location = Vector((
        0,
        0,
        (0.5 * props.Size_z)
    ))

    font_mesh_object = nameplate.children[1]
    update_object_mesh(font_mesh_object, font_object.to_mesh().copy())
    font_mesh_object.location = font_object.location

    props.editing = False
    return None


def build_name_plate(props, context):
    if props.editing:
        return None
    if props.Notches:
        build_name_plate_notches(props, context)
    else:
        build_name_plate_flat(props, context)
    build_text(props, context)
    return None


class NamePlatePropertyGroup(bpy.types.PropertyGroup):
    editing: BoolProperty(
        name="Editing",
        default=False
    )
    is_name_plate: BoolProperty(
        name="Is name plate",
        default=False,
        update=build_name_plate
    )
    Size_x: FloatProperty(
        # name='Size X',
        name='',
        default=112,
        min=0,
        unit='LENGTH',
        description='Size of name plate in the X direction',
        update=build_name_plate
    )
    Size_y: FloatProperty(
        # name='Size Y',
        name='',
        default=20,
        min=0,
        unit='LENGTH',
        description='Size of name plate in the Y direction',
        update=build_name_plate
    )
    Size_z: FloatProperty(
        # name='Size Z',
        name='',
        default=6,
        min=0,
        unit='LENGTH',
        description='Size of name plate in the Z direction',
        update=build_name_plate
    )
    Text: StringProperty(
        # name='Text',
        name='',
        default='Example',
        description='Text to put on the name plate',
        update=build_text
    )
    Text_size: FloatProperty(
        # name='Text size',
        name='',
        default=18,
        min=0,
        description='Size of the text',
        update=build_text
    )
    Notches: BoolProperty(
        # name='Notches',
        name='',
        default=False,
        description='Add notches to the name plate for attaching to the base model',
        update=build_name_plate
    )
    Base_height: FloatProperty(
        # name='Base height',
        name='',
        default=3,
        min=0,
        unit='LENGTH',
        description='This should match the "Base Thickness" value from Emboss Plane',
        update=build_name_plate
    )
    Border_width: FloatProperty(
        # name='Border width',
        name='',
        default=3,
        min=0,
        unit='LENGTH',
        description='This should match the "Border width" value from Emboss Plane',
        update=build_name_plate
    )


class NamePlatePanel(bpy.types.Panel):
    bl_label = "Name Plate Properties"
    bl_idname = "OBJECT_PT_edit_name_plate"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        def _tests():
            yield context.active_object is not None
            yield context.active_object.tu_name_plate_group.is_name_plate
            yield context.mode == "OBJECT"
        return all(_tests())

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        row = layout.row()
        row.label(text='Size X')
        row.prop(obj.tu_name_plate_group, 'Size_x')
        row = layout.row()
        row.label(text='Size Y')
        row.prop(obj.tu_name_plate_group, 'Size_y')
        row = layout.row()
        row.label(text='Size Z')
        row.prop(obj.tu_name_plate_group, 'Size_z')
        row = layout.row()
        row.label(text='Text')
        row.prop(obj.tu_name_plate_group, 'Text')
        row = layout.row()
        row.label(text='Text size')
        row.prop(obj.tu_name_plate_group, 'Text_size')
        row = layout.row()
        row.label(text='Notches')
        row.prop(obj.tu_name_plate_group, 'Notches')
        row = layout.row()
        row.label(text='Base height')
        row.prop(obj.tu_name_plate_group, 'Base_height')
        row = layout.row()
        row.label(text='Border width')
        row.prop(obj.tu_name_plate_group, 'Border_width')


class DefaultNamePlate(bpy.types.Operator):
    '''TU Name Plate'''
    bl_idname = 'object.tu_name_plate'
    bl_label = 'Make a name plate for Tactile Universe model'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # create a placeholder mesh for the object
        me = bpy.data.meshes.new('Name Plate Mesh')
        bm = bmesh.new()
        bmesh.ops.create_cube(bm)
        bm.to_mesh(me)
        bm.free()
        nameplate = bpy.data.objects.new(name='Name Plate', object_data=me)
        nameplate.matrix_world = context.scene.cursor.matrix
        
        font_curve = bpy.data.curves.new(type="FONT", name='Name Plate Font Curve')
        font_curve.extrude = 1
        font_object = bpy.data.objects.new('Name Plate Font Curve', font_curve)
        R = Matrix.Rotation(math.radians(180), 4, Vector((0, 0, 1)))
        font_object.rotation_euler.rotate(R)

        font_mesh = font_object.to_mesh()
        font_mesh_object = bpy.data.objects.new('Name Plate Font Object', font_mesh.copy())
        font_mesh_object.matrix_world = font_object.matrix_world
        font_mesh_object.rotation_euler.rotate(R)

        context.collection.objects.link(nameplate)
        context.collection.objects.link(font_object)
        context.collection.objects.link(font_mesh_object)

        font_object.hide_set(True)
        font_mesh_object.hide_set(True)

        font_object.parent = nameplate
        font_mesh_object.parent = nameplate

        nameplate.modifiers.new(type='BOOLEAN', name='text union')
        nameplate.modifiers['text union'].operation = 'UNION'
        nameplate.modifiers['text union'].object = font_mesh_object

        context.view_layer.objects.active = nameplate
        nameplate.tu_name_plate_group.is_name_plate = True
        return {'FINISHED'}
    

def add_object_button(self, context):
    self.layout.operator(
        DefaultNamePlate.bl_idname,
        text=DefaultNamePlate.__doc__,
        icon='PLUGIN'
    )


def register():
    bpy.utils.register_class(NamePlatePanel)
    bpy.utils.register_class(NamePlatePropertyGroup)
    bpy.utils.register_class(DefaultNamePlate)
    setattr(
        bpy.types.Object,
        'tu_name_plate_group',
        bpy.props.PointerProperty(type=NamePlatePropertyGroup)
    )


def unregister():
    bpy.utils.unregister_class(NamePlatePanel)
    bpy.utils.unregister_class(NamePlatePropertyGroup)
    bpy.utils.unregister_class(DefaultNamePlate)
    delattr(
        bpy.types.Object,
        'tu_name_plate_group'
    )


if __name__ == '__main__':
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    register()
