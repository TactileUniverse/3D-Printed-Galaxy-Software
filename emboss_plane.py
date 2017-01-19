bl_info = {
    "name": "Emboss plane",
    "description": "Emboss and solidify a plane",
    "author": "Coleman Krawczyk",
    "version": (1, 2),
    "blender": (2, 76, 0),
    "location": "View3D > Tools > Mesh Edit",
    "category": "Mesh",
}

import bpy
import bmesh
import math
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty


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
    me = bpy.data.meshes.new(name+'Mesh')
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

    B = IntProperty(name="Number of faces", default=1000, min=0, description="Number of faces across the top of the plane")
    Height = FloatProperty(name="Thickness", default=6, unit="LENGTH", description="Thickness of full model")
    Base_height = FloatProperty(name="Base Thickness", default=3, min=0.1, unit="LENGTH", description="Thickness of the model's base")
    Border_width = FloatProperty(name="Border width", default=3, min=0.1, unit="LENGTH", description="Width of the border")

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
        lx = bm.edges[0].calc_length()
        ly = bm.edges[1].calc_length()

        # make border
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
        origin = object.location - Vector((ly / 2, (lx / 2) + 1.3 * self.Border_width, self.Base_height))
        createBorderEdge('top', origin, ly, self.Border_width, self.Height)
        origin = object.location - Vector((ly / 2, (lx / 2) + 2.6 * self.Border_width, self.Base_height))
        createBorderEdge('bottom', origin, ly, self.Border_width, self.Height)
        origin = object.location - Vector((ly / 2,  (lx / 2) + 3.9 * self.Border_width, self.Base_height))
        createBorderEdge('left', origin, lx, self.Border_width, self.Height)
        origin = object.location - Vector((ly / 2, (lx / 2) + 5.2 * self.Border_width, self.Base_height))
        createBorderEdge('right', origin, lx, self.Border_width, self.Height)

        object.select = True
        bpy.ops.object.editmode_toggle()

        # get object
        bm = bmesh.from_edit_mesh(object.data)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()

        # get number of cuts to make
        A = lx/ly
        nx = round(math.sqrt(A*self.B)) - 1
        ny = round(math.sqrt(self.B/A)) - 1

        # make loop cuts
        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": nx, "edge_index": 0})
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": ny, "edge_index": 1})
        bpy.ops.mesh.select_all(action='TOGGLE')

        # make vertex groups
        bound = [v.index for v in bm.verts if v.is_boundary]
        face = [v.index for v in bm.verts if not v.is_boundary]
        vgk = object.vertex_groups.keys()
        if 'boundary' not in vgk:
            object.vertex_groups.new('boundary')
        if 'face' not in vgk:
            object.vertex_groups.new('face')
        bpy.ops.object.editmode_toggle()
        object.vertex_groups['boundary'].add(bound, 1, 'REPLACE')
        object.vertex_groups['face'].add(face, 1, 'REPLACE')
        bpy.ops.object.editmode_toggle()

        # Extrude down and close bottom
        bm = bmesh.from_edit_mesh(object.data)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
        extrude_normal = bm.verts[0].normal * -1 * self.Base_height
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
            displace.mid_level = 0
            displace.direction = 'Z'
            displace.vertex_group = 'face'
            displace.texture_coords = 'UV'
            displace.strength = self.Height - self.Base_height
            displace.show_in_editmode = True
        else:
            displace = object.modifiers['bump']
            displace.strength = self.Height - self.Base_height
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
