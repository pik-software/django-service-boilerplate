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
        I = __import__(".section_" + x).Installer
        I.update_settings(g)

