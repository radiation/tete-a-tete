# Generated by Django 4.2.7 on 2023-11-20 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0002_meeting_num_reschedules'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='actionitem',
            name='assignee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actionitems_assignee_related', to='restapi.user'),
        ),
        migrations.AlterField(
            model_name='actionitem',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actionitems_meeting_related', to='restapi.meeting'),
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField()),
                ('answerer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_answerer_related', to='restapi.user')),
                ('asker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_asker_related', to='restapi.user')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionanswers_question_related', to='restapi.question')),
            ],
        ),
    ]
