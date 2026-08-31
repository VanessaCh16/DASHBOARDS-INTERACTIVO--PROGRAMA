
import re
import os
from io import StringIO, BytesIO
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import Image as RLImage
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                  PageBreak, HRFlowable)

st.set_page_config(page_title="OptiFlow | Multi-Pozo", layout="wide", page_icon="🛢️")

# ══════════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
.stApp{
    background:linear-gradient(135deg,#10141c 0%,#151b26 50%,#1a212d 100%) !important;
}
.block-container{padding-top:.5rem !important;padding-left:1rem !important;padding-right:1rem !important;max-width:1500px !important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#10141c,#161c27) !important;border-right:1px solid rgba(140,160,185,.12) !important;}
[data-testid="stSidebar"] *{color:#dde4ec !important;}
div[data-testid="stPlotlyChart"]{border-radius:10px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,.25);}

/* ── HERO ── */
.hero{padding:13px 18px;border-radius:10px;background:linear-gradient(135deg,#1c2735,#222e3d);
  border:1px solid rgba(140,160,185,.18);box-shadow:0 6px 16px rgba(0,0,0,.25);margin-bottom:12px;color:white;}
.hero h1{margin:0;font-size:1.4rem;font-weight:700;color:#eef2f7;}
.hero p{margin:3px 0 0;color:#9aabbd;font-size:.85rem;}

/* ── FIELD KPIs ── */
.fk-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:14px;}
.fk{background:#1b212c;border:1px solid rgba(150,165,185,.14);border-radius:13px;padding:10px 13px;}
.fk-l{font-size:10px;color:#7c8da0;margin-bottom:3px;text-transform:uppercase;letter-spacing:.04em;}
.fk-v{font-size:18px;font-weight:900;color:#e8edf3;}
.fk-s{font-size:11px;color:#9aabbd;margin-top:2px;}

/* ── PANEL ── */
.panel{background:#1b212c;border:1px solid rgba(150,165,185,.14);border-radius:16px;padding:14px;}
.panel h3{margin:0 0 11px;font-size:13px;font-weight:700;color:#e8edf3;display:flex;align-items:center;gap:6px;}

/* ── FORM ── */
.field label{display:block;font-size:11px;color:#9aabbd;margin-bottom:3px;}
.field input{width:100%;height:32px;font-size:12px;padding:0 8px;
  border:1px solid rgba(150,165,185,.14);border-radius:9px;
  background:rgba(255,255,255,.05);color:#e8edf3;}
.frow{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;}
.frow3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;}
.add-btn{width:100%;margin-top:6px;padding:8px;font-size:13px;font-weight:700;border-radius:10px;
  background:rgba(91,141,184,.12);border:1px solid rgba(91,141,184,.30);color:#5B8DB8;cursor:pointer;}
.add-btn:hover{background:rgba(91,141,184,.20);}

/* ── RANK ── */
.rank-empty{padding:18px;text-align:center;color:#7c8da0;font-size:12px;
  border:1px dashed rgba(150,165,185,.14);border-radius:11px;}
.rrow{display:flex;align-items:center;gap:8px;padding:7px 9px;border-radius:10px;
  border:1px solid rgba(150,165,185,.14);margin-bottom:5px;cursor:default;}
.rrow:hover{background:rgba(255,255,255,.04);}
.rpos{font-size:16px;width:26px;text-align:center;flex-shrink:0;}
.rinfo{flex:1;min-width:0;}
.rname{font-size:13px;font-weight:700;color:#e8edf3;}
.rsub{font-size:11px;color:#9aabbd;}
.rbar{height:3px;background:rgba(255,255,255,.08);border-radius:2px;margin-top:3px;overflow:hidden;}
.rbar-fill{height:100%;border-radius:2px;background:rgba(29,194,100,.75);}
.rgain{font-size:12px;font-weight:700;color:#6FA287;text-align:right;}
.rmeta{font-size:11px;color:#7c8da0;text-align:right;}
.tstrip{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px;}
.ts{background:rgba(255,255,255,.05);border-radius:10px;padding:8px 10px;text-align:center;}
.ts-l{font-size:10px;color:#7c8da0;margin-bottom:2px;}
.ts-v{font-size:13px;font-weight:700;color:#e8edf3;}

/* ── WELL CARD ── */
.wgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(195px,1fr));gap:10px;}
.wc{background:#1b212c;border:1px solid rgba(150,165,185,.14);border-radius:15px;padding:12px;}
.wc:hover{border-color:rgba(91,141,184,.35);}
.wc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;}
.wc-name{font-size:14px;font-weight:900;color:#e8edf3;}
.wc-check{width:18px;height:18px;border-radius:50%;border:1px solid rgba(150,165,185,.16);
  display:flex;align-items:center;justify-content:center;font-size:10px;color:transparent;}
.wc-check.on{background:#6FA287;border-color:#6FA287;color:#07111e;}
.wc-meta{font-size:11px;color:#7c8da0;margin-bottom:7px;}
.wc-prog{height:3px;border-radius:2px;background:rgba(255,255,255,.07);overflow:hidden;margin-bottom:7px;}
.wc-prog-fill{height:100%;border-radius:2px;}
.badges{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:8px;}
.badge{font-size:10px;padding:2px 7px;border-radius:999px;font-weight:700;}
.b-ready{background:rgba(29,194,100,.18);color:#6FA287;border:1px solid rgba(29,194,100,.28);}
.b-partial{background:rgba(241,162,8,.18);color:#ffd27a;border:1px solid rgba(241,162,8,.28);}
.b-empty{background:rgba(150,165,185,.14);color:#9aabbd;border:1px solid rgba(150,165,185,.16);}
.b-opt{background:rgba(29,194,100,.18);color:#6FA287;border:1px solid rgba(29,194,100,.28);}
.b-rev{background:rgba(241,162,8,.18);color:#ffd27a;border:1px solid rgba(241,162,8,.28);}
.b-crit{background:rgba(201,163,104,.18);color:#d9b896;border:1px solid rgba(201,163,104,.28);}
.slbl{font-size:10px;color:#7c8da0;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px;margin-top:6px;}
.sgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:2px;}
.sbox{background:rgba(255,255,255,.05);border-radius:8px;padding:5px 6px;}
.sbox-l{font-size:10px;color:#7c8da0;}
.sbox-v{font-size:12px;font-weight:700;color:#e8edf3;}
.sbox-v.good{color:#6FA287;}
.sbox-v.info{color:#5B8DB8;}
.sec-head{background:linear-gradient(90deg,#1c2530,#222d3a);border:1px solid rgba(150,165,185,.14);
  border-left:3px solid #5B8DB8;border-radius:8px;padding:9px 15px;margin:12px 0 10px;color:#eef2f7;font-size:.98rem;font-weight:700;
  box-shadow:0 4px 12px rgba(0,0,0,.18);}
.anim-head{background:linear-gradient(90deg,#1c2530,#2b3645,#222d3a,#1c2530);background-size:300% 100%;
  animation:hm 6s ease infinite;border-left:3px solid #C9A368;border-radius:8px;padding:9px 15px;margin:12px 0 10px;
  color:#eef2f7;font-size:.98rem;font-weight:700;box-shadow:0 4px 12px rgba(0,0,0,.18);}
@keyframes hm{0%{background-position:0%50%}50%{background-position:100%50%}100%{background-position:0%50%}}
.kpi{background:rgba(255,255,255,.06);border:1px solid rgba(150,165,185,.14);border-radius:12px;
  padding:9px 12px;position:relative;overflow:hidden;}
.kpi:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;
  background:linear-gradient(180deg,#5B8DB8,#C9A368);}
.kpi-t{color:#7c8da0;font-size:.66rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em;margin-bottom:3px;}
.kpi-v{color:#e8edf3;font-size:1.15rem;font-weight:900;line-height:1.1;}
.kpi-s{color:#9aabbd;font-size:.68rem;margin-top:3px;}
.nodal-card{position:relative;background:linear-gradient(135deg,#1c2934,#16232f,#101b26);
  border-radius:14px;padding:14px 14px 10px;overflow:hidden;border:1px solid rgba(255,255,255,.07);}
.nodal-card:before{content:"";position:absolute;inset:0;
  background:radial-gradient(circle at 25% 22%,rgba(0,212,255,.12),transparent 25%),
             radial-gradient(circle at 74% 40%,rgba(201,163,104,.08),transparent 24%);}
.ntitle{position:relative;z-index:2;color:#7c8da0;font-size:1rem;font-weight:900;margin-bottom:8px;}
.nleg{display:flex;gap:12px;margin-top:5px;color:#9aabbd;font-size:.70rem;font-weight:800;}
.lc{display:inline-block;width:16px;height:4px;border-radius:999px;margin-right:4px;vertical-align:middle;
    background:#5B8DB8;}
.lp{display:inline-block;width:16px;height:4px;border-radius:999px;margin-right:4px;vertical-align:middle;
    background:#C9A368;}
.nstats{display:flex;justify-content:flex-end;gap:12px;margin-top:5px;position:relative;z-index:2;}
.ns{text-align:right;}
.ns span{display:block;font-size:.76rem;color:#7c8da0;font-weight:800;}
.ns b{display:block;color:#e8edf3;font-size:.92rem;}
.nsbig{font-size:2rem;font-weight:950;color:white;line-height:1;}
.cinema{position:relative;background:radial-gradient(circle at 20% 20%,rgba(0,169,199,.28),transparent 28%),
  radial-gradient(circle at 78% 35%,rgba(245,66,145,.22),transparent 24%),
  linear-gradient(135deg,#07111e,#0b1c30,#102f45);
  border-radius:18px;overflow:hidden;padding:14px;border:1px solid rgba(255,255,255,.12);color:white;}
.cinema:before{content:"";position:absolute;inset:0;
  background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);
  background-size:30px 30px;animation:gm 9s linear infinite;}
@keyframes gm{0%{background-position:0 0}100%{background-position:60px 60px}}
.cc{position:relative;z-index:2;}
.ckpis{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:9px;}
.ck{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.12);border-radius:11px;padding:7px;}
.ck b{display:block;font-size:.94rem;color:white;}
.ck span{font-size:.64rem;color:#c5d2e0;}
.dl{stroke-dasharray:900;stroke-dashoffset:900;animation:dl 3.2s ease-in-out infinite;}
.dld{animation-delay:.55s;}
@keyframes dl{0%{stroke-dashoffset:900;opacity:.12}45%{stroke-dashoffset:0;opacity:1}78%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:-900;opacity:.12}}
.mpt{animation:mp 1.4s ease-in-out infinite;}
@keyframes mp{0%,100%{r:7;opacity:.55}50%{r:11;opacity:1}}
.impact-card{background:white;border:1px solid rgba(32,90,120,.12);border-radius:14px;padding:12px;}
.impact-card h3{margin:0 0 9px;color:#172033;font-size:1rem;font-weight:900;}
.irow{display:flex;align-items:center;gap:9px;padding:8px 0;border-bottom:1px solid #e6eef6;}
.irow:last-child{border-bottom:0;}
.iico{width:30px;height:30px;border-radius:10px;display:grid;place-items:center;
  color:white;font-weight:900;background:linear-gradient(135deg,#5B8DB8,#C9A368);flex-shrink:0;font-size:.9rem;}
.ilbl{flex:1;font-size:11px;color:#61738a;}
.ival{font-size:13px;font-weight:700;color:#173f63;}
.s-ok{background:#e7f8ef;border-left:5px solid #19a463;padding:8px 11px;border-radius:11px;
  margin-bottom:8px;color:#11351f;font-size:.83rem;}
.s-warn{background:#fff4dc;border-left:5px solid #B08F5C;padding:8px 11px;border-radius:11px;
  margin-bottom:8px;color:#4c3500;font-size:.83rem;}
.s-crit{background:#ffe7ee;border-left:5px solid #C9A368;padding:8px 11px;border-radius:11px;
  margin-bottom:8px;color:#64132d;font-size:.83rem;}
.s-base{background:#edf2f7;border-left:5px solid #64748b;padding:8px 11px;border-radius:11px;
  margin-bottom:8px;color:#253142;font-size:.83rem;}
.mgrid{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:8px;}
.mbox{background:rgba(255,255,255,.05);border:1px solid rgba(150,165,185,.14);padding:8px;border-radius:10px;}
.mbox b{color:#e8edf3;font-size:1rem;display:block;}
.mbox span{display:block;color:#7c8da0;font-size:.70rem;margin-top:2px;}
.final{background:linear-gradient(135deg,#0d2140,#153558,rgba(0,169,199,.15));color:white;
  border-radius:15px;padding:14px 16px;margin-top:8px;border:1px solid rgba(150,165,185,.14);
  font-size:.90rem;line-height:1.55;}
.ftag{display:inline-block;background:rgba(255,255,255,.10);padding:3px 8px;border-radius:999px;
  margin-right:5px;font-size:.71rem;font-weight:800;}
.hint{padding:20px;text-align:center;color:#7c8da0;font-size:13px;
  border:1px dashed rgba(150,165,185,.14);border-radius:13px;}
.nl-ipr{fill:none;stroke:#5B8DB8;stroke-width:5;stroke-linecap:round;stroke-dasharray:900;stroke-dashoffset:900;animation:nd 3.4s ease-in-out infinite;}
.nl-vlp{fill:none;stroke:#C9A368;stroke-width:5;stroke-linecap:round;stroke-dasharray:900;stroke-dashoffset:900;animation:nd 3.4s ease-in-out infinite;animation-delay:.4s;}
.na-ipr{fill:url(#fc);opacity:.30;animation:ap 3.4s ease-in-out infinite;}
.na-vlp{fill:url(#fp);opacity:.22;animation:ap 3.4s ease-in-out infinite;animation-delay:.4s;}
.np{fill:white;stroke:#C9A368;stroke-width:3.5;animation:pp 1.6s ease-in-out infinite;}
.ng{stroke:rgba(255,255,255,.38);stroke-width:1.1;stroke-dasharray:5 4;fill:none;}
.nr{fill:#101b26;stroke:#e8edf3;stroke-width:1.5;opacity:.78;}
.ntl{fill:#9aabbd;font-size:10px;font-weight:700;}
.nta{fill:#e8edf3;font-size:11px;font-weight:800;}
.ngl{stroke:rgba(255,255,255,.05);stroke-width:1;}
.nlb{fill:#e8edf3;font-size:11px;font-weight:800;}
@keyframes nd{0%{stroke-dashoffset:900;opacity:.12}42%{stroke-dashoffset:0;opacity:1}78%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:-900;opacity:.12}}
@keyframes ap{0%,100%{opacity:.08}50%{opacity:.35}}
@keyframes pp{0%,100%{r:7;opacity:.72}50%{r:11;opacity:1}}

/* ── TRAZABILIDAD BOPD/BWPD ── */
.traz-box{background:#1E2530;border:1px solid rgba(46,109,164,.22);border-left:3px solid #2E6DA4;border-radius:8px;padding:14px 16px;margin:10px 0 8px;}
.traz-title{font-size:11.5px;font-weight:700;color:#6EAADC;text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px;}
.traz-grid{display:grid;grid-template-columns:1fr auto 1fr 1fr;gap:8px;align-items:center;}
.traz-item{background:rgba(46,109,164,.08);border:1px solid rgba(46,109,164,.14);border-radius:6px;padding:9px 12px;}
.traz-lbl{font-size:10px;color:#8A9DB5;margin-bottom:4px;font-weight:600;text-transform:uppercase;letter-spacing:.03em;}
.traz-val{font-size:15px;font-weight:700;color:#D8E0EA;}
.traz-val.up{color:#28A870;}
.traz-val.dn{color:#8A9DB5;}
.traz-arrow{font-size:20px;color:#2E6DA4;font-weight:700;text-align:center;padding:0 4px;}
.traz-formula{font-size:11px;color:#8A9DB5;margin-top:10px;padding:8px 12px;background:rgba(46,109,164,.06);border-radius:5px;border:1px solid rgba(46,109,164,.12);line-height:1.6;}
.traz-formula b{color:#6EAADC;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════════════
def tof(v):
    t=str(v).strip().replace(",",".")
    try: return float(t)
    except: return np.nan

def money(x):
    if pd.isna(x): return "—"
    return f"${x:,.0f}"

def cmoney(x):
    if pd.isna(x): return "—"
    if abs(x)>=1e6: return f"${x/1e6:.2f} MM"
    if abs(x)>=1e3: return f"${x/1e3:.1f} K"
    return f"${x:,.0f}"

def num(x,d=0):
    if pd.isna(x): return "—"
    return f"{x:,.{d}f}"

# ══════════════════════════════════════════════════════════════════
# GENERACIÓN DE REPORTES PDF (individual por pozo y global del campo)
# ══════════════════════════════════════════════════════════════════
_PDF_BLUE=rl_colors.HexColor("#1B3A5C")
_PDF_GRAY=rl_colors.HexColor("#5B6B7A")
_PDF_GREEN=rl_colors.HexColor("#2D7D4F")
_PDF_AMBER=rl_colors.HexColor("#A8762E")
_PDF_LIGHT=rl_colors.HexColor("#F0F3F6")
_PDF_LINE=rl_colors.HexColor("#D5DCE3")

def _pdf_styles():
    base=getSampleStyleSheet()
    styles={
        "title":ParagraphStyle("title",parent=base["Title"],fontSize=18,textColor=_PDF_BLUE,
            spaceAfter=4,alignment=TA_LEFT,fontName="Helvetica-Bold"),
        "subtitle":ParagraphStyle("subtitle",parent=base["Normal"],fontSize=10,textColor=_PDF_GRAY,
            spaceAfter=14,fontName="Helvetica"),
        "h2":ParagraphStyle("h2",parent=base["Heading2"],fontSize=13,textColor=_PDF_BLUE,
            spaceBefore=14,spaceAfter=8,fontName="Helvetica-Bold"),
        "body":ParagraphStyle("body",parent=base["Normal"],fontSize=9.5,textColor=rl_colors.HexColor("#222"),
            leading=14),
        "small":ParagraphStyle("small",parent=base["Normal"],fontSize=8,textColor=_PDF_GRAY,leading=11),
        "kpi_label":ParagraphStyle("kpi_label",parent=base["Normal"],fontSize=7.5,textColor=_PDF_GRAY,
            fontName="Helvetica-Bold",alignment=TA_CENTER),
        "kpi_value":ParagraphStyle("kpi_value",parent=base["Normal"],fontSize=13,textColor=_PDF_BLUE,
            fontName="Helvetica-Bold",alignment=TA_CENTER,spaceBefore=2),
    }
    return styles

def _pdf_header(story,styles,title,subtitle):
    story.append(Paragraph(title,styles["title"]))
    story.append(Paragraph(subtitle,styles["subtitle"]))
    story.append(HRFlowable(width="100%",thickness=1.2,color=_PDF_BLUE,spaceAfter=10))

def _pdf_kpi_row(story,styles,items):
    """items: lista de tuplas (label, value)"""
    cells_lbl=[Paragraph(lbl,styles["kpi_label"]) for lbl,_ in items]
    cells_val=[Paragraph(str(val),styles["kpi_value"]) for _,val in items]
    tbl=Table([cells_lbl,cells_val],colWidths=[(17.5*cm)/len(items)]*len(items))
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),_PDF_LIGHT),
        ("BOX",(0,0),(-1,-1),0.6,_PDF_LINE),
        ("INNERGRID",(0,0),(-1,-1),0.6,_PDF_LINE),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1,12))

def _pdf_data_table(story,styles,headers,rows,col_widths=None):
    data=[[Paragraph(f"<b>{h}</b>",styles["small"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c),styles["small"]) for c in r])
    if col_widths is None:
        col_widths=[(17.5*cm)/len(headers)]*len(headers)
    tbl=Table(data,colWidths=col_widths,repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),_PDF_BLUE),
        ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.white,_PDF_LIGHT]),
        ("GRID",(0,0),(-1,-1),0.5,_PDF_LINE),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("ALIGN",(1,0),(-1,-1),"RIGHT"),
        ("ALIGN",(0,0),(0,-1),"LEFT"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1,10))

def _pdf_ipr_vlp_chart(sc,ssum,hz_base,hz_rec):
    """Genera un gráfico IPR/VLP (caso base vs. recomendado) como imagen PNG para el PDF."""
    if sc is None or sc.empty or "LR" not in sc.columns or "VLP" not in sc.columns:
        return None
    fig,ax=plt.subplots(figsize=(7.2,4.2),dpi=150)
    has_ipr="IPR" in sc.columns
    g_base=sc[sc["Hz"]==hz_base].sort_values("LR")
    g_rec=sc[sc["Hz"]==hz_rec].sort_values("LR")
    if g_base.empty or g_rec.empty:
        plt.close(fig)
        return None
    if has_ipr:
        ax.plot(g_base["LR"],g_base["IPR"],color="#E05A5A",linestyle=":",linewidth=1.8,label="IPR (Afluencia)")
    ax.plot(g_base["LR"],g_base["VLP"],color="#9B9B9B",linewidth=2.2,label=f"VLP base ({hz_base:.0f} Hz)")
    ax.plot(g_rec["LR"],g_rec["VLP"],color="#4A90D9",linewidth=2.4,label=f"VLP recomendado ({hz_rec:.0f} Hz)")
    for hz,g,color in [(hz_base,g_base,"#555555"),(hz_rec,g_rec,"#2D5F8A")]:
        row=ssum[abs(ssum["Hz"]-hz)<0.1]
        if not row.empty:
            q=float(row.iloc[0]["BFPD"])
            pr=float(np.interp(q,g["LR"].values,g["VLP"].values))
            ax.plot([q],[pr],marker="D",markersize=7,color=color,markeredgecolor="white",markeredgewidth=1)
    ax.set_xlabel("Caudal de líquido (STB/d)",fontsize=9)
    ax.set_ylabel("Presión (psig)",fontsize=9)
    ax.set_title("Análisis nodal — caso base vs. recomendado",fontsize=10.5,color="#1E4A72",fontweight="bold")
    ax.legend(fontsize=8,frameon=False)
    ax.grid(True,linewidth=0.4,alpha=0.5)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    imgbuf=BytesIO()
    fig.savefig(imgbuf,format="png")
    plt.close(fig)
    imgbuf.seek(0)
    return imgbuf

def generate_well_pdf(pid,p):
    """Genera el PDF de reporte individual de un pozo con análisis completo."""
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=letter,
        topMargin=1.6*cm,bottomMargin=1.6*cm,leftMargin=1.5*cm,rightMargin=1.5*cm)
    styles=_pdf_styles()
    story=[]

    fecha=datetime.now().strftime("%d/%m/%Y %H:%M")
    _pdf_header(story,styles,f"OptiFlow — Reporte de pozo: {pid}",
        f"Análisis de optimización BES · Generado el {fecha}")

    br=p.get("base_row") or {}
    rec=p.get("rec_row") or {}
    ssum=p.get("summary")
    info=p.get("info",{})

    if not rec:
        story.append(Paragraph("Este pozo aún no tiene un análisis completo (faltan archivos PROSPER).",styles["body"]))
        doc.build(story)
        buf.seek(0)
        return buf

    # ── Ficha técnica ──
    story.append(Paragraph("Ficha técnica del pozo",styles["h2"]))
    ficha_rows=[
        ["Bomba",p.get("bomba") or info.get("pump","No detectada"),"Motor",info.get("motor","No detectado")],
        ["Cable",info.get("cable","No detectado"),"API (°)",f'{p.get("api","—")}'],
        ["BSW (%)",f'{p.get("bsw",0):.1f}%',"Precio petróleo","${:,.0f}/bbl".format(p.get("price",0))],
        ["Frecuencia base","{:.0f} Hz".format(br.get("Hz",0)),"Frecuencia máx. rec.","{:.0f} Hz".format(p.get("max_hz",0))],
    ]
    tbl=Table(ficha_rows,colWidths=[3.3*cm,5.4*cm,3.3*cm,5.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),_PDF_LIGHT),("BACKGROUND",(2,0),(2,-1),_PDF_LIGHT),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("GRID",(0,0),(-1,-1),0.5,_PDF_LINE),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1,12))

    # ── KPIs principales ──
    story.append(Paragraph("KPIs de optimización",styles["h2"]))
    _pdf_kpi_row(story,styles,[
        ("HZ BASE",f"{br.get('Hz',0):.0f} Hz"),
        ("HZ RECOMENDADA",f"{rec.get('Hz',0):.0f} Hz"),
        ("Δ BOPD",f"+{num(rec.get('dBOPD'),1)}"),
        ("GANANCIA/AÑO",cmoney(rec.get("RevYear"))),
    ])

    # ── Comparación base vs recomendado ──
    story.append(Paragraph("Comparación: caso base vs. escenario recomendado",styles["h2"]))
    _pdf_data_table(story,styles,
        ["Parámetro","Caso base","Recomendado","Δ"],
        [
            ["Frecuencia (Hz)",f"{br.get('Hz',0):.0f}",f"{rec.get('Hz',0):.0f}",
             f"+{rec.get('Hz',0)-br.get('Hz',0):.0f}"],
            ["BFPD",num(br.get("BFPD")),num(rec.get("BFPD")),f"+{num(rec.get('dBFPD'),0)}"],
            ["BOPD",num(br.get("BOPD")),num(rec.get("BOPD")),f"+{num(rec.get('dBOPD'),1)}"],
            ["BWPD",num(br.get("BWPD")),num(rec.get("BWPD")),"—"],
            ["Ganancia diaria","—",money(rec.get("RevDay")),"—"],
            ["Ganancia mensual","—",money(rec.get("RevMon")),"—"],
            ["Ganancia anual","—",money(rec.get("RevYear")),"—"],
            ["bbl/año incrementales","—",num(rec.get("RecBbl"),0),"—"],
        ],
        col_widths=[5.5*cm,4*cm,4*cm,4*cm]
    )

    # ── Gráfico IPR/VLP: caso base vs. recomendado ──
    curves=p.get("curves")
    chart_buf=_pdf_ipr_vlp_chart(curves,ssum,br.get("Hz",0),rec.get("Hz",0)) if curves is not None else None
    if chart_buf is not None:
        story.append(Paragraph("Curvas de análisis nodal (caso base vs. recomendado)",styles["h2"]))
        story.append(RLImage(chart_buf,width=16.5*cm,height=9.6*cm))
        story.append(Spacer(1,10))

    # ── Interpretación ──
    rst,_,_,_=classify(rec,p.get("max_hz",60),p.get("min_g",5))
    story.append(Paragraph("Interpretación y recomendación",styles["h2"]))
    interp=(f"El análisis compara el caso base de <b>{num(br.get('BFPD'))} BFPD a "
            f"{br.get('Hz',0):.0f} Hz</b> contra la alternativa recomendada de "
            f"<b>{num(rec.get('BFPD'))} BFPD a {rec.get('Hz',0):.0f} Hz</b>. "
            f"La optimización representa un incremento de <b>{num(rec.get('dBOPD'),1)} BOPD</b>, "
            f"equivalente a <b>{num(rec.get('RecBbl'),0)} barriles incrementales por año</b>, "
            f"con una ganancia anual estimada de <b>{money(rec.get('RevYear'))}</b>. "
            f"Estado de la recomendación: <b>{rst}</b>.")
    story.append(Paragraph(interp,styles["body"]))
    story.append(Spacer(1,8))
    story.append(Paragraph(
        "Nota: recomendación preliminar basada en análisis multicriterio (40% producción, "
        "30% economía, 20% riesgo operativo, 10% moderación de frecuencia). Debe validarse "
        "con restricciones reales de bomba, motor y cable antes de implementar.",
        styles["small"]))

    doc.build(story)
    buf.seek(0)
    return buf

def generate_field_pdf(pozos_dict):
    """Genera el PDF de reporte global comparando todos los pozos con análisis completo."""
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=letter,
        topMargin=1.6*cm,bottomMargin=1.6*cm,leftMargin=1.5*cm,rightMargin=1.5*cm)
    styles=_pdf_styles()
    story=[]

    fecha=datetime.now().strftime("%d/%m/%Y %H:%M")
    ready={pid:p for pid,p in pozos_dict.items() if p.get("ready")}

    _pdf_header(story,styles,"OptiFlow — Reporte global del campo",
        f"Comparación y ranking de oportunidades · {len(ready)} pozo(s) analizados · {fecha}")

    if not ready:
        story.append(Paragraph("Aún no hay pozos con análisis completo en el campo.",styles["body"]))
        doc.build(story); buf.seek(0); return buf

    total_gain=sum(p["rec_row"]["RevYear"] for p in ready.values())
    total_delta=sum(p["rec_row"]["dBOPD"] for p in ready.values())
    total_bfpd_base=sum((p.get("base_row") or {}).get("BFPD",0) or 0 for p in ready.values())

    story.append(Paragraph("Resumen ejecutivo del campo",styles["h2"]))
    _pdf_kpi_row(story,styles,[
        ("POZOS ANALIZADOS",str(len(ready))),
        ("BFPD TOTAL BASE",num(total_bfpd_base)),
        ("GANANCIA TOTAL/AÑO",cmoney(total_gain)),
        ("Δ BOPD TOTAL",f"+{total_delta:.1f}"),
    ])

    story.append(Paragraph("Ranking de oportunidades (por ganancia anual)",styles["h2"]))
    sorted_p=sorted(ready.items(),key=lambda kv:kv[1]["rec_row"]["RevYear"],reverse=True)
    rows=[]
    for i,(pid,p) in enumerate(sorted_p):
        rr=p["rec_row"]; br=p.get("base_row") or {}
        rows.append([
            f"{i+1}", pid, num(br.get("BFPD")), num(rr.get("BFPD")),
            f"+{num(rr.get('dBOPD'),1)}", cmoney(rr.get("RevYear")),
        ])
    _pdf_data_table(story,styles,
        ["#","Pozo","BFPD base","BFPD rec.","Δ BOPD","Ganancia/año"],rows,
        col_widths=[1.3*cm,3.2*cm,3.2*cm,3.2*cm,3.1*cm,3.7*cm])

    story.append(PageBreak())
    story.append(Paragraph("Detalle por pozo",styles["h2"]))
    for pid,p in sorted_p:
        rr=p["rec_row"]; br=p.get("base_row") or {}
        rst,_,_,_=classify(rr,p.get("max_hz",60),p.get("min_g",5))
        story.append(Paragraph(f"<b>{pid}</b> — {p.get('bomba') or 'Bomba no especificada'}",styles["body"]))
        line=(f"Base: {num(br.get('BFPD'))} BFPD a {br.get('Hz',0):.0f} Hz &nbsp;&gt;&gt;&nbsp; "
              f"Recomendado: {num(rr.get('BFPD'))} BFPD a {rr.get('Hz',0):.0f} Hz "
              f"(Δ {num(rr.get('dBOPD'),1)} BOPD, {cmoney(rr.get('RevYear'))}/año) — Estado: {rst}")
        story.append(Paragraph(line,styles["small"]))
        story.append(Spacer(1,8))

    doc.build(story)
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════════
# PARSERS PROSPER — versión completa compatible con archivos .prn
# ══════════════════════════════════════════════════════════════════
def extract_info(text):
    info={"pump":"No detectada","motor":"No detectado","cable":"No detectado"}
    # Solo patrones específicos que indican nombre/modelo de equipo, no genéricos
    patterns={
        "pump":[r"ESP Pump\s*[:\t]\s*(.+)",r"Current Pump\s*[:\t]\s*(.+)",r"Pump Type\s*[:\t]\s*(.+)"],
        "motor":[r"ESP Motor\s*[:\t]\s*(.+)",r"Current Motor\s*[:\t]\s*(.+)",r"Motor Type\s*[:\t]\s*(.+)"],
        "cable":[r"ESP Cable\s*[:\t]\s*(.+)",r"Current Cable\s*[:\t]\s*(.+)",r"Cable Type\s*[:\t]\s*(.+)"],
    }
    for key,regs in patterns.items():
        for rg in regs:
            match=re.search(rg,text,flags=re.I)
            if match:
                value=match.group(1).strip()
                # descartar si parece un número (sería una columna técnica, no un nombre de equipo)
                if value and len(value)>2 and not re.match(r"^[\d\.\-eE\s]+$",value):
                    info[key]=value[:95]; break
    return info

def parse_prn(text,fallback_freq=np.nan):
    info=extract_info(text)
    # Detectar Water Cut del encabezado para usar como BSW real si está disponible
    wc_match=re.search(r"Water Cut\s+([0-9]+(?:[\.,][0-9]+)?)",text,flags=re.I)
    detected_bsw=tof(wc_match.group(1)) if wc_match else np.nan
    info["bsw"]=detected_bsw

    lines=text.splitlines()
    cases=[]; current=None; header=[]; rows=[]; solution={}
    reading_table=False; reading_solution=False
    for line in lines:
        freq_match=re.search(r"Operating Frequency\s+([0-9]+(?:[\.,][0-9]+)?)",line,flags=re.I)
        if freq_match:
            if current is not None:
                current.update({"header":header,"rows":rows,"solution":solution}); cases.append(current)
            current={"frequency":tof(freq_match.group(1))}
            header,rows,solution=[],[],{}; reading_table=reading_solution=False; continue
        if "Liquid Rate" in line and "VLP Pressure" in line and "IPR Pressure" in line:
            # Si no hay caso abierto (archivo sin marcador de frecuencia, ej. caso base único)
            # se inicializa uno con la frecuencia de respaldo (fallback_freq)
            if current is None:
                current={"frequency":fallback_freq}
            header=[h.strip() for h in line.split("\t") if h.strip()]
            reading_table=reading_solution=False; continue
        if current is None: continue
        if "________" in line and header and not reading_solution:
            reading_table=True; reading_solution=False; continue
        if "Solution Point" in line: reading_table=False; reading_solution=True; continue
        if reading_table:
            if not line.strip() or "...."in line: reading_table=False; continue
            parts=[p.strip() for p in line.split("\t") if p.strip()]
            if len(parts)>=5 and tof(parts[0])==tof(parts[0]): rows.append(parts)
            continue
        if reading_solution:
            parts=[p.strip() for p in line.split("\t") if p.strip()]
            if len(parts)>=2:
                value=tof(parts[1])
                if value==value: solution[parts[0]]=value
    if current is not None:
        current.update({"header":header,"rows":rows,"solution":solution}); cases.append(current)

    # ── Deduplicar casos: si dos bloques tienen la misma frecuencia Y el mismo
    # Solution Point (mismo Liquid Rate), es un bloque repetido en el archivo
    # (ej. el reporte se exportó/pegó dos veces) → se descarta el repetido.
    seen_keys=set(); dedup_cases=[]
    for case in cases:
        freq=case.get("frequency",fallback_freq)
        sol=case.get("solution",{})
        # clave de identidad: frecuencia + caudal de líquido del Solution Point
        key=(round(float(freq),2) if pd.notna(freq) else None,
             round(float(sol.get("Liquid Rate",-1)),2) if sol else None)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        dedup_cases.append(case)
    cases=dedup_cases

    aliases={
        "Liquid Rate":"LR","Oil Rate":"OR","Water Rate":"WR",
        "VLP Pressure":"VLP","IPR Pressure":"IPR",
        "Pump Intake Pressure":"PIP","Pump Efficiency":"Pump_Eff",
        "Pump Power Requirement":"Pump_Pow","Motor Load %":"Motor_Load",
        "Solution Node Pressure":"Pwf",
    }
    curve_records=[]; summary_records=[]
    for case in cases:
        freq=case.get("frequency",fallback_freq); h=case.get("header",[])
        for row in case.get("rows",[]):
            record={"Hz":freq}
            for original,clean in aliases.items():
                if original in h:
                    idx=h.index(original)
                    if idx<len(row): record[clean]=tof(row[idx])
            if "LR" in record: curve_records.append(record)
        sol=case.get("solution",{})
        if sol:
            record={"Hz":freq}
            for original,clean in aliases.items():
                if original in sol: record[clean]=sol[original]
            record["BFPD"]=record.get("LR",np.nan)
            record["BOPD_f"]=record.get("OR",np.nan)
            record["BWPD_f"]=record.get("WR",np.nan)
            summary_records.append(record)

    curve_df=pd.DataFrame(curve_records)
    summary_df=pd.DataFrame(summary_records)
    # Deduplicación adicional por seguridad: filas de curva exactamente iguales (Hz+LR+VLP+IPR)
    if not curve_df.empty:
        dedup_cols=[c for c in ["Hz","LR","VLP","IPR"] if c in curve_df.columns]
        if dedup_cols:
            curve_df=curve_df.drop_duplicates(subset=dedup_cols).reset_index(drop=True)
    if not summary_df.empty:
        summary_df=summary_df.drop_duplicates(subset=["Hz"],keep="first").reset_index(drop=True)

    return curve_df,summary_df,info

def parse_wide(f,fallback_freq=np.nan):
    name=f.name.lower(); f.seek(0)
    if name.endswith((".xlsx",".xls")): df=pd.read_excel(f)
    else:
        raw=f.read().decode("utf-8","ignore"); df=None
        for sep in ["\t",";",","]:
            try:
                temp=pd.read_csv(StringIO(raw),sep=sep)
                if temp.shape[1]>2: df=temp; break
            except: pass
        if df is None: raise ValueError("No se pudo leer la tabla exportada.")
    df.columns=[str(c).strip() for c in df.columns]
    x_col="X" if "X" in df.columns else df.columns[0]; records=[]
    for col in df.columns:
        if "VLP Pressure" in col:
            freq_match=re.search(r"\(?([0-9]+(?:[\.,][0-9]+)?)\)?",col)
            freq=tof(freq_match.group(1)) if freq_match else fallback_freq
            ipr_col=None
            for c in df.columns:
                if "IPR Pressure" in c:
                    if freq_match is None or str(int(freq)) in c: ipr_col=c; break
            if ipr_col is None: continue
            temp=pd.DataFrame({
                "Hz":freq,"LR":df[x_col].apply(tof),
                "VLP":df[col].apply(tof),"IPR":df[ipr_col].apply(tof),
            }).dropna()
            records.extend(temp.to_dict("records"))
    return pd.DataFrame(records),{"pump":"No detectada","motor":"No detectado","cable":"No detectado"}

def read_file(f,fallback_freq=np.nan):
    if f is None:
        return pd.DataFrame(),pd.DataFrame(),{"pump":"No detectada","motor":"No detectado","cable":"No detectado"}
    if f.name.lower().endswith((".prn",".txt")):
        raw_bytes=f.read()
        try:
            text=raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text=raw_bytes.decode("latin-1","ignore")
        c,s,info=parse_prn(text,fallback_freq)
        if c.empty:
            f.seek(0); c,info=parse_wide(f,fallback_freq); s=pd.DataFrame()
    else:
        c,info=parse_wide(f,fallback_freq); s=pd.DataFrame()
    if not c.empty: c["Hz"]=c["Hz"].fillna(fallback_freq)
    if not s.empty: s["Hz"]=s["Hz"].fillna(fallback_freq)
    return c,s,info

def find_ops(curves):
    records=[]
    required=["LR","VLP","IPR"]
    if curves.empty or not all(c in curves.columns for c in required): return pd.DataFrame()
    for freq,group in curves.groupby("Hz"):
        g=group.dropna(subset=required).sort_values("LR").copy()
        if len(g)<2: continue
        diff=g["VLP"]-g["IPR"]; idx=None
        for i in range(len(diff)-1):
            if diff.iloc[i]==0 or diff.iloc[i]*diff.iloc[i+1]<0: idx=i; break
        if idx is None:
            i=int(np.argmin(np.abs(diff.values)))
            q=g.iloc[i]["LR"]; p_=g.iloc[i]["IPR"]
        else:
            x1,x2=g.iloc[idx]["LR"],g.iloc[idx+1]["LR"]
            y1,y2=diff.iloc[idx],diff.iloc[idx+1]
            q=x1 if y2==y1 else x1-y1*(x2-x1)/(y2-y1)
            p_=np.interp(q,g["LR"],g["IPR"])
        records.append({"Hz":freq,"BFPD":q,"Pwf":p_})
    return pd.DataFrame(records)

def build_sum(curves,raw_sum,bsw):
    out=find_ops(curves) if (raw_sum.empty or "BFPD" not in raw_sum.columns) else raw_sum.copy()
    if out.empty: return out
    out["BOPD"]=out.get("BOPD_f",np.nan) if "BOPD_f" in out.columns else np.nan
    out["BWPD"]=out.get("BWPD_f",np.nan) if "BWPD_f" in out.columns else np.nan
    out["BOPD"]=np.where(pd.notna(out["BOPD"]),out["BOPD"],out["BFPD"]*(1-bsw/100))
    out["BWPD"]=np.where(pd.notna(out["BWPD"]),out["BWPD"],out["BFPD"]-out["BOPD"])
    return out

def add_econ(base,scen,price,capex,max_hz):
    df=scen.copy()
    df["dBFPD"]=df["BFPD"]-base["BFPD"]
    df["dBOPD"]=df["BOPD"]-base["BOPD"]
    df["RevDay"]=df["dBOPD"]*price
    df["RevMon"]=df["RevDay"]*30
    df["RevYear"]=df["RevDay"]*365
    df["RecBbl"]=df["dBOPD"]*365
    df["Payback"]=np.where(df["RevDay"]>0,capex/df["RevDay"],np.nan)
    safe_hz=max_hz if max_hz>0 else 60

    # ══════════════════════════════════════════════════════════════
    # Vi de Producción y Economía por UMBRALES ABSOLUTOS de ingeniería
    # (no se comparan contra el máximo del propio barrido de sensibilidad,
    # para evitar que el mejor escenario simulado obtenga Vi≈1.00 por
    # definición). Cada escenario se califica según su propio mérito,
    # igual que en un modelo de suma ponderada (Weighted Sum Model)
    # clásico de ingeniería de producción.
    # ══════════════════════════════════════════════════════════════
    base_bopd=float(base.get("BOPD",0) or 0)
    pct_up=np.where(base_bopd>0, df["dBOPD"].values/base_bopd*100, 0.0)

    # Producción: % de incremento de petróleo vs. caso base
    ps=np.select(
        [pct_up>=25, pct_up>=15, pct_up>=8, pct_up>0],
        [1.00,        0.80,        0.60,       0.35],
        default=0.10)

    # Economía: ganancia anual absoluta en USD
    rev=df["RevYear"].values
    es=np.select(
        [rev>=300000, rev>=100000, rev>=30000, rev>0],
        [1.00,         0.80,        0.55,       0.30],
        default=0.05)

    rs=np.where(df["Hz"]<=safe_hz,1,0)
    fs=1-(df["Hz"]/safe_hz).clip(upper=1)
    df["PctUp"]=pct_up
    df["ProdVi"]=ps
    df["EconVi"]=es
    df["RiesgoVi"]=rs
    df["FrecVi"]=fs
    df["Score"]=(0.40*ps+0.30*es+0.20*rs+0.10*fs)*100
    return df

def classify(row,max_hz,min_g):
    if row.get("Tipo","")=="Base": return "BASE","s-base","⚪",["Caso de referencia."]
    if row.get("dBOPD",0)<=0: return "SIN MEJORA","s-warn","⚪",["No incrementa petróleo."]
    if row.get("Hz",0)>max_hz: return "LÍMITE OP.","s-crit","🔴",["Supera frecuencia máxima."]
    if row.get("Hz",0)>=max_hz: return "REVISIÓN","s-warn","🟡",["Opera en el límite de frecuencia."]
    if row.get("dBOPD",0)<min_g: return "MEJORA BAJA","s-warn","🟡",["Incremento menor al mínimo."]
    return "ÓPTIMO","s-ok","🟢",["Buen balance producción-economía-riesgo."]

# ══════════════════════════════════════════════════════════════════
# ANÁLISIS TÉCNICO AUTOMATIZADO (basado en reglas de ingeniería)
# No requiere internet ni servicios de pago — se calcula localmente
# combinando los datos reales del pozo con criterios estándar de
# ingeniería de producción / BES.
# ══════════════════════════════════════════════════════════════════
def generate_rule_based_analysis(pid, p, br, rec, ssum, rst):
    hz_base=float(br.get("Hz",0) or 0)
    hz_rec=float(rec.get("Hz",0) or 0)
    hz_max=float(p.get("max_hz",60) or 60)
    bfpd_base=float(br.get("BFPD",0) or 0)
    bfpd_rec=float(rec.get("BFPD",0) or 0)
    bopd_base=float(br.get("BOPD",0) or 0)
    bopd_rec=float(rec.get("BOPD",0) or 0)
    bwpd_base=float(br.get("BWPD",0) or 0)
    bsw=float(p.get("bsw",0) or 0)
    d_bopd=float(rec.get("dBOPD",0) or 0)
    rec_bbl=float(rec.get("RecBbl",0) or 0)
    rev_year=float(rec.get("RevYear",0) or 0)
    score=float(rec.get("Score",0) or 0)
    price=float(p.get("price",70) or 70)
    hz_margin=hz_max-hz_rec
    pct_incremento=(d_bopd/bopd_base*100) if bopd_base>0 else 0
    pump=p.get("bomba") or "no especificada"

    # ── 1. Diagnóstico del estado actual ──
    diag=(f"El pozo {pid} opera actualmente a {hz_base:.0f} Hz, entregando un caudal líquido de "
          f"{bfpd_base:,.0f} STB/d, de los cuales {bopd_base:,.1f} STB/d corresponden a petróleo y "
          f"{bwpd_base:,.1f} STB/d a agua (BSW de {bsw:.1f}%). ")
    if bsw>=90:
        diag+=("El corte de agua es muy elevado (≥90%), lo cual es típico de pozos en etapa madura de "
               "producción con alto corte de agua; esto implica que la bomba maneja principalmente "
               "fluido acuoso y el margen de ganancia depende fuertemente del pequeño porcentaje de "
               "petróleo remanente. ")
    elif bsw>=60:
        diag+=("El corte de agua es considerable, por lo que conviene vigilar la tendencia de BSW en el "
               "tiempo, ya que un incremento sostenido reduciría el beneficio económico de cualquier "
               "optimización de frecuencia. ")
    else:
        diag+="El corte de agua se mantiene en un rango moderado, favorable para la rentabilidad del pozo. "
    diag+=f"La bomba instalada es {pump}."

    # ── 2. Justificación técnica de la recomendación ──
    just=(f"El análisis de sensibilidad de frecuencia identificó que operar a {hz_rec:.0f} Hz "
          f"(frente a los {hz_base:.0f} Hz actuales) desplaza el punto de operación de la curva VLP "
          f"hacia un caudal mayor, incrementando el BFPD a {bfpd_rec:,.0f} STB/d. ")
    if d_bopd>0:
        just+=(f"Esto se traduce en un incremento de producción de petróleo de {d_bopd:+.1f} STB/d "
               f"({pct_incremento:.1f}% sobre la base), calculado como BOPD_rec − BOPD_base = "
               f"{bopd_rec:,.1f} − {bopd_base:,.1f} = {d_bopd:+.1f} STB/d. ")
    else:
        just+="En este escenario particular, el incremento de petróleo resultó nulo o negativo. "
    just+=(f"La selección de {hz_rec:.0f} Hz como frecuencia recomendada obedece a un criterio "
           f"multicriterio ponderado (40% producción incremental, 30% beneficio económico, "
           f"20% margen de riesgo respecto a la frecuencia máxima operativa, 10% moderación de "
           f"frecuencia), obteniendo un score de {score:.1f}/100.")

    # ── 3. Análisis de riesgos operativos ──
    riesgos=[]
    if hz_margin<=2:
        riesgos.append(
            f"La frecuencia recomendada ({hz_rec:.0f} Hz) está muy cerca del límite operativo máximo "
            f"definido ({hz_max:.0f} Hz), con un margen de solo {hz_margin:.1f} Hz. Se recomienda "
            f"verificar la curva de desempeño de la bomba en catálogo del fabricante para confirmar "
            f"que no se excede su rango de operación certificado (evitar zona de empuje axial excesivo "
            f"o cavitación)."
        )
    elif hz_margin<=5:
        riesgos.append(
            f"El margen entre la frecuencia recomendada y el límite máximo es moderado ({hz_margin:.1f} Hz), "
            f"por lo que se sugiere monitorear parámetros de carga del motor (amperaje) tras la implementación."
        )
    else:
        riesgos.append(
            f"Existe un margen operativo amplio ({hz_margin:.1f} Hz) respecto al límite máximo, lo cual "
            f"reduce el riesgo de sobrecarga del equipo BES."
        )
    if bsw>=90:
        riesgos.append(
            "Dado el alto corte de agua, un incremento de frecuencia también incrementará el caudal de "
            "agua manejado por la bomba; debe verificarse la capacidad de separación/manejo de agua en "
            "superficie y el desgaste esperado de la bomba por manejo de fluido abrasivo."
        )
    if hz_margin<0:
        riesgos.append(
            "⚠️ La frecuencia recomendada supera el límite máximo configurado para este pozo. "
            "Esta alternativa requiere revisión técnica antes de cualquier implementación."
        )
    riesgos_txt=" ".join(riesgos)

    # ── 4. Impacto en la producción ──
    impacto=(f"De implementarse el cambio a {hz_rec:.0f} Hz, se proyecta una recuperación incremental "
              f"de aproximadamente {rec_bbl:,.0f} barriles de petróleo por año, equivalente a una "
              f"ganancia estimada de ${rev_year:,.0f} USD/año (calculada como Δ BOPD × precio × 365 = "
              f"{d_bopd:.1f} × ${price:.0f} × 365). ")
    if d_bopd>0 and bopd_base>0:
        impacto+=(f"Esto representa un incremento relativo del {pct_incremento:.1f}% en la producción "
                   f"de petróleo del pozo respecto al caso base.")

    # ── 5. Observaciones adicionales ──
    obs=[]
    if rst=="ÓPTIMO":
        obs.append("El escenario recomendado cumple con los tres criterios evaluados (producción, "
                    "economía y riesgo operativo) sin comprometer ninguno de ellos significativamente.")
    elif rst=="REVISIÓN":
        obs.append("Aunque el escenario mejora la producción y la economía del pozo, opera cerca del "
                    "límite de frecuencia definido; se recomienda validación adicional antes de "
                    "implementar en campo.")
    elif rst=="LÍMITE OP.":
        obs.append("El escenario con mejor score supera el límite operativo configurado; se sugiere "
                    "evaluar si dicho límite puede ajustarse (previa validación con el fabricante de "
                    "la bomba) o considerar el siguiente mejor escenario dentro del rango permitido.")
    else:
        obs.append("Ningún escenario simulado ofrece una mejora significativa bajo los criterios "
                    "definidos; se recomienda revisar el rango de frecuencias simuladas o las "
                    "condiciones de contorno del modelo IPR/VLP en PROSPER.")
    obs.append("Esta interpretación se basa exclusivamente en los datos de simulación PROSPER cargados "
               "y en las reglas de evaluación multicriterio configuradas; no sustituye el juicio de "
               "un ingeniero de producción con conocimiento del historial y condiciones mecánicas reales "
               "del pozo.")
    obs_txt=" ".join(obs)

    texto=(
        f"1. DIAGNÓSTICO DEL ESTADO ACTUAL\n{diag}\n\n"
        f"2. JUSTIFICACIÓN TÉCNICA DE LA RECOMENDACIÓN\n{just}\n\n"
        f"3. ANÁLISIS DE RIESGOS OPERATIVOS\n{riesgos_txt}\n\n"
        f"4. IMPACTO EN LA PRODUCCIÓN\n{impacto}\n\n"
        f"5. OBSERVACIONES ADICIONALES\n{obs_txt}"
    )
    return texto

# ══════════════════════════════════════════════════════════════════
# SVG NODAL
# ══════════════════════════════════════════════════════════════════
def scale_path(x,y,xmn,xmx,ymn,ymx,W=540,H=200,pl=52,pr=20,pt=18,pb=38):
    x=np.asarray(x,float); y=np.asarray(y,float)
    if xmx==xmn: xmx+=1
    if ymx==ymn: ymx+=1
    xs=pl+(x-xmn)/(xmx-xmn)*(W-pl-pr)
    ys=pt+(1-(y-ymn)/(ymx-ymn))*(H-pt-pb)
    pts=list(zip(xs,ys))
    if not pts: return "","",[]
    d=f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
    for i in range(1,len(pts)):
        x0,y0=pts[i-1]; x1,y1=pts[i]; mx=(x0+x1)/2
        d+=f"C {mx:.1f} {y0:.1f},{mx:.1f} {y1:.1f},{x1:.1f} {y1:.1f} "
    area=d+f"L {pts[-1][0]:.1f} {H-pb:.1f} L {pts[0][0]:.1f} {H-pb:.1f} Z"
    return d,area,pts

def inter_pt(df):
    req=["LR","IPR","VLP"]
    if df.empty or not all(c in df.columns for c in req): return np.nan,np.nan
    try:
        g=df.dropna(subset=req).sort_values("LR").copy()
        if len(g)<2: return np.nan,np.nan
        q=g["LR"].values.astype(float); ipr=g["IPR"].values.astype(float); vlp=g["VLP"].values.astype(float)
        diff=vlp-ipr
        for i in range(len(diff)-1):
            if diff[i]==0: return float(q[i]),float(ipr[i])
            if diff[i]*diff[i+1]<0:
                q1,q2=q[i],q[i+1]; d1,d2=diff[i],diff[i+1]
                qi=q1-d1*(q2-q1)/(d2-d1)
                return float(qi),float((np.interp(qi,q,ipr)+np.interp(qi,q,vlp))/2)
        i=int(np.argmin(np.abs(diff)))
        return float(q[i]),float((ipr[i]+vlp[i])/2)
    except Exception:
        return np.nan,np.nan

def nodal_svg(title,curves,pt_row,lbl):
    W,H,pl,pr,pt_,pb=540,200,52,20,18,38
    req=["LR","IPR","VLP"]
    d=(curves.dropna(subset=req).sort_values("LR").copy()
       if not curves.empty and all(c in curves.columns for c in req) else pd.DataFrame())
    if d.empty or len(d)<2:
        return f"<div class='nodal-card'><div class='ntitle'>{title}</div><p style='color:#c5d2e0;position:relative;z-index:2;font-size:13px'>Sin datos.</p></div>"
    dp=d.iloc[np.linspace(0,len(d)-1,min(40,len(d))).astype(int)].copy()
    q_a=d["LR"].values.astype(float); ip=d["IPR"].values.astype(float); vp=d["VLP"].values.astype(float)
    xmn,xmx=float(np.nanmin(q_a)),float(np.nanmax(q_a))
    ymn=float(min(np.nanmin(ip),np.nanmin(vp))); ymx=float(max(np.nanmax(ip),np.nanmax(vp)))
    xm=(xmx-xmn)*.03 or 1; ym=(ymx-ymn)*.08 or 1
    xmn_,xmx_=xmn-xm,xmx+xm; ymn_,ymx_=max(0,ymn-ym),ymx+ym
    ip_d,ip_a,_=scale_path(dp["LR"].values,dp["IPR"].values,xmn_,xmx_,ymn_,ymx_,W,H,pl,pr,pt_,pb)
    vp_d,vp_a,_=scale_path(dp["LR"].values,dp["VLP"].values,xmn_,xmx_,ymn_,ymx_,W,H,pl,pr,pt_,pb)
    qi,pi=inter_pt(d)
    if pd.isna(qi): qi=pt_row.get("BFPD",np.nan); pi=pt_row.get("Pwf",np.nan)
    if pd.notna(qi) and pd.notna(pi):
        ox=pl+(float(qi)-xmn_)/(xmx_-xmn_)*(W-pl-pr)
        oy=pt_+(1-(float(pi)-ymn_)/(ymx_-ymn_))*(H-pt_-pb)
        ox=max(pl,min(W-pr,ox)); oy=max(pt_,min(H-pb,oy))
    else: ox,oy=pl,pt_
    xt=""; yt=""
    for v in np.linspace(xmn,xmx,5):
        tx=pl+(v-xmn_)/(xmx_-xmn_)*(W-pl-pr)
        xt+=f"<line class='ngl' x1='{tx:.0f}' y1='{pt_}' x2='{tx:.0f}' y2='{H-pb}'/>"
        xt+=f"<text class='ntl' x='{tx-18:.0f}' y='{H-14}'>{v:,.0f}</text>"
    for v in np.linspace(ymn_,ymx_,5):
        ty=pt_+(1-(v-ymn_)/(ymx_-ymn_))*(H-pt_-pb)
        yt+=f"<line class='ngl' x1='{pl}' y1='{ty:.0f}' x2='{W-pr}' y2='{ty:.0f}'/>"
        yt+=f"<text class='ntl' x='2' y='{ty+4:.0f}'>{v:,.0f}</text>"
    rp=""
    for _,rr in dp.iloc[::max(1,len(dp)//8)].iterrows():
        rx=pl+(float(rr["LR"])-xmn_)/(xmx_-xmn_)*(W-pl-pr)
        ri=pt_+(1-(float(rr["IPR"])-ymn_)/(ymx_-ymn_))*(H-pt_-pb)
        rv=pt_+(1-(float(rr["VLP"])-ymn_)/(ymx_-ymn_))*(H-pt_-pb)
        rp+=f"<circle class='nr' cx='{rx:.0f}' cy='{ri:.0f}' r='2.8'/><circle class='nr' cx='{rx:.0f}' cy='{rv:.0f}' r='2.8'/>"
    big=num(qi,0); small=num(pi,0)
    dlt=f"+{num(pt_row.get('dBOPD',np.nan),1)} BOPD" if pd.notna(pt_row.get('dBOPD',np.nan)) else ""
    return f"""
    <div class='nodal-card'>
      <div class='ntitle'>{title}</div>
      <svg viewBox='0 0 {W} {H}' style='width:100%;height:185px;display:block;position:relative;z-index:2'>
        <defs>
          <linearGradient id='fc' x1='0' x2='0' y1='0' y2='1'><stop offset='0%' stop-color='#5B8DB8' stop-opacity='.38'/><stop offset='100%' stop-color='#5B8DB8' stop-opacity='0'/></linearGradient>
          <linearGradient id='fp' x1='0' x2='0' y1='0' y2='1'><stop offset='0%' stop-color='#8A9BA8' stop-opacity='.32'/><stop offset='100%' stop-color='#8A9BA8' stop-opacity='0'/></linearGradient>
          <filter id='gc'><feGaussianBlur stdDeviation='3' result='b'/><feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter>
          <filter id='gp'><feGaussianBlur stdDeviation='3' result='b'/><feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter>
          <filter id='gk'><feGaussianBlur stdDeviation='4' result='b'/><feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter>
        </defs>
        {xt}{yt}
        <line class='ngl' x1='{pl}' y1='{pt_}' x2='{pl}' y2='{H-pb}'/>
        <line class='ngl' x1='{pl}' y1='{H-pb}' x2='{W-pr}' y2='{H-pb}'/>
        <path class='na-ipr' d='{ip_a}'/><path class='na-vlp' d='{vp_a}'/>
        <path class='nl-ipr' d='{ip_d}' filter='url(#gc)'/><path class='nl-vlp' d='{vp_d}' filter='url(#gp)'/>
        {rp}
        <path class='ng' d='M {ox:.0f} {H-pb} L {ox:.0f} {oy:.0f}'/>
        <path class='ng' d='M {pl} {oy:.0f} L {ox:.0f} {oy:.0f}'/>
        <circle class='np' cx='{ox:.0f}' cy='{oy:.0f}' r='7' filter='url(#gk)'/>
        <text class='nlb' x='{min(ox+10,W-130):.0f}' y='{max(oy-8,16):.0f}'>{lbl}</text>
        <text class='nta' x='{W/2-40:.0f}' y='{H-2}'>Caudal líquido STB/d</text>
        <text class='nta' transform='translate(11 {H/2+30:.0f}) rotate(-90)'>Presión psig</text>
      </svg>
      <div class='nleg' style='position:relative;z-index:2'>
        <div><span class='lc'></span>IPR</div><div><span class='lp'></span>VLP</div><div>● Intersección</div>
      </div>
      <div class='nstats'>
        <div class='ns'><span>Pwf</span><b>{small} psig</b></div>
        <div class='ns'><span>Δ</span><b>{dlt}</b></div>
        <div class='nsbig'>{big}</div>
      </div>
    </div>"""

def cinema_html(br,rec,ssum=None):
    # ── Comparación Base vs. Recomendado en UN SOLO EJE (estilo "bullet chart") ──
    # Base y Recomendado suelen venir de archivos PROSPER distintos (fechas o
    # condiciones de yacimiento distintas), así que sus curvas IPR/VLP completas
    # NO son comparables directamente (cada una tiene su propio AOF). Lo que sí
    # es siempre comparable, venga de donde venga, es el caudal resultante (BFPD)
    # de cada escenario — por eso se usa un solo eje cuantitativo (STB/d), sin
    # mezclar dominios de frecuencia ni de presión.
    q_b=float(br["BFPD"]); q_r=float(rec["BFPD"])
    qmax=max(q_b,q_r)*1.18 or 1
    pct=((q_r-q_b)/q_b*100) if q_b else np.nan

    x0,x1=170,860        # límites del área de trazado en X (px del SVG, eje BFPD)
    ybase,yrec=70,140    # filas: barra Base y barra Recomendado
    bar_h=34
    def X(q): return x0+(q/qmax)*(x1-x0)

    n=6
    vgrid="";xticks=""
    for i in range(n):
        gx=x0+(x1-x0)*i/(n-1)
        qv=qmax*i/(n-1)
        vgrid+=f"<line x1='{gx:.1f}' y1='30' x2='{gx:.1f}' y2='190' stroke='rgba(138,157,181,.15)' stroke-width='1'/>"
        xticks+=f"<text x='{gx:.1f}' y='208' fill='#8A9DB5' font-size='10' text-anchor='middle'>{qv:,.0f}</text>"

    xb,xr=X(q_b),X(q_r)

    return f"""
    <div class='cinema'><div class='cc'>
      <div style='font-size:1rem;font-weight:900;margin-bottom:3px;'>Curva dinámica</div>
      <div style='font-size:.74rem;color:#c5d2e0;margin-bottom:9px;'>Comparación en un solo eje: caudal (STB/d) — caso base vs. escenario recomendado</div>
      <svg viewBox='0 0 900 230' width='100%' height='200' preserveAspectRatio='none'>
        <defs>
          <linearGradient id='gb2' x1='0' x2='1'><stop offset='0%' stop-color='#3E6E96'/><stop offset='100%' stop-color='#5B8DB8'/></linearGradient>
          <linearGradient id='go2' x1='0' x2='1'><stop offset='0%' stop-color='#8F753F'/><stop offset='100%' stop-color='#C9A368'/></linearGradient>
          <filter id='gf'><feGaussianBlur stdDeviation='3' result='b'/><feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter>
        </defs>
        {vgrid}
        <line x1='{x0}' y1='30' x2='{x0}' y2='190' stroke='rgba(138,157,181,.30)' stroke-width='1'/>
        <line x1='{x0}' y1='190' x2='{x1}' y2='190' stroke='rgba(138,157,181,.30)' stroke-width='1'/>
        <text x='40' y='{ybase+bar_h/2+4}' fill='#c5d2e0' font-size='12' font-weight='800'>Base</text>
        <rect x='{x0}' y='{ybase}' width='{x1-x0}' height='{bar_h}' rx='6' fill='rgba(255,255,255,.05)'/>
        <rect x='{x0}' y='{ybase}' width='0' height='{bar_h}' rx='6' fill='url(#gb2)'><animate attributeName='width' from='0' to='{xb-x0:.1f}' dur='1.1s' fill='freeze' begin='0s'/></rect>
        <text x='{xb+8:.1f}' y='{ybase+bar_h/2+4}' fill='white' font-size='14' font-weight='800'>{num(q_b)} BFPD</text>
        <text x='22' y='{yrec+bar_h/2+4}' fill='#ffd27a' font-size='12' font-weight='800'>Rec.</text>
        <rect x='{x0}' y='{yrec}' width='{x1-x0}' height='{bar_h}' rx='6' fill='rgba(255,255,255,.05)'/>
        <rect x='{x0}' y='{yrec}' width='0' height='{bar_h}' rx='6' fill='url(#go2)' filter='url(#gf)'><animate attributeName='width' from='0' to='{xr-x0:.1f}' dur='1.4s' fill='freeze' begin='0.15s'/></rect>
        <text x='{xr+8:.1f}' y='{yrec+bar_h/2+4}' fill='white' font-size='14' font-weight='800'>{num(q_r)} BFPD</text>
        <line x1='{xb:.1f}' y1='{ybase-6}' x2='{xb:.1f}' y2='{yrec+bar_h+6}' stroke='#8FB2D6' stroke-width='1.5' stroke-dasharray='3,3'/>
        <text x='{xb:.1f}' y='22' fill='#8FB2D6' font-size='10' text-anchor='middle' font-weight='700'>nivel base</text>
        {xticks}
        <text x='{(x0+x1)/2:.1f}' y='226' fill='#8A9DB5' font-size='11' font-weight='700' text-anchor='middle'>Caudal líquido, q&#8320; (STB/d)</text>
      </svg>
      <div style='text-align:center;margin-top:2px;'>
        <span style='background:rgba(111,197,142,.14);border:1px solid rgba(111,197,142,.35);color:#8fe3ab;border-radius:999px;padding:3px 14px;font-size:.78rem;font-weight:900;'>+{pct:.1f}% vs. caso base</span>
      </div>
      <div class='ckpis'>
        <div class='ck'><b>{rec["Hz"]:.0f} Hz</b><span>Frecuencia rec.</span></div>
        <div class='ck'><b>{num(rec["dBOPD"],1)} BOPD</b><span>Δ petróleo</span></div>
        <div class='ck'><b>{num(rec["RecBbl"],0)}</b><span>bbl/año inc.</span></div>
        <div class='ck'><b>{cmoney(rec["RevYear"])}</b><span>Ganancia anual</span></div>
      </div>
    </div></div>"""

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
if "pozos" not in st.session_state: st.session_state.pozos={}
if "vista" not in st.session_state: st.session_state.vista="manager"

def nav(v): st.session_state.vista=v; st.rerun()

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛢️ OptiFlow")
    st.markdown("---")
    if st.button("🏠 Campo — gestor de pozos", use_container_width=True,
                 type="primary" if st.session_state.vista=="manager" else "secondary"):
        nav("manager")
    if st.session_state.pozos:
        st.markdown("**Pozos:**")
        for pid in list(st.session_state.pozos.keys()):
            p=st.session_state.pozos[pid]
            icon="✅" if p.get("ready") else ("⏳" if p.get("partial") else "○")
            if st.button(f"{icon} {pid}",key=f"sb_{pid}",use_container_width=True,
                         type="primary" if st.session_state.vista==f"pozo:{pid}" else "secondary"):
                nav(f"pozo:{pid}")
        if sum(1 for p in st.session_state.pozos.values() if p.get("ready"))>=2:
            st.markdown("---")
            if st.button("📊 Comparar pozos",use_container_width=True,
                         type="primary" if st.session_state.vista=="comparar" else "secondary"):
                nav("comparar")

# ══════════════════════════════════════════════════════════════════
# VISTA: GESTOR (MANAGER)
# ══════════════════════════════════════════════════════════════════
if st.session_state.vista=="manager":
    pozos=st.session_state.pozos
    ready=[p for p in pozos.values() if p.get("ready")]
    total_gain=sum(p["rec_row"]["RevYear"] for p in ready if p.get("rec_row"))
    total_delta=sum(p["rec_row"]["dBOPD"] for p in ready if p.get("rec_row"))
    total_bfpd=sum(p.get("bfpd_base",0) or 0 for p in pozos.values())

    # HERO
    st.markdown(f"""
    <div class='hero'>
      <h1>🛢️ OptiFlow — campo VCH</h1>
      <p>Gestiona tus pozos, sube la información de cada uno y compara el potencial de optimización del campo.</p>
    </div>""", unsafe_allow_html=True)

    # FIELD KPIs
    st.markdown(f"""
    <div class='fk-grid'>
      <div class='fk'><div class='fk-l'>Pozos registrados</div><div class='fk-v'>{len(pozos)}</div><div class='fk-s'>campo VCH</div></div>
      <div class='fk'><div class='fk-l'>Con análisis</div><div class='fk-v' style='color:#6FA287'>{len(ready)}</div><div class='fk-s'>datos completos</div></div>
      <div class='fk'><div class='fk-l'>BFPD total campo</div><div class='fk-v'>{num(total_bfpd)}</div><div class='fk-s'>producción actual</div></div>
      <div class='fk'><div class='fk-l'>Ganancia total</div><div class='fk-v' style='color:#6FA287'>{cmoney(total_gain)}</div><div class='fk-s'>USD/año estimado</div></div>
      <div class='fk'><div class='fk-l'>Δ BOPD total</div><div class='fk-v' style='color:#5B8DB8'>+{total_delta:.1f}</div><div class='fk-s'>barriles/día inc.</div></div>
    </div>""", unsafe_allow_html=True)

    # LAYOUT: formulario + ranking
    col_form, col_rank = st.columns([1, 1.7])

    with col_form:
        st.markdown("<div class='panel'><h3>➕ Agregar pozo</h3>", unsafe_allow_html=True)
        with st.form("add_well_form", clear_on_submit=True):
            fc1,fc2=st.columns(2)
            nid  =fc1.text_input("ID del pozo","",placeholder="VCH-006")
            nbomba=fc2.text_input("Bomba","",placeholder="D460N")
            fc3,fc4,fc5=st.columns(3)
            napi =fc3.number_input("API (°)",0.0,60.0,25.0,0.1)
            nbsw =fc4.number_input("BSW (%)",0.0,100.0,50.0,0.1,
                help="Se sobrescribe automáticamente si el archivo .prn trae 'Water Cut'.")
            nhz  =fc5.number_input("Hz base ⚠️",0.0,value=0.0,step=0.5,
                help="Frecuencia REAL de operación actual del pozo (no viene en el .prn — debes saberla tú). Ej: 37")
            fc6,fc7,fc8=st.columns(3)
            nbfpd=fc6.number_input("BFPD actual",0.0,value=0.0,step=10.0)
            nbopd=fc7.number_input("BOPD actual",0.0,value=0.0,step=1.0)
            nprice=fc8.number_input("Precio USD/bbl",0.0,value=70.0,step=1.0)
            fc9,fc10=st.columns(2)
            nmaxhz=fc9.number_input("Hz máx. rec.",0.0,value=60.0,step=1.0)
            ncapex=fc10.number_input("CAPEX USD",0.0,value=0.0,step=500.0)
            nming =st.number_input("Δ BOPD mín. esperado",0.0,value=5.0,step=1.0)
            submitted=st.form_submit_button("✅ Agregar pozo al campo",use_container_width=True)
            if submitted:
                pid=nid.strip()
                if not pid: st.error("Ingresa un ID.")
                elif pid in pozos: st.error(f"{pid} ya existe.")
                elif nhz<=0: st.error("Ingresa la frecuencia BASE real del pozo (no viene en el archivo .prn, debes conocerla).")
                else:
                    pozos[pid]={
                        "id":pid,"bomba":nbomba,"api":napi,"bsw":nbsw,
                        "hz_base":nhz,"price":nprice,"max_hz":nmaxhz,
                        "capex":ncapex,"min_g":nming,
                        "bfpd_base":nbfpd if nbfpd>0 else None,
                        "bopd_base":nbopd if nbopd>0 else None,
                        "ready":False,"partial":(nbfpd>0),
                        "curves":None,"base_curves":None,
                        "summary":None,"base_row":None,"rec_row":None,"info":{}
                    }
                    st.success(f"Pozo {pid} agregado.")
                    st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    with col_rank:
        st.markdown("<div class='panel'><h3>🏆 Ranking de oportunidades</h3>",unsafe_allow_html=True)
        sorted_ready=sorted(ready,key=lambda p:p["rec_row"]["RevYear"] if p.get("rec_row") else 0,reverse=True)
        medals=["🥇","🥈","🥉"]
        if not sorted_ready:
            st.markdown("<div class='rank-empty'>Procesa los archivos PROSPER de al menos un pozo para ver el ranking.</div>",unsafe_allow_html=True)
        else:
            max_g=sorted_ready[0]["rec_row"]["RevYear"] or 1
            rank_html=""
            for i,p in enumerate(sorted_ready):
                rr=p["rec_row"]
                m=medals[i] if i<3 else f"#{i+1}"
                pct=round((rr["RevYear"] or 0)/max_g*100)
                rank_html+=f"""
                <div class='rrow'>
                  <div class='rpos'>{m}</div>
                  <div class='rinfo'>
                    <div class='rname'>{p["id"]}</div>
                    <div class='rsub'>{p.get("bomba","—")} · {num(p.get("bfpd_base",0))} → {num(rr["BFPD"])} BFPD</div>
                    <div class='rbar'><div class='rbar-fill' style='width:{pct}%'></div></div>
                  </div>
                  <div>
                    <div class='rgain'>{cmoney(rr["RevYear"])}/año</div>
                    <div class='rmeta'>+{num(rr["dBOPD"],1)} BOPD · {rr.get("Score",0):.0f}/100</div>
                  </div>
                </div>"""
            st.markdown(rank_html,unsafe_allow_html=True)
            st.markdown(f"""
            <div class='tstrip'>
              <div class='ts'><div class='ts-l'>Ganancia campo</div><div class='ts-v' style='color:#6FA287'>{cmoney(total_gain)}/año</div></div>
              <div class='ts'><div class='ts-l'>Total Δ BOPD</div><div class='ts-v' style='color:#5B8DB8'>+{total_delta:.1f}</div></div>
              <div class='ts'><div class='ts-l'>Pozos en ranking</div><div class='ts-v'>{len(sorted_ready)}</div></div>
            </div>""",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    # TARJETAS DE POZOS
    st.markdown("<div class='sec-head'>🗂️ Pozos del campo</div>",unsafe_allow_html=True)

    if not pozos:
        st.markdown("<div class='hint'>Aún no hay pozos. Usa el formulario de arriba para agregar el primero.</div>",unsafe_allow_html=True)
    else:
        # filtros
        filt_options=["Todos","Completos","Parciales","Sin datos"]
        filt=st.radio("Filtrar:",filt_options,horizontal=True,label_visibility="collapsed")
        fmap={"Todos":"all","Completos":"ready","Parciales":"partial","Sin datos":"empty"}
        filt_key=fmap[filt]

        filtered={pid:p for pid,p in pozos.items()
                  if filt_key=="all" or
                  (filt_key=="ready" and p.get("ready")) or
                  (filt_key=="partial" and p.get("partial") and not p.get("ready")) or
                  (filt_key=="empty" and not p.get("partial") and not p.get("ready"))}

        if not filtered:
            st.markdown("<div class='hint'>No hay pozos en este filtro.</div>",unsafe_allow_html=True)
        else:
            cols=st.columns(min(len(filtered),4))
            for ci,(pid,p) in enumerate(filtered.items()):
                with cols[ci%4]:
                    state="ready" if p.get("ready") else ("partial" if p.get("partial") else "empty")
                    prog=100 if state=="ready" else (45 if state=="partial" else 0)
                    prog_color={"ready":"#6FA287","partial":"#ffd27a","empty":"rgba(150,165,185,.14)"}[state]
                    state_badge={"ready":"<span class='badge b-ready'>✅ Completo</span>",
                                 "partial":"<span class='badge b-partial'>⏳ Parcial</span>",
                                 "empty":"<span class='badge b-empty'>○ Sin datos</span>"}[state]
                    st_map={"optimo":"<span class='badge b-opt'>Óptimo</span>",
                            "revision":"<span class='badge b-rev'>Revisión</span>",
                            "critico":"<span class='badge b-crit'>Crítico</span>"}
                    status_badge=st_map.get(p.get("status",""),"")
                    check_on=" on" if state=="ready" else ""

                    # stats actuales
                    bfpd_v=p.get("bfpd_base"); bopd_v=p.get("bopd_base")
                    bsw_v=p.get("bsw")
                    if bfpd_v is None and p.get("base_row"): bfpd_v=p["base_row"].get("BFPD")
                    if bopd_v is None and p.get("base_row"): bopd_v=p["base_row"].get("BOPD")

                    # stats recomendados
                    rr=p.get("rec_row",{}) or {}
                    st.markdown(f"""
                    <div class='wc'>
                      <div class='wc-top'>
                        <div class='wc-name'>{pid}</div>
                        <div class='wc-check{check_on}'>✓</div>
                      </div>
                      <div class='wc-meta'>{p.get("bomba","—")} · {p.get("api","—")}° API · {p.get("hz_base","—")} Hz</div>
                      <div class='wc-prog'><div class='wc-prog-fill' style='width:{prog}%;background:{prog_color}'></div></div>
                      <div class='badges'>{state_badge}{status_badge}</div>
                      <div class='slbl'>Actual</div>
                      <div class='sgrid'>
                        <div class='sbox'><div class='sbox-l'>BFPD</div><div class='sbox-v'>{num(bfpd_v)}</div></div>
                        <div class='sbox'><div class='sbox-l'>BOPD</div><div class='sbox-v'>{num(bopd_v)}</div></div>
                        <div class='sbox'><div class='sbox-l'>BSW%</div><div class='sbox-v'>{f"{bsw_v:.1f}%" if bsw_v is not None else "—"}</div></div>
                      </div>
                      <div class='slbl'>Recomendado</div>
                      <div class='sgrid'>
                        <div class='sbox'><div class='sbox-l'>BFPD rec.</div><div class='sbox-v info'>{num(rr.get("BFPD")) if rr else "—"}</div></div>
                        <div class='sbox'><div class='sbox-l'>BOPD +Δ</div><div class='sbox-v good'>{("+"+num(rr["dBOPD"],1)) if rr and pd.notna(rr.get("dBOPD",np.nan)) else "—"}</div></div>
                        <div class='sbox'><div class='sbox-l'>Ganancia</div><div class='sbox-v good'>{cmoney(rr.get("RevYear")) if rr else "—"}</div></div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    ba,bb=st.columns(2)
                    if ba.button("📂 Archivos",key=f"arch_{pid}",use_container_width=True):
                        nav(f"pozo:{pid}")
                    if state=="ready":
                        if bb.button("📊 Análisis",key=f"open_{pid}",use_container_width=True):
                            nav(f"pozo:{pid}")
                    else:
                        if bb.button("🗑️",key=f"del_{pid}",use_container_width=True):
                            del st.session_state.pozos[pid]; st.rerun()

    n_ready_total=sum(1 for p in pozos.values() if p.get("ready"))
    if n_ready_total>=1:
        st.markdown("")
        dl_g1,dl_g2=st.columns(2)
        with dl_g1:
            field_pdf=generate_field_pdf(pozos)
            st.download_button("📄 Descargar reporte PDF global del campo",field_pdf,
                "optiflow_campo_reporte.pdf","application/pdf",use_container_width=True)
        with dl_g2:
            if n_ready_total>=2:
                if st.button("📊 Comparación detallada multi-pozo →",type="primary",use_container_width=True):
                    nav("comparar")

# ══════════════════════════════════════════════════════════════════
# VISTA: POZO INDIVIDUAL
# ══════════════════════════════════════════════════════════════════
elif st.session_state.vista.startswith("pozo:"):
    pid=st.session_state.vista.split(":",1)[1]
    if pid not in st.session_state.pozos: st.error("Pozo no encontrado."); st.stop()
    p=st.session_state.pozos[pid]

    if st.button("← Volver al campo",key="back_btn"): nav("manager")

    # encabezado del pozo
    state="ready" if p.get("ready") else ("partial" if p.get("partial") else "empty")
    st.markdown(f"""
    <div class='hero' style='display:flex;align-items:center;justify-content:space-between;'>
      <div>
        <h1>🛢️ {pid}</h1>
        <p>{p.get("bomba","—")} · {p.get("api","—")}° API · BSW {p.get("bsw","—")}% · Hz base {p.get("hz_base","—")}</p>
      </div>
      <div style='text-align:right;'>
        {"<span class='badge b-ready' style='font-size:13px;padding:5px 12px;'>✅ Análisis completo</span>" if state=="ready" else
         "<span class='badge b-partial' style='font-size:13px;padding:5px 12px;'>⏳ Datos parciales</span>" if state=="partial" else
         "<span class='badge b-empty' style='font-size:13px;padding:5px 12px;'>○ Sin datos</span>"}
      </div>
    </div>""", unsafe_allow_html=True)

    # ── CARGA DE ARCHIVOS ──
    st.markdown("<div class='sec-head'>📂 Archivos PROSPER</div>",unsafe_allow_html=True)
    with st.expander("⚙️ Configuración del pozo",expanded=False):
        cc1,cc2,cc3,cc4=st.columns(4)
        p["bsw"]=cc1.number_input("BSW (%)",0.0,100.0,float(p["bsw"]),0.1,key=f"bsw_{pid}")
        p["price"]=cc2.number_input("Precio USD/bbl",0.0,value=float(p["price"]),step=1.0,key=f"pr_{pid}")
        p["max_hz"]=cc3.number_input("Hz máx",0.0,value=float(p["max_hz"]),step=1.0,key=f"mhz_{pid}")
        p["hz_base"]=cc4.number_input("Hz base",0.0,value=float(p["hz_base"]),step=1.0,key=f"bhz_{pid}")
        p["capex"]=cc1.number_input("CAPEX USD",0.0,value=float(p["capex"]),step=500.0,key=f"cap_{pid}")
        p["min_g"]=cc2.number_input("Δ BOPD mín",0.0,value=float(p["min_g"]),step=1.0,key=f"mg_{pid}")
        p["bomba"]=cc3.text_input("Bomba",value=str(p.get("bomba","")),key=f"bom_{pid}")

    uf1,uf2=st.columns(2)
    base_f=uf1.file_uploader(f"Caso BASE — {pid}",type=["prn","txt","csv","xlsx","xls"],key=f"bf_{pid}")
    sens_f=uf2.file_uploader(f"Sensibilidades — {pid}",type=["prn","txt","csv","xlsx","xls"],key=f"sf_{pid}")

    pb1,pb2=st.columns(2)
    with pb1:
        if st.button("🔄 Procesar todo (base + sensibilidades)",type="primary",key=f"proc_{pid}",use_container_width=True):
            if sens_f is None:
                st.error("Sube al menos el archivo de sensibilidades.")
            else:
                with st.spinner("Procesando..."):
                    hz_base=float(p["hz_base"])
                    bc,bs,bi=read_file(base_f, hz_base)
                    sc,ss,si=read_file(sens_f, np.nan)
                    if sc.empty:
                        st.error("No se pudieron leer las sensibilidades."); st.stop()

                    # Autodetectar BSW (Water Cut) real del archivo base si está disponible
                    detected_bsw=bi.get("bsw",np.nan) if not bc.empty else np.nan
                    if pd.notna(detected_bsw) and detected_bsw>0:
                        bsw_v=float(detected_bsw)
                        p["bsw"]=bsw_v  # actualizar también en config del pozo
                    else:
                        bsw_v=float(p["bsw"])

                    # ── base_row: igual que en el dashboard original ──
                    if not bc.empty:
                        bsum=build_sum(bc,bs,bsw_v)
                        if bsum.empty:
                            bfpd_m=float(p.get("bfpd_base") or 0)
                            br={"Hz":hz_base,"BFPD":bfpd_m,
                                "BOPD":bfpd_m*(1-bsw_v/100),
                                "BWPD":bfpd_m*bsw_v/100,"Pwf":np.nan}
                        else:
                            bsum["Hz"]=bsum["Hz"].fillna(hz_base)
                            br=bsum.iloc[(bsum["Hz"]-hz_base).abs().argsort()[:1]].iloc[0].to_dict()
                            br["Hz"]=hz_base
                    else:
                        bfpd_m=float(p.get("bfpd_base") or 0)
                        br={"Hz":hz_base,"BFPD":bfpd_m,
                            "BOPD":bfpd_m*(1-bsw_v/100),
                            "BWPD":bfpd_m*bsw_v/100,"Pwf":np.nan}

                    br["Tipo"]="Base"

                    # ── escenarios desde sensibilidades (igual que el original) ──
                    ssum=build_sum(sc,ss,bsw_v)
                    if ssum.empty:
                        st.error("Sin puntos de operación en sensibilidades."); st.stop()
                    ssum["Tipo"]="Simulado"
                    ssum=add_econ(br,ssum,float(p["price"]),float(p["capex"]),float(p["max_hz"]))

                    valid=ssum[ssum["Hz"]<=float(p["max_hz"])]
                    rec=(valid.sort_values("Score",ascending=False).iloc[0] if not valid.empty
                         else ssum.sort_values("Score",ascending=False).iloc[0])

                    p.update({
                        "curves":sc,"base_curves":bc if not bc.empty else None,
                        "summary":ssum,"base_row":br,"rec_row":rec.to_dict(),
                        "info":{**bi,**si},"ready":True,"partial":False,
                        "hz_base":hz_base,
                        "bfpd_base":br["BFPD"],"bopd_base":br.get("BOPD",0),
                        "status":"optimo" if rec.get("Score",0)>=85 else ("revision" if rec.get("Score",0)>=68 else "critico")
                    })
                    st.session_state.pozos[pid]=p
                    st.success("¡Análisis completo!"); st.rerun()

    with pb2:
        if st.button("💾 Guardar solo caso base",key=f"partial_{pid}",use_container_width=True):
            if base_f is None:
                st.error("Sube el archivo del caso base.")
            else:
                with st.spinner("Leyendo caso base..."):
                    bc,bs,bi=read_file(base_f,p["hz_base"])
                    if not bc.empty:
                        bsum=build_sum(bc,bs,p["bsw"])
                        if not bsum.empty:
                            bsum["Hz"]=bsum["Hz"].fillna(p["hz_base"])
                            br=bsum.iloc[(bsum["Hz"]-p["hz_base"]).abs().argsort()[:1]].iloc[0].to_dict()
                            br["Hz"]=p["hz_base"]
                            if pd.isna(br.get("BOPD",np.nan)) or br.get("BOPD",0)<0:
                                br["BOPD"]=max(br.get("BFPD",0)*(1-p["bsw"]/100),0)
                            if pd.isna(br.get("BWPD",np.nan)) or br.get("BWPD",0)<0:
                                br["BWPD"]=max(br.get("BFPD",0)-br.get("BOPD",0),0)
                            p.update({"base_curves":bc,"base_row":br,
                                      "info":{**p.get("info",{}),**bi},
                                      "partial":True,
                                      "bfpd_base":br["BFPD"],"bopd_base":br.get("BOPD",0)})
                            st.session_state.pozos[pid]=p
                            st.success("Info base guardada. Sube sensibilidades para completar el análisis."); st.rerun()
                        else:
                            st.error("No se pudo calcular el punto de operación del caso base.")
                    else:
                        st.error("No se pudo leer el archivo base.")

    # ── VISTA PARCIAL ──
    if p.get("partial") and not p.get("ready") and p.get("base_row"):
        br=p["base_row"]; info=p.get("info",{})
        st.markdown("<div class='sec-head'>📌 Información parcial — caso base</div>",unsafe_allow_html=True)
        pk1,pk2,pk3,pk4=st.columns(4)
        for col,t,v,s in [
            (pk1,"Hz base",f"{br['Hz']:.0f} Hz","Frecuencia actual"),
            (pk2,"BFPD base",f"{num(br['BFPD'])}","Caudal de líquido"),
            (pk3,"BOPD base",f"{num(br.get('BOPD',0))}","Petróleo actual"),
            (pk4,"BSW",f"{p['bsw']:.1f}%","Corte de agua"),
        ]:
            with col:
                st.markdown(f"<div class='kpi'><div class='kpi-t'>{t}</div><div class='kpi-v'>{v}</div><div class='kpi-s'>{s}</div></div>",unsafe_allow_html=True)
        if p.get("base_curves") is not None and not p["base_curves"].empty:
            bcv=p["base_curves"]
            hz_b=bcv.iloc[(bcv["Hz"]-p["hz_base"]).abs().argsort()[:1]]["Hz"].iloc[0]
            gb=bcv[bcv["Hz"]==hz_b].sort_values("LR")
            nc1,nc2=st.columns(2)
            with nc1: st.markdown(nodal_svg("IPR/VLP — Caso base",gb,br,"Base"),unsafe_allow_html=True)
        st.markdown(f"""
        <div class='panel' style='margin-top:10px;'>
          <div style='color:#c5d2e0;font-size:.85rem;line-height:1.7;'>
            <b>Bomba:</b> {p.get("bomba") or info.get("pump","No detectada")}&nbsp;·&nbsp;
            <b>Motor:</b> {info.get("motor","No detectado")}&nbsp;·&nbsp;
            <b>Cable:</b> {info.get("cable","No detectado")}
          </div>
        </div>""",unsafe_allow_html=True)
        st.markdown("<div class='hint'>📂 Sube las <b>sensibilidades</b> y presiona <b>Procesar todo</b> para completar el análisis.</div>",unsafe_allow_html=True)

    # ── VISTA COMPLETA ──
    elif p.get("ready"):
        br=p["base_row"]; rec=p["rec_row"]; sc=p["curves"]
        bc=p.get("base_curves"); ssum=p["summary"]
        rst,rcss,ric,ralerts=classify(rec,p["max_hz"],p["min_g"])
        plot_freqs=sorted(ssum["Hz"].dropna().unique())
        base_bfpd_val=float(br["BFPD"]); rec_bfpd_val=float(rec["BFPD"])
        uplift=((rec_bfpd_val-base_bfpd_val)/base_bfpd_val*100) if base_bfpd_val else 0
        score_v=float(rec.get("Score",0)); conf=min(max(score_v+4,0),99)

        # KPIs
        st.markdown("<div class='sec-head'>📈 KPIs ejecutivos</div>",unsafe_allow_html=True)
        k1,k2,k3,k4,k5,k6=st.columns(6)
        for col,t,v,s in [
            (k1,"Hz base",f"{br['Hz']:.0f} Hz",f"{num(br['BFPD'])} BFPD"),
            (k2,"Hz rec.",f"{rec['Hz']:.0f} Hz",f"{num(rec['BFPD'])} BFPD"),
            (k3,"Δ BOPD",f"+{num(rec['dBOPD'],1)}","petróleo adicional"),
            (k4,"bbl/año",f"{num(rec['RecBbl'],0)}","incrementales"),
            (k5,"Ganancia/año",cmoney(rec["RevYear"]),"USD estimado"),
            (k6,"Estado",f"{ric} {rst}",f"Score {score_v:.0f}/100"),
        ]:
            with col:
                st.markdown(f"<div class='kpi'><div class='kpi-t'>{t}</div><div class='kpi-v'>{v}</div><div class='kpi-s'>{s}</div></div>",unsafe_allow_html=True)

        # ── TRAZABILIDAD BOPD / BWPD ──
        bopd_base=float(br.get("BOPD",0) or 0)
        bwpd_base=float(br.get("BWPD",0) or 0)
        bopd_rec=float(rec.get("BOPD",0) or 0)
        bwpd_rec=float(bopd_rec and (float(rec.get("BFPD",0) or 0)-bopd_rec) or 0)
        delta_bopd=bopd_rec-bopd_base
        st.markdown(f"""
        <div class='traz-box'>
          <div class='traz-title'>Trazabilidad del incremento — Cómo se calcula el Δ BOPD = {delta_bopd:+.1f}</div>
          <div class='traz-grid'>
            <div class='traz-item'>
              <div class='traz-lbl'>BOPD — Caso base ({br['Hz']:.0f} Hz)</div>
              <div class='traz-val dn'>{num(bopd_base,1)} STB/d</div>
            </div>
            <div class='traz-arrow'>→</div>
            <div class='traz-item'>
              <div class='traz-lbl'>BOPD — Recomendado ({rec['Hz']:.0f} Hz)</div>
              <div class='traz-val up'>{num(bopd_rec,1)} STB/d</div>
            </div>
            <div class='traz-item'>
              <div class='traz-lbl'>Δ BOPD = {num(bopd_rec,1)} − {num(bopd_base,1)}</div>
              <div class='traz-val up'>{delta_bopd:+.1f} STB/d</div>
            </div>
          </div>
          <div class='traz-grid' style='margin-top:8px'>
            <div class='traz-item'>
              <div class='traz-lbl'>BWPD — Caso base</div>
              <div class='traz-val dn'>{num(bwpd_base,1)} STB/d</div>
            </div>
            <div class='traz-arrow'>→</div>
            <div class='traz-item'>
              <div class='traz-lbl'>BWPD — Recomendado</div>
              <div class='traz-val dn'>{num(bwpd_rec,1)} STB/d</div>
            </div>
            <div class='traz-item'>
              <div class='traz-lbl'>BSW del pozo</div>
              <div class='traz-val dn'>{p["bsw"]:.1f} %</div>
            </div>
          </div>
          <div class='traz-formula'>
            <b>Fórmula:</b> Δ BOPD = BOPD<sub>rec</sub> − BOPD<sub>base</sub> = {num(bopd_rec,1)} − {num(bopd_base,1)} = <b>{delta_bopd:+.1f} STB/d</b>
            &nbsp;·&nbsp; Ganancia anual = Δ BOPD × Precio × 365 = {delta_bopd:.1f} × ${p["price"]:.0f} × 365 = <b>{money(rec.get("RevYear"))}</b>
          </div>
        </div>""",unsafe_allow_html=True)

        st.write("")

        # Resumen ejecutivo: barra prod + VLP + anillo IA
        st.markdown("<div class='sec-head'>📊 Resumen ejecutivo</div>",unsafe_allow_html=True)
        rc1,rc2,rc3=st.columns([1,1.6,0.95])
        with rc1:
            fig=go.Figure()
            fig.add_trace(go.Bar(
                x=["Base","Rec."],y=[base_bfpd_val,rec_bfpd_val],
                text=[f"{base_bfpd_val:,.0f}",f"{rec_bfpd_val:,.0f}"],
                textposition="outside",textfont=dict(size=11,color="#D8E0EA"),
                marker=dict(color=["#2E6DA4","#28A870"],
                    line=dict(color="rgba(255,255,255,.15)",width=1)),
                width=0.45,showlegend=False,
                hovertemplate="<b>%{x}</b><br>BFPD: %{y:,.0f}<extra></extra>"))
            fig.add_annotation(x=1,y=rec_bfpd_val,
                text=f"<b>+{uplift:.1f}%</b>",showarrow=True,arrowhead=2,
                arrowcolor="#28A870",ax=0,ay=-38,
                bgcolor="rgba(20,45,30,.85)",bordercolor="#28A870",
                borderwidth=1,borderpad=4,font=dict(size=11,color="#A8DFC4"))
            fig.update_layout(
                template="plotly_dark",height=310,
                margin=dict(l=10,r=10,t=35,b=45),
                plot_bgcolor="#161C24",paper_bgcolor="#1E2530",
                font=dict(color="#D8E0EA",family="Arial",size=11),
                title=dict(text="Producción de fluidos — Base vs. Recomendado",
                    font=dict(size=11,color="#8A9DB5"),x=0),
                xaxis_title="Escenario",
                yaxis_title="Caudal líquido, q<sub>L</sub> (STB/d)",
                bargap=0.5)
            fig.update_xaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.10)",showline=True,
                linecolor="rgba(138,157,181,.30)",tickfont=dict(size=11),
                title_font=dict(size=11))
            fig.update_yaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.15)",gridwidth=1,
                showline=True,linecolor="rgba(138,157,181,.30)",
                range=[0,max(base_bfpd_val,rec_bfpd_val)*1.30],
                tickformat=",d",tickfont=dict(size=10),title_font=dict(size=11),
                zeroline=True,zerolinecolor="rgba(138,157,181,.20)",zerolinewidth=1,
                minor=dict(showgrid=True,gridcolor="rgba(138,157,181,.05)"))
            st.plotly_chart(fig,use_container_width=True)


        with rc2:
            # ── Paleta profesional por frecuencia ──
            pal_lines=["#4A90D9","#5BA85C","#D4A843","#9B59B6","#E67E22","#1ABC9C"]
            fig=go.Figure()

            # Buscar curva IPR: se usa SOLO el archivo de sensibilidad (sc),
            # para no mezclar escalas distintas con el caso base (bc)
            ipr_source=sc
            ipr_g=ipr_source.dropna(subset=["LR","IPR"]).sort_values("LR") if "IPR" in ipr_source.columns else pd.DataFrame()

            # Dibujar IPR única (no cambia con Hz)
            if not ipr_g.empty:
                fig.add_trace(go.Scatter(
                    x=ipr_g["LR"], y=ipr_g["IPR"],
                    mode="lines", name="IPR (Afluencia)",
                    line=dict(color="#E05A5A", width=2.5, dash="dot"),
                    showlegend=True))

            # Dibujar curvas VLP por frecuencia
            hz_base_val=float(br.get("Hz", p["hz_base"]))
            for i,hz in enumerate(plot_freqs):
                g=sc[sc["Hz"]==hz].dropna(subset=["LR","VLP"]).sort_values("LR")
                if g.empty: continue
                is_rec=abs(hz-rec["Hz"])<1e-6
                is_base=abs(hz-hz_base_val)<1e-6
                color=pal_lines[i%len(pal_lines)]
                width=3 if is_rec else (2 if is_base else 1.5)
                dash="solid" if is_rec or is_base else "solid"
                opacity=1.0 if is_rec else (0.85 if is_base else 0.55)
                name_suffix=" ← CASO BASE" if is_base else (" ← RECOMENDADO" if is_rec else "")
                fig.add_trace(go.Scatter(
                    x=g["LR"], y=g["VLP"],
                    mode="lines",
                    name=f"VLP {hz:g} Hz{name_suffix}",
                    line=dict(color=color, width=width, dash=dash),
                    opacity=opacity))

            # Puntos de operación (intersección VLP-IPR) por frecuencia
            for _,row in ssum.iterrows():
                hz=row["Hz"]
                g=sc[sc["Hz"]==hz].dropna(subset=["LR","VLP"]).sort_values("LR")
                if g.empty or pd.isna(row.get("BFPD",np.nan)): continue
                q=float(row["BFPD"])
                pv=float(np.interp(q, g["LR"].values, g["VLP"].values))
                is_rec=abs(hz-rec["Hz"])<1e-6
                is_base=abs(hz-hz_base_val)<1e-6
                i_hz=list(plot_freqs).index(hz) if hz in plot_freqs else 0
                color=pal_lines[i_hz%len(pal_lines)]
                fig.add_trace(go.Scatter(
                    x=[q], y=[pv],
                    mode="markers+text",
                    showlegend=False,
                    text=[f"  {q:,.0f} STB/d" if is_rec or is_base else ""],
                    textposition="middle right",
                    textfont=dict(size=10, color=color),
                    marker=dict(
                        size=14 if is_rec else (10 if is_base else 7),
                        symbol="diamond" if is_rec else ("circle" if is_base else "circle"),
                        color=color,
                        line=dict(width=2, color="white"))))

            # Anotaciones: etiqueta caso base y recomendado
            base_g=sc[sc["Hz"]==hz_base_val].dropna(subset=["LR","VLP"]).sort_values("LR")
            if not base_g.empty and not pd.isna(br.get("BFPD",np.nan)):
                q_b=float(br["BFPD"])
                pv_b=float(np.interp(q_b, base_g["LR"].values, base_g["VLP"].values))
                fig.add_annotation(x=q_b, y=pv_b,
                    text=f"<b>CASO BASE<br>{hz_base_val:.0f} Hz<br>{q_b:,.0f} STB/d</b>",
                    showarrow=True, arrowhead=2, arrowcolor="#8A9DB5",
                    ax=40, ay=-45,
                    bgcolor="rgba(30,37,48,0.90)", bordercolor="#8A9DB5",
                    borderwidth=1, borderpad=5,
                    font=dict(size=10, color="#D8E0EA"))

            rec_g=sc[sc["Hz"]==rec["Hz"]].dropna(subset=["LR","VLP"]).sort_values("LR")
            if not rec_g.empty and not pd.isna(rec.get("BFPD",np.nan)):
                q_r=float(rec["BFPD"])
                pv_r=float(np.interp(q_r, rec_g["LR"].values, rec_g["VLP"].values))
                fig.add_annotation(x=q_r, y=pv_r,
                    text=f"<b>RECOMENDADO<br>{rec['Hz']:.0f} Hz<br>{q_r:,.0f} STB/d</b>",
                    showarrow=True, arrowhead=2, arrowcolor="#28A870",
                    ax=-55, ay=-45,
                    bgcolor="rgba(20,45,30,0.90)", bordercolor="#28A870",
                    borderwidth=1, borderpad=5,
                    font=dict(size=10, color="#A8DFC4"))

            fig.update_layout(
                template="plotly_dark",
                height=340,
                margin=dict(l=10, r=10, t=30, b=80),
                plot_bgcolor="#161C24",
                paper_bgcolor="#1E2530",
                font=dict(color="#D8E0EA", family="Arial, sans-serif", size=11),
                title=dict(text="Análisis Nodal — Curvas VLP e IPR", font=dict(size=12, color="#8A9DB5"), x=0),
                xaxis_title="Caudal líquido, q<sub>L</sub> (STB/d)",
                yaxis_title="Presión de nodo (psig)",
                legend=dict(
                    orientation="h", y=-0.28, x=0,
                    font=dict(size=9.5),
                    bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(0,0,0,0)"),
                hovermode="x unified")
            fig.update_xaxes(
                showgrid=True, gridcolor="rgba(138,157,181,.15)", gridwidth=1,
                showline=True, linecolor="rgba(138,157,181,.30)", linewidth=1,
                zeroline=False,
                tickformat=",d", tickfont=dict(size=10),
                title_font=dict(size=11), minor=dict(showgrid=True, gridcolor="rgba(138,157,181,.06)"))
            fig.update_yaxes(
                showgrid=True, gridcolor="rgba(138,157,181,.15)", gridwidth=1,
                showline=True, linecolor="rgba(138,157,181,.30)", linewidth=1,
                zeroline=False,
                tickformat=",d", tickfont=dict(size=10),
                title_font=dict(size=11), minor=dict(showgrid=True, gridcolor="rgba(138,157,181,.06)"))
            st.plotly_chart(fig, use_container_width=True)

        with rc3:
            ai_html=f"""
            <div style="height:340px;box-sizing:border-box;position:relative;overflow:hidden;border-radius:16px;padding:16px;color:white;
              background:radial-gradient(circle at 25% 18%,rgba(91,141,184,.16),transparent 30%),radial-gradient(circle at 85% 45%,rgba(201,163,104,.11),transparent 28%),
              linear-gradient(135deg,#111a2f,#0b1020,#121a31);border:1px solid rgba(150,165,185,.14);font-family:Arial,sans-serif;">
              <div style="display:inline-block;padding:4px 9px;border-radius:999px;background:rgba(91,141,184,.10);border:1px solid rgba(91,141,184,.25);color:#a8c5db;font-size:11px;font-weight:900;margin-bottom:14px;">● Evaluación multicriterio</div>
              <div>
                <div style="font-size:46px;line-height:1;font-weight:950;color:white;">{rec['Hz']:.0f} <span style="font-size:16px;color:#9aabbd;">Hz</span></div>
                <div style="margin-top:6px;color:#9aabbd;font-size:13px;">Mejor evaluación multicriterio.</div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:24px;">
                <div style="background:rgba(255,255,255,.07);border-radius:13px;padding:14px 10px;"><span style="display:block;color:#9aabbd;font-size:11px;font-weight:800;margin-bottom:6px;">BFPD</span><b style="color:white;font-size:19px;">{num(rec['BFPD'],0)}</b></div>
                <div style="background:rgba(255,255,255,.07);border-radius:13px;padding:14px 10px;"><span style="display:block;color:#9aabbd;font-size:11px;font-weight:800;margin-bottom:6px;">Δ BOPD</span><b style="color:white;font-size:19px;">{num(rec['dBOPD'],1)}</b></div>
                <div style="background:rgba(255,255,255,.07);border-radius:13px;padding:14px 10px;"><span style="display:block;color:#9aabbd;font-size:11px;font-weight:800;margin-bottom:6px;">Confianza</span><b style="color:white;font-size:19px;">{conf:.0f}%</b></div>
              </div>
              <div style="margin-top:12px;border-radius:11px;padding:10px;background:rgba(241,162,8,.12);border:1px solid rgba(241,162,8,.28);color:#ffd27a;font-size:13px;font-weight:900;text-align:center;">{ric} Estado: {rst}</div>
            </div>"""
            components.html(ai_html,height=350)

        # Cinema animado
        st.markdown("<div class='anim-head'>🎬 Gráfico dinámico</div>",unsafe_allow_html=True)
        st.markdown(cinema_html(br,rec,ssum),unsafe_allow_html=True)

        # Nodal comparativo
        st.markdown("<div class='sec-head'>🔬 Análisis nodal comparativo</div>",unsafe_allow_html=True)
        nc1,nc2=st.columns(2)
        with nc1:
            if bc is not None and not bc.empty:
                hz_b=bc.iloc[(bc["Hz"]-p["hz_base"]).abs().argsort()[:1]]["Hz"].iloc[0]
                st.markdown(nodal_svg("IPR/VLP — Caso base",bc[bc["Hz"]==hz_b].sort_values("LR"),br,"Base"),unsafe_allow_html=True)
            else:
                st.markdown("<div class='nodal-card'><div class='ntitle'>Caso base</div><p style='color:#9aabbd;position:relative;z-index:2;font-size:13px'>No se cargó archivo base.</p></div>",unsafe_allow_html=True)
        with nc2:
            gr=sc[sc["Hz"]==rec["Hz"]].sort_values("LR")
            st.markdown(nodal_svg(f"IPR/VLP — {rec['Hz']:.0f} Hz (recomendado)",gr,rec,"Recomendado"),unsafe_allow_html=True)

        # Impacto
        st.markdown("<div class='anim-head'>💎 Impacto esperado y recuperación incremental</div>",unsafe_allow_html=True)
        im1,im3=st.columns(2)

        with im1:
            bopd_base_disp=float(br.get("BOPD",0) or 0)
            pct_uplift=(float(rec["dBOPD"])/bopd_base_disp*100) if bopd_base_disp>0 else 0.0
            pct_gauge=min(max(pct_uplift,0),100)
            circ2=2*3.14159*58; off2=circ2*(1-pct_gauge/100)
            nota_cap=("" if pct_uplift<=100 else
                f"<br><span style=\"color:#e8b45c;\">⚠️ El anillo se satura visualmente en 100%; el incremento real calculado es {pct_uplift:.0f}%.</span>")
            components.html(f"""<div style="position:relative;min-height:400px;box-sizing:border-box;background:#1d2a35;color:white;overflow:visible;padding:15px 18px;border:1px solid rgba(255,255,255,.05);border-radius:14px;font-family:Arial,sans-serif;">
              <div style="color:#5f7f99;font-size:1.2rem;font-weight:900;margin-bottom:5px;">Incremento de petróleo</div>
              <div style="display:flex;justify-content:center;align-items:center;height:140px;">
                <svg viewBox="0 0 160 160" width="140" height="140">
                  <circle cx="80" cy="80" r="58" fill="none" stroke="#172630" stroke-width="13"/>
                  <circle cx="80" cy="80" r="58" fill="none" stroke="#5B8DB8" stroke-width="13" stroke-linecap="round"
                    transform="rotate(-90 80 80)" stroke-dasharray="{circ2:.2f}" stroke-dashoffset="{off2:.2f}"
                    style="filter:drop-shadow(0 0 8px #5B8DB8)"/>
                  <circle cx="80" cy="80" r="43" fill="#1d2a35"/>
                  <text x="80" y="85" fill="white" font-size="28" font-weight="900" text-anchor="middle">{pct_uplift:.0f}%</text>
                </svg>
              </div>
              <div style="color:#7c8da0;font-size:12px;font-weight:800;text-align:center;margin-top:3px;">Incremento vs. producción base</div>
              <div style="color:#e8edf3;font-size:13px;font-weight:900;text-align:right;margin-top:4px;">{num(rec['dBOPD'],1)} BOPD adicionales</div>
              <div style="margin-top:10px;padding-top:9px;border-top:1px solid rgba(255,255,255,.10);font-size:10.5px;color:#a9bacb;line-height:1.55;">
                <b style="color:#8fc0e6;">Fórmula:</b> % = (ΔBOPD ÷ BOPD del caso base) × 100
                <br>= ({num(rec['dBOPD'],1)} ÷ {num(bopd_base_disp,1)}) × 100 = <b style="color:#e8edf3;">{pct_uplift:.1f}%</b>
                <br><span style="color:#7c8da0;">El pozo pasaría de {num(bopd_base_disp,1)} a {num(bopd_base_disp+float(rec['dBOPD']),1)} BOPD, un aumento del {pct_uplift:.1f}% respecto a su producción actual.</span>{nota_cap}
              </div>
            </div>""",height=420)

        with im3:
            st.markdown(f"""
            <div class='impact-card'>
              <h3>Ganancias y recuperación</h3>
              <div class='irow'><div class='iico'>$</div><div class='ilbl'>Ganancia diaria</div><div class='ival'>{money(rec['RevDay'])}</div></div>
              <div class='irow'><div class='iico'>M</div><div class='ilbl'>Ganancia mensual</div><div class='ival'>{money(rec['RevMon'])}</div></div>
              <div class='irow'><div class='iico'>A</div><div class='ilbl'>Ganancia anual</div><div class='ival' style='color:#19a463'>{money(rec['RevYear'])}</div></div>
              <div class='irow'><div class='iico'>⛽</div><div class='ilbl'>bbl/año incrementales</div><div class='ival'>{num(rec['RecBbl'],0)}</div></div>
            </div>""",unsafe_allow_html=True)

        # Exploración + semáforo + BES
        st.markdown("<div class='sec-head'>🔎 Exploración y resultados</div>",unsafe_allow_html=True)
        exp_f=st.selectbox(f"Explorar frecuencia — {pid}",plot_freqs,key=f"exp_{pid}")
        exp_r=ssum.iloc[(ssum["Hz"]-exp_f).abs().argsort()[:1]].iloc[0]
        e_st,e_css,e_ic,e_al=classify(exp_r,p["max_hz"],p["min_g"])

        ex1,ex2,ex3=st.columns(3)
        with ex1:
            st.markdown(f"<div class='{e_css}'><b>{e_ic} {e_st}</b><br>{'<br>'.join(e_al)}</div>",unsafe_allow_html=True)
            st.markdown(f"""<div class='mgrid'>
              <div class='mbox'><b>{exp_r['Hz']:.0f} Hz</b><span>Frecuencia explorada</span></div>
              <div class='mbox'><b>{num(exp_r['BFPD'])}</b><span>BFPD</span></div>
              <div class='mbox'><b>{num(exp_r['dBOPD'],1)}</b><span>Δ BOPD</span></div>
              <div class='mbox'><b>{cmoney(exp_r['RevYear'])}</b><span>Ganancia anual</span></div>
            </div>""",unsafe_allow_html=True)
        with ex2:
            semaf=pd.DataFrame({"Estado":["🟢 ÓPTIMO","🟡 REVISIÓN","🔴 LÍMITE OP.","⚪ SIN MEJORA","⚪ BASE"],
                "Criterio":["Producción, economía y Hz dentro del límite.",
                            "En el límite o mejora baja.",
                            "Supera Hz máxima recomendada.",
                            "No incrementa petróleo.",
                            "Caso de referencia."]})
            st.dataframe(semaf,use_container_width=True,height=210,hide_index=True)
        with ex3:
            info=p.get("info",{})
            st.markdown(f"""
            <div class='panel'>
              <div style='color:#c5d2e0;font-size:.84rem;line-height:1.8;'>
                <b>Bomba:</b> {p.get("bomba") or info.get("pump","No detectada")}<br>
                <b>Motor:</b> {info.get("motor","No detectado")}<br>
                <b>Cable:</b> {info.get("cable","No detectado")}<br>
                <b>BSW:</b> {p["bsw"]:.1f}%<br>
                <b>Precio:</b> {money(p["price"])}/bbl<br>
                <b>Score:</b> 40% prod · 30% econ · 20% riesgo · 10% Hz
              </div>
            </div>""",unsafe_allow_html=True)


        # Animación nodal profesional
        with st.expander(f"🎞️ Análisis Nodal animado — {pid}"):
            has_ipr="IPR" in sc.columns
            pal_anim=["#4A90D9","#5BA85C","#D4A843","#9B59B6","#E67E22","#1ABC9C"]
            frames=[]
            for hz in plot_freqs:
                g=sc[sc["Hz"]==hz].sort_values("LR")
                frame_data=[]
                if has_ipr:
                    frame_data.append(go.Scatter(
                        x=g["LR"],y=g["IPR"],mode="lines",name="IPR",
                        line=dict(color="#E05A5A",width=2.5,dash="dot")))
                frame_data.append(go.Scatter(
                    x=g["LR"],y=g["VLP"],mode="lines",name=f"VLP {hz:g} Hz",
                    line=dict(color="#4A90D9",width=3)))
                # Punto de operación
                row_hz=ssum[abs(ssum["Hz"]-hz)<0.1]
                if not row_hz.empty:
                    q_op=float(row_hz.iloc[0]["BFPD"])
                    p_op=float(np.interp(q_op,g["LR"].values,g["VLP"].values))
                    frame_data.append(go.Scatter(
                        x=[q_op],y=[p_op],mode="markers+text",name="Punto operación",
                        text=[f"  q={q_op:,.0f} STB/d"],textposition="middle right",
                        textfont=dict(size=10,color="#D8E0EA"),
                        marker=dict(size=12,color="#D4A843",symbol="diamond",
                            line=dict(width=2,color="white"))))
                frames.append(go.Frame(data=frame_data,name=str(hz)))

            fg0=sc[sc["Hz"]==plot_freqs[0]].sort_values("LR")
            init_data=[]
            if has_ipr:
                init_data.append(go.Scatter(x=fg0["LR"],y=fg0["IPR"],mode="lines",
                    name="IPR (Afluencia)",line=dict(color="#E05A5A",width=2.5,dash="dot")))
            init_data.append(go.Scatter(x=fg0["LR"],y=fg0["VLP"],mode="lines",
                name=f"VLP {plot_freqs[0]:g} Hz",line=dict(color="#4A90D9",width=3)))
            row0=ssum[abs(ssum["Hz"]-plot_freqs[0])<0.1]
            if not row0.empty:
                q0=float(row0.iloc[0]["BFPD"])
                p0=float(np.interp(q0,fg0["LR"].values,fg0["VLP"].values))
                init_data.append(go.Scatter(x=[q0],y=[p0],mode="markers+text",
                    name="Punto operación",
                    text=[f"  q={q0:,.0f} STB/d"],textposition="middle right",
                    textfont=dict(size=10,color="#D8E0EA"),
                    marker=dict(size=12,color="#D4A843",symbol="diamond",
                        line=dict(width=2,color="white"))))

            # Rango fijo de ejes (usa todas las frecuencias) para que la cuadrícula
            # y los ejes no salten entre cuadros de la animación
            _x_vals=[sc["LR"]]; _y_vals=[sc["VLP"]]
            if has_ipr: _y_vals.append(sc["IPR"])
            _x_all=pd.concat(_x_vals).dropna(); _y_all=pd.concat(_y_vals).dropna()
            xr=[0,float(_x_all.max())*1.08] if not _x_all.empty else None
            yr=[0,float(_y_all.max())*1.12] if not _y_all.empty else None

            figan=go.Figure(data=init_data,frames=frames)
            figan.update_layout(
                template="plotly_dark",height=460,
                plot_bgcolor="#161C24",paper_bgcolor="#1E2530",
                font=dict(color="#D8E0EA",family="Arial",size=11),
                title=dict(text="Análisis Nodal — Sensibilidad de Frecuencia BES",
                    font=dict(size=12,color="#8A9DB5"),x=0),
                xaxis_title="Caudal líquido, q<sub>L</sub> (STB/d)",
                yaxis_title="Presión de nodo (psig)",
                legend=dict(orientation="h",y=-0.15,font=dict(size=10),
                    bgcolor="rgba(0,0,0,0)"),
                sliders=[{"currentvalue":{"prefix":"Frecuencia: ","suffix":" Hz","font":{"size":12}},
                    "y":0.02,"len":0.95,
                    "steps":[{"label":f"{hz:g}","method":"animate",
                        "args":[[str(hz)],{"frame":{"duration":0,"redraw":True},"mode":"immediate"}]}
                        for hz in plot_freqs]}])
            figan.update_xaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.15)",gridwidth=1,
                showline=True,linecolor="rgba(138,157,181,.30)",
                range=xr,autorange=False if xr else True,
                tickformat=",d",tickfont=dict(size=10),title_font=dict(size=11),
                minor=dict(showgrid=True,gridcolor="rgba(138,157,181,.06)"))
            figan.update_yaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.15)",gridwidth=1,
                showline=True,linecolor="rgba(138,157,181,.30)",
                range=yr,autorange=False if yr else True,
                tickformat=",d",tickfont=dict(size=10),title_font=dict(size=11),
                minor=dict(showgrid=True,gridcolor="rgba(138,157,181,.06)"))
            st.plotly_chart(figan,use_container_width=True)

        # Comentario final
        if rst=="REVISIÓN": conc="Mejora de producción y beneficio económico, pero opera en el límite de frecuencia. Validar con restricciones reales antes de implementar."
        elif rst=="ÓPTIMO": conc="Balance favorable entre producción, ganancia estimada y riesgo operativo. Puede considerarse como alternativa principal."
        elif rst=="LÍMITE OP.": conc="Tiene potencial productivo, pero supera el límite operativo definido. Requiere revisión técnica."
        else: conc="Los escenarios deben revisarse porque la mejora no es suficientemente clara bajo los criterios definidos."
        st.markdown(f"""
        <div class='final'>
          <span class='ftag'>Interpretación automática</span><span class='ftag'>PROSPER + KPIs</span><br><br>
          El análisis compara el caso base de <b>{num(br['BFPD'])} BFPD a {br['Hz']:.0f} Hz</b> contra la alternativa recomendada de
          <b>{num(rec['BFPD'])} BFPD a {rec['Hz']:.0f} Hz</b>. Incremento de <b>{num(rec['dBOPD'],1)} BOPD</b>,
          equivalente a <b>{num(rec['RecBbl'],0)} bbl/año</b>, con ganancia de <b>{money(rec['RevYear'])}</b>. {conc}
        </div>""",unsafe_allow_html=True)
        st.caption("Evaluación preliminar y multicriterio. Validar con criterio de ingeniería de producción.")

        # ══════════════════════════════════════════════════════════
        # ANÁLISIS TÉCNICO AUTOMATIZADO — basado en reglas de ingeniería
        # (gratuito, no requiere internet ni API de pago)
        # ══════════════════════════════════════════════════════════
        st.markdown("""
        <div style='background:linear-gradient(135deg,#0F1B2D,#142035);border:1px solid rgba(46,109,164,.30);
          border-left:4px solid #2E6DA4;border-radius:8px;padding:14px 18px;margin:12px 0 8px;'>
          <div style='display:flex;align-items:center;gap:10px;'>
            <div style='font-size:22px;'>🔍</div>
            <div>
              <div style='font-size:13px;font-weight:700;color:#D8E0EA;'>ANÁLISIS TÉCNICO AUTOMATIZADO</div>
              <div style='font-size:11px;color:#8A9DB5;margin-top:1px;'>
                Interpretación generada automáticamente aplicando reglas de ingeniería de producción
                sobre los datos reales del pozo (sin conexión a internet ni servicios externos de pago).
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        key_ia=f"ia_resultado_{pid}"

        if st.button("🔍 Generar análisis técnico", key=f"btn_ia_{pid}",
                     type="primary", use_container_width=False):
            st.session_state[key_ia] = generate_rule_based_analysis(pid, p, br, rec, ssum, rst)

        if key_ia in st.session_state and st.session_state[key_ia]:
            texto=st.session_state[key_ia]
            st.markdown(f"""
            <div style='background:#1E2530;border:1px solid rgba(46,109,164,.20);border-radius:8px;
              padding:18px 20px;margin-top:4px;'>
              <div style='display:flex;align-items:center;gap:8px;margin-bottom:12px;'>
                <div style='font-size:16px;'>🔍</div>
                <div style='font-size:12px;font-weight:700;color:#6EAADC;text-transform:uppercase;
                  letter-spacing:.05em;'>Análisis técnico automatizado — Pozo {pid}</div>
              </div>
              <div style='font-size:13px;color:#C8D4E0;line-height:1.75;white-space:pre-wrap;
                font-family:Arial,sans-serif;'>{texto}</div>
              <div style='margin-top:12px;padding-top:10px;border-top:1px solid rgba(46,109,164,.15);
                font-size:10px;color:#8A9DB5;'>
                ℹ️ Este texto se genera localmente aplicando reglas de ingeniería de producción sobre
                los datos de simulación de PROSPER cargados para este pozo. No sustituye el criterio de
                un ingeniero de producción antes de implementar cambios operativos.
              </div>
            </div>""", unsafe_allow_html=True)

            if st.button("🗑️ Limpiar análisis", key=f"clear_ia_{pid}"):
                st.session_state.pop(key_ia, None)
                st.rerun()

        # Descarga
        dl1,dl2=st.columns(2)
        with dl1:
            fc=[c for c in ["Tipo","Hz","BFPD","BOPD","BWPD","dBFPD","dBOPD","RevDay","RevMon","RevYear","RecBbl","Payback","Score"] if c in ssum.columns]
            csv=ssum[fc].round(4).to_csv(index=False).encode("utf-8")
            st.download_button(f"⬇️ Descargar CSV — {pid}",csv,f"optiflow_{pid}.csv","text/csv",use_container_width=True)
        with dl2:
            pdf_buf=generate_well_pdf(pid,p)
            st.download_button(f"📄 Descargar PDF — {pid}",pdf_buf,f"optiflow_{pid}_reporte.pdf","application/pdf",use_container_width=True)

    else:
        st.markdown("<div class='hint'>📂 Sube los archivos PROSPER y presiona <b>Procesar todo</b>.<br>Si solo tienes el caso base, usa <b>Guardar solo caso base</b> para ver info parcial.</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# VISTA: COMPARACIÓN
# ══════════════════════════════════════════════════════════════════
elif st.session_state.vista=="comparar":
    if st.button("← Volver al campo"): nav("manager")
    ready_p={pid:p for pid,p in st.session_state.pozos.items() if p.get("ready")}
    if len(ready_p)<1:
        st.markdown("<div class='hint'>Necesitas al menos 1 pozo con análisis completo.</div>",unsafe_allow_html=True); st.stop()

    st.markdown("<div class='sec-head'>📊 Comparación multi-pozo</div>",unsafe_allow_html=True)
    all_ids=list(ready_p.keys())
    if "mp_sel" not in st.session_state: st.session_state.mp_sel=all_ids[:]

    # Selector de pozos
    sel=st.multiselect("Pozos a comparar:",all_ids,default=st.session_state.mp_sel,key="mp_sel")

    if len(sel)<2:
        st.info("Selecciona al menos 2 pozos para comparar.")
    else:
        data={pid:ready_p[pid] for pid in sel}

        # Tabla comparativa
        rows=[
            ("BFPD actual","bfpd_base","max"),("BOPD actual","bopd_base","max"),
            ("BSW (%)","bsw","min"),("Hz actual","hz_base",None),("Hz recomendada",None,None),
            ("BFPD recomendado",None,"max"),("Δ BOPD",None,"max"),
            ("Ganancia/año USD",None,"max"),("Score",None,"max"),
        ]
        rec_map={pid:p["rec_row"] for pid,p in data.items()}

        def getv(p,key):
            if key=="Hz recomendada": return p["rec_row"]["Hz"]
            if key=="BFPD recomendado": return p["rec_row"]["BFPD"]
            if key=="Δ BOPD": return p["rec_row"]["dBOPD"]
            if key=="Ganancia/año USD": return p["rec_row"]["RevYear"]
            if key=="Score": return p["rec_row"].get("Score",0)
            return p.get(key,np.nan)

        hdr="<tr><th style='text-align:left;padding:8px 10px;color:#9aabbd;font-size:11px;border-bottom:1px solid rgba(150,165,185,.14);'>Parámetro</th>"
        for pid in sel: hdr+=f"<th style='text-align:right;padding:8px 10px;color:#5B8DB8;font-size:11px;border-bottom:1px solid rgba(150,165,185,.14);'>{pid}</th>"
        hdr+="</tr>"

        body=""
        for lbl,key,best in rows:
            vals=[getv(p,lbl if key is None else key) for p in data.values()]
            bv=(max(vals) if best=="max" else min(vals)) if best and all(v is not None and not (isinstance(v,float) and np.isnan(v)) for v in vals) else None
            body+=f"<tr><td style='padding:8px 10px;color:#9aabbd;font-size:12px;border-bottom:1px solid rgba(255,255,255,.04);'>{lbl}</td>"
            for pid in sel:
                p=data[pid]; v=getv(p,lbl if key is None else key)
                is_b=bv is not None and v==bv
                is_w=best=="max" and bv is not None and len(sel)>1 and v==min(vals) and not is_b
                color="#6FA287" if is_b else ("#ff7a7a" if is_w else "#c5d2e0")
                fw="800" if is_b else "400"
                disp=f"${v:,.0f}" if "USD" in lbl else (f"{v:,.1f}" if isinstance(v,float) else str(v))
                body+=f"<td style='text-align:right;padding:8px 10px;font-size:12px;color:{color};font-weight:{fw};border-bottom:1px solid rgba(255,255,255,.04);'>{disp}</td>"
            body+="</tr>"

        st.markdown(f"""
        <div style='background:#1b212c;border:1px solid rgba(150,165,185,.14);border-radius:13px;overflow-x:auto;margin-bottom:14px;'>
          <table style='width:100%;border-collapse:collapse;'><thead>{hdr}</thead><tbody>{body}</tbody></table>
        </div>""",unsafe_allow_html=True)

        # Gráficos comparación multi-pozo
        bc1,bc2=st.columns(2)
        with bc1:
            fig=go.Figure()
            fig.add_trace(go.Bar(
                name="BFPD base",x=sel,
                y=[data[pid].get("bfpd_base",0) or 0 for pid in sel],
                marker=dict(color="#2E6DA4",opacity=0.7,
                    line=dict(color="rgba(255,255,255,.10)",width=1)),
                text=[f"{data[pid].get('bfpd_base',0) or 0:,.0f}" for pid in sel],
                textposition="outside",textfont=dict(size=9),
                hovertemplate="<b>%{x}</b> — Base<br>BFPD: %{y:,.0f}<extra></extra>"))
            fig.add_trace(go.Bar(
                name="BFPD recomendado",x=sel,
                y=[data[pid]["rec_row"]["BFPD"] for pid in sel],
                marker=dict(color="#28A870",opacity=0.85,
                    line=dict(color="rgba(255,255,255,.10)",width=1)),
                text=[f"{data[pid]['rec_row']['BFPD']:,.0f}" for pid in sel],
                textposition="outside",textfont=dict(size=9),
                hovertemplate="<b>%{x}</b> — Rec.<br>BFPD: %{y:,.0f}<extra></extra>"))
            fig.update_layout(
                barmode="group",template="plotly_dark",height=300,
                margin=dict(l=10,r=10,t=35,b=60),
                plot_bgcolor="#161C24",paper_bgcolor="#1E2530",
                font=dict(color="#D8E0EA",family="Arial",size=11),
                title=dict(text="Producción de fluidos — Base vs. Recomendado por pozo",
                    font=dict(size=11,color="#8A9DB5"),x=0),
                xaxis_title="Pozo",
                yaxis_title="Caudal líquido, q<sub>L</sub> (STB/d)",
                legend=dict(orientation="h",y=-0.22,font=dict(size=10),
                    bgcolor="rgba(0,0,0,0)"),bargap=0.25,bargroupgap=0.08)
            fig.update_xaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.10)",showline=True,
                linecolor="rgba(138,157,181,.30)",tickfont=dict(size=11),
                title_font=dict(size=11))
            fig.update_yaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.15)",gridwidth=1,
                showline=True,linecolor="rgba(138,157,181,.30)",
                tickformat=",d",tickfont=dict(size=10),title_font=dict(size=11),
                zeroline=True,zerolinecolor="rgba(138,157,181,.20)",
                minor=dict(showgrid=True,gridcolor="rgba(138,157,181,.05)"))
            st.plotly_chart(fig,use_container_width=True)

        with bc2:
            gains=[data[pid]["rec_row"]["RevYear"] for pid in sel]
            pal_mp=["#2E6DA4","#1E7D58","#D4A843","#9B59B6","#E67E22"]
            fig2=go.Figure(go.Bar(
                x=sel,y=gains,
                marker=dict(
                    color=[pal_mp[i%len(pal_mp)] for i in range(len(sel))],
                    line=dict(color="rgba(255,255,255,.10)",width=1)),
                text=[cmoney(g) for g in gains],
                textposition="outside",textfont=dict(size=10,color="#D8E0EA"),
                hovertemplate="<b>%{x}</b><br>Ganancia: %{text}<extra></extra>"))
            fig2.update_layout(
                template="plotly_dark",height=300,
                margin=dict(l=10,r=10,t=35,b=60),
                plot_bgcolor="#161C24",paper_bgcolor="#1E2530",
                font=dict(color="#D8E0EA",family="Arial",size=11),
                title=dict(text="Ganancia anual estimada por pozo",
                    font=dict(size=11,color="#8A9DB5"),x=0),
                xaxis_title="Pozo",
                yaxis_title="Ganancia anual (USD/año)")
            fig2.update_xaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.10)",showline=True,
                linecolor="rgba(138,157,181,.30)",tickfont=dict(size=11),
                title_font=dict(size=11))
            fig2.update_yaxes(
                showgrid=True,gridcolor="rgba(138,157,181,.15)",gridwidth=1,
                showline=True,linecolor="rgba(138,157,181,.30)",
                tickformat="$,.0f",tickfont=dict(size=10),title_font=dict(size=11),
                zeroline=True,zerolinecolor="rgba(138,157,181,.20)",
                minor=dict(showgrid=True,gridcolor="rgba(138,157,181,.05)"))
            st.plotly_chart(fig2,use_container_width=True)

        # Ranking final
        sorted_s=sorted(sel,key=lambda pid:data[pid]["rec_row"]["RevYear"],reverse=True)
        medals=["🥇","🥈","🥉"]; mcolors=["#BA7517","#888780","#3B6D11"]
        st.markdown("<div class='sec-head'>🏆 Ranking y prioridad de intervención</div>",unsafe_allow_html=True)
        rcols=st.columns(min(len(sorted_s),5))
        for i,pid in enumerate(sorted_s):
            with rcols[i%5]:
                rr=data[pid]["rec_row"]
                m=medals[i] if i<3 else f"#{i+1}"
                mc=mcolors[i] if i<3 else "#7c8da0"
                st.markdown(f"""
                <div style='background:rgba(255,255,255,.06);border:1px solid rgba(150,165,185,.14);border-radius:13px;padding:12px;text-align:center;margin-bottom:8px;'>
                  <div style='font-size:24px;font-weight:950;color:{mc};'>{m}</div>
                  <div style='font-size:13px;font-weight:800;color:#e8edf3;margin-bottom:6px;'>{pid}</div>
                  <div style='font-size:10px;color:#7c8da0;'>Ganancia anual</div>
                  <div style='font-size:13px;color:#6FA287;font-weight:800;'>{cmoney(rr["RevYear"])}</div>
                  <div style='font-size:10px;color:#7c8da0;margin-top:5px;'>Δ BOPD · Score</div>
                  <div style='font-size:12px;color:#9aabbd;'>+{num(rr["dBOPD"],1)} · {rr.get("Score",0):.0f}/100</div>
                </div>""",unsafe_allow_html=True)

        total_g=sum(data[pid]["rec_row"]["RevYear"] for pid in sorted_s)
        total_d=sum(data[pid]["rec_row"]["dBOPD"] for pid in sorted_s)
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,rgba(91,141,184,.08),rgba(201,163,104,.06));border:1px solid rgba(91,141,184,.20);border-radius:12px;padding:12px 18px;display:flex;gap:28px;flex-wrap:wrap;margin-top:4px;'>
          <div><span style='display:block;font-size:10px;color:#7c8da0;'>Ganancia total campo</span><b style='font-size:1.2rem;font-weight:900;color:#6FA287;'>{cmoney(total_g)}/año</b></div>
          <div><span style='display:block;font-size:10px;color:#7c8da0;'>Total Δ BOPD</span><b style='font-size:1.2rem;font-weight:900;color:#5B8DB8;'>+{total_d:.1f} BOPD</b></div>
          <div><span style='display:block;font-size:10px;color:#7c8da0;'>Pozos comparados</span><b style='font-size:1.2rem;font-weight:900;color:#e8edf3;'>{len(sorted_s)}</b></div>
        </div>""",unsafe_allow_html=True)
