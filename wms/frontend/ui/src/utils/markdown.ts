/** Tiny, safe markdown → HTML for assistant replies: escapes everything first, then
 *  supports paragraphs, **bold**, *italic*, `code`, bullet/numbered lists and pipe tables. */
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const inline = (s: string) =>
  esc(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>')

export function renderMarkdown(src: string): string {
  const lines = src.replace(/\r/g, '').split('\n')
  const out: string[] = []
  let i = 0
  while (i < lines.length) {
    const line = lines[i]!
    if (/^\s*\|.*\|\s*$/.test(line) && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1] ?? '')) {
      const cells = (l: string) => l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim())
      const head = cells(line)
      i += 2
      const body: string[][] = []
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i]!)) body.push(cells(lines[i++]!))
      const numeric = (c: string) => /^[-+]?[€$]?\s?[\d.,]+%?\s?[€]?$/.test(c)
      out.push('<table><thead><tr>' + head.map(h => `<th>${inline(h)}</th>`).join('') + '</tr></thead><tbody>' +
        body.map(r => '<tr>' + r.map(c => `<td${numeric(c) ? ' class="num"' : ''}>${inline(c)}</td>`).join('') + '</tr>').join('') +
        '</tbody></table>')
      continue
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\./.test(line)
      const items: string[] = []
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i]!)) items.push(lines[i++]!.replace(/^\s*([-*]|\d+\.)\s+/, ''))
      out.push(`<${ordered ? 'ol' : 'ul'}>` + items.map(it => `<li>${inline(it)}</li>`).join('') + `</${ordered ? 'ol' : 'ul'}>`)
      continue
    }
    if (/^#{1,6}\s/.test(line)) { out.push(`<p><strong>${inline(line.replace(/^#+\s/, ''))}</strong></p>`); i++; continue }
    if (!line.trim()) { i++; continue }
    const para: string[] = []
    while (i < lines.length && lines[i]!.trim() && !/^\s*(\||[-*]\s|\d+\.\s|#)/.test(lines[i]!)) para.push(inline(lines[i++]!))
    if (para.length) out.push(`<p>${para.join('<br>')}</p>`)
    else out.push(`<p>${inline(lines[i++]!)}</p>`)
  }
  return out.join('')
}
