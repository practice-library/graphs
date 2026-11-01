# regulations/in-data-governance

Indian data governance, one fact per file in `graph/nodes/`, listed in `INDEX.md`. It covers:
- the Digital Personal Data Protection Act, 2023;
- its commencement notification, G.S.R. 843(E);
- the notification establishing the Data Protection Board, G.S.R. 844(E);
- the Digital Personal Data Protection Rules, 2025, G.S.R. 846(E);
- the CERT-In directions of 28 April 2022 under section 70B(6) of the Information Technology Act, 2000.

Each obligation, timeline, penalty, exemption and provision gives:
- whom it applies to, in the text's own terms (`attrs.scope`);
- the date from which it applies (`attrs.window`);
- its status on `measuredAt` (`attrs.status`): `in-force`, `notified-not-in-force`, `draft` or `superseded`.

Commencement is traced by edges: a `commencedBy` edge points at the provision that brings the fact into force.

## Sources

Every quote is copied from the official text, as published:

| text | source |
|---|---|
| DPDP Act, 2023 | https://egazette.gov.in/WriteReadData/2023/248045.pdf |
| G.S.R. 843(E), commencement of the Act | https://egazette.gov.in/WriteReadData/2025/267647.pdf |
| G.S.R. 844(E), Data Protection Board | https://egazette.gov.in/WriteReadData/2025/267648.pdf |
| DPDP Rules, 2025 | https://egazette.gov.in/WriteReadData/2025/267650.pdf |
| CERT-In directions, 2022 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf |

All three gazette notifications were published on 13 November 2025.

**Host evidence:** both hosts and their evidence are in `policy/sources.json`:
- `egazette.gov.in` has no robots.txt, and its disclaimer is the terms page recorded;
- `www.cert-in.org.in` has no robots file, and its terms of use are recorded.

Neither page restricts automated reading.

**Hosts not used:** two hosts that also publish these texts refused this repository's user agent, even for robots.txt. They are not listed and are not cited.

**PDF text:** quotes are matched in the text extracted from each PDF. Extraction sometimes splits a hyphenated number, for example "seventy -two". Quotes avoid those spans, and the number they would carry is given in `attrs.value` and in the `note`.

## The ten questions

The acceptance questions are in practice-library/graphs#37. These nodes answer them:

1. **Commencement:**
   - `provision.in.gsr-843-2025.a`, `.b` and `.c` (the Act);
   - `provision.in.dpdp-rules-2025.r1-2`, `r1-3` and `r1-4` (the Rules);
   - `provision.in.cert-in-directions-2022.effective`.
2. **Breach report to the Board:** `obligation.in.dpdp-rules-2025.r7-2-a` and `timeline.in.dpdp-rules-2025.r7-2-b`.
3. **Breach notice to individuals:** `obligation.in.dpdp-rules-2025.r7-1`.
4. **Incident reporting to CERT-In:** `timeline.in.cert-in-directions-2022.incident-report` and `definition.in.cert-in-directions-2022.annexure-i`.
5. **Logs:** `timeline.in.cert-in-directions-2022.log-retention`, and processing logs under the Rules in `timeline.in.dpdp-rules-2025.r8-3`.
6. **Consent notice:** `obligation.in.dpdp-rules-2025.r3`.
7. **Erasure:** `timeline.in.dpdp-rules-2025.third-schedule-1` to `-3`, and the 48-hour notice in `timeline.in.dpdp-rules-2025.r8-2`.
8. **Children:** `obligation.in.dpdp-rules-2025.r10-1`, and the exemptions in `exemption.in.dpdp-rules-2025.fourth-schedule-a` and `-b`.
9. **Significant Data Fiduciaries:**
   - `timeline.in.dpdp-rules-2025.r13-1`;
   - `obligation.in.dpdp-rules-2025.r13-3` and `r13-4`;
   - `obligation.in.dpdp-act-2023.s10-2-a`.
10. **Penalties and grievances:** `penalty.in.dpdp-act-2023.schedule-1` to `-7` (item 6 has no fixed amount and is not a node), and `timeline.in.dpdp-rules-2025.r14-3`.

**Known gap:** `instrument.in.so-5458-2026` is recorded as absent. A 2026 order under section 43 is reported to correct the wording of sections 9(1) and 10(2)(c)(ii), but its gazette copy was not located. Questions 8 and 9 are therefore answered from Rules 10 and 13, which it does not touch.

## Status changes with time

`attrs.status` is true on `measuredAt`. `scripts/graph-check.sh` fails a node whose status disagrees with its window on that date. A refresh that moves `measuredAt` past a window must therefore also change the status. For example, rule 4 and sections 6(9) and 27(1)(d) of the Act come into force on 13 November 2026.

## Attribution

The quoted passages are from official publications of the Government of India: the Gazette of India and CERT-In. They are short, unmodified, and each links to its source. The ids, names, verdicts, values, statuses and edges around them are this repository's own. They are not legal advice and are not endorsed by any authority.
