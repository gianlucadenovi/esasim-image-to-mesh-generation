# Image to Mesh Generation

**Photos in, 3D meshes out.** Drop pictures into the Mesh Studio, choose a model, press **Generate meshes**: each object comes back as a mesh you can turn in the 3D view, with a shaded preview and download buttons for GLB, OBJ, STL and PLY. Everything runs on your own machine's NVIDIA GPU.

## How to use it

1. Open [**1 · Image to mesh studio**](https://esacode.com/app/projects/18/flows/59) and switch to **View**.
2. **Pictures**: drop or choose PNG, JPEG or WebP images. One object per photo, centred, filling most of the frame; a plain background helps (the background is removed automatically; a PNG already cut out keeps its transparency).
3. **Model** and **Quality** (below), then **Generate meshes**.
4. Keep the View open for the first seconds: once the run starts on the GPU machine, the View sends it the pictures at full quality (up to 1024 px), piece by piece, and resends anything missing.
5. The meshes appear in **3 · Meshes** with their preview and **↓ GLB / OBJ / STL / PLY** buttons, in the **3D view** and in the details table.

A normal Blueprint **Run** does not generate anything (the generator just reports it is ready) unless you turn on *Run without the View* and give it *Image links* or wire pictures to its *Images* input, for batch work without the View.

## The models

| Model | Input | Output | Speed on an RTX 3070 | Licence |
|---|---|---|---|---|
| **Hunyuan3D-2 mini** (default, Tencent, 0.6B) | one photo | detailed shape, **no colour** | ~2 min per object (balanced) | Tencent Hunyuan Community — not for use in the EU, the UK or South Korea |
| **TripoSR** (VAST AI) | one photo | softer shape **with vertex colours** | a few seconds per object | MIT |
| **Hunyuan3D-2 multi-view** (Tencent, 1.1B) | 2–4 photos of the same object: front, left, back, right | one shape fused from all views, no colour | ~2–3 min per object | as Hunyuan3D-2 mini |

**Multi-view**: each picture gets a *side* (front, left, back, right) and an *object* name in the Studio. Pictures with the same object name are fused into one mesh; every object needs a front view. Names like `chair_front.png`, `chair_left.png` are recognised automatically.

**Quality**: *Fast* (Hunyuan turbo, 5 steps; TripoSR surface resolution 192), *Balanced* (30 steps; 256), *High* (50 steps on a finer grid; 320). *Variations per object* makes extra Hunyuan3D-2 shapes from different seeds.

## What you get

- `glb/<object>.glb` — the mesh, standing on the ground (y = 0), facing +Z, Y up (glTF convention).
- `exports/<object>.obj|.stl|.ply` — the same mesh in other formats.
- `previews/<object>_preview.png` — a shaded three-quarter view.
- `table/models.csv` — vertices, faces, watertightness, colour, time per object.
- `metadata/generation.json` — model, settings, seed, GPU, licences.

These are visual meshes, not measured CAD: scale is arbitrary (about one unit tall), and they may not be watertight or manifold. Check them before 3D printing or simulation.

## Where it runs

An NVIDIA GPU with at least 6 GB of memory (the generator only goes to such machines). The first run on a machine downloads the model code (Git), its libraries (a few minutes, into the worker's cache) and the weights from Hugging Face (TripoSR ~1.7 GB, Hunyuan3D-2 mini ~2 GB, multi-view ~4 GB); later runs reuse them. The model code runs with the library versions it was written for (Transformers 4.45), isolated from the rest of the worker.

## Changes in this version

- Pictures now reach the model at full quality. The first version squeezed every batch into 48 KB of run settings (384 px, low JPEG quality).
- Hunyuan3D-2 mini and multi-view added; "grouped views" now really fuses the views.
- Stable Fast 3D removed: on Windows it needs C++/CUDA extensions compiled from source and a gated Hugging Face licence, and its installation could not complete.
- TripoSR meshes were mirrored (a coordinate swap left over from the Windows marching-cubes patch) and lying on their side; both fixed.
- Real shaded previews instead of wireframes; working download buttons.

<!-- esasim: files of the project -->

---

An [EsaSim](https://esacode.com/) project of the workspace Gianluca De Novi's workspace (generative-ai).

### Blueprints in this repository

- [1 · Image to mesh studio](blueprints/1-image-to-mesh-studio.json) · 4 blocks · version 15

### Workspace blocks it uses

- [Image to mesh generator](blocks/ws-image-to-mesh-generator) · version 13
- [Image to Mesh Studio](blocks/ws-image-to-mesh-studio) · version 5

Keys pasted in blocks (secret settings) are not saved here. Datasets, results and the team stay in EsaSim.
