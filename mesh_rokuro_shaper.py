import bmesh
import bpy
import math


bl_info = {
    "name": "Rokuro Shaper",
    "description": "Adjust mesh shape as you use rokuro",
    "author": "Takashi Toyoshima",
    "version": (0, 2),
    "blender": (2, 76, 0),
    "location": "View3D > Misc > Rokuro Shaper",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}


class RokuroProperties(bpy.types.PropertyGroup):
    granularity = bpy.props.IntProperty(default=10, min=1, max=20)
    z0 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z1 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z2 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z3 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z4 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z5 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z6 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z7 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z8 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z9 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z10 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z11 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z12 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z13 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z14 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z15 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z16 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z17 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z18 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    z19 = bpy.props.FloatProperty(default=1.0, min=0.0, max=2.0)
    min_z = bpy.props.FloatProperty()
    max_z = bpy.props.FloatProperty()
    axis = bpy.props.StringProperty(default="z")


class RokuroScanOperator(bpy.types.Operator):
    bl_idname = "mesh.rokuro_op_scan"
    bl_label = "Scan target mesh"

    scanned_object = None
    scanned_co = []

    def invoke(self, context, event):
        obj = context.object
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        rotate = obj.rotation_euler
        rotate_x = math.floor(rotate[0])
        rotate_y = math.floor(rotate[1])
        rotate_z = math.floor(rotate[2])
        # Roughly check rotation to detect the right Z axis in 3D View window.
        if rotate_x == 1 and rotate_y == 0 and rotate_z == 0:
            obj.rokuro.axis = "y"
        else:
            obj.rokuro.axis = "z"
        axis = { "x": 0, "y": 1, "z": 2 }[obj.rokuro.axis]

        min_z = 0
        max_z = 0
        for v in bm.verts:
            min_z = v.co[axis]
            max_z = v.co[axis]
            break
        self.__class__.scanned_co = []

        for v in bm.verts:
            min_z = min(min_z, v.co[axis])
            max_z = max(max_z, v.co[axis])
            self.__class__.scanned_co.append(v.co.copy())

        obj.rokuro.min_z = min_z
        obj.rokuro.max_z = max_z
        self.__class__.scanned_object = obj

        bm.free()

        return {"FINISHED"}


class RokuroShapeOperator(bpy.types.Operator):
    bl_idname = "mesh.rokuro_op_shape"
    bl_label = "Adopt"

    scanned_object = None
    scanned_co = []

    def invoke(self, context, event):
        obj = context.object
        if obj.rokuro.min_z == obj.rokuro.max_z:
            return

        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        start = obj.rokuro.max_z
        step = (start - obj.rokuro.min_z) / obj.rokuro.granularity

        i = 0
        axis = { "x": 0, "y": 1, "z": 2 }[obj.rokuro.axis]
        for v in bm.verts:
            rank = min(math.floor((start - RokuroScanOperator.scanned_co[i][axis]) / step), obj.rokuro.granularity - 1)
            key = "z%d" % rank
            zoom = 1.0 if not obj.rokuro.is_property_set(key) else obj.rokuro[key]
            if axis != 0:
                v.co.x = RokuroScanOperator.scanned_co[i].x * zoom
            if axis != 1:
                v.co.y = RokuroScanOperator.scanned_co[i].y * zoom
            if axis != 2:
                v.co.z = RokuroScanOperator.scanned_co[i].z * zoom
            i += 1

        bm.to_mesh(mesh)
        bm.free()

        mesh.update()

        return {"FINISHED"}


class RokuroPanel(bpy.types.Panel):
    bl_label = "Rokuro Shaper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.label("Target mesh: %s" % obj.name)

        row = layout.row();
        row.prop(obj.rokuro, "granularity")

        row = layout.row()
        row.operator(RokuroScanOperator.bl_idname)

        row = layout.row()
        row.label("Z Range: %.1f - %.1f" % (obj.rokuro.min_z, obj.rokuro.max_z))

        start = obj.rokuro.max_z
        step = (start - obj.rokuro.min_z) / obj.rokuro.granularity
        for i in range(obj.rokuro.granularity):
            row = layout.row()
            row.prop(obj.rokuro, "z%d" % i, text="Z %.1f - %.1f" % (start, start - step))
            start -= step

        if RokuroScanOperator.scanned_object != obj:
            return

        row = layout.row()
        row.operator(RokuroShapeOperator.bl_idname)


def register():
    bpy.utils.register_class(RokuroProperties)
    bpy.types.Object.rokuro = bpy.props.PointerProperty(type=RokuroProperties)
    bpy.utils.register_class(RokuroScanOperator)
    bpy.utils.register_class(RokuroShapeOperator)
    bpy.utils.register_class(RokuroPanel)


def unregister():
    bpy.utils.unregister_class(RokuroPanel)
    bpy.utils.unregister_class(RokuroShapeOperator)
    bpy.utils.unregister_class(RokuroScanOperator)
    bpy.types.Object.rokuro = None
    bpy.utils.unregister_class(RokuroProperties)


if __name__ == "__main__":
    register()

