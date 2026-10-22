/* HESTIA - halaman Kredensial, Deployment, Konten dari tabel nyata */
(function () {
  var sel = "padding:7px 8px;border-bottom:1px solid #232833";
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }

  function baris(tb, item, kolom, kosong) {
    if (!tb) return;
    if (!item.length) {
      tb.innerHTML = '<tr><td colspan="' + kolom.length + '" style="' + sel
        + ';color:var(--muted)">' + kosong + "</td></tr>";
      return;
    }
    tb.innerHTML = item.map(function (r) {
      return "<tr>" + kolom.map(function (k) {
        var v = r[k];
        return '<td style="' + sel + '">' + (v === null || v === undefined || v === "" ? "—" : v)
          + "</td>";
      }).join("") + "</tr>";
    }).join("");
  }

  function muatSemua() {
    fetch("/api/kredensial").then(function (r) { return r.json(); }).then(function (d) {
      baris(document.getElementById("credBody"), d.item,
        ["target", "nama", "tipe", "level", "secret", "berlaku_sd"], "belum ada kredensial");
    }).catch(function (e) { lapor("kredensial-gagal", String(e)); });

    fetch("/api/deployment").then(function (r) { return r.json(); }).then(function (d) {
      baris(document.getElementById("deployBody"), d.item,
        ["waktu", "target", "path", "template", "status"], "belum ada deployment");
    }).catch(function (e) { lapor("deployment-gagal", String(e)); });

    fetch("/api/konten").then(function (r) { return r.json(); }).then(function (d) {
      baris(document.getElementById("kontenBody"), d.item,
        ["url", "target", "kata_kunci", "template", "status_indeks", "posisi"],
        "belum ada halaman konten");
      lapor("konten-diisi", "total=" + d.total);
    }).catch(function (e) { lapor("konten-gagal", String(e)); });
  }

  window.muatKonten = muatSemua;
  document.addEventListener("DOMContentLoaded", function () {
    muatSemua();
    setTimeout(muatSemua, 1200);
  });
})();
