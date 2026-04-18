"""
Crypto Grid Bot — Unified Server

Trading API + Dashboard + Background Trading Loop
Single process, no Telegram code.

Usage:
    python server.py                    # Start server (port 8000)
    python server.py --init             # Initialize grids then start
    python server.py --port 8080        # Custom port
"""
import os
import sys
import time
import json
import asyncio
import logging
import argparse
from datetime import datetime
from contextlib import asynccontextmanager

import ccxt
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from config import EXECUTION_CONFIG, DEFAULT_CONFIG, get_config_for_user
from utils import exchange as ex_mod, database
from utils.crypto import encrypt_value, decrypt_value
from utils.ai_advisor import analyze_market, generate_daily_briefing
from strategies import grid, dca

logging.basicConfig(
    level=getattr(logging, EXECUTION_CONFIG.get("log_level", "INFO")),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("server")

# ==================== State ====================

_balance_cache = {}  # account_id -> {data, ts}
CACHE_TTL = 60


def _get_exchange_for_account(acct):
    return ex_mod.get_exchange_for_account(
        decrypt_value(acct["api_key_enc"]),
        decrypt_value(acct["secret_enc"]),
        decrypt_value(acct["passphrase_enc"]),
        bool(acct["demo_mode"]),
    )


def _get_balance_cached(acct):
    aid = acct["id"]
    now = time.time()
    if aid in _balance_cache and now - _balance_cache[aid]["ts"] < CACHE_TTL:
        return _balance_cache[aid]["data"]
    try:
        ex = _get_exchange_for_account(acct)
        usdt = ex_mod.get_balance(ex, "USDT")
        btc = ex_mod.get_balance(ex, "BTC")
        eth = ex_mod.get_balance(ex, "ETH")
        bp = ex_mod.get_ticker_price(ex, "BTC/USDT")
        ep = ex_mod.get_ticker_price(ex, "ETH/USDT")
        data = {"usdt": usdt, "btc": btc, "eth": eth, "btc_price": bp, "eth_price": ep,
                "total": usdt + btc * bp + eth * ep, "error": None}
    except Exception as e:
        data = {"usdt": 0, "btc": 0, "eth": 0, "btc_price": 0, "eth_price": 0, "total": 0, "error": str(e)}
    _balance_cache[aid] = {"data": data, "ts": now}
    return data


# ==================== Background Trading Loop ====================

async def trading_loop():
    """Background task: grid check + DCA + AI analysis."""
    logger.info("Trading loop started")
    last_dca = 0
    last_ai = 0
    prev_btc = prev_eth = None

    while True:
        try:
            now = time.time()

            # AI market analysis every 15 min
            if now - last_ai > 900:
                try:
                    pub = ccxt.okx({"enableRateLimit": True})
                    bt = pub.fetch_ticker("BTC/USDT")
                    et = pub.fetch_ticker("ETH/USDT")
                    result = analyze_market(bt["last"], et["last"], bt.get("percentage"), et.get("percentage"))
                    if result:
                        risk = result.get("risk_level", "MEDIUM")
                        logger.info(f"🤖 AI: risk={risk} | {result.get('market_outlook', '')}")
                        database.log_command("system", "AI", "/analyze",
                                           f"BTC=${bt['last']:,.0f} ETH=${et['last']:,.0f}",
                                           f"risk={risk}")
                    prev_btc, prev_eth = bt["last"], et["last"]
                    last_ai = now
                except Exception as e:
                    logger.error(f"AI analysis: {e}")

            # Grid checks every 60s
            users = database.get_all_active_users()
            for user in users:
                config = get_config_for_user(user["id"])
                for acct in database.get_accounts_for_user(user["id"]):
                    try:
                        ex = _get_exchange_for_account(acct)
                        if config.get("btc_grid", {}).get("enabled"):
                            grid.run_grid(ex, config["btc_grid"], acct["id"])
                        if config.get("eth_grid", {}).get("enabled"):
                            grid.run_grid(ex, config["eth_grid"], acct["id"])
                    except Exception as e:
                        logger.error(f"Grid error acct {acct['id']}: {e}")

            # DCA every hour
            if now - last_dca > 3600:
                for user in users:
                    config = get_config_for_user(user["id"])
                    for acct in database.get_accounts_for_user(user["id"]):
                        try:
                            ex = _get_exchange_for_account(acct)
                            dca.run_dca(ex, config.get("dca", {}), acct["id"])
                        except Exception as e:
                            logger.error(f"DCA error acct {acct['id']}: {e}")
                last_dca = now

        except Exception as e:
            logger.error(f"Trading loop error: {e}", exc_info=True)

        await asyncio.sleep(EXECUTION_CONFIG.get("check_interval_seconds", 60))


# ==================== App Lifecycle ====================

@asynccontextmanager
async def lifespan(app):
    # Startup
    database.init_db()
    database.ensure_admin_user()

    # Register main OKX account
    api_key = os.getenv("OKX_API_KEY")
    secret = os.getenv("OKX_SECRET_KEY")
    passphrase = os.getenv("OKX_PASSPHRASE")
    demo = os.getenv("OKX_DEMO_MODE", "1") == "1"
    if all([api_key, secret, passphrase]):
        acct_id = database.register_main_account(
            encrypt_value(api_key), encrypt_value(secret),
            encrypt_value(passphrase), int(demo))
        admin = database.get_user_by_username("admin")
        if admin:
            conn = database._conn()
            c = conn.cursor()
            c.execute("UPDATE accounts SET user_id = ? WHERE id = ? AND user_id IS NULL", (admin["id"], acct_id))
            conn.commit()
            conn.close()

    # Start trading loop
    task = asyncio.create_task(trading_loop())
    logger.info("Server started")

    yield

    # Shutdown
    task.cancel()
    logger.info("Server stopped")


# ==================== FastAPI App ====================

app = FastAPI(title="Crypto Grid Bot", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("ENCRYPTION_KEY", "fallback"))
templates = Jinja2Templates(directory="templates")


def _render(request, name, ctx=None):
    context = {"request": request}
    if ctx:
        context.update(ctx)
    return templates.TemplateResponse(request=request, name=name, context=context)


def _get_session_user(request):
    uid = request.session.get("user_id")
    return database.get_user_by_id(uid) if uid else None


# ==================== Trading API ====================

@app.get("/api/status/{user_id}")
async def api_status(user_id: int):
    accounts = database.get_accounts_for_user(user_id)
    result = []
    for acct in accounts:
        bal = _get_balance_cached(acct)
        stats = database.get_stats(acct["id"])
        result.append({
            "account_id": acct["id"], "name": acct["name"],
            "demo_mode": acct["demo_mode"],
            **bal, "stats": stats,
        })
    return {"user_id": user_id, "accounts": result}


@app.get("/api/trades/{user_id}")
async def api_trades(user_id: int, limit: int = 20):
    accounts = database.get_accounts_for_user(user_id)
    all_trades = []
    for acct in accounts:
        all_trades.extend(database.get_trades(acct["id"], limit=limit))
    all_trades.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    return {"user_id": user_id, "trades": all_trades[:limit]}


@app.get("/api/config/{user_id}")
async def api_config(user_id: int):
    config = get_config_for_user(user_id)
    return {"user_id": user_id, "config": config}


@app.post("/api/analyze")
async def api_analyze():
    try:
        pub = ccxt.okx({"enableRateLimit": True})
        bt = pub.fetch_ticker("BTC/USDT")
        et = pub.fetch_ticker("ETH/USDT")
        result = analyze_market(bt["last"], et["last"], bt.get("percentage"), et.get("percentage"))
        return {"btc_price": bt["last"], "eth_price": et["last"], "analysis": result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/grid/init/{user_id}")
async def api_grid_init(user_id: int):
    config = get_config_for_user(user_id)
    accounts = database.get_accounts_for_user(user_id)
    results = []
    for acct in accounts:
        try:
            ex = _get_exchange_for_account(acct)
            btc_orders = grid.init_grid(ex, config["btc_grid"], acct["id"]) if config["btc_grid"].get("enabled") else []
            eth_orders = grid.init_grid(ex, config["eth_grid"], acct["id"]) if config["eth_grid"].get("enabled") else []
            results.append({"account": acct["name"], "btc_orders": len(btc_orders), "eth_orders": len(eth_orders)})
        except Exception as e:
            results.append({"account": acct["name"], "error": str(e)})
    return {"results": results}


@app.post("/api/grid/stop/{user_id}")
async def api_grid_stop(user_id: int):
    accounts = database.get_accounts_for_user(user_id)
    cancelled = 0
    for acct in accounts:
        try:
            ex = _get_exchange_for_account(acct)
            for symbol in ["BTC/USDT", "ETH/USDT"]:
                orders = ex_mod.get_open_orders(ex, symbol)
                for o in orders:
                    ex_mod.cancel_order(ex, o["id"], symbol)
                    cancelled += 1
        except Exception as e:
            logger.error(f"Stop error: {e}")
    return {"cancelled": cancelled}


@app.get("/api/commands")
async def api_commands(limit: int = 100, user_id: int = None):
    logs = database.get_command_logs(limit=limit, user_id=user_id)
    return {"logs": logs}


# ==================== Dashboard Auth ====================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return _render(request, "login.html", {"error": False})


@app.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    user = database.authenticate_user(username, password)
    if user:
        request.session["user_id"] = user["id"]
        request.session["is_admin"] = bool(user["is_admin"])
        return RedirectResponse("/admin/users" if user["is_admin"] else "/", status_code=302)
    return _render(request, "login.html", {"error": True})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ==================== User Dashboard ====================

@app.get("/", response_class=HTMLResponse)
async def user_home(request: Request):
    user = _get_session_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    if user["is_admin"]:
        return RedirectResponse("/admin/users", status_code=302)

    accounts = database.get_accounts_for_user(user["id"])
    for acct in accounts:
        acct["balance"] = _get_balance_cached(acct)
        acct["stats"] = database.get_stats(acct["id"])

    all_trades = []
    for acct in accounts:
        all_trades.extend(database.get_trades(acct["id"], limit=20))
    all_trades.sort(key=lambda t: t.get("created_at", ""), reverse=True)

    config = get_config_for_user(user["id"])
    return _render(request, "user_dashboard.html", {
        "user": user, "accounts": accounts, "trades": all_trades[:20], "config": config,
    })


# ==================== Admin Dashboard ====================

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    user = _get_session_user(request)
    if not user or not user["is_admin"]:
        return RedirectResponse("/login", status_code=302)
    users = database.get_all_active_users()
    for u in users:
        u["account_count"] = len(database.get_accounts_for_user(u["id"]))
    return _render(request, "admin/users.html", {"users": users})


@app.get("/admin/users/new", response_class=HTMLResponse)
async def admin_user_new(request: Request):
    user = _get_session_user(request)
    if not user or not user["is_admin"]:
        return RedirectResponse("/login", status_code=302)
    return _render(request, "admin/user_form.html", {
        "edit_mode": False, "user": {}, "config": DEFAULT_CONFIG, "error": None, "acct_demo": True,
    })


@app.post("/admin/users/new")
async def admin_user_create(request: Request,
                            username: str = Form(...), password: str = Form(...),
                            display_name: str = Form(""), bot_token: str = Form(""),
                            okx_api_key: str = Form(""), okx_secret: str = Form(""),
                            okx_passphrase: str = Form(""), demo_mode: str = Form("1"),
                            btc_lower: int = Form(62000), btc_upper: int = Form(90000),
                            btc_grids: int = Form(10), btc_order_size: int = Form(50),
                            btc_stop: int = Form(55000),
                            eth_lower: int = Form(1800), eth_upper: int = Form(3000),
                            eth_grids: int = Form(10), eth_order_size: int = Form(30),
                            eth_stop: int = Form(1600),
                            dca_btc: int = Form(10), dca_eth: int = Form(6)):
    admin = _get_session_user(request)
    if not admin or not admin["is_admin"]:
        return RedirectResponse("/login", status_code=302)

    if database.get_user_by_username(username):
        return _render(request, "admin/user_form.html", {
            "edit_mode": False, "user": {"username": username}, "config": DEFAULT_CONFIG,
            "error": f"用户名 '{username}' 已存在", "acct_demo": True,
        })

    bot_enc = encrypt_value(bot_token) if bot_token else ""
    uid = database.create_user(username, password, display_name, bot_enc)

    if okx_api_key and okx_secret and okx_passphrase:
        database.add_account(f"{username}'s OKX",
                            encrypt_value(okx_api_key), encrypt_value(okx_secret),
                            encrypt_value(okx_passphrase), int(demo_mode), user_id=uid)

    config = {
        "btc_grid": {"symbol": "BTC/USDT", "enabled": True, "lower_price": btc_lower,
                     "upper_price": btc_upper, "grid_count": btc_grids,
                     "order_size_usdt": btc_order_size, "total_investment": btc_grids * btc_order_size,
                     "max_open_orders": btc_grids, "stop_loss_price": btc_stop, "take_profit_price": None},
        "eth_grid": {"symbol": "ETH/USDT", "enabled": True, "lower_price": eth_lower,
                     "upper_price": eth_upper, "grid_count": eth_grids,
                     "order_size_usdt": eth_order_size, "total_investment": eth_grids * eth_order_size,
                     "max_open_orders": eth_grids, "stop_loss_price": eth_stop, "take_profit_price": None},
        "dca": {"enabled": True, "positions": [
            {"symbol": "BTC/USDT", "amount_usdt": dca_btc, "interval_hours": 24},
            {"symbol": "ETH/USDT", "amount_usdt": dca_eth, "interval_hours": 24}],
            "buy_on_dip_only": False, "dip_threshold_pct": 0},
    }
    database.save_user_config(uid, config)
    return RedirectResponse("/admin/users", status_code=302)


@app.get("/admin/users/{user_id}/edit", response_class=HTMLResponse)
async def admin_user_edit(request: Request, user_id: int):
    admin = _get_session_user(request)
    if not admin or not admin["is_admin"]:
        return RedirectResponse("/login", status_code=302)
    user = database.get_user_by_id(user_id)
    if not user:
        return HTMLResponse("Not found", 404)
    config = get_config_for_user(user_id)
    accounts = database.get_accounts_for_user(user_id)
    return _render(request, "admin/user_form.html", {
        "edit_mode": True, "user": user, "config": config, "error": None,
        "acct_demo": accounts[0]["demo_mode"] if accounts else True,
    })


@app.post("/admin/users/{user_id}/edit")
async def admin_user_update(request: Request, user_id: int,
                            username: str = Form(""), password: str = Form(""),
                            display_name: str = Form(""), bot_token: str = Form(""),
                            okx_api_key: str = Form(""), okx_secret: str = Form(""),
                            okx_passphrase: str = Form(""), demo_mode: str = Form("1"),
                            btc_lower: int = Form(62000), btc_upper: int = Form(90000),
                            btc_grids: int = Form(10), btc_order_size: int = Form(50),
                            btc_stop: int = Form(55000),
                            eth_lower: int = Form(1800), eth_upper: int = Form(3000),
                            eth_grids: int = Form(10), eth_order_size: int = Form(30),
                            eth_stop: int = Form(1600),
                            dca_btc: int = Form(10), dca_eth: int = Form(6)):
    admin = _get_session_user(request)
    if not admin or not admin["is_admin"]:
        return RedirectResponse("/login", status_code=302)

    conn = database._conn()
    c = conn.cursor()
    if password:
        c.execute("UPDATE users SET display_name=?, password_hash=? WHERE id=?",
                  (display_name, database._hash_password(password), user_id))
    else:
        c.execute("UPDATE users SET display_name=? WHERE id=?", (display_name, user_id))
    if bot_token and bot_token != "[已配置]":
        c.execute("UPDATE users SET telegram_bot_token_enc=? WHERE id=?", (encrypt_value(bot_token), user_id))
    conn.commit()
    conn.close()

    if okx_api_key and okx_secret and okx_passphrase:
        accounts = database.get_accounts_for_user(user_id)
        if accounts:
            conn = database._conn()
            c = conn.cursor()
            c.execute("UPDATE accounts SET api_key_enc=?, secret_enc=?, passphrase_enc=?, demo_mode=? WHERE id=?",
                      (encrypt_value(okx_api_key), encrypt_value(okx_secret),
                       encrypt_value(okx_passphrase), int(demo_mode), accounts[0]["id"]))
            conn.commit()
            conn.close()
        else:
            database.add_account(f"{username}'s OKX", encrypt_value(okx_api_key),
                                encrypt_value(okx_secret), encrypt_value(okx_passphrase),
                                int(demo_mode), user_id)

    config = {
        "btc_grid": {"symbol": "BTC/USDT", "enabled": True, "lower_price": btc_lower,
                     "upper_price": btc_upper, "grid_count": btc_grids,
                     "order_size_usdt": btc_order_size, "total_investment": btc_grids * btc_order_size,
                     "max_open_orders": btc_grids, "stop_loss_price": btc_stop, "take_profit_price": None},
        "eth_grid": {"symbol": "ETH/USDT", "enabled": True, "lower_price": eth_lower,
                     "upper_price": eth_upper, "grid_count": eth_grids,
                     "order_size_usdt": eth_order_size, "total_investment": eth_grids * eth_order_size,
                     "max_open_orders": eth_grids, "stop_loss_price": eth_stop, "take_profit_price": None},
        "dca": {"enabled": True, "positions": [
            {"symbol": "BTC/USDT", "amount_usdt": dca_btc, "interval_hours": 24},
            {"symbol": "ETH/USDT", "amount_usdt": dca_eth, "interval_hours": 24}],
            "buy_on_dip_only": False, "dip_threshold_pct": 0},
    }
    database.save_user_config(user_id, config)
    return RedirectResponse("/admin/users", status_code=302)


@app.get("/admin/users/{user_id}/delete")
async def admin_user_delete(request: Request, user_id: int):
    admin = _get_session_user(request)
    if not admin or not admin["is_admin"]:
        return RedirectResponse("/login", status_code=302)
    database.deactivate_user(user_id)
    return RedirectResponse("/admin/users", status_code=302)


@app.get("/admin/commands", response_class=HTMLResponse)
async def admin_commands(request: Request):
    admin = _get_session_user(request)
    if not admin or not admin["is_admin"]:
        return RedirectResponse("/login", status_code=302)
    logs = database.get_command_logs(limit=200)
    return _render(request, "commands.html", {"logs": logs})


# HTMX partial
@app.get("/api/dashboard/accounts", response_class=HTMLResponse)
async def htmx_accounts(request: Request):
    user = _get_session_user(request)
    if not user:
        return HTMLResponse("Unauthorized", 401)
    accounts = database.get_all_active_accounts() if user["is_admin"] else database.get_accounts_for_user(user["id"])
    grand_total = btc_price = eth_price = 0
    enriched = []
    for acct in accounts:
        bal = _get_balance_cached(acct)
        d = dict(acct)
        d.update(bal)
        d["stats"] = database.get_stats(acct["id"])
        enriched.append(d)
        grand_total += bal["total"]
        if bal["btc_price"]:
            btc_price, eth_price = bal["btc_price"], bal["eth_price"]
    return _render(request, "partials/accounts.html", {
        "accounts": enriched, "grand_total": grand_total,
        "btc_price": btc_price, "eth_price": eth_price,
        "updated_at": datetime.now().strftime("%H:%M:%S"),
    })


# ==================== Run ====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()

    if args.init:
        database.init_db()
        database.ensure_admin_user()
        logger.info("Database initialized. Grids will be initialized on startup.")

    uvicorn.run(app, host="0.0.0.0", port=args.port)
