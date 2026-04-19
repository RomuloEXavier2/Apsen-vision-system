"""
scan_project.py
═══════════════════════════════════════════════════════════════
Varre todos os arquivos do projeto e gera um relatorio.txt
com estrutura, arquitetura e conteúdo completo de cada arquivo.

Uso:
    python scan_project.py                  # varre a pasta atual
    python scan_project.py C:/caminho/pasta # varre pasta específica
═══════════════════════════════════════════════════════════════
"""

import os
import sys
from datetime import datetime

# ── Extensões de código que serão lidas ───────────────────────
CODE_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx",
    ".py", ".html", ".css", ".scss", ".sass",
    ".json", ".env", ".md", ".txt", ".toml",
    ".yaml", ".yml", ".xml", ".sql", ".php",
    ".config", ".babelrc", ".eslintrc",
}

# ── Pastas e arquivos a ignorar ───────────────────────────────
IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".expo",
    ".next", "dist", "build", ".cache", "coverage",
    "android", "ios", ".idea", ".vscode", "venv",
    "env", ".env", "__MACOSX",
}

IGNORE_FILES = {
    ".DS_Store", "Thumbs.db", "package-lock.json",
    "yarn.lock", ".gitignore",
}

MAX_FILE_SIZE_KB = 500  # ignora arquivos maiores que 500KB


def tamanho_formatado(bytes_):
    if bytes_ < 1024:
        return f"{bytes_} B"
    elif bytes_ < 1024 ** 2:
        return f"{bytes_ / 1024:.1f} KB"
    else:
        return f"{bytes_ / 1024 ** 2:.1f} MB"


def varrer(raiz):
    """Retorna lista de (caminho_relativo, caminho_absoluto) de todos os arquivos."""
    arquivos = []
    for dirpath, dirnames, filenames in os.walk(raiz):
        # Remove pastas ignoradas in-place para o os.walk não entrar nelas
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for filename in sorted(filenames):
            if filename in IGNORE_FILES or filename.startswith("."):
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, raiz)
            arquivos.append((rel_path, abs_path))

    return sorted(arquivos)


def arvore(raiz, prefix="", linhas=None):
    """Gera a árvore de diretórios no estilo do comando tree."""
    if linhas is None:
        linhas = []
    try:
        entradas = sorted(os.listdir(raiz))
    except PermissionError:
        return linhas

    entradas = [e for e in entradas
                if e not in IGNORE_DIRS
                and e not in IGNORE_FILES
                and not e.startswith(".")]

    for i, entrada in enumerate(entradas):
        caminho = os.path.join(raiz, entrada)
        conector = "└── " if i == len(entradas) - 1 else "├── "
        extensao = "  [pasta]" if os.path.isdir(caminho) else ""
        linhas.append(f"{prefix}{conector}{entrada}{extensao}")
        if os.path.isdir(caminho) and entrada not in IGNORE_DIRS:
            novo_prefix = prefix + ("    " if i == len(entradas) - 1 else "│   ")
            arvore(caminho, novo_prefix, linhas)
    return linhas


def ler_arquivo(abs_path):
    """Tenta ler o arquivo como texto. Retorna (conteudo, erro)."""
    tamanho = os.path.getsize(abs_path)
    if tamanho > MAX_FILE_SIZE_KB * 1024:
        return None, f"[ignorado: arquivo muito grande ({tamanho_formatado(tamanho)})]"

    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in CODE_EXTENSIONS:
        return None, f"[ignorado: extensão '{ext}' não é código]"

    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(abs_path, "r", encoding=enc) as f:
                return f.read(), None
        except UnicodeDecodeError:
            continue
    return None, "[ignorado: não foi possível decodificar o arquivo]"


def gerar_relatorio(raiz, saida="relatorio.txt"):
    arquivos = varrer(raiz)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_projeto = os.path.basename(os.path.abspath(raiz))

    # Contagens
    total_arquivos = len(arquivos)
    extensoes = {}
    for rel, _ in arquivos:
        ext = os.path.splitext(rel)[1].lower() or "(sem extensão)"
        extensoes[ext] = extensoes.get(ext, 0) + 1

    linhas_relatorio = []

    def w(*args):
        linhas_relatorio.append(" ".join(str(a) for a in args))

    # ── CABEÇALHO ─────────────────────────────────────────────
    w("=" * 70)
    w("  RELATÓRIO DE PROJETO — SCAN COMPLETO")
    w("=" * 70)
    w(f"  Projeto   : {nome_projeto}")
    w(f"  Caminho   : {os.path.abspath(raiz)}")
    w(f"  Gerado em : {agora}")
    w(f"  Total de arquivos encontrados: {total_arquivos}")
    w("=" * 70)

    # ── RESUMO DE EXTENSÕES ───────────────────────────────────
    w("")
    w("── TIPOS DE ARQUIVO ENCONTRADOS " + "─" * 38)
    for ext, count in sorted(extensoes.items(), key=lambda x: -x[1]):
        w(f"  {ext:<20} {count} arquivo(s)")

    # ── ÁRVORE DE DIRETÓRIOS ──────────────────────────────────
    w("")
    w("── ESTRUTURA DE PASTAS E ARQUIVOS " + "─" * 36)
    w(f"{nome_projeto}/")
    for linha in arvore(raiz):
        w(linha)

    # ── ÍNDICE DE ARQUIVOS ────────────────────────────────────
    w("")
    w("── ÍNDICE COMPLETO DE ARQUIVOS " + "─" * 39)
    for i, (rel, abs_path) in enumerate(arquivos, 1):
        tamanho = tamanho_formatado(os.path.getsize(abs_path))
        w(f"  [{i:03d}] {rel}  ({tamanho})")

    # ── CONTEÚDO DE CADA ARQUIVO ──────────────────────────────
    w("")
    w("═" * 70)
    w("  CONTEÚDO DOS ARQUIVOS")
    w("═" * 70)

    lidos = 0
    ignorados = 0

    for i, (rel, abs_path) in enumerate(arquivos, 1):
        conteudo, erro = ler_arquivo(abs_path)
        tamanho = tamanho_formatado(os.path.getsize(abs_path))
        linhas_codigo = conteudo.count("\n") + 1 if conteudo else 0

        w("")
        w("─" * 70)
        w(f"  ARQUIVO [{i:03d}/{total_arquivos}]: {rel}")
        w(f"  Tamanho: {tamanho}  |  Linhas: {linhas_codigo if conteudo else 'N/A'}")
        w("─" * 70)

        if erro:
            w(erro)
            ignorados += 1
        else:
            w(conteudo)
            lidos += 1

    # ── RODAPÉ ────────────────────────────────────────────────
    w("")
    w("═" * 70)
    w("  FIM DO RELATÓRIO")
    w(f"  Arquivos lidos    : {lidos}")
    w(f"  Arquivos ignorados: {ignorados}")
    w(f"  Total             : {total_arquivos}")
    w("═" * 70)

    # ── SALVAR ────────────────────────────────────────────────
    caminho_saida = os.path.join(os.path.abspath(raiz), saida)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_relatorio))

    print(f"\n{'=' * 55}")
    print(f"  Relatório gerado com sucesso!")
    print(f"{'=' * 55}")
    print(f"  Arquivo : {caminho_saida}")
    print(f"  Lidos   : {lidos} arquivos")
    print(f"  Ignorados: {ignorados} arquivos")
    print(f"  Total   : {total_arquivos} arquivos")
    print(f"{'=' * 55}\n")
    return caminho_saida


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isdir(pasta):
        print(f"Erro: '{pasta}' não é uma pasta válida.")
        sys.exit(1)

    gerar_relatorio(pasta)