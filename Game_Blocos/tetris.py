import pygame
import pdb

import random
import math
import block
import constants

class Tetris(object):
    """
        A classe com implementação da lógica do jogo tetris.
    """

    def __init__(self,bx,by):
        """
                Inicialize o objeto tetris.

                Parâmetros:
                    - bx - número de blocos em x
                    - por - número de blocos em y
        """
        # Calcular a resolução do tabuleiro de jogo com base no número necessário de blocos.
        self.resx = bx*constants.BWIDTH+2*constants.BOARD_HEIGHT+constants.BOARD_MARGIN
        self.resy = by*constants.BHEIGHT+2*constants.BOARD_HEIGHT+constants.BOARD_MARGIN
        # Prepare the pygame board objects (white lines)
        self.board_up    = pygame.Rect(0,constants.BOARD_UP_MARGIN,self.resx,constants.BOARD_HEIGHT)
        self.board_down  = pygame.Rect(0,self.resy-constants.BOARD_HEIGHT,self.resx,constants.BOARD_HEIGHT)
        self.board_left  = pygame.Rect(0,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,self.resy)
        self.board_right = pygame.Rect(self.resx-constants.BOARD_HEIGHT,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,self.resy)
        self.blk_list    = []

        self.start_x = math.ceil(self.resx/2.0)
        self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        # Dados dos blocos (formas e cores). A forma é codificada na lista de pontos [X,Y]. Cada ponto
        # representa a posição relativa. O valor verdadeiro/falso é usado para a configuração de rotação onde
        # False significa que não há rotação e True permite a rotação.
        #Blocos I S J O Z T J
        self.block_data = (
            ([[0,0],[1,0],[2,0],[3,0]],constants.RED,True),
            ([[0,0],[1,0],[0,1],[-1,1]],constants.GREEN,True),
            ([[0,0],[1,0],[2,0],[2,1]],constants.BLUE,True),
            ([[0,0],[0,1],[1,0],[1,1]],constants.ORANGE,False),
            ([[-1,0],[0,0],[0,1],[1,1]],constants.GOLD,True),
            ([[0,0],[1,0],[2,0],[1,1]],constants.PURPLE,True),
            ([[0,0],[1,0],[2,0],[0,1]],constants.CYAN,True),
        )
        # Calcula o número de blocos. Quando o número de blocos é par, podemos usá-lo diretamente, mas
        # temos que diminuir o número de blocos na linha em um quando o número for ímpar (por causa da margem usada).
        self.blocks_in_line = bx if bx%2 == 0 else bx-1
        self.blocks_in_pile = by
        # PONTUACAO
        self.score = 0
        # Lembre-se da velocidade atual
        self.speed = 1
        # O limite do nível de pontuação
        self.score_level = constants.SCORE_LEVEL

    def apply_action(self):
        """ Obtenha o evento da fila de eventos e execute o açao."""
        # Pegue o evento da fila de eventos.
        for ev in pygame.event.get():
            # Check se o botão fechar foi acionado.
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                self.done = True
            # Detecte os eventos-chave para o controle do jogo.
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    self.active_block.move(0,constants.BHEIGHT)
                if ev.key == pygame.K_LEFT:
                    self.active_block.move(-constants.BWIDTH,0)
                if ev.key == pygame.K_RIGHT:
                    self.active_block.move(constants.BWIDTH,0)
                if ev.key == pygame.K_SPACE:
                    self.active_block.rotate()
                if ev.key == pygame.K_p:
                    self.pause()
       

            if ev.type == constants.TIMER_MOVE_EVENT:
                self.active_block.move(0,constants.BHEIGHT)
       
    def pause(self):

        """ Pause o jogo e desenhe a corda. Esta função
            também chama a função flip que desenha a string na tela.
        """
        # Desenhe a corda no centro da tela.
        self.print_center(["PAUSA","Press \"p\" para continuar"])
        pygame.display.flip()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    return
       
    def set_move_timer(self):
        """
        Configure o temporizador de movimento para o
        """
        # Configure o tempo para disparar o evento de movimento. O valor mínimo permitido é 1
        speed = math.floor(constants.MOVE_TICK / self.speed)
        speed = max(1,speed)
        pygame.time.set_timer(constants.TIMER_MOVE_EVENT,speed)
 
    def run(self):
        # Inicializar game (pygame, fonts)
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont(pygame.font.get_default_font(),constants.FONT_SIZE)
        self.screen = pygame.display.set_mode((self.resx,self.resy))
        pygame.display.set_caption("Tetris")

        self.set_move_timer()
        # Variáveis de controle para o jogo. O sinal feito é usado
        # para controlar o loop principal (é definido pela ação quit), o sinal game_over
        # é definido pela lógica do jogo e também é usado para a detecção de desenho "game over".
        # Finalmente a variável new_block é usada para a solicitação de um novo bloco tetris.
        self.done = False
        self.game_over = False
        self.new_block = True
        #
        # Imprima a pontuação inicial
        self.print_status_line()
        while not(self.done) and not(self.game_over):
            self.get_block()
            self.game_logic()
            self.draw_game()

        if self.game_over:
            self.print_game_over()

        pygame.font.quit()
        pygame.display.quit()        
   
    def print_status_line(self):
        string = ["Pontos: {0}   Rapidez: {1}x".format(self.score,self.speed)]
        self.print_text(string,constants.POINT_MARGIN,constants.POINT_MARGIN)        

    def print_game_over(self):
        # Imprime o jogo por texto
        self.print_center(["Game Over","Pressione \"q\" sair"])
        pygame.display.flip()

        while True: 
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                    return

    def print_text(self,str_lst,x,y):

        """
                Imprima o texto nas coordenadas X,Y.

                Parâmetros:
                    - str_lst - lista de strings para imprimir. Cada string é impressa em uma nova linha.
                    - x - coordenada X da primeira string
                    - y - Coordenada Y da primeira string
        """
        prev_y = 0
        for string in str_lst:
            size_x,size_y = self.myfont.size(string)
            txt_surf = self.myfont.render(string,False,(255,255,255))
            self.screen.blit(txt_surf,(x,y+prev_y))
            prev_y += size_y 

    def print_center(self,str_list):

        """
                Imprima a string no centro da tela.

                Parâmetros:
                    - str_lst - lista de strings para imprimir. Cada string é impressa em uma nova linha.
         """
        max_xsize = max([tmp[0] for tmp in map(self.myfont.size,str_list)])
        self.print_text(str_list,self.resx/2-max_xsize/2,self.resy/2)

    def block_colides(self):
        for blk in self.blk_list:
            if blk == self.active_block:
                continue 
            # Detectar situaçoes
            if(blk.check_collision(self.active_block.shape)):
                return True
        return False

    def game_logic(self):

        """
            Implementação da lógica principal do jogo. Esta função detecta colisões
            e inserção de novos blocos de tetris.
        """
        # Lembre-se da configuração atual e tente
        # aplica a ação
        self.active_block.backup()
        self.apply_action()
        # Lógica de borda, verifique se colidimos com borda inferior ou qualquer
        # outra fronteira. Esta verificação também inclui a detecção com outros blocos de tetris.
        down_board  = self.active_block.check_collision([self.board_down])
        any_border  = self.active_block.check_collision([self.board_left,self.board_up,self.board_right])
        block_any   = self.block_colides()
        # Restaure a configuração se alguma colisão foi detectada
        if down_board or any_border or block_any:
            self.active_block.restore()
        # Até aí tudo bem, amostra o estado anterior e tenta mover para baixo (para detectar a colisão com outro bloco).
        # Depois disso, detecta a inserção de um novo bloco. O bloco novo bloco é inserido se chegamos à fronteira
        # ou não podemos descer.
        self.active_block.backup()
        self.active_block.move(0,constants.BHEIGHT)
        can_move_down = not self.block_colides()  
        self.active_block.restore()
        if not can_move_down and (self.start_x == self.active_block.x and self.start_y == self.active_block.y):
            self.game_over = True
        if down_board or not can_move_down:     
            # Request new block
            self.new_block = True
            # Detecta a linha preenchida e possivelmente remove a linha do
            # tela.
            self.detect_line()   
 
    def detect_line(self):
        """
        Detecta se a linha está preenchida. Se sim, remova a linha e
        mover-se com os blocos de construção restantes para novas posições.
        """
        # Pegue cada bloco de forma do bloco tetris imóvel e tente
        # para detectar a linha preenchida. O número de blocos de construção é passado para a classe
        # na função de inicialização.
        for shape_block in self.active_block.shape:
            tmp_y = shape_block.y
            tmp_cnt = self.get_blocks_in_line(tmp_y)
            # Detectar se a linha contém o número determinado de blocos
            if tmp_cnt != self.blocks_in_line:
                continue 
            # Ok, DETECTAR LINHA
            self.remove_line(tmp_y)
            self.score += self.blocks_in_line * constants.POINT_VALUE
            if self.score > self.score_level:
                self.score_level *= constants.SCORE_LEVEL_RATIO
                self.speed       *= constants.GAME_SPEEDUP_RATIO

                self.set_move_timer()

    def remove_line(self,y):
        """
        Remova a linha com as coordenadas Y fornecidas. Blocos abaixo do preenchido
        linha estão intactos. O resto dos blocos (yi > y) são movidos um nível.

        Parâmetros:
            - y - Coordenada Y a remover.
        """
        # Iterar sobre todos os blocos da lista e remover blocos com a coordenada Y.
        for block in self.blk_list:
            block.remove_blocks(y)
        self.blk_list = [blk for blk in self.blk_list if blk.has_blocks()]

    def get_blocks_in_line(self,y):
        """
                Obtenha o número de blocos de forma na coordenada Y.

                Parâmetros:
                    - y - Coordenada Y para escanear.
        """
        # Iteravela a lista de formas de todos os blocos e incrementa o contador
        # se o bloco de forma for igual à coordenada Y.
        tmp_cnt = 0
        for block in self.blk_list:
            for shape_block in block.shape:
                tmp_cnt += (1 if y == shape_block.y else 0)            
        return tmp_cnt

    def draw_board(self):
        """
                Desenhe o quadro branco.
        """
        pygame.draw.rect(self.screen,constants.WHITE,self.board_up)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_down)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_left)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_right)

        self.print_status_line()

    def get_block(self):

        if self.new_block:
            # Pegue o bloco e adicione-o à lista de blocos (estático por enquanto)
            tmp = random.randint(0,len(self.block_data)-1)
            data = self.block_data[tmp]
            self.active_block = block.Block(data[0],self.start_x,self.start_y,self.screen,data[1],data[2])
            self.blk_list.append(self.active_block)
            self.new_block = False

    def draw_game(self):
        """
                Desenhe a tela do jogo.
        """
        # Limpe a tela, desenhe o tabuleiro e desenhe
        # todos os blocos de tetris
        self.screen.fill(constants.BLACK)
        self.draw_board()
        for blk in self.blk_list:
            blk.draw()
        
        pygame.display.flip()

if __name__ == "__main__":
    Tetris(16,30).run()
