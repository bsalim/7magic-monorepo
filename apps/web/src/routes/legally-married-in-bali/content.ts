/**
 * The facts behind "Is a Bali wedding legal in Australia?", each with the
 * primary source it was checked against on LAST_CHECKED.
 *
 * Only primary sources: the Australian Government (embassy, consulate,
 * Smartraveller, Attorney-General's Department), Indonesian legislation as
 * published by the BPK legal database, the Badung regency registry and the
 * HCCH. Several claims the ranking guides repeat did not survive that check and
 * are deliberately absent: a "recognised since 1 January 1995" date (no legal
 * basis found; the Marriage Act applies to foreign marriages before or after
 * its Part VA), a fixed count of recognised religions, a sponsor letter, and a
 * rule that Catholic couples must marry in a church (reported only in news
 * coverage, so the page says to ask the parish).
 */

import type { Source } from '$lib/tools/bali-dates';

export const PATH = '/legally-married-in-bali';
export const LAST_CHECKED = '2026-10-21';

export type Fact = { text: string; source: Source };

const EMBASSY: Source = {
  title: 'Australian Embassy Indonesia: getting married in Indonesia',
  url: 'https://indonesia.embassy.gov.au/jakt/MarriageInd.html'
};
const SMARTRAVELLER_MARRIAGE: Source = {
  title: 'Smartraveller: getting married overseas (updated 18 August 2026)',
  url: 'https://www.smartraveller.gov.au/planning-trip/advice-your-planned-activities/getting-married-overseas'
};
const AGD_GET_MARRIED: Source = {
  title: "Attorney-General's Department: getting married",
  url: 'https://www.ag.gov.au/families-and-marriage/marriage/get-married'
};
const AGD_EQUALITY: Source = {
  title: "Attorney-General's Department: marriage equality in Australia",
  url: 'https://www.ag.gov.au/families-and-marriage/marriage/marriage-equality-australia'
};
const MARRIAGE_LAW: Source = {
  title: 'Indonesian Marriage Law No. 1 of 1974 (BPK legal database)',
  url: 'https://peraturan.bpk.go.id/Download/36382/UU%20Nomor%201%20Tahun%201974.pdf'
};
const PP_9_1975: Source = {
  title: 'Government Regulation No. 9 of 1975, Article 3 (BPK legal database)',
  url: 'https://peraturan.bpk.go.id/Download/58020/PP%20NO%209%20TH%201975.pdf'
};
const PERPRES_96_2018: Source = {
  title: 'Presidential Regulation No. 96 of 2018, Article 37 (BPK legal database)',
  url: 'https://peraturan.bpk.go.id/Download/88465/Perpres%20Nomor%2096%20Tahun%202018.pdf'
};
const BADUNG: Source = {
  title: 'Badung Regency civil registry: marriage certificate service',
  url: 'https://pelayanan-publik.badungkab.go.id/service/layanan-aku-sapa-penerbitan-3-in-1-akta-perkawinan/7826f413-d417-42c3-aba5-c37b267af3d7'
};
const CONSULATE_SERVICES: Source = {
  title: 'Australian Consulate-General Bali: consular and notarial services',
  url: 'https://bali.consulate.gov.au/blli/consular.html'
};
const CONSULATE_FEES: Source = {
  title: 'Australian Consulate-General Bali: fees (June 2026 schedule)',
  url: 'https://bali.consulate.gov.au/blli/Fees.html'
};
const SMARTRAVELLER_NOTARIAL: Source = {
  title: 'Smartraveller: notarial services and fees',
  url: 'https://www.smartraveller.gov.au/our-role/notarial-services#fees'
};
const SMARTRAVELLER_INDONESIA: Source = {
  title: 'Smartraveller: Indonesia travel advice (updated 16 October 2026)',
  url: 'https://www.smartraveller.gov.au/destinations/asia/indonesia'
};
const HCCH: Source = {
  title: 'HCCH: Apostille Convention status table',
  url: 'https://www.hcch.net/en/instruments/conventions/status-table/?cid=41'
};
const HCCH_AUTHORITY: Source = {
  title: 'HCCH: Indonesia’s competent authority for apostilles',
  url: 'https://www.hcch.net/en/states/authorities/details3/?aid=1167'
};
const BALI_SE_7_2025: Source = {
  title: 'Governor of Bali Circular No. 7 of 2025 on conduct for foreign tourists',
  url: 'https://cloud-ng.baliprov.go.id/disparda/2025/04/SE-NO-7-TAHUN-2025-TENTANG-TATA-TERTIB-WISATAWAN-ASING.pdf'
};

export const FACTS = {
  celebrant: {
    text: 'An Australian-authorised marriage celebrant can only marry couples in Australia. A marriage overseas cannot be performed by one, and cannot be registered in Australia.',
    source: AGD_GET_MARRIED
  },
  recognised: {
    text: 'A marriage made overseas cannot be registered in Australia, but it is usually recognised here, as long as it was valid in the country where it took place and would have been valid in Australia.',
    source: SMARTRAVELLER_MARRIAGE
  },
  nameChange: {
    text: 'An overseas marriage certificate may not be accepted as proof of a name change. Check with the births, deaths and marriages registry in your state first.',
    source: SMARTRAVELLER_MARRIAGE
  },
  sameSexAustralia: {
    text: 'Since 9 December 2017, same-sex marriages that took place overseas are generally recognised in Australia.',
    source: AGD_EQUALITY
  },
  religionLaw: {
    text: 'Under Article 2 of Indonesia’s Marriage Law, a marriage is valid when it is carried out under the law of each partner’s religion and belief, and every marriage must be recorded. The law’s official explanation adds that there is no marriage outside religious law, so there is no civil-only wedding.',
    source: MARRIAGE_LAW
  },
  sameReligion: {
    text: 'In practice both partners must hold the same religion recognised in Indonesia, or one partner converts.',
    source: EMBASSY
  },
  sameSexLaw: {
    text: 'Article 1 of Indonesia’s Marriage Law defines marriage as a bond between one man and one woman.',
    source: MARRIAGE_LAW
  },
  sameSexIndonesia: {
    text: 'Smartraveller advises that same-sex relationships are not legally recognised in Indonesia, and that its criminal code penalises sex and cohabitation outside marriage.',
    source: SMARTRAVELLER_INDONESIA
  },
  muslim: {
    text: 'Muslim couples marry through the KUA (Office of Religious Affairs), which issues the marriage book. Everyone else registers with the civil registry after the religious ceremony.',
    source: EMBASSY
  },
  notice: {
    text: 'Notice of the marriage goes to the civil registry where you will marry at least 10 working days before the wedding.',
    source: PP_9_1975
  },
  documentsLaw: {
    text: 'For a foreign partner the registry asks for the religious leader’s marriage letter, colour photos, a passport, and permission to marry from your own country, which for Australians is the Certificate of No Impediment.',
    source: PERPRES_96_2018
  },
  documentsBadung: {
    text: 'The Badung registry (Kuta, Seminyak, Canggu, Uluwatu, Nusa Dua) also asks for 4×6 cm photos, a copy of the passport, and a divorce or death certificate if either of you was married before.',
    source: BADUNG
  },
  documentsEmbassy: {
    text: 'The Australian Embassy also tells couples to bring birth certificates, and originals plus copies of everything; requirements vary by province.',
    source: EMBASSY
  },
  cniWho: {
    text: 'The Certificate of No Impediment (CNI) comes from the Australian Embassy in Jakarta or a Consulate-General. The Bali Consulate-General in Denpasar covers Bali, NTB and NTT.',
    source: EMBASSY
  },
  cniTiming: {
    text: 'The CNI is usually issued while you wait if your documents are complete. It has no expiry date, but registries do not normally accept one issued more than three months before the wedding.',
    source: EMBASSY
  },
  cniBooking: {
    text: 'Notarial services at the Bali Consulate-General are by appointment only, booked through its online customer portal.',
    source: CONSULATE_SERVICES
  },
  cniFee: {
    text: 'A CNI costs A$181 in 2026 (Rp2,232,000 at the Bali consulate), paid by card only and not refundable. Australian notarial fees rise with inflation each January.',
    source: CONSULATE_FEES
  },
  apostilleAustralia: {
    text: 'An Australian apostille costs A$105 in 2026.',
    source: SMARTRAVELLER_NOTARIAL
  },
  apostilleIndonesia: {
    text: 'Indonesia joined the Apostille Convention on 4 June 2022.',
    source: HCCH
  },
  apostilleAuthority: {
    text: 'Indonesian apostilles are issued by the Directorate General of General Legal Administration (AHU) at the Ministry of Law.',
    source: HCCH_AUTHORITY
  },
  temples: {
    text: 'Bali’s rules for foreign visitors reserve the inner and middle courtyards of a temple for worship in Balinese dress, ban climbing sacred trees and buildings, and ban indecent photos at sacred places.',
    source: BALI_SE_7_2025
  }
} satisfies Record<string, Fact>;

export const ALL_SOURCES: Source[] = [
  ...new Map(Object.values(FACTS).map((fact) => [fact.source.url, fact.source])).values()
];
