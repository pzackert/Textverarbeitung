import requests
import time
import statistics
import json
import os
import shutil
import uuid
from typing import List, Dict

BASE_URL = "http://localhost:8000/api"
DUMMY_PDF = "data/test_documents/dummy.pdf"
ITERATIONS = 5

class BenchmarkRunner:
    def __init__(self):
        self.results = []
        self._ensure_test_files()
        
    def _ensure_test_files(self):
        if not os.path.exists(DUMMY_PDF):
            os.makedirs(os.path.dirname(DUMMY_PDF), exist_ok=True)
            # Create a simple dummy PDF (mocking content for now if shutil fails)
            try:
                shutil.copy("data/projects/80a26bfc-7274-47bd-9d80-276a540b2006/documents/dummy.pdf", DUMMY_PDF)
            except:
                with open("dummy_test.txt", "w") as f:
                    f.write("Dies ist ein Testdokument für den Förderantrag. Projektkosten: 1000 Euro.")
                    
    def run_benchmark(self):
        print(f"Starting Benchmark ({ITERATIONS} iterations)...")
        print(f"Target: {BASE_URL}")
        
        for i in range(ITERATIONS):
            print(f"-- Iteration {i+1}/{ITERATIONS} --")
            metrics = self._run_single_iteration()
            if metrics:
                self.results.append(metrics)
            
            # Cleanup delay
            time.sleep(1)
            
        self._print_report()
        
    def _run_single_iteration(self) -> Dict:
        app_id = None
        metrics = {}
        
        try:
            # 1. Create App
            start = time.time()
            resp = requests.post(f"{BASE_URL}/applications", json={
                "title": f"Bench App {uuid.uuid4().hex[:6]}",
                "applicant": "Benchmarker",
                "funding_request": 5000.0
            })
            metrics["create_time"] = time.time() - start
            if resp.status_code != 200:
                print("Create failed")
                return None
            app_id = resp.json()["id"]
            
            # 2. Upload
            start = time.time()
            if os.path.exists(DUMMY_PDF):
                files = {'file': ('dummy.pdf', open(DUMMY_PDF, 'rb'))}
            else:
                 files = {'file': ('dummy.txt', open("dummy_test.txt", 'rb'))}
                 
            requests.post(f"{BASE_URL}/applications/{app_id}/documents", files=files)
            metrics["upload_time"] = time.time() - start
            
            # 3. Ingest
            start = time.time()
            requests.post(f"{BASE_URL}/applications/{app_id}/ingest")
            
            # Poll Ingest
            ingest_success = False
            for _ in range(30):
                resp = requests.get(f"{BASE_URL}/applications/{app_id}")
                if resp.json().get("rag_status") == "ready":
                    ingest_success = True
                    break
                time.sleep(1)
            metrics["ingest_time"] = time.time() - start
            
            if not ingest_success:
                print("Ingest timeout")
                return None
                
            # 4. Evaluation
            start = time.time()
            requests.post(f"{BASE_URL}/applications/{app_id}/evaluate")
            
            # Poll Evaluation
            eval_success = False
            for _ in range(30):
                resp = requests.get(f"{BASE_URL}/applications/{app_id}/evaluation")
                if resp.status_code == 200:
                    eval_success = True
                    break
                time.sleep(1)
            metrics["eval_time"] = time.time() - start
            
            # Cleanup
            requests.delete(f"{BASE_URL}/applications/{app_id}")
            
            return metrics
            
        except Exception as e:
            print(f"Error: {e}")
            if app_id:
                requests.delete(f"{BASE_URL}/applications/{app_id}")
            return None

    def _print_report(self):
        print("\n=== BENCHMARK REPORT ===")
        print(f"Total Iterations: {ITERATIONS}")
        print(f"Successful: {len(self.results)}")
        
        if not self.results:
            print("No data.")
            return
            
        avg_create = statistics.mean([r["create_time"] for r in self.results])
        avg_upload = statistics.mean([r["upload_time"] for r in self.results])
        avg_ingest = statistics.mean([r["ingest_time"] for r in self.results])
        avg_eval = statistics.mean([r["eval_time"] for r in self.results])
        
        print(f"Avg Create App:   {avg_create:.4f}s")
        print(f"Avg Upload Doc:   {avg_upload:.4f}s")
        print(f"Avg Ingestion:    {avg_ingest:.4f}s")
        print(f"Avg Evaluation:   {avg_eval:.4f}s")
        
        total_avg = avg_create + avg_upload + avg_ingest + avg_eval
        print(f"Total Avg Pipeline: {total_avg:.4f}s")

if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run_benchmark()
