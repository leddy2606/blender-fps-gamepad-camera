# blender-fps-gamepad-camera
Control Blender’s camera with an Xbox controller in FPS style. Move, look, roll, and keyframe directly from a gamepad.
# FPS Gamepad Camera for Blender 🎮📷

Control Blender’s active camera with an Xbox-compatible gamepad (XInput).  
Walk/fly in first person, roll with triggers, scrub the timeline, and add/remove keyframes — all from the pad.

> **Blender:** 4.x (tested) • **OS:** Windows (XInput) • **Input:** Xbox/compatible controller

---

## ✨ Features

- **Left Stick** – Move (strafe + forward/back)  
- **Right Stick** – Look (yaw + pitch)  
- **Triggers (LT/RT)** – Roll  
- **D-Pad L/R** – Step timeline (configurable step)  
- **Insert Key (default: Y)** – Adds camera loc + rot keys  
- **Delete Key (default: X)** – Deletes camera loc + rot keys at current frame  
- **LB / RB** – Jump to previous / next keyframe  
- **Start / Back / B** – Play forward / play backward / stop (remappable)  
- **Invert toggles** – Move X/Y, Look X/Y, Roll  
- **Auto-detect** controller, **Start/Stop** to re-hook quickly  
- **Live Input** readout (sticks, triggers, buttons)

---

## 📥 Installation

1. Download `fps_gamepad_camera.py`.  
2. In Blender: **Edit ▸ Preferences ▸ Add-ons ▸ Install…**  
3. Select the `.py` file → enable **FPS Gamepad Camera**.  
4. In the 3D View N-panel, open **FPS Cam** → click **Start**.

> Tip: Set **Auto Keying** (red dot) if you want your movement recorded automatically.

---

## 🎛️ Panel Options (N-panel ▸ FPS Cam)

- **Speeds:** Move / Look / Roll (fine 0.001 steps)  
- **Invert:** Move X/Y, Look X/Y, Roll  
- **Timeline:** Enable D-pad control + frame step size  
- **Key Buttons:** Insert, Delete, Jump Prev/Next, Play Fwd/Back, Stop  
- **Live Input:** Connected status, axes, triggers, button mask

---

## 🕹 Default Controls (change these in the panel)

| Action | Button |
|---|---|
| Insert keyframe (loc+rot) | **Y** |
| Delete keyframe (loc+rot @ current frame) | **X** |
| Jump to previous / next key | **LB / RB** |
| Play forward / backward | **Start / Back** |
| Stop playback | **B** |
| Timeline step | **D-Pad Left/Right** |
| Move / Look / Roll | **LS / RS / LT/RT** |

---

## ❓ FAQ

**It stopped reading the pad.**  
Hit **Stop** then **Start** (auto-detect will re-hook).  
Also check `joy.cpl` in Windows to confirm the controller is alive.

**How do I record movement?**  
Enable **Auto Keying** (timeline controls), then fly the camera.

**Does this work on macOS/Linux?**  
XInput is Windows-native. Ports welcome — PRs encouraged!

---

## 🧰 Development

- Single-file add-on: `fps_gamepad_camera.py`
- Versioning: bump `bl_info["version"]` on changes (e.g. `(1, 15, 1)` → `(1, 15, 2)`).
- Code style: keep UI responsive, avoid blocking calls, use edge-triggered button logic.

---

## 🤝 Contributing

Issues and PRs welcome. Ideas: non-Windows input backend, speed boost modifiers, camera collision, or path recording.

---

## 📜 License

MIT License — free to use, modify, and share. Please credit **Leddy & GPT**.

