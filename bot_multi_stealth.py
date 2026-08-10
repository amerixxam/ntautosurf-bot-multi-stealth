#!/usr/bin/env python3
# bot_multi_stealth.py - BOT MULTIACCOUNT CON STEALTH E ANALISI IP

import os
import asyncio
import time
import random
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright

# ============================================================
# CONFIGURAZIONE - 6 ACCOUNT CON PROXY DIVERSI
# ============================================================

HEADLESS = True

ACCOUNTS = [
    {
        "email": "serenamilani74@gmail.com",
        "password": "4591##Pane",
        "proxy": "wlt170deuwe4:tosnprlzh5y97c6@104.167.25.19:3129"
    },
    {
        "email": "vincenzogrulli@yahoo.com",
        "password": "dave45!!MU",
        "proxy": "wlt170deuwe4:tosnprlzh5y97c6@216.26.252.21:3129"
    },
    {
        "email": "marziadelbello@tiscali.it",
        "password": "PA45$!!#na",
        "proxy": "wlt170deuwe4:tosnprlzh5y97c6@45.3.44.227:3129"
    },
    {
        "email": "paolovecchi_62@gmail.com",
        "password": "UT56$!dama",
        "proxy": "wlt170deuwe4:tosnprlzh5y97c6@216.26.232.62:3129"
    },
    {
        "email": "veronicasibrni@libero.it",
        "password": "HJGF52!!dama",
        "proxy": "wlt170deuwe4:tosnprlzh5y97c6@216.26.244.100:3129"
    },
    {
        "email": "nanniserena@virgilio.it",
        "password": "PETR$!45vu",
        "proxy": "wlt170deuwe4:tosnprlzh5y97c6@104.207.33.227:3129"
    }
]

# ============================================================
# GESTIONE IP - TRACCIA E SALVA IP BLOCCATI
# ============================================================

IP_TRACKER = {}  # { "account": {"ip": "x.x.x.x", "timestamp": "..."} }
IP_BLOCCATI_FILE = "ip_bloccati.json"

def carica_ip_bloccati():
    """Carica la lista degli IP bloccati da file"""
    try:
        with open(IP_BLOCCATI_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def salva_ip_bloccati(ip_set):
    """Salva la lista degli IP bloccati su file"""
    try:
        with open(IP_BLOCCATI_FILE, "w") as f:
            json.dump(list(ip_set), f, indent=2)
    except:
        pass

# Carica IP bloccati all'avvio
IP_BLOCCATI = carica_ip_bloccati()
print(f"📊 Caricati {len(IP_BLOCCATI)} IP bloccati da file")

async def ottieni_ip_attuale(page):
    """Ottiene l'IP attuale del browser"""
    try:
        await page.goto("https://api.ipify.org?format=json", wait_until="domcontentloaded", timeout=10000)
        content = await page.content()
        match = re.search(r'"ip":"([^"]+)"', content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"⚠️ Errore rilevamento IP: {e}")
    return None

async def registra_ip(email, ip):
    """Registra l'IP usato per un account e controlla duplicati"""
    if not ip:
        return
    
    IP_TRACKER[email] = {
        "ip": ip,
        "timestamp": datetime.now().isoformat()
    }
    log(email, f"📌 IP registrato: {ip}")
    
    # Controlla se lo stesso IP è usato da altri account
    ip_duplicato = False
    for other_email, data in IP_TRACKER.items():
        if other_email != email and data["ip"] == ip:
            ip_duplicato = True
            log(email, f"⚠️⚠️ STESSO IP ({ip}) usato da {other_email[:10]}! ⚠️⚠️")
    
    if ip_duplicato:
        log(email, f"❌ BLOCCO PREVISTO: Antautosurf bloccherà questo IP!")
        IP_BLOCCATI.add(ip)
        salva_ip_bloccati(IP_BLOCCATI)

async def controlla_blocco_ip(page, email):
    """Controlla se la pagina mostra un blocco per IP"""
    html = await page.content()
    
    if "This IP" in html and "already used" in html:
        match = re.search(r'This IP \((.*?)\) is already used', html)
        if match:
            ip_bloccato = match.group(1)
            log(email, f"❌❌❌ IP BLOCCATO: {ip_bloccato} ❌❌❌")
            
            IP_BLOCCATI.add(ip_bloccato)
            salva_ip_bloccati(IP_BLOCCATI)
            log(email, f"💾 IP {ip_bloccato} salvato in lista nera")
            
            for acc, data in IP_TRACKER.items():
                if data.get("ip") == ip_bloccato:
                    log(email, f"   ℹ️ Questo IP era usato da: {acc}")
            
            return True, ip_bloccato
    
    # Controlla anche il messaggio "Try again tomorrow"
    if "Try again tomorrow" in html and "different IP" in html:
        match = re.search(r'This IP \((.*?)\) is already used', html)
        if match:
            ip_bloccato = match.group(1)
            log(email, f"❌❌❌ IP BLOCCATO (try again): {ip_bloccato} ❌❌❌")
            IP_BLOCCATI.add(ip_bloccato)
            salva_ip_bloccati(IP_BLOCCATI)
            return True, ip_bloccato
    
    return False, None

def mostra_statistiche_ip():
    """Mostra statistiche sugli IP usati"""
    print("\n" + "="*60)
    print("📊 STATISTICHE IP")
    print("="*60)
    
    if not IP_TRACKER:
        print("⚠️ Nessun IP registrato")
        return
    
    ip_unici = set()
    for data in IP_TRACKER.values():
        ip_unici.add(data["ip"])
    
    print(f"📋 Account analizzati: {len(IP_TRACKER)}")
    print(f"🌐 IP unici: {len(ip_unici)}")
    print(f"🚫 IP bloccati totali: {len(IP_BLOCCATI)}")
    
    if len(ip_unici) == 1 and len(IP_TRACKER) > 1:
        print("⚠️⚠️ TUTTI GLI ACCOUNT USANO LO STESSO IP! ⚠️⚠️")
        print("   → Antautosurf li bloccherà tutti!")
    elif len(ip_unici) < len(IP_TRACKER):
        print(f"⚠️ Attenzione: {len(IP_TRACKER) - len(ip_unici)} account condividono IP")
    
    print("\n📋 Dettaglio IP per account:")
    for email, data in IP_TRACKER.items():
        ip = data["ip"]
        timestamp = data["timestamp"][:16]
        bloccato = "🔴 BLOCCATO" if ip in IP_BLOCCATI else "🟢 OK"
        print(f"   {email[:20]} → {ip} {bloccato} ({timestamp})")
    
    if IP_BLOCCATI:
        print(f"\n🚫 IP bloccati salvati: {list(IP_BLOCCATI)}")
    
    print("="*60 + "\n")

# ============================================================
# STEALTH JS - NASCONDI L'AUTOMAZIONE
# ============================================================

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
Object.defineProperty(navigator, 'languages', {
    get: () => ['it-IT', 'it', 'en-US', 'en']
});
window.chrome = { runtime: {} };
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
# RISOLUZIONE CAPTCHA
# ============================================================

def carica_database():
    try:
        with open("hash_phash_db.json", "r") as f:
            return json.load(f)
    except:
        return {}

phash_db = carica_database()

async def risolvi_captcha(page, email):
    html = await page.content()
    if "Please Click Similar" not in html:
        return True
    
    log(email, "⚠️ CAPTCHA RILEVATO!")
    
    cids = [int(x) for x in re.findall(r'cid=(\d+)', html)]
    cids_unici = list(set(cids))
    log(email, f"   📌 CID disponibili: {cids_unici}")
    
    # Prova dal database
    for stored_phash, cid in phash_db.items():
        try:
            img_element = await page.locator('img[src*="capimg.php"]').first
            img_data = await img_element.screenshot()
            from PIL import Image
            import io
            import imagehash
            img_pil = Image.open(io.BytesIO(img_data))
            phash = imagehash.phash(img_pil)
            phash_str = str(phash)
            
            diff = imagehash.hex_to_hash(phash_str) - imagehash.hex_to_hash(stored_phash)
            if diff <= 10:
                await page.goto(f"https://antautosurf.com/index.php?cid={cid}")
                await asyncio.sleep(2)
                log(email, f"   ✅ CAPTCHA RISOLTO! CID: {cid} (da database)")
                return True
        except:
            pass
    
    # Prova tutti i CID
    for cid in cids_unici:
        await page.goto(f"https://antautosurf.com/index.php?cid={cid}")
        await asyncio.sleep(2)
        html_test = await page.content()
        if "Please Click Similar" not in html_test:
            log(email, f"   ✅ CAPTCHA RISOLTO! CID: {cid}")
            return True
    
    log(email, f"   ❌ CAPTCHA NON RISOLTO!")
    return False

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
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
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
        
        await page.add_init_script(STEALTH_JS)
        
        try:
            # ============================================================
            # 🔥 ANALISI IP - PRIMA DEL LOGIN
            # ============================================================
            log(email, "🔍 Rilevamento IP...")
            ip_attuale = await ottieni_ip_attuale(page)
            if ip_attuale:
                await registra_ip(email, ip_attuale)
            else:
                log(email, "⚠️ Impossibile rilevare IP")
            
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
            
            # ============================================================
            # REGISTRAZIONE - SE NUOVO ACCOUNT
            # ============================================================
            if "Set Login Password" in html:
                log(email, "📝 NUOVO ACCOUNT! Registro...")
                
                match = re.search(r'name="confirm2" value="(\d+)"', html)
                if match:
                    confirm2 = match.group(1)
                    log(email, f"   ✅ confirm2 trovato: {confirm2}")
                    
                    await page.fill('input[name="password"]', password)
                    await page.fill('input[name="passwordb"]', password)
                    await page.goto(f"https://antautosurf.com/index.php?password={password}&passwordb={password}&confirm2={confirm2}")
                    await page.wait_for_load_state("networkidle")
                    log(email, "   ✅ Registrazione inviata!")
                    
                    await asyncio.sleep(2)
                    html = await page.content()
                    if "Please enter Password" in html:
                        log(email, "   ✅ Registrazione completata con successo!")
                    else:
                        log(email, "   ⚠️ Registrazione forse fallita, continuo...")
                else:
                    log(email, "   ❌ confirm2 NON TROVATO! Impossibile registrare.")
                    return
            
            # ============================================================
            # LOGIN CON PASSWORD
            # ============================================================
            if "Please enter Password" in html:
                log(email, "🔑 Login con password...")
                await page.fill('input[name="password"]', password)
                await asyncio.sleep(random.uniform(0.5, 1.0))
                await page.click('input[value="Enter"]')
                await asyncio.sleep(random.uniform(3, 5))
                html = await page.content()
            
            log(email, "✅ Login completato!")
            
            # ============================================================
            # DASHBOARD
            # ============================================================
            log(email, "📊 Dashboard...")
            await page.goto(
                f"https://antautosurf.com/index.php?bitcoinwallet={email}&ref=",
                wait_until="domcontentloaded",
                timeout=60000
            )
            await asyncio.sleep(5)
            
            html = await page.content()
            
            # ============================================================
            # 🔥 CONTROLLO BLOCCO IP
            # ============================================================
            bloccato, ip_bloccato = await controlla_blocco_ip(page, email)
            if bloccato:
                log(email, f"🔄 Riavvio il bot per cambiare proxy...")
                await browser.close()
                return
            
            # CAPTCHA
            if "Please Click Similar" in html:
                if not await risolvi_captcha(page, email):
                    log(email, "❌ Captcha non risolto!")
                    return
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
                time_val = int(parts[1])
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
    print("🚀 BOT MULTIACCOUNT CON STEALTH + ANALISI IP")
    print("="*60)
    print(f"📋 Account: {len(ACCOUNTS)}")
    print(f"🔇 Headless: {HEADLESS}")
    print(f"🚫 IP bloccati in lista nera: {len(IP_BLOCCATI)}")
    print("="*60)
    print("🔄 Ogni account ha il suo proxy (IP diverso!)")
    print("🔄 Ogni account fa 10 cicli, poi passa al prossimo")
    print("📊 Sistema di analisi IP attivo")
    print("🚫 Rilevamento blocchi IP attivo")
    print("="*60)
    
    while True:
        for account in ACCOUNTS:
            await gestisci_account(account)
            await asyncio.sleep(5)
            print("─" * 60)
            
        # Mostra statistiche IP dopo ogni ciclo completo
        mostra_statistiche_ip()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arresto manuale...")
        mostra_statistiche_ip()
