# Computação Gráfica

Projeto com Interface Gráfica Qt e Python 3

## Instalar dependências

```
pip install -r requirements.txt
```

## Executar aplicação 

```
python3 main.py
```

## Funcionalidades

### Adição, edição e remoção de objetos
Na lateral esquerda da tela do programa temos: 
- Botão "Add" permite abrir uma tela para adição de novos objetos;
  - Formato de cor em hexadecimal (#FFFFFF);
  - Caixa de seleção para definir se o objeto que será criado é preenchido. Quando selecionada, o objeto será apresentado com uma aresta do
  ultimo ao primeiro vértice, sem necessidade de "fechar" o polígono manualmente;
  - Lista em cascata para definir que tipo de objeto será criado;
  - Campo para inserção das coordenadas. O formato da entrada em geral é (x00,y01,z02),...;(x10,y11,z12),...;...(xij,yij,zij). Existem restrições dependendo do tipo do objeto.
- Botão "Edit" que permite editar um objeto selecionado da lista de objetos;
- Botão "Remove" que permite excluir o objeto selecionado.

### Navegação
Também na lateral esquerda:
- O campo "step" define o passo que regula as operações de navegação. Valores negativos farão dos movimentos inversos; 
- Setas de navegação, para movimentar a visão pelo mundo;
  - Tabém é possível navegar pressionando Shift, Alt e arranstando com o Botão Esquerdo do Mouse.
- Botões "+" e "-" para aumentar e reduzir o "zoom" de acordo com o passo definido no campo "step";
  - Também é possível aumentar e reduzir o zoom usando o scroll do mouse.
- Botões de rotação. O ângulo de rotação é definido pelo valor do campo "step", em graus;
  - É possível fazer rotações no eixo Z pressionando Ctrl e arranstando com o Botão Esquerdo do Mouse;
  - É possível fazer rotações no eixo X e Y pressionando Shift e arranstando com o Botão Esquerdo do Mouse.
- Botões de frente e trás;
- Botões de seleção para escolher o eixo de rotação da tela.

### Transformações
O botão de transformação permite abrir uma tela para realizar as transformações de translação, escalonamento e rotação em um objeto selecionado.
As transformações desejadas podem ser definidas nas abas da tela aberta, cada aba com opções da transformação e um botão de adição de transformação na lista de transformações. Depois da confirmação, é calculada e aplicada a matriz de transformação sobre os pontos do objeto.
Também é possível transformar usando atalhos da seguinte forma:
  - Translação pode ser feita segurando a tecla G, e arrastando com o Botão Esquerdo do Mouse;
  - Escalonamento pode ser feita segurando a tecla S, o Botão Esquerdo do Mouse e arrastar para cima ou para baixo;
  - Rotação em torno do centro do objeto, com eixo paralelo ao vetor perpendicular ao VPN e ao VUP pode ser feita segurando a tecla R, o Botão Esquerdo do Mouse e arrastar para cima ou para baixo;
  - Rotação em torno do centro do objeto, com eixo paralelo ao VUP pode ser feita segurando a tecla R, o Botão Esquerdo do Mouse e arrastar para esquerda ou para direita.

### Clipping
Na parte superior da aplicação existem os menus "clipping" e "test". No menu clipping é possível habilitar/desabilitar o clipping e escolher o tipo de clipping de linha. O algoritimo de clipping de linhas pode ser Lian-Barsk ou Cohen-Sutherland. O clipping de objetos é feito com o algoritimo de Sutherland-Hodgman.

### Arquivos .obj
Arquivos .obj podem ser salvos ou carregados pelo programa através do menu "File".<br>
Os arquivos aceitam entradas de vértices (v), cores (usemtl), objetos(o), que são ou pontos(p), ou linhas ou wireframes(l) ou poligonos fechados(f).<br>
As cores são carregados dos arquivos definidos em mtlib
Os arquivos mtlib devem estar no mesmo diretório do arquivo .obj carregado.<br>
<br>
Alguns arquivos de exemplo estão na pasta "sample_files".
Alguns arquivos foram obtidos de https://people.sc.fsu.edu/~jburkardt/data/obj/obj.html e https://groups.csail.mit.edu/graphics/classes/6.837/F03/models/.