class StateResetMethod:
    NONE = "none"
    COPY_RESET = "copy_reset"
    EXTERNAL_RESET = "external_reset"

    @classmethod
    def values(cls):
        return [cls.NONE, cls.COPY_RESET, cls.EXTERNAL_RESET]