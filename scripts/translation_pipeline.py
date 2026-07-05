import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "translation" / "ITR2_CN_master.csv"
CURRENT_SOURCE_CSV = ROOT / "notes" / "english_source_current_probe.csv"

EXTRA_BLUEPRINT_ROWS = [
    {
        "key": "6F632A8D4F0E819C11B70D94DD088076",
        "text": "Critical Damage Chance",
        "new_translation": "暴击伤害几率",
        "notes": "extra_blueprint_key",
    },
    {
        "key": "1651B78043E93A1063C7DB928F90A865",
        "text": "Critical Damage Multiplier",
        "new_translation": "暴击伤害倍数",
        "notes": "extra_blueprint_key",
    },
    {
        "key": "44CB5BB84F04285E8C0A59B71B273E2B",
        "text": "Need to insert ammo box first",
        "new_translation": "请先插入弹药盒",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "4712CCB64C555D9096DE558EC26C48F7",
        "text": "Need to insert mag first",
        "new_translation": "请先插入弹匣",
        "notes": "raw_asset_text_probe_20260705",
    },
    {
        "key": "7B578A434CAA59FA50AEC08E7995C7CE",
        "text": "Mag and ammo box are incompatible",
        "new_translation": "弹匣与弹药盒不兼容",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "718532FA495485ACC1ACE2855CC37143",
        "text": "Mag is full — can't load ammo to it",
        "new_translation": "弹匣已满——无法继续装填",
        "notes": "raw_asset_text_probe_20260705",
    },
    {
        "key": "F797E76841F101620F0302AAF412B516",
        "text": "Ammo box is empty — can't load ammo from it",
        "new_translation": "弹药盒已空——无法继续装填",
        "notes": "raw_asset_text_probe_20260705",
    },
    {
        "key": "373E49414B52687EDB2995B0C40C6BD0",
        "text": "This mag cannot take ammo from ammo loader",
        "new_translation": "该弹匣无法从装弹器装填",
        "notes": "raw_asset_text_probe_20260705",
    },
    {
        "key": "4B6B21EE4658F6268DD5B8931E2ED491",
        "text": "No unbought ammo in the mag",
        "new_translation": "弹匣中没有未结算弹药",
        "notes": "raw_asset_text_probe_20260705",
    },
    {
        "key": "013AFD64401A537A996D909322FF143D",
        "text": "Not found",
        "new_translation": "未找到",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "F3F66CB94CDD9B0AE45F8B92100FAB71",
        "text": "Measurement",
        "new_translation": "测量",
        "notes": "raw_asset_text_probe_20260704|key_alignment_fix_20260705",
    },
    {
        "key": "48FEA94B43498BA0086D6BACDDABA292",
        "text": "Metric",
        "new_translation": "公制",
        "notes": "raw_asset_text_probe_20260704|key_alignment_fix_20260705",
    },
    {
        "key": "0185BCCD483EDA65844454AC76A01419",
        "text": "Imperial",
        "new_translation": "英制",
        "notes": "raw_asset_text_probe_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "FF9B5C294C75DE489E67CF8075CF7AAD",
        "text": "Finish",
        "new_translation": "完成",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "F5C1F8024F9CA678C4B982BE3C26E5E5",
        "text": "Start",
        "new_translation": "开始",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "5271051845EC6C545EEAE9BD9E1B2939",
        "text": "System booting up...",
        "new_translation": "系统正在启动...",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "7555A77042AAE45E8742E7B52B700BE1",
        "text": "Please wait...",
        "new_translation": "请稍候...",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "0715E9D74503D01C91E8ADB77BDAB703",
        "text": "Initializing components...",
        "new_translation": "正在初始化组件...",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "C097139C4DEAB23A188AE2BEC0E1BF5A",
        "text": "Checking device connections...",
        "new_translation": "正在检查设备连接...",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "269C39FC4090B73A4EFF0991F7FC572B",
        "text": "Loading operating system...",
        "new_translation": "正在加载操作系统...",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "AF0F82444018178CD15C5EAF02B976A5",
        "text": "Show",
        "new_translation": "显示",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "3A339A424B94B1582586EF8A5A0FC385",
        "text": "In Progress",
        "new_translation": "进行中",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "50776DA34EF627D87E0922985297741B",
        "text": "UNPSC Explorers",
        "new_translation": "UNPSC 探索者",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "EF1AE93746A87E656DB4D8B5D2344814",
        "text": "Pass",
        "new_translation": "通过",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "833004CA4C1E9D10B05FBB99B7695547",
        "text": "Pass",
        "new_translation": "通过",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "750BFF584257DFD856B1519B35534409",
        "text": "Skip",
        "new_translation": "跳过",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "47E20FEC42A3BAF0A69BEF9229FD5003",
        "text": "Skip",
        "new_translation": "跳过",
        "notes": "raw_asset_text_probe_20260704",
    },
    {
        "key": "6912D366473F5161D4022D9FD8F75A5F",
        "text": "<b>Carry Load</b>Indicates how much weight the Explorer is currently carrying relative to their total capacity.<L2><b>Armor Protection Level</b>",
        "new_translation": "<b>负重</b>显示探索者当前携带重量占总承重的比例。<L2><b>护甲防护等级</b>",
        "notes": "raw_asset_text_probe_20260705",
    },
    {
        "key": "E63E5DDE4613E294F07D90A946E20AF4",
        "text": "Bring your <b>watch</b> to the door lock\r\nto access <b>Training ground</b>.",
        "new_translation": "将你的<b>手表</b>靠近门锁\r\n以进入<b>训练场</b>。",
        "notes": "raw_asset_text_probe_20260705|source_variant|crlf_source_fix_20260705",
        "allow_duplicate_key": True,
    },
    {
        "key": "45B0597F481B8A014E5E8797F5C5CD6B",
        "text": "- The UNPSC Facility 27 Training Ground (requires specific mission)",
        "new_translation": "- UNPSC 27 号基地训练场（需特定任务解锁）",
        "notes": "raw_asset_text_probe_20260705|source_variant",
        "allow_duplicate_key": True,
    },
    {
        "key": "BCA1D7B34EDA55B09CCB4C9CBFE92796",
        "text": "- Explorer Basic Training Course (requires specific mission)",
        "new_translation": "- 探索者基础训练课程（需特定任务解锁）",
        "notes": "raw_asset_text_probe_20260705|source_variant",
        "allow_duplicate_key": True,
    },
    {
        "key": "5A84049B4D087545FFCAE2B11EDA3B46",
        "text": "- Explorer Starter Kit (issued during Explorer Basic Training Course)",
        "new_translation": "- 探索者新手装备包（在探索者基础训练课程中发放）",
        "notes": "raw_asset_text_probe_20260705|source_variant",
        "allow_duplicate_key": True,
    },
    {
        "key": "84368BC1432A0F54DB4A4F857AD513A6",
        "text": "Friend Name",
        "new_translation": "好友名称",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "570345814D9B3332EB2E9D85E9591C24",
        "text": "Waiting for reply",
        "new_translation": "等待回复",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "CC40892945C1118361AB3C991CC988B9",
        "text": "Already on the squad",
        "new_translation": "已在小队中",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "9588C14E4C59FA5C279B9BBB245ED1DE",
        "text": "Unable to invite",
        "new_translation": "无法邀请",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "D49A6CAA406612C866FB24A76FB6FC6D",
        "text": "Invite",
        "new_translation": "邀请",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "A3B1685C43EEA7B80D5820889DEC17D6",
        "text": "Ammo charge machine",
        "new_translation": "装弹器",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705",
    },
    {
        "key": "17D131D34C68A524573B94AF56DE32A7",
        "text": "-undefined-",
        "new_translation": " ",
        "notes": "raw_asset_text_audit_20260705|key_alignment_fix_20260705|placeholder_blank",
    },
    {
        "key": "EE4C460F434AEA4411EA4A9F976D6400",
        "text": "Wait until scanning is over.",
        "new_translation": "等待扫描完成。",
        "notes": "raw_asset_text_audit_20260705",
    },
    {
        "key": "011542634EDBB265EFB38ABE8AB9C6A8",
        "text": "Software licensed under the ownership of UNPSC Corporation.",
        "new_translation": "本软件授权归 UNPSC 公司所有。",
        "notes": "raw_asset_text_audit_20260705",
    },
    {
        "key": "69DD8E7448C70EF4A3B106B9CF53896C",
        "text": "Main Menu",
        "new_translation": "主菜单",
        "notes": "raw_asset_text_audit_20260705|source_variant",
        "allow_duplicate_key": True,
    },
    {
        "key": "2BD7FF5A42FEAB6E3CB65DA996BD9B70",
        "text": "Access Mission Points",
        "new_translation": "接入任务点",
        "notes": "raw_asset_text_audit_20260705",
    },
    {
        "key": "7EDF1A544BDDDFF30E4538809C1FB5E8",
        "text": "Show details",
        "new_translation": "显示详情",
        "notes": "raw_asset_text_audit_20260705|source_variant",
        "allow_duplicate_key": True,
    },
    {
        "key": "7EDF1A544BDDDFF30E4538809C1FB5E8",
        "text": "Hide details",
        "new_translation": "隐藏详情",
        "notes": "raw_asset_text_audit_20260705|source_variant",
        "allow_duplicate_key": True,
    },
    {
        "key": "47BA2E794AD4060FE50CDA967EF9E536",
        "text": "I broke down",
        "new_translation": "我坏掉了",
        "notes": "raw_asset_text_audit_20260705",
    },
    {
        "key": "51D2CAE94DC1F33D24708E946420B206",
        "text": "I broke down",
        "new_translation": "我坏掉了",
        "notes": "raw_asset_text_audit_20260705",
    },
    {
        "key": "8A0AC0D840310FCA66C8BDB4242F01C0",
        "text": "I broke down",
        "new_translation": "我坏掉了",
        "notes": "raw_asset_text_audit_20260705",
    },
    {
        "key": "703A893C42F84072BBCB388CED98B70F",
        "text": "Hey, buddy!",
        "new_translation": "嘿，伙计！",
        "notes": "raw_asset_text_audit_20260705",
    },
]


CSV_FIELDS = [
    "text",
    "new_translation",
    "notes",
    "key",
    "source_hash",
    "row_no",
    "category",
    "source",
]

LINE_INDENT_RE = re.compile(r"\n[ \t]+")

CRC_TABLE = []
for i in range(256):
    crc = i
    for _ in range(8):
        crc = ((crc >> 1) ^ 0xEDB88320) if crc & 1 else (crc >> 1)
    CRC_TABLE.append(crc & 0xFFFFFFFF)


def ue_str_crc32(value, base=0):
    crc = (~base) & 0xFFFFFFFF
    for char in value:
        code = ord(char)
        for _ in range(4):
            crc = ((crc >> 8) ^ CRC_TABLE[(crc ^ code) & 0xFF]) & 0xFFFFFFFF
            code >>= 8
    return (~crc) & 0xFFFFFFFF


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=CSV_FIELDS):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_note(existing, addition):
    parts = [p for p in (existing or "").split("|") if p]
    if addition and addition not in parts:
        parts.append(addition)
    return "|".join(parts)


def normalize_active_translation(value):
    return LINE_INDENT_RE.sub("\n", value or "")


def build_row(key, text, idx, current, default_translation, source):
    new_translation = current.get("new_translation") or default_translation or text
    notes = current.get("notes", "")

    if text in {"Placeholder text", "-undefined-"}:
        new_translation = " "
        notes = merge_note(notes, "placeholder_blank")

    return {
        "text": text,
        "new_translation": normalize_active_translation(new_translation),
        "notes": notes,
        "key": key,
        "source_hash": str(ue_str_crc32(text)),
        "row_no": str(idx),
        "category": current.get("category", ""),
        "source": source,
    }


def build_master_rows():
    source_rows = read_csv(CURRENT_SOURCE_CSV)
    if not source_rows:
        raise FileNotFoundError(f"missing source CSV: {CURRENT_SOURCE_CSV}")

    master_rows = read_csv(MASTER_CSV)
    master = {row["key"]: row for row in master_rows}
    master_by_key_text = {(row["key"], row["text"]): row for row in master_rows}
    rows = []
    seen = set()
    for idx, source in enumerate(source_rows, 1):
        key = source["key"]
        text = source["text"]
        current = master_by_key_text.get((key, text), master.get(key, {}))
        rows.append(build_row(key, text, idx, current, text, "EnglishSource.uasset"))
        seen.add(key)

    for extra in EXTRA_BLUEPRINT_ROWS:
        if extra["key"] in seen and not extra.get("allow_duplicate_key"):
            continue
        current = {}
        row = build_row(
            extra["key"],
            extra["text"],
            len(rows) + 1,
            current,
            extra["new_translation"],
            "extra_blueprint",
        )
        row["notes"] = merge_note(row["notes"], extra["notes"])
        rows.append(row)

    return rows
