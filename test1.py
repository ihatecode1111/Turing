import spacy
from pathlib import Path
import pandas as pd

nlp = spacy.load("zh_core_web_sm")

# ====================== 友好标签映射 ======================
label_map = {
    "PERSON": "人物", "ORG": "机构/组织", "GPE": "地名/国家/城市",
    "LOC": "地点", "DATE": "日期", "TIME": "时间",
    "WORK_OF_ART": "作品/论文", "PRODUCT": "机器/产品",
    "EVENT": "事件", "FAC": "设施/建筑", "NORP": "团体",
}

# 读取文章
text = Path("article.txt").read_text(encoding="utf-8")
doc = nlp(text)

print("=== 实体抽取结果 ===")
entities = []
for ent in doc.ents:
    friendly = label_map.get(ent.label_, ent.label_)
    entities.append({"实体": ent.text.strip(), "类型": ent.label_, "解释": friendly})
    print(f"{ent.text.strip()} → {friendly} ({ent.label_})")

# ====================== 加强版关系抽取 ======================
print("\n=== 关系抽取结果 ===")
relations = []

relation_patterns = [
    ("出生于", "BORN_IN"), ("考入", "STUDIED_AT"), ("就读于", "STUDIED_AT"),
    ("工作于", "WORKED_AT"), ("任职", "WORKED_AT"), ("在", "WORKED_AT"),
    ("破解", "BROKE"), ("破译", "BROKE"), ("开发", "DEVELOPED"),
    ("提出", "PROPOSED"), ("发明", "DEVELOPED"), ("参与", "PARTICIPATED_IN"),
    ("合作", "COLLABORATED_WITH"), ("影响", "INFLUENCED"), ("撰写", "AUTHORED"),
    ("发表", "AUTHORED"), ("主持", "HOSTED"), ("基于", "BASED_ON"),
    ("应用于", "APPLIED"), ("用于", "USED_IN"),
]

for sent in doc.sents:
    sent_entities = [ent for ent in doc.ents if ent.start >= sent.start and ent.end <= sent.end]
    if len(sent_entities) < 2:
        continue
    
    for i in range(len(sent_entities)-1):
        head = sent_entities[i]
        tail = sent_entities[i+1]
        between = sent.text[head.end_char:tail.start_char]
        
        matched = False
        for chinese_pattern, english_relation in relation_patterns:
            if chinese_pattern in between or chinese_pattern in sent.text:
                relations.append({
                    "头实体": head.text.strip(),
                    "关系": english_relation,
                    "尾实体": tail.text.strip(),
                    "关系中文": chinese_pattern
                })
                print(f"{head.text.strip()} --[{english_relation}]--> {tail.text.strip()} ({chinese_pattern})")
                matched = True
                break
        
        if not matched:
            relations.append({
                "头实体": head.text.strip(),
                "关系": "RELATED_TO",
                "尾实体": tail.text.strip(),
                "关系中文": "相关"
            })
            print(f"{head.text.strip()} --[RELATED_TO]--> {tail.text.strip()} (同句共现)")

# ====================== 保存实体和关系 ======================
Path("output").mkdir(exist_ok=True)
pd.DataFrame(entities).to_csv("output/entities.csv", index=False, encoding="utf-8")
pd.DataFrame(relations).to_csv("output/relations.csv", index=False, encoding="utf-8")

print(f"\n✅ 抽取完成！实体: {len(entities)} 个 | 关系: {len(relations)} 条")

# ====================== 自动生成并保存 Mermaid 代码 ======================
mermaid_content = """graph TD
    %% 节点
"""

for e in entities:
    node_id = e["实体"].replace(" ", "_").replace("·", "").replace("-", "").replace("·", "")
    mermaid_content += f'    {node_id}[{e["实体"]}]\n'

mermaid_content += "\n    %% 关系\n"
for r in relations:
    head = r["头实体"].replace(" ", "_").replace("·", "").replace("-", "")
    tail = r["尾实体"].replace(" ", "_").replace("·", "").replace("-", "")
    rel = r["关系"]
    mermaid_content += f"    {head} -->|{rel}| {tail}\n"

# 保存到文件
mermaid_file = Path("output/turing_knowledge_graph.mermaid")
mermaid_file.write_text(mermaid_content, encoding="utf-8")

print(f"\n✅ Mermaid 知识图谱代码已自动保存！")
print(f"   文件路径：output/turing_knowledge_graph.mermaid")
print(f"   直接打开这个文件，或复制里面的内容到 https://mermaid.live/ 即可看到图谱")