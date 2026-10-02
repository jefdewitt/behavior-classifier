import argparse
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any


LABELS = ("criticism", "defensiveness", "validation", "repair_attempt")
DIFFICULTIES = ("obvious", "subtle", "hard_negative")
LABEL_NAMES = {
    "criticism": "Criticism",
    "defensiveness": "Defensiveness",
    "validation": "Validation",
    "repair_attempt": "Repair attempt",
}


def score_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    for row in rows:
        gold = row["gold"]
        predicted = row["prediction"]
        if gold and predicted:
            counts["tp"] += 1
        elif gold:
            counts["fn"] += 1
        elif predicted:
            counts["fp"] += 1
        else:
            counts["tn"] += 1

    precision_denominator = counts["tp"] + counts["fp"]
    recall_denominator = counts["tp"] + counts["fn"]
    precision = counts["tp"] / precision_denominator if precision_denominator else 0.0
    recall = counts["tp"] / recall_denominator if recall_denominator else 0.0
    f1_denominator = precision + recall
    f1 = 2 * precision * recall / f1_denominator if f1_denominator else 0.0
    total = sum(counts.values())
    accuracy = (counts["tp"] + counts["tn"]) / total if total else 0.0
    return {
        "n": total,
        "tp": counts["tp"],
        "fp": counts["fp"],
        "tn": counts["tn"],
        "fn": counts["fn"],
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
    }


def load_experiment(path: Path, index: int) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        raw = json.load(file)
    predictions = raw.get("predictions")
    if not isinstance(predictions, list) or not predictions:
        raise ValueError(f"{path}: expected a non-empty predictions array")

    rows = []
    seen_ids = set()
    for prediction in predictions:
        sample_id = prediction.get("id")
        label = prediction.get("target_label")
        if not isinstance(sample_id, str) or label not in LABELS:
            raise ValueError(f"{path}: prediction has missing ID or unknown target label")
        if sample_id in seen_ids:
            raise ValueError(f"{path}: duplicate prediction ID {sample_id}")
        seen_ids.add(sample_id)

        label_prediction = prediction.get("predictions", {}).get(label, {})
        rows.append(
            {
                "id": sample_id,
                "plan_case_id": prediction.get("plan_case_id", ""),
                "target_label": label,
                "difficulty": prediction.get("difficulty", "unknown"),
                "gold": bool(prediction.get("expected_target_value")),
                "prediction": bool(prediction.get("predicted_target_value")),
                "confidence": label_prediction.get("confidence"),
                "evidence_is_exact": prediction.get("predicted_target_evidence_is_exact"),
                "evidence": prediction.get("predicted_target_evidence", ""),
                "decision_note": prediction.get("predicted_target_decision_note", ""),
            }
        )

    by_label = {label: score_rows([row for row in rows if row["target_label"] == label]) for label in LABELS}
    scores = [metric["f1"] for metric in by_label.values() if metric["n"]]
    all_scored_rows = [row for row in rows if row["target_label"] in LABELS]
    audited_rows = [row for row in all_scored_rows if isinstance(row["evidence_is_exact"], bool)]
    correct_evidence = sum(row["evidence_is_exact"] is True for row in audited_rows)
    return {
        "key": f"run-{index}",
        "name": raw.get("experiment_name") or raw.get("experiment") or path.stem,
        "experiment": raw.get("experiment"),
        "model": raw.get("model", "unknown"),
        "prompt_version": raw.get("prompt_version", "unknown"),
        "created_at_utc": raw.get("created_at_utc", ""),
        "input_file": raw.get("input_file", "unknown"),
        "input_sha256": raw.get("input_sha256", ""),
        "input_mode": raw.get("input_mode", "unknown"),
        "ontology_provided": raw.get("ontology_provided_to_classifier"),
        "n": len(rows),
        "macro_f1": sum(scores) / len(scores) if len(scores) == len(LABELS) else None,
        "by_label": by_label,
        "rows": rows,
        "evidence_audit": {
            "n": len(audited_rows),
            "exact": correct_evidence,
            "rate": correct_evidence / len(audited_rows) if audited_rows else None,
        },
        "source_path": path.name,
    }


def build_report(experiments: list[dict[str, Any]]) -> str:
    serialized = json.dumps(experiments, ensure_ascii=True, separators=(",", ":"))
    serialized = serialized.replace("</", "<\\/")
    run_names = " · ".join(html.escape(experiment["name"]) for experiment in experiments)
    return HTML_TEMPLATE.replace("__RUN_NAMES__", run_names).replace("__EXPERIMENTS__", serialized)


HTML_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>POC 2 | Experiment comparison</title>
<style>
:root{--ink:#202a30;--muted:#65737b;--paper:#f5f7f4;--white:#fff;--line:#dce3df;--teal:#167d78;--teal-soft:#d9eeea;--coral:#c54f45;--coral-soft:#f7e3df;--gold:#bc8825;--blue:#496b9b;--shadow:0 10px 30px rgba(24,43,45,.06)}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{background:#173d3d;color:#f5faf8;padding:34px max(24px,calc((100vw - 1200px)/2)) 30px;border-bottom:5px solid #7fc5b3}header .eyebrow{color:#a9d6c9;text-transform:uppercase;font-size:11px;font-weight:750;letter-spacing:.12em}h1{margin:5px 0 7px;font-size:32px;line-height:1.1;font-weight:720}header p{margin:0;color:#c6dcda;max-width:780px}.runs{margin-top:16px;font-size:12px;color:#d4e7e3}.page{max-width:1200px;margin:26px auto 70px;padding:0 22px}.notice{background:#fff4db;border:1px solid #ecd49a;color:#604a1c;padding:11px 14px;border-radius:7px;margin-bottom:18px;font-size:13px}.section{margin:24px 0 34px}.section-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:12px}.section h2{font-size:20px;margin:0;line-height:1.2}.section-head p{font-size:12px;color:var(--muted);margin:0;max-width:660px}.grid{display:grid;gap:14px}.kpis{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}.card,.panel{background:var(--white);border:1px solid var(--line);border-radius:7px;box-shadow:var(--shadow)}.kpi{padding:16px 18px;min-height:122px}.kpi .label{font-size:12px;color:var(--muted);font-weight:650}.kpi .value{font-size:30px;font-weight:760;line-height:1.15;margin:5px 0}.kpi .sub{font-size:12px;color:var(--muted)}.panel{padding:16px 18px}.charts{grid-template-columns:repeat(auto-fit,minmax(min(100%,510px),1fr))}.chart{width:100%;height:auto;display:block;overflow:visible}.legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:12px;margin-top:8px}.legend span{display:inline-flex;align-items:center;gap:6px}.swatch{height:9px;width:9px;border-radius:2px;display:inline-block}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:7px;background:#fff}.data{border-collapse:collapse;width:100%;font-size:13px}.data th,.data td{padding:9px 11px;text-align:left;border-bottom:1px solid #edf0ee;white-space:nowrap}.data th{background:#edf3f0;color:#47565a;font-size:11px;text-transform:uppercase;letter-spacing:.055em;position:sticky;top:0}.data tr:last-child td{border-bottom:0}.num{text-align:right!important;font-variant-numeric:tabular-nums}.pill{display:inline-block;padding:2px 7px;border-radius:99px;font-size:11px;background:#edf1ef;color:#47565a}.pill.good{background:var(--teal-soft);color:#125b55}.pill.bad{background:var(--coral-soft);color:#923a35}.heat{font-weight:700;text-align:center!important;min-width:55px}.tp,.tn{background:#e2f2ed;color:#155e4e}.fp,.fn{background:#fae7e3;color:#963d36}.na{color:#9aa4a3;background:#f6f7f6}.subtle{color:#8e6412;background:#fff4d8}.diff{color:#536577;background:#e9eff5}.callout{border-left:3px solid var(--gold);padding:10px 13px;background:#fff9eb;color:#5d5138;font-size:13px}.small{font-size:12px;color:var(--muted)}.two-col{grid-template-columns:1fr 1fr}.error-id{font-weight:700}.delta-positive{color:#167d78;font-weight:700}.delta-negative{color:#b74840;font-weight:700}.confusion{display:grid;grid-template-columns:repeat(2,minmax(30px,1fr));width:102px;gap:3px}.confusion div{padding:7px 4px;text-align:center;border-radius:3px;font-size:12px;font-weight:700}.confusion-label{font-size:10px;color:var(--muted)}.confidence-note{font-size:11px;color:var(--muted);margin-top:5px}.matrix-holder{max-height:520px;overflow:auto}.run-head{display:flex;align-items:center;gap:8px}.run-dot{height:9px;width:9px;border-radius:50%;display:inline-block}footer{margin-top:30px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}
@media(max-width:650px){header{padding:25px 20px}h1{font-size:27px}.page{padding:0 13px}.section-head{display:block}.section-head p{margin-top:5px}.panel{padding:12px}.charts{grid-template-columns:1fr}.two-col{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><div class="eyebrow">Behavior classifier · POC 2</div><h1>Performance, at a glance and under the lens</h1><p>Side-by-side experiment comparison across target labels, difficulty bands, error types, and confidence. The first input is the reference run.</p><div class="runs">Loaded: __RUN_NAMES__</div></header>
<main class="page">
<div id="dataset-warning"></div>
<section class="section"><div class="section-head"><h2>Run cards</h2><p>Quick read of each run’s overall score, evaluation coverage, and evidence audit coverage.</p></div><div id="kpis" class="grid kpis"></div></section>
<section class="section"><div class="section-head"><h2>Label performance</h2><p>Precision, recall, and F1 for each target label. Thin samples matter: each bar’s count is shown in the detail table below.</p></div><div class="panel"><svg id="label-chart" class="chart" viewBox="0 0 1000 340" role="img" aria-label="Grouped precision, recall, and F1 chart"></svg><div id="label-legend" class="legend"></div></div></section>
<section class="section"><div class="section-head"><h2>Confusion fingerprints</h2><p>Each tile shows true positives, false positives, false negatives, and true negatives. The paired cells make error tradeoffs visible even when F1 is similar.</p></div><div class="table-wrap"><table class="data" id="confusion-table"></table></div></section>
<section class="section"><div class="section-head"><h2>Where performance bends</h2><p>Target-conditioned F1 by difficulty. Hard-negative rows are valuable for exposing over-detection; small per-band counts make these directional rather than definitive.</p></div><div class="panel"><svg id="difficulty-chart" class="chart" viewBox="0 0 1000 330" role="img" aria-label="F1 by difficulty chart"></svg><div id="difficulty-legend" class="legend"></div></div></section>
<section class="section"><div class="section-head"><h2>Confidence reality check</h2><p>Self-reported confidence compared with observed correctness. A point above the diagonal is under-confident; below it is over-confident. Empty bins are omitted.</p></div><div class="grid charts"><div class="panel"><svg id="calibration-chart" class="chart" viewBox="0 0 600 400" role="img" aria-label="Confidence reliability chart"></svg><div id="confidence-legend" class="legend"></div><div class="confidence-note">Interpret cautiously: confidence is model-reported, and each bin may contain few predictions.</div></div><div class="panel"><div id="evidence-audit"></div></div></div></section>
<section class="section"><div class="section-head"><h2>Case-by-case outcome map</h2><p>Every frozen sample in one scan. Green is correct, coral is an error; hover a cell for gold, prediction, evidence, and the model’s note.</p></div><div class="table-wrap matrix-holder"><table class="data" id="case-matrix"></table></div></section>
<section class="section"><div class="section-head"><h2>What changed from the reference?</h2><p>Prediction flips across runs are often more actionable than score movement. Rows with the same decision in every run are omitted.</p></div><div class="table-wrap"><table class="data" id="flips-table"></table></div></section>
<section class="section"><div class="section-head"><h2>Error ledger</h2><p>Incorrect target-label calls, with evidence-quality status and model-generated likely reason. Treat explanations as review prompts, not ground truth.</p></div><div class="table-wrap"><table class="data" id="errors-table"></table></div></section>
<footer>Generated from experiment result JSON files. Metrics are recomputed from per-sample target predictions; reported summary metrics are not blindly trusted. “Evidence exact” reflects the run’s own audit field and is shown as a diagnostic, not a performance score.</footer>
</main>
<script>
const experiments=__EXPERIMENTS__;
const labels=["criticism","defensiveness","validation","repair_attempt"];
const labelNames={criticism:"Criticism",defensiveness:"Defensiveness",validation:"Validation",repair_attempt:"Repair attempt"};
const diffs=["obvious","subtle","hard_negative"];
const diffNames={obvious:"Obvious",subtle:"Subtle",hard_negative:"Hard negative"};
const palette=["#167d78","#496b9b","#bc8825","#c54f45","#725a8d","#4e7f45"];
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const pct=v=>v==null?"—":`${(v*100).toFixed(1)}%`;
const nfmt=v=>v==null?"—":Number(v).toFixed(2);
function score(rows){let tp=0,fp=0,tn=0,fn=0;for(const r of rows){if(r.gold&&r.prediction)tp++;else if(!r.gold&&r.prediction)fp++;else if(r.gold)fn++;else tn++;}const p=tp+fp?tp/(tp+fp):0,r=tp+fn?tp/(tp+fn):0;return {n:rows.length,tp,fp,tn,fn,precision:p,recall:r,f1:p+r?2*p*r/(p+r):0,accuracy:rows.length?(tp+tn)/rows.length:0};}
function rowsFor(run,label,filter=()=>true){return run.rows.filter(r=>(!label||r.target_label===label)&&filter(r));}
function computedMacro(run){const fs=labels.map(l=>score(rowsFor(run,l))).filter(x=>x.n).map(x=>x.f1);return fs.length===labels.length?fs.reduce((a,b)=>a+b,0)/fs.length:null;}
function evidenceRate(run){const rows=run.rows.filter(r=>typeof r.evidence_is_exact==="boolean");return rows.length?rows.filter(r=>r.evidence_is_exact).length/rows.length:null;}
function makeSvg(tag,attrs={},text=""){const el=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);if(text)el.textContent=text;return el;}
function txt(svg,x,y,text,attrs={}){svg.appendChild(makeSvg("text",{x,y,fill:"#526167","font-size":12,"font-family":"-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",...attrs},text));}
function legend(id,items){document.getElementById(id).innerHTML=items.map(x=>`<span><i class="swatch" style="background:${x.color}"></i>${esc(x.name)}</span>`).join("");}
function datasetWarnings(){const hashes=[...new Set(experiments.map(x=>x.input_sha256).filter(Boolean))];const ids=experiments.map(x=>new Set(x.rows.map(r=>r.id)));const notes=[];if(hashes.length>1)notes.push("Input hashes differ. Do not interpret score changes as a controlled comparison until the same frozen dataset is used.");if(ids.length>1){const base=ids[0];const mismatch=ids.slice(1).some(s=>s.size!==base.size||[...base].some(id=>!s.has(id)));if(mismatch)notes.push("The runs do not contain identical sample IDs; sample-level and score comparisons have different coverage.");}if(notes.length)document.getElementById("dataset-warning").innerHTML=`<div class="notice">${notes.map(esc).join(" ")}</div>`;}
function renderKpis(){const root=document.getElementById("kpis");root.innerHTML=experiments.map((run,i)=>{const m=computedMacro(run),ev=evidenceRate(run);return `<article class="card kpi"><div class="run-head"><i class="run-dot" style="background:${palette[i%palette.length]}"></i><div class="label">${esc(run.name)}</div></div><div class="value">${pct(m)}</div><div class="sub">Macro-F1 · ${run.rows.length} / ${esc(run.input_file||"input samples")} evaluated</div><div class="sub">Evidence exactness ${pct(ev)} · ${esc(run.model)}</div></article>`;}).join("");}
function renderLabelChart(){const svg=document.getElementById("label-chart");const W=1000,H=340,L=65,R=20,T=24,B=76,plotH=H-T-B,plotW=W-L-R;for(let t=0;t<=1.0001;t+=.2){const y=T+plotH*(1-t);svg.appendChild(makeSvg("line",{x1:L,y1:y,x2:W-R,y2:y,stroke:"#e4e9e6"}));txt(svg,L-10,y+4,`${Math.round(t*100)}`,{"text-anchor":"end","font-size":10});}txt(svg,17,T+plotH/2,"Score (%)",{transform:`rotate(-90 17 ${T+plotH/2})`,"text-anchor":"middle","font-size":11});const metrics=[{key:"precision",name:"Precision"},{key:"recall",name:"Recall"},{key:"f1",name:"F1"}];const groupW=plotW/labels.length,barW=Math.min(35,groupW/(experiments.length*3+2));labels.forEach((label,li)=>{const gx=L+li*groupW;txt(svg,gx+groupW/2,H-42,labelNames[label],{"text-anchor":"middle","font-size":12,"font-weight":650});experiments.forEach((run,ri)=>metrics.forEach((metric,mi)=>{const m=score(rowsFor(run,label));const x=gx+groupW/2-(experiments.length*3*barW)/2+(ri*3+mi)*barW;const h=plotH*m[metric.key];const color=mi===0?palette[ri%palette.length]:mi===1?palette[ri%palette.length]+"aa":palette[ri%palette.length]+"66";svg.appendChild(makeSvg("rect",{x,y:T+plotH-h,width:barW-2,height:h,rx:2,fill:color}));if(experiments.length===1)txt(svg,x+(barW-2)/2,T+plotH-h-5,`${Math.round(m[metric.key]*100)}`,{"text-anchor":"middle","font-size":9});}));});legend("label-legend",experiments.flatMap((run,i)=>metrics.map((m,mi)=>({name:`${run.name} · ${m.name}`,color:mi===0?palette[i%palette.length]:mi===1?palette[i%palette.length]+"aa":palette[i%palette.length]+"66"}))));}
function renderConfusion(){let h=`<thead><tr><th>Run</th><th>Target label</th><th>TP</th><th>FP</th><th>FN</th><th>TN</th><th>Precision</th><th>Recall</th><th>F1</th><th>n</th></tr></thead><tbody>`;for(const run of experiments)for(const label of labels){const m=score(rowsFor(run,label));h+=`<tr><td>${esc(run.name)}</td><td>${labelNames[label]}</td><td class="heat tp">${m.tp}</td><td class="heat fp">${m.fp}</td><td class="heat fn">${m.fn}</td><td class="heat tn">${m.tn}</td><td class="num">${pct(m.precision)}</td><td class="num">${pct(m.recall)}</td><td class="num"><b>${pct(m.f1)}</b></td><td class="num">${m.n}</td></tr>`;}document.getElementById("confusion-table").innerHTML=h+"</tbody>";}
function renderDifficulty(){const svg=document.getElementById("difficulty-chart");const W=1000,H=330,L=65,R=20,T=24,B=60,ph=H-T-B,pw=W-L-R;for(let t=0;t<=1.0001;t+=.2){const y=T+ph*(1-t);svg.appendChild(makeSvg("line",{x1:L,y1:y,x2:W-R,y2:y,stroke:"#e4e9e6"}));txt(svg,L-10,y+4,`${Math.round(t*100)}`,{"text-anchor":"end","font-size":10});}const gw=pw/diffs.length;diffs.forEach((d,di)=>{const x0=L+di*gw;txt(svg,x0+gw/2,H-25,diffNames[d],{"text-anchor":"middle","font-size":12,"font-weight":650});experiments.forEach((run,ri)=>{const selected=rowsFor(run,null,r=>r.difficulty===d);const m=score(selected);const bw=Math.min(70,gw/(experiments.length+1));const x=x0+gw/2+(ri-(experiments.length-1)/2)*bw-bw/2;const h=ph*m.f1;svg.appendChild(makeSvg("rect",{x,y:T+ph-h,width:bw-5,height:h,rx:3,fill:palette[ri%palette.length]}));txt(svg,x+bw/2-2,T+ph-h-6,`${Math.round(m.f1*100)}% · n=${m.n}`,{"text-anchor":"middle","font-size":10,"font-weight":650});});});legend("difficulty-legend",experiments.map((x,i)=>({name:x.name,color:palette[i%palette.length]})));}
function renderCalibration(){const svg=document.getElementById("calibration-chart");const W=600,H=400,L=57,R=24,T=25,B=55,S=Math.min(W-L-R,H-T-B);for(let i=0;i<=4;i++){const v=i/4,x=L+S*v,y=T+S*(1-v);svg.appendChild(makeSvg("line",{x1:L,y1:y,x2:L+S,y2:y,stroke:"#e4e9e6"}));svg.appendChild(makeSvg("line",{x1:x,y1:T,x2:x,y2:T+S,stroke:"#eef1ef"}));txt(svg,L-10,y+4,`${Math.round(v*100)}`,{"text-anchor":"end","font-size":10});txt(svg,x,T+S+22,`${Math.round(v*100)}`,{"text-anchor":"middle","font-size":10});}svg.appendChild(makeSvg("line",{x1:L,y1:T+S,x2:L+S,y2:T,stroke:"#9aa6a3","stroke-dasharray":"5 5"}));txt(svg,L+S/2,H-8,"Mean reported confidence (%)",{"text-anchor":"middle","font-size":11});txt(svg,14,T+S/2,"Observed accuracy (%)",{transform:`rotate(-90 14 ${T+S/2})`,"text-anchor":"middle","font-size":11});experiments.forEach((run,ri)=>{const buckets=Array.from({length:5},()=>[]);for(const row of run.rows){const c=Number(row.confidence);if(Number.isFinite(c)){buckets[Math.min(4,Math.floor(c*5))].push(row);}}buckets.forEach((bucket,bi)=>{if(!bucket.length)return;const avg=bucket.reduce((a,r)=>a+Number(r.confidence),0)/bucket.length;const acc=bucket.filter(r=>r.gold===r.prediction).length/bucket.length;const x=L+S*avg,y=T+S*(1-acc);svg.appendChild(makeSvg("circle",{cx:x,cy:y,r:Math.min(11,5+bucket.length/4),fill:palette[ri%palette.length],opacity:.82,stroke:"white","stroke-width":2}));txt(svg,x,y+3,String(bucket.length),{fill:"#fff","text-anchor":"middle","font-size":9,"font-weight":700});});});legend("confidence-legend",experiments.map((x,i)=>({name:x.name,color:palette[i%palette.length]})));}
function renderEvidence(){const root=document.getElementById("evidence-audit");root.innerHTML=`<h3 style="margin:2px 0 8px">Evidence exactness audit</h3><p class="small">Percentage of target predictions whose evidence was marked as an exact focal-turn quote by that run.</p>${experiments.map((run,i)=>{const rate=evidenceRate(run);const n=run.rows.filter(r=>typeof r.evidence_is_exact==="boolean").length;return `<div style="margin:18px 0"><div style="display:flex;justify-content:space-between;font-size:13px"><b>${esc(run.name)}</b><b>${pct(rate)}</b></div><div style="height:9px;background:#edf1ef;border-radius:8px;margin:6px 0"><div style="height:9px;width:${rate==null?0:rate*100}%;background:${palette[i%palette.length]};border-radius:8px"></div></div><div class="small">${n} samples audited · ${n-run.evidence_audit.exact} flagged non-exact</div></div>`;}).join("")}<div class="callout">Evidence can be poor even when a classification is correct. This diagnostic should complement, not replace, label metrics.</div>`;}
function allSampleIds(){return [...new Set(experiments.flatMap(run=>run.rows.map(r=>r.id)))].sort((a,b)=>{const x=experiments.flatMap(r=>r.rows).find(r=>r.id===a),y=experiments.flatMap(r=>r.rows).find(r=>r.id===b);return labels.indexOf(x.target_label)-labels.indexOf(y.target_label)||diffs.indexOf(x.difficulty)-diffs.indexOf(y.difficulty)||a.localeCompare(b);});}
function cellClass(r){if(!r)return"na";return r.gold?(r.prediction?"tp":"fn"):(r.prediction?"fp":"tn");}
function cellCode(r){return !r?"—":r.gold?(r.prediction?"TP":"FN"):(r.prediction?"FP":"TN");}
function renderCaseMatrix(){const ids=allSampleIds();let h=`<thead><tr><th>Sample</th><th>Target</th><th>Difficulty</th><th>Gold</th>${experiments.map(x=>`<th>${esc(x.name)}</th>`).join("")}</tr></thead><tbody>`;for(const id of ids){const rs=experiments.map(run=>run.rows.find(r=>r.id===id));const base=rs.find(Boolean);h+=`<tr><td class="error-id">${esc(id)}</td><td>${labelNames[base.target_label]}</td><td><span class="pill ${base.difficulty==='subtle'?'subtle':base.difficulty==='hard_negative'?'diff':''}">${diffNames[base.difficulty]||esc(base.difficulty)}</span></td><td>${base.gold?"Positive":"Negative"}</td>${rs.map((r,i)=>`<td class="heat ${cellClass(r)}" title="${r?esc(`${experiments[i].name}: ${r.prediction?'positive':'negative'} (confidence ${r.confidence??'n/a'})\nEvidence: ${r.evidence}\nNote: ${r.decision_note}`):'Sample absent from this run'}">${cellCode(r)}</td>`).join("")}</tr>`;}document.getElementById("case-matrix").innerHTML=h+"</tbody>";}
function renderFlips(){const ids=allSampleIds();let rows=[];for(const id of ids){const rs=experiments.map(run=>run.rows.find(r=>r.id===id));const vals=rs.filter(Boolean).map(r=>r.prediction);if(new Set(vals).size>1)rows.push({id,base:rs.find(Boolean),rs});}let h=`<thead><tr><th>Sample</th><th>Target</th><th>Difficulty</th><th>Gold</th>${experiments.map(x=>`<th>${esc(x.name)}</th>`).join("")}</tr></thead><tbody>`;if(!rows.length)h+=`<tr><td colspan="${4+experiments.length}" class="small">No prediction flips between the provided runs.</td></tr>`;for(const item of rows)h+=`<tr><td class="error-id">${esc(item.id)}</td><td>${labelNames[item.base.target_label]}</td><td>${diffNames[item.base.difficulty]||esc(item.base.difficulty)}</td><td>${item.base.gold?"Positive":"Negative"}</td>${item.rs.map(r=>`<td>${r?r.prediction?'<span class="pill good">Positive</span>':'<span class="pill bad">Negative</span>':'—'}</td>`).join("")}</tr>`;document.getElementById("flips-table").innerHTML=h+"</tbody>";}
function renderErrors(){const errors=experiments.flatMap((run,i)=>run.rows.filter(r=>r.gold!==r.prediction).map(r=>({run,i,r})));errors.sort((a,b)=>a.i-b.i||labels.indexOf(a.r.target_label)-labels.indexOf(b.r.target_label)||a.r.id.localeCompare(b.r.id));let h=`<thead><tr><th>Run</th><th>Sample</th><th>Target</th><th>Difficulty</th><th>Gold</th><th>Prediction</th><th>Confidence</th><th>Evidence audit</th><th>Likely reason · model-generated</th></tr></thead><tbody>`;if(!errors.length)h+=`<tr><td colspan="9">No target-label errors.</td></tr>`;for(const {run,r} of errors)h+=`<tr><td>${esc(run.name)}</td><td class="error-id">${esc(r.id)}</td><td>${labelNames[r.target_label]}</td><td>${diffNames[r.difficulty]||esc(r.difficulty)}</td><td>${r.gold?"Positive":"Negative"}</td><td>${r.prediction?"Positive":"Negative"}</td><td class="num">${r.confidence==null?"—":pct(r.confidence)}</td><td>${r.evidence_is_exact==null?"Not audited":r.evidence_is_exact?'<span class="pill good">Exact</span>':'<span class="pill bad">Not exact</span>'}</td><td style="white-space:normal;min-width:260px">${esc(r.decision_note)||'<span class="small">No note</span>'}</td></tr>`;document.getElementById("errors-table").innerHTML=h+"</tbody>";}
datasetWarnings();renderKpis();renderLabelChart();renderConfusion();renderDifficulty();renderCalibration();renderEvidence();renderCaseMatrix();renderFlips();renderErrors();
</script>
</body>
</html>'''


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an offline visual comparison report from POC 2 experiment result JSON files."
    )
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        required=True,
        help="Experiment result JSON; repeat for each run (first input is the reference).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "experiment_comparison.html",
        help="HTML report path (default: poc2/experiment_comparison.html).",
    )
    args = parser.parse_args()
    inputs = [path.resolve() for path in args.input]
    experiments = [load_experiment(path, index) for index, path in enumerate(inputs)]
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(experiments), encoding="utf-8")
    print(f"Loaded {len(experiments)} experiment run(s): {', '.join(item['source_path'] for item in experiments)}")
    print(f"Saved visualization dashboard to {output}")


if __name__ == "__main__":
    main()