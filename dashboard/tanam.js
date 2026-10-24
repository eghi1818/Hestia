/* Halaman Tanam: unggah blok/berkas ke docroot target lewat FTP/FTPS atau ssh. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function tampilkan(t) { var k = $("tanamOut"); if (k) k.textContent = t; }
  function baris(t) { var k = $("tanamOut"); if (k) { k.textContent += (k.textContent ? "\n" : "") + t; } }

  async function minta(jalur, opsi) {
    var r = await fetch(jalur, opsi);
    if (!r.ok) { throw new Error(jalur + " -> HTTP " + r.status); }
    return r.json();
  }

  async function daftarTarget() {
    var kandidat = ["/api/target", "/api/targets"];
    for (var i = 0; i < kandidat.length; i++) {
      try {
        var d = await minta(kandidat[i]);
        var arr = Array.isArray(d) ? d : (d.item || d.target || d.data);
        if (Array.isArray(arr) && arr.length) { return arr; }
      } catch (e) { }
    }
    return [];
  }

  window.tanamMuat = async function () {
    var sel = $("tanamTarget");
    if (!sel) { return; }
    var arr = await daftarTarget();
    sel.innerHTML = "";
    if (!arr.length) { sel.innerHTML = '<option value="">(target tidak terbaca)</option>'; return; }
    arr.forEach(function (t) {
      var o = document.createElement("option");
      o.value = t.id;
      o.textContent = (t.domain || t.nama || ("target " + t.id));
      sel.appendChild(o);
    });
    baris("target dimuat: " + arr.length);
  };

  window.tanamKirim = async function () {
    var sel = $("tanamTarget");
    var u = $("tanamUser"), s = $("tanamSandi"), sp = $("tanamSapu");
    var body = {
      target_id: sel ? sel.value : "",
      user: u ? u.value : "",
      sandi: s ? s.value : "",
      sapu: !!(sp && sp.checked)
    };
    try {
      tampilkan("MENGUNGGAH...");
      var d = await minta("/api/tanam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (d.ok === false) { tampilkan("GAGAL: " + (d.pesan || "tidak diketahui")); return; }
      tampilkan(JSON.stringify(d, null, 2));
    } catch (e) { tampilkan("GAGAL: " + e.message); }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.tanamMuat);
  } else { window.tanamMuat(); }
})();
