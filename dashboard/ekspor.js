/* HESTIA - tombol Ekspor: unduh CSV kandidat bersih */
(function () {
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }
  function eksporCsv() {
    var a = document.createElement("a");
    a.href = "/api/kandidat.csv";
    a.download = "kandidat.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    lapor("ekspor-csv", "kandidat");
    if (window.toast) window.toast("kandidat.csv diunduh");
  }
  window.eksporCsv = eksporCsv;

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("button").forEach(function (b) {
      if (/ekspor|csv/i.test(b.textContent) && !b.dataset.adaEkspor) {
        b.dataset.adaEkspor = "1";
        b.addEventListener("click", eksporCsv);
      }
    });
  });
})();
