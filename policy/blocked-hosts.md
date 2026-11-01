# Blocked hosts

Hosts that refused this repository's user agent (`userAgent` in `policy/sources.json`) when their robots.txt was checked. The sources contract leaves a refusing host out of `policy/sources.json`, so they are recorded here instead, so that nobody retries them without a reason.

Nothing past robots.txt was fetched from these hosts. Retry one only after something changes, for example a published robots.txt that allows us, or written permission. Update its row with the new result and date.

| host | refusal | checked (UTC) | would have served |
|---|---|---|---|
| www.meity.gov.in | HTTP 403 Access Denied, even for robots.txt | 2026-11-01T03:47:32Z | DPDP Act and Rules (#37; used the Gazette of India instead) |
| www.indiacode.nic.in | HTTP 403 Access Denied, even for robots.txt | 2026-11-01T03:47:34Z | Acts of Parliament (#37) |
| www.rbi.org.in | HTTP 418 "Unauthorised Access" for robots.txt | 2026-11-01T05:24:55Z | RBI directions and circulars (#36) |
| rbi.org.in | HTTP 418 "Unauthorised Access" for robots.txt | 2026-11-01T05:24:55Z | as above |
| rbidocs.rbi.org.in | a JavaScript bot challenge instead of robots.txt | 2026-11-01T05:24:56Z | RBI documents (PDF) |
| www.npci.org.in | HTTP 403 Access Denied, even for robots.txt | 2026-11-01T05:25:05Z | UPI circulars (#36) |
| npci.org.in | HTTP 403 Access Denied, even for robots.txt | 2026-11-01T05:25:05Z | as above |
| irdai.gov.in | robots.txt: `User-Agent: *` with `Disallow: /` | 2026-11-01T05:25:15Z | IRDAI guidelines (#36) |
| www.irdai.gov.in | robots.txt: `User-Agent: *` with `Disallow: /` | 2026-11-01T05:25:15Z | as above |

Acts that these regulators administer can still be cited from the Gazette of India (egazette.gov.in), which is listed in `policy/sources.json`.
