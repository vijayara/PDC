import zlib

s = """Le Lorem Ipsum est simplement du faux texte employé d
ans la composition et la mise en page avant impression. Le Lo
rem Ipsum est le faux texte standard de l'imprimerie depuis l
es années 1500, quand un peintre anonyme assembla ensemble de
s morceaux de texte pour réaliser un livre spécimen de police
s de texte. Il n'a pas fait que survivre cinq siècles, mais s
'est aussi adapté à la bureautique informatique, sans que so
n contenu n'en soit modifié. Il a été popularisé dans les ann
ées 1960 grâce à la vente de feuilles Letraset contenant des 
passages du Lorem Ipsum, et, plus récemment, par son inclusio
n dans des applications de mise en page de texte, comme Aldus PageMaker.
Cela est déoj dfslj asjdfl kahsjf fkeop asuio vvvoi opèsda"""


sb = s.encode("utf-8")
c = zlib.compress(sb, 9)
d = zlib.decompress(c)
s3 = d.decode("utf-8")
print("Initial size:\t", len(sb))
print("Compressed size:", len(c))
print(s3)
