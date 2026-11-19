"""Registro de um serviço ou orientação ao cidadão."""
from datetime import date, datetime

CAMPOS = (
    "id", "titulo", "categoria", "descricao", "publico_alvo", "canal_local",
    "referencia", "ultima_verificacao", "aviso", "abrangencia",
)
ABRANGENCIAS = ("urbano", "rural", "ambos")
DIAS_PARA_DESATUALIZAR = 180


class Servico:
    """Dados de um serviço. Os seis primeiros campos são o mínimo exigido
    pela atividade; os demais são extras ligados ao tema (referência,
    aviso de limitação, verificação e abrangência urbano/rural)."""

    def __init__(self, id, titulo, categoria, descricao, publico_alvo,
                 canal_local, referencia="", ultima_verificacao="",
                 aviso="", abrangencia="ambos"):
        self.id = id
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.publico_alvo = publico_alvo
        self.canal_local = canal_local
        self.referencia = referencia
        self.ultima_verificacao = ultima_verificacao  # AAAA-MM-DD
        self.aviso = aviso
        self.abrangencia = abrangencia

    def para_dict(self):
        return {campo: getattr(self, campo) for campo in CAMPOS}

    def dias_desde_verificacao(self, hoje=None):
        """Dias desde a última verificação, ou None se não houver data."""
        if not self.ultima_verificacao:
            return None
        hoje = hoje or date.today()
        data = datetime.strptime(self.ultima_verificacao, "%Y-%m-%d").date()
        return (hoje - data).days

    def status_verificacao(self, hoje=None):
        """'ok', 'desatualizado' ou 'sem_data'."""
        dias = self.dias_desde_verificacao(hoje)
        if dias is None:
            return "sem_data"
        return "desatualizado" if dias > DIAS_PARA_DESATUALIZAR else "ok"
