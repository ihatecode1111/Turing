import spacy
from pathlib import Path
import pandas as pd

# 加载模型
nlp = spacy.load("zh_core_web_sm")

# ====================== 友好标签映射 ======================
label_map = {
    "PERSON": "人物",
    "ORG": "机构/组织",
    "GPE": "地名/国家/城市",
    "LOC": "地点",
    "DATE": "日期",
    "TIME": "时间",
    "WORK_OF_ART": "作品/论文",
    "PRODUCT": "机器/产品",
    "EVENT": "事件",
    "FAC": "设施/建筑",
    "NORP": "团体",
}

# 读取文章
text = Path("article.txt").read_text(encoding="utf-8")
doc = nlp(text)

print("=== 实体抽取结果 ===")
entities = []
for ent in doc.ents:
    friendly = label_map.get(ent.label_, ent.label_)
    entities.append({
        "实体": ent.text.strip(),
        "类型": ent.label_,
        "解释": friendly
    })
    print(f"{ent.text.strip()} → {friendly} ({ent.label_})")

# ====================== 关系抽取（核心升级部分） ======================
print("\n=== 关系抽取结果 ===")
relations = []

# 常见中文关系模式（针对图灵生平文章优化）
relation_patterns = [
    ("就读于", "STUDIED_AT"),
    ("考入", "STUDIED_AT"),
    ("工作于", "WORKED_AT"),
    ("任职", "WORKED_AT"),
    ("在", "WORKED_AT"),      # 后面接机构
    ("破解", "BROKE"),
    ("破译", "BROKE"),
    ("提出", "PROPOSED"),
    ("开发", "DEVELOPED"),
    ("发明", "DEVELOPED"),
    ("参与", "PARTICIPATED_IN"),
    ("合作", "COLLABORATED_WITH"),
    ("影响", "INFLUENCED"),
    ("撰写", "AUTHORED"),
    ("发表", "AUTHORED"),
    ("主持", "HOSTED"),
]

for sent in doc.sents:                     # 按句子处理
    sent_text = sent.text
    sent_entities = [ent for ent in doc.ents if ent.start >= sent.start and ent.end <= sent.end]
    
    if len(sent_entities) < 2:
        continue
        
    # 简单规则匹配关系
    for i in range(len(sent_entities)-1):
        head = sent_entities[i]
        tail = sent_entities[i+1]
        
        # 在两个实体之间查找关系关键词
        between = sent_text[head.end_char:tail.start_char]
        
        for chinese_pattern, english_relation in relation_patterns:
            if chinese_pattern in between or chinese_pattern in sent_text:
                relations.append({
                    "头实体": head.text.strip(),
                    "关系": english_relation,
                    "尾实体": tail.text.strip(),
                    "关系中文": chinese_pattern
                })
                print(f"{head.text.strip()} --[{english_relation}]--> {tail.text.strip()} ({chinese_pattern})")
                break

# ====================== 保存文件 ======================
Path("output").mkdir(exist_ok=True)

# 保存实体
df_entities = pd.DataFrame(entities)
df_entities.to_csv("output/entities.csv", index=False, encoding="utf-8")

# 保存关系（三元组）
df_relations = pd.DataFrame(relations)
df_relations.to_csv("output/relations.csv", index=False, encoding="utf-8")

print(f"\n✅ 完成！共抽取 {len(entities)} 个实体，{len(relations)} 条关系")
print("   - entities.csv  → 实体列表")
print("   - relations.csv → 关系三元组（知识图谱核心数据）")

# ====================== 自动生成 Mermaid 知识图谱代码 ======================
print("\n=== 可直接复制到 mermaid.live 的知识图谱代码 ===")
print("```mermaid")
print("graph TD")
for _, row in df_relations.iterrows():
    head = row["头实体"].replace(" ", "_").replace("-", "")
    tail = row["尾实体"].replace(" ", "_").replace("-", "")
    rel = row["关系"]
    print(f"    {head} -->|{rel}| {tail}")
print("```")