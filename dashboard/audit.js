/* HESTIA - halaman Audit Log + Monitoring dari data nyata */
(function () {
  function lapor(a, r) {
    try {
      fetch("/api/clientlog?peristiwa=" + encodeURIComponent(a)
            + "&rincian=" + encodeURIComponent(r || ""), { method: "POST" });
    } catch (e) {}
  }
  var sel = "padding:7px 8px;border-bottom:1px solid #232833";

  function isiAudit() {
    fetch("/api/audit?" + kueriAudit()).then(function (r) { return r.json(); }).then(function (d) {
      var tb = document.getElementById("auditBody");
      if (!tb) return;
      if (!d.item.length) {
        tb.innerHTML = '<tr><td colspan="4" style="' + sel + '">belum ada peristiwa</td></tr>';
        return;
      }
      tb.innerHTML = d.item.map(function (a) {
        return "<tr>"
          + '<td style="' + sel + '">' + (a.waktu || "") + "</td>"
          + '<td style="' + sel + '">peramban</td>'
          + '<td style="' + sel + '">' + a.peristiwa + "</td>"
          + '<td style="' + sel + '">' + (a.rincian || "—") + "</td>"
          + "</tr>";
      }).join("");
      lapor("audit-diisi", "total=" + d.total);
    }).catch(function (e) { lapor("audit-gagal", String(e)); });
  }

  function isiMonitoring() {
    fetch("/api/monitoring").then(function (r) { return r.json(); }).then(function (d) {
      var wa = document.getElementById("monitorAlerts");
      if (wa) {
        wa.innerHTML = (d.alerts || []).length ? d.alerts.map(function (a) {
          return '<div style="display:flex;justify-content:space-between;padding:8px 12px;'
            + 'border-bottom:1px solid #232833;font-size:13px">'
            + "<span>" + a.domain + "</span>"
            + '<span style="color:var(--muted)">' + a.status
            + (a.http_status ? " " + a.http_status : "") + "</span></div>";
        }).join("") : '<div style="padding:12px;color:var(--muted);font-size:13px">tidak ada alert</div>';
      }
      var wl = document.getElementById("latencyList");
      if (wl) {
        wl.innerHTML = (d.kesehatan || []).map(function (k) {
          var pct = k.total ? Math.round(100 * k.baik / k.total) : 0;
          return '<div style="padding:8px 12px;border-bottom:1px solid #232833;font-size:13px">'
            + '<div style="display:flex;justify-content:space-between"><span>' + k.suffix
            + '</span><span style="color:var(--muted)">' + k.baik + "/" + k.total
            + "</span></div>"
            + '<div style="height:6px;background:#232833;border-radius:3px;margin-top:6px">'
            + '<div style="height:6px;width:' + pct + '%;background:var(--green);border-radius:3px">'
            + "</div></div></div>";
        }).join("");
      }
      var cb = document.getElementById("checkBody");
      if (cb) {
        cb.innerHTML = (d.riwayat || []).map(function (r2) {
          return "<tr>"
            + '<td style="' + sel + '">' + (r2.diperiksa_at || "") + "</td>"
            + '<td style="' + sel + '">' + r2.domain + "</td>"
            + '<td style="' + sel + '">HTTP</td>'
            + '<td style="' + sel + '">' + r2.status + (r2.http_status ? " " + r2.http_status : "") + "</td>"
            + '<td style="' + sel + '">' + (r2.latensi_ms ? r2.latensi_ms + " ms" : "—") + "</td>"
            + "</tr>";
        }).join("");
      }
      lapor("monitoring-diisi", "alerts=" + (d.alerts || []).length + " riwayat=" + (d.riwayat || []).length);
    }).catch(function (e) { lapor("monitoring-gagal", String(e)); });
  }

  function kueriAudit() {
    var p = document.getElementById("auditPeristiwa");
    var q = document.getElementById("auditCari");
    var b = document.getElementById("auditBatas");
    return "batas=" + encodeURIComponent(b && b.value ? b.value : "60")
      + "&peristiwa=" + encodeURIComponent(p ? p.value : "")
      + "&cari=" + encodeURIComponent(q ? q.value : "");
  }
  function isiPilihan() {
    var p = document.getElementById("auditPeristiwa");
    if (!p) return;
    fetch("/api/audit/peristiwa").then(function (r) { return r.json(); }).then(function (d) {
      var ada = p.value;
      p.innerHTML = '<option value="">semua peristiwa</option>' + (d.item || []).map(function (x) {
        return '<option value="' + x.peristiwa + '">' + x.peristiwa + " (" + x.n + ")</option>";
      }).join("");
      p.value = ada;
    }).catch(function () {});
  }
  window.isiAudit = isiAudit;
  window.isiPilihanAudit = isiPilihan;
  window.isiMonitoring = isiMonitoring;
  document.addEventListener("DOMContentLoaded", function () {
    isiPilihan(); isiAudit(); isiMonitoring();
    setTimeout(function () { isiAudit(); isiMonitoring(); }, 1200);
  });
})();
