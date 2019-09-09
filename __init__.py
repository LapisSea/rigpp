# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from . rigpp_panel import RigPP_PT_Panel
from . bclean_op import RigPP_OT_BClean

import bpy

from . import auto_load

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       CollectionProperty,
                       Scene,
                       )
from . import_properties import *

bl_info = {
    "name": "Rigging++",
    "author": "LapisSea",
    "description": "A set of utilities and automation operations focused on improving and overhauling the rigging workflow",
    "blender": (2, 80, 0),
    'location': 'View3D',
    "warning": "With great power coomes great... actually nevermind!",
    "category": "Rigging"
}


class RigppSettings(PropertyGroup):
    auto_cleanup_b_names: BoolProperty(
        name="Automatically clean up bone names",
        description="A bool property",
        default=False
    )
    auto_cleanup_b_name_by_sym: BoolProperty(
        name="Automatically clean up bone names by symetry",
        description="A bool property",
        default=False
    )


auto_load.init()


def register():
    auto_load.register()
    try:
        bpy.utils.register_class(RigppSettings)
    except:
        pass
    
    Scene.rigpp_settings = PointerProperty(type=RigppSettings)
    
    if True:
        from .node import reg
        reg()
    
    from .utils import reg
    reg()


def unregister():
    auto_load.unregister()
    del Scene.rigpp_settings
    
    if True:
        from .node import dereg
        dereg()
    
    from .utils import dereg
    dereg()
    

# classes = (
#     RigPP_OT_BClean,
#     Test_PT_Panel
# )


# register, unregister = bpy.utils.register_classes_factory(classes)
