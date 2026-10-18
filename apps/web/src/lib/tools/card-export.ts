/**
 * Turns a tool's SVG card into a PNG or a printed page, in the browser.
 *
 * No server rendering and no new dependency: the SVG is serialised, drawn into
 * a canvas through an <img>, and the canvas encoded. The catch is fonts. An SVG
 * loaded as an image is sandboxed and cannot see the page's web fonts, so the
 * card would come out in a fallback face. The two faces the card uses are
 * therefore fetched (from the same files the site already serves, so usually
 * from cache) and inlined into the SVG as data URLs.
 */

import jostUrl from '@fontsource-variable/jost/files/jost-latin-wght-normal.woff2?url';
import poppins500Url from '@fontsource/poppins/files/poppins-latin-500-normal.woff2?url';
import poppins600Url from '@fontsource/poppins/files/poppins-latin-600-normal.woff2?url';

const SVG_NS = 'http://www.w3.org/2000/svg';

let fontCss: Promise<string> | null = null;

async function dataUrl(url: string): Promise<string> {
  const blob = await (await fetch(url)).blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });
}

/** Built once per page view; a second export reuses it. */
function embeddedFonts(): Promise<string> {
  fontCss ??= Promise.all([dataUrl(poppins500Url), dataUrl(poppins600Url), dataUrl(jostUrl)])
    .then(
      ([p500, p600, jost]) => `
@font-face{font-family:'Poppins';font-weight:500;src:url(${p500}) format('woff2')}
@font-face{font-family:'Poppins';font-weight:600;src:url(${p600}) format('woff2')}
@font-face{font-family:'Jost Variable';font-weight:100 900;src:url(${jost}) format('woff2')}`
    )
    .catch(() => {
      // A missing font costs typography, not the export: fall back and retry next time.
      fontCss = null;
      return '';
    });
  return fontCss;
}

async function standaloneSvg(svg: SVGSVGElement, width: number, height: number): Promise<string> {
  const clone = svg.cloneNode(true) as SVGSVGElement;
  clone.setAttribute('xmlns', SVG_NS);
  clone.setAttribute('width', String(width));
  clone.setAttribute('height', String(height));
  // The preview may be blurred or scaled by CSS; the export never is.
  clone.removeAttribute('class');
  clone.removeAttribute('style');
  const style = document.createElementNS(SVG_NS, 'style');
  style.textContent = await embeddedFonts();
  clone.insertBefore(style, clone.firstChild);
  return new XMLSerializer().serializeToString(clone);
}

export async function svgToPng(svg: SVGSVGElement, width: number, height: number): Promise<Blob> {
  const markup = await standaloneSvg(svg, width, height);
  const url = URL.createObjectURL(new Blob([markup], { type: 'image/svg+xml;charset=utf-8' }));
  try {
    const image = new Image();
    image.decoding = 'async';
    image.src = url;
    await image.decode();

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Canvas 2D is unavailable');
    // Safari can hand back the first draw before the inlined fonts are applied;
    // a second draw after a frame is cheap and lands with the right faces.
    context.drawImage(image, 0, 0, width, height);
    await new Promise((resolve) => requestAnimationFrame(resolve));
    context.clearRect(0, 0, width, height);
    context.drawImage(image, 0, 0, width, height);

    return await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob(
        (blob) => (blob ? resolve(blob) : reject(new Error('PNG encoding failed'))),
        'image/png'
      )
    );
  } finally {
    URL.revokeObjectURL(url);
  }
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  // Revoked late: some browsers start the download only after click() returns.
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

/**
 * Gives every id in a copied SVG a suffix, and points its url(#...) references
 * at the new names. While the copy is printed the original is in a hidden
 * subtree, and a gradient referenced by a duplicate id would resolve to the
 * hidden one, which some browsers do not paint.
 */
function suffixIds(root: Element, suffix: string): void {
  const ids = new Set([...root.querySelectorAll('[id]')].map((node) => node.id));
  for (const node of root.querySelectorAll('*')) {
    if (ids.has(node.id)) node.id = `${node.id}${suffix}`;
    for (const attr of [...node.attributes]) {
      const rewritten = attr.value.replace(/url\(#([^)]+)\)/g, (match, id: string) =>
        ids.has(id) ? `url(#${id}${suffix})` : match
      );
      if (rewritten !== attr.value) node.setAttribute(attr.name, rewritten);
    }
  }
}

const PRINT_ROOT_ID = 'tool-card-print';
const PRINT_CLASS = 'tool-card-printing';

/**
 * Prints only the card, on one A5 page.
 *
 * The card is copied into a top-level node and everything else is hidden for
 * the duration, rather than relying on a permanent print stylesheet: printing
 * the article below the tool with Ctrl+P should still print the article. The
 * `@page` size is injected for the same reason, since it cannot be scoped to
 * an element, and both are removed once the print dialog closes.
 */
export function printCard(svg: SVGSVGElement): void {
  const root = document.createElement('div');
  root.id = PRINT_ROOT_ID;
  const clone = svg.cloneNode(true) as SVGSVGElement;
  clone.removeAttribute('class');
  clone.removeAttribute('style');
  suffixIds(clone, '-print');
  root.append(clone);

  const style = document.createElement('style');
  style.textContent = `
@page { size: A5 portrait; margin: 0; }
@media print {
  html.${PRINT_CLASS} body > *:not(#${PRINT_ROOT_ID}) { display: none !important; }
  #${PRINT_ROOT_ID} {
    display: flex !important; align-items: center; justify-content: center;
    width: 148mm; height: 210mm; background: #fbf7f0;
    print-color-adjust: exact; -webkit-print-color-adjust: exact;
  }
  #${PRINT_ROOT_ID} svg { width: 148mm; height: 185mm; }
}
@media screen { #${PRINT_ROOT_ID} { display: none; } }`;

  document.head.append(style);
  document.body.append(root);
  document.documentElement.classList.add(PRINT_CLASS);

  const cleanup = () => {
    document.documentElement.classList.remove(PRINT_CLASS);
    root.remove();
    style.remove();
    window.removeEventListener('afterprint', cleanup);
  };
  window.addEventListener('afterprint', cleanup);
  window.print();
  // Browsers that block in print() have already fired afterprint; the rest
  // fire it later. Either way the second call is a no-op.
  setTimeout(cleanup, 60_000);
}
