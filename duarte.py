# main.py — μOscilloscope
# LAB3b · Sistemas Eletrónicos · IST Lisboa · 2025/2026

import T_Display
import math
import gc

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
NPOINTS    = 240           # Samples per acquisition
GRID_W     = 240           # Display width  [px]
GRID_H     = 119           # Grid height = 135 - 16 px text strip
FATOR      = 1.0 / 29.3   # Resistive divider gain (Scale 2: Q1 on, Q2 off)
TEXT_Y     = GRID_H        # Bottom y of the top 16 px text strip (= 119)

# ADC transfer function:  V_ADC = ADC_A × D + ADC_B
ADC_A = 0.00044028
ADC_B = 0.091455

# Vertical scale steps [V/div]  — index 0 is the smallest
V_SCALES = [1, 2, 5, 10]
V_IDX    = 2               # default → 5 V/div

# Horizontal scale steps [ms/div] and matching read_adc total intervals [ms]
T_SCALES    = [5, 10, 20, 50]
T_INTERVALS = [50, 100, 200, 500]
T_IDX       = 1            # default → 10 ms/div

# E-mail recipient for the Button-1-Long send action
EMAIL = "duartembiscaia@tecnico.ulisboa.pt"

# ─────────────────────────────────────────────
# Runtime state
# ─────────────────────────────────────────────
pontos_volt  = [0.0] * NPOINTS   # Last acquired waveform [V]
in_freq_mode = False              # True while the spectrum view is active

# ─────────────────────────────────────────────
# ADC raw value → signal voltage at J3 input
# ─────────────────────────────────────────────
def adc_to_volt(d):
    """Convert a 12-bit ADC reading to the physical input voltage."""
    v_adc = ADC_A * d + ADC_B    # voltage at the ESP32 ADC pin
    return (v_adc - 1.0) / FATOR # remove 1 V DC offset; undo resistive divider

# ─────────────────────────────────────────────
# Acquire NPOINTS samples from the ADC
# ─────────────────────────────────────────────
def read_signal():
    global pontos_volt
    raw = tft.read_adc(NPOINTS, T_INTERVALS[T_IDX])
    for n in range(NPOINTS):
        pontos_volt[n] = adc_to_volt(raw[n])
    del raw
    gc.collect()

# ─────────────────────────────────────────────
# Waveform statistics
# ─────────────────────────────────────────────
def calc_stats():
    """Return (Vmax, Vmin, Vav, Vrms) of the last acquired waveform."""
    vmax = vmin = pontos_volt[0]
    s = s2 = 0.0
    for v in pontos_volt:
        if v > vmax: vmax = v
        if v < vmin: vmin = v
        s  += v
        s2 += v * v
    return vmax, vmin, s / NPOINTS, math.sqrt(s2 / NPOINTS)

# ─────────────────────────────────────────────
# Voltage → grid y pixel  (y = 0 at grid bottom)
# ─────────────────────────────────────────────
def volt_to_y(v, v_scale, freq_mode=False):
    """Map a voltage to a y pixel within the grid area."""
    ppd = GRID_H / 6.0                              # pixels per division
    if freq_mode:
        # Spectrum: 0 V at bottom, 6·v_scale at top (all positive)
        y = int(round(v / v_scale * ppd))
    else:
        # Waveform: 0 V at vertical centre
        y = int(round(GRID_H / 2.0 + v / v_scale * ppd))
    if y < 0:          return 0
    if y > GRID_H - 1: return GRID_H - 1
    return y

# ─────────────────────────────────────────────
# Draw grid, scale labels, and WiFi icon
# ─────────────────────────────────────────────
def draw_info():
    vs = V_SCALES[V_IDX]
    ts = T_SCALES[T_IDX]

    if not in_freq_mode:
        # Time domain — 10×6 grid WITH centre lines
        tft.display_write_grid(0, 0, GRID_W, GRID_H, 10, 6, True,
                               tft.GREY1, tft.GREY2)
        tft.display_write_str(tft.Arial16, "%dV/"  % vs, 2,  TEXT_Y)
        tft.display_write_str(tft.Arial16, "%dms/" % ts, 80, TEXT_Y)
    else:
        # Frequency domain — 10×6 grid WITHOUT centre lines
        fvs    = vs / 2.0                                    # V/div for spectrum
        fs     = NPOINTS / (T_INTERVALS[T_IDX] / 1000.0)   # sampling frequency [Hz]
        hz_div = fs / 2.0 / 10.0                             # Hz per horizontal division
        tft.display_write_grid(0, 0, GRID_W, GRID_H, 10, 6, False,
                               tft.GREY1, tft.GREY2)
        sv = ("%.1fV/" % fvs) if fvs < 1.0 else ("%gV/" % fvs)
        tft.display_write_str(tft.Arial16, sv,               2,  TEXT_Y)
        tft.display_write_str(tft.Arial16, "%gHz/" % hz_div, 80, TEXT_Y)

    tft.set_wifi_icon(224, 119)    # top-right corner (224 = 240-16, 119 = 135-16)

# ─────────────────────────────────────────────
# Plot waveform in yellow (time domain)
# ─────────────────────────────────────────────
def draw_waveform():
    vs     = V_SCALES[V_IDX]
    x_list = [n for n in range(NPOINTS)]
    y_list = [volt_to_y(pontos_volt[n], vs) for n in range(NPOINTS)]
    tft.display_nline(tft.YELLOW, x_list, y_list)   # connected line segments
    del x_list, y_list
    gc.collect()

# ─────────────────────────────────────────────
# Compute DFT and draw one-sided spectrum (frequency domain)
# ─────────────────────────────────────────────
def draw_spectrum():
    global in_freq_mode
    in_freq_mode = True

    # Redraw display with frequency-domain grid and labels
    tft.display_set(tft.BLACK, 0, 0, GRID_W, 135)
    draw_info()

    fvs    = V_SCALES[V_IDX] / 2.0   # vertical scale for spectrum [V/div]
    N      = NPOINTS                  # 240
    half_N = N // 2                   # 120 DFT bins to display (k = 0…119)

    # Compute one DFT bin at a time and draw it as a vertical bar.
    # Each bin k occupies pixel columns 2k and 2k+1 (bins are paired).
    # Xss_k: one-sided amplitude spectrum normalised to physical units.
    for k in range(half_N):
        re = im = 0.0
        step = 2.0 * math.pi * k / N
        for n in range(N):
            a   = step * n
            re += pontos_volt[n] * math.cos(a)
            im -= pontos_volt[n] * math.sin(a)

        mag = math.sqrt(re * re + im * im)
        xss = mag / N if k == 0 else 2.0 * mag / N   # DC: /N, AC: 2/N

        y = volt_to_y(xss, fvs, freq_mode=True)
        if y > 0:
            tft.display_set(tft.CYAN, 2 * k, 0, 2, y)  # vertical bar, 2 px wide

    gc.collect()

# ─────────────────────────────────────────────
# Send waveform data and statistics by e-mail
# ─────────────────────────────────────────────
def send_data_email():
    vmax, vmin, vav, vrms = calc_stats()
    dt    = (T_INTERVALS[T_IDX] / 1000.0) / NPOINTS   # time step [s]
    corpo = ("Vmax = %.4f V\nVmin = %.4f V\n"
             "Vav  = %.4f V\nVrms = %.4f V") % (vmax, vmin, vav, vrms)
    tft.send_mail(dt, pontos_volt, corpo, EMAIL)

# ─────────────────────────────────────────────
# Full oscilloscope cycle  (Steps 1 → 2 → 3)
# ─────────────────────────────────────────────
def oscilloscope_cycle():
    global in_freq_mode
    in_freq_mode = False
    tft.display_set(tft.BLACK, 0, 0, GRID_W, 135)   # Step 1: clear display
    draw_info()                                        # Step 2: grid + labels
    read_signal()                                      # Step 3a: acquire from ADC
    draw_waveform()                                    # Step 3b: plot waveform

# ─────────────────────────────────────────────
# Initialise display and run first acquisition
# ─────────────────────────────────────────────
tft = T_Display.TFT()
oscilloscope_cycle()

# ─────────────────────────────────────────────
# Step 4: Main event loop
# ─────────────────────────────────────────────
while tft.working():
    but = tft.readButton()

    if   but == tft.NOTHING:
        continue

    elif but == tft.BUTTON1_SHORT:    # 4.1 – new time-domain acquisition + plot
        oscilloscope_cycle()

    elif but == tft.BUTTON1_LONG:     # 4.2 – send waveform + stats by e-mail
        send_data_email()

    elif but == tft.BUTTON2_SHORT:    # 4.3 – cycle vertical scale upward (circular)
        V_IDX = (V_IDX + 1) % len(V_SCALES)
        oscilloscope_cycle()

    elif but == tft.BUTTON2_LONG:     # 4.4 – cycle horizontal scale upward (circular)
        T_IDX = (T_IDX + 1) % len(T_SCALES)
        oscilloscope_cycle()

    elif but == tft.BUTTON2_DCLICK:   # 4.5 – compute DFT and show spectrum
        draw_spectrum()
