import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DRF.settings")
django.setup()

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.renderers import JSONRenderer

# 创建并保存两个 Snippet
def fn1():
    snippet1 = Snippet(code='foo = "bar"\n')
    snippet1.save()

    snippet2 = Snippet(code='print("hello, world")\n')
    snippet2.save()

# 序列化 snippet2
# snippet = Snippet.objects.first()
snippet = Snippet.objects.get(id=2)
serializer = SnippetSerializer(snippet)
print("Python 字典:", serializer.data)

# 转成 JSON 字符串
# content = JSONRenderer().render(serializer.data)
# print("JSON 字符串:", content)

from snippets.serializers1 import SnippetSerializer
serializer1 = SnippetSerializer()
print(repr(serializer1))
print(serializer1)