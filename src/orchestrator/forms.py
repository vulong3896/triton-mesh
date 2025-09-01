from django import forms


class ModelForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    deploy_algorithm = forms.CharField(label="Deploy algorithm", max_length=100, required=False)
    routing_algorithm = forms.CharField(label="Name", max_length=100, required=False)
