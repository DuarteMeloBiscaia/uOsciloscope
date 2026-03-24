import T_Display

# Programa principal (main)
tft = T_Display.TFT()                             # Instancia um objeto da classe TFT

# Lê 100 amostras e calcula a média
pontos_adc = tft.read_adc(100, 200)              # Lê 100 pontos do ADC em 200ms
adc_med = sum(pontos_adc) / 100                   # Média dos 100 valores ADC
Vmed = 0.00044028 * adc_med + 0.091455            # Converte média ADC em Volt

str1 = "Vmed = %.5f" % Vmed

tft.display_set(tft.BLACK, 0, 0, 240, 135)        # Apaga display
tft.display_write_str(tft.Arial16, str1, 10, 20)  # Escreve média no display
tft.set_wifi_icon(0, 135-16)

while tft.working():
    but = tft.readButton()
    if but != tft.NOTHING:
        print("Button pressed:", but)
