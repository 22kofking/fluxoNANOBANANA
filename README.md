# fluxoNANOBANANA

Fluxo para gerar posts com a **mesma identidade visual** no Nano Banana (Google Flow ou API do Gemini), trocando só **3 blocos** por peça:

| Bloco | Exemplo no post modelo |
|---|---|
| **TEXTO CENTRAL** | `LOGIN DIÁRIO` (destaque amarelo) + `PRÊMIOS TODOS OS DIAS` (complemento branco) |
| **NOME DA CASA** | `TUCANOBET.COM` (a logo no canto superior esquerdo) |
| **PERSONAGEM PRINCIPAL** | o dragão dourado à direita |

Todo o resto fica travado: cenário tropical, moedas, barras de ouro, caça-níquel, cores, fontes, luz e posições.

![post modelo](referencias/modelo.webp)

## Como funciona

A consistência vem de duas âncoras que entram juntas em todo prompt:

| Âncora | O que é | Onde fica |
|---|---|---|
| **Post modelo** | O post aprovado. O Nano Banana copia o estilo dele. | `referencias/modelo.webp` |
| **DNA visual** | A mesma identidade descrita em texto: cenário, cores (HEX), fontes, posições, luz. | `identidade/dna-visual.txt` |

O **prompt-mestre** (`prompts/prompt-mestre.txt`) diz ao modelo: *"mantenha tudo igual à Imagem 1 e troque só o texto central, o nome da casa e o personagem principal"*. A planilha (`campanhas/*.csv`) traz apenas o que muda em cada peça.

## Estrutura

```
fluxo.py                          monta os prompts (e, opcionalmente, gera as imagens pela API)
prompts/prompt-mestre.txt         template: o que fica fixo e os 3 blocos que mudam
identidade/dna-visual.txt         identidade visual da TucanoBet descrita em texto
campanhas/exemplo.csv             uma linha por post
campanhas/pedidos.csv             pedidos avulsos feitos ao Claude
referencias/modelo.webp           post modelo
referencias/logos/                uma logo por casa: <nome da casa em minúsculas>.png
referencias/personagens/          (opcional) imagens de referência dos personagens
```

## A planilha

Abre no Excel/Google Sheets; separador `;` ou `,`.

| coluna | bloco | exemplo |
|---|---|---|
| `id` | nome do arquivo | `login-diario` |
| `texto_central` | TEXTO CENTRAL | `LOGIN DIÁRIO \| PRÊMIOS TODOS OS DIAS` (antes da `\|` = destaque amarelo; depois = complemento branco, opcional) |
| `nome_da_casa` | NOME DA CASA | `TUCANOBET.COM` |
| `personagem` | PERSONAGEM PRINCIPAL | `um tigre dourado saltando com as garras à mostra` |
| `personagem_ref` | (opcional) | `personagens/tigre.png`: imagem de referência do personagem |
| `proporcao` | (opcional) | `21:9` banner (padrão), `1:1` feed, `9:16` stories |

**Logo da casa:** o script procura `referencias/logos/<nome_da_casa em minúsculas>.png` (ou `.jpg`/`.webp`). Para `TUCANOBET.COM` ele usa `referencias/logos/tucanobet.com.png`, recortada do post modelo. Para outra casa, salve a logo dela com o nome certo (PNG com fundo transparente é o ideal). Se não houver arquivo, o modelo escreve o nome da casa no mesmo estilo da logo original.

## Gerar no Google Flow (manual)

1. Gere os prompts:
   ```bash
   python3 fluxo.py prompts campanhas/exemplo.csv
   ```
   Sai em `saida/exemplo/prompts.md`, com cada prompt e a lista de imagens a anexar.
2. No Flow, escolha geração de **imagem** com o **Nano Banana Pro** (o que escreve texto melhor).
3. **Anexe as imagens na ordem indicada**: 1º o post modelo, 2º a logo, 3º o personagem (se houver). Vale salvar o post modelo e a logo como **Ingredientes** do projeto para ter sempre à mão.
4. Cole o prompt e gere 2 a 4 variações.
5. Se uma letra sair errada, peça na mesma conversa: *"corrija o texto para exatamente 'LOGIN DIÁRIO', sem mudar mais nada"*.

## Pedir para o Claude gerar

O Google Flow **não tem API**, então nenhum assistente consegue gerar "dentro" dele a partir da nuvem. Existem dois caminhos:

### Opção A (recomendada): o Claude gera com o mesmo Nano Banana, pela API do Gemini

O modelo é o mesmo do Flow, mas acessado pela API. Depois de configurar uma vez, é só pedir numa sessão do Claude Code com este repositório, por exemplo: *"gera um post: texto central 'GIROS GRÁTIS | TODA SEXTA', casa TUCANOBET.COM, personagem um tigre dourado"*. O Claude preenche `campanhas/pedidos.csv`, roda o script e te devolve a imagem.

Configuração (uma vez):

1. Crie uma chave de API em <https://aistudio.google.com/apikey>. A geração pela API é cobrada pelo Google por imagem, separada da assinatura do Flow.
2. No Claude Code na web, abra o menu do ambiente na barra de título da sessão e clique em **Edit**:
   - em **Environment variables**, adicione `GEMINI_API_KEY=<sua chave>` (nunca cole a chave no chat);
   - em **Network access**, escolha **Custom** e adicione `generativelanguage.googleapis.com` em *Allowed domains*, mantendo a lista padrão de gerenciadores de pacotes.
   Documentação: <https://code.claude.com/docs/en/cloud-environments#network-access>
3. Abra uma **nova sessão** (as mudanças valem para sessões novas) e faça o pedido.

Também funciona no seu computador, sem o Claude:

```bash
pip install google-genai
export GEMINI_API_KEY="sua-chave"
python3 fluxo.py imagens campanhas/exemplo.csv
```

| opção | o que faz |
|---|---|
| `--variacoes 3` | gera 3 versões de cada post para você escolher |
| `--ids login-diario,cashback` | gera só alguns posts |
| `--refazer` | sobrescreve imagens já geradas |
| `--resolucao 2K` | resolução maior (`1K`, `2K`, `4K`, nos modelos que suportam) |
| `--modelo NOME` | troca o modelo (padrão: `gemini-3-pro-image-preview`, o Nano Banana Pro) |

Os nomes dos modelos mudam com o tempo: confira o atual no Google AI Studio e passe com `--modelo` ou na variável `NANO_BANANA_MODEL`.

### Opção B: o Claude usa o próprio site do Flow no seu computador

Para gastar os créditos da sua assinatura do Flow, o Claude precisa operar o site no **seu navegador, logado na sua conta Google**. Isso só funciona numa sessão rodando no seu computador: o app **Claude Desktop** ou a extensão **Claude in Chrome**. Nessa sessão, peça algo como *"abra o Flow e gere o post `giros-gratis` usando o prompt e as imagens de `saida/exemplo/`"*. É mais lento e menos previsível que a Opção A, porque depende de cliques na interface.

## Dicas para consistência máxima

- **Personagem novo em duas etapas.** Gere primeiro só o personagem no estilo do post (fundo liso), aprove, salve em `referencias/personagens/` e use em `personagem_ref`. Assim o mesmo personagem sai idêntico em vários posts.
- **Logo 100% fiel.** A IA às vezes deforma levemente logos detalhadas. Se precisar de perfeição, aplique a logo original por cima depois, no Canva/Photoshop, sempre na mesma posição.
- **Textos curtos.** O destaque com 1 a 3 palavras e o complemento com até 5 palavras saem com muito menos erros. Confira sempre a acentuação.
- **Um post modelo por formato.** Para feed (1:1) ou stories (9:16), crie um modelo nesse formato e use `--modelo-ref referencias/modelo-stories.webp`, porque o layout muda.
- **Mude só a planilha.** Para não perder a identidade, não edite o prompt-mestre nem o DNA entre campanhas.
