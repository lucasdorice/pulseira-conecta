"""
Etapa 4 - Questão 06: Regressão Logística Binária
Resposta binária  : RENDA_ALTA = 1 se RDPC > mediana de RDPC (R$ 584,90); 0 caso contrário
Explicativas      : ANOSEST (anos de estudo), ESPVIDA (esperança de vida), GINI (desigualdade)
Base: base_dados.csv (Atlas do Desenvolvimento Humano; 27 UFs x 2012-2021; n = 270)
Obs.: RDPC não entra como explicativa (evita circularidade com a variável resposta).
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("base_dados.csv")
XS = ["ANOSEST", "ESPVIDA", "GINI"]
corte = df["RDPC"].median()
df["RENDA_ALTA"] = (df["RDPC"] > corte).astype(int)
res = {"corte_RDPC_mediana": corte, "n": len(df),
       "n_classe1": int(df.RENDA_ALTA.sum()), "n_classe0": int((1 - df.RENDA_ALTA).sum())}

def sigmoid(z): return 1 / (1 + np.exp(-z))

def ajusta_logit(X, y, it=100, tol=1e-10):
    """Máxima verossimilhança por Newton-Raphson (IRLS). X já inclui a constante."""
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = sigmoid(X @ b)
        W = p * (1 - p)
        H = X.T @ (X * W[:, None])
        passo = np.linalg.solve(H, X.T @ (y - p))
        b = b + passo
        if np.max(np.abs(passo)) < tol: break
    p = sigmoid(X @ b)
    cov = np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]))
    ll = np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))
    return b, np.sqrt(np.diag(cov)), ll

# a) Equação da regressão logística (ajuste com todos os dados) -----------------
X = np.column_stack([np.ones(len(df)), df[XS].to_numpy()])
y = df["RENDA_ALTA"].to_numpy()
b, ep, ll = ajusta_logit(X, y)
z = b / ep
pz = 2 * stats.norm.sf(np.abs(z))
ll0 = np.sum(y * np.log(y.mean()) + (1 - y) * np.log(1 - y.mean()))
nomes = ["Intercepto"] + XS
res["coeficientes"] = {nm: {"beta": bi, "ep": ei, "z": zi, "p": pi, "odds_ratio": float(np.exp(bi))}
                       for nm, bi, ei, zi, pi in zip(nomes, b, ep, z, pz)}
res["McFadden_R2"] = 1 - ll / ll0
res["LR_qui2"] = 2 * (ll - ll0)
res["LR_p"] = stats.chi2.sf(2 * (ll - ll0), len(XS))

# Conferência com scikit-learn (sem penalização)
sk = LogisticRegression(C=np.inf, max_iter=10000, tol=1e-10).fit(df[XS], y)
res["confere_sklearn_max_dif"] = float(np.max(np.abs(np.r_[sk.intercept_, sk.coef_[0]] - b)))

# b) Matriz de confusão e acurácia ------------------------------------------------
prob = sigmoid(X @ b)
pred = (prob >= 0.5).astype(int)
def metricas(yv, pv, pr):
    tn, fp, fn, tp = confusion_matrix(yv, pv).ravel()
    return {"matriz": [[int(tn), int(fp)], [int(fn), int(tp)]],
            "acuracia": (tn + tp) / len(yv), "sensibilidade": tp / (tp + fn),
            "especificidade": tn / (tn + fp), "precisao": tp / (tp + fp),
            "auc": roc_auc_score(yv, pr)}
res["completa"] = metricas(y, pred, prob)

# Validação: treino em 19 UFs e teste em 8 UFs (divisão por UF para evitar vazamento
# entre anos de uma mesma UF)
rng = np.random.default_rng(42)
ufs = df["UF"].unique(); teste_ufs = rng.choice(ufs, 8, replace=False)
m_te = df["UF"].isin(teste_ufs).to_numpy()
bt, _, _ = ajusta_logit(X[~m_te], y[~m_te])
pr_te = sigmoid(X[m_te] @ bt)
res["teste_ufs"] = sorted(map(str, teste_ufs))
res["validacao"] = metricas(y[m_te], (pr_te >= 0.5).astype(int), pr_te)
res["validacao"]["n_teste"] = int(m_te.sum())

# Gráficos
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for a, (titulo, M) in zip(ax, [("Todos os dados (n=270)", res["completa"]["matriz"]),
                               (f"Validação em 8 UFs (n={int(m_te.sum())})", res["validacao"]["matriz"])]):
    sns.heatmap(np.array(M), annot=True, fmt="d", cmap="Blues", cbar=False, ax=a,
                xticklabels=["Prev. 0", "Prev. 1"], yticklabels=["Real 0", "Real 1"])
    a.set_title(titulo)
fig.suptitle("Matriz de confusão (1 = renda per capita acima da mediana)")
fig.tight_layout(); fig.savefig("figuras/q6b_matriz_confusao.png", dpi=150); plt.close(fig)

fpr, tpr, _ = roc_curve(y, prob)
fig, ax = plt.subplots(figsize=(5, 4.5))
ax.plot(fpr, tpr, color="#1f3b73", label=f"AUC = {res['completa']['auc']:.3f}")
ax.plot([0, 1], [0, 1], "--", color="gray")
ax.set_xlabel("1 - Especificidade"); ax.set_ylabel("Sensibilidade")
ax.set_title("Curva ROC da regressão logística"); ax.legend()
fig.tight_layout(); fig.savefig("figuras/q6_roc.png", dpi=150); plt.close(fig)

# c) Classificação de novos casos (3 variáveis explicativas) -----------------------
casos = [{"ANOSEST": 10.0, "ESPVIDA": 76.0, "GINI": 0.50},
         {"ANOSEST": 7.5, "ESPVIDA": 71.0, "GINI": 0.55}]
res["classificacoes"] = []
for c in casos:
    zc = b[0] + sum(b[i + 1] * c[v] for i, v in enumerate(XS))
    pc = float(sigmoid(zc))
    res["classificacoes"].append({"entrada": c, "logit": float(zc), "prob": pc,
                                  "classe": int(pc >= 0.5)})

def conv(o):
    if isinstance(o, dict): return {str(k): conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
with open("resultados/q6.json", "w", encoding="utf-8") as f:
    json.dump(conv(res), f, indent=2, ensure_ascii=False)

print(f"Corte (mediana RDPC) = R$ {corte:.2f}  classe1={res['n_classe1']}  classe0={res['n_classe0']}")
print("logit(p) = " + f"{b[0]:.4f} " + " ".join(f"{bi:+.4f}*{v}" for bi, v in zip(b[1:], XS)))
for nm, bi, ei, zi, pi in zip(nomes, b, ep, z, pz):
    print(f"  {nm:10s} b={bi:9.4f} EP={ei:8.4f} z={zi:7.2f} p={pi:.3g} OR={np.exp(bi):.4g}")
print(f"McFadden R²={res['McFadden_R2']:.4f}  LR χ²={res['LR_qui2']:.2f} p={res['LR_p']:.3g}")
print("Dif. máx vs sklearn:", res["confere_sklearn_max_dif"])
for nome in ["completa", "validacao"]:
    r = res[nome]
    print(f"\n[{nome}] matriz={r['matriz']} acurácia={r['acuracia']:.4f} sens={r['sensibilidade']:.4f} "
          f"espec={r['especificidade']:.4f} prec={r['precisao']:.4f} AUC={r['auc']:.4f}")
print("UFs de teste:", res["teste_ufs"])
for c in res["classificacoes"]:
    print(c)
