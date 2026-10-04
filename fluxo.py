#!/usr/bin/env python3
"""Fluxo Nano Banana: mesma identidade visual, trocando só frases, logo e personagem.

Uso:
  python fluxo.py prompts campanhas/exemplo.csv   # gera os prompts para colar no Flow
  python fluxo.py imagens campanhas/exemplo.csv   # gera as imagens direto pela API do Gemini
"""

import argparse
import csv
import mimetypes
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
REFERENCIAS = RAIZ / "referencias"
PROPORCAO_PADRAO = "4:5"
MODELO_PADRAO = os.environ.get("NANO_BANANA_MODEL", "gemini-3-pro-image-preview")


def ler_campanha(caminho_csv):
    texto = Path(caminho_csv).read_text(encoding="utf-8-sig")
    # Aceita CSV com ";" (Excel em português) ou ",".
    delimitador = csv.Sniffer().sniff(texto.splitlines()[0], delimiters=";,").delimiter
    linhas = list(csv.DictReader(texto.splitlines(), delimiter=delimitador))
    return [{k.strip(): (v or "").strip() for k, v in linha.items() if k} for linha in linhas]


def montar_peca(linha, template, dna, modelo_ref):
    """Preenche o prompt-mestre para uma linha da planilha e lista as imagens a anexar, em ordem."""
    erros = []
    if not linha.get("id"):
        erros.append("coluna 'id' vazia")
    if not linha.get("frase_principal"):
        erros.append("coluna 'frase_principal' vazia")
    if not linha.get("logo"):
        erros.append("coluna 'logo' vazia")
    if not linha.get("personagem") and not linha.get("personagem_ref"):
        erros.append("preencha 'personagem' ou 'personagem_ref'")

    imagens = [modelo_ref, REFERENCIAS / linha.get("logo", "")]
    personagem = linha.get("personagem") or "o personagem da IMAGEM 3"
    ref_personagem = ""
    if linha.get("personagem_ref"):
        imagens.append(REFERENCIAS / linha["personagem_ref"])
        ref_personagem = " (use a IMAGEM 3 como referência exata da aparência do personagem)"

    textos = [f'   - Título: "{linha.get("frase_principal", "")}"']
    if linha.get("frase_secundaria"):
        textos.append(f'   - Subtítulo: "{linha["frase_secundaria"]}"')
    else:
        textos.append("   - Subtítulo: nenhum (remova o subtítulo da Imagem 1 e deixe o espaço limpo)")

    prompt = (
        template.replace("{DNA_VISUAL}", dna.strip())
        .replace("{PERSONAGEM}", personagem)
        .replace("{REF_PERSONAGEM}", ref_personagem)
        .replace("{TEXTOS}", "\n".join(textos))
        .replace("{PROPORCAO}", linha.get("proporcao") or PROPORCAO_PADRAO)
    )
    return prompt, imagens, erros


def carregar_pecas(args):
    template = Path(args.template).read_text(encoding="utf-8")
    dna = Path(args.dna).read_text(encoding="utf-8")
    pecas = []
    for numero, linha in enumerate(ler_campanha(args.csv), start=2):
        if args.ids and linha.get("id") not in args.ids:
            continue
        prompt, imagens, erros = montar_peca(linha, template, dna, Path(args.modelo_ref))
        if erros:
            print(f"[linha {numero}] ignorada: {'; '.join(erros)}", file=sys.stderr)
            continue
        pecas.append((linha, prompt, imagens))
    return pecas


def pasta_saida(args):
    pasta = Path(args.saida) / Path(args.csv).stem
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def nome_imagem(caminho):
    try:
        return str(caminho.relative_to(RAIZ))
    except ValueError:
        return str(caminho)


def cmd_prompts(args):
    pecas = carregar_pecas(args)
    pasta = pasta_saida(args)
    blocos = []
    for linha, prompt, imagens in pecas:
        (pasta / f"{linha['id']}.txt").write_text(prompt, encoding="utf-8")
        anexos = "\n".join(f"{i}. `{nome_imagem(img)}`" for i, img in enumerate(imagens, start=1))
        blocos.append(f"## {linha['id']}\n\nAnexe nesta ordem:\n\n{anexos}\n\n```\n{prompt}```\n")
    (pasta / "prompts.md").write_text("\n".join(blocos), encoding="utf-8")
    print(f"{len(pecas)} prompt(s) gerado(s) em {nome_imagem(pasta)}/")


def cmd_imagens(args):
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("Instale o SDK do Gemini primeiro: pip install google-genai")
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("Defina a variável GEMINI_API_KEY com sua chave do Google AI Studio.")

    client = genai.Client()
    pasta = pasta_saida(args)
    for linha, prompt, imagens in carregar_pecas(args):
        faltando = [nome_imagem(img) for img in imagens if not img.is_file()]
        if faltando:
            print(f"[{linha['id']}] ignorada, imagem não encontrada: {', '.join(faltando)}", file=sys.stderr)
            continue

        conteudo = [prompt]
        for img in imagens:
            mime = mimetypes.guess_type(img.name)[0] or "image/png"
            conteudo.append(types.Part.from_bytes(data=img.read_bytes(), mime_type=mime))
        config_imagem = types.ImageConfig(
            aspect_ratio=linha.get("proporcao") or PROPORCAO_PADRAO,
            image_size=args.resolucao,
        )

        for n in range(1, args.variacoes + 1):
            sufixo = f"-{n}" if args.variacoes > 1 else ""
            if not args.refazer and list(pasta.glob(f"{linha['id']}{sufixo}.*")):
                print(f"[{linha['id']}{sufixo}] já existe, pulando (use --refazer para gerar de novo)")
                continue
            try:
                resposta = client.models.generate_content(
                    model=args.modelo,
                    contents=conteudo,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        image_config=config_imagem,
                    ),
                )
            except Exception as erro:
                print(f"[{linha['id']}{sufixo}] erro na API: {erro}", file=sys.stderr)
                continue

            partes = [p for p in (resposta.parts or []) if p.inline_data and not p.thought]
            if not partes:
                print(f"[{linha['id']}{sufixo}] o modelo não devolveu imagem: {resposta.text or 'sem resposta'}",
                      file=sys.stderr)
                continue
            dados = partes[-1].inline_data
            extensao = mimetypes.guess_extension(dados.mime_type or "image/png") or ".png"
            destino = pasta / f"{linha['id']}{sufixo}{extensao}"
            destino.write_bytes(dados.data)
            print(f"[{linha['id']}{sufixo}] salva em {nome_imagem(destino)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)

    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("csv", help="planilha da campanha (ex.: campanhas/exemplo.csv)")
    comum.add_argument("--modelo-ref", default=str(REFERENCIAS / "modelo.png"),
                       help="post modelo com a identidade visual aprovada (padrão: referencias/modelo.png)")
    comum.add_argument("--template", default=str(RAIZ / "prompts" / "prompt-mestre.txt"))
    comum.add_argument("--dna", default=str(RAIZ / "identidade" / "dna-visual.txt"))
    comum.add_argument("--saida", default=str(RAIZ / "saida"))
    comum.add_argument("--ids", type=lambda s: set(s.split(",")),
                       help="gera só estes ids, separados por vírgula (ex.: post-01,post-03)")

    sub.add_parser("prompts", parents=[comum], help="gera os prompts prontos para colar no Flow")

    p_imagens = sub.add_parser("imagens", parents=[comum], help="gera as imagens pela API do Gemini")
    p_imagens.add_argument("--modelo", default=MODELO_PADRAO,
                           help=f"modelo Nano Banana (padrão: {MODELO_PADRAO}, ou a variável NANO_BANANA_MODEL)")
    p_imagens.add_argument("--resolucao", choices=["1K", "2K", "4K"],
                           help="resolução de saída (só nos modelos que suportam, como o Nano Banana Pro)")
    p_imagens.add_argument("--variacoes", type=int, default=1, help="quantas versões gerar por peça")
    p_imagens.add_argument("--refazer", action="store_true", help="sobrescreve imagens já geradas")

    args = parser.parse_args()
    {"prompts": cmd_prompts, "imagens": cmd_imagens}[args.comando](args)


if __name__ == "__main__":
    main()
