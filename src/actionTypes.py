
class ActionType:
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    CLICK_AND_TYPE = "CLICK_AND_TYPE"
    DRAG_AND_DROP = "DRAG_AND_DROP"
    TYPE = "TYPE"
    
    @staticmethod
    def from_string(name):
        name = name.upper()
        if name in (ActionType.CLICK, ActionType.DOUBLE_CLICK, ActionType.CLICK_AND_TYPE, ActionType.DRAG_AND_DROP, ActionType.TYPE):
            return name
        raise ValueError("Invalid action type: " + name)