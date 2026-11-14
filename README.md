<div align="center">

# Image to Mesh Generation

**From photographs to 3D assets, directly in the EsaSim View. Upload an image or a batch, choose a reconstruction model, generate meshes, inspect them in 3D, and export files ready for downstream workflows.**

A View-first 3D reconstruction workspace for producing GLB, OBJ, STL and PLY assets from photographs with locally executed, open-weight models. The interface combines a drag-and-drop uploader, selectable inference engine, batch processing, live progress, a mesh gallery, an interactive 3D viewer, and traceable generation metadata.

![type](https://img.shields.io/badge/type-Generative%203D-blue) ![language](https://img.shields.io/badge/language-Python-3776AB) ![compute](https://img.shields.io/badge/compute-NVIDIA%20CUDA-76b900) ![formats](https://img.shields.io/badge/formats-GLB%20%7C%20OBJ%20%7C%20STL%20%7C%20PLY-178c8c) ![source](https://img.shields.io/badge/models-Open%20weights-yellow) [![built with](https://img.shields.io/badge/built%20with-EsaSim-0b7285)](https://esacode.com/)

</div>

## Overview

A single photograph shows just one side of an object. An image-to-3D model predicts geometry beyond the visible surface, creates a mesh and optionally reconstructs surface appearance. The result is not a measured CAD model, but it is useful for concept design, visualization, game assets, robotics scenes, digital twins and early-stage simulation pipelines.

**Image upload → Model selection → Generate meshes → 3D preview → Mesh inspection and export.**

To submit work, open [**1 · Image to mesh studio**](https://esacode.com/app/projects/18/flows/59) and switch to **View**. Upload files and click **Generate meshes**. A regular Blueprint **Run** does not launch reconstruction.

## The flow

| Block | Purpose |
|---|---|
| **Image to Mesh Studio** | Drag-and-drop source images, choose a model, select batch behavior, start inference and browse results. |
| **Image to mesh generator** | Download the appropriate model when necessary, infer geometry on an NVIDIA GPU, export mesh formats and record statistics. |
| **Interactive 3D mesh viewer** | Inspect generated 3D assets, orbit and zoom around them, and switch between models. |
| **Batch mesh details** | Compare object names, source counts, vertices, faces, watertightness and generation times. |

## Supported models — first release

| Model | Main strength | Input | Output | License / access |
|---|---|---|---|---|
| **[TripoSR](https://github.com/VAST-AI-Research/TripoSR)** | Lightweight single-image geometry reconstruction | One reference photo per generated mesh | GLB mesh with vertex color; converted OBJ/STL/PLY | MIT code license; verify model-weight terms |
| **[Stable Fast 3D](https://github.com/Stability-AI/stable-fast-3d)** | Fast reconstruction with textured materials | One reference photo per generated mesh | Textured GLB; converted OBJ/STL/PLY | Stability AI Community License; model access terms may apply |

The selectable backends above are **implemented as model runners**, not verified successful inference runs. Other models, such as TRELLIS.2 or Hunyuan3D multi-view, require dedicated integrations and are not currently available in this flow.

**Performance:** Both current backends are designed around a CUDA-capable NVIDIA GPU. Available VRAM, model weights, environment dependencies and the selected output quality determine whether a run can complete. A separate GPU with more VRAM may be needed for larger future backends.

## Input modes and batch generation

### Independent images — default

Add multiple JPG, PNG or WebP images. Each photograph becomes its own object and is passed to the selected model. The batch runner creates an individual result set for each object.

### Grouped views — experimental organization

Files with a shared prefix can be grouped, for example `chair_front.jpg`, `chair_side.jpg`, `chair_back.jpg`. The generator records all source filenames for the object, **but the current TripoSR and Stable Fast 3D runners only reconstruct the first image of each group**. Grouping does **not** fuse views or increase geometric accuracy yet. For true multi-view reconstruction a model such as Hunyuan3D-2mv must be integrated separately.

**Current upload limitation:** The EsaSim View-run API currently accepts settings but does not expose a native binary-file upload action. To avoid the truncated JSON error seen in the first test, Mesh Studio now compresses images to a maximum of 384 pixels on their longest side, divides a compact upload into individually bounded chunks, and verifies the payload checksum on the worker when available. This compatibility path has a conservative total payload budget of about **48 KB across the whole batch**. For larger or high-resolution photographs, proper native file staging is required; do not expect this compact mode to preserve source fidelity.

**Preserving the View:** Selected image previews, settings, and historical result cards are saved in the View's state and restored after starting a new run. Historical mesh download links may expire and should be retrieved from the original run's **Results** for reliable access. The rendering frame itself still remounts on a new run; this update restores its data rather than preventing the remount.

## Workflow

1. Check **Compute** and make sure an eligible NVIDIA machine is available.
2. Open [**Image to mesh studio**](https://esacode.com/app/projects/18/flows/59), then the **View**.
3. Drop images into the uploader or select them from your computer.
4. Choose **TripoSR** for geometry or **Stable Fast 3D** for textured assets.
5. Select **Fast**, **Balanced** or **High** resolution and independent or grouped input.
6. Click **Generate meshes**. The current run's parameters are submitted directly from the View. No Blueprint edits are required.
7. Watch the live progress panel and its waiting indicator. Once complete, inspect the snapshots, open the interactive 3D viewer and download the generated files.

## Results and export

For each object the generator aims to produce:

- **GLB** — efficient 3D exchange, including supported materials.
- **OBJ** — widely used mesh geometry format; texture/material handling depends on conversion.
- **STL** — geometry for printing and geometric workflows, no colors or textures.
- **PLY** — geometry and potentially vertex properties, depending on exporter.
- **Preview PNG** — a lightweight rendered mesh snapshot.
- **Mesh statistics** — object, model, source image, vertices, triangles, watertightness, elapsed time.
- **`models.csv`** — tabular inventory for the entire batch.
- **`generation.json`** — generation settings, object grouping and source-image manifest.

Mesh exports are **not equivalent to parametric CAD** and should not be assumed watertight, scaled correctly, manifold or mechanically accurate. Validate geometry before simulation, FEA or manufacturing.

## Live progress and reliable long runs

A **20-second independent heartbeat** reports the current stage while dependency installation, model download, inference and export run. The View shows a waiting animation, last reported stage, real progress percentage and recent events.

Heartbeat messages mean that the worker's reporting thread is responsive; they do **not** mean that the model has made additional progress. EsaSim's runner also needs to process those messages during long tasks to avoid false disconnection.

## Setup and caveats

- First use requires Git and network access to clone the selected repository and download weights.
- Python package provisioning may need CUDA, suitable PyTorch wheels, and model-specific native dependencies.
- Stable Fast 3D may require Hugging Face authentication or access acceptance depending on its model repository.
- Existing model CLI code is run in a subprocess, and output generation can take substantially longer on constrained GPUs.
- A proper runtime validation with generated files is still outstanding.
- Verify licenses of model code, downloaded model weights and generated assets before commercial use.

## Next steps

Further model adapters can add **true multi-view fusion**, advanced textured formats, better scaling, geometry cleanup and higher-fidelity reconstruction. Those capabilities should be implemented and tested as separate backends rather than silently promised by the first release.

---

<sub>Image to Mesh Generation · EsaSim workspace · Version 1</sub>

<!-- esasim: files of the project -->

---

An [EsaSim](https://esacode.com/) project of the workspace Gianluca De Novi's workspace (generative-ai).

### Blueprints in this repository

- [1 · Image to mesh studio](blueprints/1-image-to-mesh-studio.json) · 4 blocks · version 10

### Workspace blocks it uses

- [Image to mesh generator](blocks/ws-image-to-mesh-generator) · version 11
- [Image to Mesh Studio](blocks/ws-image-to-mesh-studio) · version 3

Keys pasted in blocks (secret settings) are not saved here. Datasets, results and the team stay in EsaSim.
