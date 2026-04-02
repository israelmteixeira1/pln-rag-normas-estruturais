---
title: "10.4 Resposta dinâmica de estruturas esbeltas de seção circular"
summary: "As  recomendações  desta  subseção  se  aplicam  a  estruturas  autoportantes  de  seção  circular (por exemplo, chaminé..."
norm_id: "NBR6123"
edicao: "2023"
---
## 10.4 Resposta dinâmica de estruturas esbeltas de seção circular

As  recomendações  desta  subseção  se  aplicam  a  estruturas  autoportantes  de  seção  circular (por exemplo, chaminés e torres de observação), vibrando em seu modo fundamental. Para outras formas modais, é necessário fazer uma análise mais refinada com o emprego de métodos encontrados na literatura técnica ou por meio da realização de ensaios em túnel de vento.

A presente metodologia permite a estimativa da resposta em termos de deslocamento máximo, bem como a determinação da correspondente força estática equivalente que age em uma estrutura esbelta de seção circular constante ou com pequena variação de diâmetro, ou seja 1,0 ≥ d(h) / d(0) ≥ 0,5 sendo d(z) o diâmetro na altura z acima da base e h altura total da estrutura.

A resposta de pico da estrutura em termos de deslocamento no topo é calculada pela seguinte equação:

<!-- formula-not-decoded -->

onde gy é o fator de pico; e

σ y é o desvio-padrão do deslocamento no topo da estrutura, obtido com a seguinte equação para quaisquer valores de K

<!-- formula-not-decoded -->

sendo a ℓ a amplitude-limite normalizada, igual a 0,4 para o caso de torres e chaminés;

K o parâmetro que relaciona os amortecimentos estrutural e aerodinâmico;

C o coeficiente aerodinâmico, indicado na Tabela 34;

Ka 0 o parâmetro de amortecimento aerodinâmico (Tabela 34);

mm o valor médio da massa por unidade de comprimento do terço superior da estrutura; e

ρ a massa específica do ar, igual 1,226 kg/m 3 .

O parâmetro K é dado por:

<!-- formula-not-decoded -->

onde

ζ é a razão de amortecimento estrutural crítico.

Para os casos em que K ≤ 0,95, σ y / d 0 pode ser simplificada pela seguinte equação:

<!-- formula-not-decoded -->

Para os casos em que K &gt; 1,05, σ y / d 0 pode ser simplificada pela seguinte equação:

<!-- formula-not-decoded -->

Tabela 34 Valores de C e K a0 em função de Re, V cr  (m/s), d 0 (m)

| Re                   | C                        | C                        | K a0          | K a0          |
|----------------------|--------------------------|--------------------------|---------------|---------------|
| Re = 70 000 V cr d 0 | V cr < 11 m/s            | V cr ≥ 11 m/s            | V cr < 11 m/s | V cr ≥ 11 m/s |
| Re < 2 × 10 5        | 0,0554                   | 0,0261                   | 2,0           | 1,1           |
| 2 × 10 5 ≤ Re ≤ 10 6 | 0,1840 - 0,0286 log (Re) | 0,0867 - 0,0135 log (Re) | 1,2           | 0,6           |
| Re > 10 6            | 0,0208                   | 0,0098                   | 1,2           | 0,6           |

Os valores obtidos com as equações desta tabela devem considerar quatro casas decimais.

Para a obtenção do deslocamento de pico do topo da estrutura, é necessário multiplicar o desvio-padrão do deslocamento por um fator de pico, calculado pela seguinte equação:

<!-- formula-not-decoded -->

A carga equivalente estática por unidade de comprimento agindo distribuída sobre o terço superior da estrutura FL é calculada pela seguinte equação:

<!-- formula-not-decoded -->
