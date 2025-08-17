bl_info = {
    "name": "FPS Gamepad Camera",
    "author": "Leddy & GPT",
    "version": (1, 15, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > FPS Cam",
    "description": "Drive the active camera with an XInput gamepad. LS=move, RS=look, LT/RT=roll. D-pad timeline, insert/delete keyframes, configurable playback and keyframe jumps.",
    "category": "3D View",
}

import bpy
import ctypes
from mathutils import Vector

# ---------------------- XINPUT ----------------------
class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ("wButtons",      ctypes.c_ushort),
        ("bLeftTrigger",  ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX",      ctypes.c_short),
        ("sThumbLY",      ctypes.c_short),
        ("sThumbRX",      ctypes.c_short),
        ("sThumbRY",      ctypes.c_short),
    ]

class XINPUT_STATE(ctypes.Structure):
    _fields_ = [("dwPacketNumber", ctypes.c_uint), ("Gamepad", XINPUT_GAMEPAD)]

def _load_xinput():
    for name in ("xinput1_4", "xinput1_3", "xinput9_1_0", "xinput1_2", "xinput1_1"):
        try:
            return getattr(ctypes.windll, name), name + ".dll"
        except Exception:
            continue
    return None, None

_xinput, _xinput_name = _load_xinput()
STICK_DZ = 7849
TRIG_THRESH = 30

# Button masks
BTN = {
    'DPAD_UP':    0x0001,
    'DPAD_DOWN':  0x0002,
    'DPAD_LEFT':  0x0004,
    'DPAD_RIGHT': 0x0008,
    'START':      0x0010,
    'BACK':       0x0020,
    'L_THUMB':    0x0040,
    'R_THUMB':    0x0080,
    'L_SHOULDER': 0x0100,
    'R_SHOULDER': 0x0200,
    'A':          0x1000,
    'B':          0x2000,
    'X':          0x4000,
    'Y':          0x8000,
}

BUTTON_ITEMS = [
    ('NONE','None',''),
    ('A','A',''),('B','B',''),('X','X',''),('Y','Y',''),
    ('L_SHOULDER','Left Shoulder',''),('R_SHOULDER','Right Shoulder',''),
    ('START','Start',''),('BACK','Back',''),
    ('DPAD_UP','D-pad Up',''), ('DPAD_DOWN','D-pad Down',''),
    ('DPAD_LEFT','D-pad Left',''), ('DPAD_RIGHT','D-pad Right',''),
]

# ---------------------- HELPERS ----------------------
def _norm_axis(v: int, dz: int, maxv: int = 32767):
    if abs(v) < dz:
        return 0.0
    return (v - dz) / (maxv - dz) if v > 0 else (v + dz) / (maxv - dz)

def read_pad(idx: int):
    """Return (ok, lx, ly, rx, ry, lt, rt, buttons)."""
    if not _xinput:
        return False, 0,0,0,0,0,0, 0
    st = XINPUT_STATE()
    res = _xinput.XInputGetState(idx, ctypes.byref(st))
    if res != 0:
        return False, 0,0,0,0,0,0, 0
    gp = st.Gamepad
    lx = _norm_axis(gp.sThumbLX, STICK_DZ)
    ly = _norm_axis(gp.sThumbLY, STICK_DZ)
    rx = _norm_axis(gp.sThumbRX, STICK_DZ)
    ry = _norm_axis(gp.sThumbRY, STICK_DZ)
    lt = gp.bLeftTrigger  / 255.0 if gp.bLeftTrigger  > TRIG_THRESH else 0.0
    rt = gp.bRightTrigger / 255.0 if gp.bRightTrigger > TRIG_THRESH else 0.0
    buttons = int(gp.wButtons)
    return True, lx, ly, rx, ry, lt, rt, buttons

def scan_first_live():
    for i in range(4):
        ok, *_ = read_pad(i)
        if ok:
            return i, True
    return -1, False

def enum_to_mask(choice: str) -> int:
    if choice == 'NONE':
        return 0
    return BTN.get(choice, 0)

# ---------------------- PROPERTIES ----------------------
class FPSCamProps(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(default=False)

    auto_detect: bpy.props.BoolProperty(name="Auto-Detect", default=True)
    controller_index: bpy.props.IntProperty(name="Controller", default=0, min=0, max=3)

    move_speed: bpy.props.FloatProperty(name="Move Speed", default=0.010, min=0.000, max=0.100, step=0.001, precision=4)
    look_speed: bpy.props.FloatProperty(name="Look Speed", default=0.010, min=0.000, max=0.100, step=0.001, precision=4)
    roll_speed: bpy.props.FloatProperty(name="Roll Speed", default=0.010, min=0.000, max=0.100, step=0.001, precision=4)

    invert_move_x: bpy.props.BoolProperty(name="Invert Move X (Strafe)", default=False)
    invert_move_y: bpy.props.BoolProperty(name="Invert Move Y (Forward/Back)", default=True)
    invert_look_x: bpy.props.BoolProperty(name="Invert Look X (Yaw)", default=False)
    invert_look_y: bpy.props.BoolProperty(name="Invert Look Y (Pitch)", default=False)
    invert_roll:   bpy.props.BoolProperty(name="Invert Roll", default=False)

    enable_timeline: bpy.props.BoolProperty(name="Enable D-pad Timeline", default=True)
    timeline_step: bpy.props.IntProperty(name="Timeline Step (frames)", default=1, min=1, max=240)

    key_button: bpy.props.EnumProperty(name="Insert Key Button", items=BUTTON_ITEMS, default='Y')
    delete_key_button: bpy.props.EnumProperty(name="Delete Key Button", items=BUTTON_ITEMS, default='X')

    play_forward_button:  bpy.props.EnumProperty(name="Play Forward Button",  items=BUTTON_ITEMS, default='START')
    play_backward_button: bpy.props.EnumProperty(name="Play Backward Button", items=BUTTON_ITEMS, default='BACK')
    stop_button:          bpy.props.EnumProperty(name="Stop Button",          items=BUTTON_ITEMS, default='B')

    prev_key_button: bpy.props.EnumProperty(name="Jump to Previous Key Button", items=BUTTON_ITEMS, default='L_SHOULDER')
    next_key_button: bpy.props.EnumProperty(name="Jump to Next Key Button",     items=BUTTON_ITEMS, default='R_SHOULDER')

    dbg_ok:  bpy.props.BoolProperty(name="Connected", default=False)
    dbg_idx: bpy.props.IntProperty(name="Active Idx", default=-1, min=-1, max=3)
    dbg_lx:  bpy.props.FloatProperty(name="LX", default=0.0)
    dbg_ly:  bpy.props.FloatProperty(name="LY", default=0.0)
    dbg_rx:  bpy.props.FloatProperty(name="RX", default=0.0)
    dbg_ry:  bpy.props.FloatProperty(name="RY", default=0.0)
    dbg_lt:  bpy.props.FloatProperty(name="LT", default=0.0, min=0.0, max=1.0)
    dbg_rt:  bpy.props.FloatProperty(name="RT", default=0.0, min=0.0, max=1.0)
    dbg_btns:bpy.props.StringProperty(name="Buttons", default="0x0000")

# ---------------------- OPERATORS ----------------------
class FPSCAM_OT_start(bpy.types.Operator):
    bl_idname = "view3d.fps_gamepad_camera"
    bl_label  = "Start FPS Gamepad Camera"
    _timer = None
    _active_idx = -1
    _prev_buttons = 0

    def modal(self, context, event):
        p = context.scene.fps_cam_props
        cam = context.scene.camera

        if event.type == 'ESC' or not p.enabled or not cam:
            return self.cancel(context)

        if event.type == 'TIMER':
            if p.auto_detect and self._active_idx == -1:
                idx, ok = scan_first_live()
                if ok:
                    self._active_idx = idx
                    p.controller_index = idx
                else:
                    p.dbg_ok = False; p.dbg_idx = -1
                    p.dbg_lx = p.dbg_ly = p.dbg_rx = p.dbg_ry = 0.0
                    p.dbg_lt = p.dbg_rt = 0.0
                    p.dbg_btns = "0x0000"
                    return {'PASS_THROUGH'}
            idx = self._active_idx if p.auto_detect else p.controller_index

            ok, lx, ly, rx, ry, lt, rt, buttons = read_pad(idx)
            p.dbg_ok = ok; p.dbg_idx = idx
            p.dbg_lx, p.dbg_ly, p.dbg_rx, p.dbg_ry = lx, ly, rx, ry
            p.dbg_lt, p.dbg_rt = lt, rt
            p.dbg_btns = f"0x{buttons:04X}"

            if not ok:
                if p.auto_detect:
                    self._active_idx = -1
                return {'PASS_THROUGH'}

            newly_pressed = buttons & (~self._prev_buttons)
            self._prev_buttons = buttons

            # D-pad timeline step
            if p.enable_timeline:
                if newly_pressed & BTN['DPAD_LEFT']:
                    context.scene.frame_current = max(1, context.scene.frame_current - p.timeline_step)
                if newly_pressed & BTN['DPAD_RIGHT']:
                    context.scene.frame_current += p.timeline_step

            # Keyframe jumps
            pk = enum_to_mask(p.prev_key_button)
            nk = enum_to_mask(p.next_key_button)
            if pk and newly_pressed & pk:
                bpy.ops.screen.keyframe_jump(next=False)
            if nk and newly_pressed & nk:
                bpy.ops.screen.keyframe_jump(next=True)

            # Playback
            pf = enum_to_mask(p.play_forward_button)
            pb = enum_to_mask(p.play_backward_button)
            ps = enum_to_mask(p.stop_button)
            if pf and newly_pressed & pf:
                bpy.ops.screen.animation_play()
            if pb and newly_pressed & pb:
                bpy.ops.screen.animation_play(reverse=True)
            if ps and newly_pressed & ps:
                if context.screen.is_animation_playing:
                    bpy.ops.screen.animation_cancel(restore_frame=False)

            # Insert/Delete keyframes
            ib = enum_to_mask(p.key_button)
            if ib and newly_pressed & ib:
                cam.keyframe_insert(data_path="location")
                cam.keyframe_insert(data_path="rotation_euler")
            db = enum_to_mask(p.delete_key_button)
            if db and newly_pressed & db:
                frame = context.scene.frame_current
                cam.keyframe_delete(data_path="location", frame=frame)
                cam.keyframe_delete(data_path="rotation_euler", frame=frame)

            # Inverts
            if p.invert_look_x: rx = -rx
            if p.invert_look_y: ry = -ry
            if p.invert_roll:   lt, rt = rt, lt
            if p.invert_move_x: lx = -lx
            if p.invert_move_y: ly = -ly

            # Look: yaw Z, pitch X
            e = cam.rotation_euler.copy()
            e.z -= rx * p.look_speed
            e.x += ry * p.look_speed
            cam.rotation_euler = e

            # Roll: Y via triggers
            if lt or rt:
                e = cam.rotation_euler.copy()
                e.y += (rt - lt) * p.roll_speed
                cam.rotation_euler = e

            # Move: local LS
            fwd   = Vector((0,0,-1)); fwd.rotate(cam.rotation_euler)
            right = Vector((1,0, 0)); right.rotate(cam.rotation_euler)
            move = fwd * (-ly * p.move_speed) + right * (lx * p.move_speed)
            if move.length_squared > 0.0:
                cam.location += move

            # Auto key
            if context.scene.tool_settings.use_keyframe_insert_auto:
                cam.keyframe_insert(data_path="location")
                cam.keyframe_insert(data_path="rotation_euler")

        return {'PASS_THROUGH'}

    def execute(self, context):
        if not _xinput:
            self.report({'ERROR'}, "XInput not available. Need an Xbox-compatible controller on Windows.")
            return {'CANCELLED'}
        if not context.scene.camera:
            self.report({'ERROR'}, "No active camera. Select one or press Ctrl+Alt+0.")
            return {'CANCELLED'}

        p = context.scene.fps_cam_props
        p.enabled = True
        self._active_idx = -1
        self._prev_buttons = 0
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/120.0, window=context.window)
        wm.modal_handler_add(self)
        self.report({'INFO'}, f"FPS Gamepad Camera running (DLL: {_xinput_name or 'None'}). ESC to stop.")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        p = context.scene.fps_cam_props
        p.enabled = False
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        self.report({'INFO'}, "FPS Gamepad Camera stopped.")
        return {'CANCELLED'}

class FPSCAM_OT_stop(bpy.types.Operator):
    bl_idname = "view3d.fps_gamepad_camera_stop"
    bl_label  = "Stop FPS Gamepad Camera"
    def execute(self, context):
        context.scene.fps_cam_props.enabled = False
        self.report({'INFO'}, "Stopping FPS Gamepad Camera…")
        return {'FINISHED'}

# ---------------------- PANEL ----------------------
class FPSCamPanel(bpy.types.Panel):
    bl_label = "FPS Cam"
    bl_idname = "VIEW3D_PT_fps_cam"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FPS Cam"

    def draw(self, context):
        p = context.scene.fps_cam_props
        col = self.layout.column()

        col.label(text=f"XInput DLL: {_xinput_name or 'None'}", icon='INFO')
        col.prop(p, "auto_detect")
        row = col.row()
        row.enabled = not p.auto_detect
        row.prop(p, "controller_index")

        col.separator()
        col.label(text="Speeds:")
        col.prop(p, "move_speed")
        col.prop(p, "look_speed")
        col.prop(p, "roll_speed")

        col.label(text="Invert:")
        col.prop(p, "invert_move_x")
        col.prop(p, "invert_move_y")
        col.prop(p, "invert_look_x")
        col.prop(p, "invert_look_y")
        col.prop(p, "invert_roll")

        col.separator()
        col.label(text="Timeline & Keyframe:")
        col.prop(p, "enable_timeline")
        col.prop(p, "timeline_step")
        col.prop(p, "key_button")
        col.prop(p, "delete_key_button")

        col.separator()
        col.label(text="Playback:")
        col.prop(p, "play_forward_button")
        col.prop(p, "play_backward_button")
        col.prop(p, "stop_button")

        col.separator()
        col.label(text="Keyframe Jumps:")
        col.prop(p, "prev_key_button")
        col.prop(p, "next_key_button")

        col.separator()
        box = col.box()
        box.label(text="Live Input")
        box.label(text=f"Connected: {'Yes' if p.dbg_ok else 'No'} (idx {p.dbg_idx if p.dbg_idx >= 0 else '—'})")
        box.label(text=f"LX:{p.dbg_lx:.2f}  LY:{p.dbg_ly:.2f}  RX:{p.dbg_rx:.2f}  RY:{p.dbg_ry:.2f}")
        box.label(text=f"LT:{p.dbg_lt:.2f}  RT:{p.dbg_rt:.2f}  BTN:{p.dbg_btns}")

        col.separator()
        if not p.enabled:
            col.operator(FPSCAM_OT_start.bl_idname, text="Start", icon='PLAY')
        else:
            col.operator(FPSCAM_OT_stop.bl_idname, text="Stop", icon='PAUSE')

# ---------------------- REGISTER ----------------------
classes = (
    FPSCamProps,
    FPSCAM_OT_start,
    FPSCAM_OT_stop,
    FPSCamPanel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.fps_cam_props = bpy.props.PointerProperty(type=FPSCamProps)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    if hasattr(bpy.types.Scene, "fps_cam_props"):
        del bpy.types.Scene.fps_cam_props

if __name__ == "__main__":
    register()
