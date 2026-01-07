
import asyncio
import subprocess
import time
import requests
import os
import signal
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8000"
SERVER_CMD = [".venv/bin/uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
SERVER_PROCESS = None

def kill_server():
    global SERVER_PROCESS
    # Kill process group forcefully
    subprocess.run(["pkill", "-9", "-f", "uvicorn"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-9", "-f", "start_server.py"], stderr=subprocess.DEVNULL)
    if SERVER_PROCESS:
        try:
            os.killpg(os.getpgid(SERVER_PROCESS.pid), signal.SIGTERM)
        except:
            pass
    time.sleep(2)

def start_server():
    global SERVER_PROCESS
    kill_server()
    # Start new server
    SERVER_PROCESS = subprocess.Popen(
        SERVER_CMD, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    # Wait for port
    for _ in range(30):
        try:
            requests.get(f"{BASE_URL}/docs", timeout=1)
            return True
        except:
            time.sleep(1)
    return False

async def run_cold_starts():
    print("\n=== Phase 1: 5x Cold Start Tests ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i in range(5):
            print(f"  Iteration {i+1}/5: Restarting System...")
            if not start_server():
                print("  -> Server failed to start!")
                return False
            
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 1. Load Root - Should redirect to /startup or trigger it
                await page.goto(BASE_URL)
                
                # 2. Wait for Redirect or Startup UI
                # We expect either /startup URL or Dashboard with "System Bereit"
                # For a fresh start, it should go to /startup
                
                # Check where we are
                url = page.url
                if "startup" in url:
                    print("  -> Initialized Startup Sequence (Correct)")
                    # Wait for Dashboard redirect
                    await page.wait_for_url(f"{BASE_URL}/", timeout=120000) # 2 mins max
                    print("  -> Redirected to Dashboard (Success)")
                else:
                    # Maybe it was fast or already ready?
                    # Check for dashboard element
                    if await page.query_selector("text=Dashboard"):
                         print("  -> Direct Dashboard Load (Acceptable if fast)")
                    else:
                         print(f"  -> Unexpected State: {url}")
                         return False

                # Verify Dashboard Elements
                await page.wait_for_selector("text=System Bereit", timeout=5000)
                await page.wait_for_selector("text=Model Scanner", timeout=5000)
                
            except Exception as e:
                print(f"  -> Frontend Error: {e}")
                return False
                
            await context.close()
            print("  -> verified.")
            
        await browser.close()
    return True

async def run_hot_refreshes():
    print("\n=== Phase 2: 5x Hot Refresh Tests ===")
    # Server assumed running from last step
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Ensure we are on dashboard
        await page.goto(BASE_URL)
        await page.wait_for_selector("text=Dashboard")
        
        for i in range(5):
            print(f"  Iteration {i+1}/5: Refreshing...")
            t0 = time.time()
            await page.reload()
            await page.wait_for_selector("text=System Bereit", timeout=5000)
            dur = time.time() - t0
            print(f"  -> Loaded in {dur:.2f}s")
            
        await browser.close()
    return True

async def run_navigation_test():
    print("\n=== Phase 3: 5x Navigation Tests ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(BASE_URL)
        
        for i in range(5):
            print(f"  Iteration {i+1}/5: Cycle Dashboard -> Projects -> Chat...")
            
            # 1. Go to Projects
            await page.click("a[href='/projects']")
            await page.wait_for_selector("text=Förderanträge", timeout=15000)
            
            # 2. Go to Global Chat
            await page.click("a[href='/chat']")
            await page.wait_for_selector("text=Globaler Chat", timeout=5000)
            
            # 3. Back to Dashboard (Logo) -> triggers startup restart logic
            await page.click("a[href='/startup']") 
            # Redirects to / then Dashboard
            await page.wait_for_selector("text=Dashboard", timeout=10000)
            
            print("  -> verified.")
            
        await browser.close()
    return True

async def main():
    try:
        if not await run_cold_starts():
            print("COLD START FAILED")
            exit(1)
            
        if not await run_hot_refreshes():
            print("HOT REFRESH FAILED")
            exit(1)
            
        if not await run_navigation_test():
            print("NAVIGATION FAILED")
            exit(1)
            
        print("\nALL FRONTEND TESTS PASSED")
        # Cleanup
        kill_server()
        
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        kill_server()
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
