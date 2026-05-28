from django.urls import path
from snippets import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'Snippets'

urlpatterns = [
    path("snippets/", views.snippet_list),
    path("snippets/<int:pk>/", views.snippet_detail),

    path("snippets1/", views.SnippetList.as_view()),
    path("snippets1/<int:pk>", views.SnippetDetail.as_view()),
    # 使用 Mixin 混合类 组合视图
    path("snippets2/", views.SnippetList1.as_view()),
    path("snippets2/<int:pk>", views.SnippetDetail1.as_view()),
    # 使用预定义的混合视图
    path("snippets3/", views.SnippetList2.as_view()),
    path("snippets3/<int:pk>", views.SnippetDetail2.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)