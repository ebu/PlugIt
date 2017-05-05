from django import template
from django.template.base import Node, Template, TemplateSyntaxError
from django.conf import settings

register = template.Library()


class PlugItIncludeNode(Node):
    def __init__(self, action):
        self.action = action

    def render(self, context):
        action = self.action.resolve(context)

        # Load plugIt object
        if settings.PIAPI_STANDALONE:
            # Import objects form the view
            from plugit_proxy.views import plugIt, baseURI
        else:
            # Import object using the function in the view
            from plugit_proxy.views import getPlugItObject

            # Check the secret
            from plugit_proxy.utils import create_secret
            if context['ebuio_hpro_key'] != create_secret(str(context['ebuio_hpro_pk']), context['ebuio_hpro_name'], str(context['ebuio_u'].pk)):
                return ''
            (plugIt, _, _) = getPlugItObject(context['ebuio_hpro_pk'])

        templateContent = plugIt.getTemplate(action)

        template = Template(templateContent)

        return template.render(context)


@register.tag
def plugitInclude(parser, token):
    """
        Load and render a template, using the same context of a specific action.

        Example: {% plugitInclude "/menuBar" %}
    """
    bits = token.split_contents()

    if len(bits) != 2:
        raise TemplateSyntaxError("'plugitInclude' tag takes one argument: the tempalte's action to use")

    action = parser.compile_filter(bits[1])

    return PlugItIncludeNode(action)


@register.assignment_tag
def plugitGetUser(pk):
    if settings.PIAPI_STANDALONE:
        from plugit_proxy.views import generate_user
        user = generate_user(pk=str(pk))

    else:
        from users.models import TechUser
        try:
            user = TechUser.objects.get(pk=pk)
        except Exception:
            return None

    # Return only wanted properties about the user
    class User():
        pass

    user_cleaned = User()
    for prop in settings.PIAPI_USERDATA:
        if hasattr(user, prop):
            setattr(user_cleaned, prop, getattr(user, prop))

    user_cleaned.id = str(user_cleaned.pk) if hasattr(user_cleaned, 'pk') else None

    return user_cleaned


@register.filter
def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')
