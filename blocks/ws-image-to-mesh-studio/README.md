# Image to Mesh Studio

Choose photos and a model, press Generate meshes: pictures travel in the run's own settings; shaded previews and GLB/OBJ/STL/PLY downloads.

Press Run once to open the studio, then drop pictures, choose TripoSR, Hunyuan3D-2 mini or Hunyuan3D-2 multi-view and a quality, and press Generate meshes. The pictures go with the run itself. For one object seen from several sides choose Hunyuan3D-2 multi-view, mark each picture's side (front, left, back, right) and give them the same object name.

An [EsaSim](https://esacode.com/) blueprint block: a view that draws in the browser, in JavaScript (`frontend.js`, `function render(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-studio` · version 11 |
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
