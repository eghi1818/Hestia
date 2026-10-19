/* live.js - sambungan Hestia ke API.
   Menempel dari luar: index.html milik desain tidak dibongkar.

   Tiga tugas:
     1. tampilkan data nyata dari /api/targets
     2. simpan target baru lewat POST /api/targets
     3. lapor balik ke /api/clientlog supaya bukti bisa dibaca dari terminal

   Catatan: tombol Simpan target tidak punya id, ia memakai onclick="addTarget()".
   Karena addTarget adalah function declaration di skrip klasik, ia hidup di window
   dan bisa ditimpa langsung. */
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

  function lapor(peristiwa, rincian) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(peristiwa) +
            "&rincian=" + encodeURIComponent(rincian || ""), { method: "POST" })
        .catch(function () {});
    } catch (e) { /* jangan ganggu tampilan */ }
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
        lapor("dimuat", "target=" + rows.length + " badge=ada");
        return rows;
      })
      .catch(function (e) {
        console.warn("[live] gagal tarik data:", e);
        pasangPenanda("API tidak terjangkau", true);
        lapor("gagal-muat", e.message);
      });
  }

  function simpan() {
    var domain = val("fDomain");
    if (!domain) { kabar("Domain masih kosong"); lapor("kosong", "domain kosong"); return; }
    var badan = {
      domain: domain,
      tipe: val("fType") || "lain",
      owner: val("fOwner"),
      tags: val("fTags"),
      catatan: val("fNote")
    };

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
        lapor("tersimpan", badan.domain);
        return tarik();
      })
      .catch(function (e) {
        console.warn("[live] gagal simpan:", e);
        kabar("Gagal simpan: " + e.message);
        lapor("gagal-simpan", badan.domain + " :: " + e.message);
      });
  }

  // --- perekam: catat klik supaya kita tidak menebak ---
  document.addEventListener("click", function (ev) {
    var el = ev.target;
    while (el && el.tagName !== "BUTTON" && el.tagName !== "A") { el = el.parentElement; }
    if (!el) { return; }
    var teks = (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40);
    if (/tambah|simpan|target/i.test(teks)) { lapor("klik", teks); }
  }, true);
  window.__hestia_klik = true;

  if (typeof window.openModal === "function" && !window.__hestia_openModal) {
    var _bukaAsli = window.openModal;
    window.openModal = function () {
      lapor("modal-dibuka", String(arguments[0] || ""));
      return _bukaAsli.apply(this, arguments);
    };
    window.__hestia_openModal = true;
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

  /* --- tab Kandidat: baca hasil sapuan --- */
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }

  function muatKandidat() {
    var body = document.getElementById("kandBody");
    if (!body) return;
    var q = val("kandCari"), st = val("kandStatus");
    var url = "/api/kandidat?limit=200";
    if (q) url += "&q=" + encodeURIComponent(q);
    if (st) url += "&status=" + encodeURIComponent(st);
    body.innerHTML = '<tr><td colspan="7" style="padding:10px;color:var(--muted)">memuat...</td></tr>';
    fetch(url).then(function (r) { return r.json(); }).then(function (d) {
      var info = document.getElementById("kandInfo");
      if (info) info.textContent = "menampilkan " + d.item.length + " dari " + d.total + " kandidat";
      var nb = document.getElementById("navKandCount");
      if (nb) nb.textContent = d.total;
      if (!d.item.length) {
        body.innerHTML = '<tr><td colspan="7" style="padding:10px;color:var(--muted)">belum ada kandidat</td></tr>';
        return;
      }
      var sel = "padding:7px 8px;border-bottom:1px solid #232833";
      body.innerHTML = d.item.map(function (k) {
        return "<tr>"
          + '<td style="' + sel + '">' + k.domain + "</td>"
          + '<td style="' + sel + '">' + k.suffix + "</td>"
          + '<td style="' + sel + '">' + (k.jenis || "-") + "</td>"
          + '<td style="' + sel + '">' + k.status + "</td>"
          + '<td style="' + sel + '">' + (k.http_status || "-") + "</td>"
          + '<td style="' + sel + '">' + k.skor + "</td>"
          + '<td style="' + sel + '">' + (k.waf || "-") + "</td>"
          + "</tr>";
      }).join("");
      lapor("kandidat-dimuat", "total=" + d.total);
    }).catch(function (e) {
      body.innerHTML = '<tr><td colspan="7" style="padding:10px;color:var(--red)">gagal: ' + e + "</td></tr>";
    });
  }
  window.muatKandidat = muatKandidat;
  document.addEventListener("DOMContentLoaded", function () {
    var n = document.querySelector('[data-page="kandidat"]');
    if (n) n.addEventListener("click", muatKandidat);
  });

})();
