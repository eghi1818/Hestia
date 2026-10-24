/* Modul 4 - halaman Driver 301/410. Rencana read-only; Terapkan satu-satunya jalur tulis. */
(function () {
  "use strict";

  function $(id) { return document.getElementById(id); }
  function tampilkan(teks) { var k = $("driverOut"); if (k) k.textContent = teks; }
  function domain() { var i = $("driverDomain"); return i ? i.value.trim() : ""; }

  async function minta(jalur, opsi) {
    var r = await fetch(jalur, opsi);
    if (!r.ok) throw new Error(jalur + " -> HTTP " + r.status);
    return r.json();
  }

  window.driverRencana = async function () {
    try {
      var d = await minta("/api/driver/plan?domain=" + encodeURIComponent(domain()));
      var baris = (d.item || []).map(function (x) { return x.op + "   " + x.line; }).join("\n");
      tampilkan("RENCANA  " + JSON.stringify(d.ringkas) + "\n\n" + (baris || "(tidak ada aturan untuk domain ini)"));
    } catch (e) { tampilkan("GAGAL: " + e.message); }
  };

  window.driverDryRun = function () { return window.driverTerapkan(false); };

  window.driverTerapkan = async function (sungguh) {
    if (sungguh === undefined) { sungguh = true; }
    try {
      tampilkan(sungguh ? "MENERAPKAN..." : "DRY-RUN...");
      var d = await minta("/api/driver/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: domain(), terapkan: !!sungguh })
      });
      if (!d.ok) { tampilkan("GAGAL: " + (d.pesan || "tidak diketahui")); return; }
      var h = d.hasil || {};
      tampilkan("HASIL\nchanged=" + h.changed + "  applied=" + h.applied +
        "  tested=" + h.tested + "  reloaded=" + h.reloaded +
        (d.pesan ? "\npesan: " + d.pesan : "") +
        "\n\n" + (d.diff || "(tidak ada perubahan)"));
    } catch (e) { tampilkan("GAGAL: " + e.message); }
  };

  window.driverVerifikasi = async function () {
    try {
      var d = await minta("/api/driver/verify?domain=" + encodeURIComponent(domain()));
      var baris = (d.item || []).map(function (x) { return (x.ok ? "ok     " : "GAGAL  ") + x.pesan; }).join("\n");
      tampilkan("VERIFIKASI  lulus=" + d.lulus + "\n\n" + (baris || "(tidak ada aturan untuk domain ini)"));
    } catch (e) { tampilkan("GAGAL: " + e.message); }
  };

  async function isiPilihan() {
    var sel = $("driverDomain");
    if (!sel) { return; }
    try {
      var d = await minta("/api/targets");
      var daftar = (d.item || d || []).map(function (t) { return t.domain; }).filter(Boolean);
      sel.innerHTML = daftar.map(function (x) {
        return '<option value="' + x + '">' + x + "</option>";
      }).join("");
      if (daftar.indexOf("waspadaweb.com") >= 0) { sel.value = "waspadaweb.com"; }
      if (daftar.indexOf("persaudaraan.com") >= 0) { sel.value = "persaudaraan.com"; }
    } catch (e) { /* biarkan kosong */ }
  }

  document.addEventListener("DOMContentLoaded", function () { isiPilihan(); });
})();
