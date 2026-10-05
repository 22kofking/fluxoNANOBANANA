# fluxoNANOBANANA

Gera posts com a identidade visual fixa de `referencias/modelo.webp`, trocando só 3 blocos: TEXTO CENTRAL, NOME DA CASA e PERSONAGEM PRINCIPAL. Veja o README para os detalhes.

## Quando o usuário pedir um post

1. Separe o pedido nos 3 blocos e mostre ao usuário antes de gerar:
   - **TEXTO CENTRAL**: `DESTAQUE | COMPLEMENTO` (complemento opcional). Corrija acentuação óbvia (ex.: "PREMIOS" → "PRÊMIOS") e avise.
   - **NOME DA CASA**: padrão `TUCANOBET.COM` se o usuário não disser outra.
   - **PERSONAGEM PRINCIPAL**: descrição curta e visual (ex.: "um tigre dourado saltando com as garras à mostra").
2. Acrescente uma linha em `campanhas/pedidos.csv` com um `id` curto em kebab-case e `proporcao` `21:9`, salvo pedido diferente.
3. Gere:
   - Se `GEMINI_API_KEY` estiver definida: `pip install -q google-genai` (se faltar) e
     `python3 fluxo.py imagens campanhas/pedidos.csv --ids <id>`. Envie a imagem de `saida/pedidos/` ao usuário com SendUserFile.
   - Se não estiver, ou se a API estiver bloqueada pela rede: rode `python3 fluxo.py prompts campanhas/pedidos.csv --ids <id>`, entregue o prompt e a ordem das imagens para colar no Flow, e explique a configuração da seção "Pedir para o Claude gerar" do README.
4. Não edite `prompts/prompt-mestre.txt` nem `identidade/dna-visual.txt` sem o usuário pedir: eles são a identidade visual.
