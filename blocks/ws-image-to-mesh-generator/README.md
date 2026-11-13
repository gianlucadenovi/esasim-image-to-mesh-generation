# Image to mesh generator

Run TripoSR or Stable Fast 3D on user-uploaded source images, batch objects, export GLB/OBJ/STL/PLY, previews and metadata.

The Mesh Studio View passes compressed image payloads and launch=true to start this block. A normal blueprint run remains idle. TripoSR and Stable Fast 3D require compatible NVIDIA/CUDA runtime and dependencies; gated models may require a Hugging Face token. Grouped images are recorded but these two backends use only the first view, not multiview reconstruction.

An [EsaSim](https://esacode.com/) blueprint block: it runs on a machine, in Python (`backend.py`, `def run(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-generator` · version 2 |
| Workspace | Gianluca De Novi's workspace |
| Author | Gianluca De Novi |
| Runs on | NVIDIA GPU |

## Outputs

| Port | Type | Description |
|---|---|---|
| `meshes` Generated meshes | Files (glb, obj, stl, ply) |  |
| `previews` Preview images | Files (png) |  |
| `table` Mesh inventory | Table (csv) |  |
| `metadata` Run metadata | Files (json) |  |

## Settings

| Key | Type | Default | Description |
|---|---|---|---|
| `launch` Requested by Mesh Studio | bool | `false` |  |
| `images_payload` Uploaded image payload (View-managed) | textarea | `""` |  |
| `model` Model | select | `"TripoSR"` |  |
| `batch_mode` Batch mode | select | `"independent"` |  |
| `quality` Quality | select | `"balanced"` |  |
| `candidates` Variations per object | number | `1` |  |
| `formats` Mesh formats | text | `"glb,obj,stl,ply"` |  |
| `cleanup` Clean geometry | bool | `false` |  |

## Use it in EsaSim

In a workspace, open **Projects > Blocks > New block**, choose this kind of block, copy the ports and settings above and paste the code; or ask an AI assistant connected to EsaSim (MCP) to create it from this folder.
