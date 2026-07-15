"""Genera un icono .ico de Call of Duty para el .exe"""
try:
    from PIL import Image, ImageDraw, ImageFont
    img=Image.new("RGBA",(256,256),(0,0,0,0))
    d=ImageDraw.Draw(img)
    d.rectangle((0,0,256,256),fill="#1a1a2e")
    # Circulo naranja
    d.ellipse((28,28,228,228),fill="#ff6600")
    d.ellipse((38,38,218,218),fill="#1a1a2e")
    # Texto "COD"
    try:
        f=ImageFont.truetype("arialbd.ttf",80)
    except:
        f=ImageFont.load_default()
    d.text((128,90),"COD",fill="#ff6600",font=f,anchor="mt")
    d.text((128,160),"BLACK OPS VI",fill="#ffffff",font=ImageFont.load_default(),anchor="mt")
    img.save("cod_icon.ico",format="ICO",sizes=[(256,256)])
    print("[OK] Icono generado: cod_icon.ico")
except ImportError:
    print("[!] Necesitas Pillow: py -3.13 -m pip install pillow")
except Exception as e:
    print(f"[!] Error: {e}")
