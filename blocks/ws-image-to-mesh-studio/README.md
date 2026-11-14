# Image to Mesh Studio

Choose photos and a model, press Generate meshes: pictures go to the run at full quality; shaded previews and GLB/OBJ/STL/PLY downloads.

Drop pictures, choose TripoSR, Hunyuan3D-2 mini or Hunyuan3D-2 multi-view and a quality, press Generate meshes. Keep the view open until the pictures are sent (a few seconds after the run starts). For multi-view, mark each picture's side (front, left, back, right) and give the pictures of one object the same object name.

An [EsaSim](https://esacode.com/) blueprint block: a view that draws in the browser, in JavaScript (`frontend.js`, `function render(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-studio` · version 4 |
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
