# Riset kata kunci lagu pernikahan, November 2026

**Tanggal:** 11 November 2026
**Pasar:** Indonesia (kueri berbahasa Indonesia), plus pengecekan kueri Inggris untuk Bali-Australia dan Singapura.
**Status:** Riset saja. Belum ada artikel ditulis, belum ada perubahan kode atau DB.
**Update 11 Nov 2026:** artikel #1 sudah ditulis sebagai draft: `apps/web/content/articles/lagu-pemberkatan-nikah-katolik-urutan-misa.md` (+ `en/`), terbit 13 Nov 2026; tanggal, gambar dan publikasi lewat `apps/api/scripts/finish_article_2026_11_katolik.py`. Kerangkanya memakai pengelompokan lagu A–D dari KAJ (Pen@ Katolik, Jun 2025), bukan nomor Madah Bakti, karena nomor MB tidak bisa diverifikasi dari sumber daring.
**Dokumen pendamping:** `2026-11-seo-keyword-research.md` (metode yang sama), `2026-editorial-calendar.md` (klaster musik September).

---

## 1. Metode dan batas data

- **Google Autocomplete** (`suggestqueries.google.com`, `client=firefox`), diambil 11 Nov 2026. Sekitar 200 seed dengan `hl=id&gl=id`, dan 59 seed Inggris masing-masing dengan `hl=en&gl=au` dan `hl=en&gl=sg`. Data mentah tidak di-commit.
- **Hasil penelusuran** lewat WebSearch (lokasi AS, jadi daftar pesaing hanya perkiraan) untuk empat kueri celah.
- **Inventaris 7Magic:** DB lokal (slug dengan `lagu|song|playlist|musik|band|gending`) dan `apps/web/content/articles/`. DB lokal bisa tertinggal dari prod; cocokkan lagi dengan sitemap live sebelum menulis.
- **Tidak ada volume, CPC, atau angka kesulitan.** Label permintaan memakai skala yang sama dengan dokumen pendamping: Tinggi = seed menghasilkan 8–10 saran dan muncul dari seed yang lebih luas; Sedang = 4–10 saran; Rendah = 0–3.
- **Saran AU dan SG hampir identik** untuk semua 59 seed Inggris. Parameter `gl` tampaknya tidak banyak berpengaruh untuk kueri Inggris, jadi anggap hasilnya "Inggris global", bukan sinyal lokal.

## 2. Yang sudah dimiliki 7Magic

| Slug | Terbit | Menutup kueri |
|---|---|---|
| `30-lagu-indonesia-terbaik-untuk-wedding-yang-bikin-semua-tamu-nyanyi-bareng` | 8 Jun 2025 | `lagu wedding indonesia`, `lagu pernikahan indonesia`, `playlist wedding indonesia` |
| `30-lagu-romantis-untuk-first-dance-wedding-yang-bikin-momen-jadi-unforgettable` | 8 Jun 2025 | `lagu first dance`, `lagu dansa pengantin` |
| `musik-hiburan-pernikahan-islami` | 30 Mar 2026 | sebagian `lagu pernikahan islami`, `sholawat pernikahan` |
| `playlist-sangjit-mandarin-hokkien-instrumental` | 3 Sep 2026 | `lagu sangjit`, `lagu entrance sangjit` |
| `lagu-mandarin-untuk-wedding-per-momen-dan-arti-lirik` | 7 Sep 2026 | `lagu mandarin pernikahan`, `lagu wedding mandarin` |
| `lagu-jawa-untuk-pernikahan-gending-campursari` | 11 Sep 2026 | `lagu pernikahan jawa`, `gending jawa pernikahan`, `gamelan pernikahan jawa` |
| `sungkeman-dan-tea-pai-lagu-pengiring` | 15 Sep 2026 | `lagu sungkeman`, `tea ceremony songs` (EN) |

Artinya, lagu pop Indonesia, first dance, Mandarin, dan Jawa sudah tertutup. **Celah terbesar ada di lagu barat, lagu gereja, lagu per momen resepsi, dan lagu untuk undangan digital.**

## 3. Klaster kata kunci (Indonesia)

| Klaster | Kueri utama dan varian dari autocomplete | Permintaan | Cakupan 7Magic |
|---|---|---|---|
| **Lagu barat / bahasa Inggris** | `lagu pernikahan barat` (lawas, romantis, terbaru, 90an, rock), `lagu wedding barat` (ceria, jadul, 80an, 2026), `lagu pernikahan bahasa inggris` (untuk teman, kristen, *beautiful in white*, *westlife*, viral), `lagu wedding inggris` | **Tinggi.** `barat` dan `bahasa inggris` muncul sebagai saran ke-2 sampai ke-4 untuk `lagu pernikahan`, `lagu wedding`, dan `lagu nikahan`. | Belum ada |
| **Pemberkatan Katolik** | `lagu pemberkatan nikah katolik` (susunan, list), `lagu pernikahan katolik` (madah bakti, janji setia, berkatilah, mohon restu), `lagu perarakan masuk pengantin katolik`, `lagu persembahan pernikahan katolik` (teks), `lagu penutup misa pernikahan`, `lagu tukar cincin di gereja`, `lagu midodareni katolik` (ibadat, misa, penutup) | **Tinggi**, ekornya panjang dan spesifik per bagian liturgi | Belum ada. Artikel prosesi Katolik (Jul 2026) membahas tata cara, bukan lagu. |
| **Pemberkatan Kristen Protestan** | `lagu pemberkatan nikah` (gbi, gpdi, kidung jemaat, rohani, sehidup semati), `lagu pernikahan kristen` (terbaru, kidung jemaat, dua insan bersatu, tulang rusuk, hari bahagia, selamat menempuh hidup baru), `lagu rohani pernikahan`, `lagu pengiring pengantin masuk gereja` | **Tinggi** | Belum ada |
| **Per momen resepsi** | `lagu masuk pengantin` (di resepsi, pelaminan, gedung, gereja), `lagu kirab pengantin` (saxophone, jawa, sunda, modern, islami, barat, palembang, minang), `lagu wedding kiss`, `lagu lempar bunga`, `lagu tukar cincin`, `lagu untuk wedding cake`, `list lagu wedding entrance` | **Tinggi** untuk masuk dan kirab; **Sedang** untuk kiss, lempar bunga, tukar cincin | Belum ada; first dance saja yang tertutup |
| **Undangan digital** | `lagu undangan digital` (pernikahan, jawa, 2026, anti mainstream, islami, bahasa inggris), `backsound undangan pernikahan` (digital, islami, download), `rekomendasi lagu wedding untuk undangan digital` | **Tinggi** | Belum ada |
| **Lamaran dan tunangan** | `lagu lamaran` (inggris, indonesia, jawa, romantis, islami, arab, bugis), `lagu tunangan` (jawa, islami, kristen, barat), `lagu engagement` (2026, taylor swift) | **Tinggi** | Belum ada |
| **Untuk pernikahan teman / kakak** (pembacanya tamu) | `lagu untuk pernikahan teman` (jawa, inggris, islami, dangdut, kristen, korea, untuk story, untuk post), `lagu untuk pernikahan kakak perempuan` (batak), `lagu duet pernikahan` (dangdut, pop, batak, barat) | **Tinggi** | Belum ada |
| **Batak** | `lagu pernikahan batak` (toba, karo, mandailing, simalungun, untuk pengantin), `lagu batak pernikahan` (untuk orang tua, boru, sedih, anak perempuan), `lagu batak untuk orang tua saat pernikahan` | **Tinggi** | Belum ada |
| **Sunda** | `lagu nikahan sunda` (viral, lirik, judul, pop sunda), `lagu sunda pernikahan` (degung, suling, hajatan, mp3) | **Tinggi** | Belum ada |
| **Daerah lain** | `lagu bugis pernikahan` (viral, makassar), `lagu minang pernikahan` (list, pesta), `lagu pernikahan palembang`, `lagu bali pernikahan` (untuk undangan) | Sedang (Bugis tinggi, Bali/Palembang rendah) | Belum ada |
| **Islami lanjutan** | `lagu akad nikah` (islami, jawa, sunda, setelah, sebelum, pengiring), `lagu sholawat pernikahan`, `lagu arab pernikahan`, `lagu wedding nasheed` (artinya, dari negara mana) | Tinggi | Sebagian, di `musik-hiburan-pernikahan-islami`. Cek apakah momen akad sudah dibahas. |
| **Prewedding / video** | `lagu prewedding` (inggris, jawa, batak, romantis), `lagu video wedding`, `lagu cinematic wedding` | Sedang | Belum ada; bisa ditautkan dari artikel prewedding |
| **Dangdut / koplo** | `lagu dangdut pernikahan` (jawa, terbaru, viral, seru), `lagu pernikahan dangdut koplo` | Sedang | Belum ada |
| **Korea** | `lagu wedding korea` (romantis, rekomendasi, wedding day), `lagu pernikahan korea` | Sedang | Belum ada |
| **Vendor musik** | `harga band wedding jakarta`, `sewa band wedding jakarta`, `price list band wedding jakarta`, `harga sewa gamelan jawa untuk pernikahan`, `harga sewa saxophone wedding` | **Rendah**, tapi niatnya transaksional | Belum ada |
| **Satu lagu tertentu** | `pernikahan kita` Tiara Andini & Arsy (lirik, chord), `wedding for you` (arti), `ijab kabul` Kangen Band, `first dance` Justin Bieber (makna) | Tinggi | **Lewati.** Situs lirik dan chord menguasai SERP, dan lirik lengkap tidak boleh dimuat. Cukup jadi entri di artikel daftar. |

**Kosong atau hampir kosong (jangan dijadikan artikel):** `lagu yang tidak boleh diputar di pernikahan`, `lagu patah hati di nikahan`, `lagu wedding sedih`, `lagu after party wedding`, `lagu wedding dinner`, `lagu same day edit`, `lagu ayah untuk anak perempuan menikah`, `lagu untuk ibu di hari pernikahan`, `lagu wedding 2027`, `string quartet wedding jakarta`, `harga band nikahan`, `harga organ tunggal nikahan`, `vendor musik wedding`. Untuk kueri tahun, `lagu wedding 2026` sudah punya 9 varian (`list`, `terbaru`, `trend`, `hits`, `gen z`), sedangkan `2027` belum muncul sama sekali.

## 4. Kueri Inggris (Bali-Australia, Singapura)

- Kueri umum (`wedding songs`, `first dance songs`, `walk down the aisle songs`, `wedding entrance songs for bridal party`, `songs not to play at a wedding`) permintaannya tinggi, tapi dikuasai The Knot, Brides, dan Easy Weddings. **Jangan dikejar.**
- Kueri khusus Bali **lemah**: `wedding band bali` hampir semuanya diartikan sebagai cincin, sedangkan `balinese wedding music`, `gamelan wedding`, `wedding string quartet bali`, dan `wedding dj bali` hanya menghasilkan 0–3 saran.
- Singapura: `wedding live band price singapore`, `wedding singer singapore`, `malay wedding dj singapore`, `wedding songs chinese/malay/tamil`. `chinese tea ceremony music` dan `chinese wedding tea ceremony music` sudah tertutup oleh terjemahan EN yang ada.
- **Kesimpulan:** belum ada artikel lagu berbahasa Inggris yang layak dibuat. Prioritaskan EN untuk artikel yang memang sudah punya sudut Singapura (Mandarin, tea pai).

## 5. Pesaing yang terlihat (dari WebSearch, bukan SERP lokal)

- **Lagu barat dan per momen resepsi:** Popbela, Popmama, Mojok, Prepedu, blog Shopee, Tokopedia, Zalora, Telkomsel, Orami, JawaPos. Hampir semuanya berupa daftar 7–30 lagu tanpa urutan acara dan tanpa penjelasan arti lirik. Sudut yang berhasil di artikel Mandarin ("empat lagu populer ternyata lagu patah hati") bisa dipakai lagi di sini.
- **Lagu gereja:** sangat tipis. Ada Popmama (`ide-lagu-pernikahan-katolik`), Google Doc tata misa, Scribd, dan skripsi. Tidak ada yang menyusun lagu mengikuti urutan liturgi. **Ini celah dengan persaingan paling rendah.**
- **Undangan digital:** Popbela, Hipwee, Sonora (OST drakor). Daftarnya sudah lama, dan tidak ada yang membahas lisensi atau durasi potongan lagu.

Sumber: [Popmama Katolik](https://www.popmama.com/life/relationship/ide-lagu-pernikahan-katolik-00-wz39d-n82q95), [Prepedu](https://prepedu.com/id/blog/english-wedding-songs), [Popbela undangan digital](https://www.popbela.com/relationship/married/lagu-untuk-undangan-digital-00-925lr-0lg4rx), [Hipwee](https://www.hipwee.com/wedding/lagu-untuk-undangan-pernikahan-digital/), [Sonora](https://www.sonora.id/read/423899252/9-ost-drama-korea-romantis-cocok-untuk-undangan-pernikahan-digital), [Mojok](https://mojok.co/terminal/10-lagu-bahasa-inggris-yang-cocok-untuk-pernikahan/), [Popbela lagu barat](https://www.popbela.com/relationship/married/rekomendasi-lagu-barat-romantis-untuk-acara-pernikahan-00-b9k7f-qkt4ps).

## 6. Artikel yang direkomendasikan, urut prioritas

| # | Judul kerja | Kata kunci utama | Kata kunci pendukung | Alasan |
|---|---|---|---|---|
| 1 | Lagu Pemberkatan Nikah Katolik, Disusun Menurut Urutan Misa | `lagu pemberkatan nikah katolik` | `urutan lagu misa pernikahan katolik`, `lagu perarakan masuk pengantin katolik`, `lagu persembahan pernikahan katolik`, `lagu komuni pernikahan katolik`, `lagu penutup misa pernikahan`, `mazmur tanggapan pernikahan katolik`, `lagu tukar cincin di gereja`, `madah bakti`, `lagu pernikahan katolik bahasa inggris` | Permintaan tinggi, persaingan paling tipis. Tautkan dari artikel prosesi Katolik. Setiap bagian diberi pilihan Indonesia **dan** Inggris (lihat §8). **Nomor Madah Bakti dan Puji Syukur wajib dicek ke buku aslinya; jangan ditebak.** |
| 2 | Lagu Pemberkatan Nikah Kristen: Kidung Jemaat, GBI, dan GPdI | `lagu pemberkatan nikah kristen` | `lagu pernikahan kristen kidung jemaat`, `dua insan bersatu`, `tulang rusuk`, `hari bahagia`, `selamat menempuh hidup baru`, `lagu pengiring pengantin masuk gereja` | Pasangan dari artikel #1, dengan struktur yang sama. Tautkan dari artikel tahapan pemberkatan Protestan. |
| 3 | Lagu Barat untuk Pernikahan per Momen, Plus Arti Liriknya | `lagu pernikahan barat` | `lagu wedding barat`, `lagu pernikahan bahasa inggris`, `lagu wedding kiss barat`, `lagu wedding barat 90an`, `lagu wedding barat ceria` | Klaster terbesar yang belum disentuh. Ulangi sudut artikel Mandarin: tandai lagu populer yang liriknya sebenarnya sedih atau tentang perpisahan. |
| 4 | Lagu Masuk Pengantin dan Kirab: dari Pelaminan sampai Lempar Bunga | `lagu masuk pengantin` | `lagu kirab pengantin` (saxophone, modern, sunda, minang, palembang), `lagu pengantin masuk pelaminan`, `lagu lempar bunga`, `lagu untuk wedding cake` | Melengkapi artikel first dance. Bisa menautkan artikel Jawa dan Mandarin untuk varian adat. |
| 5 | Lagu untuk Undangan Digital: Durasi, Bagian yang Dipotong, dan Soal Hak Cipta | `lagu undangan digital pernikahan` | `backsound undangan pernikahan`, `lagu undangan digital anti mainstream`, `lagu undangan digital islami`, `lagu undangan digital jawa` | Permintaan tinggi dan pesaingnya basi. Sisi hak cipta belum dibahas siapa pun. **Klaim hukum harus bersumber** (misalnya UU Hak Cipta No. 28/2014, kebijakan LMKN). |
| 6 | Lagu Lamaran dan Tunangan | `lagu lamaran` | `lagu lamaran romantis`, `lagu lamaran islami`, `lagu lamaran jawa`, `lagu tunangan`, `lagu engagement 2026` | Ditulis paling awal di perjalanan pasangan, jadi bisa menangkap pembaca sebelum mereka mencari venue. |
| 7 | Lagu Batak untuk Pernikahan, Termasuk untuk Orang Tua dan Boru | `lagu pernikahan batak` | `lagu batak untuk orang tua saat pernikahan`, `lagu pernikahan batak toba`, `lagu pernikahan batak karo`, `lagu untuk pernikahan kakak perempuan batak` | Komunitas Batak di Jakarta besar, dan ekor kuerinya kaya. Perlu narasumber atau sumber adat, jangan hanya daftar lagu. |
| 8 | Lagu Sunda untuk Pernikahan: Degung, Kecapi Suling, dan Pop Sunda | `lagu nikahan sunda` | `lagu sunda pernikahan`, `lagu degung sunda pernikahan`, `lagu kirab pengantin sunda`, `lagu seserahan sunda` | Pasangan dari artikel Jawa (Sep 2026). |
| 9 | Lagu untuk Pernikahan Teman, Sahabat, dan Kakak | `lagu untuk pernikahan teman` | `lagu untuk pernikahan sahabat`, `lagu untuk pernikahan kakak perempuan`, `lagu untuk story pernikahan teman`, `lagu duet pernikahan` | Trafik tinggi, tapi pembacanya tamu, bukan pasangan. Prioritas rendah untuk konversi. |

**Juga dipertimbangkan, tapi tidak masuk daftar:**
- **Perbarui** dua artikel Juni 2025 (Indonesia dan first dance) dengan entri 2026 daripada membuat artikel `lagu wedding 2026` baru. `list lagu wedding 2026` dan `lagu wedding terbaru 2026` sudah muncul sebagai saran, dan kedua artikel itu sudah berumur 17 bulan.
- **Lagu akad nikah:** cek dulu isi `musik-hiburan-pernikahan-islami`. Kalau momen akad belum dibahas, tambahkan satu bagian di sana alih-alih membuat artikel baru.
- **Vendor musik** (`harga band wedding jakarta`, `harga sewa gamelan jawa untuk pernikahan`): lebih cocok untuk landing page atau listing vendor kalau ada mitra sungguhan. Harga adalah data bisnis, jangan dikarang.
- **Dangdut, Korea, prewedding, Bugis, Minang:** permintaan Sedang. Lebih baik jadi bagian di artikel #4 atau #9.

## 7. Catatan penulisan

- **Jangan muat lirik lengkap.** Kutip satu atau dua baris saja untuk dibahas, lalu jelaskan artinya, seperti di artikel Mandarin.
- Judul lagu dan nama penyanyi harus dicek satu per satu. Daftar pesaing sering salah atribusi.
- Untuk lagu gereja, sebutkan bahwa setiap paroki dan jemaat punya aturan sendiri, dan pembaca sebaiknya menanyakan ke tim musik gereja.

## 8. Tambahan: lagu Katolik berbahasa Inggris (11 Nov 2026)

Pertanyaannya: apakah misa pernikahan Katolik bisa memakai lagu berbahasa Inggris, dan apakah itu layak dijadikan artikel sendiri?

### Permintaan dari pencari Indonesia

| Kueri | Saran | Catatan |
|---|---|---|
| `lagu pernikahan katolik bahasa inggris` | Muncul sebagai saran dari `lagu pernikahan katolik` (urutan ke-7 dari 10) dan dari `lagu katolik bahasa inggris` | **Kebutuhannya nyata**, tapi seed ini sendiri tidak punya ekor |
| `lagu katolik bahasa inggris` | 10: rohani, pernikahan, komuni, persembahan, gereja, misa, maria | Ada yang mencari lagu Inggris per bagian misa, tapi untuk misa umum, bukan khusus pernikahan |
| `lagu pemberkatan nikah bahasa inggris`, `lagu rohani pernikahan bahasa inggris` | 2 masing-masing, keduanya mengarah ke **Kristen** | Kebutuhan Inggris lebih kuat di sisi Protestan |
| `lagu perarakan / persembahan / komuni / penutup / tukar cincin ... bahasa inggris`, `lagu misa pernikahan bahasa inggris` | **0** | Tidak ada yang mencari per bagian dalam bahasa Inggris |
| `the wedding song kenny g` | 10 (sheet music, saxophone, piano, violin, backing track) | Instrumental, sering dipakai pemusik |
| `the wedding song paul stookey` | 10 (lyrics, chords, "there is love") | Lagu rohani-folk, cocok untuk pemberkatan |
| `wonderful day lagu pernikahan`, `the prayer lagu pernikahan` | 0–1 dalam bahasa Indonesia | Orang langsung mencari dengan judul Inggris |

Pembanding untuk klaster Indonesianya: `lagu misa pernikahan` (10: urutan, pembukaan, komuni, persembahan, penutup), `lagu komuni pernikahan` (5, termasuk `post komuni`), `mazmur pernikahan katolik` (6: edisi baru, edisi lama, mazmur tanggapan), `lagu antar bacaan pernikahan katolik` (3), `lagu ave maria pernikahan` (4, termasuk versi Indonesia).

**Kesimpulan:** jangan buat artikel terpisah untuk lagu Katolik berbahasa Inggris. Masukkan pilihan Inggris **di setiap bagian** artikel #1, dan arahkan judul/meta ke kueri Indonesia. Bagian "bisakah pakai lagu bahasa Inggris?" cukup jadi satu subjudul plus satu FAQ.

### Kueri Inggris (global, AU/SG sama)

`catholic wedding songs`, `catholic wedding hymns`, `catholic wedding music` semuanya punya 10 saran, dengan ekor per bagian: `for bride entrance`, `for offertory`, `for communion`, `recessional ... organ`, `mass song list`. Ada juga pertanyaan aturan: `songs allowed at catholic weddings`, `can you play your own music at a catholic wedding`, `catholic church wedding music guidelines`, `can ave maria be played at a wedding`. SERP-nya dikuasai paroki AS/Inggris dan situs pernikahan besar. **Tidak layak dikejar untuk Bali atau Singapura.**

### Yang ditemukan soal aturan (untuk bahan artikel, bukan untuk dikutip mentah)

- **KAJ tidak punya aturan publik** yang bisa ditemukan soal lagu Inggris atau lagu pop di misa pernikahan. Paroki punya dokumen "Ketentuan perkawinan" sendiri yang harus disetujui calon pengantin (contoh: [Paroki Blok Q](https://gerejasanta.org/perkawinan)). Artikel harus menyarankan pembaca bertanya ke sekretariat paroki dan tim liturgi, bukan memberi jawaban pasti.
- **Bahasanya tidak menjadi masalah, jenis lagunya yang menjadi masalah.** Pedoman paroki dan keuskupan di luar negeri konsisten: lagu cinta sekuler tidak cocok untuk liturgi, betapapun berartinya bagi pasangan, dan sebaiknya dipindah ke resepsi ([Archdiocese of Indianapolis](https://archindy.org/music/wedding.html), [Liturgy Office, Inggris & Wales](https://www.liturgyoffice.org/Resources/Marriage/Preparation/Prep-Music4.shtml), [Little Flower Memphis](https://littleflowermemphis.org/ministries/music-ministry/wedding-music/)). Sebagian paroki membolehkan lagu sekuler di prelude sebelum misa; ada juga yang melarangnya walaupun dimainkan instrumental. Mars Wagner dan Mendelssohn sering ditolak.
- **Pilihan Inggris/Latin yang berulang di pedoman tersebut:** Ave Maria (Schubert atau Gounod), Ubi Caritas, Ave Verum Corpus (Mozart), Air dari Water Music (Handel), Air on the G String (Bach), Canon (Pachelbel, instrumental), dan "Holy God, We Praise Thy Name" untuk penutup ([canticanova](https://www.canticanova.com/planning/other/pln_wed1_m.htm), [saintcecilia.org](https://www.saintcecilia.org/wedding-music-guidelines)).
- **"The Prayer", "Wonderful Day", dan lagu pop Inggris lain** banyak direkomendasikan oleh situs gaya hidup Indonesia untuk pemberkatan ([Popmama](https://www.popmama.com/life/relationship/ide-lagu-pernikahan-katolik-00-wz39d-n82q95), [Prepedu](https://prepedu.com/id/blog/english-wedding-songs)). Tapi tidak ada sumber yang mengonfirmasi bahwa paroki di Indonesia membolehkannya di dalam misa. **Jangan tulis bahwa lagu-lagu ini "boleh" di misa.** Tulis bahwa lagu ini sering dipakai, lalu sarankan pembaca menanyakan apakah lagu itu bisa diputar di prelude, sesudah berkat penutup, atau hanya di resepsi.

### Struktur yang disarankan untuk artikel #1

Satu tabel per bagian misa: pembukaan/perarakan, mazmur tanggapan, bait pengantar Injil, tukar cincin, persembahan, komuni, sesudah komuni / devosi Maria, penutup. Setiap baris memuat:
1. pilihan Indonesia (Madah Bakti / Puji Syukur, nomor dicek ke buku),
2. pilihan Inggris atau Latin yang memang lagu liturgi,
3. catatan apakah biasanya dibawakan koor, solo, atau instrumental.

Tambahkan satu bagian terpisah, "Lagu pop Inggris yang sering diminta, dan di mana biasanya ditempatkan", untuk menangkap kueri `the prayer wedding song` dan `wonderful day wedding song` tanpa memberi kesan bahwa lagu-lagu itu disetujui untuk liturgi.
