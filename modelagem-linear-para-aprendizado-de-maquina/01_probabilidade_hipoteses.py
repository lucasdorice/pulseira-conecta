"""
Etapa 1 - Questões 02 e 03: Distribuição Normal e Teste de Hipótese para a média
Base: base_dados.csv (Atlas do Desenvolvimento Humano - PNUD/Ipea/FJP; 27 UFs x 2012-2021)
Variável analisada: ANOSEST (anos de estudo), suposta Normal (Shapiro-Wilk p ~ 0,07).
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("base_dados.csv")
VAR = "ANOSEST"
x = df[VAR]

mu = x.mean()
sigma = x.std(ddof=0)          # desvio padrão populacional dos dados
mediana = x.median()
res = {"variavel": VAR, "N": int(len(x)), "media": mu, "desvio_padrao_pop": sigma,
       "mediana": mediana}

# Normalidade (apenas verificação da suposição do enunciado)
sw = stats.shapiro(x)
res["shapiro_W"], res["shapiro_p"] = sw.statistic, sw.pvalue

def classifica(p):
    """Classificação do evento pelo resultado probabilístico."""
    if p == 0: return "evento impossível"
    if p == 1: return "evento certo"
    if np.isclose(p, 0.5, atol=1e-9): return "evento equiprovável"
    if p < 0.5: return "evento improvável (pouco provável)"
    return "evento provável"

# ---------------- Questão 02 ----------------
p_a = stats.norm.cdf(mu, loc=mu, scale=sigma)                 # P(X < média)
p_b = 1 - stats.norm.cdf(mediana, loc=mu, scale=sigma)        # P(X > mediana)
res["q2a"] = {"prob": p_a, "classe": classifica(p_a)}
res["q2b"] = {"prob": p_b, "classe": classifica(p_b)}

fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
t = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 500)
pdf = stats.norm.pdf(t, mu, sigma)
for a, lim, lado, p, titulo in [
    (ax[0], mu, "esq", p_a, f"(a) P(X < média = {mu:.2f})"),
    (ax[1], mediana, "dir", p_b, f"(b) P(X > mediana = {mediana:.2f})")]:
    a.plot(t, pdf, color="#1f3b73")
    m = t < lim if lado == "esq" else t > lim
    a.fill_between(t[m], pdf[m], color="#e07a1f", alpha=0.6)
    a.set_title(f"{titulo} = {p:.4f}")
    a.set_xlabel("Anos de estudo (ANOSEST)")
ax[0].set_ylabel("Densidade")
fig.suptitle("Distribuição Normal ajustada aos anos de estudo (27 UFs, 2012-2021)")
fig.tight_layout(); fig.savefig("figuras/q2_normal.png", dpi=150); plt.close(fig)

# ---------------- Questão 03 ----------------
def teste_z(amostra, mu0, sig, alpha, cauda):
    n = len(amostra); xbar = amostra.mean()
    z = (xbar - mu0) / (sig / np.sqrt(n))
    if cauda == "esq":
        zc = stats.norm.ppf(alpha); p = stats.norm.cdf(z); rej = z < zc
    else:
        zc = stats.norm.ppf(1 - alpha); p = 1 - stats.norm.cdf(z); rej = z > zc
    return {"n": n, "media_amostral": xbar, "z_calc": z, "z_critico": zc,
            "p_valor": p, "alpha": alpha, "rejeita_H0": bool(rej)}

# Amostras aleatórias (seed fixa) extraídas de subgrupos reais da base:
#  (a) 20 observações da região Nordeste (média amostral < média de referência)
#  (b) 25 observações de Sul + Sudeste (média amostral > média de referência)
ne = df.loc[df.REGIAO == "Nordeste", VAR].sample(20, random_state=42)
ss = df.loc[df.REGIAO.isin(["Sul", "Sudeste"]), VAR].sample(25, random_state=42)

q3a = teste_z(ne, mu, sigma, 0.06, "esq")
q3b = teste_z(ss, mu, sigma, 0.09, "dir")
res["q3a"], res["q3b"] = q3a, q3b
res["q3_nota"] = ("Hipóteses (a): H0: mu = mu0 vs H1: mu < mu0; (b): H0: mu = mu0 vs H1: mu > mu0. "
                  "mu0 = média dos 270 registros; sigma = desvio padrão populacional dos dados; teste Z.")

fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
z = np.linspace(-4, 4, 500)
for a, r, cauda, titulo in [(ax[0], q3a, "esq", "(a) H1: μ < μ0, α = 6%, n = 20"),
                            (ax[1], q3b, "dir", "(b) H1: μ > μ0, α = 9%, n = 25")]:
    a.plot(z, stats.norm.pdf(z), color="#1f3b73")
    m = z < r["z_critico"] if cauda == "esq" else z > r["z_critico"]
    a.fill_between(z[m], stats.norm.pdf(z)[m], color="#c0392b", alpha=0.5, label="Região crítica")
    a.axvline(r["z_calc"], color="black", ls="--", label=f"Z calc = {r['z_calc']:.2f}")
    a.set_title(titulo); a.set_xlabel("Z"); a.legend()
ax[0].set_ylabel("Densidade")
fig.suptitle("Teste Z para a média de ANOSEST")
fig.tight_layout(); fig.savefig("figuras/q3_teste_z.png", dpi=150); plt.close(fig)

def conv(o):
    if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
with open("resultados/q2_q3.json", "w", encoding="utf-8") as f:
    json.dump(conv(res), f, indent=2, ensure_ascii=False)

print(f"Variável {VAR}: N={len(x)}  média={mu:.4f}  mediana={mediana:.4f}  DP pop.={sigma:.4f}")
print(f"Shapiro-Wilk: W={sw.statistic:.4f}  p={sw.pvalue:.4f}")
print(f"\nQ2a) P(X < média)   = {p_a:.4f} -> {classifica(p_a)}")
print(f"Q2b) P(X > mediana) = {p_b:.4f} -> {classifica(p_b)}")
for nome, r in [("Q3a", q3a), ("Q3b", q3b)]:
    print(f"\n{nome}) n={r['n']} x̄={r['media_amostral']:.4f} α={r['alpha']:.2f} "
          f"Zc={r['z_calc']:.4f} Zcrit={r['z_critico']:.4f} p={r['p_valor']:.4f} "
          f"-> {'Rejeita' if r['rejeita_H0'] else 'Não rejeita'} H0")
