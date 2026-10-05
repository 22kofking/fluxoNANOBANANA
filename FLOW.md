# Roteiro: o Claude gera os posts no site do Google Flow

Roteiro para o Claude seguir quando tiver acesso ao navegador do usuário: Claude Cowork com o navegador embutido do Claude Desktop, ou a extensão Claude in Chrome. O usuário só manda o pedido; o Claude faz o resto.

## Preparação (o usuário faz uma vez)

1. No navegador que o Claude vai usar, entrar na conta Google e abrir <https://labs.google/fx/tools/flow>.
2. Criar um projeto chamado `TUCANOBET`.
3. Subir `referencias/modelo.webp` e `referencias/logos/tucanobet.com.png` e salvar os dois como **Ingredientes**, com os nomes `MODELO` e `LOGO TUCANOBET`. Assim o Claude só precisa selecionar os ingredientes, sem enviar arquivos do computador a cada post.

## A cada pedido

1. **Separe o pedido nos 3 blocos** e mostre ao usuário numa mensagem curta:
   - TEXTO CENTRAL: `DESTAQUE | COMPLEMENTO` (complemento opcional). Corrija acentos óbvios e avise.
   - NOME DA CASA: `TUCANOBET.COM`, se o usuário não disser outra.
   - PERSONAGEM PRINCIPAL: descrição curta e visual.
2. **Monte o prompt.** Acrescente a linha em `campanhas/pedidos.csv` e rode
   `python3 fluxo.py prompts campanhas/pedidos.csv --ids <id>`; o prompt sai em `saida/pedidos/<id>.txt`.
   Se não for possível rodar Python, preencha `prompts/prompt-mestre.txt` com `identidade/dna-visual.txt` seguindo as mesmas regras de `fluxo.py`.
3. **Gere no Flow:**
   1. Abra o projeto `TUCANOBET`.
   2. Escolha geração de imagem com o modelo **Nano Banana Pro** e a proporção horizontal mais larga disponível (21:9; se não houver, 16:9, e avise o usuário).
   3. Anexe os ingredientes **nesta ordem**: `MODELO`, depois `LOGO TUCANOBET` (e a referência do personagem, se houver).
   4. Cole o prompt inteiro e gere.
4. **Confira antes de mostrar:**
   - texto central letra por letra, com acentos;
   - logo correta no canto superior esquerdo;
   - selo `+18` no canto superior direito;
   - mesmo cenário, elementos e estilo do post modelo.

   Se algo sair errado, peça a correção no próprio Flow, por exemplo: *"corrija o texto para exatamente 'LOGIN DIÁRIO', sem mudar mais nada"*. Faça no máximo 2 correções; depois mostre o melhor resultado e diga o que ficou errado.
5. **Entregue:** baixe a melhor imagem para `saida/pedidos/<id>.png` e mostre ao usuário.

## Regras

- O login na conta Google é do usuário: se o Flow pedir login ou verificação, peça para ele fazer.
- Não apague projetos, ingredientes nem imagens no Flow.
- Não altere `prompts/prompt-mestre.txt` nem `identidade/dna-visual.txt` sem o usuário pedir.
- Se a interface do Flow mudar e um passo falhar depois de 2 ou 3 tentativas, pare e descreva o que está vendo na tela.
