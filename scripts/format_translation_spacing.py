import csv
import re
import sys
from pathlib import Path

# 确保控制台输出使用 UTF-8，防止 Windows 平台上的 GBK 编码错误
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
master_csv_path = ROOT / "translation" / "ITR2_CN_master.csv"

# 私有区字符占位符定义，用以完全保护 HTML 标签和大括号变量
MASK_START = "\ue000"
MASK_END = "\ue001"

# HTML标签和花括号占位符的匹配
TAG_PATTERN = re.compile(r"(<[^<>]+>|\{[^{}]+\})")

def mask_tags(text):
    tags = []
    def repl(match):
        val = match.group(1)
        tags.append(val)
        return f"{MASK_START}_{len(tags)-1}_{MASK_END}"
    masked_text = TAG_PATTERN.sub(repl, text)
    return masked_text, tags

def unmask_tags(masked_text, tags):
    def repl(match):
        idx = int(match.group(1))
        return tags[idx]
    return re.sub(rf"{MASK_START}_(\d+)_{MASK_END}", repl, masked_text)

# 中文字符范围
CHINESE_CHAR_RE_STR = r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]"

# 英数字连字符片段定义
# 包含 A-Za-z0-9_'- 且其中必须含有至少一个英文字母 A-Za-z
# 边界 A: 汉字 + 英文/枪名片段
BOUNDARY_A_RE = re.compile(rf"({CHINESE_CHAR_RE_STR})(?=[A-Za-z0-9_'-]*[A-Za-z])([A-Za-z0-9_'-]+)")
# 边界 B: 英文/枪名片段 + 汉字
BOUNDARY_B_RE = re.compile(rf"((?=[A-Za-z0-9_'-]*[A-Za-z])[A-Za-z0-9_'-]+)({CHINESE_CHAR_RE_STR})")

# 音译枪名：音译枪名后如果紧随汉字，则也需要加空格
TRANSLITERATED_GUNS = ["莫辛-纳甘", "贝内利", "伯莱塔", "格洛克", "雷明顿", "野牛"]
TRANSLITERATED_RE = re.compile(rf"({'|'.join(TRANSLITERATED_GUNS)})({CHINESE_CHAR_RE_STR})")

def adjust_spacing(text):
    if not text:
        return text
    
    # 1. 保护 HTML 标签和大括号变量
    masked_text, tags = mask_tags(text)
    
    # 2. 调整中英文空格
    # 汉字 + 英文/枪名
    masked_text = BOUNDARY_A_RE.sub(r"\1 \2", masked_text)
    # 英文/枪名 + 汉字
    masked_text = BOUNDARY_B_RE.sub(r"\1 \2", masked_text)
    
    # 3. 调整音译枪名与其后的汉字
    masked_text = TRANSLITERATED_RE.sub(r"\1 \2", masked_text)
    
    # 4. 还原被保护的内容
    result = unmask_tags(masked_text, tags)
    return result

def main():
    print(f"Reading master CSV: {master_csv_path}")
    if not master_csv_path.exists():
        print(f"Error: {master_csv_path} does not exist.")
        return
        
    with master_csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
    print(f"Total rows read: {len(rows)}")
    
    changes_count = 0
    for idx, row in enumerate(rows):
        orig_trans = row["new_translation"] or ""
        adjusted_trans = adjust_spacing(orig_trans)
        if orig_trans != adjusted_trans:
            row["new_translation"] = adjusted_trans
            changes_count += 1
            # 打印前20条修改作为比对
            if changes_count <= 20:
                print(f"Row {idx+2} (Key: {row['key']}):")
                print(f"  [ORIG]: {orig_trans}")
                print(f"  [ADJU]: {adjusted_trans}")
                
    print(f"Total rows modified: {changes_count}")
    
    if changes_count > 0:
        with master_csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("Master CSV updated successfully.")
    else:
        print("No changes needed. CSV is already fully formatted.")

if __name__ == "__main__":
    main()
