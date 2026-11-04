# Pátio de Carga: Carrinho + Boneco de Blocos

Trabalho Prático de Computação Gráfica, UNIPAC 2026/02

## Integrantes e temas sorteados
| Integrante      | Tema |
|-----------------|---|
| Angelo Teixeira | (2) Carrinho de carga |
| Daniel Calixto  | (20) Boneco de blocos |

## Descrição da cena e da interação
Um pátio de carga com piso de concreto, pista sinalizada e uma pilha de caixas. A animação se repete em ciclo:

1. **Chegando:** o carrinho avança pela pista com velocidade constante, e as rodas giram.
2. **Sinal de pare:** quando o carrinho chega a `X_SINAL`, o boneco levanta o braço. Em resposta, o carrinho freia com desaceleração constante até parar na posição de entrega.
3. **Virando:** o boneco baixa o braço, gira o corpo para o carrinho e ergue a caixa acima da parede da caçamba.
4. **Aproximando:** o boneco caminha até o carrinho, balançando as pernas.
5. **Entregando:** o braço desce até a caçamba. Nesse momento, a caixa troca de pai no grafo de cena: deixa de ser filha do ombro do boneco e passa a ser filha do carrinho.
6. **Recuando e liberando:** o boneco tira a mão de dentro da caçamba, recua, vira para a saída e acena "pode ir".
7. **Partindo:** só depois do aceno o carrinho acelera e sai, levando a caixa.

A interação está na dependência entre as etapas: cada ação de um elemento só começa quando a do outro termina. Isso é controlado por uma máquina de estados (`PROXIMA_ETAPA` e `animar()` em `main.py`).

## Instalação e execução
Requisitos: Python 3.8 ou mais recente e placa de vídeo com OpenGL 3.3.

```
python -m pip install -r requirements.txt
python main.py
```

No PyCharm, abra a pasta do projeto, configure um interpretador (Virtualenv), instale o `requirements.txt` e execute `main.py`.

As texturas já estão em `images/`. Para gerá-las de novo, rode `python gerar_texturas.py`.

## Controles
| Tecla | Ação |
|---|---|
| W / A / S / D | mover a câmera |
| R / F | subir / descer |
| Q / E | girar a câmera |
| T / G | olhar para cima / para baixo |
| P | pausar / retomar a animação (a câmera continua funcionando) |
| Z | reiniciar a animação |

## Estrutura do projeto
```
main.py               cena, modelos, animação e controles
gerar_texturas.py     gera as imagens de textura
images/               texturas (chão de concreto e caixa de madeira)
core/                 base, input, attribute, uniform, matrix, object3D,
                      scene, group, camera, mesh, texture, renderTarget, renderer
geometry/             geometry, rectangle, box, polygon, parametric,
                      cylindrical, cylinder
material/             material, lambertMaterial, depthMaterial
light/                light, ambientLight, directionalLight, shadow
extras/               movementRig
```

## Onde estão os recursos gráficos
| Requisito | Onde |
|---|---|
| 1. Modelos e ambiente | `main.py`: `criar_carrinho()`, `criar_boneco()`, `criar_ambiente()` |
| 2. Animação por tempo e interação | `main.py`: `animar(dt)` usa `deltaTime` (calculado em `core/base.py`); máquina de estados `PROXIMA_ETAPA` |
| 3. Translação, rotação, escala e hierarquia | `core/object3D.py` (`translate`, `rotateX/Y/Z`, `scale`, `getWorldMatrix`); `main.py`: `set_pose()`, grupos das rodas, pernas e ombros, troca de pai em `soltar_caixa()`, `scale()` nas caixas decorativas |
| 4. Câmera em perspectiva, teclado e pausa | `core/camera.py` (`makePerspective`); `extras/movementRig.py`; tecla P em `update()` do `main.py` |
| 5. Textura de imagem | `core/texture.py`; `geometry/*` (atributo `vertexUV`); chão com UV repetida 8× em `criar_ambiente()` |
| 6. Luz direcional, materiais e normais | `light/directionalLight.py`; `material/lambertMaterial.py`; normais (`vertexNormal`) em cada geometria |
| 7. Shadow mapping (seção 6.9) | `light/shadow.py`, `material/depthMaterial.py`, passe de sombra em `core/renderer.py`, struct `Shadow` no `lambertMaterial.py` |

## Shaders, atributos e uniforms utilizados

### LambertMaterial (`material/lambertMaterial.py`): todos os objetos visíveis
- **Atributos de vértice:**
  - `vertexPosition`: posição do vértice no espaço do objeto.
  - `vertexUV`: coordenada de textura.
  - `vertexNormal`: vetor normal.
- **Uniforms de transformação:**
  - `modelMatrix`: posição, rotação e escala do objeto no mundo. Vem de `mesh.getWorldMatrix()`, que já inclui a hierarquia.
  - `viewMatrix`: inversa da matriz da câmera.
  - `projectionMatrix`: projeção em perspectiva.
  - O vertex shader calcula `gl_Position = projection * view * model * posição`.
- **Uniforms de material:**
  - `baseColor`: cor do objeto.
  - `useTexture` e `textureSampler`: a textura de imagem.
- **Uniforms de luz:** `light0` a `light3`, structs com tipo, cor, direção, posição e atenuação. Na cena: uma luz ambiente e uma direcional.
- **Uniforms de sombra:** `useShadow` e `shadow0`, uma struct com:
  - `lightDirection`: direção da luz;
  - `projectionMatrix` e `viewMatrix`: matrizes da câmera da luz;
  - `depthTexture`: textura de profundidade;
  - `strength` e `bias`.

### DepthMaterial (`material/depthMaterial.py`): passe de sombra
- **Atributo:** `vertexPosition`.
- **Uniforms:** `modelMatrix`, mais `viewMatrix` e `projectionMatrix` da câmera ortográfica presa à luz.
- O fragment shader grava `gl_FragCoord.z`, a profundidade vista da luz, na textura do `RenderTarget`.

### Sombreamento × sombra
- **Sombreamento** é o escurecimento de uma face conforme o ângulo entre a sua normal e a direção da luz. Pelo modelo de Lambert, `difusa = max(dot(normal, -direçãoDaLuz), 0)`, calculado em `lightCalc()`. Ele depende só da própria superfície: uma face virada para longe da luz fica escura mesmo sem nada na frente.
- **Sombra projetada** acontece quando um objeto bloqueia a luz que chegaria a outro. Ela é calculada pelo shadow mapping, em duas passadas:
  1. O passe de sombra renderiza a cena do ponto de vista da luz e grava a profundidade mais próxima em cada pixel.
  2. No passe principal, cada fragmento é levado para as coordenadas da câmera da luz (`shadowPosition0`). Se a sua distância até a luz for maior que a guardada na textura (mais o `bias`), outro objeto está na frente, e a cor é multiplicada por `1 - strength`.

## Framework
Os componentes em `core/`, `geometry/`, `material/`, `light/` e `extras/` foram transcritos do livro de Stemkoski e Pascale (2022), capítulos 2 a 6. Foram incluídas só as classes usadas na cena. Pequenos ajustes de compatibilidade estão marcados com `# ajuste:` no código:

- **`object3D.py`:** `setPosition` usa `matriz[i, j] = valor`, porque `numpy.itemset()` foi removido no numpy 2.0.
- **`lambertMaterial.py`:**
  - O sampler da textura se chama `textureSampler`, e não `texture`.
  - A amostragem usa `texture()` em vez de `texture2D()`.
  - Motivo: no perfil core do OpenGL 3.3, `texture2D()` não existe, e uma variável chamada `texture` esconde a função `texture()`.
- **`renderer.py`:** a cor de fundo é restaurada após o passe de sombra. No livro, ela ficava branca porque o passe de sombra limpa a tela com `glClearColor(1,1,1,1)`.
- **`base.py`:** se a placa de vídeo não suportar antialiasing, a janela é criada sem ele.
- **`input.py`:** soltar uma tecla que não estava registrada como pressionada não gera erro.

## Contribuições individuais
- Angelo Teixeira: modelagem e animação do carrinho (rodas com rotação, frenagem e partida), configuração da luz e das sombras, testes e documentação.
- Daniel Calixto: modelagem e animação do boneco (braços, pernas, sinais), entrega da caixa (troca de pai no grafo de cena), câmera e controles.

## Fontes consultadas
- STEMKOSKI, Lee; PASCALE, Michael. *Developing graphics frameworks with Python and OpenGL*. 1. ed. Boca Raton: CRC Press, 2022. DOI: 10.1201/9781003181378. É a fonte do framework e do shadow mapping (seção 6.9).
- Texturas: geradas pelo script `gerar_texturas.py`, sem imagens externas.

## Uso de inteligência artificial
- **Ferramenta:** Claude (Anthropic).
- **Finalidade:**
  - auxílio na estrutura da cena e máquina de estados (`main.py`);
  - auxílio no script de texturas.
