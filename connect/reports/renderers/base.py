from abc import ABCMeta, abstractmethod


class BaseRenderer(metaclass=ABCMeta):
    def __init__(
        self,
        environment,
        root_dir,
        account,
        report,
        template=None,
        args=None,
    ):
        self.environment = environment
        self.root_dir = root_dir
        self.account = account
        self.report = report
        self.template = template
        self.args = args or {}
        self.extra_context = None

    def get_context(self, data):
        context = {
            'account': self.account,
            'report': self.report,
            'data': data,
        }
        if self.extra_context:
            context['extra_context'] = self.extra_context
        return context

    def set_extra_context(self, data):
        self.extra_context = data

    @abstractmethod
    def render(self, data, output_file):
        raise NotImplementedError('Subclasses must implement the `render` method.')

    @classmethod
    def validate(cls, definition):
        return []
