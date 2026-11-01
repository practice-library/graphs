# regulations/in-commercial-communications

Indian rules on commercial communications over telecom networks, one fact per file in `graph/nodes/`, listed in `INDEX.md`. It covers the Telecom Commercial Communications Customer Preference Regulations, 2018 (6 of 2018), and the three amendments to it:
- the Amendment Regulations, 2018 (10 of 2018);
- the Second Amendment Regulations, 2025 (1 of 2025);
- the Third Amendment Regulations, 2026 (05 of 2026).

Each obligation, timeline, penalty, exemption and provision gives:
- whom it applies to, in the text's own terms (`attrs.scope`);
- the date from which it applies (`attrs.window`);
- its status on `measuredAt` (`attrs.status`): `in-force`, `notified-not-in-force`, `draft` or `superseded`.

## Sources: the Gazette only

Every quote is copied from the text published in the Gazette of India, Extraordinary, Part III, Section 4:

| text | Gazette dated | source |
|---|---|---|
| Principal regulations, 2018 (6 of 2018) | 19 July 2018 | https://egazette.gov.in/WriteReadData/2018/187768.pdf |
| Amendment Regulations, 2018 (10 of 2018) | 21 December 2018 | https://egazette.gov.in/WriteReadData/2018/194224.pdf |
| Second Amendment Regulations, 2025 (1 of 2025) | 12 February 2025 | https://egazette.gov.in/WriteReadData/2025/261096.pdf |
| Third Amendment Regulations, 2026 (05 of 2026) | 18 September 2026 | https://egazette.gov.in/WriteReadData/2026/276548.pdf |

**Host evidence:** `egazette.gov.in` and its evidence are in `policy/sources.json`, as for `regulations/in-data-governance`. The principal regulations' PDF is about 8.4 MB, so this graph's entry allows up to 9,000,000 bytes.

**Hosts not used:** the regulator's own website is not cited. Its website policy requires permission before its material is reproduced, and its terms say its content is not a statement of law (`policy/blocked-hosts.md`).

**PDF text:** quotes are matched in the text extracted from each PDF. Each Gazette prints the Hindi text first, then the English text, and only the English text is quoted.

## Not covered

- Directions, orders and consultation papers of the regulator that are not published in the Gazette.
- The Access Providers' Codes of Practice, and the technical specifications of the ledger platforms.
- Consolidated texts published elsewhere. Every fact here is cited to the Gazette text that made it, so a provision as amended is cited to the amendment.
- The 2010 regulations (6 of 2010) and their amendments, which regulation 38 of the 2018 regulations repeals.
- The Explanatory Memoranda printed with each regulation. They explain the changes and are not quoted.

## The ten questions

The acceptance questions are in practice-library/graphs#55. These nodes answer them:

1. **Commencement:**
   - principal regulations: `provision.in.tcccpr-2018.r1-2-a` to `-d`, with clause (e) as made (`provision.in.tcccpr-2018.r1-2-e`, superseded);
   - 2018 amendment: `provision.in.tcccpr-amendment-2018.r1-2-e`, `-f` and `-g`;
   - Second Amendment: `provision.in.tcccpr-amendment-2025.r1-3` and `r1-3-late`;
   - Third Amendment: `provision.in.tcccpr-amendment-2026.r1-3`, plus `r1-3-a` and `r1-3-b`, which are notified but not in force on 1 November 2026.
2. **Registration:**
   - `obligation.in.tcccpr-amendment-2025.r3-2` (Senders);
   - `obligation.in.tcccpr-2018.r32` (business and legal entities);
   - `obligation.in.tcccpr-2018.r13` (the ledger platform).
3. **Headers and templates:**
   - `obligation.in.tcccpr-2018.r8`;
   - `obligation.in.tcccpr-amendment-2025.r3-1`, `r22-1-c` and `r22-1-e`;
   - `obligation.in.tcccpr-amendment-2025.schedule-1-header-suffix`.
4. **Consent:**
   - `definition.in.tcccpr-amendment-2026.consent` and `.explicit-consent`;
   - `timeline.in.tcccpr-2018.schedule-2-revocation`;
   - `timeline.in.tcccpr-amendment-2025.schedule-1-reacquire`;
   - `timeline.in.tcccpr-amendment-2026.service-consent`;
   - the 2025 limit on inferred consent and its deletion in 2026: `provision.in.tcccpr-amendment-2025.r2-ah` and `provision.in.tcccpr-amendment-2026.r2-ah`.
5. **Preferences:**
   - `obligation.in.tcccpr-2018.r6`;
   - `timeline.in.tcccpr-2018.r6-3` and `.r7`;
   - `provision.in.tcccpr-amendment-2026.schedule-2-categories`;
   - `exemption.in.tcccpr-amendment-2025.government-message`.
6. **Complaints:**
   - `timeline.in.tcccpr-amendment-2025.r23-2` (seven days; it supersedes three days in `timeline.in.tcccpr-2018.r23-2`);
   - `timeline.in.tcccpr-2018.r23-3`;
   - `timeline.in.tcccpr-amendment-2026.r25-4-b` and `r25-4-d`.
7. **Sending hours:** `provision.in.tcccpr-2018.schedule-2-time-bands`. The text sets default-off time bands, not a fixed sending window. Its note says what the default allows.
8. **Action against senders:**
   - `obligation.in.tcccpr-amendment-2026.r25-5-d`, which supersedes the 2025 and 2018 thresholds;
   - `timeline.in.tcccpr-amendment-2026.r25-6-a` and `r25-6-b`;
   - `obligation.in.tcccpr-amendment-2026.r25-4-d-proviso`, which is notified but not in force.
9. **Access Providers:**
   - `obligation.in.tcccpr-2018.r5` and `.r8-1`;
   - the penalties `penalty.in.tcccpr-2018.r21`, `penalty.in.tcccpr-amendment-2025.r27-1-a`, `r27-1-b`, `r27-1-d`, `r28-1-a` and `r28a`, and `penalty.in.tcccpr-amendment-2026.r27-1-a`.
10. **Amendments:** each amendment's instrument node lists what it changes in its note. Facts that an amendment made carry an `amends` edge to the principal regulations. A replacement points to what it replaced with `supersedes`, and the replaced fact has status `superseded`.

## Conventions

These follow `regulations/in-data-governance`:
- **`partOf`** points from each fact to the instrument that made it.
- **`commencedBy`** points at the commencement clause for its window.
- **`imposes`** is not used (#46).
- **Absence** would be `unknown`, with a note starting `Absent: `. None of the ten questions needed one.

Two conventions are new here:
- **Amendments:** a fact inserted or substituted by an amendment has an id under the amendment, such as `obligation.in.tcccpr-amendment-2025.r3-2`. The id names the principal regulation it changes, here `r3-2` for regulation 3(2). The fact has an `amends` edge to `instrument.in.tcccpr-2018`.
- **Superseded facts:** text that a later amendment replaced stays in the graph with status `superseded` and the window from which it first applied. The replacing fact points to it with `supersedes`. Not every replaced provision is recorded, only those that answer a question.

## Status changes with time

`attrs.status` is true on `measuredAt`. `scripts/graph-check.sh` fails a node whose status disagrees with its window on that date. Two windows fall after 1 November 2026:
- **17 November 2026:** regulations 4, 6, 8(a) and 18 of the Third Amendment.
- **17 December 2026:** the Annexure items, including the proviso in `obligation.in.tcccpr-amendment-2026.r25-4-d-proviso`.

A refresh that moves `measuredAt` past either date must also change those statuses.

Every window counted from publication is computed: the stated number of days after the date printed on the Gazette. The e-Gazette site lists later upload dates for some issues, for example 30 July 2018 and 28 September 2026. This graph does not use them.

## Attribution

The quoted passages are from the Gazette of India, an official publication of the Government of India. They are short and unmodified, and each links to its source. The ids, names, verdicts, values, statuses and edges around them are this repository's own. They are not legal advice and are not endorsed by any authority.
