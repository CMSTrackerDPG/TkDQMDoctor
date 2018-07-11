
class ChecklistTemplateContextMixin(object):
    """
    Sets the checklist_base_template_name context variable to use the
    modal-base.html base template for each Checklist when creating/updating a RunInfo
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checklist_base_template_name"] = 'certhelper/checklists/modal-base.html'
        return context
