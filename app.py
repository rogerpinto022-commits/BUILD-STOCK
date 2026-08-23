ent_anexa = df[df.LOCAL=="SALA ANEXA"]["ENTRADA"].sum()
sai_anexa = df[df.LOCAL=="SALA ANEXA"]["SAIDA"].sum()  # <-- TOTAL DE SAIDAS NA SALA ANEXA
ent_bar = df[df.LOCAL=="BARRACÃO"]["ENTRADA"].sum()
sai_bar = df[df.LOCAL=="BARRACÃO"]["SAIDA"].sum()
