from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib import admin

# Constants

ACCESS = (
    ('public', 'Public'),
    ('private', 'Private'),
    ('archived', 'Archived')
)
PUBLIC = 'public'

GROUP_BY = (
    ('strain', 'Strain'),
    ('protocol', 'Protocol'),

)

STRAIN = 'strain'

FIELDS = ( ('red', 'Red'), ('green', 'Green'), ('blue', 'Blue'), ('merge', 'All'))
ALL = 'merge'

MICRO = ( ('Dye', 'Dye/Stain'), ('IF', 'Antibody-labeling IF'), ('IHC', 'Antibody-labeling IHC'))

MICRO_DYE = 'Dye'


# Common Models


class Course(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.code)


class Assignment(models.Model):
    course = models.ForeignKey(Course, related_name='assignments')
    assignment_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    access = models.CharField(max_length=50, choices=ACCESS, default=PUBLIC)
    basedOn = models.ForeignKey("Assignment", null=True, blank=True)
    group_by = models.CharField(max_length=50, choices=GROUP_BY, default=STRAIN)
    # tecniques
    has_wb = models.BooleanField(default=False)
    has_fc = models.BooleanField(default=False)
    has_micro = models.BooleanField(default=False)
    # protocol parts
    has_concentration = models.BooleanField(default=True)
    has_temperature = models.BooleanField(default=True)
    has_start_time = models.BooleanField(default=True)
    has_duration = models.BooleanField(default=True)
    has_collection_time = models.BooleanField(default=True)


# Experiment setup

class AssignmentText(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='assignment_text')
    title = models.CharField(max_length=40)
    text = models.TextField()


class Strains(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='strains')
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Protocol(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='protocols')
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class StrainProtocol(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='strain_protocol')
    strain = models.ForeignKey(Strains)
    protocol = models.ForeignKey(Protocol)
    enabled = models.BooleanField(default=True)


class Treatments(models.Model):
    protocol = models.ForeignKey(Protocol, related_name='treatments')
    order = models.IntegerField(default=0)
    treatment = models.CharField(max_length=50)
    concentration = models.CharField(max_length=50)
    concentration_unit = models.CharField(max_length=50)
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    temperature = models.CharField(max_length=50)
    collection_time = models.CharField(max_length=50)

    class Meta:
        ordering = ['order', ]


class WesternBlot(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True, related_name='western_blot')
    # lysate types
    has_whole_cell_lysate = models.BooleanField(default=True)
    has_nuclear_fractination = models.BooleanField(default=True)
    has_cytoplasmic_fractination = models.BooleanField(default=True)
    # gel types
    has_gel_10 = models.BooleanField(default=True)
    has_gel_12 = models.BooleanField(default=True)
    has_gel_15 = models.BooleanField(default=True)


class WesternBlotAntibody(models.Model):
    western_blot = models.ForeignKey(WesternBlot, related_name='antibodies')
    primary = models.CharField(max_length=50)
    secondary = models.CharField(max_length=50)


class WesternBlotAntibodyBands(models.Model):
    antibody = models.ForeignKey(WesternBlotAntibody, related_name='bands')
    strain_protocol = models.ForeignKey(StrainProtocol, related_name='bands')
    wcl_weight = models.FloatField(default=0.00)
    wcl_intensity = models.FloatField(default=0.00)
    nuc_weight = models.FloatField(default=0.00)
    nuc_intensity = models.FloatField(default=0.00)
    cyto_weight = models.FloatField(default=0.00)
    cyto_intensity = models.FloatField(default=0.00)
    is_background = models.BooleanField(default=False)


class MicroscopySamplePrep(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='microscopy_sample_prep')
    analysis = models.CharField(max_length=50, choices=MICRO, default=MICRO_DYE)
    condition = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    has_filters = models.BooleanField(default=False)


class MicroscopyImages(models.Model):
    sample_prep = models.ForeignKey(MicroscopySamplePrep, related_name='microscopy_images')
    strain_protocol = models.ForeignKey(StrainProtocol, related_name='microscopy_images')
    order = models.IntegerField(default=0)
    objective = models.CharField(max_length=50, default='N/A')
    url = models.URLField(max_length=300)
    image = models.FileField(max_length=300, upload_to='microscopy_images', null=True)
    filter = models.CharField(max_length=50, choices=FIELDS, default=ALL)


FACS_CT = (( 'Fixed', 'Fixed Cells'), ('Live', 'Live Cells'))

FACS_FIXED = 'Fixed'

FACS_KINDS = (( 'Dye', 'Dye/Stain' ), ('Anti', 'Antibody-labeling'))

FACS_DYE = 'Dye'


class FlowCytometrySamplePrep(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='facs_sample_prep')
    treatment = models.CharField(max_length=50, choices=FACS_CT, default=FACS_FIXED)
    analysis = models.CharField(max_length=50, choices=FACS_KINDS, default=FACS_DYE)
    condition = models.CharField(max_length=50)
    order = models.IntegerField(default=0)


HISTOGRAMS = (( 'normal', 'Normal'),
              ('s-block','s-block'),
              ('g1-block','g1-block'),
              ('g2-block','g2-block'),
              ('alpha-block','alpha-block'),
              ('2-peak-normal-400','2-peak-normal-400'),
              ('peak-100-normal-400','peak-100-normal-400'),
              ('2-peak-uneven-normal-400','2-peak-uneven-normal-400'),
              ('peak-50-normal-400','peak-50-normal-400'),
              ('4-peak-normal-400','4-peak-normal-400'),
              ('s-block-normal-400','s-block-normal-400'),
              ('custom', 'Custom'))

GAUSS = 'normal'


class FlowCytometryHistogram(models.Model):
    sample_prep = models.ForeignKey(FlowCytometrySamplePrep, related_name='histograms')
    strain_protocol = models.ForeignKey(StrainProtocol, related_name='histograms')
    kind = models.CharField(max_length=50, choices=HISTOGRAMS, default=GAUSS)
    data = models.TextField(null=True,blank=True)
    enabled = models.BooleanField(default=False)

admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Protocol)
admin.site.register(Strains)
admin.site.register(StrainProtocol)
admin.site.register(Treatments)
admin.site.register(WesternBlot)
admin.site.register(WesternBlotAntibody)
admin.site.register(WesternBlotAntibodyBands)




