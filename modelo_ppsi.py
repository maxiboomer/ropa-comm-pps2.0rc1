#!/usr/bin/env python3
"""
modelo_ppsi.py — Campos e taxonomia do RoPA alinhados ao
Guia para Elaboração do Registro das Operações de Tratamento (PPSI 2.0, v1.0)
e ao controle 19 do framework do PPSI 2.0 (Portaria SGD/MGI nº 9.511/2025).

Compartilhado por app.py (web) e ropa.py (CLI) para evitar divergência.
Conteúdo mínimo (blocos 4.1–4.6 da Tabela 1 do Guia).
"""
import json
import os

# ── Situações do registro (Guia 4.1.5) ───────────────────────────────────────
SITUACOES = [
    ("em_andamento", "Em andamento"),
    ("em_revisao",   "Em revisão"),
    ("concluido",    "Concluído"),
    ("descontinuado","Descontinuado"),
    ("cancelado",    "Cancelado"),
]

# ── Taxonomia de categorias de dados compatível com o FCI da ANPD (Guia 4.2.3)
CATEGORIAS_DADOS_FCI = {
    "dados_basicos_identificacao":   "Dados básicos de identificação",
    "documentos_identificacao":      "Documentos de identificação oficial",
    "dados_contato":                 "Dados de contato",
    "dados_financeiros":             "Dados financeiros e meios de pagamento",
    "sigilo_legal_profissional":     "Dados protegidos por sigilo legal ou profissional",
    "dados_autenticacao":            "Dados de autenticação",
    "imagem_voz_localizacao":        "Imagem, voz e localização geográfica",
    "dados_biometricos":             "Dados biométricos",
    "dados_saude":                   "Dados de saúde",
    "outros":                        "Outros",
}

# ── Titulares que demandam proteção reforçada (Guia 4.2.2) ───────────────────
CATEGORIAS_PROTECAO_REFORCADA = [
    "criancas",
    "adolescentes",
    "idosos",
    "outros vulneráveis",
]

# ── Categorias de titulares sugeridas (Guia 4.2.2) — sugestão via datalist ──
CATEGORIAS_TITULARES_SUGERIDAS = [
    "Servidores públicos",
    "Empregados públicos / celetistas",
    "Estagiários e aprendizes",
    "Cidadãos / cidadãs em geral",
    "Usuários de serviços públicos",
    "Fornecedores e prestadores de serviço",
    "Candidatos a cargos públicos",
    "Pensionistas e aposentados",
    "Menores de idade",
    "Idosos",
    "Pessoas com deficiência",
    "Visitantes",
    "Terceirizados",
]


# ── Campos cujo valor é armazenado como JSON (multivalorado) ─────────────────
JSON_FIELDS = {
    "titulares_estimativa",            # {categoria: quantidade}
    "titulares_protecao_reforcada",    # [categoria, ...]
    "tipos_dados",                     # {categoria_FCI: [tipos, ...]}
    "tipos_dados_sensiveis",           # [tipo, ...]
    "origem_dados",                    # [fonte, ...]
    "controladores",                   # [linha, ...]
    "operadores",                      # [linha, ...]
    "compartilhamentos",               # [linha, ...]
    "transferencia_internacional",     # [linha, ...]
}

# ── Completude (soma = 100) alinhada ao conteúdo mínimo do Guia ──────────────
CAMPOS_VALIDACAO = {
    "nome_atividade":            ("Nome da atividade de tratamento", 8),
    "unidade_controladora":      ("Unidade administrativa responsável", 5),
    "responsavel_preenchimento": ("Responsável pelo preenchimento", 3),
    "situacao":                  ("Situação do registro", 3),
    "finalidade":                ("Finalidade do tratamento", 7),
    "base_legal":                ("Base legal", 8),
    "previsao_normativa":        ("Previsão normativa específica", 4),
    "categorias_titulares":      ("Categorias de titulares", 5),
    "titulares_protecao_reforcada": ("Titulares com proteção reforçada", 3),
    "categorias_dados":          ("Tipos de dados pessoais", 3),
    "tipos_dados_sensiveis":     ("Tipos de dados sensíveis", 3),
    "fluxo_tratamento":          ("Fluxo de tratamento dos dados", 6),
    "origem_dados":              ("Origem dos dados pessoais", 4),
    "local_armazenamento":       ("Local e meio de armazenamento", 4),
    "prazo_retencao":            ("Período de retenção", 5),
    "eliminacao_destinacao":     ("Forma de eliminação/destinação final", 4),
    "frequencia_tratamento":     ("Frequência do tratamento", 3),
    "controladores":             ("Controladores", 4),
    "operadores":                ("Operadores", 5),
    "destinatarios":             ("Compartilhamento", 5),
    "transferencia_internacional": ("Transferência internacional", 3),
    "medidas_seguranca":         ("Medidas de segurança", 5),
}
assert sum(p for _, p in CAMPOS_VALIDACAO.values()) == 100, "CAMPOS_VALIDACAO deve somar 100"


# ── Módulo RIPD (controles 23.3, 25.8, 25.10 do PPSI 2.0) ────────────────────

SITUACOES_RIPD = [
    ("rascunho",   "Rascunho"),
    ("em_revisao", "Em revisão"),
    ("aprovado",   "Aprovado"),
    ("publicado",  "Publicado"),
    ("desatualizado", "Desatualizado (revisar)"),
]

# 10 princípios do art. 6º da LGPD
PRINCIPIOS_LGPD = [
    ("finalidade", "Finalidade (art. 6º, I)"),
    ("adequacao", "Adequação (art. 6º, II)"),
    ("necessidade", "Necessidade (art. 6º, III)"),
    ("livre_acesso", "Livre acesso (art. 6º, IV)"),
    ("qualidade_dados", "Qualidade dos dados (art. 6º, V)"),
    ("transparencia", "Transparência (art. 6º, VI)"),
    ("seguranca", "Segurança (art. 6º, VII)"),
    ("prevencao", "Prevenção (art. 6º, VIII)"),
    ("nao_discriminacao", "Não discriminação (art. 6º, IX)"),
    ("responsabilizacao", "Responsabilização e prestação de contas (art. 6º, X)"),
]

# Direitos do titular (art. 18 LGPD)
DIREITOS_TITULARES = [
    ("confirmacao", "Confirmação de tratamento (art. 18, I)"),
    ("acesso", "Acesso aos dados (art. 18, II)"),
    ("correcao", "Correção de dados (art. 18, III)"),
    ("anonimizacao", "Anonimização/eliminação (art. 18, IV)"),
    ("portabilidade", "Portabilidade (art. 18, V)"),
    ("informacao", "Informação sobre compartilhamento (art. 18, VI)"),
    ("revogacao", "Revogação de consentimento (art. 18, VIII)"),
    ("oposicao", "Oposição a tratamento (art. 18, X)"),
]

CRITERIO_GERAL_LABELS = {
    "larga_escala": "Tratamento de dados em larga escala",
    "direitos_fundamentais": "Tratamento que afeta significativamente interesses e direitos fundamentais dos titulares",
}

CRITERIO_ESPECIFICO_LABELS = {
    "tecnologias_emergentes": "Uso de tecnologias emergentes ou inovadoras",
    "vigilancia": "Vigilância ou controle de zonas acessíveis ao público",
    "decisoes_automatizadas": "Decisões unicamente baseadas em tratamento automatizado (perfilamento)",
    "dados_sensiveis_vulneraveis": "Utilização de dados sensíveis ou de crianças, adolescentes ou idosos",
}

_LARGA_ESCALA_MIN = int(os.environ.get("ROPA_RIPD_LARGA_ESCALA_MIN", "10000"))


def calcular_risco(atividade) -> dict:
    """Avalia alto risco (RIPD) conforme Res. CD/ANPD nº 2/2022, art. 4º, e a boa
    prática do Guia de RIPD do PPSI 2.0 (2+ fatores). Alimenta o gatilho controle 19 → 23.3."""
    a = dict(atividade or {})

    # ── Critérios gerais ──
    geral = []
    total = 0
    try:
        est = json.loads(a.get("titulares_estimativa") or "{}")
        if isinstance(est, dict):
            for v in est.values():
                try:
                    num = int(str(v).replace(".", "").replace(",", "").strip() or 0)
                    total += num
                except Exception:
                    pass
    except Exception:
        pass
    if total >= _LARGA_ESCALA_MIN:
        geral.append("larga_escala")

    prot = parse_json(a.get("titulares_protecao_reforcada"))
    if (a.get("dados_sensiveis") or prot or
            a.get("decisoes_automatizadas") or a.get("tecnologias_emergentes") or
            a.get("vigilancia_zonas_publicas")):
        geral.append("direitos_fundamentais")

    # ── Critérios específicos ──
    especifico = []
    if a.get("tecnologias_emergentes"):
        especifico.append("tecnologias_emergentes")
    if a.get("vigilancia_zonas_publicas"):
        especifico.append("vigilancia")
    if a.get("decisoes_automatizadas"):
        especifico.append("decisoes_automatizadas")
    if a.get("dados_sensiveis") or any(x in prot for x in ("criancas", "adolescentes", "idosos")):
        especifico.append("dados_sensiveis_vulneraveis")

    fatores = list(dict.fromkeys(geral + especifico))
    alto_risco = bool(geral) and bool(especifico)
    recomenda = alto_risco or len(fatores) >= 2  # boa prática PPSI 2.0

    return {
        "geral": geral,
        "especifico": especifico,
        "fatores": fatores,
        "larga_escala_total": total,
        "alto_risco": alto_risco,
        "recomenda": recomenda,
    }


# ── Helpers JSON ──────────────────────────────────────────────────────────────

def _vazio(val) -> bool:
    """True se o valor está vazio para fins de completude."""
    if not val:
        return True
    s = str(val).strip()
    if not s or s.upper() in ("N/A", "NENHUM", "—", "NONE", "NULL", "[]", "{}"):
        return True
    if s in JSON_FIELDS or s in ("tipos_dados", "titulares_estimativa", "compartilhamentos"):
        pass
    return False


def preenchido(campo: str, val) -> bool:
    """Campo preenchido? (JSON é considerado preenchido se a estrutura não é vazia)."""
    if not val:
        return False
    s = str(val).strip()
    if not s or s.upper() in ("N/A", "NENHUM", "—", "NONE", "NULL"):
        return False
    if campo in JSON_FIELDS:
        try:
            parsed = json.loads(s)
            if isinstance(parsed, (list, dict)):
                return bool(parsed)
        except Exception:
            pass
    return True


def json_ou_vazio(val):
    """Normaliza um valor JSON para string, '' se vazio."""
    if val is None:
        return ""
    if isinstance(val, str):
        s = val.strip()
        if s in ("", "[]", "{}", "null"):
            return ""
        return s
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False) if val else ""
    return str(val)


def parse_json(val):
    """Converte JSON armazenado (str) em list/dict para uso em templates."""
    if isinstance(val, (list, dict)):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val) if val else []
        except Exception:
            return []
    return []


def parse_lista(texto: str) -> list:
    """Cada linha não vazia vira um item da lista."""
    out = []
    for linha in (texto or "").splitlines():
        item = linha.strip().strip(";,")
        if item:
            out.append(item)
    return out


def parse_dict_tipos(texto: str) -> dict:
    """Formato 'Categoria: tipo1; tipo2; tipo3' por linha -> {categoria: [tipos]}."""
    out = {}
    for linha in (texto or "").splitlines():
        if ":" not in linha:
            continue
        chave, resto = linha.split(":", 1)
        chave = chave.strip()
        tipos = [t.strip() for t in resto.split(";") if t.strip()]
        if chave and tipos:
            out[chave] = tipos
    return out


def parse_estimativa(texto: str) -> dict:
    """Formato 'categoria: quantidade' por linha -> {categoria: quantidade}."""
    out = {}
    for linha in (texto or "").splitlines():
        if ":" not in linha:
            continue
        chave, valor = linha.split(":", 1)
        chave = chave.strip()
        valor = valor.strip()
        if chave and valor:
            out[chave] = valor
    return out


def lista_para_texto(raw) -> str:
    """JSON list -> texto (um item por linha) para preencher textarea."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw else []
        except Exception:
            return raw
    if not isinstance(raw, list):
        return ""
    return "\n".join(str(x) for x in raw)


def dict_tipos_para_texto(raw) -> str:
    """JSON {categoria: [tipos]} -> texto 'categoria: tipo1; tipo2' por linha."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw else {}
        except Exception:
            return raw
    if not isinstance(raw, dict):
        return ""
    linhas = []
    for cat, tipos in raw.items():
        if tipos:
            linhas.append(f"{cat}: {'; '.join(str(t) for t in tipos)}")
    return "\n".join(linhas)


def dict_estimativa_para_texto(raw) -> str:
    """JSON {categoria: quantidade} -> texto 'categoria: quantidade' por linha."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw else {}
        except Exception:
            return raw
    if not isinstance(raw, dict):
        return ""
    return "\n".join(f"{k}: {v}" for k, v in raw.items() if v)


# ── Migração de schema (aditiva, não destrutiva) ─────────────────────────────

NOVAS_COLUNAS = {
    "responsavel_preenchimento": "TEXT",
    "situacao":                  "TEXT",
    "versao":                    "TEXT",
    "titulares_estimativa":      "TEXT",
    "titulares_protecao_reforcada": "TEXT",
    "tipos_dados":               "TEXT",
    "tipos_dados_sensiveis":     "TEXT",
    "fluxo_tratamento":          "TEXT",
    "origem_dados":              "TEXT",
    "local_armazenamento":       "TEXT",
    "eliminacao_destinacao":     "TEXT",
    "frequencia_tratamento":     "TEXT",
    "previsao_normativa":        "TEXT",
    "controladores":             "TEXT",
    "operadores":                "TEXT",
    "compartilhamentos":         "TEXT",
    "transferencia_internacional": "TEXT",
    # Critérios de alto risco p/ gatilho de RIPD (Res. CD/ANPD 2/2022, art. 4º)
    "tecnologias_emergentes":    "INTEGER DEFAULT 0",
    "decisoes_automatizadas":    "INTEGER DEFAULT 0",
    "vigilancia_zonas_publicas": "INTEGER DEFAULT 0",
}


def migrar_schema(conn):
    """Adiciona colunas novas e tabela de versões, sem tocar nos dados atuais."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(atividades)")}
    for nome, tipo in NOVAS_COLUNAS.items():
        if nome not in cols:
            conn.execute(f"ALTER TABLE atividades ADD COLUMN {nome} {tipo}")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS versoes (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        atividade_id  INTEGER,
        versao        TEXT,
        sintese       TEXT,
        responsavel   TEXT,
        snapshot      TEXT,
        criado_em     TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ── Módulo RIPD (controles 23.3, 25.8, 25.10 do PPSI 2.0) ──
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ripds (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        atividade_id        INTEGER NOT NULL,
        titulo              TEXT,
        situacao            TEXT DEFAULT 'rascunho',
        versao              TEXT DEFAULT '1.0',
        justificativa       TEXT,
        criterio_geral      TEXT,
        criterio_especifico TEXT,
        fatores_risco       TEXT,
        alto_risco          INTEGER DEFAULT 0,
        descricao_operacoes TEXT,
        principios          TEXT,
        direitos_titulares  TEXT,
        riscos              TEXT,
        medidas_mitigacao   TEXT,
        riscos_residuais    TEXT,
        restricoes_publicacao TEXT,
        aprovado_por        TEXT,
        aprovado_em         TEXT,
        criado_em           TEXT DEFAULT (datetime('now','localtime')),
        atualizado_em       TEXT DEFAULT (datetime('now','localtime'))
    )""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS versoes_ripd (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ripd_id       INTEGER,
        versao        TEXT,
        sintese       TEXT,
        responsavel   TEXT,
        snapshot      TEXT,
        criado_em     TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ── Workflow de aprovação do RIPD em etapas (porte do repo `ropa`) ──
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ripd_aprovacoes (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        ripd_id       INTEGER NOT NULL,
        papel         TEXT NOT NULL,
        aprovador_sub TEXT,
        aprovador_nome TEXT,
        status        TEXT NOT NULL DEFAULT 'pendente',
        comentario    TEXT,
        solicitado_em TEXT DEFAULT (datetime('now','localtime')),
        respondido_em TEXT,
        FOREIGN KEY (ripd_id) REFERENCES ripds(id) ON DELETE CASCADE
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_ripd_aprov_ripd ON ripd_aprovacoes(ripd_id)")


    # Registros legados (pré-PPSI 2.0) passam a "concluído" / versão 1.0.
    conn.execute("UPDATE atividades SET situacao='concluido' WHERE situacao IS NULL OR situacao=''")
    conn.execute("UPDATE atividades SET versao='1.0' WHERE versao IS NULL OR versao=''")

    # Semear versão 1.0 (snapshot) para registros ainda sem histórico de versões.
    rows = conn.execute("SELECT * FROM atividades").fetchall()
    for r in rows:
        n = conn.execute("SELECT COUNT(*) FROM versoes WHERE atividade_id=?", (r["id"],)).fetchone()[0]
        if n == 0:
            snap = dict(r)
            snap.pop("id", None)
            conn.execute("""
                INSERT INTO versoes (atividade_id, versao, sintese, responsavel, snapshot)
                VALUES (?,?,?,?,?)
            """, (r["id"], "1.0", "v1.0 – registro original (migração PPSI 2.0)",
                   "Migração PPSI 2.0", json.dumps(snap, ensure_ascii=False, default=str)))


def proxima_versao(versao_atual: str, alteracao_estrutural: bool) -> str:
    """Versionamento semântico: major para alterações estruturais, minor caso contrário."""
    try:
        major, minor = (versao_atual or "1.0").split(".")
        major = int(major)
        minor = int(minor)
    except Exception:
        major, minor = 1, 0
    if alteracao_estrutural:
        return f"{major + 1}.0"
    return f"{major}.{minor + 1}"


def campos_estruturais() -> set:
    """Alterações nestes campos geram nova versão MAJOR."""
    return {"finalidade", "base_legal", "categorias_dados", "tipos_dados",
            "operadores", "controladores", "fluxo_tratamento", "prazo_retencao"}


# ══════════════════════════════════════════════════════════════════════════════
# Porte do módulo RIPD do repo `ropa` (ripd_module.py) — matriz 5×5 ISO 27005,
# catálogo de riscos/salvaguardas típicos, gatilhos e sugestões.
# Lógica pura (sem DB). Integrado aos campos JSON do modelo PPSI 2.0.
# ══════════════════════════════════════════════════════════════════════════════

# Matriz 5×5 (ISO 27005): probabilidade × impacto → nível
PROB_LABELS = {1: "Muito baixa", 2: "Baixa", 3: "Média", 4: "Alta", 5: "Muito alta"}
IMPACTO_LABELS = {1: "Insignificante", 2: "Menor", 3: "Moderado", 4: "Maior", 5: "Catastrófico"}


def risco_score(probabilidade, impacto) -> int:
    p = max(1, min(5, int(probabilidade or 1)))
    i = max(1, min(5, int(impacto or 1)))
    return p * i


def nivel_risco(probabilidade, impacto) -> str:
    score = risco_score(probabilidade, impacto)
    if score <= 4:
        return "baixo"
    if score <= 9:
        return "moderado"
    if score <= 15:
        return "alto"
    return "critico"


NIVEL_LABEL = {"baixo": "Baixo", "moderado": "Moderado", "alto": "Alto", "critico": "Crítico"}
NIVEL_COR = {"baixo": "#198754", "moderado": "#ffc107", "alto": "#fd7e14", "critico": "#dc3545"}
NIVEL_ORDEM = {"baixo": 1, "moderado": 2, "alto": 3, "critico": 4}


def consolidar_risco(niveis) -> str:
    """Pior risco vence (risco residual consolidado)."""
    if not niveis:
        return "baixo"
    return max(niveis, key=lambda n: NIVEL_ORDEM.get(n, 0))


CATEGORIAS_RISCO = [
    ("confidencialidade", "Confidencialidade"),
    ("integridade", "Integridade"),
    ("disponibilidade", "Disponibilidade"),
    ("conformidade", "Conformidade legal"),
]


# Riscos típicos sugeridos a partir de fatores do RoPA (adaptado aos campos PPSI 2.0)
RISCOS_TIPICOS_POR_FATOR: dict = {
    "dados_sensiveis": [
        {"categoria": "confidencialidade",
         "ameaca": "Acesso indevido a dados pessoais sensíveis",
         "vulnerabilidade": "Controles de acesso insuficientes a dados sensíveis",
         "impacto_titular": "Discriminação, exposição de informações íntimas",
         "probabilidade": 3, "impacto": 5},
        {"categoria": "conformidade",
         "ameaca": "Tratamento de dado sensível sem base legal específica do Art. 11",
         "vulnerabilidade": "Documentação de base legal incompleta",
         "impacto_titular": "Tratamento ilícito; sanções da ANPD",
         "probabilidade": 2, "impacto": 4},
    ],
    "transferencia_internacional": [
        {"categoria": "conformidade",
         "ameaca": "Transferência internacional sem mecanismo válido (Art. 33)",
         "vulnerabilidade": "Ausência de cláusulas contratuais ou decisão de adequação",
         "impacto_titular": "Dados sob jurisdição com proteção inferior",
         "probabilidade": 3, "impacto": 4},
    ],
    "decisao_automatizada": [
        {"categoria": "conformidade",
         "ameaca": "Decisão automatizada sem possibilidade de revisão (Art. 20)",
         "vulnerabilidade": "Ausência de canal de revisão humana",
         "impacto_titular": "Decisão injusta sem direito a contestação",
         "probabilidade": 3, "impacto": 4},
        {"categoria": "conformidade",
         "ameaca": "Viés algorítmico discriminatório",
         "vulnerabilidade": "Modelo não auditado quanto a viés",
         "impacto_titular": "Discriminação ilícita",
         "probabilidade": 2, "impacto": 4},
    ],
    "dados_criancas": [
        {"categoria": "conformidade",
         "ameaca": "Tratamento de dados de crianças sem consentimento parental (Art. 14)",
         "vulnerabilidade": "Verificação de idade ausente ou frágil",
         "impacto_titular": "Tratamento ilícito de dados de menores",
         "probabilidade": 3, "impacto": 5},
    ],
    "alto_volume": [
        {"categoria": "confidencialidade",
         "ameaca": "Vazamento massivo de dados pessoais",
         "vulnerabilidade": "Concentração de grande volume sem segregação",
         "impacto_titular": "Exposição em larga escala",
         "probabilidade": 2, "impacto": 5},
    ],
    "compartilhamento_amplo": [
        {"categoria": "confidencialidade",
         "ameaca": "Uso indevido por terceiro destinatário",
         "vulnerabilidade": "Cláusulas de proteção de dados ausentes ou fracas",
         "impacto_titular": "Uso fora da finalidade informada",
         "probabilidade": 3, "impacto": 3},
    ],
    "retencao_longa": [
        {"categoria": "conformidade",
         "ameaca": "Retenção além do necessário (princípio da necessidade)",
         "vulnerabilidade": "Política de descarte não automatizada",
         "impacto_titular": "Permanência indevida dos dados",
         "probabilidade": 4, "impacto": 2},
    ],
    "base_consentimento": [
        {"categoria": "conformidade",
         "ameaca": "Coleta sem consentimento livre, informado e inequívoco",
         "vulnerabilidade": "Termos de consentimento genéricos ou agrupados",
         "impacto_titular": "Tratamento sem base legal válida",
         "probabilidade": 3, "impacto": 3},
    ],
    "base_legitimo_interesse": [
        {"categoria": "conformidade",
         "ameaca": "Falha no teste de balanceamento (legítimo interesse)",
         "vulnerabilidade": "LIA não documentado",
         "impacto_titular": "Sobreposição indevida sobre direitos do titular",
         "probabilidade": 3, "impacto": 3},
    ],
    "default": [
        {"categoria": "confidencialidade",
         "ameaca": "Acesso não autorizado por usuário interno",
         "vulnerabilidade": "Perfis de acesso amplos demais",
         "impacto_titular": "Exposição não autorizada",
         "probabilidade": 3, "impacto": 3},
        {"categoria": "integridade",
         "ameaca": "Alteração indevida de dados",
         "vulnerabilidade": "Ausência de logs de alteração",
         "impacto_titular": "Decisão baseada em dado incorreto",
         "probabilidade": 2, "impacto": 3},
        {"categoria": "disponibilidade",
         "ameaca": "Indisponibilidade do sistema com perda de dados",
         "vulnerabilidade": "Backup não testado",
         "impacto_titular": "Impossibilidade de exercer direitos",
         "probabilidade": 2, "impacto": 3},
    ],
}

# Catálogo de salvaguardas típicas (técnica, organizacional, jurídica)
SALVAGUARDAS_TIPICAS: list = [
    {"tipo": "tecnica", "descricao": "Criptografia em repouso e em trânsito (TLS 1.2+)"},
    {"tipo": "tecnica", "descricao": "Pseudonimização ou anonimização quando aplicável"},
    {"tipo": "tecnica", "descricao": "Controle de acesso baseado em papéis (RBAC)"},
    {"tipo": "tecnica", "descricao": "Trilha de auditoria de acesso e alterações"},
    {"tipo": "tecnica", "descricao": "MFA para acessos privilegiados"},
    {"tipo": "tecnica", "descricao": "Backup com testes periódicos de restauração"},
    {"tipo": "tecnica", "descricao": "Mascaramento de dados em ambientes não produtivos"},
    {"tipo": "organizacional", "descricao": "Política de privacidade publicada e atualizada"},
    {"tipo": "organizacional", "descricao": "Treinamento periódico em LGPD para a equipe"},
    {"tipo": "organizacional", "descricao": "Procedimento documentado de atendimento ao titular"},
    {"tipo": "organizacional", "descricao": "Procedimento de notificação de incidentes (Art. 48)"},
    {"tipo": "organizacional", "descricao": "Revisão periódica de perfis de acesso"},
    {"tipo": "juridica", "descricao": "Cláusulas de proteção de dados em contratos com operadores"},
    {"tipo": "juridica", "descricao": "Termo de confidencialidade assinado pela equipe"},
    {"tipo": "juridica", "descricao": "Cláusulas contratuais padrão (SCC) para transferência internacional"},
]

TIPO_SALVAGUARDA_LABEL = {"tecnica": "Técnica", "organizacional": "Organizacional", "juridica": "Jurídica"}


def _fatores_atividade(atividade) -> list:
    """Mapeia atividade (campos PPSI 2.0) para chaves de RISCOS_TIPICOS_POR_FATOR."""
    a = dict(atividade or {})
    fatores = []
    if a.get("dados_sensiveis"):
        fatores.append("dados_sensiveis")
    prot = parse_json(a.get("titulares_protecao_reforcada"))
    if any(x in (prot or []) for x in ("criancas", "adolescentes")):
        fatores.append("dados_criancas")
    if a.get("decisoes_automatizadas"):
        fatores.append("decisao_automatizada")
    transf = parse_json(a.get("transferencia_internacional")) or []
    if transf and not (len(transf) == 1 and str(transf[0]).upper() in ("N/A", "NAO", "NÃO", "NONE", "")):
        fatores.append("transferencia_internacional")
    try:
        est = parse_json(a.get("titulares_estimativa"))
        total = 0
        if isinstance(est, dict):
            for v in est.values():
                total += int(str(v).replace(".", "").replace(",", "").strip() or 0)
        elif est:
            total = int(str(est).replace(".", "").replace(",", "").strip() or 0)
        if total >= 10000:
            fatores.append("alto_volume")
    except Exception:
        pass
    base = (a.get("base_legal") or "").upper()
    if base.startswith("IX"):
        fatores.append("base_legitimo_interesse")
    elif base.startswith(("I", "II", "III", "IV")):
        fatores.append("base_consentimento")
    comp = parse_json(a.get("compartilhamentos")) or []
    if len(comp) >= 2:
        fatores.append("compartilhamento_amplo")
    prazo = (a.get("prazo_retencao") or "").lower()
    if "ano" in prazo:
        try:
            anos = int("".join(ch for ch in prazo if ch.isdigit()) or "0")
            if anos >= 5:
                fatores.append("retencao_longa")
        except ValueError:
            pass
    if not fatores:
        fatores.append("default")
    return fatores


def gatilhos_ripd(atividade) -> list:
    """Fatores que tornam o RIPD recomendável/obrigatório (sinalização ao usuário)."""
    a = dict(atividade or {})
    g = []
    if a.get("dados_sensiveis"):
        g.append("Tratamento envolve dados pessoais sensíveis (Art. 5º, II)")
    prot = parse_json(a.get("titulares_protecao_reforcada"))
    if any(x in (prot or []) for x in ("criancas", "adolescentes")):
        g.append("Tratamento envolve dados de crianças e adolescentes (Art. 14)")
    if a.get("decisoes_automatizadas"):
        g.append("Decisões automatizadas que afetem o titular (Art. 20)")
    base = (a.get("base_legal") or "").upper()
    if base.startswith("IX"):
        g.append("Base de legítimo interesse (Art. 7º, IX) — ANPD pode exigir RIPD")
    transf = parse_json(a.get("transferencia_internacional")) or []
    if transf and not (len(transf) == 1 and str(transf[0]).upper() in ("N/A", "NAO", "NÃO", "NONE", "")):
        g.append("Transferência internacional de dados (Art. 33)")
    try:
        est = parse_json(a.get("titulares_estimativa"))
        total = 0
        if isinstance(est, dict):
            for v in est.values():
                total += int(str(v).replace(".", "").replace(",", "").strip() or 0)
        elif est:
            total = int(str(est).replace(".", "").replace(",", "").strip() or 0)
        if total >= 10000:
            g.append(f"Alto volume de titulares (~{total:,})".replace(",", "."))
    except Exception:
        pass
    return g


def sugerir_riscos(atividade) -> list:
    """Riscos típicos sugeridos a partir dos fatores da atividade, com nível inerente."""
    sugestoes = []
    seen = set()
    for fator in _fatores_atividade(atividade):
        for r in RISCOS_TIPICOS_POR_FATOR.get(fator, []):
            key = (r["categoria"], r["ameaca"])
            if key in seen:
                continue
            seen.add(key)
            risco = dict(r)
            risco["nivel_inerente"] = nivel_risco(risco["probabilidade"], risco["impacto"])
            sugestoes.append(risco)
    if len(sugestoes) < 3:
        for r in RISCOS_TIPICOS_POR_FATOR["default"]:
            key = (r["categoria"], r["ameaca"])
            if key not in seen:
                seen.add(key)
                risco = dict(r)
                risco["nivel_inerente"] = nivel_risco(risco["probabilidade"], risco["impacto"])
                sugestoes.append(risco)
    return sugestoes


# Papéis para o workflow de aprovação do RIPD
PAPEIS_APROVACAO = [
    ("dpo", "DPO / Encarregado"),
    ("gestor_unidade", "Gestor da Unidade"),
    ("aprovador", "Aprovador formal"),
    ("compliance", "Compliance / Jurídico"),
]


def papel_label(papel) -> str:
    return dict(PAPEIS_APROVACAO).get(papel, papel)


