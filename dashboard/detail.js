/* HESTIA - halaman detail target dari data nyata */
(function () {
  var idTarget = null;
  var s = "padding:7px 8px;border-bottom:1px solid #232833";
  function $(id) { return document.getElementById(id); }
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }
  function kv(el, baris) {
    if (!el) return;
    el.innerHTML = baris.map(function (b) {
      return '<div style="display:flex;justify-content:space-between;padding:6px 0;'
        + 'border-bottom:1px solid #232833;font-size:13px"><span>' + b[0]
        + '</span><b>' + (b[1] === null || b[1] === undefined || b[1] === "" ? "—" : b[1])
        + "</b></div>";
    }).join("");
  }

  function isiDetail() {
    if (idTarget === null) return;
    fetch("/api/targets").then(function (r) { return r.json(); }).then(function (ts) {
      var t = null, i;
      for (i = 0; i < ts.length; i++) { if (String(ts[i].id) === String(idTarget)) t = ts[i]; }
      if (!t) return;
      kv($("detailKv"), [["Domain", t.domain], ["Pemilik", t.owner], ["Tipe", t.tipe],
                         ["Status", t.status], ["Dibuat", t.created_at]]);

      fetch("/api/targets/" + idTarget + "/recon").then(function (r) { return r.json(); })
        .then(function (d) {
          var item = d.item || [];
          kv($("detailHealth"), item.length ? [
            ["Cek terakhir", item[0].waktu], ["HTTP", item[0].http_status],
            ["Server", item[0].server || "—"], ["Latensi", (item[0].ms || 0) + " ms"],
            ["Jumlah cek", item.length]
          ] : [["Cek terakhir", "belum ada"], ["HTTP", "—"], ["Server", "—"], ["Latensi", "—"]]);
          kv($("fpKv"), item.length ? [
            ["Server", item[0].server || "—"], ["Content-Type", item[0].content_type || "—"],
            ["Redirect", item[0].redirect || "—"], ["Judul", item[0].judul || "—"]
          ] : [["Server", "belum ada recon"]]);
          var dc = $("detailChecks");
          if (dc) dc.innerHTML = item.length ? item.map(function (x) {
            return '<div style="display:flex;justify-content:space-between;padding:6px 0;'
              + 'border-bottom:1px solid #232833;font-size:12px"><span>' + x.waktu
              + '</span><b>' + (x.http_status || 0) + " · " + (x.ms || 0) + " ms</b></div>";
          }).join("") : '<div style="color:var(--muted);font-size:13px">belum ada cek</div>';
          var dt = $("detailTimeline");
          if (dt) dt.innerHTML = item.map(function (x) {
            return '<div class="tl-item"><div class="tl-title">Recon ' + (x.http_status || 0)
              + '</div><div class="tl-meta">' + x.waktu + " · " + (x.catatan || "ok") + "</div></div>";
          }).join("");
        }).catch(function (e) { lapor("detail-recon-gagal", String(e)); });

      fetch("/api/kredensial?target=" + encodeURIComponent(t.domain))
        .then(function (r) { return r.json(); }).then(function (d) {
          var tb = $("detailCredBody");
          if (!tb) return;
          tb.innerHTML = d.item.length ? d.item.map(function (c) {
            return "<tr>" + ["target", "nama", "tipe", "level", "secret", "berlaku_sd"].map(function (k) {
              return '<td style="' + s + '">' + (c[k] || "—") + "</td>";
            }).join("") + '<td style="' + s + '"></td></tr>';
          }).join("") : '<tr><td colspan="7" style="' + s
            + ';color:var(--muted)">belum ada kredensial untuk target ini</td></tr>';
        }).catch(function (e) { lapor("detail-cred-gagal", String(e)); });

      fetch("/api/konten?target=" + encodeURIComponent(t.domain))
        .then(function (r) { return r.json(); }).then(function (d) {
          var tb = $("detailPageBody");
          if (!tb) return;
          tb.innerHTML = d.item.length ? d.item.map(function (k) {
            return "<tr>" + [k.url, k.kata_kunci, k.status_indeks].map(function (v) {
              return '<td style="' + s + '">' + (v || "—") + "</td>";
            }).join("") + '<td style="' + s + '">—</td></tr>';
          }).join("") : '<tr><td colspan="4" style="' + s
            + ';color:var(--muted)">belum ada halaman tamu</td></tr>';
        }).catch(function (e) { lapor("detail-konten-gagal", String(e)); });

      lapor("detail-diisi", t.domain);
    }).catch(function (e) { lapor("detail-gagal", String(e)); });
  }

  window.jalankanRecon = function () {
    if (idTarget === null) { if (window.toast) window.toast("buka target dulu"); return; }
    if (window.toast) window.toast("recon berjalan...");
    fetch("/api/targets/" + idTarget + "/recon", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        lapor("recon-jalan", "target=" + idTarget + " http=" + (d.http_status || 0));
        if (window.toast) window.toast("recon selesai");
        isiDetail();
      })
      .catch(function (e) { lapor("recon-gagal", String(e)); });
  };

  var asli = window.bukaDetail;
  window.bukaDetail = function (id) {
    if (typeof asli === "function") asli(id);
    idTarget = (id === undefined ? idTarget : id);
    setTimeout(isiDetail, 80);
  };

  document.addEventListener("DOMContentLoaded", function () { isiDetail(); });
})();
