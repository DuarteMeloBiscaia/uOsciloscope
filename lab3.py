import T_Display


# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

# Dimensions of the TFT display
tft_width = 240
tft_height = 135
tft = T_Display.TFT()

#Time and amplitude scales
time_range = [5, 10, 20, 50] # time scale in ms
time_start_scale = 10 # starting time
time_div = 10 # horizontal divisions

y_range = [1, 2, 5, 10] # amplitude scale in volts
y_start_scale = 5 
y_div = 6 




# ============================================================================
# CLASSES
# ============================================================================
class uOscilloscope:
    """Oscilloscope class for TFT display"""
    
    def time_display(self):
        pass
    
    def send_email(self):
        pass
    
    def write_to_display(self):
        pass
    
    def change_x_scale(self):
        pass
    
    def change_y_scale(self):
        pass
    
    def freq_display(self):
        pass




# ============================================================================
# select_button function
# ============================================================================
def select_button(osc):
    """Main event loop for the oscilloscope"""
    button_actions = {
        11: osc.time_display,          # Fast click button 1
        12: osc.send_email,            # Long click button 1
        13: osc.write_to_display,      # Double click button 1
        21: osc.change_x_scale,        # Fast click button 2
        22: osc.change_y_scale,        # Long click button 2
        23: osc.freq_display,          # Double click button 2
    }
    
    while tft.working():
        button = tft.readButton()
        if button != tft.NOTHING:
            print("Button pressed:", button)
        
        if button in button_actions:
            button_actions[button]()
        elif button != tft.NOTHING:
            print("Invalid button key")







# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    osc = uOscilloscope()
    select_button(osc)