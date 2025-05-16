
class ActionType:
    NONE = "NONE"
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    CLICK_AND_TYPE = "CLICK_AND_TYPE"
    DRAG_AND_DROP = "DRAG_AND_DROP"
    
    @staticmethod
    def from_string(name):
        name = name.upper()
        if name in (ActionType.CLICK, ActionType.DOUBLE_CLICK, ActionType.CLICK_AND_TYPE, ActionType.DRAG_AND_DROP):
            return name
        raise ValueError("Invalid action type: " + name)
    
    @staticmethod
    def is_valid_action(action):
        return action in [ActionType.CLICK, ActionType.DOUBLE_CLICK, ActionType.CLICK_AND_TYPE, ActionType.DRAG_AND_DROP]

    @staticmethod
    def requires_image(action):
        return action in [ActionType.CLICK, ActionType.DOUBLE_CLICK, ActionType.CLICK_AND_TYPE]

    @staticmethod
    def requires_drag_and_drop_images(action):
        return action == ActionType.DRAG_AND_DROP