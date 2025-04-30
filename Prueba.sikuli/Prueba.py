""" 
Forma 1
Funcional pero poco optimizado ya que tenemos que especificar por imágenes cada acción.
click("1746007244746.png")
click("1746007301522.png")
type("calc" + Key.ENTER)
wait("1746007614373.png")
click("1746007427159.png")
click("1746007528534.png")
click("1746007436875.png")
click("1746007544069.png")
click("1746007301522.png")
type("Me ahorro la rima :)")
"""

# Vamos a utilizar menos imágenes que en el apartado anterior. Para ello vamos a tomar como referencia la imagen de la calculadora completa
# y vamos a representar los clicks en las teclas necesarias como clicks con offsets.
click("1746007244746.png")
click("1746007301522.png")
type("calc" + Key.ENTER)
wait("1746007614373.png")
click(Pattern("1746007614373.png").similar(0.50).targetOffset(-4,159))
click(Pattern("1746007614373.png").similar(0.50).targetOffset(592,173))
click(Pattern("1746007614373.png").similar(0.50).targetOffset(304,158))
click(Pattern("1746007614373.png").similar(0.50).targetOffset(618,246))
click("1746007301522.png")
type("Me ahorro la rima :)")