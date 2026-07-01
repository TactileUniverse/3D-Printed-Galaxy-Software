import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector, Euler, Matrix
from bpy.props import (
    FloatProperty,
    EnumProperty,
    BoolProperty,
    StringProperty,
    FloatVectorProperty
)


def build_emboss(props, context):
    if props.editing:
        return None

    props.editing = True

    # update modifier values

    plane = props.id_data
    lx, ly, _ = plane.dimensions
    B = lx * ly * props.Fpu**2
    A = ly / lx

    ny = round(math.sqrt(A * B))
    nx = round(math.sqrt(B / A))

    old_me = plane.data
    me_name = old_me.name
    # use a copy so materials and vertex groups carry over
    me = old_me.copy()

    # make new regular grid mesh with the correct FPU
    bm = bmesh.new()
    bm.from_mesh(me)
    # empty copy
    for v in bm.verts:
        bm.verts.remove(v)
    # ensure a uv layer exists before create_grid
    bm.loops.layers.uv.new(me_name)
    bmesh.ops.create_grid(
        bm,
        x_segments=nx,
        y_segments=ny,
        size=lx / 2,
        matrix=Matrix.Scale(A, 4, Vector((0, 1, 0))),
        calc_uvs=True
    )
    bm.verts.ensure_lookup_table()

    # get weights for vertex group
    # bm.to_mesh(me)
    # verts_np = np.empty(len(me.vertices) * 3)
    # me.vertices.foreach_get('co', verts_np)
    # verts_np = verts_np.reshape(-1, 3)
    verts_np = np.array([v.co for v in bm.verts])

    # find corners
    cond1 = (verts_np[:, 0] == verts_np[:, 0].min()) & (verts_np[:, 1] == verts_np[:, 1].min())
    cond2 = (verts_np[:, 0] == verts_np[:, 0].min()) & (verts_np[:, 1] == verts_np[:, 1].max())
    cond3 = (verts_np[:, 0] == verts_np[:, 0].max()) & (verts_np[:, 1] == verts_np[:, 1].min())
    cond4 = (verts_np[:, 0] == verts_np[:, 0].max()) & (verts_np[:, 1] == verts_np[:, 1].max())
    verts_corner = np.nonzero(cond1 | cond2 | cond3 | cond4)[0]

    # find verts to be embossed
    x_high = 0.5 * lx - props.Border_width
    x_low = props.Border_width - 0.5 * lx
    y_high = 0.5 * ly - props.Border_width
    y_low = props.Border_width - 0.5 * ly

    cond1 = (props.External_edge != 'RIGHT') & (verts_np[:, 0] > x_high)
    cond2 = (props.External_edge != 'LEFT') & (verts_np[:, 0] < x_low)
    cond3 = (props.External_edge != 'TOP') & (verts_np[:, 1] > y_high)
    cond4 = (props.External_edge != 'BOTTOM') & (verts_np[:, 1] < y_low)

    weights = ~(cond1 | cond2 | cond3 | cond4)

    # set vertex group weights
    bm.verts.layers.deform.verify()
    deform = bm.verts.layers.deform.active
    for w, v in zip(weights, bm.verts):
        v[deform][0] = w

    # set crease on corner and outside edges
    bm.edges.layers.float.verify()
    bm.edges.ensure_lookup_table()
    crease_layer = bm.edges.layers.float.get("crease_edge")
    if not crease_layer:
        crease_layer = bm.edges.layers.float.new("crease_edge")

    bound_edges = [e for e in bm.edges if e.is_boundary]
    for e in bound_edges:
        e[crease_layer] = 1

    bm.verts.layers.float.verify()
    bm.verts.ensure_lookup_table()
    crease_layer_v = bm.verts.layers.float.get("crease_vert")
    if not crease_layer_v:
        crease_layer_v = bm.verts.layers.float.new("crease_vert")

    for vdx in verts_corner:
        bm.verts[vdx][crease_layer_v] = 1

    # extrude to make solid object
    r = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:] + bound_edges)
    verts_extrude = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(
        bm,
        vec=Vector((0, 0, -props.Base_height - props.Emboss_height)),
        verts=verts_extrude
    )

    # set vertex group weights for new extruded verts
    bm.verts.ensure_lookup_table()
    bm.verts.layers.deform.verify()
    deform = bm.verts.layers.deform.active
    for v in verts_extrude:
        bm.verts[v.index][deform][0] = 0

    # update normals
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # associate mesh with object
    bm.to_mesh(me)
    plane.data = me
    bpy.data.meshes.remove(old_me)
    plane.data.rename(me_name)

    # set modifier values
    if not props.Invert_image:
        plane.modifiers["bump"].strength = props.Emboss_height
        plane.modifiers["bump"].mid_level = 1
    else:
        plane.modifiers["bump"].strength = -props.Emboss_height
        plane.modifiers["bump"].mid_level = -1

    # external edge/nameplate and wedges and back frame
    update_external_edge(props, context)

    props.editing = False
    return None


def clean_up_meshes(me_name):
    # I can't figure out where the orphaned mesh
    # comes from, so just loop over all meshes and
    # remove old ones that are no liked to objects
    for me in bpy.data.meshes:
        if (me.users == 0) and (me.name.startswith(me_name)):
            bpy.data.meshes.remove(me)


def flatten_spikes(props, context):
    plane = props.id_data

    old_me = plane.data
    me_name = old_me.name
    # use a copy so materials and vertex groups carry over
    me = old_me.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    bm.verts.layers.deform.verify()
    deform = bm.verts.layers.deform.active
    verts_emboss = [v.index for v in bm.verts if v[deform][0] == 1]

    # reset to zero before starting
    for vdx in verts_emboss:
        bm.verts[vdx].co.z = 0

    bm.to_mesh(me)
    plane.data = me

    if props.Spike_removal:
        if 'smooth' in plane.modifiers:
            plane.modifiers.remove(plane.modifiers['smooth'])

        depsgraph = context.evaluated_depsgraph_get()
        object_mod = plane.evaluated_get(depsgraph)
        bm_mod = bmesh.new()
        bm_mod.from_mesh(bpy.data.meshes.new_from_object(object_mod))
        bm_mod.verts.ensure_lookup_table()

        for vdx in verts_emboss:
            # move the verts on the un-applied mesh
            v = bm.verts[vdx]
            # check for spikes on the applied mesh
            z = bm_mod.verts[vdx].co.z
            other_z_dif = 0
            other_z_count = 0
            spike = True
            for e in v.link_edges:
                other_z = bm_mod.verts[ e.other_vert(v).index].co.z
                if abs(z - other_z) < props.Spike_threshold:
                    spike = False
                else:
                    other_z_dif += abs(z - other_z)
                    other_z_count += 1
            if spike:
                average_dif = other_z_dif / other_z_count
                if props.Invert_image:
                    v.co.z += props.Spike_reduction_factor * average_dif
                else:
                    v.co.z -= props.Spike_reduction_factor * average_dif

        subsurf = plane.modifiers.new(name='smooth', type='SUBSURF')
        subsurf.quality = 1
        subsurf.show_viewport = True
        subsurf.levels = 2

    bm.to_mesh(me)
    plane.data = me
    bpy.data.meshes.remove(old_me)
    plane.data.rename(me_name)
    clean_up_meshes(me_name)
    return None


def update_filter(props, context):
    iTex = bpy.data.textures[props.texture_name]
    iTex.filter_size = props.Noise_filter
    return None


def remove_frame(props, index):
    if (index == 1) and (props.frame_1_name != ''):
        frame1 = bpy.data.objects[props.frame_1_name]
        # remove the mesh to ensure full removal of the object
        bpy.data.meshes.remove(frame1.data)
        props.frame_1_name = ''
    elif (index == 2) and (props.frame_2_name != ''):
        frame2 = bpy.data.objects[props.frame_2_name]
        # remove the mesh to ensure full removal of the object
        bpy.data.meshes.remove(frame2.data)
        props.frame_2_name = ''


def remove_edge(props):
    if props.edge_name != '':
        edge = bpy.data.objects[props.edge_name]
        for child in edge.children:
            # remove the curve and mesh to ensure full removal of the object
            if child.type == 'MESH':
                bpy.data.meshes.remove(child.data)
            else:
                bpy.data.curves.remove(child.data)
        # remove the mesh to ensure full removal of the object
        bpy.data.meshes.remove(edge.data)
        props.edge_name = ''


def update_back_frame(props, context):
    plane = props.id_data
    lx, ly, _ = plane.dimensions
    update_values(props)

    if props.Back_frame:
        # if a back frame is needed
        if props.frame_1_name == '':
            # if there is not already a back frame
            # make one, name it, and set parent
            bpy.ops.object.tu_back_frame()
            frame1 = context.view_layer.objects.active
            frame1.name = 'Back frame 1'
            frame1.parent = plane
            props.frame_1_name = frame1.name
            context.view_layer.objects.active = plane
        else:
            # if frame already exists grab it
            frame1 = bpy.data.objects[props.frame_1_name]
        # set properties
        frame1.location = props.frame_1_location
        frame1.rotation_euler = props.wedge_frame_rotation
        if props.External_edge in ['NONE', 'TOP', 'BOTTOM']:
            frame1.tu_back_frame_group.Size_x = lx
            frame1.tu_back_frame_group.Size_y = ly
        else:
            frame1.tu_back_frame_group.Size_x = ly
            frame1.tu_back_frame_group.Size_y = lx
        frame1.tu_back_frame_group.Gap_size = props.Gap_size
        frame1.tu_back_frame_group.Border_width = props.Border_width
        if props.External_edge == 'NONE':
            remove_frame(props, 2)
            frame1.tu_back_frame_group.Close = True
            if props.Name_plate:
                frame1.tu_back_frame_group.Size_y += props.Name_plate_Y
        else:
            frame1.tu_back_frame_group.Close = False
            # rotate to match edge
            if props.frame_2_name == '':
                # make a second frame for the name plate
                bpy.ops.object.tu_back_frame()
                frame2 = context.view_layer.objects.active
                frame2.name = 'Back frame 2'
                frame2.parent = plane
                props.frame_2_name = frame2.name
                context.view_layer.objects.active = plane
            else:
                frame2 = bpy.data.objects[props.frame_2_name]

            # set props
            frame2.location = props.edge_location + props.frame_2_location
            frame2.rotation_euler = props.wedge_frame_rotation
            frame2.tu_back_frame_group.Close = False
            if props.External_edge in ['NONE', 'TOP', 'BOTTOM']:
                frame2.tu_back_frame_group.Size_x = lx
            else:
                frame2.tu_back_frame_group.Size_x = ly
            frame2.tu_back_frame_group.Size_y = props.plate_Y
            frame2.tu_back_frame_group.Gap_size = props.Gap_size
            frame2.tu_back_frame_group.Border_width = props.Border_width
            if props.edge_name != '':
                edge = bpy.data.objects[props.edge_name]
                edge.location = props.edge_location
    else:
        # No frame needed
        remove_frame(props, 1)
        remove_frame(props, 2)
    return None


def update_values(props):
    plane = props.id_data
    lx, ly, _ = plane.dimensions

    total_height = props.Emboss_height + props.Base_height

    if props.Name_plate:
        props.plate_Y = props.Name_plate_Y
    else:
        props.plate_Y = props.Border_width

    props.frame_1_location = Vector((0, 0, -total_height))
    props.frame_2_location = Vector((0, 0, -0.5 * total_height))
    if props.External_edge == 'NONE':
        props.edge_location = Vector((
            0,
            (0.5 * ly) + (0.5 * props.Name_plate_Y) - (0.25 * props.Border_width),
            -0.5 * total_height
        ))
        props.edge_rotation = Euler((0, 0, math.radians(180)))
        props.edge_size_x = lx
        props.wedge_frame_rotation = Euler((0, 0, 0))
        if props.Name_plate:
            props.frame_1_location = Vector((0, 0.5 * props.Name_plate_Y, -total_height))
    elif props.External_edge == 'TOP':
        props.wedge_location = Vector((0, 0.5 * ly, -props.Emboss_height))
        props.wedge_frame_rotation = Euler((0, 0, 0))
        props.edge_location = Vector((
            0,
            0.5 * (props.plate_Y - ly),
            3 + props.Gap_size + 0.5 * total_height
        ))
        props.edge_rotation = Euler((0, 0, 0))
        props.edge_size_x = lx
    elif props.External_edge == 'BOTTOM':
        props.wedge_location = Vector((0, -0.5 * ly, -props.Emboss_height))
        props.wedge_frame_rotation = Euler((0, 0, math.radians(180)))
        props.edge_location = Vector((
            0,
            0.5 * (ly - props.plate_Y),
            3 + props.Gap_size + 0.5 * total_height
        ))
        props.edge_rotation = Euler((0, 0, math.radians(180)))
        props.edge_size_x = lx
    elif props.External_edge == 'RIGHT':
        props.wedge_location = Vector((0.5 * lx, 0, -props.Emboss_height))
        props.wedge_frame_rotation = Euler((0, 0, math.radians(-90)))
        props.edge_location = Vector((
            0.5 * (props.plate_Y - lx),
            0,
            3 + props.Gap_size + 0.5 * total_height
        ))
        props.edge_rotation = Euler((0, 0, math.radians(-90)))
        props.edge_size_x = ly
    elif props.External_edge == 'LEFT':
        props.wedge_location = Vector((-0.5 * lx, 0, -props.Emboss_height))
        props.wedge_frame_rotation = Euler((0, 0, math.radians(90)))
        props.edge_location = Vector((
            0.5 * (lx - props.plate_Y),
            0,
            3 + props.Gap_size + 0.5 * total_height
        ))
        props.edge_rotation = Euler((0, 0, math.radians(90)))
        props.edge_size_x = ly


def update_external_edge(props, context):
    plane = props.id_data
    update_back_frame(props, context)
    if (props.External_edge != 'NONE') or (props.Name_plate):
        if props.edge_name == '':
            bpy.ops.object.tu_name_plate()
            edge = context.view_layer.objects.active
            edge.name = 'External edge'
            edge.parent = plane
            props.edge_name = edge.name
            context.view_layer.objects.active = plane
        else:
            edge = bpy.data.objects[props.edge_name]
        if props.Name_plate:
            edge.tu_name_plate_group.Text = props.Name_plate_text
            edge.tu_name_plate_group.Text_size = props.Name_plate_text_size
        else:
            edge.tu_name_plate_group.Text = ''
        edge.location = props.edge_location
        edge.rotation_euler = props.edge_rotation
        edge.tu_name_plate_group.Size_x = props.edge_size_x
        edge.tu_name_plate_group.Size_z = props.Emboss_height + props.Base_height
        edge.tu_name_plate_group.Base_height = props.Base_height
        edge.tu_name_plate_group.Border_width = props.Border_width
        if props.External_edge == 'NONE':
            # this is an internal name plate
            edge.tu_name_plate_group.Size_y = props.plate_Y + (0.5 * props.Border_width)
            edge.tu_name_plate_group.Notches = False
        else:
            # this is an external name plate/edge
            edge.tu_name_plate_group.Size_y = props.plate_Y
            edge.tu_name_plate_group.Notches = True
    else:
        remove_edge(props)
    if props.External_edge != 'NONE':
        make_wedges(props, context)
    else:
        remove_wedge(props)
    return None


def make_wedges(props, context):
    plane = props.id_data
    shift = 0.25 * props.edge_size_x
    x = [
        -2.25,
        2.25,
        -1.125,
        1.125
    ]
    y = [
        (2 * props.Border_width / 3),
        -props.Border_width
    ]
    z = [
        -0.05,
        -props.Base_height + 0.05
    ]
    verts = [
        Vector((x[0] + shift, y[0], z[0])),
        Vector((x[1] + shift, y[0], z[0])),
        Vector((x[1] + shift, y[1], z[0])),
        Vector((x[0] + shift, y[1], z[0])),

        Vector((x[2] + shift, y[0], z[1])),
        Vector((x[3] + shift, y[0], z[1])),
        Vector((x[3] + shift, y[1], z[1])),
        Vector((x[2] + shift, y[1], z[1])),

        Vector((x[0] - shift, y[0], z[0])),
        Vector((x[1] - shift, y[0], z[0])),
        Vector((x[1] - shift, y[1], z[0])),
        Vector((x[0] - shift, y[1], z[0])),

        Vector((x[2] - shift, y[0], z[1])),
        Vector((x[3] - shift, y[0], z[1])),
        Vector((x[3] - shift, y[1], z[1])),
        Vector((x[2] - shift, y[1], z[1]))
    ]
    faces = [
        (3, 2, 1, 0),
        (0, 4, 7, 3),
        (4, 5, 6, 7),
        (1, 2, 6, 5),
        (0, 1, 5, 4),
        (2, 3, 7, 6),

        (3 + 8, 2 + 8, 1 + 8, 0 + 8),
        (0 + 8, 4 + 8, 7 + 8, 3 + 8),
        (4 + 8, 5 + 8, 6 + 8, 7 + 8),
        (1 + 8, 2 + 8, 6 + 8, 5 + 8),
        (0 + 8, 1 + 8, 5 + 8, 4 + 8),
        (2 + 8, 3 + 8, 7 + 8, 6 + 8)
    ]
    
    if props.wedge_name == '':
        me = bpy.data.meshes.new('Wedges')
        wedge = bpy.data.objects.new('Wedges', me)
        wedge.parent = plane
        wedge.matrix_world = context.scene.cursor.matrix
        context.collection.objects.link(wedge)
        props.wedge_name = wedge.name
        me.from_pydata(verts, [], faces)
        me.update()
    else:
        wedge = bpy.data.objects[props.wedge_name]
        old_me = wedge.data
        me_name = old_me.name
        me = bpy.data.meshes.new(me_name)
        me.from_pydata(verts, [], faces)
        me.update()
        wedge.data = me
        bpy.data.meshes.remove(old_me)
        wedge.data.rename(me_name)

    wedge.location = props.wedge_location
    wedge.rotation_euler = props.wedge_frame_rotation
    return None


def remove_wedge(props):
    if props.wedge_name != '':
        wedge = bpy.data.objects[props.wedge_name]
        # remove the mesh to ensure full removal of the object
        bpy.data.meshes.remove(wedge.data)
        props.wedge_name = ''


class EmbossPlanePropertyGroup(bpy.types.PropertyGroup):
    editing: BoolProperty(
        name="Editing",
        default=False
    )
    is_emboss_plane: BoolProperty(
        name="Is name plate",
        default=False,
        update=build_emboss
    )
    texture_name: StringProperty(
        name='Texture name'
    )
    frame_1_name: StringProperty(
        name='Back frame 1 name',
        default=''
    )
    frame_1_location: FloatVectorProperty(
        name='Back frame 1 location',
        subtype='XYZ'
    )
    frame_2_name: StringProperty(
        name='Back frame 2 name',
        default=''
    )
    frame_2_location: FloatVectorProperty(
        name='Back frame 2 location',
        subtype='XYZ'
    )
    wedge_name: StringProperty(
        name='Wedge name',
        default=''
    )
    edge_name: StringProperty(
        name='External edge name',
        default=''
    )
    edge_location: FloatVectorProperty(
        name='Edge location',
        subtype='XYZ'
    )
    edge_rotation: FloatVectorProperty(
        name='Edge rotation',
        subtype='EULER'
    )
    edge_size_x: FloatProperty(
        name='Edge size x'
    )
    plate_Y: FloatProperty(
        name='Plate Y'
    )
    wedge_location: FloatVectorProperty(
        name='Wedge location',
        subtype='XYZ'
    )
    wedge_frame_rotation: FloatVectorProperty(
        name='Wedge frame rotation',
        subtype='EULER'
    )
    Fpu: FloatProperty(
        # name='Faces Per Unit',
        name='',
        default=2,
        min=0,
        description='Number of faces per unit length across the top of the plane',
        update=build_emboss
    )
    Emboss_height: FloatProperty(
        # name='Emboss Thickness',
        name='',
        default=3,
        min=0.1,
        unit='LENGTH',
        description='The emboss height for the model',
        update=build_emboss
    )
    Invert_image: BoolProperty(
        # name='Invert Image',
        name='',
        default=False,
        description='Invert the emboss direction',
        update=build_emboss
    )
    Base_height: FloatProperty(
        # name='Base Thickness',
        name='',
        default=3,
        min=0.1,
        unit='LENGTH',
        description="Thickness of the model's base",
        update=build_emboss
    )
    Border_width: FloatProperty(
        # name='Border Width',
        name='',
        default=3,
        min=0.1,
        unit='LENGTH',
        description='Width of the border',
        update=build_emboss
    )
    External_edge: EnumProperty(
        # name='External Edge',
        name='',
        description='Select what edge should be made external (if any)',
        default='NONE',
        items=[
            ('NONE', 'none', ''),
            ('RIGHT', 'right', ''),
            ('LEFT', 'left', ''),
            ('TOP', 'top', ''),
            ('BOTTOM', 'bottom', '')
        ],
        update=build_emboss
    )
    Back_frame: BoolProperty(
        # name='Back Frame',
        name='',
        default=True,
        description='Add a back frame to the model',
        update=update_back_frame
    )
    Gap_size: FloatProperty(
        # name='Back Frame Gap Size',
        name='',
        default=1,
        min=0,
        unit='LENGTH',
        description='Size of the gap between the back frame and model',
        update=update_back_frame
    )
    Noise_filter: FloatProperty(
        # name='Noise Filter Size',
        name='',
        default=1,
        min=1,
        description='Smooth out noise in the image',
        update=update_filter
    )
    Spike_removal: BoolProperty(
        # name='Spike Removal',
        name='',
        default=False,
        description='Remove sharp spikes from the model',
        update=flatten_spikes
    )
    Spike_threshold: FloatProperty(
        # name='Spike Threshold',
        name='',
        default=0.75,
        min=0,
        unit='LENGTH',
        description='A single vertex that has a hight difference of at least this threshold from all of its neighbors is flagged as a spike',
        update=flatten_spikes
    )
    Spike_reduction_factor: FloatProperty(
        # name='Spike Reduction Factor',
        name='',
        default=0.75,
        min=0,
        description='Identified spikes will have their hight lowered by this fraction',
        update=flatten_spikes
    )
    Name_plate: BoolProperty(
        # name='Make Name Plate',
        name='',
        default=False,
        description='Make a name plate for the model',
        update=build_emboss
    )
    Name_plate_Y: FloatProperty(
        # name='Name Plate Height',
        name='',
        default=20,
        min=0,
        unit='LENGTH',
        description='The height of the name plate',
        update=update_external_edge
    )
    Name_plate_text: StringProperty(
        # name='Name Plate Text',
        name='',
        default='Example',
        description='Text for the name plate',
        update=update_external_edge
    )
    Name_plate_text_size: FloatProperty(
        # name='Name Plate Text Size',
        name='',
        default=18,
        min=0,
        description='Font size of the text',
        update=update_external_edge
    )


class EmbossPlanePanel(bpy.types.Panel):
    bl_label = "TU Emboss Plane Properties"
    bl_idname = "OBJECT_PT_edit_emboss_plane"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        def _tests():
            yield context.active_object is not None
            yield context.active_object.tu_emboss_plane_group.is_emboss_plane
            yield context.mode == "OBJECT"
        return all(_tests())

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        box1 = layout.box()
        box1.label(text='Emboss Properties')

        row = box1.row()
        row.label(text='Faces Per Unit')
        row.prop(obj.tu_emboss_plane_group, 'Fpu')

        row = box1.row()
        row.label(text='Emboss Thickness')
        row.prop(obj.tu_emboss_plane_group, 'Emboss_height')

        row = box1.row()
        row.label(text='Invert Image')
        row.prop(obj.tu_emboss_plane_group, 'Invert_image')

        row = box1.row()
        row.label(text='Base Thickness')
        row.prop(obj.tu_emboss_plane_group, 'Base_height')

        row = box1.row()
        row.label(text='Border Width')
        row.prop(obj.tu_emboss_plane_group, 'Border_width')

        row = box1.row()
        row.label(text='External Edge')
        row.prop(obj.tu_emboss_plane_group, 'External_edge')

        row = box1.row()
        row.label(text='Back Frame')
        row.prop(obj.tu_emboss_plane_group, 'Back_frame')

        row = box1.row()
        row.enabled = obj.tu_emboss_plane_group.Back_frame
        row.label(text='Back Frame Gap Size')
        row.prop(obj.tu_emboss_plane_group, 'Gap_size')

        box2 = layout.box()
        box2.label(text='Filter Properties')

        row = box2.row()
        row.label(text='Noise Filter Size')
        row.prop(obj.tu_emboss_plane_group, 'Noise_filter')

        row = box2.row()
        row.label(text='Spike Removal')
        row.prop(obj.tu_emboss_plane_group, 'Spike_removal')

        row = box2.row()
        row.enabled = obj.tu_emboss_plane_group.Spike_removal
        row.label(text='Spike Threshold')
        row.prop(obj.tu_emboss_plane_group, 'Spike_threshold')

        row = box2.row()
        row.enabled = obj.tu_emboss_plane_group.Spike_removal
        row.label(text='Spike Reduction Factor')
        row.prop(obj.tu_emboss_plane_group, 'Spike_reduction_factor')

        box3 = layout.box()
        box3.label(text='Name Plate Properties')

        row = box3.row()
        row.label(text='Make Name Plate')
        row.prop(obj.tu_emboss_plane_group, 'Name_plate')

        row = box3.row()
        row.enabled = obj.tu_emboss_plane_group.Name_plate
        row.label(text='Name Plate Height')
        row.prop(obj.tu_emboss_plane_group, 'Name_plate_Y')

        row = box3.row()
        row.enabled = obj.tu_emboss_plane_group.Name_plate
        row.label(text='Name Plate Text')
        row.prop(obj.tu_emboss_plane_group, 'Name_plate_text')

        row = box3.row()
        row.enabled = obj.tu_emboss_plane_group.Name_plate
        row.label(text='Name Plate Text Size')
        row.prop(obj.tu_emboss_plane_group, 'Name_plate_text_size')


class DefaultEmbossPlane(bpy.types.Operator):
    '''TU Emboss Plane'''

    bl_idname = 'object.tu_emboss_plane'
    bl_label = 'Emboss and solidify a plane'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        plane = context.active_object

        # create texture
        # use "base name" of the object to look for the texture
        base_name = plane.name.split('.')[0]
        image_keys = [k for k in bpy.data.images.keys() if k.startswith(base_name)]
        if len(image_keys) > 0:
            image_key = image_keys[0]
            image = bpy.data.images[image_key]
            iTex = bpy.data.textures.new(f'Displacement {plane.name}', type='IMAGE')
            iTex.image = image

            plane.vertex_groups.new(name='emboss')

            # add all modifiers
            displace = plane.modifiers.new(name='bump', type='DISPLACE')
            displace.texture = iTex
            displace.direction = 'Z'
            displace.vertex_group = 'emboss'
            displace.texture_coords = 'UV'
            displace.show_in_editmode = True
            displace.show_on_cage = True
            displace.mid_level = 1

            subsurf = plane.modifiers.new(name='smooth', type='SUBSURF')
            subsurf.quality = 1
            subsurf.show_viewport = True
            subsurf.levels = 2

            plane.tu_emboss_plane_group.texture_name = iTex.name
            plane.tu_emboss_plane_group.is_emboss_plane = True
        else:
            self.report({'WARNING'}, f'No images found matching the base name of the object {base_name}.')
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        DefaultEmbossPlane.bl_idname,
        text=DefaultEmbossPlane.__doc__,
        icon='PLUGIN'
    )


def register():
    bpy.utils.register_class(EmbossPlanePanel)
    bpy.utils.register_class(EmbossPlanePropertyGroup)
    bpy.utils.register_class(DefaultEmbossPlane)
    setattr(
        bpy.types.Object,
        'tu_emboss_plane_group',
        bpy.props.PointerProperty(type=EmbossPlanePropertyGroup)
    )
    bpy.types.VIEW3D_MT_object.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(EmbossPlanePanel)
    bpy.utils.unregister_class(EmbossPlanePropertyGroup)
    bpy.utils.unregister_class(DefaultEmbossPlane)
    delattr(
        bpy.types.Object,
        'tu_emboss_plane_group'
    )
    bpy.types.VIEW3D_MT_object.remove(add_object_button)


if __name__ == '__main__':
    register()
