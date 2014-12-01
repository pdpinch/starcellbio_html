from instructor.models import *
import json


def preview_as_json(assignment_id):
    return json.dumps(preview(assignment_id))


def preview(assignment_id):
    ret = dict()
    ret['app_title'] = 'StarCellBio Preview'
    ret['app_description'] = 'StarCellBio Instructor Preview'
    ret['assignments'] = {'list': [compile(assignment_id)]}
    return ret


def compile(assignment_id):
    a = Assignment.objects.get(id=assignment_id)
    ret = {
        'id': 'a_{}'.format(a.id),
        'name': a.name,
        'course': a.course.code,
        'course_name': a.course.name,
        'description': a.name,
        'notebook': {},
        'experiments': {},
        'template': {
            'experiment_setup': 'Experiment Setup',
            'ui': {
                'experimental_design': {
                    'techniques': compile_techniques(a)
                },
                'experiment_setup': {
                    'table': [
                        {'kind': "cell_line",
                         'title': "Strain",
                         'editable': 'false'
                        },
                    ], 'actions': [
                    {'kind': 'add_protocol', 'name': 'Add Protocol'}
                ]
                }
            },
            'cell_lines': compile_cell_lines(a.strains.all()),
            'time_unit': {
                'kind': 'minutes'
            }
        }
    }
    treatments = [{'kind': "drug", 'title': "Treatments", 'editable': False}, ]
    if a.has_concentration:
        treatments.append({'kind': "concentration", 'title': "Concentration", 'editable': False})
    if a.has_temperature:
        treatments.append({'kind': "temperature", 'title': "Temperature", 'editable': False})
    if a.has_start_time:
        treatments.append({'kind': "start", 'title': "Start", 'editable': False})
    if a.has_duration:
        treatments.append({'kind': "duration", 'title': "Duration", 'editable': False})
    if a.has_collection_time:
        treatments.append({'kind': "collection", 'title': "Collection Time", 'editable': False})
    table = ret['template']['ui']['experiment_setup']['table']
    table.append({'kind': "treatments", 'children': treatments})

    instructions = []
    for t in a.assignment_text.all():
        instructions.append([t.title, t.text])
    ret['template']['instructions'] = instructions

    ret['template']['ui']['add_multiple_dialog'] = add_multiple_dialog(a)
    ret['template']['drugs'] = drugs(a)
    ret['template']['concentrations'] = concentrations(a)
    ret['template']['experiment_temperatures'] = experiment_temperatures(a)

    return ret


def drugs(a):
    ret = {}
    for sp in a.strain_protocol.filter(enabled=True):
        strain = sp.strain
        protocol = sp.protocol
        for t in protocol.treatments.all():
            tr = t.treatment
            ret[str(tr)] = { 'name': str(tr) }
    return ret


def concentrations(a):
    ret = {}
    for sp in a.strain_protocol.filter(enabled=True):
        strain = sp.strain
        protocol = sp.protocol
        for t in protocol.treatments.all():
            tr = t.concentration
            ret[str(tr)] = {
                'name': str(tr),
                'value': tr
            }
    return ret


def experiment_temperatures(a):
    ret = {}
    for sp in a.strain_protocol.filter(enabled=True):
        strain = sp.strain
        protocol = sp.protocol
        for t in protocol.treatments.all():
            tr = t.temperature
            ret[str(tr)] = {
                'name': str(tr),
                'value': tr
            }
    return ret


def add_multiple_dialog(a):
    ret = []
    for sp in a.strain_protocol.filter(enabled=True):
        strain = sp.strain
        protocol = sp.protocol
        row = {
            'id': "SP_ID_{}".format(str(sp.id)),
            'protocol': protocol.name,
            'strain': strain.name,
            'cell_line': str(strain.id),
            'treatment_list': {
                'list': compile_treatments(protocol.treatments.all())
            }
        }
        ret.append(row)
    return ret


def compile_treatments(treatments):
    ret = []
    for t in treatments:
        row = {
            'id': 'treatment_{}'.format(t.id),
            'drug_list': {'list': [{
                                       'drug_id': t.treatment,
                                       'drug_name': t.treatment,
                                       'concentration_id': t.concentration
                                   }]},
            'start_time': t.start_time,
            'end_time': t.end_time,
            'temperature': t.temperature,
            'collection_time': t.collection_time
        }
        ret.append(row)
    return ret


def compile_cell_lines(cell_lines):
    ret = {}
    for c in cell_lines:
        ret[str(c.id)] = {'name': c.name}
    return ret


def compile_techniques(a):
    ret = []
    if a.has_fc:
        ret.append('facs')
    if a.has_micro:
        ret.append('micro')
    if a.has_wb:
        ret.append('wb')
    return ret
