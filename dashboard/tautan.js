/* HESTIA - halaman Laporan + Backlink dari data tautan nyata */
(function () {
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }

  function isiLaporan() {
    fetch("/api/tautan/ringkas").then(function (r) { return r.json(); }).then(function (d) {
      var kartu = document.querySelectorAll("#page-laporan .k-val");
      if (kartu.length >= 4) {
        kartu[0].innerHTML = d.penerima
          + ' <span style="font-size:13px;color:var(--muted)">/ ' + d.kandidat + "</span>";
        kartu[1].textContent = d.total;
        kartu[2].textContent = d.sumber;
        kartu[3].textContent = d.penerima;
      }
      var wadah = document.getElementById("opsMetrics");
      if (wadah) {
        var baris = [
          ["Tautan tercatat", d.total],
          ["Domain sumber", d.sumber],
          ["Domain penerima", d.penerima],
          ["Kandidat di basis", d.kandidat],
        ];
        wadah.innerHTML = baris.map(function (b) {
          return '<div style="display:flex;justify-content:space-between;padding:8px 0;'
            + 'border-bottom:1px solid #232833;font-size:13px">'
            + "<span>" + b[0] + '</span><b>' + b[1] + "</b></div>";
        }).join("");
      }
      var tb = document.getElementById("backlinkBody");
      if (tb) {
        tb.innerHTML = (d.teratas || []).map(function (t) {
          var sel = "padding:7px 8px;border-bottom:1px solid #232833";
          return "<tr>"
            + '<td style="' + sel + '">' + t.ke + "</td>"
            + '<td style="' + sel + '">1</td>'
            + '<td style="' + sel + '">otomatis</td>'
            + '<td style="' + sel + '">' + t.ke + "</td>"
            + '<td style="' + sel + '">' + t.n + " tautan masuk</td>"
            + '<td style="' + sel + '">—</td>'
            + "</tr>";
        }).join("");
      }
      lapor("tautan-diisi", "total=" + d.total + " penerima=" + d.penerima);
    }).catch(function (e) { lapor("tautan-gagal", String(e)); });
  }

  window.isiLaporan = isiLaporan;
  document.addEventListener("DOMContentLoaded", function () {
    isiLaporan();
    setTimeout(isiLaporan, 1200);
  });
})();
