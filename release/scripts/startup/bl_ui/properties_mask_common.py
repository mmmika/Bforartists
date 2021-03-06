﻿# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

# panels get subclassed (not registered directly)
# menus are referenced `as is`

import bpy
from bpy.types import Menu, UIList


class MASK_UL_layers(UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        # assert(isinstance(item, bpy.types.MaskLayer)
        mask = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(mask, "name", text="", emboss=False, icon_value=icon)
            row = layout.row(align=True)
            row.prop(mask, "hide", text="", emboss=False)
            row.prop(mask, "hide_select", text="", emboss=False)
            row.prop(mask, "hide_render", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class MASK_PT_mask:
    # subclasses must define...
    #~ bl_space_type = 'CLIP_EDITOR'
    #~ bl_region_type = 'UI'
    bl_label = "Mask Settings"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        return space_data.mask and space_data.mode == 'MASK'

    def draw(self, context):
        layout = self.layout

        sc = context.space_data
        mask = sc.mask

        col = layout.column(align=True)
        col.prop(mask, "frame_start")
        col.prop(mask, "frame_end")


class MASK_PT_layers:
    # subclasses must define...
    #~ bl_space_type = 'CLIP_EDITOR'
    #~ bl_region_type = 'UI'
    bl_label = "Mask Layers"

    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        return space_data.mask and space_data.mode == 'MASK'

    def draw(self, context):
        layout = self.layout

        sc = context.space_data
        mask = sc.mask
        active_layer = mask.layers.active

        rows = 4 if active_layer else 1

        row = layout.row()
        row.template_list("MASK_UL_layers", "", mask, "layers",
                          mask, "active_layer_index", rows=rows)

        sub = row.column(align=True)

        sub.operator("mask.layer_new", icon='ZOOMIN', text="")
        sub.operator("mask.layer_remove", icon='ZOOMOUT', text="")

        if active_layer:
            sub.separator()

            sub.operator("mask.layer_move", icon='TRIA_UP', text="").direction = 'UP'
            sub.operator("mask.layer_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            # blending
            row = layout.row(align=True)
            row.prop(active_layer, "alpha")
            row.prop(active_layer, "invert", text="", icon='IMAGE_ALPHA')

            layout.prop(active_layer, "blend")
            layout.prop(active_layer, "falloff")

            row = layout.row(align=True)
            row.prop(active_layer, "use_fill_overlap", text="Overlap")
            row.prop(active_layer, "use_fill_holes", text="Holes")


class MASK_PT_spline:
    # subclasses must define...
    #~ bl_space_type = 'CLIP_EDITOR'
    #~ bl_region_type = 'UI'
    bl_label = "Active Spline"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        mask = sc.mask

        if mask and sc.mode == 'MASK':
            return mask.layers.active and mask.layers.active.splines.active

        return False

    def draw(self, context):
        layout = self.layout

        sc = context.space_data
        mask = sc.mask
        spline = mask.layers.active.splines.active

        col = layout.column()
        col.prop(spline, "offset_mode")
        col.prop(spline, "weight_interpolation")

        row = col.row()
        row.prop(spline, "use_cyclic")
        row.prop(spline, "use_fill")

        col.prop(spline, "use_self_intersection_check")


class MASK_PT_point:
    # subclasses must define...
    #~ bl_space_type = 'CLIP_EDITOR'
    #~ bl_region_type = 'UI'
    bl_label = "Active Point"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        mask = sc.mask

        if mask and sc.mode == 'MASK':
            mask_layer_active = mask.layers.active
            return (mask_layer_active and
                    mask_layer_active.splines.active_point)

        return False

    def draw(self, context):
        layout = self.layout

        sc = context.space_data
        mask = sc.mask
        point = mask.layers.active.splines.active_point
        parent = point.parent

        col = layout.column()
        # Currently only parenting the movie-clip is allowed,
        # so do not over-complicate things for now by using single template_ID
        #col.template_any_ID(parent, "id", "id_type", text="")

        col.label("Parent:")
        col.prop(parent, "id", text="")

        if parent.id_type == 'MOVIECLIP' and parent.id:
            clip = parent.id
            tracking = clip.tracking

            row = col.row()
            row.prop(parent, "type", expand=True)

            col.prop_search(parent, "parent", tracking,
                            "objects", icon='OBJECT_DATA', text="Object:")

            tracks_list = "tracks" if parent.type == 'POINT_TRACK' else "plane_tracks"

            if parent.parent in tracking.objects:
                object = tracking.objects[parent.parent]
                col.prop_search(parent, "sub_parent", object,
                                tracks_list, icon='ANIM_DATA', text="Track:")
            else:
                col.prop_search(parent, "sub_parent", tracking,
                                tracks_list, icon='ANIM_DATA', text="Track:")


class MASK_PT_display:
    # subclasses must define...
    #~ bl_space_type = 'CLIP_EDITOR'
    #~ bl_region_type = 'UI'
    bl_label = "Mask Display"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        return space_data.mask and space_data.mode == 'MASK'

    def draw(self, context):
        layout = self.layout

        space_data = context.space_data
        row = layout.row(align=True)
        row.prop(space_data, "show_mask_smooth", text="Smooth")
        row.prop(space_data, "mask_draw_type", text="")
        row = layout.row(align=True)
        row.prop(space_data, "show_mask_overlay", text="Overlay")
        sub = row.row()
        sub.active = space_data.show_mask_overlay
        sub.prop(space_data, "mask_overlay_mode", text="")


class MASK_PT_tools:
    # subclasses must define...
    #~ bl_space_type = 'CLIP_EDITOR'
    #~ bl_region_type = 'TOOLS'
    bl_label = "Mask Tools"
    bl_category = "Mask"

    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        return space_data.mask and space_data.mode == 'MASK'

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.label(text="Add Spline:")
        col.operator("mask.primitive_circle_add", text = "  Add Circle            ", icon='MESH_PLANE')
        col.operator("mask.primitive_square_add", text= "  Add Square            ",  icon='MESH_CIRCLE')

        col = layout.column(align=True)
        col.label(text="Spline:")
        col.operator("mask.delete", text = "  Delete                    ", icon = "DELETE")
        col.operator("mask.cyclic_toggle", text = "  Toggle Cyclic        ", icon = 'TOGGLE_CYCLIC')
        col.operator("mask.switch_direction", text = "  Switch Direction     ", icon = 'SWITCH_DIRECTION')
        col.operator("mask.handle_type_set", text = "  Set Handle Type     ", icon = 'HANDLE_AUTO')
        col.operator("mask.feather_weight_clear", text = "  Clear Feather Weight", icon = "CLEAR")

        col = layout.column(align=True)
        col.label(text="Animation:")
        col.operator("mask.shape_key_insert", text="  Insert Key               ", icon = "KEYFRAMES_INSERT")
        col.operator("mask.shape_key_clear", text="  Clear Key               ", icon = "CLEAR")
        col.operator("mask.shape_key_feather_reset", text="  Reset Feather Animation", icon = "RESET")
        col.operator("mask.shape_key_rekey", text="  Re-Key Shape Points", icon='KEY_HLT')


class MASK_MT_mask(Menu):
    bl_label = "Mask"

    def draw(self, context):
        layout = self.layout

        layout.operator("mask.delete", icon = "DELETE")
        layout.operator("mask.duplicate_move", text = "Duplicate", icon = "DUPLICATE")

        layout.separator()
        layout.operator("mask.parent_clear", icon = "PARENT_CLEAR")
        layout.operator("mask.parent_set", icon = "PARENT_SET")

        layout.separator()
        layout.operator("mask.copy_splines", icon = "COPYDOWN")
        layout.operator("mask.paste_splines", icon = "PASTEDOWN")

        layout.separator()
        layout.menu("MASK_MT_visibility")
        layout.menu("MASK_MT_transform")
        #layout.menu("MASK_MT_animation") # bfa - this menu is still there and can be called by hotkey. But it is not longer part of this mask menu.


class MASK_MT_visibility(Menu):
    bl_label = "Show/Hide"

    def draw(self, context):
        layout = self.layout

        layout.operator("mask.hide_view_clear", text="Show Hidden", icon = "RESTRICT_VIEW_OFF")
        layout.operator("mask.hide_view_set", text="Hide Selected", icon = "RESTRICT_VIEW_ON").unselected = False
        layout.operator("mask.hide_view_set", text="Hide Unselected", icon = "HIDE_UNSELECTED").unselected = True


class MASK_MT_transform(Menu):
    bl_label = "Transform"

    def draw(self, context):
        layout = self.layout

        layout.operator("transform.translate", icon = "TRANSFORM_MOVE")
        layout.operator("transform.rotate", icon = "TRANSFORM_ROTATE")
        layout.operator("transform.resize", text="Scale",  icon = "TRANSFORM_SCALE")
        layout.operator("transform.transform", text="Scale Feather", icon = 'SHRINK_FATTEN').mode = 'MASK_SHRINKFATTEN'

 # bfa - this menu is still there and can be called by hotkey. But it is not longer part of this mask menu.
class MASK_MT_animation(Menu):
    bl_label = "Animation"

    def draw(self, context):
        layout = self.layout

        layout.operator("mask.shape_key_clear")
        layout.operator("mask.shape_key_insert")
        layout.operator("mask.shape_key_feather_reset")
        layout.operator("mask.shape_key_rekey")


class MASK_MT_select(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("mask.select_border", icon='BORDER_RECT')
        layout.operator("mask.select_circle", icon = 'CIRCLE_SELECT')

        layout.separator()

        layout.operator("mask.select_all", icon='SELECT_ALL').action = 'TOGGLE'
        layout.operator("mask.select_all", text="Inverse", icon='INVERSE').action = 'INVERT'
        layout.operator("mask.select_linked", text="Select Linked", icon = "LINKED")

        layout.separator()

        layout.operator("mask.select_more", icon = "SELECTMORE")
        layout.operator("mask.select_less", icon = "SELECTLESS")


classes = (
    MASK_UL_layers,
    MASK_MT_mask,
    MASK_MT_visibility,
    MASK_MT_transform,
    MASK_MT_animation,
    MASK_MT_select,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
