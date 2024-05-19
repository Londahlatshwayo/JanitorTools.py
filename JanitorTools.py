import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

class OBJECT_PT_ScaleDisplay(bpy.types.Panel):
    bl_label = "JanitorTools"
    bl_idname = "PT_ScaleDisplay"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JanitorTools'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("object.toggle_wireframe", text="Toggle Wireframe")
        

        row = layout.row()
        row.operator("object.reset_transforms", text="Reset Transforms")
        

        row = layout.row()
        row.operator("object.freeze_transforms", text="Freeze Transforms")
        

        row = layout.row()
        row.operator("object.delete_materials", text="Delete Materials")
        

        row = layout.row()
        row.operator("object.add_material_slot", text="Add Material Slot")
        

        row = layout.row()
        row.operator("object.rename_selected", text="Rename Selected")
        

        row = layout.row()
        row.operator("object.batch_export_fbx", text="Batch Export FBX")
        

        row = layout.row()
        row.operator("object.join_meshes", text="Join Meshes")
        
        
        row = layout.row()
        row.operator("object.triangulate_faces", text="Triangulate NGONS")
        
        
        row = layout.row()
        row.operator("object.inset_and_poke", text="Inset and Poke")

        row.operator("object.inset_and_triangulate", text="Inset and Triangulate")
        
        
        row = layout.row()
        row.operator("object.select_and_mark_seam", text="Seam Loop")
        
        row.operator("object.select_and_clear_seam", text="Clear Seam Loop")
        
                

        obj = context.active_object
        if obj is not None:
            layout.label(text="Selected Object: " + obj.name)
            layout.label(text="Scale: " + str(obj.scale))
            layout.label(text="Dimensions: " + str(obj.dimensions))

            material_slots = obj.material_slots
            if material_slots:
                layout.label(text="Materials:")
                for index, material_slot in enumerate(material_slots):
                    row = layout.row(align=True)
                    if material_slot.material:
                        row.prop(material_slot.material, "name", text="")  # Dropdown to select the material
                    else:
                        row.label(text="Slot {}: None".format(index))
        else:
            layout.label(text="No active object selected.")
            
            
            
class OBJECT_OT_ToggleWireframe(bpy.types.Operator):
    bl_label = "Toggle Wireframe"
    bl_idname = "object.toggle_wireframe"
    bl_description = "Toggle Wireframe Display for Selected Objects"

    def execute(self, context):
        # Get the selected objects
        selected_objects = context.selected_objects
        
        # Toggle wireframe display for each selected object
        for obj in selected_objects:
            if obj.type == 'MESH':
                obj.show_wire = not obj.show_wire
        
        return {'FINISHED'}
    
    

class OBJECT_OT_ResetTransforms(bpy.types.Operator):
    bl_idname = "object.reset_transforms"
    bl_label = "Reset Transforms"

    def execute(self, context):
        obj = context.active_object
        if obj is not None:
            obj.location = (0, 0, 0)
            obj.rotation_euler = (0, 0, 0)
            obj.scale = (1, 1, 1)
            self.report({'INFO'}, "Transforms reset for {}".format(obj.name))
        else:
            self.report({'WARNING'}, "No active object selected.")
        return {'FINISHED'}

class OBJECT_OT_FreezeTransforms(bpy.types.Operator):
    bl_idname = "object.freeze_transforms"
    bl_label = "Freeze Transforms"

    def execute(self, context):
        obj = context.active_object
        if obj is not None:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            self.report({'INFO'}, "Transforms frozen for {}".format(obj.name))
        else:
            self.report({'WARNING'}, "No active object selected.")
        return {'FINISHED'}

class OBJECT_OT_DeleteMaterials(bpy.types.Operator):
    bl_idname = "object.delete_materials"
    bl_label = "Delete Materials"

    def execute(self, context):
        obj = context.active_object
        if obj is not None:
            obj.data.materials.clear()
            for material_slot in obj.material_slots:
                material_slot.material = None
            self.report({'INFO'}, "Materials deleted for {}".format(obj.name))
        else:
            self.report({'WARNING'}, "No active object selected.")
        return {'FINISHED'}

class OBJECT_OT_AddMaterialSlot(bpy.types.Operator):
    bl_idname = "object.add_material_slot"
    bl_label = "Add Material Slot"
    
    new_material_name: bpy.props.StringProperty(name="New Material Name", default="M_")

    def execute(self, context):
        obj = context.active_object
        if obj is not None:
            if not self.new_material_name.startswith("M_"):
                self.report({'WARNING'}, "Material name should start with 'M_'")
                return {'CANCELLED'}
            
            material = bpy.data.materials.new(name=self.new_material_name)  # Create a new material with the specified name
            obj.data.materials.append(material)  # Append the new material to the object's material list
            self.report({'INFO'}, "Material slot added to {} with name '{}'".format(obj.name, self.new_material_name))
        else:
            self.report({'WARNING'}, "No active object selected.")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_RenameSelected(bpy.types.Operator):
    bl_idname = "object.rename_selected"
    bl_label = "Rename Selected"
    
    new_name: bpy.props.StringProperty(name="New Name", default="SM_")

    def execute(self, context):
        obj = context.active_object
        if obj is not None:
            if not self.new_name.startswith("SM_"):
                self.report({'WARNING'}, "New name should start with 'SM_'")
                return {'CANCELLED'}
            
            obj.name = self.new_name
            self.report({'INFO'}, "Object renamed to {}".format(obj.name))
        else:
            self.report({'WARNING'}, "No active object selected.")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OBJECT_OT_BatchExportFBX(bpy.types.Operator, ExportHelper):
    bl_idname = "object.batch_export_fbx"
    bl_label = "Batch Export FBX"
    bl_options = {'REGISTER'}

    filename_ext = ".fbx"

    filter_glob: StringProperty(default="*.fbx", options={'HIDDEN'})

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected for export")
            return {'CANCELLED'}

        # Check prefixes for objects and materials
        for obj in selected_objects:
            if not obj.name.startswith("SM_"):
                self.report({'WARNING'}, "Object '{}' does not have the correct prefix 'SM_'".format(obj.name))
                return {'CANCELLED'}
            for material_slot in obj.material_slots:
                if material_slot.material and not material_slot.material.name.startswith("M_"):
                    self.report({'WARNING'}, "Material '{}' on object '{}' does not have the correct prefix 'M_'".format(material_slot.material.name, obj.name))
                    return {'CANCELLED'}

        # Export the objects
        for obj in selected_objects:
            filepath = self.filepath
            if not filepath.lower().endswith('.fbx'):
                filepath += '.fbx'
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True, object_types={'MESH'})

        self.report({'INFO'}, "Exported {} objects to FBX".format(len(selected_objects)))
        return {'FINISHED'}

class OBJECT_OT_JoinMeshes(bpy.types.Operator):
    bl_idname = "object.join_meshes"
    bl_label = "Join Meshes"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) <= 1:
            self.report({'WARNING'}, "Select at least two objects to join")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        selected_objects[0].select_set(True)
        bpy.context.view_layer.objects.active = selected_objects[0]

        for obj in selected_objects[1:]:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.join()

        self.report({'INFO'}, "Joined {} objects into {}".format(len(selected_objects), selected_objects[0].name))
        return {'FINISHED'}
    
class OBJECT_OT_triangulate_faces(bpy.types.Operator):
    bl_idname = "object.triangulate_faces"
    bl_label = "Triangulate Faces"
    
    def execute(self, context):
        obj = bpy.context.active_object

        if obj and obj.type == 'MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            self.report({'ERROR'}, "No active mesh object found.")
        return {'FINISHED'}


class OBJECT_OT_InsetAndPoke(bpy.types.Operator):
    bl_idname = "object.inset_and_poke"
    bl_label = "Inset and Poke"
    
    def execute(self, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            selected_faces = [f for f in obj.data.polygons if f.select]

            if selected_faces:
                bpy.ops.mesh.inset(thickness=0.1)
                bpy.ops.mesh.poke()
            else:
                self.report({'ERROR'}, "No faces selected.")
        else:
            self.report({'ERROR'}, "No mesh object selected.")

        return {'FINISHED'}   
 
class OBJECT_OT_InsetAndTriangulate(bpy.types.Operator):
    bl_idname = "object.inset_and_triangulate"
    bl_label = "Inset and Triangulate"
    
    def execute(self, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            selected_faces = [f for f in obj.data.polygons if f.select]

            if selected_faces:
                bpy.ops.mesh.inset(thickness=0.1)
                bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            else:
                self.report({'ERROR'}, "No faces selected.")
        else:
            self.report({'ERROR'}, "No mesh object selected.")

        return {'FINISHED'}
    
  
  # Operator class to select an entire edge loop and mark it as seam
class SelectAndMarkSeamOperator(bpy.types.Operator):
    bl_idname = "object.select_and_mark_seam"
    bl_label = "Select Edge Loop and Mark Seam"
    
    def execute(self, context):
        # Get the active object and its mesh data
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh or does not exist.")
            return {'CANCELLED'}
        
        # Ensure we are in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            bpy.ops.mesh.select_mode(type="EDGE")  # Change selection mode to edges
            bpy.ops.mesh.loop_multi_select(ring=False)  # Select edge loop
            bpy.ops.mesh.mark_seam()  # Mark selected edges as seam
        except RuntimeError:
            self.report({'ERROR'}, "Unable to select edge loop or mark seam.")
            return {'CANCELLED'}

        return {'FINISHED'}
    
      
      # Operator class to select an entire edge loop and mark it as seam
class SelectAndClearSeamOperator(bpy.types.Operator):
    bl_idname = "object.select_and_clear_seam"
    bl_label = "Select Edge Loop and Mark Seam"
    
    def execute(self, context):
        # Get the active object and its mesh data
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh or does not exist.")
            return {'CANCELLED'}
        
        # Ensure we are in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            bpy.ops.mesh.select_mode(type="EDGE")  # Change selection mode to edges
            bpy.ops.mesh.loop_multi_select(ring=False)  # Select edge loop
            bpy.ops.mesh.mark_seam(clear=True)  # Clear selected edges as seam
        except RuntimeError:
            self.report({'ERROR'}, "Unable to select edge loop or mark seam.")
            return {'CANCELLED'}

        return {'FINISHED'}
    
    
      
# Register and unregister the panel and operators
def register():
    bpy.utils.register_class(OBJECT_PT_ScaleDisplay)
    bpy.utils.register_class(OBJECT_OT_ToggleWireframe)
    bpy.utils.register_class(OBJECT_OT_ResetTransforms)
    bpy.utils.register_class(OBJECT_OT_FreezeTransforms)
    bpy.utils.register_class(OBJECT_OT_DeleteMaterials)
    bpy.utils.register_class(OBJECT_OT_AddMaterialSlot)
    bpy.utils.register_class(OBJECT_OT_RenameSelected)
    bpy.utils.register_class(OBJECT_OT_BatchExportFBX)
    bpy.utils.register_class(OBJECT_OT_JoinMeshes)
    bpy.utils.register_class(OBJECT_OT_triangulate_faces)
    bpy.utils.register_class(OBJECT_OT_InsetAndPoke)
    bpy.utils.register_class(OBJECT_OT_InsetAndTriangulate)
    bpy.utils.register_class(SelectAndMarkSeamOperator)
    bpy.utils.register_class(SelectAndClearSeamOperator)
    

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_ScaleDisplay)
    bpy.utils.unregister_class(OBJECT_OT_ToggleWireframe)
    bpy.utils.unregister_class(OBJECT_OT_ResetTransforms)
    bpy.utils.unregister_class(OBJECT_OT_FreezeTransforms)
    bpy.utils.unregister_class(OBJECT_OT_DeleteMaterials)
    bpy.utils.unregister_class(OBJECT_OT_AddMaterialSlot)
    bpy.utils.unregister_class(OBJECT_OT_RenameSelected)
    bpy.utils.unregister_class(OBJECT_OT_BatchExportFBX)
    bpy.utils.unregister_class(OBJECT_OT_JoinMeshes)
    bpy.utils.unregister_class(OBJECT_OT_triangulate_faces)
    bpy.utils.unregister_class(OBJECT_OT_InsetAndPoke)
    bpy.utils.unregister_class(OBJECT_OT_InsetAndTriangulate)
    bpy.utils.unregister_class(SelectAndMarkSeamOperator)
    bpy.utils.unregister_class(SelectAndClearSeamOperator)
    


# Run the script
if __name__ == "__main__":
    register()
