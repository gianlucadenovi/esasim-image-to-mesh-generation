# ── EsaSim block ──────────────────────────────────────────────────────
# Image to mesh generator (ws-image-to-mesh-generator) · version 3 · machine block, Python: def run(ctx)
# Run TripoSR or Stable Fast 3D on user-uploaded source images, batch objects, export GLB/OBJ/STL/PLY, previews and metadata.
# Workspace: Gianluca De Novi's workspace · Author: Gianluca De Novi
# Saved: 2026-11-13
#
# Inputs   ctx.inputs["id"] is a list of files: .path .name .size .read_text() .read_json()
#   (none)
# Outputs  ctx.output("id", "name.ext") is the path to write; ctx.write_json / ctx.write_text
#   meshes      Files (glb, obj, stl, ply) Generated meshes
#   previews    Files (png)               Preview images
#   table       Table (csv)               Mesh inventory
#   metadata    Files (json)              Run metadata
#   telemetry   Live telemetry            ctx.telemetry("channel", data) while it runs
# Settings ctx.params["key"]
#   launch      bool      Requested by Mesh Studio = false
#   images_payload textarea  Uploaded image payload (View-managed) = ""
#   model       select    Model = "TripoSR" of TripoSR | Stable Fast 3D
#   batch_mode  select    Batch mode = "independent" of independent | grouped
#   quality     select    Quality = "balanced" of fast | balanced | high
#   candidates  number    Variations per object = 1
#   formats     text      Mesh formats = "glb,obj,stl,ply"
#   cleanup     bool      Clean geometry = false
#   images_chunk_count number    Upload image chunk count = 0
#   images_checksum text      Upload integrity digest = ""
#   img_chunk_000 textarea  Upload chunk 1 = ""
#   img_chunk_001 textarea  Upload chunk 2 = ""
#   img_chunk_002 textarea  Upload chunk 3 = ""
#   img_chunk_003 textarea  Upload chunk 4 = ""
#   img_chunk_004 textarea  Upload chunk 5 = ""
#   img_chunk_005 textarea  Upload chunk 6 = ""
#   img_chunk_006 textarea  Upload chunk 7 = ""
#   img_chunk_007 textarea  Upload chunk 8 = ""
#   img_chunk_008 textarea  Upload chunk 9 = ""
#   img_chunk_009 textarea  Upload chunk 10 = ""
#   img_chunk_010 textarea  Upload chunk 11 = ""
#   img_chunk_011 textarea  Upload chunk 12 = ""
#   img_chunk_012 textarea  Upload chunk 13 = ""
#   img_chunk_013 textarea  Upload chunk 14 = ""
#   img_chunk_014 textarea  Upload chunk 15 = ""
#   img_chunk_015 textarea  Upload chunk 16 = ""
#   img_chunk_016 textarea  Upload chunk 17 = ""
#   img_chunk_017 textarea  Upload chunk 18 = ""
#   img_chunk_018 textarea  Upload chunk 19 = ""
#   img_chunk_019 textarea  Upload chunk 20 = ""
#   img_chunk_020 textarea  Upload chunk 21 = ""
#   img_chunk_021 textarea  Upload chunk 22 = ""
#   img_chunk_022 textarea  Upload chunk 23 = ""
#   img_chunk_023 textarea  Upload chunk 24 = ""
#   img_chunk_024 textarea  Upload chunk 25 = ""
#   img_chunk_025 textarea  Upload chunk 26 = ""
#   img_chunk_026 textarea  Upload chunk 27 = ""
#   img_chunk_027 textarea  Upload chunk 28 = ""
#   img_chunk_028 textarea  Upload chunk 29 = ""
#   img_chunk_029 textarea  Upload chunk 30 = ""
#   img_chunk_030 textarea  Upload chunk 31 = ""
#   img_chunk_031 textarea  Upload chunk 32 = ""
#   img_chunk_032 textarea  Upload chunk 33 = ""
#   img_chunk_033 textarea  Upload chunk 34 = ""
#   img_chunk_034 textarea  Upload chunk 35 = ""
#   img_chunk_035 textarea  Upload chunk 36 = ""
#   img_chunk_036 textarea  Upload chunk 37 = ""
#   img_chunk_037 textarea  Upload chunk 38 = ""
#   img_chunk_038 textarea  Upload chunk 39 = ""
#   img_chunk_039 textarea  Upload chunk 40 = ""
#   img_chunk_040 textarea  Upload chunk 41 = ""
#   img_chunk_041 textarea  Upload chunk 42 = ""
#   img_chunk_042 textarea  Upload chunk 43 = ""
#   img_chunk_043 textarea  Upload chunk 44 = ""
#   img_chunk_044 textarea  Upload chunk 45 = ""
#   img_chunk_045 textarea  Upload chunk 46 = ""
#   img_chunk_046 textarea  Upload chunk 47 = ""
#   img_chunk_047 textarea  Upload chunk 48 = ""
# Runs on  NVIDIA GPU. Return a dict to fill the "result" output.
# Packages numpy, Pillow, trimesh, matplotlib, torch (installed by the worker with pip when missing)
# EsaSim rewrites these lines from the block's definition each time it is saved: change the definition, not them.
# ── end of EsaSim block header ────────────────────────────────────────

import os, io, re, json, csv, time, base64, subprocess, sys, pathlib, shutil, traceback, threading

def run(ctx):
    p = ctx.params
    hb_state = {"stage":"preparing","message":"Preparing mesh workflow","percent":1}
    hb_stop = threading.Event()
    def heartbeat():
        while not hb_stop.wait(20):
            try:
                s = dict(hb_state)
                ctx.log("[heartbeat] Worker alive; " + s["message"])
                ctx.progress(int(s["percent"]), s["message"] + " (worker alive)")
                ctx.telemetry("mesh_status", {"stage":s["stage"],"message":s["message"]+" — still working","percent":s["percent"],"heartbeat":True})
            except Exception as exc:
                print("[heartbeat] Could not report: %s" % exc, flush=True)
    def update(stage, msg, pct, **extra):
        hb_state.update(stage=stage,message=msg,percent=int(pct))
        ctx.log("[mesh] " + msg)
        ctx.progress(max(0,min(100,int(pct))), msg)
        ctx.telemetry("mesh_status", dict(stage=stage, message=msg, percent=int(pct), **extra))
    if not p.get("launch", False):
        update("idle", "Mesh Studio ready. Choose images in View and click Generate meshes.", 100)
        return {"result":{"status":"idle"}}
    threading.Thread(target=heartbeat,daemon=True).start()
    import numpy as np
    from PIL import Image
    import trimesh
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n_chunks = int(p.get("images_chunk_count", 0) or 0)
    if n_chunks:
        if not 1 <= n_chunks <= 48:
            raise ValueError("Too many image upload chunks: split the batch.")
        chunks = [str(p.get("img_chunk_%03d" % i, "") or "") for i in range(n_chunks)]
        if any(not x or len(x)>1050 for x in chunks):
            raise ValueError("Image transfer chunk missing or truncated. The run parameter API cannot reliably transport this upload.")
        payload = "".join(chunks)
        if len(payload)>49152:
            raise ValueError("Image payload exceeds this View API's safe 48 KiB limit.")
        checksum = str(p.get("images_checksum", ""))
        import hashlib
        if checksum and hashlib.sha256(payload.encode("utf-8")).hexdigest()!=checksum:
            raise ValueError("Image transfer checksum mismatch: refusing to reconstruct with corrupted source.")
    else:
        payload = str(p.get("images_payload") or "")
        if len(payload)>49152:
            raise ValueError("Legacy upload too large. Reopen the updated Mesh Studio.")
    try:
        items = json.loads(payload)
    except Exception as e:
        raise ValueError("The image upload was incomplete. Try a smaller image; native file uploads are not yet supported by this EsaSim View API.") from e
    if not isinstance(items,list) or not items or len(items)>24:
        raise ValueError("Upload between 1 and 24 pictures for a run.")
    quality = str(p.get("quality","balanced"))
    model = str(p.get("model","TripoSR"))
    batch = str(p.get("batch_mode","independent"))
    if model not in ("TripoSR","Stable Fast 3D"):
        raise ValueError("Executable backends in this version: TripoSR and Stable Fast 3D.")
    if batch not in ("independent","grouped"):
        raise ValueError("Invalid batch mode.")
    if batch == "grouped" and model not in ("TripoSR","Stable Fast 3D"):
        raise ValueError("Unsupported model for grouped input.")
    update("preparing","Reading %d uploaded pictures…" % len(items), 2)
    work = pathlib.Path(ctx.folder)/"mesh_studio"
    work.mkdir(parents=True,exist_ok=True)
    groups={}
    for i,entry in enumerate(items):
        if not isinstance(entry,dict): raise ValueError("Invalid image entry")
        name = re.sub(r"[^a-zA-Z0-9._-]","_",str(entry.get("name","image_%d"%i)))[:100]
        raw = str(entry.get("data",""))
        if "," in raw: raw = raw.split(",",1)[1]
        blob=base64.b64decode(raw,validate=True)
        if len(blob)>2500000: raise ValueError("One image exceeds 2.5 MB")
        im=Image.open(io.BytesIO(blob))
        im.load()
        if im.width*im.height>3000000: raise ValueError("Image too large")
        im=im.convert("RGB")
        path=work/("source_%03d.jpg"%i)
        im.save(path,quality=91)
        stem=re.sub(r"_(front|back|left|right|side|top|bottom|view[0-9]+)$","",pathlib.Path(name).stem,flags=re.I)
        group=str(entry.get("group") or stem or ("object_%03d"%i))
        key=("object_%03d"%i) if batch=="independent" else group
        groups.setdefault(key,[]).append(dict(name=name,path=path))
    if len(groups)>24: raise ValueError("Too many objects")
    # Grouped views are retained as evidence; current backends use the first photograph.
    if batch=="grouped":
        update("notice","Grouped source views stored, but this model generates from the first view only. True multiview fusion is not claimed.",3)
    cache=pathlib.Path(os.environ.get("ESASIM_MESH_REPOS",str(pathlib.Path.home()/".cache"/"esasim-mesh")))
    cache.mkdir(parents=True,exist_ok=True)
    repo_name="TripoSR" if model=="TripoSR" else "stable-fast-3d"
    origin="https://github.com/VAST-AI-Research/TripoSR.git" if model=="TripoSR" else "https://github.com/Stability-AI/stable-fast-3d.git"
    repo=cache/repo_name
    if not (repo/"run.py").exists():
        update("installing","Downloading " + model + " source repository…",5)
        subprocess.run(["git","clone","--depth","1",origin,str(repo)],check=True,timeout=180)
    if not (repo/"run.py").exists(): raise RuntimeError("Model runner missing: "+str(repo/"run.py"))
    # Installation on workers can require CUDA/toolchain and access to gated weights.
    if not (repo/".esasim_requirements_ready").exists():
        update("installing","Installing " + model + " dependencies; CUDA toolchain may be needed…",7)
        requirements=repo/"requirements.txt"
        if requirements.exists():
            subprocess.run([sys.executable,"-m","pip","install","-r",str(requirements)],cwd=str(repo),check=True,timeout=1800)
        (repo/".esasim_requirements_ready").write_text("ok")
    variants=max(1,min(4,int(p.get("candidates",1))))
    do_cleanup=bool(p.get("cleanup",False))
    formats=[x.strip().lower() for x in str(p.get("formats","glb,obj,stl,ply")).split(",") if x.strip().lower() in ("glb","obj","stl","ply")]
    if not formats: formats=["glb"]
    rows=[]; records=[]; total=len(groups)*variants; finished=0
    for key,sources in groups.items():
        for v in range(variants):
            idx=finished+1
            safe=re.sub(r"[^a-zA-Z0-9_-]","_",key)[:50]+"_%02d"%(v+1)
            outdir=work/safe
            outdir.mkdir(parents=True,exist_ok=True)
            source=sources[0]["path"]
            update("generating","Generating mesh %d/%d — %s with %s" %(idx,total,key,model),10+int(70*finished/total),object=key,completed=finished,total=total)
            t0=time.monotonic()
            cmd=[sys.executable,str(repo/"run.py"),str(source),"--output-dir",str(outdir)]
            if model=="TripoSR":
                cmd+=["--model-save-format","glb","--mc-resolution",str({"fast":128,"balanced":192,"high":256}.get(quality,192))]
            else:
                cmd+=["--texture-resolution",str({"fast":512,"balanced":1024,"high":2048}.get(quality,1024))]
            env=dict(os.environ)
            proc=subprocess.Popen(cmd,cwd=str(repo),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace",env=env)
            tail=[]
            for line in proc.stdout:
                line=line.rstrip()
                if line:
                    tail.append(line)
                    if len(tail)>12: tail.pop(0)
                    if ("error" in line.lower() or "loading" in line.lower()):
                        ctx.log("[model] " + line[:450])
            rc=proc.wait()
            if rc!=0:
                raise RuntimeError("%s failed for %s (exit %d). Last output: %s" %(model,key,rc," | ".join(tail[-5:])))
            found=list(outdir.rglob("mesh.glb"))+list(outdir.rglob("mesh.obj"))
            if not found: raise RuntimeError("Model finished but no mesh was produced for "+key)
            asset=trimesh.load(str(found[0]),force="scene",process=False)
            mesh=trimesh.util.concatenate([g for g in asset.geometry.values() if isinstance(g,trimesh.Trimesh)])
            if do_cleanup:
                mesh.remove_unreferenced_vertices()
                mesh.merge_vertices()
                mesh.fix_normals()
            files=[]
            for fmt in formats:
                filename=safe+"."+fmt
                target=ctx.output("meshes",filename)
                if fmt=="glb" and not do_cleanup and found[0].suffix.lower()==".glb":
                    shutil.copyfile(found[0],target)
                else:
                    mesh.export(target,file_type=fmt)
                files.append(filename)
            # Lightweight preview raster without OpenGL.
            imgpath=ctx.output("previews",safe+"_preview.png")
            fig=plt.figure(figsize=(5,4),dpi=120)
            ax=fig.add_subplot(111,projection="3d")
            xyz=mesh.vertices
            faces=mesh.faces
            if len(faces)>9000: faces=faces[np.linspace(0,len(faces)-1,9000).astype(int)]
            tris=xyz[faces]
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            poly=Poly3DCollection(tris,alpha=1,linewidth=0.08,edgecolor="#202937")
            poly.set_facecolor("#84afcc")
            ax.add_collection3d(poly)
            lo=xyz.min(axis=0); hi=xyz.max(axis=0); mid=(lo+hi)/2; extent=max(1e-4,float(np.max(hi-lo)))*.63
            ax.set(xlim=(mid[0]-extent,mid[0]+extent),ylim=(mid[1]-extent,mid[1]+extent),zlim=(mid[2]-extent,mid[2]+extent))
            ax.view_init(elev=24,azim=43)
            ax.set_axis_off()
            fig.tight_layout(pad=0)
            fig.savefig(imgpath,transparent=False,facecolor="#eaf0f5")
            plt.close(fig)
            elapsed=round(time.monotonic()-t0,2)
            row=dict(object=key,variation=v+1,model=model,source_views=len(sources),primary_image=sources[0]["name"],vertices=len(mesh.vertices),faces=len(mesh.faces),watertight=bool(mesh.is_watertight),duration_s=elapsed,formats=";".join(files),preview=safe+"_preview.png")
            rows.append(row)
            records.append(dict(row,source_images=[x["name"] for x in sources],warning=("Only first view used; no multi-view fusion" if len(sources)>1 else None)))
            finished+=1
            update("completed","Finished %s — %d vertices, %d faces" %(safe,len(mesh.vertices),len(mesh.faces)),10+int(80*finished/total),object=key,completed=finished,total=total)
    path=ctx.output("table","models.csv")
    with open(path,"w",newline="",encoding="utf-8") as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    ctx.write_json("metadata","generation.json",dict(model=model,quality=quality,batch_mode=batch,objects=len(groups),variations=variants,outputs=records,multiview_fusion=False))
    hb_stop.set()
    update("done","Finished generating %d mesh assets. Review previews and download formats below."%len(rows),100,completed=len(rows),total=len(rows))
    return {"result":{"generated":len(rows),"objects":len(groups)}}
