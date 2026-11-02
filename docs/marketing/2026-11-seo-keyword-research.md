# Riset kata kunci SEO, November 2026

**Tanggal:** 2 November 2026
**Pasar:** Jakarta (Indonesia), Bali (Indonesia + Inggris: Australia dan internasional), Singapura (sebagian besar Inggris). Kota lain sengaja tidak dibahas, kecuali kueri yang jelas mengarah ke Jakarta.
**Status:** Riset dan perencanaan saja. Belum ada artikel yang ditulis, belum ada perubahan kode atau DB.
**Koreksi setelah penulisan (2 Nov 2026):** SKB libur nasional dan cuti bersama 2027 **sudah terbit** (No. 1205/3/2 Tahun 2026, 15 Sep 2026), jadi baris "belum terbit" di §2 dan §6 sudah usang. Rajab 1448 H menurut kalender Hijriah Kemenag mulai **Kamis 10 Des 2026**; "±11 Des" di §2 adalah Rejeb Jawa. Tahun janda 2027 ternyata disebut eksplisit oleh sumber (Kwong Wah Yit Poh, 2024, dan dua tulisan praktisi di Sohu, Okt 2026). Kedua belas artikel di §4 sudah ditulis; lihat `apps/api/scripts/finish_article_2026_11.py`.
**Dokumen pendamping:** `2026-editorial-calendar.md`, `2026-08-16-seo-technical-strategy.md`, `ads/2026-08-01-google-ads-plan.md`, `celebrity-wedding-watchlist.md`.

---

## 1. Metode dan batas data

### Yang benar-benar dipakai

| Sinyal | Cara | Catatan |
|---|---|---|
| **Google Autocomplete** | `suggestqueries.google.com` (`client=firefox`), diambil 2 Nov 2026. `hl=id&gl=id` untuk Jakarta dan Bali-Indonesia, `hl=en&gl=au` untuk Bali-Australia, `hl=en&gl=sg` untuk Singapura. Sekitar 150 seed, termasuk ekspansi dengan modifier (tahun, wilayah, "berapa", "syarat"). | Saran autocomplete menunjukkan bahwa sebuah kueri **ada** dan cukup sering dicari sampai Google menyarankannya. Urutannya **bukan** peringkat volume. Endpoint sempat membatasi permintaan (rate limit); seed yang gagal diulang dengan jeda. |
| **Hasil penelusuran** | Tool WebSearch. **Lokasinya di AS, bukan google.co.id atau google.com.sg**, jadi daftar situs yang ranking hanya perkiraan, bukan posisi SERP lokal. | Dipakai untuk melihat siapa yang menerbitkan konten untuk sebuah kueri dan untuk memeriksa fakta (tanggal, aturan). |
| **Inventaris 7Magic** | `sitemap.xml` live (821 URL, 201 URL `/artikel/`), `apps/web/content/articles/` (95 ID, 46 EN), rute landing page di `apps/web/src/routes/`. | Banyak artikel lama hanya ada di DB, tidak punya Markdown. Pemeriksaan duplikat dilakukan ke sitemap, bukan hanya ke folder Markdown. |

### Yang tidak tersedia

- **Tidak ada volume pencarian, CPC, atau angka kesulitan.** Tidak ada Keyword Planner, Ahrefs, Semrush, atau Search Console dalam sesi ini. Semua label permintaan di bawah adalah **estimasi relatif**.
- **Google Trends tidak diambil.** Klaim musiman di dokumen ini berasal dari kalender (Ramadan, Imlek, musim hujan), bukan dari kurva Trends.
- **Tidak ada pemeriksaan posisi 7Magic.** Rekomendasi pertama di §5: tarik data Search Console sebelum memfinalkan rencana.

### Cara membaca label permintaan

- **Tinggi:** kueri muncul sebagai saran di seed yang luas (misalnya `bali wedding` → `bali wedding guest dress`) **dan** seed-nya sendiri menghasilkan 8–10 varian.
- **Sedang:** seed-nya menghasilkan 5–10 varian, tapi tidak muncul dari seed yang lebih luas.
- **Rendah:** 0–3 saran.
- **Persaingan** dinilai dari situs yang muncul di hasil penelusuran (situs media besar, portal pemerintah, atau situs nikah mapan dibanding blog kecil dan halaman paket hotel).

---

## 2. Penanda musim November 2026 sampai awal 2027

| Penanda | Tanggal | Status | Sumber |
|---|---|---|---|
| Rajab 1448 H | ±11 Des 2026 – 9 Jan 2027 | Dari kalender Kemenag, dikutip di artikel `bulan-baik-menikah-2027-kalender-jawa` | file Markdown repo |
| Syakban 1448 H | ±10 Jan – 7 Feb 2027 | sama | sama |
| **Imlek 2027 (Tahun Kambing Api)** | **Sabtu 6 Feb 2027** | Tanggal astronomis sudah pasti; status libur menunggu SKB 2027 | [officeholidays](https://www.officeholidays.com/holidays/indonesia/chinese-new-year), [Popmama](https://www.popmama.com/life/health/tahun-2027-shio-apa-00-wjk9l-spyfms) |
| **1 Ramadan 1448 H** | **±Senin 8 Feb 2027** | Muhammadiyah (KHGT) dan perhitungan BRIN/MABIMS sama-sama 8 Feb; pemerintah menunggu sidang isbat | [Metro TV](https://www.metrotvnews.com/read/KYVC0XgP-prediksi-awal-ramadan-dan-lebaran-2027-versi-brin), [Haibunda](https://haibunda.com/moms-life/20260918115713-76-397705/prediksi-awal-ramadhan-2027-jadwal-libur-lebaran-1448-h) |
| Idulfitri 1448 H | 9 Mar (Muhammadiyah) atau ±10 Mar 2027 (MABIMS) | belum resmi | sama |
| SKB libur nasional dan cuti bersama 2027 | — | **Belum terbit** menurut kalenderku.id; satu klaim Fortune IDN soal SKB bertentangan dengan sumber lain | [Fortune IDN](https://www.fortuneidn.com/news/berapa-bulan-lagi-puasa-2027-d7w02-00-fykp7-70cs1r) |
| Musim hujan Bali | ±Nov–Mar | umum diketahui; tidak diverifikasi untuk 2026/27 | — |

**Dua temuan yang membentuk rencana:**

1. **Imlek (6 Feb) dan awal Ramadan (±8 Feb) hanya berjarak dua hari di 2027.** Jendela "menikah sebelum puasa" bagi keluarga Muslim dan jendela "menikah sebelum Imlek" bagi keluarga Tionghoa tertutup pada minggu yang sama. Kedua kelompok sedang mengunci venue Desember–awal Februari **sekarang**. Ini alasan "kenapa sekarang" yang paling kuat bulan ini, dan berlaku di Jakarta maupun Singapura.
2. **Tahun Kambing 2027 tampaknya merupakan "tahun janda" (寡妇年, tahun tanpa lichun).** Lichun 2027 jatuh 4 Feb 2027, dua hari *sebelum* Imlek 6 Feb, dan lichun 2028 (±4 Feb 2028) jatuh *setelah* Imlek 2028 (26 Jan 2028). Jadi tahun lunar Kambing tidak memuat lichun. **Ini kesimpulan saya dari tanggal-tanggal tersebut. Belum ada sumber yang menyebut 2027 sebagai tahun janda secara eksplisit.** Definisinya: [SCMP explainer](https://scmp.com/news/people-culture/trending-china/article/3249490/explainer-what-widow-year-why-do-chinese-believe-it-bad-time-marry-and-how-break-curse); contoh pasangan di Tiongkok yang mengejar tanggal sebelum tahun janda: [Asia News Network](https://asianews.network/couples-in-china-race-against-widow-year-belief). Kalau benar, kepercayaan ini mendorong keluarga Tionghoa (Jakarta dan Singapura) memajukan pernikahan ke sebelum 6 Feb 2027. Di Singapura muncul saran autocomplete `widow years surcharge` dan `2027 year of the goat marriage`; di Indonesia muncul `tahun janda kapan` dan `menikah di tahun kambing`.

**Harbolnas 11.11 / 12.12:** tidak ada saran autocomplete yang mengaitkan Harbolnas dengan pernikahan (`11.11 wedding` dan `12.12 wedding` kosong atau tidak relevan). Yang ada hanya `promo wedding akhir tahun` (Rendah–Sedang). **Tidak layak jadi artikel.** Kalau ada promo venue sungguhan, lebih cocok ditaruh di landing page atau dikirim lewat WhatsApp.

**Pameran pernikahan:** `jakarta wedding festival 2026`, `wedding expo jakarta 2027`, dan `jakarta wedding expo 2026` muncul, termasuk di autocomplete Singapura. Tapi jadwal Nov–Des 2026 tidak ditemukan di sumber yang bisa dicek ([hasil penelusuran](https://www.metrotvnews.com/play/k8oCQqAE-grand-wedding-expo-2026-ungkap-tren-konsep-pernikahan-tahun-ini) hanya menyebut Grand Wedding Expo 16–18 Jan 2026). Jangan ditulis sampai tanggal 2027 dari penyelenggara bisa dikonfirmasi.

---

## 3. Klaster kata kunci

Kolom "Cakupan 7Magic" merujuk slug live (sitemap) atau landing page. ⚠ = tumpang tindih dengan artikel yang sudah ada.

### 3a. Jakarta (Indonesia)

| Kata kunci | Intent | Permintaan (relatif) + bukti | Persaingan | Cakupan 7Magic |
|---|---|---|---|---|
| `tanggal cantik 2027`, `tanggal cantik 2027 untuk menikah`, `tanggal cantik 2027 weekend` / `hari sabtu` / `hari minggu` / `menurut islam`, `tanggal cantik menikah 2027`, `tanggal cantik januari 2027` | Informasional | **Tinggi.** Seed menghasilkan 10 varian; `tanggal cantik menikah` sudah melengkapi ke `2027` di posisi pertama. | Sedang. Popmama ([31 tanggal cantik 2027](https://www.popmama.com/life/relationship/31-tanggal-cantik-tahun-2027-untuk-menikah-00-k4xm8-zy13m7)), Popbela, Sonora. Daftarnya dangkal: hanya angka kembar, tanpa benturan dengan libur, Ramadan, atau Imlek. | Ada versi 2026 (`tanggal-cantik-pernikahan-2026-inspirasi-kalender-lengkap-dari-januari-sampai-desember`, hanya di DB). Belum ada versi 2027. |
| `tanggal baik menikah 2027` + `menurut islam` / `menurut jawa` / `menurut primbon jawa` / **`menurut cina`**, `tanggal baik menikah di bulan rajab 2027`, `... syawal 2027` | Informasional | **Tinggi** (10 varian) | Versi Jawa: sedang. Versi Tionghoa dalam bahasa Indonesia: **tipis**; hasilnya didominasi [masterseanchan.com](https://www.masterseanchan.com/auspicious-wedding-dates-january-2027/) berbahasa Inggris. | `bulan-baik-menikah-2027-kalender-jawa` ⚠ **ada di Markdown tapi 404 di live** (lihat §5) |
| `nikah bulan rajab`, `menikah bulan rajab menurut islam` / `menurut jawa`, `bolehkah menikah bulan rajab`, `bulan rajab 2026 jatuh pada tanggal`, `menikah sebelum bulan puasa`, `apakah boleh nikah sebelum puasa`, `ramadhan 2027 kapan` | Informasional | **Sedang–Tinggi.** `rajab 2026` dan `ramadhan 2027` masing-masing 10 varian; `nikah bulan rajab` 9 varian. | Sedang (portal Islam umum). Hampir tidak ada yang menghubungkannya dengan logistik pernikahan seperti antrean KUA dan booking venue. | `menikah-di-bulan-ramadan` dan `bolehkah-menikah-di-bulan-ramadan-...` ⚠ (dua artikel saling makan untuk topik yang sama) |
| `tahun 2027 shio apa` (+ `yang ciong`, `unsur apa`), `menikah di tahun kambing`, `tahun janda kapan`, `menikah sebelum imlek`, `imlek 2027 tanggal berapa` | Informasional | **Sedang.** `tahun 2027 shio` 10 varian; `tahun janda` 7; `menikah sebelum imlek` 1. | Rendah untuk sudut pernikahan. Tidak ada artikel Indonesia soal 2027 sebagai tahun janda. | `menentukan-tanggal-pernikahan-weton-shio` (masih membahas 2026), `kecocokan-pasangan-menurut-ba-zi`, alat `/wedding-tools/kalkulator-bazi-pasangan` |
| `biaya nikah jakarta`, `biaya nikah di jakarta 2026`, `biaya nikah kua jakarta`, `biaya nikah gedung jakarta`, `biaya nikah hotel jakarta`, `biaya nikah katedral jakarta`; `biaya resepsi pernikahan di gedung` / `di hotel` | Komersial | **Tinggi.** 10 varian; `biaya nikah` sendiri melengkapi ke `di kua 2026`. Di Singapura juga muncul `wedding cost in jakarta`. | Sedang. Belum ada rincian Jakarta 2026 yang baru; angka yang beredar dari 2023 atau tanpa tanggal ([CNBC 2023](https://www.cnbcindonesia.com/mymoney/20230209162900-72-412524/nikah-di-kua-saja-atau-resepsi-kamu-pilih-mana/amp)). Biaya resmi KUA jelas: Rp0 di KUA pada jam kerja, Rp600.000 di luar KUA ([Metro TV](https://www.metrotvnews.com/read/NleC9W7W-calon-pengantin-wajib-tahu-berikut-biaya-nikah-di-kua-2026)). | Hub `/wedding-venue/jakarta`, `intimate-wedding-100-tamu-jakarta-rincian-biaya` (⚠ harga hasil estimasi model, belum diverifikasi) |
| `gedung pernikahan jakarta selatan` / `timur` / `utara` / `pusat` / `barat` (+ `murah`, `mewah`); pola yang sama untuk `venue pernikahan`, `paket wedding`, `paket pernikahan`, `wedding organizer`, `intimate wedding` | Lokal/komersial | **Tinggi.** Setiap seed kepala melengkapi ke kelima wilayah Jakarta. | Tinggi (Local Pack, Bridestory). Long tail berbudget masih terbuka (lihat rencana Ads). | Hub `/wedding-venue/jakarta` (sudah ada) tanpa halaman per wilayah |
| `paket wedding jakarta price list`, `paket pernikahan jakarta murah`, `paket intimate wedding jakarta murah`, `paket pernikahan hotel jakarta` | Komersial | Tinggi | Tinggi | Hub dan halaman venue |
| `syarat nikah 2027`, `syarat nikah kua 2027`, `syarat nikah di kua 2026`, `daftar nikah online` (+ `simkah`, `jakarta`), `simkah4`, `kartu nikah digital`, `buku nikah 2026`, `bimbingan perkawinan` (+ `apakah wajib`), `sertifikat elsimil` (+ `apakah wajib`) | Informasional | **Tinggi** untuk `syarat nikah` dan `simkah`; **Sedang** untuk `elsimil` dan `bimbingan perkawinan` (masing-masing 10 varian). `syarat nikah 2027` baru 2 varian, tapi mulai muncul. | Tinggi (portal berita, Kemenag). Belum ditemukan aturan nikah baru di 2026; dasar hukum yang berlaku masih PMA 30/2024 ([Kontan](https://nasional.kontan.co.id/news/aturan-baru-akad-nikah-bisa-dilaksanakan-di-luar-kua-dan-hari-kerja-cek-syaratnya)). Khas Jakarta: surat pengantar nikah bisa diurus online lewat **JakEvo** ([Kompas TV](https://www.kompas.tv/info-publik/643204/cara-urus-pengantar-nikah-online-di-jakarta-lewat-jakevo-gratis-dan-praktis)). | `syarat-dokumen-nikah-2026-kua-catatan-sipil`, `syarat-alur-nikah-terbaru-2025-...` ⚠ (dua artikel yang tumpang tindih) |
| `nikah dengan wna`, `syarat nikah dengan wna di indonesia`, `syarat nikah dengan wna di kua`, `dokumen menikah dengan wna`, `syarat pernikahan campuran di indonesia`, `syarat menikah dengan wna australia` / `china` | Informasional | **Tinggi** (tiga seed, masing-masing 10 varian) | Sedang–Tinggi: Katadata, detik, Bloomberg Technoz ("terbaru 2026"), Hukumonline, firma hukum. | `perjanjian-pranikah-perkawinan-campuran-wna` (hanya soal prenup), `/en/legally-married-in-bali` (Inggris, khusus Bali) |
| `angpao pernikahan berapa`, `angpao pernikahan tionghoa berapa`, `angpao nikahan chinese`, `angpao nikah ganjil genap`; `angpao sangjit` (+ `apa saja`, `berapa`, `4 angpao sangjit apa saja`, `angpao susu sangjit`); `isi amplop kondangan berapa` | Informasional | **Sedang–Tinggi.** `angpao sangjit` 10 varian; `angpao nikah` 10; `isi amplop kondangan` 10. | **Rendah** untuk sudut Tionghoa. Tidak ditemukan artikel Indonesia yang membahas angpao pernikahan secara khusus; [CNBC](https://www.cnbcindonesia.com/mymoney/20260114124040-72-702276/berapa-anggaran-angpao-yang-harus-dipersiapkan-saat-imlek-2026) hanya membahas angpao Imlek. | Disinggung di `angka-baik-dan-pantangan-pernikahan-tionghoa`; artikel sangjit di DB tidak membahas angpao di isi artikelnya |
| `sangjit jakarta` (+ `venue`, `restaurant`, `murah`), `paket sangjit jakarta`, `hantaran sangjit apa saja`, `tea pai sebelum atau sesudah pemberkatan`, `tea pai dan sangjit` | Komersial/informasional | Tinggi | Sedang | `/paket-sangjit`, 5+ artikel sangjit |
| `nikah di masjid istiqlal` (+ `berapa`, `syarat`), `syarat nikah di gereja katedral jakarta`, `tempat pemberkatan nikah di jakarta` | Lokal | Sedang | Sedang | `masjid-gedung-favorit-jabodetabek-akad-nikah`, artikel pemberkatan |

### 3b. Bali (Indonesia + Inggris)

| Kata kunci | Bahasa/pasar | Intent | Permintaan + bukti | Persaingan | Cakupan 7Magic |
|---|---|---|---|---|---|
| `bali wedding guest dress` / `guest outfit` / `guest dress male` / `mens outfit` / `guest dress ideas` | EN, AU + SG | Informasional | **Tinggi.** Muncul langsung dari seed `bali wedding` di AU **dan** SG. | Sedang: [inivie](https://inivie.com/discover-bali/what-to-wear-to-a-bali-wedding-as-a-guest), Nathan Tailors (khusus pria), SingaporeBrides. Tidak ada yang menulis dari sudut musim hujan. | **Belum ada** (gelombang 3 "guest guide" di hub Bali masih terbuka) |
| `bali wedding venues uluwatu` / `seminyak` / `canggu` / `nusa dua` / `ubud`; `bali wedding packages uluwatu` | EN, AU | Komersial | **Tinggi** (8–10 varian per wilayah) | Tinggi (direktori, halaman venue) | Hub `/wedding-venue/bali` (13 venue); halaman per wilayah masuk gelombang 2 |
| `bali wedding packages 20 guests` / `30` / `50` / `100 guests` / `for two` / `with accommodation` | EN, AU + SG | Komersial | Tinggi | Tinggi (planner) | `/en/bali-wedding-cost`, kalkulator biaya |
| `getting married in bali for foreigners` / `from australia` / `legal requirements`, `can australians legally marry in bali`, `is bali marriage recognised in australia` | EN, AU | Informasional | Tinggi | Sedang | **Sudah ada:** `/en/legally-married-in-bali` |
| `bali vow renewal` / `packages` / `packages all inclusive` / `ceremony`, `bali wedding renewal` | EN, AU | Komersial | **Sedang–Tinggi** (10 varian) | **Rendah untuk konten editorial.** SERP diisi halaman paket hotel (Grand Mirage, Oberoi, Aryaduta) tanpa penjelasan. | Belum ada (landing vow renewal ada di gelombang 2) |
| `bali elopement packages all inclusive`, `bali elopement for two`, `bali elopement cost` | EN | Komersial | Tinggi | Tinggi | `apa-itu-elopement-menikah-berdua-di-bali` (ID + EN) |
| `bali wedding cost breakdown`, `bali wedding budget reddit`, `how much does it cost to get married in bali` | EN | Komersial | Tinggi | Tinggi | `/en/bali-wedding-cost` + kalkulator |
| `nikah di bali beda agama`, `nikah di bali bisa beda agama`, `nikah beda agama di bali` | ID | Informasional | **Tinggi.** Saran ke-2 untuk `nikah di bali`. | Sensitif secara hukum (lihat §6) | Belum ada |
| `biaya nikah di bali 2026`, `menikah di bali berapa`, `paket wedding bali dibawah 50 juta` (+ `price list`), `intimate wedding bali murah`, `biaya intimate wedding bali` | ID | Komersial | Tinggi | Sedang | ⚠ `menikah-di-bali-budget-masuk-akal`, `nikah-hemat-di-bali-...-di-bawah-50-juta` (DB), `mau-nikah-cuma-sama-orang-tersayang-...-villa-private-di-bali` (DB). Lebih cocok di-refresh daripada ditulis baru. |
| `bali wedding in december`, `bali wedding rainy season`, `nikah di bali musim hujan`, `wedding outdoor hujan` | EN/ID | — | **Rendah** (kosong atau 1 saran) | — | `rencana-nikah-outdoor-tapi-takut-hujan-...-bali-...` (DB), date planner. **Tidak perlu artikel baru**; cukup jadi bagian di artikel lain. |
| `dewasa nikah desember 2026`, `duasa nikah desember 2026` | ID (Bali) | Informasional | Sedang | Rendah | `dewasa-ayu-pawiwahan-hari-baik-menikah-bali` ⚠ **404 di live** |

### 3c. Singapura (sebagian besar Inggris, `gl=sg`)

| Kata kunci | Kelompok | Intent | Permintaan + bukti | Persaingan dan realistiskah untuk 7Magic | Cakupan 7Magic |
|---|---|---|---|---|---|
| `bali wedding ang bao rate`, `bali wedding ang bao`, `destination wedding ang bao` | (a) SG → Bali | Informasional | **Sedang.** `bali wedding ang bao rate` muncul **langsung dari seed `bali wedding`** di SG. | Moneysmart ([destination wedding ang bao](https://blog.moneysmart.sg/wedding/destination-wedding-ang-bao)), SingSaver, SingaporeBrides. **Kepala kueri `ang bao rates 2026/2027` di luar jangkauan** (situs finansial menguasai). Ekor panjang khusus Bali masih mungkin, terutama sebagai bagian dari panduan tamu atau panduan pasangan. | Belum ada |
| `bali wedding packages`, `bali wedding packages all-inclusive`, `bali wedding photoshoot`, `bali wedding dress rental` | (a) | Komersial | Tinggi (SG) | Tinggi | Halaman hub Bali |
| `overseas marriage singapore`, `register overseas marriage singapore`, `overseas marriage recognised in singapore`, `can singaporean register marriage overseas` | (a) | Informasional | **Sedang–Tinggi** (10 varian) | Kueri pendaftaran dikuasai halaman pemerintah ([ask.gov.sg](https://ask.gov.sg/ourmarriagejourney/questions/cm4b5wmyz00gncm2jc9rsi32u?from=topics): pendaftaran ulang di ROM bersifat **sukarela**). Panduan yang menggabungkan "orang Singapura menikah di Bali" dengan langkah sipil Indonesia **sangat sedikit**. 7Magic realistis masuk lewat sudut itu. | `/en/legally-married-in-bali` (dibuat untuk orang Australia) |
| `menikah di singapura`, `syarat menikah di singapura`, `cara wni menikah di singapura`, `syarat wni menikah di singapura`, `biaya menikah di singapura`, `nikah sipil di singapura`, `orang indonesia menikah di singapura` | (b) WNI → SG | Informasional | **Tinggi** (`gl=id`, tiga seed, masing-masing 10 varian) | **Tipis:** [RRI Batam](https://rri.co.id/batam/regional/2617955/menikah-di-singapura-ini-cara-wni-mencatatkan-pernikahan-agar-sah), tanya-jawab lama Hukumonline. **Peluang yang jelas.** | Artikel venue Singapura di DB, `/en/wedding-planning-singapore`, hub `/wedding-venue/singapore` |
| `menikah di singapura beda agama`, `nikah beda agama di singapura` (+ `biaya`, `syarat`, `cara`) | (b) | Informasional | **Tinggi** | Sensitif secara hukum; jurnal dan berita soal SEMA 2/2023 (lihat §6) | Belum ada |
| `singaporean marry indonesian`, `indonesian marriage in singapore`, `how to get married in indonesia for foreigners`, `wedding in indonesia for foreigners` | (a)/(b) | Informasional | Sedang | Sedang | `/en/legally-married-in-bali` |
| `sangjit singapore`, `sangjit meaning`, `sangjit dress` / `cheongsam`, `indonesian chinese wedding customs` / `traditions` | (b)/(c) | Informasional | **Sedang.** `sangjit` di `gl=sg` menghasilkan 10 saran, termasuk `sangjit singapore`. | **Rendah:** WebSearch tidak menemukan halaman yang membahas sangjit dalam konteks Singapura. | Banyak artikel sangjit (ID + EN), `sangjit-by-dialect-group` (EN) |
| `guo da li checklist`, `teochew` / `hokkien` / `cantonese guo da li list`, `guo da li ang bao amount`, `tea ceremony ang bao rate`, `an chuang` (+ `items`, `auspicious date`) | (c) | Informasional | Tinggi | **Tinggi:** SingaporeBrides, Her World, jeweller blog. Sebagai halaman yang berdiri sendiri **di luar jangkauan**; hanya berguna sebagai bagian yang ditautkan dari artikel lintas negara. | `sangjit-hokkien-khek-tiociu-kanton-beda-aturan` (EN sudah memetakan sangjit = Guo Da Li) |
| `auspicious wedding dates 2027` (+ `singapore`, `chinese calendar`), `chinese wedding dates 2027`, `auspicious wedding dates in december 2026`, `2027 year of the goat marriage`, `widow years surcharge` | (c) | Informasional | **Tinggi** | **Tinggi:** [masterseanchan](https://www.masterseanchan.com/auspicious-wedding-dates-may-2027/) punya halaman per bulan, ditambah SingaporeBrides dan Aluxe. **Kepala kueri di luar jangkauan.** Sudut "tahun janda / tahun Kambing" lebih terbuka. | `kecocokan-pasangan-menurut-ba-zi` (ID + EN), kalkulator BaZi |
| `rom singapore` (+ `dates`, `booking`, `price`), `solemnisation singapore venue`, `wedding banquet singapore price`, `wedding package singapore malay` / `muslim` / `2027`, `wedding fair singapore 2027` | Lokal SG | Komersial | Tinggi | **Di luar jangkauan.** Pemerintah (ROM) dan direktori SG yang mapan; 7Magic tidak punya data harga venue Singapura (18 venue dengan harga 0, menurut rencana Ads). Jangan ditarget. | 18 venue SG dengan harga 0; artikel venue SG di DB |
| `wedding in jakarta`, `wedding cost in jakarta`, `jakarta wedding venue`, `raffles` / `fairmont` / `langham` / `westin` / `plataran jakarta wedding venue` | (a)/(b) | Komersial | Sedang (SG) | Rendah–Sedang | Halaman venue (EN), `/en/jabodetabek-wedding` |

---

## 4. Rencana artikel November

Dua belas artikel, satu tanggal per artikel. Tanggal **14 dan 28 Nov sengaja dikosongkan** untuk artikel selebriti di hari pernikahan yang sudah ada di pipeline (Lee You-jin & Cha Gyeong-eun 14 Nov, Kwak Si-yang & Yoo Jiae 28 Nov, menurut `celebrity-wedding-watchlist.md`). Keduanya tetap wajib melewati dua kali verifikasi independen untuk nama dan tanggal sebelum terbit.

Sebaran pasar: **Jakarta 5, Bali 4, Singapura 3.** Selain itu, versi Inggris dari #3 dan #9 ditujukan ke pembaca Singapura.

| # | Tgl | Pasar | Judul kerja (ID) | Kata kunci utama | Kata kunci pendukung | Intent | Kenapa sekarang | Tautan internal | EN? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **3 Nov** | Jakarta | Tanggal Cantik Menikah 2027: Daftar per Bulan, Harinya, dan yang Bentrok dengan Imlek, Ramadan, dan Libur | `tanggal cantik 2027` | `tanggal cantik 2027 untuk menikah`, `tanggal cantik 2027 hari sabtu` / `minggu`, `tanggal cantik 2027 menurut islam`, `tanggal cantik januari 2027` | Info | Pasangan yang menikah 2027 sedang memilih tanggal sebelum booking venue. Pesaing hanya mendaftar angka kembar tanpa konteks. Bedanya di kita: tandai tanggal yang jatuh di Ramadan (±8 Feb–9 Mar), sekitar Imlek, dan akhir pekan panjang. | `bulan-baik-menikah-2027-kalender-jawa`, `menentukan-tanggal-pernikahan-weton-shio`, versi 2026 (DB), hub `/wedding-venue/jakarta`, alat `mahar-tanggal-pernikahan` | Tidak |
| 2 | **5 Nov** | Bali | *(EN)* What to Wear to a Bali Wedding: A Guest Guide for the Wet Season | `bali wedding guest dress` | `bali wedding guest outfit`, `bali wedding guest dress male`, `bali wedding mens outfit`, `what to wear to a bali wedding` | Info | Puncak liburan Australia Des–Jan jatuh di musim hujan Bali. Panduan pesaing tidak membahas hujan, lumpur di venue tebing, atau dress code pura. | `/en/bali-wedding-planning`, `/en/bali-wedding-concierge`, `lokasi-prewedding-unik-bali` (EN), `makeup-tahan-lama-cuaca-tropis` (EN) | **Hanya EN** (perlu entri di `ENGLISH_ONLY_PATHS` kalau dijadikan halaman, bukan artikel) |
| 3 | **7 Nov** | Jakarta (+ SG) | Menikah di Tahun Kambing Api 2027: Benarkah "Tahun Janda", dan Kenapa Banyak Keluarga Mengejar Tanggal Sebelum Imlek | `tahun 2027 shio apa` / `menikah di tahun kambing` | `tahun janda`, `menikah sebelum imlek`, `tanggal baik untuk menikah 2027 menurut cina`, `imlek 2027 tanggal berapa`; EN: `2027 year of the goat marriage`, `widow year` | Info | Imlek jatuh 6 Feb 2027. Keluarga yang menghindari tahun janda harus mengunci tanggal Des–Jan **sekarang**. Belum ada artikel Indonesia soal ini. | `kecocokan-pasangan-menurut-ba-zi`, `mengenal-ba-zi-empat-pilar-kelahiran`, `angka-baik-dan-pantangan-pernikahan-tionghoa`, `/paket-sangjit`, kalkulator BaZi | **Ya** (pembaca Tionghoa Singapura) |
| 4 | **9 Nov** | Jakarta | Menikah Sebelum Ramadan 2027: Jendela Rajab–Syakban, Antrean KUA, dan Venue yang Masih Tersedia | `menikah sebelum bulan puasa` | `nikah bulan rajab`, `bolehkah menikah bulan rajab`, `tanggal baik menikah di bulan rajab 2027`, `ramadhan 2027 kapan`, `rajab 2026 jatuh pada tanggal` | Info → komersial | Rajab mulai ±11 Des, Ramadan ±8 Feb. Pendaftaran di KUA paling lambat 10 hari sebelum akad, jadi pasangan Desember–Januari harus bergerak bulan ini. | `menikah-di-bulan-ramadan`, `bulan-baik-menikah-2027-kalender-jawa`, `syarat-dokumen-nikah-2026-kua-catatan-sipil`, `masjid-gedung-favorit-jabodetabek-akad-nikah`, `/free-venue-tour` | Tidak |
| 5 | **11 Nov** | Singapura | WNI Menikah di Singapura: Syarat ROM, Apostille, Lapor KBRI, dan Pencatatan di Dukcapil | `menikah di singapura` | `syarat wni menikah di singapura`, `cara wni menikah di singapura`, `nikah sipil di singapura`, `biaya menikah di singapura`, `orang indonesia menikah di singapura` | Info | Permintaan tinggi, pesaing berbahasa Indonesia sedikit dan banyak yang usang. Sudah ada inventaris venue Singapura dan halaman perencanaan Singapura untuk ditautkan. | `/en/wedding-planning-singapore`, hub `/wedding-venue/singapore`, `venue-halal-friendly-di-singapore-...` (DB), `perjanjian-pranikah-perkawinan-campuran-wna`, `lokasi-prewedding-unik-singapura` | **Ya.** EN: "Marrying an Indonesian in Singapore", menyasar `singaporean marry indonesian` |
| 6 | **13 Nov** | Bali | *(EN)* Uluwatu, Nusa Dua, Canggu, Seminyak or Ubud? Choosing Where in Bali to Get Married | `bali wedding venues uluwatu` (dan pola yang sama untuk empat wilayah lain) | `bali wedding venues nusa dua` / `canggu` / `seminyak`, `bali ubud wedding packages`, `bali wedding packages uluwatu` | Komersial | Menangkap pencarian per wilayah sebelum halaman wilayah gelombang 2 dibangun, dan bisa jadi dasarnya nanti. Tidak perlu angka harga. | Hub `/en/wedding-venue/bali`, `/en/bali-wedding-cost`, kalkulator biaya, `/en/bali-wedding-concierge`, `lokasi-prewedding-unik-bali` | **Hanya EN** (ID opsional) |
| 7 | **16 Nov** | Jakarta | Biaya Nikah di Jakarta: dari KUA Gratis sampai Resepsi Hotel, dengan Harga Venue yang Nyata | `biaya nikah di jakarta` | `biaya nikah jakarta 2026`, `biaya nikah kua jakarta`, `biaya nikah gedung jakarta`, `biaya nikah hotel jakarta`, `biaya resepsi pernikahan di gedung` | Komersial | Kueri biaya mengikuti keputusan venue Des–Feb. Pesaing memakai angka 2023. 7Magic punya harga "mulai dari" untuk 51 venue Jakarta, aset yang tidak dimiliki pesaing. | Hub `/wedding-venue/jakarta`, `intimate-wedding-100-tamu-jakarta-rincian-biaya`, `cara-menghitung-porsi-katering-pernikahan`, `/perjanjian-pranikah`, `12-pertanyaan-sebelum-tanda-tangan-venue-pernikahan` | **Ya** (`wedding cost in jakarta` muncul di autocomplete SG) |
| 8 | **18 Nov** | Singapura (+ Bali) | *(EN)* Getting Married in Bali as a Singaporean: ROM, the Indonesian Civil Step, and What Guests Give | `overseas marriage singapore` / `bali wedding singapore` | `register overseas marriage singapore`, `overseas marriage recognised in singapore`, `bali wedding ang bao rate`, `bali wedding packages 50 guests` | Info → komersial | Pasangan Singapura merencanakan pernikahan Bali untuk 2027 sekarang. Halaman pemerintah hanya membahas pendaftaran, bukan langkah di Indonesia. Bagian soal ang bao menyasar `bali wedding ang bao rate` tanpa harus melawan Moneysmart untuk kueri kepala. | `/en/legally-married-in-bali`, `/en/bali-wedding-concierge` (tim Bali menangani CNI + Dukcapil), `/en/bali-wedding-cost`, `/en/wedding-planning-singapore` | **Hanya EN** |
| 9 | **20 Nov** | Jakarta (+ SG) | Angpao Pernikahan Tionghoa: Berapa Isinya, Siapa yang Memberi, dan Arti Empat Angpao Sangjit | `angpao pernikahan tionghoa berapa` | `angpao nikahan chinese`, `angpao sangjit apa saja`, `4 angpao sangjit apa saja`, `angpao susu sangjit`, `angpao nikah ganjil genap` | Info | Musim sangjit sebelum Imlek. Celah konten yang jelas dalam bahasa Indonesia. | `/paket-sangjit`, `angka-baik-dan-pantangan-pernikahan-tionghoa`, `sungkeman-dan-tea-pai-lagu-pengiring`, `sangjit-hokkien-khek-tiociu-kanton-beda-aturan`, `tea-pai-tradisi-teh-...` (DB) | **Ya**, dengan sudut SG ("ang bao vs angpao: Jakarta and Singapore norms") |
| 10 | **23 Nov** | Jakarta + Bali | Menikah dengan WNA di Indonesia: Syarat KUA dan Catatan Sipil, CNI, dan Urutan Mengurusnya | `syarat nikah dengan wna` | `nikah dengan wna di indonesia`, `syarat nikah dengan wna di kua`, `dokumen menikah dengan wna`, `syarat pernikahan campuran di indonesia`, `syarat menikah dengan wna australia` | Info | Permintaan tinggi sepanjang tahun. Menghubungkan klaster prenup (produk Rp 4 juta) dengan hub Bali. Puncak liburan Des–Jan adalah saat pasangan campuran mengurus berkas. | `perjanjian-pranikah-perkawinan-campuran-wna`, `/perjanjian-pranikah`, `/en/legally-married-in-bali`, `syarat-dokumen-nikah-2026-kua-catatan-sipil` | Opsional (`/en/legally-married-in-bali` sudah melayani pembaca Inggris) |
| 11 | **25 Nov** | Bali | *(EN)* Renewing Your Vows in Bali: What's Involved, What's Legal, and How to Plan It | `bali vow renewal` | `bali vow renewal packages`, `bali vow renewal packages all inclusive`, `bali vow renewal ceremony`, `bali wedding renewal` | Komersial | SERP-nya hanya halaman paket hotel, jadi panduan editorial bisa menang. Perjalanan ulang tahun pernikahan di libur Des–Jan. | `/en/bali-wedding-concierge`, `apa-itu-elopement-menikah-berdua-di-bali` (EN), `/en/bali-wedding-cost`, kalkulator tanggal | **Hanya EN** |
| 12 | **27 Nov** | Singapura | *(EN + ID)* When a Jakarta Family Meets a Singapore Family: Sangjit, Guo Da Li, and Who Hosts What | `sangjit singapore` | `sangjit meaning`, `indonesian chinese wedding customs`, `guo da li ang bao amount`, `tea ceremony ang bao rate`; ID: `sangjit dan guo da li` | Info | Musim sangjit sebelum Imlek. `sangjit singapore` tidak punya pesaing. Sudutnya pasangan lintas negara, **bukan** pengulangan pemetaan per dialek. | `sangjit-hokkien-khek-tiociu-kanton-beda-aturan`, `/paket-sangjit` + `/en/sangjit-package`, artikel #9, `/en/wedding-planning-singapore` | **Ya** (EN utama, ID terjemahan) |

**Cadangan, kalau ada slot atau salah satu di atas tertunda:**

- **30 Nov, Jakarta:** *Gedung dan Hotel Pernikahan di Jakarta Selatan: Kapasitas dan Harga Mulai dari Data 7Magic* (`gedung pernikahan jakarta selatan`, `venue pernikahan jakarta selatan`, `paket wedding jakarta selatan`). Permintaannya Tinggi, tapi lebih tepat dibangun sebagai halaman wilayah di bawah `/wedding-venue/jakarta` daripada sebagai artikel. Harga wajib dari DB dan sudah diverifikasi.
- **Ditahan untuk tinjauan hukum:** *Nikah beda agama di Bali atau Singapura: apa yang bisa dicatat setelah SEMA 2/2023.* Permintaannya Tinggi di dua pasar (lihat §6). Jangan terbit tanpa ditinjau notaris atau tim legal 7Magic.

**Per pasar:**
- **Jakarta:** #1, #3, #4, #7, #9 (+ #10 bersama Bali)
- **Bali:** #2, #6, #11 (+ #10, + #8 bersama Singapura)
- **Singapura:** #5, #8, #12 (+ versi EN dari #3 dan #9)

**Catatan produksi:**
- Semua artikel mengikuti alur di memori `article-writing-workflow`: tanpa em dash, tanpa harga karangan, foto berlisensi di R2, daftar `## Referensi`. Kategori di front matter **bukan** slug URL; uji semua tautan internal setelah terbit.
- #2, #6, #8, dan #11 hanya berbahasa Inggris. Tentukan apakah dijadikan artikel (`content/articles/en/` mengharuskan pasangan ID karena importer membandingkan tag stream dengan `body_id`) atau halaman hub Bali (`ENGLISH_ONLY_PATHS`). Importer artikel saat ini tidak mendukung artikel yang hanya berbahasa Inggris.

---

## 5. Daftar refresh

| Artikel yang ada | Kata kunci yang perlu diserap | Yang perlu diubah | Prioritas |
|---|---|---|---|
| `bulan-baik-menikah-2027-kalender-jawa`, `dewasa-ayu-pawiwahan-hari-baik-menikah-bali`, `hari-baik-menikah-tradisi-sunda-paririmbon`, `larangan-menikah-adat-jawa`, `weton-jodoh-menghitung-kecocokan-pasangan-primbon-jawa` | `tanggal baik untuk menikah 2027 menurut jawa`, `dewasa nikah desember 2026`, `rajab 2026` | **Kelimanya ada di Markdown dengan tanggal 20–24 Okt tapi tidak ada di sitemap live, dan dua yang dicek mengembalikan 404.** Pastikan sudah di-import dan diterbitkan di prod sebelum #1, #3, dan #4 menautkannya. Ini yang paling mendesak di dokumen ini. | **Mendesak** |
| `syarat-dokumen-nikah-2026-kua-catatan-sipil` | `syarat nikah 2027`, `syarat nikah kua 2027`, `daftar nikah online jakarta`, `simkah4`, `sertifikat elsimil apakah wajib`, `bimbingan perkawinan apakah wajib`, `kartu nikah digital` | Perbarui ke 2027 di judul dan isi. Tambah JakEvo (pengantar nikah online Jakarta), SIMKAH, Elsimil, bimwin. Cek ulang PMA 30/2024 dan batas 10 hari (satu sumber menulis "10 hari kerja"). | Tinggi |
| `syarat-alur-nikah-terbaru-2025-...` (DB) | sama | Tumpang tindih dengan artikel di atas. Gabungkan dan 301 ke artikel 2026/2027, atau ubah sudutnya. | Tinggi (kanibalisasi) |
| `menikah-di-bulan-ramadan` + `bolehkah-menikah-di-bulan-ramadan-...` (DB) | `menikah sebelum bulan puasa`, `ramadhan 2027` | Dua artikel bersaing untuk kueri yang sama. Pilih satu sebagai kanonik, tambahkan tanggal 2027 (perkiraan), dan tautkan ke #4. | Sedang |
| `tanggal-cantik-pernikahan-2026-...` (DB) | — | Tambahkan tautan ke artikel #1 di bagian atas. Jangan ganti slug yang memuat 2026. | Sedang |
| `menentukan-tanggal-pernikahan-weton-shio` | `tahun 2027 shio apa`, `tanggal baik untuk menikah 2027 menurut cina` | Paragraf soal shio masih menulis "tahun 2026 = Kuda Api" dan Bulan Hantu 2026. Perbarui ke Kambing Api 2027 dan tautkan ke #3. Tanggal Bulan Hantu 2027 harus dicek ulang. | Sedang |
| `tren-seserahan-mas-kawin-2026` | `trend seserahan 2026`, `list seserahan 2026`, `seserahan lamaran apa saja` | Belum ada saran autocomplete untuk `seserahan 2027`. Refresh di Januari, bukan sekarang. | Rendah (Jan) |
| `menikah-di-bali-budget-masuk-akal` + `nikah-hemat-di-bali-...-di-bawah-50-juta` (DB) | `biaya nikah di bali 2026`, `paket wedding bali dibawah 50 juta price list`, `intimate wedding bali murah` | Tambahkan bagian biaya 2026/2027 dengan harga yang **sudah diverifikasi** (11 dari 12 venue Bali masih berharga 0 di DB). Pertimbangkan menggabungkan keduanya. | Sedang |
| `intimate-wedding-100-tamu-jakarta-rincian-biaya` | `intimate wedding jakarta price list`, `paket intimate wedding jakarta murah` | **Harganya masih estimasi model (id 122–145).** Verifikasi dulu sebelum #7 menautkannya sebagai rujukan harga. | Tinggi (sebelum #7) |
| `perjanjian-pranikah-perkawinan-campuran-wna` | `syarat nikah dengan wna` | Tautkan ke #10 begitu terbit. Tidak perlu menulis ulang. | Rendah |
| `jadwal-pernikahan-artis-2026-2027` | — | Pembaruan mingguan sesuai watch list (Lee You-jin 14 Nov, Kwak Si-yang 28 Nov, Ji Ye-eun 12 Des, Abe Hoed Des). Verifikasi dua kali. | Rutin |
| `/en/legally-married-in-bali` | `getting married in bali for foreigners`, `can foreigners get married in bali`, `getting married in bali from uk` | Saat ini ditulis untuk orang Australia. Tambahkan satu bagian singkat "dari negara lain (Inggris, Singapura)" atau tautkan ke #8. | Rendah |

---

## 6. Pertanyaan terbuka dan fakta yang perlu diverifikasi

**Tanggal (jangan dicetak sebelum dicek):**
1. **Status 2027 sebagai tahun janda (tanpa lichun).** Ini kesimpulan saya dari lichun 4 Feb 2027, Imlek 6 Feb 2027, Imlek 26 Jan 2028, dan lichun ±4 Feb 2028. Konfirmasi dengan almanak Tong Shu 2027 atau praktisi sebelum #3 terbit, dan tulis sebagai kepercayaan, bukan fakta.
2. 1 Ramadan 1448 H (±8 Feb 2027) dan Idulfitri (9 atau 10 Mar) menunggu sidang isbat. Tulis sebagai perkiraan beserta sumbernya.
3. SKB libur nasional dan cuti bersama 2027 belum terbit. Daftar tanggal cantik di #1 tidak boleh mengklaim status libur sebelum SKB keluar. Tambahkan catatan "akan diperbarui".
4. Rajab dan Syakban 1448: tanggal diambil dari tabel di `bulan-baik-menikah-2027-kalender-jawa`. Cocokkan ulang dengan kalender Kemenag.
5. Hari dalam seminggu untuk setiap tanggal di #1 harus dihitung mesin, bukan disalin dari Popmama; versi-versi Popmama sendiri tidak konsisten satu sama lain.
6. Bulan Hantu (bulan ke-7 kalender lunar) 2027, untuk refresh artikel weton/shio.

**Harga (jangan dikarang):**
7. #7 Biaya nikah Jakarta: harga "mulai dari" dari `price_start_from`, hanya untuk venue yang sudah diaudit (harga outlier venue 80, Yello, sudah dikosongkan dan angka sebenarnya belum diketahui, jadi jangan ditebak). Biaya KUA Rp0/Rp600.000 berasal dari PNBP, kutip Kemenag langsung.
8. #8 dan #9: nominal ang bao atau angpao **tidak boleh** ditulis sebagai norma 7Magic. Kutip sumber Singapura (Moneysmart, SingaporeBrides) dengan tahun, dan untuk Indonesia jelaskan polanya (genap, hindari 4) tanpa angka rupiah karangan.
9. #11 Vow renewal: jangan ada harga. Kalau perlu, arahkan ke konsierge. Cek apakah vow renewal termasuk dalam 18 layanan konsierge yang sudah dikonfirmasi user (memori `bali-australia-hub` tidak mencantumkannya secara eksplisit).

**Hukum dan prosedur (perlu sumber primer):**
10. #5 WNI menikah di Singapura: dokumen KBRI, apostille dari Singapore Academy of Law, batas lapor 30 hari ke Dukcapil (dari [Hukumonline](https://www.hukumonline.com/klinik/a/mencatatkan-perkawinan-di-dua-negara-lt56d4fd4251dc2/), sumbernya lama), dan dasar Perpres 96/2018. Cek ke laman KBRI Singapura dan [ROM](https://marriage.gov.sg/Civil_Overview_of_Marriage_Process.pdf).
11. #8 Pendaftaran ulang di ROM bersifat sukarela, biaya S$75 ([ask.gov.sg](https://ask.gov.sg/ourmarriagejourney/questions/cm4b5wmyz00gncm2jc9rsi32u?from=topics)). Cek ulang angkanya saat menulis. ROM sementara pindah dari Canning Rise sampai 2029 ([The Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/02/08/marriage-solemnisations-in-singapore-to-return-to-canning-rise-in-2029-after-redevelopment)).
12. #10 Daftar dokumen WNA menurut PMA 30/2024 belum terekstrak dengan andal dari sumber sekunder. Pakai teks PMA atau laman Kemenag.
13. **Nikah beda agama (Bali dan Singapura).** Setelah [SEMA 2/2023](https://news.detik.com/berita/d-6831689/tertutup-pintu-pencatatan-nikah-beda-agama-usai-terbit-surat-edaran-ma), pengadilan tidak lagi mengabulkan pencatatan, dan Dukcapil menyatakan tidak akan mencatat tanpa penetapan pengadilan ([Kompas TV](https://www.kompas.tv/nasional/427488/dukcapil-tegaskan-tidak-akan-catat-perkawinan-beda-agama-tanpa-penetapan-pengadilan)). Tidak ditemukan sumber yang jelas soal pencatatan pernikahan WNI beda agama yang dilangsungkan di Singapura *setelah* SEMA. Permintaannya nyata, tapi ini konten YMYL hukum. **Keputusan user: ditulis dengan tinjauan notaris, atau tidak sama sekali.**

**Keputusan bisnis untuk user:**
14. Apakah 7Magic mau dan bisa melayani pasangan yang menikah *di* Singapura (#5, #12), atau hanya warga Singapura yang menikah di Bali/Jakarta? Ini menentukan CTA di #5.
15. Artikel yang hanya berbahasa Inggris (#2, #6, #8, #11): dijadikan halaman hub Bali, atau importer diperluas agar mendukung artikel EN tanpa pasangan ID?
16. Untuk #12, apakah sangjit 7Magic juga melayani keluarga di Singapura? Memori `jakarta-landing-pages` menyebut isi paket sangjit masih belum dikonfirmasi.
17. Tarik data Search Console (impresi per kueri, 90 hari) untuk memvalidasi urutan prioritas di §4, terutama apakah `tanggal cantik` dan `sangjit` sudah mendatangkan impresi.

**Selebriti:**
18. Sudut selebriti mana pun di bulan ini (Lee You-jin 14 Nov, Kwak Si-yang 28 Nov, Ji Ye-eun 12 Des, Abe Hoed Des, Azriel Hermansyah & Sarah Menzel untuk Bali 2027) wajib melewati **dua kali verifikasi nama dan tanggal oleh agen independen**, sesuai `celebrity-content-verification`. Artikel di §4 sengaja tidak memakai sudut selebriti.

---

## Lampiran: cuplikan autocomplete yang menjadi dasar keputusan

Diambil 2 Nov 2026. Urutan sesuai yang dikembalikan Google; urutan ini bukan volume.

- `tanggal cantik 2027` (id/id): untuk menikah · weekend · hari sabtu · hari minggu · hari jumat · dan harinya · menurut islam · di 2027 · januari 2027
- `tanggal baik menikah 2027` (id/id): menurut islam · menurut jawa · menurut primbon jawa · **menurut cina** · januari 2027 · di bulan rajab 2027 · di bulan syawal 2027
- `nikah di bali` (id/id): **beda agama** · budget · berapa · murah · bisa beda agama · berapa hari · siri · biaya · tempat
- `menikah di singapura` (id/id): beda agama · syarat · cara · **wni menikah di singapura** · biaya · cara … beda agama · syarat wni · cara wni · orang indonesia
- `angpao sangjit` (id/id): apa saja · berapa · jumbo · 4 angpao sangjit · angpao susu · 4 angpao apa saja · amplop · isi · kertas
- `bali wedding` (en/sg): packages · venues · photoshoot · **ang bao rate** · cost · guest dress · dress rental · dress · planner
- `bali wedding` (en/au): packages · venues · **guest dress** · planner · dress · **mens outfit** · cost · outfit · **guest outfit**
- `bali vow renewal` (en/au): packages · (itself) · packages all inclusive · ceremony · waterfall · wedding renewal packages
- `overseas marriage singapore` (en/sg): international · foreign · overseas wedding · register · update · recognised · registration · certificate recognised
- `auspicious wedding dates` (en/sg): 2027 · 2026 · 2028 · 2027 singapore · 2027 chinese calendar · … · **in december 2026** · in november 2026
- `sangjit` (en/sg): dress · meaning · cheongsam · in chinese · **singapore** · wedding dress · gown · adalah · ceremony
- `widow year` (en/sg): **widow years surcharge** · …; `year of the goat wedding` (en/sg): **2027 year of the goat marriage**
- Kosong atau hampir kosong: `11.11 wedding`, `12.12 wedding`, `nikah musim hujan`, `bali wedding rainy season`, `bali wedding in december`, `seserahan 2027`, `solemnisation date 2027`, `wedding in bali from singapore`
