from django.urls import path
from .views import PostListView, post_comment, post_detail, post_share


app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view() , name='post_list'),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:post>/',
        post_detail,
        name='post_detail'
    ),
    path('<int:post_id>/share/', post_share, name='post_share'),
    path(
        '<int:post_id>/comment/', post_comment, name='post_comment'
    ),
]