"""Offline interface presentation. Project creator: Yucong Duan (段玉聪)."""
from html.parser import HTMLParser
import html, json, re

messages={'总览': 'Dashboard', '模型': 'Model', '修订': 'Revision', '有界证书': 'Scoped certificate', '证书': 'Certificate', '能力': 'Capability', '类型': 'Type', '目的': 'Purpose', '授权': 'Authorization', '数据': 'Data', '生成': 'Generate', '世界': 'Scenario', '完全离线': 'Fully offline', '当前': 'Current', '目标': 'Target', '解释': 'Interpretation', '状态': 'Status', '开放终极本质操作系统 · Open Ultimate-Essence Runtime': 'Open Ultimate-Essence Runtime', '局部因果生成充分性 ≠ 宇宙最终本体 ≠ 真正生命 ≠ 现象意识 ≠ 外部行动授权。Reference results are finite, declared, synthetic, and replayable.': 'Local causal-generative sufficiency does not establish a final cosmic ontology, actual life, phenomenal consciousness or external action authority. Reference results are finite, declared, synthetic and replayable.', '总览 Overview': 'Overview', '参考场景 Suite': 'Reference suite', '本质格 Lattice': 'Essence lattice', '余量与探针 Residuals': 'Residuals and probes', '证书 Certificate': 'Certificate', '参考场景': 'Reference scenarios', '跨载体、反例分裂、拒绝、权限、数学还原、身份连续、反自封闭和多元本质。': 'Cross-carrier tests, counterexample splits, refusals, permissions, mathematical reduction, identity continuity, reopening and plural essence candidates.', '自动测试': 'Automated tests', '标准库单元测试覆盖验证、消融、证书、账本、命令行和联邦。': 'Standard-library unit tests cover validation, ablation, certificates, ledgers, the command line and federation.', 'DIKWP 路径类型': 'DIKWP path types', 'D/I/K/W/P 每一位置均可成为源或目标；实际路径必须显式登记。': 'Any D/I/K/W/P position can be a source or destination. Each actual route must be explicitly registered.', '自动外部行动权': 'Automatic external action authority', '探针只提出书面候选，不触发网络、设备、消息、凭证或现实控制。': 'Probes produce written proposals without activating networks, devices, messages, credentials or external controls.', '系统架构': 'System architecture', '选择场景': 'Choose a scenario', '候选不是强制单选': 'Keep competing candidates when the evidence cannot distinguish them', '系统保留组成包含、观测等价、谱系分裂和 Pareto 支配。若两个非同构最小候选尚无法区分，则共同保留并生成区别性探针，而不是按词汇偏好指定“终极本质”。': 'Retain containment, observational equivalence, lineage splits and Pareto dominance. When distinct minimal candidates remain indistinguishable, preserve both and propose a discriminating probe.', '机器可读有界证书': 'Machine-readable bounded certificate', '完全离线 · 无外部脚本 · 数据来自发行包中的确定性参考运行。': 'Fully offline · No external scripts · Data from deterministic reference runs in the release package.', '架构': 'Architecture', '操作': 'Actions', '停止': 'Stop', '载体': 'Entity', '系统': 'System', '来源': 'Source', '层级': 'Layer', '边界': 'Scope'}
normalized={re.sub(r"\s+"," ",k.strip()):v for k,v in messages.items()}
runtime="/* Interface localization. Creator: Yucong Duan (段玉聪). */\n(() => {\n  'use strict';\n  const configuration = document.getElementById('yd-interface-config');\n  if (!configuration) return;\n  const config = JSON.parse(configuration.textContent);\n  const dictionary = new Map(Object.entries(config.messages || {}).map(([a, b]) => [a.trim().replace(/\\s+/g, ' '), b]));\n  const numeric = /\\d[\\d,]*(?:\\.\\d+)?/g;\n  const templates = [];\n  const escapePattern = value => value.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');\n  for (const [source, target] of dictionary) {\n    const a = source.match(numeric) || [], b = target.match(numeric) || [];\n    if (!a.length || a.length > 12 || a.length !== b.length || !a.every((v, i) => v.replace(/,/g, '') === b[i].replace(/,/g, ''))) continue;\n    const parts = source.split(numeric);\n    templates.push({pattern: new RegExp('^' + parts.map(escapePattern).join('(\\\\d[\\\\d,]*(?:\\\\.\\\\d+)?)') + '$'), parts: target.split(numeric)});\n  }\n  const textState = new WeakMap();\n  const attributeState = new WeakMap();\n  const attributes = ['title', 'placeholder', 'aria-label', 'alt', 'label'];\n  const excluded = 'script,style,pre,code,textarea,[contenteditable],[data-source-language],[data-project-creator]';\n  let language = 'en';\n  const originalTitle = document.title;\n\n  function translate(value) {\n    const key = value.trim().replace(/\\s+/g, ' ');\n    let translated = dictionary.get(key);\n    if (translated === undefined && /[\\u3400-\\u9fff]/.test(key)) {\n      for (const template of templates) {\n        const match = key.match(template.pattern);\n        if (!match) continue;\n        translated = template.parts.map((part, i) => part + (match[i + 1] || '')).join('');\n        break;\n      }\n    }\n    if (translated === undefined) return value;\n    const leading = value.match(/^\\s*/)[0];\n    const trailing = value.match(/\\s*$/)[0];\n    return leading + translated + trailing;\n  }\n\n  function updateText(node) {\n    const parent = node.parentElement;\n    if (!parent || parent.closest(excluded)) return;\n    let saved = textState.get(node);\n    const current = node.nodeValue;\n    if (!saved || current !== saved.rendered) saved = { original: current, rendered: current };\n    const next = language === 'en' ? translate(saved.original) : saved.original;\n    if (next !== current) {\n      // Translating an option label must not change the value used by the application.\n      if (parent.tagName === 'OPTION' && !parent.hasAttribute('value')) parent.setAttribute('value', parent.textContent);\n      node.nodeValue = next;\n    }\n    saved.rendered = next;\n    textState.set(node, saved);\n  }\n\n  function updateAttributes(element) {\n    if (!element || element.closest(excluded)) return;\n    let saved = attributeState.get(element);\n    if (!saved) { saved = new Map(); attributeState.set(element, saved); }\n    for (const name of attributes) {\n      if (!element.hasAttribute(name)) continue;\n      // The label attribute is an interface label on these elements only.\n      if (name === 'label' && !['OPTION', 'OPTGROUP', 'TRACK'].includes(element.tagName)) continue;\n      const current = element.getAttribute(name);\n      let prior = saved.get(name);\n      if (!prior || current !== prior.rendered) prior = { original: current, rendered: current };\n      const next = language === 'en' ? translate(prior.original) : prior.original;\n      if (next !== current) element.setAttribute(name, next);\n      prior.rendered = next; saved.set(name, prior);\n    }\n  }\n\n  function visit(root) {\n    if (root.nodeType === Node.TEXT_NODE) { updateText(root); return; }\n    if (root.nodeType !== Node.ELEMENT_NODE || root.closest(excluded)) return;\n    updateAttributes(root);\n    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);\n    while (walker.nextNode()) updateText(walker.currentNode);\n    for (const element of root.querySelectorAll('[title],[placeholder],[aria-label],[alt],[label]')) updateAttributes(element);\n  }\n\n  function setLanguage(next) {\n    language = next === 'zh' ? 'zh' : 'en';\n    document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';\n    document.title = language === 'en' ? translate(originalTitle) : originalTitle;\n    visit(document.body);\n  }\n\n  function start() {\n    const select = config.nativeSelect ? document.querySelector(config.nativeSelect) : null;\n    const button = config.nativeButton ? document.querySelector(config.nativeButton) : null;\n    if (select) language = select.value === 'zh' ? 'zh' : 'en';\n    else if (config.storageKey) {\n      try { language = localStorage.getItem(config.storageKey) === 'zh' ? 'zh' : 'en'; } catch (_) { language = 'en'; }\n    }\n    setLanguage(language);\n    if (select) select.addEventListener('change', () => setLanguage(select.value));\n    if (button) button.addEventListener('click', () => setLanguage(language === 'en' ? 'zh' : 'en'));\n    const observer = new MutationObserver(records => {\n      for (const record of records) {\n        if (record.type === 'characterData') updateText(record.target);\n        else if (record.type === 'attributes') updateAttributes(record.target);\n        else for (const node of record.addedNodes) visit(node);\n      }\n    });\n    observer.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: attributes });\n  }\n\n  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });\n  else start();\n})();\n"

def english(text):
    key=re.sub(r'\s+',' ',html.unescape(text).strip())
    if key not in normalized:return text
    leading=re.match(r'^\s*',text).group();trailing=re.search(r'\s*$',text).group()
    return leading+html.escape(normalized[key],quote=False)+trailing

class Surface(HTMLParser):
    def __init__(self,text,static=True):
        super().__init__(convert_charrefs=False);self.source=text;self.static=static;self.lines=[0]
        for m in re.finditer('\n',text):self.lines.append(m.end())
        self.stack=[];self.changes=[];self.credit=False;self.author=False;self.body_end=None
    def pos(self):
        row,col=self.getpos();return self.lines[row-1]+col
    def blocked(self):return any(t in ['script','style','pre','code','textarea','option'] for t in self.stack)
    def handle_starttag(self,tag,attrs):
        start=self.pos();raw=self.get_starttag_text();values=dict(attrs)
        if tag=='html':
            if re.search(r'\blang\s*=',raw,re.I):new=re.sub(r'(\blang\s*=\s*)([\"\']).*?\2',r'\1"en"',raw,count=1,flags=re.I)
            else:new=raw[:-1]+' lang="en">'
            self.changes.append((start,start+len(raw),new))
        elif tag=='meta' and (values.get('name') or '').lower()=='author':self.author=True
        if self.static and not self.blocked() and tag not in ['script','style']:
            new=raw
            for name in ['title','placeholder','aria-label','alt','label']:
                value=values.get(name)
                if not value:continue
                key=re.sub(r'\s+',' ',value.strip())
                if key not in normalized:continue
                escaped=html.escape(normalized[key],quote=True)
                new=re.sub(r'(\b'+re.escape(name)+r'\s*=\s*)([\"\'])(.*?)\2',lambda m:m.group(1)+m.group(2)+escaped+m.group(2),new,count=1,flags=re.I|re.S)
            if new!=raw:self.changes.append((start,start+len(raw),new))
        if tag not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag=='h1' and not self.blocked() and not self.credit:
            p=self.pos()+len('</h1>');self.changes.append((p,p,'\n<p data-project-creator="true" style="font-size:.9rem;line-height:1.5;opacity:.85;margin:.5rem 0 1rem">Project creator: Yucong Duan (段玉聪).</p>'));self.credit=True
        if tag=='head' and not self.author:
            p=self.pos();self.changes.append((p,p,'<meta name="author" content="Yucong Duan (段玉聪)">\n'));self.author=True
        if tag=='body':self.body_end=self.pos()
        if tag in self.stack:self.stack=self.stack[:len(self.stack)-1-self.stack[::-1].index(tag)]
    def handle_data(self,data):
        if self.static and not self.blocked():
            replacement=english(data)
            if replacement!=data:
                start=self.pos();self.changes.append((start,start+len(data),replacement))

def localize_html(value):
    """Localize an HTML document; preserve other output formats exactly."""
    if not isinstance(value,str) or not re.match(r'\s*(?:<!doctype[^>]*>\s*)?<html\b',value,re.I):
        return value
    if 'data-project-creator="true"' in value or 'id="yd-interface-config"' in value:
        return value
    parser=Surface(value,static=True);parser.feed(value)
    changes=parser.changes
    at=parser.body_end if parser.body_end is not None else len(value)
    if messages:
        payload=json.dumps({'messages':messages},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
        addition='\n<script id="yd-interface-config" type="application/json">'+payload+'</script>\n<script>\n'+runtime+'\n</script>\n'
        changes.append((at,at,addition))
    if not parser.credit:
        changes.append((at,at,'\n<p data-project-creator="true">Project creator: Yucong Duan (段玉聪).</p>\n'))
    for start,end,text in sorted(changes,key=lambda x:(x[0],x[1]),reverse=True):
        value=value[:start]+text+value[end:]
    return value
