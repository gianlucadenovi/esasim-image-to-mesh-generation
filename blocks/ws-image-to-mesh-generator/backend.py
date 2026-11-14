# ── EsaSim block ──────────────────────────────────────────────────────
# Image to mesh generator (ws-image-to-mesh-generator) · version 14 · machine block, Python: def run(ctx)
# Photos to 3D meshes on an NVIDIA GPU: TripoSR (coloured), Hunyuan3D-2 mini (detailed shape) or Hunyuan3D-2 multi-view (front/left/back/right fused); GLB/OBJ/STL/PLY, shaded previews.
# Workspace: Gianluca De Novi's workspace · Author: Gianluca De Novi
# Saved: 2026-11-14
#
# Inputs   ctx.inputs["id"] is a list of files: .path .name .size .read_text() .read_json()
#   images      Files (png, jpg, jpeg, webp) Images (optional) · several · optional · Pictures for a run started from the blueprint (with Run without the View on)
# Outputs  ctx.output("id", "name.ext") is the path to write; ctx.write_json / ctx.write_text
#   glb         Files (glb)               Meshes (GLB) · One GLB per object: for the 3D view and downloads
#   exports     Files (obj, stl, ply)     Other formats
#   previews    Files (png)               Previews
#   table       Table (csv)               Mesh inventory
#   metadata    Files (json)              Run metadata
#   telemetry   Live telemetry            ctx.telemetry("channel", data) while it runs
# Settings ctx.params["key"]
#   model       select    Model = "Hunyuan3D-2 mini" of TripoSR | Hunyuan3D-2 mini | Hunyuan3D-2 multi-view
#   quality     select    Quality = "balanced" of fast | balanced | high
#   candidates  number    Variations per object (Hunyuan3D-2) = 1
#   seed        number    Seed = 1234
#   formats     text      Mesh formats = "glb,obj,stl,ply"
#   image_urls  textarea  Image links = ""
#   run_without_view bool      Run without the View = false
#   launch      bool      Requested by Mesh Studio (View only) = false
#   session     text      Upload session (View only) = ""
#   upload_manifest textarea  Upload manifest (View only) = ""
#   compact_count number    Compact upload pieces (View only) = 0
#   compact_len number    Compact upload length (View only) = 0
#   c00         textarea  Compact upload 1 (View only) = ""
#   c01         textarea  Compact upload 2 (View only) = ""
#   c02         textarea  Compact upload 3 (View only) = ""
#   c03         textarea  Compact upload 4 (View only) = ""
#   c04         textarea  Compact upload 5 (View only) = ""
#   c05         textarea  Compact upload 6 (View only) = ""
#   c06         textarea  Compact upload 7 (View only) = ""
#   c07         textarea  Compact upload 8 (View only) = ""
#   c08         textarea  Compact upload 9 (View only) = ""
#   c09         textarea  Compact upload 10 (View only) = ""
#   c10         textarea  Compact upload 11 (View only) = ""
#   c11         textarea  Compact upload 12 (View only) = ""
#   c12         textarea  Compact upload 13 (View only) = ""
#   c13         textarea  Compact upload 14 (View only) = ""
#   c14         textarea  Compact upload 15 (View only) = ""
#   c15         textarea  Compact upload 16 (View only) = ""
#   c16         textarea  Compact upload 17 (View only) = ""
#   c17         textarea  Compact upload 18 (View only) = ""
#   c18         textarea  Compact upload 19 (View only) = ""
#   c19         textarea  Compact upload 20 (View only) = ""
#   c20         textarea  Compact upload 21 (View only) = ""
#   c21         textarea  Compact upload 22 (View only) = ""
#   c22         textarea  Compact upload 23 (View only) = ""
#   c23         textarea  Compact upload 24 (View only) = ""
#   c24         textarea  Compact upload 25 (View only) = ""
#   c25         textarea  Compact upload 26 (View only) = ""
#   c26         textarea  Compact upload 27 (View only) = ""
#   c27         textarea  Compact upload 28 (View only) = ""
#   c28         textarea  Compact upload 29 (View only) = ""
#   c29         textarea  Compact upload 30 (View only) = ""
#   c30         textarea  Compact upload 31 (View only) = ""
#   c31         textarea  Compact upload 32 (View only) = ""
#   c32         textarea  Compact upload 33 (View only) = ""
#   c33         textarea  Compact upload 34 (View only) = ""
#   c34         textarea  Compact upload 35 (View only) = ""
#   c35         textarea  Compact upload 36 (View only) = ""
#   c36         textarea  Compact upload 37 (View only) = ""
#   c37         textarea  Compact upload 38 (View only) = ""
#   c38         textarea  Compact upload 39 (View only) = ""
#   c39         textarea  Compact upload 40 (View only) = ""
#   c40         textarea  Compact upload 41 (View only) = ""
#   c41         textarea  Compact upload 42 (View only) = ""
#   c42         textarea  Compact upload 43 (View only) = ""
#   c43         textarea  Compact upload 44 (View only) = ""
#   c44         textarea  Compact upload 45 (View only) = ""
#   c45         textarea  Compact upload 46 (View only) = ""
#   c46         textarea  Compact upload 47 (View only) = ""
#   c47         textarea  Compact upload 48 (View only) = ""
# Runs on  NVIDIA GPU. Return a dict to fill the "result" output.
# Packages torch[cuda], numpy, Pillow, trimesh, matplotlib (installed by the worker with pip when missing)
# EsaSim rewrites these lines from the block's definition each time it is saved: change the definition, not them.
# ── end of EsaSim block header ────────────────────────────────────────

"""Image to mesh: photographs become 3D meshes on the machine's NVIDIA GPU.

Models
  TripoSR (VAST AI, MIT)                 one photo -> coloured mesh, a few seconds
  Hunyuan3D-2 mini (Tencent, 0.6B)       one photo -> detailed shape (no colour)
  Hunyuan3D-2 mv (Tencent, 1.1B)         front/left/back/right photos of one object -> one shape

Pictures come from the Mesh Studio view (compactly in the run's own settings, or live in pieces as messages), from
links in Image links, or from files wired to the Images input. The model code is cloned once into the machine's cache
and run in a subprocess with the library versions it was written for (Transformers 4.45), so nothing else on the
worker changes."""
import base64
import csv
import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

MODELS = {
    "TripoSR": {"kind": "triposr", "views": 1},
    "Hunyuan3D-2 mini": {"kind": "hunyuan", "views": 1, "repo": "tencent/Hunyuan3D-2mini",
                         "sub": "hunyuan3d-dit-v2-mini", "turbo": "hunyuan3d-dit-v2-mini-turbo"},
    "Hunyuan3D-2 multi-view": {"kind": "hunyuan", "views": 4, "repo": "tencent/Hunyuan3D-2mv",
                               "sub": "hunyuan3d-dit-v2-mv", "turbo": "hunyuan3d-dit-v2-mv-turbo"},
}
ALIASES = {"Stable Fast 3D": "Hunyuan3D-2 mini"}            # removed: needs a C++/CUDA build on Windows, gated
VIEWS = ("front", "left", "back", "right")
QUALITY = {  # TripoSR marching-cubes resolution; Hunyuan steps, octree resolution, turbo
    "fast": {"mc": 192, "steps": 5, "octree": 256, "turbo": True, "faces": 40000},
    "balanced": {"mc": 256, "steps": 30, "octree": 320, "turbo": False, "faces": 80000},
    "high": {"mc": 320, "steps": 50, "octree": 380, "turbo": False, "faces": 150000},
}
CHANNEL = "mesh_upload"
MAX_SIDE = 1024


def run(ctx):
    p = ctx.params
    hb = {"stage": "preparing", "message": "Preparing", "percent": 1}
    stop = threading.Event()

    def update(stage, msg, pct=None, **extra):
        if pct is not None:
            hb["percent"] = int(max(0, min(100, pct)))
            ctx.progress(hb["percent"], msg)
        hb.update(stage=stage, message=msg)
        ctx.log("[mesh] " + msg)
        ctx.telemetry("mesh_status", dict(stage=stage, message=msg, percent=hb["percent"], **extra))

    has_inputs = bool(ctx.inputs.get("images")) or str(p.get("image_urls") or "").strip()
    if not p.get("launch", False) and not (p.get("run_without_view") and has_inputs):
        update("idle", "Mesh Studio ready. Choose images in the View and click Generate meshes.", 100)
        return {"status": "idle"}

    def heartbeat():
        while not stop.wait(15):
            try:
                ctx.progress(hb["percent"], hb["message"])
                ctx.telemetry("mesh_status", {"stage": hb["stage"], "message": hb["message"], "percent": hb["percent"], "heartbeat": True})
            except Exception:
                pass
    threading.Thread(target=heartbeat, daemon=True).start()
    try:
        return generate(ctx, p, update)
    finally:
        stop.set()


# ------------------------------------------------------------------------------------------------ pictures
def receive_upload(ctx, p, update):
    """The View's pictures: in the run's own settings (compact upload), or a manifest in the settings and the bytes
    as messages in pieces, asking for what is missing until everything is here (the View answers each request)."""
    compact = int(p.get("compact_count") or 0)
    if compact:                                                    # the pictures came in the run's own settings
        pieces = [str(p.get("c%02d" % k) or "") for k in range(compact)]
        data, want = "".join(pieces), int(p.get("compact_len") or 0)
        if want and len(data) != want:
            sizes = sorted(set(len(x) for x in pieces[:-1])) if len(pieces) > 1 else [len(pieces[0])]
            raise RuntimeError("The compact upload arrived cut short: %d of %d characters (setting lengths seen: %s). EsaSim shortens "
                               "long run settings; tell us this number so the piece size can be lowered." % (len(data), want, sizes))
        items = json.loads(data)
        update("upload_complete", "%d picture%s received in the run's settings (compact upload)." % (len(items), "s" if len(items) != 1 else ""), 8)
        out = []
        for it in items:
            raw = str(it.get("data") or "")
            out.append({"name": str(it.get("name") or "image"), "bytes": base64.b64decode(raw.split(",", 1)[-1]),
                        "view": str(it.get("view") or ""), "object": str(it.get("object") or "")})
        return out
    session = str(p.get("session") or "")
    manifest = json.loads(str(p.get("upload_manifest") or "[]"))
    if not session or not manifest:
        return []
    total = sum(int(m["parts"]) for m in manifest)
    names = [str(m.get("name") or "") for m in manifest]
    got, stats = {}, {"messages": 0, "other_session": 0, "unreadable": 0, "kinds": set()}
    last_ask, last_diag, t0 = 0.0, time.time(), time.time()

    def fetch():
        """ctx.messages(channel) as documented; also the unfiltered queue, in case this worker names channels differently."""
        out = []
        for args in ((CHANNEL,), ()):
            try:
                r = ctx.messages(*args)
            except TypeError:
                continue
            except Exception as e:
                stats["kinds"].add("error: %s" % type(e).__name__)
                continue
            if r:
                out.extend(list(r))
        return out
    while True:
        for m in fetch():
            stats["messages"] += 1
            stats["kinds"].add(type(m).__name__)
            d = m
            if isinstance(d, dict) and isinstance(d.get("data"), dict):
                d = d["data"]
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except ValueError:
                    pass
            if not isinstance(d, dict) or "b64" not in d:
                stats["unreadable"] += 1
                continue
            if str(d.get("session")) != session:
                stats["other_session"] += 1
                continue
            try:
                got[(int(d["i"]), int(d["part"]))] = str(d["b64"])
            except (KeyError, TypeError, ValueError):
                stats["unreadable"] += 1
        missing = [[int(m["i"]), k] for m in manifest for k in range(int(m["parts"])) if (int(m["i"]), k) not in got]
        if not missing:
            break
        now = time.time()
        if now - last_ask > 3:
            last_ask = now
            update("awaiting_upload", "Waiting for the pictures from the View: %d of %d pieces" % (total - len(missing), total),
                   2 + 6 * (total - len(missing)) / max(1, total), session=session, names=names, piece=45000,
                   missing=missing[:300], received=total - len(missing), total=total)
        if now - last_diag > 30:
            last_diag = now
            ctx.log("[upload] %d message(s) seen so far (%s); %d for another upload, %d unreadable."
                    % (stats["messages"], ", ".join(sorted(stats["kinds"])) or "none", stats["other_session"], stats["unreadable"]))
        if stats["messages"] == 0 and now - t0 > 60:
            update("upload_failed", "No message from the View reached this run in 60 s. Press Generate meshes again (compact upload).", 2, session=session)
            raise RuntimeError("No message from the View reached this run in 60 s, so live transfer does not work here. Press "
                               "Generate meshes again: the View now sends the pictures in the run's own settings.")
        if now - t0 > 240:
            raise RuntimeError("The pictures did not reach this run from the View within 4 minutes (%d of %d pieces; %d message(s) "
                               "seen). Keep the View open after pressing Generate meshes." % (total - len(missing), total, stats["messages"]))
        time.sleep(0.4)
    update("upload_complete", "All %d picture%s received." % (len(manifest), "s" if len(manifest) != 1 else ""), 8, session=session)
    out = []
    for m in manifest:
        data = "".join(got[(int(m["i"]), k)] for k in range(int(m["parts"])))
        raw = base64.b64decode(data.split(",", 1)[1] if data.startswith("data:") else data)
        if m.get("sha256") and hashlib.sha256(raw).hexdigest() != m["sha256"]:
            raise RuntimeError("Picture %s arrived damaged (checksum mismatch): press Generate meshes again." % m.get("name"))
        out.append({"name": str(m.get("name") or "image_%d" % m["i"]), "bytes": raw, "view": str(m.get("view") or ""),
                    "object": str(m.get("object") or "")})
    return out


def other_pictures(ctx, p):
    out = []
    for f in ctx.inputs.get("images", []) or []:
        if re.search(r"\.(png|jpe?g|webp|bmp)$", f.name, re.I):
            with open(f.path, "rb") as fh:
                out.append({"name": f.name, "bytes": fh.read(), "view": "", "object": ""})
    for url in [u.strip() for u in str(p.get("image_urls") or "").splitlines() if u.strip()]:
        req = urllib.request.Request(url, headers={"User-Agent": "EsaSim-mesh/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.append({"name": url.rstrip("/").split("/")[-1].split("?")[0] or "image", "bytes": r.read(), "view": "", "object": ""})
    return out


def view_of(name):
    m = re.search(r"[_\-\s](front|left|back|right)$", pathlib.Path(name).stem, re.I)
    return m.group(1).lower() if m else ""


def object_of(name):
    stem = pathlib.Path(name).stem
    return re.sub(r"[_\-\s](front|left|back|right|side|top|bottom|view\d*)$", "", stem, flags=re.I) or stem


# ------------------------------------------------------------------------------------------------ main
def generate(ctx, p, update):
    from PIL import Image
    choice = ALIASES.get(str(p.get("model") or "TripoSR"), str(p.get("model") or "TripoSR"))
    if choice not in MODELS:
        raise ValueError("Model: one of %s." % ", ".join(MODELS))
    spec = MODELS[choice]
    quality = str(p.get("quality") or "balanced")
    q = QUALITY.get(quality, QUALITY["balanced"])
    variants = max(1, min(4, int(p.get("candidates") or 1))) if spec["kind"] == "hunyuan" else 1
    seed0 = int(p.get("seed") or 1234)
    formats = [x for x in (s.strip().lower() for s in str(p.get("formats") or "glb,obj,stl,ply").split(",")) if x in ("glb", "obj", "stl", "ply")] or ["glb"]
    if "glb" not in formats:
        formats.insert(0, "glb")

    update("preparing", "Collecting the pictures…", 2)
    pics = receive_upload(ctx, p, update) if p.get("launch") else []
    pics += other_pictures(ctx, p)
    if not pics:
        raise ValueError("No pictures: add images in the Mesh Studio view (or Image links / the Images input).")
    if len(pics) > 24:
        raise ValueError("At most 24 pictures per run.")

    work = pathlib.Path(ctx.folder) / "mesh_inputs"
    work.mkdir(parents=True, exist_ok=True)
    images = []
    for i, pic in enumerate(pics):
        im = Image.open(io.BytesIO(pic["bytes"]))
        im.load()
        im = im.convert("RGBA") if (im.mode in ("RGBA", "LA", "P") and "A" in im.convert("RGBA").getbands()) else im.convert("RGB")
        if max(im.size) > MAX_SIDE:
            s = MAX_SIDE / max(im.size)
            im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        path = work / ("in_%02d.png" % i)
        im.save(path)
        images.append({"name": pic["name"], "path": path, "view": (pic["view"] or view_of(pic["name"])).lower(),
                       "object": pic["object"] or object_of(pic["name"]), "size": im.size})

    # objects: one per picture, or (multi-view) the pictures of one object by view
    objects = []
    if spec["views"] > 1:
        groups = {}
        for im in images:
            groups.setdefault(im["object"], []).append(im)
        for name, ims in groups.items():
            views, free = {}, [v for v in VIEWS]
            for im in ims:
                if im["view"] in VIEWS and im["view"] not in views:
                    views[im["view"]] = im
                    free.remove(im["view"])
            for im in ims:
                if im not in views.values() and free:
                    views[free.pop(0)] = im
            if "front" not in views:
                raise ValueError("Object %s has no front view: mark one of its pictures as front." % name)
            objects.append({"name": name, "views": views})
    else:
        for im in images:
            objects.append({"name": im["object"], "views": {"front": im}})
    seen = {}
    for o in objects:                                               # unique, file-safe names
        base = re.sub(r"[^A-Za-z0-9_-]+", "_", o["name"])[:40].strip("_") or "object"
        seen[base] = seen.get(base, 0) + 1
        o["safe"] = base if seen[base] == 1 else "%s_%d" % (base, seen[base])

    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("These models need an NVIDIA GPU usable from PyTorch, and this machine has none.")
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    update("preparing", "%d object%s with %s (%s quality) on %s, %.0f GB." % (len(objects), "s" if len(objects) != 1 else "", choice, quality, gpu, vram), 9)

    env = prepare_env(ctx, spec, update)
    out_root = pathlib.Path(ctx.folder) / "mesh_raw"
    out_root.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    if spec["kind"] == "triposr":
        raw = run_triposr(ctx, env, objects, q, out_root, update)
    else:
        raw = run_hunyuan(ctx, env, spec, objects, q, variants, seed0, out_root, update)

    import trimesh
    rows = []
    for k, (obj, var, path, secs) in enumerate(raw):
        mesh = load_mesh(path)
        if spec["kind"] == "triposr":                               # TripoSR is Z-up, facing -X: stand it up facing +Z (glTF)
            import numpy as np
            mesh.fix_normals()
            mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
            mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [0, 1, 0]))
        lo, hi = mesh.bounds
        mesh.apply_translation([-(lo[0] + hi[0]) / 2, -lo[1], -(lo[2] + hi[2]) / 2])   # centred, standing on y = 0
        stem = obj["safe"] + ("_v%d" % (var + 1) if variants > 1 else "")
        files = []
        for fmt in formats:
            target = ctx.output("glb" if fmt == "glb" else "exports", stem + "." + fmt)
            mesh.export(target, file_type=fmt)
            files.append(stem + "." + fmt)
        render_preview(mesh, ctx.output("previews", stem + "_preview.png"))
        row = {"object": stem, "model": choice, "views": ",".join(sorted(obj["views"])), "pictures": ";".join(v["name"] for v in obj["views"].values()),
               "variation": var + 1, "vertices": len(mesh.vertices), "faces": len(mesh.faces), "watertight": bool(mesh.is_watertight),
               "colour": "vertex colours" if getattr(mesh.visual, "kind", None) == "vertex" else "none",
               "height_units": round(float(mesh.extents[1]), 3), "seconds": round(secs, 1), "files": ";".join(files), "preview": stem + "_preview.png"}
        rows.append(row)
        ctx.telemetry("mesh_done", {"object": stem, "vertices": row["vertices"], "faces": row["faces"]})
        update("exported", "%s: %d vertices, %d faces, exported as %s." % (stem, row["vertices"], row["faces"], ", ".join(f.upper() for f in formats)),
               90 + 9 * (k + 1) / len(raw))
    with open(ctx.output("table", "models.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ctx.write_json("metadata", "generation.json", {"model": choice, "quality": quality, "settings": q, "variations": variants,
                                                    "seed": seed0, "gpu": gpu, "objects": rows, "total_s": round(time.time() - t_all, 1),
                                                    "licence": "TripoSR: MIT. Hunyuan3D-2: Tencent Hunyuan Community licence (not for use in the EU, UK or South Korea)."})
    update("done", "Finished: %d mesh%s from %d picture%s in %.0f s." % (len(rows), "es" if len(rows) != 1 else "", len(images),
                                                                        "s" if len(images) != 1 else "", time.time() - t_all), 100)
    return {"meshes": len(rows), "model": choice, "gpu": gpu}


def load_mesh(path):
    import trimesh
    asset = trimesh.load(str(path), force="scene", process=False)
    geoms = [g for g in asset.geometry.values() if isinstance(g, trimesh.Trimesh)] if hasattr(asset, "geometry") else [asset]
    if not geoms:
        raise RuntimeError("The model wrote an empty mesh (%s)." % path)
    if hasattr(asset, "dump"):
        geoms = [g for g in asset.dump() if isinstance(g, trimesh.Trimesh)] or geoms   # scene transforms applied
    return geoms[0] if len(geoms) == 1 else trimesh.util.concatenate(geoms)


# ------------------------------------------------------------------------------------------------ environments
def cache_root():
    return pathlib.Path(os.environ.get("ESASIM_MESH_REPOS", str(pathlib.Path.home() / ".cache" / "esasim-mesh")))


def short_temp(fallback):
    roots = [pathlib.Path(os.environ.get("SystemRoot", "C:/Windows")) / "Temp", pathlib.Path(os.environ.get("PUBLIC", "C:/Users/Public"))] if os.name == "nt" else [pathlib.Path("/tmp")]
    for root in roots:
        try:
            d = root / "em"
            d.mkdir(parents=True, exist_ok=True)
            probe = d / ("_probe_%d" % os.getpid())
            probe.write_text("ok")
            probe.unlink()
            return d
        except OSError:
            continue
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def pip(ctx, args, env, cwd, timeout=1800):
    cmd = [sys.executable, "-m", "pip", "install", "--no-warn-script-location", "--disable-pip-version-check"] + args
    r = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, errors="replace", timeout=timeout)
    if r.returncode:
        ctx.log("[pip] " + (r.stdout[-2500:] + "\n" + r.stderr[-2500:]))
        raise RuntimeError("Installing %s failed (see the log above)." % " ".join(a for a in args if not a.startswith("-"))[:200])


def prepare_env(ctx, spec, update):
    cache = cache_root()
    cache.mkdir(parents=True, exist_ok=True)
    scratch = short_temp(cache / "tmp")
    env = dict(os.environ)
    env.update(TMP=str(scratch), TEMP=str(scratch), TMPDIR=str(scratch), PIP_USER="0", PYTHONNOUSERSITE="1",
               PYTHONIOENCODING="utf-8", HF_HUB_DISABLE_SYMLINKS_WARNING="1", PYTHONUNBUFFERED="1")
    # Transformers 4.45 for both models (their DINO/CLIP image encoders do not load with Transformers 5), isolated
    compat = cache / "hf-compat-4_45"
    if not (compat / ".ready").exists():
        update("installing", "Installing Transformers 4.45 for the mesh models (once per machine)…", 9)
        pip(ctx, ["--target", str(compat), "--no-deps", "--upgrade", "transformers==4.45.0", "tokenizers==0.20.3",
                  "huggingface-hub==0.34.0", "diffusers==0.32.2"], env, scratch, 900)
        (compat / ".ready").write_text("ok")
    deps = cache / "mesh-deps-v1"
    if not (deps / ".ready").exists():
        update("installing", "Installing the mesh libraries (once per machine, a few minutes)…", 9)
        # none of these depend on PyTorch, so pip --target does not pull a second copy of it
        pip(ctx, ["--target", str(deps), "--prefer-binary", "omegaconf==2.3.0", "einops>=0.7", "rembg", "onnxruntime",
                  "scikit-image", "trimesh", "pymeshlab", "opencv-python-headless", "pyyaml", "tqdm", "imageio", "xatlas",
                  "moderngl", "regex", "requests", "filelock", "fsspec", "packaging", "safetensors", "typing-extensions",
                  "importlib-metadata"], env, scratch)
        # accelerate declares PyTorch as a dependency: install it alone, without dependencies
        pip(ctx, ["--target", str(deps), "--no-deps", "accelerate", "psutil"], env, scratch, 600)
        (deps / ".ready").write_text("ok")
    env["PYTHONPATH"] = os.pathsep.join([str(compat), str(deps), env.get("PYTHONPATH", "")])
    env["U2NET_HOME"] = str(cache / "rembg")                       # background-removal model, kept with the rest

    if spec["kind"] == "triposr":
        repo = cache / "TripoSR"
        if not (repo / "run.py").exists():
            update("installing", "Downloading TripoSR's code…", 9)
            subprocess.run(["git", "clone", "--depth", "1", "https://github.com/VAST-AI-Research/TripoSR.git", str(repo)], check=True, timeout=300)
        patch_triposr(repo)
    else:
        repo = cache / "Hunyuan3D-2"
        if not (repo / "hy3dgen").exists():
            update("installing", "Downloading Hunyuan3D-2's code…", 9)
            subprocess.run(["git", "clone", "--depth", "1", "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git", str(repo)], check=True, timeout=300)
        env["HY3DGEN_MODELS"] = str(cache / "hy3dgen-models")
    env["ESASIM_REPO"] = str(repo)
    check = "import skimage.measure, einops, omegaconf, rembg, trimesh, transformers; assert transformers.__version__ == '4.45.0', transformers.__version__"
    if spec["kind"] == "hunyuan":
        check = "import sys; sys.path.insert(0, %r); " % str(repo) + check + "; import pymeshlab, cv2, diffusers; from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline"
    r = subprocess.run([sys.executable, "-c", check], cwd=str(repo), env=env, capture_output=True, text=True, errors="replace", timeout=300)
    if r.returncode:
        ctx.log("[setup] " + r.stderr[-2500:])
        raise RuntimeError("The %s environment does not import cleanly (see the log above)." % ("TripoSR" if spec["kind"] == "triposr" else "Hunyuan3D-2"))
    update("ready", "Model code and libraries ready.", 10)
    return env


def patch_triposr(repo):
    """TripoSR's torchmcubes does not build on Windows: use scikit-image's marching cubes (same surface)."""
    iso = repo / "tsr" / "models" / "isosurface.py"
    src = iso.read_text(encoding="utf-8")
    if "from torchmcubes import marching_cubes" not in src:
        # an earlier patch kept torchmcubes' axis swap, which mirrors scikit-image's output: take it out
        swap = "        v_pos = v_pos[..., [2, 1, 0]]\n"
        if "density = level.detach()" in src and swap in src:
            iso.write_text(src.replace(swap, "", 1), encoding="utf-8")
        return
    src = src.replace("from torchmcubes import marching_cubes", "from skimage.measure import marching_cubes")
    old = """        try:
            v_pos, t_pos_idx = self.mc_func(level.detach(), 0.0)
        except AttributeError:
            print("torchmcubes was not compiled with CUDA support, use CPU version instead.")
            v_pos, t_pos_idx = self.mc_func(level.detach().cpu(), 0.0)
        v_pos = v_pos[..., [2, 1, 0]]
        v_pos = v_pos / (self.resolution - 1.0)
        return v_pos.to(level.device), t_pos_idx.to(level.device)"""
    new = """        density = level.detach().float().cpu().numpy()
        v_pos, t_pos_idx, _, _ = self.mc_func(density, level=0.0)
        v_pos = torch.as_tensor(v_pos.copy(), dtype=torch.float32, device=level.device)
        t_pos_idx = torch.as_tensor(t_pos_idx.copy(), dtype=torch.long, device=level.device)
        v_pos = v_pos / (self.resolution - 1.0)          # scikit-image already returns (i, j, k): no axis swap
        return v_pos, t_pos_idx"""
    if old not in src:
        raise RuntimeError("TripoSR's isosurface code changed upstream: the Windows patch cannot be applied.")
    iso.write_text(src.replace(old, new), encoding="utf-8")


def stream(ctx, cmd, env, cwd, on_line):
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", bufsize=1)
    tail = []
    for line in proc.stdout:
        line = line.rstrip()
        if not line:
            continue
        tail = (tail + [line])[-15:]
        on_line(line)
    rc = proc.wait()
    if rc:
        for t in tail:
            ctx.log("[model] " + t[:400])
        raise RuntimeError("The model stopped with exit code %d: %s" % (rc, tail[-1][:300] if tail else ""))


# ------------------------------------------------------------------------------------------------ TripoSR
def run_triposr(ctx, env, objects, q, out_root, update):
    repo = pathlib.Path(env["ESASIM_REPO"])
    paths = [str(o["views"]["front"]["path"]) for o in objects]
    cmd = [sys.executable, str(repo / "run.py")] + paths + ["--output-dir", str(out_root), "--model-save-format", "glb",
                                                            "--mc-resolution", str(q["mc"]), "--foreground-ratio", "0.85"]
    update("generating", "TripoSR: %d picture%s (background removal, then reconstruction)…" % (len(paths), "s" if len(paths) != 1 else ""), 12)
    t0, state = time.time(), {"n": 0}

    def on_line(line):
        low = line.lower()
        if "exporting mesh" in low or "extracting mesh" in low:
            state["n"] += 1 if "exporting" in low else 0
            update("generating", "TripoSR: %s" % line.split(" - ")[-1][:120], 12 + 76 * state["n"] / max(1, len(paths)))
        elif "error" in low or "traceback" in low:
            ctx.log("[model] " + line[:400])
    stream(ctx, cmd, env, repo, on_line)
    secs = (time.time() - t0) / max(1, len(paths))
    out = []
    for i, o in enumerate(objects):
        f = out_root / str(i) / "mesh.glb"
        if not f.exists():
            raise RuntimeError("TripoSR produced no mesh for %s." % o["name"])
        out.append((o, 0, f, secs))
    return out


# ------------------------------------------------------------------------------------------------ Hunyuan3D-2
HY_RUNNER = r'''
import json, os, sys, time
cfg = json.load(open(sys.argv[1], encoding="utf-8"))
sys.path.insert(0, cfg["repo"])
import torch
from PIL import Image
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline, FloaterRemover, DegenerateFaceRemover, FaceReducer
print("ESASIM loading", cfg["model"], cfg["subfolder"], flush=True)
pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(cfg["model"], subfolder=cfg["subfolder"], use_safetensors=True, device="cuda")
if cfg.get("flashvdm"):
    try:
        pipe.enable_flashvdm()
    except Exception as e:
        print("ESASIM note FlashVDM unavailable:", e, flush=True)
rembg = BackgroundRemover()
def prep(path):
    im = Image.open(path)
    if im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 250:
        return im                                # already cut out
    return rembg(im.convert("RGB"))
for n, job in enumerate(cfg["jobs"]):
    views = {k: prep(v) for k, v in job["views"].items()}
    image = views if cfg["multiview"] else views["front"]
    t0 = time.time()
    mesh = pipe(image=image, num_inference_steps=cfg["steps"], octree_resolution=cfg["octree"], num_chunks=cfg["chunks"],
                generator=torch.manual_seed(job["seed"]), output_type="trimesh")[0]
    mesh = FloaterRemover()(mesh)
    mesh = DegenerateFaceRemover()(mesh)
    mesh = FaceReducer()(mesh, max_facenum=cfg["faces"])
    mesh.export(job["out"])
    print("ESASIM done %d %.1f" % (n, time.time() - t0), flush=True)
    torch.cuda.empty_cache()
'''


def run_hunyuan(ctx, env, spec, objects, q, variants, seed0, out_root, update):
    repo = pathlib.Path(env["ESASIM_REPO"])
    jobs, index = [], []
    for o in objects:
        for v in range(variants):
            out = out_root / ("%s_%d.glb" % (o["safe"], v))
            jobs.append({"views": {k: str(im["path"]) for k, im in o["views"].items()}, "seed": seed0 + v, "out": str(out)})
            index.append((o, v, out))
    vram = __import__("torch").cuda.get_device_properties(0).total_memory / 1e9
    cfg = {"repo": str(repo), "model": spec["repo"], "subfolder": spec["turbo"] if q["turbo"] else spec["sub"], "flashvdm": q["turbo"],
           "multiview": spec["views"] > 1, "steps": q["steps"], "octree": q["octree"], "faces": q["faces"],
           "chunks": 20000 if vram >= 10 else 8000, "jobs": jobs}
    cfg_path = out_root / "hy3d_jobs.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    script = out_root / "hy3d_run.py"
    script.write_text(HY_RUNNER, encoding="utf-8")
    update("loading", "Loading %s (the first time downloads it from Hugging Face, a few GB)…" % spec["repo"], 12)
    times, state = {}, {"done": 0}

    def on_line(line):
        if line.startswith("ESASIM done"):
            _, _, n, secs = line.split()
            times[int(n)] = float(secs)
            state["done"] += 1
            update("generating", "Shape %d of %d done (%.0f s)." % (state["done"], len(jobs), float(secs)), 15 + 75 * state["done"] / len(jobs))
        elif line.startswith("ESASIM"):
            update("loading" if "loading" in line else "generating", line[7:][:160], None)
            if "loading" in line:
                update("generating", "Generating shape 1 of %d…" % len(jobs), 15)
        elif "Traceback" in line or "Error" in line:
            ctx.log("[model] " + line[:400])
    stream(ctx, [sys.executable, str(script), str(cfg_path)], env, repo, on_line)
    return [(o, v, out, times.get(i, 0.0)) for i, (o, v, out) in enumerate(index)]


# ------------------------------------------------------------------------------------------------ preview
def render_preview(mesh, path, size=640):
    """A shaded picture of the mesh from three quarters, drawn with Matplotlib (no OpenGL on a service account)."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    v = np.asarray(mesh.vertices, dtype=float)
    f = np.asarray(mesh.faces)
    if len(f) > 250000:                                              # very dense meshes: simplify the picture only
        try:
            m2 = mesh.simplify_quadric_decimation(face_count=200000)
            v, f = np.asarray(m2.vertices, dtype=float), np.asarray(m2.faces)
            mesh = m2
        except Exception:
            pass
    v = v - (v.min(0) + v.max(0)) / 2
    az, el = np.radians(35), np.radians(20)
    ry = np.array([[np.cos(az), 0, np.sin(az)], [0, 1, 0], [-np.sin(az), 0, np.cos(az)]])
    rx = np.array([[1, 0, 0], [0, np.cos(el), -np.sin(el)], [0, np.sin(el), np.cos(el)]])
    p = v @ ry.T @ rx.T
    tri = p[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    light = np.array([0.35, 0.55, 0.75])
    light /= np.linalg.norm(light)
    shade = 0.28 + 0.72 * np.abs(n @ light)
    base = np.tile([0.70, 0.74, 0.80], (len(f), 1))
    vc = getattr(mesh.visual, "vertex_colors", None) if getattr(mesh.visual, "kind", None) == "vertex" else None
    if vc is not None and len(vc) == len(mesh.vertices):
        base = np.asarray(vc, dtype=float)[f][:, :, :3].mean(1) / 255.0
    col = np.clip(base * shade[:, None], 0, 1)
    order = np.argsort(tri[:, :, 2].mean(1))                        # far to near
    fig = plt.figure(figsize=(size / 100, size / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.add_collection(PolyCollection(tri[order][:, :, :2], facecolors=col[order], edgecolors=col[order], linewidths=0.15))
    span = max(np.ptp(p[:, 0]), np.ptp(p[:, 1])) * 0.56 + 1e-6
    cx, cy = (p[:, 0].min() + p[:, 0].max()) / 2, (p[:, 1].min() + p[:, 1].max()) / 2
    ax.set_xlim(cx - span, cx + span)
    ax.set_ylim(cy - span, cy + span)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#eef2f6")
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
