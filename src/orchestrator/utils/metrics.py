# scrape_triton_metrics.py
import requests
from prometheus_client.parser import text_string_to_metric_families
from collections import defaultdict
import time

def fetch_metrics_text(url, timeout=5):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text

def parse_metrics(metrics_text):
    """
    Returns: dict: metric_name -> list of {labels: {...}, value: float}
    """
    metrics = {}
    for family in text_string_to_metric_families(metrics_text):
        name = family.name
        for sample in family.samples:
            metrics[sample.name] = float(sample.value)
    return metrics

if __name__ == "__main__":
    url = "http://localhost:8002/metrics" 
    txt = fetch_metrics_text(url)
    # print(txt)
    metrics = parse_metrics(txt)
    print("Metrics:", metrics)
