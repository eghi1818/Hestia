/* HESTIA - ikhtisar: kartu KPI + diagram dari data nyata */
(function () {
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }

  function gambarBar(id, data, warna) {
    var svg = document.getElementById(id);
    if (!svg || !data.length) return;
    var W = 560, H = 240, pad = 34;
    var maks = Math.max.apply(null, data.map(function (d) { return d.n; }).concat([1]));
    var langkah = (W - pad * 2) / data.length;
    var lebar = Math.min(langkah * 0.6, 46);
    var out = "";
    data.forEach(function (d, i) {
      var h = (H - pad * 2) * (d.n / maks);
      var x = pad + langkah * i + (langkah - lebar) / 2;
      var y = H - pad - h;
      out += '<rect x="' + x + '" y="' + y + '" width="' + lebar + '" height="' + Math.max(h, 1)
        + '" fill="' + warna[i % warna.length] + '" rx="4"></rect>'
        + '<text x="' + (x + lebar / 2) + '" y="' + (H - pad + 15)
        + '" fill="#8b93a7" font-size="11" text-anchor="middle">' + d.label + '</text>'
        + '<text x="' + (x + lebar / 2) + '" y="' + (y - 5)
        + '" fill="#e6e8ee" font-size="11" text-anchor="middle">' + d.n + '</text>';
    });
    svg.innerHTML = out;
  }

  function isiIkhtisar() {
    Promise.all([
      fetch("/api/targets").then(function (r) { return r.json(); }),
      fetch("/api/kandidat/ringkas").then(function (r) { return r.json(); })
    ]).then(function (res) {
      var tg = res[0] || [], rk = res[1] || {};
      var kartu = document.querySelectorAll("#page-dashboard .k-val");
      if (kartu.length >= 4) {
        kartu[0].textContent = tg.length;
        kartu[1].textContent = rk.bersih || 0;
        kartu[2].textContent = rk.hidup || 0;
        kartu[3].textContent = rk.kosong || 0;
      }
      var tr = document.querySelectorAll("#page-dashboard .k-trend");
      if (tr.length >= 4) {
        tr[0].textContent = "— " + tg.length;
        tr[1].textContent = "infra " + (rk.infra || 0);
        tr[2].textContent = "dijaga " + (rk.dijaga || 0);
        tr[3].textContent = "panel " + (rk.panel || 0);
      }
      var bs = document.getElementById("ikhtisarBersih");
      if (bs) bs.textContent = (rk.bersih || 0) + " bersih";
      var st = {};
      (rk.per_suffix_status || []).forEach(function (r) { st[r.status] = (st[r.status] || 0) + r.n; });
      gambarBar("barChart", [
        { label: "hidup", n: st.hidup || 0 }, { label: "dijaga", n: st.dijaga || 0 },
        { label: "alih", n: st.alih || 0 }, { label: "galat", n: st.galat || 0 },
        { label: "mati", n: st.mati || 0 }, { label: "baru", n: st.baru || 0 }
      ], ["var(--green)", "var(--yellow)", "var(--blue)", "#f4a259", "var(--red)", "var(--gray)"]);
      var per = {};
      (rk.per_suffix_status || []).forEach(function (r) { per[r.suffix] = (per[r.suffix] || 0) + r.n; });
      gambarBar("lineChart",
        Object.keys(per).sort().map(function (s2) { return { label: s2, n: per[s2] }; }),
        ["var(--blue)", "var(--green)", "var(--yellow)", "var(--red)", "var(--gray)"]);
      lapor("ikhtisar-diisi", "target=" + tg.length + " kandidat=" + (rk.total || 0));
    }).catch(function (e) { lapor("ikhtisar-gagal", String(e)); });
  }

  window.isiIkhtisar = isiIkhtisar;
  document.addEventListener("DOMContentLoaded", function () {
    isiIkhtisar();
    setTimeout(isiIkhtisar, 1400);
  });
})();
