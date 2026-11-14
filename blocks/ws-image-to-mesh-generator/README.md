# Image to mesh generator

Photos to 3D meshes on an NVIDIA GPU: TripoSR (coloured), Hunyuan3D-2 mini (detailed shape) or Hunyuan3D-2 multi-view (front/left/back/right fused); GLB/OBJ/STL/PLY, shaded previews.

Start it from the Mesh Studio view: it sends the chosen pictures to this run at full quality (up to 1024 px). Or, for a run from the blueprint, give Image links (one per line) or wire pictures to Images and turn on Run without the View. Models: TripoSR (MIT, coloured mesh, seconds), Hunyuan3D-2 mini (detailed shape without colour, about 6 GB of GPU memory), Hunyuan3D-2 multi-view (pictures of one object from the front, left, back and right, named like chair_front.png, fused into one shape). Hunyuan3D-2 is under the Tencent Hunyuan Community licence, which does not cover the EU, the UK or South Korea. The model code is cloned once into the machine's cache and runs with its own library versions.

An [EsaSim](https://esacode.com/) blueprint block: it runs on a machine, in Python (`backend.py`, `def run(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-generator` · version 12 |
| Workspace | Gianluca De Novi's workspace |
| Author | Gianluca De Novi |
| Runs on | NVIDIA GPU |

## Inputs

| Port | Type | Description |
|---|---|---|
| `images` Images (optional) | Files (png, jpg, jpeg, webp) | Pictures for a run started from the blueprint (with Run without the View on) Several connections. Optional. |

## Outputs

| Port | Type | Description |
|---|---|---|
| `glb` Meshes (GLB) | Files (glb) | One GLB per object: for the 3D view and downloads |
| `exports` Other formats | Files (obj, stl, ply) |  |
| `previews` Previews | Files (png) |  |
| `table` Mesh inventory | Table (csv) |  |
| `metadata` Run metadata | Files (json) |  |

## Settings

| Key | Type | Default | Description |
|---|---|---|---|
| `model` Model | select | `"Hunyuan3D-2 mini"` |  |
| `quality` Quality | select | `"balanced"` | TripoSR: surface resolution 192 / 256 / 320. Hunyuan3D-2: turbo 5 steps / 30 steps / 50 steps at a finer octree |
| `candidates` Variations per object (Hunyuan3D-2) | number | `1` |  |
| `seed` Seed | number | `1234` |  |
| `formats` Mesh formats | text | `"glb,obj,stl,ply"` |  |
| `image_urls` Image links | textarea | `""` | One picture link per line, for a run from the blueprint |
| `run_without_view` Run without the View | bool | `false` | On: a blueprint Run generates from Image links / the Images input. Off: only the View's Generate meshes starts generation |
| `launch` Requested by Mesh Studio (View only) | bool | `false` |  |
| `session` Upload session (View only) | text | `""` |  |
| `upload_manifest` Upload manifest (View only) | textarea | `""` |  |

## Use it in EsaSim

In a workspace, open **Projects > Blocks > New block**, choose this kind of block, copy the ports and settings above and paste the code; or ask an AI assistant connected to EsaSim (MCP) to create it from this folder.
