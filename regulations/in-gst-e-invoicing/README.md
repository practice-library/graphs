# regulations/in-gst-e-invoicing

Indian GST e-invoicing, one fact per file in `graph/nodes/`, listed in `INDEX.md`. It covers:
- rule 48(4) to (6) of the Central Goods and Services Tax Rules, 2017, and the later rule changes that touch it;
- the notification of the e-invoice portals;
- Central Tax notification 13/2020, which names the class of registered persons who must issue e-invoices, with each notification that amended it.

Each obligation, timeline, exemption and provision gives:
- whom it applies to (`attrs.scope`);
- the date from which it applies (`attrs.window`);
- its status on `measuredAt` (`attrs.status`).

## Sources: the Gazette only

Every quote is copied from the Gazette of India, Extraordinary, Part II, Section 3, Sub-section (i), as published on egazette.gov.in:

| Gazette dated | notifications used | source |
|---|---|---|
| 13 December 2019 | 68/2019 (rule 48(4) to (6)), 69/2019 (portals), 70/2019 | https://egazette.gov.in/WriteReadData/2019/214686.pdf |
| 21 March 2020 | 13/2020 | https://egazette.gov.in/WriteReadData/2020/218849.pdf |
| 30 July 2020 | 60/2020 (FORM GST INV-01), 61/2020 | https://egazette.gov.in/WriteReadData/2020/220781.pdf |
| 30 September 2020 | 70/2020 | https://egazette.gov.in/WriteReadData/2020/222145.pdf |
| 30 September 2020 | 72/2020 (rule 46(r), proviso to rule 48(4)) | https://egazette.gov.in/WriteReadData/2020/222164.pdf |
| 1 October 2020 | 73/2020 | https://egazette.gov.in/WriteReadData/2020/222200.pdf |
| 10 November 2020 | 88/2020 | https://egazette.gov.in/WriteReadData/2020/223036.pdf |
| 8 March 2021 | 05/2021 | https://egazette.gov.in/WriteReadData/2021/225713.pdf |
| 1 June 2021 | 23/2021 | https://egazette.gov.in/WriteReadData/2021/227318.pdf |
| 24 February 2022 | 01/2022 | https://egazette.gov.in/WriteReadData/2022/233716.pdf |
| 5 July 2022 | 14/2022 (rule 46(s)) | https://egazette.gov.in/WriteReadData/2022/237097.pdf |
| 1 August 2022 | 17/2022 | https://egazette.gov.in/WriteReadData/2022/237796.pdf |
| 10 May 2023 | 10/2023 | https://egazette.gov.in/WriteReadData/2023/245793.pdf |

**How they were found:** with the e-Gazette text search, which matches only a notification's subject line. The phrases searched were "sub-rule (4) of rule 48", "Invoice Registration Portal" and "e-invoice". Each notification's own note on what last amended 13/2020 was then followed. A notification whose subject line uses none of those phrases could have been missed.

**Hosts not used:** the tax administration's websites and the e-invoice portal are not cited. Their website policies require permission before material is reproduced (`policy/blocked-hosts.md`).

**PDF text:** quotes are matched in the text extracted from each PDF. Each Gazette prints Hindi and English, and only the English is quoted. Some PDFs print quotation marks as `―` and `‖`, and quotes keep them as printed.

## Not covered

- Portal advisories, FAQs, and the API and schema specifications published outside the Gazette.
- Time limits for uploading set outside the Gazette (see question 9).
- The State GST and Integrated GST counterparts, e-way bills and case law.
- The text of rule 54. Notification 13/2020 excludes the persons referred to in rule 54(2) to (4A), and this graph does not name them.

## The ten questions

The acceptance questions are in practice-library/graphs#57. These nodes answer them:

1. **The rule:** `provision.in.ct-68-2019.r48-4`, in force from 13 December 2019.
2. **Who, today:** `obligation.in.ct-10-2023.threshold`: aggregate turnover above five crore rupees from 1 August 2023. Turnover is counted in any preceding financial year from 2017-18 (`provision.in.ct-70-2020.preceding-year`).
3. **History:** each threshold `supersedes` the one before it:
   - `obligation.in.ct-17-2022.threshold` (ten crore);
   - `ct-01-2022` (twenty crore);
   - `ct-05-2021` (fifty crore);
   - `ct-88-2020` (one hundred crore);
   - `ct-61-2020` (five hundred crore, the starting threshold on 1 October 2020);
   - `ct-13-2020` and `ct-70-2019`, two earlier texts that never came into force as made.
4. **Exempt persons:**
   - `exemption.in.ct-13-2020.rule-54`;
   - `exemption.in.ct-61-2020.sez-unit`;
   - `exemption.in.ct-23-2021.government`;
   - the Commissioner's power to exempt, in `provision.in.ct-72-2020.r48-4-proviso`.
5. **Documents and supplies:** `provision.in.ct-13-2020.documents` (supplies to registered persons) and `provision.in.ct-70-2020.exports` (exports). The texts say "invoice and other prescribed documents" without listing those documents, and the node's note says so.
6. **The portal:** `provision.in.ct-69-2019.portals`, from 1 January 2020.
7. **Contents:**
   - `provision.in.ct-60-2020.inv-01` (FORM GST INV-01);
   - `provision.in.ct-60-2020.irn` (the portal generates the IRN);
   - `provision.in.ct-72-2020.r46-r` (the QR code carrying the IRN).
8. **Consequence:** `provision.in.ct-68-2019.r48-5`: the invoice is not treated as an invoice. Persons above the threshold who are not required to issue e-invoices declare so under `provision.in.ct-14-2022.r46-s`.
9. **Time limits:** `timeline.in.cgst-rules-2017.upload-time-limit` is absent. No Gazette text checked sets a standing limit. Notification 73/2020 set thirty days for October 2020 only.
10. **Amendments:** each amending notification has an instrument node with an `amends` edge, to `instrument.in.ct-13-2020` or to `instrument.in.cgst-rules-2017`. Notification 13/2020 `supersedes` 70/2019. The thresholds form a `supersedes` chain.

## Conventions

These follow `regulations/in-commercial-communications`:
- A fact made by a notification has an id under that notification, such as `provision.in.ct-68-2019.r48-4`.
- Each fact is `partOf` its notification and carries an `amends` edge to what it changes.
- Replaced text stays with status `superseded`.
- `commencedBy` is not used, because each notification states its own date. That date is the fact's window, and the note says where no date is stated.
- Notification numbers are written as printed, so 05/2021 becomes `ct-05-2021`.

## Attribution

The quoted passages are from the Gazette of India, an official publication of the Government of India. They are short and unmodified, and each links to its source. The ids, names, verdicts, values, statuses and edges around them are this repository's own. They are not legal advice and are not endorsed by any authority.
