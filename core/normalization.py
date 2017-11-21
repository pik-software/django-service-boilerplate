import re
from cucco import Cucco

_CUCCO = Cucco()


def normalize(text: str):
    """
    Text normalization.

    >>> normalize("ООО  'ВЫМПЕЛКОМ' ")
    "ООО 'ВЫМПЕЛКОМ'"
    >>> normalize('ЗАО "ЮВЕЛИРНЫЙ завод')
    'ЗАО "ЮВЕЛИРНЫИ завод'

    :param text: some hand typed text
    :return: normalized text
    """
    return _CUCCO.normalize(text, [
        'remove_extra_white_spaces', 'remove_accent_marks',
        'replace_emojis', 'replace_symbols',
    ])


def company_name_normalization(name: str):
    """
    Company name normalization

    >>> company_name_normalization("ООО  'ВЫМПЕЛКОМ' ")
    'ООО ВЫМПЕЛКОМ'
    >>> company_name_normalization('ЗАО "ЮВЕЛИРНЫЙ завод')
    'ЗАО ЮВЕЛИРНЫИ ЗАВОД'
    >>> company_name_normalization('ООО ПИК-Комфорт')
    'ООО ПИК-КОМФОРТ'
    >>> company_name_normalization('ООО ПИК\u2015Комфорт')
    'ООО ПИК-КОМФОРТ'
    >>> company_name_normalization('ООО ПИК - Комфорт')
    'ООО ПИК-КОМФОРТ'
    >>> company_name_normalization('ООО ПИК - - Комфорт')
    'ООО ПИК-КОМФОРТ'
    >>> company_name_normalization('ZAO “Interfax”')
    'ЗАО INTERFAX'

    :param name: company name
    :return: normalized company name
    """
    name = normalize(name)
    name = _CUCCO.replace_punctuation(name, excluded='-')
    name = re.sub(r'[\u2010-\u2017]', '-', name)
    name = re.sub(r'\s*-\s*', '-', name)
    name = re.sub(r'[-]+', '-', name)
    name = ' '.join(re.findall(r'[\w-]+', name))
    name = name.replace('IP ', 'ИП ')  # Individual entrepreneur
    name = name.replace('OOO ', 'ООО ')  # Limited liability company
    name = name.replace('ZAO ', 'ЗАО ')  # Private joint-stock company
    name = name.replace('ANO ', 'АНО ')  # Autonomous non-profit organization
    name = name.replace('GP ', 'ГП ')  # Unitary state enterprise
    name = name.replace('GUP ', 'ГУП ')  # Unitary state enterprise
    name = name.replace('PK ', 'ПК ')  # Production Cooperative
    name = name.replace('PP ', 'ПП ')  # Political party
    return name.upper()
