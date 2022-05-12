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
- Setas de navegação, para movimentar a visão pelo mundo;
  - Tabém é possível navegar pressionando Shift, Alt, segurar o Botão Esquerdo do Mouse e arrastar.
- Botões "+" e "-" para aumentar e reduzir o "zoom".
  - Também é possível aumentar e reduzir o zoom usando o scroll do mouse.

### Transformações
O botão de transformação permite abrir uma tela para realizar as transformações de translação, escalonamento e rotação em um objeto selecionado.
As transformações desejadas podem ser definidas nas abas da tela aberta, cada aba com opções da transformação e um botão de adição de transformação na lista de transformações. Depois da confirmação, é calculada e aplicada a matriz de transformação sobre os pontos do objeto.
Também é possível transformar usando atalhos:
  - Translação pode ser feita segurando a tecla G, o Botão Esquerdo do Mouse e arrastar.
  - Escalonamento pode ser feita segurando a tecla S, o Botão Esquerdo do Mouse e arrastar para cima ou para baixo.
  - Rotação pode ser feita segurando a tecla R, o Botão Esquerdo do Mouse e arrastar para cima ou para baiaxo.
