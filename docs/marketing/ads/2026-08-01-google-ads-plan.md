# Google Ads Plan — 7Magic

**Date:** 2026-08-01
**Status:** Planning. Nothing launched, no account connected yet.
**Next session:** user shares Google Ads / Keyword Planner access; work continues in the browser.

## Objective

Buy qualified demand for two separate businesses that share one site:

1. **Wedding venue marketplace** — 121 active venues, packages, enquiry forms.
2. **Corporate event organizer** — new landing page at `/bali-event-organizer`
   (outing, team building, gathering, gala dinner, conference, incentive).

These have different buyers, different languages and different economics. They do
not share campaigns.

## What was measured, and what was not

Everything in the competition table below was observed directly on live Google
Indonesia SERPs (`gl=id&hl=id`) on 2026-08-01. The CPC bands are published
third-party benchmarks, cited inline.

**No search volumes and no real CPCs were available.** Those need Keyword Planner,
Ahrefs or Semrush. Any priority ordering in this document is reasoned from intent
and observed competition, not from volume data. Re-validate once Planner access
lands — that is the first job of the next session.

## Finding 1 — the auctions are empty

Paid competition, observed directly:

| Query | Ads on SERP |
|---|---|
| `paket outing bali perusahaan` | none |
| `gathering perusahaan bali` | none |
| `event organizer bali outing kantor` | none |
| `event organizer bali` | none |
| `event organizer jakarta` | none |
| `wedding organizer jakarta` | none |
| `jasa event organizer gala dinner jakarta` | none |
| `paket pernikahan jakarta` | none |
| `paket pernikahan hotel jakarta 300 undangan` | none |
| `gedung pernikahan jakarta` | none |
| `paket pernikahan ritz carlton pacific place` | none |
| `paket wedding kempinski jakarta` | none |
| `wedding organizer bali` | 1 sponsored (local) |
| `bali wedding planner` (`gl=au`) | 1 sponsored + sitelinks |
| `team building bali` | **2 sponsored + sponsored local pack** |

Indonesian CPC benchmark: **Rp 500–1,500 average**, competitive terms
Rp 3,000–8,000, long-tail **under Rp 500**
([Arfadia](https://www.arfadia.com/resources/digital-marketing-benchmark-indonesia-2026),
[Lopokopi](https://lopokopi.co/biaya-google-ads-indonesia/)).

Empty auctions clear near the floor. Indonesian-language long-tail is the cheap
inventory.

**Do not bid the head terms.** `event organizer bali`, `event organizer jakarta`,
`wedding organizer jakarta` and `gedung pernikahan jakarta` are dominated by the
Local Pack with no ads at all. Paying to sit under a map you could rank in for
free is the worst spend available. Google Business Profile is the lever there,
and it costs nothing.

**Treat `team building bali` as the exception.** FINNS Beach Club (45,898 reviews)
and Adventure Indonesia both bid it. Avoid or bid deliberately.

## Finding 2 — buyer and venue are in different cities

The corporate buyer sits in Jakarta; the event happens in Bali. An HR manager in
Kuningan searches *"paket outing bali"*.

**Geo-target Jakarta, Surabaya, Bandung, Tangerang. Keep the keywords Bali-flavoured.**
Geo-targeting Bali reaches people already on the island — the wrong audience.

## Finding 3 — venue-name keywords are the best inventory we have

Zero advertisers, maximum intent, and the landing pages already exist at
`/wedding-venue/{city}/{slug}`. Keyword, ad and page all name the same hotel,
which lifts Quality Score and lowers CPC further.

Bridestory owns organic rank 1 on these. Paid is the shortcut past them.

**Biddable set: 71 venues.** Active venues that have a non-zero `price_start_from`,
excluding Singapore:

| City | Active | With real price |
|---|---|---|
| Jakarta | 61 | 51 |
| Tangerang | 18 | 17 |
| Bogor | 5 | 2 |
| Bekasi | 1 | 1 |
| Bali | 12 | **0** |
| Singapore | 18 | **0** — deprioritised by decision |
| Batam | 6 | **0** |

`price_start_from` is populated on every row but is `0.00` on 50 of 121. Those 50
stay out of the campaign — see the blocker below.

Generated assets in this directory:

- `7magic-venue-keywords.csv` — 486 phrase-match keywords across the 71 venues,
  in Google Ads Editor import format (Campaign / Ad Group / Keyword / Match Type /
  Final URL). One ad group per venue. Patterns per venue:
  `paket pernikahan {v}`, `paket wedding {v}`, `harga paket pernikahan {v}`,
  `biaya pernikahan di {v}`, `{v} ballroom pernikahan`, `wedding package {v}` —
  plus a shortened name variant where the legal name is long.
- `7magic-negative-keywords.txt` — 34 account-level negatives.

**Launch structure:** start with Dynamic Search Ads scoped to a feed of **only the
71 priced venue URLs** — not the whole sitemap, or Google will generate ads for
the unpriced Bali and Singapore pages. Run 4 weeks, then promote the venues with
real impressions into exact-match ad groups with hand-written copy. Do not
hand-build 71 ad groups up front; most will have negligible volume.

## Blocker — prices exist but are not displayed

Every keyword above is a `harga` / `paket` / `biaya` search. The venue pages
currently gate pricing behind the "See venue pricing" modal, while Bridestory's
snippet shows `IDR 228,000,000` and Google's AI summary quotes their numbers
directly.

For 71 venues this is a **display decision, not a data problem** — the number is
already in `price_start_from`.

**Surface a "mulai dari Rp X" band on the venue card and detail page before
spending anything on these keywords.** Paying for people who are asking the price
and landing on a form is the most expensive way to waste this budget.

### Data quality

`Yello Hotel Harmoni` has `price_start_from = 950,000,000` — the highest value in
the database, above The Orient (365jt) and every 5-star in the set. Yello is a
budget brand; this is almost certainly a data-entry error and it currently tops
any price sort. Audit outliers at both ends before these numbers go on the page.

## Keyword tiers — corporate

**Tier 1, cheap and high intent, no ad competition. Start here.**

`paket outing bali` · `paket outing kantor bali` · `outing perusahaan bali` ·
`paket gathering bali` · `gathering perusahaan bali` · `paket outbound bali` ·
`paket outing bali 2 hari 1 malam` · `paket outing bali 3 hari 2 malam` ·
`paket outing bali 30 pax` · `gala dinner bali` · `paket meeting bali`

The pax- and duration-qualified variants are the best on the list.

**Tier 2, Jakarta demand side.**

`jasa event organizer jakarta` · `EO gathering jakarta` ·
`event organizer gala dinner jakarta` · `paket gathering karyawan jakarta` ·
`EO corporate jakarta`

**Tier 3, wedding, bid last.** `wedding organizer bali` and English
`bali wedding planner` have real advertisers, and the English side competes with
Australian and Singaporean budgets. If entered, use price and logistics long-tails
(`paket pernikahan bali harga`, `wedding organizer bali murah`) where the
international players do not compete.

## Account structure

Two entities: **PT Perorangan** (Indonesia) and a **Sole Proprietorship**
(Singapore). One Google Ads Manager (MCC) on top, two accounts underneath.

| Campaign | Account |
|---|---|
| 71 venue-name keywords (Jakarta / Tangerang / Bogor / Bekasi) | PT — IDR |
| Bali corporate outing & gathering, geo-targeted Jakarta | PT — IDR |
| 18 Singapore venues, once priced | SP — SGD |
| English `bali wedding planner` (AU/SG traffic) | SP — SGD |

**The entity that earns the revenue pays for the ads.** Do not route Indonesian
campaigns through the Singapore account to chase a lower tax rate — it breaks the
spend/revenue link, adds personal liability on a sole proprietorship, and produces
a foreign invoice the Indonesian accountant cannot use.

**Currency cannot be changed after account creation.** Getting it wrong means a
new account and losing all campaign history.

### Tax position — affects budgeting, not bidding

Billing currency does not affect CPC. Google converts every auction to USD
internally to compute Ad Rank, so no currency wins auctions more cheaply.

- **PT Perorangan** uses PPh Final UMKM 0.5% while turnover stays under
  **Rp 4.8bn/year**, which is also the PKP threshold. Below it, almost certainly
  not PKP — so the **12% PPN on Google Ads is a dead cost, not creditable**.
  Budget gross: Rp 10jt of spend bills at Rp 11.2jt.
- **Singapore SP** must register for GST only above **S$1M** turnover. Below that
  it is voluntary, with a 2-year minimum commitment, and from 1 April 2026 new
  voluntary registrants must transmit via InvoiceNow/Peppol. Likely not
  registered, so its 9% GST is also a dead cost.

Net: 12% dead vs 9% dead. The 3% gap does not justify restructuring.

**PP 20/2026** now calculates the Rp 4.8bn threshold **in aggregate** — personal
income, every PT Perorangan owned, and spousal income combined. The threshold may
arrive sooner than the PT's own books suggest
([Pajakku](https://pajakku.com/artikel/rangkuman-tanya-jawab-webinar-pajakku-x-djp-ketentuan-baru-pph-umkm-pp-no-20-tahun-2026),
[Ortax](https://ortax.org/update-ketentuan-pajak-umkm)).

### The PKP question gates corporate sales

Indonesian HR and procurement buyers routinely require vendors who can issue
**faktur pajak**. A non-PKP PT Perorangan cannot. That blocks the exact segment
`/bali-event-organizer` targets, and it costs far more than any ad-tax difference.

This is why the "paperwork handled properly" section was removed from the landing
page — it promised something not currently deliverable.

Voluntary PKP registration would allow issuing faktur pajak and make the 12%
recoverable, but requires charging 12% PPN on 7Magic's own invoices. That helps
with corporate clients and hurts with wedding couples paying personally. **Genuine
strategic trade between the two customer types — decision for the accountant, not
a settings change.**

## Compliance note

Bidding on hotel names as **keywords** is permitted by Google. Using them in **ad
headline text** can draw a trademark complaint from the brand owner. Keep hotel
names in keywords and on the landing page; keep ad copy generic
(`Paket Pernikahan Ballroom Jakarta — Harga & Kapasitas`) until a given hotel is
known not to object.

## Open decisions

| Question | Owner |
|---|---|
| Register PT Perorangan as PKP voluntarily? Gates corporate segment. | Accountant |
| Register SG SP for GST voluntarily? Only if SG spend becomes material. | Accountant |
| Does showing "mulai dari Rp X" conflict with hotel partner agreements? | User |
| Replace placeholder rates on `/bali-event-organizer` with real ones | User |

## Next session

1. Connect the shared Keyword Planner account.
2. Pull real volume and bid estimates for: the 486 venue keywords, corporate
   Tier 1 and Tier 2. Replace the reasoned ordering in this document with data.
3. Confirm which of the 71 venues have meaningful volume — expect a long tail
   where most have almost none.
4. Build the DSA campaign against the 71-URL feed. Do not launch until the
   price-display blocker is cleared.
5. Load `7magic-negative-keywords.txt` as a shared account-level list first.
