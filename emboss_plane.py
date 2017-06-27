import bpy
import bmesh
import math
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty

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

    Fpu = FloatProperty(name="Faces per unit", default=3, min=0, description="Number of faces per unit length across the top of the plane")
    Emboss_height = FloatProperty(name="Emboss thickness", default=3, min=0.1, unit="LENGTH", description="The Emboss height for the model")
    Base_height = FloatProperty(name="Base Thickness", default=1, min=0.1, unit="LENGTH", description="Thickness of the model's base")
    Border_width = FloatProperty(name="Border width", default=3, min=0.1, unit="LENGTH", description="Width of the border")

    def get_weight(self, vert):
        x, y, _ = vert.co
        oy_minus = self.object_location[1] - (0.5 * self.ly)
        oy_plus = self.object_location[1] + (0.5 * self.ly)
        ox_minus = self.object_location[0] - (0.5 * self.lx)
        ox_plus = self.object_location[0] + (0.5 * self.lx)
        BE = self.Border_width + self.Emboss_height
        if (y > oy_plus - self.Border_width) or \
           (y < oy_minus + self.Border_width) or \
           (x > ox_plus - self.Border_width) or \
           (x < ox_minus + self.Border_width):
            return 0
        elif (y < oy_plus - BE) and \
             (y > oy_minus + BE) and \
             (x < ox_plus - BE) and \
             (x > ox_minus + BE):
            return 1
        else:
            y_high = (y <= oy_plus - self.Border_width) and (y >= oy_plus - BE)
            y_high_weight = (oy_plus - self.Border_width - y) / self.Emboss_height
            y_low = (y <= oy_minus + BE) and (y >= oy_minus + self.Border_width)
            y_low_weight = (y - oy_minus - self.Border_width) / self.Emboss_height
            x_high = (x <= ox_plus - self.Border_width) and (x >= ox_plus - BE)
            x_high_weight = (ox_plus - self.Border_width - x) / self.Emboss_height
            x_low = (x <= ox_minus + BE) and (x >= ox_minus + self.Border_width)
            x_low_weight = (x - ox_minus - self.Border_width) / self.Emboss_height
            if y_low:
                if x_low:
                    return min(y_low_weight, x_low_weight)
                elif x_high:
                    return min(y_low_weight, x_high_weight)
                else:
                    return y_low_weight
            if y_high:
                if x_low:
                    return min(y_high_weight, x_low_weight)
                elif x_high:
                    return min(y_high_weight, x_high_weight)
                else:
                    return y_high_weight
            elif x_high:
                return x_high_weight
            else:
                return x_low_weight

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
