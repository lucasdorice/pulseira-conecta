"""Classe BaseConhecimento: o conjunto de todas as orientações.

Responsabilidades: ler o JSON, listar categorias, pontuar e buscar.
Também contém a função normalizar(), usada em toda comparação de texto.
"""

import difflib
import json
from datetime import date

from orientacao import Orientacao

# ---------------------------------------------------------------------------
# Regras de pontuação (ajustáveis; explicadas no README)
# ---------------------------------------------------------------------------
PONTOS_PALAVRA_CHAVE = 3   # palavra-chave da orientação que aparece na pergunta
PONTOS_TITULO = 1          # palavra da pergunta (4+ letras) que aparece no título
MIN_LETRAS_TITULO = 4
LIMITE_ALTA = 6            # 6 pontos ou mais -> confiança ALTA
LIMITE_MEDIA = 3           # de 3 a 5 pontos  -> confiança MÉDIA

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}
SINAIS = "?!.,;:()-/\"'"


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação.

    O resultado vem com um espaço no começo e outro no fim. Assim, procurar
    " sus " dentro do texto só encontra a palavra inteira "sus" (e não "sustento").
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Lê o JSON e responde: quais são as categorias? qual é a melhor orientação?"""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []      # lista de objetos Orientacao
        self.erro = ""             # mensagem se o arquivo não pôde ser lido
        self.ignoradas = []        # registros inválidos que foram pulados
        self.vocabulario = []      # palavras conhecidas (usado no "você quis dizer?")

    # ------------------------------------------------------------------ leitura
    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Devolve True se houver dados.

        Arquivo ausente ou corrompido NÃO levanta exceção: guarda a mensagem em
        self.erro e devolve False, para o programa continuar funcionando.
        """
        self.orientacoes = []
        self.ignoradas = []
        self.erro = ""
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"Arquivo não encontrado: {self.caminho}"
            return False
        except json.JSONDecodeError as problema:
            self.erro = (f"Arquivo corrompido ({problema.msg}, linha {problema.lineno}): "
                         f"{self.caminho}")
            return False
        except (OSError, UnicodeDecodeError) as problema:
            self.erro = f"Não consegui ler {self.caminho}: {problema}"
            return False

        if not isinstance(dados, list):
            self.erro = "O JSON deve ser uma lista de orientações."
            return False

        ids_vistos = set()
        for posicao, registro in enumerate(dados, start=1):
            try:
                orientacao = Orientacao.de_dicionario(registro)
            except ValueError as problema:
                self.ignoradas.append(f"registro {posicao}: {problema}")
                continue
            if orientacao.id in ids_vistos:
                self.ignoradas.append(f"registro {posicao}: id {orientacao.id} repetido")
                continue
            ids_vistos.add(orientacao.id)
            self.orientacoes.append(orientacao)

        self._montar_vocabulario()
        if not self.orientacoes:
            self.erro = "Nenhuma orientação válida foi encontrada no arquivo."
        return bool(self.orientacoes)

    def _montar_vocabulario(self):
        palavras = set()
        for orientacao in self.orientacoes:
            textos = orientacao.palavras_chave + [orientacao.titulo]
            for texto in textos:
                for palavra in normalizar(texto).split():
                    if len(palavra) >= MIN_LETRAS_TITULO:
                        palavras.add(palavra)
        self.vocabulario = sorted(palavras)

    def verificar_requisitos(self):
        """Confere os requisitos da atividade. Devolve a lista de problemas."""
        problemas = []
        if len(self.orientacoes) < 10:
            problemas.append(f"Há {len(self.orientacoes)} orientações (mínimo: 10).")
        if len(self.categorias()) < 3:
            problemas.append(f"Há {len(self.categorias())} categorias (mínimo: 3).")
        for o in self.orientacoes:
            if len(o.palavras_chave) < 3:
                problemas.append(f"Orientação {o.id}: menos de 3 palavras-chave.")
            if not o.fonte.startswith("http"):
                problemas.append(f"Orientação {o.id}: fonte sem endereço (http).")
            try:
                date.fromisoformat(o.verificado_em)
            except ValueError:
                problemas.append(f"Orientação {o.id}: data inválida ({o.verificado_em}).")
        problemas.extend(f"Ignorado: {item}" for item in self.ignoradas)
        return problemas

    # ---------------------------------------------------------------- categorias
    def categorias(self):
        """Categorias sem repetição, na ordem em que aparecem no JSON."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def exemplos_de_palavras(self, quantidade=6):
        """Algumas palavras-chave para sugerir quando a busca não acha nada."""
        exemplos = []
        for orientacao in self.orientacoes:
            for palavra in orientacao.palavras_chave:
                if len(palavra) >= MIN_LETRAS_TITULO and palavra.isalpha():
                    exemplos.append(palavra)
                    break
            if len(exemplos) == quantidade:
                break
        return exemplos

    # ------------------------------------------------------------------- busca
    def acertos(self, pergunta, orientacao):
        """Quais palavras-chave e quais palavras do título casaram com a pergunta.

        Devolve (palavras_chave_encontradas, palavras_do_titulo_encontradas).
        """
        texto = normalizar(pergunta)

        chaves = []
        chaves_normalizadas = []
        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            if chave_norm.strip() and chave_norm in texto and chave_norm not in chaves_normalizadas:
                chaves.append(chave)
                chaves_normalizadas.append(chave_norm)

        titulo = normalizar(orientacao.titulo)
        no_titulo = []
        for palavra in texto.split():
            if (len(palavra) >= MIN_LETRAS_TITULO and f" {palavra} " in titulo
                    and palavra not in no_titulo):
                no_titulo.append(palavra)
        return chaves, no_titulo

    def pontuar(self, pergunta, orientacao):
        """Pontos de UMA orientação para a pergunta: +3 por palavra-chave, +1 por palavra do título."""
        chaves, no_titulo = self.acertos(pergunta, orientacao)
        return len(chaves) * PONTOS_PALAVRA_CHAVE + len(no_titulo) * PONTOS_TITULO

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor pontuação.

        Só entram orientações com pelo menos 1 ponto. Em caso de empate, vence o menor id.
        """
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda par: (-par[0], par[1].id))
        return resultados

    @staticmethod
    def classificar(pontos):
        """Traduz pontos em nível de confiança."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return "NENHUMA"

    # ------------------------------------------------------ "você quis dizer?"
    def corrigir(self, pergunta):
        """Tenta consertar erros de digitação usando as palavras da própria base.

        Devolve (texto_corrigido, trocas), onde trocas é uma lista de
        (palavra_digitada, palavra_sugerida). Usa difflib, da biblioteca padrão.
        """
        novas = []
        trocas = []
        for palavra in normalizar(pergunta).split():
            if len(palavra) >= 5 and palavra not in self.vocabulario and not palavra.isdigit():
                parecidas = difflib.get_close_matches(palavra, self.vocabulario, n=1, cutoff=0.8)
                if parecidas:
                    trocas.append((palavra, parecidas[0]))
                    novas.append(parecidas[0])
                    continue
            novas.append(palavra)
        return " ".join(novas), trocas
