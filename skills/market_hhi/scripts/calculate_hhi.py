import sys
import json

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Comma-separated list of proxy metrics (reviews or installs) required"}))
        sys.exit(1)
        
    raw_input = sys.argv[1]
    
    try:
        # Parse the comma-separated string into a list of numbers
        values = [float(x.strip()) for x in raw_input.split(',') if x.strip()]
        
        if not values or sum(values) == 0:
            print(json.dumps({"error": "Sum of proxy metrics cannot be zero"}))
            sys.exit(1)
            
        total = sum(values)
        
        hhi = 0
        shares = []
        for v in values:
            # Calculate percentage share
            share = (v / total) * 100
            shares.append(round(share, 2))
            # Square the share and add to total HHI
            hhi += share ** 2
            
        hhi = round(hhi, 2)
        
        # Map HHI score to standard DOJ market concentration brackets
        if hhi < 1500:
            status = "Low Concentration (Highly Competitive - IDEAL)"
        elif hhi <= 2500:
            status = "Moderate Concentration (Viable)"
        else:
            status = "High Concentration (Monopoly - REJECT)"
            
        print(json.dumps({
            "total_proxy_volume": total,
            "calculated_hhi": hhi,
            "market_status": status,
            "firm_market_shares_pct": shares
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()