from django.utils.text import slugify
import random
import string


def random_string_generator(size, chars=string.ascii_uppercase + string.digits):  # pragma: no cover
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):  # pragma: no cover
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    slug = slugify(instance.name)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new = f"{slug}-{random_string_generator(size=4)}"
        return new
    return slug


def unique_slug_generator_for_category(instance, new_slug=None):  # pragma: no cover
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name_en)

    slug = slugify(instance.name_en)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new = f"{slug}-{random_string_generator(size=4)}"
        return new
    return slug
