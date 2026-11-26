import time
import mlflow, pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from rag.classify import classify, PROMPT_VERSION
from rag.llm import MODEL

df = pd.read_csv("eval/test_set.csv")
df = df[df["adkar_humain"].notna()]
preds = []
for i, text in enumerate(df["text"], 1):
    preds.append(classify(text)["adkar_stage"])
    print(f"{i}/{len(df)}", end="\r")
    time.sleep(1)
df["adkar_llm"] = preds
df.to_csv(f"eval/results_{PROMPT_VERSION}.csv", index=False)

acc = accuracy_score(df["adkar_humain"], df["adkar_llm"])
print(f"\nAccuracy : {acc:.0%}\n")
print(classification_report(df["adkar_humain"], df["adkar_llm"], zero_division=0))
print(pd.crosstab(df["adkar_humain"], df["adkar_llm"]))

mlflow.set_experiment("adkar-classification")
with mlflow.start_run(run_name=PROMPT_VERSION):
    mlflow.log_params({"prompt_version": PROMPT_VERSION, "llm": MODEL, "n_test": len(df)})
    mlflow.log_metric("accuracy", acc)
    mlflow.log_artifact(f"eval/results_{PROMPT_VERSION}.csv")