# Hestia Dashboard (Prototype UI)

Prototype frontend untuk panel Authority Hosting — satu file HTML mandiri,
tanpa dependensi eksternal (CSS & chart SVG dibuat inline, data dummy).

## Cara menjalankan

Opsi 1 — buka langsung:
    open dashboard/index.html

Opsi 2 — server lokal (disarankan):
    cd dashboard
    python3 -m http.server 8787 --bind 127.0.0.1
Lalu buka http://127.0.0.1:8787

## Struktur

- index.html — seluruh UI: Dashboard, Target, Detail target (tabbed),
  Recon (antrian animasi), Kredensial (mask/reveal), Deployment,
  Konten, Monitoring, Backlink, Laporan, Audit Log, Pengaturan.

## Modifikasi cepat

- Warna/tema   : blok `:root` di <style> (ubah --accent untuk warna utama)
- Data dummy   : konstanta `targets`, `creds`, `alerts`, `deployments`,
  `konten`, `backlinks`, `audit`, `checks` di bagian <script>
- Navigasi     : elemen `.nav-item` (data-page) + `<section class="page">`

Catatan: ini prototype UI (Tahap 1 PRD). Integrasi API nyata (POST /targets,
/recon, dsb.) menyusul pada implementasi backend.
