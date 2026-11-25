# Riset artikel hukum pernikahan, November 2026

**Tanggal:** 25 November 2026
**Tujuan:** membangun klaster artikel hukum pernikahan (ID + EN) yang mengalirkan trafik ke `/perjanjian-pranikah-bali` (dan `/en/perjanjian-pranikah-bali`), lalu ke `/perjanjian-pranikah` Jakarta.
**Status:** riset dan perencanaan. Belum ada artikel yang ditulis.
**Dokumen pendamping:** `2026-11-bali-wedding-article-research.md` (§4 #5–#7, #10), `2026-11-seo-keyword-research.md` (metode dan label permintaan).

---

## 1. Metode dan batas data

- **Google Autocomplete**, diambil 25 Nov 2026: ±140 seed `hl=id&gl=id` dan ±120 seed `hl=en` (`gl=au`, `gb`, `sg`, `us`). Untuk kueri Inggris, `gl` hampir tidak berpengaruh (49 dari 52 seed identik), jadi pasar ditentukan dari bunyi kueri dan siapa yang menempati hasil, bukan dari autocomplete per negara.
- **WebSearch** (lokasi AS) untuk melihat pesaing dan memeriksa fakta hukum ke sumber primer (BPK, mkri.id, imigrasi.go.id, gov.uk, kedutaan, DJP, Hukumonline).
- Label Tinggi/Sedang/Rendah sama dengan riset 2 November: lebar autocomplete, **bukan volume**. Tidak ada data Search Console atau CPC.
- Semua artikel hukum adalah konten YMYL. Fakta yang ditandai ⚠ belum terverifikasi atau sumbernya bertentangan; jangan terbit sebelum dicek.

---

## 2. Yang sudah kita punya

**Artikel (semuanya masih `status: draft`):** `perjanjian-pranikah-panduan-lengkap`, `perjanjian-pranikah-dan-hak-waris-pasangan`, `perjanjian-pranikah-perkawinan-campuran-wna`, `perjanjian-pranikah-pisah-harta-kpr-dan-utang`, `syarat-dokumen-nikah-2026-kua-catatan-sipil`, `syarat-nikah-dengan-wna-di-indonesia`, `akad-nikah-di-bali-kua-wali-venue`, `pemberkatan-nikah-kristen-katolik-di-bali`, `vow-renewal-di-bali-...`, `menikah-di-bali-warga-singapura`, `wni-menikah-di-singapura`.

**Landing page:** `/perjanjian-pranikah`, `/perjanjian-pranikah-bali`, `/en/legally-married-in-bali` (ditulis untuk orang Australia), `/en/bali-wedding-cost`, `/en/bali-wedding-concierge`.

**Ditahan:** nikah beda agama di Bali/Singapura (SEMA 2/2023), menunggu tinjauan hukum.

---

## 3. Perbaikan mendesak sebelum menulis apa pun

| # | Masalah | Di mana | Tindakan |
|---|---|---|---|
| A | **FAQ salah soal kapan perjanjian pascanikah berlaku.** Halaman menulis "berlaku sejak dicatatkan, bukan mundur ke tanggal pernikahan". Pasal 29(3) UU Perkawinan sebagaimana dimaknai Putusan MK 69/PUU-XIII/2015: "mulai berlaku sejak perkawinan dilangsungkan, kecuali ditentukan lain dalam Perjanjian Perkawinan". Pencatatan menentukan kapan perjanjian mengikat **pihak ketiga**. Artikel KPR kita sudah menulis versi yang benar, jadi situs saat ini bertentangan dengan dirinya sendiri. | `apps/web/src/routes/perjanjian-pranikah/content.ts:225` (ID) dan `:501` (EN); halaman Bali mewarisinya | Minta notaris mitra mengonfirmasi kalimatnya, lalu perbaiki. Sumber: [BPK, putusan MK 69](https://peraturan.bpk.go.id/DownloadUjiMateri/14/69_PUU-XIII_2015.pdf), [Hukumonline](https://www.hukumonline.com/klinik/a/status-aset-yang-dibeli-sebelum-perjanjian-perkawinan-dicatatkan-lt640afd202060a/). |
| B | **Tidak satu pun dari 4 artikel prenup menautkan `/perjanjian-pranikah-bali`.** Semuanya hanya ke halaman Jakarta. | 4 artikel `perjanjian-pranikah-*` | Tambahkan tautan Bali di samping tautan Jakarta: bagian timeline Bali di artikel WNA, "Langkah berikutnya" di panduan lengkap, CTA di artikel KPR dan hak waris. |
| C | **Artikel hukum belum terbit.** Seluruh klaster di §2 masih `draft`; tiga draft Bali sebelumnya juga 404 di situs live. | `apps/web/content/articles/` | Terbitkan, setelah A dan B. Ini kerja termurah dengan dampak terbesar. |
| D | **⚠ Putusan MK 334/PUU-XXIV/2026 kemungkinan sudah dibacakan** (15 Okt 2026, "tidak dapat diterima" karena *legal standing*, ada *dissenting opinion*), menurut [pasal.id](https://pasal.id/peraturan/putusan-mk/puu-mk-334-2026). Artikel hak waris (5 Okt) masih menulis belum ada putusan. | `perjanjian-pranikah-dan-hak-waris-pasangan` | Konfirmasi di mkri.id, lalu perbarui. Pokok perkaranya tetap belum diputus, jadi saran "tulis tegas di akta" tetap berlaku. |
| E | **"Prenup" dalam bahasa Inggris Filipina/Singapura berarti sesi foto prewedding.** Autocomplete `prenup bali` → `bali prenup shoot`. | Judul dan meta EN halaman prenup Bali | Pakai "prenuptial agreement" utuh di judul EN; tambahkan frasa "notary in Bali" / "Bali notary public". |
| F | Artikel lama di DB `wedding-preparation/perjanjian-pranikah-pro-kontra-tren-dan-realita-untuk-pasangan-millennial` masih di sitemap dan bersaing dengan panduan lengkap. | DB | 301 ke `perjanjian-pranikah-panduan-lengkap`. |

---

## 4. Rencana artikel baru, urut prioritas

Kolom "Bahasa": artikel ID tetap ditulis dulu sebagai sumber (importer membandingkan `body_en` dengan `body_id`); "EN utama" berarti versi EN dioptimalkan untuk kueri Inggris.

| # | Judul kerja | Kueri utama | Kueri pendukung | Bahasa | Permintaan | Persaingan | Jalur ke halaman prenup Bali | Fakta hukum inti | Risiko |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Perjanjian Kawin Setelah Menikah: Kapan Berlaku, Didaftarkan ke Mana, dan Apa Batasnya** | `perjanjian kawin setelah menikah` / `perjanjian pisah harta setelah menikah` | didaftarkan kemana · berlaku surut · dengan wna · biaya · contoh · perjanjian pasca nikah · postnuptial agreement indonesia · putusan mk 69 · pembatalan perjanjian kawin | ID + EN | **Tinggi** (4 seed × 10) | Sedang–Tinggi (Hukumonline, firma hukum, jurnal); tidak ada panduan untuk awam | Langsung: halaman Bali menjual perjanjian pascanikah | MK 69/2015 (dibacakan 27 Okt 2016). Pencatatan non-Muslim: SE Dirjen Dukcapil 472.2/5876/DUKCAPIL (19 Mei 2017); Muslim: surat Kemenag B.2674/DJ.III/KW.00/9/2017 ([Hukumonline](https://www.hukumonline.com/berita/a/5-poin-se-kemenag-soal-pencatatan-perjanjian-perkawinan-lt59cdfc6a2df7e)). Mengikat pihak ketiga sejak dicatat. | ⚠ Retroaktivitas: sebagian jurnal berpendapat perjanjian pascanikah tidak berlaku surut. Selaraskan dengan perbaikan §3A dan artikel KPR. Setelah terbit, ringkas subbagian serupa di panduan lengkap dan artikel KPR. Tinjauan notaris. |
| 2 | *(EN utama)* **Married Abroad, Now Living in Bali: Register the Marriage, Then Sign a Postnup** | `postnuptial agreement indonesia` | how to register foreign marriage in indonesia · postnuptial vs prenuptial · `pelaporan perkawinan luar negeri` (+ syarat, formulir) | EN (+ ID untuk `pelaporan perkawinan luar negeri`) | Sedang | Tipis (Mondaq, SIP); tidak ada yang menjelaskan urutannya | Konversi paling langsung: lapor nikah → postnup di Bali → catat → beli properti | Lapor ke Dukcapil 30 hari setelah kembali (UU Adminduk Pasal 37) vs 1 tahun (UU Perkawinan Pasal 56(2)) — konflik ini sudah dibahas di artikel WNA ([Mondaq](https://www.mondaq.com/family-law/1442280/how-to-register-a-marriage-held-abroad-in-indonesia)). Visa E31A mensyaratkan pernikahan luar negeri sudah dilaporkan. | Bergantung pada jawaban Q2 (§7). Bagian "Married abroad?" di artikel WNA dijadikan ringkasan yang menautkan ke sini. |
| 3 | **Waris dan Bentuk Perkawinan Adat Bali: Purusa, Nyentana, Pada Gelahang, dan Hak Anak Perempuan** | `hukum waris adat bali` / `perkawinan pada gelahang` | pembagian warisan adat bali · hak waris anak perempuan bali · nyentana (beda agama, beda kasta) · purusa dan pradana · tanah ayahan desa | ID | Sedang (pada gelahang 10, waris adat 8, nyentana 7) | **Rendah** untuk sudut praktis (jurnal + satu klinik Hukumonline 2012) | **Tautan khas Bali terkuat.** Pasangan dengan pihak Bali, anak tunggal, atau membawa tanah keluarga adalah pembeli halaman Bali. | Keputusan Pesamuhan Agung III MUDP Bali No. 01/Kep/PSM-3/MDP Bali/X/2010 ([Hukumonline](https://www.hukumonline.com/klinik/a/hak-waris-perempuan-menurut-hukum-adat-bali--lt4f6ac3987ac0e/)); tidak semua desa menerapkannya ([Undiksha](https://ejournal.undiksha.ac.id/index.php/jatayu/article/view/28658/16171)). Pada gelahang hanya diakui bila awig-awig desa mengaturnya ([Warmadewa](https://www.ejournal.warmadewa.ac.id/index.php/analogihukum/article/download/14093/7099/65556)). | ⚠ Bagian anak perempuan berbeda antar sumber (½ setelah dikurangi ⅓ pusaka / 30% / penuh). Baca teks keputusan asli. ⚠ Cek apakah MUDP kini MDA (Perda Bali 4/2019). Sensitif agama dan adat; tinjauan notaris Bali atau ahli adat. **Jangan menulis bahwa prenup bisa mengesampingkan harta pusaka.** |
| 4 | *(EN utama)* **Married to an Indonesian and Buying in Bali: Freehold in Your Spouse's Name, Hak Pakai, or Leasehold?** | `can foreigners buy property in bali` (sudut pasangan) | can foreigners own land in bali · freehold bali foreigner · leasehold vs freehold bali · hak pakai untuk wna · buying property in bali as an australian | EN + ID | **Tinggi** | Tinggi untuk kueri umum (agen properti); **Rendah** untuk sudut pasangan menikah | Tanpa pisah harta, Hak Milik yang dibeli selama menikah jadi harta bersama dan bagian asingnya wajib dilepas dalam setahun | UUPA Pasal 21(3); PP 18/2021 Pasal 70; Hak Pakai WNA (Permen ATR/BPN 18/2021). ⚠ Harga minimum Bali Rp5 M rumah / Rp2 M apartemen (Kepmen ATR/BPN 1241/2022) baru dari [detik](https://finance.detik.com/properti/d-6723693/wna-boleh-beli-rumah-apartemen-di-ri-begini-aturannya). ⚠ Jangka waktu Hak Pakai berbeda antar sumber. | Tinjauan notaris/PPAT. Fokus ke keputusan membeli; jangan ulang bagian "apa yang tetap bisa dimiliki WNA" di artikel WNA. |
| 5 | **Harta Bersama dan Harta Bawaan: Apa yang Terjadi pada Harta dan Utang Anda Tanpa Perjanjian Pranikah** | `harta bersama dan harta bawaan` / `harta gono gini` | harta bawaan istri apakah suami berhak · pembagian harta gono gini jika suami meninggal · menurut KHI · utang suami siapa yang menanggung · utang suami sebelum menikah | ID | **Tinggi** (5 seed × 10; `utang suami` 10) | Tinggi (Hukumonline, detik, NU; banyak didorong berita cerai selebriti) | Artikel "aturan bawaan" yang menjelaskan kenapa prenup perlu; masuk ke kedua halaman prenup | UU 1/1974 Pasal 35–37; KHI Pasal 96–97 ([Hukumonline](https://www.hukumonline.com/klinik/a/harta-bersama-jika-tak-ada-perjanjian-perkawinan-cl2159/)); pengadilan tidak selalu 50:50 ([Hukumonline 2025](https://www.hukumonline.com/berita/a/pembagian-harta-bersama-tidak-selalu-dibagi-rata-dalam-perceraian-lt67ec1d15a28dc)). Utang: KHI Pasal 93 ([Hukumonline](https://www.hukumonline.com/klinik/a/utang-dan-harta-bersama-dalam-poligami-lt5f77163db1e69/)). | ⚠ Bagian janda menurut KHI Pasal 180 belum dicek ke teks. Sudut "sebelum menikah", bukan perceraian. Utang dijadikan bagian di sini (bukan artikel sendiri); ringkas bagian utang di artikel KPR. |
| 6 | **Rumah atas Nama Istri atau Suami: Milik Siapa Saat Cerai atau Salah Satu Meninggal?** | `rumah atas nama istri` | apakah termasuk harta gono gini · saat suami meninggal · rumah atas nama suami · kpr atas nama istri · harta gono gini rumah kpr | ID | **Tinggi** (4 seed × 10) | Sedang (klinik tanya-jawab, tidak ada panduan utuh) | Nama di sertifikat tidak menentukan kepemilikan; perjanjian kawin yang menentukan | Pasal 35(1) dan 36(1) UU Perkawinan; KHI Pasal 92 ([Hukumonline](https://www.hukumonline.com/klinik/a/rumah-yang-dihadiahkan-suami-kepada-istrinya--harta-bersama-atau-bukan-lt50f37286a8600/)) | Tautkan dua arah dengan `menikah-dulu-atau-beli-rumah-dulu` dan artikel KPR. |
| 7 | **Legalisir dan Apostille Buku Nikah, Akta Perkawinan, dan Akta Prenup** | `apostille buku nikah` / `apostille indonesia` | legalisir buku nikah dimana · di kemenag · apostille bali · sworn translator bali · apostille indonesia marriage certificate | ID + EN | **Tinggi** (masing-masing 10) | Sedang (agen jasa, PDF kedutaan lama) | WNA perlu ini untuk visa pasangan, pencatatan di negara asal, dan dokumen ke notaris. 7Magic sudah menawarkan penerjemah/apostille terpisah. | Indonesia anggota Konvensi Apostille sejak 4 Juni 2022 ([HCCH](https://www.hcch.net/en/instruments/conventions/status-table/?cid=41)); Perpres 2/2021, kini Permenkum 50/2025 ([teks](https://peraturan.go.id/files/permenkum-no-50-tahun-2025.pdf)). Alur buku nikah: KUA → legalisir Kemenag → apostille ([Kedutaan Swiss](https://www.dfae.admin.ch/content/dam/countries/countries-content/indonesia/id/after-marriage-performed-in-Indonesia_ID.pdf)). Akta wajib dwibahasa untuk pihak asing (UU 24/2009). | ⚠ Biaya bertentangan antar sumber; jangan sebut angka sebelum cek AHU. Cek tumpang tindih dengan `syarat-nikah-dengan-wna-...`. Bergantung pada Q4 (§7). |
| 8 | *(EN)* **Certificate of No Impediment for an Indonesian Wedding, Country by Country** | `certificate of no impediment indonesia` | letter of no impediment · how long is a CNI valid · can us citizens get married in bali · can two foreigners get married in bali | EN | Sedang–Tinggi (9) | Halaman kedutaan tersebar, blog usang | Dokumen yang sama dikumpulkan sekali untuk catatan sipil dan notaris | AS: pernyataan di kedutaan, USD 50 ([usembassy](https://id.usembassy.gov/marriage/)). Inggris: affidavit di Jakarta/konsulat Bali, £50 ([gov.uk](https://www.gov.uk/guidance/notarial-and-documentary-services-guide-for-indonesia)). Belanda: verklaring, €30, berlaku 6 bulan ([netherlandsworldwide](https://www.netherlandsworldwide.nl/declaration/capacity-to-marry/apply-indonesia)). Jerman: Ehefähigkeitszeugnis + sertifikat konsuler Jakarta ([Merkblatt 2022](https://jakarta.diplo.de/blob/1807728/602a6a5a48eed1d0ef6d733d4c73abd2/merkblatt-eheschliessung-in-idn-data.pdf)). | Cantumkan tanggal cek biaya. Untuk Australia cukup tautkan `/en/legally-married-in-bali`. ⚠ Untuk Inggris, blog menyebut CNI dari register office, gov.uk menyebut affidavit di kedutaan — konfirmasi ke konsulat Inggris di Bali. Bisa menyerap usulan "UK citizens marrying in Bali" sebagai satu bagian. |
| 9 | **Pisah Harta dan Pajak: NPWP Istri, Status PH atau MT, dan Lapor SPT di Coretax** | `pisah harta pajak` / `npwp suami istri` | npwp istri apakah ikut suami · digabung atau dipisah · memilih terpisah · pisah harta npwp · coretax | ID | **Tinggi** (10) | DJP dan DDTC; tidak ada situs pernikahan yang menyambungkan prenup dan pajak | Konsekuensi prenup yang jarang diduga; tepat waktu menjelang musim SPT 2026 | PH vs MT, Lampiran IV, risiko kurang bayar ([DJP](https://www.pajak.go.id/id/artikel/istri-punya-npwp-sendiri-sekarang-jadi-kurang-bayar-simak-penjelasannya), [panduan DJP v20260721](https://pajak.go.id/sites/default/files/2026-09/Panduan%20DUK%20%26%20Wanita%20Kawin%20Versi%2020260721.pdf), [DDTC](https://news.ddtc.co.id/review/konsultasi-coretax/1818169/suami-istri-pisah-harta-bagaimana-administrasinya-di-coretax)); UU PPh Pasal 8(2). | Tinjauan konsultan pajak. Tanpa contoh perhitungan; kutip panduan DJP beserta versinya. |
| 10 | *(EN)* **Nominee Agreements in Bali: Why They Fail, and the 2026 Bali Regulation** | `nominee agreement bali` | bali property scam · bali villa scam · bali property lawyer | EN | Rendah–Sedang | Blog agen properti; sudut berita masih segar | Jawaban panjang untuk "kenapa tidak atas nama istri saja?" (FAQ halaman prenup sudah menyinggung UUPA 26(2)) | UUPA Pasal 26(2). ⚠ Perda Bali No. 4/2026 (konversi lahan dan nominee), dilaporkan ditandatangani 24 Feb 2026 ([Emerhub](https://emerhub.com/news/bali-criminalizes-rice-field-conversions/), [Antara](https://bali.antaranews.com/berita/387685/wagub-bali-rampungkan-kajian-akademis-nominee-sebelum-ke-dprd)); teksnya belum terbaca. | **Ditahan** sampai teks Perda diperoleh dari JDIH Bali. Tinjauan advokat. |
| 11 | **Anak dari Perkawinan Campuran: Kewarganegaraan Ganda Terbatas dan Batas Memilih** | `anak hasil perkawinan campuran` / `dual citizenship indonesia` | status anak perkawinan campuran · akta kelahiran · indonesia dual citizenship children · dual citizenship prabowo | ID + EN | **Tinggi** (10) | Sedang (imigrasi, Hukumonline, situs ekspat) | Lemah–sedang: warisan Hak Milik untuk anak berkewarganegaraan ganda | UU 12/2006 Pasal 6 (memilih saat 18, paling lambat 3 tahun kemudian); PP 21/2022 ([Imigrasi 2025](https://www.imigrasi.go.id/berita/2025/09/24/ini-aturan-khusus-yang-perlu-dipahami-tentang-paspor-bagi-anak-berkewarganegaraan-ganda)). Wacana kewarganegaraan ganda dewasa belum jadi hukum ([Jakarta Post, Agu 2026](https://www.thejakartapost.com/indonesia/2026/08/01/mixed-marriage-families-seek-priority-in-dual-citizenship-plan)). | Kebijakan sedang bergerak: wajib baris "terakhir dicek". ⚠ Hak Milik untuk anak ganda belum terverifikasi. |
| 12 | *(EN)* **Spouse KITAS (E31A) to KITAP to Citizenship** | `spouse kitas` | spouse kitas bali · cost · to kitap · e31a · kitap requirements · indonesian citizenship by marriage | EN | **Tinggi** | Agen visa (semua berjualan) | Hak Pakai butuh izin tinggal; KITAS butuh perkawinan tercatat | [imigrasi E31A](https://imigrasi.go.id/wna/daftar-visa-indonesia/E31A): 1/2 tahun, Rp6 jt / Rp8,5 jt, saldo USD 2.000; ITAS → ITAP setelah 2 tahun menikah ([FAQ imigrasi](https://www.imigrasi.go.id/faq/izin-tinggal?lang=en-US)); kewarganegaraan: UU 12/2006 Pasal 19. | **Hanya kalau ada mitra visa** (Q4). Biaya berubah; cantumkan tanggal. ⚠ "5 tahun berturut / 10 tidak berturut" baru dari satu agen. |
| 13 | **Hibah Suami ke Istri: Boleh atau Tidak, dan Kena Pajak Apa?** | `hibah suami ke istri` | hibah ke istri apakah bisa · apakah kena pajak · hibah tanah/rumah ke istri | ID | **Tinggi** (10) | Sedang | Orang mencoba hibah untuk "memindahkan rumah ke nama istri"; perjanjian kawin jalan yang lebih bersih | KUHPer Pasal 1678 melarang hibah antar suami-istri selama perkawinan, kecuali benda bergerak bernilai kecil ([Udayana](https://ojs.unud.ac.id/index.php/kerthasemaya/article/view/48527)). | ⚠ Dua posisi DJP bertentangan soal objek pajak ([DDTC](https://news.ddtc.co.id/berita/nasional/1801649/berstatus-pisah-harta-harta-hibah-suami-ke-istri-tetap-bebas-pajak)). ⚠ Berlakunya Pasal 1678 untuk pasangan Muslim belum pasti. YMYL tinggi; tinjauan notaris/PPAT dan pajak. |
| 14 | **Setelah Akad atau Pemberkatan: Ganti KK dan KTP, NPWP, dan Mencatatkan Perjanjian Kawin** | `ganti kk setelah menikah` | ganti status ktp setelah menikah (online, syarat) · dukcapil denpasar / badung | ID | **Tinggi** (9) | Tinggi (portal berita) | Checklist pascanikah yang memuat langkah pencatatan prenup dan NPWP (#9). Trafik tinggi, tautan tidak langsung. | Syarat beda per Disdukcapil ([detik](https://www.detik.com/jateng/berita/d-8069813/syarat-buat-kk-baru-setelah-menikah-dan-pindah-domisili)); ⚠ gratis menurut UU 24/2013 Pasal 79A belum dicek. | Risiko hukum rendah. Contoh Denpasar/Badung hanya kalau dicek lokal. |

**Urutan kerja yang disarankan:** §3 (A → B → C → D → E) → #1 + #2 (satu klaster pascanikah) → #3 → #5 → #6 → #4 → #7 → #8 → #9 → #11 → #14 → #12 (kalau ada mitra visa) → #13 → #10 (setelah teks Perda).

Alasan: #1/#2 menjual layanan yang sudah ada di halaman Bali dan permintaannya tertinggi. #3 adalah satu-satunya topik yang khas Bali dan hampir tanpa pesaing praktis. #5/#6 adalah kueri "aturan bawaan" bervolume tinggi yang menjelaskan kenapa orang butuh prenup. #4 membawa pembaca ekspat dengan niat beli properti. Sisanya memperluas klaster atau bergantung pada keputusan di §7.

---

## 5. Bagian halaman, bukan artikel baru

**`/en/legally-married-in-bali`:** baris "Two foreigners?" (`can two foreigners get married in bali`); catatan singkat untuk yang pernah menikah (akta cerai/kematian, terjemahan tersumpah); KUHP baru (UU 1/2023, berlaku Jan 2026) di bagian sesama jenis yang sudah ada; satu bagian untuk Inggris/Singapura atau tautan ke #8.

**Halaman prenup (Jakarta dan Bali):** contoh garis besar klausul (`prenuptial agreement indonesia sample`, `contoh postnuptial agreement`, `contoh perjanjian pisah harta`); FAQ yang muncul di autocomplete tapi belum dijawab — `dibuat dimana`, `tanpa notaris apakah sah`, `dalam islam boleh`, `di kua`, `isinya apa saja`, `bayar berapa`; syarat akta dwibahasa (UU 24/2009).

**Artikel lain:**
- `akad-nikah-di-bali-kua-wali-venue` membahas surat rekomendasi tapi tidak memakai frasa yang dicari, **`numpang nikah`** (`syarat numpang nikah di bali`).
- `pernikahan-adat-bali-tahapan-dan-makna` menautkan ke #3 begitu terbit.
- `perjanjian-pranikah-dan-hak-waris-pasangan`: tambah bagian wasiat (`surat wasiat notaris`, 10 saran) alih-alih artikel terpisah.
- Tiga draft Bali (`syarat-nikah-dengan-wna-...`, `vow-renewal-...`, `menikah-di-bali-warga-singapura`): tambah tautan prenup Bali sebelum terbit.

---

## 6. Sengaja tidak direncanakan

- **Perceraian, hak asuh, nafkah anak, gugatan/biaya cerai, cerai di Bali/dengan WNA:** permintaan tinggi, tapi didorong berita selebriti atau komersial advokat, dan tidak cocok untuk merek pernikahan. Kalau mau, satu artikel EN "Divorce in Indonesia with a foreign spouse" dengan sudut "kenapa pasangan merencanakan sejak awal", dengan tinjauan advokat.
- **Nikah siri / isbat nikah, batas usia & dispensasi kawin:** permintaan tinggi, tapi berdekatan dengan topik poligami dan perkawinan anak. Keputusan merek (Q5).
- **Pernikahan sesama jenis di Bali:** 10 saran EN, tapi tidak ada jalur ke prenup. Keputusan kebijakan, bukan artikel funnel.
- **Wasiat dan warisan untuk pasangan WNA (EN):** belum ada sumber apakah wasiat mengubah akibat UUPA 21(3). Tunggu jawaban notaris.
- **Nikah beda agama:** tetap ditahan (riset 16 Nov §4 #7).

---

## 7. Keputusan yang dibutuhkan dari 7Magic

1. **Notaris mitra mengonfirmasi** kalimat soal kapan perjanjian pascanikah berlaku (§3A, #1).
2. **Apakah layanan Bali menerima pasangan yang menikah di luar negeri** (lapor ke Dukcapil dulu, lalu postnup)? Juga pembatalan/perubahan perjanjian dan wasiat? #2 dan CTA #1 bergantung pada ini.
3. **Apakah notaris mitra juga PPAT**, dan bisa menerima rujukan pembelian properti/Hak Pakai? (#4, #10)
4. **Cakupan "penerjemah/apostille" yang dikutip terpisah:** terjemahan tersumpah, apostille AHU untuk akta atau buku nikah, atau keduanya? Ada mitra visa (KITAS)? (#7, #12)
5. **Batas merek:** siri/isbat, dispensasi kawin, perceraian, sesama jenis, beda agama — terbit atau tidak?
6. **Siapa peninjau artikel YMYL** (#1, #3, #4, #5, #9, #10, #13), dan bolehkah namanya dicantumkan sebagai peninjau? Ada ahli adat Bali (MDA/universitas) untuk #3 dan konsultan pajak untuk #9/#13?
7. **Teks resmi Perda Bali 4/2026 dan Kepmen ATR/BPN 1241/2022** lewat notaris?
8. **Harga Bali.** Sampai dikonfirmasi, semua CTA artikel menulis "dikonfirmasi saat konsultasi".
9. **Prospek Bali lebih banyak WNA atau WNI?** Menentukan apakah #4/#7/#8/#12 naik di atas #5/#6.
10. **Kewarganegaraan klien Bali sejauh ini** (UK, AS, DE, NL?) — menentukan seberapa dalam #8.

---

## 8. Data autocomplete utama (25 Nov 2026)

Urutan sesuai yang dikembalikan Google; bukan peringkat volume. Angka dalam kurung = jumlah saran.

**ID (`hl=id&gl=id`):**
- `perjanjian pranikah` (10): adalah · dalam islam · contoh · dibuat dimana · notaris · isinya apa saja · bayar berapa
- `perjanjian pranikah bali` (0) · `prenup bali` (3): notaris prenup bali · bali prenup shoot
- `perjanjian pranikah notaris` (10): tanpa notaris · harus notaris · tanpa notaris apakah sah · biaya
- `perjanjian kawin setelah menikah` (10): didaftarkan kemana · berlaku surut · akta · contoh · pencatatan · dasar hukum
- `perjanjian pisah harta setelah menikah` (10): apakah bisa · dengan wna · contoh · biaya
- `perjanjian pasca nikah` (10): notaris · didaftarkan dimana · selingkuh · dalam islam · dengan wna · biaya
- `harta bersama` / `harta gono gini` / `harta bawaan` / `pembagian harta gono gini` (masing-masing 10)
- `rumah atas nama istri` (10): saat bercerai · saat suami meninggal · apakah termasuk harta gono gini
- `utang suami` (10): siapa yang menanggung · sebelum menikah tanggung jawab siapa · tanpa sepengetahuan istri
- `hibah ke istri` (10): apakah bisa · apakah kena pajak · tanah · rumah
- `npwp istri` (10) · `npwp suami istri` (9) · `pisah harta pajak` (10) · `memilih terpisah pajak` (8)
- `hukum waris adat bali` (8) · `pada gelahang` (10) · `perkawinan pada gelahang` (8) · `nyentana` (7): beda agama · beda kasta · `ayahan desa` (6)
- `anak perkawinan campuran` (10): status · kewarganegaraan · akta kelahiran
- `legalisir buku nikah` (10): dimana · di kua · di kemenag · online · `apostille buku nikah` (10): dimana · di kemenkumham · syarat · biaya
- `ganti kk setelah menikah` (9) · `ganti status ktp setelah menikah` (8)
- `syarat nikah di bali` (10): di kua bali · **numpang nikah di bali** · catatan sipil di bali · beda agama
- `pencatatan perkawinan luar negeri` (7) · `pelaporan perkawinan luar negeri` (5)
- `surat wasiat notaris` (10): biaya · tanpa notaris apakah sah
- **Kosong/noise:** `perjanjian pranikah wna`, `harta bersama wna`, `isbat nikah di bali`, `kewarganegaraan ganda anak`; `waris bali`, `kua bali`, `catatan sipil bali` tercampur Balikpapan/Balige.

**EN (`hl=en`, au/gb/sg/us hampir identik):**
- `prenup bali`: bali prenup shoot · notaris prenup bali · `prenuptial agreement bali` (0)
- `prenuptial agreement indonesia`: sample · contoh · `postnuptial agreement indonesia`: contoh · vs prenuptial
- `can foreigners buy property in bali` / `own land` / `villa` / `buying land in bali` / `leasehold vs freehold bali` (masing-masing 10)
- `hak pakai` (10): bali · untuk wna · berapa tahun · `nominee agreement bali` (1) · `bali property scam` (6)
- `kitas spouse` (10) · `kitap indonesia` (10) · `spouse visa indonesia` (10) · `indonesian citizenship by marriage` (7)
- `dual citizenship indonesia` (10): australia · usa · prabowo · children
- `certificate of no impediment indonesia` (9) · `get married in bali uk` (8) · `can two foreigners get married in bali`
- `apostille indonesia` (10) · `apostille bali` (10) · `sworn translator bali` (10)
- `divorce in indonesia` (10): for foreigners · `same sex marriage bali` (10) · `indonesian inheritance law` (10, sebagian besar pajak)
- **Kosong:** `foreigner married to indonesian property`, `register bali marriage`, `getting married in bali divorced`, `can a foreigner inherit property`, `children of mixed marriage indonesia`.
