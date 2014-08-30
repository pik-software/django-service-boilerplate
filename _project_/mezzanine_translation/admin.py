from copy import deepcopy
from django.contrib import admin
from django.utils.translation import activate, get_language
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.conf import settings

applications = settings.INSTALLED_APPS


def save_obj_for_every_language(obj):
    """
    When ``Displayable`` are saved, they auto-populate some fields.
    Do it for every languages.
    """
    lang = get_language()
    for code, _ in settings.LANGUAGES:
        try:
            activate(code)
        except:
            pass
        else:
            obj.save()
    activate(lang)


if "mezzanine.pages" in applications:
    from mezzanine.pages.models import Page, Link, RichTextPage
    from mezzanine.pages.admin import PageAdmin, LinkAdmin

    class TranslatedPageAdmin(PageAdmin, TranslationAdmin):
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_model(self, request, obj, form, change):
            super(TranslatedPageAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    # Avoid 'content' fields to be displayed twice
    richtextpage_fieldsets = deepcopy(PageAdmin.fieldsets)
    richtextpage_fieldsets[0][1]["fields"].insert(3, "content")
    class TranslatedRichTextPageAdmin(TranslatedPageAdmin):
        fieldsets = richtextpage_fieldsets

    class TranslatedLinkAdmin(LinkAdmin, TranslationAdmin):
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedLinkAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_model(self, request, obj, form, change):
            super(TranslatedLinkAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    admin.site.unregister(Page)
    admin.site.unregister(RichTextPage)
    admin.site.unregister(Link)
    admin.site.register(Page, TranslatedPageAdmin)
    admin.site.register(RichTextPage, TranslatedRichTextPageAdmin)
    admin.site.register(Link, TranslatedLinkAdmin)

if "mezzanine.galleries" in applications:
    from mezzanine.galleries.models import Gallery, GalleryImage
    from mezzanine.galleries.admin import GalleryAdmin, GalleryImageInline

    # If no inline class, the original 'description' field is still displayed
    class TranslatedGalleryImageInline(GalleryImageInline, TranslationTabularInline):
        # If no fieldsets, the translated 'description' fields are displayed twice
        fieldsets = ((None, {"fields": ('file', 'description')}),)

    # Avoid 'content' fields to be displayed twice
    gallery_fieldsets = deepcopy(GalleryAdmin.fieldsets)
    gallery_fieldsets[0][1]["fields"].insert(3, "content")
    class TranslatedGalleryAdmin(GalleryAdmin, TranslationAdmin):
        fieldsets = gallery_fieldsets
        inlines = (TranslatedGalleryImageInline,)

        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedGalleryAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_model(self, request, obj, form, change):
            super(TranslatedGalleryAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    admin.site.unregister(Gallery)
    admin.site.register(Gallery, TranslatedGalleryAdmin)

if "mezzanine.forms" in applications:
    from mezzanine.forms.models import Form
    from mezzanine.forms.admin import FormAdmin, FieldAdmin

    # Same as GalleryImageInline
    field_fieldsets = ((None, {"fields": ['label', 'field_type', 'required', 'visible', 'choices', 'default', 'help_text']}),)
    if settings.FORMS_USE_HTML5:
        field_fieldsets[0][1]["fields"].insert(6, 'placeholder_text')
    class TranslatedFieldInline(FieldAdmin, TranslationTabularInline):
        fieldsets = field_fieldsets

    class TranslatedFormAdmin(FormAdmin, TranslationAdmin):
        inlines = (TranslatedFieldInline,)

        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedFormAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_model(self, request, obj, form, change):
            super(TranslatedFormAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    admin.site.unregister(Form)
    admin.site.register(Form, TranslatedFormAdmin)

if "mezzanine.blog" in applications:
    from mezzanine.blog.models import BlogPost, BlogCategory
    from mezzanine.blog.admin import BlogPostAdmin, BlogCategoryAdmin

    class TranslatedBlogPostAdmin(BlogPostAdmin, TranslationAdmin):
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedBlogPostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_model(self, request, obj, form, change):
            super(TranslatedBlogPostAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    class TranslatedBlogCategoryAdmin(BlogCategoryAdmin, TranslationAdmin):
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedBlogCategoryAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

    admin.site.unregister(BlogPost)
    admin.site.unregister(BlogCategory)
    admin.site.register(BlogPost, TranslatedBlogPostAdmin)
    admin.site.register(BlogCategory, TranslatedBlogCategoryAdmin)

if "cartridge.shop" in applications:
    from cartridge.shop.models import Category, Product, ProductOption, ProductImage, ProductVariation
    from cartridge.shop.admin import CategoryAdmin, ProductAdmin, ProductOptionAdmin, ProductImageAdmin, option_fields
    from mezzanine.core.models import CONTENT_STATUS_DRAFT

    class TranslatedCategoryAdmin(CategoryAdmin, TranslationAdmin):
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedCategoryAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_model(self, request, obj, form, change):
            super(TranslatedCategoryAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    class TranslatedOptionAdmin(ProductOptionAdmin, TranslationAdmin):
        pass

    class TranslatedProductImageInline(ProductImageAdmin, TranslationTabularInline):
        fieldsets = ((None, {"fields": ('file', 'description',)}),)

    class TranslatedProductAdmin(ProductAdmin, TranslationAdmin):
        inlines = (TranslatedProductImageInline,) + deepcopy(ProductAdmin.inlines[1:])

        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(TranslatedProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            self.patch_translation_field(db_field, field, **kwargs)
            return field

        def save_formset(self, request, form, formset, change):
            """
            Add an additionnal pass to save every translated fields from
            ``ProdcutOption`` into the required ``ProductVariation``.
            """
            super(TranslatedProductAdmin, self).save_formset(request, form, formset, change)
            if formset.model == ProductVariation:
                for option_name in option_fields:
                    for option_value in request.POST.getlist(option_name):
                        # Option name is declared as "option%s" % type
                        option_model = ProductOption.objects.get(type=option_name[6:], name=option_value)
                        for var in eval('self._product.variations.filter('+option_name+'="'+option_value+'")'):
                            for code, _ in settings.LANGUAGES:
                                exec("var."+option_name+"_"+code+" = option_model.name_"+code)
                            var.save()

        def save_model(self, request, obj, form, change):
            super(TranslatedProductAdmin, self).save_model(request, obj, form, change)
            save_obj_for_every_language(obj)

    admin.site.unregister(Category)
    admin.site.unregister(Product)
    admin.site.unregister(ProductOption)
    admin.site.register(Category, TranslatedCategoryAdmin)
    admin.site.register(Product, TranslatedProductAdmin)
    admin.site.register(ProductOption, TranslatedOptionAdmin)
