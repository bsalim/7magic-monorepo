# Translation Style Guide — 7magic

Working reference for translating article and venue content. Every translator, human or
subagent, works from this file.

## The standard

The output must read as though an English-speaking wedding blogger wrote it from scratch for
the same audience. If a sentence reads like something that came out of a translation tool, it
is wrong, even when it is accurate.

Two failure modes to avoid, in order of how often they happen:

1. **Flattening.** The Indonesian is chatty, funny and direct. Neutral, competent English that
   drops the jokes and the asides is the most common way this goes wrong.
2. **Calquing.** Rendering an idiom word by word. `bikin dompet nangis` is not "makes your
   wallet cry" — it is "without wrecking your budget".

## Register: articles

Second person, contractions, present tense, direct address. Em-dashes and rhetorical questions
are part of the voice — keep them. The reader is always "you".

| Indonesian | Do not write | Write |
|---|---|---|
| `Pernah kepikiran buat nikah di tempat yang gak pasaran?` | "Have you ever thought about marrying in a place that is not mainstream?" | "Ever pictured getting married somewhere that isn't the usual banquet hall?" |
| `bikin dompet nangis` | "makes your wallet cry" | "without wrecking your budget" |
| `Yuk, cek list lengkapnya!` | "Come on, check the complete list!" | "Let's get into it." |
| `dreamy banget, kan?` | "very dreamy, right?" | "Pretty dreamy, right?" |
| `bikin semua orang speechless` | "makes everyone speechless" | "the kind that leaves your guests speechless" |
| `tanggal cantik` | "beautiful date" | "a lucky date" (or "a date everyone wants" — pick by context) |
| `rebutan slot` | "fighting over slots" | "everyone is chasing the same dates" |
| `anti-heboh` | "anti-crowded" | "low-key" |
| `gak bikin dompet nangis` | — | "easy on the budget" |
| `Yuk jangan sampai tanggal cantik kamu diambil pasangan lain` | "Don't let your beautiful date be taken by another couple" | "Don't let another couple grab your date first." |

### The code-mixing problem

Much of the source is already part English — `Grand Rooms - Spacious dengan modern amenities`,
`Best for: Grand wedding yang bikin semua orang speechless`. Article 7 is roughly half English
before translation even starts.

Do not simply delete the Indonesian connective words and call the result English. Rewrite the
whole line as natural English:

- `Spacious dengan modern amenities` → "Roomy, with modern amenities"
- `Perfect untuk: Pengantin & VIP wedding guests` → "Perfect for: the couple and VIP guests"
- `50+ authentic dishes dari dim sum sampai Peking duck` → "50+ authentic dishes, from dim sum to Peking duck"
- `Bisa disesuaikan untuk intimate sampai mega celebration` → "Scales from an intimate dinner to a full-blown celebration"

### Indonesian terms that stay Indonesian

Cultural terms with no clean English equivalent stay in Indonesian, glossed once on first use in
that article. This matters most for the 28 "Tradisi wedding" articles.

**Gloss in plain text, never with markup.** Adding an `<em>` around a term would change the tag
stream and fail validation, and asterisks would render literally in HTML. Use a dash-bracketed
aside instead: `the akad — the Islamic marriage ceremony — or a dinner`. Where the source
already has `<em>` around a phrase, keep it around the corresponding English phrase.

`akad` · `akad nikah` · `siraman` · `seserahan` · `ngunduh mantu` · `lamaran` · `mahram` ·
`marga` · `adat` · `sungkeman` · `mahar` · `mas kawin` · `ijab qobul` · `wali nikah` ·
`saksi nikah` · `buku nikah`

Ritual and object names that function as proper nouns are kept as-is without needing a gloss
every time: nontoni, nglamar, srah-srahan, paes, kuluk, midodareni, panggih, ngerik, ratus,
mangaririt, ulos, sinamot, sawer panganten, huap lingkung, khitbah, walimah.

`mahar` is **not** "dowry" — a dowry flows from the bride's family to the groom's, which is the
opposite direction. Keep the Indonesian and gloss it as "the bridal gift from the groom".

Terms that DO have clean English equivalents are translated, not preserved as local colour:
`musholla` is "prayer room", `gedung` is "hall" or "building".

Indonesian administrative terms in practical how-to articles (KTP, KK, KUA, RT/RW, kelurahan,
form numbers N1/N2/N4, surat numpang nikah) stay Indonesian with a gloss on first use — the
reader has to ask for these by name at the counter.

Example: "the *akad nikah* — the Islamic marriage contract itself".

`marga` is worth care: it is a Batak clan name, not a surname in the Western sense. Write
"*marga*, the Batak clan name" on first use, then `marga` alone.

Do not gloss twice in the same article. Do not add footnotes or translator's notes.

## Register: venues

Venue descriptions are listing copy, not blog posts. The target here is Indonesian, since the
stored English is being demoted to a translation.

Natural informative marketing prose. No slang, no second person.

- Hospitality vocabulary Indonesian speakers genuinely use in English stays English:
  *ballroom*, *rooftop*, *check-in*, *suite*, *lounge*, *room service*, *minibar*, *gym*,
  *conference center*, *nightclub*, *poolside bar*.
- Numbers use Indonesian formatting: `31,200` → `31.200`, `1,500` → `1.500`.
- Units are preserved, never converted. Square feet stays *kaki persegi*.
- Proper nouns, districts and landmarks keep their local form: Mega Kuningan, SCBD,
  Bundaran HI, Summarecon Mall Serpong, Orchard, Sentosa.
- Paragraph breaks in the source (`\r\n\r\n`) are preserved exactly.

Example:

> **EN:** Luxury 5-star hotel in Mega Kuningan & Central Business District with 317 rooms and
> 31,200 square feet of event space.
>
> **ID:** Hotel bintang 5 mewah di Mega Kuningan dan kawasan Central Business District dengan
> 317 kamar serta ruang acara seluas 31.200 kaki persegi.

## HTML rules — non-negotiable

Article bodies are Quill markup. **Only text nodes change.** Everything else is copied byte for
byte.

Preserve exactly:

- Tag names, nesting and order.
- **`id` attributes on headings.** `<h2 id="section-mau-nikah-di-bali-…-3">` keeps its
  Indonesian slug and its number. These anchors are linked to from tables of contents; changing
  them breaks links.
- `class`, `style`, `sizes`, `data-src`, `contenteditable`, `rel`, `target`.
- Image `src` URLs and `alt` text values that are generic (`alt="Article image"`).
- `<span class="ql-ui" contenteditable="false"></span>` — these empty spans are Quill list
  bullets. Never drop them.
- `&amp;` and other entities stay encoded.
- Emoji used as visual markers: 📍 💍 ✨ 📸 🔥 👉 🌴 👣 💧 🎶 🏆 😩 💍✨. Keep them in the same
  positions.
- Empty headings such as `<h2 id="…-7"><br></h2>`. They are layout, not content.
- Prices and figures: `Rp 198,000++`, `2.305 m²`, `50–200 pax`, `Up to 3,500`.

### Number formatting — value is preserved, separators are converted

"Never changed" means the **value**, not the punctuation. Indonesian and English use opposite
separators, so an article translated into English must switch them or the number changes meaning:
`5.000 guests` reads as *five* guests to an English reader.

| Indonesian source | English translation |
|---|---|
| `5.000 guests` | `5,000 guests` |
| `2.866 square metres` | `2,866 square metres` |
| `17,8%` | `17.8%` |
| `8,3 metre` | `8.3 metre` |

Currency in rupiah keeps its Indonesian form, because it is a rupiah price either way:
`Rp 198.000++` stays as written. Figures already in English format (`Up to 2,000`, `3,760 m²`)
are left alone. The venue direction is the mirror image: English → Indonesian converts
`31,200` → `31.200` and `2.4 km` → `2,4 km`.
- Brand names: Seven Magic Organizer, 7Magic Organizer, Swissôtel (with the circumflex).

Translate `alt` text only when it carries real meaning; leave `alt="Article image"` alone.

### Self-check before submitting

Strip all text between tags from source and translation. The remaining tag streams must be
identical. If they differ, the translation is rejected.

## Things that are never changed

- Capacities, prices, dates, addresses, phone numbers, URLs.
- Hotel, venue, restaurant and district names.
- The factual claims. If the source says the ballroom holds 3,500 guests, so does the
  translation, even if that seems high.
- Errors in the source stay. `Lucern` is not corrected to `Lucerne`; `officially largest hotel
  ballroom in North Jakarta` stays on the Lausanne and Zurich entries even though it is
  copy-pasted and wrong, because fixing content is not this task.
