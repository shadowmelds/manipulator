from typing import cast

import bpy
from bpy.types import Area, Context, KeyMap, KeyMapItem, Menu, Operator, SpaceView3D

bl_info = {
    "name": "Alt+RMB Manipulator Pie",
    "author": "Demeter Dzadik <demeter@blender.org>",
    "version": (1, 0, 0),
    "blender": (5, 1, 0),
    "location": "3D View",
    "description": "3D Viewport Pie Menus 分离出来的一个功能，Alt + 鼠标右键显示 Gizmo 饼菜单",
    "category": "3D View",
}


addon_keymaps: list[KeyMap, KeyMapItem] = []


class PIE_MT_manipulator(Menu):
    bl_idname = "PIE_MT_manipulator"
    bl_label = "Manipulator"

    def draw(self, context: Context) -> None:
        pie = self.layout.menu_pie()
        space = cast(SpaceView3D, context.space_data)
        if not space:
            return

        # 4 - LEFT
        pie.operator(
            "view3d.set_manipulator",
            text="Rotation",
            icon="CON_ROTLIKE",
            depress=space.show_gizmo_object_rotate,
        ).manipulator = "ROT"

        # 6 - RIGHT
        pie.operator(
            "view3d.set_manipulator",
            text="Scale",
            icon="CON_SIZELIKE",
            depress=space.show_gizmo_object_scale,
        ).manipulator = "SCALE"

        # 2 - BOTTOM
        pie.operator(
            "view3d.set_manipulator", text="None", icon="X"
        ).manipulator = "NONE"

        # 8 - TOP
        pie.operator(
            "view3d.set_manipulator",
            text="Location",
            icon="CON_LOCLIKE",
            depress=space.show_gizmo_object_translate,
        ).manipulator = "LOC"

        # 7 - TOP LEFT
        pie.operator(
            "view3d.set_manipulator",
            text="Loc/Rot",
            icon="CON_LOCLIKE",
            depress=(
                space.show_gizmo_object_translate and space.show_gizmo_object_rotate
            ),
        ).manipulator = "LOCROT"

        # 9 - TOP RIGHT
        pie.operator(
            "view3d.set_manipulator",
            text="Loc/Scale",
            icon="CON_SIZELIKE",
            depress=(
                space.show_gizmo_object_translate and space.show_gizmo_object_scale
            ),
        ).manipulator = "LOCSCALE"

        # 1 - BOTTOM LEFT
        pie.operator(
            "view3d.set_manipulator",
            text="Loc/Rot/Scale",
            icon="CON_LOCLIKE",
            depress=(
                space.show_gizmo_object_translate
                and space.show_gizmo_object_rotate
                and space.show_gizmo_object_scale
            ),
        ).manipulator = "LOCROTSCALE"


class VIEW3D_OT_set_manipulator(Operator):
    bl_idname = "view3d.set_manipulator"
    bl_label = "Set Manipulator"
    bl_options = {"REGISTER"}

    manipulator: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", "None"),
            ("LOC", "Translate", "Translate"),
            ("ROT", "Rotate", "Rotate"),
            ("SCALE", "Scale", "Scale"),
            ("LOCROT", "Translate & Rotate", "Translate & Rotate"),
            ("LOCSCALE", "Translate & Scale", "Translate & Scale"),
            ("LOCROTSCALE", "All", "All"),
        ],
        description="Set manipulator type",
        default="LOC",
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        space = context.space_data
        return bool(space) and space.type == "VIEW_3D"

    def execute(self, context: Context) -> set[str]:
        space = cast(SpaceView3D, context.space_data)
        if not space:
            return {"CANCELLED"}

        if self.manipulator != "NONE":
            space.show_gizmo = True

        space.show_gizmo_object_translate = "LOC" in self.manipulator
        space.show_gizmo_object_rotate = "ROT" in self.manipulator
        space.show_gizmo_object_scale = "SCALE" in self.manipulator

        return {"FINISHED"}


class VIEW3D_OT_call_manipulator_pie(Operator):
    bl_idname = "view3d.call_manipulator_pie"
    bl_label = "Call Manipulator Pie"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        # 必须鼠标在 3D VIEW 区域，否则不触发
        space: Area | None = context.area
        return bool(space) and space.type == "VIEW_3D"

    def execute(self, context: Context) -> set[str]:
        # 立即刷新 UI，确保第一次呼出也不会延迟
        context.area.tag_redraw()
        bpy.ops.wm.call_menu_pie(name="PIE_MT_manipulator")
        return {"FINISHED"}


def register_keymaps() -> None:
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon or wm.keyconfigs.user

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    # 防止重复注册
    for km2, kmi2 in addon_keymaps:
        if km2 == km:
            km.keymap_items.remove(kmi2)

    kmi = km.keymap_items.new(
        idname="view3d.call_manipulator_pie",
        type="RIGHTMOUSE",
        value="PRESS",
        alt=True,
    )

    addon_keymaps.append((km, kmi))


def register() -> None:
    bpy.utils.register_class(PIE_MT_manipulator)
    bpy.utils.register_class(VIEW3D_OT_set_manipulator)
    bpy.utils.register_class(VIEW3D_OT_call_manipulator_pie)
    register_keymaps()


def unregister() -> None:
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(VIEW3D_OT_call_manipulator_pie)
    bpy.utils.unregister_class(VIEW3D_OT_set_manipulator)
    bpy.utils.unregister_class(PIE_MT_manipulator)


if __name__ == "__main__":
    register()
