from pygame.image import load
from pathlib import Path 

def load_sprite(name, with_alpha=True, endung = ".png"):
    filename = Path(__file__).parent / Path("assets/sprites/" + name + endung)
    sprite = load(filename.resolve())

    if with_alpha:
        return sprite.convert_alpha()
    
    return sprite.convert()