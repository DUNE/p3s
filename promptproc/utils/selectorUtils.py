from django import forms

#########################################################    
class boxSelector(forms.Form):

    def __init__(self, *args, **kwargs):
       self.what = kwargs.pop('what')
       self.states = kwargs.pop('states')
       self.label = kwargs.pop('label')

       super(boxSelector, self).__init__(*args, **kwargs)
       self.fields['stateChoice'].choices	= self.states # SELECTORS[self.what]['states']
       self.fields['stateChoice'].label		= self.label  # SELECTORS[self.what]['stateLabel']

    def handleBoxSelector(self):
        selectedStates = self.cleaned_data['stateChoice']
        if len(selectedStates):
            if('all' in selectedStates):
                return ''
            else:
                return 'state='+",".join(selectedStates)+'&'
        return ''

    stateChoice = forms.MultipleChoiceField(label='DUMMY',
                                            required=False,
                                            widget=forms.CheckboxSelectMultiple,
                                            choices=[('place', 'holder'),])

#########################################################    
class dropDownGeneric(forms.Form):
    def __init__(self, *args, **kwargs):
       self.label	= kwargs.pop('label')
       self.choices	= kwargs.pop('choices')
       self.tag		= kwargs.pop('tag')
       self.fieldname	= self.tag # 'choice'
       
       super(dropDownGeneric, self).__init__(*args, **kwargs)
       
       self.fields[self.fieldname] = forms.ChoiceField(choices = self.choices, label = self.label)

    def handleDropSelector(self):
        selection = self.cleaned_data[self.fieldname]
        if(selection=='All'):
            return ''
        else:
            return self.tag+'='+selection+'&'
