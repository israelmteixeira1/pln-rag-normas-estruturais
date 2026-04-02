"""
scripts/split_nbr6120_sections.py
==================================
Divide a NBR6120_2019.md em arquivos de seção com frontmatter YAML.

Cada seção é salva como um arquivo .md individual em data/norms/sections/
com o formato:

    ---
    title: "Título da seção"
    summary: "Resumo descritivo do conteúdo"
    ---
    conteúdo da seção
"""

from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_MD = PROJECT_ROOT / "data" / "norms" / "md" / "NBR6120_2019.md"
OUTPUT_DIR = PROJECT_ROOT / "data" / "norms" / "sections"


def _make_section(filename: str, title: str, summary: str, content: str) -> None:
    """Cria um arquivo de seção com frontmatter."""
    filepath = OUTPUT_DIR / filename
    frontmatter = f'---\ntitle: "{title}"\nsummary: "{summary}"\n---\n'
    filepath.write_text(frontmatter + content.strip() + "\n", encoding="utf-8")
    print(f"  ✓ {filename} ({len(content.strip())} chars)")


def main():
    # Limpa diretório de saída
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    text = SOURCE_MD.read_text(encoding="utf-8")

    print(f"[split] Dividindo NBR6120_2019.md em seções...")
    print(f"[split] Fonte: {SOURCE_MD}")
    print(f"[split] Destino: {OUTPUT_DIR}\n")

    # -----------------------------------------------------------------------
    # Seção 01: Preâmbulo / Dados da norma
    # -----------------------------------------------------------------------
    _make_section(
        "01_preambulo.md",
        "NBR 6120 — Preâmbulo",
        "Dados de identificação da norma NBR 6120:1980, incluindo origem, comitê responsável e errata de 2000.",
        """\
NBR 6120 — Cargas para o cálculo de estruturas de edificações

NOV 1980

ABNT - Associação Brasileira de Normas Técnicas

Origem: Projeto ABNT-NB-5/1978
CB-02 - Comitê Brasileiro de Construção Civil
CE-02:03.11 - Comissão de Estudo de Cargas para o Cálculo de Estruturas de Edifícios

Palavras-chave: Edificação. Estrutura

Esta Errata nº 1 de ABR 2000 tem por objetivo corrigir a NBR 6120:1980.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 02: Objetivo (§ 1)
    # -----------------------------------------------------------------------
    _make_section(
        "02_objetivo.md",
        "1 Objetivo",
        "Define o escopo da norma: fixar condições para determinação dos valores das cargas no projeto de estruturas de edificações.",
        """\
1.1 Esta Norma fixa as condições exigíveis para determinação dos valores das cargas que devem ser consideradas no projeto de estrutura de edificações, qualquer que seja sua classe e destino, salvo os casos previstos em normas especiais.

1.2 Para os efeitos desta Norma, as cargas são classificadas nas seguintes categorias:
a) carga permanente (g);
b) carga acidental (q).
""",
    )

    # -----------------------------------------------------------------------
    # Seção 03: Carga permanente (§ 2.1)
    # -----------------------------------------------------------------------
    _make_section(
        "03_carga_permanente.md",
        "2.1 Carga permanente",
        "Definição de carga permanente: peso próprio da estrutura e elementos construtivos fixos. Inclui regra para paredes divisórias sem posição definida (mínimo 1 kN/m²).",
        """\
2.1.1 Este tipo de carga é constituído pelo peso próprio da estrutura e pelo peso de todos os elementos construtivos fixos e instalações permanentes.

2.1.2 Quando forem previstas paredes divisórias, cuja posição não esteja definida no projeto, o cálculo de pisos com suficiente capacidade de distribuição transversal da carga, quando não for feito por processo exato, pode ser feito admitindo, além dos demais carregamentos, uma carga uniformemente distribuída por metro quadrado de piso não menor que um terço do peso por metro linear de parede pronta, observado o valor mínimo de 1 kN/m².

2.1.3 Na falta de determinação experimental, deve ser utilizada a Tabela 1 para adotar os pesos específicos aparentes dos materiais de construção mais frequentes.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 04: Tabela 1 — Peso específico dos materiais
    # -----------------------------------------------------------------------
    _make_section(
        "04_tabela1_pesos_especificos.md",
        "Tabela 1 — Peso específico dos materiais de construção",
        "Tabela com pesos específicos aparentes (kN/m³) de materiais de construção: rochas, blocos artificiais, revestimentos, madeiras e metais.",
        """\
Tabela 1 - Peso específico dos materiais de construção

| Categoria            | Material                          | Peso específico aparente (kN/m³) |
|----------------------|-----------------------------------|----------------------------------|
| 1 Rochas             | Arenito                           | 26                               |
| 1 Rochas             | Basalto                           | 30                               |
| 1 Rochas             | Gneiss                            | 30                               |
| 1 Rochas             | Granito                           | 28                               |
| 1 Rochas             | Mármore e calcáreo                | 28                               |
| 2 Blocos artificiais | Blocos de argamassa               | 22                               |
| 2 Blocos artificiais | Cimento amianto                   | 20                               |
| 2 Blocos artificiais | Lajotas cerâmicas                 | 18                               |
| 2 Blocos artificiais | Tijolos furados                   | 13                               |
| 2 Blocos artificiais | Tijolos maciços                   | 18                               |
| 2 Blocos artificiais | Tijolos sílico-calcáreos          | 20                               |
| 3 Revestimentos      | Argamassa de cal, cimento e areia | 19                               |
| 3 Revestimentos      | Argamassa de cimento e areia      | 21                               |
| 3 Revestimentos      | Argamassa de gesso                | 12,5                             |
| 3 Revestimentos      | Concreto simples                  | 24                               |
| 3 Revestimentos      | Concreto armado                   | 25                               |
| 4 Madeiras           | Pinho, cedro                      | 5                                |
| 4 Madeiras           | Louro, imbuia, pau óleo           | 6,5                              |
| 4 Madeiras           | Guajuvirá, guatambu, grápia       | 8                                |
| 4 Madeiras           | Angico, cabriuva, ipê róseo       | 10                               |
| 5 Metais             | Aço                               | 78,5                             |
| 5 Metais             | Alumínio e ligas                  | 28                               |
| 5 Metais             | Bronze                            | 85                               |
| 5 Metais             | Chumbo                            | 114                              |
| 5 Metais             | Cobre                             | 89                               |
| 5 Metais             | Ferro fundido                     | 72,5                             |
| 5 Metais             | Estanho                           | 74                               |
| 5 Metais             | Latão                             | 85                               |
| 5 Metais             | Zinco                             | 72                               |
| 6 Diversos           | Alcatrão                          | 12                               |
| 6 Diversos           | Asfalto                           | 13                               |
| 6 Diversos           | Borracha                          | 17                               |
| 6 Diversos           | Papel                             | 15                               |
| 6 Diversos           | Plástico em folhas                | 21                               |
| 6 Diversos           | Vidro plano                       | 26                               |
""",
    )

    # -----------------------------------------------------------------------
    # Seção 05: Carga acidental — definição (§ 2.2)
    # -----------------------------------------------------------------------
    _make_section(
        "05_carga_acidental.md",
        "2.2 Carga acidental",
        "Definição de carga acidental: toda carga que pode atuar sobre a estrutura em função do seu uso (pessoas, móveis, materiais, veículos etc.).",
        """\
É toda aquela que pode atuar sobre a estrutura de edificações em função do seu uso (pessoas, móveis, materiais diversos, veículos etc.).
""",
    )

    # -----------------------------------------------------------------------
    # Seção 06: Condições peculiares (§ 2.2.1.1 a 2.2.1.2)
    # -----------------------------------------------------------------------
    _make_section(
        "06_condicoes_peculiares.md",
        "2.2.1 Condições peculiares",
        "Regras para carregamentos especiais (acréscimo de 3 kN/m²), e valores mínimos de cargas verticais uniformemente distribuídas conforme Tabela 2.",
        """\
2.2.1.1 Nos compartimentos destinados a carregamentos especiais, como os devidos a arquivos, depósitos de materiais, máquinas leves, caixas-fortes etc., não é necessária uma verificação mais exata destes carregamentos, desde que se considere um acréscimo de 3 kN/m² no valor da carga acidental.

2.2.1.2 As cargas verticais que se consideram atuando nos pisos de edificações, além das que se aplicam em caráter especial referem-se a carregamentos devidos a pessoas, móveis, utensílios e veículos, e são supostas uniformemente distribuídas, com os valores mínimos indicados na Tabela 2.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 07: Tabela 2 — Cargas verticais mínimas
    # -----------------------------------------------------------------------
    _make_section(
        "07_tabela2_cargas_verticais.md",
        "Tabela 2 — Valores mínimos das cargas verticais",
        "Tabela com valores mínimos de cargas verticais (kN/m²) para diversos tipos de ocupação: residências, escritórios, escolas, hospitais, garagens, etc.",
        """\
Tabela 2 - Valores mínimos das cargas verticais (Unidade: kN/m²)

| Item | Local                          | Carga (kN/m²)          |
|------|--------------------------------|------------------------|
| 1    | Arquibancadas                  | 4                      |
| 2    | Balcões                        | Mesma carga da peça com a qual se comunicam e as previstas em 2.2.1.5 |
| 3    | Bancos — Escritórios e banheiros | 2                    |
| 3    | Bancos — Salas de diretoria e gerência | 1,5            |
| 4    | Bibliotecas — Sala de leitura  | 2,5                    |
| 4    | Bibliotecas — Depósito de livros | 4                    |
| 4    | Bibliotecas — Estantes de livros | 2,5 kN/m² por metro de altura, mínimo 6 |
| 5    | Casas de máquinas              | mínimo 7,5             |
| 6    | Cinemas — Platéia com assentos fixos | 3                |
| 6    | Cinemas — Estúdio e platéia com assentos móveis | 4     |
| 6    | Cinemas — Banheiro             | 2                      |
| 7    | Clubes — Sala de refeições/assembléia com assentos fixos | 3 |
| 7    | Clubes — Assembléia com assentos móveis | 4              |
| 7    | Clubes — Salão de danças e esportes | 5                  |
| 7    | Clubes — Sala de bilhar e banheiro | 2                   |
| 8    | Corredores — Com acesso ao público | 3                   |
| 8    | Corredores — Sem acesso ao público | 2                   |
| 9    | Cozinhas não residenciais      | mínimo 3               |
| 10   | Depósitos                      | Determinar em cada caso conforme 2.2.1.3 |
| 11   | Edifícios residenciais — Dormitórios, sala, copa, cozinha, banheiro | 1,5 |
| 11   | Edifícios residenciais — Despensa, área de serviço, lavanderia | 2 |
| 12   | Escadas — Com acesso ao público | 3                     |
| 12   | Escadas — Sem acesso ao público (ver 2.2.1.7) | 2,5     |
| 13   | Escolas — Anfiteatro com assentos fixos | 3              |
| 13   | Escolas — Corredor e sala de aula | 3                    |
| 13   | Escolas — Outras salas         | 2                      |
| 14   | Escritórios — Salas de uso geral e banheiro | 2          |
| 15   | Forros — Sem acesso a pessoas  | 0,5                    |
| 16   | Galerias de arte               | mínimo 3               |
| 17   | Galerias de lojas              | mínimo 3               |
| 18   | Garagens e estacionamentos     | 3 (para veículos de passageiros até 25 kN, com ϕ conforme 2.2.1.6) |
| 19   | Ginásios de esportes           | 5                      |
| 20   | Hospitais — Dormitórios, enfermarias, cirurgia, raio X, banheiro | 2 |
| 20   | Hospitais — Corredor           | 3                      |
| 21   | Laboratórios                   | mínimo 3               |
| 22   | Lavanderias                    | 3                      |
| 23   | Lojas                          | 4                      |
| 24   | Restaurantes                   | 3                      |
| 25   | Teatros — Palco                | 5                      |
| 25   | Teatros — Demais dependências  | mesmas cargas de cinemas |
| 26   | Terraços — Sem acesso ao público | 2                    |
| 26   | Terraços — Com acesso ao público | 3                    |
| 26   | Terraços — Inacessível a pessoas | 0,5                  |
| 26   | Terraços — Heliportos elevados | cargas fornecidas pelo Ministério da Aeronáutica |
| 27   | Vestíbulo — Sem acesso ao público | 1,5                 |
| 27   | Vestíbulo — Com acesso ao público | 3                   |
""",
    )

    # -----------------------------------------------------------------------
    # Seção 08: Condições peculiares — itens 2.2.1.3 a 2.2.1.5
    # -----------------------------------------------------------------------
    _make_section(
        "08_condicoes_depositos_coberturas.md",
        "2.2.1.3 a 2.2.1.5 — Depósitos, coberturas e parapeitos",
        "Regras para armazenagem em depósitos (usar Tabela 3), cargas em elementos isolados de coberturas (1 kN) e cargas em parapeitos/balcões (0,8 kN/m horizontal + 2 kN/m vertical).",
        """\
2.2.1.3 No caso de armazenagem em depósitos e na falta de valores experimentais, o peso dos materiais armazenados pode ser obtido através dos pesos específicos aparentes que constam na Tabela 3.

2.2.1.4 Todo elemento isolado de coberturas (ripas, terças e barras de banzo superior de treliças) deve ser projetado para receber, na posição mais desfavorável, uma carga vertical de 1 kN, além da carga permanente.

2.2.1.5 Ao longo dos parapeitos e balcões devem ser consideradas aplicadas uma carga horizontal de 0,8 kN/m na altura do corrimão e uma carga vertical mínima de 2 kN/m.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 09: Coeficiente ϕ para garagens (§ 2.2.1.6)
    # -----------------------------------------------------------------------
    _make_section(
        "09_coeficiente_garagens.md",
        "2.2.1.6 — Coeficiente ϕ de majoração para garagens",
        "Fórmula para calcular o coeficiente ϕ de majoração das cargas acidentais em garagens e estacionamentos, com base no vão da viga ou laje.",
        """\
2.2.1.6 O valor do coeficiente ϕ de majoração das cargas acidentais a serem consideradas no projeto de garagens e estacionamentos para veículos deve ser determinado do seguinte modo:

Sendo ℓ o vão de uma viga ou o vão menor de uma laje; sendo ℓ₀ = 3 m para o caso das lajes e ℓ₀ = 5 m para o caso das vigas, tem-se:

a) ϕ = 1,00 quando ℓ ≥ ℓ₀;
b) ϕ = ℓ₀/ℓ quando ℓ < ℓ₀.

Nota: O valor de ϕ não precisa ser considerado no cálculo das paredes e pilares.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 10: Escadas com degraus isolados (§ 2.2.1.7)
    # -----------------------------------------------------------------------
    _make_section(
        "10_escadas_degraus.md",
        "2.2.1.7 — Escadas com degraus isolados",
        "Carga concentrada de 2,5 kN para degraus isolados de escadas, aplicada na posição mais desfavorável. Vigas de suporte devem usar Tabela 2.",
        """\
2.2.1.7 Quando uma escada for constituída por degraus isolados, estes devem ser calculados para suportarem uma carga concentrada de 2,5 kN, aplicada na posição mais desfavorável. Este carregamento não deve ser considerado na composição de cargas das vigas que suportam os degraus, as quais devem ser calculadas para carga indicada na Tabela 2.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 11: Redução de cargas acidentais (§ 2.2.1.8)
    # -----------------------------------------------------------------------
    _make_section(
        "11_reducao_cargas.md",
        "2.2.1.8 — Redução das cargas acidentais",
        "Redução percentual permitida das cargas acidentais em pilares e fundações conforme o número de pisos, aplicável a escritórios, residências e casas comerciais.",
        """\
2.2.1.8 No cálculo dos pilares e das fundações de edifícios para escritórios, residências e casas comerciais não destinados a depósitos, as cargas acidentais podem ser reduzidas de acordo com os valores indicados na Tabela 4.
""",
    )

    # -----------------------------------------------------------------------
    # Seção 12: Tabela 3 — Materiais de armazenagem
    # -----------------------------------------------------------------------
    _make_section(
        "12_tabela3_armazenagem.md",
        "Tabela 3 — Características dos materiais de armazenagem",
        "Tabela com pesos específicos aparentes (kN/m³) e ângulos de atrito interno para materiais de armazenagem: minerais, materiais de construção e gêneros alimentícios.",
        """\
Tabela 3 - Características dos materiais de armazenagem

| Material                  | Peso específico aparente (kN/m³) | Ângulo de atrito interno |
|---------------------------|----------------------------------|--------------------------|
| Areia com umidade natural | 17-18                            | 30°                      |
| Argila arenosa            | 10                               | 25°                      |
| Cal em pó                 | 10                               | 25°                      |
| Cal em pedra              | 10                               | 45°                      |
| Caliça                    | 13                               | —                        |
| Cimento                   | 14                               | 25°                      |
| Clinker de cimento        | 15                               | 30°                      |
| Pedra britada             | 18                               | 40°                      |
| Seixo                     | 19                               | 30°                      |
| Carvão mineral (pó)       | 7                                | 25°                      |
| Carvão vegetal            | 4                                | 45°                      |
| Carvão em pedra           | 8,5                              | 30°                      |
| Lenha                     | 5                                | 45°                      |
| Açúcar                    | 7,5                              | 35°                      |
| Arroz com casca           | 5,5                              | 36°                      |
| Aveia                     | 5                                | 30°                      |
| Batatas                   | 7,5                              | 30°                      |
| Café                      | 3,5                              | —                        |
| Centeio                   | 7                                | 35°                      |
| Cevada                    | 7                                | 25°                      |
| Farinha                   | 5                                | 45°                      |
| Feijão                    | 7,5                              | 31°                      |
| Feno prensado             | 1,7                              | —                        |
| Frutas                    | 3,5                              | —                        |
| Fumo                      | 3,5                              | 35°                      |
| Milho                     | 7,5                              | 27°                      |
| Soja                      | 7                                | 29°                      |
| Trigo                     | 7,8                              | 27°                      |
""",
    )

    # -----------------------------------------------------------------------
    # Seção 13: Tabela 4 — Redução das cargas acidentais
    # -----------------------------------------------------------------------
    _make_section(
        "13_tabela4_reducao.md",
        "Tabela 4 — Redução das cargas acidentais",
        "Tabela com percentuais de redução das cargas acidentais em função do número de pisos atuantes sobre o elemento estrutural (0% a 60%).",
        """\
Tabela 4 - Redução das cargas acidentais

| Número de pisos que atuam sobre o elemento | Redução percentual das cargas acidentais (%) |
|--------------------------------------------|----------------------------------------------|
| 1, 2 e 3                                   | 0                                            |
| 4                                           | 20                                           |
| 5                                           | 40                                           |
| 6 ou mais                                   | 60                                           |

Nota: Para efeito de aplicação destes valores, o forro deve ser considerado como piso.
""",
    )

    # -----------------------------------------------------------------------
    # Resumo
    # -----------------------------------------------------------------------
    n_files = len(list(OUTPUT_DIR.glob("*.md")))
    print(f"\n[split] ✓ {n_files} seções criadas em {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
