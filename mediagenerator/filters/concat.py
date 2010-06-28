from mediagenerator.base import Filter

class ConcatFilter(Filter):
    """
    Simply concatenates multiple files into a single file.

    This is also the default root filter.
    """
    def get_output(self, variation):
        yield '\n\n'.join(input for input in self.get_input(variation))
