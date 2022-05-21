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
  - Formato de cor em hexadecimal (#FFFFFF) e coordenadas no formato (x1,y1),(x2,y2),...,(xn,yn)
- Botão "Edit" que permite editar um objeto selecionado da lista de objetos;
- Botão "Del" que permite excluir o objeto selecionado.

### Navegação
Também na lateral esquerda:
- O campo "step" define o passo que regula as operações de navegação. Valores negativos farão dos movimentos inversos; 
- Setas de navegação, para movimentar a visão pelo mundo;
  - Tabém é possível navegar pressionando Shift, Alt, segurar o Botão Esquerdo do Mouse e arrastar.
- Botões "+" e "-" para aumentar e reduzir o "zoom" de acordo com o passo definido no campo "step";
  - Também é possível aumentar e reduzir o zoom usando o scroll do mouse.
- Botão de rotação. O ângulo de rotação é definido pelo valor do campo "step", em graus.
- Slider de rotação. Se o passo é 1, o slider oferecerá ângulos de 0 à 360 graus. O valor do campo "step" é multiplicador desse ângulo.

### Transformações
O botão de transformação permite abrir uma tela para realizar as transformações de translação, escalonamento e rotação em um objeto selecionado.
As transformações desejadas podem ser definidas nas abas da tela aberta, cada aba com opções da transformação e um botão de adição de transformação na lista de transformações. Depois da confirmação, é calculada e aplicada a matriz de transformação sobre os pontos do objeto.
Também é possível transformar usando atalhos da seguinte forma:
  - Translação pode ser feita segurando a tecla G, o Botão Esquerdo do Mouse e arrastar.
  - Escalonamento pode ser feita segurando a tecla S, o Botão Esquerdo do Mouse e arrastar para cima ou para baixo.

### Arquivos .obj
Arquivos .obj podem ser salvos ou carregados pelo programa através do menu "File".<br>
Os arquivos aceitam entradas de vértices (v), cores (usemtl), objetos(o), que são ou pontos(p), ou linhas ou wireframes(l) ou poligonos fechados(f).<br>
As cores são carregados dos arquivos definidos em mtlib
Os arquivos mtlib devem estar no mesmo diretório do arquivo .obj carregado.<br>
Exemplo de arquivo obj:
```
v -18.000000 -20.000000 0.000000
v 64.431373 62.000000 0.000000
v 0.010000 0.020000 0.000000
v -10.000000 -10.000000 0.000000
v 10.000000 -10.000000 0.000000
v 10.000000 10.000000 0.000000
v -10.000000 10.000000 0.000000
v 47.000000 40.000000 0.000000
v -20.000000 -20.000000 0.000000
v 0.000000 10.000000 0.000000
mtlib material.mtl
o window
w 1 2
o red_dot
p 3
usemtl color_1
o green_square
f 4 5 6 7
usemtl color_2
o blue_triangle
f 8 9 10
usemtl color_3
o yellow_line
l 4 6
usemtl color_4
```

Exemplo de arquivo mtl:
```
newmtl color_1
Kd 1.000000 0.000000 0.000000
newmtl color_2
Kd 0.000000 1.000000 0.000000
newmtl color_3
Kd 0.000000 0.000000 1.000000
newmtl color_4
Kd 1.000000 1.000000 0.000000
```

