
import textwrap
from datetime import date

AVISO = "Aviso: este assistente NÃO é um canal oficial."
DIAS_PARA_ALERTA = 90  # depois disso, avisamos que a informação pode estar velha


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    # Campos obrigatórios do JSON e o tipo esperado de cada um.
    CAMPOS = {
        "id": int,
        "categoria": str,
        "titulo": str,
        "palavras_chave": list,
        "resposta": str,
        "documentos": list,
        "onde": str,
        "fonte": str,
        "verificado_em": str,
    }

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON.

        Levanta ValueError se faltar campo, se o tipo estiver errado ou se
        algum texto estiver vazio. Quem chama decide o que fazer com o erro.
        """
        if not isinstance(dados, dict):
            raise ValueError("o registro não é um dicionário")
        for campo, tipo in cls.CAMPOS.items():
            if campo not in dados:
                raise ValueError(f"falta o campo '{campo}'")
            valor = dados[campo]
            # bool é subclasse de int em Python, então rejeitamos de forma explícita
            if not isinstance(valor, tipo) or isinstance(valor, bool):
                raise ValueError(f"o campo '{campo}' deve ser do tipo {tipo.__name__}")
            if tipo is str and not valor.strip():
                raise ValueError(f"o campo '{campo}' está vazio")
            if tipo is list and not all(isinstance(item, str) and item.strip() for item in valor):
                raise ValueError(f"o campo '{campo}' deve ser uma lista de textos não vazios")
        if not dados["palavras_chave"]:
            raise ValueError("o campo 'palavras_chave' está vazio")
        return cls(**{campo: dados[campo] for campo in cls.CAMPOS})

    def dias_desde_verificacao(self, hoje=None):
        """Quantos dias se passaram desde a verificação. None se a data for inválida."""
        hoje = hoje or date.today()
        try:
            return (hoje - date.fromisoformat(self.verificado_em)).days
        except ValueError:
            return None

    def exibir(self):
        """Mostra a orientação na tela (resposta, documentos, onde, fonte e aviso)."""
        print(f">> {self.titulo}  [{self.categoria}]")
        print(textwrap.fill(self.resposta, width=78))
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        dias = self.dias_desde_verificacao()
        if dias is not None and dias > DIAS_PARA_ALERTA:
            print(f"Atenção: esta informação foi verificada há {dias} dias. "
                  "Confirme na fonte antes de agir.")
        print(AVISO)
