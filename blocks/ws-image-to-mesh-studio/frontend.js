// ── EsaSim block ──────────────────────────────────────────────────────
// Image to Mesh Studio (ws-image-to-mesh-studio) · version 9 · view, JavaScript: function render(ctx)
// Choose photos and a model, press Generate meshes: pictures travel in the run's own settings; shaded previews and GLB/OBJ/STL/PLY downloads.
// Workspace: Gianluca De Novi's workspace · Author: Gianluca De Novi
// Saved: 2026-11-14
//
// Inputs   ctx.input("id") gives { files, stream }; ctx.rows("id"), ctx.json("id"), ctx.text("id")
//   glb         Files (glb)               Meshes (GLB) · several · optional
//   exports     Files (obj, stl, ply)     Other formats · several · optional
//   previews    Files (png)               Previews · several · optional
//   details     Table (csv)               Mesh inventory · optional
//   status      Live telemetry            Live progress · optional
// Settings ctx.params.key
//   (none)
// EsaSim rewrites these lines from the block's definition each time it is saved: change the definition, not them.
// ── end of EsaSim block header ────────────────────────────────────────

/* Mesh Studio: choose pictures, a model and a quality, press Generate meshes. The pictures (re-encoded as JPEG, up to
 * 512 px) are packed ahead of time and travel inside the run's own settings, so the click starts the run at once and
 * no live connection to the run is needed. The older live transfer (ctx.send) is kept as a fallback. Results: a shaded
 * preview of each mesh and Download buttons for GLB, OBJ, STL and PLY. */
function render(ctx) {
  var MAX_SIDE = 1024, PIECE = 45000, MAX_PICS = 24;
  var VIEWS = ['front', 'left', 'back', 'right'];
  var MODELS = {
    'Hunyuan3D-2 mini': 'Best shape from one photo (Tencent, 0.6B, about 6 GB of GPU memory). Grey mesh without colour. Tencent Hunyuan Community licence: not for use in the EU, the UK or South Korea.',
    'TripoSR': 'Fast coloured mesh from one photo (VAST AI, MIT licence). Softer geometry than Hunyuan3D-2.',
    'Hunyuan3D-2 multi-view': 'Two to four photos of the SAME object from the front, left, back and right, fused into one shape (Tencent, 1.1B). Mark each photo\'s side below. Same licence as Hunyuan3D-2 mini.'
  };
  var st = ctx.state || {};
  var settings = Object.assign({ model: 'Hunyuan3D-2 mini', quality: 'balanced', candidates: 1, compact: true }, st.settings || {});
  if (!MODELS[settings.model]) settings.model = 'Hunyuan3D-2 mini';
  var sources = Array.isArray(st.sources) ? st.sources.filter(function (s) { return s && s.data; }) : [];
  var session = st.session || '', manifest = st.manifest || null;
  var busy = false, notice = '', sentAt = {}, seenReq = {}, sending = false, cards = {};

  var root = ctx.el;
  root.innerHTML = '<div class="viz-pad" style="display:flex;flex-direction:column;gap:12px;padding:14px;box-sizing:border-box">'
    + '<div><div style="font-size:22px;font-weight:750">Image to Mesh Studio</div><div class="viz-small viz-muted">Photos in, 3D meshes out: preview them here, turn them in the 3D view, download GLB, OBJ, STL or PLY.</div></div>'
    + '<div class="viz-tile" style="display:flex;flex-direction:column;gap:10px;padding:13px"><strong>1 · Pictures</strong>'
    + '<label id="ms-drop" style="border:2px dashed var(--line,#8b98ac);border-radius:12px;padding:20px;display:flex;flex-direction:column;align-items:center;gap:5px;cursor:pointer;text-align:center">'
    + '<span style="font-size:24px">↑</span><strong>Choose or drop pictures</strong><span class="viz-small viz-muted">PNG, JPEG or WebP · one object per photo, centred, plain background works best · up to 24</span>'
    + '<input id="ms-file" type="file" accept="image/png,image/jpeg,image/webp" multiple style="display:none"></label>'
    + '<div id="ms-pics" style="display:flex;gap:8px;flex-wrap:wrap"></div>'
    + '<div style="display:flex;gap:8px;align-items:center"><button id="ms-clear" class="viz-btn" type="button">Remove all</button><span id="ms-count" class="viz-small viz-muted"></span></div></div>'
    + '<div class="viz-tile" style="display:flex;flex-direction:column;gap:10px;padding:13px"><strong>2 · Model</strong>'
    + '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px">'
    + '<label class="viz-small">Model<select id="ms-model" class="viz-in" style="display:block;width:100%;margin-top:5px"><option>Hunyuan3D-2 mini</option><option>TripoSR</option><option>Hunyuan3D-2 multi-view</option></select></label>'
    + '<label class="viz-small">Quality<select id="ms-quality" class="viz-in" style="display:block;width:100%;margin-top:5px"><option value="fast">Fast</option><option value="balanced">Balanced</option><option value="high">High (slower)</option></select></label>'
    + '<label class="viz-small" id="ms-varlabel">Variations per object<input id="ms-var" class="viz-in" type="number" min="1" max="4" style="display:block;width:100%;box-sizing:border-box;margin-top:5px"></label></div>'
    + '<div id="ms-info" class="viz-small viz-muted" style="padding:9px 10px;border-radius:8px;background:var(--panel-2)"></div>'
    + '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><button id="ms-go" class="viz-btn primary" style="padding:10px 18px;font-weight:650">Generate meshes</button><button id="ms-compact" class="viz-btn" type="button" style="display:none" title="Sends the pictures (up to 512 px, JPEG) inside the run\'s own settings. Generate meshes does this by default">Send compactly</button><span id="ms-hint" class="viz-small viz-muted"></span></div></div>'
    + '<div class="viz-tile" style="display:flex;flex-direction:column;gap:8px;padding:13px"><div style="display:flex;gap:10px;align-items:center"><div id="ms-spin" style="display:none;width:24px;height:24px;flex:none;border:3px solid #adb8c54d;border-top-color:var(--accent,#2f4ae0);border-radius:50%;animation:msspin .8s linear infinite"></div><div style="flex:1;min-width:0"><strong id="ms-phase">Ready</strong><div id="ms-msg" class="viz-small viz-muted">Nothing runs until you press Generate meshes.</div></div><b id="ms-pct" class="viz-small">0%</b></div>'
    + '<div style="height:7px;background:#adb8c52b;border-radius:8px;overflow:hidden"><div id="ms-bar" style="width:0%;height:100%;background:var(--accent,#2f4ae0);transition:width .25s"></div></div>'
    + '<div id="ms-events" class="viz-small viz-muted" style="max-height:130px;overflow:auto"></div><style>@keyframes msspin{to{transform:rotate(360deg)}}</style></div>'
    + '<div style="font-size:16px;font-weight:700">3 · Meshes</div><div id="ms-results" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:11px"></div></div>';
  function $(id) { return root.querySelector('#ms-' + id); }

  function persist() {
    if (!ctx.saveState) return Promise.resolve();
    try {
      changed();
      var r = ctx.saveState({ settings: settings, sources: sources, session: session, manifest: manifest }, true);
      return r && r.then ? r : Promise.resolve();
    } catch (e) { return Promise.reject(e); }
  }
  function multi() { return settings.model === 'Hunyuan3D-2 multi-view'; }
  function changed() { setTimeout(function () { prepack().catch(function () {}); }, 0); }

  // ---------------------------------------------------------------------------------------------- pictures
  function viewOf(name) { var m = /[_\-\s](front|left|back|right)$/i.exec(String(name).replace(/\.[^.]+$/, '')); return m ? m[1].toLowerCase() : ''; }
  function objectOf(name) { return String(name).replace(/\.[^.]+$/, '').replace(/[_\-\s](front|left|back|right|side|top|bottom|view\d*)$/i, '') || 'object'; }
  function readFile(f) {
    return new Promise(function (resolve, reject) {
      var rd = new FileReader();
      rd.onload = function () {
        var im = new Image();
        im.onload = function () {
          var s = Math.min(1, MAX_SIDE / Math.max(im.width, im.height));
          var c = document.createElement('canvas'); c.width = Math.max(1, Math.round(im.width * s)); c.height = Math.max(1, Math.round(im.height * s));
          var g = c.getContext('2d'); g.drawImage(im, 0, 0, c.width, c.height);
          var alpha = false;
          if (/png|webp/i.test(f.type)) {                             // keep a cut-out's transparency
            var d = g.getImageData(0, 0, c.width, c.height).data;
            for (var i = 3; i < d.length; i += 16) if (d[i] < 250) { alpha = true; break; }
          }
          var data = alpha ? c.toDataURL('image/png') : c.toDataURL('image/jpeg', 0.92);
          var t = document.createElement('canvas'), ts = Math.min(1, 160 / Math.max(c.width, c.height));
          t.width = Math.round(c.width * ts); t.height = Math.round(c.height * ts); t.getContext('2d').drawImage(c, 0, 0, t.width, t.height);
          resolve({ name: f.name, data: data, thumb: t.toDataURL('image/jpeg', 0.7), view: viewOf(f.name), object: viewOf(f.name) ? objectOf(f.name) : '', w: c.width, h: c.height });
        };
        im.onerror = function () { reject(new Error('Cannot read ' + f.name)); };
        im.src = rd.result;
      };
      rd.onerror = function () { reject(new Error('Cannot read ' + f.name)); };
      rd.readAsDataURL(f);
    });
  }
  function add(list) {
    if (ctx.run && ctx.run.active) { notice = 'Wait for the current run to finish before changing the pictures.'; paint(); return; }
    var files = Array.prototype.filter.call(list, function (f) { return /image\/(png|jpeg|webp)/.test(f.type); });
    var chain = Promise.resolve();
    files.forEach(function (f) {
      chain = chain.then(function () {
        if (sources.length >= MAX_PICS) return;
        return readFile(f).then(function (s) { sources.push(s); }, function (e) { notice = e.message; });
      });
    });
    chain.then(function () {
      autoViews(); paintPics(); paint();
      persist().catch(function () { notice = 'These pictures are too large to keep in the view: remove some and try again.'; paint(); });
    });
  }
  function autoViews() {                                            // multi-view: unlabelled pictures get the free sides in order
    var used = {};
    sources.forEach(function (s) { if (s.view) used[(s.object || 'object') + '|' + s.view] = 1; });
    sources.forEach(function (s) {
      if (s.view) return;
      var o = s.object || 'object';
      for (var i = 0; i < VIEWS.length; i++) if (!used[o + '|' + VIEWS[i]]) { s.view = VIEWS[i]; used[o + '|' + VIEWS[i]] = 1; return; }
    });
  }
  function paintPics() {
    var box = $('pics'); box.replaceChildren();
    sources.forEach(function (s, i) {
      var card = document.createElement('div');
      card.style.cssText = 'width:118px;border:1px solid var(--line,#8b98ac55);border-radius:9px;overflow:hidden;position:relative;display:flex;flex-direction:column';
      var img = document.createElement('img'); img.src = s.thumb || s.data; img.alt = s.name; img.style.cssText = 'width:100%;height:80px;object-fit:contain;background:var(--panel-2)';
      var cap = document.createElement('div'); cap.className = 'viz-small'; cap.textContent = s.name; cap.title = s.name + ' · ' + s.w + '×' + s.h + ' px';
      cap.style.cssText = 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:3px 5px';
      var x = document.createElement('button'); x.type = 'button'; x.textContent = '×'; x.title = 'Remove'; x.style.cssText = 'position:absolute;right:3px;top:3px;border-radius:6px;cursor:pointer';
      x.onclick = function () { if (ctx.run && ctx.run.active) return; sources.splice(i, 1); paintPics(); paint(); persist(); };
      card.append(img, cap, x);
      if (multi()) {
        var sel = document.createElement('select'); sel.className = 'viz-in viz-small'; sel.style.margin = '0 4px 4px';
        VIEWS.forEach(function (v) { var o = document.createElement('option'); o.value = v; o.textContent = v; sel.appendChild(o); });
        sel.value = s.view || 'front';
        sel.onchange = function () { s.view = sel.value; persist(); paint(); };
        var obj = document.createElement('input'); obj.className = 'viz-in viz-small'; obj.placeholder = 'object'; obj.value = s.object || '';
        obj.title = 'Pictures with the same object name are fused into one mesh'; obj.style.cssText = 'margin:0 4px 5px;box-sizing:border-box;width:calc(100% - 8px)';
        obj.oninput = function () { s.object = obj.value.trim(); persist(); paint(); };
        card.append(sel, obj);
      }
      box.appendChild(card);
    });
    $('count').textContent = sources.length ? sources.length + ' picture' + (sources.length === 1 ? '' : 's') : 'No pictures yet.';
  }
  $('file').onchange = function () { add(this.files); this.value = ''; };
  var drop = $('drop');
  drop.ondragover = function (e) { e.preventDefault(); drop.style.background = 'var(--panel-2)'; };
  drop.ondragleave = function () { drop.style.background = ''; };
  drop.ondrop = function (e) { e.preventDefault(); drop.style.background = ''; add(e.dataTransfer.files); };
  $('clear').onclick = function () { if (ctx.run && ctx.run.active) return; sources = []; paintPics(); paint(); persist(); };

  // ---------------------------------------------------------------------------------------------- settings
  $('model').value = settings.model; $('quality').value = settings.quality; $('var').value = settings.candidates;
  $('model').onchange = function () { settings.model = this.value; if (multi()) autoViews(); persist(); paintPics(); paint(); };
  $('quality').onchange = function () { settings.quality = this.value; persist(); };
  $('var').onchange = function () { settings.candidates = Math.max(1, Math.min(4, Math.floor(+this.value) || 1)); this.value = settings.candidates; persist(); };

  function problems() {
    if (!sources.length) return 'Add at least one picture.';
    if (multi()) {
      var objs = {};
      sources.forEach(function (s) { var o = s.object || 'object'; (objs[o] = objs[o] || []).push(s.view || 'front'); });
      for (var o in objs) {
        var v = objs[o];
        if (v.length > 4) return 'Object "' + o + '" has more than 4 pictures: one per side at most.';
        if (v.indexOf('front') < 0) return 'Object "' + o + '" needs a picture marked front.';
        if (v.some(function (x, i) { return v.indexOf(x) !== i; })) return 'Object "' + o + '" has two pictures marked as the same side.';
      }
    }
    return '';
  }

  // ---------------------------------------------------------------------------------------------- generate
  function b64of(s) { return s.data.slice(s.data.indexOf(',') + 1); }
  function sha256(b64) {
    if (!(window.crypto && crypto.subtle)) return Promise.resolve('');
    var bin = atob(b64), u = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return crypto.subtle.digest('SHA-256', u).then(function (d) { return Array.from(new Uint8Array(d)).map(function (x) { return x.toString(16).padStart(2, '0'); }).join(''); }).catch(function () { return ''; });
  }
  $('compact').onclick = startCompact;
  $('go').onclick = function () {
    if (settings.compact) { startCompact(); return; }               // default: the pictures go in the run's settings
    if (busy || (ctx.run && ctx.run.active)) return;
    var bad = problems(); if (bad) { notice = bad; paint(); return; }
    busy = true; notice = 'Preparing the pictures…'; paint();
    Promise.all(sources.map(function (s) { return sha256(b64of(s)); })).then(function (hashes) {
      session = 's' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
      manifest = sources.map(function (s, i) {
        return { i: i, name: s.name, view: multi() ? (s.view || 'front') : '', object: multi() ? (s.object || 'object') : '',
                 parts: Math.max(1, Math.ceil(b64of(s).length / PIECE)), sha256: hashes[i] };
      });
      sentAt = {}; seenReq = {}; cards = {}; $('results').replaceChildren();
      return persist().then(function () {
        return ctx.run({ params: { generator: { launch: true, session: session, upload_manifest: JSON.stringify(manifest),
          compact_count: 0, model: settings.model, quality: settings.quality, candidates: settings.candidates } } });
      });
    }).then(function () { busy = false; notice = ''; paint(); }, function (e) {
      busy = false; notice = (e && e.message) || 'Could not start the run.'; paint();
    });
  };

  // Compact upload: the pictures, re-encoded smaller, travel in the run's own settings (pieces of SLOT characters):
  // no live messages needed.
  var SLOTS = 48, SLOT = 4000, RUN_SLOTS = 24;
  function shrink(s, side, q) {
    return new Promise(function (resolve) {
      var im = new Image();
      im.onload = function () {
        var k = Math.min(1, side / Math.max(im.width, im.height)), c = document.createElement('canvas');
        c.width = Math.max(1, Math.round(im.width * k)); c.height = Math.max(1, Math.round(im.height * k));
        var g = c.getContext('2d'); g.fillStyle = '#ffffff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
        resolve(c.toDataURL('image/jpeg', q));
      };
      im.onerror = function () { resolve(''); };
      im.src = s.data;
    });
  }
  // Both models look at the object at about 512 px, so 512 px pictures lose nothing. The total size is at most the
  // budget below; it halves when EsaSim refuses a start for its size.
  function budget() { return Math.max(8000, Math.min(RUN_SLOTS * SLOT, +settings.size_budget || RUN_SLOTS * SLOT)); }
  function compactPayload() {
    var tries = [[512, 0.9], [512, 0.8], [448, 0.75], [384, 0.7], [320, 0.65], [256, 0.6]], n = 0, limit = budget();
    function attempt() {
      var t = tries[n];
      return Promise.all(sources.map(function (s) { return shrink(s, t[0], t[1]); })).then(function (datas) {
        var json = JSON.stringify(sources.map(function (s, i) {
          return { name: s.name, data: datas[i], view: multi() ? (s.view || 'front') : '', object: multi() ? (s.object || 'object') : '' };
        }));
        if (json.length <= limit) return { json: json, side: t[0] };
        n++;
        if (n >= tries.length) throw new Error('Too many pictures for one run: generate a few at a time.');
        return attempt();
      });
    }
    return attempt();
  }
  // The payload is prepared ahead (whenever the pictures or their sides change), so a click starts the run at once:
  // EsaSim only lets a view start a run straight from the click, not after slow work.
  var packed = null, packKey = '', packing = null;
  function payloadKey() { return settings.model + '|' + budget() + '|' + sources.map(function (s) { return s.name + ':' + s.data.length + ':' + (s.view || '') + ':' + (s.object || ''); }).join('|'); }
  function prepack() {
    var key = payloadKey();
    if (!sources.length) { packed = null; packKey = key; return Promise.resolve(null); }
    if (packed && packKey === key) return Promise.resolve(packed);
    var p = packing = compactPayload().then(function (r) { if (p === packing) { packed = r; packKey = key; packing = null; if (/^Preparing the pictures/.test(notice)) notice = ''; paint(); } return r; },
      function (e) { if (p === packing) { packing = null; notice = e.message; paint(); } throw e; });
    return p;
  }
  function startCompact() {
    if (busy || (ctx.run && ctx.run.active)) return;
    var bad = problems(); if (bad) { notice = bad; paint(); return; }
    if (!packed || packKey !== payloadKey()) { notice = 'Preparing the pictures… press Generate meshes again in a moment.'; prepack().catch(function () {}); paint(); return; }
    var r = packed;
    // EsaSim takes at most 30 settings per run: 6 here plus only the pieces actually used (at most RUN_SLOTS)
    var count = Math.ceil(r.json.length / SLOT);
    var gen = { launch: true, compact_count: count, compact_len: r.json.length, model: settings.model, quality: settings.quality, candidates: settings.candidates };
    for (var k = 0; k < count; k++) gen['c' + String(k).padStart(2, '0')] = r.json.slice(k * SLOT, (k + 1) * SLOT);
    busy = true; notice = 'Starting the run…'; paint();
    var call, done = false;
    try { call = ctx.run({ params: { generator: gen } }); } catch (e) { call = Promise.reject(e); }   // called straight from the click
    sendInfo = 'Pictures sent with the run (' + sources.length + ' at up to ' + r.side + ' px, ' + Math.round(r.json.length / 1000) + ' kB).';
    function refused(why) {
      if (done) return; done = true; busy = false;
      var sizeIssue = /20 s|large|long|size|bytes|too big/i.test(why);
      if (sizeIssue && budget() > 8000) { settings.size_budget = Math.floor(budget() / 2); packed = null; persist().catch(function () {}); }
      notice = 'EsaSim did not start the run (' + why + ').' + (sizeIssue ? ' Smaller pictures are being prepared: press Generate meshes again.' : '');
      paint();
    }
    setTimeout(function () { if (!done && !(ctx.run && ctx.run.active)) refused('no answer in 20 s'); }, 20000);
    Promise.resolve(call).then(function () { if (done) return; done = true; busy = false; notice = ''; cards = {}; $('results').replaceChildren(); paint(); },
      function (e) { refused((e && e.message) || String(e)); });
  }

  // The generator asks for the pictures (stage awaiting_upload, naming them and the pieces still missing): send them.
  // The request carries its own upload session, so this works even if the view restarted and lost its own copy.
  var sendInfo = '';
  function serve(items) {
    if (sending) return;
    var req = null;
    for (var i = items.length - 1; i >= 0; i--) {
      if (items[i].data.stage === 'upload_complete' || items[i].data.stage === 'upload_failed') return;
      if (items[i].data.stage === 'awaiting_upload') { req = items[i].data; break; }
    }
    if (!req || !Array.isArray(req.missing)) return;
    var names = Array.isArray(req.names) ? req.names : null;
    if (names && (names.length !== sources.length || names.some(function (n, k) { return sources[k].name !== n; }))) {
      sendInfo = 'The run asks for ' + names.length + ' picture(s) that this view no longer holds: press Generate meshes again.';
      return;
    }
    var piece = +req.piece || PIECE, sid = req.session || session;
    var now = Date.now(), todo = req.missing.filter(function (m) { return !(sentAt[m[0] + ':' + m[1]] > now - 8000); });
    if (!todo.length) return;
    sending = true;
    var chain = Promise.resolve(), sent = 0;
    todo.forEach(function (m) {
      chain = chain.then(function () {
        var s = sources[m[0]]; if (!s) return;
        var b = b64of(s), parts = Math.max(1, Math.ceil(b.length / piece));
        sentAt[m[0] + ':' + m[1]] = Date.now();
        var call;
        try { call = ctx.send('mesh_upload', { session: sid, i: m[0], part: m[1], parts: parts, b64: b.slice(m[1] * piece, (m[1] + 1) * piece) }); }
        catch (e) { return Promise.reject(e); }
        return Promise.race([Promise.resolve(call), new Promise(function (_, no) { setTimeout(function () { no(new Error('no answer from EsaSim in 15 s')); }, 15000); })])
          .then(function () { sent++; });
      });
    });
    chain.then(function () { sendInfo = 'Sent ' + sent + ' piece(s) to the run; waiting for it to confirm…'; },
               function (e) { sendInfo = 'Sending the pictures failed: ' + ((e && e.message) || String(e)); })
      .then(function () { sending = false; paint(); });
  }

  // ---------------------------------------------------------------------------------------------- progress
  function paint() {
    var active = !!(busy || (ctx.run && ctx.run.active));
    var items = ((ctx.input('status') || {}).stream || []).filter(function (x) { return x.channel === 'mesh_status' && x.data && typeof x.data === 'object'; });
    serve(items);
    var bad = problems();
    $('go').disabled = active || !!bad;
    $('compact').disabled = active || !!bad;
    if (items.some(function (x) { return x.data.stage === 'upload_failed'; }) && !settings.compact) { settings.compact = true; persist(); }
    $('hint').textContent = notice || (active && sendInfo ? sendInfo : '') || (active ? 'Working…' : bad || (packing ? 'Preparing the pictures…' : '') || 'Ready: ' + sources.length + ' picture' + (sources.length === 1 ? '' : 's') + '.');
    $('info').textContent = MODELS[settings.model];
    $('varlabel').style.display = settings.model === 'TripoSR' ? 'none' : '';
    var last = items.length ? items[items.length - 1].data : null;
    var pct = last && isFinite(+last.percent) ? Math.max(0, Math.min(100, +last.percent)) : 0;
    var failed = !active && ctx.run && ['failed', 'lost', 'canceled'].indexOf(ctx.run.status) >= 0;
    var names = { awaiting_upload: 'Sending the pictures', upload_failed: 'Live transfer failed: press Generate meshes again', upload_complete: 'Pictures received', installing: 'Installing (first time only)', loading: 'Loading the model',
                  generating: 'Generating', exported: 'Exporting', done: 'Done', idle: 'Ready', ready: 'Ready to generate', preparing: 'Preparing' };
    $('spin').style.display = active ? 'block' : 'none';
    $('phase').textContent = /^EsaSim did not start/.test(notice) ? 'Run not started' : !active && notice ? 'Note' : failed ? 'Generation stopped' : last && last.stage ? (names[last.stage] || last.stage) : active ? 'Starting…' : 'Ready';
    $('msg').textContent = !active && notice ? notice : failed ? 'Run ' + ctx.run.status + ': open the run\'s log for the reason.' : last && last.message ? last.message : active ? 'Waiting for the GPU machine…' : 'Nothing runs until you press Generate meshes.';
    $('bar').style.width = pct + '%'; $('pct').textContent = Math.round(pct) + '%';
    var ev = $('events'); ev.replaceChildren();
    items.filter(function (x) { return !x.data.heartbeat; }).slice(-6).reverse().forEach(function (x) {
      var d = document.createElement('div'); d.textContent = '• ' + x.data.message; ev.appendChild(d);
    });
  }

  // ---------------------------------------------------------------------------------------------- results
  function save(file, btn) {
    var label = btn.textContent; btn.disabled = true; btn.textContent = '…';
    var mime = /\.glb$/i.test(file.name) ? 'model/gltf-binary' : /\.stl$/i.test(file.name) ? 'model/stl' : 'application/octet-stream';
    ctx.files.buffer(file).then(function (buf) { return ctx.save(file.name, new Blob([buf], { type: mime })); })
      .then(function () { btn.textContent = '✓ ' + label; setTimeout(function () { btn.textContent = label; }, 1500); },
            function (e) { btn.textContent = label; notice = 'Download failed: ' + ((e && e.message) || 'file not available'); paint(); })
      .then(function () { btn.disabled = false; });
  }
  // ctx.rows may give the rows, a promise of them, or nothing yet: keep the last list it gave
  var rowCache = [], rowAsked = '';
  function tableRows() {
    var files = ((ctx.input('details') || {}).files || []), sig = files.map(function (f) { return f.id; }).join(',');
    var r;
    try { r = ctx.rows('details'); } catch (e) { r = null; }
    if (Array.isArray(r)) rowCache = r;
    else if (r && typeof r.then === 'function' && rowAsked !== sig) {
      rowAsked = sig;
      r.then(function (x) { if (Array.isArray(x)) { rowCache = x; results(); } }, function () {});
    } else if (r && Array.isArray(r.rows)) rowCache = r.rows;
    return rowCache;
  }
  function results() {
    var all = [].concat((ctx.input('glb') || {}).files || [], (ctx.input('exports') || {}).files || []);
    var previews = (ctx.input('previews') || {}).files || [];
    var rows = tableRows();
    var groups = {};
    all.forEach(function (f) { var k = f.name.replace(/\.(glb|obj|stl|ply)$/i, ''); (groups[k] = groups[k] || []).push(f); });
    var box = $('results'), keys = Object.keys(groups).sort();
    var ph = box.querySelector('[data-placeholder]');
    if (!keys.length) { if (!box.children.length) box.innerHTML = '<div data-placeholder="1" class="viz-small viz-muted">The meshes of the last run appear here.</div>'; return; }
    if (ph) ph.remove();
    keys.forEach(function (k) {
      var c = cards[k];
      if (!c) {
        var tile = document.createElement('div'); tile.className = 'viz-tile'; tile.style.cssText = 'padding:11px;display:flex;flex-direction:column;gap:8px';
        var t = document.createElement('b'); t.textContent = k;
        var img = document.createElement('img'); img.alt = 'Preview of ' + k; img.style.cssText = 'width:100%;height:200px;object-fit:contain;background:var(--panel-2);border-radius:8px';
        var meta = document.createElement('div'); meta.className = 'viz-small viz-muted';
        var dl = document.createElement('div'); dl.style.cssText = 'display:flex;gap:6px;flex-wrap:wrap';
        tile.append(t, img, meta, dl); box.appendChild(tile);
        c = cards[k] = { img: img, meta: meta, dl: dl, buttons: {}, preview: '' };
      }
      var pv = previews.filter(function (f) { return f.name === k + '_preview.png'; })[0];
      if (pv && c.preview !== pv.id) { c.preview = pv.id; ctx.files.url(pv).then(function (u) { c.img.src = u; }); }
      var r = rows.filter(function (x) { return x.object === k; })[0];
      if (r) c.meta.textContent = r.model + ' · ' + Number(r.vertices).toLocaleString() + ' vertices · ' + Number(r.faces).toLocaleString() + ' faces · ' + (r.colour === 'none' ? 'no colour' : r.colour) + (+r.seconds ? ' · ' + r.seconds + ' s' : '');
      ['glb', 'obj', 'stl', 'ply'].forEach(function (ext) {
        var f = groups[k].filter(function (x) { return x.name.toLowerCase().endsWith('.' + ext); })[0];
        if (!f || c.buttons[ext]) return;
        var b = document.createElement('button'); b.type = 'button'; b.className = 'viz-btn' + (ext === 'glb' ? ' primary' : ''); b.textContent = '↓ ' + ext.toUpperCase();
        b.onclick = function () { save(f, b); };
        c.buttons[ext] = b; c.dl.appendChild(b);
      });
    });
  }

  ctx.on('update', function () { paint(); results(); });
  ctx.on('run', function () { notice = ''; paint(); results(); });
  paintPics(); paint(); results(); changed();
}
