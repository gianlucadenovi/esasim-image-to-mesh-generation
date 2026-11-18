# Image to mesh generator

Photos to 3D meshes on an NVIDIA GPU: TripoSR (coloured), Hunyuan3D-2 mini (detailed shape) or Hunyuan3D-2 multi-view (front/left/back/right fused); GLB/OBJ/STL/PLY, shaded previews.

Start it from the Mesh Studio view. Generate meshes sends the pictures in the run's own settings (compact, up to 1024 px) or live as messages. Or, for a run from the blueprint, give Image links (one per line) or wire pictures to Images and turn on Run without the View. Models: TripoSR (MIT, coloured mesh, seconds), Hunyuan3D-2 mini (detailed shape without colour, about 6 GB of GPU memory), Hunyuan3D-2 multi-view (pictures of one object from the front, left, back and right fused into one shape). Hunyuan3D-2 is under the Tencent Hunyuan Community licence, which does not cover the EU, the UK or South Korea.

An [EsaSim](https://esacode.com/) blueprint block: it runs on a worker, in Python (`backend.py`, `def run(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-generator` · version 14 |
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
| `run_without_view` Run without the View | bool | `false` | On: a blueprint Run generates from Image links / the Images input. Off: only the View starts generation |
| `launch` Requested by Mesh Studio (View only) | bool | `false` |  |
| `session` Upload session (View only) | text | `""` |  |
| `upload_manifest` Upload manifest (View only) | textarea | `""` |  |
| `compact_count` Compact upload pieces (View only) | number | `0` |  |
| `compact_len` Compact upload length (View only) | number | `0` |  |
| `c00` Compact upload 1 (View only) | textarea | `""` |  |
| `c01` Compact upload 2 (View only) | textarea | `""` |  |
| `c02` Compact upload 3 (View only) | textarea | `""` |  |
| `c03` Compact upload 4 (View only) | textarea | `""` |  |
| `c04` Compact upload 5 (View only) | textarea | `""` |  |
| `c05` Compact upload 6 (View only) | textarea | `""` |  |
| `c06` Compact upload 7 (View only) | textarea | `""` |  |
| `c07` Compact upload 8 (View only) | textarea | `""` |  |
| `c08` Compact upload 9 (View only) | textarea | `""` |  |
| `c09` Compact upload 10 (View only) | textarea | `""` |  |
| `c10` Compact upload 11 (View only) | textarea | `""` |  |
| `c11` Compact upload 12 (View only) | textarea | `""` |  |
| `c12` Compact upload 13 (View only) | textarea | `""` |  |
| `c13` Compact upload 14 (View only) | textarea | `""` |  |
| `c14` Compact upload 15 (View only) | textarea | `""` |  |
| `c15` Compact upload 16 (View only) | textarea | `""` |  |
| `c16` Compact upload 17 (View only) | textarea | `""` |  |
| `c17` Compact upload 18 (View only) | textarea | `""` |  |
| `c18` Compact upload 19 (View only) | textarea | `""` |  |
| `c19` Compact upload 20 (View only) | textarea | `""` |  |
| `c20` Compact upload 21 (View only) | textarea | `""` |  |
| `c21` Compact upload 22 (View only) | textarea | `""` |  |
| `c22` Compact upload 23 (View only) | textarea | `""` |  |
| `c23` Compact upload 24 (View only) | textarea | `""` |  |
| `c24` Compact upload 25 (View only) | textarea | `""` |  |
| `c25` Compact upload 26 (View only) | textarea | `""` |  |
| `c26` Compact upload 27 (View only) | textarea | `""` |  |
| `c27` Compact upload 28 (View only) | textarea | `""` |  |
| `c28` Compact upload 29 (View only) | textarea | `""` |  |
| `c29` Compact upload 30 (View only) | textarea | `""` |  |
| `c30` Compact upload 31 (View only) | textarea | `""` |  |
| `c31` Compact upload 32 (View only) | textarea | `""` |  |
| `c32` Compact upload 33 (View only) | textarea | `""` |  |
| `c33` Compact upload 34 (View only) | textarea | `""` |  |
| `c34` Compact upload 35 (View only) | textarea | `""` |  |
| `c35` Compact upload 36 (View only) | textarea | `""` |  |
| `c36` Compact upload 37 (View only) | textarea | `""` |  |
| `c37` Compact upload 38 (View only) | textarea | `""` |  |
| `c38` Compact upload 39 (View only) | textarea | `""` |  |
| `c39` Compact upload 40 (View only) | textarea | `""` |  |
| `c40` Compact upload 41 (View only) | textarea | `""` |  |
| `c41` Compact upload 42 (View only) | textarea | `""` |  |
| `c42` Compact upload 43 (View only) | textarea | `""` |  |
| `c43` Compact upload 44 (View only) | textarea | `""` |  |
| `c44` Compact upload 45 (View only) | textarea | `""` |  |
| `c45` Compact upload 46 (View only) | textarea | `""` |  |
| `c46` Compact upload 47 (View only) | textarea | `""` |  |
| `c47` Compact upload 48 (View only) | textarea | `""` |  |

## Use it in EsaSim

In a workspace, open **Projects > Blocks > New block**, choose this kind of block, copy the ports and settings above and paste the code; or ask an AI assistant connected to EsaSim (MCP) to create it from this folder.
