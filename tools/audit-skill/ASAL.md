# Asal berkas ini

Vendor dari https://github.com/cloudflare/security-audit-skill (MIT, Cloudflare).
Commit yang dipin: c1c8a8c1471069fb0e188eeaff69b8e8db6564a8 (14 Sep 2026).
Diambil dari: skills/security-audit/{report-schema.json,validate-findings.cjs,validate-findings.test.cjs}

Aturan: report-schema.json TIDAK boleh disunting. Kalau disunting, validasi-silang dengan upstream putus.
Validator dijalankan oleh tools/gate_audit.sh. Berkas .md panduan sengaja tidak di-vendor
supaya pemeriksaan sterilisasi gate tidak terganggu.

Ditambah: validate-coverage-ledger.cjs dari skills/security-audit/ (commit yang sama). Wajib ada karena validate-findings.test.cjs:576 me-require-nya.
