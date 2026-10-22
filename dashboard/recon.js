/* HESTIA - halaman Recon: antrean nyata + jalankan berurutan */
(function () {
  var jalan = false;
  var s = "padding:7px 8px;border-bottom:1px solid #232833";
  function $(id) { return document.getElementById(id); }
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }
  function progres(pct, teks) {
    var pr = $("reconProgress");
    if (pr) {
      if (pr.tagName === "PROGRESS") { pr.value = pct; pr.max = 100; }
      else { pr.style.width = pct + "%"; }
    }
    var st = $("queueStatus");
    if (st && teks) st.textContent = teks;
  }

  function isiAntrean() {
    fetch("/api/recon").then(function (r) { return r.json(); }).then(function (d) {
      var w = $("reconQueue");
      if (!w) return;
      var tb = (w.tagName === "TBODY");
      var isi = d.item.length ? d.item.map(function (x) {
        var kol = [x.waktu, x.target_id, x.http_status, (x.ms || 0) + " ms"];
        return tb
          ? "<tr>" + kol.map(function (v) { return '<td style="' + s + '">' + (v || "—") + "</td>"; }).join("") + "</tr>"
          : '<div style="display:flex;justify-content:space-between;padding:7px 8px;'
            + 'border-bottom:1px solid #232833;font-size:12px"><span>' + (kol[0] || "—")
            + "</span><b>" + (kol[2] || 0) + " · " + kol[3] + "</b></div>";
      }).join("") : (tb
        ? '<tr><td colspan="4" style="' + s + ';color:var(--muted)">belum ada recon</td></tr>'
        : '<div style="padding:10px;color:var(--muted);font-size:13px">belum ada recon</div>');
      w.innerHTML = isi;
      var st = $("queueStatus");
      if (st && !jalan) st.textContent = d.total + " baris riwayat";
    }).catch(function (e) { lapor("recon-daftar-gagal", String(e)); });
  }

  window.runReconQueue = function () {
    if (jalan) { if (window.toast) window.toast("antrean sedang berjalan"); return; }
    fetch("/api/targets").then(function (r) { return r.json(); }).then(function (ts) {
      if (!ts.length) { if (window.toast) window.toast("belum ada target"); return; }
      jalan = true;
      var i = 0;
      lapor("recon-antrean-mulai", "target=" + ts.length);
      function lanjut() {
        if (i >= ts.length) {
          jalan = false;
          progres(100, "selesai " + ts.length + " target");
          lapor("recon-antrean-selesai", "target=" + ts.length);
          if (window.toast) window.toast("antrean recon selesai");
          isiAntrean();
          return;
        }
        var t = ts[i++];
        progres(Math.round(100 * i / ts.length), "memeriksa " + i + " / " + ts.length + " — " + t.domain);
        fetch("/api/targets/" + t.id + "/recon", { method: "POST" })
          .then(function () { setTimeout(lanjut, 400); })
          .catch(function () { setTimeout(lanjut, 400); });
      }
      lanjut();
    }).catch(function (e) { lapor("recon-antrean-gagal", String(e)); });
  };

  document.addEventListener("DOMContentLoaded", function () { isiAntrean(); });
})();
