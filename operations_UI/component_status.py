class ComponentsSet:

    @classmethod
    def led_control(cls,ui,status):
        # lighter set --slider
        # ui.widget_19.setEnabled(status)
        pass
    
    @classmethod
    def laser_radar(cls,ui,status):
        ui.radar_button.setEnabled(status)
    
    @classmethod
    def basic_control(cls,ui,status):
        ui.widget_8.setEnabled(status)

    @classmethod
    def map_nav(cls,ui,status):

        ui.save_map_button.setEnabled(status)
        ui.widget_13.setEnabled(status)

    
    @classmethod
    def testing(cls,ui,status):
        ui.widget_24.setEnabled(status)
    


    @classmethod
    def radar_open_close(cls,ui,status):
        ComponentsSet.led_control(ui, status)
        ComponentsSet.testing(ui, status)
    


    @classmethod
    def testing_open_close(cls,ui,status):
        print("in testing set")
        ComponentsSet.laser_radar(ui, status)
        ComponentsSet.basic_control(ui, status)
        ComponentsSet.map_nav(ui, status)
        ComponentsSet.led_control(ui, status)
    

