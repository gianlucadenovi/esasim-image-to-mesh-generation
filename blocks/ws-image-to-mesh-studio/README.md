# Image to Mesh Studio

View-first image uploads, model selection, batch generation, progress, mesh preview thumbnails, statistics and export downloads.

Upload one or more images in the View; every file creates its own mesh. Grouped view mode records shared object sources but TripoSR and Stable Fast 3D currently use only the first view for geometry. Click Generate meshes to start a run with temporary image parameters. No inference occurs on ordinary Blueprint Run. Files are browser-resized for transport. GLB/OBJ/STL/PLY files and preview cards are displayed as run results.

An [EsaSim](https://esacode.com/) blueprint block: a view that draws in the browser, in JavaScript (`frontend.js`, `function render(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-studio` · version 1 |
| Workspace | Gianluca De Novi's workspace |
| Author | Gianluca De Novi |

## Inputs

| Port | Type | Description |
|---|---|---|
| `meshes` Mesh results | Files (glb, obj, stl, ply) | Several connections. Optional. |
| `previews` Mesh snapshots | Files (png) | Several connections. Optional. |
| `details` Mesh metadata | Table (csv) | Optional. |
| `status` Live progress | Live telemetry | Optional. |

## Use it in EsaSim

In a workspace, open **Projects > Blocks > New block**, choose this kind of block, copy the ports and settings above and paste the code; or ask an AI assistant connected to EsaSim (MCP) to create it from this folder.
