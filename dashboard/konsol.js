/* HESTIA - halaman Konsol: jalankan aksi whitelist dari browser */
(function () {
  function $(id) { return document.getElementById(id); }
  var jobAktif = null, timer = null, urut = 0;

  function lapor(a, r) {
    var q = "?peristiwa=" + encodeURIComponent(a) + "&rincian=" + encodeURIComponent(r || "");
    var hdr = { "Content-Type": "application/json" };
    var badan = JSON.stringify({ peristiwa: a, rincian: r || "" });
    try {
      fetch("/api/clientlog" + q, { method: "POST", headers: hdr, body: badan }).then(function (x) {
        if (!x.ok) { fetch("/api/clientlog" + q).catch(function () {}); }
      }).catch(function () { fetch("/api/clientlog" + q).catch(function () {}); });
    } catch (e) {
      fetch("/api/clientlog" + q).catch(function () {});
    }
  }
  function siap(fn) { if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn); else fn(); }

  function isiAksi() {
    fetch("/api/konsol/aksi").then(function (r) { return r.json(); }).then(function (d) {
      var s = $("konsolAksi"); if (!s) return;
      s.innerHTML = "";
      (d.aksi || []).forEach(function (a) {
        var o = document.createElement("option");
        o.value = a.nama;
        o.textContent = a.nama + (a.menulis ? "  (menulis)" : "");
        s.appendChild(o);
      });
      if (!s.options.length) {
        var o2 = document.createElement("option"); o2.value = ""; o2.textContent = "(kosong)"; s.appendChild(o2);
      }
    });
  }

  function tampilLog(sejak) {
    if (!jobAktif) return;
    fetch("/api/job/" + jobAktif + "/log?sejak=" + sejak).then(function (r) { return r.json(); }).then(function (d) {
      var el = $("konsolLog"); if (!el) return;
      (d.baris || []).forEach(function (b) {
        urut = Math.max(urut, b.urutan);
        var w = document.createElement("div");
        w.className = "konsol-baris konsol-" + b.aliran;
        w.textContent = "[" + b.aliran + "] " + (b.baris || "");
        el.appendChild(w);
      });
      el.scrollTop = el.scrollHeight;
    });
  }

  function pantau() {
    if (!jobAktif) return;
    fetch("/api/job/" + jobAktif).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) return;
      var j = d.job, s = $("konsolStatus");
      if (j.status === "jalan") { if (s) s.textContent = "job " + j.r_nomor + " - jalan"; return; }
      clearInterval(timer); timer = null;
      if (s) s.textContent = "job " + j.r_nomor + " selesai: " + j.status;
      if ($("konsolBatal")) $("konsolBatal").disabled = true;
      lapor("konsol-selesai", j.r_nomor + "=" + j.status);
    });
  }

  function jalankan() {
    var a = $("konsolAksi"), dom = $("konsolDomain"), ex = $("konsolExtra"), pk = $("konsolPaksa");
    var badan = { aksi: a ? a.value : "" };
    if (dom && dom.value.trim()) badan.domain = dom.value.trim();
    if (ex && ex.value.trim()) badan.extra = ex.value.trim();
    if (pk && pk.checked) badan.paksa = 1;
    fetch("/api/konsol/jalankan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(badan) })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var s = $("konsolStatus"), el = $("konsolLog");
        if (!d.ok) { if (s) s.textContent = "ditolak: " + d.sebab; lapor("konsol-ditolak", d.sebab || ""); return; }
        jobAktif = d.job_id; urut = 0;
        if (el) el.innerHTML = "";
        if (s) s.textContent = "job " + d.r_nomor + " jalan";
        if ($("konsolBatal")) $("konsolBatal").disabled = false;
        lapor("konsol-jalankan", d.r_nomor + " " + (d.argv || []).join(" "));
        if (timer) clearInterval(timer);
        timer = setInterval(function () { tampilLog(urut); pantau(); }, 900);
      });
  }

  function batal() {
    if (!jobAktif) return;
    fetch("/api/job/" + jobAktif + "/batal", { method: "POST" }).then(function () { lapor("konsol-batal", String(jobAktif)); });
  }

  siap(function () {
    if ($("konsolJalankan")) $("konsolJalankan").addEventListener("click", jalankan);
    if ($("konsolBatal")) $("konsolBatal").addEventListener("click", batal);
    if ($("konsolSegarkan")) $("konsolSegarkan").addEventListener("click", function () { isiAksi(); lapor("konsol-segarkan", ""); });
    isiAksi();
    lapor("konsol-dimuat", "halaman konsol");
  });
})();

/* HESTIA - panel Kunci di halaman Konsol */
(function () {
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? "" : s).replace(/[<>&]/g, function (c) { return { "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]; }); }
  var ujiTerakhir = {};

  function isiUji() {
    return fetch("/api/kredensial-uji").then(function (r) { return r.json(); }).then(function (d) {
      ujiTerakhir = {};
      (d.item || []).forEach(function (u) { if (!ujiTerakhir[u.kredensial_id]) ujiTerakhir[u.kredensial_id] = u; });
    }).catch(function () {});
  }

  function barisKunci(item) {
    var u = ujiTerakhir[item.id];
    var tr = document.createElement("tr");
    tr.innerHTML = "<td>" + esc(item.target) + "</td><td>" + esc(item.nama) + "</td><td>" + esc(item.tipe) + "</td><td>" + esc(item.level) + "</td>"
      + "<td>" + (u ? esc(u.hasil) + " (" + esc(u.metode) + ")" : "belum diuji") + "</td>"
      + "<td><button class=\"btn btn-sm\" data-uji=\"" + item.id + "\">Uji</button> "
      + "<button class=\"btn btn-ghost btn-sm\" data-hapus=\"" + item.id + "\">Hapus</button></td>";
    return tr;
  }

  function isiKunci() {
    return isiUji().then(function () { return fetch("/api/kredensial"); }).then(function (r) { return r.json(); }).then(function (d) {
      var b = $("kunciBody"); if (!b) return;
      b.innerHTML = "";
      (d.item || []).forEach(function (it) { b.appendChild(barisKunci(it)); });
      if (!b.children.length) {
        var tr = document.createElement("tr");
        tr.innerHTML = "<td colspan=\"6\" style=\"opacity:.6\">belum ada kunci</td>";
        b.appendChild(tr);
      }
      var s = $("kunciStatus"); if (s) s.textContent = (d.item || []).length + " kunci";
    }).catch(function (e) { var s = $("kunciStatus"); if (s) s.textContent = "galat: " + e; });
  }

  function uji(kid) {
    var s = $("kunciStatus"); if (s) s.textContent = "menguji #" + kid + " ...";
    fetch("/api/kredensial/" + kid + "/uji", { method: "POST" }).then(function (r) { return r.json(); }).then(function (d) {
      if (s) s.textContent = "#" + kid + " " + (d.hasil || "gagal") + " - " + (d.pesan || d.sebab || "");
      isiKunci();
    });
  }

  function hapus(kid) { fetch("/api/kredensial/" + kid, { method: "DELETE" }).then(function () { isiKunci(); }); }

  function tambah() {
    var t = $("kunciTarget"), n = $("kunciNama"), tp = $("kunciTipe"), sc = $("kunciSecret"), lv = $("kunciLevel");
    fetch("/api/kredensial", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target: t ? t.value.trim() : "", nama: n ? n.value.trim() : "", tipe: tp ? tp.value.trim() : "", level: lv ? lv.value.trim() : "", secret: sc ? sc.value : "" })
    }).then(function () { if (sc) sc.value = ""; isiKunci(); });
  }

  function siap(fn) { if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn); else fn(); }
  siap(function () {
    var b = $("kunciBody");
    if (!b) return;
    b.addEventListener("click", function (e) {
      var a = e.target.getAttribute && e.target.getAttribute("data-uji");
      if (a) { uji(a); return; }
      var h = e.target.getAttribute && e.target.getAttribute("data-hapus");
      if (h) { hapus(h); }
    });
    if ($("kunciTambah")) $("kunciTambah").addEventListener("click", tambah);
    if ($("kunciSegarkan")) $("kunciSegarkan").addEventListener("click", isiKunci);
    isiKunci();
  });
})();
