# Импортируем модуль админки Django для настройки административного интерфейса
from django.contrib import admin
# Импортируем модель Post из текущего приложения
from .models import Comment, Post

# Используем декоратор для регистрации модели Post с настройками, определёнными в классе PostAdmin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):  # Создаём класс для кастомизации отображения модели в админке
    # Указываем поля, которые будут отображаться в списке объектов
    list_display = ['title', 'slug', 'author', 'publish', 'status']  # Поля: заголовок, слаг, автор, дата публикации, статус

    # Добавляем фильтры для боковой панели, чтобы можно было фильтровать записи по указанным полям
    list_filter = ['status', 'created', 'publish', 'author']  # Фильтры: статус, дата создания, дата публикации, автор

    # Указываем поля, по которым можно искать записи через строку поиска
    search_fields = ['title', 'body']  # Поля: заголовок и содержимое поста

    # Настраиваем автозаполнение поля `slug` на основе значения поля `title`
    prepopulated_fields = {'slug': ('title',)}  # Поле slug автоматически заполняется на основе title

    # Заменяем выпадающий список для поля `author` (ForeignKey) на виджет поиска
    raw_id_fields = ['author']  # Поле author становится удобным для поиска при большом количестве пользователей

    # Добавляем навигацию по дате публикации в виде временной шкалы
    date_hierarchy = 'publish'  # Навигация организована по полю publish (дата публикации)

    # Указываем порядок сортировки записей по умолчанию: сначала по статусу, затем по дате публикации
    ordering = ['status', 'publish']  # Поля: статус, затем дата публикации

    # Настраиваем отображение дополнительных элементов интерфейса
    show_facets = admin.ShowFacets.ALWAYS  # Всегда показывать дополнительные элементы интерфейса (если поддерживается версией Django)


    @admin.register(Comment)
    class CommentAdmin(admin.ModelAdmin):
        list_display = ['name', 'email', 'post', 'created', 'active']
        list_filter = ['active', 'created', 'updated']
        search_fields = ['name', 'email', 'body']
