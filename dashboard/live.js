/* live.js - sambungan Hestia ke API.
   Menempel dari luar: index.html milik desain tidak dibongkar.
   Dua tugas: tampilkan data nyata, dan simpan target baru ke basis data.

   Catatan penting: tombol "Simpan target" TIDAK punya id - ia memakai
   onclick="addTarget()". Karena addTarget adalah function declaration di
   skrip klasik, ia hidup di window dan bisa ditimpa langsung. */
(function () {
  "use strict";

  var LABEL = {
    kandidat: "Kandidat", dianalisis: "Dianalisis", aktif: "Aktif",
    rusak: "Rusak", dibersihkan: "Dibersihkan", nonaktif: "Nonaktif"
  };

  function judul(s) { return LABEL[s] || s; }

  function val(id) {
    var e = document.getElementById(id);
    return e && typeof e.value === "string" ? e.value.trim() : "";
  }

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

  function kabar(teks) {
    if (typeof toast === "function") { toast(teks); }
    else { console.log("[live] " + teks); }
  }

  function pasangPenanda(teks, merah) {
    var lama = document.getElementById("liveBadge");
    if (lama) { lama.remove(); }
    var b = document.createElement("div");
    b.id = "liveBadge";
    b.textContent = teks;
    b.style.cssText = "display:inline-block;font-size:11px;padding:3px 9px;border-radius:999px;" +
      "margin:6px 0;border:1px solid " + (merah ? "rgba(248,113,113,.5)" : "rgba(74,222,128,.35)") + ";" +
      "color:" + (merah ? "#fca5a5" : "#4ade80") + ";background:rgba(127,127,127,.10)";
    var host = document.getElementById("page-dashboard");
    if (host) { host.insertBefore(b, host.firstChild); }
  }

  function isiKpi(rows) {
    var kartu = document.querySelectorAll("#page-dashboard .k-val");
    if (kartu.length >= 1) { kartu[0].textContent = String(rows.length); }
    if (kartu.length >= 2) { kartu[1].textContent = hitungSehat(rows) + "%"; }
  }

  function tarik() {
    return fetch("/api/targets", { cache: "no-store" })
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
        pasangPenanda("data nyata - " + rows.length + " target");
        return rows;
      })
      .catch(function (e) {
        console.warn("[live] gagal tarik data:", e);
        pasangPenanda("API tidak terjangkau", true);
      });
  }

  function simpan() {
    var domain = val("fDomain");
    if (!domain) { kabar("Domain masih kosong"); return; }
    var tipe = val("fType") || "lain";
    var badan = { domain: domain, tipe: tipe, owner: val("fOwner") };

    fetch("/api/targets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(badan)
    })
      .then(function (r) {
        if (r.status === 409) { throw new Error("domain sudah terdaftar"); }
        if (!r.ok) { throw new Error("http " + r.status); }
        return r.json();
      })
      .then(function () {
        if (typeof closeModal === "function") { closeModal("modalTarget"); }
        var fd = document.getElementById("fDomain");
        if (fd) { fd.value = ""; }
        kabar("Target tersimpan ke basis data");
        return tarik();
      })
      .catch(function (e) {
        console.warn("[live] gagal simpan:", e);
        kabar("Gagal simpan: " + e.message);
      });
  }

  window.__hestia_refresh = tarik;
  window.__hestia_simpan = simpan;
  window.addTarget = simpan;
  console.log("[live] window.addTarget ditimpa");

  function mulai() { tarik(); }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mulai);
  } else {
    mulai();
  }
})();
