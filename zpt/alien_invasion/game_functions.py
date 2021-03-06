import sys
import pygame
from time import sleep
from bullet import Bullet
from alien import Alien

def check_keydown_events(event,ai_settings,screen,ship,bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)
    elif event.key == pygame.K_q:
        sys.exit()

def check_keyup_events(event,ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False    

def fire_bullet(ai_settings,screen,ship,bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

def check_events(ai_settings,stats,screen,play_button,ship,bullets):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(stats,play_button,mouse_x,mouse_y)

def check_play_button(stats,play_button,mouse_x,mouse_y):
    """点击play开始新游戏"""
    if play_button.rect.collidepoint(mouse_x,mouse_y):
        stats.game_active = True

def update_screen(ai_settings,screen,stats,ship,aliens,bullets,
    play_button):
    """更新屏幕上的图像，并切换到新屏幕"""
    #每次循环都重绘屏幕
    screen.fill(ai_settings.bg_color)

    #重绘子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    if not stats.game_active:
        #如果非活动状态，展示play
        play_button.draw_button()

    pygame.display.flip()

def update_bullets(ai_settings,screen,ship,aliens,bullets):
    """更新子弹的位置，删除已消失的子弹"""
    #更新位置
    bullets.update()

    #删除子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom<=0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings,screen,ship,aliens,bullets)


def check_bullet_alien_collisions(ai_settings,screen,ship,aliens,bullets):
    """相应子弹和外星人的碰撞"""
    #检查是否有子弹击中了外星人
    #如果击中了，删除子弹和外星人
    #两个True分别是子弹和外星人是否删除的标志
    collisions = pygame.sprite.groupcollide(bullets,aliens,False,True)
    if len(aliens) == 0:
        #删除现有子弹并新建一群外星人
        # bullets.empty()
        create_fleet(ai_settings,screen,ship,aliens)

def get_number_aliens_x(ai_settings,alien_width):
    """计算每行可容纳多少个外星人"""
    available_space_x = ai_settings.screen_width -  2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    """创建一个外星人并将其放至当前行"""
    alien = Alien(ai_settings,screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def create_fleet(ai_settings,screen,ship,aliens):
    """创建外星人群"""
    #创建一个外星人，并计算可以容纳多少外星人
    #外星人间距为外星人宽度
    alien = Alien(ai_settings,screen)
    number_aliens_x = get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows = get_number_rows(ai_settings,ship.rect.height,alien.rect.height)
    
    #创建第一行外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)

def get_number_rows(ai_settings,ship_height,alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height - 
                            (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def check_fleet_edges(ai_settings,aliens):
    """有外星人到达边缘时采取相应措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    """将整群外星人下降，并改变他们方向"""
    for alien in aliens.sprites():
        alien.rect.y = alien.rect.y + ai_settings.fleet_drop_speed
        # print(y)
        # alien.rect.y = y
    ai_settings.fleet_direction *= -1

def update_aliens(ai_settings,stats,screen,ship,aliens,bullets):
    """检查是否有外星人位于屏幕边缘，并更新整群外星人位置"""
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    #检测外星人与飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings,stats,screen,ship,aliens,bullets)

    #检测外星人是否触及底端
    check_alines_bottom(ai_settings,stats,screen,ship,aliens,bullets)

def ship_hit(ai_settings,stats,screen,ship,aliens,bullets):
    """响应被外星人撞到的飞船"""
    #将ship_left减一
    stats.ships_left -= 1

    #清空子弹和外星人列表
    aliens.empty()
    bullets.empty()

    if stats.ships_left > 0:
        #创建一群新的外星人，并将飞船放到屏幕底端中央
        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()
        #暂停
        sleep(0.5)
    else:
        stats.game_active = False

def check_alines_bottom(ai_settings,stats,screen,ship,aliens,bullets):
    """检查是否有外星人到达底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            #像飞船被撞到一样处理
            ship_hit(ai_settings,stats,screen,ship,aliens,bullets)
            break
    