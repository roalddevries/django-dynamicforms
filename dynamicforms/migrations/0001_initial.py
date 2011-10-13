# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DynamicFieldValue'
        db.create_table('dynamicforms_dynamicfieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, blank=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dynamicforms.DynamicField'])),
        ))
        db.send_create_signal('dynamicforms', ['DynamicFieldValue'])

        # Adding model 'DynamicField'
        db.create_table('dynamicforms_dynamicfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('default', self.gf('django.db.models.fields.related.ForeignKey')(max_length=200, related_name='default_for', null=True, blank=True, to=orm['dynamicforms.DynamicFieldValue'])),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('dynamicforms', ['DynamicField'])

        # Adding model 'DynamicFormFieldRelation'
        db.create_table('dynamicforms_dynamicformfieldrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dynamicform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamicforms.DynamicForm'])),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('dynamicfield', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamicforms.DynamicField'], null=True, blank=True)),
            ('sort_weight', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
        ))
        db.send_create_signal('dynamicforms', ['DynamicFormFieldRelation'])

        # Adding model 'DynamicForm'
        db.create_table('dynamicforms_dynamicform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('success_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('notification_emails', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('send_confirmation', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email_recipients', self.gf('django.db.models.fields.CharField')(max_length=502, blank=True)),
            ('email_subject', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('email_content', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('dynamicforms', ['DynamicForm'])

        # Adding model 'DynamicFormData'
        db.create_table('dynamicforms_dynamicformdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dynamicform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamicforms.DynamicForm'])),
            ('raw_post_data', self.gf('django.db.models.fields.TextField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('headers', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('dynamicforms', ['DynamicFormData'])


    def backwards(self, orm):
        
        # Deleting model 'DynamicFieldValue'
        db.delete_table('dynamicforms_dynamicfieldvalue')

        # Deleting model 'DynamicField'
        db.delete_table('dynamicforms_dynamicfield')

        # Deleting model 'DynamicFormFieldRelation'
        db.delete_table('dynamicforms_dynamicformfieldrelation')

        # Deleting model 'DynamicForm'
        db.delete_table('dynamicforms_dynamicform')

        # Deleting model 'DynamicFormData'
        db.delete_table('dynamicforms_dynamicformdata')


    models = {
        'dynamicforms.dynamicfield': {
            'Meta': {'object_name': 'DynamicField'},
            'default': ('django.db.models.fields.related.ForeignKey', [], {'max_length': '200', 'related_name': "'default_for'", 'null': 'True', 'blank': 'True', 'to': "orm['dynamicforms.DynamicFieldValue']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'dynamicforms.dynamicfieldvalue': {
            'Meta': {'object_name': 'DynamicFieldValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['dynamicforms.DynamicField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'})
        },
        'dynamicforms.dynamicform': {
            'Meta': {'ordering': "['name']", 'object_name': 'DynamicForm'},
            'email_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_recipients': ('django.db.models.fields.CharField', [], {'max_length': '502', 'blank': 'True'}),
            'email_subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dynamicforms.DynamicField']", 'through': "orm['dynamicforms.DynamicFormFieldRelation']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notification_emails': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'send_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'success_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'dynamicforms.dynamicformdata': {
            'Meta': {'ordering': "['dynamicform', '-timestamp']", 'object_name': 'DynamicFormData'},
            'dynamicform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamicforms.DynamicForm']"}),
            'headers': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_post_data': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'dynamicforms.dynamicformfieldrelation': {
            'Meta': {'ordering': "['dynamicform__name', 'sort_weight', 'field_name']", 'object_name': 'DynamicFormFieldRelation'},
            'dynamicfield': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamicforms.DynamicField']", 'null': 'True', 'blank': 'True'}),
            'dynamicform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamicforms.DynamicForm']"}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sort_weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'})
        }
    }

    complete_apps = ['dynamicforms']
