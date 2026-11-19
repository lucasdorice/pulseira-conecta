"""
Etapa 2 - Questão 04: Análise bivariada e Regressão Linear Simples
X (explicativa) = ANOSEST  (anos de estudo)
Y (resposta)    = RDPC     (renda domiciliar per capita, R$)
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
X, Y = "ANOSEST", "RDPC"
x, y = df[X].to_numpy(), df[Y].to_numpy()
n = len(x)
res = {"x": X, "y": Y, "n": n}

# a) Gráfico de dispersão -----------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(x, y, alpha=0.6, color="#1f3b73", edgecolor="white")
ax.set_title("Dispersão: anos de estudo x renda domiciliar per capita (UFs, 2012-2021)")
ax.set_xlabel("Anos de estudo (ANOSEST)")
ax.set_ylabel("Renda domiciliar per capita em R$ (RDPC)")
fig.tight_layout(); fig.savefig("figuras/q4a_dispersao.png", dpi=150); plt.close(fig)

# b) Covariância e correlação de Pearson ---------------------------------------
cov = np.cov(x, y, ddof=1)[0, 1]
r, p_r = stats.pearsonr(x, y)
res["covariancia"], res["pearson_r"], res["pearson_p"] = cov, r, p_r

# c) Gráfico da correlação linear de Pearson (mapa de calor) ------------------
fig, ax = plt.subplots(figsize=(4.8, 4))
sns.heatmap(df[[X, Y]].corr(), annot=True, fmt=".3f", cmap="Blues", vmin=0, vmax=1,
            square=True, cbar_kws={"label": "Correlação de Pearson"}, ax=ax)
ax.set_title("Correlação linear de Pearson")
fig.tight_layout(); fig.savefig("figuras/q4c_correlacao.png", dpi=150); plt.close(fig)

# d) Regressão linear simples (mínimos quadrados) ------------------------------
b1 = cov / np.var(x, ddof=1)
b0 = y.mean() - b1 * x.mean()
y_hat = b0 + b1 * x
res["b0"], res["b1"] = b0, b1

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(x, y, alpha=0.6, color="#1f3b73", edgecolor="white", label="Observações")
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, b0 + b1 * xs, color="#c0392b", lw=2,
        label=f"RDPC = {b0:.2f} + {b1:.2f}·ANOSEST")
ax.set_title("Regressão linear simples: renda per capita x anos de estudo")
ax.set_xlabel("Anos de estudo (ANOSEST)")
ax.set_ylabel("Renda domiciliar per capita em R$ (RDPC)")
ax.legend()
fig.tight_layout(); fig.savefig("figuras/q4d_regressao.png", dpi=150); plt.close(fig)

# e) Adequação do modelo: R², Teste F e teste t ---------------------------------
sqe = np.sum((y - y_hat) ** 2)            # soma dos quadrados dos resíduos
sqt = np.sum((y - y.mean()) ** 2)         # soma dos quadrados totais
sqr = sqt - sqe                           # soma dos quadrados da regressão
r2 = sqr / sqt
gl_res = n - 2
F = (sqr / 1) / (sqe / gl_res)
p_F = stats.f.sf(F, 1, gl_res)
ep_b1 = np.sqrt((sqe / gl_res) / np.sum((x - x.mean()) ** 2))
t_b1 = b1 / ep_b1
res.update({"R2": r2, "R2_ajustado": 1 - (1 - r2) * (n - 1) / gl_res,
            "F": F, "gl": [1, gl_res], "p_F": p_F, "ep_b1": ep_b1, "t_b1": t_b1,
            "erro_padrao_residuos": np.sqrt(sqe / gl_res),
            "F_critico_5pct": stats.f.ppf(0.95, 1, gl_res)})

# Normalidade dos resíduos (diagnóstico complementar)
sw = stats.shapiro(y - y_hat)
res["shapiro_residuos_p"] = sw.pvalue
fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(y_hat, y - y_hat, alpha=0.6, color="#1f3b73", edgecolor="white")
ax.axhline(0, color="#c0392b")
ax.set_title("Resíduos x valores ajustados (regressão simples)")
ax.set_xlabel("Valores ajustados de RDPC (R$)"); ax.set_ylabel("Resíduo (R$)")
fig.tight_layout(); fig.savefig("figuras/q4e_residuos.png", dpi=150); plt.close(fig)

# f) Previsão -----------------------------------------------------------------
x_novo = 10.0
y_prev = b0 + b1 * x_novo
res["previsao"] = {"ANOSEST": x_novo, "RDPC_prevista": y_prev,
                   "dentro_do_intervalo_observado": bool(x.min() <= x_novo <= x.max()),
                   "ANOSEST_min": x.min(), "ANOSEST_max": x.max()}

def conv(o):
    if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, np.bool_): return bool(o)
    return o
with open("resultados/q4.json", "w", encoding="utf-8") as f:
    json.dump(conv(res), f, indent=2, ensure_ascii=False)

print(f"n = {n}")
print(f"Covariância (amostral) = {cov:.4f}")
print(f"Pearson r = {r:.4f}  (p = {p_r:.3g})")
print(f"Equação: RDPC = {b0:.4f} + {b1:.4f} * ANOSEST")
print(f"R² = {r2:.4f}  R² ajustado = {res['R2_ajustado']:.4f}")
print(f"F(1,{gl_res}) = {F:.2f}  p = {p_F:.3g}  F crítico 5% = {res['F_critico_5pct']:.3f}")
print(f"t(b1) = {t_b1:.2f}  EP(b1) = {ep_b1:.3f}")
print(f"Erro padrão dos resíduos = {res['erro_padrao_residuos']:.2f} R$")
print(f"Shapiro dos resíduos: p = {sw.pvalue:.4g}")
print(f"Previsão: ANOSEST = {x_novo} -> RDPC = R$ {y_prev:.2f}")
print(f"ANOSEST observado: {x.min():.2f} a {x.max():.2f}")
