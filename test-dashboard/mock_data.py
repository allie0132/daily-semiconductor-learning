"""
Generates a SQLite database of realistic semiconductor ATE test data.
Covers Sep 1 – Nov 4, 2026 (~65 days, 2-4 lots/day, 25 wafers/lot).
"""
import sqlite3, random, math, os
from datetime import datetime, timedelta, date as Date

# ── Wafer geometry ───────────────────────────────────────────────────
GRID      = 20
CENTER    = 9.5
RADIUS    = 9.5
EDGE_ZONE = 7.5

def _in_wafer(x, y):
    return (x + 0.5 - CENTER)**2 + (y + 0.5 - CENTER)**2 <= RADIUS**2

WAFER_DIES = [(x, y) for x in range(GRID) for y in range(GRID) if _in_wafer(x, y)]
DIE_COUNT  = len(WAFER_DIES)

# ── Bin definitions ──────────────────────────────────────────────────
# BIN1  = Grade A full-speed pass (highest spec, highest price).
# BIN1B = Speed downgrade Grade B: failed 1 GHz but passed re-test at 750 MHz — still sellable.
# BIN1C = Speed downgrade Grade C: failed 750 MHz but passed re-test at 500 MHz — still sellable.
# BIN2–BIN11 = Failure categories (device scrapped / rejected).
BINS = {
    "BIN1":  {"label": "Grade A Pass (1 GHz)",       "color": "#10b981", "sellable": True},
    "BIN1B": {"label": "Grade B Downgrade (750 MHz)", "color": "#06b6d4", "sellable": True},
    "BIN1C": {"label": "Grade C Downgrade (500 MHz)", "color": "#f59e0b", "sellable": True},
    "BIN2":  {"label": "Open / Short",               "color": "#f97316", "sellable": False},
    "BIN3":  {"label": "Contact",                    "color": "#eab308", "sellable": False},
    "BIN4":  {"label": "DC Parametric",              "color": "#ef4444", "sellable": False},
    "BIN5":  {"label": "IDDQ / Leakage",             "color": "#dc2626", "sellable": False},
    "BIN6":  {"label": "AC / Timing Fail",           "color": "#ec4899", "sellable": False},
    "BIN7":  {"label": "Memory",                     "color": "#8b5cf6", "sellable": False},
    "BIN8":  {"label": "Scan / ATPG",                "color": "#6366f1", "sellable": False},
    "BIN9":  {"label": "Functional",                 "color": "#a16207", "sellable": False},
    "BIN10": {"label": "Data Eye / SI",              "color": "#67e8f9", "sellable": False},
    "BIN11": {"label": "Assembly / Crack",           "color": "#7f1d1d", "sellable": False},
    "EDGE":  {"label": "Not Tested",                 "color": "#1e2d45", "sellable": False},
}
# AC/Timing failures can be re-tested at lower speeds → downgrade instead of reject
DOWNGRADABLE_BINS = {"BIN6"}

# ── Test definitions ─────────────────────────────────────────────────
# (name, display_category, unit, avg_time_ms, base_fail_pct, bin)
TEST_DEFS = [
    # Open / Short
    ("OPEN_SHORT_POWER",   "Open/Short", "-",    2.5,  1.8,  "BIN2"),
    ("OPEN_SHORT_IO_A",    "Open/Short", "-",    2.5,  1.4,  "BIN2"),
    ("OPEN_SHORT_IO_B",    "Open/Short", "-",    2.5,  1.2,  "BIN2"),
    ("OPEN_SHORT_IO_C",    "Open/Short", "-",    2.5,  0.9,  "BIN2"),
    ("CONTINUITY_VDD",     "Open/Short", "-",    1.8,  0.7,  "BIN2"),
    # Contact
    ("CONTACT_RES_VDD",    "Contact",    "mΩ",   5.2,  1.1,  "BIN3"),
    ("CONTACT_RES_VSS",    "Contact",    "mΩ",   5.2,  0.9,  "BIN3"),
    ("CONTACT_RES_IO",     "Contact",    "mΩ",   5.8,  1.3,  "BIN3"),
    # DC Parametric
    ("VDD_CORE_NOM",       "DC",         "V",    3.2,  1.2,  "BIN4"),
    ("VDD_CORE_HIGH",      "DC",         "V",    3.1,  0.8,  "BIN4"),
    ("VDD_IO_3V3",         "DC",         "V",    3.5,  1.5,  "BIN4"),
    ("VDD_AUX_1V8",        "DC",         "V",    3.3,  0.9,  "BIN4"),
    ("VDD_PLL",            "DC",         "V",    3.4,  1.1,  "BIN4"),
    ("IDD_ACTIVE_1G",      "DC",         "mA",   8.5,  2.3,  "BIN4"),
    ("IDD_ACTIVE_500M",    "DC",         "mA",   8.5,  1.8,  "BIN4"),
    ("IDD_SLEEP",          "DC",         "uA",   6.2,  3.1,  "BIN4"),
    ("IDD_SHUTDOWN",       "DC",         "uA",   5.8,  2.4,  "BIN4"),
    ("VOH_LVCMOS33",       "DC",         "V",    4.1,  0.6,  "BIN4"),
    ("VOL_LVCMOS33",       "DC",         "V",    4.1,  0.5,  "BIN4"),
    ("IOH_12MA",           "DC",         "mA",   5.2,  1.4,  "BIN4"),
    ("IOL_12MA",           "DC",         "mA",   5.2,  1.3,  "BIN4"),
    ("PIN_LEAK_BANK0",     "DC",         "nA",   12.0, 1.8,  "BIN4"),
    ("PIN_LEAK_BANK1",     "DC",         "nA",   12.0, 2.1,  "BIN4"),
    ("ESD_HBM_CLASS2",     "DC",         "V",    18.0, 0.4,  "BIN4"),
    # IDDQ / Leakage
    ("IDDQ_SCAN_1",        "IDDQ",       "uA",   65.0, 8.5,  "BIN5"),
    ("IDDQ_SCAN_2",        "IDDQ",       "uA",   65.0, 7.8,  "BIN5"),
    ("IDDQ_SCAN_3",        "IDDQ",       "uA",   65.0, 9.2,  "BIN5"),
    ("IDDQ_SCAN_4",        "IDDQ",       "uA",   65.0, 7.1,  "BIN5"),
    ("IDDQ_SCAN_5",        "IDDQ",       "uA",   65.0, 6.8,  "BIN5"),
    # AC / Timing
    ("OSC_FREQ_1GHz",      "AC",         "MHz",  22.0, 3.8,  "BIN6"),
    ("OSC_FREQ_500MHz",    "AC",         "MHz",  20.0, 3.2,  "BIN6"),
    ("OSC_FREQ_200MHz",    "AC",         "MHz",  18.0, 2.1,  "BIN6"),
    ("PLL_LOCK_TIME",      "AC",         "us",   28.0, 4.5,  "BIN6"),
    ("PLL_JITTER_RMS",     "AC",         "ps",   35.0, 5.2,  "BIN6"),
    ("PLL_JITTER_PEAK",    "AC",         "ps",   35.0, 10.3, "BIN6"),
    ("CLK_DUTY_CYCLE",     "AC",         "%",    15.0, 2.8,  "BIN6"),
    ("CLK_FREQ_ACC",       "AC",         "ppm",  15.0, 1.9,  "BIN6"),
    ("LVDS_VOD",           "AC",         "mV",   8.5,  1.2,  "BIN6"),
    ("LVDS_VCOM",          "AC",         "V",    8.5,  0.9,  "BIN6"),
    ("SETUP_TIME_CLK",     "Timing",     "ps",   18.0, 2.2,  "BIN6"),
    ("HOLD_TIME_CLK",      "Timing",     "ps",   18.0, 2.8,  "BIN6"),
    ("PROPAGATION_A2Y",    "Timing",     "ps",   22.0, 3.1,  "BIN6"),
    ("PROPAGATION_B2Y",    "Timing",     "ps",   22.0, 2.9,  "BIN6"),
    ("ACCESS_TIME_SRAM",   "Timing",     "ns",   25.0, 3.8,  "BIN6"),
    ("RECOVERY_TIME_RST",  "Timing",     "ns",   15.0, 1.5,  "BIN6"),
    ("OUTPUT_DELAY_MAX",   "Timing",     "ns",   20.0, 2.4,  "BIN6"),
    ("INPUT_DELAY_MIN",    "Timing",     "ns",   20.0, 1.8,  "BIN6"),
    ("CLK_TO_Q_DELAY",     "Timing",     "ps",   22.0, 2.6,  "BIN6"),
    # Memory
    ("SRAM_BIST_MB0",      "Memory",     "-",   180.0, 5.6,  "BIN7"),
    ("SRAM_BIST_MB1",      "Memory",     "-",   185.0, 6.1,  "BIN7"),
    ("SRAM_BIST_MB2",      "Memory",     "-",   182.0, 5.4,  "BIN7"),
    ("SRAM_BIST_MB3",      "Memory",     "-",   178.0, 7.2,  "BIN7"),
    ("SRAM_MARCH_C",       "Memory",     "-",   220.0, 4.8,  "BIN7"),
    ("SRAM_CHECKERBOARD",  "Memory",     "-",   210.0, 4.3,  "BIN7"),
    ("CACHE_L1_BIST",      "Memory",     "-",   155.0, 3.9,  "BIN7"),
    ("CACHE_L2_BIST",      "Memory",     "-",   245.0, 4.5,  "BIN7"),
    ("ROM_CRC_CHECK",      "Memory",     "-",    45.0, 0.8,  "BIN7"),
    ("FLASH_PGM_VERIFY",   "Memory",     "-",   350.0, 1.2,  "BIN7"),
    # Scan / ATPG
    ("SCAN_CHAIN_1",       "Scan",       "-",   420.0, 2.1,  "BIN8"),
    ("SCAN_CHAIN_2",       "Scan",       "-",   415.0, 2.3,  "BIN8"),
    ("SCAN_CHAIN_3",       "Scan",       "-",   425.0, 1.9,  "BIN8"),
    ("SCAN_CHAIN_4",       "Scan",       "-",   418.0, 2.5,  "BIN8"),
    ("SCAN_CHAIN_5",       "Scan",       "-",   422.0, 2.0,  "BIN8"),
    ("ATPG_PATTERN_SET_1", "Scan",       "-",   680.0, 3.2,  "BIN8"),
    ("ATPG_PATTERN_SET_2", "Scan",       "-",   710.0, 2.8,  "BIN8"),
    ("ATPG_PATTERN_SET_3", "Scan",       "-",   695.0, 3.1,  "BIN8"),
    ("BSCAN_CHAIN_TEST",   "Scan",       "-",    85.0, 1.4,  "BIN8"),
    # Functional
    ("REG_RW_CORE",        "Functional", "-",    12.0, 0.5,  "BIN9"),
    ("REG_RW_IO",          "Functional", "-",    11.5, 0.4,  "BIN9"),
    ("UART_LOOPBACK",      "Functional", "-",    18.0, 0.7,  "BIN9"),
    ("SPI_LOOPBACK",       "Functional", "-",    15.0, 0.6,  "BIN9"),
    ("I2C_LOOPBACK",       "Functional", "-",    14.0, 0.5,  "BIN9"),
    ("GPIO_HIGH_LOW",      "Functional", "-",     8.0, 0.3,  "BIN9"),
    ("DMA_TRANSFER_64K",   "Functional", "-",    45.0, 0.8,  "BIN9"),
    ("CPU_ALU_ADVANCED",   "Functional", "-",    38.0, 0.6,  "BIN9"),
    ("CPU_FPU_DOUBLE",     "Functional", "-",    45.0, 0.8,  "BIN9"),
    ("USB_PHY_ENUMERATE",  "Functional", "-",    35.0, 1.5,  "BIN9"),
    ("PCIE_LTSSM_L0",      "Functional", "-",    32.0, 1.8,  "BIN9"),
    ("PCIE_TLP_LOOPBACK",  "Functional", "-",    48.0, 2.1,  "BIN9"),
    ("ETH_PHY_LINK",       "Functional", "-",    38.0, 1.6,  "BIN9"),
    ("POWER_SEQ_RAMP",     "Functional", "-",    28.0, 2.5,  "BIN9"),
    ("THERMAL_SHUTDOWN",   "Functional", "-",    85.0, 0.4,  "BIN9"),
    # Data Eye / Signal Integrity
    ("EYE_PCIE_GEN3_TX",   "Data Eye",   "mV",   95.0, 4.2,  "BIN10"),
    ("EYE_PCIE_GEN3_RX",   "Data Eye",   "mV",   95.0, 3.8,  "BIN10"),
    ("EYE_USB3_TX",        "Data Eye",   "mV",   88.0, 4.5,  "BIN10"),
    ("EYE_USB3_RX",        "Data Eye",   "mV",   88.0, 3.9,  "BIN10"),
    ("EYE_DDR4_DQ_WIDTH",  "Data Eye",   "ps",  110.0, 5.1,  "BIN10"),
    ("EYE_DDR4_DQ_HEIGHT", "Data Eye",   "mV",  110.0, 4.8,  "BIN10"),
    ("JITTER_DDR4_CLK",    "Data Eye",   "ps",   75.0, 3.6,  "BIN10"),
    ("EYE_SERDES_TX",      "Data Eye",   "mV",  120.0, 3.1,  "BIN10"),
    ("EYE_SERDES_RX",      "Data Eye",   "mV",  120.0, 2.9,  "BIN10"),
    ("SKEW_DDR4_DQ_DQS",   "Data Eye",   "ps",   65.0, 4.0,  "BIN10"),
    # Assembly / Die Crack
    ("DIE_CRACK_DETECT",   "Assembly",   "-",    12.0, 0.6,  "BIN11"),
    ("SUBSTRATE_OPEN",     "Assembly",   "-",     8.0, 0.4,  "BIN11"),
    ("BOND_CONTINUITY",    "Assembly",   "-",    10.0, 0.5,  "BIN11"),
    ("DIE_ATTACH_RES",     "Assembly",   "mΩ",   15.0, 0.3,  "BIN11"),
    # ── HBM (High Bandwidth Memory) ─────────────────────────────────────
    # TSV (Through-Silicon Via) integrity — open/short on microbumps
    ("HBM_TSV_CONT_CH0",   "HBM-TSV",   "-",     8.5, 2.1,  "BIN2"),
    ("HBM_TSV_CONT_CH1",   "HBM-TSV",   "-",     8.5, 1.9,  "BIN2"),
    ("HBM_TSV_CONT_CH2",   "HBM-TSV",   "-",     8.5, 2.3,  "BIN2"),
    ("HBM_TSV_CONT_CH3",   "HBM-TSV",   "-",     8.5, 1.8,  "BIN2"),
    ("HBM_UBUMP_RES_CH0",  "HBM-TSV",   "mΩ",   12.0, 1.4,  "BIN3"),
    ("HBM_UBUMP_RES_CH1",  "HBM-TSV",   "mΩ",   12.0, 1.3,  "BIN3"),
    # PHY training — speed-graded; fail at 6.4 Gbps may downgrade to 4.8 Gbps
    # These fall in BIN6 (AC/Timing) → eligible for speed downgrade
    ("HBM_PHY_TRAIN_CH0",  "HBM-PHY",   "Gbps",  38.0, 5.8,  "BIN6"),
    ("HBM_PHY_TRAIN_CH1",  "HBM-PHY",   "Gbps",  38.0, 6.1,  "BIN6"),
    ("HBM_PHY_TRAIN_CH2",  "HBM-PHY",   "Gbps",  38.0, 5.5,  "BIN6"),
    ("HBM_PHY_TRAIN_CH3",  "HBM-PHY",   "Gbps",  38.0, 5.9,  "BIN6"),
    ("HBM_PHY_LANE_EQ",    "HBM-PHY",   "-",     45.0, 4.2,  "BIN6"),
    ("HBM_CLK_PHASE_ADJ",  "HBM-PHY",   "ps",    28.0, 3.8,  "BIN6"),
    # Eye diagram at HBM3 speed (6.4 Gbps/pin)
    ("HBM_EYE_WIDTH_6G",   "HBM-Eye",   "ps",    95.0, 7.2,  "BIN10"),
    ("HBM_EYE_HEIGHT_6G",  "HBM-Eye",   "mV",    95.0, 6.8,  "BIN10"),
    ("HBM_EYE_WIDTH_4G",   "HBM-Eye",   "ps",    88.0, 3.1,  "BIN10"),
    ("HBM_JITTER_RMS",     "HBM-Eye",   "ps",    75.0, 4.5,  "BIN10"),
    # MBiST (Memory Built-in Self-Test) for stacked DRAM dies
    ("HBM_MBIST_DIE0",     "HBM-MBiST", "-",    220.0, 4.8,  "BIN7"),
    ("HBM_MBIST_DIE1",     "HBM-MBiST", "-",    220.0, 5.1,  "BIN7"),
    ("HBM_MBIST_DIE2",     "HBM-MBiST", "-",    220.0, 4.6,  "BIN7"),
    ("HBM_MBIST_DIE3",     "HBM-MBiST", "-",    220.0, 5.3,  "BIN7"),
    # On-die ECC verification (HBM3 feature)
    ("HBM_ECC_INJECT_1B",  "HBM-ECC",   "-",     35.0, 1.2,  "BIN7"),
    ("HBM_ECC_INJECT_2B",  "HBM-ECC",   "-",     35.0, 2.1,  "BIN7"),
    ("HBM_ECC_MULTI_RANK", "HBM-ECC",   "-",     42.0, 1.8,  "BIN7"),
    # Row Hammer / Retention (reliability screen)
    ("HBM_ROW_HAMMER",     "HBM-MBiST", "-",    380.0, 3.4,  "BIN7"),
    ("HBM_RETENTION_FAST", "HBM-MBiST", "-",    280.0, 2.9,  "BIN7"),
]

TOTAL_TIME_PER_DIE_MS = sum(t[3] for t in TEST_DEFS)

# Each product family contains several product part numbers.
PRODUCT_FAMILIES = {
    "Kintex-7": ["XC7K325T", "XC7K410T", "XC7K480T"],
    "Artix-7":  ["XC7A100T", "XC7A200T"],
    "Virtex-7": ["XC7VX485T", "XC7VX690T"],
    "HBM3":     ["HBM3_16GB", "HBM3_24GB"],
}
# Reverse lookup: product -> family
PRODUCT_TO_FAMILY = {p: fam for fam, prods in PRODUCT_FAMILIES.items() for p in prods}
PRODUCTS   = list(PRODUCT_TO_FAMILY.keys())
FAMILIES   = list(PRODUCT_FAMILIES.keys())
TP_REVS    = ["TPR_1.0", "TPR_1.1", "TPR_1.2", "TPR_2.0"]
TEST_STEPS = ["CP1", "CP2", "FT1", "FT2"]
PROC_NODES = ["N7_A1", "N7_A2", "N7_B1", "N5_A1"]
TESTERS    = ["T93K_ATE01", "T93K_ATE02", "ETS364_ATE01", "ETS364_ATE02"]
SOCKETS    = ["PSCB_A01", "PSCB_A02", "PSCB_B01", "PSCB_B02", "SOCK_C01"]

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data.db")


def init_db(force=False):
    if os.path.exists(DB_PATH) and not force:
        return
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    c.executescript("""
        CREATE TABLE lots (
            lot_id TEXT PRIMARY KEY, product TEXT, product_family TEXT, tp_rev TEXT,
            test_step TEXT, proc_node TEXT,
            wafer_count INT, total_dies INT, pass_dies INT, fail_dies INT,
            yield_pct REAL, start_date TEXT, end_date TEXT, avg_test_time_s REAL
        );
        CREATE TABLE wafers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id TEXT, wafer_id TEXT, product TEXT, product_family TEXT, tp_rev TEXT,
            test_step TEXT, proc_node TEXT, tester TEXT, socket TEXT,
            total_dies INT, pass_dies INT, fail_dies INT,
            yield_pct REAL, test_time_s REAL, test_date TEXT, start_time TEXT
        );
        CREATE TABLE test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id TEXT, test_name TEXT, category TEXT, unit TEXT, bin TEXT,
            fail_count INT, total_count INT, avg_time_ms REAL, test_date TEXT
        );
        CREATE INDEX idx_w_date     ON wafers(test_date);
        CREATE INDEX idx_w_product  ON wafers(product);
        CREATE INDEX idx_w_family    ON wafers(product_family);
        CREATE INDEX idx_w_lot      ON wafers(lot_id);
        CREATE INDEX idx_w_tprev    ON wafers(tp_rev);
        CREATE INDEX idx_w_step     ON wafers(test_step);
        CREATE INDEX idx_w_node     ON wafers(proc_node);
        CREATE INDEX idx_w_tester   ON wafers(tester);
        CREATE INDEX idx_w_socket   ON wafers(socket);
        CREATE INDEX idx_tr_date    ON test_results(test_date);
        CREATE INDEX idx_tr_name    ON test_results(test_name);
        CREATE INDEX idx_tr_lot     ON test_results(lot_id);
    """)

    rng     = random.Random(42)
    cur_dt  = Date(2026, 9, 1)
    end_dt  = Date(2026, 11, 4)
    lot_num = 1
    wafer_rows, test_rows, lot_rows = [], [], []

    while cur_dt <= end_dt:
        for _ in range(rng.randint(2, 4)):
            lot_id    = f"LOT2026{lot_num:03d}"
            product   = rng.choice(PRODUCTS)
            family    = PRODUCT_TO_FAMILY[product]
            tp_rev    = rng.choice(TP_REVS)
            test_step = rng.choice(TEST_STEPS)
            proc_node = rng.choice(PROC_NODES)
            lot_yoff  = rng.uniform(-4.0, 2.5)
            lot_start = datetime(cur_dt.year, cur_dt.month, cur_dt.day,
                                 rng.randint(0, 20), 0)
            lot_pass = lot_total = 0

            for w in range(1, 26):
                tester  = rng.choice(TESTERS)
                socket  = rng.choice(SOCKETS)
                base_y  = max(85.0, min(99.5, 93.0 + lot_yoff + rng.uniform(-2.0, 2.0)))
                fail_c  = int(DIE_COUNT * (100 - base_y) / 100)
                pass_c  = DIE_COUNT - fail_c
                lot_pass  += pass_c
                lot_total += DIE_COUNT
                wafer_rows.append((
                    lot_id, f"W{w:02d}", product, family, tp_rev, test_step, proc_node,
                    tester, socket, DIE_COUNT, pass_c, fail_c,
                    round(pass_c / DIE_COUNT * 100, 2),
                    round(TOTAL_TIME_PER_DIE_MS * DIE_COUNT / 1000, 1),
                    cur_dt.isoformat(),
                    (lot_start + timedelta(minutes=w * 30)).strftime("%Y-%m-%d %H:%M"),
                ))

            for name, cat, unit, time_ms, fail_rate, bin_num in TEST_DEFS:
                adj   = max(0.0, fail_rate * (1 + lot_yoff * -0.05) * rng.uniform(0.8, 1.2))
                fails = int(lot_total * adj / 100)
                test_rows.append((lot_id, name, cat, unit, bin_num,
                                  fails, lot_total, round(time_ms, 1), cur_dt.isoformat()))

            lot_rows.append((
                lot_id, product, family, tp_rev, test_step, proc_node, 25,
                lot_total, lot_pass, lot_total - lot_pass,
                round(lot_pass / lot_total * 100, 2),
                cur_dt.isoformat(),
                (lot_start + timedelta(hours=12)).strftime("%Y-%m-%d"),
                round(TOTAL_TIME_PER_DIE_MS / 1000, 2),
            ))
            lot_num += 1
        cur_dt += timedelta(days=1)

    c.executemany(
        "INSERT INTO lots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lot_rows)
    c.executemany(
        "INSERT INTO wafers (lot_id,wafer_id,product,product_family,tp_rev,test_step,proc_node,"
        "tester,socket,total_dies,pass_dies,fail_dies,yield_pct,test_time_s,"
        "test_date,start_time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", wafer_rows)
    c.executemany(
        "INSERT INTO test_results (lot_id,test_name,category,unit,bin,"
        "fail_count,total_count,avg_time_ms,test_date) VALUES (?,?,?,?,?,?,?,?,?)",
        test_rows)
    conn.commit()
    conn.close()
    print(f"DB ready: {len(lot_rows)} lots, {len(wafer_rows)} wafers")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Wafer map (generated on demand, no DB) ───────────────────────────
def generate_wafer_map(lot_id, wafer_id, yield_pct):
    rng       = random.Random(hash(lot_id + wafer_id))
    fail_rate = (100 - yield_pct) / 100
    clusters  = [(rng.uniform(3, 17), rng.uniform(3, 17), rng.uniform(1.0, 2.5))
                 for _ in range(rng.randint(0, 2))]
    weighted  = [(t[0], t[4], t[5]) for t in TEST_DEFS if t[4] > 0]
    total_w   = sum(w[1] for w in weighted)
    dies, bin_counts = [], {b: 0 for b in BINS}

    for x in range(GRID):
        for y in range(GRID):
            dist = math.sqrt((x + 0.5 - CENTER)**2 + (y + 0.5 - CENTER)**2)
            if dist > RADIUS:
                dies.append({"x": x, "y": y, "status": "EDGE", "bin": "EDGE"})
                bin_counts["EDGE"] += 1
                continue
            p = fail_rate * (2.5 if dist > EDGE_ZONE else 1.0)
            for cx, cy, cr in clusters:
                if math.sqrt((x - cx)**2 + (y - cy)**2) < cr:
                    p *= 4.0; break
            p = min(p, 0.95)
            if rng.random() < p:
                r, cumul = rng.random() * total_w, 0
                ft, fb = weighted[0][0], weighted[0][2]
                for nm, fw, fbn in weighted:
                    cumul += fw
                    if r <= cumul:
                        ft, fb = nm, fbn; break
                # Speed downgrade: AC/Timing fails re-tested at lower speed
                # 60% → Grade B (750 MHz), 25% → Grade C (500 MHz), 15% → hard fail
                if fb in DOWNGRADABLE_BINS:
                    r2 = rng.random()
                    if r2 < 0.60:
                        fb = "BIN1B"
                    elif r2 < 0.85:
                        fb = "BIN1C"
                    # else: stays as BIN6 (hard AC fail, cannot downgrade further)
                assigned_status = "DOWNGRADE" if fb in ("BIN1B", "BIN1C") else "FAIL"
                die = {"x": x, "y": y, "status": assigned_status, "fail_test": ft, "bin": fb}
                dies.append(die)
                bin_counts[fb] = bin_counts.get(fb, 0) + 1
            else:
                dies.append({"x": x, "y": y, "status": "PASS", "bin": "BIN1"})
                bin_counts["BIN1"] += 1

    pass_c = bin_counts["BIN1"] + bin_counts.get("BIN1B", 0) + bin_counts.get("BIN1C", 0)
    fail_c = sum(v for k, v in bin_counts.items()
                 if k not in ("BIN1", "BIN1B", "BIN1C", "EDGE"))
    fail_map  = {}
    down_map  = {}
    for d in dies:
        t = d.get("fail_test", "?")
        if d["status"] == "FAIL":
            fail_map[t] = fail_map.get(t, 0) + 1
        elif d["status"] == "DOWNGRADE":
            down_map[t] = down_map.get(t, 0) + 1

    total_tested = pass_c + fail_c + bin_counts.get("BIN1B", 0) + bin_counts.get("BIN1C", 0)
    return {
        "lot_id": lot_id, "wafer_id": wafer_id, "grid_size": GRID,
        "yield_pct":        round(pass_c / total_tested * 100, 2) if total_tested else 0,
        "grade_a_pct":      round(bin_counts["BIN1"] / total_tested * 100, 2) if total_tested else 0,
        "grade_b_pct":      round(bin_counts.get("BIN1B", 0) / total_tested * 100, 2) if total_tested else 0,
        "grade_c_pct":      round(bin_counts.get("BIN1C", 0) / total_tested * 100, 2) if total_tested else 0,
        "pass_count":       bin_counts["BIN1"],
        "downgrade_count":  bin_counts.get("BIN1B", 0) + bin_counts.get("BIN1C", 0),
        "fail_count":       fail_c,
        "edge_count":       bin_counts["EDGE"],
        "bin_counts":       {k: v for k, v in bin_counts.items() if v > 0},
        "top_fail_tests":   [{"name": k, "count": v}
                             for k, v in sorted(fail_map.items(), key=lambda x: -x[1])[:5]],
        "top_downgrade_tests": [{"name": k, "count": v}
                                for k, v in sorted(down_map.items(), key=lambda x: -x[1])[:5]],
        "dies": dies,
    }
