# fluxoNANOBANANA

Fluxo para gerar várias imagens com a **mesma identidade visual** no Nano Banana (Google Flow ou API do Gemini), trocando apenas **3 coisas** por peça:

1. as **frases** (título e subtítulo)
2. a **logo**
3. o **animal/personagem central**

Tudo o resto (layout, cores, tipografia, iluminação, fundo, posição dos elementos) fica travado.

## Como funciona

A consistência vem de duas âncoras usadas juntas em todo prompt:

| Âncora | O que é | Onde fica |
|---|---|---|
| **Post modelo** | Uma imagem já aprovada com a identidade visual. O Nano Banana copia o estilo dela. | `referencias/modelo.png` |
| **DNA visual** | A mesma identidade descrita em texto: paleta (com HEX), fontes, posições, luz. | `identidade/dna-visual.txt` |

O **prompt-mestre** (`prompts/prompt-mestre.txt`) diz ao modelo: *"mantenha tudo igual à Imagem 1 e troque só o personagem, a logo e os textos"*. A planilha (`campanhas/*.csv`) traz apenas o que muda em cada peça.

```
referencias/modelo.png ─┐
identidade/dna-visual ──┼─► prompt-mestre ─► Nano Banana ─► peça final
campanhas/*.csv ────────┘   (frases, logo, personagem)
```

## Estrutura

```
fluxo.py                    script que monta os prompts (e, opcionalmente, gera as imagens)
prompts/prompt-mestre.txt   template com o que fica fixo e o que muda
identidade/dna-visual.txt   descrição da sua identidade visual (edite!)
campanhas/exemplo.csv       uma linha por imagem: frases, logo, personagem, proporção
referencias/modelo.png      seu post modelo (você adiciona)
referencias/logos/          logos em PNG com fundo transparente
referencias/personagens/    (opcional) imagens de referência dos personagens
```

## Passo a passo

### 1. Prepare a identidade (uma vez só)

1. Coloque o post modelo em `referencias/modelo.png`. Se ainda não tiver um, gere no Flow até chegar num resultado que você aprove: ele vira o padrão de todas as peças.
2. Edite `identidade/dna-visual.txt` descrevendo esse post: estilo, cores em HEX, fonte e posição do título e do subtítulo, posição da logo, iluminação, fundo. Quanto mais específico, mais consistente.
3. Coloque as logos em `referencias/logos/` (PNG com fundo transparente funciona melhor).

### 2. Preencha a planilha

Edite `campanhas/exemplo.csv` (ou crie outra). Abre no Excel/Google Sheets; separador `;` ou `,`.

| coluna | obrigatória | exemplo |
|---|---|---|
| `id` | sim | `post-01` |
| `frase_principal` | sim | `SEU NEGÓCIO NO TOPO` |
| `frase_secundaria` | não | `Conheça nossos planos` (vazio = sem subtítulo) |
| `logo` | sim | `logos/marca-exemplo.png` (caminho dentro de `referencias/`) |
| `personagem` | sim* | `uma coruja simpática de óculos redondos` |
| `personagem_ref` | não* | `personagens/guepardo.png` (imagem de referência do animal) |
| `proporcao` | não | `4:5` feed, `9:16` stories/reels, `1:1` quadrado (padrão: `4:5`) |

\* Preencha pelo menos um dos dois: `personagem` (descrição em texto) ou `personagem_ref` (imagem).

### 3. Gere os prompts

```bash
python3 fluxo.py prompts campanhas/exemplo.csv
```

Sai em `saida/exemplo/`: um `prompts.md` com todos os prompts e a lista de imagens a anexar em cada um, e um `.txt` por peça. Não precisa instalar nada além do Python.

### 4. Gere no Google Flow com Nano Banana

Para cada peça do `prompts.md`:

1. Abra seu projeto no Flow e escolha o modo de **imagem** com o modelo **Nano Banana** (prefira o **Nano Banana Pro**, que escreve texto melhor).
2. **Anexe as imagens na ordem indicada**: 1º o post modelo, 2º a logo, 3º o personagem (se houver).
   - Dica: salve o post modelo como **Ingrediente** no projeto, assim ele fica sempre à mão.
3. Cole o prompt da peça e gere 2 a 4 variações.
4. Escolha a melhor. Se uma letra ou detalhe sair errado, peça a correção na mesma conversa, por exemplo: *"corrija o título para exatamente 'SEU NEGÓCIO NO TOPO', sem mudar mais nada"*.

## Opcional: gerar tudo automaticamente pela API do Gemini

O Flow não tem API, mas o mesmo modelo Nano Banana está na API do Gemini. Com ela, o script gera a campanha inteira sozinho:

```bash
pip install google-genai
export GEMINI_API_KEY="sua-chave"   # crie em https://aistudio.google.com/apikey
python3 fluxo.py imagens campanhas/exemplo.csv
```

As imagens saem em `saida/exemplo/`. Opções úteis:

| opção | o que faz |
|---|---|
| `--variacoes 3` | gera 3 versões de cada peça para você escolher |
| `--ids post-02,post-05` | gera de novo só algumas peças |
| `--refazer` | sobrescreve imagens já geradas |
| `--resolucao 2K` | resolução maior (`1K`, `2K`, `4K`, nos modelos que suportam) |
| `--modelo NOME` | troca o modelo (padrão: `gemini-3-pro-image-preview`, o Nano Banana Pro) |

Os nomes dos modelos mudam com o tempo. Confira o atual no Google AI Studio e passe com `--modelo` ou na variável `NANO_BANANA_MODEL` (por exemplo, `gemini-2.5-flash-image` é o Nano Banana original, mais barato, mas aceita só 3 imagens de referência e escreve texto pior).

## Dicas para consistência máxima

- **Personagem novo em duas etapas.** Primeiro gere só o animal no estilo da marca (fundo liso), aprove, salve em `referencias/personagens/` e use em `personagem_ref`. Funciona melhor do que descrever em texto, e o mesmo personagem fica idêntico em várias peças.
- **Logo 100% fiel.** A IA às vezes deforma levemente logos com muitos detalhes. Se precisar de perfeição, peça ao modelo para deixar o espaço da logo vazio e aplique a logo original depois no Canva/Photoshop, sempre na mesma posição.
- **Frases curtas.** Títulos de até ~6 palavras saem com muito menos erros de digitação. Sempre confira a acentuação.
- **Um post modelo por formato.** Se usar feed (4:5) e stories (9:16), tenha um modelo para cada proporção (`--modelo-ref referencias/modelo-stories.png`), porque o layout muda.
- **Mude só a planilha.** Para manter a identidade, não edite o prompt-mestre entre campanhas: troque apenas as linhas do CSV.
