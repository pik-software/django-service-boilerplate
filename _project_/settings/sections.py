import os

_current_dir = os.path.dirname(__file__)

SECTIONS = (
    'mezzanine',
)


class SectionInstallerInterface(object):
    @staticmethod
    def update_urls(urlpatterns):
        pass

    @staticmethod
    def update_settings(settings):
        pass


def update_settings(g):
    for x in SECTIONS:
        section_file = os.path.join(_current_dir, "section_" + x + ".py")
        with open(section_file) as f:
            section_code = f.read()

        exec(section_code)

        Installer.update_settings(g)


def update_urls(urlpatterns):
    for x in SECTIONS:
        section_file = os.path.join(_current_dir, "section_" + x + ".py")
        with open(section_file) as f:
            section_code = f.read()

        exec(section_code)

        Installer.update_urls(urlpatterns)
