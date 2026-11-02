# Blocked hosts

Hosts that refused this repository's user agent (`userAgent` in `policy/sources.json`) when their robots.txt was checked. The sources contract leaves a refusing host out of `policy/sources.json`, so they are recorded here instead, so that nobody retries them without a reason. `scripts/sources-check.py` fails when a host is both here and in `policy/sources.json`.

What counts as a refusal follows the refresh specification (`spec/README.md`, rule 1): a robots.txt that answers 404 or 410 is absent and blocks nothing; one that answers 401, 403 or any other 4xx but 404, 410 and 429 is a refusal; 429 is throttling; a challenge page instead of robots.txt is a challenge; a 5xx or a network error is unreadable; a rule that disallows `/` or a path we fetch is a disallow. Each of the last five blocks the host, in the rows below and in a refresh run, which records it as `refused`, `throttled`, `challenge`, `unreachable` or `disallowed` and fetches nothing from that host.

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

## Reproduction needs permission

These hosts allow robots, but their published terms require permission before their material is reproduced. Quotes are not taken from them. The facts they would have served come from the Gazette of India instead.

| host | terms | checked (UTC) | would have served |
|---|---|---|---|
| trai.gov.in | /website-policy: material "may be reproduced free of charge after taking proper permission by sending a mail to us" | 2026-11-01T05:29:58Z | TRAI regulations and directions on commercial communications |
| cbic-gst.gov.in | /disclaimer.html: the same sentence | 2026-11-01T05:33:19Z | GST law and notifications |
| einvoice1.gst.gov.in | /Others/WebsitePolicies: no reproduction or reuse "without the prior written permission of NIC" | 2026-11-01T05:33:23Z | e-invoice portal specifications and FAQs |

Acts and regulations that these bodies administer can still be cited from the Gazette of India (egazette.gov.in), which is listed in `policy/sources.json`.
