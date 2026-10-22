/* HESTIA - sambungkan tombol-tombol yang masih mati */
(function () {
  function $(id) { return document.getElementById(id); }
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }
  function kirim(url, isi, metode) {
    return fetch(url, {
      method: metode || "POST",
      headers: { "Content-Type": "application/json" },
      body: isi ? JSON.stringify(isi) : undefined
    }).then(function (r) { return r.json(); });
  }
  function hariIni() { return new Date().toISOString().slice(0, 10); }
  function pasang(kunci, fn, lewatJudul) {
    document.querySelectorAll("button").forEach(function (b) {
      if (b.dataset.aksi) return;
      var t = (b.textContent || "").trim();
      var j = b.getAttribute("title") || "";
      var cocok = lewatJudul ? (j === kunci) : (t.indexOf(kunci) >= 0);
      if (cocok) { b.dataset.aksi = "1"; b.addEventListener("click", fn); }
    });
  }

  function halamanBaru() {
    var url = prompt("URL halaman tamu:"); if (!url) return;
    var target = prompt("Target (domain):") || "";
    var kk = prompt("Kata kunci:") || "";
    kirim("/api/konten", { url: url, target: target, kata_kunci: kk, template: "artikel",
                           status_indeks: "menunggu", posisi: 0 })
      .then(function () { lapor("halaman-baru", url); if (window.toast) window.toast("halaman dicatat");
                          if (window.muatKonten) window.muatKonten(); });
  }
  function kanalAlert() {
    var k = prompt("Kanal alert (mis. email / slack):"); if (!k) return;
    kirim("/api/setelan", { kunci: "kanal", nilai: k })
      .then(function () { lapor("kanal-alert", k); if (window.toast) window.toast("kanal: " + k); });
  }
  function pindaiSekarang() {
    if (window.runReconQueue) window.runReconQueue();
    else if (window.toast) window.toast("antrean recon tidak ada");
  }
  function nodeBaru() {
    var dari = prompt("Dari (domain sumber):"); if (!dari) return;
    var ke = prompt("Ke (domain tujuan):"); if (!ke) return;
    kirim("/api/tautan", { dari: dari, ke: ke })
      .then(function () { lapor("node-baru", dari + "->" + ke);
                          if (window.toast) window.toast("node ditambahkan"); });
  }
  function filterLanjutan() {
    var s = prompt("Akhiran (go.id / desa.id / mil.id / ac.id / sch.id) — kosongkan untuk semua:", "go.id");
    if (s === null) return;
    var e = $("kandStatus");
    if (e) e.value = "";
    var ti = $("kandTanpaInfra"); if (ti) ti.checked = true;
    var tk = $("kandTanpaKosong"); if (tk) tk.checked = true;
    lapor("filter-lanjutan", "suffix=" + s);
    if (window.muatKandidat) window.muatKandidat();
    if (window.toast) window.toast(s ? ("saringan " + s) : "saringan semua akhiran");
  }
  function undang() {
    var n = prompt("Nama anggota:"); if (!n) return;
    var p = prompt("Peran (admin / editor / pengamat):", "pengamat") || "pengamat";
    kirim("/api/anggota", { nama: n, peran: p, ditambah: hariIni() })
      .then(function () { lapor("undang-anggota", n); if (window.toast) window.toast("diundang: " + n); });
  }
  function rotasi() {
    if (!confirm("Rotasi semua kredensial: masa berlaku diundur 1 tahun?")) return;
    kirim("/api/kredensial/rotasi", null).then(function (d) {
      lapor("rotasi-kredensial", JSON.stringify(d));
      if (window.toast) window.toast("rotasi: " + (d.diubah || 0) + " baris");
      if (window.muatKonten) window.muatKonten();
    });
  }
  function lihatAlert() {
    fetch("/api/monitoring").then(function (r) { return r.json(); }).then(function (d) {
      var teks = (d.alerts || []).slice(0, 6).map(function (a) {
        return "• " + a.domain + " — " + a.status + (a.http_status ? " " + a.http_status : "");
      }).join("\n");
      alert("Alert teratas:\n" + (teks || "(tidak ada)"));
      lapor("lihat-alert", String((d.alerts || []).length));
    });
  }
  function logDeploy() {
    fetch("/api/deployment").then(function (r) { return r.json(); }).then(function (d) {
      var teks = (d.item || []).slice(0, 8).map(function (x) {
        return "• " + x.waktu + "  " + x.target + "  " + (x.path || "");
      }).join("\n");
      alert("Log deployment:\n" + (teks || "(belum ada)"));
      lapor("log-deployment", String((d.item || []).length));
    });
  }
  function rollback() {
    fetch("/api/deployment").then(function (r) { return r.json(); }).then(function (d) {
      if (!d.item || !d.item.length) { if (window.toast) window.toast("belum ada deployment"); return; }
      var x = d.item[0];
      if (!confirm("Batalkan deployment terakhir?\n" + x.target + " " + (x.path || ""))) return;
      kirim("/api/deployment/" + x.id, null, "DELETE").then(function () {
        lapor("rollback", String(x.id));
        if (window.toast) window.toast("dibatalkan: " + x.target);
        if (window.muatKonten) window.muatKonten();
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    pasang("Halaman baru", halamanBaru);
    pasang("Kanal alert", kanalAlert);
    pasang("Pindai sekarang", pindaiSekarang);
    pasang("Node baru", nodeBaru);
    pasang("Filter lanjutan", filterLanjutan);
    pasang("Undang", undang);
    pasang("Rotasi", rotasi, true);
    pasang("Log", logDeploy, true);
    pasang("Rollback", rollback, true);
    pasang("Lihat", lihatAlert);
  });
})();
