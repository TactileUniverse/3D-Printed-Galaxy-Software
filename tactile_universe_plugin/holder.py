import bpy
import bmesh
from mathutils import Vector
from bpy.props import FloatProperty, BoolProperty, IntProperty, StringProperty


def update_object(obj, verts, edges, faces):
    old_me = obj.data
    me_name = old_me.name
    me = bpy.data.meshes.new(me_name)
    me.from_pydata(verts, edges, faces)
    me.update()
    obj.data = me
    bpy.data.meshes.remove(old_me)
    obj.data.rename(me_name)


def build_rectangle(corner, size, obj):
    x, y, z = corner
    sx, sy, sz = size
    verts = [
        Vector((x, y, z)),
        Vector((x + sx, y, z)),
        Vector((x + sx, y + sy, z)),
        Vector((x, y + sy, z)),

        Vector((x, y, z + sz)),
        Vector((x + sx, y, z + sz)),
        Vector((x + sx, y + sy, z + sz)),
        Vector((x, y + sy, z + sz))
    ]
    faces = [
        (3, 2, 1, 0),
        (4, 5, 6, 7),
        (1, 2, 6, 5),
        (3, 0, 4, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6)
    ]
    update_object(obj, verts, [], faces)


def build_diag(H, W, L, props, obj, y='front', x='left'):
    xf = 1
    if x == 'left':
        xf = -1
    yf = 1
    if y == 'front':
        yf = -1
    x = 0.5 * L * xf
    y1 = 0.0
    y2 = 0.5 * W * yf 
    z = 20
    sx = -props.Thickness_walls * xf
    sy = 20 * yf
    sz = H - 25
    verts = [
        Vector((x, y1 + sy, z)),
        Vector((x + sx, y1 + sy, z)),
        Vector((x + sx, y1, z)),
        Vector((x, y1, z)),

        Vector((x, y2, z + sz)),
        Vector((x + sx, y2, z + sz)),
        Vector((x + sx, y2 - sy, z + sz)),
        Vector((x, y2 - sy, z + sz))
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
    update_object(obj, verts, [], faces)


def build_holder(props, context):
    if props.editing:
        return None

    props.editing = True
    holder = props.id_data
    lid = [c for c in holder.children if c.name.startswith('Lid')][0]

    H = props.Height_models + props.Thickness_walls + 3
    W = props.Length_models + (2 * props.Thickness_walls) + 3
    L = props.Number_slots * (props.Width_slots + props.Thickness_slats) - props.Thickness_slats + 2 * props.Thickness_walls
    
    lid_offset = W + 10
    base_bar_center = H / 3
    bar_center_1 = base_bar_center
    bar_center_2 = (2 * base_bar_center)

    # base center
    build_rectangle(
        [-10, -0.5 * W, 0],
        [20, W, props.Thickness_walls],
        holder
    )

    # lid center
    build_rectangle(
        [-10, lid_offset - (0.5 * W), 0],
        [20, W, props.Thickness_walls],
        lid
    )

    corners_lid = [
        # lid
        [-0.5 * L, lid_offset - (0.5 * W), 0],
        [-0.5 * L, lid_offset + (0.5 * W) - 20, 0],
        [-0.5 * L, 5 + lid_offset - (0.5 * W), 0],
        [(0.5 * L) - 20, 5 + lid_offset - (0.5 * W), 0],
        [-0.5 * L, lid_offset - 10, 0]
    ]

    sizes_lid = [
        # lid
        [L, 20, props.Thickness_walls],
        [L, 20, props.Thickness_walls],
        [20, W - 10, props.Thickness_walls],
        [20, W - 10, props.Thickness_walls],
        [L, 20, props.Thickness_walls]
    ]

    for child, corner, size in zip(lid.children, corners_lid, sizes_lid):
        build_rectangle(
            corner,
            size,
            child
        )

    corners = [
        # base
        [-0.5 * L, -0.5 * W, 0],
        [-0.5 * L, (0.5 * W) - 20, 0],
        [-0.5 * L, 5 - (0.5 * W), 0],
        [(0.5 * L) - 20, 5 - (0.5 * W), 0],
        [-0.5 * L, -10, 0],
        # front and back sides
        [-0.5 * L, -0.5 * W, bar_center_1 - 10],
        [-0.5 * L, (0.5 * W) - props.Thickness_walls, bar_center_1 - 10],
        [-0.5 * L, -0.5 * W, bar_center_2 - 10],
        [-0.5 * L, (0.5 * W) - props.Thickness_walls, bar_center_2 - 10],
        [-0.5 * L, -0.5 * W, H - props.Thickness_walls],
        [-0.5 * L, (0.5 * W) - props.Thickness_walls, H - props.Thickness_walls],
        # # right and left sides
        [(0.5 * L) - props.Thickness_walls, -0.5 * W, props.Thickness_walls],
        [-0.5 * L, -0.5 * W, props.Thickness_walls],
        [(0.5 * L) - props.Thickness_walls, -0.5 * W, 20],
        [-0.5 * L, -0.5 * W, 20],
        [(0.5 * L) - props.Thickness_walls, (0.5 * W) - 20, 20],
        [-0.5 * L, (0.5 * W) - 20, 20],
    ]

    sizes = [
        # base
        [L, 20, props.Thickness_walls],
        [L, 20, props.Thickness_walls],
        [20, W - 10, props.Thickness_walls],
        [20, W - 10, props.Thickness_walls],
        [L, 20, props.Thickness_walls],
        # front and back sides
        [L, props.Thickness_walls, 20],
        [L, props.Thickness_walls, 20],
        [L, props.Thickness_walls, 20],
        [L, props.Thickness_walls, 20],
        [L, props.Thickness_walls, props.Thickness_walls],
        [L, props.Thickness_walls, props.Thickness_walls],
        # # right and left sides
        [props.Thickness_walls, W, (20 - props.Thickness_walls)],
        [props.Thickness_walls, W, (20 - props.Thickness_walls)],
        [props.Thickness_walls, 20, H - 20],
        [props.Thickness_walls, 20, H - 20],
        [props.Thickness_walls, 20, H - 20],
        [props.Thickness_walls, 20, H - 20],
    ]

    holder_parts = [c for c in holder.children if c.name.startswith('Holder')]
    for child, corner, size in zip(holder_parts[:-5], corners, sizes):
        build_rectangle(
            corner,
            size,
            child
        )

    build_diag(H, W, L, props, holder_parts[-5], y='front', x='right')
    build_diag(H, W, L, props, holder_parts[-4], y='front', x='left')
    build_diag(H, W, L, props, holder_parts[-3], y='back', x='right')
    build_diag(H, W, L, props, holder_parts[-2], y='back', x='left')

    slat = holder_parts[-1]
    slat_center_base = (L - 2 * props.Thickness_walls) / (props.Number_slots) - props.Thickness_slats * (1 - 1 / props.Number_slots)
    slat_center = slat_center_base + props.Thickness_walls - (0.5 * L)    
    build_rectangle(
        [slat_center, -0.5 * W, props.Thickness_walls],
        [props.Thickness_slats, 20, H - props.Thickness_walls],
        slat
    )
    array_x = slat_center_base / props.Thickness_slats + 1
    slat.modifiers['slats x'].count = props.Number_slots - 1
    slat.modifiers['slats x'].relative_offset_displace[0] = array_x
    slat.modifiers['slats x'].relative_offset_displace[1] = 0
    slat.modifiers['slats x'].relative_offset_displace[2] = 0

    array_y = W / 20 - 1
    slat.modifiers['slats y'].count = 2
    slat.modifiers['slats y'].relative_offset_displace[0] = 0
    slat.modifiers['slats y'].relative_offset_displace[1] = array_y
    slat.modifiers['slats y'].relative_offset_displace[2] = 0

    props.editing = False
    return None


class HolderPropertyGroup(bpy.types.PropertyGroup):
    editing: BoolProperty(
        name="Editing",
        default=False
    )
    is_holder: BoolProperty(
        name="Is holder",
        default=False,
        update=build_holder
    )
    holder_collection_name: StringProperty(
        name='Holder collection name',
        default='Holder'
    )
    holder_lid_collection_name: StringProperty(
        name='Holder lid collection name',
        default='Holder lid'
    )
    Number_slots: IntProperty(
        # name='Number of slots',
        name='',
        default=10,
        min=1,
        description='Number of slots the holder should have',
        update=build_holder
    )
    Width_slots: FloatProperty(
        # name='Width of slots',
        name='',
        default=20,
        min=1,
        unit='LENGTH',
        description='Width of the slots in the holder',
        update=build_holder
    )
    Height_models: FloatProperty(
        # name='Height of models',
        name='',
        default=132,
        min=1,
        unit='LENGTH',
        description='The height of the models to be held',
        update=build_holder
    )
    Length_models: FloatProperty(
        # name='Length of models',
        name='',
        default=112,
        min=1,
        unit='LENGTH',
        description='The length of the models to be held',
        update=build_holder
    )
    Thickness_slats: FloatProperty(
        # name='Thickness of slot walls',
        name='',
        default=2,
        min=1,
        unit='LENGTH',
        description='Thickness of slot walls',
        update=build_holder
    )
    Thickness_walls: FloatProperty(
        # name='Thickness of outside walls',
        name='',
        default=5,
        min=1,
        unit='LENGTH',
        description='Thickness of outside walls',
        update=build_holder
    )


class HolderPanel(bpy.types.Panel):
    bl_label = "Holder Properties"
    bl_idname = "OBJECT_PT_holder"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        def _tests():
            yield context.active_object is not None
            yield context.active_object.tu_holder_group.is_holder
            yield context.mode == "OBJECT"
        return all(_tests())
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        row = layout.row()
        row.label(text='Number of slots')
        row.prop(obj.tu_holder_group, 'Number_slots')
        row = layout.row()
        row.label(text='Width of slots')
        row.prop(obj.tu_holder_group, 'Width_slots')
        row = layout.row()
        row.label(text='Height of models')
        row.prop(obj.tu_holder_group, 'Height_models')
        row = layout.row()
        row.label(text='Length of models')
        row.prop(obj.tu_holder_group, 'Length_models')
        row = layout.row()
        row.label(text='Thickness of slot walls')
        row.prop(obj.tu_holder_group, 'Thickness_slats')
        row = layout.row()
        row.label(text='Thickness of outside walls')
        row.prop(obj.tu_holder_group, 'Thickness_walls')


def default_object(name):
    me = bpy.data.meshes.new(f'{name} Mesh')
    bm = bmesh.new()
    bmesh.ops.create_cube(bm)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name=name, object_data=me)


class DefaultHolder(bpy.types.Operator):
    '''TU Holder'''
    bl_idname = 'object.tu_holder'
    bl_label = 'Make a holder for Tactile Universe models'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # make new collection for holder
        # make new collection for lid

        holder_collection = bpy.data.collections.new('Holder')
        context.scene.collection.children.link(holder_collection)

        lid_collection = bpy.data.collections.new('Lid')
        context.scene.collection.children.link(lid_collection)

        holder = default_object('Holder')
        holder.matrix_world = context.scene.cursor.matrix
        holder_collection.objects.link(holder)
        context.view_layer.objects.active = holder
        # add bool union for new collection
        holder.modifiers.new(type='BOOLEAN', name='holder union')
        holder.modifiers['holder union'].operand_type = 'COLLECTION'
        holder.modifiers['holder union'].collection = holder_collection
        holder.modifiers['holder union'].operation = 'UNION'

        lid = default_object('Lid')
        # lid.matrix_world = context.scene.cursor.matrix
        lid_collection.objects.link(lid)
        lid.parent = holder
        lid.modifiers.new(type='BOOLEAN', name='lid union')
        lid.modifiers['lid union'].operand_type = 'COLLECTION'
        lid.modifiers['lid union'].collection = lid_collection
        lid.modifiers['lid union'].operation = 'UNION'

        # add children
        for i in range(22):
            base_i = default_object(f'Holder part {i:02d}')
            # add to new collection
            holder_collection.objects.link(base_i)
            base_i.parent = holder
            base_i.hide_set(True)
        
        for i in range(5):
            base_i = default_object(f'Lid part {i:02d}')
            lid_collection.objects.link(base_i)
            base_i.parent = lid
            base_i.hide_set(True)

        holder_parts = [c for c in holder.children if c.name.startswith('Holder')]
        slats = holder_parts[-1]
        slats.modifiers.new(type='ARRAY', name='slats x')
        slats.modifiers.new(type='ARRAY', name='slats y')
        holder.tu_holder_group.is_holder = True
        holder.tu_holder_group.holder_collection_name = holder_collection.name
        holder.tu_holder_group.holder_lid_collection_name = lid_collection.name
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        DefaultHolder.bl_idname,
        text=DefaultHolder.__doc__,
        icon='PLUGIN'
    )


def register():
    bpy.utils.register_class(HolderPanel)
    bpy.utils.register_class(HolderPropertyGroup)
    bpy.utils.register_class(DefaultHolder)
    setattr(
        bpy.types.Object,
        'tu_holder_group',
        bpy.props.PointerProperty(type=HolderPropertyGroup)
    ) 


def unregister():
    bpy.utils.unregister_class(HolderPanel)
    bpy.utils.unregister_class(HolderPropertyGroup)
    bpy.utils.unregister_class(DefaultHolder)
    delattr(
        bpy.types.Object,
        'tu_holder_group'
    )


if __name__ == '__main__':
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    register()
