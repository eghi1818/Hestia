/* HESTIA - halaman Konsol: jalankan aksi whitelist dari browser */
(function () {
  function $(id) { return document.getElementById(id); }
  var jobAktif = null, timer = null, urut = 0;

  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a) + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
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
