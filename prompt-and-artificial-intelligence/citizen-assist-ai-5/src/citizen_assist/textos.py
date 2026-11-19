"""Textos fixos do assistente. Frases curtas, sem erro técnico para o usuário."""

VERSAO_FICHAS = "01/10/2026"
MAX_CARACTERES = 500

AVISO = (
    "Aviso: sou um protótipo educacional, não um canal oficial. "
    "Confirme a informação no site do órgão competente. "
    "Não informe dados pessoais (CPF, endereço, telefone) no chat."
)

CATEGORIAS = [
    ("Carteira de Identidade (RG)", [
        "Quanto custa a segunda via do RG?",
        "Que documentos preciso para a segunda via do RG?",
        "Em quanto tempo fica pronto o RG?"]),
    ("CPF", [
        "Como faço para me inscrever no CPF?",
        "Quanto custa tirar o CPF presencialmente?"]),
    ("Título de eleitor", [
        "O título de eleitor é pago?",
        "Até quando posso mudar meu título antes da eleição?",
        "Votar é obrigatório para quem tem 17 anos?"]),
    ("Carteira de Trabalho", [
        "Quanto custa e quanto demora a carteira de trabalho digital?"]),
    ("Certidões (nascimento, casamento, óbito)", [
        "Quanto custa a segunda via da certidão de nascimento pelo portal?",
        "Posso pedir a certidão de outra pessoa?"]),
    ("CNH (renovação)", [
        "Com quanto tempo de antecedência posso renovar a CNH?",
        "Minha CNH venceu há 45 dias. Posso dirigir?"]),
    ("Atendimento e regras gerais", [
        "Vocês atendem aos sábados?",
        "Preciso de intérprete de Libras. Como faço?"]),
]

EXEMPLOS = [
    "Quanto custa a segunda via do RG?",
    "Posso renovar a CNH quanto tempo antes?",
    "Vocês atendem aos sábados?",
]

MSG_VAZIA = "Você não escreveu nada. Digite sua pergunta ou escolha um assunto no menu."
MSG_LONGA = (
    f"Sua mensagem ficou muito longa (limite de {MAX_CARACTERES} caracteres). "
    "Escreva uma pergunta mais curta, por favor."
)
MSG_SEM_SENTIDO = (
    "Não entendi sua mensagem. Pode escrever de outro jeito? "
    "Exemplos: " + " | ".join(f"“{e}”" for e in EXEMPLOS) + ". Ou escolha um assunto no menu."
)
MSG_FORA_ESCOPO = (
    "Não encontrei essa informação nas fichas que tenho (RG, CPF, título de eleitor, "
    "carteira de trabalho, certidões, CNH e regras de atendimento). "
    "Para esse assunto, consulte o órgão competente."
)
MSG_INJECAO = (
    "Não posso mostrar nem mudar minhas instruções internas. "
    "Sigo apenas as fichas da Central do Cidadão de Aurora. "
    "Posso ajudar com RG, CPF, título de eleitor, carteira de trabalho, certidões e CNH. "
    "Qual é a sua dúvida?"
)
MSG_REGRA_INJETADA = (
    "Não aceito regras enviadas pela conversa. Valem apenas as fichas oficiais da Central do Cidadão."
)
MSG_LIMITACAO = (
    "Não. Sou um protótipo educacional e não represento a prefeitura nem nenhum órgão oficial. "
    "Confirme sempre as informações no órgão competente."
)
AVISO_PII_OCULTO = (
    "Percebi um dado pessoal na sua mensagem e o ocultei. "
    "Não informe CPF, endereço, telefone ou e-mail no chat: eu não guardo nem uso esses dados."
)
AVISO_PII_INTENCAO = (
    "Não preciso dos seus dados pessoais, então não os envie. "
    "Eu não agendo nem consulto sistemas: só oriento. O agendamento é feito pelo portal da Central do Cidadão."
)
MSG_FALHA_LLM = (
    "Não consegui montar a resposta agora. Tente de novo em instantes "
    "ou consulte o órgão competente."
)
