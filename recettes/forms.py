from django import forms
from .models import Recette, Ingredient, RecetteIngredient


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['nom', 'unite', 'seuil_critique', 'prix_unitaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'unite': forms.TextInput(attrs={'class': 'form-control'}),
            'seuil_critique': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        fields = ['nom', 'description', 'temps_cuisson', 'chef_responsable']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'temps_cuisson': forms.NumberInput(attrs={'class': 'form-control'}),
            'chef_responsable': forms.Select(attrs={'class': 'form-control'}),
        }


class RecetteIngredientForm(forms.ModelForm):
    class Meta:
        model = RecetteIngredient
        fields = ['ingredient', 'quantite']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        }