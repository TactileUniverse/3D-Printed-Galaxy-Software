import bpy
from mathutils import Vector
from bpy.props import FloatProperty, BoolProperty, StringProperty


class BackFrame(bpy.types.Operator):
    '''TU Back Frame'''

    bl_idname = 'object.back_frame'
    bl_label = 'Make a back frame for a Tactile Universe model'
    bl_options = {'REGISTER', 'UNDO'}

    Size_x: FloatProperty(
        name='Size X',
        default=112,
        min=0,
        unit='LENGTH',
        description='Size of frame in the X direction'
    )
    Size_y: FloatProperty(
        name='Size Y',
        default=112,
        min=0,
        unit='LENGTH',
        description='Size of frame in the Y direction'
    )
    Gap_size: FloatProperty(
        name='Gap Size',
        default=1,
        min=0,
        unit='LENGTH',
        description='Size of the gap between the frame and the model'
    )
    Border_width: FloatProperty(
        name='Border Width',
        default=3,
        min=0,
        unit='LENGTH',
        description='Width of fame border'
    )
    Close: BoolProperty(
        name='Close Frame',
        default=False,
        description='Close the frame on all sides'
    )
    Object_name: StringProperty(
        name='Base object name',
        default='BackFrame',
        description='Base name used for the frame object created'
    )

    def execute(self, context):
        x = [
            -0.5 * self.Size_x,
            (self.Border_width / 3) - (0.5 * self.Size_x),
            -(0.5 * self.Size_x) + self.Border_width,
            (0.5 * self.Size_x) - self.Border_width,
            (0.5 * self.Size_x) - (self.Border_width / 3),
            0.5 * self.Size_x
        ]
        y = [
            -0.5 * self.Size_y,
            (self.Border_width / 3) - (0.5 * self.Size_y),
            -(0.5 * self.Size_y) + self.Border_width,
            0.5 * self.Size_y
        ]
        z = [
            -self.Gap_size - 1,
            -self.Gap_size,
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

        if self.Close:
            for i in [1, 2, 9, 10]:
                verts[i][1] -= self.Border_width

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

        name_frame_object_key = '{0}Object'.format(self.Object_name)
        name_frame_mesh_key = '{0}Mesh'.format(self.Object_name)
        if name_frame_object_key in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name_frame_object_key], do_unlink=True)
        if name_frame_mesh_key in bpy.data.meshes.keys():
            bpy.data.meshes.remove(bpy.data.meshes[name_frame_mesh_key], do_unlink=True)
        me = bpy.data.meshes.new(name_frame_mesh_key)
        frame = bpy.data.objects.new(name_frame_object_key, me)
        bpy.context.scene.collection.objects.link(frame)
        me.from_pydata(verts, [], faces)
        me.update()
        frame.location += bpy.context.scene.cursor.location
        frame.rotation_euler.rotate(bpy.context.scene.cursor.rotation_euler)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        BackFrame.bl_idname,
        text=BackFrame.__doc__,
        icon='PLUGIN'
    )


def register():
    bpy.utils.register_class(BackFrame)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(BackFrame)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == '__main__':
    register()