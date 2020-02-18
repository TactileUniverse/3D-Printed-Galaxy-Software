import bpy
import bmesh
import math
from mathutils import Vector, Matrix
from bpy.props import FloatProperty, EnumProperty, BoolProperty

bl_info = {
    'name': 'Emboss plane',
    'description': 'Emboss and solidify a plane',
    'author': 'Coleman Krawczyk',
    'version': (3, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Menu > Mesh Edit',
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
    Invert_image = BoolProperty(
        name='Invert image',
        default=False,
        description='Invert the emboss direction'
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
    Spike_removal = BoolProperty(
        name='Spike Removal',
        default=False,
        description='Remove sharp spikes from the model'
    )
    Spike_threshold = FloatProperty(
        name='Spike Threshold',
        default=0.75,
        min=0,
        unit='LENGTH',
        description='A single vertex that has a hight difference of at least this threshold from all of its neighbors is flagged as a spike'
    )
    Spike_reduction_factor = FloatProperty(
        name='Spike Reduction Factor',
        default=0.75,
        min=0,
        description='Identified spikes will have their hight lowered by this fraction'
    )

    def get_bm(self):
        bm = bmesh.from_edit_mesh(self.object.data)
        if hasattr(bm.verts, 'ensure_lookup_table'):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
        return bm

    def get_external_rot(self):
        if self.External_edge == 'TOP':
            R = Matrix.Rotation(0, 4, Vector((0, 0, 1)))
        elif self.External_edge == 'BOTTOM':
            R = Matrix.Rotation(math.radians(180), 4, Vector((0, 0, 1)))
        elif self.External_edge == 'RIGHT':
            R = Matrix.Rotation(math.radians(-90), 4, Vector((0, 0, 1)))
        else:
            R = Matrix.Rotation(math.radians(90), 4, Vector((0, 0, 1)))
        T = Matrix.Translation(self.object.location)
        self.external_rot = T @ R @ T.inverted()

    def remove_wedge(self):
        bpy.ops.object.editmode_toggle()
        if 'wedge' in bpy.data.objects.keys():
            self.object.select_set(False)
            bpy.data.objects['wedge'].select_set(True)
            bpy.ops.object.delete()
            self.object.select_set(True)
        bpy.ops.object.editmode_toggle()

    def make_wedge(self):
        self.remove_wedge()
        shift = 0.25 * self.lx
        x = [
            self.object.location[0] - 2.25,
            self.object.location[0] + 2.25,
            self.object.location[0] - 1.125,
            self.object.location[0] + 1.125
        ]
        y = [
            self.object.location[1] + (0.5 * self.ly) + (2 * self.Border_width / 3),
            self.object.location[1] + (0.5 * self.ly) - self.Border_width
        ]
        z = [
            self.object.location[2] - self.Emboss_height - 0.05,
            self.object.location[2] - self.Emboss_height - self.Base_height + 0.05
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
        me = bpy.data.meshes.new('wedge')
        self.wedge = bpy.data.objects.new('wedge', me)
        bpy.context.scene.collection.objects.link(self.wedge)
        me.from_pydata(verts, [], faces)
        me.update()
        bpy.ops.object.editmode_toggle()
        self.wedge.select_set(True)
        self.object.select_set(False)
        bpy.context.view_layer.objects.active = self.wedge
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        self.wedge.location = self.external_rot @ self.wedge.location
        self.wedge.rotation_euler.rotate(self.external_rot)
        bpy.context.view_layer.objects.active = self.object
        self.wedge.select_set(False)
        self.object.select_set(True)
        bpy.ops.object.editmode_toggle()

    def remove_external_edge(self):
        bpy.ops.object.editmode_toggle()
        if 'ExternalEdge' in bpy.data.objects.keys():
            self.object.select_set(False)
            bpy.data.objects['ExternalEdge'].select_set(True)
            bpy.ops.object.delete()
            self.object.select_set(True)
        bpy.ops.object.editmode_toggle()

    def make_external_edge(self):
        self.remove_external_edge()
        x = [
            self.object.location[0] - (0.5 * self.lx),
            self.object.location[0] + (0.5 * self.lx),
            self.object.location[0] + (0.25 * self.lx) - 1.75,
            self.object.location[0] + (0.25 * self.lx) + 1.75,
            self.object.location[0] + (0.25 * self.lx) - 3.5,
            self.object.location[0] + (0.25 * self.lx) + 3.5,
            self.object.location[0] - (0.25 * self.lx) - 1.75,
            self.object.location[0] - (0.25 * self.lx) + 1.75,
            self.object.location[0] - (0.25 * self.lx) - 3.5,
            self.object.location[0] - (0.25 * self.lx) + 3.5
        ]
        y = [
            self.object.location[1] - (0.5 * self.ly) + self.Border_width,
            self.object.location[1] - (0.5 * self.ly),
            self.object.location[1] - (0.5 * self.ly) + (self.Border_width / 3)
        ]
        z = [
            self.object.location[2] + 3,
            self.object.location[2] + 3 + self.Emboss_height + self.Base_height,
            self.object.location[2] + 3 + self.Base_height
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
            (0, 1, 2, 3),
            (0, 3, 7, 4),
            (5, 6, 2, 1),
            (3, 2, 6, 7),
            (15, 14, 13, 12),
            (13, 14, 10, 9),
            (8, 11, 15, 12),
            (11, 10, 14, 15),
            (23, 22, 21, 20),
            (21, 22, 18, 17),
            (16, 19, 23, 20),
            (19, 18, 22, 23),
            (7, 6, 5, 9, 10, 11, 8, 17, 18, 19, 16, 4),
            (4, 16, 20, 21, 17, 8, 12, 13, 9, 5, 1, 0)
        ]
        me = bpy.data.meshes.new('ExternalEdgeMesh')
        self.external_edge = bpy.data.objects.new('ExternalEdge', me)
        bpy.context.scene.collection.objects.link(self.external_edge)
        me.from_pydata(verts, [], faces)
        me.update()
        bpy.ops.object.editmode_toggle()
        self.external_edge.select_set(True)
        self.object.select_set(False)
        bpy.context.view_layer.objects.active = self.external_edge
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        self.external_edge.location = self.external_rot @ self.external_edge.location
        self.external_edge.rotation_euler.rotate(self.external_rot)
        bpy.context.view_layer.objects.active = self.object
        self.external_edge.select_set(False)
        self.object.select_set(True)
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
        x = x + x0
        y = y + y0
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

    def flatten_spikes(self, context):
        bm = self.get_bm()
        depsgraph = context.evaluated_depsgraph_get()
        bm_mod = bmesh.new()
        bm_mod.from_object(self.object, depsgraph)
        bm_mod.verts.ensure_lookup_table()
        for v in bm.verts:
            z = bm_mod.verts[v.index].co.z
            # z = v.co.z
            other_z_dif = 0
            other_z_count = 0
            spike = True
            for e in v.link_edges:
                other_z = bm_mod.verts[e.other_vert(v).index].co.z
                # other_z = e.other_vert(v).co.z
                if abs(z - other_z) < self.Spike_threshold:
                    spike = False
                else:
                    other_z_dif += abs(z - other_z)
                    other_z_count += 1
            if spike:
                # Select the spikes to make them easy to see
                v.select = True
                average_dif = other_z_dif / other_z_count
                v.co.z -= self.Spike_reduction_factor * average_dif
        self.object.data.update()

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
        areas3D = [area for area in context.window.screen.areas if area.type == 'VIEW_3D']
        region = [region for region in areas3D[0].regions if region.type == 'WINDOW']
        for r in region:
            override = {
                'window': context.window,
                'screen': context.window.screen,
                'area': areas3D[0],
                'region': r,
                'scene': context.scene
            }
            try:
                bpy.ops.mesh.loopcut(
                    override,
                    number_cuts=nx,
                    object_index=object.pass_index,
                    edge_index=0
                )
                bpy.ops.mesh.loopcut(
                    override,
                    number_cuts=ny,
                    object_index=object.pass_index,
                    edge_index=1
                )
                break
            except RuntimeError:
                continue

        bpy.ops.mesh.select_all(action='TOGGLE')

        # make vertex groups
        vertex_weights = [self.get_weight(v) for v in bm.verts]
        verts = [v.index for v in bm.verts]
        vgk = self.object.vertex_groups.keys()
        if 'emboss' not in vgk:
            self.object.vertex_groups.new(name='emboss')
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
        bpy.ops.mesh.select_all(action='DESELECT')
        for e in bound_edges:
            e.select = True
        bpy.ops.mesh.fill_grid()
        bottom_face_verts_index = [v.index for v in bm.verts if v.select]
        bpy.ops.mesh.select_all(action='DESELECT')

        # set crease on boundary
        bpy.ops.object.editmode_toggle()
        self.object.vertex_groups['emboss'].remove(bottom_face_verts_index)
        self.object.vertex_groups['emboss'].remove(bound_verts_index)
        for idx in bound_edges_index:
            self.object.data.edges[idx].select = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.transform.edge_crease(value=1)

        # add modifiers
        invert_multiplyer = 1
        if self.Invert_image:
            invert_multiplyer = -1
        tex = bpy.data.textures.keys()
        mod = self.object.modifiers.keys()
        if 'Displacement' not in tex:
            iTex = bpy.data.textures.new('Displacement', type='IMAGE')
            iTex.image = bpy.data.images[0]  # assume last image loaded is the correct one
        else:
            iTex = bpy.data.textures['Displacement']
        if 'bump' not in mod:
            displace = self.object.modifiers.new(name='bump', type='DISPLACE')
            displace.texture = iTex
            displace.direction = 'Z'
            displace.mid_level = 1 * invert_multiplyer
            displace.vertex_group = 'emboss'
            displace.texture_coords = 'UV'
            displace.strength = self.Emboss_height * invert_multiplyer
            displace.show_in_editmode = True
            displace.show_on_cage = True
        else:
            displace = self.object.modifiers['bump']
            displace.strength = self.Emboss_height * invert_multiplyer
            displace.mid_level = 1 * invert_multiplyer
        if 'smooth' not in mod:
            subsurf = self.object.modifiers.new(name='smooth', type='SUBSURF')
            subsurf.quality = 1
            subsurf.show_viewport = True
            subsurf.levels = 2
        else:
            subsurf = self.object.modifiers['smooth']
            subsurf.show_viewport = True

        # if external edge create wedge and edge
        if self.External_edge != 'NONE':
            self.get_external_rot()
            self.make_wedge()
            self.make_external_edge()
        else:
            self.remove_external_edge()
            self.remove_wedge()

        # Deselect everything
        bpy.ops.mesh.select_all(action='DESELECT')

        # remove spikes
        if self.Spike_removal:
            self.flatten_spikes(context)

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
    bpy.types.VIEW3D_MT_edit_mesh.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(EmbossPlane)
    bpy.types.VIEW3D_MT_edit_mesh.remove(add_object_button)


if __name__ == '__main__':
    register()
