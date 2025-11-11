import pygame

class Visualizer:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((760, 520))
        pygame.display.set_caption("Learn2Slither")
        running = True

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # fill the screen with a color to wipe away anything from last frame
            screen.fill("purple")

            pygame.draw.rect(screen, "red", pygame.Rect(screen.get_width() / 2, screen.get_height() / 2, 20, 20))

            # flip() the display to put your work on screen
            pygame.display.flip()

        pygame.quit()