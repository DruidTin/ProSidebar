import bpy
import math
import mathutils
from bpy_extras import view3d_utils

def get_object_icon(obj):
    ''' 
    This returns the correct icon for the object type

    ARGS
    obj (bpy.types.Object) - Object to get the icon for

    '''
    if 'IS_ASSEMBLY_BP' in obj:
        return 'FILE_3D'
    if obj.type == 'MESH':
        return 'OUTLINER_OB_MESH'
    if obj.type == 'CURVE':
        return 'OUTLINER_OB_CURVE'
    if obj.type == 'FONT':
        return 'OUTLINER_OB_FONT'
    if obj.type == 'EMPTY':
        return 'OUTLINER_OB_EMPTY'
    if obj.type == 'LATTICE':
        return 'OUTLINER_OB_LATTICE'
    if obj.type == 'META':
        return 'OUTLINER_OB_META'                                            
    if obj.type == 'LIGHT':
        return 'OUTLINER_OB_LIGHT'    
    if obj.type == 'CAMERA':
        return 'OUTLINER_OB_CAMERA'    
    if obj.type == 'SURFACE':
        return 'OUTLINER_OB_SURFACE'    
    if obj.type == 'ARMATURE':
        return 'OUTLINER_OB_ARMATURE'    
    if obj.type == 'SPEAKER':
        return 'OUTLINER_OB_SPEAKER'    
    if obj.type == 'FORCE_FIELD':
        return 'OUTLINER_OB_FORCE_FIELD'    
    if obj.type == 'GPENCIL':
        return 'OUTLINER_OB_GREASEPENCIL'    
    if obj.type == 'LIGHT_PROBE':
        return 'OUTLINER_OB_LIGHTPROBE'  

def meter_to_inch(meter):
    """ Converts meter to inch
    """
    return round(meter * 39.3700787,6)

def meter_to_millimeter(meter):
    """ Converts meter to millimeter
    """
    return meter * 1000

def meter_to_active_unit(meter):
    """ Converts meter to active unit
    """
    if bpy.context.scene.unit_settings.system == 'METRIC':
        return meter_to_millimeter(meter)
    else:
        return meter_to_inch(meter)

def delete_obj_list(obj_list):
    ''' 
    This function deletes every object in the list
    '''
    bpy.ops.object.select_all(action='DESELECT')
    for obj in obj_list:
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                # THESE DRIVERS MUST BE REMOVED TO DELETE OBJECTS
                if driver.data_path in {'hide','hide_select'}: 
                    obj.driver_remove(driver.data_path) 
        
        obj.parent = None
        obj.hide_select = False
        obj.hide_viewport = False
        obj.select_set(True)
        
        #TODO: FIGURE OUT IF THIS IS RIGHT
        if obj.name in bpy.context.view_layer.active_layer_collection.collection.objects:
            bpy.context.view_layer.active_layer_collection.collection.objects.unlink(obj)
            # bpy.context.scene.objects.unlink(obj)

    for obj in obj_list:
        bpy.data.objects.remove(obj,do_unlink=True)

def delete_object_and_children(obj_bp):
    '''
    Deletes a object and all it's children

    ARGS
    obj_bp (bpy.types.Object) - Parent Object to Delete
    '''
    obj_list = []
    obj_list.append(obj_bp)
    for child in obj_bp.children:
        if len(child.children) > 0:
            delete_object_and_children(child)
        else:
            obj_list.append(child)
    delete_obj_list(obj_list)

def floor_raycast(context, mx, my):
    '''
    This casts a ray into the 3D view and returns information based on what is under the mouse

    ARGS
    context (bpy.context) = current blender context
    mx (float) = 2D mouse x location
    my (float) = 2D mouse y location

    RETURNS tuple
    has_hit (boolean) - determines if an object is under the mouse
    snapped_location (tuple) - x,y,z location of location under mouse
    snapped_normal (tuple) - normal direction
    snapped_rotation (tuple) - rotation
    face_index (int) - face index under mouse
    object (bpy.types.Object) - Blender Object under mouse
    martix (float multi-dimensional array of 4 * 4 items in [-inf, inf]) - matrix of placement under mouse
    '''
    r = context.region
    rv3d = context.region_data
    coord = mx, my

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(r, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(r, rv3d, coord)
    # ray_target = ray_origin + (view_vector * 1000000000)
    ray_target = ray_origin + view_vector

    snapped_location = mathutils.geometry.intersect_line_plane(ray_origin, ray_target, (0, 0, 0), (0, 0, 1),
                                                               False)
    if snapped_location != None:
        has_hit = True
        snapped_normal = mathutils.Vector((0, 0, 1))
        face_index = None
        object = None
        matrix = None
        snapped_rotation = snapped_normal.to_track_quat('Z', 'Y').to_euler()
        offset_rotation_amount = 0
        randomize_rotation_amount = 0
        randomize_rotation = False
        if randomize_rotation:
            randoffset = offset_rotation_amount + math.pi + (
                    random.random() - 0.5) * randomize_rotation_amount
        else:
            randoffset = offset_rotation_amount + math.pi
        snapped_rotation.rotate_axis('Z', randoffset)

    return has_hit, snapped_location, snapped_normal, snapped_rotation, face_index, object, matrix

def get_selection_point(context, event, ray_max=10000.0,objects=None,floor=None,exclude_objects=[]):
    """Gets the point to place an object based on selection"""
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_target = ray_origin + view_vector
 
    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""
 
        for obj in context.visible_objects:
             
            if objects:
                if obj in objects and obj not in exclude_objects:
                    yield (obj, obj.matrix_world.copy())
             
            else:
                if obj not in exclude_objects:
                    if floor is not None and obj == floor:
                        yield (obj, obj.matrix_world.copy())
                         
    #                 if obj.draw_type != 'WIRE':
                    if obj.type == 'MESH' and obj.hide_select == False:
                        yield (obj, obj.matrix_world.copy())
    
                    if obj.instance_type != 'NONE':
                        obj.dupli_list_create(scene)
                        for dob in obj.dupli_list:
                            obj_dupli = dob.object
                            if obj_dupli.type == 'MESH':
                                yield (obj_dupli, dob.matrix.copy())
 
            # obj.dupli_list_clear()
 
    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""
        try:
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj
     
            # cast the ray
            success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
     
            if success:
                return location, normal, face_index
            else:
                return None, None, None
        except:
            print("ERROR IN obj_ray_cast",obj)
            return None, None, None
             
    best_length_squared = ray_max * ray_max
    best_obj = None
    best_hit = (0,0,0)
    for obj, matrix in visible_objects_and_duplis():
        if obj.type == 'MESH':
            if obj.data:
                hit, normal, face_index = obj_ray_cast(obj, matrix)
                if hit is not None:
                    hit_world = matrix @ hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if length_squared < best_length_squared:
                        best_hit = hit_world
                        best_length_squared = length_squared
                        best_obj = obj
                        
    return best_hit, best_obj    

def calc_distance(point1,point2):
    """ This gets the distance between two points (X,Y,Z)
    """
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2)     