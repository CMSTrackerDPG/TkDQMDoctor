from django import template

from certhelper.utilities.logger import get_configured_logger

logger = get_configured_logger(loggername=__name__, filename="form_tags.log")

register = template.Library()


@register.inclusion_tag('certhelper/components/templatetags/checklist_checkbox.html')
def render_checklist_checkbox(form_checklist, label=""):
    """"
    renders a Checklist checkbox with a label

    Example Usage:
    {% render_checklist_checkbox form.checklists.general %}
    """
    try:
        checklist = form_checklist["checklist"]
        checkbox = form_checklist["field"]
        if not label:
            label = checklist.title + " Checklist"
        return {'checklist': checklist, 'checkbox': checkbox, 'label': label}
    except TypeError:
        # Don't render if no checklist is provided
        return {}


@register.inclusion_tag('certhelper/components/templatetags/checklist_modal.html')
def render_checklist_modal(form_checklist, label=""):
    """"
    renders a Checkbox and a Modal

    Example Usage:
    {% render_checklist_modal form.checklists.trackermap %}
    """
    try:
        checklist = form_checklist["checklist"]
        checkbox = form_checklist["field"]
        if not label:
            label = checklist.title + " Checklist"
        return {'checklist': checklist, 'checkbox': checkbox, 'label': label}
    except TypeError:
        # Don't render if no checklist is provided
        return {}


@register.inclusion_tag('certhelper/components/templatetags/label_and_field.html')
def render_label_and_field_for(field):
    return {'field': field}
