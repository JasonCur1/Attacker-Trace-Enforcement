import subprocess
import re
import csv
import os
import itertools
import time

# range(1, 4) means [1, 2, 3]
EXT_RANGE = range(1, 8)  
INT_RANGE = range(1, 8)
CRIT_RANGE = range(1, 8)

CONFIG_FILE = "final_gridworld_domain.py"
OUTPUT_CSV = "gridsearch_results.csv"
TIMEOUT = 1800  # 30 minutes

GEN_CMD = ["python3", "translate_independent.py"]

PLANNER_CMD = [
    "./stackelberg-planner-sls/src/fast-downward.py",
    "domain.pddl",
    "problem.pddl",
    "--search",
    "sym_stackelberg(optimal_engine=symbolic(plan_reuse_minimal_task_upper_bound=false, plan_reuse_upper_bound=true), upper_bound_pruning=false)"
]

def update_domain_config(file_path, ext_count, int_count, crit_count):
    """
    Updates the 'pc_count_by_segment' dictionary in the config file.
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    subs = {
        'external': ext_count,
        'internal': int_count,
        'critical': crit_count
    }

    new_content = content
    for key, val in subs.items():
        pattern = f"(['\"]{key}['\"]\s*:\s*)(\d+)"
        
        if not re.search(pattern, new_content):
            print(f"WARNING: Could not find key '{key}' in {file_path}")
            continue
            
        new_content = re.sub(pattern, f"\\g<1>{val}", new_content)

    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
    else:
        print("  Warning: Config file was not changed (regex match failed?).")


def parse_output(output_text):
    times = {
        "translator": 0.0,
        "preprocessor": 0.0,
        "search": 0.0,
        "total_wall": 0.0, # Calculated later
        "solved": False
    }

    # Translator (Wall clock)
    trans = re.search(r"Done! \[.*?([\d\.]+)s wall-clock\]", output_text)
    if trans: times["translator"] = float(trans.group(1))

    # Preprocessor
    prep = re.search(r"Preprocessor time:\s*([\d\.]+)s", output_text)
    if prep: times["preprocessor"] = float(prep.group(1))

    # Search Time (Algorithm)
    search = re.search(r"Search time:\s*([\d\.]+)s", output_text)
    if search: times["search"] = float(search.group(1))

    # Real Total (from the very end of log)
    total = re.findall(r"Total time:\s*([\d\.]+)s", output_text)
    if total: times["total_wall"] = float(total[-1])

    if "Pareto-frontier size:" in output_text:
        times["solved"] = True
        
    return times


def main():
    combinations = list(itertools.product(EXT_RANGE, INT_RANGE, CRIT_RANGE))
    
    # Sort by TOTAL number of PCs (sum) so we do small problems first
    #    If sums are equal, it sorts by Ext, then Int.
    combinations.sort(key=lambda x: (sum(x), x[0], x[1], x[2]))

    print(f"Queue generated: {len(combinations)} experiments.")
    print(f"Range: {combinations[0]} -> {combinations[-1]}")

    headers = ["Ext PCs", "Int PCs", "Crit PCs", "Total PCs", 
               "Translator (s)", "Preprocessor (s)", "Search (s)", 
               "Total Time (s)", "Solved"]
    
    write_header = not os.path.exists(OUTPUT_CSV)
    
    with open(OUTPUT_CSV, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(headers)

        for (e, i, c) in combinations:
            print(f"\n--- Running: Ext={e}, Int={i}, Crit={c} (Sum={e+i+c}) ---")

            update_domain_config(CONFIG_FILE, e, i, c)

            try:
                subprocess.run(GEN_CMD, check=True, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print("  Error: PDDL Generation failed.")
                continue

            start_time = time.time()
            try:
                result = subprocess.run(
                    PLANNER_CMD, 
                    capture_output=True, 
                    text=True, 
                    timeout=TIMEOUT
                )
                output = result.stdout
            except subprocess.TimeoutExpired:
                print(f"  TIMEOUT ({TIMEOUT}s)")
                writer.writerow([e, i, c, e+i+c, "TIMEOUT", "TIMEOUT", "TIMEOUT", "TIMEOUT", False])
                csvfile.flush()
                continue

            data = parse_output(output)
            
            if data["total_wall"] == 0.0:
                data["total_wall"] = round(time.time() - start_time, 4)

            row = [
                e, i, c, (e+i+c),
                data["translator"],
                data["preprocessor"],
                data["search"],
                data["total_wall"],
                data["solved"]
            ]
            
            writer.writerow(row)
            csvfile.flush()
            print(f"  Done in {data['total_wall']}s | Solved: {data['solved']}")

if __name__ == "__main__":
    main()