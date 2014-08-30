from mezzanine.conf import settings
from modeltranslation.translator import translator, TranslationOptions
 
applications = settings.INSTALLED_APPS
 
class TranslatedSlugged(TranslationOptions):
    fields = ('title',)
 
class TranslatedDisplayable(TranslatedSlugged):
    fields = ('_meta_title', 'description')
 
class TranslatedBasePage(TranslatedDisplayable):
    fields = ('titles',)
 
class TranslatedRichText(TranslationOptions):
    fields = ('content',)
 
if "mezzanine.pages" in applications:
    from mezzanine.pages.models import RichTextPage, Page, Link
 
    class TranslatedPage(TranslatedBasePage):
        fields = ()
 
    class TranslatedRichTextPage(TranslatedRichText):
        fields = ()
 
    class TranslatedLink(TranslationOptions):
        fields = ()
 
    translator.register(Page, TranslatedPage)
    translator.register(RichTextPage, TranslatedRichTextPage)
    translator.register(Link, TranslatedLink)
 
if "mezzanine.galleries" in applications:
    from mezzanine.galleries.models import GalleryImage, Gallery
 
    class TranslatedGallery(TranslatedRichText):
        fields = ()
 
    class TranslatedGalleryImage(TranslationOptions):
        fields = ('description',)
 
    translator.register(Gallery, TranslatedGallery)
    translator.register(GalleryImage, TranslatedGalleryImage)
 
if "mezzanine.forms" in applications:
    from mezzanine.forms.models import Form, Field
 
    class TranslatedForm(TranslatedRichText):
        # fields = ('button_text', 'response', 'email_subject', 'email_message',)
        fields = ('button_text', 'response',)

    class TranslatedField(TranslationOptions):
        fields = ('label', 'choices', 'default', 'placeholder_text', 'help_text',)
 
    translator.register(Form, TranslatedForm)
    translator.register(Field, TranslatedField)
 
if "mezzanine.blog" in applications:
    from mezzanine.blog.models import BlogCategory, BlogPost
 
    class TranslatedBlogCategory(TranslatedSlugged):
        fields = ()
 
    class TranslatedBlogPost(TranslatedDisplayable, TranslatedRichText):
        fields = ()
 
    translator.register(BlogCategory, TranslatedBlogCategory)
    translator.register(BlogPost, TranslatedBlogPost)
 
# mezzanine.boot, mezzanine.conf, mezzanine.generic, mezzanine.accounts
# and mezzanine.mobile does not need translated models
 
# what about mezzanine.twitter ?
 
if "cartridge.shop" in applications:
    from cartridge.shop.models import Category, Product, ProductOption, ProductImage, ProductVariation
    from cartridge.shop.fields import OptionField
 
    class TranslatedProduct(TranslatedDisplayable, TranslatedRichText):
        fields = ()
 
    class TranslatedProductImage(TranslationOptions):
        fields = ('description',)
 
    class TranslatedProductOption(TranslationOptions):
        fields = ('name',)
 
    class TranslatedProductVariation(TranslationOptions):
        fields = tuple(('option%s' % opt[0] for opt in settings.SHOP_OPTION_TYPE_CHOICES))
 
    @classmethod
    def no_translated_option_fields(cls):
        """
        Returns each of the model fields that are dynamically created
        from ``SHOP_OPTION_TYPE_CHOICES`` in
        ``ProductVariationMetaclass``. Excludes translation fields added
        by ``TranslatedProductVariation``.
        """
        all_fields = cls._meta.fields
        all_codes = [code for code, _ in settings.LANGUAGES]
        return [f for f in all_fields if isinstance(f, OptionField) and f.name.split('_')[-1] not in all_codes]
    # Fix form creation for the admin
    ProductVariation.option_fields = no_translated_option_fields
 
    class TranslatedCategory(TranslatedRichText):
        fields = ()
 
    translator.register(Category, TranslatedCategory)
    translator.register(Product, TranslatedProduct)
    translator.register(ProductImage, TranslatedProductImage)
    translator.register(ProductOption, TranslatedProductOption)
    translator.register(ProductVariation, TranslatedProductVariation)
