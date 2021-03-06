import bpy
from bpy.types import Header, Menu, Operator, UIList, PropertyGroup
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)
import os

class general_OT_open_browser_window(Operator):
    bl_idname = "bp_general.open_browser_window"
    bl_label = "Open Browser Window"
    bl_description = "This will open the path that is passed in a file browser"

    path: StringProperty(name="Message",default="Error")

    def execute(self, context):
        import subprocess
        if 'Windows' in str(bpy.app.build_platform):
            subprocess.Popen(r'explorer ' + self.path)
        elif 'Darwin' in str(bpy.app.build_platform):
            subprocess.Popen(['open' , os.path.normpath(self.path)])
        else:
            subprocess.Popen(['xdg-open' , os.path.normpath(self.path)])
        return {'FINISHED'}

class general_OT_open_new_editor(Operator):
    bl_idname = "bp_general.open_new_editor"
    bl_label = "Open New Editor"

    space_type: StringProperty(name="Space Type")
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):      
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'PREFERENCES':
                window.screen.areas[0].type = self.space_type
        return {'FINISHED'}

class general_OT_open_texture_editor(bpy.types.Operator):
    bl_idname = "bp_general.open_texture_editor"
    bl_label = "Open Texture Editor"

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'MESH':
            return True
        else:
            return False
        
    def execute(self, context):
        if context.object.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
            
        bpy.ops.mesh.select_all(action='SELECT')
        
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        for window in context.window_manager.windows:
            if len(window.screen.areas) == 1 and window.screen.areas[0].type == 'PREFERENCES':
                window.screen.areas[0].type = 'IMAGE_EDITOR'
                for space in window.screen.areas[0].spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.mode = 'UV'
        return {'FINISHED'} 

class general_OT_split_region(bpy.types.Operator):
    bl_idname = "bp_general.split_region"
    bl_label = "Show Animation Timeline"
    
    space_type: StringProperty(name="Space Type")
    space_sub_type: StringProperty(name="Space Sub Type")
    split_direction: StringProperty(name="Split Direction")
    split_factor: FloatProperty(name="Factor")

    def execute(self, context):
        #LOAD ALL AREAS INTO A DICTIONARY
        #SPLIT CURRENT AREA
        #LOOK FOR NEW AREA (AREA THAT IS NOT IN DICTIONARY) THEN SET THE TYPE
        areas = []

        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                areas.append(area)

        bpy.ops.screen.area_split(direction=self.split_direction,factor=self.split_factor)

        for window in context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:           
                if area not in areas:      
                    area.type = self.space_type
                    for space in area.spaces:
                        if space.type == 'DOPESHEET_EDITOR' and self.space_sub_type != "":
                            space.mode = self.space_sub_type
                        if space.type == 'IMAGE_EDITOR' and self.space_sub_type != "":
                            space.mode = self.space_sub_type                            
        return {'FINISHED'}


class general_OT_create_new_folder(bpy.types.Operator):
    bl_idname = "bp_general.create_new_folder"
    bl_label = "Create New Folder"
    
    path: bpy.props.StringProperty(name="Path",description="Path to Add Folder to To")
    folder_name: bpy.props.StringProperty(name="Folder Name",description="Folder Name to Create")

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the folder name to add")
        layout.prop(self,'folder_name',icon='FILE_FOLDER')

    def execute(self, context):
        path = os.path.join(self.path, self.folder_name)
        
        if not os.path.exists(path):
            os.makedirs(path)
            
        return {'FINISHED'}

classes = (
    general_OT_open_browser_window,
    general_OT_open_new_editor,
    general_OT_open_texture_editor,
    general_OT_split_region,
    general_OT_create_new_folder
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        