from deprecated import deprecated
import pik.utils.normalization


@deprecated('use pik.utils.normalization.normalize() instead')
def normalize(text: str):
    return pik.utils.normalization.normalize(text)


@deprecated('use pik.utils.normalization.company_name_normalization() instead')
def company_name_normalization(name: str):
    return pik.utils.normalization.company_name_normalization(name)
