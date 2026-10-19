/* live.js - sambungan Hestia ke API.
   Menempel dari luar: index.html milik desain tidak dibongkar.
   Tugasnya satu: ganti data contoh dengan data nyata dari /api. */
(function () {
  "use strict";

  var LABEL = {
    kandidat: "Kandidat", dianalisis: "Dianalisis", aktif: "Aktif",
    rusak: "Rusak", dibersihkan: "Dibersihkan", nonaktif: "Nonaktif"
  };

  function judul(s) { return LABEL[s] || s; }

  function keBentukLokal(r) {
    return {
      id: r.id,
      domain: r.domain,
      sub: r.tipe || "-",
      type: r.tipe || "Lain",
      status: judul(r.status),
      score: 0,
      owner: r.owner || "-",
      pages: 0,
      checked: String(r.updated_at || "").replace("T", " "),
      tags: String(r.tags || "").split(",").filter(Boolean)
    };
  }

  function hitungSehat(rows) {
    if (!rows.length) { return 0; }
    var sehat = rows.filter(function (r) {
      return r.status === "aktif" || r.status === "kandidat";
    }).length;
    return Math.round((sehat / rows.length) * 100);
  }

  function pasangPenanda(jumlah) {
    var lama = document.getElementById("liveBadge");
    if (lama) { lama.remove(); }
    var b = document.createElement("div");
    b.id = "liveBadge";
    b.textContent = jumlah >= 0 ? ("data nyata - " + jumlah + " target") : "API tidak terjangkau";
    b.style.cssText = "display:inline-block;font-size:11px;padding:3px 9px;border-radius:999px;" +
      "margin:6px 0;background:rgba(74,222,128,.14);color:#4ade80;" +
      "border:1px solid rgba(74,222,128,.35)";
    var host = document.getElementById("page-dashboard");
    if (host) { host.insertBefore(b, host.firstChild); }
  }

  function isiKpi(rows) {
    var kartu = document.querySelectorAll("#page-dashboard .k-val");
    if (kartu.length >= 1) { kartu[0].textContent = String(rows.length); }
    if (kartu.length >= 2) { kartu[1].textContent = hitungSehat(rows) + "%"; }
  }

  function tarik() {
    fetch("/api/targets", { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) { throw new Error("http " + r.status); }
        return r.json();
      })
      .then(function (rows) {
        if (typeof targets !== "undefined") {
          targets.length = 0;
          rows.map(keBentukLokal).forEach(function (x) { targets.push(x); });
        }
        if (typeof renderTargets === "function") { renderTargets(); }
        isiKpi(rows);
        pasangPenanda(rows.length);
        console.log("[live] " + rows.length + " target dari API");
      })
      .catch(function (e) {
        console.warn("[live] gagal tarik data:", e);
        pasangPenanda(-1);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", tarik);
  } else {
    tarik();
  }
})();
