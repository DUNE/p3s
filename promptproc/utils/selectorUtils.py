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
       
       self.fields[self.fieldname] = forms.ChoiceField(choices = self.choices, label = self.label, required=False)

    def handleDropSelector(self):
        selection = self.cleaned_data[self.fieldname]
        if(selection=='All' or selection=='Never'):
            return ''
        else:
            return self.tag+'='+selection+'&'
#########################################################
#---
class twoFieldGeneric(forms.Form):
    def __init__(self, *args, **kwargs):
       self.label1	= kwargs.pop('label1')
       self.label2	= kwargs.pop('label2')
       
       self.field1	= kwargs.pop('field1')
       self.field2	= kwargs.pop('field2')
       
       self.init1	= kwargs.pop('init1')
       self.init2	= kwargs.pop('init2')

       super(twoFieldGeneric, self).__init__(*args, **kwargs)
       
       self.fields[self.field1] = forms.CharField(required=False, initial=self.init1, label=self.label1)
       self.fields[self.field2] = forms.CharField(required=False, initial=self.init2, label=self.label2)

    def getval(self, what):
        return self.cleaned_data[what]
   
#---
