// ── EsaSim block ──────────────────────────────────────────────────────
// Image to Mesh Studio (ws-image-to-mesh-studio) · version 2 · view, JavaScript: function render(ctx)
// View-first image uploads, model selection, batch generation, progress, mesh preview thumbnails, statistics and export downloads.
// Workspace: Gianluca De Novi's workspace · Author: Gianluca De Novi
// Saved: 2026-11-13
//
// Inputs   ctx.input("id") gives { files, stream }; ctx.rows("id"), ctx.json("id"), ctx.text("id")
//   meshes      Files (glb, obj, stl, ply) Mesh results · several · optional
//   previews    Files (png)               Mesh snapshots · several · optional
//   details     Table (csv)               Mesh metadata · optional
//   status      Live telemetry            Live progress · optional
// Settings ctx.params.key
//   (none)
// EsaSim rewrites these lines from the block's definition each time it is saved: change the definition, not them.
// ── end of EsaSim block header ────────────────────────────────────────

function render(ctx) {
 const root=ctx.el;
 let saved=ctx.state||{}, settings=Object.assign({model:"TripoSR",batch_mode:"independent",quality:"balanced",candidates:1,formats:"glb,obj,stl,ply",cleanup:false},saved.settings||{});
 let uploads=Array.isArray(saved.uploads)?saved.uploads.slice(0,24):[], busy=false, notice="", seen={}, latestFiles=[], lastRun=ctx.run&&ctx.run.id;
 let history=Array.isArray(saved.meshHistory)?saved.meshHistory.slice(0,70):[];
 let cards={};
 root.innerHTML='<div class="viz-pad" style="display:flex;flex-direction:column;gap:13px;padding:14px">'
 +'<div><div style="font-size:22px;font-weight:750">Image to Mesh Studio</div><div class="viz-small viz-muted">Upload photos, choose a reconstruction model, generate mesh assets and review your results.</div></div>'
 +'<div class="viz-tile" style="display:flex;flex-direction:column;gap:10px;padding:13px"><strong>1. Source images</strong><label id="meshd-drop" style="border:2px dashed var(--line,#8b98ac);border-radius:12px;padding:23px;display:flex;justify-content:center;align-items:center;text-align:center;cursor:pointer;flex-direction:column;gap:6px"><span style="font-size:27px">↑</span><strong>Choose or drop images here</strong><span class="viz-small viz-muted">PNG, JPEG, WebP · multiple files · up to 24 images</span><input id="meshd-upload" type="file" accept="image/png,image/jpeg,image/webp" multiple style="display:none"></label><div id="meshd-uploads" style="display:flex;gap:8px;flex-wrap:wrap"></div>'
 +'<label class="viz-small">Input interpretation<select id="meshd-batch" class="viz-in" style="display:block;width:100%;margin-top:4px"><option value="independent">Batch: each image is a separate object</option><option value="grouped">Group views by filename stem (uses first view only)</option></select></label>'
 +'<span class="viz-small viz-muted">Grouped naming: chair_front.jpg, chair_side.jpg, chair_back.jpg. TripoSR and Stable Fast 3D are single-image models; grouping preserves input names but does not fuse views.</span></div>'
 +'<div class="viz-tile" style="display:flex;flex-direction:column;gap:10px;padding:13px"><strong>2. Model and generation</strong><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">'
 +'<label class="viz-small">Reconstruction model<select id="meshd-model" class="viz-in" style="width:100%;display:block;margin-top:5px"><option value="TripoSR">TripoSR — geometry</option><option value="Stable Fast 3D">Stable Fast 3D — textured GLB</option></select></label>'
 +'<label class="viz-small">Quality<select id="meshd-quality" class="viz-in" style="width:100%;display:block;margin-top:5px"><option value="fast">Fast</option><option value="balanced">Balanced</option><option value="high">High</option></select></label></div>'
 +'<div id="meshd-modelinfo" class="viz-small viz-muted" style="padding:10px;border-radius:8px;background:var(--panel-2)"></div>'
 +'<label class="viz-small"><input id="meshd-cleanup" type="checkbox"> Clean mesh geometry (may discard material when converting)</label>'
 +'<div class="viz-small">Export formats: GLB · OBJ · STL · PLY</div>'
 +'<button class="viz-btn primary" id="meshd-go" style="padding:10px 16px;font-weight:650">Generate meshes</button><div class="viz-small viz-muted" id="meshd-hint"></div></div>'
 +'<div class="viz-tile" style="display:flex;flex-direction:column;gap:9px;padding:13px"><div style="display:flex;gap:10px;align-items:center"><div id="meshd-spin" style="display:none;width:25px;height:25px;flex:none;border:3px solid #adb8c54d;border-top-color:#2f4ae0;border-radius:50%;animation:meshspin .8s linear infinite"></div><div style="flex:1"><strong id="meshd-phase">Ready</strong><div id="meshd-msg" class="viz-small viz-muted">Generation starts only after you click the button.</div></div><b id="meshd-pct" class="viz-small">0%</b></div><div style="height:7px;background:#adb8c52b;border-radius:8px;overflow:hidden"><div id="meshd-bar" style="width:0%;height:100%;background:#2f4ae0;transition:width .25s"></div></div><div id="meshd-events" class="viz-small viz-muted" style="max-height:150px;overflow:auto"></div><style>@keyframes meshspin{to{transform:rotate(360deg)}}</style></div>'
 +'<div style="font-size:16px;font-weight:700">3. Generated meshes</div><div id="meshd-results" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:11px"></div></div>';
 function $ (id){return root.querySelector("#meshd-"+id);}
 function persist(){if(ctx.saveState)ctx.saveState({settings:settings,uploads:uploads,meshHistory:history},true);}
 ["model","batch","quality"].forEach(function(k){let key=k==="batch"?"batch_mode":k;$(k).value=settings[key];$(k).onchange=function(){settings[key]=this.value;persist();modelInfo();}});
 $("cleanup").checked=!!settings.cleanup;$("cleanup").onchange=function(){settings.cleanup=this.checked;persist();};
 function modelInfo(){let a=settings.model==="TripoSR";$("modelinfo").textContent=a?"TripoSR · MIT licensed · single-photo mesh reconstruction · approximately 6GB CUDA VRAM · vertex-colored GLB. Quality controls surface extraction resolution.":"Stable Fast 3D · textured UV/PBR GLB · typically about 6GB CUDA VRAM · Stability AI Community License. Quality controls texture resolution; model access may require Hugging Face authorization.";}
 modelInfo();
 async function handle(list){
  if(ctx.run&&ctx.run.active){notice="Finish current run before changing input";paint();return;}
  let additions=[...list].filter(f=>/image\/(png|jpeg|webp)/.test(f.type)).slice(0,24);
  for(let f of additions){
   if(uploads.length>=24)break;
   if(f.size>2500000){notice=f.name+" exceeds the 2.5MB input size; resize it first.";continue;}
   // Resize in browser to reduce request size and keep a bounded per-run payload.
   try {
    let data=await new Promise(function(resolve,reject){
     let reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(new Error("Cannot read "+f.name));reader.readAsDataURL(f);
    });
    let optimized=await new Promise(function(resolve,reject){
     let im=new Image();im.onload=function(){
      let factor=Math.min(1,384/Math.max(im.width,im.height));
      let c=document.createElement("canvas");c.width=Math.max(1,Math.round(im.width*factor));c.height=Math.max(1,Math.round(im.height*factor));
      c.getContext("2d").drawImage(im,0,0,c.width,c.height);
      resolve(c.toDataURL("image/jpeg",.52));
     };im.onerror=()=>reject(new Error("Cannot decode "+f.name));im.src=data;
    });
    uploads.push({name:f.name,data:optimized});
   } catch(e){notice=e.message;}
  }
  persist();paintUploads();paint();
 }
 function paintUploads(){
  let dest=$("uploads");dest.replaceChildren();
  uploads.forEach(function(it,i){
   let card=document.createElement("div");card.style.cssText="width:100px;border-radius:9px;border:1px solid var(--line);overflow:hidden;position:relative";
   let img=document.createElement("img");img.src=it.data;img.alt=it.name;img.style="width:100%;height:65px;object-fit:contain";
   let cap=document.createElement("div");cap.className="viz-small";cap.textContent=it.name;cap.title=it.name;cap.style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:4px";
   let remove=document.createElement("button");remove.type="button";remove.textContent="×";remove.title="Remove "+it.name;remove.style.cssText="position:absolute;right:3px;top:3px;border-radius:6px;cursor:pointer";
   remove.onclick=function(){uploads.splice(i,1);persist();paintUploads();paint();};
   card.append(img,cap,remove);dest.appendChild(card);
  });
 }
 $("upload").onchange=function(){handle(this.files);this.value="";};
 let drop=$("drop");drop.ondragover=function(e){e.preventDefault();drop.style.background="var(--panel-2)";};drop.ondragleave=function(){drop.style.background="";};drop.ondrop=function(e){e.preventDefault();drop.style.background="";handle(e.dataTransfer.files);};
 function paint(){
  let active=!!(busy||(ctx.run&&ctx.run.active));
  $("go").disabled=active||!uploads.length;
  $("hint").textContent=notice||(active?"Run in progress. Wait for the results.":uploads.length+" source image(s) selected.");
  let stream=(ctx.input("status")||{stream:[]}).stream||[];
  let items=stream.filter(x=>x.channel==="mesh_status"&&x.data&&typeof x.data==="object");
  let last=items.length?items[items.length-1].data:null;
  let pct=last&&Number.isFinite(+last.percent)?Math.max(0,Math.min(100,+last.percent)):0;
  $("spin").style.display=active?"block":"none";
  let failed=!active&&ctx.run&&["failed","lost","canceled"].includes(ctx.run.status);
  $("phase").textContent=failed?"Generation stopped":last&&last.stage?last.stage.replace(/_/g," ").replace(/^./,c=>c.toUpperCase()):active?"Starting run":"Ready";
  $("msg").textContent=failed?"Run "+ctx.run.status+". Open its log for details.":last&&last.message?last.message:active?"Waiting for an available worker…":"Generation starts only after you click the button.";
  $("bar").style.width=pct+"%";$("pct").textContent=Math.round(pct)+"%";
  $("events").replaceChildren();
  items.slice(-6).reverse().forEach(x=>{let div=document.createElement("div");div.textContent="• "+x.data.message;$("events").appendChild(div);});
 }
 $("go").onclick=function(){
  if(!uploads.length||busy||(ctx.run&&ctx.run.active))return;
  let payload=JSON.stringify(uploads);
  if(payload.length>48000){notice="The current EsaSim run API can carry at most 48 KB of image data. Reduce the batch size or use smaller images.";paint();return;}
  const chunks=payload.match(/[\s\S]{1,1000}/g)||[];
  if(chunks.length>48){notice="Upload too large for the run parameter transport.";paint();return;}
  let gen={launch:true,images_chunk_count:chunks.length,images_payload:"",model:settings.model,batch_mode:settings.batch_mode,quality:settings.quality,candidates:1,formats:"glb,obj,stl,ply",cleanup:!!settings.cleanup};
  chunks.forEach(function(chunk,i){gen["img_chunk_"+String(i).padStart(3,"0")]=chunk;});
  busy=true;notice="Submitting "+uploads.length+" image(s) in "+chunks.length+" verified chunks…";persist();paint();
  function submit(){
    ctx.run({params:{generator:gen}}).then(function(){busy=false;notice="Run started. Your uploaded images remain selected.";paint();},function(e){busy=false;notice=e&&e.message||"Could not start run.";paint();});
  }
  // Use SHA-256 where WebCrypto is available. The backend checks before decoding.
  if(typeof crypto!=="undefined"&&crypto.subtle){
    crypto.subtle.digest("SHA-256",new TextEncoder().encode(payload)).then(function(digest){
      gen.images_checksum=Array.from(new Uint8Array(digest)).map(function(v){return v.toString(16).padStart(2,"0");}).join("");
      submit();
    }).catch(function(){submit();});
  }else submit();
 };
 function showResults(){
  let assets=(ctx.input("meshes")||{files:[]}).files||[];
  let previews=(ctx.input("previews")||{files:[]}).files||[];
  let rows=ctx.rows("details")||[];
  let box=$("results"),run=ctx.run&&ctx.run.id||0;
  // Keep previous cards; never call replaceChildren() at a new run.
  let currentGroups={};
  [...assets,...previews].forEach(function(f){
   let key=String(f.name||"").replace(/_preview\.png$|\.(glb|obj|stl|ply)$/i,"");
   (currentGroups[key]||(currentGroups[key]=[])).push(f);
  });
  function addCard(key,runId,record,sourceFiles){
   let uid=String(runId)+":"+key;
   if(cards[uid])return cards[uid];
   let card=document.createElement("div");card.className="viz-tile";
   card.style.cssText="padding:12px;display:flex;flex-direction:column;gap:9px";
   let title=document.createElement("b");title.textContent=key+" · Run #"+runId;card.appendChild(title);
   let img=document.createElement("img");img.alt="Mesh preview "+key;
   img.style.cssText="width:100%;height:175px;object-fit:contain;background:var(--panel-2);border-radius:8px";
   card.appendChild(img);
   let meta=document.createElement("div");meta.className="viz-small viz-muted";
   meta.textContent=record&&record.row?record.row:"Loading mesh details…";card.appendChild(meta);
   let downloads=document.createElement("div");downloads.style.cssText="display:flex;flex-wrap:wrap;gap:6px";
   card.appendChild(downloads);box.appendChild(card);
   cards[uid]={card:card,img:img,meta:meta,downloads:downloads};
   if(record&&record.preview)img.src=record.preview;
   (record&&record.links||[]).forEach(function(f){appendLink(downloads,f.label,f.url);});
   return cards[uid];
  }
  function appendLink(container,label,url){
   let a=document.createElement("a");a.className="viz-btn viz-small";a.textContent=label+" ↓";
   a.target="_blank";a.rel="noopener";a.href=url;container.appendChild(a);
  }
  history.slice().reverse().forEach(function(record){
   if(record&&record.key)addCard(record.key,record.run,record);
  });
  Object.keys(currentGroups).forEach(function(key){
   let group=currentGroups[key],row=rows.find(function(r){return String(r.preview||"").replace(/_preview\.png$/,"")===key;});
   let uid=String(run)+":"+key,existing=cards[uid],record=history.find(function(h){return h.run===run&&h.key===key;});
   if(!record){
    record={key:key,run:run,preview:"",links:[],row:row?row.model+" · "+row.vertices+" vertices · "+row.faces+" faces · "+row.duration_s+" s":""};
    history.unshift(record);history=history.slice(0,70);persist();
   }
   let card=existing||addCard(key,run,record);
   if(row){record.row=row.model+" · "+row.vertices+" vertices · "+row.faces+" faces · "+row.duration_s+" s";card.meta.textContent=record.row;}
   let preview=group.find(function(f){return /_preview\.png$/i.test(f.name);});
   if(preview&&!record.preview)ctx.files.url(preview).then(function(url){record.preview=url;card.img.src=url;persist();}).catch(function(){});
   group.filter(function(f){return /\.(glb|obj|stl|ply)$/i.test(f.name);}).forEach(function(f){
    let label=f.name.split(".").pop().toUpperCase();
    if(record.links.some(function(x){return x.label===label;}))return;
    ctx.files.url(f).then(function(url){
      record.links.push({label:label,url:url});appendLink(card.downloads,label,url);persist();
    }).catch(function(){});
   });
  });
  if(!Object.keys(cards).length){
   box.textContent="Generated meshes and historical previews will appear here. Existing results remain under their original run's Results page.";
  }
 }
 ctx.on("run",function(){if(ctx.run&&ctx.run.id!==lastRun){lastRun=ctx.run.id;seen={};}paint();showResults();});
 ctx.on("update",function(){paint();showResults();});
 paintUploads();paint();showResults();
}