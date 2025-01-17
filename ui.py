import pygame
import pygame_gui
import globals

def handle_ui_events(event, slider, textbox):
    if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and event.ui_element == slider:
        neuron_training_rate = event.value
        textbox.set_text(f"{neuron_training_rate:.3f}")
        return neuron_training_rate

    if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_element == textbox:
        try:
            new_value = float(event.text)
            if 0.001 <= new_value <= 0.1:
                slider.set_current_value(new_value)
                return new_value
            else:
                textbox.set_text(f"{slider.get_current_value():.3f}")
        except ValueError:
            textbox.set_text(f"{slider.get_current_value():.3f}")

    return None

def create_neuron_training_rate_slider(ui_manager):
    # Calculate positions
    slider_width = 150
    slider_height = 20
    textbox_width = 50
    textbox_height = 20
    margin_left = 20
    margin_bottom = 80

    # Create a label
    label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((margin_left, globals.window_size[1] - margin_bottom - slider_height - 30), (200, 30)),
        text="Training Rate",
        manager=ui_manager,
        object_id=pygame_gui.core.ObjectID(class_id="@labels", object_id="#neuron_rate_label")
    )

    # Create a slider
    slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((margin_left, globals.window_size[1] - margin_bottom - slider_height), (slider_width, slider_height)),
        start_value=globals.neuron_training_rate,
        value_range=(0.001, 0.1),
        manager=ui_manager
    )

    # Create a textbox
    textbox = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((margin_left + slider_width + 10, globals.window_size[1] - margin_bottom - textbox_height), (textbox_width, textbox_height)),
        manager=ui_manager
    )
    textbox.set_text(f"{slider.get_current_value():.3f}")

    return label, slider, textbox

def create_neuron_training_decay_ratio_slider(ui_manager):
    # Calculate positions
    slider_width = 150
    slider_height = 20
    textbox_width = 50
    textbox_height = 20
    margin_left = 20
    margin_bottom = 20

    # Create a label
    label1 = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((margin_left, globals.window_size[1] - margin_bottom - slider_height - 30), (200, 30)),
        text="Training Decay Ratio",
        manager=ui_manager,
        object_id=pygame_gui.core.ObjectID(class_id="@labels", object_id="#neuron_decay_ratio_label")
    )

    # Create a slider
    slider1 = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((margin_left, globals.window_size[1] - margin_bottom - slider_height), (slider_width, slider_height)),
        start_value=globals.neuron_training_decay_ratio,
        value_range=(30, 5),
        manager=ui_manager
    )

    # Create a textbox
    textbox1 = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((margin_left + slider_width + 10, globals.window_size[1] - margin_bottom - textbox_height), (textbox_width, textbox_height)),
        manager=ui_manager
    )
    textbox1.set_text(f"{slider1.get_current_value():.3f}")

    return label1, slider1, textbox1