# Celebrity wedding watch list

**Researched:** 2026-10-07 · **Window:** mid-October 2026 to about June 2027
**Category on the site:** `pernikahan-selebriti` (en `celebrity-weddings`)

The first celebrity batch (commit `dd9d836`) looked back on weddings that were
months old. Search and Google Discover interest in a celebrity wedding peaks in
the first two days after it happens, and a retrospective piece misses that
window. This list exists so the slow part (background research and
verification) is done before the wedding, and only the day's own details are
left to add afterwards.

## How to publish within 48 hours

**Before the wedding: the parts that will not change.** For each couple marked
CONFIRMED, or showing signs of being close (a pre-wedding medical check, a
pre-wedding shoot, an announced month), write the background in ID and EN now:
who they are, how they met, the lamaran. Run the first independent verification
pass on that brief, exactly as the first batch did. Leave the wedding-day
sections as headings only.

**Wedding day, within 24 hours.** Collect the day's facts: date, venue, adat,
attire and designer, mahar, notable vendors. The couple's own posts come first,
then at least two outlets. Anything that rests on one source, or where outlets
disagree, is dropped rather than guessed. Fill in the sections, then have a
fresh agent run the second verification pass on the finished ID and EN drafts.

**Publish.** Use the normal pipeline: `import_markdown_articles.py`, then
`import_article_translations_md.py`, then `tag_article_clusters.py`, each with
`--commit`, first locally and then on production. Two differences from a normal
batch:

- **Don't backdate.** `published_at` is the real publish time, because being
  first is the whole point here.
- **Use a photo of the couple as the header, with the credit printed on it.**
  Changed on 2026-10-07 at the owner's request; stock scenes were the earlier
  rule. Crop and credit it with `apps/api/scripts/credit_article_photo.py`,
  then upload it to R2 the usual way. A printed credit names the owner, it is
  not a licence: prefer agency press handouts and the couple's own posts, and
  ask the photographer where you can. Roundups with no single couple still use
  an openly licensed scene.

Then paste the URL into WhatsApp and check the preview shows the photo and
headline.

**Weekly.** Every Monday, take out couples who have married (moving any article
to the archive section) and add new engagements. Each addition still needs two
independent sources. Rumours never go on the list.

## Draft now

| Couple | Why now |
|---|---|
| Song Ji-ho & Kim So-ri | Wedding in October 2026, day not announced; may already be within days |
| Asnawi Mangkualam & Yuriska Patricia | Pre-wedding medical check done 30 Sep–1 Oct; detik says "tinggal menghitung hari" (only days away) |
| Yoon Jong-hoon & Han Eun-seo | 1 Nov 2026, Gangnam, Seoul |
| Lee You-jin & Cha Gyeong-eun | 14 Nov 2026, Seoul |
| Kwak Si-yang & Yoo Jiae | 28 Nov 2026 |
| Gege Elisa | Pre-wedding photos posted 3 Oct 2026 |
| Abe Hoed | December 2026, per Melly Goeslaw; day to follow |
| Ji Ye-eun & Vata | 12 Dec 2026 |

Check every spelling against the table below, including the CONFLICT notes, when
drafting begins. A date on this list is the date as reported on 2026-10-07, not
a verified fact for the article.

---

## The list

**Confidence scale.** CONFIRMED means the couple, their family or their agency announced a wedding **date or month**, and two or more outlets carry it. REPORTED means everything else on this list: an engagement with no date, or only a year or a window ("end of 2026 or early 2027"). Rumours are left out. Where the couple themselves stated a year, the Status column says so.

**Private partners.** Partners who are not public figures appear as "partner (private person)", even when the press names them.

---

## Scope 1: Indonesia

Ordered by how soon the wedding looks likely, from the signals we have (pre-wedding medical checks, pre-wedding photo shoots, an announced month).

| Couple (exact spellings) | Status | Expected venue/city | Confidence | Sources |
|---|---|---|---|---|
| **Asnawi Mangkualam** (national-team footballer; full name Asnawi Mangkualam Bahar, IG @asnawi_bhr) & **Yuriska Patricia** (actress/model) | Lamaran 26 Jun 2026, after a proposal on a boat on Danau Beratan, Bedugul, Bali (lake, not sea). Pre-wedding medical check at RS Mitra Keluarga Cibubur, reported 30 Sep–1 Oct. Pre-wedding shoots in Makassar adat dress (late Sep) and a vintage theme (posted by 3 Oct, exact day unconfirmed; Kompas's 4 Oct is wrong). **No wedding date announced.** detik wrote that the wedding was "tinggal menghitung hari" (only days away). Wolipop wrote that the date "belum diketahui" (is not yet known). | Not reported. Both pre-wedding shoots used Makassar/Bugis adat dress. | REPORTED | detikHOT, 2026-10-01: https://hot.detik.com/celeb/d-8686949/asnawi-mangkualam-yuriska-patricia-jalani-mcu-jelang-nikah · Wolipop, 2026-10-04: https://wolipop.detik.com/foto-wedding/d-8692130/gaya-prewedding-terbaru-asnawi-yuriska-patricia-bertema-vintage-yang-glamour · Kompas, 2026-10-05: https://lifestyle.kompas.com/read/2026/10/05/180000620/gaya-prewedding-asnawi-mangkualam-dan-yuriska-patricia-bernuansa-vintage · ANTARA Bengkulu, 2026-09-30: https://bengkulu.antaranews.com/berita/480969/prewedding-asnawi-dan-yuriska-tampil-elegan-berbalut-adat-makassar |
| **Gege Elisa** & partner (private person, not named publicly) | Proposed to in Paris, posted about 22 Mar 2026. On 3 Oct 2026 she posted pre-wedding photos captioned "...sebelum mengucap 'i do' #prewedding". **No date announced.** | Not reported | REPORTED | detikHOT, 2026-03-22: https://hot.detik.com/celeb/d-8410804/kabar-bahagia-dari-gege-elisa · detikHOT, 2026-10-03: https://hot.detik.com/celeb/d-8690918/gege-elisa-otw-nikah-calon-suaminya-bikin-penasaran · KapanLagi, 2026-03-24: https://www.kapanlagi.com/foto/berita-foto/indonesia/potret-gege-elisa-dilamar-sang-kekasih-di-paris-romantis-dan-penuh-kehangatan.html |
| **Prinsa Mandagie** (singer) & partner (pilot, private person) | Lamaran reported 27 Mar 2026. Pre-wedding photos in classic Javanese dress, 10 Sep 2026. **No date announced.** | Not reported | REPORTED | detikHOT, 2026-03-27: https://hot.detik.com/celeb/d-8416285/kabar-bahagia-dari-prinsa-mandagie · detikHOT, 2026-09-10: https://hot.detik.com/celeb/d-8656370/foto-prewedding-prinsa-mandagie-sangga-barkah-bernuansa-jawa-klasik · Medcom, 2026-09-10: https://www.medcom.id/hiburan/musik/JKR2eDOK-segera-menikah-foto-prewedding-prinsa-mandagie-dan-sangga-bikin-pangling |
| **Muhammad Shohibul Fikri** (badminton, men's doubles) & **Lisa Ayu Kusumawati** (badminton, former mixed doubles) | Lamaran reported Jan 2026. Engagement ceremony 28 Mar 2026. Pre-wedding photos, 3 Sep 2026. **No date announced.** | Not reported | REPORTED | KapanLagi, 2026-09-03: https://www.kapanlagi.com/foto/berita-foto/indonesia/potret-shohibul-fikri-dan-lisa-ayu-kusumawati-prewedding-makin-dekat-ke-pelaminan.html · Okezone Women, 2026-07-29: https://women.okezone.com/read/2026/07/29/612/3232930/profil-dan-potret-cantik-lisa-ayu-tunangan-shohibul-fikri-yang-baru-juara-japan-dan-china-open-2026 |
| **Abe Hoed** (son of Melly Goeslaw & Anto Hoed; full name "Pria Bernama Hoed") & partner (daughter of Bambang Soesatyo, private person) | Lamaran Saturday 26 Sep 2026 in Jakarta. Melly Goeslaw said the akad and resepsi will both be in **December 2026**, with the exact date to follow. The couple plan to start master's degrees in early 2027. | Not reported (lamaran was in Jakarta) | **CONFIRMED** (month, from the family) | detikHOT, 2026-09-28: https://hot.detik.com/celeb/d-8681698/abe-hoed-dan-putri-bamsoet-bakal-menikah-desember-2026 · Harapan Rakyat, 2026-09-28: https://www.harapanrakyat.com/2026/09/abe-hoed-dan-putri-bamsoet-akan-menikah-lamaran-digelar-26-september-2026/ |
| **DJ Una** & partner (businessman, private person) | Lamaran 26 Jun 2026. Una said "kalau nggak tahun ini mungkin masih awal tahun depan" (if not this year, then probably early next year). Akad and reception will be in Jakarta. **No update since late June.** | Jakarta | REPORTED (window stated by the couple) | Liputan6, 2026-06-29: https://www.liputan6.com/showbiz/read/8062400/dj-una-dan-andi-agum-bocorkan-jadwal-pernikahan-mereka-akan-digelar-di-jakarta · Tribunnews, 2026-06-27: https://www.tribunnews.com/seleb/7847201/dj-una-target-menikah-tahun-ini-rela-geser-jadwal-kerja-demi-acara-lamaran |
| **Azriel Hermansyah** & **Sarah Menzel** (full name Sarah Rai Menzel) | Engaged Jun 2024. Azriel said on 29 Sep 2026 that preparations are 80% done and the wedding is "tahun depan" (**2027**), in Bali. **No month announced.** Lamaran date CONFLICT: 27 Jun 2024 (most outlets, his 24th birthday) vs 28 Jun 2024 (one Popmama piece). | Bali | REPORTED (year, from Azriel himself) | Okezone, 2026-09-29: https://celebrity.okezone.com/read/2026/09/29/33/3244864/persiapan-nikah-sudah-80-persen-azriel-hermansyah-pastikan-gelar-acara-di-bali-tahun-depan · Inilah.com, 2026-09-29: https://www.inilah.com/azriel-hermansyah-dan-sarah-menzel-spill-pernikahan-tahun-depan-acara-digelar-di-bali · Tribunnews headline, 2026-10-06 ("...Mantap Nikahi Sarah Menzel pada 2027") |
| **Hana Malasan** & **Sean Gelael** (racing driver) | Proposal at Nihi, Sumba, posted 31 Oct 2025. Family lamaran on **Saturday 15 Aug 2026** at NuArt Sculpture Park, Bandung. **No wedding date announced.** RCTI+/iNews called 15 Aug a "Jumat" (Friday), but it was a Saturday, as Kompas and Okezone say. | Not reported (lamaran was in Bandung) | REPORTED | Kompas, 2026-08-15: https://entertainment.kompas.com/read/2026/08/15/194656766/hana-malasan-dan-sean-gelael-gelar-acara-lamaran · Okezone, 2026-08-15: https://celebrity.okezone.com/read/2026/08/15/33/3236427/hana-malasan-dan-sean-gelael-gelar-lamaran-setelah-2-tahun-pacaran · VIVA, 2026-08-16: https://www.viva.co.id/gaya-hidup/showbiz/1921719-bakal-jadi-menantu-rini-s-bono-ini-sosok-hana-malasan-yang-resmi-tunangan-dengan-sean-gelael |
| **Jeje Slebew** (influencer) & **Rio Ramadhan** (FTV actor) | Proposal posted about 8–9 Sep 2026. The couple said "InsyaAllah tahun depan" (next year, **2027**). Grid reported "awal tahun depan" (early next year). A meeting between the two families is planned for Nov 2026. | Not reported | REPORTED | Grid, 2026-09-20: https://www.grid.id/read/044414097/profil-rio-ramadhan-mantan-kekeyi-yang-akan-menikahi-jeje-slebew-sebut-akan-undang-sang-selebgram · Medcom, 2026-09-09: https://www.medcom.id/hiburan/montase/Dkq1OnRk-rio-ramadhan-lamar-jeje-slebew-setelah-6-bulan-pacaran-siap-menikah · detikHOT, 2026-09-10: https://hot.detik.com/celeb/d-8656007/banyak-doa-baik-usai-jeje-slebew-dilamar-rio-ramadhan |
| **Leony** (former child singer; outlets write "Leony", "Leony Vitria" and "Leony VH", IG @leonyvh) & partner (New Zealand-based, private person) | Engagement announced 17–18 Sep 2026. **No date.** | Not reported | REPORTED | CNN Indonesia, 2026-09-18: https://www.cnnindonesia.com/hiburan/20260918152704-234-1405488/leony-vitria-bertunangan-dengan-kekasihnya-charles-seaman · detikHOT, 2026-09-18: https://hot.detik.com/celeb/d-8667876/so-sweet-leony-umumkan-dilamar-pacar-bule |
| **Jerome Polin** (YouTuber) & partner (private person) | Proposed at Mt Fuji, announced 27 Sep 2026. **No date.** | Not reported | REPORTED | Kompas, 2026-09-27: https://entertainment.kompas.com/read/2026/09/27/145720466/jerome-polin-lamar-gracia-caroline-berlatar-gunung-fuji-jepang · Okezone, 2026-09-27: https://celebrity.okezone.com/read/2026/09/27/33/3244476/jerome-polin-lamar-gracia-caroline-gunung-fuji-jadi-saksi |
| **Puteri Modiyanti** (daughter of Tommy Soeharto & Sandy Harun) & partner (businessman, private person) | Proposed at Lake Kawaguchiko, Japan, posted about 29 Sep 2026. **No date.** Spelling CONFLICT: Kompas, detik and KapanLagi write "Puteri Modiyanti"; SINDOnews writes "Putri Moediyanti". | Not reported | REPORTED | Kompas, 2026-10-01: https://entertainment.kompas.com/read/2026/10/01/154304166/profil-puteri-modiyanti-anak-sandy-harun-yang-baru-dilamar-pengusaha · detikHOT, 2026-09-30: https://hot.detik.com/celeb/d-8685731/momen-romantis-puteri-modiyanti-anak-tommy-soeharto-dilamar-di-danau-kawaguchiko |
| **Marion Jola** & **Dennis Talakua** (guitarist) | Proposal at Candi Prambanan, posted Sunday 20 Sep 2026. Marion said it is "gak mungkin tahun ini" (not possible this year) and that a Sumba belis custom comes first. **Earliest 2027. No date.** | Not reported | REPORTED | detikHOT, 2026-09-20: https://hot.detik.com/celeb/d-8671265/so-sweet-marion-jola-dilamar-dennis-talakua-di-pelataran-prambanan · Sudutpandang, 2026-09-30: https://sudutpandang.id/usai-dilamar-kekasih-marion-jola-akui-tak-menikah-tahun-ini/ · ANTARA, 2026-09-25: https://www.antaranews.com/berita/5757720/profil-dennis-talakua-gitaris-yang-melamar-marion-jola |
| **Yoriko Angeline** & **Aldio Oekon** (racing driver) | Proposed in Paris, early Sep 2026. **No date.** detik also carried "Yoriko Angeline Pilih Gak Buru-buru Nikah" (Yoriko chooses not to rush the wedding). | Not reported | REPORTED | ANTARA, 2026-09-04: https://www.antaranews.com/berita/5725339/profil-yoriko-angeline-artis-yang-dilamar-aldio-oekon-di-paris · detikHOT, 2026-09-25: https://hot.detik.com/celeb/d-8678131/impian-jadi-nyata-yoriko-angeline-bahagia-dilamar-di-prancis |
| **Maizura** (actress/singer, IG @maiiizura) & partner (private person) | Mappetuada (Bugis lamaran), 19 Apr 2026. Pre-wedding photos in Bugis dress, posted 29 Jul 2026. **No date.** See the note below the table about an August "batal menikah?" piece. | Not reported | REPORTED | detikHOT, 2026-04-19: https://hot.detik.com/celeb/d-8451365/maizura-dilamar-calon-suaminya-bikin-penasaran · detikHOT, 2026-07-29: https://hot.detik.com/celeb/d-8594990/maizura-anggun-dalam-balutan-busana-adat-modern · IDN Times, 2026-04-21: https://www.idntimes.com/hype/entertainment/aktris-dan-penyanyi-maizura-dilamar-kekasih-dengan-adat-bugis-00-ccqh2-m18tls |
| **Maria Simorangkir** (Indonesian Idol 2018 winner) & partner (private person) | Proposal announced 4–5 Jul 2026. **No date.** | Not reported | REPORTED | Kompas, 2026-07-05: https://www.kompas.com/hype/read/2026/07/05/082630966/selamat-maria-simorangkir-resmi-dilamar-kekasih · Okezone, 2026-07-04: https://celebrity.okezone.com/read/2026/07/04/33/3228130/congrats-maria-simorangkir-resmi-dilamar-sang-kekasih |
| **Frislly Herlind** & **Difa Ryansyah** (former Idola Cilik singer; full name Muhammad Difa Ryansyah; Liputan6 once wrote "Difa Riansyah") | Lamaran 1 Jan 2026. **No date, and no wedding news since January.** | Not reported | REPORTED | detikHOT, 2026-01-02: https://hot.detik.com/celeb/d-8288550/tahun-baru-frislly-herlind-ganti-status-usai-dilamar-difa-ryansyah · Suara, 2026-01-02: https://www.suara.com/entertainment/2026/01/02/103130/selamat-frislly-herlind-dilamar-sang-kekasih |
| **Naomi Zaskia** & partner (private person) | Engaged. **CONFLICT on when:** IDN Times (31 Oct and 2 Nov 2025) reports a proposal on stage at the Laleilmanino & Friends concert. Popmama dates that proposal 30 Nov 2025. detik (20 Jul 2026) quotes her IG story saying "engaged since 2024". **No wedding date.** Outlets also spell the partner's name two ways. | Not reported | REPORTED | detikHOT, 2026-07-20: https://hot.detik.com/celeb/d-8581157/naomi-zaskia-sudah-tunangan-dengan-albi-mardhani · IDN Times, 2025-11-02: https://www.idntimes.com/hype/entertainment/momen-naomi-zaskia-dilamar-saat-konser-laleilmanino-00-ccqh2-l88d67 |
| **Bernadette Gainara** (influencer; Gora Juara writes "Bernadette Cyan Gainara") & **Erick Fathoni** (swimmer) | Proposed in Sydney, late Jul 2026. **No date.** | Not reported | REPORTED | detikHOT, 2026-07-30: https://hot.detik.com/celeb/d-8595423/bernadette-gainara-dilamar-perenang-erick-fathoni-di-australia · Gora Juara, 2026-07-28: https://www.gorajuara.com/ragam/10017434433/selamat-influencer-bernadette-cyan-gainara-dilamar-atlet-renang-erick-fathoni-pada-penghujung-juli-2026 |
| **Leonardo Edwin** (YouTuber) & partner (private person) | Beach proposal announced about 23–24 Aug 2026. **No date.** | Not reported | REPORTED | KapanLagi, 2026-08-24: https://www.kapanlagi.com/showbiz/selebriti/potret-leonardo-edwin-melamar-sang-kekasih-romantis-di-kala-senja-8936a1f4.html · IDN Times, 2026-08-23: https://www.idntimes.com/life/relationship/gaya-catharina-benita-dilamar-leonardo-edwin-00-mm7zv-vbkh47 |
| **Nadhif Basalamah** (singer) & partner (private person) | Proposed at Kawaguchiko, Japan, 26 Jan 2025. Popmama still listed him among upcoming weddings in Apr 2026. **No date, and no wedding news found.** | Not reported | REPORTED | KapanLagi, 2025-01-26 (Google News listing) · Haibunda, 2025-01-28: https://www.haibunda.com/trending/20250128133735-95-358565/romantis-5-potret-nadhif-basalamah-lamar-taska-amani-berlatar-gunung-fuji-di-jepang · Popmama, 2026-04-27: https://www.popmama.com/life/relationship/seleb-laki-laki-ini-bakal-menikah-menyusul-el-rumi-00-1xg6q-7fdtnl |
| **Shanty** (pop singer) & partner (private person) | Proposed by the sea, posted early Feb 2026. **No date, and no wedding news since.** | Not reported | REPORTED | KapanLagi, 2026-02-09: https://www.kapanlagi.com/foto/berita-foto/indonesia/momen-shanty-dilamar-di-usia-47-tahun-romantis-di-tepi-laut.html · IDN Times, 2026-02-09: https://www.idntimes.com/hype/entertainment/penyanyi-shanty-dilamar-kekasih-siap-lepas-status-janda-00-6x7yf-n9dtnp |

### Wedding year stated, but no engagement yet

| Couple | Status | Venue | Confidence | Sources |
|---|---|---|---|---|
| **Dul Jaelani** & **Tissa Biani** | No lamaran reported. Ahmad Dhani said on 5–7 May 2026: "Dul akan menikah tahun depan atau 2027" (Dul will marry next year, in 2027). He promised a lavish party rather than a ceremony at the KUA (religious affairs office). **No month.** | Not reported | REPORTED (year, from the father) | Tribunnews Depok, 2026-05-07: https://depok.tribunnews.com/seleb/50078/ahmad-dhani-tolak-keras-dul-jaelani-nikah-di-kua-siapkan-pesta-mewah-di-2027 · Nyata Media, 2026-05-08: https://nyatamedia.com/08052026-dibocorkan-ahmad-dhani-pernikahan-dul-jaelani-dan-tissa-biani-akan-digelar-2027 |
| **Bastian Steel** & **Sitha Marino** | Not engaged. Sitha had earlier apologised for a "tunangan" (engagement) prank post. **CONFLICT:** Bastian told Kompas (26 May 2026) he hopes to marry in **2027** with Batak adat. detik (28 Aug 2026) wrote that they are "disebut-sebut" (said to be) planning a reception at the **end of 2026**, and both deflected when asked. | Not reported | REPORTED | Kompas, 2026-05-26: https://entertainment.kompas.com/read/2026/05/26/145302066/bastian-steel-serius-nikahi-sitha-marino-2027-siap-pesta-adat-batak · detikHOT, 2026-08-28: https://hot.detik.com/celeb/d-8638363/jawaban-bastian-steel-dan-sitha-marino-disinggung-soal-rencana-nikah-tahun-ini |

**Note on Maizura.** Jatim Network ran a "fakta atau tidak?" (fact or not?) piece on 6 Aug 2026 about a "batal menikah" (called-off wedding). No mainstream outlet carried it, and nothing confirms it. Before drafting, check that the engagement is still on.

**Note on Abe Hoed's partner.** Outlets spell her name three different ways. She is a private person, so the article should not name her unless the couple's own accounts do, and then in their spelling.

---

## Scope 2: International (capped at 6, all with confirmed dates or months)

| Couple (exact spellings) | Status | Expected venue/city | Confidence | Sources |
|---|---|---|---|---|
| **Song Ji-ho** (Lovely Runner; also written "Song Jiho" / "Song Ji Ho") & **Kim So-ri** (singer-actress; also written "Kim So Ri" / "Kim Sori") | Wedding in **October 2026, exact day not given**. Both posted handwritten letters. Agency Inyeon Entertainment. **CONFLICT on the announcement date:** RRI and Chosun say 6 Oct 2026; SINDOnews says "10 Juni 2026", which is probably an error. The wedding could fall before the mid-October window opens. | Not reported | **CONFIRMED** (month) | RRI, 2026-10-06: https://rri.co.id/hiburan/2791204/aktor-song-ji-ho-dan-kim-so-ri-umumkan-pernikahan-digelar-oktober-2026 · Chosun English, 2026-10-06: https://www.chosun.com/english/kpop-culture-en/2026/10/06/MSH36QCIYVC2JAAJXK2DP2KZ5A/ · SINDOnews, 2026-10-06: https://lifestyle.sindonews.com/read/1757439/600/song-ji-ho-dan-kim-so-ri-akan-menikah-oktober-2026-1791263454 |
| **Yoon Jong-hoon** (The Penthouse) & **Han Eun-seo** | **1 Nov 2026**, confirmed by agency YK Media Plus. | Gangnam, Seoul | **CONFIRMED** | Okezone, 2026-09-08: https://celebrity.okezone.com/read/2026/09/08/33/3240775/yoon-jong-hoon-dan-han-eun-seo-umumkan-akan-menikah-berawal-dari-drama-return · Viu Indonesia, 2026-09-20: https://www.viu.com/ott/id/articles/aktor-the-penthouse-yoon-jong-hoon-akan-menikah-dengan-han-eun-seo/ |
| **Lee You-jin** & **Cha Gyeong-eun** | **14 Nov 2026**, private ceremony. Announced 6 Oct 2026 together with Cha's pregnancy. | Undisclosed location in Seoul | **CONFIRMED** | Medcom, 2026-10-06: https://www.medcom.id/hiburan/film/yKXe3a4N-lee-you-jin-dan-cha-gyeong-eun-segera-menikah-november-ini · detik, 2026-10-06: https://www.detik.com/pop/korean-wave/d-8694885/cha-gyeong-eun-umumkan-hamil-nikah-dengan-lee-you-jin |
| **Kwak Si-yang** & **Yoo Jiae** (Lovelyz) | **28 Nov 2026**, private, confirmed by 9Ato Entertainment. | Not disclosed | **CONFIRMED** | Wolipop, 2026-09-03: https://wolipop.detik.com/entertainment-news/d-8647203/kwak-si-yang-yoo-jiae-go-public-mantap-menikah-setelah-1-tahun-pacaran · RCTI+, 2026-09-03 ("akhir November"): https://www.rctiplus.com/news/detail/seleb/5465633/kwak-si-yang-dan-yoo-jiae-bakal-menikah-akhir-november-2026 |
| **Ji Ye-eun** (Running Man) & **Vata** (WeDemBoyz leader) | **12 Dec 2026**, which is Vata's birthday. Confirmed by CP Entertainment and A-RA. | Not reported | **CONFIRMED** | CNN Indonesia, 2026-09-02: https://www.cnnindonesia.com/hiburan/20260902090710-234-1399019/ji-ye-eun-dan-vata-bakal-menikah-desember-2026 · Wolipop, 2026-09-02: https://wolipop.detik.com/entertainment-news/d-8645043/teman-satu-gereja-ji-ye-eun-vata-cinlok-hingga-berlanjut-ke-pernikahan |
| **Baek Jin-hee** & partner (non-celebrity, Canada-based, private person) | **23 Jan 2027**, announced by her management, AM9. | Not reported | **CONFIRMED** | detik, 2026-09-09: https://www.detik.com/pop/korean-wave/d-8654786/baek-jin-hee-tulis-surat-buat-fans-jelang-pernikahan · detik, 2026-09-07: https://www.detik.com/pop/korean-wave/d-8652191/aktris-baek-jin-hee-umumkan-pernikahan-bakal-tinggal-di-kanada · Medcom, 2026-09-09: https://www.medcom.id/hiburan/film/8Kyxa3rk-baek-jin-hee-umumkan-rencana-pernikahan-kisah-cinta-ldr-korea-kanada |

---

## Dropped, and why

**Already married before 2026-10-07**
- Hessel Steven & Sandy: married 26 Jul 2026 (detikHOT).
- Agnes Naomi: church ceremony around 26 Sep 2026 (IDN Times). She was engaged in July.
- Gisela Cindy: married in Canada, Aug 2026 (VIVA, Okezone).
- Nadin Amizah & Faishal Tanjung: already married, "setahun nikah" (one year married) per detikHOT, Aug 2026.
- Andre Taulany & Amanda Rigby: married 20 Sep 2026.
- Mario Caesar & Givina Lukita: married 20 Sep 2026.
- Axel Matthew Thomas: married Sep 2026.
- Also married: Dikta & Rachel Florencia (Aug), Dea Annisa & Mazaki Ahmad (Aug), Irma Darmawangsa (Sep), Jerry Andrean & Stefani Horison (Oct), Rizky Irmansyah (Aug), Christian Wilfandio (Sep), Harry Vaughan & Nevy Tania (Sep), Nathalie Holscher (Jul), Pinkan Mambo & Arya Khan (reception Jun), Ochi Rosdiana (Feb 2025).
- January–May 2026 weddings, per Popbela: Ayushita, Shindy Huang, Ranty Maria, Jaz Hayat, Virgoun, Teuku Rassya, Gabriella Larasati, Indian Akbar and others.
- The 10 couples the site already covered.

**Called off**
- Riza Syah & Claudia Andhara: engaged 14 Feb 2026, split about Sep 2026 (Okezone, 14 Sep).
- Amal Buton (Arie Kriting's brother): died 24 Sep 2026, before his 10 Oct wedding.

**Stale or misdated items** (KapanLagi photo galleries re-surface in Google News with new dates)
- Thalita Latief & Dennis Lyla: the gallery is from 2012. They divorced in 2021.
- Ayu Ting Ting "pedang pora" (military-style wedding): a 2024 story. That engagement ended in 2024.

**No engagement, only speculation**
- Aura Kasih: says she plans to remarry; partner unnamed.
- Jonathan Frizzy & Ririn Dwi Ariyanti: speculation only.
- Sintya Marisca: her "engagement" was film promotion.
- Kylie Jenner & Timothée Chalamet: not engaged; they were wedding guests in Saint-Tropez.
- Zendaya & Tom Holland: a wedding celebration was reported in Aug 2026, and Law Roach says it was not an "official" ceremony. Their status is unclear and the event has already happened.

**Only one source found**
- Muhammad Ferarri (national-team footballer): lamaran reported by IDN Times only, 22 Jun 2026.

**Left out of Scope 2 by the cap of 6, or for lack of a date**
- Madison Beer & Justin Herbert: engaged Jul 2026, no date.
- Post Malone & Christy Lee: engaged Aug 2026, no date.
- Jang Dong-yoon & Kim Seung-yoon ("this year"), Won Hyun-joon & Lee Su-jin, Bae Na-ra & Han Jae-ah, Alisha Lehmann & Montel McKenzie: not checked against two sources.
