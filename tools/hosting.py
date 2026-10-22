"""Cari penyedia hosting dan repo sumber sebuah domain, tanpa kredensial.

Situs di Netlify membocorkan repo_url lewat API publiknya.
"""
import json
import re
import sys
import urllib.error
import urllib.request

HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
TANDA = [("netlify", ["x-nf-request-id", "x-nf-request-id"]), ("vercel", ["x-vercel-id"]),
         ("cloudflare", ["cf-ray"]), ("cloudfront", ["x-amz-cf-id"]),
         ("github pages", ["x-github-request-id"]), ("firebase", ["x-cloud-trace-context"])]


def http(url, t=20):
    try:
        r = urllib.request.Request(url, headers=HDR)
        with urllib.request.urlopen(r, timeout=t) as x:
            return x.status, x.read(500000).decode("utf-8", "ignore"), {k.lower(): v for k, v in x.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, "", {k.lower(): v for k, v in e.headers.items()}
    except Exception:
        return 0, "", {}


def penyedia(hd):
    kunci = " ".join(hd.keys())
    for nama, tanda in TANDA:
        if any(t in kunci for t in tanda):
            return nama
    return hd.get("server", "-")


def netlify(domain):
    for k in (domain, domain.replace(".", "-"), domain.split(".")[0]):
        s, t, _ = http("https://api.netlify.com/api/v1/sites/" + k)
        if s == 200:
            try:
                return k, json.loads(t)
            except Exception:
                pass
    return None, None


def periksa(domain):
    print("== %s ==" % domain)
    s, isi, hd = http("https://" + domain + "/")
    if s == 0:
        s, isi, hd = http("http://" + domain + "/")
    pen = penyedia(hd)
    print("   http %s | penyedia %s | byte %d" % (s, pen, len(isi)))
    m = re.search(r"<title[^>]*>([^<]*)", isi, re.I)
    print("   judul:", (m.group(1).strip()[:70] if m else "-"))
    kerangka = []
    if "/_next/" in isi:
        kerangka.append("next.js")
    if "/_nuxt/" in isi:
        kerangka.append("nuxt")
    if re.search(r"wp-content|wp-includes", isi):
        kerangka.append("wordpress")
    if not kerangka and re.search(r"<html", isi, re.I):
        kerangka.append("html biasa")
    print("   kerangka:", ", ".join(kerangka) or "-")
    print("   pages.dev/workers.dev:", ", ".join(sorted(set(re.findall(r"[a-z0-9-]+\.(?:pages|workers)\.dev", isi)))) or "-")
    if pen == "netlify":
        k, d = netlify(domain)
        if not d:
            print("   netlify api: tidak ketemu")
        else:
            bs = d.get("build_settings") or {}
            print("   netlify api: kunci=%s | site_id=%s" % (k, d.get("id")))
            print("   REPO       :", bs.get("repo_url") or "(tidak ada - deploy manual)")
            print("   cabang     :", bs.get("repo_branch"), "| perintah:", bs.get("cmd"), "| dir:", bs.get("dir"))
            print("   framework  :", bs.get("framework"), "| domain:", d.get("custom_domain"))
            pd = d.get("published_deploy") or {}
            print("   deploy terbit:", pd.get("id"), pd.get("published_at"), pd.get("branch"))
    print()


if __name__ == "__main__":
    for d in (sys.argv[1:] or ["waspadaweb.com"]):
        periksa(d)
