"""
Data Analysis Script
Analyzes member messages data for anomalies and inconsistencies
"""
import json
import httpx
from collections import defaultdict, Counter
from typing import Dict, List, Any


MESSAGES_API_URL = "https://november7-730026606190.europe-west1.run.app/messages"


def fetch_messages() -> List[Dict[str, Any]]:
    """Fetch messages from API"""
    try:
        response = httpx.get(MESSAGES_API_URL, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
        # API returns {'total': N, 'items': [...]}, extract items
        if isinstance(data, dict) and 'items' in data:
            return data['items']
        elif isinstance(data, list):
            return data
        else:
            return [data]
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []


def analyze_data(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze messages for anomalies and inconsistencies"""
    findings = {
        "total_messages": len(messages),
        "anomalies": [],
        "statistics": {},
        "inconsistencies": []
    }
    
    if not messages:
        return findings
    
    # Basic statistics
    field_counts = defaultdict(int)
    field_types = defaultdict(set)
    member_names = set()
    dates = []
    
    # Analyze each message
    for i, msg in enumerate(messages):
        # Check for missing required fields
        if not isinstance(msg, dict):
            findings["anomalies"].append(f"Message {i} is not a dictionary: {type(msg)}")
            continue
        
        # Track field presence
        for key in msg.keys():
            field_counts[key] += 1
            field_types[key].add(type(msg.get(key)).__name__)
        
        # Extract member names (common patterns)
        msg_str = json.dumps(msg, ensure_ascii=False).lower()
        # Look for common name patterns
        if "name" in msg:
            member_names.add(str(msg.get("name")))
        if "member" in msg:
            member_names.add(str(msg.get("member")))
        
        # Extract dates
        for key, value in msg.items():
            if "date" in key.lower() or "time" in key.lower():
                if value:
                    dates.append(value)
    
    findings["statistics"] = {
        "total_fields": len(field_counts),
        "field_frequency": dict(field_counts),
        "field_type_variations": {k: list(v) for k, v in field_types.items()},
        "unique_members_found": len(member_names),
        "date_entries": len(dates)
    }
    
    # Check for inconsistencies
    # 1. Fields with inconsistent types
    for field, types in field_types.items():
        if len(types) > 1:
            findings["inconsistencies"].append(
                f"Field '{field}' has inconsistent types: {list(types)}"
            )
    
    # 2. Fields that appear in some messages but not others
    all_fields = set(field_counts.keys())
    for field in all_fields:
        presence_rate = field_counts[field] / len(messages)
        if presence_rate < 0.5:
            findings["inconsistencies"].append(
                f"Field '{field}' only appears in {presence_rate*100:.1f}% of messages"
            )
    
    # 3. Check for empty/null values
    empty_fields = defaultdict(int)
    for msg in messages:
        for key, value in msg.items():
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                empty_fields[key] += 1
    
    if empty_fields:
        findings["statistics"]["empty_field_counts"] = dict(empty_fields)
        findings["inconsistencies"].append(
            f"Found {len(empty_fields)} fields with empty/null values"
        )
    
    # 4. Check for duplicate messages
    message_strings = [json.dumps(msg, sort_keys=True) for msg in messages]
    duplicates = len(message_strings) - len(set(message_strings))
    if duplicates > 0:
        findings["anomalies"].append(f"Found {duplicates} duplicate messages")
    
    return findings


def print_findings(findings: Dict[str, Any]):
    """Print analysis findings"""
    print("=" * 60)
    print("DATA ANALYSIS FINDINGS")
    print("=" * 60)
    print(f"\nTotal Messages: {findings['total_messages']}")
    
    print("\n--- Statistics ---")
    stats = findings.get("statistics", {})
    print(f"Total unique fields: {stats.get('total_fields', 0)}")
    print(f"Unique members found: {stats.get('unique_members_found', 0)}")
    
    if "field_frequency" in stats:
        print("\nField frequency (top 10):")
        sorted_fields = sorted(stats["field_frequency"].items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:10]:
            print(f"  {field}: {count}")
    
    print("\n--- Anomalies ---")
    if findings["anomalies"]:
        for anomaly in findings["anomalies"]:
            print(f"  ⚠️  {anomaly}")
    else:
        print("  ✓ No major anomalies detected")
    
    print("\n--- Inconsistencies ---")
    if findings["inconsistencies"]:
        for inconsistency in findings["inconsistencies"]:
            print(f"  ⚠️  {inconsistency}")
    else:
        print("  ✓ No major inconsistencies detected")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("Fetching messages from API...")
    messages = fetch_messages()
    
    if not messages:
        print("No messages found or error fetching data.")
        exit(1)
    
    print(f"Analyzing {len(messages)} messages...")
    findings = analyze_data(messages)
    print_findings(findings)
    
    # Save findings to file
    with open("data_analysis.json", "w") as f:
        json.dump(findings, f, indent=2)
    print("\nDetailed findings saved to data_analysis.json")

