import pik.utils.normalization


def normalize(text: str):
    """
    Text normalization.

    >>> normalize("ООО  'ВЫМПЕЛКОМ' ")
    "ООО 'ВЫМПЕЛКОМ'"
    >>> normalize('ЗАО "ЮВЕЛИРНЫЙ завод')
    'ЗАО "ЮВЕЛИРНЫЙ завод'

    :param text: some hand typed text
    :return: normalized text
    """
    return pik.utils.normalization.normalize(text)


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
    return pik.utils.normalization.company_name_normalization(name)
