#!/usr/bin/env python3
# bot_multi_stealth.py - BOT MULTIACCOUNT CON STEALTH

import os
import asyncio
import time
import random
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright

# ============================================================
# CONFIGURAZIONE - 6 ACCOUNT CON PROXY DIVERSI (AGGIORNATI)
# ============================================================

HEADLESS = True

# 🔥 6 ACCOUNT - TUTTI CON PROXY DIVERSI (3 NUOVI!)
ACCOUNTS = [
    # 🔥 SOSTITUITI CON PROXY NUOVI
    {
        "email": "ninodellarocca@yahoo.com",
        "password": "UF45$!dama",
        "proxy": "cm3gl0eyljem:yyb9w8s8n90a0yz@104.207.62.14:3129"
    },
    {
        "email": "marcogiacchetti@yahoo.com",
        "password": "LGZE45$!tm",
        "proxy": "cm3gl0eyljem:yyb9w8s8n90a0yz@216.26.238.47:3129"
    },
    {
        "email": "nicolavigilebari@tiscali.it",
        "password": "RM56$!RRTT",
        "proxy": "cm3gl0eyljem:yyb9w8s8n90a0yz@216.26.231.167:3129"
    },
    # ✅ QUESTI GIA' FUNZIONANO
    {
        "email": "valentinamirgione1245@gmail.com",
        "password": "UL2454ZM!!ug",
        "proxy": "cm3gl0eyljem:yyb9w8s8n90a0yz@45.3.37.230:3129"
    },
    {
        "email": "pinorenettideluigini@tiscali.it",
        "password": "YH6595ma!!",
        "proxy": "cm3gl0eyljem:yyb9w8s8n90a0yz@65.111.24.17:3129"
    },
    {
        "email": "legadilettantibarattini@libero.it",
        "password": "MZ45$!avanx",
        "proxy": "cm3gl0eyljem:yyb9w8s8n90a0yz@216.26.228.26:3129"
    }
]

# ============================================================
# STEALTH JS - NASCONDI L'AUTOMAZIONE
# ============================================================

STEALTH_JS = """
// Nascondi webdriver
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Plugin finti
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// Lingue
Object.defineProperty(navigator, 'languages', {
    get: () => ['it-IT', 'it', 'en-US', 'en']
});

// Chrome
window.chrome = {
    runtime: {}
};

// Permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);
"""

# ============================================================
# LOGGING
# ============================================================

def log(email, msg):
    prefix = email[:10] if email else "SISTEMA"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{prefix}...] {msg}", flush=True)

# ============================================================
# PARSE PROXY
# ============================================================

def parse_proxy(proxy_str):
    try:
        auth, host = proxy_str.split('@')
        user, password = auth.split(':')
        return {
            "server": f"http://{host}",
            "username": user,
            "password": password
        }
    except:
        return None

# ============================================================
# MOVIMENTI UMANI
# ============================================================

async def movimenti_umani(page):
    """Simula movimenti umani casuali"""
    try:
        x = random.randint(100, 800)
        y = random.randint(100, 500)
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        await asyncio.sleep(random.uniform(0.1, 0.5))
    except:
        pass

# ============================================================
# PULISCI URL
# ============================================================

def pulisci_url(url):
    url = re.sub(r'<[^>]+>', '', url)
    url = url.strip()
    url = re.sub(r'[<>\'"]', '', url)
    return url

def pulisci_ad_id(ad_id):
    ad_id = re.sub(r'<[^>]+>', '', ad_id)
    ad_id = re.sub(r'[<>\'"]', '', ad_id)
    match = re.search(r'(\d+)', ad_id)
    if match:
        return match.group(1)
    return ad_id

# ============================================================
# GESTISCI UN ACCOUNT
# ============================================================

async def gestisci_account(account_data):
    email = account_data["email"]
    password = account_data["password"]
    proxy_str = account_data["proxy"]
    
    log(email, "🚀 Avvio account...")
    
    proxy_config = parse_proxy(proxy_str)
    if not proxy_config:
        log(email, "❌ Proxy non valido!")
        return
    
    log(email, f"🌐 Proxy: {proxy_str.split('@')[1] if '@' in proxy_str else proxy_str}")
    
    # User-Agent reale
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Argomenti anti-rilevamento
    args = [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            proxy=proxy_config,
            args=args
        )
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1366, 'height': 768}
        )
        
        page = await context.new_page()
        
        # Inietta stealth
        await page.add_init_script(STEALTH_JS)
        
        try:
            # ============================================================
            # LOGIN
            # ============================================================
            log(email, "📧 Login...")
            await page.goto("https://antautosurf.com/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(2, 3))
            
            await movimenti_umani(page)
            
            await page.fill('input[name="bitcoinwallet"]', email)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            await page.click('input[type="submit"][value*="Enter"]')
            await asyncio.sleep(random.uniform(3, 5))
            
            html = await page.content()
            
            if "Please enter Password" in html:
                log(email, "🔑 Login con password...")
                await page.fill('input[name="password"]', password)
                await asyncio.sleep(random.uniform(0.5, 1.0))
                await page.click('input[value="Enter"]')
                await asyncio.sleep(random.uniform(3, 5))
                html = await page.content()
            
            log(email, "✅ Login completato!")
            
            # ============================================================
            # DASHBOARD - ATTESA PIÙ LUNGA
            # ============================================================
            log(email, "📊 Dashboard...")
            await page.goto(
                f"https://antautosurf.com/index.php?bitcoinwallet={email}&ref=",
                wait_until="domcontentloaded",
                timeout=60000
            )
            await asyncio.sleep(5)  # Attesa più lunga per caricare tutto
            
            html = await page.content()
            
            # CAPTCHA
            if "Please Click Similar" in html:
                log(email, "⚠️ CAPTCHA RILEVATO!")
                cids = [int(x) for x in re.findall(r'cid=(\d+)', html)]
                for cid in list(set(cids)):
                    await page.goto(f"https://antautosurf.com/index.php?cid={cid}")
                    await asyncio.sleep(2)
                    html_test = await page.content()
                    if "Please Click Similar" not in html_test:
                        log(email, f"   ✅ CAPTCHA RISOLTO! CID: {cid}")
                        break
                await asyncio.sleep(2)
                html = await page.content()
            
            # BALANCE
            balance_match = re.search(r'btoday["\']?\s*[=:]\s*([\d.]+)', html)
            if balance_match:
                log(email, f"💰 Balance: {balance_match.group(1)}")
            
            # CSRF
            csrf_match = re.search(r'csrf_token=([a-f0-9]+)', html)
            if not csrf_match:
                log(email, "❌ CSRF non trovato! Riprovo...")
                # Ricarica dashboard
                await page.goto(
                    f"https://antautosurf.com/index.php?bitcoinwallet={email}&ref=",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                await asyncio.sleep(3)
                html = await page.content()
                csrf_match = re.search(r'csrf_token=([a-f0-9]+)', html)
                if not csrf_match:
                    log(email, "❌ CSRF non trovato dopo secondo tentativo!")
                    return
            
            csrf = csrf_match.group(1)
            log(email, f"🎫 CSRF: {csrf[:16]}...")
            
            # ============================================================
            # SURF
            # ============================================================
            log(email, "🚀 Avvio surf...")
            
            key = ""
            time_val = 12
            ad_id = ""
            cycle = 0
            MAX_CYCLES = 10
            csrf_invalidi = 0
            MAX_CSRF_INVALIDI = 5
            
            while cycle < MAX_CYCLES:
                cycle += 1
                log(email, f"🔄 CICLO {cycle}")
                
                if ad_id:
                    ad_id_pulito = pulisci_ad_id(ad_id)
                else:
                    ad_id_pulito = ""
                
                params = {
                    "wallet": email,
                    "key": key,
                    "time": time_val,
                    "ad_id": ad_id_pulito,
                    "isitbad": 0,
                    "csrf_token": csrf
                }
                
                url = "https://antautosurf.com/surf.php?" + "&".join([f"{k}={v}" for k, v in params.items()])
                
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                except Exception as e:
                    log(email, f"⚠️ Errore goto: {e}")
                    await asyncio.sleep(5)
                    continue
                
                page_text = await page.content()
                
                if "Invalid CSRF token" in page_text:
                    csrf_invalidi += 1
                    log(email, f"❌ CSRF invalido! ({csrf_invalidi}/{MAX_CSRF_INVALIDI})")
                    
                    if csrf_invalidi >= MAX_CSRF_INVALIDI:
                        log(email, "🔄 Troppi CSRF invalidi!")
                        break
                    
                    await page.goto(
                        f"https://antautosurf.com/index.php?bitcoinwallet={email}&ref=",
                        wait_until="domcontentloaded",
                        timeout=60000
                    )
                    await asyncio.sleep(3)
                    html = await page.content()
                    csrf_match = re.search(r'csrf_token=([a-f0-9]+)', html)
                    if csrf_match:
                        csrf = csrf_match.group(1)
                        csrf_invalidi = 0
                        log(email, f"🎫 Nuovo CSRF: {csrf[:16]}...")
                    continue
                else:
                    csrf_invalidi = 0
                
                if "--_--" not in page_text:
                    await asyncio.sleep(5)
                    continue
                
                parts = page_text.split("--_--")
                if len(parts) < 4:
                    continue
                
                ad_url = pulisci_url(parts[0])
                time_val = int(parts[1])  # 🔥 Timer dalla response!
                key = parts[2]
                ad_id = parts[3]
                
                if "connection.php" in ad_url:
                    log(email, "   📂 Test anti-bot...")
                    try:
                        await page.goto(ad_url, wait_until="domcontentloaded", timeout=30000)
                    except:
                        pass
                    for i in range(time_val, 0, -1):
                        print(f"   ⏳ {i}s", end="\r")
                        await asyncio.sleep(1)
                    print("   " * 20, end="\r")
                    continue
                
                log(email, f"   📢 Annuncio reale! Timer: {time_val}s")
                
                try:
                    new_page = await context.new_page()
                    await new_page.goto(ad_url, wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(1)
                except Exception as e:
                    log(email, f"   ⚠️ Errore apertura: {e}")
                
                for i in range(time_val, 0, -1):
                    print(f"   ⏳ {i}s", end="\r")
                    await asyncio.sleep(1)
                print("   " * 20, end="\r")
                log(email, f"   ✅ Timer completato!")
                
                try:
                    await new_page.close()
                except:
                    pass
                
                if cycle % 3 == 0:
                    await page.goto(
                        f"https://antautosurf.com/index.php?bitcoinwallet={email}&ref=",
                        wait_until="domcontentloaded",
                        timeout=60000
                    )
                    await asyncio.sleep(2)
                    html = await page.content()
                    csrf_match = re.search(r'csrf_token=([a-f0-9]+)', html)
                    if csrf_match:
                        csrf = csrf_match.group(1)
                        log(email, f"   🎫 CSRF aggiornato: {csrf[:16]}...")
            
            log(email, f"✅ Completati {MAX_CYCLES} cicli!")
            
        except Exception as e:
            log(email, f"❌ Errore: {e}")
        finally:
            await browser.close()

# ============================================================
# MAIN
# ============================================================

async def main():
    print("="*60)
    print("🚀 BOT MULTIACCOUNT CON STEALTH")
    print("="*60)
    print(f"📋 Account: {len(ACCOUNTS)}")
    print(f"🔇 Headless: {HEADLESS}")
    print("="*60)
    print("🔄 Ogni account ha il suo proxy (IP diverso!)")
    print("🔄 Ogni account fa 10 cicli, poi passa al prossimo")
    print("="*60)
    
    while True:
        for account in ACCOUNTS:
            await gestisci_account(account)
            await asyncio.sleep(5)
            print("─" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arresto manuale...")
        
