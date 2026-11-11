#!/usr/bin/env python3
"""Read-only helper for CapCut Desktop drafts (Windows).

  python draft_tool.py backup  <project>            copy the draft folder to Documents/capcut_backups
  python draft_tool.py summary <project> [t0] [t1]  tracks/segments with times, volume, keyframes, masks, effects
  python draft_tool.py loudness <project> [t0] [t1] ffmpeg LUFS of timeline clips/voiceovers (needs ffmpeg)

Never writes into the draft. CapCut keeps the project in memory and autosaves every few
seconds, so wait ~5 s after a UI change before trusting `summary`.
"""
import json, math, os, shutil, subprocess, sys, time

DRAFTS = os.path.expanduser(r"~\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
BACKUPS = os.path.expanduser(r"~\Documents\capcut_backups")
FFMPEG_CANDIDATES = [r"C:\Program Files\Shotcut\ffmpeg.exe"]


def load(project):
    p = os.path.join(DRAFTS, project, "draft_content.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f), p


def db(v):
    return "-inf" if v <= 0 else "%+.1fdB" % (20 * math.log10(v))


def backup(project):
    src = os.path.join(DRAFTS, project)
    os.makedirs(BACKUPS, exist_ok=True)
    dst = os.path.join(BACKUPS, "%s_%s" % (project, time.strftime("%Y%m%d_%H%M")))
    shutil.copytree(src, dst)
    print("backup ->", dst)


def names(m):
    vid = {v["id"]: os.path.basename(v.get("path", "")) for v in m.get("videos", [])}
    aud = {a["id"]: (a.get("name") or os.path.basename(a.get("path", ""))) for a in m.get("audios", [])}
    return vid, aud


def summary(project, t0=0.0, t1=1e9):
    d, p = load(project)
    m = d["materials"]
    vid, aud = names(m)
    byid = {x["id"]: (k, x) for k, v in m.items() if isinstance(v, list) for x in v if isinstance(x, dict) and "id" in x}
    print("saved:", time.ctime(os.path.getmtime(p)), "| duration %.1fs" % (d["duration"] / 1e6))
    for i, t in enumerate(d["tracks"]):
        segs = [s for s in t["segments"] if t0 <= s["target_timerange"]["start"] / 1e6 <= t1]
        if not segs:
            continue
        print("\ntrack %d [%s] %d segments" % (i, t["type"], len(segs)))
        for s in segs:
            tr = s["target_timerange"]
            a, b = tr["start"] / 1e6, (tr["start"] + tr["duration"]) / 1e6
            nm = vid.get(s["material_id"]) or aud.get(s["material_id"]) or ("TEXT" if t["type"] == "text" else "?")
            extra = []
            if t["type"] in ("video", "audio"):
                extra.append("vol " + db(s.get("volume", 1)))
            for k in s.get("common_keyframes", []):
                extra.append("kf:%s(%d)" % (k["property_type"].replace("KFType", ""), len(k["keyframe_list"])))
            for r in s.get("extra_material_refs", []):
                k, x = byid.get(r, ("?", {}))
                if k == "common_mask":
                    c = x.get("config", {})
                    extra.append("MASK %s w%.2f h%.2f feather%.2f invert=%s" % (x.get("resource_type"), c.get("width", 0), c.get("height", 0), c.get("feather", 0), c.get("invert")))
                elif k == "video_effects":
                    extra.append("fx:" + str(x.get("name")))
                elif k == "transitions":
                    extra.append("transition:" + str(x.get("name")))
                elif k == "effects":
                    extra.append("adj:%s=%.2f" % (x.get("type"), x.get("value", 0)))
            print("  %7.2f-%7.2f  %-36s %s" % (a, b, nm[:36].encode("ascii", "ignore").decode(), " ".join(extra)))


def ffmpeg():
    for c in FFMPEG_CANDIDATES:
        if os.path.exists(c):
            return c
    return shutil.which("ffmpeg")


def lufs(path, ss=None, dur=None):
    cmd = [ffmpeg(), "-hide_banner", "-nostats"]
    if ss is not None:
        cmd += ["-ss", str(ss)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    for line in out.splitlines()[::-1]:
        if line.strip().startswith("I:"):
            return line.split()[1]
    return "n/a"


def loudness(project, t0=0.0, t1=1e9):
    d, _ = load(project)
    m = d["materials"]
    if not ffmpeg():
        sys.exit("ffmpeg not found")
    base = os.path.join(DRAFTS, project)
    for t in d["tracks"]:
        for s in t["segments"]:
            st = s["target_timerange"]["start"] / 1e6
            if not (t0 <= st <= t1) or t["type"] not in ("video", "audio"):
                continue
            src = next((x for k in ("videos", "audios") for x in m.get(k, []) if x["id"] == s["material_id"]), None)
            if not src:
                continue
            path = src["path"].replace("##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##", base.replace("\\", "/"))
            if not os.path.exists(path):
                continue
            sr = s["source_timerange"]
            vol = s.get("volume", 1)
            print("%7.1f  %-30s source %s LUFS  gain %s" % (st, os.path.basename(path)[:30], lufs(path, sr["start"] / 1e6, sr["duration"] / 1e6), db(vol)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, proj = sys.argv[1], sys.argv[2]
    a = [float(x) for x in sys.argv[3:5]]
    {"backup": lambda: backup(proj), "summary": lambda: summary(proj, *a), "loudness": lambda: loudness(proj, *a)}[cmd]()
