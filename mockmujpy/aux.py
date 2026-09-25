def _available_components_():
    """
    returns a list of template dictionaries (one per fit component):

    retreived magically from the mucomponents mumodel class.
    Each dictionary contains 'name' and 'pardicts', 
           'pardicts' = list of parameter dictionaries, 
                        keys: 
                          'name',
                          'error,
                          'limits'
           errore are used by minuit as initial steps
           limits are 
               [None,None] for uncostrained parameters A,B,φ,λ
               [0,None] for positive parity parameters Δ,σ
                        and for positive defined parameters 'α','β','Λ','ν'
               [0,0] for fake parameter BL
    ::  ({'name':'bl','pardicts':[{'name':'A','error':0.01,'limits'[None,None]},
                                  {'name':'λ','error':0.01,'limits'[None,None]}}, 
                                  ...)
        used in mufit and mudashed
    """

    from mockmujpy.aux import mumodel
    from iminuit import describe
    
    available_components = [] # generates the template of available components.
    for name in [module for module in dir(mumodel()) if module[0]!='_']: # magical extraction of component names
        pars = describe(mumodel.__dict__[name])[2:]            #  [12:] because the first two arguments are self, x
        _pars = [] 
        # print('pars are {}'.format(pars))
        attrib = getattr(mumodel,name)
        tip = attrib.__doc__
        positive_defined = ['α','β','Λ','ν']
        positive_parity = ['Δ','σ']
        for parname in pars:
        # parname, error, limits
        # In this template only
        #   {'name':'amplitude','error':0.01,'limits':[0, 0]}
        # parameter name will get a label later 
            error, limits = 0.002, [None, None] # defaults for 'A', 'λ', 'Γ'
            if parname == 'B' or parname == 'Bd': error = 0.05
            if parname == 'BL': error, limits = 0, [0,0]
            if parname == 'φ': error = 1.0
            if parname in positive_defined+positive_parity: limits = [0., None]
            # add here special cases for errors and limits, e.g. positive defined parameters
            if parname in positive_parity:
                _pars.append({'name':parname,'error':error,'limits':limits,'positive_parity':True})
            else:
                _pars.append({'name':parname,'error':error,'limits':limits})
        available_components.append({'name':name,'pardicts':_pars,'tip':tip})
    # [available_components[i]['name'] for i in range(len(available_components))] 
    # list of just mucomponents method names
    return available_components

def make_copy(test):
    """
    copy groups and, in case, the test data that
    """

    from importlib import resources
    from os import getcwd, access, W_OK, listdir, mkdir, remove
    from os.path import join, isdir, islink, isfile
    from shutil import copyfile as cp

    # copy grp files
    startup_path = getcwd()
    writeable = access(startup_path, W_OK)
    grp_dir = join(startup_path,"groups")
    if writeable:
        if not isdir(grp_dir): mkdir(grp_dir)
        for file in listdir(resources.files("mockmujpy.tests").joinpath("groups")):
            srcfile = resources.files("mockmujpy.tests").joinpath("groups").joinpath(file)
            destfile = join(grp_dir,file)
            if not isfile(destfile): cp(srcfile,destfile)

        # copy      return True
        if test:
            fit = "fit_"+test.lower()
            fit_dir = join(startup_path,"fit")
            if islink(fit_dir): remove(fit_dir)
            if isdir(fit_dir): # clean it up
                for file in listdir(fit_dir):
                    pathfil = join(fit_dir,file) 
                    remove(pathfil)
            else: # make it  
                mkdir(fit_dir)
            for file in listdir(resources.files("mockmujpy.tests").joinpath(fit)):
                srcfile = resources.files("mockmujpy.tests").joinpath(fit).joinpath(file)
                destfile = join(fit_dir,file)
                cp(srcfile,destfile)

   #         copy data files
            data = "data_"+test.lower()
            data_dir = join(startup_path,"data")
            if islink(data_dir): remove(data_dir)
            if isdir(data_dir):  # clean it up
                for file in listdir(data_dir):
                    pathfil = join(data_dir,file) 
                    remove(pathfil)
            else: # make it
                mkdir(data_dir)
            for file in listdir(resources.files("mockmujpy.tests").joinpath(data)):
                srcfile = resources.files("mockmujpy.tests").joinpath(data).joinpath(file)
                destfile = join(data_dir,file)
                cp(srcfile,destfile)
            return data_dir
        else:
            return True
    else:
        return False

def derun(string):
    """
    parses string, producing a list of runs; 
    expects comma separated items

    looks for 'l','l:m','l+n+m','l:m:-1' 
    where l, m, n are integers
    also more than one, comma separated 

    rejects all other characters

    returns a list of lists of integer
        used in musuite and mudashed
    """
    import re
    from copy import deepcopy as cp
    s = []
    try:
    # substitute ',' followed by spaces by plain ','
        string_in = cp(string)
        string = re.sub(r",\s+", ",", string.strip())
    # substitute multiple consecutive spaces with ',' in strings separated by spaces only
        string = re.sub(r"\s+", ",", string) #
    # systematic str(int(b[])) to check that b[] ARE integers
        for b in string.split(','): # csv
            kminus = b.find(':-1') # '-1' means reverse order
            kcolon = b.find(':') # ':' and '+' are mutually exclusive
            kplus = b.find('+')
            #print(kminus,kcolon,kplus)

            if kminus<0 and kcolon<0 and kplus<0: # single run, no run addition
                int(b) # produces an Error if b is not an integer
                s.append([b]) # append single run string   
            else:
                if kminus>0 and kminus == kcolon:
                    return [], 'l:-1 is illegal'
                elif kplus>0:
                    # add files, append a list or run strings
                    ss = []
                    k0 = 0
                    while kplus>0: # str(int(b[]))
                        ss.append(int(b[k0:kplus])) 
                        k0 = kplus+1
                        kplus = b.find('+',k0)
                    ss.append(int(b[k0:]))
                    s.append([str(q) for q in ss])
                else:
                    # either kminus=-1 (just a range) or  kcolon<kminus, (range in reverse order)
                    # in both cases:
                    if kminus<0:
                        #print(int(b[:kcolon]),int(b[kcolon+1:]))
                        if int(b[:kcolon])>int(b[kcolon+1:]):
                            return [], 'l:m must have l<m'
                        for j in range(int(b[:kcolon]),int(b[kcolon+1:])+1):
                            s.append([str(j)]) # append single run strings
                    else:
                        ss = [] 
                        # # :-1 reverse order
                        if int(b[:kcolon])>int(b[kcolon+1:kminus]):
                            return ss, 'l:m:-1 must have l<m'
                        for j in range(int(b[:kcolon]),int(b[kcolon+1:kminus])+1):
                            ss.append([str(j)]) # append single run strings
                        ss = ss[::-1]
                        for sss in ss:
                            s.append(sss)
        return s, None
    except:
        return [], 'not a valid string: {}'.format(string_in)

def get_title(run,notemp=False,nofield=False):
    """
    form standard psi title
        used in tools mufit musuite mudashed
    """
    title = [(run.get_sample()).rstrip()]
    title.append((run.get_orient()).rstrip())  
    if not notemp:
        tstr = run.get_temp()
        try:
            temp = float(tstr[:tstr.index('K')])
        except:
            temp = float(tstr)
        title.append('{:.1f}K'.format(temp))
    if not nofield:
        field = run.get_field()
        try:
            title.append('{:.0f}mT'.format(float(field[:field.index('G')])/10))
        except:
            title.append('{:.0f}mT'.format(float(field)/10))
    return ' '.join(title)    
 
def get_gtotals(suite):
    """
    calculates the grand totals and group totals for multi run multi group 

    input is self.suite of class musuite
    returns totalcounts (list of run total str)
            groupcounts (list of lists group total str) 
            nsbin, maxbin (str)
        used in mudashed
    """

    from numpy import array, concatenate
    # called only by self.suite after having loaded a run or a run suite

    ###################
    # grouping set 
    # suite.grouping['forward'] and suite.grouping['backward'] are np.arrays of integers
    # initialize totals
    ###################
    grc = []
    for k,grpdict in enumerate(suite.grouping):
        if not k: # k is 0
            gr = concatenate((grpdict['forward'],grpdict['backward']))
            grc.append(gr)
        else:
            g = concatenate((grpdict['forward'],grpdict['backward']))
            grc.append(g)

    ts,gs =  [],[]
    n1 = suite.offset+suite.nt0[0]
    for k,runs in enumerate(suite._the_runs_):
        tsum = 0
        ggs = []
        for j,group in enumerate(grc):
            gsum = 0
            for counter in group:
                for j,run in enumerate(runs): # add values for runs to add
                    suite.log('inside get_gtotals counter {} suite.datafile[-3:] = {}'.format(counter,suite.datafile[-3:]))
                    if suite.datafile[-3:]=='bin' or suite.datafile[-3:]=='mdu' or suite.datafile[-4:]=='root':
                        n1 = suite.offset+suite.nt0[counter] 
                    histo = array(run.get_histo_vector(counter,1)).sum() 
                    gsum += histo
                    tsum += histo
            gggs = '{:.2f}'.format(gsum/1e6)+'Mev'
            ggs.append(gggs)
        gs.append(ggs)
        ts.append('{:.2f}'.format(tsum/1e6)+'Mev')
    suite.log('inside get_gtotals ts = {}, gs  = {}, ns {},  '.format(ts,gs,suite._the_runs_[0][0].get_binWidth_ns()))
    return ts, gs, '{:.3}'.format(suite._the_runs_[0][0].get_binWidth_ns()), str(suite.histoLength)
 
def get_grouping(groupcsv):
    """
    input
      groupcsv is a shorthand csv string, e.g. '1:3,5' or '1,3,5' etc.
      contained in self.suite.group[k]["forward] of self.suite.group[k]["backward"]
          (the k-th detector group of a multi group fit)
    output
     grouping is an np.array of indices, 0 based
        used in musuite
    """
    import numpy as np

    # two shorthands: either a list, comma separated, such as 1,3,5,6 
    # or a pair of integers, separated by a colon, such as 1:3 = 1,2,3 
    # only one column is allowed, but 1, 3, 5 , 7:9 = 1, 3, 5, 7, 8, 9 
    # or 1:3,5,7 = 1,2,3,5,7  are also valid
    # no more complex nesting (3:5,5,8:10 is not allowed)
    #       get the shorthand from the gui Text 
    #groupcsv = groupcsv.replace('.',',') # can only be a mistake: '.' means ','
    try:
        if groupcsv.find(':')==-1: # no colon, it's a pure csv
            grouping = np.array([int(ss) for ss in groupcsv.split(',')]) # read it
        else:  # colon found                 
            if groupcsv.find(',')==-1: # (no commas, only colon, must be n:m)
                nm = [int(w) for w in groupcsv.split(':')] # read n m
                grouping = np.array(list(range(nm[0],nm[1]+1))) # single counters
            else: # general case, mixed csv and colon
                p = groupcsv.split(':') # '1,2,3,4,6' '7,10,12,14' '16,20,23'
                ncolon = len(p)-1 
                grouping = np.array([])
                for k in range(ncolon):
                    q = p[k].split(',') # ['1' '2' '3' '4' '6']
                    if k>0:
                        last = int(q[0])
                        grouping = np.concatenate((grouping,np.array(list(range(first,last+1)))))
                        first = int(q[-1])
                        grouping = np.concatenate((grouping,np.array(list(int(w) for w in q[1:-1]))))
                    elif k==0:
                        first = int(q[-1])
                        grouping = np.concatenate((grouping,np.array(list(int(w) for w in q[:-1]))))
                q = p[-1].split(',') # '22','25'
                last = int(q[0])
                grouping = np.concatenate((grouping,np.array(list(range(first,last+1)))))
                grouping = np.concatenate((grouping,np.array(list(int(w) for w in q[1:])))).astype(int)

        grouping -=1 # this is counter index, remove 1 for python 0-based indexing 
    except Exception as e:
        grouping = e # np.array([-1]) # error flag
        
    return grouping

def check_multigroup(group,alpha):
    """
    check shorthand in single group and alpha for Groups ...

    returns grp_cal dict if ok
            error message if not ok
    """

    from mockmujpy.aux import get_grouping
    try:
        forward, backward = group.split('-')
        fg, bg = get_grouping(forward), get_grouping(backward)
        if all(fg>=0) and fg.dtype == int and all(bg>=0) and bg.dtype == int: # get_grouping is an np.array
            grp_cal = {'forward':forward, 
                      'backward':backward, 
                       'alpha':float(alpha)}
            return grp_cal
    except ValueError as e:
        text = 'Exception {}'.format(e)
        text += '\nGroups ... syntax error:\ncheck Groups... = {} and α = {}'.format(group,alpha)
        return text

def ipyw_yes_no_dialog(title="Check!",message=""):
    """ 
    ask yes or no 

    return  overlay to be shown in tab and observe its layout.display to toggle tabs
            yes_btn.value True/False 
    """

    from mockmujpy.aux import create_overlay_layout, create_dialog_box_layout
    title_html = HTML(f"<h3>{title}</h3>") #⚠️
    message_html = HTML(f"<p>{message}</p>", layout=Layout(margin='10px 0px 20px 0px'))
    yes_btn = ValueButton(description="Yes", layout=Layout(width='100px', align_self='center'))
    yes_btn.style.button_color = '#c0b1ab'
    no_btn = Button(description="No", layout=Layout(width='100px', align_self='center'))
    no_btn.style.button_color = '#c0c0c0'
    # Contenitore del dialogo
    dialog_box = VBox([title_html, message_html,HBox([yes_btn,no_btn])], layout=create_dialog_box_layout())
    overlay = VBox([dialog_box], layout=create_overlay_layout())
    
    yes_btn.on_click(lambda b: [setattr(yes_btn,'value',True), setattr(overlay.layout, 'display', 'none')])
    no_btn.on_click(lambda b: [setattr(yes_btn,'value',False), setattr(overlay.layout, 'display', 'none')])
    return overlay, yes_btn 

def ipyw_warning_dial(title="Warning", message=""):
    """
    Warning in dialog with OK button.

    rerurns overlay to display it in an Tab, Output, ...
            ok_btn to 1) observe(overlay.layout,names='display') e.g. to toggle tab.selected_index
                      2) setattr(overlay.layout, 'display', 'flex')
    """

    from mockmujpy.aux import create_overlay_layout, create_dialog_box_layout
    # Elementi dell'interfaccia
    title_html = HTML(f"<h3>{title}</h3>") #⚠️
    message_html = HTML(f"<p>{message}</p>", layout=Layout(margin='10px 0px 20px 0px'))
    ok_btn = Button(description="OK", layout=Layout(width='100px', align_self='center'))
    ok_btn.style.button_color = '#c0b1ab'
    # Contenitore del dialogo
    dialog_box = VBox([title_html, message_html, ok_btn], layout=create_dialog_box_layout())
    overlay = VBox([dialog_box], layout=create_overlay_layout())
    
    ok_btn.on_click(lambda b: setattr(overlay.layout, 'display', 'none'))
    return overlay

def ipyw_radio_dial(options, title="<b>Select one option:</b>"):
    """
    Display a range of Radiobutton and store the choice 

    returns overlay, radio 
    use options = ['text0','text1','text2'] to get selected string in radio.value
    use options = [('text0',0),('text1',1)] to get also selected index in radio.index
    observe(overlay.layout,names='display') e.g. to toggle tab.selected_index for a tabbed output
    """

    from mockmujpy.aux import create_overlay_layout, create_dialog_box_layout
    title_html = HTML(value=f"<h3>{title}</h3>")
    
    radio = RadioButtons(
        options=options,
        layout=Layout(width='100%', margin='10px 0px')
    )
    
    cancel_btn = Button(description="Cancel", layout=Layout(margin='0 5px 0 0'))
    ok_btn = widgets.Button(description="OK", layout=Layout(margin='0 0 0 5px'))
    ok_btn.style.button_color = '#c0b1ab'
    buttons_hbox = HBox([cancel_btn, ok_btn], layout=Layout(justify_content='flex-end', margin='10px 0 0 0'))
    
    dialog_box = VBox([title_html, radio, buttons_hbox], layout=create_dialog_box_layout())
    overlay = VBox([dialog_box], layout=create_overlay_layout())
    
    confirm_btn.on_click(lambda b: setattr(overlay.layout, 'display', 'flex'))
    cancel_btn.on_click(lambda b: setattr(overlay.layout, 'display', 'none'))
    return overlay, radio

def ipyw_path_file_dial(target_button, callback, path=None, filter_pattern=None, title="<b>1-click select:</b>"):
    """
    Builds an ipywidget native File Browser in an overlay.
    
    just 2 clicks to load a path, exploiting instantaneous 'value' of ValueButton target_button.
    Actions flow:
    1. click target_button -> opens modal_overlay.
    2. single click on a file (📄) -> instantly writes path string in target_button.value and closes modal_overlay.
    * Note: a single click on a folder (📁) navigates inside it.
    """

    from mockmujpy.aux import create_overlay_layout, create_dialog_box_layout
    if path is None:
        current_dir = os.getcwd()
    else:
        current_dir = os.path.abspath(path)
        
    if filter_pattern: # if not None make sure it is a list
        if not isinstance(filter_pattern,list): filter_pattern = [filter_pattern]
    #if not os.path.exists(current_dir):
    #    os.makedirs(current_dir, exist_ok=True)

    # Widget di selezione nativo
    file_list_widget = Select(
        options=[],
        layout=Layout(width='100%', height='250px', font_family='monospace') # height='250px'
    )
    
    title_html = HTML(value='')#,layout=Layout(height='16pt'))
    warn_html = HTML(value=f'{title} &nbsp;')
    hspacer = Label(' ',layout={'width':'25%','height':'16pt'})
    close_btn = Button(description="Cancel", layout=Layout(align_self='flex-end', margin='10px 0 0 0'))
    close_btn.style.button_color = '#c0b1ab'
    
    modal_content = VBox([title_html,file_list_widget,HBox([warn_html,hspacer,close_btn])], layout=create_dialog_box_layout())
    #                     Layout(
    #    padding='20px', border='1px solid #ccc', box_shadow='0px 4px 15px rgba(0,0,0,0.3)',
    #    border_radius='4px', width='560px', background_color='white'
    #))
    
    modal_overlay = VBox([modal_content], layout=create_overlay_layout())
    #                     Layout(
    #    position='absolute', left='0', top='0',#, right='0', bottom='0',
    #    background_color='rgba(0, 0, 0, 0.5)', justify_content='center', align_items='flex-start',
    #    display='none', z_index='9999'
    #))
    
    #open_button = Button(description="Load", button_style='primary')
    
    state = {
        'current_dir': current_dir,
        'ignore_observe': False  # Flag per evitare loop durante il ripopolamento della lista
    }

    def populate_list():
        state['ignore_observe'] = True
        try:
            items = os.listdir(state['current_dir'])
        except Exception:
            items = []
            
        directories = []
        files = []
        
        if os.path.dirname(state['current_dir']) != state['current_dir']:
            directories.append('📁 ..')
            
        for item in sorted(items):
            full_path = os.path.join(state['current_dir'], item)
            if os.path.isdir(full_path):
                directories.append(f"📁 {item}")
            elif os.path.isfile(full_path):
                if filter_pattern:
                    # if not isinstance(filter_pattern,list): filter_pattern = list(filter_pattern)
                    for pattern in filter_pattern:
                        ext = pattern.replace('*', '')
                        if item.endswith(ext):
                            files.append(f"📄 {item}")
                else:
                    files.append(f"📄 {item}")
                    
        # Reset della selezione a None prima di cambiare le opzioni per forzare l'evento al prossimo clic
        file_list_widget.value = None
        file_list_widget.options = directories + files
        title_html.value = f"<small>Path: <b style='color:#2196F3;'>{state['current_dir']}</b></small>"
        state['ignore_observe'] = False

    def handle_selection_change(change):
        """Loads or selects folder on single click"""
        if state['ignore_observe']:
            return
            
        selected_raw = change['new']
        if not selected_raw:
            return
            
        clean_name = selected_raw[2:]
        
        if selected_raw.startswith('📁'):
            # NAVIGAZIONE IMMEDIATA: Entra nella cartella al singolo clic
            if clean_name.startswith('..'):
                state['current_dir'] = os.path.dirname(state['current_dir'])
            else:
                state['current_dir'] = os.path.join(state['current_dir'], clean_name)
            populate_list()
            index=3
            
        elif selected_raw.startswith('📄'):
            # SELEZIONE IMMEDIATA: Un solo clic sul file scrive e chiude il modale (Ottimo a 2 azioni)
            target_button.value = os.path.join(state['current_dir'], clean_name)
            callback(None)
            index = 0
            modal_overlay.layout.display = 'none'

    # Sfrutta l'observe sul valore nativo, incredibilmente robusto ed esente da latenze JavaScript
    file_list_widget.observe(handle_selection_change, names='value')
    
    target_button.on_click(lambda b: [populate_list(), setattr(modal_overlay.layout, 'display', 'flex')])
    close_btn.on_click(lambda b: [callback(b), setattr(modal_overlay.layout, 'display', 'none')])
    
    return modal_overlay, target_button

def show_hide_tab(overlay,display_change,tabs):
    """ shows overlay in toggling tabs on display toggle"""

    overlay.layout.observe(display_change,names='display')
    setattr(overlay.layout, 'display', 'flex')
    kiddos = list(tabs.children)
    kids = list(kiddos[3].children)
    kids[3] = overlay
    kiddos[3].children = kids
    tabs.children = kiddos
    return tabs

def validmodel(model):
    """
    checks validity of model name, e.g. "almlmg"
        used in mudashed
    """

    from mockmujpy.aux import _available_components_
    available_components =_available_components_() # creates list automagically from mucomponents
    component_names = [available_components[i]['name'] 
                            for i in range(len(available_components))]
    components = [model[i:i+2] for i in range(0, len(model), 2)]
    # print('valid model, available components: ',*component_names)
    if not components: # empty model
        return False
    for component in components: 
        if component in component_names:
            pass
        else:
            return False
    if 'al' in components: # check that model has only one 'al' at the beginning
        if model.count('al')>1 or model.index('al')>0:
            return False      
    return True

def find_model_difference(oldmodel,model):
    """
    distinguish une component addition, removal from more complex changes

    input 
        oldmodel string
        model string
    return 
        [k] k is one-based index of added component, its negative for subtracted, zero for complex
        if the added/removed component is repeated, all possibilities are listed [k,j,...]
        no checks on syntax, model names have already been verified
    """
    # Ensure both strings have even lengths for 2-letter syllables

    # Split strings into lists of 2-letter syllables
    sys1 = [oldmodel[i:i+2] for i in range(0, len(oldmodel), 2)]
    sys2 = [model[i:i+2] for i in range(0, len(model), 2)]

    out = []
    if len(sys2) == len(sys1) + 1:
        for i in range(len(sys2)):
            if sys1[:i] + [sys2[i]] + sys1[i:] == sys2:
                out.append(i)
                
    # Case 2: First string is the second plus a syllable
    # (i.e., Removing a single syllable from sys1 at index i creates sys2)
    elif len(sys1) == len(sys2) + 1:
        for i in range(len(sys1)):
            if sys1[:i] + sys1[i+1:] == sys2:
                out.append(-(i))                
    return out

import os
from ipywidgets import VBox, HBox, Layout, Button, HTML, Text, Select, Label
from traitlets import Any

class ValueButton(Button):
    """defines an ipywidget Button with a .value attached"""

    def __init__(self, value=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a custom value traitlet
        self.add_traits(value=Any(value))

def create_overlay_layout(start='none'):
    """Crea lo stile CSS per lo sfondo oscurato del popup"""
    return Layout(
        position='absolute', left='0', top='0',#, right='0', bottom='0',
        background_color='rgba(0, 0, 0, 0.5)', justify_content='center', align_items='flex-start',
        display=start, z_index='9999')

def create_dialog_box_layout():
    """Crea lo stile per la finestra di dialogo interna"""
    return Layout(
        padding='20px', border='1px solid #ccc', box_shadow='0px 4px 15px rgba(0,0,0,0.3)',
        border_radius='4px', width='560px', background_color='white')

def check_dashboard_json(dashboard):
    """
    checks for typos against list of allowed keys
    """

    allowed_keys = ["version",
                    "fit_range",
                    "offset",
                    "globpardicts_guess",
                    "model_guess",
                    "globpardicts_result",
                    "model_result",
                    "name",
                    "value",
                    "flag",
                    "error",
                    "limits",
                    "positive_parity",
                    "label",
                    "pardicts",
                    "function",
                    "function_multi",
                    "std",
                    "chi2"
                    ]
    #print(len(allowed_keys))
    for key in dashboard.keys():
        allowed = [allowed_keys[i] for i in [0,1,2,3,4,5,6,18]]
        if key not in allowed: return 'dashboard keys'
    if allowed_keys[3] in dashboard.keys(): # globpardicts
        allowed = [allowed_keys[i] for i in range(7,13)]
        for pardict in dashboard[allowed_keys[3]]:
            for key in pardict: 
                if key not in allowed: return 'globpardicts_guess keys'
    for kc,component in enumerate(dashboard[allowed_keys[4]]):
        allowed = [allowed_keys[i] for i in [7,13,14]]
        for key in component:
            if key not in allowed: return 'model keys'
        allowed = [allowed_keys[i] for i in [7,8,9,10,11,15,16]]
        for kp,pardict in enumerate(component["pardicts"]):
            for key in pardict:
                if key not in allowed: return '{}{} pardict {} keys'.format(component['name'],kc,kp)
    return ''


######################
# Mock mujpy classes #
######################

class suite():
    """Mock suite: ignores runlist, considers groups"""

    def __init__(self, datafile , runlist , grp_calib , offset , startuppath, console = 'print',mplot=False):
        from os.path import join
        from os import getcwd
        self.loadfirst = True
        self.log = console
        self.nruns = 1
        self.nt0 = [0,0,0,0]
        self.histoLength = 2
        strtpth = getcwd()
        self.__fitpath__ = join(strtpth,'fit')
        self.__datapath__ = join(strtpth,'data')
        self.datafile = datafile
        self.offset = offset
        self._the_facility_ = 'PSI'
        console('inside suite before run')
        class run():
            def get_timeStart_vector(self):
                return '01-MAY-21 15:14:00'
            def get_timeStop_vector(self):
                return '01-MAY-21 15:40:31'
            def get_comment(self):
                return 'mock comment'
            def get_sample(self):
                return 'MnBi6T10'
            def get_orient(self):
                return 'pellet'
            def get_temp(self):
                return '30.1K'
            def get_field(self):
                return '100 G'
            def get_binWidth_ns(self):
                return 0.391
            def get_histo_vector(self,k,binning):
                from numpy import array
                return array([1234567,23456])
            def get_numberHisto_int(self):
                return 4
        self.groups = grp_calib
        self._the_runs_ = [[run()]]
        self.store_groups()
        self.log('inside suite after store_goups self.grouping = {}'.format(self.grouping))

    def store_groups(self):
        """
        from self.groups dashboard shorthand dict to self.grouping dict alpha, lists of histogram numbers  
        """

        from mockmujpy.aux import get_grouping
        self.log('inside store_groups 0')
        self.log('inside store_groups runs {}'.format(self._the_runs_[0][0].get_histo_vector(0,1)))
        for k,group in enumerate(self.groups):
            fgroup, bgroup, alpha = get_grouping(group['forward']), get_grouping(group['backward']), group['alpha']
            if alpha>0 and self.check_group(fgroup) and self.check_group(bgroup) and not isinstance(fgroup,str) and not isinstance(bgroup,str): # checks legal grpcalib_file
                if k==0: self.grouping=[]
                self.grouping.append({'forward':fgroup, 'backward':bgroup, 'alpha':alpha})
                # fgroup bgroup are two np.arrays of integers
            else:
                self.log('forw {}, backw {}, alpha {:.2f}, Nhisto = {}'.format(fgroup,bgroup,alpha,
                                self._the_runs_[0][0].get_numberHisto_int()))
                self.log('Groups calibration file corrupted')
                return False
        return True

    def check_group(self,group):
        """
        rough check that this is a group of existing detectors
        """

        # numberHisto_int is the number of physics detectors
        # RedGreen mode has more than one period (in Isis parlance) for different stimuli ON or OFF 
        # for this purpose nexus detector counts have three indices: period, detector, bin
        # MusrRoot instead has offsets, typically [0,20,40,80] or [0,10,20,30], reflected in the label Histo No
        # whereas the list self._histo.counts() has two indices: histogram, bin, and histogram numbers are contiguous
        # e.g. on lem for numberHisto_int = 8 and offsets [0,10] indices 0,...,7 are the original histos and 8,...,15 are PPC
        numberHisto = self._the_runs_[0][0].get_numberHisto_int()
        periods = 1
        if 'get_RedGreen_offsets' in self._the_runs_[0][0].__dir__(): # RedGreen may be present
            periods = len(self._the_runs_[0][0].get_RedGreen_offsets()) # are there RedGreen copies (periods>1)?
        if 'get_beamline' in self._the_runs_[0][0].__dir__(): # PSI only
            numberHisto = numberHisto*periods           
        return (group>=0).all()*(group<numberHisto).all()


class mufit():
    def __init__(self,suite,dashboard_file,dash_log = None): # writes text to board_box
        dash_log('                successfully lauched mock mufit!')
        self.log = dash_log

class mufitplot():
    def __init__(plot_range, fit, rotating_frame_frequencyMHz = 0, plot_out = None, fig_fit = None): # plots in self.figure_box
        fit.log('                  successfully lauched mock mufitplot!')
        fit.log('sorry, no plots ;)')

from numpy import cos, sin, pi, exp, sqrt, log, real, nan_to_num, inf, ceil, linspace, zeros, empty, ones, hstack, fft, sum, zeros_like, abs, array, where, arctan, pi, any, set_printoptions
from scipy.special import dawsn,erf, j0, j1
from scipy.constants import physical_constants as C
from iminuit.util import make_func_code

class mumodel(object):
    """Mock components of the fitting model."""

    def __init__(self):
        """ 
        Defines few constants and _help_ dictionary
        """

        self._radeg_ = pi/180.
        self._gamma_Mu_MHzperT = 3.183345142*C['proton gyromag. ratio over 2 pi'][0]  # numbers are from Particle Data Group 2017
        self._gamma_mu_ = 135.538817
        self._gamma_Mu_MHzper_mT = self._gamma_Mu_MHzperT*1e-3
        self._help_ = {'bl':r'Lorentz decay: $A\exp(-\lambda\,t)$',
                     'bg':r'Gauss decay: $A\exp(-0.5(\sigma\,t)^2)$',
                     'bs':r'stretched decay: $A\exp(-0.5(\Lambda\,t)^\beta)$',
                     'ba':r'Lorentz and Gauss decay: $A\exp(-\lambda\,t)\exp(-0.5(\sigma\,t)^2)$',
                     'da':r'Linearized dalpha correction: $f = \frac{2f_0(1+\alpha/\mbox{dalpha})-1}{1-f_0+2\alpha/dalpha}$',
                     'ml':r'Lorentz decay: $A\cos[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-\lambda\,t)$',
                     'mg':r'Lorentz and Gauss decay: $A\cos[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-\lambda\,t)\exp(-0.5(\sigma\,t)^2)$',
                     'mu':r'Gauss decay: $A\cos[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-0.5(\sigma\,t)^2)$',
                     'ms':r'Gauss decay: $A\cos[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-(\Lambda\,t)^\beta)$',
                     'jl':r'Lorentz Bessel: $Aj_0[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-\lambda\,t)$',
                     'jg':r'Gauss Bessel: $A j_0[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-0.5(\sigma\,t)^2)$',
                     'js':r'Gauss Bessel: $A j_0[2\pi(\gamma_\mu B\, t +\phi/360)]\exp(-(\Lambda\,t)^\beta)$',
                     'fm':r'FMuF: $A/6[3+\cos 2*\pi\gamma_\mu\mbox{dipfield}\sqrt{3}\, t + \
               (1-1/\sqrt{3})\cos \pi\gamma_\mu\mbox{dipfield}(3-\sqrt{3})\,t + \
               (1+1/\sqrt{3})\cos\pi\gamma_\mu\mbox{dipfield}(3+\sqrt{3})\,t ]\exp(-\mbox{Lor_rate}\,t)$', 
                     'kg':r'Gauss Kubo-Toyabe: static and dynamic, in zero or longitudinal field by G. Allodi [Phys Scr 89, 115201]',
                     'kl':r'Lorentz Kubo-Toyabe: static, in zero or longitudinal field by G. Allodi [Phys Scr 89, 115201]',
                     'kd':r'Lorentz Kubo-Toyabe: static, in zero field, multiplied by Lorentz decay, by G. Allodi [Phys Scr 89, 115201]'}

    def al(self,x,α):
        """
        alpha calibration

        x [mus], α
        x dummy, for compatibility
        """
        
        # empty method  (could remove x from argument list ?)
        # print('al = {}'.format(α))
        return []
        al.func_code = make_func_code(["α"])                
           
    def bl(self,x,A,λ): 
        """
        Lorentzian decay, A*exp(-x*λ)
        
        x [mus], A, λ [mus-1]
        """
        
        # x need not be self.x (e.g. in plot)
        # λ = -87. if λ < -87. else λ
        return A*exp(-x*λ)
        bl.func_code = make_func_code(["A","λ"])

    def bg(self,x,A,σ): 
        """
        Gaussian decay, A*exp(-0.5*(x*σ)**2)
        
        x [mus], A, σ [mus-1] (positive parity)
        """
        
        # x need not be self.x (e.g. in plot)        
        return A*exp(-0.5*(x*σ)**2)
        bg.func_code = make_func_code(["A","σ"])

    def ba(self,x,A,λ,σ): 
        """
        Lorentzian times Gaussian decay, A*exp(-x*λ)*exp(-0.5*(x*σ)**2)
        
        x [mus], A, λ [mus-1], σ [mus-1] (positive parity)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*exp(-x*λ)*exp(-0.5*(x*σ)**2)
        ba.func_code = make_func_code(["A","λ","σ"])

    def bs(self,x,A,Λ,β): 
        """
        stretched decay A*exp(-(x*Λ)**β), 
        
        x [mus], A, Λ [mus-1] (>0), β (>0)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*exp(-(x*Λ)**β)
        bs.func_code = make_func_code(["A","Λ","β"])

    def ml(self,x,A,B,φ,λ): 
        """
        precession A cos(2 pi _gamma_Mu_MHzper_mT B x+φ _radeg_) times Lorentzian decay, 
        
        x [mus], A, B [mT], φ [deg], λ [mus-1]
        """
        
        return A*cos(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-x*λ)
        ml.func_code = make_func_code(["A","B","φ","λ"])

    def mg(self,x,A,B,φ,σ): 
        """
        precession A cos(2 pi _gamma_Mu_MHzper_mT B x+φ _radeg_) times Gaussian decay, 
        
        x [mus], A, B [mT], φ [degrees], σ [mus-1]  (positive parity)
        """
        
        return A*cos(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-0.5*(x*σ)**2)
        mg.func_code = make_func_code(["A","B","φ","σ"])
        
    def mu(self,x,A,B,φ,λ,σ): 
        """
        precession A cos(2 pi _gamma_Mu_MHzper_mT B x+φ _radeg_) times Gaussian times Lorentzian decays, 
        
        x [mus], A, B [mT], φ [degrees], 
        λ [mus-1], σ [mus-1]  (positive parity)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*cos(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-x*λ)*exp(-0.5*(x*σ)**2)
        mu.func_code = make_func_code(["A","B","φ","λ","σ"])

    def ms(self,x,A,B,φ,Λ,β): 
        """
        precession A cos(2 pi _gamma_Mu_MHzper_mT B x+φ _radeg_) times stretched decay, 
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*cos(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-(x*Λ)**β)
        ms.func_code = make_func_code(["A","B","φ","Λ","β"])

    def fm(self,x,A,B,λ):
        """
        FmuF (powder average)
        
        according to Book  
        x [mus], A, B [mT], λ [mus-1]
        B is Bdip
        """
        
        # x need not be self.x (e.g. in plot)
        return A/6.0*(1.+cos(2*pi*self._gamma_Mu_MHzper_mT*B*x)+
               2.*(cos(pi*self._gamma_Mu_MHzper_mT*B*x)+
                   cos(3*pi*self._gamma_Mu_MHzper_mT*B*x) ))*exp(-x*λ)
        fm.func_code = make_func_code(["A","B","λ"])

    def jl(self,x,A,B,φ,λ): 
        """
        Bessel j0 precession times Lorentzian decay, 
        
        x [mus], A, B [mT], φ [degrees], λ [mus-1]
        """
        # x need not be self.x (e.g. in plot)
        
        return A*j0(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-x*λ)
        jl.func_code = make_func_code(["A","B","φ","λ"])

    def jg(self,x,A,B,φ,σ): 
        """
        Bessel j0 precession times Gaussian decay, 
        
        x [mus], A, B [mT], φ [degrees], σ [mus-1] (positive parity)
        """
        
        # x need not be self.x (e.g. in plot)
        
        return A*j0(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-0.5*(x*σ)**2)
        jg.func_code = make_func_code(["A","B","φ","σ"])

    def j0(self,x,A,B,φ,λ,σ): 
        """
        precession A j1(2 pi _gamma_Mu_MHzper_mT B x+φ _radeg_) times Gaussian times Lorentzian decays, 
        
        x [mus], A, B [mT], φ [degrees], 
        λ [mus-1], σ [mus-1]  (positive parity)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*j0(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-x*λ)*exp(-0.5*(x*σ)**2)
        mu.func_code = make_func_code(["A","B","φ","λ","σ"])

    def js(self,x,A,B,φ,Λ,β): 
        """
        Bessel j0 precession times stretched decay, 
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*j0(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-(x*Λ)**β)
        js.func_code = make_func_code(["A","B","φ","Λ","β"])

    def _derivative_js_(self,x,A,B,φ,Λ,β): 
        """
        derivative of js with respect to total phase alpha =  2 pi _gamma_Mu_MHzper_mT B x + φ _radeg_,
        
        - A sin(2 pi _gamma_Mu_MHzper_mT B x + φ _radeg_) times stretched decay
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0)
        """
        
        return -A*j1(2*pi*self._gamma_Mu_MHzper_mT*B*x+φ*self._radeg_)*exp(-(x*Λ)**β)

    def _grad_js_0_(self,x,A,B,φ,Λ,β): 
        """
        derivative of js with respect to A in terms of self.mu and self._derivative_mu_
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0) 
        """
        
        return self.js(x,A,B,φ,Λ,β)/A

    def _grad_js_1_(self,x,A,B,φ,Λ,β): 
        """
        derivative of js with respect to B in terms of self.mu and self._derivative_mu_
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0) 
        """
        
        return -2*pi*self._gamma_Mu_MHzper_mT*x*self._derivative_js_(x,A,B,φ,Λ,β)

    def _grad_js_2_(self,x,A,B,φ,Λ,β): 
        """
        derivative of js with respect to φ in terms of self.mu and self._derivative_mu_
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0)
        """
        
        return -self._radeg_*self._derivative_js_(x,A,B,φ,Λ,β)

    def _grad_js_3_(self,x,A,B,φ,Λ,β): 
        """
        derivative of ms with respect to Λ in terms of self.mu and self._derivative_mu_
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0)
        """
        
        return -β/Λ*(Λ*x)**β*self.js(x,A,B,φ,Λ,β)

    def _grad_js_4_(self,x,A,B,φ,Λ,β): 
        """
        derivative of js with respect to β in terms of self.mu and self._derivative_mu_
        
        x [mus], A, B [mT], φ [degrees], Λ [mus-1] (>0), β (>0)
        """
        
        return -log(Λ*x)*(Λ*x)**β*self.js(x,A,B,φ,Λ,β)
        
# kubo toyabe and fm gradients not implemented

    def _kg(self,t,w,Δ):
        """
        auxiliary component for a static Gaussian Kubo Toyabe in longitudinal field, 
        
        t [mus], w [mus-1], Δ [mus-1], 
        w = 2*pi*gamma_mu*L_field
        The first derivative of dawsn(x) is 1-2*x*dawsn(x)
        """
        
        # note that t can be different from self._x_
        Dt = Δ*t
        DDtt = Dt**2
        DD = Δ**2
        sqr2 = sqrt(2)
        argf = w/(sqr2*Δ)
        fdc = dawsn(argf)
        wt = w*t
        if (w!=0): # non-vanishing Longitudinal Field
            Aa = real(exp(-0.5*DDtt + 1j*wt)*dawsn(-argf - 1j*Dt/sqr2) )
            Aa[Aa == inf] = 0 # bi-empirical fix
            nan_to_num(Aa,copy=False) # empirical fix 
            A=sqr2*(Aa + fdc)
            f = 1. - 2.*DD/w**2*(1-exp(-.5*DDtt)*cos(wt)) + 2.*(Δ/w)**3*A
        else:
            f = (1. + 2.*(1-DDtt)*exp(-.5*DDtt))/3.
        return f

    def _kl(self,t,w,Δ):
        """
        static Lorentzian Kubo Toyabe in longitudinal field, 
        
        t [mus], w [mus-1], Δ [mus-1], 
        w = 2*pi*gamma_mu*L_field
        """
        
        # note that t can be different from self._x_
        Dt = Δ*t
        wt = w*t
        dt = t[1]-t[0]
        Dtt = Δ*t[1:] # eliminate first point when singular at t=0
        wtt = w*t[1:] # eliminate first point when singular at t=0
        if w*Δ: # non-vanishing Longitudinal Field
            if abs(w/Δ)<2e-9:
                f = (1. + 2.*(1-Dt)*exp(-Dt))/3.
            else:
                
                if t[0]: # singularity at t=0
                    c = Δ/wtt**2.*(1+Dtt) 
                    f =append(-2/3*Δ, exp(-Dtt)*(sin(wtt)/wtt*(c-Δ)-c*cos(wtt))) # put back first point
                else: # no singularities
                    c = Δ/wt**2.*(1+Dt)
                    f = exp(-Dt)*(sin(wt)/wt*(c-Δ)-c*cos(wt))
                f = 2*cumsum(f*dt)+1 # simplified integral, accuracy < 1e-3;
        else:
            f = (1. + 2.*(1-Dt)*exp(-Dt))/3.
        return f

    def _kgdyn(self,x,w,Δ,ν,*argv):
        """ 
        auxiliary dynamization of Gaussian Kubo Toyabe by G. Allodi 
        
        N: number of sampling points;
        dt: time interval per bin [i.e. time base is t = dt*(0:N-1)]
        w [mus-1], Δ [mus-1], ν [MHz] 
        (longitudinal field freq, Gaussian distribution, scattering frequency 
        % alphaN: [optional argument] weighting coefficient alpha times N. Default=10 
        """
        
        alphaN = 10. if not argv else argv[0] # default is 10.
        dt = x[1]-x[0]
        N = x.shape[0] + int(ceil(x[0]/dt)) # for function to include t=0
        Npad = N * 2 # number of total time points, includes as many zeros
        t = dt*linspace(0.,Npad-1,Npad)
        expwei = exp(-(alphaN/(N*dt))*t)

        gg = self._kg(t,w,Δ)*(t < dt*N)  #  padded_KT, here t is not x 
        # gg = 1/3*(1 + 2*(1 - s^2*tt.^2).*exp(-(.5*s^2)*tt.^2)) % 

        ff = fft.fft(gg*expwei*exp(-ν*t)) # fft(padded_KT*exp(-jump_rate*t))
        FF = exp(-ν*dt)*ff/(1.-(1.-exp(-ν*dt))*ff) # (1-jump_rate*dt*ff)  

        dkt = real(fft.ifft(FF))/expwei  # ifft
        dkt = dkt[0:N] # /dkt(1) 

        #if (nargout > 1),
        #   t = t[0:intN-1]
        return dkt
         
    def kg(self,x,A,BL,Δ,ν):
        """
        Gauss Kubo Toyabe in (fixed) long field, static or dynamic
        
        x [mus], A, BL [mT], Δ [mus-1] (positive parity), ν (MHz)
        """
        
        # x need not be self.x (e.g. in plot)
        N = x.shape[0]
        w = 2*pi*BL*self._gamma_Mu_MHzper_mT
        if ν==0: # static 
           f = self._kg(x,w,Δ) # normalized to 1. In this case t = x
        else :            # dynamic
           # P=[w Δ];
 
           f = self._kgdyn(x,w,Δ,ν)
# function generated from t=0, shift result nshift=data(1,1)/dt bins backward
           dt = x[1]-x[0]
           nshift = x[0]/dt
           Ns = N + ceil(nshift)
           if Ns%2: # odd
               Np = Ns//2
               Nm = -Np
           else: # even
               Np = Ns//2-1
               Nm = -Ns//2
           # WARNING! was is inspace)0,Np,,Np+1= but what is inspace?
           n = hstack((linspace(0,Np,Np+1),linspace(Nm,-1.,-Nm))) # 
           f = fft.ifft(fft.fft(f)*exp(nshift*1j*2*pi*n/Ns)) # shift back
        # multiply by amplitude
        f = A*real(f[0:N])
        return f
        kg.func_code = make_func_code(["A","BL","Δ","ν"])

    def kl(self,x,A,BL,Γ):
        """
        Lorent Kubo Toyabe in (fixed) long field, static 
        
        x [mus], A, BL [mT], Γ [mus-1] 
        """
        
        # x need not be self.x (e.g. in plot)
        # (dynamic makes no sense)
        w = 2*pi*BL*self._gamma_Mu_MHzper_mT
        return A*self._kl(x,w,Γ)
        kl.func_code = make_func_code(["A","BL","Γ"])

    def kd(self,x,A,Δ,λ):
        """
        Gauss Kubo Toyabe static times Lorentz decay
        
        x [mus], A, B [T], Δ [mus-1], ν (MHz)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*self._kg(x,0,Δ)*exp(-x*λ)
        kd.func_code = make_func_code(["A","Δ","λ"])
        #kd.limits = [[None,None],[0.,None],[None,None]]
        #kd.error = [0.002,0.05,0.05]

    def ks(self,x,A,Δ,Λ,β):
        """
        Gauss Kubo Toyabe times stretched decay
        
        x [mus], A, B [T], Δ [mus-1], Λ [mus-1] (>0), β (>0)
        """
        
        # x need not be self.x (e.g. in plot)
        return A*self._kg(x,0,Δ)*exp(-(x*Λ)**β)
        ks.func_code = make_func_code(["A","Δ","Λ","β"])
        #kd.limits = [[None,None],[0.,None],[None,None]]
        #kd.error = [0.002,0.05,0.05]

