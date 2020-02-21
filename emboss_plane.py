import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from bpy.props import FloatProperty, EnumProperty, BoolProperty, StringProperty

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

    Fpu: FloatProperty(
        name='Faces per unit',
        default=2,
        min=0,
        description='Number of faces per unit length across the top of the plane'
    )
    Emboss_height: FloatProperty(
        name='Emboss thickness',
        default=3,
        min=0.1,
        unit='LENGTH',
        description='The Emboss height for the model'
    )
    Invert_image: BoolProperty(
        name='Invert image',
        default=False,
        description='Invert the emboss direction'
    )
    Base_height: FloatProperty(
        name='Base Thickness',
        default=3,
        min=0.1,
        unit='LENGTH',
        description="Thickness of the model's base"
    )
    Border_width: FloatProperty(
        name='Border width',
        default=3,
        min=0.1,
        unit='LENGTH',
        description='Width of the border'
    )
    External_y = False
    External_my = False
    External_x = False
    External_mx = False
    External_edge: EnumProperty(
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
    Noise_filter: FloatProperty(
        name='Noise Filter Size',
        default=1,
        min=1,
        description='Smooth out noise in the image'
    )
    Spike_removal: BoolProperty(
        name='Spike Removal',
        default=False,
        description='Remove sharp spikes from the model'
    )
    Spike_threshold: FloatProperty(
        name='Spike Threshold',
        default=0.75,
        min=0,
        unit='LENGTH',
        description='A single vertex that has a hight difference of at least this threshold from all of its neighbors is flagged as a spike'
    )
    Spike_reduction_factor: FloatProperty(
        name='Spike Reduction Factor',
        default=0.75,
        min=0,
        description='Identified spikes will have their hight lowered by this fraction'
    )
    Name_plate: BoolProperty(
        name='Make Name Plate',
        default=False,
        description='Make a name plate for the model'
    )
    Name_plate_Y: FloatProperty(
        name='Name Plate Height',
        default=20,
        min=0,
        unit='LENGTH',
        description='The height of the name plate'
    )
    Name_plate_text: StringProperty(
        name='Name Plate Text',
        default='Example',
        description='Text for the name plate'
    )
    Name_plate_text_size: FloatProperty(
        name='Name Plate Text Size',
        default=18,
        min=0,
        description='Font size of the text'
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

    def remove_external_object(self, name):
        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    def set_external_location(self, name):
        external_object = self.__getattribute__(name)
        external_object.select_set(True)
        self.object.select_set(False)
        bpy.context.view_layer.objects.active = external_object
        external_object.location = self.external_rot @ external_object.location
        external_object.rotation_euler.rotate(self.external_rot)
        bpy.context.view_layer.objects.active = self.object
        external_object.select_set(False)
        self.object.select_set(True)

    def make_wedge(self):
        self.remove_external_object('wedge')
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
        self.collection.objects.link(self.wedge)
        me.from_pydata(verts, [], faces)
        me.update()
        self.set_external_location('wedge')

    def make_external_edge(self):
        self.remove_external_object('{0}Plate'.format(self.object.name))
        self.remove_external_object('{0}FontObject'.format(self.object.name))
        if self.Name_plate:
            plate_Y = self.Name_plate_Y
            text = self.Name_plate_text
        else:
            plate_Y = self.Border_width
            text = ''
        # more cursor to the correct location
        if self.External_edge == 'TOP':
            cursor_location = Vector((
                0,
                (plate_Y - self.ly) / 2,
                3 + (self.Emboss_height + self.Base_height) / 2
            ))
            cursor_rotation = Euler((0, 0, math.radians(180)))
            size_x = self.lx
        elif self.External_edge == 'BOTTOM':
            cursor_location = Vector((
                0,
                (self.ly - plate_Y) / 2,
                3 + (self.Emboss_height + self.Base_height) / 2
            ))
            cursor_rotation = Euler((0, 0, 0))
            size_x = self.lx
        elif self.External_edge == 'RIGHT':
            cursor_location = Vector((
                (plate_Y - self.lx) / 2,
                0,
                3 + (self.Emboss_height + self.Base_height) / 2
            ))
            cursor_rotation = Euler((0, 0, math.radians(90)))
            size_x = self.ly
        else:
            cursor_location = Vector((
                (self.lx - plate_Y) / 2,
                0,
                3 + (self.Emboss_height + self.Base_height) / 2
            ))
            cursor_rotation = Euler((0, 0, math.radians(-90)))
            size_x = self.ly
        bpy.context.scene.cursor.location = cursor_location + self.object.location
        bpy.context.scene.cursor.rotation_euler = cursor_rotation
        # make the name plate with no text
        bpy.ops.object.name_plate(
            Size_x=size_x,
            Size_y=plate_Y,
            Size_z=self.Emboss_height + self.Base_height,
            Text=text,
            Text_size=self.Name_plate_text_size,
            Notches=True,
            Base_height=self.Base_height,
            Border_width=self.Border_width,
            Object_name=self.object.name
        )
        bpy.context.scene.collection.objects.unlink(bpy.data.objects['{0}Plate'.format(self.object.name)])
        bpy.context.scene.collection.objects.unlink(bpy.data.objects['{0}FontObject'.format(self.object.name)])
        self.collection.objects.link(bpy.data.objects['{0}Plate'.format(self.object.name)])
        self.collection.objects.link(bpy.data.objects['{0}FontObject'.format(self.object.name)])

    def make_internal_name_plate(self):
        self.remove_external_object('{0}Plate'.format(self.object.name))
        self.remove_external_object('{0}FontObject'.format(self.object.name))
        # more cursor to the correct location
        bpy.context.scene.cursor.location = Vector((
            0,
            (0.5 * self.ly) + (0.5 * self.Name_plate_Y) - (0.25 * self.Border_width),
            -(self.Emboss_height + self.Base_height) / 2
        )) + self.object.location
        bpy.context.scene.cursor.rotation_euler = Euler((0, 0, 0))
        # make the name plate
        bpy.ops.object.name_plate(
            Size_x=self.lx,
            Size_y=self.Name_plate_Y + (0.5 * self.Border_width),
            Size_z=self.Emboss_height + self.Base_height,
            Text=self.Name_plate_text,
            Text_size=self.Name_plate_text_size,
            Notches=False,
            Base_height=self.Base_height,
            Border_width=self.Border_width,
            Object_name=self.object.name
        )
        bpy.context.scene.collection.objects.unlink(bpy.data.objects['{0}Plate'.format(self.object.name)])
        bpy.context.scene.collection.objects.unlink(bpy.data.objects['{0}FontObject'.format(self.object.name)])
        self.collection.objects.link(bpy.data.objects['{0}Plate'.format(self.object.name)])
        self.collection.objects.link(bpy.data.objects['{0}FontObject'.format(self.object.name)])

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

    def get_weight(
            self,
            vert,
            object_location,
            lx,
            ly,
            Border_width,
            External_y,
            External_my,
            External_x,
            External_mx
        ):
        # Pass all arguments by value since this is called a
        # large number of times and Blender's self.__getattribute__
        # very slow (saves 50% compute time doing it this way)
        x, y, _ = vert.co
        x0, y0, _ = object_location
        x = x + x0
        y = y + y0
        x2 = x0 + (0.5 * lx)
        x1 = x2 - Border_width
        y2 = y0 + (0.5 * ly)
        y1 = y2 - Border_width
        xm2 = x0 - (0.5 * lx)
        xm1 = xm2 + Border_width
        ym2 = y0 - (0.5 * ly)
        ym1 = ym2 + Border_width
        if (not External_y and (y > y1)) or \
           (not External_my and (y < ym1)) or \
           (not External_x and (x > x1)) or \
           (not External_mx and (x < xm1)):
            return 0
        else:
            return 1

    def flatten_spikes(
            self,
            context,
            Spike_threshold,
            Spike_reduction_factor,
            Invert_image
        ):
        bm = self.get_bm()
        # make copy of mesh with modifiers applies
        depsgraph = context.evaluated_depsgraph_get()
        object_mod = self.object.evaluated_get(depsgraph)
        bm_mod = bmesh.new()
        bm_mod.from_mesh(bpy.data.meshes.new_from_object(object_mod))
        bm_mod.verts.ensure_lookup_table()

        # loop over emboss group looking for spikes
        for v_index in self.verts_1:
            v = bm.verts[v_index]
            z = bm_mod.verts[v_index].co.z
            other_z_dif = 0
            other_z_count = 0
            spike = True
            for e in v.link_edges:
                other_z = bm_mod.verts[e.other_vert(v).index].co.z
                if abs(z - other_z) < Spike_threshold:
                    spike = False
                else:
                    other_z_dif += abs(z - other_z)
                    other_z_count += 1
            if spike:
                # Select the spikes to make them easy to see
                v.select = True
                average_dif = other_z_dif / other_z_count
                if Invert_image:
                    v.co.z += Spike_reduction_factor * average_dif
                else:
                    v.co.z -= Spike_reduction_factor * average_dif
        self.object.data.update()

    def execute(self, context):
        object = context.active_object
        name = object.name
        self.object = bpy.data.objects[name]
        if len(self.object.users_collection) > 0:
            self.collection = self.object.users_collection[0]
        else:
            self.collection = bpy.context.scene.collection
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

        bpy.ops.mesh.select_all(action='DESELECT')

        # make vertex groups
        if 'emboss' not in self.object.vertex_groups.keys():
            self.object.vertex_groups.new(name='emboss')

        # apply weights
        weight_args = (
            self.object.location,
            self.lx,
            self.ly,
            self.Border_width,
            self.External_y,
            self.External_my,
            self.External_x,
            self.External_mx
        )
        bm = self.get_bm()
        bm.verts.layers.deform.verify()
        deform = bm.verts.layers.deform.active
        self.verts_1 = []
        for v in bm.verts:
            w = self.get_weight(v, *weight_args)
            v[deform][0] = w
            if w == 1:
                self.verts_1.append(v.index)

        # Extrude down and close bottom
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

        # set vertex group values
        bm = self.get_bm()
        bm.verts.layers.deform.verify()
        deform = bm.verts.layers.deform.active
        for v_index in bottom_face_verts_index + bound_verts_index:
            bm.verts[v_index][deform][0] = 0

        # set crease on boundary
        for e_index in bound_edges_index:
            bm.edges[e_index].select = True
        bpy.ops.transform.edge_crease(value=1)

        # add modifiers
        invert_multiplyer = 1
        if self.Invert_image:
            invert_multiplyer = -1
        tex = bpy.data.textures.keys()
        mod = self.object.modifiers.keys()
        if 'Displacement' not in tex:
            iTex = bpy.data.textures.new('Displacement', type='IMAGE')
        else:
            iTex = bpy.data.textures['Displacement']
        iTex.image = bpy.data.images[0]  # assume last image loaded is the correct one
        iTex.filter_size = self.Noise_filter
        if 'bump' not in mod:
            displace = self.object.modifiers.new(name='bump', type='DISPLACE')
            displace.texture = iTex
            displace.direction = 'Z'
            displace.vertex_group = 'emboss'
            displace.texture_coords = 'UV'
            displace.show_in_editmode = True
            displace.show_on_cage = True
        else:
            displace = self.object.modifiers['bump']
        displace.strength = self.Emboss_height * invert_multiplyer
        displace.mid_level = 1 * invert_multiplyer

        # Deselect all verts
        bpy.ops.mesh.select_all(action='DESELECT')

        # Spike removal
        if self.Spike_removal:
            # for spike removal temp remove the smoothing modifier
            if 'smooth' in mod:
                subsurf = self.object.modifiers['smooth']
                self.object.modifiers.remove(subsurf)
            self.flatten_spikes(
                context,
                self.Spike_threshold,
                self.Spike_reduction_factor,
                self.Invert_image
            )

        # if external or name plate edge create wedge and edge/name plate
        if self.External_edge != 'NONE':
            self.get_external_rot()
            self.make_wedge()
            self.make_external_edge()
        else:
            self.remove_external_object('wedge')
            if self.Name_plate:
                self.make_internal_name_plate()
            else:
                self.remove_external_object('{0}Plate'.format(self.object.name))
                self.remove_external_object('{0}FontObject'.format(self.object.name))

        # Smooth surface
        if 'smooth' not in mod:
            subsurf = self.object.modifiers.new(name='smooth', type='SUBSURF')
            subsurf.quality = 1
            subsurf.show_viewport = True
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
    bpy.types.VIEW3D_MT_edit_mesh.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(EmbossPlane)
    bpy.types.VIEW3D_MT_edit_mesh.remove(add_object_button)


if __name__ == '__main__':
    register()
