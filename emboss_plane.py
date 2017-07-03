import bpy
import bmesh
import math
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty, BoolProperty

bl_info = {
    "name": "Emboss plane",
    "description": "Emboss and solidify a plane",
    "author": "Coleman Krawczyk",
    "version": (1, 3),
    "blender": (2, 76, 0),
    "location": "View3D > Tools > Mesh Edit",
    "category": "Mesh",
}


def createBorderEdge(name, origin, length, width, height):
    # origin is the bottom left vertex of the border edge
    verts = [
        (origin[0], origin[1], origin[2]),
        (origin[0] - width, origin[1] - width, origin[2]),
        (origin[0] + length + width, origin[1] - width, origin[2]),
        (origin[0] + length, origin[1], origin[2]),
        (origin[0], origin[1], origin[2] + height),
        (origin[0] - width, origin[1] - width, origin[2] + height),
        (origin[0] + length + width, origin[1] - width, origin[2] + height),
        (origin[0] + length, origin[1], origin[2] + height),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 4, 7, 3),
        (1, 5, 6, 2),
        (0, 4, 5, 1),
        (3, 7, 6, 2),
    ]
    me = bpy.data.meshes.new(name + 'Mesh')
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.objects.link(ob)
    me.from_pydata(verts, [], faces)
    me.update()
    return ob


class EmbossPlane(bpy.types.Operator):
    """Emboss Plane"""
    bl_idname = "object.emboss_plane"
    bl_label = "Emboss and solidify a plane"
    bl_options = {'REGISTER', 'UNDO'}

    Fpu = FloatProperty(
        name="Faces per unit",
        default=2,
        min=0,
        description="Number of faces per unit length across the top of the plane"
    )
    Emboss_height = FloatProperty(
        name="Emboss thickness",
        default=3,
        min=0.1,
        unit="LENGTH",
        description="The Emboss height for the model"
    )
    Base_height = FloatProperty(
        name="Base Thickness",
        default=2,
        min=0.1,
        unit="LENGTH",
        description="Thickness of the model's base"
    )
    Border_width = FloatProperty(
        name="Border width",
        default=3,
        min=0.1,
        unit="LENGTH",
        description="Width of the border"
    )
    Theta = FloatProperty(
        name="Taper angle",
        default=math.radians(90),
        min=math.radians(10),
        max=math.radians(90),
        unit="ROTATION",
        description="Angle to taper into the edges"
    )
    External_x = BoolProperty(
        name="Exteranl +X",
        default=False,
        description="Make +X edge external to the model"
    )
    External_mx = BoolProperty(
        name="Exteranl -X",
        default=False,
        description="Make -X edge external to the model"
    )
    External_y = BoolProperty(
        name="Exteranl +Y",
        default=False,
        description="Make +Y edge external to the model"
    )
    External_my = BoolProperty(
        name="Exteranl -Y",
        default=False,
        description="Make -Y edge external to the model"
    )

    def get_weight(self, vert):
        x, y, _ = vert.co
        x0, y0, _ = self.object_location
        fac = self.Emboss_height / math.tan(self.Theta)
        x3 = x0 + (0.5 * self.lx)
        x2 = x3 - self.Border_width
        x1 = x2 - fac
        y3 = y0 + (0.5 * self.ly)
        y2 = y3 - self.Border_width
        y1 = y2 - fac
        xm3 = x0 - (0.5 * self.lx)
        xm2 = xm3 + self.Border_width
        xm1 = xm2 + fac
        ym3 = y0 - (0.5 * self.ly)
        ym2 = ym3 + self.Border_width
        ym1 = ym2 + fac
        if (not self.External_y and (y > y2)) or \
           (not self.External_my and (y < ym2)) or \
           (not self.External_x and (x > x2)) or \
           (not self.External_mx and (x < xm2)):
            return 0
        elif (self.External_y or (y < y1)) and \
             (self.External_my or (y > ym1)) and \
             (self.External_x or (x < x1)) and \
             (self.External_mx or (x > xm1)):
            return 1
        else:
            x_weight = 1
            xm_weight = 1
            y_weight = 1
            ym_weight = 1
            if not self.External_x:
                x_weight = 1 - ((x - x1) / fac)
            if not self.External_mx:
                xm_weight = 1 - ((xm1 - x) / fac)
            if not self.External_y:
                y_weight = 1 - ((y - y1) / fac)
            if not self.External_my:
                ym_weight = 1 - ((ym1 - y) / fac)
            return min([x_weight, xm_weight, y_weight, ym_weight])

    def execute(self, context):
        object = context.active_object
        name = object.name
        object = bpy.data.objects[name]

        # get object
        bm = bmesh.from_edit_mesh(object.data)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()

        # get length and width
        self.ly = bm.edges[0].calc_length()
        self.lx = bm.edges[1].calc_length()

        # make border
        '''
        all_objects = bpy.data.objects.keys()
        bpy.ops.object.editmode_toggle()
        object.select = False
        if 'top' in all_objects:
            bpy.data.objects['top'].select = True
        if 'bottom' in all_objects:
            bpy.data.objects['bottom'].select = True
        if 'left' in all_objects:
            bpy.data.objects['left'].select = True
        if 'right' in all_objects:
            bpy.data.objects['right'].select = True
        bpy.ops.object.delete()
        origin = object.location - Vector((self.lx / 2, (self.ly / 2) + 1.3 * self.Border_width, self.Base_height))
        createBorderEdge('top', origin, lx, self.Border_width, self.Height)
        origin = object.location - Vector((self.lx / 2, (self.ly / 2) + 2.6 * self.Border_width, self.Base_height))
        createBorderEdge('bottom', origin, lx, self.Border_width, self.Height)
        origin = object.location - Vector((self.lx / 2, (self.ly / 2) + 3.9 * self.Border_width, self.Base_height))
        createBorderEdge('left', origin, lx, self.Border_width, self.Height)
        origin = object.location - Vector((self.lx / 2, (self.ly / 2) + 5.2 * self.Border_width, self.Base_height))
        createBorderEdge('right', origin, lx, self.Border_width, self.Height)

        object.select = True
        bpy.ops.object.editmode_toggle()

        # get object
        bm = bmesh.from_edit_mesh(object.data)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
        '''
        # get number of cuts to make
        B = self.lx * self.ly * self.Fpu**2
        A = self.ly / self.lx
        nx = round(math.sqrt(A * B)) - 1
        ny = round(math.sqrt(B / A)) - 1
        self.report({'INFO'}, '{0} total faces'.format(nx * ny))

        # make loop cuts
        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": nx, "edge_index": 0})
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": ny, "edge_index": 1})
        bpy.ops.mesh.select_all(action='TOGGLE')

        # make vertex groups
        self.object_location = object.location
        vertex_weights = [self.get_weight(v) for v in bm.verts]
        verts = [v.index for v in bm.verts]
        vgk = object.vertex_groups.keys()
        if 'emboss' not in vgk:
            object.vertex_groups.new('emboss')
        bpy.ops.object.editmode_toggle()
        for v, w in zip(verts, vertex_weights):
            object.vertex_groups['emboss'].add([v], w, 'REPLACE')
        bpy.ops.object.editmode_toggle()

        # Extrude down and close bottom
        bm = bmesh.from_edit_mesh(object.data)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
        extrude_normal = bm.verts[0].normal * -1 * (self.Emboss_height + self.Base_height)
        bound_edges = [e for e in bm.edges if e.is_boundary]
        bound_edges_index = [e.index for e in bound_edges]
        bmesh.ops.extrude_edge_only(bm, edges=bound_edges)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
        bound_verts = [v for v in bm.verts if v.is_boundary]
        bound_edges = [e for e in bm.edges if e.is_boundary]
        bound_edges_index += [e.index for e in bound_edges]
        bmesh.ops.translate(bm, vec=extrude_normal, verts=bound_verts)
        bmesh.ops.edgeloop_fill(bm, edges=bound_edges)

        # set crease on boundary
        bpy.ops.object.editmode_toggle()
        for idx in bound_edges_index:
            object.data.edges[idx].select = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.transform.edge_crease(value=1)

        # add modifiers
        tex = bpy.data.textures.keys()
        mod = object.modifiers.keys()
        if 'Displacement' not in tex:
            iTex = bpy.data.textures.new('Displacemnt', type='IMAGE')
            iTex.image = bpy.data.images[-1]  # assume last image loaded is the correct one
        if 'bump' not in mod:
            displace = object.modifiers.new(name='bump', type='DISPLACE')
            displace.texture = iTex
            displace.mid_level = 1
            displace.direction = 'Z'
            displace.vertex_group = 'emboss'
            displace.texture_coords = 'UV'
            displace.strength = self.Emboss_height
            displace.show_in_editmode = True
        else:
            displace = object.modifiers['bump']
            displace.strength = self.Emboss_height
        if 'smooth' not in mod:
            subsurf = object.modifiers.new(name='smooth', type='SUBSURF')
            subsurf.show_viewport = False
            subsurf.levels = 2

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        object = context.active_object
        sx, sy, sz = object.scale
        good = sx == sy == sz
        good = good and object is not None
        good = good and object.mode == 'EDIT'
        return good


def add_object_button(self, context):
    self.layout.operator(EmbossPlane.bl_idname, text=EmbossPlane.__doc__)


def register():
    bpy.utils.register_class(EmbossPlane)
    bpy.types.VIEW3D_PT_tools_meshedit.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(EmbossPlane)


if __name__ == "__main__":
    register()
