class StateResetMethod:
    RELAUNCH = "relaunch"
    INTERNAL_RESET = "internal_reset"

    @classmethod
    def values(cls):
        return [cls.RELAUNCH, cls.INTERNAL_RESET]