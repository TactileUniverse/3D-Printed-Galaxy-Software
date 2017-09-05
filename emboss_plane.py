import bpy
import bmesh
import math
from mathutils import Vector, kdtree, Matrix
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty

bl_info = {
    'name': 'Emboss plane',
    'description': 'Emboss and solidify a plane',
    'author': 'Coleman Krawczyk',
    'version': (1, 4),
    'blender': (2, 76, 0),
    'location': 'View3D > Tools > Mesh Edit',
    'category': 'Mesh',
}


class EmbossPlane(bpy.types.Operator):
    '''Emboss Plane'''
    bl_idname = 'object.emboss_plane'
    bl_label = 'Emboss and solidify a plane'
    bl_options = {'REGISTER', 'UNDO'}

    Fpu = FloatProperty(
        name='Faces per unit',
        default=2,
        min=0,
        description='Number of faces per unit length across the top of the plane'
    )
    Emboss_height = FloatProperty(
        name='Emboss thickness',
        default=3,
        min=0.1,
        unit='LENGTH',
        description='The Emboss height for the model'
    )
    Base_height = FloatProperty(
        name='Base Thickness',
        default=3,
        min=0.1,
        unit='LENGTH',
        description="Thickness of the model's base"
    )
    Border_width = FloatProperty(
        name='Border width',
        default=3,
        min=0.1,
        unit='LENGTH',
        description='Width of the border'
    )
    Theta = math.radians(90)
    External_y = False
    External_my = False
    External_x = False
    External_mx = False

    External_edge = EnumProperty(
        name='External Edge',
        description='Select what edge should be made external (if any)',
        default='NONE',
        items=[
            ('NONE', 'none', ''),
            ('RIGHT', 'right', ''),
            ('LEFT', 'left', ''),
            ('TOP', 'top', ''),
            ('BOTTOM', 'bottom', '')
        ]
    )

    def get_bm(self):
        bm = bmesh.from_edit_mesh(self.object.data)
        if hasattr(bm.verts, 'ensure_lookup_table'):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
        return bm

    def get_wedge_loc(self):
        if self.External_edge == 'TOP':
            w1_l = Vector((
                self.object.location[0] - 0.25 * self.lx - 3,
                self.object.location[1] + 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w1_r = Vector((
                self.object.location[0] - 0.25 * self.lx + 3,
                self.object.location[1] + 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_l = Vector((
                self.object.location[0] + 0.25 * self.lx - 3,
                self.object.location[1] + 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_r = Vector((
                self.object.location[0] + 0.25 * self.lx + 3,
                self.object.location[1] + 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc = Vector((
                self.object.location[0],
                self.object.location[1] + 0.5 * (self.ly + self.Border_width),
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc_final = Vector((
                self.object.location[0],
                self.object.location[1] - 0.5 * (self.ly - self.Border_width),
                self.object.location[2] + (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_rot = (math.radians(180), 0, 0)
            self.external_edge_scale = Vector((
                self.lx,
                self.Border_width,
                self.Emboss_height + self.Base_height
            ))
        elif self.External_edge == 'BOTTOM':
            w1_l = Vector((
                self.object.location[0] - 0.25 * self.lx - 3,
                self.object.location[1] - 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w1_r = Vector((
                self.object.location[0] - 0.25 * self.lx + 3,
                self.object.location[1] - 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_l = Vector((
                self.object.location[0] + 0.25 * self.lx - 3,
                self.object.location[1] - 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_r = Vector((
                self.object.location[0] + 0.25 * self.lx + 3,
                self.object.location[1] - 0.5 * self.ly,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc = Vector((
                self.object.location[0],
                self.object.location[1] - 0.5 * (self.ly + self.Border_width),
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc_final = Vector((
                self.object.location[0],
                self.object.location[1] + 0.5 * (self.ly - self.Border_width),
                self.object.location[2] + (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_rot = (math.radians(180), 0, 0)
            self.external_edge_scale = Vector((
                self.lx,
                self.Border_width,
                self.Emboss_height + self.Base_height
            ))
        elif self.External_edge == 'RIGHT':
            w1_l = Vector((
                self.object.location[0] + 0.5 * self.lx,
                self.object.location[1] - 0.25 * self.ly - 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w1_r = Vector((
                self.object.location[0] + 0.5 * self.lx,
                self.object.location[1] - 0.25 * self.ly + 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_l = Vector((
                self.object.location[0] + 0.5 * self.lx,
                self.object.location[1] + 0.25 * self.ly - 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_r = Vector((
                self.object.location[0] + 0.5 * self.lx,
                self.object.location[1] + 0.25 * self.ly + 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc = Vector((
                self.object.location[0] + 0.5 * (self.lx + self.Border_width),
                self.object.location[1],
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc_final = Vector((
                self.object.location[0] - 0.5 * (self.lx - self.Border_width),
                self.object.location[1],
                self.object.location[2] + (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_rot = (0, math.radians(180), 0)
            self.external_edge_scale = Vector((
                self.Border_width,
                self.ly,
                self.Emboss_height + self.Base_height
            ))
        else:
            w1_l = Vector((
                self.object.location[0] - 0.5 * self.lx,
                self.object.location[1] - 0.25 * self.ly - 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w1_r = Vector((
                self.object.location[0] - 0.5 * self.lx,
                self.object.location[1] - 0.25 * self.ly + 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_l = Vector((
                self.object.location[0] - 0.5 * self.lx,
                self.object.location[1] + 0.25 * self.ly - 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            w2_r = Vector((
                self.object.location[0] - 0.5 * self.lx,
                self.object.location[1] + 0.25 * self.ly + 3,
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc = Vector((
                self.object.location[0] - 0.5 * (self.lx + self.Border_width),
                self.object.location[1],
                self.object.location[2] - 0.5 * (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_loc_final = Vector((
                self.object.location[0] + 0.5 * (self.lx - self.Border_width),
                self.object.location[1],
                self.object.location[2] + (self.Emboss_height + self.Base_height)
            ))
            self.external_edge_rot = (0, math.radians(180), 0)
            self.external_edge_scale = Vector((
                self.Border_width,
                self.ly,
                self.Emboss_height + self.Base_height
            ))
        return [w1_l, w1_r], [w2_l, w2_r]

    def make_wedge(self, wedge, name='wedge1'):
        left, right = wedge
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='FACE')
        kd, bm = self.get_kd_faces()
        normal = bm.faces[kd.find(left)[1]].normal * self.Border_width * 2.0 / 3.0
        bm.faces[kd.find(left)[1]].select = True
        bm.faces[kd.find(right)[1]].select = True
        bpy.ops.mesh.shortest_path_select()
        bpy.ops.transform.edge_crease(value=1)
        selected_faces = [f for f in bm.faces if f.select]
        selected_verts = [v for v in bm.verts if v.select]
        wedge_verts = [v.index for v in selected_verts]
        bottom_verts = [v for v in selected_verts if v.co[2] == self.object.location[2] - 1 * (self.Emboss_height + self.Base_height)]
        vgk = self.object.vertex_groups.keys()
        bpy.ops.mesh.select_all(action='DESELECT')
        for v in bottom_verts:
            v.select = True
        resize = (0.5, 1.0, 1.0)
        if normal[0] != 0:
            resize = (1.0, 0.5, 1.0)
        bpy.ops.transform.resize(value=resize)
        bpy.ops.mesh.select_all(action='DESELECT')
        for f in selected_faces:
            f.select = True
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": normal})
        selected_verts = [v for v in bm.verts if v.select]
        for v in selected_verts:
            wedge_verts.append(v.index)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.object.editmode_toggle()
        if name not in vgk:
            self.object.vertex_groups.new(name)
        self.object.vertex_groups[name].add(wedge_verts, 1, 'REPLACE')
        bpy.ops.object.editmode_toggle()

    def scale_wedge(self, name='wedge1'):
        bpy.ops.mesh.select_all(action='DESELECT')
        vindex = self.object.vertex_groups[name].index
        self.object.vertex_groups.active_index = vindex
        bpy.ops.object.vertex_group_select()
        resize = (4.5 / 6.0, 1.0, 1.0)
        if self.external_edge_rot[0] == 0:
            resize = (1.0, 4.5 / 6.0, 1.0)
        bpy.ops.transform.resize(value=resize)
        bpy.ops.mesh.select_all(action='DESELECT')

    def get_kd_faces(self):
        bm = self.get_bm()
        size = len(bm.faces)
        kd = kdtree.KDTree(size)
        for i, f in enumerate(bm.faces):
            n_v = len(f.verts)
            vs = [v.co for v in f.verts]
            f_co = sum(vs, Vector((0, 0, 0))) / float(n_v)
            kd.insert(f_co, i)
        kd.balance()
        return kd, bm

    def remove_external_edge(self):
        bpy.ops.object.editmode_toggle()
        if 'ExternalEdge' in bpy.data.objects.keys():
            self.object.select = False
            self.external_edge.select = True
            bpy.ops.object.delete()
            self.object.select = True
        bpy.ops.object.editmode_toggle()

    def make_external_edge(self):
        self.remove_external_edge()
        start_vert = self.external_edge_loc + 0.5 * self.external_edge_scale
        x, y, z = self.external_edge_scale
        verts = [
            start_vert,
            start_vert - Vector((0, 0, z)),
            start_vert - Vector((x, 0, z)),
            start_vert - Vector((x, 0, 0)),
            start_vert - Vector((x, y, 0)),
            start_vert - Vector((x, y, z)),
            start_vert - Vector((0, y, z)),
            start_vert - Vector((0, y, 0)),
        ]
        faces = [
            (0, 1, 2, 3),
            (7, 4, 5, 6),
            (0, 3, 4, 7),
            (6, 5, 2, 1),
            (0, 7, 6, 1),
            (4, 3, 2, 5)
        ]
        me = bpy.data.meshes.new('ExternalEdgeMesh')
        self.external_edge = bpy.data.objects.new('ExternalEdge', me)
        bpy.context.scene.objects.link(self.external_edge)
        me.from_pydata(verts, [], faces)
        me.update()
        bpy.ops.object.editmode_toggle()
        self.external_edge.select = True
        self.object.select = False
        bpy.context.scene.objects.active = self.external_edge
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        bool_mod = self.external_edge.modifiers.new(name='bool', type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'CARVE'
        bool_mod.object = self.object
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='bool')
        self.external_edge.location = self.external_edge_loc_final
        self.external_edge.rotation_euler = self.external_edge_rot
        bpy.context.scene.objects.active = self.object
        self.external_edge.select = False
        self.object.select = True
        bpy.ops.object.editmode_toggle()

    def update_external(self):
        self.External_y = False
        self.External_my = False
        self.External_x = False
        self.External_mx = False
        if self.External_edge == 'RIGHT':
            self.External_x = True
        elif self.External_edge == 'LEFT':
            self.External_mx = True
        elif self.External_edge == 'TOP':
            self.External_y = True
        elif self.External_edge == 'BOTTOM':
            self.External_my = True

    def get_weight(self, vert):
        x, y, _ = vert.co
        x0, y0, _ = self.object.location
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
        self.object = bpy.data.objects[name]
        self.update_external()

        # get object
        bm = self.get_bm()

        # get length and width
        self.ly = bm.edges[0].calc_length()
        self.lx = bm.edges[1].calc_length()

        # get number of cuts to make
        B = self.lx * self.ly * self.Fpu**2
        A = self.ly / self.lx
        nx = round(math.sqrt(A * B)) - 1
        ny = round(math.sqrt(B / A)) - 1
        self.report({'INFO'}, '{0} total faces'.format(nx * ny))

        # make loop cuts
        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={'number_cuts': nx, 'edge_index': 0})
        bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={'number_cuts': ny, 'edge_index': 1})
        bpy.ops.mesh.select_all(action='TOGGLE')

        # make vertex groups
        vertex_weights = [self.get_weight(v) for v in bm.verts]
        verts = [v.index for v in bm.verts]
        vgk = self.object.vertex_groups.keys()
        if 'emboss' not in vgk:
            self.object.vertex_groups.new('emboss')
        bpy.ops.object.editmode_toggle()
        for v, w in zip(verts, vertex_weights):
            self.object.vertex_groups['emboss'].add([v], w, 'REPLACE')
        bpy.ops.object.editmode_toggle()

        # Extrude down and close bottom
        bm = self.get_bm()
        extrude_normal = bm.verts[0].normal * -1 * (self.Emboss_height + self.Base_height)
        bound_edges = [e for e in bm.edges if e.is_boundary]
        bound_edges_index = [e.index for e in bound_edges]
        bmesh.ops.extrude_edge_only(bm, edges=bound_edges)
        bm = self.get_bm()
        bound_verts = [v for v in bm.verts if v.is_boundary]
        bound_verts_index = [v.index for v in bound_verts]
        bound_edges = [e for e in bm.edges if e.is_boundary]
        bound_edges_index += [e.index for e in bound_edges]
        bmesh.ops.translate(bm, vec=extrude_normal, verts=bound_verts)
        bmesh.ops.edgeloop_fill(bm, edges=bound_edges)

        # set crease on boundary
        bpy.ops.object.editmode_toggle()
        self.object.vertex_groups['emboss'].remove(bound_verts_index)
        for idx in bound_edges_index:
            self.object.data.edges[idx].select = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.transform.edge_crease(value=1)

        # if external edge create wedge
        if self.External_edge != 'NONE':
            w1, w2 = self.get_wedge_loc()
            self.make_wedge(w1, name='wedge1')
            self.make_wedge(w2, name='wedge2')

        # add modifiers
        tex = bpy.data.textures.keys()
        mod = self.object.modifiers.keys()
        if 'Displacement' not in tex:
            iTex = bpy.data.textures.new('Displacemnt', type='IMAGE')
            iTex.image = bpy.data.images[0]  # assume last image loaded is the correct one
        if 'bump' not in mod:
            displace = self.object.modifiers.new(name='bump', type='DISPLACE')
            displace.texture = iTex
            displace.mid_level = 1
            displace.direction = 'Z'
            displace.vertex_group = 'emboss'
            displace.texture_coords = 'UV'
            displace.strength = self.Emboss_height
            displace.show_in_editmode = True
        else:
            displace = self.object.modifiers['bump']
            displace.strength = self.Emboss_height
        if 'smooth' not in mod:
            subsurf = self.object.modifiers.new(name='smooth', type='SUBSURF')
            subsurf.show_viewport = False
            subsurf.levels = 2
        else:
            subsurf = self.object.modifiers['smooth']
            subsurf.show_viewport = False

        # if external edge create edge
        if self.External_edge != 'NONE':
            self.make_external_edge()
            self.scale_wedge(name='wedge1')
            self.scale_wedge(name='wedge2')
        else:
            self.remove_external_edge()
        subsurf.show_viewport = True
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


if __name__ == '__main__':
    register()
