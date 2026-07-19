from multiprocessing import context

import bpy

# --- METADATA ---

bl_info = {
    "name": "CK-CMD Collision Generator",
    "author": "You",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Object > CK-CMD > Generate MOPP Collision nodes",
    "description": "Generate MOPP collision nodes from active object",
    "category": "Object",
}

# --- FUNCTIONS ---


def generate_nodes_from_active(self, mat_name):

    myObj = bpy.context.active_object

    if myObj is None:
        self.report({"ERROR"}, "No active object selected to generate nodes from!")
    
    elif myObj.type != 'MESH':
        self.report({"ERROR"}, "Active object is not a mesh! Please select a mesh object.")

    else:
        # Grab the top-level collection of the active object, or use the scene collection if none exists
        top_coll = (
            myObj.users_collection[0] if myObj.users_collection else bpy.context.scene.collection
        )

        col_name = "Collision_" + myObj.name
        col_coll = bpy.data.collections.get(col_name)
        
        # Check if there is an existing "Collision" collection in the top-level collection
        if col_coll is None:
            col_coll = bpy.data.collections.new(col_name)
            top_coll.children.link(col_coll)

        # Check if name is in use
        rb_name = myObj.name + "_rb"
        suffix = 1
        while rb_name in bpy.data.objects:
            # If it exists, append a number to the name to make it unique
            # :03d formats the number with leading zeros, treats it like an integer
            rb_name = f"{myObj.name}_rb_{suffix:03d}"
            suffix += 1

        # Create the empty and add to the collection
        rb = bpy.data.objects.new(rb_name, None)
        rb.empty_display_type = "PLAIN_AXES"
        col_coll.objects.link(rb)

        # Create MOPP node
        rb_mopp_name = myObj.name + "_rb_mopp"
        suffix = 1
        while rb_mopp_name in bpy.data.objects:
            rb_mopp_name = f"{myObj.name}_rb_mopp_{suffix:03d}"
            suffix += 1

        rb_mopp = bpy.data.objects.new(rb_mopp_name, None)
        rb_mopp.empty_display_type = "PLAIN_AXES"
        rb_mopp.parent = rb
        col_coll.objects.link(rb_mopp)

        # Copy the mesh data from the original object to a new collision mesh
        rb_mopp_mesh_data = myObj.data.copy()
        rb_mopp_mesh_name = myObj.name + "_rb_mopp_mesh"
        suffix = 1
        while rb_mopp_mesh_name in bpy.data.meshes:
            rb_mopp_mesh_name = f"{myObj.name}_rb_mopp_mesh_{suffix:03d}"
            suffix += 1
        rb_mopp_mesh_data.name = rb_mopp_mesh_name
        rb_mopp_mesh = bpy.data.objects.new(rb_mopp_mesh_data.name, rb_mopp_mesh_data)
        rb_mopp_mesh.parent = rb_mopp
        col_coll.objects.link(rb_mopp_mesh)

        # Clear all materials from the collision mesh
        if rb_mopp_mesh.data.materials:
            rb_mopp_mesh.data.materials.clear()

        # Create a new material if it doesn't exist
        if not mat_name in bpy.data.materials:
            myMat = bpy.data.materials.new(name=mat_name)
        else:
            myMat = bpy.data.materials[mat_name]

        # Assign the new material to the collision mesh
        rb_mopp_mesh.data.materials.append(myMat)


# --- INTERFACE ---


# This defines the list item objects added to the UIList
class MaterialsDropdownItem(bpy.types.PropertyGroup):
    # Define properties without using variable annotations
    name = bpy.props.StringProperty(name="Item Name")
    description = bpy.props.StringProperty(name="Item Description")


# This defines the list interface, which extends class UIList
class MaterialsDropdownInterface(bpy.types.UIList):

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        # This draws each row in the list view
        layout.label(text=item.name)


# This defines what the dropdown does
class MaterialsDropdownOperator(bpy.types.Operator):

    bl_idname = "object.materials_dropdown_operator"
    bl_label = "Choose a material."
    bl_options = {"REGISTER", "UNDO"}

    # Checking if there is an active object and if it is a mesh
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.select_get() and context.active_object.type == 'MESH'

    def execute(self, context):
        # Check if we've chosen a material before.
        saved_ix = context.scene.havok_material_list_current_index
        if len(context.scene.havok_material_list) == 0 or saved_ix < 0:
            self.report({"WARNING"}, "No material selected.")
            return {"CANCELLED"}

        else:
            selected_item = context.scene.havok_material_list[saved_ix]
            self.report(
                {"INFO"}, f"Creating new MOPP chain with material  {selected_item.name}"
            )
            ok = generate_nodes_from_active(self, selected_item.name)
            if ok:
                self.report({"INFO"}, "Nodes generated successfully.")
                return {"FINISHED"}
            return {"CANCELLED"}

    def invoke(self, context, event):
        # Populate the list of materials if you haven't already.
        if len(context.scene.havok_material_list) == 0:
            list_materials = [
                "SKY_HAV_MAT_ALDUIN",
                "SKY_HAV_MAT_ARMOR_HEAVY",
                "SKY_HAV_MAT_ARMOR_LIGHT",
                "SKY_HAV_MAT_ARROW",
                "SKY_HAV_MAT_ASH",
                "SKY_HAV_MAT_BARREL",
                "SKY_HAV_MAT_BASKET",
                "SKY_HAV_MAT_BONE_ACTOR",
                "SKY_HAV_MAT_BONE",
                "SKY_HAV_MAT_BOOK",
                "SKY_HAV_MAT_BOTTLE_SMALL",
                "SKY_HAV_MAT_BOTTLE",
                "SKY_HAV_MAT_BOULDER_LARGE",
                "SKY_HAV_MAT_BOULDER_MEDIUM",
                "SKY_HAV_MAT_BOULDER_SMALL",
                "SKY_HAV_MAT_CARPET",
                "SKY_HAV_MAT_CARRIAGE_WHEEL",
                "SKY_HAV_MAT_CERAMIC",
                "SKY_HAV_MAT_CHAIN",
                "SKY_HAV_MAT_CLOTH",
                "SKY_HAV_MAT_COIN",
                "SKY_HAV_MAT_DIRT",
                "SKY_HAV_MAT_DRAGON",
                "SKY_HAV_MAT_GHOST",
                "SKY_HAV_MAT_GLASS",
                "SKY_HAV_MAT_GRASS",
                "SKY_HAV_MAT_GRAVEL",
                "SKY_HAV_MAT_ICE_FORM",
                "SKY_HAV_MAT_ICE",
                "SKY_HAV_MAT_INSECT",
                "SKY_HAV_MAT_MEAT",
                "SKY_HAV_MAT_METAL_CHAIN",
                "SKY_HAV_MAT_METAL_HEAVY",
                "SKY_HAV_MAT_METAL_LIGHT",
                "SKY_HAV_MAT_METAL_SOLID",
                "SKY_HAV_MAT_MUD",
                "SKY_HAV_MAT_ORGANIC_LARGE",
                "SKY_HAV_MAT_ORGANIC",
                "SKY_HAV_MAT_POTS_AND_PANS",
                "SKY_HAV_MAT_SAND",
                "SKY_HAV_MAT_SHIELD_HEAVY",
                "SKY_HAV_MAT_SHIELD_LIGHT",
                "SKY_HAV_MAT_SKIN_LARGE",
                "SKY_HAV_MAT_SKIN_METAL_LARGE",
                "SKY_HAV_MAT_SKIN_METAL_SMALL",
                "SKY_HAV_MAT_SKIN_SKELETON",
                "SKY_HAV_MAT_SKIN_SMALL",
                "SKY_HAV_MAT_SKIN",
                "SKY_HAV_MAT_SNOW",
                "SKY_HAV_MAT_STAIRS_GLASS",
                "SKY_HAV_MAT_STAIRS_METAL",
                "SKY_HAV_MAT_STAIRS_SNOW",
                "SKY_HAV_MAT_STAIRS_STONE_BROKEN",
                "SKY_HAV_MAT_STAIRS_STONE",
                "SKY_HAV_MAT_STAIRS_WOOD",
                "SKY_HAV_MAT_STONE_AS_STAIRS",
                "SKY_HAV_MAT_STONE_BROKEN",
                "SKY_HAV_MAT_STONE_HEAVY",
                "SKY_HAV_MAT_STONE",
                "SKY_HAV_MAT_WARD",
                "SKY_HAV_MAT_WATER_PUDDLE",
                "SKY_HAV_MAT_WATER",
                "SKY_HAV_MAT_WEAPON_AXE_BLOCK",
                "SKY_HAV_MAT_WEAPON_AXE",
                "SKY_HAV_MAT_WEAPON_BLADE_1HAND_BLOCK",
                "SKY_HAV_MAT_WEAPON_BLADE_1HAND_SMALL",
                "SKY_HAV_MAT_WEAPON_BLADE_1HAND",
                "SKY_HAV_MAT_WEAPON_BLADE_2HAND_BLOCK",
                "SKY_HAV_MAT_WEAPON_BLADE_2HAND",
                "SKY_HAV_MAT_WEAPON_BLUNT_1HAND_BLOCK",
                "SKY_HAV_MAT_WEAPON_BLUNT_1HAND",
                "SKY_HAV_MAT_WEAPON_BLUNT_2HAND_BLOCK",
                "SKY_HAV_MAT_WEAPON_BLUNT_2HAND",
                "SKY_HAV_MAT_WEAPON_BOWS_AND_STAVES_BLOCK",
                "SKY_HAV_MAT_WEAPON_BOWS_AND_STAVES",
                "SKY_HAV_MAT_WEB",
                "SKY_HAV_MAT_WOOD_AS_STAIRS",
                "SKY_HAV_MAT_WOOD_HEAVY",
                "SKY_HAV_MAT_WOOD_LIGHT",
                "SKY_HAV_MAT_WOOD",
            ]

            # Populate the UIList with the temporary list items
            for i in range(len(list_materials)):
                item = context.scene.havok_material_list.add()
                item.name = f"{list_materials[i]}"

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Draw the template_list. Blender automatically builds the search bar at the bottom!
        layout.template_list(
            "MaterialsDropdownInterface",
            "",
            scene,
            "havok_material_list",
            scene,
            "havok_material_list_current_index",
            rows=8,
        )


class VIEW3D_MT_ckcmd(bpy.types.Menu):
    bl_label = "CK-CMD"
    bl_idname = "VIEW3D_MT_ckcmd"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            MaterialsDropdownOperator.bl_idname,
            text="Generate MOPP Collision nodes",
        )


# Registering the classes

classes = (
    MaterialsDropdownItem,
    MaterialsDropdownInterface,
    MaterialsDropdownOperator,
    VIEW3D_MT_ckcmd,
)


def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_ckcmd", text="CK-CMD")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Save variables to the Scene (CollectionProperty != an actual Collection object)
    bpy.types.Scene.havok_material_list = bpy.props.CollectionProperty(
        type=MaterialsDropdownItem
    )
    bpy.types.Scene.havok_material_list_current_index = bpy.props.IntProperty(
        name="Active Index", default=0
    )
    bpy.types.VIEW3D_MT_object.append(menu_func)


# Required for GC!
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    scene_type = bpy.types.Scene
    if hasattr(scene_type, "havok_material_list"):
        del scene_type.havok_material_list 
    if hasattr(scene_type, "havok_material_list_current_index"):
        del scene_type.havok_material_list_current_index
    try:
        bpy.types.VIEW3D_MT_object.remove(menu_func)
    except ValueError:
        pass
