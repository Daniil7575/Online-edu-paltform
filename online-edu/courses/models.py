from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .fields import OrderField


class Subject(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self) -> str:
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User,
                              verbose_name='Преподаватель',
                              on_delete=models.CASCADE,
                              related_name='courses')
    subject = models.ForeignKey(Subject,
                                verbose_name='Предмет',
                                on_delete=models.CASCADE,
                                related_name='courses')
    title = models.CharField(max_length=200, verbose_name='Наименование курса')
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField(verbose_name='Описание')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self) -> str:
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE,
                               verbose_name='Курс')
    title = models.CharField(max_length=200, verbose_name='Название модуля')
    description = models.TextField(blank=True, verbose_name='Описание модуля')
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': (
                                                            'text',
                                                            'video',
                                                            'image',
                                                            'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']
        verbose_name = verbose_name_plural = 'Контент'


class ItemBase(models.Model):
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE,
                              verbose_name='Преподаватель')
    title = models.CharField(max_length=250, verbose_name='Название')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True,
                                   verbose_name='Дата изменения')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField(verbose_name='Содержание')

    class Meta:
        verbose_name = 'Текст'
        verbose_name_plural = 'Тексты'


class File(ItemBase):
    file = models.FileField(upload_to='files', verbose_name='Путь до файла')

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'


class Image(ItemBase):
    file = models.FileField(upload_to='images',
                            verbose_name='Путь до картинки')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class Video(ItemBase):
    url = models.URLField(verbose_name='Ссылка на видео')

    class Meta:
        verbose_name = verbose_name_plural = 'Видео'
