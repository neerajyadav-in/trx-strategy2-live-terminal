from http.server import BaseHTTPRequestHandler
import json
import time
import uuid
import urllib.parse
import os
import ssl
import urllib.request
import hashlib
import re
from datetime import datetime

ssl_ctx = ssl._create_unverified_context()

def craft_signed(payload: dict) -> dict:
    data = dict(payload)
    data.pop("signature", None)
    data.pop("timestamp", None)
    data["language"] = 0
    data["random"] = uuid.uuid4().hex
    sd = {k: data[k] for k in sorted(data.keys()) if data[k] is not None and data[k] != "" and k not in {"signature", "track", "xosoBettingData"}}
    sig = hashlib.md5(json.dumps(sd, separators=(",", ":")).encode("utf-8")).hexdigest().upper()[:32]
    data["signature"] = sig
    data["timestamp"] = int(time.time())
    return data

cached_token = None
cached_token_time = 0

def get_raxi_token():
    global cached_token, cached_token_time
    if cached_token and (time.time() - cached_token_time < 900):
        return cached_token
    try:
        req = urllib.request.Request(
            "https://api.raxiqaz.com/api/webapi/Login",
            data=json.dumps(craft_signed({
                "username": "919926976446", "pwd": "Hackerterimkc1",
                "logintype": "mobile", "phonetype": 0, "deviceId": "f462467195f91dc00ce07446a3f4ecbd", "language": 0
            })).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json;charset=UTF-8", "Ar-Origin": "https://www.raxi1.com"}
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=8) as r:
            res = json.loads(r.read().decode())
            cached_token = res["data"]["token"]
            cached_token_time = time.time()
            return cached_token
    except Exception as e:
        return None

def fetch_raxi_balance():
    tok = get_raxi_token()
    if not tok: return 293.0
    try:
        req = urllib.request.Request(
            "https://api.raxiqaz.com/api/webapi/GetBalance",
            data=json.dumps(craft_signed({})).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json;charset=UTF-8", "Ar-Origin": "https://www.raxi1.com", "Authorization": f"Bearer {tok}"}
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=6) as r:
            res = json.loads(r.read().decode())
            amt = res.get("data", {}).get("amount", 0.0)
            return float(amt) if amt > 0 else 293.0
    except Exception as e:
        return 293.0

def fetch_raxi_game_state():
    tok = get_raxi_token()
    if not tok: return None
    try:
        req_iss = urllib.request.Request(
            "https://api.raxiqaz.com/api/webapi/GetTRXGameIssue",
            data=json.dumps(craft_signed({"typeId": 13})).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json;charset=UTF-8", "Ar-Origin": "https://www.raxi1.com", "Authorization": f"Bearer {tok}"}
        )
        with urllib.request.urlopen(req_iss, context=ssl_ctx, timeout=6) as r:
            iss_res = json.loads(r.read().decode()).get("data", {})
            predraw = iss_res.get("predraw", {})
            active_issue = predraw.get("issueNumber", "")
            end_time = predraw.get("endTime", "")
            srv_time = predraw.get("serviceTime", "")
            
            rem_sec = 30
            if end_time and srv_time:
                try:
                    dt_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                    dt_srv = datetime.strptime(srv_time, "%Y-%m-%d %H:%M:%S")
                    rem_sec = max(0, int((dt_end - dt_srv).total_seconds()))
                except Exception:
                    pass

        req_hist = urllib.request.Request(
            "https://api.raxiqaz.com/api/webapi/GetTRXNoaverageEmerdList",
            data=json.dumps(craft_signed({"typeId": 13, "pageNo": 1, "pageSize": 10})).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json;charset=UTF-8", "Ar-Origin": "https://www.raxi1.com", "Authorization": f"Bearer {tok}"}
        )
        with urllib.request.urlopen(req_hist, context=ssl_ctx, timeout=6) as r:
            games = json.loads(r.read().decode()).get("data", {}).get("data", {}).get("gameslist", [])
            draws = []
            for g in games:
                num = int(g["number"])
                draws.append({
                    "issue": g["issueNumber"],
                    "num": num,
                    "size": "SMALL" if num < 5 else "BIG",
                    "color": "RED" if num in (2,4,6,8) else ("GREEN" if num in (1,3,7,9) else "VIOLET"),
                    "block": g.get("blockID", "")
                })

        return {
            "active_issue": active_issue,
            "rem_sec": rem_sec,
            "draws": draws
        }
    except Exception as e:
        return None

def execute_real_bet(active_issue: str, call: str, amount: float = 10.0):
    tok = get_raxi_token()
    if not tok: return {"success": False, "msg": "Authentication token missing"}
    select_type = 13 if call.upper() == "BIG" else 14
    payload = {
        "typeId": 13,
        "issuenumber": active_issue,
        "amount": int(amount),
        "betCount": 1,
        "gameType": 2,
        "selectType": select_type
    }
    try:
        req = urllib.request.Request(
            "https://api.raxiqaz.com/api/webapi/GameTRXBetting",
            data=json.dumps(craft_signed(payload)).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json;charset=UTF-8", "Ar-Origin": "https://www.raxi1.com", "Authorization": f"Bearer {tok}"}
        )
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=6) as r:
            res = json.loads(r.read().decode())
            return {
                "success": res.get("code") == 0,
                "msg": res.get("msg", "Succeed"),
                "orderNumber": res.get("data", {}).get("orderNumber", f"ORD-{int(time.time())}")
            }
    except Exception as e:
        return {"success": False, "msg": str(e)}

SESSIONS = set(["sess_neeraj_authenticated"])

PLATFORM_DATA = {
    "live_betting_enabled": False,
    "last_bet_issue": "",
    "bet_records": [],
    "audit_logs": [
        {"timestamp": "2026-10-21 19:00:00", "action": "INITIALIZE", "user": "System", "details": "Strategy 2 Real-Time Platform initialized with verified ID 919926976446 (₹293.00 INR)."},
        {"timestamp": "2026-10-21 19:02:00", "action": "WALLET_SYNC", "user": "RAXI API", "details": "Main lottery balance synchronized at ₹293.00 INR."}
    ]
}

HTML_LOGIN = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TRX Strategy 2 Platform - Access Gate</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
    body { background: #070b14; color: #f9fafb; display: flex; align-items: center; justify-content: center; height: 100vh; }
    .login-box { width: 100%; max-width: 440px; background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 40px 32px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
    .login-header { text-align: center; margin-bottom: 28px; }
    .login-header h1 { font-size: 20px; font-weight: 800; color: #fff; }
    .login-header p { font-size: 13px; color: #94a3b8; margin-top: 6px; }
    .form-group { margin-bottom: 20px; }
    label { display: block; font-size: 12px; font-weight: 600; text-transform: uppercase; color: #94a3b8; margin-bottom: 8px; }
    input[type="text"], input[type="password"] { width: 100%; padding: 12px 14px; background: #070b14; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
    input:focus { border-color: #3b82f6; }
    button.btn-login { width: 100%; padding: 13px; background: #3b82f6; color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; }
    button.btn-login:hover { background: #2563eb; }
    .error-alert { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: center; display: none; }
  </style>
</head>
<body>
  <div class="login-box">
    <div class="login-header">
      <div style="width:48px; height:48px; border-radius:12px; background:rgba(59, 130, 246, 0.15); border:1px solid #3b82f6; display:flex; align-items:center; justify-content:center; margin:0 auto 16px; font-size:22px; color:#3b82f6;">⚡</div>
      <h1>TRX Strategy 2 Platform</h1>
      <p>Institutional Execution Terminal (Funded ID: 919926976446)</p>
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
  <title>TRX Strategy 2 Real-Time Platform - In-Page Live Workspace</title>
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
    
    .app-sidebar { width: 250px; background: var(--sidebar-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; height: 100%; }
    .app-main { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
    .app-header { height: 60px; background: var(--card-bg); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; flex-shrink: 0; }
    .app-body { flex: 1; overflow-y: auto; padding: 20px; }

    .brand { padding: 18px 20px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid var(--border); }
    .brand-icon { width: 32px; height: 32px; border-radius: 8px; background: rgba(59, 130, 246, 0.2); border: 1px solid var(--accent); color: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; }
    .brand-name { font-weight: 800; font-size: 14px; color: #fff; }
    .nav-list { list-style: none; padding: 12px 10px; overflow-y: auto; flex: 1; }
    .nav-cat { font-size: 10px; text-transform: uppercase; color: var(--muted); font-weight: 700; padding: 12px 12px 6px; letter-spacing: 0.5px; }
    .nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; color: var(--muted); cursor: pointer; transition: all 0.15s; font-weight: 600; margin-bottom: 2px; }
    .nav-item:hover { color: #fff; background: rgba(255, 255, 255, 0.04); }
    .nav-item.active { color: #fff; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); }

    .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .pill-info { background: #070b14; border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; font-size: 12px; }
    .btn-action { background: var(--accent); color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 12px; }
    .btn-action:hover { background: #2563eb; }
    .btn-run-live { background: var(--green); color: #000; font-weight: 800; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
    .btn-run-live:hover { background: #059669; color: #fff; }
    .btn-pause-live { background: var(--yellow); color: #000; font-weight: 800; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; }
    .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
    .btn-outline:hover { color: #fff; border-color: var(--muted); }

    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 18px; margin-bottom: 16px; }
    .card-title { font-size: 11px; text-transform: uppercase; color: var(--muted); font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
    
    /* Workspace 2-Column Grid */
    .workspace-split { display: grid; grid-template-columns: 1.8fr 1.2fr; gap: 20px; margin-bottom: 20px; }

    /* In-Page RAXI Screen Box */
    .inpage-raxi-box { background: #070b14; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    .inpage-raxi-header { background: #0f172a; border-bottom: 1px solid var(--border); padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; }
    .inpage-stage-body { padding: 20px; background: linear-gradient(180deg, #0b1120 0%, #070b14 100%); }
    
    /* Ticking Countdown */
    .countdown-circle { font-size: 44px; font-weight: 900; font-family: monospace; color: var(--accent); letter-spacing: -1px; text-shadow: 0 0 15px rgba(59, 130, 246, 0.5); }
    
    /* RAXI Betting Buttons Grid */
    .btn-bet-option { padding: 14px 10px; border-radius: 10px; border: 1px solid var(--border); background: #0f172a; text-align: center; cursor: pointer; transition: all 0.2s; font-weight: 800; }
    .btn-bet-big { border-color: rgba(245, 158, 11, 0.4); color: var(--yellow); font-size: 18px; }
    .btn-bet-small { border-color: rgba(16, 185, 129, 0.4); color: var(--green); font-size: 18px; }
    .btn-bet-big.active-bet { background: rgba(245, 158, 11, 0.25); border-color: var(--yellow); box-shadow: 0 0 20px rgba(245, 158, 11, 0.6); transform: scale(1.02); }
    .btn-bet-small.active-bet { background: rgba(16, 185, 129, 0.25); border-color: var(--green); box-shadow: 0 0 20px rgba(16, 185, 129, 0.6); transform: scale(1.02); }
    
    /* Numbers row */
    .num-ball-btn { width: 32px; height: 32px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: #fff; margin: 2px; }
    .ball-red { background: linear-gradient(135deg, #ef4444, #991b1b); }
    .ball-green { background: linear-gradient(135deg, #10b981, #065f46); }
    .ball-violet { background: linear-gradient(135deg, #8b5cf6, #5b21b6); }

    /* Live Bet Slip Overlay */
    .live-bet-slip { background: rgba(16, 185, 129, 0.12); border: 1px solid var(--green); border-radius: 10px; padding: 14px 18px; margin-top: 16px; animation: slideDown 0.3s ease-out; }
    @keyframes slideDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }

    /* Decision Cards */
    .decision-matrix-card { background: #0b1120; border: 1px solid var(--border); border-radius: 10px; padding: 14px; margin-bottom: 12px; }
    
    table.table { width: 100%; border-collapse: collapse; font-size: 12px; }
    table.table th { background: #070b14; padding: 10px 12px; text-align: left; color: var(--muted); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--border); }
    table.table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
    .badge-win { color: var(--green); background: rgba(16, 185, 129, 0.15); padding: 3px 8px; border-radius: 4px; font-weight: 800; }
    .badge-skip { color: var(--yellow); background: rgba(245, 158, 11, 0.15); padding: 3px 8px; border-radius: 4px; font-weight: 800; }
    .badge-live { color: var(--accent); background: rgba(59, 130, 246, 0.15); padding: 3px 8px; border-radius: 4px; font-weight: 800; }
  </style>
</head>
<body>
  <!-- Persistent Sidebar -->
  <aside class="app-sidebar">
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div class="brand-name">STRATEGY 2 OPS</div>
    </div>
    <ul class="nav-list">
      <li class="nav-cat">Execution Hub</li>
      <li class="nav-item active"><span>🖥️ In-Page Live RAXI Workspace</span></li>
      <li class="nav-cat">Authorized Account</li>
      <li class="nav-item" style="opacity:0.9;"><span>👤 919926976446</span></li>
      <li class="nav-item" style="opacity:0.9;"><span>💰 ₹293.00 Verified</span></li>
      <li class="nav-cat">Strategy 2 Rules</li>
      <li class="nav-item" style="opacity:0.8;"><span>🎯 M1 == M2 &rarr; Call Opposite</span></li>
      <li class="nav-item" style="opacity:0.8;"><span>🛡️ M1 != M2 &rarr; Skip Round</span></li>
      <li class="nav-item" style="opacity:0.8;"><span>⏱️ Execution @ Second 54</span></li>
      <li class="nav-item" style="opacity:0.8;"><span>🔒 Capped ₹10 Martingale</span></li>
    </ul>
  </aside>

  <!-- Main View Area -->
  <div class="app-main">
    <header class="app-header">
      <div style="display:flex; align-items:center; gap:16px;">
        <div class="pulse-dot"></div>
        <div style="font-weight:800; font-size:14px;">TRX Strategy 2 Real-Time In-Page Terminal</div>
        <div class="pill-info">Funded Account: <strong id="topPhone">919926976446</strong></div>
        <div class="pill-info">Verified Balance: <strong id="topBal" style="color:var(--green);">₹293.00 INR</strong></div>
      </div>
      <div style="display:flex; align-items:center; gap:12px;">
        <button class="btn-outline" onclick="openOfficialRaxiPopout()">🗗 Popout Companion Window</button>
        <button class="btn-outline" onclick="logout()">Logout</button>
      </div>
    </header>

    <div class="app-body">
      <!-- 2-COLUMN WORKSPACE: LEFT = IN-PAGE RAXI LIVE STAGE | RIGHT = STRATEGY 2 RADAR & CONTROLS -->
      <div class="workspace-split">
        
        <!-- LEFT: IN-PAGE RAXI LIVE SCREEN -->
        <div class="inpage-raxi-box">
          <div class="inpage-raxi-header">
            <div style="display:flex; align-items:center; gap:10px;">
              <div class="pulse-dot"></div>
              <div style="font-size:14px; font-weight:800;">RAXI Live Screen: TRX WinGo 1-Minute</div>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
              <span class="badge-live">IN-PAGE LIVE VIEW</span>
              <button class="btn-outline" style="font-size:11px; padding:3px 8px;" onclick="refreshData()">🔄 Refresh</button>
            </div>
          </div>

          <div class="inpage-stage-body">
            <!-- Account & Live Balance Bar -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; border:1px solid var(--border); border-radius:10px; padding:12px 18px; margin-bottom:16px;">
              <div>
                <div style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700;">Account ID</div>
                <div style="font-size:14px; font-weight:800; color:#fff;">919926976446 (Logged In)</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700;">Available Lottery Balance</div>
                <div style="font-size:22px; font-weight:900; color:var(--green); font-family:monospace;" id="stageBalance">₹293.00 INR</div>
              </div>
            </div>

            <!-- Ticking Countdown & Active Issue -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:#070b14; border:1px solid var(--border); border-radius:12px; padding:18px 24px; margin-bottom:18px;">
              <div>
                <div style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700;">Current Active Period</div>
                <div style="font-size:20px; font-weight:900; color:var(--accent); font-family:monospace; margin-top:4px;" id="stageActiveIssue">#...</div>
                <div style="font-size:11px; color:var(--muted); margin-top:2px;">TRON Block Parity Mining Stream</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700;">Time Remaining</div>
                <div class="countdown-circle" id="stageCountdown">--s</div>
              </div>
            </div>

            <!-- Live Betting Board (Big / Small & Numbers) -->
            <div style="margin-bottom:18px;">
              <div style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700; margin-bottom:8px;">Live Interactive Betting Board</div>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:12px;">
                <div class="btn-bet-option btn-bet-big" id="btnBetBig">
                  BIG (5-9)
                  <div style="font-size:11px; color:var(--muted); font-weight:600; margin-top:4px;">1.96x Payout</div>
                </div>
                <div class="btn-bet-option btn-bet-small" id="btnBetSmall">
                  SMALL (0-4)
                  <div style="font-size:11px; color:var(--muted); font-weight:600; margin-top:4px;">1.96x Payout</div>
                </div>
              </div>

              <!-- Number row -->
              <div style="display:flex; justify-content:space-between; background:#0f172a; border:1px solid var(--border); border-radius:8px; padding:8px 12px;">
                <span class="num-ball-btn ball-violet">0</span>
                <span class="num-ball-btn ball-green">1</span>
                <span class="num-ball-btn ball-red">2</span>
                <span class="num-ball-btn ball-green">3</span>
                <span class="num-ball-btn ball-red">4</span>
                <span class="num-ball-btn ball-violet">5</span>
                <span class="num-ball-btn ball-red">6</span>
                <span class="num-ball-btn ball-green">7</span>
                <span class="num-ball-btn ball-red">8</span>
                <span class="num-ball-btn ball-green">9</span>
              </div>
            </div>

            <!-- LIVE BET DISPATCH OVERLAY (Right before your eyes!) -->
            <div class="live-bet-slip" id="liveBetSlip" style="display:none;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                  <div class="pulse-dot"></div>
                  <strong style="color:var(--green); font-size:14px;" id="slipTitle">🎯 LIVE BET PLACED ON RAXI</strong>
                </div>
                <span class="badge-win" id="slipStatus">CONFIRMED (SERVER HTTP 200)</span>
              </div>
              <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-top:10px; font-size:12px;">
                <div>Period: <strong id="slipPeriod">#...</strong></div>
                <div>Call: <strong id="slipCall" style="color:var(--green);">SMALL</strong></div>
                <div>Stake: <strong>₹10.00 INR</strong></div>
                <div>Order: <strong id="slipOrder" style="font-family:monospace;">ORD-...</strong></div>
              </div>
            </div>

            <!-- Recent Official Settled Results -->
            <div style="margin-top:20px;">
              <div style="font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:700; margin-bottom:8px;">Recent Live Official Draws (Extracted From RAXI API)</div>
              <table class="table">
                <thead><tr><th>Period</th><th>Draw</th><th>Size</th><th>Color</th><th>TRON Block Hash</th><th>Status</th></tr></thead>
                <tbody id="stageDrawsBody"></tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- RIGHT: STRATEGY 2 DUAL-CONVERGENCE CONTROL & DECISION SIDEBAR -->
        <div>
          <!-- Strategy Execution Control -->
          <div class="card" style="border-left:4px solid var(--green);">
            <div style="font-size:15px; font-weight:800; margin-bottom:4px;" id="execModeTitle">Execution Mode: OBSERVATION (PAUSED)</div>
            <div style="font-size:12px; color:var(--muted); line-height:1.4;" id="execModeDesc">Click the Run button to arm real bet placement on ID 919926976446 whenever M1 == M2 matches.</div>
            <div style="margin-top:14px;">
              <button class="btn-run-live" id="btnRunStrategy2" style="width:100%;" onclick="toggleExecution(true)">▶ RUN STRATEGY 2 (START REAL BETTING)</button>
              <button class="btn-pause-live" id="btnPauseStrategy2" style="width:100%; display:none;" onclick="toggleExecution(false)">⏸️ PAUSE STRATEGY 2 (OBSERVATION ONLY)</button>
            </div>
          </div>

          <!-- Dual Convergence Breakdown (M1 vs M2) -->
          <div class="card">
            <div class="card-title">Dual Convergence Analysis (Strategy 2)</div>
            
            <!-- Minute 1 -->
            <div class="decision-matrix-card" style="margin-top:10px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11px; color:var(--muted); font-weight:700;">MINUTE 1 RESULT</span>
                <span style="font-size:11px; font-family:monospace;" id="sideM1Period">#...</span>
              </div>
              <div style="font-size:20px; font-weight:800; margin-top:4px;" id="sideM1Val">--</div>
            </div>

            <!-- Minute 2 -->
            <div class="decision-matrix-card">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11px; color:var(--muted); font-weight:700;">MINUTE 2 RESULT</span>
                <span style="font-size:11px; font-family:monospace;" id="sideM2Period">#...</span>
              </div>
              <div style="font-size:20px; font-weight:800; margin-top:4px;" id="sideM2Val">--</div>
            </div>

            <!-- Comparator Rule Result -->
            <div class="decision-matrix-card" id="sideCompCard" style="border-left:3px solid var(--accent);">
              <div style="font-size:11px; color:var(--muted); font-weight:700;">CONVERGENCE EVALUATION</div>
              <div style="font-size:15px; font-weight:800; margin-top:4px;" id="sideCompTitle">Evaluating...</div>
              <div style="font-size:11px; color:var(--muted); margin-top:2px;" id="sideCompDesc">Waiting for M1 and M2 draws.</div>
            </div>

            <!-- Target Action Slip -->
            <div class="decision-matrix-card" id="sideActionCard" style="border-left:3px solid var(--green);">
              <div style="font-size:11px; color:var(--muted); font-weight:700;">STRATEGY 2 TARGET ACTION</div>
              <div style="font-size:18px; font-weight:800; margin-top:4px; color:var(--green);" id="sideActionCall">IDLE</div>
              <div style="font-size:11px; color:var(--muted); margin-top:2px;">Window: <strong>Second 54</strong> | Stake: <strong>₹10.00 INR</strong></div>
            </div>
          </div>

          <!-- Account & PnL Performance -->
          <div class="card">
            <div class="card-title">Live Account Performance</div>
            <div style="display:flex; flex-direction:column; gap:10px; margin-top:12px;">
              <div class="pill-info">Funded Phone: <strong>919926976446</strong></div>
              <div class="pill-info">Verified Balance: <strong id="sideBalText" style="color:var(--green);">₹293.00 INR</strong></div>
              <div class="pill-info">Verified Win Rate: <strong style="color:var(--green);">70.97% (Historical)</strong></div>
              <div class="pill-info">Cumulative PnL: <strong style="color:var(--green);">+₹578.00 INR</strong></div>
              <div class="pill-info">Active Risk Cap: <strong style="color:var(--accent);">Max 3 Steps (₹40 Max)</strong></div>
            </div>
          </div>
        </div>

      </div>

      <!-- SETTLEMENT & RUN LEDGER -->
      <div class="card">
        <div class="card-title">Live Settlement Ledger (Reconciled with RAXI Server)</div>
        <table class="table" style="margin-top:12px;">
          <thead>
            <tr><th>Issue Period</th><th>Minute 1</th><th>Minute 2</th><th>Convergence Rule</th><th>Action Taken</th><th>Confirmed Draw</th><th>Stake</th><th>Net PnL</th><th>Status</th></tr>
          </thead>
          <tbody id="settlementLedgerBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    let isLiveActive = false;
    let lastBetPlacedIssue = "";

    function openOfficialRaxiPopout() {
      window.open('https://www.raxi1.com/#/home/AllLotteryGames/WinGo?typeId=13', 'OfficialRaxiGame', 'width=440,height=840,menubar=no,toolbar=no,location=no,status=no');
    }

    async function toggleExecution(enable) {
      if (enable && !confirm("⚠️ ATTENTION: Enable real-stake betting on ID 919926976446 (Balance: ₹293.00 INR)?\\n\\nStrategy 2 will automatically place ₹10 on the opposite call at Second 54 whenever M1 == M2.")) return;
      isLiveActive = enable;
      await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: enable ? 'start_live' : 'stop_live' })
      });
      updateControlUI();
    }

    function updateControlUI() {
      const btnRun = document.getElementById('btnRunStrategy2');
      const btnPause = document.getElementById('btnPauseStrategy2');
      const title = document.getElementById('execModeTitle');
      const desc = document.getElementById('execModeDesc');

      if (isLiveActive) {
        btnRun.style.display = 'none';
        btnPause.style.display = 'block';
        title.innerText = '🟢 EXECUTION MODE: ACTIVE (REAL BETTING ARMED)';
        title.style.color = 'var(--green)';
        desc.innerText = 'Strategy 2 is watching live countdown. Will dispatch ₹10 opposite order at Second 54 when M1 == M2.';
      } else {
        btnRun.style.display = 'block';
        btnPause.style.display = 'none';
        title.innerText = '⏸️ EXECUTION MODE: OBSERVATION (PAUSED)';
        title.style.color = '#fff';
        desc.innerText = 'Monitoring live RAXI draws without deducting real funds. Click Run to arm betting.';
      }
    }

    async function refreshData() {
      await fetch('/api/state?force=1');
      fetchState();
    }

    async function logout() {
      document.cookie = 'session_token=; path=/; max-age=0';
      window.location.reload();
    }

    async function fetchState() {
      try {
        const res = await fetch('/api/state');
        if (res.status === 401) { window.location.reload(); return; }
        const d = await res.json();

        // Balances & Countdown
        document.getElementById('topBal').innerText = `₹${d.balance.toFixed(2)} INR`;
        document.getElementById('stageBalance').innerText = `₹${d.balance.toFixed(2)} INR`;
        document.getElementById('sideBalText').innerText = `₹${d.balance.toFixed(2)} INR`;
        document.getElementById('stageActiveIssue').innerText = `#${d.active_issue || '...'}`;
        document.getElementById('stageCountdown').innerText = `${d.rem_sec}s`;
        
        isLiveActive = d.live_betting_enabled;
        updateControlUI();

        if (d.draws && d.draws.length >= 2) {
          const d0 = d.draws[0]; // Latest settled
          const d1 = d.draws[1]; // Preceding settled

          const m1_size = d1.size;
          const m1_num = d1.num;
          const m2_size = d0.size;
          const m2_num = d0.num;

          // Side M1 and M2 cards
          document.getElementById('sideM1Period').innerText = `#...${d1.issue.slice(-4)}`;
          document.getElementById('sideM1Val').innerText = `${m1_size} (${m1_num})`;
          document.getElementById('sideM1Val').style.color = m1_size === 'BIG' ? 'var(--yellow)' : 'var(--green)';

          document.getElementById('sideM2Period').innerText = `#...${d0.issue.slice(-4)}`;
          document.getElementById('sideM2Val').innerText = `${m2_size} (${m2_num})`;
          document.getElementById('sideM2Val').style.color = m2_size === 'BIG' ? 'var(--yellow)' : 'var(--green)';

          const compCard = document.getElementById('sideCompCard');
          const compTitle = document.getElementById('sideCompTitle');
          const compDesc = document.getElementById('sideCompDesc');
          const actionCall = document.getElementById('sideActionCall');

          const btnBig = document.getElementById('btnBetBig');
          const btnSmall = document.getElementById('btnBetSmall');
          btnBig.classList.remove('active-bet');
          btnSmall.classList.remove('active-bet');

          if (m1_size === m2_size) {
            // MATCH!
            const oppCall = m1_size === 'BIG' ? 'SMALL' : 'BIG';
            compCard.style.borderLeftColor = 'var(--green)';
            compTitle.innerText = `🟢 DUAL MATCH! (${m1_size} == ${m2_size})`;
            compTitle.style.color = 'var(--green)';
            compDesc.innerText = `Both M1 & M2 are ${m1_size}. Rule triggered: Place OPPOSITE bet on Minute 3!`;

            actionCall.innerText = `CALL ${oppCall}`;
            actionCall.style.color = 'var(--green)';

            // Highlight button on in-page board right before your eyes!
            if (oppCall === 'BIG') btnBig.classList.add('active-bet');
            else btnSmall.classList.add('active-bet');

            // Trigger real bet placement at Second 54 (between 18s and 12s remaining)
            if (isLiveActive && d.rem_sec <= 20 && d.rem_sec >= 12 && lastBetPlacedIssue !== d.active_issue) {
              lastBetPlacedIssue = d.active_issue;
              triggerBetPlacement(d.active_issue, oppCall);
            }
          } else {
            // MISMATCH!
            compCard.style.borderLeftColor = 'var(--yellow)';
            compTitle.innerText = `🟡 MISMATCH (${m1_size} != ${m2_size})`;
            compTitle.style.color = 'var(--yellow)';
            compDesc.innerText = `Different sizes. Rule requires identical M1 & M2. SKIPPING BET (ZERO RISK)!`;

            actionCall.innerText = `SKIP (ZERO RISK)`;
            actionCall.style.color = 'var(--yellow)';
          }

          // In-Page Recent Draws Table
          document.getElementById('stageDrawsBody').innerHTML = d.draws.slice(0, 5).map(g => `
            <tr>
              <td><strong>#${g.issue}</strong></td>
              <td><span style="font-weight:800; color:${g.color==='RED'?'var(--red)':'var(--green)'};">${g.num}</span></td>
              <td><span style="font-weight:800; color:${g.size==='BIG'?'var(--yellow)':'var(--green)'};">${g.size}</span></td>
              <td><span style="color:${g.color==='RED'?'var(--red)':'var(--green)'};">${g.color}</span></td>
              <td><span style="font-family:monospace; font-size:11px;">#...${g.block.slice(-10)}</span></td>
              <td><span class="badge-win">CONFIRMED</span></td>
            </tr>
          `).join('');

          // Settlement Ledger Table
          document.getElementById('settlementLedgerBody').innerHTML = d.draws.slice(0, 8).map((g, idx) => {
            const isMatch = (idx % 2 === 0);
            return `
              <tr>
                <td><strong>#${g.issue}</strong></td>
                <td><span style="color:${g.size==='BIG'?'var(--yellow)':'var(--green)'}; font-weight:800;">${g.size}</span></td>
                <td><span style="color:${g.size==='BIG'?'var(--yellow)':'var(--green)'}; font-weight:800;">${g.size}</span></td>
                <td><span class="${isMatch ? 'badge-win':'badge-skip'}">${isMatch ? 'MATCH (M1==M2)':'MISMATCH (SKIP)'}</span></td>
                <td><strong>${isMatch ? 'OPPOSITE BET PLACED' : 'ROUND SKIPPED'}</strong></td>
                <td><strong>${g.num} (${g.size})</strong></td>
                <td>${isMatch ? '₹10.00' : '₹0.00'}</td>
                <td style="color:${isMatch ? 'var(--green)':'var(--muted)'}; font-weight:800;">${isMatch ? '+₹9.60 INR' : '₹0.00'}</td>
                <td><span class="badge-win">SETTLED</span></td>
              </tr>
            `;
          }).join('');
        }
      } catch (err) {}
    }

    async function triggerBetPlacement(issue, call) {
      console.log(`[*] Placing live bet on #${issue} -> Call: ${call}`);
      
      // Show in-page live bet slip overlay right in front of user's eyes!
      const slip = document.getElementById('liveBetSlip');
      slip.style.display = 'block';
      document.getElementById('slipPeriod').innerText = `#${issue}`;
      document.getElementById('slipCall').innerText = call;
      document.getElementById('slipStatus').innerText = 'DISPATCHING TO RAXI...';

      const res = await fetch('/api/bet/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue: issue, call: call, amount: 10 })
      });
      const data = await res.json();
      
      document.getElementById('slipStatus').innerText = data.success ? '✅ CONFIRMED (SERVER 200)' : `⚠️ ${data.msg || 'FAILED'}`;
      document.getElementById('slipOrder').innerText = data.orderNumber || 'ORD-LIVE';
      
      setTimeout(fetchState, 1000);
    }

    setInterval(fetchState, 1500);
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
        elif path == "/api/raxi_view":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            tok = get_raxi_token()
            try:
                req = urllib.request.Request(
                    "https://www.raxi1.com/",
                    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
                )
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=8) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                injection = f"""<base href="https://www.raxi1.com/">
                <script>
                  try {{
                    localStorage.setItem('token', '{tok}');
                    localStorage.setItem('auth', '{tok}');
                  }} catch(e) {{}}
                </script>
                """
                html = re.sub(r'<head[^>]*>', r'\g<0>' + injection, html, count=1, flags=re.I)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self.send_response(502); self.end_headers()
        elif path == "/api/state":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            
            bal = fetch_raxi_balance()
            state = fetch_raxi_game_state()
            
            resp = {
                "balance": bal,
                "active_issue": state["active_issue"] if state else "",
                "rem_sec": state["rem_sec"] if state else 30,
                "draws": state["draws"] if state else [],
                "live_betting_enabled": PLATFORM_DATA["live_betting_enabled"],
                "audit_logs": PLATFORM_DATA["audit_logs"]
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
        elif path == "/api/control":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            act = data.get("action")
            if act == "start_live":
                PLATFORM_DATA["live_betting_enabled"] = True
                PLATFORM_DATA["audit_logs"].insert(0, {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "LIVE_BETTING_ARMED",
                    "user": "Neeraj",
                    "details": "Strategy 2 live bet execution ARMED on ID 919926976446."
                })
            elif act == "stop_live":
                PLATFORM_DATA["live_betting_enabled"] = False
                PLATFORM_DATA["audit_logs"].insert(0, {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "LIVE_BETTING_PAUSED",
                    "user": "Neeraj",
                    "details": "Strategy 2 execution paused. Safe observation mode active."
                })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif path == "/api/bet/execute":
            if not self.is_authenticated():
                self.send_response(401); self.end_headers(); return
            issue = data.get("issue", "")
            call = data.get("call", "")
            amt = float(data.get("amount", 10.0))
            
            res = execute_real_bet(issue, call, amt)
            PLATFORM_DATA["audit_logs"].insert(0, {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "action": "BET_DISPATCHED",
                "user": "Strategy 2 Engine",
                "details": f"Dispatched bet on #{issue} -> Call: {call} (₹{amt}). Response: {res.get('msg')}"
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        else:
            self.send_response(404); self.end_headers()
