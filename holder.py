import bpy
import copy
from mathutils import Vector
from bpy.props import FloatProperty, IntProperty

bl_info = {
    'name': 'Tactile Universe model holder',
    'description': 'Make a holder for Tactile Universe models',
    'author': 'Coleman Krawczyk',
    'version': (2, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Add > Mesh > New Object',
    'category': 'Mesh',
}


class Holder(bpy.types.Operator):
    '''TU Model Holder'''

    bl_idname = 'object.holder'
    bl_label = 'Make a holder for Tactile Universe models'
    bl_options = {'REGISTER', 'UNDO'}
    class_counter = 0

    Number_slots: IntProperty(
        name='Number of slots',
        default=10,
        min=1,
        description='Number of slots the holder should have'
    )

    Width_slots: FloatProperty(
        name='Width of slots',
        default=20,
        min=1,
        unit='LENGTH',
        description='Width of the slots in the holder'
    )

    Height_models: FloatProperty(
        name='Height of models',
        default=132,
        min=1,
        unit='LENGTH',
        description='The height of the models to be held'
    )

    Length_models: FloatProperty(
        name='Length of models',
        default=112,
        min=1,
        unit='LENGTH',
        description='The length of the models to be held'
    )

    Thickness_slats: FloatProperty(
        name='Thickness of slot walls',
        default=2,
        min=1,
        unit='LENGTH',
        description='Thickness of slot walls'
    )

    Thickness_walls: FloatProperty(
        name='Thickness of outside walls',
        default=5,
        min=1,
        unit='LENGTH',
        description='Thickness of outside walls'
    )

    def __init__(self, *args, **kwargs):
        '''Define object names and update the class counter'''
        if self.class_counter == 0:
            self.name_ending = ''
        else:
            self.name_ending = '.{0:03d}'.format(Holder.class_counter)
        Holder.class_counter += 1
        super().__init__(*args, **kwargs)

    def remove_by_name(self, name):
        if name in bpy.data.objects.keys():
            obj = bpy.data.objects[name]
            obj.select_set(True)
            bpy.ops.object.delete()

    def make_rectangle(self, corner, size, name='rectangle'):
        name_in = copy.deepcopy(name)
        name = name_in + self.name_ending
        name_mesh = '{0}_mesh{1}'.format(name_in, self.name_ending)
        self.remove_by_name(name)
        x, y, z = corner
        x += self.location.x
        y += self.location.y
        z += self.location.z
        sx, sy, sz = size
        verts = [
            Vector((x,      y,      z)),
            Vector((x + sx, y,      z)),
            Vector((x + sx, y + sy, z)),
            Vector((x,      y + sy, z)),

            Vector((x,      y,      z + sz)),
            Vector((x + sx, y,      z + sz)),
            Vector((x + sx, y + sy, z + sz)),
            Vector((x,      y + sy, z + sz))
        ]
        faces = [
            (3, 2, 1, 0),
            (4, 5, 6, 7),
            (1, 2, 6, 5),
            (3, 0, 4, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6)
        ]
        me = bpy.data.meshes.new(name_mesh)
        rectangle = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(rectangle)
        me.from_pydata(verts, [], faces)
        me.update()
        rectangle.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        rectangle.select_set(False)
        return rectangle

    def make_diag(self, y='front', x='left', name='diag'):
        xf = 1
        if x == 'left':
            xf = -1
        yf = 1
        if y == 'front':
            yf = -1
        name_in = copy.deepcopy(name)
        name = name_in + self.name_ending
        name_mesh = '{0}_mesh{1}'.format(name_in, self.name_ending)
        self.remove_by_name(name)
        x = 0.5 * self.L * xf + self.location.x
        y1 = self.location.y
        y2 = 0.5 * self.W * yf + self.location.y
        z = self.location.z + 20
        sx = -self.Thickness_walls * xf
        sy = 20 * yf
        sz = self.H - 25
        verts = [
            Vector((x,      y1 + sy, z)),
            Vector((x + sx, y1 + sy, z)),
            Vector((x + sx, y1,      z)),
            Vector((x,      y1,      z)),

            Vector((x,      y2,      z + sz)),
            Vector((x + sx, y2,      z + sz)),
            Vector((x + sx, y2 - sy, z + sz)),
            Vector((x,      y2 - sy, z + sz))
        ]
        if xf == yf:
            faces = [
                (3, 2, 1, 0),
                (4, 5, 6, 7),
                (1, 2, 6, 5),
                (3, 0, 4, 7),
                (0, 1, 5, 4),
                (2, 3, 7, 6)
            ]
        else:
            faces = [
                (0, 1, 2, 3),
                (7, 6, 5, 4),
                (5, 6, 2, 1),
                (7, 4, 0, 3),
                (4, 5, 1, 0),
                (6, 7, 3, 2)
            ]
        me = bpy.data.meshes.new(name_mesh)
        diag = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(diag)
        me.from_pydata(verts, [], faces)
        me.update()
        diag.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        diag.select_set(False)
        return diag

    def execute(self, context):
        self.location = copy.deepcopy(bpy.context.scene.cursor.location)
        self.H = self.Height_models + self.Thickness_walls + 3
        self.W = self.Length_models + (2 * self.Thickness_walls) + 3
        self.L = self.Number_slots * (self.Width_slots + self.Thickness_slats) - self.Thickness_slats + 2 * self.Thickness_walls
        # Base rectangles
        self.base = []
        self.base.append(self.make_rectangle(
            [-0.5 * self.L, -0.5 * self.W, 0],
            [self.L, 20, self.Thickness_walls],
            name='base_1'
        ))
        self.base.append(self.make_rectangle(
            [-0.5 * self.L, (0.5 * self.W) - 20, 0],
            [self.L, 20, self.Thickness_walls],
            name='base_2'
        ))
        self.base.append(self.make_rectangle(
            [-0.5 * self.L, 5 - (0.5 * self.W), 0],
            [20, self.W - 10, self.Thickness_walls],
            name='base_3'
        ))
        self.base.append(self.make_rectangle(
            [(0.5 * self.L) - 20, 5 - (0.5 * self.W), 0],
            [20, self.W - 10, self.Thickness_walls],
            name='base_4'
        ))
        self.base.append(self.make_rectangle(
            [-0.5 * self.L, -10, 0],
            [self.L, 20, self.Thickness_walls],
            name='base_5'
        ))
        self.base.append(self.make_rectangle(
            [-10, -0.5 * self.W, 0],
            [20, self.W, self.Thickness_walls],
            name='base_6'
        ))
        # Lid rectangles
        self.lid = []
        lid_offset = self.W + 10
        self.lid.append(self.make_rectangle(
            [-0.5 * self.L, lid_offset - (0.5 * self.W), 0],
            [self.L, 20, self.Thickness_walls],
            name='lid_1'
        ))
        self.lid.append(self.make_rectangle(
            [-0.5 * self.L, lid_offset + (0.5 * self.W) - 20, 0],
            [self.L, 20, self.Thickness_walls],
            name='lid_2'
        ))
        self.lid.append(self.make_rectangle(
            [-0.5 * self.L, 5 + lid_offset - (0.5 * self.W), 0],
            [20, self.W - 10, self.Thickness_walls],
            name='lid_3'
        ))
        self.lid.append(self.make_rectangle(
            [(0.5 * self.L) - 20, 5 + lid_offset - (0.5 * self.W), 0],
            [20, self.W - 10, self.Thickness_walls],
            name='lid_4'
        ))
        self.lid.append(self.make_rectangle(
            [-0.5 * self.L, lid_offset - 10, 0],
            [self.L, 20, self.Thickness_walls],
            name='lid_5'
        ))
        self.lid.append(self.make_rectangle(
            [-10, lid_offset - (0.5 * self.W), 0],
            [20, self.W, self.Thickness_walls],
            name='lid_6'
        ))
        # Side rectangles
        base_bar_center = self.H / 3
        bar_center_1 = base_bar_center
        bar_center_2 = (2 * base_bar_center)
        self.front_side = []
        self.front_side.append(self.make_rectangle(
            [-0.5 * self.L, -0.5 * self.W, bar_center_1 - 10],
            [self.L, self.Thickness_walls, 20],
            name='front_side_1'
        ))
        self.front_side.append(self.make_rectangle(
            [-0.5 * self.L, -0.5 * self.W, bar_center_2 - 10],
            [self.L, self.Thickness_walls, 20],
            name='front_side_2'
        ))
        self.front_side.append(self.make_rectangle(
            [-0.5 * self.L, -0.5 * self.W, self.H - self.Thickness_walls],
            [self.L, self.Thickness_walls, self.Thickness_walls],
            name='front_side_3'
        ))
        self.back_side = []
        self.back_side.append(self.make_rectangle(
            [-0.5 * self.L, (0.5 * self.W) - self.Thickness_walls, bar_center_1 - 10],
            [self.L, self.Thickness_walls, 20],
            name='back_side_1'
        ))
        self.back_side.append(self.make_rectangle(
            [-0.5 * self.L, (0.5 * self.W) - self.Thickness_walls, bar_center_2 - 10],
            [self.L, self.Thickness_walls, 20],
            name='back_side_2'
        ))
        self.back_side.append(self.make_rectangle(
            [-0.5 * self.L, (0.5 * self.W) - self.Thickness_walls, self.H - self.Thickness_walls],
            [self.L, self.Thickness_walls, self.Thickness_walls],
            name='back_side_3'
        ))
        # Slats
        self.front_slats = []
        self.back_slats = []
        slat_center_base = (self.L - 2 * self.Thickness_walls) / (self.Number_slots)
        for i in range(1, self.Number_slots):
            slat_center = i * slat_center_base + self.Thickness_walls - (0.5 * self.L)
            self.front_slats.append(self.make_rectangle(
                [slat_center - self.Thickness_slats, -0.5 * self.W, self.Thickness_walls],
                [self.Thickness_slats, 20, self.H - self.Thickness_walls],
                name='front_slat_{0}'.format(i)
            ))
            self.back_slats.append(self.make_rectangle(
                [slat_center - self.Thickness_slats, (0.5 * self.W) - 20, self.Thickness_walls],
                [self.Thickness_slats, 20, self.H - self.Thickness_walls],
                name='back_slat_{0}'.format(i)
            ))
        # Faces
        self.left_face = []
        self.left_face.append(self.make_rectangle(
            [-0.5 * self.L, -0.5 * self.W, self.Thickness_walls],
            [self.Thickness_walls, self.W, (20 - self.Thickness_walls)],
            name='left_face_1'
        ))
        self.left_face.append(self.make_rectangle(
            [-0.5 * self.L, -0.5 * self.W, 20],
            [self.Thickness_walls, 20, self.H - 20],
            name='left_face_2'
        ))
        self.left_face.append(self.make_rectangle(
            [-0.5 * self.L, (0.5 * self.W) - 20, 20],
            [self.Thickness_walls, 20, self.H - 20],
            name='left_face_3'
        ))
        self.right_face = []
        self.right_face.append(self.make_rectangle(
            [(0.5 * self.L) - self.Thickness_walls, -0.5 * self.W, self.Thickness_walls],
            [self.Thickness_walls, self.W, (20 - self.Thickness_walls)],
            name='right_face_1'
        ))
        self.right_face.append(self.make_rectangle(
            [(0.5 * self.L) - self.Thickness_walls, -0.5 * self.W, 20],
            [self.Thickness_walls, 20, self.H - 20],
            name='right_face_2'
        ))
        self.right_face.append(self.make_rectangle(
            [(0.5 * self.L) - self.Thickness_walls, (0.5 * self.W) - 20, 20],
            [self.Thickness_walls, 20, self.H - 20],
            name='right_face_3'
        ))
        # Diags
        self.diag = []
        self.diag.append(self.make_diag(
            y='front',
            x='left',
            name='left_face_4'
        ))
        self.diag.append(self.make_diag(
            y='back',
            x='left',
            name='left_face_5'
        ))
        self.diag.append(self.make_diag(
            y='front',
            x='right',
            name='right_face_4'
        ))
        self.diag.append(self.make_diag(
            y='back',
            x='right',
            name='right_face_5'
        ))
        bpy.ops.object.select_all(action='TOGGLE')
        for lid_rectangle in self.lid:
            lid_rectangle.select_set(False)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        Holder.bl_idname,
        text=Holder.__doc__,
        icon='PLUGIN'
    )


def register():
    bpy.utils.register_class(Holder)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(Holder)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == '__main__':
    register()
