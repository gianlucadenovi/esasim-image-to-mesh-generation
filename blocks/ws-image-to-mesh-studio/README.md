# Image to Mesh Studio

View-first image uploads, model selection, batch generation, progress, mesh preview thumbnails, statistics and export downloads.

Compact compressed image uploads via chunked per-run settings, with integrity checksum. Saves selected images and result cards in View state so they reappear across runs. Current View API lacks native file upload and old-run file handles; previous download URLs can expire.

An [EsaSim](https://esacode.com/) blueprint block: a view that draws in the browser, in JavaScript (`frontend.js`, `function render(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-studio` · version 2 |
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
