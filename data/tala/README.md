# data/tala - set tala ambang kemiripan

Dua berkas, dua keputusan, kosakata terpisah. Jangan dicampur.

## pasangan.csv - menala PENSKOR
id, id_halaman, url_mati, url_kandidat, asal_kandidat, label_pasangan, catatan, dilabeli_pada
- asal_kandidat: seksi | lintas | acak   (minimal 50% tidak berasal dari penskor)
- label_pasangan: 301-kuat | 301-wajar | tidak-ok

## halaman.csv - menguji ATURAN, bukan menala
id, url_mati, backlink, label_halaman, rujukan_pasangan, status_saat_label, catatan
- backlink: terverifikasi-ada | terverifikasi-nol | tidak-ada-data
- label_halaman: 301 | 410 | tinjau
Enam sel wajib terisi: 3 status backlink x (ada kandidat layak / tidak ada).

## ulang.csv - 15 pasangan dilabeli dua kali, jeda >= 14 hari, berlapis
id_pasangan, putaran, label, tanggal

## Aturan
- Ambang diturunkan dari pasangan.csv saja.
- label_halaman dilabeli dengan penilaian manusia, BUKAN memakai ambang.
- Baris dengan kolom label kosong = belum dilabeli.
