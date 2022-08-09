#  Copyright © 2022 CloudBlue. All rights reserved.

class aiter:
    """
    Convert to async iterator.
    """
    def __init__(self, values):
        self._values = iter(values)

    async def __anext__(self):
        try:
            return next(self._values)
        except StopIteration:
            raise StopAsyncIteration

    def __aiter__(self):
        return self
