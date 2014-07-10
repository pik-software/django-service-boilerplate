import os

_current_dir = os.path.dirname(__file__)

SECTIONS = (
    'mezzanine',
)


class SectionInterface:
    @staticmethod
    def make_urls():
        raise NotImplemented

    @staticmethod
    def update_settings(settings):
        pass


def loader(g):
    for x in SECTIONS:
        section_file = os.path.join(_current_dir, "section_" + x + ".py")
        with open(section_file) as f:
            section_code = f.read()

        exec(section_code)

        Installer.update_settings(g)

