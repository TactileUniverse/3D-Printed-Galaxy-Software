import bpy
import bmesh
from mathutils import Vector
from bpy.props import FloatProperty, BoolProperty


def build_back_frame(props, context):
    if props.editing:
        return None
    
    props.editing = True
    x = [
        -0.5 * props.Size_x,
        (props.Border_width / 3) - (0.5 * props.Size_x),
        -(0.5 * props.Size_x) + props.Border_width,
        (0.5 * props.Size_x) - props.Border_width,
        (0.5 * props.Size_x) - (props.Border_width / 3),
        0.5 * props.Size_x
    ]
    y = [
        -0.5 * props.Size_y,
        (props.Border_width / 3) - (0.5 * props.Size_y),
        -(0.5 * props.Size_y) + props.Border_width,
        0.5 * props.Size_y
    ]
    z = [
        -props.Gap_size - 1,
        -props.Gap_size,
        1
    ]
    verts = [
        Vector((x[0], y[3], z[0])),
        Vector((x[2], y[3], z[0])),
        Vector((x[3], y[3], z[0])),
        Vector((x[5], y[3], z[0])),
        Vector((x[0], y[0], z[0])),
        Vector((x[2], y[2], z[0])),
        Vector((x[3], y[2], z[0])),
        Vector((x[5], y[0], z[0])),

        Vector((x[1], y[3], z[1])),
        Vector((x[2], y[3], z[1])),
        Vector((x[3], y[3], z[1])),
        Vector((x[4], y[3], z[1])),
        Vector((x[1], y[1], z[1])),
        Vector((x[2], y[2], z[1])),
        Vector((x[3], y[2], z[1])),
        Vector((x[4], y[1], z[1])),

        Vector((x[0], y[3], z[2])),
        Vector((x[1], y[3], z[2])),
        Vector((x[4], y[3], z[2])),
        Vector((x[5], y[3], z[2])),
        Vector((x[0], y[0], z[2])),
        Vector((x[1], y[1], z[2])),
        Vector((x[4], y[1], z[2])),
        Vector((x[5], y[0], z[2])),
    ]
    faces = [
        (2, 3, 7, 6),
        (6, 7, 4, 5),
        (0, 1, 5, 4),

        (11, 10, 14, 15),
        (13, 12, 15, 14),
        (12, 13, 9, 8),

        (19, 18, 22, 23),
        (21, 20, 23, 22),
        (20, 21, 17, 16),

        (0, 4, 20, 16),
        (4, 7, 23, 20),
        (7, 3, 19, 23),

        (14, 10, 2, 6),
        (13, 14, 6, 5),
        (9, 13, 5, 1),

        (17, 21, 12, 8),
        (21, 22, 15, 12),
        (22, 18, 11, 15)
    ]

    if props.Close:
        for i in [1, 2, 9, 10]:
            verts[i][1] -= props.Border_width

        for i in [8, 11, 17, 18]:
            verts[i][1] -= 1

        faces.append((0, 3, 2, 1))
        faces.append((11, 8, 9, 10))
        faces.append((19, 16, 17, 18))

        faces.append((3, 0, 16, 19))
        faces.append((10, 9, 1, 2))
        faces.append((18, 17, 8, 11))
    else:
        faces.append((3, 2, 10, 11, 18, 19))
        faces.append((1, 0, 16, 17, 8, 9))

    frame = props.id_data
    old_me = frame.data
    me_name = old_me.name
    me = bpy.data.meshes.new(me_name)
    me.from_pydata(verts, [], faces)
    me.update()
    frame.data = me
    bpy.data.meshes.remove(old_me)
    frame.data.rename(me_name)
    props.editing = False
    return None


class DefaultBackFrame(bpy.types.Operator):
    '''TU Back Frame'''
    bl_idname = 'object.tu_back_frame'
    bl_label = 'Make a back frame for a Tactile Universe model'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # create a placeholder mesh for the object
        me = bpy.data.meshes.new('Back Frame Mesh')
        bm = bmesh.new()
        bmesh.ops.create_cube(bm)
        bm.to_mesh(me)
        bm.free()
        # create new object
        frame = bpy.data.objects.new(name='Back Frame', object_data=me)
        frame.matrix_world = context.scene.cursor.matrix
        context.collection.objects.link(frame)
        # set as active
        context.view_layer.objects.active = frame
        # object properties to indicate this is a back frame
        # updating this will trigger `build_back_frame` as a callback
        # and replace the placeholder mesh with a default frame
        frame.tu_back_frame_group.is_frame = True
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        DefaultBackFrame.bl_idname,
        text=DefaultBackFrame.__doc__,
        icon='PLUGIN'
    )


class BackFramePropertyGroup(bpy.types.PropertyGroup):
    editing: BoolProperty(
        name="Editing",
        default=False
    )
    is_frame: BoolProperty(
        name="Is frame",
        default=False,
        update=build_back_frame
    )
    Size_x: FloatProperty(
        # name='Size X',
        name='',
        default=112,
        min=0,
        unit='LENGTH',
        description='Size of frame in the X direction',
        update=build_back_frame
    )
    Size_y: FloatProperty(
        # name='Size Y',
        name='',
        default=112,
        min=0,
        unit='LENGTH',
        description='Size of frame in the Y direction',
        update=build_back_frame
    )
    Gap_size: FloatProperty(
        # name='Gap Size',
        name='',
        default=1,
        min=0,
        unit='LENGTH',
        description='Size of the gap between the frame and the model',
        update=build_back_frame
    )
    Border_width: FloatProperty(
        # name='Border Width',
        name='',
        default=3,
        min=0,
        unit='LENGTH',
        description='Width of fame border',
        update=build_back_frame
    )
    Close: BoolProperty(
        # name='Close Frame',
        name='',
        default=False,
        description='Close the frame on all sides',
        update=build_back_frame
    )


class BackFramePanel(bpy.types.Panel):
    bl_label = "Back Frame Properties"
    bl_idname = "OBJECT_PT_edit_back_frame"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        def _tests():
            yield context.active_object is not None
            yield context.active_object.tu_back_frame_group.is_frame
            yield context.mode == "OBJECT"
        return all(_tests())

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        row = layout.row()
        row.label(text='Size X')
        row.prop(obj.tu_back_frame_group, 'Size_x')
        row = layout.row()
        row.label(text='Size Y')
        row.prop(obj.tu_back_frame_group, 'Size_y')
        row = layout.row()
        row.label(text='Gap size')
        row.prop(obj.tu_back_frame_group, 'Gap_size')
        row = layout.row()
        row.label(text='Border width')
        row.prop(obj.tu_back_frame_group, 'Border_width')
        row = layout.row()
        row.label(text='Close')
        row.prop(obj.tu_back_frame_group, 'Close')


def register():
    bpy.utils.register_class(BackFramePanel)
    bpy.utils.register_class(BackFramePropertyGroup)
    bpy.utils.register_class(DefaultBackFrame)
    setattr(
        bpy.types.Object,
        'tu_back_frame_group',
        bpy.props.PointerProperty(type=BackFramePropertyGroup)
    )
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(BackFramePanel)
    bpy.utils.unregister_class(BackFramePropertyGroup)
    bpy.utils.unregister_class(DefaultBackFrame)
    delattr(
        bpy.types.Object,
        'tu_back_frame_group'
    )
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == '__main__':
    register()
