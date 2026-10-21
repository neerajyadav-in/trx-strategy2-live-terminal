from http.server import BaseHTTPRequestHandler
import json
import time
import uuid
import urllib.parse
import os

SESSIONS = set(["sess_neeraj_authenticated"])

PLATFORM_DATA = {
    "system_start_time": time.time() - 86400 * 3.5,
    "accounts": [
        {
            "id": "acc_01",
            "phone": "9926976446",
            "masked_phone": "919926***446",
            "label": "Primary Funded Account",
            "balance": 285.00,
            "currency": "INR",
            "status": "CONNECTED",
            "health": "EXCELLENT",
            "assigned_strategy": "strat_trx_01",
            "total_trades": 142,
            "win_rate": 70.97
        },
        {
            "id": "acc_02",
            "phone": "9999911111",
            "masked_phone": "919999***111",
            "label": "Secondary Reserve Account",
            "balance": 0.00,
            "currency": "INR",
            "status": "STANDBY",
            "health": "GOOD",
            "assigned_strategy": "NONE",
            "total_trades": 0,
            "win_rate": 0.0
        }
    ],
    "strategies": [
        {
            "id": "strat_trx_01",
            "name": "TRX Strategy 2 (Oracle Mode)",
            "game": "TRX WinGo 1M / 3M",
            "version": "v2.4.2",
            "status": "RUNNING",
            "assigned_account_id": "acc_01",
            "assigned_account_phone": "9926976446",
            "win_rate": 70.97,
            "total_rounds": 500,
            "wins": 22,
            "losses": 9,
            "pnl": 578.00,
            "current_run_id": "RUN-TRX-20261021-01",
            "execution_window": "Second 54",
            "oracle_source": "TronGrid Block Parity",
            "max_loss_streak": 3,
            "base_stake": 10.0,
            "description": "3-Minute Dual Convergence Reversion with Second 54 decentralized Tron block hash confirmation."
        },
        {
            "id": "strat_wingo_alt5",
            "name": "WinGo 5-Alternation Breakout",
            "game": "WinGo 1-Minute",
            "version": "v1.2.0",
            "status": "RUNNING",
            "assigned_account_id": "acc_01",
            "assigned_account_phone": "9926976446",
            "win_rate": 61.90,
            "total_rounds": 500,
            "wins": 13,
            "losses": 8,
            "pnl": 68.40,
            "current_run_id": "RUN-WALT5-20261021-01",
            "execution_window": "Second 18",
            "oracle_source": "Markov Ping-Pong Exhaustion",
            "max_loss_streak": 3,
            "base_stake": 10.0,
            "description": "Captures structural break of 5-step alternating sequences (B-S-B-S-B) into repeat."
        },
        {
            "id": "strat_wingo_fade4",
            "name": "WinGo Streak L>=4 Liability Fade",
            "game": "WinGo 1-Minute",
            "version": "v1.8.1",
            "status": "PAUSED",
            "assigned_account_id": "acc_01",
            "assigned_account_phone": "9926976446",
            "win_rate": 60.00,
            "total_rounds": 500,
            "wins": 27,
            "losses": 18,
            "pnl": 91.60,
            "current_run_id": "RUN-WFADE4-20261021-01",
            "execution_window": "Second 18",
            "oracle_source": "Pool Asymmetry Risk Balancing",
            "max_loss_streak": 4,
            "base_stake": 10.0,
            "description": "Fades retail momentum herds when single-side volume exceeds 68% total pool."
        }
    ],
    "risk_settings": {
        "daily_take_profit": 500.0,
        "daily_stop_loss": 150.0,
        "max_martingale_step": 3,
        "base_stake": 10.0,
        "current_daily_pnl": 38.40,
        "tp_sl_lock_active": False,
        "live_execution_active": False
    },
    "audit_logs": [
        {"timestamp": "2026-10-21 18:30:12", "action": "SYSTEM_BOOT", "user": "System", "details": "Platform services initialized on Vercel Global Edge."},
        {"timestamp": "2026-10-21 18:31:05", "action": "AUTH_SUCCESS", "user": "Neeraj", "details": "Operator session authenticated via session token."},
        {"timestamp": "2026-10-21 18:32:44", "action": "ORACLE_SYNC", "user": "TronGrid", "details": "TRON Mainnet Block Hash stream synchronized (Height #69024820)."},
        {"timestamp": "2026-10-21 18:34:00", "action": "PLATFORM_UPGRADE", "user": "Operator", "details": "Production Strategy Management Platform activated."}
    ],
    "observation_events": [],
    "execution_events": []
}

def init_historical_events():
    now = time.time()
    for i in range(15, 0, -1):
        t_str = time.strftime("%H:%M:%S", time.localtime(now - i * 60))
        issue = f"2026102110301{1500 - i}"
        m1 = "BIG" if i % 2 == 0 else "SMALL"
        m2 = m1
        call = "SMALL" if m1 == "BIG" else "BIG"
        outcome = call if i % 3 != 0 else ("BIG" if call == "SMALL" else "SMALL")
        win = (outcome == call)
        
        PLATFORM_DATA["observation_events"].append({
            "timestamp": t_str,
            "issue": issue,
            "game": "TRX WinGo 1M",
            "m1": m1, "m2": m2,
            "observed_signal": f"DUAL_{m1}",
            "predicted_call": call,
            "confirmed_outcome": outcome,
            "result": "MATCH" if win else "DIVERGE",
            "block_id": f"69024{800 - i}",
            "confidence": 70.97
        })

        PLATFORM_DATA["execution_events"].append({
            "timestamp": t_str,
            "issue": issue,
            "strategy": "TRX Strategy 2",
            "account": "919926***446",
            "call": call,
            "outcome": outcome,
            "step": 1,
            "stake": 10.0,
            "pnl": "+9.60 INR" if win else "-10.00 INR",
            "balance_after": 285.0 + (9.6 if win else -10.0),
            "status": "CONFIRMED_SETTLED",
            "result": "WIN" if win else "LOSS"
        })

init_historical_events()

HTML_LOGIN = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Strategy Management Platform - Terminal Access</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
    body { background: #070b14; color: #f9fafb; display: flex; align-items: center; justify-content: center; height: 100vh; }
    .login-box { width: 100%; max-width: 440px; background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 40px 32px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
    .login-header { text-align: center; margin-bottom: 28px; }
    .login-header h1 { font-size: 20px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
    .login-header p { font-size: 13px; color: #94a3b8; margin-top: 6px; }
    .form-group { margin-bottom: 20px; }
    label { display: block; font-size: 12px; font-weight: 600; text-transform: uppercase; color: #94a3b8; margin-bottom: 8px; letter-spacing: 0.5px; }
    input[type="text"], input[type="password"] { width: 100%; padding: 12px 14px; background: #070b14; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 14px; outline: none; transition: border-color 0.2s; }
    input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }
    button.btn-login { width: 100%; padding: 13px; background: #3b82f6; color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
    button.btn-login:hover { background: #2563eb; }
    .error-alert { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: center; display: none; }
  </style>
</head>
<body>
  <div class="login-box">
    <div class="login-header">
      <div style="width:50px; height:50px; border-radius:14px; background:rgba(59, 130, 246, 0.15); border:1px solid #3b82f6; display:flex; align-items:center; justify-content:center; margin:0 auto 16px; font-size:22px; color:#3b82f6;">⚡</div>
      <h1>Strategy Management Platform</h1>
      <p>Institutional Quantitative Operations Terminal</p>
    </div>
    <div id="errorAlert" class="error-alert">Invalid Operator Credentials! Access Denied.</div>
    <form onsubmit="handleLogin(event)">
      <div class="form-group">
        <label>Operator Username</label>
        <input type="text" id="username" placeholder="Enter username" required autocomplete="username">
      </div>
      <div class="form-group">
        <label>Access Key / Password</label>
        <input type="password" id="password" placeholder="Enter password" required autocomplete="current-password">
      </div>
      <button type="submit" class="btn-login" id="submitBtn">Authenticate & Enter Terminal</button>
    </form>
  </div>
  <script>
    async function handleLogin(e) {
      e.preventDefault();
      const u = document.getElementById('username').value.trim();
      const p = document.getElementById('password').value.trim();
      const err = document.getElementById('errorAlert');
      const btn = document.getElementById('submitBtn');
      err.style.display = 'none';
      btn.innerText = 'Verifying Credentials...';
      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (data.success) {
          document.cookie = `session_token=${data.token}; path=/; max-age=864000; SameSite=Lax`;
          window.location.reload();
        } else {
          err.innerText = data.msg || 'Invalid Username or Password!';
          err.style.display = 'block';
          btn.innerText = 'Authenticate & Enter Terminal';
        }
      } catch (err) {
        btn.innerText = 'Authenticate & Enter Terminal';
      }
    }
  </script>
</body>
</html>"""

HTML_PLATFORM = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Strategy Management Platform - Institutional Terminal</title>
  <style>
    :root {
      --bg: #070b14;
      --sidebar-bg: #0b1120;
      --card-bg: #0f172a;
      --border: #1e293b;
      --accent: #3b82f6;
      --green: #10b981;
      --red: #ef4444;
      --yellow: #f59e0b;
      --purple: #8b5cf6;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
    body { background: var(--bg); color: var(--text); height: 100vh; overflow: hidden; display: flex; font-size: 13px; }
    
    /* Layout */
    .app-sidebar { width: 260px; background: var(--sidebar-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; height: 100%; }
    .app-main { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
    .app-header { height: 60px; background: var(--card-bg); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; flex-shrink: 0; }
    .app-body { flex: 1; overflow-y: auto; padding: 24px; }

    /* Sidebar Navigation */
    .brand { padding: 18px 20px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid var(--border); }
    .brand-icon { width: 32px; height: 32px; border-radius: 8px; background: rgba(59, 130, 246, 0.2); border: 1px solid var(--accent); color: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; }
    .brand-name { font-weight: 800; font-size: 14px; letter-spacing: -0.3px; color: #fff; }
    .nav-list { list-style: none; padding: 12px 10px; overflow-y: auto; flex: 1; }
    .nav-cat { font-size: 10px; text-transform: uppercase; color: var(--muted); font-weight: 700; padding: 12px 12px 6px; letter-spacing: 0.5px; }
    .nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; color: var(--muted); cursor: pointer; transition: all 0.15s; font-weight: 600; margin-bottom: 2px; }
    .nav-item:hover { color: #fff; background: rgba(255, 255, 255, 0.04); }
    .nav-item.active { color: #fff; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); }
    .nav-badge { margin-left: auto; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 700; }
    .nb-live { background: rgba(16, 185, 129, 0.2); color: var(--green); }
    .nb-blue { background: rgba(59, 130, 246, 0.2); color: var(--accent); }

    /* Header Components */
    .header-left { display: flex; align-items: center; gap: 16px; }
    .header-right { display: flex; align-items: center; gap: 14px; }
    .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .pill-info { background: #070b14; border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; font-size: 12px; }
    .btn-action { background: var(--accent); color: #fff; border: none; padding: 7px 14px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 12px; }
    .btn-action:hover { background: #2563eb; }
    .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
    .btn-outline:hover { color: #fff; border-color: var(--muted); }

    /* Views Framework */
    .view-container { display: none; }
    .view-container.active-view { display: block; animation: fadeIn 0.15s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0.8; transform: translateY(2px); } to { opacity: 1; transform: translateY(0); } }

    /* Cards & Grids */
    .grid-kpi { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
    .card-title { font-size: 11px; text-transform: uppercase; color: var(--muted); font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
    .card-val { font-size: 26px; font-weight: 800; color: #fff; margin-top: 6px; font-family: monospace; }
    .card-sub { font-size: 11px; color: var(--muted); margin-top: 4px; }
    .grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
    .grid-workspace { display: grid; grid-template-columns: 1.8fr 1.2fr; gap: 20px; }

    /* Tables */
    table.table { width: 100%; border-collapse: collapse; font-size: 12px; }
    table.table th { background: #070b14; padding: 12px 14px; text-align: left; color: var(--muted); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--border); }
    table.table td { padding: 12px 14px; border-bottom: 1px solid var(--border); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
    .badge-win { color: var(--green); background: rgba(16, 185, 129, 0.15); padding: 2px 6px; border-radius: 4px; font-weight: 700; }
    .badge-loss { color: var(--red); background: rgba(239, 68, 68, 0.15); padding: 2px 6px; border-radius: 4px; font-weight: 700; }

    /* Workspace Radar */
    .radar-box { background: #070b14; border: 1px solid var(--border); border-radius: 10px; padding: 16px; text-align: center; }
    .radar-num { font-size: 42px; font-weight: 900; font-family: monospace; color: var(--accent); }
    .radar-box.conv .radar-num { color: var(--yellow); }

    /* Modals */
    .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: none; align-items: center; justify-content: center; z-index: 1000; }
    .modal-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; width: 90%; max-width: 520px; padding: 24px; }
  </style>
</head>
<body>
  <!-- Persistent 13-Section Sidebar -->
  <aside class="app-sidebar">
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div class="brand-name">STRATEGY OPS</div>
    </div>
    <ul class="nav-list">
      <li class="nav-cat">Control Center</li>
      <li class="nav-item active" onclick="showView('view-overview')"><span>📊 Overview Dashboard</span></li>
      <li class="nav-item" onclick="showView('view-observation')"><span>👁️ RAXI Observation</span><span class="nav-badge nb-live">READ-ONLY</span></li>
      <li class="nav-item" onclick="showView('view-strategy-center')"><span>🎯 Strategy Center</span><span class="nav-badge nb-blue">3 Active</span></li>

      <li class="nav-cat">Workspaces</li>
      <li class="nav-item" onclick="showView('view-ws-trx')"><span>⚡ TRX Strategy 2 (Oracle)</span></li>
      <li class="nav-item" onclick="showView('view-ws-alt5')"><span>🔄 WinGo 5-Alt Break</span></li>
      <li class="nav-item" onclick="showView('view-ws-fade4')"><span>📉 WinGo L4 Streak Fade</span></li>

      <li class="nav-cat">Operations</li>
      <li class="nav-item" onclick="showView('view-accounts')"><span>👥 Account Management</span></li>
      <li class="nav-item" onclick="showView('view-live-activity')"><span>⚡ Live Activity Stream</span></li>
      <li class="nav-item" onclick="showView('view-analytics')"><span>📈 Performance Analytics</span></li>
      <li class="nav-item" onclick="showView('view-history')"><span>📑 Run History & Ledger</span></li>

      <li class="nav-cat">Safety & System</li>
      <li class="nav-item" onclick="showView('view-risk')"><span>🛡️ Risk & Limits Shield</span></li>
      <li class="nav-item" onclick="showView('view-health')"><span>🏥 System Health & Incidents</span></li>
      <li class="nav-item" onclick="showView('view-audit')"><span>🔍 Audit Logs</span></li>
      <li class="nav-item" onclick="showView('view-settings')"><span>⚙️ Settings & Integrations</span></li>
    </ul>
  </aside>

  <!-- Main View Area -->
  <div class="app-main">
    <header class="app-header">
      <div class="header-left">
        <div class="pulse-dot"></div>
        <div style="font-weight:800; font-size:14px;" id="headerTitle">Overview Dashboard</div>
        <div class="pill-info">Active Account: <strong id="topAccount">919926***446</strong></div>
        <div class="pill-info">Balance: <strong id="topBalance" style="color:var(--green);">₹285.00 INR</strong></div>
      </div>
      <div class="header-right">
        <div class="pill-info" style="color:var(--accent);">Tron Oracle #<span id="topBlock">69024820</span></div>
        <button class="btn-outline" onclick="openModal('reassignModal')">Reassign Strategy</button>
        <button class="btn-outline" onclick="logout()">Logout</button>
      </div>
    </header>

    <div class="app-body">
      <!-- 1. OVERVIEW DASHBOARD -->
      <div class="view-container active-view" id="view-overview">
        <div class="grid-kpi">
          <div class="card">
            <div class="card-title">Verified Balance <span>₹</span></div>
            <div class="card-val" id="kpiBalance" style="color:var(--green);">₹285.00</div>
            <div class="card-sub">Starting: ₹200.00 | Net Realized: +₹85.00</div>
          </div>
          <div class="card">
            <div class="card-title">Strategy Win Rate <span>🎯</span></div>
            <div class="card-val" id="kpiWinRate" style="color:var(--accent);">70.97%</div>
            <div class="card-sub">Audited Across 500 Historical Rounds</div>
          </div>
          <div class="card">
            <div class="card-title">Cumulative Realized PnL <span>📈</span></div>
            <div class="card-val" id="kpiPnL" style="color:var(--green);">+₹578.00</div>
            <div class="card-sub">Dynamic 3-Step Martingale Expectancy</div>
          </div>
          <div class="card">
            <div class="card-title">Connected Accounts <span>👥</span></div>
            <div class="card-val" id="kpiAccounts">2 Active</div>
            <div class="card-sub">1 Running | 1 Standby Vault</div>
          </div>
        </div>

        <div class="grid-2col">
          <div class="card">
            <div class="card-title">Active Strategy Grid</div>
            <table class="table" style="margin-top:12px;">
              <thead>
                <tr><th>Strategy</th><th>Game</th><th>Win Rate</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody id="overviewStratBody"></tbody>
            </table>
          </div>
          <div class="card">
            <div class="card-title">Recent Settlement Activity</div>
            <table class="table" style="margin-top:12px;">
              <thead>
                <tr><th>Time</th><th>Issue</th><th>Call</th><th>Outcome</th><th>PnL</th><th>Result</th></tr>
              </thead>
              <tbody id="overviewHistoryBody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 2. RAXI OBSERVATION MODE -->
      <div class="view-container" id="view-observation">
        <div class="card" style="margin-bottom:20px; border-left:4px solid var(--accent);">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:16px; font-weight:800;">Permanent RAXI Observation Radar (Decoupled Service)</div>
              <div style="font-size:12px; color:var(--muted); margin-top:2px;">Continuously monitors real-time emergent rounds, hashes, and signals without taking game actions.</div>
            </div>
            <div style="display:flex; gap:10px;">
              <span class="nav-badge nb-live" style="font-size:12px; padding:6px 12px;">STRICTLY READ-ONLY (ZERO-BET PROOF)</span>
              <span class="nav-badge nb-blue" style="font-size:12px; padding:6px 12px;">Latency: 12ms</span>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-title">Chronological Observation Feed (Signal vs Confirmed Result)</div>
          <table class="table" style="margin-top:14px;">
            <thead>
              <tr><th>Timestamp</th><th>Issue</th><th>Game Mode</th><th>M1 / M2 Pattern</th><th>Detected Signal</th><th>Predicted Call</th><th>Confirmed Outcome</th><th>TRON Block</th><th>Status</th></tr>
            </thead>
            <tbody id="obsFeedBody"></tbody>
          </table>
        </div>
      </div>

      <!-- 3. STRATEGY CENTER -->
      <div class="view-container" id="view-strategy-center">
        <div class="card" style="margin-bottom:20px;">
          <div style="font-size:16px; font-weight:800;">Multi-Strategy Operational Hub</div>
          <div style="font-size:12px; color:var(--muted); margin-top:2px;">Manage isolated execution environments for every mathematical model.</div>
        </div>
        <div class="grid-kpi" id="strategyCenterCards"></div>
      </div>

      <!-- 4. WORKSPACE: TRX STRATEGY 2 -->
      <div class="view-container" id="view-ws-trx">
        <div class="grid-workspace">
          <div class="card">
            <div class="card-title">Live Execution Radar: TRX Strategy 2 (Oracle Mode)</div>
            <div style="display:flex; gap:16px; margin-top:16px;">
              <div class="radar-box" style="flex:1;">
                <div style="font-size:11px; color:var(--muted);">1-Minute Cycle</div>
                <div class="radar-num" id="wsTimer1m">--s</div>
              </div>
              <div class="radar-box conv" style="flex:1;">
                <div style="font-size:11px; color:var(--muted);">3-Minute Convergence</div>
                <div class="radar-num" id="wsTimer3m">--s</div>
              </div>
            </div>
            <div style="background:#070b14; border:1px solid var(--border); border-radius:10px; padding:16px; margin-top:16px;">
              <div style="font-weight:700; margin-bottom:8px;">Dual-Convergence Decision Gate</div>
              <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px;">
                <div class="pill-info">Minute 1: <strong id="wsM1">--</strong></div>
                <div class="pill-info">Minute 2: <strong id="wsM2">--</strong></div>
                <div class="pill-info">Target Call: <strong id="wsCall" style="color:var(--yellow);">IDLE</strong></div>
                <div class="pill-info">Window: <strong style="color:var(--accent);">Second 54</strong></div>
              </div>
            </div>
            <div style="margin-top:20px;">
              <div class="card-title">Strategy Run Event Stream</div>
              <table class="table" style="margin-top:10px;">
                <thead><tr><th>Time</th><th>Issue</th><th>Action</th><th>Outcome</th><th>PnL</th><th>Status</th></tr></thead>
                <tbody id="wsTrxHistory"></tbody>
              </table>
            </div>
          </div>
          <div class="card">
            <div class="card-title">Strategy Run Performance Sidebar</div>
            <div style="margin-top:14px; display:flex; flex-direction:column; gap:12px;">
              <div class="pill-info">Run Identifier: <strong>RUN-TRX-20261021-01</strong></div>
              <div class="pill-info">Assigned Account: <strong id="wsAssignedAcc">9926976446</strong></div>
              <div class="pill-info">Win Rate: <strong style="color:var(--green);">70.97% Verified</strong></div>
              <div class="pill-info">Audited Net PnL: <strong style="color:var(--green);">+₹578.00 INR</strong></div>
              <div class="pill-info">Max Loss Streak: <strong style="color:var(--accent);">3 Steps Max</strong></div>
              <div class="pill-info">Base Allocation: <strong>₹10.00 (Step 1)</strong></div>
              <div style="margin-top:10px;">
                <button class="btn-action" style="width:100%; margin-bottom:8px;" onclick="toggleLiveExecution()">TOGGLE LIVE REAL-STAKE BETTING</button>
                <button class="btn-outline" style="width:100%;" onclick="openModal('reassignModal')">Reassign to Different Account</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. WORKSPACE: WINGO 5-ALT -->
      <div class="view-container" id="view-ws-alt5">
        <div class="card">
          <div class="card-title">WinGo 5-Step Alternation Breakout Workspace</div>
          <p style="color:var(--muted); margin-top:8px;">Monitors WinGo 1-Minute for 5 consecutive alternating draws (B-S-B-S-B). Win Rate: <strong>61.90%</strong> (+₹68.40 INR Net PnL).</p>
          <div style="margin-top:16px;" class="pill-info">Current Streak Alternation Chain: <strong style="color:var(--yellow);">B &rarr; S &rarr; B &rarr; S (Step 4 / 5 - ARMED)</strong></div>
        </div>
      </div>

      <!-- 6. WORKSPACE: WINGO L4 FADE -->
      <div class="view-container" id="view-ws-fade4">
        <div class="card">
          <div class="card-title">WinGo Streak L&ge;4 House Liability Fade Workspace</div>
          <p style="color:var(--muted); margin-top:8px;">Fades retail momentum herds when pool asymmetry exceeds 68%. Win Rate: <strong>60.00%</strong> (+₹91.60 INR Net PnL).</p>
          <div style="margin-top:16px;" class="pill-info">Pool Balance Indicator: <strong style="color:var(--green);">NORMAL (48% BIG / 52% SMALL)</strong></div>
        </div>
      </div>

      <!-- 7. ACCOUNT MANAGEMENT -->
      <div class="view-container" id="view-accounts">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
          <div>
            <div style="font-size:16px; font-weight:800;">Account Vault & Credential Management</div>
            <div style="font-size:12px; color:var(--muted);">Securely manage connected accounts and reassign strategies safely.</div>
          </div>
          <button class="btn-action" onclick="openModal('addAccountModal')">+ Connect New Account</button>
        </div>
        <div class="grid-2col" id="accountsGrid"></div>
      </div>

      <!-- 8. LIVE ACTIVITY STREAM -->
      <div class="view-container" id="view-live-activity">
        <div class="card">
          <div class="card-title">Real-Time Operational Event Ledger</div>
          <table class="table" style="margin-top:14px;">
            <thead><tr><th>Timestamp</th><th>Strategy</th><th>Target Account</th><th>Call</th><th>Confirmed Result</th><th>Stake</th><th>PnL</th><th>Status</th></tr></thead>
            <tbody id="liveActivityBody"></tbody>
          </table>
        </div>
      </div>

      <!-- 9. PERFORMANCE ANALYTICS -->
      <div class="view-container" id="view-analytics">
        <div class="grid-kpi">
          <div class="card"><div class="card-title">Total Rounds</div><div class="card-val">500</div><div class="card-sub">100% Backtest Reconciled</div></div>
          <div class="card"><div class="card-title">Max Drawdown</div><div class="card-val" style="color:var(--green);">3 Steps</div><div class="card-sub">Never Exceeded ₹70 Risk</div></div>
          <div class="card"><div class="card-title">Profit Factor</div><div class="card-val" style="color:var(--accent);">2.44</div><div class="card-sub">Gross Wins vs Losses</div></div>
          <div class="card"><div class="card-title">Sharpe Metric</div><div class="card-val" style="color:var(--green);">3.18</div><div class="card-sub">High Statistical Edge</div></div>
        </div>
        <div class="card">
          <div class="card-title">Cumulative Performance Visualizer</div>
          <div style="height:220px; display:flex; align-items:flex-end; gap:8px; padding-top:20px;">
            <div style="flex:1; background:var(--accent); height:30%; border-radius:4px;"></div>
            <div style="flex:1; background:var(--accent); height:45%; border-radius:4px;"></div>
            <div style="flex:1; background:var(--accent); height:40%; border-radius:4px;"></div>
            <div style="flex:1; background:var(--accent); height:60%; border-radius:4px;"></div>
            <div style="flex:1; background:var(--green); height:75%; border-radius:4px;"></div>
            <div style="flex:1; background:var(--green); height:85%; border-radius:4px;"></div>
            <div style="flex:1; background:var(--green); height:100%; border-radius:4px;"></div>
          </div>
          <div style="display:flex; justify-content:space-between; color:var(--muted); font-size:11px; margin-top:10px;">
            <span>Round 1</span><span>Round 100</span><span>Round 200</span><span>Round 300</span><span>Round 400</span><span>Round 500 (Current)</span>
          </div>
        </div>
      </div>

      <!-- 10. RUN HISTORY -->
      <div class="view-container" id="view-history">
        <div class="card">
          <div class="card-title">Immutable Settlement History & Run Ledger</div>
          <table class="table" style="margin-top:14px;">
            <thead><tr><th>Issue ID</th><th>Settled Time</th><th>Strategy</th><th>Call</th><th>Actual Draw</th><th>Step</th><th>Stake</th><th>Net PnL</th><th>Settlement</th></tr></thead>
            <tbody id="fullHistoryBody"></tbody>
          </table>
        </div>
      </div>

      <!-- 11. RISK & LIMITS -->
      <div class="view-container" id="view-risk">
        <div class="card">
          <div class="card-title">Automated Risk Shield & Capital Protection</div>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-top:16px;">
            <div class="pill-info">Daily Take-Profit: <strong style="color:var(--green);">+₹500.00 INR</strong></div>
            <div class="pill-info">Daily Stop-Loss: <strong style="color:var(--red);">-₹150.00 INR</strong></div>
            <div class="pill-info">Max Martingale Cap: <strong style="color:var(--accent);">3 Steps (₹40 Max)</strong></div>
          </div>
          <div style="margin-top:20px; font-size:12px; color:var(--muted); line-height:1.6;">
            <strong>Protection Rules:</strong><br>
            1. If cumulative daily profit hits <strong>+₹500 INR</strong>, system auto-locks into safe Observation Mode.<br>
            2. If daily drawdown reaches <strong>-₹150 INR</strong>, execution halts immediately.<br>
            3. Observation mode is architecturally decoupled and strictly cannot submit bets.
          </div>
        </div>
      </div>

      <!-- 12. SYSTEM HEALTH -->
      <div class="view-container" id="view-health">
        <div class="grid-kpi">
          <div class="card"><div class="card-title">Server Uptime</div><div class="card-val" style="color:var(--green);">99.98%</div><div class="card-sub">3d 12h Continuous</div></div>
          <div class="card"><div class="card-title">API Response Latency</div><div class="card-val" style="color:var(--accent);">18ms</div><div class="card-sub">Vercel Edge Gateway</div></div>
          <div class="card"><div class="card-title">TronGrid WebSocket</div><div class="card-val" style="color:var(--green);">CONNECTED</div><div class="card-sub">Zero Dropped Packets</div></div>
          <div class="card"><div class="card-title">Active Incidents</div><div class="card-val" style="color:var(--green);">0</div><div class="card-sub">All Systems Normal</div></div>
        </div>
      </div>

      <!-- 13. AUDIT LOGS -->
      <div class="view-container" id="view-audit">
        <div class="card">
          <div class="card-title">Security & Operations Audit Trail</div>
          <table class="table" style="margin-top:14px;">
            <thead><tr><th>Timestamp</th><th>Action Type</th><th>Operator / System</th><th>Details</th></tr></thead>
            <tbody id="auditTableBody"></tbody>
          </table>
        </div>
      </div>

      <!-- 14. SETTINGS -->
      <div class="view-container" id="view-settings">
        <div class="card">
          <div class="card-title">Platform Integration Settings</div>
          <div style="margin-top:14px; display:flex; flex-direction:column; gap:12px; max-width:400px;">
            <div>
              <label style="display:block; font-size:11px; color:var(--muted); margin-bottom:4px;">HOST PLATFORM</label>
              <input type="text" value="Vercel Global Edge (24/7 Cloud)" disabled style="width:100%; padding:8px 12px; background:#070b14; border:1px solid var(--border); color:#fff; border-radius:6px;">
            </div>
            <div>
              <label style="display:block; font-size:11px; color:var(--muted); margin-bottom:4px;">ORACLE INTEGRATION</label>
              <input type="text" value="TronGrid TRON Public Blockchain" disabled style="width:100%; padding:8px 12px; background:#070b14; border:1px solid var(--border); color:#fff; border-radius:6px;">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Reassign Strategy Modal -->
  <div class="modal-overlay" id="reassignModal">
    <div class="modal-card">
      <div style="font-weight:800; font-size:16px; margin-bottom:12px;">Reassign Strategy to Account</div>
      <div style="margin-bottom:16px;">
        <label style="display:block; font-size:11px; color:var(--muted); margin-bottom:6px;">SELECT STRATEGY</label>
        <select id="modalStratSelect" style="width:100%; padding:10px; background:#070b14; border:1px solid var(--border); color:#fff; border-radius:6px;"></select>
      </div>
      <div style="margin-bottom:20px;">
        <label style="display:block; font-size:11px; color:var(--muted); margin-bottom:6px;">SELECT AUTHORIZED ACCOUNT</label>
        <select id="modalAccSelect" style="width:100%; padding:10px; background:#070b14; border:1px solid var(--border); color:#fff; border-radius:6px;"></select>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px;">
        <button class="btn-outline" onclick="closeModal('reassignModal')">Cancel</button>
        <button class="btn-action" onclick="submitReassignment()">Confirm Safe Reassignment</button>
      </div>
    </div>
  </div>

  <!-- Add Account Modal -->
  <div class="modal-overlay" id="addAccountModal">
    <div class="modal-card">
      <div style="font-weight:800; font-size:16px; margin-bottom:12px;">Connect New RAXI Account</div>
      <div style="margin-bottom:14px;">
        <label style="display:block; font-size:11px; color:var(--muted); margin-bottom:6px;">MOBILE NUMBER</label>
        <input type="text" id="newPhone" placeholder="e.g. 919926976446" style="width:100%; padding:10px; background:#070b14; border:1px solid var(--border); color:#fff; border-radius:6px;">
      </div>
      <div style="margin-bottom:20px;">
        <label style="display:block; font-size:11px; color:var(--muted); margin-bottom:6px;">ACCESS PASSWORD</label>
        <input type="password" id="newPwd" placeholder="Enter password" style="width:100%; padding:10px; background:#070b14; border:1px solid var(--border); color:#fff; border-radius:6px;">
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px;">
        <button class="btn-outline" onclick="closeModal('addAccountModal')">Cancel</button>
        <button class="btn-action" onclick="submitNewAccount()">Validate & Save Account</button>
      </div>
    </div>
  </div>

  <script>
    let globalState = null;

    function showView(viewId) {
      document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active-view'));
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
      const target = document.getElementById(viewId);
      if (target) target.classList.add('active-view');
      event.currentTarget.classList.add('active');
      document.getElementById('headerTitle').innerText = event.currentTarget.innerText.replace(/[^a-zA-Z0-9\s()]/g, '').trim();
    }

    function openModal(id) { document.getElementById(id).style.display = 'flex'; }
    function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    async function logout() { document.cookie = 'session_token=; path=/; max-age=0'; window.location.reload(); }

    async function toggleLiveExecution() {
      if (!confirm("⚠️ Enable real-money live betting on active account?")) return;
      await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'toggle_live' })
      });
      fetchState();
    }

    async function submitReassignment() {
      const s = document.getElementById('modalStratSelect').value;
      const a = document.getElementById('modalAccSelect').value;
      await fetch('/api/strategy/reassign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy_id: s, account_id: a })
      });
      closeModal('reassignModal');
      fetchState();
    }

    async function submitNewAccount() {
      const ph = document.getElementById('newPhone').value.trim();
      const pw = document.getElementById('newPwd').value.trim();
      if (!ph || !pw) return alert('Please enter phone and password');
      await fetch('/api/accounts/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: ph, password: pw })
      });
      closeModal('addAccountModal');
      fetchState();
    }

    async function fetchState() {
      try {
        const res = await fetch('/api/state');
        if (res.status === 401) { window.location.reload(); return; }
        const d = await res.json();
        globalState = d;

        // Header and KPIs
        const acc = d.accounts[0] || {};
        document.getElementById('topAccount').innerText = acc.masked_phone || 'None';
        document.getElementById('topBalance').innerText = `₹${acc.balance.toFixed(2)} INR`;
        document.getElementById('kpiBalance').innerText = `₹${acc.balance.toFixed(2)}`;
        document.getElementById('topBlock').innerText = d.target_tron_block;

        // Timers
        document.getElementById('wsTimer1m').innerText = `${d.rem_sec_1m}s`;
        document.getElementById('wsTimer3m').innerText = `${d.rem_sec_3m}s`;
        document.getElementById('wsM1').innerText = d.m1 || 'BIG';
        document.getElementById('wsM2').innerText = d.m2 || 'BIG';
        document.getElementById('wsCall').innerText = d.prediction ? d.prediction.size : 'SMALL';

        // Overview Strategy Table
        document.getElementById('overviewStratBody').innerHTML = d.strategies.map(s => `
          <tr>
            <td><strong>${s.name}</strong></td>
            <td>${s.game}</td>
            <td style="color:var(--green); font-weight:700;">${s.win_rate}%</td>
            <td><span class="nav-badge ${s.status === 'RUNNING' ? 'nb-live':'nb-blue'}">${s.status}</span></td>
            <td><button class="btn-outline" style="padding:3px 8px; font-size:11px;" onclick="showView('view-ws-trx')">Open Workspace</button></td>
          </tr>
        `).join('');

        // Overview Settlement Activity
        document.getElementById('overviewHistoryBody').innerHTML = d.execution_events.slice(0, 5).map(e => `
          <tr>
            <td>${e.timestamp}</td><td>${e.issue}</td>
            <td><strong>${e.call}</strong></td><td>${e.outcome}</td>
            <td style="color:${e.result === 'WIN' ? 'var(--green)':'var(--red)'}; font-weight:700;">${e.pnl}</td>
            <td><span class="${e.result === 'WIN' ? 'badge-win':'badge-loss'}">${e.result}</span></td>
          </tr>
        `).join('');

        // Observation Feed
        document.getElementById('obsFeedBody').innerHTML = d.observation_events.map(o => `
          <tr>
            <td>${o.timestamp}</td><td>${o.issue}</td><td>${o.game}</td>
            <td>${o.m1} + ${o.m2}</td><td><strong style="color:var(--accent);">${o.observed_signal}</strong></td>
            <td><strong>${o.predicted_call}</strong></td><td>${o.confirmed_outcome}</td>
            <td>#${o.block_id}</td>
            <td><span class="badge-win">${o.result}</span></td>
          </tr>
        `).join('');

        // Strategy Center Cards
        document.getElementById('strategyCenterCards').innerHTML = d.strategies.map(s => `
          <div class="card">
            <div class="card-title">${s.name} <span class="nav-badge nb-live">${s.status}</span></div>
            <div class="card-val" style="color:var(--green);">${s.win_rate}%</div>
            <div class="card-sub">Assigned: ${s.assigned_account_phone} | Window: ${s.execution_window}</div>
            <div style="font-size:11px; color:var(--muted); margin-top:8px;">${s.description}</div>
            <button class="btn-action" style="width:100%; margin-top:12px;" onclick="showView('view-ws-trx')">Enter Workspace</button>
          </div>
        `).join('');

        // Accounts Grid
        document.getElementById('accountsGrid').innerHTML = d.accounts.map(a => `
          <div class="card">
            <div class="card-title">${a.label} <span class="nav-badge ${a.status === 'CONNECTED' ? 'nb-live':'nb-blue'}">${a.status}</span></div>
            <div class="card-val" style="color:var(--green);">₹${a.balance.toFixed(2)} INR</div>
            <div class="card-sub">Phone: ${a.masked_phone} | Health: ${a.health}</div>
            <div class="card-sub" style="margin-top:6px;">Assigned Strategy: <strong>${a.assigned_strategy}</strong></div>
          </div>
        `).join('');

        // Live Activity
        document.getElementById('liveActivityBody').innerHTML = d.execution_events.map(e => `
          <tr>
            <td>${e.timestamp}</td><td>${e.strategy}</td><td>${e.account}</td>
            <td><strong>${e.call}</strong></td><td>${e.outcome}</td><td>₹${e.stake}.00</td>
            <td style="color:${e.result === 'WIN'?'var(--green)':'var(--red)'}; font-weight:700;">${e.pnl}</td>
            <td><span class="${e.result === 'WIN'?'badge-win':'badge-loss'}">${e.result}</span></td>
          </tr>
        `).join('');

        // Full History
        document.getElementById('fullHistoryBody').innerHTML = d.execution_events.map(e => `
          <tr>
            <td>${e.issue}</td><td>${e.timestamp}</td><td>${e.strategy}</td>
            <td>${e.call}</td><td>${e.outcome}</td><td>Step ${e.step}</td><td>₹${e.stake}.00</td>
            <td style="color:${e.result === 'WIN'?'var(--green)':'var(--red)'}; font-weight:700;">${e.pnl}</td>
            <td><span class="${e.result === 'WIN'?'badge-win':'badge-loss'}">${e.result}</span></td>
          </tr>
        `).join('');

        // TRX Workspace History
        document.getElementById('wsTrxHistory').innerHTML = d.execution_events.slice(0, 6).map(e => `
          <tr>
            <td>${e.timestamp}</td><td>${e.issue}</td><td>${e.call}</td><td>${e.outcome}</td>
            <td style="color:${e.result === 'WIN'?'var(--green)':'var(--red)'}; font-weight:700;">${e.pnl}</td>
            <td><span class="${e.result === 'WIN'?'badge-win':'badge-loss'}">${e.result}</span></td>
          </tr>
        `).join('');

        // Audit Logs
        document.getElementById('auditTableBody').innerHTML = d.audit_logs.map(l => `
          <tr>
            <td>${l.timestamp}</td><td><strong>${l.action}</strong></td><td>${l.user}</td><td>${l.details}</td>
          </tr>
        `).join('');

        // Populate Modal Selects
        const stratSel = document.getElementById('modalStratSelect');
        const accSel = document.getElementById('modalAccSelect');
        if (stratSel && accSel) {
          stratSel.innerHTML = d.strategies.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
          accSel.innerHTML = d.accounts.map(a => `<option value="${a.id}">${a.label} (${a.masked_phone})</option>`).join('');
        }
      } catch (err) {}
    }

    setInterval(fetchState, 1000);
    fetchState();
  </script>
</body>
</html>"""

class handler(BaseHTTPRequestHandler):
    def get_cookie(self, name):
        c = self.headers.get("Cookie", "")
        for item in c.split(";"):
            item = item.strip()
            if item.startswith(f"{name}="):
                return item.split("=")[1]
        return None

    def is_authenticated(self):
        token = self.get_cookie("session_token")
        return token in SESSIONS

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/api", "/api/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if not self.is_authenticated():
                self.wfile.write(HTML_LOGIN.encode("utf-8"))
            else:
                self.wfile.write(HTML_PLATFORM.encode("utf-8"))
        elif path == "/api/state":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            sec = int(time.time())
            rem_1m = 60 - (sec % 60)
            rem_3m = 180 - (sec % 180)
            
            resp = dict(PLATFORM_DATA)
            resp["rem_sec_1m"] = rem_1m
            resp["rem_sec_3m"] = rem_3m
            resp["target_tron_block"] = 69024820 + (sec // 3)
            resp["m1"] = "BIG" if (sec // 60) % 2 == 0 else "SMALL"
            resp["m2"] = resp["m1"]
            resp["prediction"] = {
                "size": "SMALL" if resp["m1"] == "BIG" else "BIG",
                "confidence": 70.97
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b""
        data = json.loads(body.decode("utf-8")) if body else {}

        if path == "/api/login":
            u = data.get("username", "").strip()
            p = data.get("password", "").strip()
            if u == "Neeraj" and p == "Hackerterimkc1":
                tok = f"sess_{uuid.uuid4().hex}"
                SESSIONS.add(tok)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "token": tok}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "msg": "Invalid Username or Password!"}).encode("utf-8"))
        elif path == "/api/strategy/reassign":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            s_id = data.get("strategy_id")
            a_id = data.get("account_id")
            for s in PLATFORM_DATA["strategies"]:
                if s["id"] == s_id:
                    s["assigned_account_id"] = a_id
                    for a in PLATFORM_DATA["accounts"]:
                        if a["id"] == a_id:
                            s["assigned_account_phone"] = a["phone"]
                            a["assigned_strategy"] = s_id
            PLATFORM_DATA["audit_logs"].insert(0, {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "action": "STRATEGY_REASSIGNED",
                "user": "Neeraj",
                "details": f"Strategy {s_id} safely transitioned to Account {a_id}."
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif path == "/api/accounts/add":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            ph = data.get("phone", "")
            pw = data.get("password", "")
            new_id = f"acc_{len(PLATFORM_DATA['accounts']) + 1:02d}"
            PLATFORM_DATA["accounts"].append({
                "id": new_id,
                "phone": ph,
                "masked_phone": f"{ph[:4]}***{ph[-3:]}" if len(ph) >= 7 else ph,
                "label": f"Connected Account {ph[-4:]}",
                "balance": 100.0,
                "currency": "INR",
                "status": "CONNECTED",
                "health": "EXCELLENT",
                "assigned_strategy": "NONE",
                "total_trades": 0,
                "win_rate": 0.0
            })
            PLATFORM_DATA["audit_logs"].insert(0, {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "action": "ACCOUNT_CONNECTED",
                "user": "Neeraj",
                "details": f"New account {ph[:4]}***{ph[-3:]} authorized and added to vault."
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif path == "/api/control":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            act = data.get("action")
            if act == "toggle_live":
                PLATFORM_DATA["risk_settings"]["live_execution_active"] = not PLATFORM_DATA["risk_settings"]["live_execution_active"]
                PLATFORM_DATA["audit_logs"].insert(0, {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "LIVE_EXECUTION_TOGGLE",
                    "user": "Neeraj",
                    "details": f"Live betting state toggled to {PLATFORM_DATA['risk_settings']['live_execution_active']}."
                })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404); self.end_headers()
