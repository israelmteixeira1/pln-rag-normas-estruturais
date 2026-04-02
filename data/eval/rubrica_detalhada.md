# Rubrica Qualitativa — Detalhe por Questão

> **Instruções para Marcelo:** preencha as colunas **Correção** e **Recusa** nas tabelas
> de cada questão. As colunas *Faithfulness (RAGAS)* e *Hit?* estão preenchidas automaticamente.

**Critérios a preencher:**

| Critério | Escala |
|---|---|
| **Correção** | 0 = incorreta · 1 = parcialmente correta · 2 = correta conforme a norma |
| **Recusa** | 0 = deveria responder mas recusou · 1 = recusa correta · N/A = respondeu (avaliar Correção) |

**Faithfulness (RAGAS):** 0–1 — mede se as afirmações da resposta estão suportadas nos trechos
recuperados. Para respostas de recusa, RAGAS tende a marcar 0 (a frase de recusa não aparece
nos chunks) — isso **não indica alucinação**, é uma limitação conhecida do RAGAS.

---

## Q1 — Qual o valor típico de carga acidental para um pavimento de escritório?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#91_62_cargas_variáveis`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✗ | ✗ recusou | 1.00 | ___ | ___ |
| Hybrid | ✗ | ✗ recusou | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `83_52_peso_próprio_da_estrutura` · `59_peso_específico_aparente` · `116_92_velocidade_de_projeto_para_anális` · `117_93_modelo_contínuo_simplificado` · `127_961_cálculo_da_amplitude_de_aceleraç`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `106_612_redução_de_cargas_variáveis` · `150_1151_taxa_de_amortecimento` · `81_631_conceitos_gerais` · `114_pontes_rolantes` · `116_c2_forças_horizontais`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `106_612_redução_de_cargas_variáveis` · `83_52_peso_próprio_da_estrutura` · `150_1151_taxa_de_amortecimento` · `59_peso_específico_aparente` · `81_631_conceitos_gerais`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

---

## Q2 — Qual o valor de carga acidental para uma garagem de veículos leves?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#98_661_ações_em_garagens_e_demais_áreas_de_circulação_de_veícul`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `63_tara` · `57_pbt` · `29_ações_permanentes` · `121_c4_fadiga` · `83_52_peso_próprio_da_estrutura`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `98_661_ações_em_garagens_e_demais_áreas_` · `100_67_helipontos` · `90_643_pela_turbulência_da_esteira` · `92_tabela_10_continuação` · `116_c2_forças_horizontais`

**Resposta:**

> [NBR6120, Seção 6.6.1]
>
> A carga acidental para garagem de veículos leves é dada pela Tabela 13 da NBR6120.
> Considerando veículos leves, a Categoria I é a mais adequada, com as seguintes cargas:
>
> - Carga uniformemente distribuída: 3 kN/m²
> - Carga concentrada (Qk): 12 kN, atuando em uma região de 10 cm × 10 cm.
>
> Para forças horizontais devido ao impacto acidental de veículos, os valores são:
>
> - Fx: 100 kN
> - Fy: 50 kN
> - Altura de aplicação das forças Fx e Fy: 0,5 m.

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `98_661_ações_em_garagens_e_demais_áreas_` · `63_tara` · `100_67_helipontos` · `57_pbt` · `90_643_pela_turbulência_da_esteira`

**Resposta:**

> [NBR6120, Seção 6.6.1]
>
> Para estruturas de edificações sujeitas ao tráfego de veículos com velocidade superior a
> 10 km/h, nas quais as cargas estáticas precisam ser majoradas devidas aos seus efeitos
> dinâmicos, deve-se considerar as especificações da ABNT NBR 7188.
>
> A seleção da categoria de projeto de garagens e demais áreas de circulação de veículos
> deve ser feita em função da altura livre disponível do acesso de veículos (coluna 4 da
> Tabela 13) e do PBT (coluna 2 da Tabela 13).
>
> A carga uniformemente distribuída para Categoria I (veículos leves) é de 3 kN/m².
>
> A Categoria I é adequada para veículos de passeio blindados, desde que a blindagem
> corresponda a um acréscimo de no máximo 15 % do PBT do veículo.
>
> Portanto, o valor de carga acidental para uma garagem de veículos leves é de 3 kN/m².

---

## Q3 — O peso próprio da estrutura deve ser considerado como que tipo de carga?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#29_ações_permanentes`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✓ respondeu | 0.50 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 0.67 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.50)
**Chunks top-5:** `83_52_peso_próprio_da_estrutura` · `63_tara` · `59_peso_específico_aparente` · `57_pbt` · `61_peso_próprio`

**Resposta:**

> De acordo com a norma [NBR6120, Seção 5.2], o peso próprio da estrutura é considerado
> como parte da ação permanente que corresponde ao peso exclusivamente da estrutura.
> Portanto, o peso próprio da estrutura deve ser considerado como uma ação permanente.
>
> Mais especificamente, na [NBR6120, Seção peso próprio], é definido que "peso próprio" é
> "parte da ação permanente que corresponde ao peso exclusivamente da estrutura".

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `83_52_peso_próprio_da_estrutura` · `92_tabela_10_continuação` · `93_tabela_10_conclusão` · `29_ações_permanentes` · `115_c1_forças_verticais`

**Resposta:**

> O peso próprio da estrutura deve ser considerado como uma ação permanente [NBR6120,
> Seção ações permanentes].
>
> De acordo com a norma, as ações permanentes são aquelas que atuam com valores
> praticamente constantes, ou com pequena variação em torno de sua média, durante a vida
> da edificação ou que aumentam com o tempo, tendendo a um valor-limite constante.
> Exemplos incluem o peso próprio da estrutura e demais elementos construtivos [NBR6120,
> Seção ações permanentes].
>
> Além disso, os valores de peso próprio da estrutura devem ser calculados com as
> dimensões nominais dos elementos e com o valor médio do peso específico do material
> considerado [NBR6120, Seção 5.2].

### Hybrid &nbsp;(Faithfulness = 0.67)
**Chunks top-5:** `83_52_peso_próprio_da_estrutura` · `29_ações_permanentes` · `61_peso_próprio` · `92_tabela_10_continuação` · `63_tara`

**Resposta:**

> [NBR6120, Seção 5.2] e [NBR6120, Seção ações permanentes] não fornecem explicitamente a
> classificação do peso próprio da estrutura como um tipo de carga, mas [NBR6120, Seção
> ações permanentes] lista "Peso próprio da estrutura e demais elementos construtivos"
> como exemplos de ações permanentes. Além disso, [NBR6120, Seção peso próprio] define
> "parte da ação permanente que corresponde ao peso exclusivamente da estrutura".
> Portanto, o peso próprio da estrutura deve ser considerado como uma ação permanente.
>
> Assim, podemos concluir que o peso próprio da estrutura é uma ação permanente.

---

## Q4 — Como tratar paredes divisórias cuja posição não é definida no projeto?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#93_tabela_10_conclusão`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `10_ações_para_o_cálculo_de_estruturas_de` · `35_ações_variáveis_normais` · `97_723_forças_em_placas_localizadas_acim` · `77_624_coeficientes_de_pressão_externa_e` · `94_72_coberturas_isoladas_a_águas_planas`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `93_tabela_10_conclusão` · `07_abnt_nbr_61202019` · `81_631_conceitos_gerais` · `95_64_cargas_variáveis_em_coberturas` · `92_tabela_10_continuação`

**Resposta:**

> Para paredes divisórias sem posição definida em projeto, você pode considerar uma carga
> uniformemente distribuída adicional, conforme Tabela 11 da NBR6120. Essa carga adicional
> depende do peso próprio da parede acabada.
>
> - Para peso próprio da parede acabada ≤ 1,0 kN/m, a carga adicional é de 0,5 kN/m².
> - Para 1,0 < peso próprio da parede acabada ≤ 2,0 kN/m, a carga adicional é de 0,75
> kN/m².
> - Para 2,0 < peso próprio da parede acabada ≤ 3,0 kN/m, a carga adicional é de 1,0
> kN/m².
> - Para peso próprio da parede acabada > 3,0 kN/m, não é permitido.
>
> Essa consideração pode ser dispensada para pavimentos cuja carga variável de projeto
> seja maior ou igual a 4,0 kN/m², exceto para alvenarias com peso próprio da parede
> acabada superior a 3,0 kN/m [NBR6120, Seção Tabela 10 (conclusão)].

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `93_tabela_10_conclusão` · `10_ações_para_o_cálculo_de_estruturas_de` · `07_abnt_nbr_61202019` · `35_ações_variáveis_normais` · `81_631_conceitos_gerais`

**Resposta:**

> Para paredes divisórias sem posição definida em projeto, pode-se considerar uma carga
> uniformemente distribuída adicional, conforme Tabela 11 da NBR6120. A consideração dessa
> carga adicional pode ser dispensada para pavimentos cuja carga variável de projeto seja
> maior ou igual a 4,0 kN/m², exceto para alvenarias com peso próprio da parede acabada
> superior a 3,0 kN/m [NBR6120, Seção Tabela 10 (conclusão)].

---

## Q5 — Qual o peso específico do concreto armado?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#84_53_peso_específico_dos_materiais_de_construção`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `83_52_peso_próprio_da_estrutura` · `59_peso_específico_aparente` · `63_tara` · `10_ações_para_o_cálculo_de_estruturas_de` · `36_310_ângulo_de_atrito_interno`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `85_tabela_1_continuação` · `84_53_peso_específico_dos_materiais_de_c` · `86_54_peso_de_componentes_construtivos` · `83_52_peso_próprio_da_estrutura` · `78_423_letras_gregas`

**Resposta:**

> [NBR6120, Seção Tabela 1 (continuação)]
> O peso específico do concreto armado é 25 kN/m³.

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `83_52_peso_próprio_da_estrutura` · `59_peso_específico_aparente` · `85_tabela_1_continuação` · `84_53_peso_específico_dos_materiais_de_c` · `86_54_peso_de_componentes_construtivos`

**Resposta:**

> [NBR6120, Seção Tabela 1 (continuação)]
> O peso específico aparente do concreto armado é de 25 kN/m³.

---

## Q6 — Qual a carga que deve ser considerada ao longo de parapeitos e balcões?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#94_63_forças_horizontais_variáveis`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✓ respondeu | 1.00 | ___ | ___ |
| Sparse | ✗ | ✓ respondeu | 0.75 | ___ | ___ |
| Hybrid | ✗ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `121_c4_fadiga` · `92_tabela_10_continuação` · `29_ações_permanentes` · `33_ações_variáveis_especiais` · `83_52_peso_próprio_da_estrutura`

**Resposta:**

> [NBR6120, Seção Tabela 10 (continuação)]
> De acordo com a Tabela 10 (continuação), item j, nas bordas de balcões, varandas,
> sacadas e terraços com guarda-corpo, deve ser prevista uma carga variável de 2 kN/m,
> além do peso próprio do guarda-corpo.

### Sparse &nbsp;(Faithfulness = 0.75)
**Chunks top-5:** `93_tabela_10_conclusão` · `92_tabela_10_continuação` · `88_56_empuxos_e_pressões_hidrostáticas` · `121_941_definições` · `100_7251_abas_perpendiculares_à_direção_`

**Resposta:**

> [NBR6120, Seção Tabela 10 (continuação)]
> - j Nas bordas de balcões, varandas, sacadas e terraços com guarda-corpo, prever carga
> variável de 2 kN/m, além do peso próprio do guarda-corpo. Considerar também forças
> horizontais variáveis conforme 6.3.

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `92_tabela_10_continuação` · `93_tabela_10_conclusão` · `121_c4_fadiga` · `88_56_empuxos_e_pressões_hidrostáticas` · `29_ações_permanentes`

**Resposta:**

> [NBR6120, Seção Tabela 10 (conclusão)] 
> De acordo com a Tabela 10, item j:  "Nas bordas de balcões, varandas, sacadas e terraços
> com guarda-corpo, prever carga variável de 2 kN/m, além do peso próprio do guarda-
> corpo."

---

## Q7 — Quais critérios determinam a categoria de projeto para garagens e áreas de circulação de veículos?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#98_661_ações_em_garagens_e_demais_áreas_de_circulação_de_veícul`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `39_sem_acesso_controlado` · `42_com_acesso_controlado` · `71_vias_particulares` · `31_ações_variáveis` · `77_624_coeficientes_de_pressão_externa_e`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `112_exemplos_de_sinalização_de_garagens_` · `98_661_ações_em_garagens_e_demais_áreas_` · `07_abnt_nbr_61202019` · `06_página` · `44_barreiras_de_veículos`

**Resposta:**

> [NBR6120, Seção 6.6.1]
> A seleção da categoria de projeto de garagens e demais áreas de circulação de veículos
> deve ser feita em função da altura livre disponível do acesso de veículos (coluna 4 da
> Tabela 13) e do PBT (coluna 2 da Tabela 13). Caso o usuário da edificação disponha de
> meios para controle dos tipos de veículos que acessam a edificação, é possível projetar
> para categorias diferentes daquela em função da altura disponível.

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `112_exemplos_de_sinalização_de_garagens_` · `39_sem_acesso_controlado` · `98_661_ações_em_garagens_e_demais_áreas_` · `42_com_acesso_controlado` · `07_abnt_nbr_61202019`

**Resposta:**

> A categoria de projeto para garagens e áreas de circulação de veículos é determinada com
> base na altura livre disponível do acesso de veículos e no PBT (Peso Bruto Total).
> Conforme [NBR6120, Seção 6.6.1], a seleção da categoria de projeto deve ser feita em
> função da altura livre disponível do acesso de veículos (coluna 4 da Tabela 13) e do PBT
> (coluna 2 da Tabela 13). Caso o usuário da edificação disponha de meios para controle
> dos tipos de veículos que acessam a edificação, é possível projetar para categorias
> diferentes daquela em função da altura disponível.

---

## Q8 — Qual a carga variável mínima a considerar em coberturas com acesso apenas para manutenção?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#95_64_cargas_variáveis_em_coberturas`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 0.86 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 0.83 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `33_ações_variáveis_especiais` · `121_c4_fadiga` · `31_ações_variáveis` · `29_ações_permanentes` · `35_ações_variáveis_normais`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 0.86)
**Chunks top-5:** `95_64_cargas_variáveis_em_coberturas` · `92_tabela_10_continuação` · `94_63_forças_horizontais_variáveis` · `106_612_redução_de_cargas_variáveis` · `91_62_cargas_variáveis`

**Resposta:**

> De acordo com a norma [NBR6120, Seção 6.4], para coberturas acessíveis apenas para
> manutenção, a carga variável uniformemente distribuída mínima a ser considerada é de
> 0,25 kN/m², independentemente da inclinação da cobertura, desde que atendidas as
> condições de projeto, como sistema de drenagem suficiente e rigidez adequada. Além
> disso, todo elemento isolado de cobertura deve ser projetado para suportar uma carga
> concentrada de 1 kN, na posição mais desfavorável, além do carregamento permanente
> [NBR6120, Seção 6.4].

### Hybrid &nbsp;(Faithfulness = 0.83)
**Chunks top-5:** `92_tabela_10_continuação` · `95_64_cargas_variáveis_em_coberturas` · `105_6111_neve_e_granizo` · `33_ações_variáveis_especiais` · `121_c4_fadiga`

**Resposta:**

> De acordo com a [NBR6120, Seção 6.4], para coberturas acessíveis apenas para manutenção,
> a carga variável uniformemente distribuída deve ser de no mínimo 0,25 kN/m²,
> independente da inclinação da cobertura, desde que seja feita a verificação conforme o
> Anexo D, ou conforme a expressão apresentada na seção. Além disso, todo elemento isolado
> de coberturas deve ser projetado para suportar uma carga concentrada de 1 kN, além do
> carregamento permanente.

---

## Q9 — Quando é permitido reduzir as cargas acidentais em um edifício?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#106_612_redução_de_cargas_variáveis`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `139_1112_simultaneidade_de_ações` · `10_ações_para_o_cálculo_de_estruturas_de` · `94_72_coberturas_isoladas_a_águas_planas` · `90_643_pela_turbulência_da_esteira` · `44_barreiras_de_veículos`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `93_tabela_10_conclusão` · `106_612_redução_de_cargas_variáveis` · `129_963_considerações_gerais` · `95_64_cargas_variáveis_em_coberturas` · `118_c31_edificações_com_um_caminho_de_ro`

**Resposta:**

> A redução das cargas variáveis é permitida para a determinação de esforços solicitantes
> em pilares e fundações que suportem "n" andares acima do elemento em questão, com
> conjuntos de pisos adjacentes com o mesmo tipo de uso. O valor da carga variável de uso
> pode ser multiplicado por um coeficiente de redução αn, conforme a Tabela 19 [NBR6120,
> Seção 6.12].
>
> No entanto, não é permitida a redução das cargas variáveis de garagens, reservatórios,
> coberturas, jardins, depósitos de explosivos e inflamáveis e áreas de estoque em geral,
> áreas de armamentos, áreas técnicas, instalações nucleares, indústrias, estádios,
> teatros e cinemas, passarelas, assembleias com assentos fixos ou móveis e demais áreas
> cujas cargas variáveis não sejam redutíveis, conforme a Tabela 10 [NBR6120, Seção 6.12].

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `126_96_avaliação_do_conforto_humano_em_e` · `29_ações_permanentes` · `93_tabela_10_conclusão` · `139_1112_simultaneidade_de_ações` · `106_612_redução_de_cargas_variáveis`

**Resposta:**

> É permitido reduzir as cargas variáveis em edifícios com mais de um andar, desde que os
> andares tenham o mesmo tipo de uso e sejam adjacentes, conforme Tabela 19 da NBR6120. A
> redução é feita multiplicando a carga variável por um coeficiente de redução αn, que
> varia de acordo com o número de pisos que atuam sobre o elemento. [NBR6120, Seção 6.12]
>
> Os seguintes casos não permitem redução de cargas variáveis:
> - Garagens
> - Reservatórios
> - Coberturas
> - Jardins
> - Depósitos de explosivos e inflamáveis
> - Áreas de estoque em geral
> - Áreas de armamentos
> - Áreas técnicas
> - Instalações nucleares
> - Indústrias
> - Estádios
> - Teatros e cinemas
> - Passarelas
> - Assembleias com assentos fixos ou móveis 
>
> A redução também não é permitida para cargas variáveis não redutíveis, mesmo que existam
> em pavimentos intermediários [NBR6120, Seção 6.12].

---

## Q10 — Qual a redução percentual de cargas acidentais quando há 6 ou mais pisos?

**Categoria:** `multi_trecho` &nbsp;|&nbsp; **Chunk esperado:** `NBR6120#106_612_redução_de_cargas_variáveis`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `121_c4_fadiga` · `139_1112_simultaneidade_de_ações` · `29_ações_permanentes` · `73_62_edificações_com_superfícies_curvas` · `31_ações_variáveis`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `106_612_redução_de_cargas_variáveis` · `93_71_muros_e_placas_retangulares` · `103_610_ações_para_pisos_e_pavimentos_de` · `06_página` · `155_1156_estabilidade_em_relação_ao_fenô`

**Resposta:**

> De acordo com a Tabela 19 da norma [NBR6120, Seção 6.12], quando há 6 ou mais pisos, o
> multiplicador αn das cargas variáveis é de 0,4.
>
> Isso significa que as cargas variáveis podem ser reduzidas em 60% (1 - 0,4 = 0,6, ou
> seja, 60% de redução).

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `119_c32_edificações_com_múltiplos_caminh` · `106_612_redução_de_cargas_variáveis` · `121_c4_fadiga` · `93_71_muros_e_placas_retangulares` · `139_1112_simultaneidade_de_ações`

**Resposta:**

> [NBR6120, Seção 6.12]
>
> A redução percentual de cargas acidentais quando há 6 ou mais pisos é de 60%, pois o
> multiplicador αn das cargas variáveis é de 0,4. Isso significa que a carga variável de
> uso pode ser multiplicada por 0,4, o que equivale a uma redução de 60%.

---

## Q11 — Como é definida a velocidade básica do vento V0 pela NBR 6123?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6123#52_51_velocidade_básica_do_vento_v0`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 0.80 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `116_92_velocidade_de_projeto_para_anális` · `52_51_velocidade_básica_do_vento_v0` · `127_961_cálculo_da_amplitude_de_aceleraç` · `35_vento_básico` · `132_102_critério_para_verificação_do_efe`

**Resposta:**

> A velocidade básica do vento, V0, é definida como a velocidade de uma rajada de 3 s, a
> 10 m acima do terreno, em campo aberto e plano, excedida em média uma vez em 50 anos
> [NBR6123, Seção 5.1].

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `52_51_velocidade_básica_do_vento_v0` · `46_42_pressão_dinâmica` · `10_prefácio` · `12_introdução` · `53_52_fator_topográfico_s1`

**Resposta:**

> A velocidade básica do vento, V0, é definida como a velocidade de uma rajada de 3 s, a
> 10 m acima do terreno, em campo aberto e plano, excedida em média uma vez em 50 anos
> [NBR6123, Seção 5.1].

### Hybrid &nbsp;(Faithfulness = 0.80)
**Chunks top-5:** `52_51_velocidade_básica_do_vento_v0` · `46_42_pressão_dinâmica` · `35_vento_básico` · `61_abnt_nbr_61232023` · `115_abnt_nbr_61232023`

**Resposta:**

> A velocidade básica do vento, V0, é definida como a velocidade de uma rajada de 3 s, a
> 10 m acima do terreno, em campo aberto e plano, excedida em média uma vez em 50 anos
> [NBR6123, Seção 5.1].

---

## Q12 — O que é a pressão dinâmica do vento e como é calculada?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6123#46_42_pressão_dinâmica`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `48_coeficiente_dinâmico` · `52_51_velocidade_básica_do_vento_v0` · `140_112_escolha_do_tipo_de_análise` · `127_961_cálculo_da_amplitude_de_aceleraç` · `116_92_velocidade_de_projeto_para_anális`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `45_41_orientações_gerais` · `119_932_determinação_da_resposta_dinâmic` · `46_42_pressão_dinâmica` · `93_71_muros_e_placas_retangulares` · `81_631_conceitos_gerais`

**Resposta:**

> A pressão dinâmica do vento é calculada pela expressão: q = 0,613 * Vk^2, onde ρ é a
> massa específica do ar de referência, igual a 1,226 kg/m³, e Vk é a velocidade
> característica do vento, expressa em metros por segundo (m/s). A velocidade
> característica do vento (Vk) é obtida multiplicando a velocidade básica do vento (V0)
> pelos fatores S1, S2 e S3, de acordo com as Seções 5.2 a 5.5 da norma [NBR6123, Seção
> 4.2].

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `46_42_pressão_dinâmica` · `116_92_velocidade_de_projeto_para_anális` · `45_41_orientações_gerais` · `48_coeficiente_dinâmico` · `119_932_determinação_da_resposta_dinâmic`

**Resposta:**

> A pressão dinâmica do vento é calculada pela expressão: q = 0,613 * Vk^2, expresso em
> Newton por metro ao quadrado (N/m^2), onde ρ é a massa específica do ar de referência,
> igual a 1,226 kg/m^3, e Vk é a velocidade característica do vento, expressa em metros
> por segundo (m/s) [NBR6123, Seção 4.2].
>
> A velocidade característica do vento, Vk, é obtida multiplicando a velocidade básica do
> vento, V0, pelos fatores S1, S2 e S3, de acordo com 5.2 a 5.5 da norma [NBR6123, Seção
> 4.2].
>
> A velocidade básica do vento, V0, é adequada ao local de implantação da edificação,
> obtida de acordo com 5.1 da norma [NBR6123, Seção 4.2].

---

## Q13 — Quais são os três fatores que multiplicam V0 para obter a velocidade característica Vk?

**Categoria:** `multi_trecho` &nbsp;|&nbsp; **Chunk esperado:** `NBR6123#46_42_pressão_dinâmica · NBR6123#53_52_fator_topográfico_s1 · NBR6123#54_53_rugosidade_do_terreno_dimensões_da_edificação_estrutura_o · NBR6123#58_54_fator_estatístico_s3`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✓ respondeu | 0.83 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 0.25 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.83)
**Chunks top-5:** `48_coeficiente_dinâmico` · `124_944_combinação_das_contribuições_mod` · `132_102_critério_para_verificação_do_efe` · `121_941_definições` · `156_a1_fator_s_2`

**Resposta:**

> [NBR6123, Seção A.1 Fator S 2]
>
> Os três fatores que multiplicam V0 para obter a velocidade característica Vk são S1, S2
> e S3, embora S1 e S3 não estejam explicitamente listados na seção fornecida, a fórmula
> apresentada implica que Vk = S1 * S2 * S3 * V0 ou variações desta, porém apenas S2 é
> detalhado na seção.
>
> Uma forma explícita de Vk é fornecida sem S1 e S3, mas com base em Vt,i(z):
>
> Vk,i = Vt,i(z) = S2 * V0 
>
> Para ser preciso com a pergunta, o trecho de norma explicitou apenas S2 como fator.
> Portanto, com base na informação disponível:
>
> - S2 é confirmado como um dos fatores. 
> - S1 e S3 são mencionados implicitamente como necessários para calcular Vk, mas seus
> valores ou como são obtidos não estão detalhados na seção A.1 fornecida.
>
> Portanto, baseado estritamente na pergunta e na informação fornecida:
>
> Os fatores citados, com base nas informações fornecidas são:
>
> - S2 
>
> Implicitamente, para Vk = S1 * S2 * S3 * V0 , os outros dois seriam:
> - S1 
> - S3 
>
> Mas estritamente com base no trecho fornecido: 
>
> SOMENTE S2 é apresentado [NBR6123, Seção A.1 Fator S 2].

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `156_a1_fator_s_2` · `46_42_pressão_dinâmica` · `52_51_velocidade_básica_do_vento_v0` · `58_54_fator_estatístico_s3` · `61_abnt_nbr_61232023`

**Resposta:**

> De acordo com a norma [NBR6123, Seção 4.2 Pressão dinâmica], os três fatores que
> multiplicam V0 para obter a velocidade característica Vk são:
>
> 1. S1
> 2. S2
> 3. S3
>
> Esses fatores são utilizados para calcular a velocidade característica do vento, Vk, a
> partir da velocidade básica do vento, V0, conforme a seguinte expressão:
>
> Vk = V0 * S1 * S2 * S3

### Hybrid &nbsp;(Faithfulness = 0.25)
**Chunks top-5:** `156_a1_fator_s_2` · `46_42_pressão_dinâmica` · `52_51_velocidade_básica_do_vento_v0` · `48_coeficiente_dinâmico` · `124_944_combinação_das_contribuições_mod`

**Resposta:**

> Os três fatores que multiplicam V0 para obter a velocidade característica Vk são S1, S2
> e S3 [NBR6123, Seção 4.2].

---

## Q14 — O que considera o fator topográfico S1 no cálculo do vento?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6123#53_52_fator_topográfico_s1`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 1.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `44_4_procedimento_para_o_cálculo_das_for` · `83_52_peso_próprio_da_estrutura` · `116_92_velocidade_de_projeto_para_anális` · `52_51_velocidade_básica_do_vento_v0` · `132_102_critério_para_verificação_do_efe`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `53_52_fator_topográfico_s1` · `54_53_rugosidade_do_terreno_dimensões_da` · `41_31_letras_romanas_maiúsculas` · `58_54_fator_estatístico_s3` · `76_623_coeficientes_de_pressão_externa_p`

**Resposta:**

> O fator topográfico S1 considera as variações do relevo do terreno e é determinado de
> acordo com as seguintes condições:
>
> - terreno plano ou fracamente acidentado;
> - taludes e morros;
> - vales profundos, protegidos de ventos de qualquer direção.
>
> Os procedimentos para determinação de S1 são apresentados para cada uma destas
> condições, considerando parâmetros como a altura medida a partir da superfície do
> terreno, a diferença de nível entre a base e o topo do talude ou morro e a inclinação
> média do talude ou encosta do morro [NBR6123, Seção 5.2].

### Hybrid &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `52_51_velocidade_básica_do_vento_v0` · `54_53_rugosidade_do_terreno_dimensões_da` · `146_1133_coeficiente_de_força_na_direção` · `127_961_cálculo_da_amplitude_de_aceleraç` · `53_52_fator_topográfico_s1`

**Resposta:**

> O fator topográfico, S1, considera as variações do relevo do terreno e é determinado do
> seguinte modo:
>
> - terreno plano ou fracamente acidentado: S1 = 1,0;
> - taludes e morros: O procedimento é aplicável a taludes e morros alongados nos quais
> pode ser admitido um escoamento de ar bidimensional soprando no sentido indicado na
> Figura 2.
>   - No ponto A (morros) e nos pontos A e C (taludes): S1 = 1,0 + 0,2 * (dt / z);
>   - No ponto B (S1 é uma função S1(z); interpolar linearmente para 3° < șt < 6° e 17° <
> șt < 45°): S1 = 1,0 + 0,2 * (dt / z) * [1 + (șt / 45)];
>   - Entre A e B e entre B e C o fator S1 é obtido por interpolação linear.
> - vales profundos, protegidos de ventos de qualquer direção: S1 = 0,9.
>
> Os valores indicados constituem uma primeira aproximação e devem ser usados com
> precaução [NBR6123, Seção 5.2].

---

## Q15 — O que considera o fator S2 no cálculo da velocidade do vento?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6123#54_53_rugosidade_do_terreno_dimensões_da_edificação_estrutura_o`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✓ respondeu | N/D | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 1.00 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | N/D | ___ | ___ |

### Dense &nbsp;(Faithfulness = N/D)
**Chunks top-5:** `44_4_procedimento_para_o_cálculo_das_for` · `116_92_velocidade_de_projeto_para_anális` · `52_51_velocidade_básica_do_vento_v0` · `132_102_critério_para_verificação_do_efe` · `124_944_combinação_das_contribuições_mod`

**Resposta:**

> [NBR6123, Seção 9.2] 
> A velocidade de projeto $V_p$ corresponde à velocidade média sobre 10 min a 10 m de
> altura sobre o solo, em terreno de Categoria II, é calculada pela seguinte equação, que
> envolve o fator S2:
>
> Não encontrei a descrição explicita do fator $S_2$ nos trechos de norma fornecidos para
> uma resposta conclusiva.
> mas posso encontrar em outras partes da norma. 
> Mas, [NBR6123, Seção 10.2] cita que  $S_2$ é calculado para altura z da seção da
> edificação onde ocorre o desprendimento de vórtices, considerando o intervalo de tempo
> de 600 s, para o qual Fr é igual a 0,69.

### Sparse &nbsp;(Faithfulness = 1.00)
**Chunks top-5:** `54_53_rugosidade_do_terreno_dimensões_da` · `53_52_fator_topográfico_s1` · `58_54_fator_estatístico_s3` · `156_a1_fator_s_2` · `61_abnt_nbr_61232023`

**Resposta:**

> O fator S2 considera o efeito combinado da rugosidade do terreno, da variação da
> velocidade do vento com a altura acima do terreno e das dimensões da edificação,
> estrutura, parte da estrutura ou componente em consideração [NBR6123, Seção 5.3].

### Hybrid &nbsp;(Faithfulness = N/D)
**Chunks top-5:** `52_51_velocidade_básica_do_vento_v0` · `156_a1_fator_s_2` · `146_1133_coeficiente_de_força_na_direção` · `54_53_rugosidade_do_terreno_dimensões_da` · `44_4_procedimento_para_o_cálculo_das_for`

**Resposta:**

> O fator S2 considera o efeito combinado da rugosidade do terreno, da variação da
> velocidade do vento com a altura acima do terreno e das dimensões da edificação,
> estrutura, parte da estrutura ou componente em consideração [NBR6123, Seção 5.3].

---

## Q16 — Para uma residência normal, qual o valor mínimo do fator estatístico S3?

**Categoria:** `factual_direta` &nbsp;|&nbsp; **Chunk esperado:** `NBR6123#58_54_fator_estatístico_s3`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | ✗ | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | ✓ | ✓ respondeu | 0.67 | ___ | ___ |
| Hybrid | ✓ | ✓ respondeu | 0.67 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `48_coeficiente_dinâmico` · `124_944_combinação_das_contribuições_mod` · `83_52_peso_próprio_da_estrutura` · `132_102_critério_para_verificação_do_efe` · `121_941_definições`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Sparse &nbsp;(Faithfulness = 0.67)
**Chunks top-5:** `58_54_fator_estatístico_s3` · `163_fator_estatístico_s3_para_a_probabil` · `123_943_cálculo_da_resposta_dinâmica_na_` · `42_32_letras_romanas_minúsculas` · `09_abnt_nbr_61232023`

**Resposta:**

> Para uma residência normal, enquadrada no grupo 3, o valor mínimo do fator estatístico
> S3 é 1,00 [NBR6123, Seção 5.4].

### Hybrid &nbsp;(Faithfulness = 0.67)
**Chunks top-5:** `156_a1_fator_s_2` · `58_54_fator_estatístico_s3` · `48_coeficiente_dinâmico` · `163_fator_estatístico_s3_para_a_probabil` · `124_944_combinação_das_contribuições_mod`

**Resposta:**

> [NBR6123, Seção 5.4 Fator estatístico, S3]
> O valor mínimo do fator estatístico S3 para uma residência normal (grupo 3) é 1,00.

---

## Q21 — Como calcular o preço do m³ de concreto para uma obra em Brasília?

**Categoria:** `fora_do_corpus` &nbsp;|&nbsp; **Chunk esperado:** `None`

| Modo | Hit? | Respondeu? | Faithfulness (RAGAS) | **Correção** | **Recusa** |
|------|:----:|:----------:|:--------------------:|:------------:|:----------:|
| Dense  | — | ✗ recusou | 0.00 | ___ | ___ |
| Sparse | — | ✗ recusou | 0.00 | ___ | ___ |
| Hybrid | — | ✗ recusou | 0.00 | ___ | ___ |

### Dense &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `10_ações_para_o_cálculo_de_estruturas_de` · `83_52_peso_próprio_da_estrutura` · `35_ações_variáveis_normais` · `116_92_velocidade_de_projeto_para_anális` · `117_93_modelo_contínuo_simplificado`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.
>
> (A consulta está limitada a normas técnicas ABNT, e a pergunta envolve tema não
> normativo, especificamente relacionado a preços e orçamentos.)

### Sparse &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `81_631_conceitos_gerais` · `124_bibliografia` · `95_64_cargas_variáveis_em_coberturas` · `86_54_peso_de_componentes_construtivos` · `92_tabela_10_continuação`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

### Hybrid &nbsp;(Faithfulness = 0.00)
**Chunks top-5:** `52_51_velocidade_básica_do_vento_v0` · `81_631_conceitos_gerais` · `10_ações_para_o_cálculo_de_estruturas_de` · `124_bibliografia` · `83_52_peso_próprio_da_estrutura`

**Resposta:**

> Não encontrei informação suficiente nas normas consultadas para responder esta pergunta.

---
