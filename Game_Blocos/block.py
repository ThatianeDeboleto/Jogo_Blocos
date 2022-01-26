import pdb

import constants
import pygame
import math
import copy
import sys

class Block(object):
    """
    Classe para manipulação de bloco de tetris
    """    

    def __init__(self,shape,x,y,screen,color,rotate_en):
        """
        Inicialize a classe do bloco tetris

        Parâmetros:
            - forma - lista de dados do bloco. A lista contém as coordenadas [X,Y] de
                      blocos de construção.
            - x - Coordenada X do primeiro bloco de forma de tetris
            - y - Coordenada Y do primeiro bloco de forma de tetris
            - tela - tela para desenhar
            - color - a cor de cada bloco de forma em notação RGB
            - rotate_en - habilita ou desabilita a rotação
        """
        # A forma inicial (converte tudo em objetos Rect)
        self.shape = []
        for sh in shape:
            bx = sh[0]*constants.BWIDTH + x
            by = sh[1]*constants.BHEIGHT + y
            block = pygame.Rect(bx,by,constants.BWIDTH,constants.BHEIGHT)
            self.shape.append(block)     
        # Atributo de rotação
        self.rotate_en = rotate_en
        # Configure o resto das variáveis
        self.x = x
        self.y = y
        # Movimento nas coordenadas X,Y
        self.diffx = 0
        self.diffy = 0
        #Tela para desenhar
        self.screen = screen
        self.color = color
        # Rotação
        self.diff_rotation = 0

    def draw(self):
        """
      Desenhe o bloco de blocos de forma. Cada bloco de forma
        é preenchido com uma borda colorida e preta.
        """
        for bl in self.shape:
            pygame.draw.rect(self.screen,self.color,bl)
            pygame.draw.rect(self.screen,constants.BLACK,bl,constants.MESH_WIDTH)
        
    def get_rotated(self,x,y):
        """
      Calcule as novas coordenadas com base no ângulo de rotação.

        Parâmetros:
            - x - a coordenada X para transferir
            - y - a coordenada Y para transferir

        Retorna a tupla com novas coordenadas (X,Y).
        """
        # Use a matriz de transformação clássica:
        # https://www.siggraph.org/education/materials/HyperGraph/modeling/mod_tran/2drota.htm
        rads = self.diff_rotation * (math.pi / 180.0)
        newx = x*math.cos(rads) - y*math.sin(rads)
        newy = y*math.cos(rads) + x*math.sin(rads)
        return (newx,newy)        

    def move(self,x,y):
        """
                Mova todos os elementos do bloco usando o deslocamento fornecido.

                Parâmetros:
                    - x - movimento na coordenada X
                    - y - movimento na coordenada Y
                """
        # Acumula as coordenadas X,Y e chama a função de atualização
        self.diffx += x
        self.diffy += y  
        self._update()

    def remove_blocks(self,y):
        """
                Remova os blocos na coordenada Y. Todos os blocos
                acima do Y são movidos um degrau para baixo.

                Parâmetros:
                    - y - coordenada Y para trabalhar.
        """
        new_shape = []
        for shape_i in range(len(self.shape)):
            tmp_shape = self.shape[shape_i]
            if tmp_shape.y < y:
                # O bloco está acima do y, mova para baixo e adicione-o à lista de formas ativas
                # blocos.
                new_shape.append(tmp_shape)  
                tmp_shape.move_ip(0,constants.BHEIGHT)
            elif tmp_shape.y > y:
                # O bloco está abaixo do y, adicione-o à lista. O bloco não precisa ser movido porque
                # a linha removida está acima dela.
                new_shape.append(tmp_shape)
        # O bloco está abaixo do y, adicione-o à lista. O bloco não precisa ser movido porque
        self.shape = new_shape

    def has_blocks(self):
        """
                Retorna verdadeiro se o bloco tiver alguns blocos de forma na lista de formas.
        """
        return True if len(self.shape) > 0 else False

    def rotate(self):
        """
                Configure o valor de rotação para 90 graus.
        """
        # Configure a rotação e atualize as coordenadas de todos os blocos de forma.
        # O bloco é girado se a rotação estiver habilitada
        if self.rotate_en:
            self.diff_rotation = 90
            self._update()

    def _update(self):
        """
                Atualize a posição de todas as caixas de forma.
        """
        for bl in self.shape:
            # Obtenha as coordenadas antigas e calcule as novas coordenadas x,y.
            # Todos os cálculos de rotação são feitos nas coordenadas originais.
            origX = (bl.x - self.x)/constants.BWIDTH
            origY = (bl.y - self.y)/constants.BHEIGHT
            rx,ry = self.get_rotated(origX,origY)
            newX = rx*constants.BWIDTH  + self.x + self.diffx
            newY = ry*constants.BHEIGHT + self.y + self.diffy
            newPosX = newX - bl.x
            newPosY = newY - bl.y
            bl.move_ip(newPosX,newPosY)
        # Tudo foi movido. Configure novas coordenadas x,y, e redefina tudo desabilite o movimento
        # variáveis.
        self.x += self.diffx
        self.y += self.diffy
        self.diffx = 0
        self.diffy = 0
        self.diff_rotation = 0

    def backup(self):

        """
                Faça backup da configuração atual dos blocos de forma.
        """
        # Faça a cópia profunda da lista de formas. Também, lembre-se
        # a configuração atual.
        self.shape_copy = copy.deepcopy(self.shape)
        self.x_copy = self.x
        self.y_copy = self.y
        self.rotation_copy = self.diff_rotation     

    def restore(self):
        """
                Restaure a configuração anterior.
       """
        self.shape = self.shape_copy
        self.x = self.x_copy
        self.y = self.y_copy
        self.diff_rotation = self.rotation_copy

    def check_collision(self,rect_list):
        """
                A função verifica se o bloco colide com qualquer outro bloco
                na lista de formas.

                Parâmetros:
                    - rect_list - a função aceita a lista de objetos Rect que
                                 são usados para a detecção de colisão.
    """
        for blk in rect_list:
            collist = blk.collidelistall(self.shape)
            if len(collist):
                return True
        return False

