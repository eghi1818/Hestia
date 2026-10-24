"""RedirectDriver - abstraksi eksekusi 301/410 lintas panel.

Modul 4 satu-satunya pemanggil. read/plan/verify = read-only.
apply(dry_run=True) juga read-only. apply(dry_run=False) satu-satunya write.
"""
from __future__ import annotations

import abc, argparse, dataclasses, difflib, json, os, re, shlex, subprocess, sys, time

MARK_A = "# >>> hestia-managed >>>"
MARK_B = "# <<< hestia-managed <<<"
POLA = re.compile(r'location\s*=\s*(\S+)\s*\{\s*return\s+(\d{3})(?:\s+([^;]+))?\s*;')


@dataclasses.dataclass(frozen=True)
class Rule:
    path: str
    code: int
    target: str | None = None

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError("path wajib diawali / : %r" % self.path)
        if self.code not in (301, 410):
            raise ValueError("code wajib 301 atau 410 : %r" % self.code)
        if self.code == 301 and not self.target:
            raise ValueError("301 wajib punya target : %r" % self.path)

    def line(self) -> str:
        if self.code == 410:
            return "location = %s { return 410; }" % self.path
        return "location = %s { return 301 %s; }" % (self.path, self.target)


@dataclasses.dataclass
class Step:
    op: str
    rule: Rule
    before: str | None = None
    after: str | None = None

    def __str__(self) -> str:
        return "%-6s %s" % (self.op, self.rule.line())


class RedirectDriver(abc.ABC):
    name = "?"

    @abc.abstractmethod
    def read(self, domain: str) -> dict[str, Rule]: ...
    @abc.abstractmethod
    def render(self, rules: list[Rule]) -> str: ...
    @abc.abstractmethod
    def apply(self, domain: str, rules: list[Rule], dry_run: bool = True) -> dict: ...
    @abc.abstractmethod
    def verify(self, domain: str, rule: Rule, base_url: str) -> tuple[bool, str]: ...

    def plan(self, domain: str, desired: list[Rule]) -> list[Step]:
        cur = self.read(domain)
        want = {r.path for r in desired}
        out: list[Step] = []
        for r in desired:
            b = cur.get(r.path)
            if b is None:
                out.append(Step("add", r))
            elif b != r:
                out.append(Step("update", r, str(b), str(r)))
            else:
                out.append(Step("noop", r, str(b), str(b)))
        for p, b in cur.items():
            if p not in want:
                out.append(Step("remove", b))
        return out


def _env(nama: str, bawaan: str) -> str:
    return os.environ.get(nama, bawaan)


def _ssh_host(script: str, timeout: int = 30):
    cmd = ["ssh", "-i", os.path.expanduser(_env("HESTIA_SSH_KEY", "~/.ssh/wesearch_vps_key")),
           "-p", _env("HESTIA_SSH_PORT", "10053"),
           "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
           "-o", "ConnectTimeout=10",
           "%s@%s" % (_env("HESTIA_SSH_USER", "administrator"), _env("HESTIA_SSH_HOST", "93.127.133.160")),
           script]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def _ssh_ct(script: str, data: str | None = None, timeout: int = 30):
    ct = _env("HESTIA_CT", "hx")
    cmd = ["ssh", "-i", os.path.expanduser(_env("HESTIA_SSH_KEY", "~/.ssh/wesearch_vps_key")),
           "-p", _env("HESTIA_SSH_PORT", "10053"),
           "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
           "-o", "ConnectTimeout=10",
           "%s@%s" % (_env("HESTIA_SSH_USER", "administrator"), _env("HESTIA_SSH_HOST", "93.127.133.160")),
           "lxc exec %s -- sh -c %s" % (ct, shlex.quote(script))]
    r = subprocess.run(cmd, input=data, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


class NginxDriver(RedirectDriver):
    """nginx polos. Baca/tulis lewat container root; nginx -t dan reload lewat host."""

    name = "nginx"

    def __init__(self, hostprefix: str = "/mnt/host", reload_cmd: str | None = None):
        self.p = hostprefix
        self.reload_cmd = reload_cmd or _env("HESTIA_NGINX_RELOAD", "sudo -n systemctl reload nginx")

    _cache: dict = {}

    def _coba(self, daftar, via):
        kunci = (tuple(daftar), via)
        if kunci in self._cache:
            return self._cache[kunci]
        out = ""
        for cmd in daftar:
            fn = _ssh_ct if via == "ct" else _ssh_host
            rc, out, err = fn(cmd, timeout=45)
            if rc == 0:
                self._cache[kunci] = (True, cmd, out + err)
                return self._cache[kunci]
        self._cache[kunci] = (False, daftar[-1], out)
        return self._cache[kunci]

    def _test(self):
        ok, cmd, out = self._coba([
            "sudo -n nginx -t",
            "chroot %s /usr/sbin/nginx -t" % self.p,
        ], "host")
        return ok, "%s | %s" % (cmd, out.strip())

    def _reload(self):
        ok, cmd, out = self._coba([
            "sudo -n systemctl reload nginx",
            "chroot %s /usr/sbin/nginx -s reload" % self.p,
        ], "host")
        return ok, "%s | %s" % (cmd, out.strip())

    def conf(self, domain: str) -> str:
        return "%s/etc/nginx/sites-available/%s" % (self.p, domain)

    def _baca(self, domain: str) -> str:
        rc, out, err = _ssh_ct("cat %s 2>/dev/null || true" % shlex.quote(self.conf(domain)))
        if rc != 0:
            raise RuntimeError("baca gagal: %s" % err.strip())
        return out

    def read(self, domain: str) -> dict[str, Rule]:
        teks = self._baca(domain)
        if MARK_A not in teks or MARK_B not in teks:
            return {}
        region = teks.split(MARK_A, 1)[1].split(MARK_B, 1)[0]
        out: dict[str, Rule] = {}
        for baris in region.splitlines():
            m = POLA.search(baris)
            if not m:
                continue
            path, code, target = m.group(1), int(m.group(2)), (m.group(3) or "").strip() or None
            out[path] = Rule(path, code, target)
        return out

    def render(self, rules: list[Rule]) -> str:
        isi = "\n".join("    " + r.line() for r in sorted(rules, key=lambda x: x.path))
        return "%s\n%s\n%s\n" % (MARK_A, isi, MARK_B)

    def _sisip(self, teks: str, blok: str) -> str:
        """Idempoten by construction: buang region lama dulu, baru sisip.

        Satu jalur saja - tidak ada cabang "sudah ada region" vs "belum ada",
        karena cabang itulah yang membuat file tidak konvergen.
        """
        teks = re.sub(r"(?ms)^%s\n.*?^%s\n" % (re.escape(MARK_A), re.escape(MARK_B)),
                      "", teks)
        i = teks.rstrip().rfind("}")
        if i < 0:
            raise RuntimeError("config tanpa penutup blok server")
        head = teks[:i].rstrip("\n") + "\n"
        return head + blok + teks[i:]

    def apply(self, domain: str, rules: list[Rule], dry_run: bool = True) -> dict:
        lama = self._baca(domain)
        blok = self.render(rules)
        baru = self._sisip(lama, blok)
        assert self._sisip(baru, blok) == baru, "splice bukan fixed point"
        beda = list(difflib.unified_diff(lama.splitlines(), baru.splitlines(),
                                        "sebelum", "sesudah", lineterm=""))
        hasil = {"domain": domain, "changed": lama != baru, "diff": "\n".join(beda),
                 "applied": False, "tested": False, "reloaded": False}
        if not hasil["changed"] or dry_run:
            return hasil

        cap = "%s/var/backup/nginx/%s/%s.conf" % (self.p, domain, time.strftime("%Y%m%d-%H%M%S"))
        _ssh_ct("mkdir -p $(dirname %s) && cp %s %s"
                % (shlex.quote(cap), shlex.quote(self.conf(domain)), shlex.quote(cap)))
        rc, _o, err = _ssh_ct("cat > %s" % shlex.quote(self.conf(domain)), data=baru)
        if rc != 0:
            raise RuntimeError("tulis gagal: %s" % err.strip())

        ok, out = self._test()
        hasil["tested"] = ok
        if not ok:
            _ssh_ct("cp %s %s" % (shlex.quote(cap), shlex.quote(self.conf(domain))))
            hasil["rollback"] = True
            hasil["pesan"] = (out + err).strip()[:400]
            return hasil

        ok, out = self._reload()
        hasil["reloaded"] = ok
        if not ok:
            hasil["pesan"] = out.strip()[:400]
        hasil["applied"] = True
        hasil["backup"] = cap.replace(self.p, "", 1)
        return hasil

    def verify(self, domain: str, rule: Rule, base_url: str) -> tuple[bool, str]:
        fmt = "%{http_code} %{redirect_url}"
        rc, out, err = _ssh_host(
            "curl -sS -o /dev/null -w '%s' -H %s http://127.0.0.1%s"
            % (fmt, shlex.quote("Host: " + domain), shlex.quote(rule.path)))
        asal = out.strip()
        r2 = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", fmt, "--max-time", "15",
                             base_url.rstrip("/") + rule.path],
                            capture_output=True, text=True)
        publik = r2.stdout.strip()

        def cocok(txt: str) -> bool:
            bagian = txt.split()
            if not bagian or bagian[0] != str(rule.code):
                return False
            if rule.code == 301:
                return bool(rule.target) and bagian[1].endswith(rule.target)
            return True

        ok = cocok(asal) and cocok(publik)
        pesan = "origin=[%s] publik=[%s] harap=%d%s" % (asal, publik, rule.code,
                                                        " -> " + str(rule.target) if rule.target else "")
        return ok, pesan


DRIVER = {"nginx": NginxDriver}


def _muat(path: str) -> list[Rule]:
    d = json.load(open(path, encoding="utf-8"))
    return [Rule(r["path"], int(r["code"]), r.get("target")) for r in d["rules"]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("aksi", choices=["plan", "apply", "verify", "read"])
    ap.add_argument("--domain", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--driver", default="nginx")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--apply", action="store_true", help="tanpa ini = dry-run")
    a = ap.parse_args(argv)

    d = DRIVER[a.driver]()
    rules = _muat(a.rules)
    base = a.base_url or ("https://" + a.domain)

    if a.aksi == "read":
        print(json.dumps({k: dataclasses.asdict(v) for k, v in d.read(a.domain).items()},
                         indent=2, ensure_ascii=False))
        return 0
    if a.aksi == "plan":
        langkah = d.plan(a.domain, rules)
        for s in langkah:
            print(s)
        print("ringkas: add=%d update=%d remove=%d noop=%d" % (
            sum(s.op == "add" for s in langkah), sum(s.op == "update" for s in langkah),
            sum(s.op == "remove" for s in langkah), sum(s.op == "noop" for s in langkah)))
        return 0
    if a.aksi == "apply":
        h = d.apply(a.domain, rules, dry_run=not a.apply)
        print("changed=%s applied=%s tested=%s reloaded=%s" % (h["changed"], h["applied"],
                                                              h["tested"], h["reloaded"]))
        if h["diff"]:
            print(h["diff"])
        if h.get("pesan"):
            print("pesan:", h["pesan"])
        return 0 if (not h["changed"] or a.apply and h["applied"]) else 1
    if a.aksi == "verify":
        gagal = 0
        for r in rules:
            ok, pesan = d.verify(a.domain, r, base)
            print("%-6s %s" % ("ok" if ok else "GAGAL", pesan))
            gagal += 0 if ok else 1
        return 0 if gagal == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
