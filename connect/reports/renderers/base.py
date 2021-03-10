from abc import ABCMeta, abstractmethod


class BaseRenderer(metaclass=ABCMeta):
    def __init__(
        self,
        environment,
        root_dir,
        account,
        report,
        template=None,
        kwargs=None,
    ):
        self.environment = environment
        self.root_dir = root_dir
        self.account = account
        self.report = report
        self.template = template
        self.kwargs = kwargs or {}

    def get_context(self, data):
        return {
            'account': self.account,
            'report': self.report,
            'data': data,
        }

    @abstractmethod
    def render(self, data, output_file):
        raise NotImplementedError('Subclasses must implement the `render` method.')

    @classmethod
    def validate(cls, definition):
        return []
