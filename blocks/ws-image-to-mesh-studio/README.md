# Image to Mesh Studio

Choose photos and a model, press Generate meshes: several photos of one object become one mesh (multi-view); shaded previews and GLB/OBJ/STL/PLY downloads.

Press Run once to open the studio, then drop pictures and press Generate meshes. Several pictures of one object switch to Hunyuan3D-2 multi-view, which fuses up to four of them (front, left, back, right) into one mesh: check each picture's side; extra pictures are marked "not used". To make a separate mesh from every picture, choose Hunyuan3D-2 mini or TripoSR instead.

An [EsaSim](https://esacode.com/) blueprint block: a view that draws in the browser, in JavaScript (`frontend.js`, `function render(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-studio` · version 12 |
| Workspace | Gianluca De Novi's workspace |
| Author | Gianluca De Novi |

## Inputs

| Port | Type | Description |
|---|---|---|
| `glb` Meshes (GLB) | Files (glb) | Several connections. Optional. |
| `exports` Other formats | Files (obj, stl, ply) | Several connections. Optional. |
| `previews` Previews | Files (png) | Several connections. Optional. |
| `details` Mesh inventory | Table (csv) | Optional. |
| `status` Live progress | Live telemetry | Optional. |

## Use it in EsaSim

In a workspace, open **Projects > Blocks > New block**, choose this kind of block, copy the ports and settings above and paste the code; or ask an AI assistant connected to EsaSim (MCP) to create it from this folder.
