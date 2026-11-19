"""
Etapa 3 - Questão 05: Análise multivariada e Regressão Linear Múltipla
Y (resposta)      = RDPC     (renda domiciliar per capita, R$)
X (explicativas)  = ANOSEST (anos de estudo), ESPVIDA (esperança de vida, anos), GINI (desigualdade)
Base: base_dados.csv (Atlas do Desenvolvimento Humano; 27 UFs x 2012-2021; n = 270)
Usa apenas numpy, pandas, scipy, matplotlib e seaborn.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

df = pd.read_csv("base_dados.csv")
Y = "RDPC"
XS = ["ANOSEST", "ESPVIDA", "GINI"]
VARS = [Y] + XS
d = df[VARS]
n, k = len(d), len(XS)
res = {"y": Y, "x": XS, "n": n}

# a) Gráfico de dispersão (matriz de dispersão) --------------------------------
g = sns.pairplot(d, corner=False, plot_kws={"alpha": 0.5, "s": 18, "color": "#1f3b73"},
                 diag_kws={"color": "#1f3b73"})
g.figure.suptitle("Matriz de dispersão: RDPC, ANOSEST, ESPVIDA e GINI", y=1.02)
g.savefig("figuras/q5a_dispersao.png", dpi=130); plt.close("all")

# b) Matriz de covariância e de correlação de Pearson --------------------------
cov = d.cov()
cor = d.corr(method="pearson")
res["matriz_covariancia"] = cov.round(4).to_dict()
res["matriz_correlacao"] = cor.round(4).to_dict()

# c) Gráfico da correlação de Pearson (mapa de calor) --------------------------
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cor, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, square=True,
            cbar_kws={"label": "Correlação de Pearson"}, ax=ax)
ax.set_title("Matriz de correlação linear de Pearson")
fig.tight_layout(); fig.savefig("figuras/q5c_correlacao.png", dpi=150); plt.close(fig)

# d) Regressão linear múltipla (MQO) --------------------------------------------
Xm = np.column_stack([np.ones(n), d[XS].to_numpy()])
y = d[Y].to_numpy()
XtX_inv = np.linalg.inv(Xm.T @ Xm)
beta = XtX_inv @ Xm.T @ y
y_hat = Xm @ beta
resid = y - y_hat

# e) Adequação: R², R² ajustado, Teste F e testes t -----------------------------
sqe = resid @ resid
sqt = np.sum((y - y.mean()) ** 2)
sqr = sqt - sqe
gl_res = n - k - 1
r2 = sqr / sqt
r2aj = 1 - (1 - r2) * (n - 1) / gl_res
F = (sqr / k) / (sqe / gl_res)
p_F = stats.f.sf(F, k, gl_res)
s2 = sqe / gl_res
ep = np.sqrt(np.diag(s2 * XtX_inv))
t = beta / ep
p_t = 2 * stats.t.sf(np.abs(t), gl_res)
nomes = ["Intercepto"] + XS
res["coeficientes"] = {nm: {"beta": b, "ep": e, "t": tt, "p": pp}
                       for nm, b, e, tt, pp in zip(nomes, beta, ep, t, p_t)}
res.update({"R2": r2, "R2_ajustado": r2aj, "F": F, "gl": [k, gl_res], "p_F": p_F,
            "F_critico_5pct": stats.f.ppf(0.95, k, gl_res),
            "erro_padrao_residuos": np.sqrt(s2),
            "shapiro_residuos_p": stats.shapiro(resid).pvalue})

# Multicolinearidade: VIF de cada explicativa
vif = {}
for j, nm in enumerate(XS):
    outros = [c for c in XS if c != nm]
    A = np.column_stack([np.ones(n), d[outros].to_numpy()])
    b = np.linalg.lstsq(A, d[nm].to_numpy(), rcond=None)[0]
    r2j = 1 - np.sum((d[nm].to_numpy() - A @ b) ** 2) / np.sum((d[nm] - d[nm].mean()) ** 2)
    vif[nm] = 1 / (1 - r2j)
res["VIF"] = vif

fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(y_hat, resid, alpha=0.6, color="#1f3b73", edgecolor="white")
ax.axhline(0, color="#c0392b")
ax.set_title("Resíduos x valores ajustados (regressão múltipla)")
ax.set_xlabel("Valores ajustados de RDPC (R$)"); ax.set_ylabel("Resíduo (R$)")
fig.tight_layout(); fig.savefig("figuras/q5e_residuos.png", dpi=150); plt.close(fig)

# f) Previsão com 3 variáveis explicativas ---------------------------------------
novo = {"ANOSEST": 10.0, "ESPVIDA": 76.0, "GINI": 0.50}
y_prev = beta[0] + sum(beta[i + 1] * novo[c] for i, c in enumerate(XS))
res["previsao"] = {"entrada": novo, "RDPC_prevista": y_prev,
                   "faixa_observada": {c: [d[c].min(), d[c].max()] for c in XS}}

def conv(o):
    if isinstance(o, dict): return {str(k_): conv(v) for k_, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
with open("resultados/q5.json", "w", encoding="utf-8") as f:
    json.dump(conv(res), f, indent=2, ensure_ascii=False)

pd.set_option("display.width", 120)
print("Matriz de covariância:\n", cov.round(3))
print("\nMatriz de correlação:\n", cor.round(3))
print("\nEquação: RDPC = " + f"{beta[0]:.3f} " +
      " ".join(f"{b:+.3f}*{c}" for b, c in zip(beta[1:], XS)))
for nm, b, e, tt, pp in zip(nomes, beta, ep, t, p_t):
    print(f"  {nm:10s} b={b:10.3f} EP={e:8.3f} t={tt:7.2f} p={pp:.3g}")
print(f"\nR² = {r2:.4f}  R² aj. = {r2aj:.4f}")
print(f"F({k},{gl_res}) = {F:.2f}  p = {p_F:.3g}  F crít. 5% = {res['F_critico_5pct']:.3f}")
print(f"EP resíduos = {np.sqrt(s2):.2f}   Shapiro resíduos p = {res['shapiro_residuos_p']:.4g}")
print("VIF:", {a: round(b, 2) for a, b in vif.items()})
print(f"Previsão {novo} -> RDPC = R$ {y_prev:.2f}")
print("Faixas observadas:", {c: (round(d[c].min(), 2), round(d[c].max(), 2)) for c in XS})
