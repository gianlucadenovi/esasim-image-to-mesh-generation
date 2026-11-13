# Image to mesh generator

Run TripoSR or Stable Fast 3D on user-uploaded source images, batch objects, export GLB/OBJ/STL/PLY, previews and metadata.

Stable Fast 3D on Windows uses gpytoolbox 0.3.3 prebuilt CPython 3.12 wheel (upstream compatibility PR). Installs with --prefix, not --target, so pip can reuse worker's CUDA torch. Validates critical module imports before marking cache ready. Native extension build remains under no-build-isolation with short TMP/TEMP.

An [EsaSim](https://esacode.com/) blueprint block: it runs on a machine, in Python (`backend.py`, `def run(ctx)`).

| | |
|---|---|
| Block | `ws-image-to-mesh-generator` · version 10 |
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
| `images_chunk_count` Upload image chunk count | number | `0` |  |
| `images_checksum` Upload integrity digest | text | `""` |  |
| `img_chunk_000` Upload chunk 1 | textarea | `""` |  |
| `img_chunk_001` Upload chunk 2 | textarea | `""` |  |
| `img_chunk_002` Upload chunk 3 | textarea | `""` |  |
| `img_chunk_003` Upload chunk 4 | textarea | `""` |  |
| `img_chunk_004` Upload chunk 5 | textarea | `""` |  |
| `img_chunk_005` Upload chunk 6 | textarea | `""` |  |
| `img_chunk_006` Upload chunk 7 | textarea | `""` |  |
| `img_chunk_007` Upload chunk 8 | textarea | `""` |  |
| `img_chunk_008` Upload chunk 9 | textarea | `""` |  |
| `img_chunk_009` Upload chunk 10 | textarea | `""` |  |
| `img_chunk_010` Upload chunk 11 | textarea | `""` |  |
| `img_chunk_011` Upload chunk 12 | textarea | `""` |  |
| `img_chunk_012` Upload chunk 13 | textarea | `""` |  |
| `img_chunk_013` Upload chunk 14 | textarea | `""` |  |
| `img_chunk_014` Upload chunk 15 | textarea | `""` |  |
| `img_chunk_015` Upload chunk 16 | textarea | `""` |  |
| `img_chunk_016` Upload chunk 17 | textarea | `""` |  |
| `img_chunk_017` Upload chunk 18 | textarea | `""` |  |
| `img_chunk_018` Upload chunk 19 | textarea | `""` |  |
| `img_chunk_019` Upload chunk 20 | textarea | `""` |  |
| `img_chunk_020` Upload chunk 21 | textarea | `""` |  |
| `img_chunk_021` Upload chunk 22 | textarea | `""` |  |
| `img_chunk_022` Upload chunk 23 | textarea | `""` |  |
| `img_chunk_023` Upload chunk 24 | textarea | `""` |  |
| `img_chunk_024` Upload chunk 25 | textarea | `""` |  |
| `img_chunk_025` Upload chunk 26 | textarea | `""` |  |
| `img_chunk_026` Upload chunk 27 | textarea | `""` |  |
| `img_chunk_027` Upload chunk 28 | textarea | `""` |  |
| `img_chunk_028` Upload chunk 29 | textarea | `""` |  |
| `img_chunk_029` Upload chunk 30 | textarea | `""` |  |
| `img_chunk_030` Upload chunk 31 | textarea | `""` |  |
| `img_chunk_031` Upload chunk 32 | textarea | `""` |  |
| `img_chunk_032` Upload chunk 33 | textarea | `""` |  |
| `img_chunk_033` Upload chunk 34 | textarea | `""` |  |
| `img_chunk_034` Upload chunk 35 | textarea | `""` |  |
| `img_chunk_035` Upload chunk 36 | textarea | `""` |  |
| `img_chunk_036` Upload chunk 37 | textarea | `""` |  |
| `img_chunk_037` Upload chunk 38 | textarea | `""` |  |
| `img_chunk_038` Upload chunk 39 | textarea | `""` |  |
| `img_chunk_039` Upload chunk 40 | textarea | `""` |  |
| `img_chunk_040` Upload chunk 41 | textarea | `""` |  |
| `img_chunk_041` Upload chunk 42 | textarea | `""` |  |
| `img_chunk_042` Upload chunk 43 | textarea | `""` |  |
| `img_chunk_043` Upload chunk 44 | textarea | `""` |  |
| `img_chunk_044` Upload chunk 45 | textarea | `""` |  |
| `img_chunk_045` Upload chunk 46 | textarea | `""` |  |
| `img_chunk_046` Upload chunk 47 | textarea | `""` |  |
| `img_chunk_047` Upload chunk 48 | textarea | `""` |  |
| `token` Hugging Face access token (Stable Fast 3D) | secret | (secret) | A Hugging Face read token authorized for stabilityai/stable-fast-3d. Accept the repository license first. Only stored as EsaSim secret; do not paste into View. |

## Use it in EsaSim

In a workspace, open **Projects > Blocks > New block**, choose this kind of block, copy the ports and settings above and paste the code; or ask an AI assistant connected to EsaSim (MCP) to create it from this folder.
