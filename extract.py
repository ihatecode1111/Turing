import spacy
from pathlib import Path
import pandas as pd

# 加载中文模型
nlp = spacy.load("zh_core_web_sm")

# ====================== 友好标签映射 ======================
label_map = {
    "PERSON": "人物",
    "ORG": "机构/组织",
    "GPE": "地名/国家/城市",
    "LOC": "地点",
    "DATE": "日期",
    "TIME": "时间",
    "WORK_OF_ART": "作品/论文/书籍",
    "PRODUCT": "机器/产品",
    "EVENT": "事件",
    "FAC": "设施/建筑",
    "NORP": "民族/团体",
    "CARDINAL": "数字",
    "ORDINAL": "序数",
    "QUANTITY": "数量",
    "MONEY": "货币金额",
    "PERCENT": "百分比",
    # 如果还有其他标签，可以继续在这里添加
}

# 读取文章
text = Path("article.txt").read_text(encoding="utf-8")

# 实体抽取
doc = nlp(text)

print("=== 实体抽取结果（带友好解释）===")
entities = []

for ent in doc.ents:
    # 获取友好解释，如果没有映射就用原始标签
    friendly_label = label_map.get(ent.label_, ent.label_)
    
    entities.append({
        "实体": ent.text.strip(),
        "类型": ent.label_,           # 保留原始 spaCy 类型（方便调试）
        "解释": friendly_label         # ← 这里就是更友好的中文标签
    })
    
    print(f"{ent.text.strip()} → {friendly_label} ({ent.label_})")

# 创建 output 文件夹（防止报错）
Path("output").mkdir(exist_ok=True)

# 保存为 CSV
df = pd.DataFrame(entities)
df.to_csv("output/entities.csv", index=False, encoding="utf-8")
print("\n✅ 实体已保存到 output/entities.csv（共 {} 个实体）".format(len(entities)))