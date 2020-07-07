

class Urban:
    """Holds definition of urban agent

    """

    def __init__(self, **kwargs):
        
        self.density = kwargs.get('density')

        assert(self.density == 0 or self.density == 1 or self.density == 2)
