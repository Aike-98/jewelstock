from django import template
register = template.Library()

@register.simple_tag()
def url_replace(request, key, value):
    '''
    urlパラメータを管理するカスタムテンプレートタグ
    '''
    copied = request.GET.copy()
    copied[key] = value
    return copied.urlencode()