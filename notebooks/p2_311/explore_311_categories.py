"""Which 311 request types spike during big floods, and is there free text? Run from the repo root."""
import json, urllib.parse, urllib.request
B = "https://data.cityofchicago.org/resource/v6vf-nfxy.json"
def q(**p):
    p = {"$" + k: v for k, v in p.items()}
    u = B + "?" + urllib.parse.urlencode(p, quote_via=urllib.parse.quote)
    return json.load(urllib.request.urlopen(u, timeout=150))

print("Q1. Any free-text field? Fields on one sewer request:")
r = q(where="sr_type='Sewer Cleaning Inspection Request'", limit="1")[0]
print("  ", sorted(r.keys()))

print("\nQ2/Q3. Daily counts, Jul 1-6 2023 (flood started Jul 2):")
for t in ["Water in Basement Complaint", "Water On Street Complaint", "Sewer Cleaning Inspection Request"]:
    rows = q(select="date_trunc_ymd(created_date) as day, count(*) as n",
             where=f"sr_type='{t}' AND created_date between '2023-06-28T00:00:00' and '2023-07-07T00:00:00' AND duplicate=false",
             group="day", order="day")
    print(f"  {t[:34]:34}", [int(x['n']) for x in rows])

def window(a, b):
    rows = q(select="sr_type, count(*) as n", where=f"created_date between '{a}T00:00:00' and '{b}T23:59:59' AND duplicate=false",
             group="sr_type", limit="500")
    return {x["sr_type"]: int(x["n"]) for x in rows}

def ratio(flood, base, fd, bd, label):
    print(f"\nQ4. Which request types jump during {label}? (per-day average, flood vs normal)")
    out = []
    for t, n in flood.items():
        b = base.get(t, 0) / bd
        f = n / fd
        if f >= 15:
            out.append((f / max(b, 0.5), f, b, t))
    for ratio_, f, b, t in sorted(out, reverse=True)[:8]:
        print(f"  x{ratio_:6.1f}   {f:8.0f}/day vs {b:6.1f}/day   {t}")

ratio(window("2023-07-02", "2023-07-05"), window("2023-06-01", "2023-06-20"), 4, 20, "Jul 2-5 2023")
ratio(window("2025-08-17", "2025-08-19"), window("2025-06-01", "2025-06-20"), 3, 20, "Aug 17-19 2025")

print("\nQ5. Request types handled by the Water Management department (all, by volume):")
rows = q(select="sr_type, count(*) as n", where="owner_department like 'DWM%'", group="sr_type", order="n DESC", limit="30")
for x in rows: print(f"  {int(x['n']):>8}  {x['sr_type']}")
