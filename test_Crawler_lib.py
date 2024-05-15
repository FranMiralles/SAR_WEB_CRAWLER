import json
from SAR_Crawler_lib import SAR_Wiki_Crawler

def main():
    # Inicializar el crawler
    crawler = SAR_Wiki_Crawler()

    # Definir la URL de prueba
    test_url = "https://es.wikipedia.org/wiki/Oric_1"

    # Obtener el contenido del artículo de Wikipedia
    content = crawler.get_wikipedia_entry_content(test_url)
    if content is None:
        print("No se pudo obtener el contenido del artículo.")
        return

    text, links = content

    # Parsear el contenido crudo
    parsed_content = crawler.parse_wikipedia_textual_content(text, test_url)
    if parsed_content is None:
        print("No se pudo parsear el contenido del artículo.")
        return

    # Convertir la salida parseada a JSON
    parsed_content_json = json.dumps(parsed_content, ensure_ascii=False, indent=2)

    # Salida esperada proporcionada por el profesor
    expected_output = {
        "url": "https://es.wikipedia.org/wiki/oric_1",
        "title": "Oric 1",
        "summary": " \n \n \n \n \n \n \nEl Oric 1 fue un ordenador doméstico fabricado por Tangerine Computer Systems mediante la creación de la compañía Oric Products International Ltd para competir con el Sinclair ZX Spectrum con un procesador 6502.",
        "sections": [
            {
                "name": "Índice",
                "text": "1 Datos técnicos\n2 Historia\n3 Referencias\n4 Fuente\n5 Enlaces externos",
                "subsections": []
            },
            {
                "name": "Datos técnicos",
                "text": "CPU Synertek SY6502A o Rockwell R6502AP (versiones licenciadas del MOS Technology 6502)[1]​ a 1 MHz\nROM 16 Kilobytes con un BASIC derivado del de Microsoft que incluye comandos de sonido. Puede ampliarse mediante ROMs externas, como la de la unidad de disco (con hardware capaz de conmutar su ROM con la del equipo)\nRAM 16 Kilobytes el modelo básico, 64 Kilobytes el resto. Aunque se anuncia de 48 Kb esto es debido a que la ROM oculta la parte alta de la memoria, pero al igual que en el Commodore 64 se puede acceder a todos los bancos de memoria mediante lenguaje ensamblador\nVRAM no tiene. La pantalla se direcciona en la RAM alta :\nTexto: 3B80-3FE0 en los 16 Kb, BB80-BFE0 en los 64 Kb\nHires: 2000-4000 en los 16 Kb, A000-BFE0 en los 64 Kb\nCarcasa pequeña, de 280 x 178 x 150 mm, en plástico blanco con fondo de teclado negro. Inclinada para facilitar la escritura. Hueco de altavoz en la parte inferior (los Oric, al revés que el resto, tienen la cara principal de la placa madre boca abajo). En la esquina superior derecha luce el logotipo que en los últimos modelos pasa a ser arco iris\nTeclado teclado tipo chiclet QWERTY de 57 teclas pero en lugar de las gomas del Spectrum usa barras de plástico más parecidas a las de una calculadora. No presentan TAB o CAPS LOCK (esta se ha asignado a CTRL-T). Teclas de cursor a ambos lados de la barra espaciadora.\nPantalla usa una ULA con 2 modos:\nModo texto de 40 x 28 con 8 colores. Set ASCII de 128 caracteres en matriz de 6 x 8 pixeles, redefinibles por soft. Fila superior no utilizada (normalmente usada por la ROM como línea de status). El atributo Serial de los caracteres de Teletexto se usa para seleccionar colores, parpadeo, caracteres de doble ancho, insertar fragmentos de gráficos modo texto, y seleccionar entre el set de caracteres estándar (ASCII), y el alternativo (caracteres semigráficos de Teletexto), en el que cada carácter representa una cadena de 2 x 3 PELs (bloques gráficos). Cada atributo serial ocupa el espacio de un carácter que no puede ser utilizado para nada más. Por ello, para cambiar a tinta amarilla sobre fondo azul, necesitamos 2 espacios. Esta es la mayor desventaja del ordenador.\nModo gráfico de 240 x 200 píxeles. 6 bits por pixel. Los atributos serial se utilizan también aquí (cada atributo ocupa hasta 6 por 1 píxeles). Tres líneas de texto en la zona inferior de la pantalla.\nSonido General Instrument AY-3-8912 con 3 canales de 8 octavas de sonido más uno de ruido blanco. Sonido Mono, con 16 niveles de volumen por el altavoz interno.\nSoporte interfaz de casete a 300 y 2400 baudios. Se planeó una unidad de disquete, pero la heredó su sucesor el Oric Atmos (puede usarse también).\nEntrada/Salida Visto por detrás, de izquierda a derecha\nConector de TV PAL (modulador de RF UHF)\nConector DIN 5 de Monitor RGB\nConector DIN 7 de Interfaz de casete a 300 baudios y 2400 baudios\nPuerto paralelo de impresora de 20 pines\nConector de BUS de 34 pines\nConector de alimentación DC 9 Voltios 600 mA (negativo fuera, positivo centro)\nAmpliaciones\nPlotter de 4 colores y 40 columnas\nUnidad de disco Oric de 3 pulgadas\nJasmin (una controladora alternativa de floppy para 1/Atmos)\nCumana Disk Interface\nPort MIDI\nInterfaz RS-232C (de MCP): se distribuye con el módem Telemod y soft para Prestel (Videotex en Inglaterra)\nInterfaz serie a 300 baudios de Kenema Associates\nOric V23 módem (V22/V23)\nVarias Interfaz de Joystick (por el puerto paralelo o el BUS)\nSintetizadores de voz",
                "subsections": []
            },
            {
                "name": "Historia",
                "text": "Tangerine produjo uno de los primeros ordenadores en kit basado en el 6502, el Tangerine Microtan 65, que tuvo bastante éxito. Tenía planes de producir un equipo de sobremesa orientado al mercado profesional, pero la empresa a quien lo encargó nunca lo acabó.\nCon el éxito del ZX Spectrum decide fabricar en su lugar un ordenador para competir en el incipiente mercado, pero escarmentada de la anterior, decide crear una subsidiaria, Oric Products International Ltd para desarrollar y comercializar el Oric-1 en 1983. Hereda bastantes cosas del Microtan, como el método de lectura del teclado y varias rutinas de la ROM\nSale a la venta a 129£ el modelo de 16 Kb y 169 £ el de 64 Kb, siendo este último más barato que el Spectrum por unas pocas libras. Aunque presenta el mismo problema de atributos (llamado colour clash en Inglaterra) que el Spectrum, al poder direccionar un color por línea en lugar de por matriz de 8x8 se ve menos afectado. Al incorporar una salida de monitor RGB, un chip de sonido y un mejor teclado sobrepasaba a aquél, pero su ROM era un hervidero de Bugs que dificultaban la programación de juegos comerciales, y sin ellos un ordenador doméstico estaba sentenciado. No obstante, se estima en unos 160.000 los Oric-1 vendidos en Gran Bretaña y 50.000 en Francia en 1983. Además se comercializó por toda Europa, con buenas ventas en España. No se llegó a los 350.000 previstos, pero fue suficiente para que Oric International fuera comprada por Edenspring con 4 millones de libras esterlinas.",
                "subsections": []
            },
            {
                "name": "Referencias",
                "text": "↑ Defence-Force tiene imágenes de las placas madre de los Oric/Pravetz",
                "subsections": []
            },
            {
                "name": "Fuente",
                "text": "La mayor parte de este artículo procede de El Museo de los 8 Bits bajo licencia Creative Commons Atribución 2.5",
                "subsections": []
            },
            {
                "name": "Enlaces externos",
                "text": "Oric.org Principal portal de los usuarios de Oric\nThe Oric FAQ sobre los Microtan 65, Oric 1, Oric Atmos & Stratos IQ164/Telestrat; website de James Groom\nDefence-Force: Oric Forums – The main Oric discussion forum\nLe monde Oric con un libro en línea sobre Oric\nOric Webring",
                "subsections": []
            }
        ]
    }

    expected_output_json = json.dumps(expected_output, ensure_ascii=False, indent=2)

    # Comparar la salida parseada con la salida esperada
    if parsed_content_json == expected_output_json:
        print("La salida generada coincide con la salida esperada.")
    else:
        print("La salida generada no coincide con la salida esperada.")
        print("\nSalida generada:\n", parsed_content_json)
        print("\nSalida esperada:\n", expected_output_json)

if __name__ == "__main__":
    main()
