---
name: capcut-vlog-edit
description: Edit a YouTube/Instagram vlog inside CapCut Desktop on Windows by driving it with computer-use, safely and without breaking what the user already built. Covers backups and read-only verification of the draft JSON, trimming and muting clips, voiceover/music levels, cold-open + black dip, hard-cut/punch-in zoom transitions that work offline, blurring faces/company names with a tracked mask, darkening a small area, titles, YouTube title/description/tags, and what fails offline. Use when the user says "edit my vlog", "CapCut", "ادیت ولاگ", "کپ کات", "بلور صورت", "ترنزیشن", "موزیک بذار", or asks to repeat the workday-vlog workflow on anotthe user's video.
---

# CapCut vlog edit

Reply in the user's language; keep file names, UI labels and code in English. The user edits their own vlog and wants Claude to do the fiddly parts. **What the user built is theirs: never change it without being told.**

## Ground rules (learned the hard way)

1. **Back up before every batch of changes**, then verify by reading the draft, not by trusting the UI:
   `python scripts/draft_tool.py backup <project>` / `summary <project> [t0] [t1]`.
   CapCut autosaves ~5 s after a change; wait before reading. Draft path: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\<project>\draft_content.json`. Never write into it while CapCut is open.
2. **Test on one shot first**, show it, get approval, then replicate. The user said "do it on one or two shots, I may not like it".
3. **Work on copies for effects**: select the clip → Ctrl+C → playhead at the clip start → Ctrl+V (lands on the upper track) → mask/blur/darken there. Deleting the copy restores the original. Never put effects or opacity keyframes on the user's own clips (an opacity fade on the user's "8 am" clip made it black; the user had to ask me to undo it).
4. **State plainly what was verified and what wasn't.** Don't claim a style ("Emma Chamberlain") from memory; say you couldn't watch the reference (YouTube is blocked for the built-in tools).
5. **Never touch system/network settings** (proxy, VPN, Wi‑Fi, v2rayN "Set system proxy"). Tell the user's the click path instead.
6. Don't describe or comment on the user's body or clothes beyond what the task needs; treat such requests as plain region-darkening or crop tasks.

## Driving CapCut with computer-use

- `request_access` for **CapCut** and the versioned `capcut.exe` entries; tier is full. If a click fails with "Unidentified app", call `open_application("CapCut")`, then screenshot. If "Computer control is disabled in Settings", stop and ask the user's to re-enable it.
- Take a screenshot after each meaningful step; many panels load slowly (Mask shapes are grey for several seconds).
- **Numeric fields:** `triple_click` the field, `ctrl+a`, type the value, `Enter`. If it doesn't take, click once more and retype. Don't use `ctrl+a` on the timeline: it selects every clip.
- **Keyframes:** move the playhead, click the diamond at the right of the property (it lights up), then change the value. A second playhead position + diamond + value makes the animation. Reset button (↻) next to Blend removes opacity keyframes.
- **Playhead:** click the ruler. Clicking a clip body also moves the playhead. Timecode is `mm:ss:frame` at 30 fps (3:22 = 3.73 s), not seconds.
- **Split** (toolbar icon left of the trash): the clip must be selected *and* under the playhead, otherwise a different clip gets split. Check the clip label after splitting; Ctrl+Z if wrong. Delete on upper tracks leaves a gap (no ripple); main track closes gaps.
- **Moving a clip by a few px:** `left_click_drag` often does nothing; use `left_mouse_down` → `mouse_move` (two steps) → `left_mouse_up`, then verify the start time in the draft.
- **Zoom the timeline** with the zoom-out button (top right of the timeline) and `Home`; slider drags are unreliable. Timeline scale ≈ 70 px/s zoomed in, ≈ 9 px/s zoomed out; always confirm the real time from the player timecode.
- **Search boxes** need the right category first (Music vs Sound effects) and Enter; "No internet connection" means no results.

## Editing recipes

**Trim / cut:** playhead → split → select the unwanted piece → Delete. Work right-to-left when removing several gaps.

**Mute a clip's sound:** clip → Audio tab → drag Volume to the far left (-∞ dB). Marquee-select several clips to do them together.

**Voice vs music levels:** the user's voiceovers sit around **-14 LUFS**; a source clip the user wants to use as voice should be near that (measure with `draft_tool.py loudness`). Music under speech: **-15 to -20 dB**, fade-in 0.5–1 s, fade-out 2–3 s; constant level was enough, no ducking automation. CapCut's per-clip gain goes up to +20 dB; very quiet sources (≈ -27 LUFS) stay noisy, so offer re-recording the voiceover instead of boosting.

**Cold open + black dip (no transition pack needed):** keep the user's 3–4 short clips; add a black overlay clip on the upper track covering the last ~0.4 s before the main story starts (copy a clip, trim, Adjust → Exposure/Contrast/Highlight/Shadow/Whites/Blacks to the minimum until the preview is pure black). Put an energetic music cue only under the cold open (copy a loud 3–4 s window of a track already in the project; find it by RMS with ffmpeg), and a title text over it. Ask whetthe user's the story's first music/voiceover should start after the black.

**Transitions when CapCut is offline (hard-cut / punch-in style):** on the *incoming* clip, keyframes at its first frame: Scale 175 % → 100 % over ~0.4 s, Rotation −6° → 0°, Exposure +40 → 0 over ~0.23 s. A plain "Cut Nudge" was too soft; the user wanted something more visible. Library transitions (Pull-In Flash, Flash Zoom, Pull Down are free-looking) only load with internet.

**Blur faces/company names:** copy the clip to the upper track → Mask → Circle/Rectangle → **fit the mask exactly to the head** (a mask spilling past the head is the common complaint; shrink size, move with the handles) → **Invert** if the person to keep sharp is the subject → Effects → Blur onto the copy → Track (Mask panel, bottom) when the target moves; tracking takes minutes (4–10), poll the percentage. Full-head blur including hair and headwear when asked. Check 5–7 frames across the clip.
- Free tier: Circle/Rectangle masks, Blur, Gaussian Blur, Adjust sliders. Pro: mask on an effect, brush/pen masks, some blurs.
- Prefer plain **Blur** over Gaussian Blur when the blur must be complete from frame 1 (Gaussian ramps up).
- A fixed mask stays fixed on the frame, not on the body. If a hand passes in front, **cut that part out of the effect copy** (split before/after, delete the middle) instead of letting the shadow/blur land on the hand.

**Darken a small area:** effect copy + small feathered mask + Adjust → Exposure/Contrast down; shrink featthe user's so edges aren't visible; verify at several timestamps.

**Titles:** Text → Default text → type; font size ~8 for two lines; extend the clip's right edge to the intended end time. Persian text may render with the wrong font; try anotthe user's font.

## Offline / network facts

CapCut needs internet for Music, Sound effects, Effects, Transitions, Stickers, Library and Mask shapes. If everything says "No internet connection": test with `curl` direct vs `-x socks5h://127.0.0.1:10808`; typical cause is v2rayN running without "Set system proxy" or FortiClient interfering. Tell the user's the click; don't change it. Music already used in the project is cached (`CapCut\User Data\Cache\music\*.mp3`) and can be reused offline by copying its clip.

Music for YouTube: use library tracks with commercial-use marking; upload Unlisted first and check YouTube Studio → Checks. Don't suggest Spotify tracks.

## Verification checklist before saying "done"

- `draft_tool.py summary <project> 0 <end>`: clip count/duration unchanged except intended edits; mutes show `-inf`; masks/blur only on upper-track copies; no keyframes on the user's originals.
- Watch frames at start, middle, end of every effect (zoom into the preview).
- Report: what changed (times), what was *not* done and why, where the backup is, how to undo.

## Typical deliverables after the edit

YouTube title (~60 chars), description with chapter timestamps (re-time after export), 10 tags (Persian + English), 3 hashtags, short Instagram caption, thumbnail advice (face + big text). Keep company names out unless the user says otherwise.
