/* Modul 5 - panel Monitor: ringkasan status halaman + jalankan pemeriksa. */
(function () {
  "use strict";
  function $(id) { return document.getElementById(id); }
  function keluar(t) { var k = $("monitorOut"); if (k) { k.textContent = t; } }
  function domain() { var i = $("monitorDomain"); return i ? i.value : ""; }

  async function minta(jalur, opsi) {
    var r = await fetch(jalur, opsi);
    if (!r.ok) { throw new Error(jalur + " -> HTTP " + r.status); }
    return r.json();
  }

  var WARNA = {
    terverifikasi: "#3fb950", kedaluwarsa: "#f85149", ditimpa: "#d29922",
    dicabut: "#8b949e", gagal: "#f85149", tertanam: "#58a6ff", belum: "#8b949e"
  };

  window.monitorSegarkan = async function () {
    try {
      var d = await minta("/api/status/ringkas");
      var tb = $("monitorBody");
      if (!tb) { return; }
      if (!d.item || !d.item.length) {
        tb.innerHTML = '<tr><td colspan="5" style="opacity:.6">belum ada status tercatat - jalankan Periksa</td></tr>';
      } else {
        tb.innerHTML = d.item.map(function (x) {
          var w = WARNA[x.status] || "#8b949e";
          return "<tr>"
            + '<td style="max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'
            + (x.url || ("konten #" + x.konten_id)) + "</td>"
            + '<td><span style="color:' + w + '">' + (x.status || "-") + "</span></td>"
            + "<td>" + (x.basis || "-") + "</td>"
            + "<td>" + (x.bukti_terakhir || "-") + "</td>"
            + "<td>" + (x.diperbarui || "-") + "</td></tr>";
        }).join("");
      }
      var m = (d.metrik || []).map(function (x) {
        return x.nama + ": " + (x.nilai === null || x.nilai === undefined ? "-" : x.nilai)
          + (x.satuan ? " " + x.satuan : "");
      }).join("\n");
      keluar("ringkas status\n" + JSON.stringify(d.per_status) + "\n\ntotal: " + d.total
        + (m ? "\n\nmetrik:\n" + m : ""));
    } catch (e) { keluar("GAGAL: " + e.message); }
  };

  window.monitorPeriksa = async function (sungguh) {
    try {
      keluar(sungguh ? "memeriksa & menerapkan..." : "memeriksa (dry-run)...");
      var d = await minta("/api/status/periksa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: domain(), terapkan: !!sungguh, batas: 8 })
      });
      if (!d.ok) { keluar("GAGAL (kode " + d.kode + ")\n" + (d.galat || "")); return; }
      var h = d.hasil || {};
      keluar("ringkas: " + JSON.stringify(h.ringkas || {}) +
        "\n\nitem:\n" + (h.item || []).map(function (x) {
          return (x.kelas || "-") + "  " + x.aksi + "  " + x.url;
        }).join("\n"));
      window.monitorSegarkan();
    } catch (e) { keluar("GAGAL: " + e.message); }
  };

  async function isiPilihan() {
    var sel = $("monitorDomain");
    if (!sel) { return; }
    try {
      var d = await minta("/api/targets");
      var daftar = (d.item || d || []).map(function (t) { return t.domain; }).filter(Boolean);
      sel.innerHTML = '<option value="">semua domain</option>' + daftar.map(function (x) {
        return '<option value="' + x + '">' + x + "</option>";
      }).join("");
      sel.value = "waspadaweb.com";
    } catch (e) { /* biarkan */ }
  }

  document.addEventListener("DOMContentLoaded", function () {
    isiPilihan();
    window.monitorSegarkan();
  });
})();
