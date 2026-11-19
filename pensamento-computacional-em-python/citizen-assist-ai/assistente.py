"""Classe Assistente: quem conversa com o cidadão.

Responsabilidades: atender (perguntar e navegar), bloquear dados pessoais,
guardar o histórico, calcular indicadores e exportar o CSV.
"""

import csv
import json
import os
import time
from collections import Counter
from datetime import datetime
from urllib.parse import urlsplit

from base_conhecimento import (BaseConhecimento, LIMITE_MEDIA, MIN_LETRAS_TITULO,
                               PONTOS_PALAVRA_CHAVE, PONTOS_TITULO, normalizar)

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou", "confianca",
              "ajudou", "tentativas", "tempo_segundos", "sessao", "nota_facilidade"]

# Frases que indicam perigo imediato. Se aparecerem, os telefones vêm primeiro.
FRASES_EMERGENCIA = ["socorro", "afogando", "afogado", "desabando", "desabou", "soterrado",
                     "soterrada", "ilhado", "ilhada", "urgente", "emergencia",
                     "agua entrando", "casa caindo", "agua subindo rapido"]

ENCURTADORES = ("bit.ly", "tinyurl.com", "t.co", "cutt.ly", "is.gd", "goo.gl", "rb.gy",
                "shorturl.at", "ow.ly", "encurtador.com.br")


class EncerrarPrograma(Exception):
    """Levantada quando a entrada acaba (Ctrl+D) ou o usuário aperta Ctrl+C."""


def contem_dado_pessoal(texto):
    """Regra do enunciado: 8 ou mais dígitos (CPF, telefone, CEP...) ou um '@' (e-mail)."""
    digitos = sum(1 for letra in texto if letra.isdigit())
    return digitos >= 8 or "@" in texto


def analisar_link(texto):
    """Analisa um endereço de site. Devolve (nivel, motivos).

    nivel: "PARECE OFICIAL", "NÃO OFICIAL" ou "SUSPEITO".
    Atenção: terminar em .gov.br NÃO garante que o link é seguro.
    """
    bruto = texto.strip()
    try:
        partes = urlsplit(bruto if "://" in bruto else "//" + bruto)
        host = (partes.hostname or "").lower().rstrip(".")
        usuario = partes.username
        esquema = partes.scheme.lower()
    except ValueError:
        return "SUSPEITO", ["O endereço está em um formato inválido."]
    if not host:
        return "SUSPEITO", ["Não consegui identificar o endereço do site."]

    alertas = []
    if usuario is not None:
        alertas.append(f"Tem '@' no endereço: o site de verdade é '{host}', "
                       "e não o nome que aparece antes do '@'.")
    if host in ENCURTADORES:
        alertas.append("É um link encurtado: ele esconde para onde você vai.")
    if host.startswith("xn--") or ".xn--" in host:
        alertas.append("O endereço usa caracteres disfarçados (punycode), truque comum em golpes.")
    if esquema == "http":
        alertas.append("O endereço usa http e não https (sem conexão segura).")

    oficial = host == "gov.br" or host.endswith(".gov.br")
    imita_governo = (not oficial
                     and any(trecho in host for trecho in ("gov.br", "govbr", "gov-br", "governo")))
    if imita_governo:
        alertas.append("O endereço tenta parecer do governo, mas o site NÃO termina em .gov.br.")

    if oficial and not alertas:
        return "PARECE OFICIAL", [f"O endereço '{host}' termina em .gov.br."]
    if alertas:
        return "SUSPEITO", alertas
    return "NÃO OFICIAL", [f"O endereço '{host}' não termina em .gov.br."]


class Assistente:
    """Atende o cidadão usando a BaseConhecimento (composição)."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base                      # objeto BaseConhecimento
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.historico = []                   # lista de dicionários (um por atendimento)
        self.aviso_historico = ""
        self._carregar_historico()

    # ============================================================ entrada segura
    def _entrada(self, texto):
        try:
            return input(texto).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise EncerrarPrograma()

    def ler_numero(self, texto, minimo, maximo):
        """Pede um número entre minimo e maximo. Entrada inválida nunca encerra o programa."""
        while True:
            resposta = self._entrada(texto)
            if not resposta:
                print("Você não digitou nada. Digite um número.")
            elif not resposta.isdecimal():
                print("Digite apenas números.")
            elif not minimo <= int(resposta) <= maximo:
                print(f"Opção fora da lista. Digite um número de {minimo} a {maximo}.")
            else:
                return int(resposta)

    def ler_sn(self, texto):
        """Pede s ou n. Devolve True para sim e False para não."""
        while True:
            resposta = normalizar(self._entrada(texto)).strip()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao"):
                return False
            print("Responda apenas com s (sim) ou n (não).")

    # ======================================================== histórico em arquivo
    def _carregar_historico(self):
        """Lê historico.json. Se não existir ou estiver corrompido, começa vazio."""
        self.historico = []
        if not os.path.exists(self.caminho_historico):
            return
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list):
                raise ValueError("o histórico deve ser uma lista")
            self.historico = [item for item in dados if isinstance(item, dict)]
        except (json.JSONDecodeError, ValueError, OSError, UnicodeDecodeError):
            copia = self.caminho_historico + ".bak"
            try:
                os.replace(self.caminho_historico, copia)
                self.aviso_historico = (f"O histórico estava corrompido. Guardei uma cópia em "
                                        f"{copia} e comecei um histórico novo.")
            except OSError:
                self.aviso_historico = "O histórico estava ilegível. Comecei um histórico novo."

    def _salvar_historico(self):
        """Grava historico.json. Escreve em arquivo temporário para não perder dados."""
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            temporario = self.caminho_historico + ".tmp"
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho_historico)
            return True
        except OSError as problema:
            print(f"Aviso: não consegui salvar o histórico ({problema}).")
            return False

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo_segundos, confianca):
        """Guarda um atendimento no histórico. Pergunta com dado pessoal NUNCA é registrada."""
        if contem_dado_pessoal(pergunta):
            return None
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,                     # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "confianca": confianca,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo_segundos,
            "sessao": self.sessao,
            "nota_facilidade": None,              # preenchida ao sair
        }
        self.historico.append(atendimento)
        self._salvar_historico()
        return atendimento

    def atendimentos_da_sessao(self):
        return [a for a in self.historico if a.get("sessao") == self.sessao]

    # ============================================================== atendimento
    def boas_vindas(self):
        print("=" * 60)
        print(f" {self.nome}")
        print(" Orientação para moradores de áreas de risco")
        print("=" * 60)
        print("Respondo só com informações verificadas, sempre com a fonte.")
        print("Não peço nem guardo dados pessoais: nunca digite nome, CPF,")
        print("telefone ou e-mail.")
        print("EM PERIGO AGORA? Ligue 193 (Bombeiros), 192 (SAMU) ou 199 (Defesa Civil).")
        print("Aviso: este assistente NÃO é um canal oficial.")
        if self.aviso_historico:
            print(f"\n{self.aviso_historico}")

    def _avisar_emergencia(self, texto):
        pergunta = normalizar(texto)
        if any(f" {frase} " in pergunta or frase in pergunta for frase in FRASES_EMERGENCIA):
            print("\n!!! SE VOCÊ ESTÁ EM PERIGO AGORA, LIGUE: 193 (Bombeiros), 192 (SAMU)")
            print("!!! ou 199 (Defesa Civil, quando existir na sua cidade).")
            print("!!! Depois, veja a orientação abaixo.")

    def _buscar_com_sugestao(self, texto):
        """Busca; se nada for encontrado, tenta o 'você quis dizer?'."""
        resultados = self.base.buscar(texto)
        if resultados and resultados[0][0] >= LIMITE_MEDIA:
            return resultados
        corrigido, trocas = self.base.corrigir(texto)
        if trocas:
            if self.ler_sn(f"Você quis dizer: \"{corrigido.strip()}\"? (s/n): "):
                novos = self.base.buscar(corrigido)
                if novos and novos[0][0] >= LIMITE_MEDIA:
                    return novos
        return resultados

    def _mostrar_nao_encontrado(self):
        print("\nNão encontrei uma orientação para essa dúvida na base.")
        exemplos = ", ".join(self.base.exemplos_de_palavras())
        print(f"Tente outras palavras (exemplos: {exemplos}).")
        print("Ou use a opção 2 do menu para navegar pelas categorias:")
        print("  " + " | ".join(self.base.categorias()))

    def perguntar(self):
        """Atendimento por texto livre: busca, mostra a melhor orientação e até 2 alternativas."""
        if not self.base.orientacoes:
            print("A base de conhecimento não foi carregada. Não consigo responder dúvidas.")
            if self.base.erro:
                print(f"Motivo: {self.base.erro}")
            return

        inicio = time.time()
        tentativas = 0
        pergunta_final = ""
        id_final = None
        encontrou = False
        confianca = "NENHUMA"
        ajudou = False

        while True:
            texto = self._entrada("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                break
            if not texto:
                print("Você não digitou nada. Escreva sua dúvida com poucas palavras "
                      "(ex.: enchente, alerta, documentos).")
                continue
            if contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            pergunta_final = texto
            self._avisar_emergencia(texto)
            resultados = self._buscar_com_sugestao(texto)
            melhor_pontos = resultados[0][0] if resultados else 0

            if melhor_pontos < LIMITE_MEDIA:
                encontrou, id_final, confianca, ajudou = False, None, "NENHUMA", False
                self._mostrar_nao_encontrado()
                continue

            melhor = resultados[0][1]
            alternativas = [par for par in resultados[1:3] if par[0] >= LIMITE_MEDIA]
            encontrou, id_final = True, melhor.id
            confianca = self.base.classificar(melhor_pontos)

            print(f"\nConfiança da resposta: {confianca} ({melhor_pontos} pontos)\n")
            melhor.exibir()
            if alternativas:
                print("\nVeja também:")
                for numero, (pontos, outra) in enumerate(alternativas, start=1):
                    print(f"  {numero}) {outra.titulo} ({pontos} pontos)")

            ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if ajudou:
                break

            if alternativas:
                escolha = self.ler_numero(
                    "Digite o número de uma alternativa para ver, "
                    "ou 0 para reescrever a dúvida: ", 0, len(alternativas))
                if escolha > 0:
                    tentativas += 1
                    pontos_alt, alternativa = alternativas[escolha - 1]
                    id_final = alternativa.id
                    confianca = self.base.classificar(pontos_alt)
                    print()
                    alternativa.exibir()
                    ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
                    if ajudou:
                        break
            else:
                print("Tente escrever com outras palavras ou use a opção 2 (categorias).")

        if tentativas > 0:
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", pergunta_final, id_final, encontrou, ajudou,
                           tentativas, tempo, confianca)

    def navegar(self):
        """Navegação por categorias, com '0 para voltar' em todas as telas."""
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento não foi carregada. Não há categorias para mostrar.")
            return
        while True:
            print("\n--- Categorias ---")
            for numero, categoria in enumerate(categorias, start=1):
                quantidade = len(self.base.por_categoria(categoria))
                print(f"  {numero}) {categoria} ({quantidade})")
            print("  0) Voltar")
            escolha = self.ler_numero("Escolha a categoria: ", 0, len(categorias))
            if escolha == 0:
                return
            self._navegar_categoria(categorias[escolha - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n--- {categoria} ---")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero}) {orientacao.titulo}")
            print("  0) Voltar")
            escolha = self.ler_numero("Escolha a orientação: ", 0, len(orientacoes))
            if escolha == 0:
                return
            inicio = time.time()
            orientacao = orientacoes[escolha - 1]
            print()
            orientacao.exibir()
            ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", f"[{categoria}] {orientacao.titulo}", orientacao.id,
                           True, ajudou, 1, tempo, "NAVEGAÇÃO")

    # ============================================================ modo didático
    def modo_didatico(self):
        """Mostra, passo a passo, como a pontuação de uma pergunta é calculada."""
        if not self.base.orientacoes:
            print("A base de conhecimento não foi carregada.")
            return
        while True:
            texto = self._entrada("\nDigite uma pergunta para ver o cálculo (0 para voltar): ")
            if texto == "0":
                return
            if not texto:
                print("Você não digitou nada.")
                continue
            if contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue
            print(f"\n1) Normalização: \"{normalizar(texto).strip()}\"")
            resultados = self.base.buscar(texto)
            if not resultados:
                print("2) Nenhuma orientação recebeu pontos.")
                continue
            print("2) Pontuação das orientações (as 3 melhores):")
            for pontos, orientacao in resultados[:3]:
                chaves, no_titulo = self.base.acertos(texto, orientacao)
                print(f"\n   Orientação {orientacao.id}: {orientacao.titulo}")
                for chave in chaves:
                    print(f"     +{PONTOS_PALAVRA_CHAVE}  palavra-chave \"{chave}\" está na pergunta")
                for palavra in no_titulo:
                    print(f"     +{PONTOS_TITULO}  \"{palavra}\" (de {MIN_LETRAS_TITULO}+ letras) "
                          "está no título")
                rotulo = "ponto" if pontos == 1 else "pontos"
                print(f"     = {pontos} {rotulo} -> confiança {self.base.classificar(pontos)}")
            melhor = resultados[0][0]
            print(f"\n3) Resultado: melhor orientação com {melhor} pontos "
                  f"-> {self.base.classificar(melhor)}.")

    # ========================================================= verificador de link
    def verificar_link(self):
        """Avisa se um endereço parece oficial. O link NÃO é registrado."""
        print("\nCole o endereço de um site para eu avaliar. O link não é guardado.")
        while True:
            texto = self._entrada("Endereço (0 para voltar): ")
            if texto == "0":
                return
            if not texto:
                print("Você não digitou nada.")
                continue
            nivel, motivos = analisar_link(texto)
            print(f"\nResultado: {nivel}")
            for motivo in motivos:
                print(f"  - {motivo}")
            print("Lembrete: terminar em .gov.br indica site de governo, mas não garante "
                  "segurança.")
            print("Prefira digitar o endereço você mesmo ou usar o aplicativo gov.br.")
            print("Aviso: este assistente NÃO é um canal oficial.")

    # ============================================================== indicadores
    def indicadores(self):
        """Calcula os indicadores a partir de TODO o histórico salvo."""
        total = len(self.historico)
        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]

        tempos = [a.get("tempo_segundos", 0) for a in encontrados]
        tentativas = [a.get("tentativas", 1) for a in self.historico]

        notas_por_sessao = {}
        for atendimento in self.historico:
            nota = atendimento.get("nota_facilidade")
            if isinstance(nota, int) and 1 <= nota <= 5:
                notas_por_sessao[atendimento.get("sessao")] = nota
        notas = list(notas_por_sessao.values())

        sem_solucao = Counter()
        for atendimento in self.historico:
            if not atendimento.get("ajudou"):
                pergunta = str(atendimento.get("pergunta", "")).strip()
                if pergunta:
                    sem_solucao[normalizar(pergunta).strip()] += 1

        def media(valores):
            return round(sum(valores) / len(valores), 1) if valores else 0.0

        return {
            "total": total,
            "resposta_encontrada_pct": round(100 * len(encontrados) / total, 1) if total else 0.0,
            "taxa_acerto_pct": round(100 * len(ajudaram) / total, 1) if total else 0.0,
            "tempo_medio_segundos": media(tempos),
            "tentativas_por_atendimento": media(tentativas),
            "facilidade_media": media(notas),
            "sessoes_avaliadas": len(notas),
            "duvidas_sem_solucao": sem_solucao.most_common(),
        }

    def mostrar_indicadores(self):
        dados = self.indicadores()
        print("\n=== Indicadores ===")
        if dados["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos registrados:    {dados['total']}")
        print(f"Resposta encontrada (%):     {dados['resposta_encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%):  {dados['taxa_acerto_pct']}")
        print(f"Tempo médio para encontrar:  {dados['tempo_medio_segundos']} s")
        print(f"Tentativas por atendimento:  {dados['tentativas_por_atendimento']}")
        if dados["sessoes_avaliadas"]:
            print(f"Facilidade de uso (1 a 5):   {dados['facilidade_media']} "
                  f"({dados['sessoes_avaliadas']} avaliações)")
        else:
            print("Facilidade de uso (1 a 5):   sem avaliações ainda")
        print("Dúvidas sem solução:")
        if dados["duvidas_sem_solucao"]:
            for pergunta, vezes in dados["duvidas_sem_solucao"]:
                print(f"  - {pergunta} ({vezes}x)")
        else:
            print("  (nenhuma)")

    # ================================================================== CSV
    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv com csv.DictWriter."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            # utf-8-sig: o Excel abre os acentos corretamente
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    linha = dict(atendimento)
                    for campo in ("encontrou", "ajudou"):
                        linha[campo] = "sim" if atendimento.get(campo) else "nao"
                    escritor.writerow(linha)
        except OSError as problema:
            print(f"Não consegui salvar o CSV ({problema}). "
                  "Se o arquivo estiver aberto em outro programa, feche-o e tente de novo.")
            return False
        print(f"CSV exportado: {self.caminho_csv} ({len(self.historico)} atendimentos)")
        return True

    # ============================================================== encerramento
    def encerrar(self, pedir_nota=True):
        """Pede a nota de facilidade (1 a 5), salva o histórico e exporta o CSV."""
        if pedir_nota and self.atendimentos_da_sessao():
            print("\nAntes de sair: de 1 (muito difícil) a 5 (muito fácil), "
                  "quão fácil foi usar o assistente?")
            try:
                nota = self.ler_numero("Sua nota (0 para pular): ", 0, 5)
            except EncerrarPrograma:
                nota = 0
            if nota > 0:
                for atendimento in self.atendimentos_da_sessao():
                    atendimento["nota_facilidade"] = nota
        self._salvar_historico()
        self.exportar_csv()
