from pathlib import Path
from svg2gakko.parser import svg2base64gakko

print(svg2base64gakko(Path("data/example.svg")))
