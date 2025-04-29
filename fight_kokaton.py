import os
import random
import sys
import time
import math
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 #爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し、真理値タプルを返す関数
    引数：こうかとんや爆弾、ビームなどのRect
    戻り値：横方向、縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.directions = (+5, 0) #初期向き(右)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.directions = tuple(sum_mv)
        screen.blit(self.img, self.rct)


class Beam: # ビームクラス:
    # """
    # こうかとんが放つビームに関するクラス
    # """
    def __init__(self, bird:"Bird"): # def イニシャライザ(self, bird:"Bird"):
    #     """
    #     ビーム画像Surfaceを生成する
    #     引数 bird：ビームを放つこうかとん（Birdインスタンス）
    #     """
        self.img = pg.image.load(f"fig/beam.png") #     self.img = pg.画像のロード(f"fig/beam.png")
        self.rct = self.img.get_rect()  #self.rct = self.img.Rectの取得()
        self.rct.centery = bird.rct.centery #ビームの中心縦座標 = こうかとんの中心縦座標
        self.rct.left = bird.rct.right  #ビームの左座標 = こうかとんの右座標
        self.vx, self.vy = bird.directions
        self.speed = 5 #ビームスピード

        self.img0 = pg.image.load("fig/beam.png")
        angle = math.degrees(math.atan2(-self.vy, self.vx))  # 向きの角度（-vyに注意）
        self.img = pg.transform.rotozoom(self.img0, angle, 1.0)  # 角度に応じて回転

        self.rct = self.img.get_rect()
        # 初期配置をこうかとんの向きに合わせる
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx / 5
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy / 5

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    爆弾を打ち落とした数を記録して表示するクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)    # 青色
        self.score = 0  # スコアの初期値
        self.img = self.fonto.render(f"Score: {self.score}", True, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)    # 画面左下に配置

    def update(self, screen: pg.Surface):
        """
        スコアを更新して画面に描画する
        """
        self.img = self.fonto.render(f"Score: {self.score}", True, self.color)
        screen.blit(self.img, self.rct)

    def score_plus(self): 
        """
        scoreの加算
        """
        self.score += 1
    

class Explosion:
    """
    爆弾を撃ち落とした際にパーティクルを表示
    """
    def __init__(self, center: tuple[int, int]):
        self.imgs = [  
            pg.image.load("fig/explosion.gif"),
            pg.transform.flip(pg.image.load("fig/explosion.gif"), True, False)
        ]
        self.rct = self.imgs[0].get_rect()
        self.rct.center = center
        self.life = 20  #爆発時間
    
    def update(self, screen: pg.Surface):
        if self.life > 0:
            screen.blit(self.imgs[self.life // 10 % 2], self.rct)
            self.life -= 1


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bomb = Bomb((255, 0, 0), 10)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)] 
    score = Score()
    beam = None
    m_beams = []
    explosions = []
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                 beam = Beam(bird)
                 m_beams.append(Beam(bird))            
        screen.blit(bg_img, [0, 0])

        for bomb in bombs:
            for beam in m_beams:
                if bomb.rct.colliderect(beam.rct):
                    explosions.append(Explosion(bomb.rct.center))
                    bombs.remove(bomb)
                    m_beams.remove(beam)
                    score.score_plus()
                    break

            if bird.rct.colliderect(bomb.rct):
            # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH // 2 - 150, HEIGHT // 2])
                pg.display.update()
                time.sleep(1)
                return
            
                    
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        #beam.update(screen)   
        bombs = [bomb for bomb in bombs if bomb is not None]
        m_beams = [beam for beam in m_beams if beam is not None ]

        for bomb in bombs:
            bomb.update(screen)
        if beam is not None:
            beam.update(screen)
        for beam in m_beams:
            beam.update(screen)
        add_explosions = []
        for x in explosions:
            x.update(screen)
            if x.life > 0:
                add_explosions.append(x)
        explosions = add_explosions 
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50) 


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
