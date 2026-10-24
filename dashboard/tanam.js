/* Halaman Tanam: unggah blok/berkas ke docroot target lewat FTP/FTPS atau ssh. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function tampilkan(t) { var k = $("tanamOut"); if (k) { k.textContent = t; } }
  function baris(t) { var k = $("tanamOut"); if (k) { k.textContent += (k.textContent ? "\n" : "") + t; } }

  async function minta(jalur, opsi) {
    var r = await fetch(jalur, opsi);
    var teks = await r.text();
    var d = null;
    try { d = teks ? JSON.parse(teks) : null; } catch (e) { d = null; }
    if (!r.ok) {
      var pesan = (d && (d.detail || d.pesan)) || teks || "";
      throw new Error(jalur + " -> HTTP " + r.status + (pesan ? " | " + pesan : ""));
    }
    return d;
  }

  async function daftarTarget() {
    var d = await minta("/api/targets");
    var arr = Array.isArray(d) ? d : (d && (d.item || d.target || d.data));
    return Array.isArray(arr) ? arr : [];
  }

  window.tanamMuat = async function () {
    var sel = $("tanamTarget");
    if (!sel) { return; }
    try {
      var arr = await daftarTarget();
      sel.innerHTML = "";
      if (!arr.length) { sel.innerHTML = '<option value="">(tidak ada target)</option>'; return; }
      arr.forEach(function (t) {
        var o = document.createElement("option");
        o.value = t.id;
        o.textContent = t.domain + (t.tipe ? "  [" + t.tipe + "]" : "") + (t.status ? " - " + t.status : "");
        sel.appendChild(o);
      });
      baris("target dimuat: " + arr.length + " (dari /api/targets)");
    } catch (e) { tampilkan("GAGAL memuat target: " + e.message); }
  };

  window.tanamKirim = async function () {
    var sel = $("tanamTarget"), u = $("tanamUser"), s = $("tanamSandi"), sp = $("tanamSapu");
    if (!sel || !sel.value) { tampilkan("Pilih target dulu."); return; }
    var body = {
      target_id: sel.value,
      user: u ? u.value : "",
      sandi: s ? s.value : "",
      sapu: !!(sp && sp.checked)
    };
    try {
      tampilkan("MENGUNGGAH ke " + sel.options[sel.selectedIndex].textContent + " ...");
      var d = await minta("/api/tanam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (d && d.ok === false) { tampilkan("GAGAL: " + (d.pesan || JSON.stringify(d))); return; }
      tampilkan(JSON.stringify(d, null, 2));
    } catch (e) { tampilkan("GAGAL: " + e.message); }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.tanamMuat);
  } else { window.tanamMuat(); }
})();
