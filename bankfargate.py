"""Northstar Demo Bank — single-file educational banking UI for AWS ECS Fargate.

All balances and transactions are simulated in the browser using localStorage.
No real authentication, payment processing, credential handling or financial APIs.
"""
from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

PORT = int(os.getenv("PORT", "8080"))

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="theme-color" content="#073b91" />
<title>Northstar Demo Bank | Personal Banking</title>
<style>
:root{--navy:#092f76;--blue:#0756ba;--royal:#0e5bc4;--yellow:#ffca32;--ink:#17335c;--muted:#697d99;--line:#e4ebf5;--bg:#f4f7fc;--white:#fff;--green:#07856e;--red:#c74851;--shadow:0 10px 32px rgba(32,67,120,.07)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,"Segoe UI",Arial,sans-serif;color:var(--ink);font-size:14px}button,input,select{font:inherit}button{cursor:pointer}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #ffca32;outline-offset:2px}a{color:var(--blue)}.hidden{display:none!important}
.demo-ribbon{position:sticky;top:0;z-index:50;background:#fff5d6;border-bottom:1px solid #ffe094;color:#684c00;text-align:center;padding:8px 12px;font-weight:700;font-size:11px;letter-spacing:.055em}.shell{display:grid;grid-template-columns:247px minmax(0,1fr);min-height:calc(100vh - 31px)}
.sidebar{background:linear-gradient(170deg,#082962 0%,#07418f 56%,#0a53ad 100%);padding:29px 17px 25px;color:#fff;display:flex;flex-direction:column;gap:38px}.logo{display:flex;align-items:center;gap:10px;padding:0 13px}.logo-mark{background:#ffcb37;color:#073d89;font-weight:1000;font-size:22px;width:38px;height:38px;line-height:38px;text-align:center;border-radius:11px;box-shadow:0 5px 18px #00244e60}.logo-words strong{font-size:18px;letter-spacing:-.05em}.logo-words span{display:block;color:#bfd5f9;font-size:10px;text-transform:uppercase;letter-spacing:.18em;margin-top:2px}.nav-title{font-size:10px;font-weight:700;letter-spacing:.17em;color:#96bbef;padding:0 15px;margin:0 0 12px}.nav{display:grid;gap:6px}.nav-btn{border:0;background:transparent;color:#cfe1fb;text-align:left;padding:12px 14px;border-radius:11px;display:flex;gap:12px;align-items:center;font-weight:600;width:100%;transition:background .2s}.nav-btn svg{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.nav-btn:hover{background:#ffffff18;color:#fff}.nav-btn.active{background:#ffffff20;color:#fff;border-left:3px solid var(--yellow);padding-left:11px}.nav-label{font-size:13px}.side-bottom{margin-top:auto;padding:16px 12px;background:#ffffff12;border:1px solid #ffffff20;border-radius:15px}.side-bottom h4{font-size:12px;margin:0 0 6px}.side-bottom p{color:#b4d2fc;font-size:11px;line-height:1.6;margin:0}.side-bottom button{display:block;margin-top:12px;border:0;border-radius:8px;background:#fff;color:var(--navy);padding:8px 12px;font-weight:800;font-size:11px}
.content{min-width:0}.topbar{height:81px;border-bottom:1px solid var(--line);background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 36px;gap:14px}.crumb{font-size:12px;color:#7b8eaa;font-weight:600}.crumb strong{font-size:16px;color:#153b7b;display:block;margin-top:4px}.top-right{display:flex;align-items:center;gap:17px}.search{position:relative}.search input{width:205px;background:#f4f7fd;border:1px solid #e7edf6;border-radius:22px;padding:10px 16px 10px 37px;font-size:12px}.search svg{position:absolute;left:13px;top:11px;color:#99a9bd;width:16px;height:16px}.avatar{width:39px;height:39px;display:grid;place-items:center;background:#e9f1ff;border:2px solid #d2e2fb;color:#08488f;font-weight:900;border-radius:50%}.profile{font-size:12px;font-weight:800;line-height:1.4}.profile small{display:block;color:var(--muted);font-size:10px;font-weight:500}
.main{padding:29px 36px 54px;max-width:1500px;margin:0 auto}.view{display:none}.view.active{display:block}.eyebrow{color:var(--blue);font-weight:800;letter-spacing:.11em;text-transform:uppercase;font-size:10px;margin:0 0 8px}.page-title{font-size:27px;margin:0 0 5px;color:#153a72;letter-spacing:-.045em}.page-desc{color:var(--muted);margin:0 0 22px;line-height:1.5}
.hero{background:linear-gradient(110deg,#064797 0%,#0757b8 53%,#007bd1 100%);color:#fff;border-radius:20px;padding:31px 36px;display:flex;gap:25px;justify-content:space-between;align-items:center;box-shadow:0 18px 36px #075ab32a;overflow:hidden;position:relative}.hero:before{content:"";position:absolute;width:420px;height:420px;border:1px solid #ffffff24;border-radius:50%;right:-115px;top:-190px}.hero:after{content:"";position:absolute;width:300px;height:300px;border:1px solid #ffffff26;border-radius:50%;right:-47px;bottom:-245px}.hero-content{position:relative;z-index:1}.hero .muted{color:#e0edff;font-size:12px}.hero h1{font-size:38px;margin:10px 0 6px;font-weight:800;letter-spacing:-.06em}.hero .balance-label{font-size:12px;color:#e5f1ff}.hero .hero-note{font-size:12px;margin-top:21px;display:flex;align-items:center;gap:7px;color:#eaf3ff}.hero-note b{color:#ffde6d}.bank-card{z-index:1;position:relative;flex:0 0 240px;height:145px;border-radius:15px;background:linear-gradient(145deg,#f2d778,#d5a743 57%,#f8e8ac);color:#21375c;box-shadow:0 15px 34px #003c7a55;padding:19px 21px;transform:rotate(-7deg);overflow:hidden}.bank-card:before{content:"";position:absolute;width:240px;height:240px;right:-115px;top:-100px;border-radius:50%;border:25px solid #ffffff3a}.bank-card small{font-size:9px;letter-spacing:.14em;font-weight:900}.bank-card .chip{width:28px;height:20px;border-radius:5px;background:linear-gradient(130deg,#d2b67b,#fcf1ce,#c39a4e);margin:20px 0 10px;border:1px solid #ac8a4b}.bank-card .card-num{font-size:12px;font-weight:800;letter-spacing:.17em}.bank-card .card-foot{display:flex;justify-content:space-between;align-items:center;font-size:9px;font-weight:800;margin-top:10px}
.section-head{display:flex;align-items:center;justify-content:space-between;margin:30px 0 14px;gap:12px}.section-head h2{font-size:17px;letter-spacing:-.03em;margin:0}.link-btn{background:none;border:0;color:var(--blue);font-weight:800;font-size:12px;padding:4px 0}.account-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}.account{background:#fff;border:1px solid var(--line);border-radius:15px;padding:21px;box-shadow:var(--shadow)}.account-top{display:flex;justify-content:space-between;align-items:start;gap:8px}.account-icon{width:42px;height:42px;display:grid;place-items:center;border-radius:12px;background:#e8f1ff;color:#1260c2}.account-icon svg{width:21px;height:21px;stroke:currentColor;fill:none;stroke-width:1.8}.account-tag{font-size:9px;background:#e9f7f4;color:#008773;padding:5px 8px;border-radius:30px;font-weight:800}.account h3{font-size:13px;margin:15px 0 5px}.account .acct-num{font-size:11px;color:var(--muted)}.account .amount{font-size:24px;font-weight:800;margin:18px 0 3px;letter-spacing:-.05em;color:#0c346b}.account .foot{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:10px}.account .foot b{font-size:10px;color:#1669c7}.account.credit .amount{color:#94444d}
.actions{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:11px}.action-btn{background:#fff;border:1px solid var(--line);border-radius:13px;padding:17px 7px;display:flex;align-items:center;flex-direction:column;gap:9px;color:#153d7e;font-weight:800;font-size:11px;box-shadow:var(--shadow)}.action-btn:hover{background:#eef5ff;border-color:#b6d2f7}.action-icon{display:grid;place-items:center;width:39px;height:39px;border-radius:12px;background:#e8f1ff}.action-icon svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.lower-grid{display:grid;grid-template-columns:minmax(0,1.58fr) minmax(260px,.92fr);gap:17px;margin-top:26px}.panel{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:22px;min-width:0}.panel-head{display:flex;justify-content:space-between;align-items:center;gap:8px}.panel-head h2{font-size:16px;margin:0}.panel-sub{color:var(--muted);font-size:11px;margin:6px 0 0}.filter-row{display:flex;gap:7px;flex-wrap:wrap;margin:19px 0 14px}.pill{border:1px solid #e2eaf7;border-radius:22px;padding:7px 13px;font-weight:700;font-size:11px;background:#fff;color:#67809f}.pill.selected{background:#e8f1ff;color:#0756ba;border-color:#afcff8}.tx-list{display:grid;gap:0}.tx{display:flex;align-items:center;gap:13px;padding:13px 1px;border-top:1px solid #f0f3f9}.tx-badge{flex:0 0 37px;width:37px;height:37px;border-radius:12px;display:grid;place-items:center;background:#ecf2fd;color:#2161b1;font-size:17px}.tx-badge.credit{background:#e9f7f2;color:#07856e}.tx-name{font-size:12px;font-weight:800}.tx-date{font-size:10px;color:var(--muted);margin-top:4px}.tx-amount{margin-left:auto;font-size:12px;font-weight:800;white-space:nowrap}.tx-amount.positive{color:var(--green)}.empty{font-size:12px;color:var(--muted);padding:25px 0}
.insights-summary{margin:24px 0 17px;display:flex;justify-content:space-between;align-items:end}.insights-summary strong{font-size:25px;letter-spacing:-.05em}.insights-summary span{font-size:11px;color:var(--muted)}.bar-chart{display:flex;align-items:end;gap:12px;height:143px;padding-bottom:22px;border-bottom:1px solid #dce4f1}.month-col{flex:1;display:flex;align-items:center;justify-content:flex-end;flex-direction:column;height:100%;position:relative;gap:4px}.bar{width:100%;max-width:35px;min-height:6px;background:#c8dafa;border-radius:6px 6px 1px 1px}.month-col:last-child .bar{background:#0d62c7}.month-label{position:absolute;bottom:-20px;font-size:10px;color:var(--muted)}.insight-tip{display:flex;gap:11px;padding:14px;background:#fff8e4;border-radius:11px;margin-top:33px;color:#6c540e;font-size:11px;line-height:1.5}.insight-tip b{display:block;margin-bottom:3px}
.info-card{background:#eaf2ff;border:1px solid #d7e6fc;border-radius:13px;padding:17px;font-size:12px;line-height:1.7;color:#2b568d}.info-card strong{color:#074789}.data-table{width:100%;border-collapse:collapse;margin-top:14px}.data-table th{text-align:left;color:#7389a6;font-size:10px;text-transform:uppercase;letter-spacing:.06em;padding:13px 8px;border-bottom:1px solid #eaf0f9}.data-table td{border-bottom:1px solid #f0f3f9;padding:13px 8px;font-size:12px}.data-table td:last-child,.data-table th:last-child{text-align:right}.wide-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}.large-cta{background:#0a51ad;border:0;border-radius:10px;color:#fff;font-weight:800;padding:12px 17px;margin-top:14px}.illustrative{background:#e9f6f2;color:#0b8068;border-radius:30px;font-size:10px;font-weight:800;padding:5px 9px}.settings-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:15px}.outline-btn{border:1px solid #adc6e6;background:#fff;color:#0a4d9d;padding:11px 14px;border-radius:9px;font-weight:800}
.modal-backdrop,.login-backdrop{position:fixed;inset:0;z-index:100;background:rgba(4,24,57,.58);display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(3px)}.modal,.login-card{background:#fff;width:min(465px,100%);border-radius:19px;box-shadow:0 30px 90px #001f4c60;padding:28px;max-height:90vh;overflow:auto}.modal-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}.modal-head h2{margin:0;font-size:22px;letter-spacing:-.04em}.close{border:0;background:#eef4fc;color:#245795;font-size:20px;border-radius:8px;width:31px;height:31px}.modal-intro{color:var(--muted);font-size:12px;line-height:1.5;margin-bottom:22px}.field{display:grid;gap:7px;margin:15px 0}.field label{color:#415c80;font-weight:800;font-size:11px}.field input,.field select{border:1px solid #d9e4f2;border-radius:9px;background:#f9fbff;color:var(--ink);padding:12px;width:100%}.fine{font-size:11px;color:#7b8fa8;line-height:1.6}.submit{width:100%;margin-top:10px;border:0;background:#0a57b5;color:#fff;border-radius:10px;padding:13px 16px;font-weight:800}.submit:hover,.large-cta:hover{background:#003f8a}.modal-error{min-height:16px;color:#b62638;font-size:11px;font-weight:700}.login-backdrop{z-index:120;background:linear-gradient(125deg,#052f73ed,#0a65bbdd);backdrop-filter:none}.login-card{text-align:left;max-width:450px;padding:37px}.login-logo{display:flex;align-items:center;gap:9px;font-size:21px;font-weight:900;color:#0c4d9c;margin-bottom:33px}.login-logo span{background:#ffca32;color:#073b91;width:39px;height:39px;display:grid;place-items:center;border-radius:10px}.login-card h1{font-size:29px;letter-spacing:-.05em;margin:0 0 8px}.login-card p{font-size:13px;color:var(--muted);line-height:1.7}.demo-account{border:1px solid #d9e8fa;background:#f4f8ff;border-radius:12px;padding:14px;margin-top:20px;display:flex;align-items:center;gap:12px}.demo-account b{font-size:12px}.demo-account small{color:var(--muted);display:block;margin-top:5px}.demo-disclaimer{margin:23px 0 0;padding:12px;border-left:3px solid var(--yellow);font-size:11px;line-height:1.5;background:#fff8e9;color:#795a14}.toast{position:fixed;z-index:180;bottom:24px;right:24px;max-width:380px;background:#0d477d;color:#fff;box-shadow:0 9px 32px #102a5244;border-radius:11px;padding:13px 18px;font-size:12px;font-weight:700;line-height:1.5;display:none}.toast.show{display:block}.mobile-menu{display:none}.footer{text-align:center;color:#8b9bb0;font-size:10px;margin-top:26px}
@media(max-width:1150px){.sidebar{width:215px}.shell{grid-template-columns:215px minmax(0,1fr)}.main{padding:25px}.topbar{padding:0 25px}.hero{padding:27px}.bank-card{flex-basis:194px;height:120px}.account .amount{font-size:21px}.lower-grid{grid-template-columns:1.3fr .85fr}}
@media(max-width:900px){.shell{display:block}.sidebar{padding:15px 16px;gap:10px;position:sticky;top:31px;z-index:35}.logo{padding:0 3px}.side-bottom{display:none}.nav{display:flex;gap:6px;overflow-x:auto;white-space:nowrap;padding:4px 0}.nav-btn{width:auto;padding:9px 12px}.nav-btn.active{border-left:0;border-bottom:3px solid var(--yellow);padding:9px 12px 6px}.sidebar{gap:10px}.topbar{height:65px}.lower-grid{grid-template-columns:1fr 1fr}.search{display:none}.account-grid{gap:10px}}
@media(max-width:650px){.demo-ribbon{font-size:9px}.main{padding:20px 15px 40px}.topbar{padding:0 15px}.profile{display:none}.hero{padding:25px 22px;min-height:205px}.hero h1{font-size:31px}.bank-card{display:none}.account-grid{grid-template-columns:1fr;gap:10px}.account{padding:17px}.account .amount{margin:10px 0 4px}.actions{grid-template-columns:repeat(3,1fr);gap:8px}.lower-grid,.wide-grid{grid-template-columns:1fr}.panel{padding:17px}.page-title{font-size:24px}.search{display:none}.section-head{margin-top:23px}.action-btn{padding:14px 5px}.nav-label{font-size:11px}}
</style>
</head>
<body>
<div class="demo-ribbon">★ EDUCATIONAL DEMO — FICTIONAL BANK · NO REAL ACCOUNTS, CREDENTIALS OR PAYMENTS</div>
<div class="shell">
<aside class="sidebar" aria-label="Main menu">
  <div class="logo"><div class="logo-mark">✦</div><div class="logo-words"><strong>Northstar</strong><span>DEMO BANK</span></div></div>
  <div>
    <p class="nav-title">PERSONAL BANKING</p>
    <nav class="nav" id="sidebarNav">
      <button class="nav-btn active" data-route="overview"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg><span class="nav-label">Overview</span></button>
      <button class="nav-btn" data-route="accounts"><svg viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="15" rx="2"/><path d="M2 10h20"/></svg><span class="nav-label">My accounts</span></button>
      <button class="nav-btn" data-route="payments"><svg viewBox="0 0 24 24"><path d="m4 12 7-7 9 9-7 7z"/><path d="M14 4h7v7"/></svg><span class="nav-label">Payments & transfers</span></button>
      <button class="nav-btn" data-route="activity"><svg viewBox="0 0 24 24"><path d="M4 4v16h16"/><path d="m6 14 5-5 3 3 6-6"/></svg><span class="nav-label">Transaction history</span></button>
      <button class="nav-btn" data-route="insights"><svg viewBox="0 0 24 24"><path d="M4 20V9m6 11V4m6 16v-8m5 8v-5"/></svg><span class="nav-label">Insights</span></button>
      <button class="nav-btn" data-route="settings"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><span class="nav-label">Demo settings</span></button>
    </nav>
  </div>
  <div class="side-bottom"><h4>Designed for AWS Fargate</h4><p>One Python file. No external dependencies. No real financial data.</p><button id="sidebarReset">Reset demo balances</button></div>
</aside>
<div class="content">
<header class="topbar"><div><div class="crumb">Personal banking</div><strong id="currentPage">Overview</strong></div><div class="top-right"><label class="search" aria-label="Search transactions"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="topSearch" placeholder="Search transactions..."/></label><div class="profile">Alex Morgan<small>Demo customer</small></div><div class="avatar">AM</div></div></header>
<main class="main">
<section class="view active" data-view="overview">
  <p class="eyebrow">Your banking, simplified</p><p class="page-desc" id="greeting">Welcome back, Alex. Here's your financial overview.</p>
  <div class="hero"><div class="hero-content"><div class="balance-label">TOTAL CASH BALANCE · CAD</div><h1 id="heroTotal">$44,386.00</h1><div class="muted">Across your chequing and savings accounts</div><div class="hero-note"><b>★</b> A brighter way to manage your money. <span style="opacity:.8">• Simulated data</span></div></div><div class="bank-card" aria-label="Decorative fictional card"><small>✦ NORTHSTAR DEMO BANK</small><div class="chip"></div><div class="card-num">•••• &nbsp; •••• &nbsp; •••• &nbsp; 9081</div><div class="card-foot"><span>ALEX MORGAN</span><span>DEMO</span></div></div></div>
  <div class="section-head"><h2>Your accounts</h2><button class="link-btn" data-open-view="accounts">View all accounts →</button></div><div class="account-grid" id="overviewAccounts"></div>
  <div class="section-head"><h2>Quick actions</h2><span class="illustrative">Simulation mode</span></div><div class="actions" id="quickActions"></div>
  <div class="lower-grid"><div class="panel"><div class="panel-head"><div><h2>Recent activity</h2><p class="panel-sub">Your latest simulated transactions</p></div><button class="link-btn" data-open-view="activity">See all →</button></div><div class="tx-list" id="recentList"></div></div><div class="panel"><div class="panel-head"><div><h2>Spending snapshot</h2><p class="panel-sub">Illustrative monthly activity</p></div><span class="illustrative">Demo data</span></div><div class="insights-summary"><div><span>Monthly spending</span><br/><strong id="spendingTotal">$0.00</strong></div><span>CAD</span></div><div class="bar-chart" id="barChart"></div><div class="insight-tip"><span style="font-size:18px">✦</span><div><b>A little insight goes a long way</b>Keep track of your spending as you explore this demonstration.</div></div></div></div>
</section>
<section class="view" data-view="accounts"><p class="eyebrow">Banking accounts</p><h1 class="page-title">Everything in one place.</h1><p class="page-desc">Explore your sample balances, chequing, savings and credit card.</p><div class="account-grid" id="allAccounts"></div><div class="section-head"><h2>Account management</h2></div><div class="wide-grid"><div class="panel"><h2>Move money between accounts</h2><p class="page-desc">Transfer funds between your two demo deposit accounts.</p><button class="large-cta" data-action="transfer">Make a transfer</button></div><div class="info-card"><strong>About these balances</strong><div>This demo stores fictional account information in your browser only. Balances are not connected to a bank and do not represent real money.</div></div></div></section>
<section class="view" data-view="payments"><p class="eyebrow">Payment centre</p><h1 class="page-title">Pay and transfer with confidence.</h1><p class="page-desc">Practice banking flows with entirely simulated payments.</p><div class="actions" id="paymentActions"></div><div class="section-head"><h2>How this demo works</h2></div><div class="info-card"><strong>No money moves in or out.</strong><div>Deposits, withdrawals, transfers, bill payments and send-money actions modify your sample browser balances and transaction list. No payment network or external service is called.</div></div></section>
<section class="view" data-view="activity"><p class="eyebrow">Account activity</p><h1 class="page-title">Your transaction history.</h1><p class="page-desc">Review, filter and search your demonstration transactions.</p><div class="panel"><div class="filter-row" id="activityFilters"></div><div style="overflow:auto"><table class="data-table"><thead><tr><th>Transaction</th><th>Account</th><th>Date</th><th>Type</th><th>Amount</th></tr></thead><tbody id="activityRows"></tbody></table></div><p class="empty hidden" id="noActivity">No transactions match your search.</p></div></section>
<section class="view" data-view="insights"><p class="eyebrow">Financial wellness</p><h1 class="page-title">Understand your money.</h1><p class="page-desc">Sample charts to show how account insights can look.</p><div class="wide-grid"><div class="panel"><div class="panel-head"><h2>Spending by category</h2><span class="illustrative">Illustrative</span></div><div id="categoryBreakdown"></div></div><div class="panel"><h2>Available cash</h2><p class="page-desc">Current simulated combined cash balances</p><div style="font-size:34px;font-weight:850;color:#0c4a9c;letter-spacing:-.05em" id="insightsTotal">$0.00</div><div class="info-card" style="margin-top:24px"><strong>Keep it simple</strong><div>Your demo spending categories are calculated from local transactions. These are not financial recommendations.</div></div></div></div></section>
<section class="view" data-view="settings"><p class="eyebrow">Learning environment</p><h1 class="page-title">Demo settings</h1><p class="page-desc">Manage your fictional banking session.</p><div class="panel"><h2>Reset sample account data</h2><p class="page-desc">Return all demonstration balances and transaction activity to their original values.</p><div class="settings-actions"><button class="large-cta" id="resetButton">Reset balances and history</button><button class="outline-btn" id="signOutButton">Exit demo session</button></div></div><div class="section-head"><h2>Important notice</h2></div><div class="info-card"><strong>Not affiliated with RBC or any financial institution.</strong><div>Northstar Demo Bank is a fictional interface for an AWS container training project. It intentionally does not collect real credentials, store customer details on a backend, process real payments, or provide production banking security. Deploy this training demo to a restricted lab environment only.</div></div></section>
<footer class="footer">© Northstar Demo Bank — Fictional educational interface · AWS ECS Fargate classroom project · Not affiliated with any real bank</footer>
</main>
</div>
</div>
<div class="modal-backdrop hidden" id="modalBackdrop" role="presentation"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle"><div class="modal-head"><h2 id="modalTitle">New transaction</h2><button class="close" id="modalClose" aria-label="Close">×</button></div><div class="modal-intro" id="modalIntro"></div><form id="transactionForm"><div id="formFields"></div><div class="modal-error" id="formError" role="alert"></div><button type="submit" class="submit" id="formSubmit">Confirm demo transaction</button><p class="fine">Demo only — no actual financial transaction will occur.</p></form></div></div>
<div class="login-backdrop" id="loginBackdrop"><div class="login-card"><div class="login-logo"><span>✦</span> Northstar <b style="font-size:10px;background:#fff1bd;padding:5px 7px;border-radius:20px">DEMO</b></div><div class="eyebrow">Welcome to personal banking</div><h1>Good to see you again.</h1><p>Explore a modern Canadian banking dashboard powered by a Python container running on AWS Fargate.</p><div class="demo-account"><div class="avatar">AM</div><div><b>Alex Morgan</b><small>Sample customer • No password required</small></div></div><button class="submit" id="demoLogin">Continue to demo banking →</button><div class="demo-disclaimer">Training environment only. Do not enter real bank credentials or financial details. This is not an RBC website.</div></div></div>
<div class="toast" id="toast" aria-live="polite"></div>
<script>
(()=>{
'use strict';
const STORAGE='northstar-bank-sample-v1';
const money=c=>new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD'}).format(c/100);
const today=()=>new Date().toISOString().slice(0,10);
const icon=(name)=>({deposit:'↙',withdraw:'↗',transfer:'↔',send:'✦',bill:'▣',card:'▤',income:'↙',purchase:'▣'}[name]||'◈');
const defaultState=()=>({accounts:[{id:'chequing',name:'Everyday Chequing',number:'•••• 9081',cents:1284572,kind:'chequing'},{id:'savings',name:'High Interest Savings',number:'•••• 4412',cents:3154028,kind:'savings'},{id:'credit',name:'Rewards Credit Card',number:'•••• 0096',cents:-128550,kind:'credit'}],transactions:[
{id:'s1',name:'Direct deposit · Pay',account:'chequing',type:'deposit',amount:420000,date:'2026-11-15',category:'Income'},
{id:'s2',name:'Fresh Market Groceries',account:'chequing',type:'purchase',amount:-12564,date:'2026-11-14',category:'Groceries'},
{id:'s3',name:'Transfer to savings',account:'chequing',type:'transfer',amount:-80000,date:'2026-11-13',category:'Transfers'},
{id:'s4',name:'Coffee & Co.',account:'chequing',type:'purchase',amount:-780,date:'2026-11-12',category:'Dining'},
{id:'s5',name:'Hydro One · Bill payment',account:'chequing',type:'bill',amount:-15620,date:'2026-11-11',category:'Bills'},
{id:'s6',name:'City Transit Pass',account:'chequing',type:'purchase',amount:-4500,date:'2026-11-10',category:'Transport'},
{id:'s7',name:'Savings interest',account:'savings',type:'deposit',amount:2150,date:'2026-11-09',category:'Income'},
{id:'s8',name:'Restaurant · Dinner',account:'chequing',type:'purchase',amount:-6640,date:'2026-11-08',category:'Dining'}]});
function load(){try{const saved=JSON.parse(localStorage.getItem(STORAGE));if(saved&&Array.isArray(saved.accounts)&&Array.isArray(saved.transactions)&&saved.accounts.length===3)return saved;}catch(e){}return defaultState();}
let state=load(),currentView='overview',filter='all',query='',action=null;
const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s));
function save(){localStorage.setItem(STORAGE,JSON.stringify(state));}
function acc(id){return state.accounts.find(x=>x.id===id);}
function cash(){return acc('chequing').cents+acc('savings').cents;}
function label(id){const a=acc(id);return a?a.name:id;}
function safe(s){return String(s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function dateDisplay(s){const d=new Date(s+'T12:00:00');return d.toLocaleDateString('en-CA',{month:'short',day:'numeric',year:'numeric'});}
function accountCard(a){return `<div class="account ${a.kind==='credit'?'credit':''}"><div class="account-top"><div class="account-icon"><svg viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="15" rx="2"/><path d="M2 10h20"/></svg></div><span class="account-tag">${a.kind==='credit'?'CREDIT':'ACTIVE'}</span></div><h3>${a.name}</h3><div class="acct-num">${a.number}</div><div class="amount">${money(a.cents)}</div><div class="foot"><span>${a.kind==='credit'?'Outstanding balance':'Available balance'}</span><b>CAD</b></div></div>`;}
function displayTx(tx){const positive=tx.amount>=0;return `<div class="tx"><div class="tx-badge ${positive?'credit':''}">${icon(tx.type)}</div><div><div class="tx-name">${safe(tx.name)}</div><div class="tx-date">${dateDisplay(tx.date)} · ${label(tx.account)}</div></div><span class="tx-amount ${positive?'positive':''}">${positive?'+':'−'}${money(Math.abs(tx.amount))}</span></div>`;}
const actions=[['send','Send money'],['transfer','Transfer'],['deposit','Deposit'],['withdraw','Withdraw'],['bill','Pay a bill']];
function renderActions(){const html=actions.map(([id,l])=>`<button class="action-btn" data-action="${id}"><span class="action-icon">${icon(id)}</span>${l}</button>`).join('');$('#quickActions').innerHTML=html;$('#paymentActions').innerHTML=html;}
function renderAccounts(){$('#overviewAccounts').innerHTML=state.accounts.map(accountCard).join('');$('#allAccounts').innerHTML=state.accounts.map(accountCard).join('');$('#heroTotal').textContent=money(cash());$('#insightsTotal').textContent=money(cash());}
function renderRecent(){const txs=state.transactions.slice(0,5);$('#recentList').innerHTML=txs.map(displayTx).join('')||'<p class="empty">No transactions yet.</p>';}
function spend(){return state.transactions.filter(t=>t.amount<0&&!['transfer','withdraw'].includes(t.type)).reduce((a,t)=>a-Math.min(0,t.amount),0);}
function renderInsights(){$('#spendingTotal').textContent=money(spend());const months=['Jun','Jul','Aug','Sep','Oct','Nov'],heights=[53,72,46,86,62,75];$('#barChart').innerHTML=months.map((m,i)=>`<div class="month-col"><div class="bar" style="height:${heights[i]}%"></div><span class="month-label">${m}</span></div>`).join('');const totals={};for(const t of state.transactions){if(t.amount<0&&!['transfer','withdraw'].includes(t.type)){totals[t.category]=(totals[t.category]||0)-t.amount;}}const entries=Object.entries(totals).sort((a,b)=>b[1]-a[1]);const max=entries.length?entries[0][1]:1;$('#categoryBreakdown').innerHTML=entries.map(([n,v])=>`<div style="margin-top:20px"><div style="display:flex;justify-content:space-between;font-weight:750;font-size:12px;margin-bottom:9px"><span>${safe(n)}</span><span>${money(v)}</span></div><div style="height:9px;background:#ebf1fa;border-radius:7px;overflow:hidden"><div style="width:${Math.max(5,Math.round(v/max*100))}%;height:100%;background:linear-gradient(90deg,#075bc6,#42a9de);border-radius:7px"></div></div></div>`).join('')||'<p class="empty">No spending activity yet.</p>';}
function matches(tx){const q=query.toLowerCase();return(filter==='all'||filter==='in'&&tx.amount>0||filter==='out'&&tx.amount<0)&&(!q||(tx.name+' '+tx.type+' '+tx.category+' '+label(tx.account)).toLowerCase().includes(q));}
function renderHistory(){const buttons=[['all','All activity'],['in','Money in'],['out','Money out']];$('#activityFilters').innerHTML=buttons.map(([k,v])=>`<button class="pill ${filter===k?'selected':''}" data-filter="${k}">${v}</button>`).join('');const tx=state.transactions.filter(matches);$('#activityRows').innerHTML=tx.map(t=>`<tr><td><b>${safe(t.name)}</b></td><td>${safe(label(t.account))}</td><td>${dateDisplay(t.date)}</td><td>${safe(t.type)}</td><td style="font-weight:800;color:${t.amount>=0?'#07856e':'#17335c'}">${t.amount>=0?'+':'−'}${money(Math.abs(t.amount))}</td></tr>`).join('');$('#noActivity').classList.toggle('hidden',tx.length>0);}
function render(){renderAccounts();renderRecent();renderInsights();renderHistory();}
const titles={overview:'Overview',accounts:'My accounts',payments:'Payments & transfers',activity:'Transaction history',insights:'Insights',settings:'Demo settings'};
function showView(view){if(!titles[view])return;currentView=view;$$('[data-view]').forEach(x=>x.classList.toggle('active',x.dataset.view===view));$$('[data-route]').forEach(x=>x.classList.toggle('active',x.dataset.route===view));$('#currentPage').textContent=titles[view];window.scrollTo({top:0,behavior:'smooth'});if(view==='activity')renderHistory();}
const field=(key,label,inner)=>`<div class="field"><label for="f-${key}">${label}</label>${inner}</div>`;
const select=(key,options)=>`<select id="f-${key}" name="${key}" required>${options.map(([v,t])=>`<option value="${v}">${safe(t)}</option>`).join('')}</select>`;
const amountInput=()=>field('amount','Amount (CAD)',`<input id="f-amount" name="amount" type="number" min="0.01" max="100000" step="0.01" inputmode="decimal" placeholder="0.00" required/>`);
const acctOptions=()=>state.accounts.filter(a=>a.kind!=='credit').map(a=>[a.id,`${a.name} · ${money(a.cents)}`]);
function openModal(which){action=which;const conf={deposit:['Add a demo deposit','Credit an account with simulated funds.'],withdraw:['Make a demo withdrawal','Reduce a sample balance without moving real money.'],transfer:['Transfer between accounts','Move simulated funds between chequing and savings.'],send:['Send a demo transfer','Send fictional money to a sample recipient.'],bill:['Pay a demo bill','Practice paying a sample payee.']}[which];if(!conf)return;$('#modalTitle').textContent=conf[0];$('#modalIntro').textContent=conf[1];$('#formError').textContent='';const options=acctOptions();let content='';if(which==='deposit'||which==='withdraw'){content=field('account',which==='deposit'?'Deposit to':'Withdraw from',select('account',options))+amountInput();}
if(which==='transfer'){content=field('from','From account',select('from',options))+field('to','To account',select('to',[...options].reverse()))+amountInput();}
if(which==='send'){content=field('from','From account',select('from',options))+field('recipient','Recipient (fictional)',select('recipient',[['Taylor Smith','Taylor Smith'],['Jamie Lee','Jamie Lee'],['Casey Brown','Casey Brown']]))+amountInput();}
if(which==='bill'){content=field('from','Pay from account',select('from',options))+field('payee','Demo biller',select('payee',[['Electricity','Electricity utility'],['Internet','Internet provider'],['Phone','Mobile phone provider'],['Property','Property services']]))+amountInput();}
$('#formFields').innerHTML=content;$('#modalBackdrop').classList.remove('hidden');setTimeout(()=>$('#f-amount')?.focus(),10);}
function closeModal(){$('#modalBackdrop').classList.add('hidden');action=null;}
function toast(msg){const box=$('#toast');box.textContent=msg;box.classList.add('show');clearTimeout(window._toastTimeout);window._toastTimeout=setTimeout(()=>box.classList.remove('show'),3800);}
function submitTransaction(event){event.preventDefault();const data=new FormData(event.currentTarget);const raw=String(data.get('amount')||'').trim();if(!/^\d+(?:\.\d{1,2})?$/.test(raw)){return $('#formError').textContent='Enter a valid amount with up to 2 decimal places.';}const cents=Math.round(Number(raw)*100);if(!Number.isSafeInteger(cents)||cents<1||cents>10000000)return $('#formError').textContent='Enter an amount from $0.01 to $100,000.00.';
let from=data.get('from')||data.get('account'),to=data.get('to')||data.get('account');if(action==='transfer'&&from===to)return $('#formError').textContent='Choose two different accounts.';
if(action!=='deposit'&&(!acc(from)||acc(from).cents<cents))return $('#formError').textContent='Insufficient demo funds in the selected account.';
const tx={id:'t'+Date.now(),name:'',account:from,type:action,amount:-cents,date:today(),category:'Transfers'};
if(action==='deposit'){acc(to).cents+=cents;tx.name='Demo deposit';tx.amount=cents;tx.account=to;tx.category='Income';}
if(action==='withdraw'){acc(from).cents-=cents;tx.name='Demo cash withdrawal';tx.category='Cash';}
if(action==='transfer'){acc(from).cents-=cents;acc(to).cents+=cents;tx.name='Transfer to '+label(to);tx.category='Transfers';state.transactions.unshift({...tx,id:tx.id+'r',name:'Transfer from '+label(from),account:to,amount:cents});}
if(action==='send'){acc(from).cents-=cents;tx.name='Demo send to '+String(data.get('recipient'));tx.category='Transfers';}
if(action==='bill'){acc(from).cents-=cents;tx.name=String(data.get('payee'))+' · Demo bill payment';tx.category='Bills';}
state.transactions.unshift(tx);save();render();closeModal();toast('✓ '+money(cents)+' simulated successfully. No real money moved.');}
function reset(){if(!confirm('Reset all fictional balances and transactions to the starting demo values?'))return;state=defaultState();save();render();toast('Demo accounts have been reset.');}
document.addEventListener('click',e=>{const nav=e.target.closest('[data-route]');if(nav)showView(nav.dataset.route);const view=e.target.closest('[data-open-view]');if(view)showView(view.dataset.openView);const act=e.target.closest('[data-action]');if(act)openModal(act.dataset.action);const fil=e.target.closest('[data-filter]');if(fil){filter=fil.dataset.filter;renderHistory();}});
$('#modalClose').addEventListener('click',closeModal);$('#modalBackdrop').addEventListener('click',e=>{if(e.target.id==='modalBackdrop')closeModal();});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});$('#transactionForm').addEventListener('submit',submitTransaction);
$('#sidebarReset').addEventListener('click',reset);$('#resetButton').addEventListener('click',reset);
$('#topSearch').addEventListener('input',e=>{query=e.target.value;showView('activity');renderHistory();});
$('#demoLogin').addEventListener('click',()=>{sessionStorage.setItem('northstar-demo-session','yes');$('#loginBackdrop').classList.add('hidden');toast('Welcome to Northstar Demo Bank, Alex.');});
$('#signOutButton').addEventListener('click',()=>{sessionStorage.removeItem('northstar-demo-session');$('#loginBackdrop').classList.remove('hidden');showView('overview');});
if(sessionStorage.getItem('northstar-demo-session')==='yes')$('#loginBackdrop').classList.add('hidden');
const hour=new Date().getHours();$('#greeting').textContent=`Good ${hour<12?'morning':hour<17?'afternoon':'evening'}, Alex. Here's your financial overview.`;
renderActions();render();
})();
</script>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        route = urlsplit(self.path).path
        if route in ("/", "/index.html"):
            return self.respond(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        if route == "/health":
            return self.respond_json(200, {"status": "ok", "app": "northstar-demo-bank"})
        if route == "/api/hello":
            return self.respond_json(200, {
                "message": "Hello from Northstar Demo Bank on AWS ECS Fargate!",
                "hostname": socket.gethostname(),
                "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "demo_only": True,
            })
        if route == "/api/info":
            return self.respond_json(200, {
                "app": "Northstar Demo Bank",
                "type": "educational-simulation",
                "real_money": False,
                "backend_database": False,
                "container_port": PORT,
            })
        return self.respond_json(404, {"error": "Not found"})

    def do_HEAD(self) -> None:
        route = urlsplit(self.path).path
        self.send_response(200 if route in ("/", "/health", "/api/hello", "/api/info") else 404)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

    def respond_json(self, status: int, payload: dict) -> None:
        self.respond(status, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

    def respond(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Northstar Demo Bank serving on port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
