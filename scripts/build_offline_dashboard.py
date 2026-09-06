from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs" / "reference"
TARGET = ROOT / "web" / "DIKWP_ESSENCE_OMEGA_OS_Offline_Demo.html"


def load_runs() -> list[dict]:
    runs = []
    for directory in sorted(path for path in OUTPUTS.iterdir() if path.is_dir()):
        certificate = json.loads((directory / "essence_certificate.json").read_text(encoding="utf-8"))
        evaluations = json.loads((directory / "candidate_evaluations.json").read_text(encoding="utf-8"))
        lattice = json.loads((directory / "essence_lattice.json").read_text(encoding="utf-8"))
        probe = json.loads((directory / "probe_plan.json").read_text(encoding="utf-8"))
        manifest = json.loads((directory / "output_manifest.json").read_text(encoding="utf-8"))
        runs.append({"certificate": certificate, "evaluations": evaluations, "lattice": lattice, "probe": probe, "manifest": manifest})
    return runs


def main() -> None:
    runs = load_runs()
    architecture = (ROOT / "assets" / "architecture.svg").read_text(encoding="utf-8")
    data = json.dumps(runs, ensure_ascii=False).replace("</", "<\\/")
    html_text = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DIKWP-ESSENCE-OMEGA-OS · Offline Demo</title>
<style>
:root{{--bg:#071525;--panel:#0d2334;--panel2:#132f43;--text:#edf8fb;--muted:#9fc1ce;--cyan:#54d8ce;--blue:#5795ff;--gold:#f5bd57;--red:#ff7c96;--green:#55d9a1;--purple:#c795ff}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 20% 0,#163a50 0,#071525 45%);color:var(--text);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
a{{color:var(--cyan)}}header{{padding:48px 6vw 20px;max-width:1500px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4.8rem);line-height:1.02;margin:0}}.sub{{color:var(--cyan);font-size:1.25rem;margin-top:14px}}.boundary{{margin-top:22px;padding:15px 18px;border-left:4px solid var(--red);background:#281c2a;border-radius:9px;color:#ffd5dc}}nav{{display:flex;gap:10px;flex-wrap:wrap;margin:26px 0}}button{{border:1px solid #2e6173;background:#0f2b3d;color:var(--text);padding:10px 14px;border-radius:999px;cursor:pointer}}button.active,button:hover{{background:#1b5264;border-color:var(--cyan)}}main{{max-width:1500px;margin:auto;padding:0 6vw 80px}}section{{display:none}}section.active{{display:block}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card{{background:linear-gradient(145deg,var(--panel),var(--panel2));border:1px solid #234b5d;border-radius:18px;padding:20px;box-shadow:0 12px 35px #0005}}.card h3{{margin-top:0}}.metric{{font-size:2rem;font-weight:800;color:var(--cyan)}}.tag{{display:inline-block;padding:3px 9px;border-radius:999px;margin:2px;font-size:.78rem;background:#18394c;color:#cbeaf0}}.good{{color:var(--green)}}.warn{{color:var(--gold)}}.bad{{color:var(--red)}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:9px;border-bottom:1px solid #285064;vertical-align:top}}th{{color:#bceee9}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#06111c;padding:14px;border-radius:12px;color:#c7e8ef}}.arch{{background:white;border-radius:18px;overflow:auto;padding:6px}}.arch svg{{width:100%;height:auto}}.runbtn{{display:block;width:100%;text-align:left;border-radius:12px;margin:6px 0}}.two{{display:grid;grid-template-columns:minmax(230px,.7fr) minmax(0,2fr);gap:18px}}@media(max-width:850px){{.two{{grid-template-columns:1fr}}}}.bar{{height:9px;background:#07131e;border-radius:99px;overflow:hidden}}.bar span{{display:block;height:100%;background:linear-gradient(90deg,var(--cyan),var(--blue))}}.footer{{color:var(--muted);margin-top:30px}}
</style>
</head>
<body>
<header>
<h1>DIKWP-ESSENCE-OMEGA-OS</h1>
<div class="sub">开放终极本质操作系统 · Open Ultimate-Essence Runtime</div>
<div class="boundary">局部因果生成充分性 ≠ 宇宙最终本体 ≠ 真正生命 ≠ 现象意识 ≠ 外部行动授权。Reference results are finite, declared, synthetic, and replayable.</div>
<nav>
<button class="active" data-tab="overview">总览 Overview</button><button data-tab="suite">参考场景 Suite</button><button data-tab="lattice">本质格 Lattice</button><button data-tab="residuals">余量与探针 Residuals</button><button data-tab="certificate">证书 Certificate</button>
</nav>
</header>
<main>
<section id="overview" class="active">
<div class="grid">
<div class="card"><div class="metric">{len(runs)}</div><h3>参考场景</h3><p>跨载体、反例分裂、拒绝、权限、数学还原、身份连续、反自封闭和多元本质。</p></div>
<div class="card"><div class="metric">67</div><h3>自动测试</h3><p>标准库单元测试覆盖验证、消融、证书、账本、命令行和联邦。</p></div>
<div class="card"><div class="metric">25</div><h3>DIKWP 路径类型</h3><p>D/I/K/W/P 每一位置均可成为源或目标；实际路径必须显式登记。</p></div>
<div class="card"><div class="metric">0</div><h3>自动外部行动权</h3><p>探针只提出书面候选，不触发网络、设备、消息、凭证或现实控制。</p></div>
</div>
<h2>系统架构</h2><div class="arch">{architecture}</div>
</section>
<section id="suite"><div class="two"><div class="card"><h3>选择场景</h3><div id="runButtons"></div></div><div id="runDetail" class="card"></div></div></section>
<section id="lattice"><div class="card"><h2>候选不是强制单选</h2><p>系统保留组成包含、观测等价、谱系分裂和 Pareto 支配。若两个非同构最小候选尚无法区分，则共同保留并生成区别性探针，而不是按词汇偏好指定“终极本质”。</p><div id="latticeView"></div></div></section>
<section id="residuals"><div class="two"><div id="residualList" class="card"></div><div id="probeView" class="card"></div></div></section>
<section id="certificate"><div class="card"><h2>机器可读有界证书</h2><pre id="certificateJson"></pre></div></section>
<div class="footer">完全离线 · 无外部脚本 · 数据来自发行包中的确定性参考运行。</div>
</main>
<script>
const RUNS={data}; let current=0;
const tabs=[...document.querySelectorAll('nav button')];tabs.forEach(b=>b.onclick=()=>{{tabs.forEach(x=>x.classList.remove('active'));document.querySelectorAll('main section').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.tab).classList.add('active')}});
function esc(x){{return String(x??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}
function cls(s){{return /CERTIFIED|SATISFIED|PROPOSED/.test(s)?'good':/OPEN|NOT_ESTABLISHED|PARTIAL/.test(s)?'warn':'bad'}}
function renderButtons(){{document.getElementById('runButtons').innerHTML=RUNS.map((r,i)=>`<button class="runbtn ${{i===current?'active':''}}" onclick="selectRun(${{i}})">${{esc(r.certificate.title.zh)}}<br><small>${{esc(r.certificate.scenario_id)}}</small></button>`).join('')}}
function selectRun(i){{current=i;renderButtons();renderAll()}}
function renderAll(){{const r=RUNS[current],c=r.certificate,e=r.evaluations;
 document.getElementById('runDetail').innerHTML=`<h2>${{esc(c.title.zh)}}</h2><p>${{esc(c.title.en)}}</p><p><b>局部：</b><span class="${{cls(c.local_essence_status)}}">${{esc(c.local_essence_status)}}</span><br><b>终极：</b><span class="warn">${{esc(c.ultimate_essence_status)}}</span></p><h3>候选</h3><table><tr><th>ID</th><th>状态</th><th>层级</th><th>保真</th><th>组件</th></tr>${{e.map(x=>`<tr><td>${{esc(x.candidate_id)}}</td><td class="${{cls(x.status)}}">${{esc(x.status)}}</td><td>${{esc(x.essence_level)}}</td><td>${{(x.metrics.fidelity*100).toFixed(0)}}%</td><td>${{x.components.map(y=>`<span class=tag>${{esc(y)}}</span>`).join('')}}</td></tr>`).join('')}}</table><h3>运行哈希</h3><pre>${{esc(r.manifest.run_hash)}}</pre>`;
 const l=r.lattice;document.getElementById('latticeView').innerHTML=`<p><b>Pareto frontier:</b> ${{l.pareto_frontier.map(x=>`<span class=tag>${{esc(x)}}</span>`).join('')}}</p><h3>观测等价</h3><pre>${{esc(JSON.stringify(l.equivalence_edges,null,2))}}</pre><h3>谱系</h3><pre>${{esc(JSON.stringify(l.lineage_edges,null,2))}}</pre>`;
 const open=c.residual_frontier.open_items;document.getElementById('residualList').innerHTML=`<h2>余量前沿</h2>${{open.length?open.map(x=>`<div class=card style="margin:10px 0"><b>${{esc(x.residual_id)}}</b> <span class=tag>${{esc(x.type)}}</span><p>${{esc(x.description_zh||x.description)}}</p></div>`).join(''):'<p class=good>声明范围内无开放余量</p>'}}`;
 const p=r.probe;document.getElementById('probeView').innerHTML=`<h2>区别性探针</h2><p class="${{cls(p.status)}}"><b>${{esc(p.status)}}</b></p><p>选择：${{esc(p.selected_probe_id||'无')}}</p><table><tr><th>探针</th><th>硬门</th><th>区分力</th></tr>${{p.evaluated_probes.map(x=>`<tr><td>${{esc(x.probe_id)}}</td><td class="${{x.hard_filter_passed?'good':'bad'}}">${{x.hard_filter_passed}}</td><td>${{(x.discrimination*100).toFixed(0)}}%</td></tr>`).join('')}}</table><p>自动外部行动权：<b>0</b></p>`;
 document.getElementById('certificateJson').textContent=JSON.stringify(c,null,2);
}}
renderButtons();renderAll();
</script>
</body></html>'''
    TARGET.write_text(html_text, encoding="utf-8")
    print(TARGET)


if __name__ == "__main__":
    main()
