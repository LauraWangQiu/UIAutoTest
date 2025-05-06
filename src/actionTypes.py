
class ActionType:
    CLICK = "CLICK"
    CLICK_AND_TYPE = "CLICK_AND_TYPE"
    TYPE = "TYPE"
    
    @staticmethod
    def from_string(name):
        name = name.upper()
        if name in (ActionType.CLICK, ActionType.CLICK_AND_TYPE, ActionType.TYPE):
            return name
        raise ValueError("Invalid action type: " + name)