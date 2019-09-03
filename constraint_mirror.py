import bpy
from . utils import *


def doTarget(new, toMirror, target="target", subtarget="subtarget"):
    obj = getattr(toMirror, target)
    if obj is None:
        return

    name = obj.name
    reverseName = tryMirrorName(name)
    if reverseName == name:
        setattr(new, target, obj)
    elif reverseName in bpy.data.objects:
        setattr(new, target, bpy.data.objects[reverseName])


def doTargetSubtarget(new, toMirror, target="target", subtarget="subtarget"):
    obj = getattr(toMirror, target)
    if obj is None:
        return

    doTarget(new, toMirror, target, subtarget)

    if obj.type == "ARMATURE":
        name = getattr(toMirror, subtarget)
        if name is None:
            return
        reverseName = tryMirrorName(name)
        setattr(new, subtarget,
                reverseName if reverseName in getattr(toMirror, target).data.bones else name)


def doCopy(new, toMirror, *attributes):
    for toCopy in attributes:
        setattr(new, toCopy, getattr(toMirror, toCopy))


def doCopyNegated(new, toMirror, *attributes):
    for toCopy in attributes:
        setattr(new, toCopy, getattr(toMirror, toCopy)*-1)


def mirrorLimitRotationConstraint(new, toMirror):
    doCopy(new, toMirror,
           "max_x", "max_y", "max_z",
           "min_x", "min_y", "min_z",
           "use_limit_x", "use_limit_y", "use_limit_z",
           "use_transform_limit")


def mirrorCameraSolverConstraint(new, toMirror):
    doCopy(new, toMirror,
           "clip", "use_active_clip")


def mirrorFollowTrackConstraint(new, toMirror):
    doCopy(new, toMirror,
           "camera", "clip", "depth_object", "frame_method", "object", "track", "use_3d_position", "use_active_clip", "use_undistorted_position")


def mirrorObjectSolverConstraint(new, toMirror):
    doCopy(new, toMirror,
           "camera", "clip", "object", "use_active_clip")


def mirrorCopyLocationConstraint(new, toMirror):
    doCopy(new, toMirror,
           "invert_x", "invert_y", "invert_z",
           "use_x", "use_y", "use_z",
           "head_tail", "use_bbone_shape", "use_offset")
    doTargetSubtarget(new, toMirror)


def mirrorCopyRotationConstraint(new, toMirror):
    doCopy(new, toMirror,
           "invert_x", "invert_y", "invert_z",
           "use_x", "use_y", "use_z",
           "use_offset")

    doTargetSubtarget(new, toMirror)


def mirrorCopyScaleConstraint(new, toMirror):
    doCopy(new, toMirror,                           "power",
           "use_add", "use_offset", "use_x", "use_y", "use_z")
    doTargetSubtarget(new, toMirror)


def mirrorCopyTransformsConstraint(new, toMirror):
    doCopy(new, toMirror,
           "head_tail", "use_bbone_shape")
    doTargetSubtarget(new, toMirror)


def mirrorLimitDistanceConstraint(new, toMirror):
    doCopy(new, toMirror,                           "distance",
           "head_tail", "limit_mode", "use_bbone_shape", "use_transform_limit")
    doTargetSubtarget(new, toMirror)


def mirrorLimitLocationConstraint(new, toMirror):
    doCopy(new, toMirror,
           "max_x", "max_y", "max_z",
           "min_x", "min_y", "min_z",
           "use_max_x", "use_max_y", "use_max_z",
           "use_min_x", "use_min_y", "use_min_z",
           "use_transform_limit")


def mirrorLimitScaleConstraint(new, toMirror):
    doCopy(new, toMirror,
           "max_x", "max_y", "max_z",
           "min_x", "min_y", "min_z",
           "use_max_x", "use_max_y", "use_max_z",
           "use_min_x", "use_min_y", "use_min_z",
           "use_transform_limit")


def mirrorMaintainVolumeConstraint(new, toMirror):
    doCopy(new, toMirror,
           "free_axis", "mode", "volume")


def mirrorTransformConstraint(new, toMirror):
    doCopy(new, toMirror,
           "from_max_x", "from_max_x_rot", "from_max_x_scale", "from_min_x", "from_min_x_rot", "from_min_x_scale",
           "from_max_y", "from_max_y_rot", "from_max_y_scale", "from_min_y", "from_min_y_rot", "from_min_y_scale",
           "from_max_z", "from_max_z_rot", "from_max_z_scale", "from_min_z", "from_min_z_rot", "from_min_z_scale",
           "map_to", "map_to_x_from", "map_to_y_from", "map_to_z_from", "use_motion_extrapolate")
    doCopyNegated(new, toMirror,
                  "to_max_x", "to_max_x_rot", "to_max_x_scale", "to_min_x", "to_min_x_rot", "to_min_x_scale",
                  "to_max_y", "to_max_y_rot", "to_max_y_scale", "to_min_y", "to_min_y_rot", "to_min_y_scale",
                  "to_max_z", "to_max_z_rot", "to_max_z_scale", "to_min_z", "to_min_z_rot", "to_min_z_scale")
    doTargetSubtarget(new, toMirror)


def mirrorTransformCacheConstraint(new, toMirror):
    doCopy(new, toMirror,
           "cache_file", "object_path")


def mirrorClampToConstraint(new, toMirror):
    doCopy(new, toMirror,
           "main_axis", "use_cyclic")
    doTarget(new, toMirror)


def mirrorDampedTrackConstraint(new, toMirror):
    doCopy(new, toMirror,
           "head_tail", "track_axis", "use_bbone_shape")
    doTargetSubtarget(new, toMirror)


def mirrorKinematicConstraint(new, toMirror):
    doCopy(new, toMirror,
           "chain_count", "distance", "ik_type", "iterations", "limit_mode", "orient_weight", "reference_axis", "use_location", "use_rotation", "use_stretch", "use_tail", "weight",
           "lock_location_x", "lock_location_y", "lock_location_z",
           "lock_rotation_x", "lock_rotation_y", "lock_rotation_z")

    doTargetSubtarget(new, toMirror)
    doTargetSubtarget(new, toMirror,
                      "pole_target",  "pole_subtarget")

    import math
    if toMirror.pole_angle > 0:
        new.pole_angle = math.pi-toMirror.pole_angle
    else:
        new.pole_angle = -math.pi-toMirror.pole_angle


def mirrorLockedTrackConstraint(new, toMirror):
    doCopy(new, toMirror,
           "head_tail", "lock_axis", "use_bbone_shape")
    doTargetSubtarget(new, toMirror)

    new.track_axis = (
        "TRACK_" if "_NEGATIVE" in toMirror.track_axis else "TRACK_NEGATIVE_")+toMirror.track_axis[-1]


def mirrorSplineIKConstraint(new, toMirror):
    doCopy(new, toMirror,
           "bulge", "bulge_max", "bulge_min", "bulge_smooth", "chain_count", "joint_bindings", "use_bulge_max", "use_bulge_min", "use_chain_offset", "use_curve_radius", "use_even_divisions", "use_original_scale", "xz_scale_mode", "y_scale_mode")
    doTarget(new, toMirror)


def mirrorStretchToConstraint(new, toMirror):
    doCopy(new, toMirror, "bulge", "bulge_max", "bulge_min", "bulge_smooth",
           "head_tail", "keep_axis", "rest_length", "use_bbone_shape", "use_bulge_max", "use_bulge_min", "volume")
    doTargetSubtarget(new, toMirror)


def mirrorTrackToConstraint(new, toMirror):
    doCopy(new, toMirror, "head_tail",
           "track_axis", "up_axis", "use_bbone_shape", "use_target_z")
    doTargetSubtarget(new, toMirror)


def mirrorActionConstraint(new, toMirror):
    doCopy(new, toMirror,
           "action", "frame_end", "frame_start", "max", "min", "transform_channel", "use_bone_object_action")
    doTargetSubtarget(new, toMirror)


def mirrorArmatureConstraint(new, toMirror):
    doCopy(new, toMirror,
           "use_bone_envelopes", "use_current_location", "use_deform_preserve_volume")

    for target in toMirror.targets:
        newTarget = new.targets.new()
        doTargetSubtarget(newTarget, target)
        newTarget.weight = target.weight


def mirrorChildOfConstraint(new, toMirror):
    doCopy(new, toMirror,
           "use_location_x", "use_location_y", "use_location_z",
           "use_rotation_x", "use_rotation_y", "use_rotation_z",
           "use_scale_x", "use_scale_y", "use_scale_z")
    doTargetSubtarget(new, toMirror)
    new.inverse_matrix = toMirror.inverse_matrix.copy()
    import mathutils
    import math
    from math import radians
    from mathutils import Matrix

    translation, rotation, scale = new.inverse_matrix.decompose()
    # TODO: add support for xyz fixing
    translation.x *= -1

    rotationMat = rotation.to_matrix()
    rotationMat.resize_4x4()
    
    scaleMat =\
    Matrix.Scale(scale.x, 4, (1, 0, 0))@\
    Matrix.Scale(scale.y, 4, (0, 1, 0))@\
    Matrix.Scale(scale.z, 4, (0, 0, 1))
    
    new.inverse_matrix = Matrix.Translation(translation)@rotationMat@scaleMat


def mirrorFloorConstraint(new, toMirror):
    doCopy(new, toMirror,
           "floor_location", "offset", "use_rotation", "use_sticky")
    doTargetSubtarget(new, toMirror)


def mirrorFollowPathConstraint(new, toMirror):
    doCopy(new, toMirror,
           "forward_axis", "offset", "offset_factor", "up_axis", "use_curve_follow", "use_curve_radius", "use_fixed_location")
    doTarget(new, toMirror)


def mirrorPivotConstraint(new, toMirror):
    doCopy(new, toMirror,
           "head_tail", "offset", "rotation_range", "use_bbone_shape", "use_relative_location")
    doTargetSubtarget(new, toMirror)


def mirrorShrinkwrapConstraint(new, toMirror):
    doCopy(new, toMirror,
           "cull_face", "distance", "project_axis", "project_axis_space", "project_limit", "shrinkwrap_type", "track_axis", "use_invert_cull", "use_project_opposite", "use_track_normal", "wrap_mode")
    doTarget(new, toMirror)


mirrorMap = {
    "LIMIT_ROTATION": mirrorLimitRotationConstraint,
    "CAMERA_SOLVER": mirrorCameraSolverConstraint,
    "FOLLOW_TRACK": mirrorFollowTrackConstraint,
    "OBJECT_SOLVER": mirrorObjectSolverConstraint,
    "COPY_LOCATION": mirrorCopyLocationConstraint,
    "COPY_ROTATION": mirrorCopyRotationConstraint,
    "COPY_SCALE": mirrorCopyScaleConstraint,
    "COPY_TRANSFORMS": mirrorCopyTransformsConstraint,
    "LIMIT_DISTANCE": mirrorLimitDistanceConstraint,
    "LIMIT_LOCATION": mirrorLimitLocationConstraint,
    "LIMIT_SCALE": mirrorLimitScaleConstraint,
    "MAINTAIN_VOLUME": mirrorMaintainVolumeConstraint,
    "TRANSFORM": mirrorTransformConstraint,
    "TRANSFORM_CACHE": mirrorTransformCacheConstraint,
    "CLAMP_TO": mirrorClampToConstraint,
    "DAMPED_TRACK": mirrorDampedTrackConstraint,
    "IK": mirrorKinematicConstraint,
    "LOCKED_TRACK": mirrorLockedTrackConstraint,
    "SPLINE_IK": mirrorSplineIKConstraint,
    "STRETCH_TO": mirrorStretchToConstraint,
    "TRACK_TO": mirrorTrackToConstraint,
    "ACTION": mirrorActionConstraint,
    "ARMATURE": mirrorArmatureConstraint,
    "CHILD_OF": mirrorChildOfConstraint,
    "FLOOR": mirrorFloorConstraint,
    "FOLLOW_PATH": mirrorFollowPathConstraint,
    "PIVOT": mirrorPivotConstraint,
    "SHRINKWRAP": mirrorShrinkwrapConstraint
}


def makeMirrorConsrtaint(targetBone, constraint):
    if constraint.type not in mirrorMap:
        raise Exception(
            str(type(constraint).__name__) + "("+constraint.type+") not implemented!")

    newC = targetBone.constraints.new(constraint.type)

    doCopy(newC, constraint,
           "owner_space", "target_space", "mute", "influence")

    mirrorMap[constraint.type](newC, constraint)
