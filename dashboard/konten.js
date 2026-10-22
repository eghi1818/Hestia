/* HESTIA - Kredensial / Deployment / Konten: tampil, tambah, hapus */
(function () {
  var sel = "padding:7px 8px;border-bottom:1px solid #232833";
  function $(id) { return document.getElementById(id); }
  function nilai(id) { var e = $(id); return e ? e.value : ""; }
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }
  function hariIni() { return new Date().toISOString().slice(0, 10); }

  function baris(tb, item, kolom, tabel, kosong) {
    if (!tb) return;
    if (!item.length) {
      tb.innerHTML = '<tr><td colspan="' + (kolom.length + 1) + '" style="' + sel
        + ';color:var(--muted)">' + kosong + "</td></tr>";
      return;
    }
    tb.innerHTML = item.map(function (r) {
      return "<tr>" + kolom.map(function (k) {
        var v = r[k];
        return '<td style="' + sel + '">' + (v === null || v === undefined || v === "" ? "—" : v)
          + "</td>";
      }).join("") + '<td style="' + sel + ';text-align:right">'
        + (tabel === "konten"
            ? '<button class="btn btn-ghost btn-sm" onclick="tandaiIndeks(' + r.id
              + ')">indeks</button> '
            : "")
        + '<button class="btn btn-ghost btn-sm" onclick="hapusBaris(\'' + tabel + "'," + r.id
        + ')">hapus</button></td></tr>';
    }).join("");
  }

  function muatSemua() {
    fetch("/api/kredensial").then(function (r) { return r.json(); }).then(function (d) {
      var kol = ["target", "nama", "tipe", "level", "secret", "berlaku_sd"];
      baris($("credBody"), d.item, kol, "kredensial", "belum ada kredensial");
      baris($("detailCredBody"), d.item, kol, "kredensial", "belum ada kredensial");
      var batas = new Date(Date.now() + 90 * 864e5).toISOString().slice(0, 10);
      var rot = 0;
      d.item.forEach(function (r) { if (!r.berlaku_sd || r.berlaku_sd <= batas) rot++; });
      var el = $("credRotasi"); if (el) el.textContent = rot;
    }).catch(function (e) { lapor("kredensial-gagal", String(e)); });

    fetch("/api/deployment").then(function (r) { return r.json(); }).then(function (d) {
      baris($("deployBody"), d.item, ["waktu", "target", "path", "template", "status"],
            "deployment", "belum ada deployment");
    }).catch(function (e) { lapor("deployment-gagal", String(e)); });

    fetch("/api/konten").then(function (r) { return r.json(); }).then(function (d) {
      baris($("kontenBody"), d.item,
            ["url", "target", "kata_kunci", "template", "status_indeks", "posisi"],
            "konten", "belum ada halaman konten");
    }).catch(function (e) { lapor("konten-gagal", String(e)); });
  }

  function kirim(alamat, isi, aksi) {
    return fetch(alamat, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(isi)
    }).then(function (r) {
      if (r.status !== 200) throw new Error("http " + r.status);
      lapor(aksi, JSON.stringify(isi).slice(0, 120));
      if (window.toast) window.toast(aksi.replace(/-/g, " "));
      if (window.closeModal) window.closeModal(aksi.indexOf("kredensial") >= 0 ? "modalCred" : "modalDeploy");
      muatSemua();
    }).catch(function (e) { lapor(aksi + "-gagal", String(e)); });
  }

  window.addCred = function () {
    var t = nilai("cTarget");
    if (!t) { if (window.toast) window.toast("pilih target dulu"); return; }
    kirim("/api/kredensial", {
      target: t, nama: nilai("cName"), tipe: nilai("cType"),
      level: nilai("cLevel"), secret: nilai("cSecret"),
      berlaku_sd: nilai("cValid"), created_at: hariIni()
    }, "kredensial-ditambah");
  };

  window.doDeploy = function () {
    var t = nilai("dTarget"), p = nilai("dPath");
    if (!t) { if (window.toast) window.toast("pilih target dulu"); return; }
    var cat = document.querySelector("#modalDeploy .modal-body input:not([id])");
    var alamat = /^https?:\/\//i.test(p) ? p : (t + p);
    kirim("/api/deployment", {
      waktu: hariIni(), target: t, path: p, template: nilai("dTpl"),
      status: "terpasang" + (cat && cat.value ? " — " + cat.value : "")
    }, "deployment-ditambah").then(function () {
      kirim("/api/konten", {
        url: alamat, target: t, kata_kunci: "", template: nilai("dTpl"),
        status_indeks: "menunggu", posisi: 0
      }, "konten-ditambah");
    });
  };

  window.tandaiIndeks = function (id) {
    fetch("/api/konten/" + id + "/indeks?nilai=terindeks", { method: "POST" })
      .then(function () { lapor("konten-terindeks", String(id));
                          if (window.toast) window.toast("ditandai terindeks"); muatSemua(); });
  };

  window.hapusBaris = function (tabel, id) {
    fetch("/api/" + tabel + "/" + id, { method: "DELETE" }).then(function () {
      lapor("hapus-" + tabel, String(id));
      muatSemua();
    }).catch(function (e) { lapor("hapus-gagal", String(e)); });
  };

  window.muatKonten = muatSemua;

  var asli = window.openModal;
  window.openModal = function (id) {
    if (typeof asli === "function") asli(id);
    if (id === "modalDeploy") {
      fetch("/api/targets").then(function (r) { return r.json(); }).then(function (t) {
        var e = $("dTarget");
        if (e) e.innerHTML = t.map(function (x) { return "<option>" + x.domain + "</option>"; }).join("");
      });
    }
  };

  document.addEventListener("DOMContentLoaded", function () {
    muatSemua();
    setTimeout(muatSemua, 1200);
  });
})();
