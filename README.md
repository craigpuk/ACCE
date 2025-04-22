**ACCE User Manual: Adding Tags & Creating Smart Logic**

This guide walks you through extending ACCE by introducing new process or chemistry tags and crafting smart diagnostic rules that cross‑reference multiple tags.

---

## 1. Project Structure

```
ACCE_Demo/
├─ smart_engine/
│  ├─ excel_to_json.py    # Converter script
│  ├─ main.py             # Flask server + logic engine
│  ├─ tag_config.json     # Tag definitions & thresholds
│  └─ logic_rules.json    # Diagnostic rule definitions
├─ dashboard_ui/          # HTML, CSS, JS dashboard
├─ data/
│  ├─ live_data.csv       # Sample input spreadsheet
│  ├─ live_data.json      # Generated JSON data
│  └─ faults.txt          # Logged alarms
└─ run_demo.bat           # Batch file to launch ACCE
```

---

## 2. Defining New Tags

Tags represent your process measurements. To add a new tag:

1. **Open** `smart_engine/tag_config.json`.
2. **Add** an entry under the root object using the tag’s exact name as DCS/PI emits it.
3. **Specify** its unit, minimum, and maximum (for status coloring):

```jsonc
{
  "New_Tag_Name": {
    "unit": "<unit>",
    "min": <minimum_value>,
    "max": <maximum_value>
  }
}
```

- **unit**: Shown in the dashboard (e.g. `%`, `°F`, `ppm`).
- **min/max**: Values outside this range → **red**; values within 10% of boundaries → **yellow**; otherwise **green**.

4. **Save** the file. The converter will pick it up on next restart.

---

## 3. Creating Smart Logic Rules

Rules live in `smart_engine/logic_rules.json`. Each rule uses multiple tags to detect conditions.

### Rule Structure

```jsonc
"Rule_Key": {
  "conditions": {
    "TagA": { "above":  X },
    "TagB": { "below":  Y },
    "TagC": { "above":  P,  "below": Q }
  },
  "message": "Brief action text",
  "cause":   "Underlying cause explanation",
  "impact":  "Potential impact if unaddressed"
}
```

- **Rule_Key**: Unique identifier (no spaces) for your rule.
- **conditions**: A map of tag names to thresholds:
  - `"above"`: Fires if tag value > threshold.
  - `"below"`: Fires if tag value < threshold.
- **message**: What appears in Diagnostics (must be concise).
- **cause/impact**: Contextual details shown alongside the message.

### Example: Burner Misalignment Rule

```jsonc
"High_CO_vs_Stoich": {
  "conditions": {
    "Gas_Flow_CFM": { "above": 450, "below": 550 },
    "Feed_End_O2":  { "above": 1.0, "below": 2.0 },
    "CO_Stack_ppm": { "above": 1000 }
  },
  "message": "CO high despite stoichiometric air → check burner position",
  "cause":   "Normal flow & O₂ but elevated CO",
  "impact":  "Incomplete combustion, safety risk"
}
```

Once saved, ACCE will automatically evaluate the new rule every cycle and display any triggered alarms.

---

## 4. Testing Your Changes

1. **Restart** ACCE via `run_demo.bat`.
2. **Edit** `data/live_data.csv` (or your PI export) to include new tag columns and values.
3. **Save** the spreadsheet; the converter will write `live_data.json`.
4. **Watch** the dashboard:
   - New tags appear as colored cards in the Inputs tab.
   - Any new rule triggers show up in Diagnostics with your custom message, cause, and impact.
   - Trends tab lets you click cards to plot historical values.

---

## 5. Advanced Tips

- **Multi‑tag rules**: Combine any number of tags—ACCE only fires when *all* conditions are met.
- **Custom thresholds**: For tags like `CO_Stack_ppm`, you can override min/max logic in `main.py` if needed.
- **Persistent logging**: Alarms are appended to `data/faults.txt` with timestamps for audit.
- **Memory management**: History deques auto‑clear after logging to keep RAM usage constant.

---

**That’s it!** You now know how to extend ACCE with new measurements and tailored engineering logic. If you run into any issues, let me know.

